#!/usr/bin/env python3
"""
build_moon.py -- beat table CSV -> engine beats.json, and the register probe.

  python3 build_moon.py film            # $0 -- the WHOLE film: silence, spectacle, duplicates
  python3 build_moon.py normalise       # $0 -- recompute derived columns in the master, in place
  python3 build_moon.py sweep           # $0 -- setting mix, object-led ratio, banned words. RUN FIRST.
  python3 build_moon.py blocks [N ...]  # -> moon-bNN-finish/beats.json (default: every CSV present)
  python3 build_moon.py audio           # $0 -- one narration.txt for the whole film\n  python3 build_moon.py calibrate J    # measure whisper.json vs the 5s grid, print per-beat fix
  python3 build_moon.py probe           # -> moon-probe-finish/beats.json  (16 stills, $1.28)
  python3 build_moon.py reprobe         # -> moon-reprobe-finish/beats.json (5 stills, $0.40)
  python3 build_moon.py probe3          # -> moon-probe3-finish/beats.json (10 stills, $0.80)
  python3 build_moon.py probe4          # -> moon-probe4-finish/beats.json (10 stills, $0.80)
  python3 build_moon.py probe5          # -> moon-probe5-finish/beats.json (10 stills, $0.80)
  python3 build_moon.py probe6          # -> moon-probe6-finish/beats.json (10 stills, $0.80)
  python3 build_moon.py probe7          # -> moon-probe7-finish/beats.json (10 stills, $0.80)
  python3 build_moon.py probe7          # -> moon-probe7-finish/beats.json (10 stills, $0.80)

Run from sacred-dawn/projects/enoch-moon/.  Reads beats/moon_master.csv + canon.json.

TOKENS ARE NOT EXPANDED HERE.  (The old docstring said they were, and the code never did it --
_LEGO.md's own law applied to itself: the artifact beat the comment.)  cmd_blocks emits
{"canon": ..., "beats": [...]} and `stills --beats` expands both image_prompt and motion_prompt
into storyboard.json via _expand_canon (FLAGS #8, verified against cmd_stills).  One string,
one place, verbatim by construction.  check_tokens below only GATES -- it raises at authoring
time, for free, instead of at render time, for money.
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
    "plated", "seamed", "colonnade",   # STAR DESTROYER + colonnade wells, block 1 full render
    # BLOCK 5's metaphor, banned BEFORE it renders rather than after. `chariot` is a worse
    # literal-metaphor bomb than `mechanism` was: the model has a perfect reference for it and it
    # comes with horses. `wheel` additionally drags Ezekiel into any biblical prompt.
    # THE RESOLUTION, same as machine: the narration says chariot. The image renders the moon
    # ITSELF under way -- dust torn off the rims, streaming one direction, a world in motion.
    # The vehicle IS the moon, which is the film's own conceit. The viewer supplies the word.
    "chariot", "horse", "wheel", "axle", "rein", "yoke", "quadriga", "cart", "wagon", "harness",
]

# NOT banned -- DEPRECATED. A gateway is a thing you walk through, so it carries human scale and
# renders door-sized. Every de-doored beat says "openings cut into the lunar rock" instead. Kept
# out of the gate because the fix is a rewrite of the composition, not a word swap.
SOFT_VISUAL = ["gateway", "gateways", "doorway", "archway", "portal"]

# Object-led sweep (FLAGS #5a). Sacred Dawn's authority is not "look at the evidence" -- it is
# "look at what they were looking at." Block 2 draft 1 was 27/40 object-led. Fixed: 11/40.
OBJECT_LED = [
    "page", "pages", "codex", "scroll", "roll", "rolls", "fragment", "tablet", "clay",
    "vellum", "manuscript", "book", "spine", "leather", "numeral", "numerals", "script",
    "ink", "wedge mark", "reading stand", "printed", "verses",
]

# Humans inside {heavens}: the token itself now says "no people, no human figures". A beat that
# asks for one is a prompt fighting its own canon. REPORTED, never gated -- the resolution is a
# judgement call (drop the token from tight faces; move wides out of {heavens}), not a rewrite.
HUMAN_REQ = re.compile(
    r"(\bfigures?\b|the man's|\ba man\b|\bmen\b|\bwoman\b|\bchild\b|human silhouette|"
    r"face turned|astronaut|\bcrowd|\bpeople\b)", re.I)


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

# ---------------------------------------------------------------- block 3 probe
# THE CHANGE UNDER TEST, per PHASE 3's first-rule-that-fires:
#   (a) {horizon} -- a NEW canon token, never rendered. Earthly canary, mandatory.
#   (b) THE LOCKED FRAME -- beats 9-15 and 20-26 are verbatim-identical prompts with ONE variable
#       moved. If the frame does not hold, the sequence reads as seven unrelated shots and the
#       block's argument evaporates. Novel composition class; a failure costs the payload.
#   (c) the small windows -- a density this film has never asked for.
PROBE3 = [
    (3,  1, "canary-cosmic",  "Six openings COUNTABLE on a planetary limb? No door, no star destroyer?"),
    (3, 10, "novel",          "LOCKED FRAME: is this the SAME rank as beat 9 with the light one along?"),
    (3, 13, "novel",          "The rank STOPPING DEAD at the limb -- reads as an end, or as a crop?"),
    (3, 18, "canary-earthly", "{horizon} first render: BRIGHT, flat ridgeline, no ruins, no murk?"),
    (3, 21, "novel",          "Same ridge, same cairn, moon moved LEFT of it. Is the ridge identical to 20?"),
    (3, 26, "novel",          "THE PAYOFF -- moon at the far end of the cairn row. Does the scale read?"),
    (3, 30, "known-failure",  "Ge'ez numeral + fraction: garbled? (expect yes -- know it for $0.08)"),
    (3, 36, "novel",          "Stars standing IN the windows -- ranked points, or a starfield behind rock?"),
    (3, 37, "novel",          "The whole face as one ruled wall. Immense, or a texture map?"),
    (3, 40, "novel",          "The closer: a column of light with NO SOURCE. A poster, or a lens flare?"),
]


# ---------------------------------------------------------------- block 4 probe
# THE CHANGE UNDER TEST:
#   (a) {interior} -- a NEW canon token, never rendered, and the first time the film goes inside
#       the thing the title names. Three slots: it is the block's whole spine.
#   (b) THE TOKENLESS BEAT -- beats 23/24/27/28 carry NO canon token. A close-up has no place:
#       there is no setting to lock and no scale reference to corrupt, and {highland}'s "bare rock,
#       dry scrub" would drag land into a pure-sky telephoto. If this holds it retires the
#       four contradicted {heavens} face beats in blocks 1-2 by the same rule.
#   (c) the locked band sequence again, one exact step per beat.
PROBE4 = [
    (4,  7, "change-token",   "{interior} FIRST RENDER: a squared void cut from lunar rock -- or a cathedral?"),
    (4,  4, "change-token",   "{interior}: bright squares in a RULED ROW on the floor. Countable, or a light show?"),
    (4, 40, "change-token",   "{interior} closer: colossal, empty, no source. Or a corridor?"),
    (4, 21, "canary-earthly", "{highland} blazing afternoon: bright, no murk, sun and moon the same width?"),
    (4, 10, "canary-cosmic",  "Every opening BLACK across the limb. Reads as EMPTY, or as unlit rock?"),
    (4, 28, "novel",          "TOKENLESS: the eclipse ring. Does a beat with no canon token hold together?"),
    (4, 33, "novel",          "LOCKED FRAME: same crater field as 32, band one exact step wider?"),
    (4,  9, "known-failure",  "One opening tight WITH the rank behind it. Door, or a hole in a planet?"),
    (4, 16, "novel",          "The sun beyond the limb so bright the lit rock reads grey. Or blown out?"),
    (4, 38, "known-failure",  "Ge'ez grid: legible ruling, or mush? (expect mush -- know it for $0.08)"),
]


# ---------------------------------------------------------------- block 5 probe
# THE CHANGE UNDER TEST: the film MOVES for the first time.
#   (a) STREAMING DUST inside {heavens} -- the token says "no atmosphere" and 32 beats now ask for
#       matter blown off the surface in one direction. That is the block's entire answer to
#       `chariot`, and if the token vetoes it the block has no image. Three slots.
#   (b) THE FAR SIDE -- a composition class the film has never asked for, and the payoff of a
#       negation: {heavens} says "no earth", so the film has been behind the moon all along.
#   (c) THE FOUR-QUARTER LOCKED FRAME -- same face, four light angles, one per name.
PROBE5 = [
    (5,  3, "change-dust",    "MOON UNDER WAY: dust torn off the rims and trailing. Or a static rock?"),
    (5, 12, "change-dust",    "'The wind.' Whole body streaming one direction -- or {heavens} vetoing it?"),
    (5, 15, "canary-earthly", "{ridge} at night, scrub blowing, robe streaming: BRIGHT, or has murk returned?"),
    (5, 21, "novel",          "The far side under way, dust trail curving behind. Poster, or a comet?"),
    (5, 23, "canary-cosmic",  "Unfamiliar crater fields, no earth. Planetary, or a rock in a fog?"),
    (5, 29, "novel",          "Face divided into FOUR exact quarters by light. Countable, or a pattern?"),
    (5, 31, "novel",          "LOCKED FRAME: same face as 30 with the light moved. Same rock, or a new moon?"),
    (5, 40, "novel",          "THE CLOSER -- four black windows in a wall of lit ones. Legible at a glance?"),
    (5,  4, "known-failure",  "One Ge'ez word alone: garbled? (expect yes -- know it for $0.08)"),
    (5,  8, "novel",          "'Built and driven': does ordered stone plus motion read without a vehicle?"),
]


# ---------------------------------------------------------------- block 6 probe
# THE CHANGE UNDER TEST: the first block with a PERSON in it, and the first that must render a
# being without breaking the Balrog rule.
#   (a) THE TOKENLESS FACE at volume -- 11 beats. Block 4 proved the law on 4 sky shots. If it
#       holds on faces it retires the four contradicted {heavens} face beats in blocks 1-2.
#   (b) THE ABSENCE -- 5, 6, 30, 31: the text says somebody was with him; the frame shows one man
#       alone, pointing. Deliberate emptiness beside a figure is a composition the model will
#       want to fill. If it puts a second figure in, the block's argument inverts.
#   (c) the recurring figure at close range (LEGO 5: "anonymous, never faceless" -- Enoch is the
#       one face that recurs, and beat 40 looks straight at camera).
PROBE6 = [
    (6,  1, "change-token",   "TOKENLESS FACE: a real ancient face, hard-lit, no place. Or floating in soup?"),
    (6, 16, "change-token",   "Eyes alone filling frame. Retains, or uncanny?"),
    (6, 40, "novel",          "THE CLOSER -- eyes direct to camera. Thumbnail candidate, or a portrait?"),
    (6, 31, "novel",          "THE ABSENCE: one man pointing, NOBODY beside him. Or has the model added one?"),
    (6, 30, "novel",          "'no second shadow anywhere' -- does the negation hold, or invite what it names?"),
    (6, 21, "canary-earthly", "{hermon} colossal figure, weight and shadow, BRIGHT. Balrog, or vapour?"),
    (6, 19, "canary-cosmic",  "'nothing standing anywhere on it' -- empty limb, or a figure invented?"),
    (6, 36, "novel",          "A squared shaft cut into Hermon, bottom lost in black. Reads as the pit?"),
    (6, 27, "known-failure",  "Ge'ez part-finished column, wet ink: legible? (expect mush -- $0.08 to know)"),
    (6, 24, "novel",          "Head tilted toward an empty space at his shoulder. Reads as LISTENING?"),
]


# ---------------------------------------------------------------- block 7 probe
# THE CHANGE UNDER TEST: this block's argument is arithmetic, and arithmetic has to be SEEN.
#   (a) THE DRIFT -- 14/36/37/38 detonate block 3's cairn row. The whole payload is "the sun is
#       standing at the wrong cairn." If the row does not read as a ruled scale, the block has no
#       proof and reverts to a man asserting a number. Three slots.
#   (b) THE SEAM -- 5/6/16: the page where the ruled columns stop and running script begins.
#       Block 1 rendered that shot the other way round and it worked; this is the mirror.
#   (c) BROKEN ORDER -- 20/24: a rank with gaps, a moon in the wrong place. The film has spent six
#       blocks teaching the model that everything is even and ordered. Now it must render WRONG,
#       and "wrong" is exactly what a model smooths away.
PROBE7 = [
    (7, 38, "novel",          "THE PAYOFF -- sun at the far WRONG end of the cairn row. Does the error read?"),
    (7, 14, "novel",          "'Error.' Sun three cairns off the end. Legible as a mistake, or just a sunrise?"),
    (7, 37, "novel",          "Sun a hand's width off the cairn it should sit behind. Or has it snapped on?"),
    (7,  6, "known-failure",  "THE SEAM: ruled line above, running script below, two hands. Or Ge'ez mush?"),
    (7, 20, "novel",          "Windows with the ranks BROKEN, gaps in the order. Or has the model tidied it?"),
    (7, 24, "novel",          "Moon far right of where it broke before. Reads as wrong, or as a moonrise?"),
    (7, 19, "canary-earthly", "{highland} bleached and empty under a blazing sky: bright, or has murk returned?"),
    (7, 31, "canary-cosmic",  "Face divided into FOUR exact quarters. Countable, or a pattern?"),
    (7, 40, "novel",          "THE CLOSER -- the moon exactly where it always was, ordinary, bright. Lands?"),
    (7,  1, "change-token",   "TOKENLESS FACE again, eyes to camera. Consistent with block 6 beat 40?"),
]


# ---------------------------------------------------------------- block 7 probe
# THE CHANGE UNDER TEST: the block's argument is a MISMATCH, and every failure mode here is the
# model smoothing it away.
#   (a) THE INSERTED STONE -- 29/30/31/32/33/36/37/40. A short run of paler stone whose courses
#       do not line up, standing in a rank that is otherwise perfect. The model's whole instinct
#       is to make a wall look right. If it harmonises the join, block 7 has no image and the
#       splice is unfilmable. Four slots: this is the payload.
#   (b) THE BROKEN ORDER -- 24/26: two openings lit at once, star-points out of place. The same
#       risk inverted: the model wants pattern.
#   (c) {horizon} IN RAIN and the drifted cairn -- block 3 built the instrument, block 7 shows it
#       failing. If the ridge is not identical to block 3's the whole payoff evaporates.


def check_tokens(text: str, where: str) -> None:
    """The engine expands. We only GATE -- every token must resolve, before spend.
    _expand_canon raises at render time; this raises at authoring time, for free."""
    for k in re.findall(r"\{(\w+)\}", text):
        if k not in CANON:
            raise SystemExit(f"{where}: unknown setting token {{{k}}} -- add it to canon.json")


def wc(s: str) -> int:
    """Standalone punctuation is not a word. The prosody rule MANDATES em-dashes over full stops,
    so a naive split() penalises exactly the writing the doctrine requires. (FLAGS #22.)"""
    return len([t for t in s.split() if re.search(r"[A-Za-z0-9]", t)])


MASTER = HERE / "beats" / "moon_master.csv"


def load_master():
    """One table. One order. The blocks are a render/audio/pick unit, not an authoring unit --
    block_id was always a column. (_LEGO.md 3: nothing else knows the ORDER.)"""
    if not MASTER.is_file():
        raise SystemExit(f"missing {MASTER} -- run patch_merge_master.py on the LAPTOP first")
    rows = list(csv.DictReader(MASTER.open()))
    order = [(int(r["block_id"]), int(r["clip_index"])) for r in rows]
    if order != sorted(order):
        raise SystemExit("master is out of order -- run `build_moon.py normalise`")
    return rows


def blocks_present():
    return sorted({int(r["block_id"]) for r in load_master()})


def load(block: int):
    rows = [r for r in load_master() if int(r["block_id"]) == block]
    if not rows:
        raise SystemExit(f"master has no block {block}")
    return rows


def derive(row):
    """Recompute every derived cell from the authored ones. The TOKEN is the truth; `setting` is
    a label. Five derived columns were five places to drift -- b1/15 said heavens and rendered
    {ascent} for a day. Now it cannot."""
    m = re.findall(r"\{(\w+)\}", row["phenomenon"])
    row["setting"] = m[0] if m else "none"
    row["words"] = str(wc(row["narration"]))
    v = 4 if row["weight"] == "hero" else 2
    row["variants"] = str(v)
    row["still_cost"] = f"{v * 0.08:.2f}"
    row["clip_cost"] = "0.42"
    row["beat_cost"] = f"{v * 0.08 + 0.42:.2f}"
    return row


def cmd_normalise(argv):
    """Recompute the derived columns in the master, in place, idempotently. Run after every edit.
    Authored: clip_index, block_id, sentence_id, weight, register, narration, phenomenon."""
    rows = list(csv.DictReader(MASTER.open()))
    before = [dict(r) for r in rows]
    rows.sort(key=lambda r: (int(r["block_id"]), int(r["clip_index"])))
    for r in rows:
        derive(r)
    changed = sum(1 for a, b in zip(before, rows) if a != b)
    fields = list(before[0].keys())
    with MASTER.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"  normalised {len(rows)} rows | {changed} changed")


