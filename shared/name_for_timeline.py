#!/usr/bin/env python3
"""
name_for_timeline.py -- build ONE folder that drags into Filmora in exact order.

    timeline/b00-01.mp4 .. b00-10.mp4    the cold open, in RUNNING order
    timeline/b01-01.mp4 .. b01-40.mp4    block 1
    ...
    timeline/b12-40.mp4                  the last beat
                                         = 490 files, left-to-right on the timeline

The cold open clips are COPIES of film beats renumbered to b00 -- nothing is
re-rendered and nothing extra is charged. Those ten beats therefore appear twice
in the timeline: once at the front, once in their own block position later. That
is normal for a cold open cut from the film's own footage.

Source of truth is master.csv row order: row N -> clips/shot_{N:03d}.mp4.

    cd ~/Pipeline/sacred-dawn/projects/methuselah
    python ~/Pipeline/shared/name_for_timeline.py

Idempotent (re-run overwrites). Hard-fails BEFORE copying anything if a clip is
missing, so it never leaves a half-built folder.
"""
import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

# cold open running order -> flat beat index (see SESSION-NOTES.md section 5)
COLD_OPEN = [294, 295, 419, 304, 362, 301, 236, 240, 128, 163]


def duration(p):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(p)],
            capture_output=True, text=True, timeout=30)
        return float(out.stdout.strip())
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="master.csv")
    ap.add_argument("--clips", default="clips")
    ap.add_argument("--out", default="timeline")
    ap.add_argument("--no-cold-open", action="store_true",
                    help="film blocks only, skip the b00 block")
    ap.add_argument("--check-duration", action="store_true",
                    help="ffprobe every source clip (slow, thorough)")
    args = ap.parse_args()

    csv_path, clips, out = Path(args.csv), Path(args.clips), Path(args.out)
    if not csv_path.exists():
        print("FAIL: %s not found -- run from the PROJECT dir" % csv_path)
        return 1
    if not clips.is_dir():
        print("FAIL: %s/ not found" % clips)
        return 1

    rows = list(csv.DictReader(csv_path.open()))
    n = len(rows)
    print("master: %d beats, %d blocks" % (n, len({r["block_id"] for r in rows})))

    # ---- build the full plan first; copy nothing until it verifies
    plan = []                                    # (src, dest_name)
    if not args.no_cold_open:
        for pos, flat in enumerate(COLD_OPEN, 1):
            if not 1 <= flat <= n:
                print("FAIL: cold-open beat %d is outside 1..%d" % (flat, n))
                return 1
            plan.append((clips / ("shot_%03d.mp4" % flat), "b00-%02d.mp4" % pos))

    for i, r in enumerate(rows, 1):
        dest = "b%02d-%02d.mp4" % (int(r["block_id"]), int(r["clip_index"]))
        plan.append((clips / ("shot_%03d.mp4" % i), dest))

    missing = [str(s) for s, _ in plan if not s.exists()]
    if missing:
        print("FAIL: %d source clip(s) missing -- nothing copied:" % len(missing))
        for m in missing[:20]:
            print("   " + m)
        if len(missing) > 20:
            print("   ... and %d more" % (len(missing) - 20))
        return 1

    dests = [d for _, d in plan]
    if len(dests) != len(set(dests)):
        dup = sorted({d for d in dests if dests.count(d) > 1})
        print("FAIL: duplicate destination names: %s" % dup)
        return 1

    if args.check_duration:
        print("ffprobing %d sources..." % len({s for s, _ in plan}))
        bad = []
        for s in sorted({s for s, _ in plan}):
            d = duration(s)
            if d is None or abs(d - 5.0) > 0.05:
                bad.append((s.name, d))
        if bad:
            print("FAIL: %d clip(s) not 5.000s -- run verify_clips --normalise first:" % len(bad))
            for name, d in bad[:20]:
                print("   %s  %s" % (name, "unreadable" if d is None else "%.3fs" % d))
            return 1
        print("  all sources 5.000s")

    # ---- copy
    out.mkdir(parents=True, exist_ok=True)
    for src, dest in plan:
        shutil.copy2(src, out / dest)

    made = sorted(p.name for p in out.glob("*.mp4"))
    print("\nwrote %d files -> %s/" % (len(made), out))
    print("  first: %s   last: %s" % (made[0], made[-1]))

    # ---- verify the sequence has no gaps
    expected = []
    if not args.no_cold_open:
        expected += ["b00-%02d.mp4" % i for i in range(1, len(COLD_OPEN) + 1)]
    for r in rows:
        expected.append("b%02d-%02d.mp4" % (int(r["block_id"]), int(r["clip_index"])))
    expected.sort()

    if made != expected:
        only_made = set(made) - set(expected)
        only_exp = set(expected) - set(made)
        print("FAIL: folder does not match the plan")
        if only_exp:
            print("  missing: %s" % sorted(only_exp)[:10])
        if only_made:
            print("  unexpected: %s" % sorted(only_made)[:10])
        return 1

    total = len(made)
    print("  sequence COMPLETE, no gaps: b00-01 .. %s" % made[-1])
    print("  timeline length %d x 5s = %d:%02d" % (total, total * 5 // 60, total * 5 % 60))
    print("\nNEXT: pull the folder down and drag it into Filmora as one selection.")
    print("  rsync -avz -e 'ssh -p 443' \\")
    print("    peter@116.202.18.68:%s/ ~/Downloads/methuselah-timeline/" % out.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
