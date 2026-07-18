#!/usr/bin/env python3
"""
patch_moon_openings.py -- fix the opening-geometry gravity wells surfaced by the
20-beat probe, film-wide and setting-aware (FLAGS #3: probe discovers, sweep fixes).

Four transforms, applied ONLY where the canon token makes the text wrong:
  1. RETAG (9 beats): {heavens} -> {limb} on beats that author a distant earth.
     {heavens} forbids earth; {limb} permits it. b4/9 also gets its moon darkened
     to match its own narration ("the whole moon completely dark -- a shell").
  2. DOOR-WELL (4 heavens beats): "light through the opening" -> light down into /
     up out of square SHAFTS cut into the surface. Chapel "through the opening"
     beats are window light and are left alone.
  3. JAMB (9 heavens beats): doorframe vocab "jamb" -> "cut rim / shaft rim".
  4. NIGHT (b4/15): the drifted night sky -> a pale daytime moon, daylight reasserted.

Each edit is a targeted substring op, idempotent: applies if the OLD text is present,
skips if the NEW text is already there, aborts loudly if neither (anchor mismatch).
Edits ONLY the phenomenon column. Run `build_moon.py normalise` AFTER this to
recompute the derived `setting` column for the retagged beats.

Backs up to moon_master.csv.pre_<ts>. ASCII only. Run from enoch-moon project dir.
"""
import csv, time
from pathlib import Path

TARGET = Path("beats/moon_master.csv")

# (block, clip) -> list of (old_substring, new_substring)
EDITS = {
    # ---- RETAG {heavens} -> {limb} (earth authored against a no-earth token) ----
    ("5", "20"): [("{heavens}.", "{limb}.")],
    ("6", "10"): [("{heavens}.", "{limb}.")],
    ("7", "7"):  [("{heavens}.", "{limb}.")],
    ("7", "21"): [("{heavens}.", "{limb}.")],
    ("7", "26"): [("{heavens}.", "{limb}.")],
    ("7", "34"): [("{heavens}.", "{limb}.")],
    ("7", "40"): [("{heavens}.", "{limb}.")],
    ("8", "12"): [("{heavens}.", "{limb}.")],
    ("4", "9"): [
        ("{heavens}.", "{limb}."),
        ("the entire curve of the moon, ranked openings limb to limb, every one black -- and the bright curve of the earth small and far beyond it, the only lit thing in the sky. Blazing raw sunlight on bare rock, black openings, black space.",
         "the entire curve of the moon in shadow, ranked openings limb to limb, the whole sphere dark and unlit -- and the bright curve of the earth small and far beyond it, the only lit thing in the frame. Faint raw sunlight grazing the limb, the moon dark, black openings, black space."),
    ],
    # ---- DOOR-WELL: light through opening -> shafts cut into the surface ----
    ("1", "1"): [
        ("six colossal square openings cut into the lunar rock in one ranked row, countable, running away over the curve -- and the raw white sun cresting the limb hard behind them, its light standing through every opening in visible shafts of dust. Overwhelming raw sunlight, deep black shadow, black star-scattered space.",
         "six colossal square shafts cut down into the lunar rock in one ranked row, countable, running away over the curve -- and the raw white sun cresting the limb hard behind them, its light raking low across the surface and pouring down into every open shaft, striking the cut stone floor and inner walls. Overwhelming raw sunlight, deep black shadow inside the shafts, black star-scattered space. Openings sunk into the ground, no door, no frame, no lintel."),
    ],
    ("4", "31"): [
        ("the western rank, raw light breaking outward through the openings into black space, the crater field behind falling into hard shadow. Blazing raw light in the openings, deep black shadow.",
         "the western rank of square shafts cut down into the surface, raw light standing up out of each shaft in a hard column, the crater field behind falling into hard shadow. Blazing raw light in the shafts, deep black shadow. Shafts sunk into the rock, no door, no frame."),
    ],
    ("5", "18"): [
        ("the western rank with raw light breaking outward through the openings, the crater field beyond already falling into hard shadow, the dust still streaming. Blazing raw light, deep black shadow, brilliant dust.",
         "the western rank of square shafts cut into the surface, raw light standing up out of each in a hard column, the crater field beyond already falling into hard shadow, the dust still streaming. Blazing raw light, deep black shadow, brilliant dust. Shafts sunk into the rock, no door, no frame."),
    ],
    ("6", "12"): [
        ("the western rank with raw white light breaking outward through every opening at once, ordered, exact, unattended, nothing moving. Blazing raw light, deep black shadow.",
         "the western rank of square shafts, raw white light standing up out of every one at once in ordered hard columns, exact, unattended, nothing moving. Blazing raw light, deep black shadow. Shafts sunk into the rock, no door, no frame."),
    ],
    # ---- JAMB -> cut rim / shaft rim ----
    ("1", "5"): [
        ("One opening seen edge-on, its span wider than the whole crater field behind it, its far jamb lost over the horizon. Hard raw sunlight, the near jamb blazing, black space above.",
         "One square shaft seen edge-on, its span wider than the whole crater field behind it, its far cut rim lost over the horizon, the ranked row continuing past it. Hard raw sunlight, the near cut rim blazing, black space above. A pit cut down into the rock, no door, no frame."),
    ],
    ("4", "8"): [
        ("Tight at one opening, the row running past it: the jamb blazing at the rim and nothing beyond it but black, no floor, no far wall. Overwhelming raw sunlight on the rim, absolute black inside.",
         "Tight at one shaft's cut rim, the ranked row running past it: the rim blazing and the square shaft dropping into black below, no floor visible, cut walls falling away. Overwhelming raw sunlight on the rim, absolute black inside the shaft. A pit cut down into the rock, no door, no frame."),
    ],
    ("1", "18"): [("the cut stone of one jamb", "the cut stone of one shaft rim")],
    ("2", "10"): [("the cut stone of one jamb", "the cut stone of one shaft rim")],
    ("3", "2"): [
        ("a second ranked row of six openings", "a second ranked row of six shafts"),
        ("their jambs receding", "their cut rims receding"),
        ("the near jamb blazing", "the near cut rim blazing"),
    ],
    ("3", "14"): [
        ("the sixth opening still lit", "the sixth shaft still lit"),
        ("off its far jamb", "off its far cut rim"),
    ],
    ("5", "7"): [("Extreme close on one jamb", "Extreme close on one shaft rim")],
    ("6", "34"): [("Extreme close on one jamb", "Extreme close on one shaft rim")],
    ("7", "8"): [("Extreme close on one jamb", "Extreme close on one shaft rim")],
    # ---- SINGLE-OPENING (barest two; add shaft/no-door clause) ----
    ("3", "9"): [
        ("one opening blazing white, the other five in deep black shadow, countable, the limb behind. Raw unfiltered sunlight, hard shadow.",
         "one shaft blazing white, the other five in deep black shadow, countable, the limb behind. Raw unfiltered sunlight, hard shadow. Square shafts cut into the rock, no door, no frame."),
    ],
    ("3", "11"): [
        ("the light one opening further along again, the two behind it black. Raw unfiltered sunlight, hard shadow.",
         "the light one shaft further along again, the two behind it black. Raw unfiltered sunlight, hard shadow. Square shafts cut into the rock, no door, no frame, no mechanism."),
    ],
    # ---- NIGHT DRIFT (b4/15): daylight reasserted ----
    ("4", "15"): [
        ("and beyond it through the high opening, out of focus and enormous, the moon. One brilliant blade of daylight on the page, the moon bright behind.",
         "and beyond it through the high opening, out of focus, the pale moon hanging in a bright daylight sky. One brilliant blade of hard daylight on the page. Hard bright daylight, bright sky, no night, no darkness."),
    ],
}


