#!/usr/bin/env python3
"""
patch_limb_degalaxy.py -- remove ", no galaxy, no nebula" from the {limb} canon token.

gate_canon greps every canon token's TEXT for BANNED_VISUAL words and cannot tell a
negation from a subject, so "no galaxy, no nebula" inside {limb} fails the grid/blocks
gate. The clause was redundant anyway -- the channel rulebook already bans galaxy/nebula
globally. This strips it. (probe20 never gate_canon'd, which is why it wasn't caught
until `grid`.)

Idempotent, anchor-verified, .pre_<ts> backup, ASCII. Run from the enoch-moon project dir.
"""
import json, time
from pathlib import Path

TARGET = Path("canon.json")
CLAUSE = ", no galaxy, no nebula"


def die(msg):
    print("PATCH ABORTED: " + msg)
    raise SystemExit(1)


def main():
    if not TARGET.exists():
        die("canon.json not found. Run from the enoch-moon project dir.")
    data = json.loads(TARGET.read_text())
    limb = data.get("canon", {}).get("limb")
    if limb is None:
        die("{limb} token not present -- run patch_moon_limb_token.py first.")
    if CLAUSE not in limb:
        print("Already applied ({limb} has no banned-word clause). No change.")
        return

    data["canon"]["limb"] = limb.replace(CLAUSE, "")
    out = json.dumps(data, indent=2, ensure_ascii=False)
    if not out.isascii():
        die("result contains non-ASCII bytes.")

    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts)
    backup.write_text(TARGET.read_text())
    TARGET.write_text(out)
    print("Patched canon.json")
    print("  backup: %s" % backup.name)
    print("  removed banned-word clause from {limb}")


if __name__ == "__main__":
    main()
