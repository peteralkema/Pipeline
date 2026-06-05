#!/usr/bin/env python3
"""
patch_assemble_ffmpeg.py — replace moviepy assembly with ffmpeg assembly,
permanently, in recreation_pipeline.py.

WHY: moviepy's concatenate_videoclips OOMs on long videos (eyam: 109 clips,
killed even at 14GB free — it's a moviepy memory blowup, not a RAM ceiling).
ffmpeg streams via the concat demuxer at near-constant memory.

WHAT IT DOES (safely):
  1. Backs up recreation_pipeline.py -> .pre_ffmpeg_assemble
  2. Renames the existing `def assemble(` -> `def assemble_moviepy(`  (kept as fallback)
  3. Inserts a new ffmpeg-based `def assemble(` with the IDENTICAL signature
     directly above it, so both call sites work unchanged.
  4. Verifies and prints a grep.

The new assemble():
  - same signature: assemble(clip_paths, voice_path, out_path, music_path=None)
  - reads per-shot durations from storyboard.json (Whisper audio_duration first,
    then word-count proxy, then uniform) — same three-tier logic as before
  - trims each clip to its duration (light re-encode, low memory)
  - concatenates via ffmpeg concat demuxer (streaming)
  - muxes voiceover (+ optional looped music bed) at the original mix levels
  - writes out_path

Idempotent: aborts if already patched. Reversible: cp the backup back.

Run on the box:
    cd ~/Pipeline
    python shared/patch_assemble_ffmpeg.py
"""

import shutil
import sys
from pathlib import Path

PIPE = Path(__file__).resolve().parent / "recreation_pipeline.py"

NEW_ASSEMBLE = '''def assemble(clip_paths: list, voice_path: Path, out_path: Path,
             music_path=None) -> Path:
    """
    ffmpeg-based assembly (replaces the moviepy version, which OOMs on long
    videos). Trims each clip to its per-shot duration, concatenates via the
    ffmpeg concat demuxer (streaming, near-constant memory), then muxes the
    voiceover and optional music bed. The moviepy implementation is preserved
    as assemble_moviepy() for fallback.

    Per-shot duration source priority (unchanged from the moviepy version):
      1. Whisper-measured audio_duration in storyboard.json
      2. word-count proxy from narration
      3. uniform (voice_duration / n)
    """
    import json as _json
    import subprocess as _sub
    import tempfile as _tmp
    import shutil as _shutil
    import math as _math

    n = len(clip_paths)
    if n == 0:
        raise SystemExit("No clips to assemble.")

    project_dir = Path(voice_path).parent

    def _probe(p):
        r = _sub.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                     stdout=_sub.PIPE, stderr=_sub.DEVNULL, text=True)
        try:
            return float(r.stdout.strip())
        except ValueError:
            return 0.0

    def _run(cmd, desc):
        r = _sub.run(cmd, stdout=_sub.DEVNULL, stderr=_sub.PIPE, text=True)
        if r.returncode != 0:
            tail = "\\n".join(r.stderr.strip().splitlines()[-8:])
            raise SystemExit(f"ffmpeg failed during {desc}:\\n{tail}")

    voice_dur = _probe(voice_path)

    # Auto-align with Whisper if available (same hook the moviepy path used).
    _storyboard_path = project_dir / "storyboard.json"
    if _storyboard_path.exists():
        try:
            _auto_align_with_whisper(voice_path, _storyboard_path)
        except Exception as _e:
            print(f"   assemble: whisper auto-align skipped ({_e})")

    # Resolve per-shot durations.
    durations = None
    try:
        if _storyboard_path.exists():
            _data = _json.loads(_storyboard_path.read_text())
            _shots = _data if isinstance(_data, list) else _data.get("beats", _data.get("shots", []))
            if len(_shots) == n:
                if all("audio_duration" in s for s in _shots):
                    durations = [float(s["audio_duration"]) for s in _shots]
                    print(f"   assemble: Whisper-measured per-shot durations")
                else:
                    _words = [max(1, len(s.get("narration", "").split())) for s in _shots]
                    _total = sum(_words)
                    durations = [voice_dur * (w / _total) for w in _words]
                    print(f"   assemble: word-count-proxy per-shot durations")
    except Exception as _e:
        print(f"   assemble: duration lookup failed ({_e}), using uniform")
        durations = None

    if durations is None:
        z = voice_dur / n
        durations = [z] * n
        print(f"   assemble: uniform {voice_dur:.1f}s / {n} = {z:.2f}s per clip")

    print(f"   assemble: range {min(durations):.2f}s - {max(durations):.2f}s, "
          f"total {sum(durations):.1f}s (ffmpeg streaming)")

    work = Path(_tmp.mkdtemp(prefix="assemble_", dir=str(project_dir)))
    try:
        # Trim each clip to its target duration (low-memory, one at a time).
        trimmed = []
        for i, (clip, target) in enumerate(zip(clip_paths, durations), 1):
            dst = work / f"t_{i:03d}.mp4"
            native = _probe(clip)
            cut = min(target, native) if native > 0 else target
            _run([
                "ffmpeg", "-y", "-i", str(clip),
                "-t", f"{cut:.3f}",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-pix_fmt", "yuv420p", "-an",
                "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,"
                       "pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
                str(dst),
            ], f"trim clip {i}")
            trimmed.append(dst)
            if i % 10 == 0 or i == n:
                print(f"   assemble: trimmed {i}/{n}")

        # Concat via demuxer (streaming).
        print("   assemble: concatenating (ffmpeg demuxer)...")
        concat_list = work / "concat.txt"
        concat_list.write_text("".join(f"file '{c.resolve()}'\\n" for c in trimmed))
        silent = work / "silent.mp4"
        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
              "-i", str(concat_list), "-c", "copy", str(silent)], "concat")

        # Build audio: voice, optional music bed looped + ducked under it.
        if music_path and Path(music_path).exists():
            print("   assemble: muxing voice + music bed...")
            music_dur = _probe(music_path)
            looped_music = work / "music_looped.m4a"
            if music_dur > 0 and music_dur < voice_dur:
                reps = _math.ceil(voice_dur / music_dur)
                mlist = work / "mlist.txt"
                mlist.write_text("".join(f"file '{Path(music_path).resolve()}'\\n" for _ in range(reps)))
                _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(mlist),
                      "-c", "copy", str(looped_music)], "loop music")
                music_src = looped_music
            else:
                music_src = Path(music_path)
            # Mix: voice at 1.15, music at 0.07 (original VOICE_LEVEL/MUSIC_LEVEL).
            _run([
                "ffmpeg", "-y",
                "-i", str(silent),
                "-i", str(voice_path),
                "-i", str(music_src),
                "-filter_complex",
                "[1:a]volume=1.15[v];[2:a]volume=0.07[m];[v][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
                "-map", "0:v:0", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-t", f"{voice_dur:.3f}",
                str(out_path),
            ], "mux voice+music")
        else:
            print("   assemble: muxing voiceover...")
            _run([
                "ffmpeg", "-y",
                "-i", str(silent),
                "-i", str(voice_path),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-map", "0:v:0", "-map", "1:a:0",
                "-t", f"{voice_dur:.3f}",
                str(out_path),
            ], "mux voice")

        final_dur = _probe(out_path)
        print(f"   assemble: DONE {final_dur:.1f}s ({final_dur/60:.1f} min) -> {out_path}")
    finally:
        _shutil.rmtree(work, ignore_errors=True)

    return out_path


'''


