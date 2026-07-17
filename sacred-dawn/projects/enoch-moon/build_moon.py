#!/usr/bin/env python3
"""
build_moon.py -- beat table CSV -> engine beats.json, and the register probe.

  python3 build_moon.py blocks          # -> moon-bNN-finish/beats.json for every block
  python3 build_moon.py probe           # -> moon-probe-finish/beats.json (16 stills, $1.28)

Run from sacred-dawn/projects/enoch-moon/.  Reads beats/*.csv + canon.json.

TOKENS ARE EXPANDED HERE, NOT BY THE ENGINE.
_expand_canon is verified to exist on the modea_beats.py translate leg; it is NOT verified
to fire on `stills --beats`.  Expanding locally gives verbatim repetition by construction
with zero dependency on unverified engine behaviour.  Verbatim repetition IS the mechanism
(_LEGO.md 3A.2, setting continuity).  Route through canon later, once proven.
"""
import csv, json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
CANON = json.loads((HERE / "canon.json").read_text())["canon"]

# BANNED IN image_prompt -- gravity wells found by probe, 17 Jul.
#
# "machine" is this film's METAPHOR. _LEGO.md 3A.2: "No literal-metaphor beats. Models
# render metaphors as corny props." The model rendered `mechanism` as VICTORIAN CLOCKWORK --
# gears, chains, rivets, an orrery. Magnificent mass, wrong millennium.
#
# THE RESOLUTION: the NARRATION says machine. The IMAGE never renders one.
# Enoch describes gates, portions, storehouses -- ARCHITECTURE. Render cyclopean cut stone,
# ranked megalithic openings, nothing moving. The viewer supplies the word.
BANNED_VISUAL = [
    "machine", "machinery", "mechanism", "mechanical", "machined",
    "gear", "cog", "clockwork", "brass", "rivet", "chain", "orrery", "piston", "industrial",
    "galaxy", "nebula",          # modern astronomy in a third-century text
    "luminous", "glowing", "faceless", "half-seen", "soft movement",   # the Final Hours pull
    "dusty library", "dust-filled",
    "hieroglyph", "egyptian", "sun disk", "pharaoh", "obelisk",   # well #5, 17 Jul
]


# ---------------------------------------------------------------- probe slots
# PHASE 3 selection procedure -- run per slot, first rule that fires claims it.
#   1. change-weighted   (what changed since last probe = half the probe)
#   2. novel-composition (never rendered before -- a failure costs a payload, not a still)
#   3. axis canaries     (one cosmic + one earthly per block, MANDATORY, never uniform-random)
#   4. known-failure     (any class that has rendered wrong before)
#
# THE CHANGE (17 Jul): light moved OUT of style_suffix (the god-ray clause was killed --
# it stamped every still) and INTO the beat.  So the probe is weighted at both ends of the
# light axis.  Strip the blanket and skip the per-beat light rule and the murk comes back
# by a different road.

PROBE = [
    # (block, clip_index, rule, verdict question -- WRITTEN BEFORE IT RENDERS)
    (1,  1, "canary-cosmic",  "Are TWELVE gates countable, or do they read as texture?"),
    (1, 11, "known-failure",  "Ge'ez script: garbled? (expect yes -- we need to know for $0.08, not at frame 600)"),
    (1, 13, "canary-earthly", "Highland exterior: BRIGHT daylight with no stamped storm?"),
    (1, 18, "change-light",   "Machine spanning sky: MASS and shadow, or glow and vapour? (Balrog)"),
    (1, 20, "change-light",   "Descending host: enormous PHYSICAL figures, or luminous floaters?"),
    (1, 24, "canary-earthly", "Chapel from outside: is the cliff face bright, or has murk returned?"),
    (1, 31, "novel",          "ORDINARY moon cresting a ridge -- ordinary enough for the gap to work?"),
    (1, 40, "change-light",   "Figure at the gate: face brightest object, solid, no glow?"),
    (2,  5, "canary-earthly", "Cave mouth in blazing desert: bright, or has it gone dim?"),
    (2, 13, "canary-cosmic",  "Mechanism across the whole sky: engineered, or abstract light?"),
    (2, 17, "novel",          "Wall of water taller than mountains: physical mass, bright?"),
    (2, 21, "novel",          "THE KILLER SHOT -- ziggurat + the same moon + the same gates. Does it land?"),
    (2, 23, "known-failure",  "Cuneiform close-up: legible wedge marks, or mush?"),
    (2, 29, "novel",          "Machine revealed deeper -- mechanism behind mechanism. Reads?"),
    (2, 32, "novel",          "THE GAP -- a missing section of machine. Block 2's payload has no image without this."),
    (2, 36, "novel",          "The gap filling frame: vast, bright, empty. Or just a hole?"),
]


