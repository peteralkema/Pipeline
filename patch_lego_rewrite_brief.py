# -*- coding: utf-8 -*-
# patch_lego_rewrite_brief.py
# Inserts a REWRITE BRIEF into shared/docs/_LEGO.md, right after the TEST-RUN
# FINDINGS block. This is the work list for the next FULL rewrite of the doc:
# G22 (paths-are-canonical) with exact placement, plus rewrite recommendations.
#
# G22 dogfood: with no argument this self-locates the repo root (walks up for .git)
# and targets the CANONICAL path shared/docs/_LEGO.md. A path argument overrides.
#     python3 patch_lego_rewrite_brief.py                 # canonical
#     python3 patch_lego_rewrite_brief.py some/other.md   # override
#
# Idempotent (marker-guarded), anchor-verified, .pre_ backup, ASCII payload.
import io, os, sys

CANON_REL = "shared/docs/_LEGO.md"
MARKER = "<!-- REWRITE-BRIEF-2026-07-21 -->"
ANCHOR = "<!-- TESTRUN-FINDINGS-WITW-2026-07-21 -->"   # insert AFTER the findings block
RULE = "\n---\n"


def repo_root(start="."):
    p = os.path.abspath(start)
    while p != "/":
        if os.path.isdir(os.path.join(p, ".git")):
            return p
        p = os.path.dirname(p)
    return None


def resolve_target():
    if len(sys.argv) > 1:
        return sys.argv[1]
    root = repo_root()
    if root:
        return os.path.join(root, CANON_REL)
    return CANON_REL