def to_beat(row, index: int) -> dict:
    """The schema `stills --beats` reads. Verified against cmd_stills, not inferred.

      b["image_prompt"]          REQUIRED -- no .get(), a missing key is a KeyError
      b.get("motion_prompt")     optional -> falls back to channel.json default_motion
      b.get("narration", "")     optional

    NOT the parse leg's schema (visual/mode/component/found_line) -- that is a different
    artifact that happens to share the filename beats.json. Read the consumer, not a neighbour.

    motion_prompt is deliberately OMITTED: motion is derived at PHASE 6 from
    beat x variant x register, after the pick. Never authored here.
    """
    return {
        "narration": row["narration"],
        "image_prompt": row["phenomenon"],
    }


def gate_canon():
    """The canon is expanded into EVERY prompt that uses it. BANNED_VISUAL has only ever been
    swept against the beat table -- one banned word in {heavens} contaminates 160 beats at once
    and nothing would have caught it. Sweep the thing that is actually consumed."""
    errs = []
    for k, v in CANON.items():
        for w in BANNED_VISUAL:
            if re.search(rf"\b{w}", v, re.I):
                errs.append(f"canon {{{k}}}: BANNED VISUAL '{w}' -- it would reach every beat "
                            f"that uses this token")
    return errs


# GATE 2: HERO = COLLISION.
# MEASURED across 320 beats: 9 of the film's 11 spectacle frames name TWO unlike things at true
# scale in one frame -- ziggurat AND moon, cairn row AND moon, a man AND nothing. 41 of 133 hero
# beats named ONE subject; those are wallpaper wearing a hero badge, and they are the
# same-similar-moon problem. A single object, however colossal, is not a spectacle.
# This is crude as a regex and exact as a discipline: if you cannot say what a hero frame
# COLLIDES, it is not a hero frame. Demote it to connective -- it can still render, it just does
# not earn four candidates and a pick sitting.
DOMAIN = {
    "machine": r"\b(ranked|rank|openings?|windows?|cut stone|dressed (rock|stone)|jamb|courses|limb|crater)",
    "human":   r"\b(figure|silhouette|face|eyes|hand|robed|shoulder|men|man)\b",
    # `earth` itself was missing and it is the film's most important collision -- the moon AND
    # the world it is for. The gate rejected "the bright curve of the earth through the hole in
    # the moon" as a single subject. A crude gate that vetoes the best frame is worse than none.
    "earth":   r"\b(earth|world|ridge|ridgeline|escarpment|scrub|boulder|cairn|desert|cliff|mountain|summit|plain|land|sand|rain|grain|terrace|frost)",
    # `the sun` missed "the raw white sun". \bsun\b is safe -- it does not match "sunlight",
    # which has no word boundary after "sun". Third regex gap in three blocks: the DOMAIN map is
    # the crudest thing in this file and every hole in it vetoes a real frame.
    "sun":     r"\b(sun|sunrise|solar)\b",
    "built":   r"\b(ziggurat|chapel|codex|stand|wall|house|caravan)",
    "water":   r"\b(water|sea|flood|river|salt)",
    "text":    r"\b(page|ge'ez|numeral|script|ink|fragment|scroll|roll|cuneiform)",
    "motion":  r"\b(streaming|torn off|trailing|blowing|descending|pouring|breaking)",
}


