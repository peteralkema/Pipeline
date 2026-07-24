#!/usr/bin/env python3
"""
patch_chambers_canon_v2.py -- probe-driven canon rewrite, round 1.

Seven tokens failed the $3.84 probe. Each is rewritten ONCE. Per _LEGO.md, a token
rewritten more than twice means the IDEA is wrong, not the wording -- so if any of
these fails round 2, the concept changes rather than the phrasing.

WHAT FAILED AND WHY

 guidetwo    rendered a NUDE CLASSICAL BRONZE STATUE on a plinth (flat 231).
             'deep bronze-red' made the model build a bronze. This token carries
             Raphael through b6/b7/b8 -- the whole back half -- and nudity is a
             spell-breaker. FIX: drop the word bronze entirely; say living man,
             robed shoulder to ankle, and state the height as a comparison.

 guideone    read as an ordinary-sized man (flat 022). Scene played as an arrest,
             not a taking. FIX: same explicit height comparison.

 upland      invented mass migrations and monumental architecture (flat 039).
             The model's biblical-epic prior fills empty ground with extras.
             FIX: 'wild trackless country far from any settlement' -- stated
             POSITIVELY, since gate_canon cannot read a negation.

 cornerstone no geometry at all, plus a RING on the finger (flat 141). FIX: name
             the right angles and the tooled faces; add bare unadorned hands to
             enochman so the modern object stops appearing.

 windstores  rainbow pastel wind, matte-painting flatness, camels and tents
             (flat 125). FIX: lock the palette to amber and cold grey, say
             photorealistic, and describe the air as dense visible current.

 archface    produced a DIPTYCH -- two panels with a visible seam (flat 234).
             FIX: 'a single continuous photographic frame'.

 thronepeak  a small marble chair on a hilltop above a tent camp (flat 157).
             The seat read as furniture. FIX: the SUMMIT ITSELF is the seat,
             carved out of the mountain, hundreds of feet high.

Idempotent. Anchor-verified. Backs up to canon.json.pre_v2. ASCII only.
"""
import json, os, re, sys, shutil

SLUG, CHANNEL = "chambers-of-the-dead", "sacred-dawn"

def repo_root(start=None):
    p = os.path.abspath(start or os.getcwd())
    while p != "/":
        if os.path.isdir(os.path.join(p, ".git")): return p
        p = os.path.dirname(p)
    sys.exit("FAIL: no .git found walking up. Pass the repo root as argv[1].")

ROOT = repo_root(sys.argv[1] if len(sys.argv) > 1 else None)
P = os.path.join(ROOT, CHANNEL, "projects", SLUG, "canon.json")
if not os.path.isfile(P): sys.exit("FAIL: missing %s" % P)
d = json.load(open(P, encoding="utf-8"))

NEW = {
 "guidetwo": (
   "an enormous living man standing about twice the height of an ordinary person beside him, "
   "robed from shoulder to ankle in heavy deep red-brown wool, weathered human face and dark hair, "
   "broad and physically solid with full weight and a hard cast shadow, both hands open and empty at rest"),

 "guideone": (
   "an enormous living man standing about twice the height of an ordinary person beside him, "
   "robed from shoulder to ankle in heavy undyed pale grey wool, calm weathered human face, "
   "broad and physically solid with full weight and a hard cast shadow"),

 "upland": (
   "a dry bare upland of pale packed earth and low scattered scrub running to open horizons, "
   "shallow dry watercourses cutting through low hills, the ground hard-swept and stony, "
   "wild trackless country far from any settlement, a wide clear sky above"),

 "cornerstone": (
   "the exposed corner of the earth itself, one titanic square-cut foundation block of pale weathered "
   "stone with flat tooled faces and sharp right-angled edges, laid level and projecting out over an "
   "immeasurable drop, the surrounding land bedded against two of its faces, the geometry unmistakably "
   "built rather than eroded"),

 "windstores": (
   "an enormous row of open doorways of cut pale stone set into a cliff at the edge of the world, each "
   "giving onto a vast vaulted chamber, dense visible currents of moving air held inside them, the whole "
   "scene in warm amber and cold grey tones under hard raking daylight, photorealistic and physically "
   "solid, bare swept ground before them"),

 "archface": (
   "an enormous plane of grey-black rock rising sheer from bare ground, the whole side of a mountain "
   "taken down flat with fine parallel working marks across it, four colossal arched openings cut in a "
   "row into its base, cold hard light raking the surface, a single continuous photographic frame"),

 "thronepeak": (
   "the seventh mountain at the centre of the group, its entire summit carved into the colossal shape of "
   "a great seat hundreds of feet high, arms and a high back and a broad step formed out of the white "
   "stone of the mountain itself, heavy dark trees ringing the base far below, one narrow shaft of bright "
   "cold light standing on the summit"),

 "enochman": (
   "a lean upright man of middle years in a heavy undyed woollen robe, dark beard cut short, weathered "
   "sunlit face, bare unadorned hands and forearms, moving with purpose"),
}

if all(d.get(k) == v for k, v in NEW.items()):
    print("ALREADY APPLIED. Nothing to do."); sys.exit(0)

missing = [k for k in NEW if k not in d]
if missing: sys.exit("FAIL anchor: tokens absent from canon: %s" % missing)

BAD = re.compile(r"\bno\b|\bnot\b|\bwithout\b|\bnever\b|\bnothing\b")
for k, v in NEW.items():
    if BAD.search(v): sys.exit("FAIL: negation in new %s -- gate_canon cannot read it" % k)

shutil.copyfile(P, P + ".pre_v2")
for k, v in NEW.items():
    print("  %-12s %d -> %d chars" % (k, len(d[k]), len(v)))
    d[k] = v
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("\n  %d tokens total | backup canon.json.pre_v2" % len(d))
print("  negation sweep across ALL tokens:",
      [k for k, v in d.items() if BAD.search(v)] or "clean")
print("\n  re-probe: 1/22 1/39 4/5 4/13 4/21 4/37 6/31 6/34")
print("  plus the four tokens the sampler never reached:")
print("    6/5 westmountain | 7/35 hollowfour | 8/31 floodwater | 8/35 westmountain_after")
