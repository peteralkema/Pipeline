#!/usr/bin/env python3
"""
reassemble_static.py - rebuild final_video as TRUE-STATIC (zero Ken-Burns).

Ken-Burns motion is baked into each modea/clips/shot_NNN.mp4 (the zoompan was
applied at clip-generation). The stills (modea/stills/shot_NNN.png) are clean.
Each existing clip already carries the correct per-beat duration (from Whisper
alignment), so we don't need any timing file: we read each clip's duration,
hold the matching still frozen for exactly that long, concat all beats, and mux
the existing voiceover.

No fal spend. Pure ffmpeg. Outputs final_video_static.mp4 alongside the original
final_video.mp4 so they can be A/B compared. Non-destructive.

This is the throwaway/seed version of Patch B (true-static in the pipeline).
If static reads right over long form, graduate it into _still_to_held_clip as a
--static flag next session.

Run on BOX in the venv:  python shared/reassemble_static.py --project crew-wip/projects/soap-full
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True,
                    help="project dir, e.g. crew-wip/projects/soap-full")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--out", default="final_video_static.mp4")
    args = ap.parse_args()

    proj = Path(args.project).resolve()
    stills_dir = proj / "modea" / "stills"
    clips_dir = proj / "modea" / "clips"
    voiceover = proj / "voiceover.mp3"
    out_path = proj / args.out

    for p in (stills_dir, clips_dir, voiceover):
        if not p.exists():
            sys.exit(f"missing: {p}")

    # enumerate beats from the clips (they hold the authoritative durations)
    clips = sorted(clips_dir.glob("shot_*.mp4"))
    if not clips:
        sys.exit(f"no clips in {clips_dir}")
    print(f"found {len(clips)} clips")

    work = Path(tempfile.mkdtemp(prefix="static_reassemble_"))
    concat_list = work / "concat.txt"
    seg_paths = []

    vf = (f"scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
          f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:color=black,"
          f"setsar=1,fps={args.fps}")

    total = 0.0
    for clip in clips:
        stem = clip.stem  # shot_001
        still = stills_dir / f"{stem}.png"
        if not still.exists():
            sys.exit(f"missing still for {stem}: {still}")
        dur = probe_duration(clip)
        total += dur
        seg = work / f"{stem}_static.mp4"
        # frozen still held for exactly `dur`, no zoompan, silent
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-loop", "1", "-i", str(still),
             "-t", f"{dur:.6f}",
             "-vf", vf,
             "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-r", str(args.fps),
             str(seg)],
            check=True,
        )
        seg_paths.append(seg)
        print(f"  {stem}  {dur:5.2f}s  static", flush=True)

    concat_list.write_text("".join(f"file '{p}'\n" for p in seg_paths))
    print(f"\nconcat {len(seg_paths)} segments, total video {total:.2f}s")

    # concat all static segments, then mux the existing voiceover.
    silent = work / "video_silent.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c", "copy", str(silent)],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-i", str(silent), "-i", str(voiceover),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-map", "0:v:0", "-map", "1:a:0",
         "-shortest", str(out_path)],
        check=True,
    )

    vdur = probe_duration(out_path)
    adur = probe_duration(voiceover)
    print(f"\nwrote {out_path}")
    print(f"  video duration: {vdur:.2f}s  |  voiceover: {adur:.2f}s  |  delta {abs(vdur-adur):.3f}s")
    if abs(vdur - adur) > 1.0:
        print("  WARNING: >1s drift between video and voiceover -- check beat durations")
    else:
        print("  OK durations aligned")
    print(f"\n  (scratch dir {work} -- safe to delete)")


if __name__ == "__main__":
    main()
