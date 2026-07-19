#!/usr/bin/env python3
"""
patch_lego_consolidate.py -- prepend PART I (THE PROCESS & THE DATA) to _LEGO.md.

Makes the process lead the document and installs the beat-CSV column dictionary as
the heart, folding in the session's variant-grid / gravity-well-sweep / Ken-Burns-
moves / project-structure / engine-facts work. The existing craft sections remain
below as PART II. SUPERSEDES the old Section 10 pathway.

Append/prepend-only (no edits to existing craft), idempotent, .pre_<ts> backup, ASCII.
Run from the docs dir, or pass the path:  python3 patch_lego_consolidate.py [_LEGO.md]
Needs _LEGO-PART-I.md in the same dir (or pass it as arg 2).
"""
import sys, time
from pathlib import Path

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_LEGO.md")
PART1 = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("_LEGO-PART-I.md")
MARKER = "THE ARCHITECTURE IN ONE LAW"


def die(m):
    print("PATCH ABORTED: " + m); raise SystemExit(1)


def main():
    if not TARGET.exists():
        die("%s not found." % TARGET)
    if not PART1.exists():
        die("%s not found (needed for the prepend)." % PART1)
    src = TARGET.read_text()
    if MARKER in src:
        print("Already applied (PART I present). No change."); return
    part1 = PART1.read_text()
    if not part1.isascii():
        die("PART I contains non-ASCII bytes.")
    ts = time.strftime("%Y%m%d-%H%M%S")
    TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts).write_text(src)
    TARGET.write_text(part1.rstrip("\n") + "\n\n---\n\n# PART II -- THE CRAFT (the law that hangs off the process)\n\n" + src)
    print("Patched %s" % TARGET.name)
    print("  backup: %s.pre_%s" % (TARGET.name, ts))
    print("  prepended PART I; existing craft is now PART II")
    print("  TODO by hand: delete or flag-as-superseded the old Section 10 pathway (PHASE 0-12)")


if __name__ == "__main__":
    main()