def die(msg):
    print("PATCH ABORTED: " + msg)
    raise SystemExit(1)


def main():
    if not TARGET.exists():
        die("beats/moon_master.csv not found. Run from the enoch-moon project dir.")

    rows = list(csv.DictReader(TARGET.open()))
    fields = list(rows[0].keys())
    index = {(r["block_id"], r["clip_index"]): r for r in rows}

    changed = 0
    already = 0
    fails = []
    for (b, c), ops in EDITS.items():
        row = index.get((b, c))
        if row is None:
            fails.append("beat %s/%s not found" % (b, c))
            continue
        cell = row["phenomenon"]
        for old, new in ops:
            if old in cell:
                cell = cell.replace(old, new, 1)
            elif new in cell:
                already += 1
            else:
                fails.append("beat %s/%s: anchor not found -> %r" % (b, c, old[:40]))
        if cell != row["phenomenon"]:
            row["phenomenon"] = cell
            changed += 1

    if fails:
        print("\n".join("  ANCHOR FAIL: " + f for f in fails))
        die("%d anchor mismatch(es) -- CSV is not the expected text. No write." % len(fails))

    if changed == 0:
        print("Already applied (all edits present). No change.")
        return

    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts)
    backup.write_text(TARGET.read_text())
    with TARGET.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("Patched beats/moon_master.csv")
    print("  backup: %s" % backup.name)
    print("  beats changed: %d  (ops already-present: %d)" % (changed, already))
    print("  NEXT: python3 build_moon.py normalise   (recomputes setting for the {limb} retags)")


if __name__ == "__main__":
    main()