def domains(p):
    return {k for k, v in DOMAIN.items() if re.search(v, p, re.I)}


def gate(rows, block):
    """Fail loudly, before spend. One-directional: under-run is safe, the tail is a pad."""
    WPM, CLIP = 143.0, 5.0
    errs = []
    if len(rows) != 40:
        errs.append(f"block {block}: {len(rows)} rows, expected 40")
    for r in rows:
        at = f"b{block} beat {r['clip_index']}"
        if not r["narration"].strip():
            errs.append(f"{at}: empty narration")
        if not r["phenomenon"].strip():
            errs.append(f"{at}: empty visual")
        if re.search(r"\{(\w+)\}", r["narration"]):
            errs.append(f"{at}: TOKEN IN NARRATION -- that column is measured")
        check_tokens(r["phenomenon"], at)
        for w in BANNED_VISUAL:
            if re.search(rf"\b{w}", r["phenomenon"], re.I):
                errs.append(f"{at}: BANNED VISUAL '{w}' -- see BANNED_VISUAL")
        if wc(r["narration"]) > 11:
            errs.append(f"{at}: {wc(r['narration'])} words > 11 ceiling")
        if r["weight"] == "hero" and len(domains(r["phenomenon"])) < 2:
            errs.append(f"{at}: HERO names one subject "
                        f"{sorted(domains(r['phenomenon'])) or '[]'} -- a hero frame must "
                        f"COLLIDE two things. Give it a second subject or set weight=connective")
        d = derive(dict(r))
        for c in ("setting", "words", "variants", "still_cost", "beat_cost"):
            if r.get(c) != d[c]:
                errs.append(f"{at}: derived column {c}={r.get(c)} != computed {d[c]}"
                            f" -- run `build_moon.py normalise`")
    # sentence-span gate: words <= span * 11.9   (the REAL gate; the block total is a measurement)
    spans = {}
    for r in rows:
        spans.setdefault(r["sentence_id"], []).append(r)
    for sid, rs in spans.items():
        w = sum(wc(r["narration"]) for r in rs)
        cap = len(rs) * CLIP * WPM / 60.0
        if w > cap:
            errs.append(f"b{block} {sid}: {w} words > {cap:.1f} cap over {len(rs)} beats")
        # THE FLOOR (17 Jul, measured). Under-run is safe for the BLOCK -- the tail pads.
        # It is NOT safe for the SENTENCE: the pad has to fit in a break and Inworld caps one
        # break at 10s. floor = span*11.9 - 10s of speech = len(rs)*11.9 - 23.8 words.
        pad = len(rs) * CLIP - w * 60.0 / WPM
        if pad > 10.0:
            errs.append(f"b{block} {sid}: {pad:.1f}s of pad over {len(rs)} beats "
                        f"({w} words) -- ONE break caps at 10s. Need >= "
                        f"{max(0, len(rs)*11.9 - 23.8):.0f} words, or split the sentence")
    return errs


