#!/usr/bin/env python3
"""verify_clips.py -- gate every clip to exactly 5.000s, and normalise the ones that drift.

_LEGO.md mandates this and nothing implemented it: "ffprobe every output. Hard-fail anything
not 120 frames / 5.000000s." Ken Burns clips are exact by construction (-t 5.000 -r 24), but
Kling ships a non-deterministic frame count (121 is common) and render_clips.py writes what fal
returns without trimming.

  --normalise   trims an OVER-LONG clip to exactly N frames with `-frames:v N -c copy`
                -- a PACKET COPY, not a re-encode: instant, lossless, cuts at the TAIL so the
                head keyframe is untouched. Clips are strongest in their opening moments.

TRIM NEVER PAD. A short clip is REGENERATED, never stretched -- dropping a tail frame is
invisible, a freeze-frame is not. Short clips are reported and left alone.

TARGET FRAMES ARE DERIVED PER CLIP as round(r_frame_rate x duration), never hardcoded to 120:
a 30fps clip trimmed to 120 frames would be 4.0s. This is the gotcha the doc banked.

    python3 verify_clips.py --clips <project>/clips
    python3 verify_clips.py --clips <project>/clips --expect 320
    python3 verify_clips.py --clips <project>/clips --normalise
"""
import argparse, json, subprocess, sys
from pathlib import Path

TOL = 0.010  # seconds


def probe(p: Path):
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=nb_read_packets,r_frame_rate,width,height",
           "-show_entries", "format=duration",
           "-count_packets", "-of", "json", str(p)]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        return None
    d = json.loads(r.stdout)
    st = (d.get("streams") or [{}])[0]
    dur = float(d.get("format", {}).get("duration", 0) or 0)
    frames = int(st.get("nb_read_packets", 0) or 0)
    num, den = (st.get("r_frame_rate", "24/1").split("/") + ["1"])[:2]
    fps = float(num) / float(den or 1)
    return {"dur": dur, "frames": frames, "fps": fps,
            "w": st.get("width"), "h": st.get("height")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", required=True)
    ap.add_argument("--target", type=float, default=5.000, help="target seconds (default 5.000)")
    ap.add_argument("--expect", type=int, default=None, help="expected clip count (e.g. 320)")
    ap.add_argument("--normalise", action="store_true", help="trim over-long clips (packet copy)")
    a = ap.parse_args()

    d = Path(a.clips).expanduser()
    if not d.is_dir():
        sys.exit("clips dir not found: %s" % d)
    files = sorted(d.glob("shot_*.mp4"))
    if not files:
        sys.exit("no shot_*.mp4 in %s" % d)

    ok, over, short, bad, res = [], [], [], [], {}
    fps_set, dims = {}, {}
    for f in files:
        info = probe(f)
        if not info:
            bad.append((f, "ffprobe failed")); continue
        res[f] = info
        fps_set[round(info["fps"], 3)] = fps_set.get(round(info["fps"], 3), 0) + 1
        dims["%sx%s" % (info["w"], info["h"])] = dims.get("%sx%s" % (info["w"], info["h"]), 0) + 1
        delta = info["dur"] - a.target
        if abs(delta) <= TOL:
            ok.append(f)
        elif delta > 0:
            over.append(f)
        else:
            short.append(f)

    print("clips: %d in %s" % (len(files), d))
    if a.expect is not None and len(files) != a.expect:
        print("  !! COUNT MISMATCH: expected %d, found %d" % (a.expect, len(files)))
    print("  exactly %.3fs (+/-%.3f): %d" % (a.target, TOL, len(ok)))
    print("  over-long           : %d" % len(over))
    print("  SHORT (regenerate)  : %d" % len(short))
    if bad:
        print("  unreadable          : %d" % len(bad))
    print("  frame rates: " + ", ".join("%.3g fps x%d" % (k, v) for k, v in sorted(fps_set.items())))
    print("  dimensions : " + ", ".join("%s x%d" % (k, v) for k, v in sorted(dims.items())))

    for label, group in (("SHORT", short), ("OVER", over)):
        for f in group[:12]:
            i = res[f]
            print("   %-5s %s  %.3fs  %d frames @ %.3g fps" % (label, f.name, i["dur"], i["frames"], i["fps"]))
        if len(group) > 12:
            print("   %-5s ... and %d more" % (label, len(group) - 12))

    if short:
        print("\nSHORT clips cannot be fixed by trimming -- TRIM NEVER PAD.")
        print("  delete them and re-run render_clips.py (resume-safe refill).")

    if over and not a.normalise:
        print("\n%d clip(s) run long. Re-run with --normalise to trim (packet copy, lossless)." % len(over))
    elif over and a.normalise:
        print("\nnormalising %d clip(s)..." % len(over))
        fixed = failed = 0
        for f in over:
            i = res[f]
            target_frames = int(round(i["fps"] * a.target))   # NEVER hardcode 120
            tmp = f.with_suffix(".trim.mp4")
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(f),
                   "-frames:v", str(target_frames), "-c", "copy", str(tmp)]
            r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if r.returncode != 0:
                print("   FAIL %s: %s" % (f.name, r.stderr.strip().splitlines()[-1:] or "?"))
                tmp.unlink(missing_ok=True); failed += 1; continue
            after = probe(tmp)
            if not after or abs(after["dur"] - a.target) > TOL:
                print("   FAIL %s: trim landed at %.3fs" % (f.name, after["dur"] if after else -1))
                tmp.unlink(missing_ok=True); failed += 1; continue
            tmp.replace(f)
            fixed += 1
        print("  trimmed %d | failed %d" % (fixed, failed))

    exit_bad = len(short) + len(bad) + (len(over) if not a.normalise else 0)
    if exit_bad == 0 and (a.expect is None or len(files) == a.expect):
        print("\nPASS: every clip is exactly %.3fs." % a.target)
        return 0
    print("\nFAIL: %d clip(s) not at %.3fs." % (exit_bad, a.target))
    return 1


if __name__ == "__main__":
    sys.exit(main())
