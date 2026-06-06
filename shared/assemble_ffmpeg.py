#!/usr/bin/env python3
"""
assemble_ffmpeg.py — memory-safe final assembly via ffmpeg.

Drop-in replacement for the moviepy assemble() step when it OOMs (moviepy's
concatenate_videoclips balloons past available RAM on long videos — eyam died
at 14GB free). ffmpeg streams clips through the concat demuxer at near-constant
memory regardless of clip count.

What it does (mirrors the pipeline's assemble logic):
  1. Reads each shot's Whisper-measured `audio_duration` from storyboard.json
  2. Trims each clip to exactly that duration (light re-encode, CPU-bound, low RAM)
  3. Concatenates all trimmed clips via the ffmpeg concat demuxer (streaming)
  4. Muxes the voiceover over the concatenated video, trimming video to voice length
  5. Writes final_video.mp4 into the project folder

Reads ONLY existing on-disk files. No Kling, no Inworld, no fal. $0.
Does NOT modify recreation_pipeline.py.

Usage (from channel root, e.g. final-hours/):
    python ../shared/assemble_ffmpeg.py --project projects/eyam

    # keep the per-shot trimmed temp files for inspection:
    python ../shared/assemble_ffmpeg.py --project projects/eyam --keep-temp
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd: list, desc: str):
    """Run ffmpeg quietly; surface errors clearly."""
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        print(f"\nERROR during {desc}:", file=sys.stderr)
        # last few lines of ffmpeg stderr are the useful part
        tail = "\n".join(r.stderr.strip().splitlines()[-8:])
        print(tail, file=sys.stderr)
        sys.exit(1)


def ffprobe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def load_shots(storyboard: Path) -> list:
    d = json.loads(storyboard.read_text())
    return d if isinstance(d, list) else d.get("beats", d.get("shots", []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--keep-temp", action="store_true")
    ap.add_argument("--output", default=None, help="override output path")
    args = ap.parse_args()

    # Resolve project dir (match pipeline convention: bare name -> projects/<name>)
    project = Path(args.project)
    if not project.is_absolute() and len(project.parts) == 1 and Path("projects").is_dir():
        project = Path("projects") / project
    if not project.is_dir():
        sys.exit(f"Project dir not found: {project}")

    clips_dir = project / "clips"
    voice = project / "voiceover.mp3"
    storyboard = project / "storyboard.json"
    out = Path(args.output) if args.output else project / "final_video.mp4"

    for p, label in [(clips_dir, "clips dir"), (voice, "voiceover.mp3"), (storyboard, "storyboard.json")]:
        if not p.exists():
            sys.exit(f"Missing {label}: {p}")

    shots = load_shots(storyboard)
    n = len(shots)
    print(f"Project: {project.name}")
    print(f"Shots: {n}")

    # Verify clips + durations present
    missing, durations = [], []
    for i, s in enumerate(shots, 1):
        clip = clips_dir / f"shot_{i:03d}.mp4"
        if not clip.exists():
            missing.append(clip.name)
        dur = s.get("audio_duration")
        if dur is None:
            sys.exit(f"Shot {i} has no audio_duration — run alignment first.")
        durations.append(float(dur))
    if missing:
        sys.exit(f"Missing clips: {missing[:5]}{' ...' if len(missing) > 5 else ''}")

    voice_dur = ffprobe_duration(voice)
    print(f"Voiceover duration: {voice_dur:.1f}s")
    print(f"Sum of shot durations: {sum(durations):.1f}s")

    work = Path(tempfile.mkdtemp(prefix="assemble_", dir=str(project)))
    print(f"Working dir: {work}")

    try:
        # ── Step 1: trim each clip to its target duration ──────────────────
        # Light re-encode to a uniform codec/params so the concat demuxer can
        # stream them without re-muxing surprises. Memory stays flat — one clip
        # at a time, ffmpeg streams it.
        print(f"\nTrimming {n} clips to measured durations...")
        trimmed = []
        for i, target in enumerate(durations, 1):
            src = clips_dir / f"shot_{i:03d}.mp4"
            dst = work / f"t_{i:03d}.mp4"
            native = ffprobe_duration(src)
            # If a clip is shorter than its slot, we still cut to min(native,target);
            # ffmpeg holds the last frame only if asked. Here we trim to target but
            # cap at native so we never request frames that don't exist.
            cut = min(target, native) if native > 0 else target
            run([
                "ffmpeg", "-y", "-i", str(src),
                "-t", f"{cut:.3f}",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-pix_fmt", "yuv420p", "-an",
                "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,"
                       "pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
                str(dst),
            ], f"trim shot {i}")
            trimmed.append(dst)
            if i % 10 == 0 or i == n:
                print(f"  trimmed {i}/{n}")

        # ── Step 2: concat via demuxer (streaming, low memory) ─────────────
        print("\nConcatenating (ffmpeg concat demuxer, streaming)...")
        concat_list = work / "concat.txt"
        concat_list.write_text("".join(f"file '{c.resolve()}'\n" for c in trimmed))
        silent = work / "silent.mp4"
        run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy", str(silent),
        ], "concat")

        # ── Step 3: mux voiceover, trim video to voice length ──────────────
        print("Muxing voiceover...")
        run([
            "ffmpeg", "-y",
            "-i", str(silent),
            "-i", str(voice),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-t", f"{voice_dur:.3f}",
            str(out),
        ], "mux voiceover")

        final_dur = ffprobe_duration(out)
        print(f"\nDONE -> {out}")
        print(f"  duration: {final_dur:.1f}s ({final_dur/60:.1f} min)")
        print(f"  size: {out.stat().st_size/1_000_000:.1f} MB")

    finally:
        if args.keep_temp:
            print(f"\n(kept temp dir: {work})")
        else:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
