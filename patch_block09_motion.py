#!/usr/bin/env python3
"""PATCH: block 09 motion — kill the settle-lull.

17 of block 09's 40 clips derived as SETTLE (43%). Every other block is 0-5.
Cause: the grief classifier fires on "the dead / souls / waits" and overrides
everything, so cosmic-wonder beats that happen to concern the dead ("the chambers
vast and deep", "a map of the afterlife") were classified as mourning and settled.
Block 09 is already the softest retention beat, sitting between the moon and the
finale. 17 near-static clips there is a lull, not a breath.

FIX: correct the REGISTER of the 13 misclassified beats, then RE-DERIVE the move
with the normal doctrine rules (vertical->crane, c->push, a->pull, b->push,
d->scale?pull:push). Motion stays derived, never hand-picked. Four genuine
grief beats keep their SETTLE — if nothing settles, nothing pushes.

Idempotent. Backs up .pre_block09motion_*. Run from repo root (~/Projects/Pipeline).
"""
import json, pathlib, sys, shutil, datetime, os

BJ = pathlib.Path("enoch-finish/block09/beats.json")
PJ = pathlib.Path("enoch-finish/block09/picks.json")

# beat -> corrected register.  KEEP = genuine grief, stays SETTLE.
CORRECTED = {
     1: "awe",    # A great mountain in the west      - vast mountain, not mourning
     3: "grief",  # Where the spirits wait            - KEEP
     7: "fear",   # Separated from the rest           - division/judgment
     9: "fear",   # Kept until the judgment           - dread
    11: "awe",    # Every spirit assigned             - systematic vastness
    14: "grief",  # A place of waiting                - KEEP
    15: "awe",    # The angel over the dead           - towering figure
    17: "fear",   # Nothing is forgotten              - dread
    20: "grief",  # The proud brought low             - KEEP
    22: "awe",    # The chambers vast and deep        - vast architecture
    24: "awe",    # The path each soul takes          - cosmic structure
    25: "awe",    # Where Enoch stood among them      - encounter
    26: "grief",  # The stillness of it               - KEEP (literally stillness)
    32: "awe",    # A map of the afterlife            - vast structure
    34: "awe",    # Written before the rest           - revelation
    35: "awe",    # Enoch was shown it all            - vast reveal
    37: "fear",   # The living who saw the dead       - encounter/dread
}

MOVES = {
 "CRANE-UP":    "Slow, steady crane up. The camera rises with the vertical force, weighted and eased, never abrupt. Subject locked; only ambient dust, smoke and cloth drift. One motion only.",
 "PUSH-IN":     "Slow, steady push in. The camera eases forward into the subject, weighted and gradual, increasing pressure. Subject locked; only ambient dust, smoke and cloth drift. One motion only.",
 "PULL-BACK":   "Slow, steady pull back. The camera eases outward to reveal the full scale, weighted and gradual. Subject locked; only ambient dust, smoke and cloth drift. One motion only.",
 "SETTLE":      "Very slow downward drift and settle, near-locked. A visual exhale. The camera barely moves; only ambient dust, smoke and water drift. One motion only, no push.",
}

VERTICAL = ("descend","descending","descends","tower","towering","towers","rise","rises","rising","ascend",
            "ascending","ascends","column","pillar","fall from","falling from","cast down","cast into",
            "down from","from the sky","from above","upward","overhead","looming above","vortex","plunge",
            "shaft","staircase","stairs","climb","climbing","above the","high above","spire","deep","descent")
SCALE = ("horizon","endless","countless","vast","spreads","spreading","across the","stretching","whole",
         "entire","every","thousands","multitude","as far as","all the land","the world","world-wide",
         "wide valley","panorama","expanse","legion","host of","armies","crowd","gathering","procession",
         "chambers","map","all of it","each soul")


def derive(t, p, w, variant, emotion):
    txt = (t + " " + p + " " + (w or "")).lower()
    if emotion == "grief":
        return "SETTLE"
    if any(k in txt for k in VERTICAL):
        return "CRANE-UP"
    if variant == "c":
        return "PUSH-IN"
    if variant == "a":
        return "PULL-BACK"
    if variant == "b":
        return "PUSH-IN"
    if any(k in txt for k in SCALE):
        return "PULL-BACK"
    return "PUSH-IN"


def load_blocks():
    for cand in (pathlib.Path("build_enoch_all.py"),
                 pathlib.Path(os.path.expanduser("~/Downloads/build_enoch_all.py"))):
        if cand.exists():
            src = cand.read_text()
            src = src[:src.index("arg = sys.argv[1]")]
            ns = {}
            exec(compile(src, str(cand), "exec"), ns)
            return ns["BLOCKS"]
    sys.exit("ERROR: build_enoch_all.py not found (repo root or ~/Downloads)")


def main():
    if not BJ.exists():
        sys.exit("ERROR: %s not found -- run from repo root after `build_finish.py emit`" % BJ)
    BLOCKS = load_blocks()
    beats_data = BLOCKS[9][2]
    bj = json.loads(BJ.read_text())
    rows = bj["beats"]
    if len(rows) != 40:
        sys.exit("ERROR: block09 beats.json has %d rows, expected 40" % len(rows))

    before = {}
    for r in rows:
        before[r["motion"]] = before.get(r["motion"], 0) + 1

    changes = []
    for i, r in enumerate(rows):
        beat = i + 1
        if beat not in CORRECTED:
            continue
        t, p, a, w = beats_data[beat - 1]
        if r["beat_title"] != t:
            sys.exit("ERROR: beat %d title mismatch -- '%s' vs '%s'" % (beat, r["beat_title"], t))
        new = derive(t, p, w, r["variant"], CORRECTED[beat])
        if new != r["motion"]:
            changes.append((beat, t, r["motion"], new, r["variant"]))
            r["motion"] = new
            r["motion_prompt"] = MOVES[new]

    if not changes:
        print("already patched -- no change")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(BJ, BJ.with_name("beats.json.pre_block09motion_%s" % stamp))
    BJ.write_text(json.dumps(bj, indent=2, ensure_ascii=False) + "\n")

    # keep picks.json in sync so `place` reports the same moves
    if PJ.exists():
        pj = json.loads(PJ.read_text())
        for p in pj["picks"]:
            p["move"] = rows[p["beat"] - 1]["motion"]
        PJ.write_text(json.dumps(pj, indent=2) + "\n")

    after = {}
    for r in rows:
        after[r["motion"]] = after.get(r["motion"], 0) + 1

    print("BLOCK 09 MOTION PATCH -- %d beats re-derived\n" % len(changes))
    print("  beat  var  %-10s ->  %-10s  title" % ("was", "now"))
    for beat, t, old, new, v in changes:
        print("  %4d   %s   %-10s ->  %-10s  %s" % (beat, v, old, new, t))
    print("\n  before: " + "  ".join("%s=%d" % kv for kv in sorted(before.items())))
    print("  after : " + "  ".join("%s=%d" % kv for kv in sorted(after.items())))
    print("\n  settles kept (genuine grief): beats 3, 14, 20, 26")
    print("  backup: %s" % BJ.with_name("beats.json.pre_block09motion_%s" % stamp).name)


if __name__ == "__main__":
    main()