def cmd_blocks(argv):
    ce = gate_canon()
    if ce:
        print("\n".join("  CANON FAIL: " + e for e in ce)); raise SystemExit(1)
    wanted = [int(a) for a in argv] or blocks_present()
    total_w = total_s = 0
    for block in wanted:
        rows = load(block)
        errs = gate(rows, block)
        if errs:
            print("\n".join("  GATE FAIL: " + e for e in errs)); raise SystemExit(1)
        beats = [to_beat(r, i) for i, r in enumerate(rows)]
        out = HERE.parent / f"moon-b{block:02d}-finish"
        out.mkdir(exist_ok=True)
        (out / "beats.json").write_text(
            json.dumps({"canon": CANON, "beats": beats}, indent=2, ensure_ascii=False))
        w = sum(wc(r["narration"]) for r in rows)
        st = sum(int(r["variants"]) for r in rows)
        total_w += w; total_s += st
        print(f"  block {block}: {len(rows)} beats -> {out}/beats.json | {w} words "
              f"({w/len(rows):.1f}/beat) | {st} stills | ${st*0.08:.2f}")
    n = len(wanted)
    print(f"\n  gates: PASS | {total_w} words | {total_s} stills | "
          f"${total_s*0.08:.2f} stills + ${n*40*0.42:.2f} kling")


