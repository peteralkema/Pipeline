#!/usr/bin/env python3
"""
assemble_test.py - Step 4a of the Synthetic dual-mode pipeline.

Proves the ASSEMBLE step accepts a Mode B clip sitting between Mode A clips,
in order, as one continuous MP4. This is a PLUMBING test, not an episode:
the Mode A beats are stand-in solid-colour clips (ffmpeg, free, instant),
because their content is irrelevant here - we are testing that mixed-source
clips concatenate cleanly at matching resolution/fps with no seam artifacts.

What it does:
  1. For a small slice of beats (default 26,27,28), build a clip per beat:
       - Mode A  -> generate a labelled solid-grey placeholder via ffmpeg
       - Mode B  -> use the REAL rendered clip if present in clips/, else a
                    coloured placeholder so the test still runs end to end
  2. Concatenate them in beat order into one timeline.mp4
  3. Report duration and that the B clip landed in the middle.

Real-footage note: in the real pipeline these A placeholders are replaced by
render_mode_a() calling the existing stills->Kling path. The assemble logic
here is exactly what stays.

Usage:
  python3 assemble_test.py /tmp/ep1_beats.json --slice 26,27,28
  python3 assemble_test.py /tmp/ep1_beats.json --slice 26,27,28 --run   # actually ffmpeg
"""
import os, sys, json, argparse, subprocess

FPS = 30
W, H = 1920, 1080
CLIPS_DIR = os.path.abspath("clips")
OUT = os.path.abspath("clips/timeline_4a.mp4")

def estimate_frames(beat):
    text = beat.get("narration") or beat.get("found_line") or ""
    words = len(text.split())
    secs = max(1.5, words/135*60) if words else (3.0 if beat["mode"]=="B" else 2.5)
    if beat.get("silence_after"): secs += 1.5
    return round(secs*FPS)

def placeholder_cmd(path, seconds, label, color):
    # duration INSIDE the filter via d= (a color source with no d= is infinite,
    # which errors); hex colors so the name parser can't reject them.
    return [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={color}:s={W}x{H}:d={seconds:.2f}",
        "-r", str(FPS),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        path,
    ]

def build_clip_for(beat, run):
    idx, mode = beat["index"], beat["mode"]
    frames = estimate_frames(beat); secs = frames/FPS
    if mode == "B":
        real = os.path.join(CLIPS_DIR, f"beat_{idx:02d}_B_{beat['component']}.mp4")
        if os.path.exists(real):
            print(f"  [{idx:02d}] B  REAL clip  {os.path.basename(real)}")
            return real, True
        path = os.path.join(CLIPS_DIR, f"ph_{idx:02d}_B.mp4")
        label = f"[B placeholder] {beat.get('component','')}"
        color = "0x0a1628"
    else:
        path = os.path.join(CLIPS_DIR, f"ph_{idx:02d}_A.mp4")
        label = f"[A placeholder] beat {idx}"
        color = "0x222222"
    print(f"  [{idx:02d}] {mode}  placeholder ({secs:.1f}s)  {label}")
    if run:
        r = subprocess.run(placeholder_cmd(path, secs, label, color),
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("     !! ffmpeg FAILED building placeholder:")
            print("       ", (r.stderr.strip().splitlines()[-1] if r.stderr else "?"))
            return None, False
        if not os.path.exists(path):
            print("     !! placeholder not written:", path)
            return None, False
    return path, False

def assemble(clip_paths, run):
    # concat via ffmpeg demuxer (re-encode to be safe across mixed sources)
    listfile = os.path.join(CLIPS_DIR, "concat_4a.txt")
    if run:
        with open(listfile,"w") as f:
            for p in clip_paths: f.write(f"file '{p}'\n")
        cmd = ["ffmpeg","-y","-f","concat","-safe","0","-i",listfile,
               "-c:v","libx264","-pix_fmt","yuv420p","-r",str(FPS), OUT]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("!! concat failed:", r.stderr.strip().splitlines()[-1] if r.stderr else "?")
            return None
    else:
        print("  (dry-run) would concat in order:")
        for p in clip_paths: print("    ", os.path.basename(p))
    return OUT

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("beats_json")
    ap.add_argument("--slice", default="26,27,28", help="comma-separated beat indices, in order")
    ap.add_argument("--run", action="store_true", help="actually run ffmpeg (default dry-run)")
    args = ap.parse_args()
    beats = {b["index"]: b for b in json.load(open(args.beats_json, encoding="utf-8"))}
    want = [int(x) for x in args.slice.split(",")]
    os.makedirs(CLIPS_DIR, exist_ok=True)

    print(f"\n=== Step 4a assemble test: beats {want} ===\n")
    clips, used_real_b = [], False
    for i in want:
        if i not in beats:
            print(f"  !! beat {i} not in beats.json"); continue
        path, is_real = build_clip_for(beats[i], args.run)
        if path:
            clips.append(path)
        elif args.run:
            print(f"  !! beat {i} produced no clip — aborting so we don't assemble a partial timeline.")
            sys.exit(1)
        if is_real: used_real_b = True

    print(f"\n  timeline order: {[os.path.basename(c) for c in clips]}")
    out = assemble(clips, args.run)
    print("\n" + "="*56)
    if args.run and out and os.path.exists(out):
        # probe duration
        try:
            d = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                                "-of","default=nw=1:nk=1", out], capture_output=True, text=True)
            dur = float(d.stdout.strip()) if d.stdout.strip() else 0
            print(f"OK  -> {out}  ({dur:.1f}s, {len(clips)} clips)")
        except Exception:
            print(f"OK  -> {out}  ({len(clips)} clips)")
        print(f"Mode B clip in middle was {'the REAL render' if used_real_b else 'a placeholder'}.")
    else:
        print("dry-run complete. add --run to actually build timeline_4a.mp4")
        print("(needs ffmpeg; on the laptop you have it. The real beat-27 B clip will be")
        print(" used automatically if clips/beat_27_B_NumberCounter.mp4 exists.)")

if __name__ == "__main__":
    main()
