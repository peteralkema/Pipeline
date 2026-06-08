#!/usr/bin/env python3
"""
diagnose_conform.py — measure the ACTUAL conformed-segment duration vs the INTENDED
duration, by re-running the real make_video_segment ffmpeg command on sample beats.

WHY: the first diagnostic (diagnose_drift.py) wrongly measured the RAW pooled clips in
clips/ (all ~5s — the inputs, not the conformed output). The real video is full-length,
but Filmora evidence shows audio runs AHEAD of video by a cumulatively growing amount
(~3s @ beat32, ~9s @ beat70, ~32s @ beat114) — i.e. the conformed VIDEO segments are
each slightly LONGER than their intended duration, and it piles up. This script measures
the conform output directly to confirm and quantify the per-beat overshoot.

It reproduces make_video_segment's Mode A slow-fill command EXACTLY:
   vf = setpts=PTS*factor, scale, pad, setsar, fps        (+ -t dur)
then probes the actual output duration and reports intended vs actual vs overshoot.

READ-ONLY w.r.t. the project — writes temp files to a scratch dir it cleans up.

Usage:
  python3 shared/diagnose_conform.py --project final-hours/projects/troy
  python3 shared/diagnose_conform.py --project final-hours/projects/troy --beats 1,32,70,114,141 --all
"""
import os, sys, json, argparse, subprocess, tempfile, shutil
from pathlib import Path

FPS = 30


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def conform_modea(src, dur, W, H, work, i):
    """EXACT replica of make_video_segment's Mode A slow-fill path."""
    dst = work / f"v_{i:03d}.mp4"
    native = probe(src)
    scale_pad = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                 f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS}")
    if native >= dur:
        vf = scale_pad
        cmd = ["ffmpeg", "-y", "-i", str(src), "-t", f"{dur:.3f}", "-vf", vf,
               "-c:v", "libx264", "-preset", "medium", "-crf", "18",
               "-pix_fmt", "yuv420p", "-an", str(dst)]
        mode = "trim"
    else:
        factor = dur / native
        vf = f"setpts=PTS*{factor:.6f},{scale_pad}"
        cmd = ["ffmpeg", "-y", "-i", str(src), "-vf", vf, "-t", f"{dur:.3f}",
               "-c:v", "libx264", "-preset", "medium", "-crf", "18",
               "-pix_fmt", "yuv420p", "-an", str(dst)]
        mode = f"slow-fill x{factor:.2f}"
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return None, native, mode, (r.stderr or "").strip().splitlines()[-3:]
    return dst, native, mode, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--beats", default="1,32,70,114,141",
                    help="comma-separated beat indices to test (default: the ones from Filmora)")
    ap.add_argument("--all", action="store_true",
                    help="conform EVERY beat and sum actual vs intended (slow but definitive)")
    args = ap.parse_args()

    proj = Path(args.project)
    durations = json.load(open(proj / "durations.json", encoding="utf-8"))
    index = json.load(open(proj / "_index.json", encoding="utf-8"))
    rev = {int(b): int(s) for s, b in index.items()}
    source_dir = proj / "modea" / "clips"
    voice = probe(proj / "voiceover.mp3")
    W, H = args.width, args.height

    keys = sorted(durations, key=lambda x: int(x))
    if args.all:
        test = [int(k) for k in keys]
    else:
        test = [int(x) for x in args.beats.split(",")]

    work = Path(tempfile.mkdtemp(prefix="conform_diag_"))
    print(f"\n=== conform diagnosis: {proj} ===")
    print(f"voiceover: {voice:.2f}s   testing {len(test)} beat(s)   {W}x{H}@{FPS}\n")
    hdr = f"{'beat':>4} {'shot':>4} {'intended':>9} {'native':>7} {'ACTUAL':>8} {'overshoot':>9}  mode"
    print(hdr); print("-" * len(hdr))

    sum_int = 0.0; sum_act = 0.0; sum_over = 0.0; n = 0
    try:
        for idx in test:
            k = str(idx)
            if k not in durations:
                continue
            d = durations[k]
            intended = float(d.get("duration", 0.0))
            shot = rev.get(idx)
            if shot is None:
                continue
            src = source_dir / f"shot_{shot:03d}.mp4"
            if not src.exists():
                print(f"{idx:>4} {shot:>4}  (source clip missing: {src})")
                continue
            dst, native, mode, err = conform_modea(src, intended, W, H, work, idx)
            if dst is None:
                print(f"{idx:>4} {shot:>4}  CONFORM FAILED: {err}")
                continue
            actual = probe(dst)
            over = actual - intended
            sum_int += intended; sum_act += actual; sum_over += over; n += 1
            if not args.all or idx in (int(x) for x in "1,32,70,114,141".split(",")) or idx % 15 == 0 or idx >= len(keys)-3:
                print(f"{idx:>4} {shot:>4} {intended:>9.3f} {native:>7.3f} {actual:>8.3f} {over:>+9.3f}  {mode}")
            # clean each temp file as we go to avoid filling disk on --all
            try: os.remove(dst)
            except OSError: pass

        print("\n--- summary ---")
        print(f"beats tested: {n}")
        print(f"mean overshoot/beat = {sum_over/n:+.4f}s   (sum tested overshoot = {sum_over:+.2f}s)")
        if args.all:
            print(f"sum(intended) = {sum_int:.2f}s   sum(ACTUAL conformed) = {sum_act:.2f}s   "
                  f"diff = {sum_act - sum_int:+.2f}s")
            print(f"voice = {voice:.2f}s")
            print(f"\n  => if sum(ACTUAL) >> voice, the video LAGS the audio by that much,")
            print(f"     absorbed only by the tiny tail beats. Predicted Filmora drift ~= {sum_act - sum_int:+.0f}s.")
        else:
            est = (sum_over / n) * len(keys)
            print(f"\n  per-beat overshoot x {len(keys)} beats => est. total drift ~= {est:+.1f}s")
            print(f"  (compare to Filmora: audio ~32s ahead of video by beat 114.)")
        print("\n  Positive overshoot = conformed clip LONGER than intended = video lags audio (matches Filmora).")
        print("  Likely cause: setpts slowdown + fps resample overruns the -t cut. Fix: force exact")
        print("  output duration/frame-count (e.g. -t applied to OUTPUT, or build to round(dur*FPS) frames).")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