WPM_S = 143.0


def spans_of(rows):
    d = {}
    for r in rows:
        d.setdefault(r["sentence_id"], []).append(r)
    return d


def cmd_sweep(argv):
    """FLAGS #5. The register gate is a beat-table SWEEP, not a doc. Two commands, ten seconds.
    Scrubbing a document does not scrub the authoring -- so COUNT the draft before you read it."""
    wanted = [int(a) for a in argv] or blocks_present()
    for block in wanted:
        rows = load(block)
        setting = {}
        for r in rows:
            for k in re.findall(r"\{(\w+)\}", r["phenomenon"]):
                setting[k] = setting.get(k, 0) + 1
        obj = [r["clip_index"] for r in rows
               if any(re.search(rf"\b{w}", r["phenomenon"], re.I) for w in OBJECT_LED)]
        ban = [(r["clip_index"], w) for r in rows for w in BANNED_VISUAL
               if re.search(rf"\b{w}", r["phenomenon"], re.I)]
        soft = [(r["clip_index"], w) for r in rows for w in SOFT_VISUAL
                if re.search(rf"\b{w}\b", r["phenomenon"], re.I)]
        # "no people" is the token doing its job. Strip every negation before matching, or the
        # sweep reports the fix as the failure.
        hum = [r["clip_index"] for r in rows
               if "{heavens}" in r["phenomenon"]
               and HUMAN_REQ.search(re.sub(r"\bno [a-z ]+?(?=,|\.|$)", "", r["phenomenon"], flags=re.I))]
        unlit = [r["clip_index"] for r in rows if not re.search(
            r"\b(light|lit|sunlight|moonlight|daylight|blazing|brilliant|bright|starlight|"
            r"backlit|rim-lit|shadow|silhouette)\b", r["phenomenon"], re.I)]
        notok = [r["clip_index"] for r in rows if not re.search(r"\{\w+\}", r["phenomenon"])]
        hero = sum(1 for r in rows if r["weight"] == "hero")
        w = sum(wc(r["narration"]) for r in rows)
        n = len(rows)

        print(f"\n== BLOCK {block} ==  {n} beats | {w} words ({w/n:.1f}/beat, "
              f"{100*(1-(w/n)/11.9):.0f}% air) | hero {hero}/{n} | "
              f"{sum(int(r['variants']) for r in rows)} stills")
        print("   setting mix : " + "  ".join(f"{k} {v}" for k, v in
                                              sorted(setting.items(), key=lambda x: -x[1])))
        print(f"   object-led  : {len(obj)}/{n}"
              + ("   <-- ARTIFACT TOURISM (block 2 draft 1 was 27/40)" if len(obj) > 12 else "")
              + (f"   {obj}" if obj else ""))
        print(f"   BANNED      : {'none' if not ban else ban}")
        print(f"   deprecated  : {'none' if not soft else soft}")
        print(f"   humans in {{heavens}} : {'none' if not hum else hum}"
              + ("   <-- the token negates them; the beat requests them" if hum else ""))
        print(f"   tokenless   : {'none' if not notok else notok}"
              + ("   (a close-up has no place -- deliberate, or a dropped token?)" if notok else ""))
        speech = w * 60.0 / WPM_S
        pads = []
        for sid, rs in spans_of(rows).items():
            sw = sum(wc(r["narration"]) for r in rs)
            pads.append((len(rs)*5.0 - sw*60.0/WPM_S, sid, len(rs), sw))
        thin = sorted([x for x in pads if x[2] > 1 and x[0]/(x[2]-1) > 2.5], reverse=True)
        print(f"   timing      : {speech:.0f}s speech in 200s -> {200-speech:.0f}s air "
              f"({100*(200-speech)/200:.0f}%) | {len(pads)} sentences | "
              f"{sum(1 for p,_,_,_ in pads if p > 0.05)}-40 breaks -> "
              f"{max(2, -(-len(pads)//20))} TTS requests min (20/request cap)")
        print(f"   thin sents  : {'none' if not thin else [f'{sid} {n}b/{sw}w {p:.1f}s' for p,sid,n,sw in thin[:3]]}"
              + ("   <-- pad lands INSIDE the sentence; whisper will find it" if thin else ""))
        print(f"   unlit beats : {'none' if not unlit else unlit}"
              + ("   <-- an unlit prompt renders muddy" if unlit else ""))


