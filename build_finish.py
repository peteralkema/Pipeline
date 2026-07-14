#!/usr/bin/env python3
"""ENOCH FINISH-PROJECT ASSEMBLER

Turns the 400 picked winners into 10 Kling-ready finish projects.

Motion is DERIVED (Motion Doctrine), never invented:
  grief/aftermath  -> SETTLE      (never push; VO re-read of "never push on silence")
  vertical force   -> CRANE-UP    (overrides variant)
  c tight face     -> PUSH-IN     (a face is the single overwhelming subject)
  a wide/scale     -> PULL-BACK   (that framing's meaning IS scale)
  b mid            -> PUSH-IN
  d wildcard       -> read off beat text (scale->pull, vertical->crane, else push)

NEAR-LOCKED is deliberately unused: under continuous VO a locked frame reads as a
stalled slideshow, not a held breath. SETTLE carries the quiet work.

TWO MODES (no 600MB upload -- the stills already live on the box):

  LAPTOP:  python3 build_finish.py emit
     reads ~/Downloads/enoch-stills/blockNN/stills/Winners/
     writes enoch-finish/blockNN/{beats.json,picks.json} + _MOTION-VETO.md

  BOX:     python build_finish.py place
     reads picks.json, copies picked stills out of enoch-blockNN-v2/stills/
     into enoch-blockNN-finish/stills/ renamed shot_001..040 in BEAT order.
"""
import json, os, re, shutil, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
WINNERS_ROOT = pathlib.Path(os.environ.get("ENOCH_WINNERS", os.path.expanduser("~/Downloads/enoch-stills")))
OUT_ROOT = HERE / "enoch-finish"
BOX_PROJECTS = HERE / "sacred-dawn" / "projects"

MOVES = {
 "CRANE-UP":    "Slow, steady crane up. The camera rises with the vertical force, weighted and eased, never abrupt. Subject locked; only ambient dust, smoke and cloth drift. One motion only.",
 "PUSH-IN":     "Slow, steady push in. The camera eases forward into the subject, weighted and gradual, increasing pressure. Subject locked; only ambient dust, smoke and cloth drift. One motion only.",
 "PULL-BACK":   "Slow, steady pull back. The camera eases outward to reveal the full scale, weighted and gradual. Subject locked; only ambient dust, smoke and cloth drift. One motion only.",
 "SETTLE":      "Very slow downward drift and settle, near-locked. A visual exhale. The camera barely moves; only ambient dust, smoke and water drift. One motion only, no push.",
 "NEAR-LOCKED": "Static locked camera. No camera movement at all. Only ambient drift of dust, smoke, cloth or water within the frame. Absolutely no push, no pull.",
}

VERTICAL = ("descend","descending","descends","tower","towering","towers","rise","rises","rising","ascend",
            "ascending","ascends","column","pillar","fall from","falling from","cast down","cast into",
            "down from","from the sky","from above","upward","overhead","looming above","vortex","plunge",
            "shaft","staircase","stairs","climb","climbing","above the","high above","spire")
SCALE = ("horizon","endless","countless","vast","spreads","spreading","across the","stretching","whole",
         "entire","every","thousands","multitude","as far as","all the land","the world","world-wide",
         "wide valley","panorama","expanse","legion","host of","armies","crowd","gathering","procession")


def derive(beat_title, phenom, wild, variant, emotion):
    txt = (beat_title + " " + phenom + " " + (wild or "")).lower()
    vertical = any(k in txt for k in VERTICAL)
    scale = any(k in txt for k in SCALE)
    if emotion == "grief":
        return "SETTLE", "grief/aftermath beat -> settle (never push)"
    if vertical:
        return "CRANE-UP", "vertical force in frame -> crane rises with it"
    if variant == "c":
        return "PUSH-IN", "tight face = single overwhelming subject -> push"
    if variant == "a":
        return "PULL-BACK", "wide/phenomenon-dominant: framing's meaning is scale -> pull"
    if variant == "b":
        return "PUSH-IN", "mid, phenomenon looming behind -> push"
    if scale:
        return "PULL-BACK", "wildcard, beat is about scale/number -> pull"
    return "PUSH-IN", "wildcard, single subject / default -> push"


def load_blocks():
    cands = [HERE / "build_enoch_all.py",
             pathlib.Path(os.path.expanduser("~/Downloads/build_enoch_all.py")),
             HERE / "sacred-dawn" / "build_enoch_all.py"]
    for cand in cands:
        if cand.exists():
            src = cand.read_text()
            src = src[:src.index("arg = sys.argv[1]")]
            ns = {}
            exec(compile(src, str(cand), "exec"), ns)
            return ns["BLOCKS"], ns["emotion_for"]
    sys.exit("ERROR: build_enoch_all.py not found (looked in ., ~/Downloads, ./sacred-dawn)")


