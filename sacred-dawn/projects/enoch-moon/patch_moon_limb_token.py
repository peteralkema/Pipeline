#!/usr/bin/env python3
"""
patch_moon_limb_token.py -- add the {limb} canon token to enoch-moon/canon.json.

{limb} is {heavens} with one change: it PERMITS a small distant earth beyond the
limb, where {heavens} forbids it ("no earth"). Nine earthrise beats authored the
earth against {heavens}'s own "no earth" clause; retagging them to {limb} (done in
patch_moon_openings.py) resolves the token-vs-beat contradiction that threw b4/9
into galaxies-and-mush. The ~286 pure-sky beats keep {heavens} and its "no earth".

Idempotent. Verifies {heavens} exists as the anchor, writes the FULL object
explicitly (FLAGS #9 -- never read-modify-write a config from a partial view),
backs up to canon.json.pre_<ts>, ASCII only. Run from the enoch-moon project dir.
"""
import json, time
from pathlib import Path

TARGET = Path("canon.json")

LIMB = ("the airless surface of the moon seen close above it -- grey lunar rock and "
        "crater fields curving away to a hard black horizon, black star-scattered space "
        "beyond, a small distant earth low on the horizon far beyond the limb, raw "
        "unfiltered sunlight, no atmosphere, no clouds, no blue sky, no ground, no "
        "vegetation, no ruins, no people, no human figures, no astronauts, no crowds, "
        "no galaxy, no nebula")


def die(msg):
    print("PATCH ABORTED: " + msg)
    raise SystemExit(1)


def main():
    if not TARGET.exists():
        die("canon.json not found in cwd. Run from the enoch-moon project dir.")
    data = json.loads(TARGET.read_text())
    canon = data.get("canon")
    if not isinstance(canon, dict):
        die("canon.json has no 'canon' dict.")
    if "heavens" not in canon:
        die("anchor token {heavens} not present -- not the expected canon.json.")
    if canon.get("limb") == LIMB:
        print("Already applied ({limb} present). No change.")
        return
    if "limb" in canon and canon["limb"] != LIMB:
        die("{limb} already exists with different text -- refusing to overwrite.")

    canon["limb"] = LIMB
    out = json.dumps(data, indent=2, ensure_ascii=False)
    if not out.isascii():
        die("result contains non-ASCII bytes.")

    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts)
    backup.write_text(TARGET.read_text())
    TARGET.write_text(out)
    print("Patched canon.json")
    print("  backup: %s" % backup.name)
    print("  added token: {limb} (%d tokens total)" % len(canon))


if __name__ == "__main__":
    main()