SEAM_PAUSE = "------"   # 2-3s held silence at a block seam, for the music swell. Authored,
                       # not a pipeline feature: it lives in the beat's narration as plain text.


def cmd_audio(argv):
    """$0. Emit ONE plain-text narration for the whole film -> narration.txt.

    THE MODEL (Peter, 18 Jul): the VO sits ABOVE the clips. One continuous track, one Inworld
    call, sentences flow across the 5s clip boundaries. No SSML, no breaks, no per-block calls,
    no 20-cap -- Inworld takes plain text and dashes carry the prosody. A block seam is just a
    beat ending in '------' (SEAM_PAUSE) to hold ~2-3s for the music swell.

    Beats join with a single space; the punctuation already in each beat does all the work.
    Sentences that span beats (71 of them) join mid-phrase, exactly as Elliot should read them.

    This is a HYPOTHESIS: this sequence of words will fill this sequence of 5s clips. You render
    it (cents), whisper it, and `calibrate` measures the truth. Then adjust words/dashes and
    repeat. Nothing here is assumed -- the rate comes out of the measurement, not into it.
    """
    rows = load_master()
    text = " ".join(r["narration"].strip() for r in rows)
    out = HERE / "narration.txt"
    out.write_text(text + "\n")
    words = sum(wc(r["narration"]) for r in rows)
    seams = sum(1 for r in rows if SEAM_PAUSE in r["narration"])
    print(f"  {len(rows)} beats -> {out}")
    print(f"  {words} words | {len(text)} chars | {seams} seam pauses (------)")
    print(f"  ONE Inworld call. Paste narration.txt, render, whisper, then: build_moon.py calibrate <whisper.json>")


def _dash_seconds(rows, per_word):
    """What a trailing dash-run is worth, MEASURED later. Until calibrate has run once we don't
    know; this returns None and calibrate fills it from actuals. Placeholder for the estimate path."""
    return None


