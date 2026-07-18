#!/usr/bin/env python3
"""
patch_probe20.py -- add the 20-beat, 8-block register probe to build_moon.py.

Idempotent. Verifies every anchor before writing, backs up to build_moon.py.pre_<ts>,
compile-checks the result in memory, and only then writes. ASCII only. Run from the
enoch-moon project dir (where build_moon.py lives):  python3 patch_probe20.py

The probe renders ONE still per slot through the existing cmd_probe/shot_NNN path --
variants are NOT consumed here, which is correct: this samples register and gravity
wells across the axis, it does not test the pick. 20 stills, $1.60.
"""
import sys, time
from pathlib import Path

TARGET = Path("build_moon.py")

MARKER = "PROBE20 = ["

PROBE20_BLOCK = '''PROBE20 = [
    # (block, clip_index, rule, verdict question -- WRITTEN BEFORE IT RENDERS)
    # 8 blocks, 20 slots: cosmic canary + earthly canary per block, + 4 door/novel.
    (1,  1, "canary-cosmic",  "Six ranked openings COUNTABLE over the limb, or texture? Limb anchors planetary?"),
    (1, 19, "canary-earthly", "Page BRIGHT highland daylight, Ge'ez legible not garbled, no stamped murk?"),
    (1,  5, "known-failure",  "ONE opening edge-on -- crater field + horizon anchor it PLANETARY, or reads as a door?"),
    (2,  1, "canary-cosmic",  "Ranked openings ordered over the curve, sun mass at the limb -- countable, not abstract?"),
    (2, 12, "canary-earthly", "Two pages side by side BRIGHT, ruled columns crisp, no dim or sepia drift?"),
    (3,  1, "canary-cosmic",  "Even spacing + count hold, or do the openings smear into rock texture?"),
    (3, 27, "canary-earthly", "Numerals legible in raking perspective, page BRIGHT, no murk in the recession?"),
    (3, 11, "known-failure",  "The ROW reads as the scale anchor -- planetary, not a lone lit doorway?"),
    (4,  9, "canary-cosmic",  "Earth in frame -- deliberate earthrise, or does {heavens} 'no earth' fight it into a smear?"),
    (4, 15, "canary-earthly", "Foreground page BRIGHT and sharp AND the opening beyond legible -- depth holds?"),
    (4,  8, "known-failure",  "Nothing-beyond-but-black -- does the ROW past it save it from reading as a door/void?"),
    (5,  1, "canary-cosmic",  "Dust streaming reads as AIR in motion (Kling-worthy), field bright, mass not vapour?"),
    (5,  5, "canary-earthly", "Repeated Ge'ez word legible + BRIGHT, controlled shadow -- not murk swallowing the page?"),
    (5,  9, "novel",          "{winds} torrent reads bright and PHYSICAL -- air, not a grey smoke prop; land bright?"),
    (6,  3, "canary-cosmic",  "Immense + countable to a HARD black horizon -- no vapour softening the limb?"),
    (6,  8, "canary-earthly", "First ruled line crisp + BRIGHT, focus falloff clean -- not dim or muddy below?"),
    (7,  1, "canary-cosmic",  "Twelve countable limb to limb, ordered -- the money frame; texture = FAIL?"),
    (7,  3, "canary-earthly", "Four Ge'ez repeats legible + BRIGHT, columns even -- no murk between them?"),
    (8,  2, "canary-cosmic",  "BARE moon reads as the same world now empty -- continuity with the built frames, still bright?"),
    (8, 21, "canary-earthly", "Hand + book physical and BRIGHT, section legible -- no dim or reverent drift?"),
]


'''

PROBE20_FUNC = '''def cmd_probe20():
    cmd_probe(PROBE20, "moon-probe20-finish", "PROBE20-CARD.md")


'''

DISPATCH_LINE = '    elif cmd == "probe20": cmd_probe20()\n'

ANCHOR_CONST = "def check_tokens(text: str, where: str) -> None:\n"
ANCHOR_FUNC = "def cmd_film(argv):\n"
ANCHOR_DISPATCH = '    elif cmd == "probe7": cmd_probe7()\n'


def die(msg):
    print("PATCH ABORTED: " + msg)
    raise SystemExit(1)


def main():
    if not TARGET.exists():
        die("build_moon.py not found in cwd. Run from the enoch-moon project dir.")

    src = TARGET.read_text()

    if MARKER in src:
        print("Already applied (PROBE20 present). No change.")
        return

    for name, anchor, n in (
        ("const", ANCHOR_CONST, 1),
        ("func", ANCHOR_FUNC, 1),
        ("dispatch", ANCHOR_DISPATCH, 1),
    ):
        found = src.count(anchor)
        if found != n:
            die("anchor '%s' found %d times, expected %d. File not the expected build_moon.py."
                % (name, found, n))

    new = src.replace(ANCHOR_CONST, PROBE20_BLOCK + ANCHOR_CONST, 1)
    new = new.replace(ANCHOR_FUNC, PROBE20_FUNC + ANCHOR_FUNC, 1)
    new = new.replace(ANCHOR_DISPATCH, ANCHOR_DISPATCH + DISPATCH_LINE, 1)

    if not new.isascii():
        die("result contains non-ASCII bytes.")

    try:
        compile(new, str(TARGET), "exec")
    except SyntaxError as e:
        die("compile check failed: %s" % e)

    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts)
    backup.write_text(src)
    TARGET.write_text(new)
    print("Patched build_moon.py")
    print("  backup: %s" % backup.name)
    print("  added:  PROBE20 (20 slots), cmd_probe20(), dispatch 'probe20'")
    print("  run:    python3 build_moon.py probe20   -> moon-probe20-finish/beats.json ($1.60)")


if __name__ == "__main__":
    main()