def check_tokens(text: str, where: str) -> None:
    """The engine expands. We only GATE -- every token must resolve, before spend.
    _expand_canon raises at render time; this raises at authoring time, for free."""
    for k in re.findall(r"\{(\w+)\}", text):
        if k not in CANON:
            raise SystemExit(f"{where}: unknown setting token {{{k}}} -- add it to canon.json")


def load(block: int):
    p = HERE / "beats" / f"moon_block{block:02d}_beats.csv"
    if not p.is_file():
        raise SystemExit(f"missing {p}")
    return list(csv.DictReader(p.open()))


def to_beat(row, index: int) -> dict:
    """The schema `stills --beats` reads. Verified against cmd_stills, not inferred.

      b["image_prompt"]          REQUIRED -- no .get(), a missing key is a KeyError
      b.get("motion_prompt")     optional -> falls back to channel.json default_motion
      b.get("narration", "")     optional

    NOT the parse leg's schema (visual/mode/component/found_line) -- that is a different
    artifact that happens to share the filename beats.json. Read the consumer, not a neighbour.

    motion_prompt is deliberately OMITTED: motion is derived at PHASE 6 from
    beat x variant x register, after the pick. Never authored here.

    Tokens stay UNEXPANDED. _expand_canon runs inside cmd_stills on both prompts and
    writes the expanded text into storyboard.json, so nothing downstream knows about canon.
    One string, one place, verbatim by construction.
    """
    return {
        "narration": row["narration"],
        "image_prompt": row["phenomenon"],
    }


def gate(rows, block):
    """Fail loudly, before spend."""
    WPM, CLIP = 143.0, 5.0
    wc = lambda s: len([t for t in s.split() if re.search(r"[A-Za-z0-9]", t)])
    errs = []
    if len(rows) != 40:
        errs.append(f"block {block}: {len(rows)} rows, expected 40")
    for r in rows:
        if not r["narration"].strip():
            errs.append(f"b{block} beat {r['clip_index']}: empty narration")
        if not r["phenomenon"].strip():
            errs.append(f"b{block} beat {r['clip_index']}: empty visual")
        if re.search(r"\{(\w+)\}", r["narration"]):
            errs.append(f"b{block} beat {r['clip_index']}: TOKEN IN NARRATION -- that column is measured")
        check_tokens(r["phenomenon"], f"b{block} beat {r['clip_index']}")
        for w in BANNED_VISUAL:
            if re.search(rf"\b{w}", r["phenomenon"], re.I):
                errs.append(f"b{block} beat {r['clip_index']}: BANNED VISUAL '{w}' -- see BANNED_VISUAL")
        if wc(r["narration"]) > 11:
            errs.append(f"b{block} beat {r['clip_index']}: {wc(r['narration'])} words > 11 ceiling")
    # sentence-span gate: words <= span * 11.9   (the REAL gate; the block total is a measurement)
    spans = {}
    for r in rows:
        spans.setdefault(r["sentence_id"], []).append(r)
    for sid, rs in spans.items():
        w = sum(wc(r["narration"]) for r in rs)
        cap = len(rs) * CLIP * WPM / 60.0
        if w > cap:
            errs.append(f"b{block} {sid}: {w} words > {cap:.1f} cap over {len(rs)} beats")
    return errs