def cmd_calibrate(argv):
    """The measurement half of the loop. Eats whisper JSON + the master, prints per-beat over/under
    and the WORDS to add/cut to close each gap -- at the rate MEASURED from this very render, so it
    self-calibrates. Flags cumulative drift at every 40-beat seam (block boundary must land on the
    200.000s grid or the video assembly de-syncs from the animation).

      build_moon.py calibrate voiceover.json

    whisper JSON: {"segments":[{"words":[{"word":"...","start":s,"end":s}, ...]}, ...]}
    """
    import json
    if not argv:
        raise SystemExit("usage: build_moon.py calibrate <whisper.json>")
    wj = json.loads(Path(argv[0]).read_text())
    words = [w for seg in wj.get("segments", []) for w in seg.get("words", [])]
    if not words:
        raise SystemExit("no word timestamps in whisper JSON -- render with --word_timestamps True")
    norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
    stream = [(norm(w["word"]), w.get("start"), w.get("end")) for w in words if norm(w["word"])]

    rows = load_master()
    # walk the whisper stream, consuming each beat's word count; the beat's end = last word's end.
    si = 0
    measured = []
    ok = True
    for r in rows:
        n = wc(r["narration"])
        if si + n > len(stream):
            ok = False; measured.append((r, None, None)); continue
        start = stream[si][1]
        end = stream[si + n - 1][2]
        si += n
        measured.append((r, start, end))
    if not ok:
        print("  WARN: whisper stream ran out before the last beat -- word-match drifted. "
              "Check the render matches narration.txt exactly.")

    # measured global rate
    spoken_words = sum(wc(r["narration"]) for r, s, e in measured if s is not None)
    span = next((e for r, s, e in reversed(measured) if e is not None), None)
    first = next((s for r, s, e in measured if s is not None), 0.0)
    if span:
        wpm = spoken_words / ((span - first) / 60.0)
        per_word = (span - first) / spoken_words
        print(f"  MEASURED: {spoken_words} words in {span-first:.1f}s = {wpm:.0f} WPM "
              f"| 1 word ~= {per_word:.2f}s")
    else:
        per_word = 60.0 / 184.0
        print("  (no span; using 184 WPM fallback)")

    print(f"\n  {'beat':>7} {'words':>5} {'measured':>9} {'target':>7} {'over/under':>11} {'fix':>14}")
    cum_seam = 0.0
    for i, (r, start, end) in enumerate(measured):
        if start is None:
            print(f"  {r['block_id']}/{r['clip_index']:>2}   -- unmeasured --"); continue
        dur = end - start
        seam = SEAM_PAUSE in r["narration"]
        target = 5.0  # every clip is 5s; a seam beat is deliberately longer, flagged not fixed
        delta = dur - target
        if seam:
            fix = "SEAM (hold)"
        elif abs(delta) < 0.25:
            fix = "ok"
        else:
            dw = round(delta / per_word)
            fix = f"{'cut' if dw>0 else 'add'} {abs(dw)}w"
        print(f"  {r['block_id']}/{r['clip_index']:>2} {wc(r['narration']):>5} "
              f"{dur:>7.2f}s {target:>6.1f}s {delta:>+9.2f}s {fix:>14}")
        # seam drift: cumulative error since last 40-beat boundary
        cum_seam += delta
        if (i + 1) % 40 == 0:
            print(f"  ----- block {(i+1)//40} seam: cumulative drift {cum_seam:+.2f}s "
                  f"(block should end on {(i+1)*5.0:.0f}.0s grid) -----")
            cum_seam = 0.0


def cmd_probe(slots=PROBE, out_name="moon-probe-finish", card_name="PROBE-CARD.md"):
    picked, card = [], []
    for i, (block, clip, rule, question) in enumerate(slots):
        rows = load(block)
        row = next((r for r in rows if int(r["clip_index"]) == clip), None)
        if row is None:
            raise SystemExit(f"probe: block {block} has no beat {clip}")
        check_tokens(row["phenomenon"], f"probe b{block}/{clip}")
        picked.append(to_beat(row, i))
        # FLAGS #19: print the SHOT number the stills carry, not the array index.
        card.append(f"| shot_{i+1:03d} | b{block}/{clip:02d} | {rule:14s} | {question} | |")
    out = HERE.parent / out_name
    out.mkdir(exist_ok=True)
    (out / "beats.json").write_text(
        json.dumps({"canon": CANON, "beats": picked}, indent=2, ensure_ascii=False))

    from collections import Counter
    c = Counter(r for _, _, r, _ in slots)
    print(f"  {len(picked)} stills -> {out}/beats.json | ${len(picked)*0.08:.2f}")
    print("  slots: " + " | ".join(f"{k} {v}" for k, v in c.most_common()))

    verdict = HERE / card_name
    verdict.write_text(
        "# Register probe -- verdict card\n"
        "*Write the verdict BEFORE looking. Judging after is how you rationalise a bad render at frame 600.*\n\n"
        "**THE VERDICT IS BINARY PER SLOT. Any canary-earthly failure = the register is NOT locked, stop.**\n\n"
        "| shot | beat | rule | question | PASS/FAIL |\n|---|---|---|---|---|\n"
        + "\n".join(card)
        + "\n\n## Overall\n"
          "- [ ] earthly canaries read BRIGHT with no stamped storm\n"
          "- [ ] cosmic beats hold MASS without vapour (Balrog)\n"
          "- [ ] the openings are COUNTABLE, not texture\n"
          "- [ ] no single opening reads as a door\n"
          "- [ ] no beat rendered dark or muddy for want of its own light\n\n"
          "**If any fail: fix the BEAT's light, not the suffix.** The suffix is palette. Light is content.\n\n"
          "**Before you spend: count the beats in the CONSUMED beats.json.** A generated artifact is\n"
          "stale until you have read it. (FLAGS #21 -- $0.64 for a round that tested nothing.)\n")
    print(f"  card -> {verdict}")


