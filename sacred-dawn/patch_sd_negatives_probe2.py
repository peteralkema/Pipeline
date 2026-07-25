#!/usr/bin/env python3
"""
patch_sd_negatives_probe2.py -- union the bridge-probe (chambers, 20 beats,
25 Jul) negatives into the Sacred Dawn CHANNEL rulebook.

Surfaced by the probe:
  - baked letterbox / black bars on ~15% of stills (survive KB crops unpredictably)
  - armour drift on witness figures (breastplates, shield) against the Witness
    Register's ordinary-frightened-people law

Deliberately NOT banned: sword (the Eden guardian's flaming sword is core Sacred
Dawn material), weapons as a generic term (same reason), earth terms (see v1 note).

Laptop-safe: pure stdlib, no engine import. Idempotent: creates rulebook.json if
absent, unions new terms case-insensitively if present, writes the FULL object
explicitly (FLAGS #9). Backs up any existing file to rulebook.json.pre_<ts>.
ASCII only. Run from the sacred-dawn channel dir.
"""
import json
import time
from pathlib import Path

TARGET = Path("rulebook.json")

NEGATIVES = [
    "letterbox", "black bars", "cinematic bars", "widescreen bars",
    "film frame border", "black border",
    "armor", "armour", "breastplate", "bronze breastplate", "cuirass",
    "chainmail", "shield", "helmet", "warrior gear",
]


def die(msg):
    print("PATCH ABORTED: " + msg)
    raise SystemExit(1)


def main():
    existed = TARGET.exists()
    rb = {}
    if existed:
        try:
            rb = json.loads(TARGET.read_text())
        except Exception as e:
            die("existing rulebook.json is not valid JSON: %s" % e)
        backup = TARGET.with_name("rulebook.json.pre_%d" % int(time.time()))
        backup.write_text(TARGET.read_text())
        print("backed up existing rulebook -> %s" % backup.name)

    if not isinstance(rb, dict):
        die("rulebook.json root is not an object")

    negs = rb.get("negatives", [])
    if not isinstance(negs, list):
        die("rulebook.json 'negatives' is not a list")

    have = {str(n).strip().lower() for n in negs}
    added = []
    for term in NEGATIVES:
        if term.lower() not in have:
            negs.append(term)
            have.add(term.lower())
            added.append(term)

    rb["negatives"] = negs
    TARGET.write_text(json.dumps(rb, indent=2, ensure_ascii=True) + "\n")

    print("rulebook.json %s" % ("updated" if existed else "created"))
    print("added %d term(s): %s" % (len(added), ", ".join(added) if added else "(none - already present)"))
    print("total negatives: %d" % len(negs))


if __name__ == "__main__":
    main()
