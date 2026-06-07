#!/usr/bin/env python3
"""
patch_episode_audio_trueup.py — fix the 'audio cuts then resumes' artifact in
assemble_episode.py by building the whole audio track in ONE ffmpeg pass.

Same idempotent style as patch_animate_only.py. Run from repo root:
    python shared/patch_episode_audio_trueup.py

WHY: the old path encoded each beat's audio to AAC separately then concatenated
them. AAC encoder-delay padding leaves a tiny gap at every beat boundary (~40 of
them) — the audible chop. It also used `-ss` before `-i`, an imprecise MP3 seek
that clips word-tails.

FIX (validated against real ffmpeg before shipping): the spoken beats' vo_start/
vo_span tile the voiceover contiguously, so the continuous VO is reconstructable
by atrim-slicing it (sample-accurate, on decoded samples). Build ONE filtergraph:
  - spoken beat (vo_span>0): atrim [vo_start, vo_start+vo_span] from the VO
  - any inserted silence (silent-beat hold, or audio_duration - vo_span = the
    silence_after bonus): anullsrc
  - join with the concat FILTER (single decode+encode → no boundary gaps)
Total duration == sum(audio_duration) == the video track, so sync is structural.

Idempotent + self-verifying (ast-parse). Backs up to assemble_episode.py.pre_audio_trueup.
Independent of patch_episode_slowfill_music (different functions); apply either order.
"""
import sys, ast, shutil
from pathlib import Path

TARGET = Path(__file__).parent / "assemble_episode.py"

# ── Edit 1: insert build_audio_track() just before `def concat(` ───────────
CONCAT_DEF_ANCHOR = "def concat(segments, out, work, kind):\n"
BUILD_FN = '''def build_audio_track(beats, voiceover, work):
    """Build ONE continuous audio track in a single ffmpeg pass. Replaces the
    per-beat make_audio_segment + AAC-concat, which left encoder-delay gaps at
    every beat boundary ('audio cuts then resumes'). For each beat in order:
      - spoken (vo_span>0): atrim the real VO at [vo_start, vo_start+vo_span].
        These slices are contiguous across spoken beats, so they reconstruct the
        continuous voiceover exactly, sample-accurate (atrim is on decoded samples,
        unlike -ss). Any remainder (audio_duration - vo_span = silence_after bonus)
        becomes trailing silence.
      - fully silent beat (hold): anullsrc of audio_duration.
    Joined with the concat FILTER (single decode+encode) so there are NO inter-
    segment gaps. Total == sum(audio_duration) == the video track."""
    SR = 48000
    AFMT = f"aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo"
    parts, labels, k = [], [], 0
    for b in sorted(beats, key=lambda x: x["index"]):
        a_dur = float(b["audio_duration"])
        vo_span = float(b.get("vo_span") or 0.0)
        vo_start = b.get("vo_start")
        if vo_span > 0 and vo_start is not None:
            lbl = f"s{k}"; k += 1
            parts.append(f"[0:a]atrim=start={float(vo_start):.3f}:duration={vo_span:.3f},"
                         f"asetpts=PTS-STARTPTS,{AFMT}[{lbl}]")
            labels.append(lbl)
            gap = a_dur - vo_span
            if gap > 0.001:
                lbl = f"s{k}"; k += 1
                parts.append(f"anullsrc=r={SR}:cl=stereo,atrim=duration={gap:.3f},{AFMT}[{lbl}]")
                labels.append(lbl)
        else:
            if a_dur > 0.001:
                lbl = f"s{k}"; k += 1
                parts.append(f"anullsrc=r={SR}:cl=stereo,atrim=duration={a_dur:.3f},{AFMT}[{lbl}]")
                labels.append(lbl)
    if not labels:
        raise SystemExit("build_audio_track: no audio segments produced (empty/invalid timing table).")
    parts.append("".join(f"[{l}]" for l in labels) + f"concat=n={len(labels)}:v=0:a=1[aout]")
    graph = ";\\n".join(parts)
    script = work / "audio_filter.txt"
    script.write_text(graph)
    out = work / "audio.m4a"
    run(["ffmpeg", "-y", "-i", str(voiceover),
         "-filter_complex_script", str(script),
         "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", str(out)], "build continuous audio")
    return out


'''

# ── Edit 2: drop the per-beat audio segment call in the main loop ──────────
LOOP_ANCHOR = "            v_segs.append(make_video_segment(b, src, is_ph, dur, W, H, work, i))\n            a_segs.append(make_audio_segment(b, dur, voiceover, work, i))\n"
LOOP_REPLACE = "            v_segs.append(make_video_segment(b, src, is_ph, dur, W, H, work, i))\n"

# ── Edit 3: build the audio in one pass instead of concatenating segments ──
AUDIO_CONCAT_ANCHOR = '        full_a = concat(a_segs, work / "audio.m4a", work, "a")\n'
AUDIO_CONCAT_REPLACE = '        full_a = build_audio_track(beats, voiceover, work)\n'

EDITS = [
    ("def build_audio_track(", CONCAT_DEF_ANCHOR, BUILD_FN + CONCAT_DEF_ANCHOR, "insert build_audio_track()"),
    ("__LOOP__", LOOP_ANCHOR, LOOP_REPLACE, "drop per-beat audio segment call"),
    ("full_a = build_audio_track", AUDIO_CONCAT_ANCHOR, AUDIO_CONCAT_REPLACE, "single-pass audio build"),
]


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found. Run from repo root: python shared/patch_episode_audio_trueup.py")
    src = TARGET.read_text()
    original = src
    applied = []
    for marker, anchor, replacement, label in EDITS:
        if marker != "__LOOP__" and marker in src:
            print(f"skip: {label} already present.")
            continue
        if marker == "__LOOP__" and LOOP_ANCHOR not in src and "a_segs.append(make_audio_segment" not in src:
            print(f"skip: {label} already done.")
            continue
        if anchor not in src:
            sys.exit(f"FAIL: anchor for '{label}' not found — assemble_episode.py changed. Nothing written.")
        if src.count(anchor) != 1:
            sys.exit(f"FAIL: anchor for '{label}' not unique ({src.count(anchor)}). Nothing written.")
        src = src.replace(anchor, replacement, 1)
        applied.append(label)

    if src == original:
        print("Already fully patched — no changes. No-op.")
        return

    try:
        ast.parse(src)
    except SyntaxError as e:
        sys.exit(f"FAIL: patched source does not parse ({e}). Nothing written.")

    backup = TARGET.with_suffix(".py.pre_audio_trueup")
    if not backup.exists():
        shutil.copy2(TARGET, backup)
        print(f"Backed up original -> {backup.name}")
    TARGET.write_text(src)
    print(f"OK wrote {TARGET.name} (compiles). Applied: {', '.join(applied)}")


if __name__ == "__main__":
    main()