def cmd_reprobe():
    cmd_probe(REPROBE, "moon-reprobe-finish", "REPROBE-CARD.md")


def cmd_probe3():
    cmd_probe(PROBE3, "moon-probe3-finish", "PROBE3-CARD.md")


def cmd_probe4():
    cmd_probe(PROBE4, "moon-probe4-finish", "PROBE4-CARD.md")


def cmd_probe5():
    cmd_probe(PROBE5, "moon-probe5-finish", "PROBE5-CARD.md")


def cmd_probe6():
    cmd_probe(PROBE6, "moon-probe6-finish", "PROBE6-CARD.md")


def cmd_probe7():
    cmd_probe(PROBE7, "moon-probe7-finish", "PROBE7-CARD.md")


def cmd_film(argv):
    """$0. The whole film in one read: silence, prosody, pick load, contrast, subject, duplicates.
    Targets are _LEGO.md's -- 5 says ~25% hero; 4 says 380 words/block = 20% air; 3A.2 says a
    poster every 20-30s and that repetition is invisibility. Rebuilt after the body was lost in
    an edit -- the dispatch line survived but the function did not, and a call to an undefined
    name is a runtime error py_compile cannot see. Verify the CONSUMED thing, not the inputs."""
    from difflib import SequenceMatcher
    rows = load_master()
    N = len(rows); TOT = (N / 40) * 200.0
    W = sum(int(r["words"]) for r in rows); SP = W * 60.0 / WPM_S

    print(f"\n=== ENOCH-MOON | {N} beats | {N//40} blocks | {TOT/60:.0f}:{TOT%60:02.0f} ===\n")

    print(f"SILENCE   {W} words | {SP/60:.0f}:{SP%60:02.0f} speech | "
          f"{(TOT-SP)/60:.0f}:{(TOT-SP)%60:02.0f} silence = {100*(TOT-SP)/TOT:.0f}% air"
          f"   [target 20%, LEGO 4 -> {int(TOT*WPM_S/60*0.8)} words]")
    band = lambda w: "landing <=5w" if w <= 5 else ("SLACK 6-8w" if w <= 8 else "dense 9-11w")
    for k in ("landing <=5w", "SLACK 6-8w", "dense 9-11w"):
        rs = [r for r in rows if band(int(r["words"])) == k]
        sil = len(rs) * 5.0 - sum(int(r["words"]) for r in rs) * 60.0 / WPM_S
        print(f"          {k:<14}{len(rs):>4} beats  {sil/60:>2.0f}:{sil%60:02.0f} silence"
              f"  {100*sil/(TOT-SP):>3.0f}% of all silence")

    sents = len({(r["block_id"], r["sentence_id"]) for r in rows})
    print(f"\nPROSODY   {sents} sentences = {sents/(N/40):.0f}/block   [<=21]")

    H = sum(1 for r in rows if r["weight"] == "hero")
    ST = sum(int(r["variants"]) for r in rows)
    print(f"\nPICK      {H} hero / {N-H} conn = {100*H/N:.0f}% hero | {ST} stills | ${ST*0.08:.2f}"
          f"   [target 25% = {int(N*0.25)} hero]")

    COSMIC = {"heavens", "interior", "ascent"}
    C = sum(1 for r in rows if r["setting"] in COSMIC)
    print(f"\nCONTRAST  {100*C/N:.0f}% cosmic. Per block: " + " ".join(
        f"b{b}:{100*sum(1 for r in rows if int(r['block_id'])==b and r['setting'] in COSMIC)/40:.0f}%"
        for b in sorted({int(r["block_id"]) for r in rows})))

    arch = sum(1 for r in rows if re.search(
        r"\b(ranked|rank|openings?|windows?|cut stone|dressed (rock|stone)|jamb|courses)\b",
        r["phenomenon"], re.I))
    print(f"\nSUBJECT   {arch}/{N} = {100*arch/N:.0f}% of beats are ranked openings / cut stone")

    norm = lambda p: re.sub(r"[^a-z ]", " ", p.lower())
    dups = 0
    for i in range(N):
        for j in range(i + 1, N):
            if rows[i]["block_id"] == rows[j]["block_id"]:
                continue
            if SequenceMatcher(None, norm(rows[i]["phenomenon"])[:190],
                               norm(rows[j]["phenomenon"])[:190]).ratio() > 0.66:
                dups += 1
    print(f"\nDUPLICATE {dups} cross-block pairs >66% identical")


if __name__ == "__main__":
    cmd, rest = (sys.argv[1] if len(sys.argv) > 1 else ""), sys.argv[2:]
    if cmd == "blocks": cmd_blocks(rest)
    elif cmd == "sweep": cmd_sweep(rest)
    elif cmd == "audio": cmd_audio(rest)
    elif cmd == "normalise": cmd_normalise(rest)
    elif cmd == "calibrate": cmd_calibrate(rest)
    elif cmd == "film": cmd_film(rest)
    elif cmd == "probe": cmd_probe()
    elif cmd == "reprobe": cmd_reprobe()
    elif cmd == "probe3": cmd_probe3()
    elif cmd == "probe4": cmd_probe4()
    elif cmd == "probe5": cmd_probe5()
    elif cmd == "probe6": cmd_probe6()
    elif cmd == "probe7": cmd_probe7()
    else: raise SystemExit(__doc__)