def shot_to_beat_variant(n):
    return (n + 3) // 4, "abcd"[(n - 1) % 4]


def emit():
    BLOCKS, emotion_for = load_blocks()
    OUT_ROOT.mkdir(exist_ok=True)
    veto = ["# ENOCH MOTION VETO TABLE",
            "Derived by the Motion Doctrine from beat x variant x register. Review before Kling ($168).",
            "Flip any row by editing motion_prompt in that block's beats.json.",
            "Moves: CRANE-UP / PUSH-IN / PULL-BACK / SETTLE / NEAR-LOCKED"]
    grand = {}
    for n in sorted(BLOCKS):
        slug, title, beats = BLOCKS[n]
        wdir = WINNERS_ROOT / ("block%02d" % n) / "stills" / "Winners"
        if not wdir.exists():
            sys.exit("ERROR: %s not found" % wdir)
        shots = []
        for f in wdir.glob("*.png"):
            m = re.search(r"(\d+)", f.name)
            if m:
                shots.append(int(m.group(1)))
        if len(shots) != 40:
            sys.exit("ERROR: block%02d has %d winners, expected 40" % (n, len(shots)))
        picked = {}
        for s in shots:
            b, v = shot_to_beat_variant(s)
            if b in picked:
                sys.exit("ERROR: block%02d beat %d picked twice (shots %d and %d)" % (n, b, picked[b][0], s))
            picked[b] = (s, v)
        missing = [b for b in range(1, 41) if b not in picked]
        if missing:
            sys.exit("ERROR: block%02d missing beats %s" % (n, missing))

        bj = {"beats": []}
        picks = {"block": n, "slug": slug, "picks": []}
        veto.append("")
        veto.append("## BLOCK %d - %s" % (n, title))
        veto.append("")
        veto.append("| beat | shot | var | move | why |")
        veto.append("|------|------|-----|------|-----|")
        counts = {}
        for b in range(1, 41):
            s, v = picked[b]
            t, p, a, w = beats[b - 1]
            emo = emotion_for(t, p, w)
            move, why = derive(t, p, w, v, emo)
            counts[move] = counts.get(move, 0) + 1
            bj["beats"].append({"narration": "", "image_prompt": "",
                                "motion_prompt": MOVES[move], "motion": move,
                                "beat_title": t, "source_shot": s, "variant": v})
            picks["picks"].append({"beat": b, "src_shot": s, "variant": v,
                                   "dst": "shot_%03d.png" % b, "move": move})
            veto.append("| %d | %03d | %s | **%s** | %s |" % (b, s, v, move, why))
        veto.append("")
        veto.append("*spread: " + "  ".join("%s=%d" % kv for kv in sorted(counts.items())) + "*")
        grand[n] = counts
        d = OUT_ROOT / ("block%02d" % n)
        d.mkdir(exist_ok=True)
        (d / "beats.json").write_text(json.dumps(bj, indent=2, ensure_ascii=False) + "\n")
        (d / "picks.json").write_text(json.dumps(picks, indent=2) + "\n")

    tot = {}
    for c in grand.values():
        for k, v in c.items():
            tot[k] = tot.get(k, 0) + v
    veto.insert(4, "**PORTFOLIO SPREAD (400 clips):** " + "  ".join("%s=%d" % kv for kv in sorted(tot.items())))
    (OUT_ROOT / "_MOTION-VETO.md").write_text("\n".join(veto) + "\n")
    print("wrote enoch-finish/blockNN/{beats.json,picks.json} + _MOTION-VETO.md")
    print("portfolio spread:", tot)


def place():
    for n in range(1, 11):
        pj = OUT_ROOT / ("block%02d" % n) / "picks.json"
        if not pj.exists():
            sys.exit("ERROR: %s not found -- run `emit` on laptop and push first" % pj)
        picks = json.loads(pj.read_text())
        src_dir = BOX_PROJECTS / ("enoch-block%02d-v2" % n) / "stills"
        proj = BOX_PROJECTS / ("enoch-block%02d-finish" % n)
        dst_dir = proj / "stills"
        dst_dir.mkdir(parents=True, exist_ok=True)
        for p in picks["picks"]:
            src = src_dir / ("shot_%03d.png" % p["src_shot"])
            if not src.exists():
                sys.exit("ERROR: %s missing" % src)
            shutil.copy2(src, dst_dir / p["dst"])
        shutil.copy2(OUT_ROOT / ("block%02d" % n) / "beats.json", proj / "beats.json")
        print("block%02d-finish: 40 stills placed in beat order" % n)
    print("")
    print("all 10 finish projects ready. set kling_count: 40 before animating.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "emit":
        emit()
    elif mode == "place":
        place()
    else:
        sys.exit("usage: build_finish.py emit   (laptop)\n       build_finish.py place  (box)")
