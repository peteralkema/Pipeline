#!/usr/bin/env python3
"""patch_canon_newearth.py  --  strengthen the {newearth} token.

The finale token was reading as a bright DESERT / generic ancient city: brightness
adjectives alone ("radiant/bright/clean") do not say new-creation to the image model.
This rewrites {newearth} to inject glory as SUBSTANCE (things glowing as if lit from
within, white-and-gold radiance) and to close out the sea POSITIVELY (a shining
unbroken ground) rather than via the unreliable "no sea" negation. Re-steers all eight
finale beats at once -- no phenomenon re-authoring.

JSON key overwrite (parse -> set -> dump); idempotent; .pre_ backup; ASCII-only.
Operates on the project canon.json. Run from the project dir or pass --canon.
"""
import argparse, json, os, sys

KEY = "newearth"
NEW = 'the new creation itself, a vast transfigured realm of radiant white-and-gold light where everything glows as if lit from within, brilliant heavenly glory filling a luminous sky, the shining ground dry and unbroken to a bright far horizon, immense, sacred, dazzlingly new'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canon", default="canon.json")
    a = ap.parse_args()
    p = a.canon
    if not os.path.isfile(p):
        sys.stderr.write("ERROR: not found: %s\n" % p); sys.exit(1)
    canon = json.loads(open(p, encoding="utf-8").read())
    if KEY not in canon:
        sys.stderr.write("ERROR: canon.json has no %r key -- ABORT.\n" % KEY); sys.exit(1)
    if canon[KEY] == NEW:
        print("no change (newearth already at new value)"); return
    bak = p + ".pre_newearth"
    if not os.path.exists(bak):
        open(bak, "w", encoding="utf-8").write(open(p, encoding="utf-8").read()); print("backup:", bak)
    old = canon[KEY]
    canon[KEY] = NEW
    with open(p, "w", encoding="utf-8") as f:
        json.dump(canon, f, indent=2, ensure_ascii=True)
        f.write("\n")
    print("OK: {newearth} updated.")
    print("  old:", old[:70], "...")
    print("  new:", NEW[:70], "...")

if __name__ == "__main__":
    main()