BRIEF = MARKER + """
## REWRITE BRIEF -- for the next full rewrite of this document

This document grew by accretion: PART I (process) + PART II (craft) + S12 SUPERSEDED
+ LEDGER ADDITIONS + S0.0 QUICK START (override-by-decree) + TEST-RUN FINDINGS. A fresh
reader now holds four-plus layers of "what is actually current." The next pass should
CONSOLIDATE into one coherent, deterministic document that states a single current truth
in the body, with the overrides merged IN and the stale text deleted -- a short CHANGELOG
at the end preserves history. The whole point is: a fresh Claude should never have to
reconcile the doc against itself.

### G22 -- PATHS ARE CANONICAL  (the friction the 21 Jul session hit four times)
The LEGO thesis is "config in JSON, never code." **File paths are also config**, and today
they lived implicitly in the operator's head -- so every patch script had to be told its
target by trial and error (the doc is at shared/docs/_LEGO.md not repo root; the project
folder was assumed-new when it existed; master.csv / patch destinations were unspecified).
A path assumed is a path that breaks on a fresh laptop, a new channel, or a fresh Claude
with no memory. Integrate, at these exact places:
- ADD to S0.0 a **PATHS ARE CANONICAL** sub-block naming every artifact's repo-relative home:
    docs:            shared/docs/_LEGO.md , shared/docs/_Sacred-Dawn.md (+ one per channel)
    channel config:  <channel>/channel.json , <channel>/rulebook.json
    shared rulebook: shared/rulebook.json
    project:         <channel>/projects/<slug>/{master.csv, canon.json, narration.txt}
    grid stills:     <channel>/projects/<slug>/stills/{beat}-{variant}.png
    placed stills:   <channel>/projects/<slug>/stills/shot_NNN.png
    clips:           <channel>/projects/<slug>/clips/shot_NNN.mp4
- STATE the rule in the PROGRAMS section: **patch/build scripts DEFAULT to the canonical
  path** (resolve the repo root by walking up for .git); a path argument is an OVERRIDE,
  not a requirement. (This file's own 21 Jul patches already dogfood this -- copy the
  repo_root() helper into the shared tooling.)
- ADD a one-line preflight -- a `build_lego paths <channel> <slug>` verb (or paths_check.py)
  that verifies every canonical path exists before a run -- turning N separate
  "no such file" surprises into one upfront green/red.

### FURTHER REWRITE RECOMMENDATIONS
1. **Collapse override-by-decree.** Merge S0.0's corrections INTO the body; delete the
   superseded lines (143 WPM, 380-as-hard, per-block VO, the 10-word hard ceiling, the
   160-stills/4-variant model). The body states the current truth ONCE; S0.0 becomes a
   genuine summary, not a correction layer.
2. **Reconcile the timing model in place (G3/G4):** 159 WPM, ONE continuous whole-film
   narration.txt, word-band ~6-13, calibrate the 200s seams. No stale 143/430/380/per-block
   left anywhere in the body or in _Sacred-Dawn.md.
3. **Six clean sections:** (a) the 0-9 PROCESS table, (b) the beat-CSV column dictionary,
   (c) the authoring CRAFT law, (d) the per-channel JSON config contract, (e) ENGINE FACTS
   / gotchas (gather the scattered ones into one place), (f) a CHANGELOG. Process, craft,
   and engine currently interleave.
4. **Fold TEST-RUN FINDINGS (G1-G22) into the sections they belong to** -- G11 into
   spine/authoring, G13/G16 into craft, G17/G19 into Step 3, G21 into the retention law --
   so they become doctrine in place, not a standing to-do list. Keep G20 in FUTURE.
5. **Make the gate/aim line explicit per column:** which numbers are HARD gates (a script
   consumes them) vs SOFT aims (human judgment). Anywhere a "~" or "should" is consumed by
   code, pin it or mark it human-only. Determinism is the deliverable.
6. **State scope up front:** S16 WHAT LEGO IS NOT FOR and S15 MODE OVERRIDES are
   load-bearing and belong near the top, not buried at the end.
7. **Add the analysis-layer guardrail as doctrine:** "a flat distribution is not the goal;
   a motivated one is" (S0 pointed at the data audit). The method catches unmotivated
   UNIFORMITY and is blind to unmotivated MONOTONY-IN-SEQUENCE; name that limit so a reader
   does not "balance" the arc (the antediluvian front-load / tension lead are correct).
8. **Kill the fragments:** _LEGO-PART-I.md and _LEGO-FEATURE-FILM.md exist alongside this
   consolidated doc. Confirm shared/docs/_LEGO.md is the single source; delete or mark-retire
   the fragments so no stale fragment is ever read.
9. **Add the FUTURE section (G20):** a time-axis read for Step 3 -- per-block escalation
   delta + a retention-data-playback that joins YouTube's actual curve back onto the beat
   rows (the row where viewers leave becomes the next film's training signal).
10. **Determinism sweep of the token contract (G6/G7):** state ONCE, unambiguously, that on
    text-to-image channels tokens are SETTING place-locks defined in canon.json and expanded
    by {token} (never hand-pasted, never a column); on reference channels they are
    character/object plates via reference_map. The two modes currently blur.
"""


def main():
    target = resolve_target()
    if not os.path.exists(target):
        print("ERROR: target not found:", target, "(pass a path to override)"); sys.exit(1)
    src = io.open(target, encoding="utf-8").read()
    try:
        BRIEF.encode("ascii")
    except UnicodeEncodeError as e:
        print("ERROR: payload not ASCII:", e); sys.exit(1)
    if MARKER in src:
        print("skipped: rewrite brief already present (idempotent) ->", target); return
    if ANCHOR not in src:
        print("ERROR: findings anchor not found; run patch_lego_testrun.py first ->", target); sys.exit(1)
    a = src.index(ANCHOR)
    rule = src.find(RULE, a)
    if rule == -1:
        print("ERROR: no '---' after findings block; refusing to write"); sys.exit(1)
    ins = rule + len(RULE)
    io.open(target + ".pre_rewritebrief", "w", encoding="utf-8").write(src)
    new = src[:ins] + "\n" + BRIEF + "\n---\n" + src[ins:]
    io.open(target, "w", encoding="utf-8").write(new)
    print("applied: inserted REWRITE BRIEF (G22 + recommendations) ->", target)


if __name__ == "__main__":
    main()