def main():
    src = PIPE.read_text()

    if "def assemble_moviepy(" in src:
        print("Already patched (assemble_moviepy present). No change.")
        return

    anchor = "def assemble(clip_paths: list, voice_path: Path, out_path: Path,\n             music_path=None) -> Path:"
    if anchor not in src:
        print("ERROR: could not find the exact assemble() signature to patch.", file=sys.stderr)
        print("       The function may have changed. Aborting WITHOUT editing.", file=sys.stderr)
        print("       Inspect shared/recreation_pipeline.py around line 770 manually.", file=sys.stderr)
        sys.exit(1)

    backup = PIPE.with_suffix(".py.pre_ffmpeg_assemble")
    shutil.copy2(PIPE, backup)
    print(f"Backed up -> {backup.name}")

    # 1. Rename the existing assemble() to assemble_moviepy() (keep as fallback).
    renamed = src.replace(anchor, anchor.replace("def assemble(", "def assemble_moviepy(", 1), 1)

    # 2. Insert the new ffmpeg assemble() directly ABOVE assemble_moviepy().
    patched = renamed.replace(
        "def assemble_moviepy(clip_paths: list, voice_path: Path, out_path: Path,",
        NEW_ASSEMBLE + "def assemble_moviepy(clip_paths: list, voice_path: Path, out_path: Path,",
        1,
    )

    PIPE.write_text(patched)

    check = PIPE.read_text()
    ok_new = check.count("def assemble(clip_paths: list, voice_path: Path, out_path: Path,") >= 1
    ok_old = "def assemble_moviepy(" in check
    ok_ffmpeg = "ffmpeg concat demuxer" in check
    print(f"new ffmpeg assemble() present: {ok_new}")
    print(f"assemble_moviepy() fallback present: {ok_old}")
    print(f"ffmpeg logic inserted: {ok_ffmpeg}")
    if not (ok_new and ok_old and ok_ffmpeg):
        print("\\nVERIFICATION FAILED — restoring backup.", file=sys.stderr)
        shutil.copy2(backup, PIPE)
        print("Restored. No changes applied.", file=sys.stderr)
        sys.exit(1)

    print("\\nPatched OK. Verify with:")
    print('  grep -n "def assemble" ~/Pipeline/shared/recreation_pipeline.py')
    print("  (expect: def assemble(...) AND def assemble_moviepy(...))")
    print("\\nThen re-run eyam assembly (reuses clips/voice, $0):")
    print("  cd ~/Pipeline/final-hours")
    print("  python ../shared/recreation_pipeline.py finish --project projects/eyam --no-music --assemble-only")
    print("\\nIf anything is wrong, restore with:")
    print(f"  cp {backup} {PIPE}")


if __name__ == "__main__":
    main()
