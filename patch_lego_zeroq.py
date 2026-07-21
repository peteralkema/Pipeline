#!/usr/bin/env python3
"""
patch_lego_zeroq.py -- make _LEGO.md answer the five questions a fresh reader
should never have to ask. Targeted, idempotent doc edits (no 940-line rewrite):

  A. front-matter QUICK START (S0.0) -- the authoritative "read this first" block;
     overrides any stale number in the body.
  B. fix the S2 word-ceiling row: 10-flat -> the ~6-13 word BAND (55 = backstop).
  C. S4 timing correction blockquote: 159 WPM / one continuous track / calibrate;
     mark the interior 143-WPM arithmetic as the old illustrative derivation.
  D. programs table: build_moon.py -> RETIRED; build_lego.py canonical.
  E. new S7.1 FILLING THE move COLUMN -- the allocation rule (ladder + draft_moves
     + validate-against-a-shipped-film). The trigger the session had to reconstruct.

Each edit is independent: skips if already applied, WARNS (does not abort) if its
anchor is missing, so a body number that drifted on the box can't block the rest.
One .pre_<ts> backup before any write. Payloads are ASCII (the doc itself keeps its
unicode; anchors are chosen ASCII-only). Run where _LEGO.md is, or pass the path.

  python3 patch_lego_zeroq.py [path/to/_LEGO.md]
"""
import sys, time
from pathlib import Path

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_LEGO.md")

FRONTMATTER = '''
## 0.0 QUICK START -- ZERO-QUESTION START (read this first; it overrides any stale number below)

Six things a fresh reader must NOT have to ask. If the body contradicts this block, THIS block wins.

1. **AUTHORING WORD TARGET.** Author each 5.000s beat to a BAND of **~6-13 words** -- a hero beat breathes at 6, a dense sequence carries 13. This band IS the pace instrument (S3A, S12); a flat count on every beat is a S0 blanket. **~380 words/block is the block AVERAGE, not a per-beat rule.** The "10-word ceiling" / "<=10 words/beat" phrasings elsewhere mean the band's centre, not a hard cap. The code gate in build_lego fires at **55 words -- a RUNAWAY BACKSTOP** (it catches a paragraph pasted into one cell), never the target. Do not author to 55; do not flatten to 10.

2. **CANONICAL TOOLSET** (one name per leg; aliases retired).
   - Author / normalise / sweep / audit / VO / calibrate -> `build_lego.py` (verbs: normalise, sweep, film, blocks, stills, audio, calibrate). `build_moon.py` is RETIRED (the enoch-only proof).
   - Stills grid -> `build_lego stills` (attaches references) OR `render_grid.py` (text-to-image only; does NOT attach refs). See #3.
   - The pick -> `place.py` (promotes grid winners to `stills/shot_NNN.png`).
   - Clips -> `render_clips.py` (reads air/move/motion; `--floor-only`, `--dry-run`). Do NOT use any `clips` verb inside build_lego -- that path renders a MOVELESS STATIC floor (it passes no `move`) and is a trap. `render_clips.py` is the ONLY clips leg.

3. **MODE -> RENDER PATH** (which stills tool a channel uses).

   | channel `render_mode` | stills grid tool | why |
   |---|---|---|
   | **reference** (character/object plates: Bentley) | `build_lego stills` | only it attaches the `reference_map` plates via /edit |
   | **text-to-image** (Sacred Dawn, Scripture, Synthetic, Final Hours, YHTBT) | `build_lego stills` OR `render_grid.py` | no refs to attach; either works |

4. **FILLING THE `move` COLUMN.** `move` (push/pull/crane/settle/static) is DERIVED off the picked frame's `phenomenon` + `register` via the S7 ladder, then eye-corrected -- never hand-invented per beat. Tool: `draft_moves.py`. `static` is hand-placed (not derivable). Validate the drafter against a shipped film (`draft_moves.py --validate` on enoch-moon). Full rule: **S7.1**.

5. **TIMING MODEL.** Shipping model is **159 WPM (Elliot), ONE continuous whole-film `narration.txt`** (not per-block), whisper + `calibrate` measuring each seam against the 5.000s grid; the tail is a pad, never a trim; Inworld's 20-break-per-request cap is a hard limit. S4's interior 143-WPM / per-block-break arithmetic is the OLD illustrative derivation -- the METHOD (calibrate the seams) is current; the 143 / 380-as-hard specifics are retired.

6. **CONFIG LIVES IN JSON, NEVER CODE.** `channel.json` (grade/style_suffix, voice_id, image_model, ken_burns flag, render_mode, reference_map), project `canon.json` ({token} definitions), `rulebook.json` (negatives; two-layer, CWD-scoped). A per-beat fact is a CSV column; a per-channel fact is JSON. Tempted to special-case in code -> add a column instead.

---
'''

S4_NOTE = '''
> **TIMING MODEL -- CURRENT (159), read before the arithmetic below.** The shipping model is **159 WPM (Elliot), ONE continuous whole-film `narration.txt`** (not per-block MP3s), rendered then measured by whisper + `calibrate` against the 5.000s grid. The derivation in this section is the older **143-WPM / per-block-break** illustration -- the METHOD it teaches (measure the rendered audio, adjust the seam, the tail is a pad never a trim) is current and correct; treat the specific 143 / 380-as-hard-ceiling numbers as illustrative, and author to the ~6-13 word BAND (S0.0 #1), never a flat count.
'''

