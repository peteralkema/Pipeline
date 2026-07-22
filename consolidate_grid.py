#!/usr/bin/env python3
"""consolidate_grid.py -- fold per-block grid folders into ONE flat-named grid folder.

The pick reviews every still in a single folder, and place.py parses
`^(\\d{1,4})-(\\d+)\\.png$` where group 1 is the FLAT FILM INDEX (1..N) -- the same
number render_clips.py uses for shot_{i:03d}. Per-block names ({clip}-{variant}.png)
repeat across blocks and collide the moment they share a folder.

This moves  <project>/grid-bNN/{clip:03d}-{variant:02d}.png
        ->  <project>/grid/{flat:03d}-{variant:02d}.png
and writes a consolidated GRID-INDEX.csv.

FLAT INDEX IS CSV ROW ORDER, never (block-1)*40+clip -- the formula only agrees when
every block holds exactly 40 rows. This reads master.csv and enumerates, so a short or
long block cannot silently misalign every beat after it.

Validates the ENTIRE mapping (every file maps, no collisions, no orphans) before moving
a single file. Dry-run by default; --apply to move. Idempotent. Pure stdlib.

    python3 consolidate_grid.py --project sacred-dawn/projects/women-in-the-water
    python3 consolidate_grid.py --project ... --apply
"""
import argparse, csv, os, re, sys
from pathlib import Path

GRIDNAME = re.compile(r"^(\d{1,4})-(\d{1,2})\.png$")


def die(msg):
    sys.stderr.write("ABORTED: %s\n" % msg)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="path to the project dir")
    ap.add_argument("--csv", default=None, help="master.csv (default: <project>/master.csv)")
    ap.add_argument("--dest", default="grid", help="destination folder name (default: grid)")
    ap.add_argument("--apply", action="store_true", help="actually move (default: dry-run)")
    a = ap.parse_args()

    proj = Path(a.project).expanduser()
    if not proj.is_dir():
        die("project dir not found: %s" % proj)
    master = Path(a.csv).expanduser() if a.csv else proj / "master.csv"
    if not master.is_file():
        die("master.csv not found: %s" % master)

    rows = list(csv.DictReader(master.open(newline="", encoding="utf-8")))
    if not rows:
        die("master.csv has no rows")
    for col in ("block_id", "clip_index", "weight"):
        if col not in rows[0]:
            die("master.csv missing column: %s" % col)

    # FLAT = CSV row order, not arithmetic
    flat = {}
    for i, r in enumerate(rows, 1):
        key = (int(r["block_id"]), int(r["clip_index"]))
        if key in flat:
            die("duplicate beat in master.csv: block %d clip %d" % key)
        flat[key] = i
    n_beats = len(rows)

    # how many real variants each beat should have (mirrors _stills_render)
    nreal = {}
    for r in rows:
        key = (int(r["block_id"]), int(r["clip_index"]))
        nreal[key] = 4 if r["weight"] == "hero" else 2

    dest = proj / a.dest
    src_dirs = sorted([p for p in proj.iterdir() if p.is_dir() and re.match(r"^grid-b\d+$", p.name)])
    if not src_dirs:
        if dest.is_dir() and any(dest.glob("*.png")):
            print("nothing to do: no grid-bNN dirs, %s already holds %d PNG(s)."
                  % (dest, len(list(dest.glob("*.png")))))
            return
        die("no grid-bNN folders found under %s" % proj)

    plan = []          # (src_path, dest_name, block, clip, variant)
    unmapped = []
    for d in src_dirs:
        m = re.match(r"^grid-b(\d+)$", d.name)
        block = int(m.group(1))
        for f in sorted(d.glob("*.png")):
            mm = GRIDNAME.match(f.name)
            if not mm:
                unmapped.append(str(f)); continue
            clip = int(mm.group(1)); var = int(mm.group(2))
            key = (block, clip)
            if key not in flat:
                unmapped.append("%s (block %d clip %d not in master.csv)" % (f, block, clip))
                continue
            plan.append((f, "%03d-%02d.png" % (flat[key], var), block, clip, var))

    if unmapped:
        die("%d file(s) could not be mapped:\n  %s" % (len(unmapped), "\n  ".join(unmapped[:15])))

    # collision check on the NEW names before touching anything
    seen = {}
    for src, name, b, c, v in plan:
        if name in seen:
            die("collision on %s: %s and %s" % (name, seen[name], src))
        seen[name] = src

    beats_present = sorted({flat[(b, c)] for _, _, b, c, _ in plan})
    missing = [i for i in range(1, n_beats + 1) if i not in set(beats_present)]

    print("project      : %s" % proj)
    print("beats in CSV : %d  (flat 1..%d)" % (n_beats, n_beats))
    print("source dirs  : %d  (%s)" % (len(src_dirs), ", ".join(d.name for d in src_dirs)))
    print("files to move: %d  -> %s/" % (len(plan), dest))
    print("beats covered: %d" % len(beats_present))
    if missing:
        print("WARNING: %d beat(s) have NO stills yet: %s%s"
              % (len(missing), missing[:15], " ..." if len(missing) > 15 else ""))
    ex = [p for p in plan if p[2] == 6 and p[3] == 19][:1] or plan[:1]
    for src, name, b, c, v in ex:
        print("example      : block %d clip %d  ->  flat %d   %s -> %s"
              % (b, c, flat[(b, c)], src.name, name))

    if not a.apply:
        print("\nDRY RUN -- nothing moved. Re-run with --apply.")
        return

    dest.mkdir(parents=True, exist_ok=True)
    moved = skipped = 0
    for src, name, b, c, v in plan:
        dst = dest / name
        if dst.exists():
            skipped += 1; continue
        os.replace(str(src), str(dst))   # same filesystem: instant, no copy
        moved += 1

    with (dest / "GRID-INDEX.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["flat", "block_id", "clip_index", "variant", "kind", "file"])
        for src, name, b, c, v in sorted(plan, key=lambda p: (flat[(p[2], p[3])], p[4])):
            kind = "real" if v <= nreal[(b, c)] else "skip"
            w.writerow([flat[(b, c)], b, c, v, kind, name])

    print("\nOK: moved %d file(s) -> %s  (already present: %d)" % (moved, dest, skipped))
    print("    consolidated index: %s" % (dest / "GRID-INDEX.csv"))
    leftovers = [d for d in src_dirs if any(d.iterdir())]
    if leftovers:
        print("    old dirs still hold non-PNG files (GRID-INDEX.csv): %s"
              % ", ".join(d.name for d in leftovers))
        print("    remove when happy:  rm -rf %s/grid-b*" % proj)


if __name__ == "__main__":
    main()
