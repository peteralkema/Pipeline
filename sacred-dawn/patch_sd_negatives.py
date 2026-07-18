#!/usr/bin/env python3
"""
patch_sd_negatives.py -- create (or union into) the Sacred Dawn CHANNEL rulebook
with the door/gear/galaxy negatives surfaced by the 20-beat probe.

Laptop-safe: pure stdlib, no engine import, no dotenv. Writes the channel-scoped
rulebook.json so the negatives ADD to the universal shared rulebook without
touching it. NO earth terms -- the earthrise motif is intended on the {limb}
beats; b4/9's earth is fixed in the beat, not banned channel-wide.

Idempotent: creates the file if absent, unions new terms (case-insensitive) if
present, writes the FULL object explicitly (FLAGS #9). Backs up any existing file
to rulebook.json.pre_<ts>. ASCII only. Run from the sacred-dawn channel dir.
"""
import json, time
from pathlib import Path

TARGET = Path("rulebook.json")

NEGATIVES = [
    "door leaf", "hinged door", "wooden door", "panelled door", "door hinge",
    "backlit glowing doorway", "freestanding archway", "ornate gate frame",
    "sci-fi portal",
    "gear", "cog", "clockwork", "brass fittings", "visible machinery",
    "spiral galaxy", "galaxy", "nebula",
]


def die(msg):
    print("PATCH ABORTED: " + msg)
    raise SystemExit(1)


def main():
    existed = TARGET.exists()
    if existed:
        try:
            rb = json.loads(TARGET.read_text())
        except Exception as e:
            die("existing rulebook.json is not valid JSON: %s" % e)
        if not isinstance(rb, dict):
            die("existing rulebook.json is not a JSON object.")
    else:
        rb = {}

    rb.setdefault("negative", [])
    rb.setdefault("motion_rules", [])
    rb.setdefault("people_directive", "")
    if not isinstance(rb["negative"], list):
        die("rulebook 'negative' is not a list.")

    have = {t.lower() for t in rb["negative"]}
    added = 0
    for term in NEGATIVES:
        if term.lower() not in have:
            rb["negative"].append(term)
            have.add(term.lower())
            added += 1

    if added == 0 and existed:
        print("Already applied (all %d negatives present). No change." % len(NEGATIVES))
        return

    out = json.dumps(rb, indent=2, ensure_ascii=False)
    if not out.isascii():
        die("result contains non-ASCII bytes.")

    if existed:
        ts = time.strftime("%Y%m%d-%H%M%S")
        backup = TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts)
        backup.write_text(TARGET.read_text())
        print("  backup: %s" % backup.name)
    TARGET.write_text(out)
    print("%s sacred-dawn/rulebook.json" % ("Updated" if existed else "Created"))
    print("  negatives added: %d  (total in channel rulebook: %d)" % (added, len(rb["negative"])))


if __name__ == "__main__":
    main()