S71 = '''## 7.1 FILLING THE `move` COLUMN -- the allocation rule (draft, then correct)

`move` (push | pull | crane | settle | static) is the trigger `ken_burns_still(move=...)` reads. It is **derived off the PICKED frame's `phenomenon` + `register` via the S7 ladder**, drafted by tool and corrected by eye -- never hand-invented per beat, never a flat value.

**The ladder (first match wins) -- the S7 precedence made mechanical:**
1. quiet register (reflection / grief / sorrow) OR quiet phenomenon words (aftermath, ash, empty, still, dark) -> **settle** (never push)
2. vertical force (rising, column, tower, shaft, pillar, ascends) -> **crane**
3. scale / wide (ranked, vast, receding, whole curve, to the horizon, thousands) -> **pull**
4. everything else -> **push** (one overwhelming subject; the default)

**`static` is NOT auto-derivable.** Hand-place it sparingly on eerie-stillness / near-locked beats (~1 in 6 on enoch). The drafter never assigns it; you promote specific held beats by eye.

**Register alone does NOT determine the move** -- on enoch, `awe` maps to pull, push AND static across the film. The **phenomenon drives it**; register is the tiebreak. That is why the ladder reads the image, not just the mood.

**TOOL: `draft_moves.py`.**
- `--csv master.csv` fills blank `move` cells off phenomenon+register (idempotent; preserves edits; `.pre_` backup).
- `--dry-run` prints the push/pull/crane/settle spread before a frame renders. A flatline (all push) is the S0 blanket signal -- widen the cues.
- `--validate` measures the drafter against an ALREADY-SHIPPED film's `move` column. Run it on enoch-moon: the match rate tells you the ladder is the rule, and every disagreement is either a hand-placed `static` or a phenomenon cue to widen. This is how you trust the drafter before spending it on a new film.

`enoch-moon/beats/moon_master.csv` is the ground-truth exemplar of this rule; a new channel's floor is drafted the same way, then eye-corrected.

'''

# ---- edit specs -------------------------------------------------------------
# ("insert_after", line_anchor, payload, marker)
# ("insert_before", anchor, payload, marker)
# ("replace", old, new, marker)
EDITS = [
    ("insert_after",
     "# _LEGO.md -- the channel-agnostic pathway for cinematic feature videos",
     FRONTMATTER, "0.0 QUICK START"),
    ("replace",
     "| **word ceiling** | **10 words per beat** | hard gate |",
     "| **word band** | **~6-13 words/beat** | the pace instrument (S3A/S12), NOT a flat cap; ~380/block is the block AVERAGE. The code gate at 55 words is a runaway backstop, never the authoring target. |",
     "| **word band** |"),
    ("insert_after",
     "## 4. TIMING",
     S4_NOTE, "TIMING MODEL -- CURRENT (159)"),
    ("replace",
     "*(today `build_moon.py`; lift to `shared/` at video two)*",
     "*(`build_lego.py` -- channel-agnostic; `build_moon.py` RETIRED)*",
     "`build_moon.py` RETIRED)*"),
    ("insert_before",
     "## 8. THE FILM SPINE",
     S71, "## 7.1 FILLING THE"),
]


def die(m):
    print("PATCH ABORTED: " + m); raise SystemExit(1)


def main():
    if not TARGET.exists():
        die("_LEGO.md not found. Pass the path or run from its dir.")
    src = TARGET.read_text()
    orig = src
    log = []

    for spec in EDITS:
        kind = spec[0]
        if kind == "replace":
            _, old, new, marker = spec
            if marker in src:
                log.append("  skip (already applied): " + marker); continue
            if old in src:
                src = src.replace(old, new, 1); log.append("  applied replace: " + marker)
            else:
                log.append("  WARN anchor missing (skipped): " + repr(old[:48]))
        elif kind == "insert_after":
            _, anchor, payload, marker = spec
            if marker in src:
                log.append("  skip (already applied): " + marker); continue
            i = src.find(anchor)
            if i == -1:
                log.append("  WARN anchor missing (skipped): " + repr(anchor[:48])); continue
            eol = src.find("\n", i)
            eol = len(src) if eol == -1 else eol
            src = src[:eol + 1] + payload + src[eol + 1:]
            log.append("  applied insert-after: " + marker)
        elif kind == "insert_before":
            _, anchor, payload, marker = spec
            if marker in src:
                log.append("  skip (already applied): " + marker); continue
            i = src.find(anchor)
            if i == -1:
                log.append("  WARN anchor missing (skipped): " + repr(anchor[:48])); continue
            src = src[:i] + payload + src[i:]
            log.append("  applied insert-before: " + marker)

    print("\n".join(log))
    if src == orig:
        print("No changes (all edits already applied or all anchors missing).")
        return
    ts = time.strftime("%Y%m%d-%H%M%S")
    TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts).write_text(orig)
    TARGET.write_text(src)
    print("Patched %s  (backup .pre_%s)" % (TARGET.name, ts))


if __name__ == "__main__":
    main()
