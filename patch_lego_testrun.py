# -*- coding: utf-8 -*-
# patch_lego_testrun.py
# Consolidated deliverable of the women-in-the-water test run (21 Jul 2026).
# Inserts a TEST-RUN FINDINGS section (G1-G21) into _LEGO.md, right after the
# 0.0 QUICK START block, so the next fresh reader hits it early.
#
# Discipline: idempotent (marker-guarded), anchor-verified before write,
# .pre_ backup, ASCII-only. Run laptop-side against the repo copy:
#     python3 patch_lego_testrun.py ~/Projects/Pipeline/_LEGO.md
#
# It does NOT rewrite the stale body lines itself (G3/G4 touch multiple files and
# the Sacred-Dawn doc); those are listed as APPLY-INTO-BODY items at the top of the
# inserted block so they are done by hand, deliberately, once.
import io, sys, os

PATH = sys.argv[1] if len(sys.argv) > 1 else "_LEGO.md"
MARKER = "<!-- TESTRUN-FINDINGS-WITW-2026-07-21 -->"
ANCHOR = "## 0.0 QUICK START"          # insert AFTER the quick-start section
NEXT_HDR = "\n---\n"                    # the first horizontal rule after the anchor

BLOCK = MARKER + """
## TEST-RUN FINDINGS -- women-in-the-water (21 Jul 2026)  [G1-G21]

First full authored film run as a live test of this document. G1-G21 are the gaps
the run exposed. GREEN = doc sufficient; AMBER = a judgment the doc did not guide;
RED = doc silent or self-contradictory. The two fattest (G11 anti-scroll bias, G16
render-the-idea) were invisible on a read-through and only surfaced by authoring
against the real gate -- which is the case for running a film as the test.

### APPLY INTO THE BODY BY HAND (deliberate, once):
- **G3 (RED):** put a SUPERSEDED banner at the head of S4 and on the S2 VO row and the
  bottom LEDGER "five verbs" line, pointing to S0.0. The override wins by decree today;
  the body should admit it lost.
- **G4 (RED):** reconcile Elliot WPM -- S0.0 says 159, S2/S4 say 143, and
  `_Sacred-Dawn.md` S10 says 143. Pick the measured value; fix all three.

### AUTHORING + PROCESS PATCHES (fold into the named section):
- **G1 (S0):** Step 0 must cross-ref the channel's attribution/assertion rule before
  committing a title (an asserting title, e.g. "Mermaids Were Real", breaks the moat).
- **G2 (S0):** Step 0 thumbnail-concept line must flag topic-level render-safety risk
  (family-safe/YPP) before generating -- some topics pull the model to unsafe frames.
- **G5 (S1):** Step 1 must link S8 for block-count sizing (~3000-3600 words = 8 blocks);
  the heuristic is buried in the competitor analysis and unlinked from Architect.
- **G6 (S1):** state that canon tokens are SETTING place-locks on text-to-image channels
  and character/object plates on reference channels -- S14 currently dominates and misleads.
- **G7 (S3A.2):** on a channel with a `canon` block, the `{token}` IS the verbatim-paste;
  author the token, define the phrase once in `canon.json`. Hand-paste the full phrase
  ONLY on a channel with no canon. (Kills 40-cell bloat + drift.)
- **G9 (S8/Step2):** each 40-beat block is a mini-spine -- open its question, build, turn,
  close on the handoff loop; ~10 heroes cluster on the turn and the loop beats.
- **G10 (S0.0 #1):** under ~380/block is safe -- it becomes air, tuned at calibrate.
  NEVER pad narration to hit a number. Over-budget is the bug, not under.
- **G11 (S8/Step1) [the big one]:** if "the object" is a DOCUMENT, do NOT render the
  document when the narration names it (that is captioning) and do NOT let the model
  default to scroll/lectern/window furniture. Show what the book is ABOUT; reserve 1-2
  MONUMENTAL hero shots of the object (a bound book in a hard shaft, no stand); ban the
  STAGING in `rulebook.json` (no scroll on a table, no book on a lectern/stand, no study,
  no window-behind-desk, no quill, no scattered pages) -- never ban "book" itself.
- **G12 (S6):** name the whole-genre furniture bias (Enoch -> scrolls) as the largest
  two-home case: rulebook bans the staging, authoring stops asking for it.
- **G13 (S3A.2):** a supernatural SUBJECT (the Watchers, Leviathan, the water-woman) gets
  an anti-glow / anti-translucence clause IN its place-lock token (Balrog principle),
  the same way faces get anonymity -- render mass and weight, never vapor.
- **G14 (S3A):** a COMPARATIVE sequence (N cultures / N examples) is still a sequence of
  hero shots -- each item its own monumental frame. The info-graphic / chart / corkboard
  is the S16 Mode-B trap, never the render. (The competitor literalized convergence as a
  whiteboard; we render it as bright hero-figures across real landscapes.)
- **G15 (S1/Step2):** the block plan is a LIVING draft -- re-map the remaining spine
  against the authored state after each block; the plan serves the film, not the reverse.
- **G16 (S3A/S8) [the other big one]:** an abstract/argument beat renders its REFERENT as
  a monumental physical image (the archetype -> a colossal figure over a tiny human),
  never a chart or symbol. The idea gets the Balrog treatment too. This is what carries
  the reflective/danger-zone blocks S8 says need the strangest frames.
- **G17 (S3A/Step3):** a high-frequency spine token (>~20% of beats) gets a dedicated
  master-wide framing-repeat scan; vary the SUBJECT WITHIN the locked place, not the
  place -- motivated by what the beat reveals (a prow, a hand, wreckage, a shoal), not
  a new location. (deep ran 82/320 here; the empty-wide cluster was the one real risk.)
- **G18 (S8/Step2):** author the FINAL block to pay off the cold-open loop before the cold
  open is cut. The payoff is written in Step 2; the setup is assembled in Filmora at Step 9.
- **G19 (Step3):** the two load-bearing data scans are (a) the token x block heatmap
  (proves the arc / catches a token that never retires) and (b) a framing-repeat scan on
  any token over ~20% of beats (catches same-place monotony a per-beat variety gate misses).
- **G21 (S6/Step2):** an abstract/argument block must keep a HUMAN foreground thread --
  at least one person every few beats -- or it hits the mid-video cliff. The person is the
  retention anchor the argument cannot be. (Block 5 was person-less until the depth pass.)

### METHOD OBSERVATION (guardrail on the analysis layer):
The percentage audit is excellent at catching unmotivated UNIFORMITY (banned words, a
token that never retires) and blind to unmotivated MONOTONY IN SEQUENCE (a spine-token
run, the retention curve) -- % flattens the time axis. Guardrail: **a flat distribution
is not the goal; a motivated one is** (S0 pointed at the analysis layer). Do NOT "balance"
the antediluvian front-load or the tension lead -- the imbalance IS the arc.

### DEFERRED TO NEXT MAJOR VERSION:
- **G20:** add a time-axis read to Step 3 -- per-block escalation delta + a
  retention-data-playback that joins YouTube's actual retention curve back onto the beat
  rows (the beat where viewers leave becomes the training signal for the next film's audit).
"""


def main():
    if not os.path.exists(PATH):
        print("ERROR: file not found:", PATH); sys.exit(1)
    src = io.open(PATH, encoding="utf-8").read()

    # ensure ASCII-only payload
    try:
        BLOCK.encode("ascii")
    except UnicodeEncodeError as e:
        print("ERROR: patch payload not ASCII:", e); sys.exit(1)

    if MARKER in src:
        print("skipped: findings already present (idempotent)"); return

    if ANCHOR not in src:
        print("ERROR: anchor not found, refusing to write:", ANCHOR); sys.exit(1)

    # insert after the FIRST horizontal rule that follows the anchor
    a = src.index(ANCHOR)
    rule = src.find(NEXT_HDR, a)
    if rule == -1:
        print("ERROR: no '---' after anchor; refusing to write"); sys.exit(1)
    ins = rule + len(NEXT_HDR)

    io.open(PATH + ".pre_testrun", "w", encoding="utf-8").write(src)
    new = src[:ins] + "\n" + BLOCK + "\n---\n" + src[ins:]
    io.open(PATH, "w", encoding="utf-8").write(new)
    print("applied: inserted G1-G21 findings after 0.0 QUICK START")


if __name__ == "__main__":
    main()
