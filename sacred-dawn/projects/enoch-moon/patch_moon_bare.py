#!/usr/bin/env python3
"""
patch_moon_bare.py -- make the empty-moon beat 8/2 render bare.

8/2 says "bare, unbuilt, nothing cut into it" but rendered WITH shafts (probe
shot_019), because it lacks the explicit negative list its sibling 8/7 carries
("no openings, no windows, no courses"). 8/7 renders bare; 8/2 gets the same
clause. One beat. Edits phenomenon only; run `build_moon.py normalise` after.

Idempotent, anchor-verified, .pre_<ts> backup, ASCII. Run from enoch-moon dir.
"""
import csv, time
from pathlib import Path

TARGET = Path("beats/moon_master.csv")

OLD = ("grey crater fields running limb to limb, bare, unbuilt, nothing cut into it "
       "anywhere -- and the raw sun hard beyond the limb.")
NEW = ("grey crater fields running limb to limb, bare, unbuilt, no openings, no windows, "
       "no shafts, no courses, nothing cut into it anywhere -- and the raw sun hard "
       "beyond the limb.")


def die(msg):
    print("PATCH ABORTED: " + msg)
    raise SystemExit(1)


def main():
    if not TARGET.exists():
        die("beats/moon_master.csv not found. Run from the enoch-moon project dir.")
    rows = list(csv.DictReader(TARGET.open()))
    fields = list(rows[0].keys())
    row = next((r for r in rows if (r["block_id"], r["clip_index"]) == ("8", "2")), None)
    if row is None:
        die("beat 8/2 not found.")
    cell = row["phenomenon"]
    if NEW in cell:
        print("Already applied (8/2 carries the no-openings clause). No change.")
        return
    if OLD not in cell:
        die("anchor not found in 8/2 -- text is not what was expected. No write.")

    row["phenomenon"] = cell.replace(OLD, NEW, 1)
    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts)
    backup.write_text(TARGET.read_text())
    with TARGET.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("Patched beats/moon_master.csv (beat 8/2)")
    print("  backup: %s" % backup.name)
    print("  NEXT: python3 build_moon.py normalise")


if __name__ == "__main__":
    main()