def cmd_blocks():
    total_w = total_s = 0
    for block in (1, 2):
        rows = load(block)
        errs = gate(rows, block)
        if errs:
            print("\n".join("  GATE FAIL: " + e for e in errs)); raise SystemExit(1)
        beats = [to_beat(r, i) for i, r in enumerate(rows)]
        out = HERE.parent / f"moon-b{block:02d}-finish"
        out.mkdir(exist_ok=True)
        doc = {"canon": CANON, "beats": beats}
        (out / "beats.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False))
        wc = lambda s: len([t for t in s.split() if re.search(r"[A-Za-z0-9]", t)])
        w = sum(wc(r["narration"]) for r in rows)
        st = sum(int(r["variants"]) for r in rows)
        total_w += w; total_s += st
        print(f"  block {block}: 40 beats -> {out}/beats.json | {w} words | {st} stills | ${st*0.08:.2f}")
    print(f"\n  gates: PASS | {total_w} words | {total_s} stills | ${total_s*0.08:.2f} stills + ${2*40*0.42:.2f} kling")


def cmd_probe():
    picked, card = [], []
    for i, (block, clip, rule, question) in enumerate(PROBE):
        rows = load(block)
        row = next((r for r in rows if int(r["clip_index"]) == clip), None)
        if row is None:
            raise SystemExit(f"probe: block {block} has no beat {clip}")
        check_tokens(row["phenomenon"], f"probe b{block}/{clip}")
        picked.append(to_beat(row, i))
        card.append(f"| {i:2d} | b{block}/{clip:02d} | {rule:14s} | {question} | |")
    out = HERE.parent / "moon-probe-finish"
    out.mkdir(exist_ok=True)
    doc = {"canon": CANON, "beats": picked}
    (out / "beats.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False))

    from collections import Counter
    c = Counter(r for _, _, r, _ in PROBE)
    print(f"  {len(picked)} stills -> {out}/beats.json | ${len(picked)*0.08:.2f}")
    print("  slots:", " · ".join(f"{k} {v}" for k, v in c.most_common()))

    verdict = (HERE / "PROBE-CARD.md")
    verdict.write_text(
        "# Register probe — verdict card\n"
        "*Write the verdict BEFORE looking. Judging after is how you rationalise a bad render at frame 600.*\n\n"
        "**THE CHANGE UNDER TEST:** light moved out of `style_suffix` (the god-ray clause stamped every still)\n"
        "and into the beat. Every beat now names its own scene light. **An unlit prompt renders muddy.**\n\n"
        "**THE VERDICT IS BINARY PER SLOT. Any canary-earthly failure = the register is NOT locked, stop.**\n\n"
        "| # | beat | rule | question | PASS/FAIL |\n|---|---|---|---|---|\n"
        + "\n".join(card)
        + "\n\n## Overall\n- [ ] earthly canaries read BRIGHT with no stamped storm\n"
        "- [ ] cosmic beats hold MASS without glowing vapour (Balrog)\n"
        "- [ ] twelve gates are COUNTABLE, not texture\n"
        "- [ ] the gap in the machine has an image\n"
        "- [ ] no beat rendered dark/muddy for want of its own light\n\n"
        "**If any fail: fix the BEAT's light, not the suffix.** The suffix is palette. Light is content.\n"
    )
    print(f"  verdict card -> {verdict}")


REPROBE = [
    # ROUND 3 -- humans out of {heavens}.
    # FOUND 17 Jul: 4 of 5 wide shots WITH a man came back door-sized. The one WITHOUT was
    # instantly planetary. The model sizes the object to the person -> diorama.
    # THE CEILING ON THE HUMAN-SCALE RULE: "scale needs a human at the bottom of the frame"
    # works mountain-to-city. At PLANETARY scale the witness destroys scale instead of setting it.
    # The moon's own limb is the only reference that survives. TIGHT faces are exempt --
    # a close-up has no scale reference to corrupt.
    (1,  5, "no-human", "Gateway wider than the crater field -- or a door? (v3: man at the threshold)"),
    (1,  6, "no-human", "Figure the size of a mountain range, BOTH dwarfed by the limb."),
    (1, 16, "no-human", "Ranked openings running over the curve to a black horizon."),
    (2, 27, "no-human", "Scale from CRATER FIELDS, not a witness."),
    (2, 34, "no-human", "A crescent torn out. Black where rock should be. (best frame so far had no man)"),
]

def cmd_reprobe():
    picked, card = [], []
    for i,(block,clip,rule,q) in enumerate(REPROBE):
        row = next(r for r in load(block) if int(r["clip_index"])==clip)
        check_tokens(row["phenomenon"], f"reprobe b{block}/{clip}")
        picked.append(to_beat(row, i)); card.append(f"| {i+1:2d} | b{block}/{clip:02d} | {q} | |")
    out = HERE.parent / "moon-reprobe-finish"; out.mkdir(exist_ok=True)
    (out / "beats.json").write_text(json.dumps({"canon": CANON, "beats": picked}, indent=2, ensure_ascii=False))
    (HERE / "REPROBE-CARD.md").write_text(
        "# Re-probe — the steampunk fix\n\n"
        "**FOUND 17 Jul:** `mechanism` in an image_prompt renders as Victorian clockwork.\n"
        "A literal-metaphor violation (3A.2) on the film's own central word.\n\n"
        "**THE FIX:** narration says machine; the image renders cyclopean cut stone, nothing moving.\n\n"
        "| # | beat | question | PASS/FAIL |\n|---|---|---|---|\n" + "\n".join(card) +
        "\n\n- [ ] zero gears, cogs, chains, rivets anywhere\n- [ ] mass and shadow held (Balrog)\n"
        "- [ ] the descending host reads COLOSSAL\n- [ ] the gap reads as ABSENCE, not an aperture\n")
    print(f"  {len(picked)} stills -> {out}/beats.json | ${len(picked)*0.08:.2f}")
    print(f"  card -> {HERE}/REPROBE-CARD.md")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "blocks": cmd_blocks()
    elif cmd == "probe": cmd_probe()
    elif cmd == "reprobe": cmd_reprobe()
    else: raise SystemExit(__doc__)
