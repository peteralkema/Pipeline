#!/usr/bin/env python3
"""patch_lego_filmrecord_storyarc.py  --  two additions to shared/docs/_LEGO.md.

  1. STORY ARC -- THE UNSOLVED MEASURE. Names the gap the CSV cannot see (the arc the
     film produces in the viewer), states that it must eventually be BOTH a post-hoc
     instrument AND an authoring rubric, and fixes the order: build the instrument
     first, promote a measure to a gate only once it has predicted a real retention
     drop. Inserted before FUTURE.
  2. FILM RECORD -- a growing appendix, one block per shipped film: structure, words,
     words/beat, measured WPM, drift, spend, then CTR/AVD slots filled when YouTube
     data lands. Entry 1 = women-in-the-water. Appended at the end.
  Plus: a words/beat cross-ref in TIMING, and the FUTURE time-axis bullet redirected
  to STORY ARC (it was the same idea, stated weaker -- no duplicate truths).

Anchor-verified, idempotent, .pre_ backup. NOTE: this patch writes em-dashes and other
unicode because _LEGO.md uses them as house style -- the ASCII-only rule is for CODE
patches. Content is UTF-8 throughout.

    cd ~/Projects/Pipeline
    python3 shared/patch_lego_filmrecord_storyarc.py
"""
import argparse, os, sys

STORY_ARC = "## STORY ARC — THE UNSOLVED MEASURE (build the instrument, then the rubric)\n\n**The gap, stated plainly.** The CSV measures *structure* — register distribution, word\ndensity, hero/connective balance, token mix, escalation-countable-every-4-8-rows. A film is\njudged on something else: the **arc it produces in the viewer** — does tension rise, does a\nquestion stay open, does the viewer lean forward at minute fourteen. Nothing in this pipeline\ncurrently measures or designs for that. Structural counts are proxies, and the audit that reads\nthem **flattens the time axis** (see GOVERNING LAW) — a perfect distribution can still be a\nflat film.\n\nThis section is a **named open problem**, not a solved spec. It is written down so the next\nfilms test it rather than re-discover it.\n\n### It must eventually be BOTH\n\n| mode | what it is | when |\n|---|---|---|\n| **post-hoc instrument** | score a finished `master.csv`, join the shipped retention curve onto the beat rows, learn which measures predict where viewers actually left | **build first** — you cannot validate a rubric you have never correlated against real retention |\n| **authoring rubric** | score the arc at Step 2–3 and gate on it, the way the variety law is gated today | **graduates from the instrument** — a measure is promoted to a gate only once it has predicted a real drop |\n\n### The ground truth is exact, and that is the unlock\n\nBecause the container is arithmetic (40 beats × 5.000s = 200.000s, block N starts at\n(N−1)×200), **a retention timestamp maps onto a beat row with no estimation**: beat *i* of the\nfilm spans `(i−1)×5.000` to `i×5.000` seconds. YouTube's retention curve can be joined directly\nonto the CSV. **The row where viewers leave becomes the next film's training signal.** No other\npart of this pipeline gets ground truth that clean — use it.\n\n### Candidate measures (sequence-aware, not distributional)\n\nAll of these are computable from the existing master CSV. None is yet proven to predict\nretention — that is exactly what the instrument is for.\n\n- **Escalation delta, block over block.** Does at least one of scale / danger / mystery /\n  consequence / emotion / urgency / human-cost increase from block N to N+1? A film that\n  plateaus in the middle should show it here. *(The craft law already demands this; nothing\n  measures it.)*\n- **Open-loop count at each beat.** How many questions are live and unanswered. The curiosity\n  engine says the stack never empties — this counts it. Would need an authored column\n  (`opens` / `closes`); **unbuilt, and the only candidate that costs new authoring**.\n- **Longest human-absent run.** Consecutive beats with no person in `phenomenon`. The known\n  mid-video cliff on argument blocks is a human-absence failure — this is its early warning.\n- **Longest single-token run.** Consecutive beats sharing one `setting` token — same-place\n  monotony that a per-beat variety gate misses entirely.\n- **Register trajectory, not register mix.** The *sequence* of registers, read as a curve;\n  a flatline over several blocks is viewer fatigue even when the distribution looks healthy.\n- **Hero-beat spacing.** Gap between hero beats vs. the 20–30s doctrine — measured in rows.\n\n### The protocol\n\n1. Score every shipped film's `master.csv` on the candidates above (cheap, pure-stdlib, no spend).\n2. When day-14/21 retention lands, join the curve onto the beat rows and record it in FILM RECORD.\n3. Correlate: at the beats where viewers actually left, which measures were already flashing red?\n4. **Promote what predicts; drop what does not.** A measure that survives two or three films\n   graduates from instrument to authoring rubric and gets a gate at Step 3.\n\n> **Do not gate on any of these yet.** Gating on an unvalidated proxy is exactly the blanket\n> the GOVERNING LAW warns about — it would enforce a shape no evidence supports.\n\n---\n\n"
FILM_RECORD = '\n---\n\n## FILM RECORD — shipped films, facts and figures\n\nOne block per completed film. Authoring/production figures are filled at ship; the distribution\nfigures are filled when the data lands (48h, then day 14/21). The point is **comparison across\nfilms** — the questions no single film can answer (does higher word density help or hurt\nretention? does a heavier Kling count pay? does a tighter arc score predict a flatter curve?).\nAdd STORY ARC scores here as the instrument comes online.\n\n### 1 — *The Daughters of the Watchers — the Mystery Every Ocean Kept*\n**Sacred Dawn · shipped: (pending) · project `women-in-the-water`**\n\n| | |\n|---|---|\n| structure | 8 blocks · 320 beats · ~26.7 min |\n| narration | **4,318 words · 13.5 words/beat** |\n| voice | Elliot (Inworld) · **161 WPM measured** |\n| VO passes | 3 — 2,734 w (156 WPM) → 3,464 w (158) → 4,318 w (161) |\n| drift at lock | b1 +5.3 · b2 −2.4 · b3 +5.7 · b4 −12.3 · b5 +0.3 · b6 +5.5 · b7 −15.1 · b8 +19.4 (seconds, per block) |\n| canon | 12 tokens (project `canon.json`) |\n| probe | 20 beats / 62 real stills / ~$5 |\n| grid | ~800 real stills / ~$71 |\n| clips | (pending — floor + additive Kling) |\n| **CTR @48h** | *(pending)* |\n| **AVD @48h** | *(pending)* |\n| **AVD day-14 / day-21** | *(pending)* |\n| traffic mix @day-14 | *(pending)* |\n| arc scores | *(pending — see STORY ARC)* |\n\n**Notes.** First film authored under **container-fill** (blocks filled to ~0 drift rather than\ncarrying ~20% air) — 13.5 w/beat against the ~13.3 predicted by 161 WPM on a 5.000s slot, so\nthe model held. Six of eight blocks landed within ±6s; b7 (−15s) and b8 (+19s) were accepted\nrather than chasing a fourth pass. First film to use the self-selecting `probe` verb and the\nproject-`canon.json` load. `{newearth}` initially rendered as bright desert and was fixed at\nthe **token** (glory-as-substance + positive fullness), not by re-authoring phenomena.\n'
TIMING_OLD = 'neighbour fuller) so long as the BLOCK totals ~530.'
TIMING_NEW = 'neighbour fuller) so long as the BLOCK totals ~530. *(WITW shipped at 13.5 words/beat\nmeasured — see FILM RECORD.)*'
FUTURE_OLD = "- **Time-axis read for Step 3** — a per-block escalation delta, and a retention-data-playback\n  that joins YouTube's actual retention curve back onto the beat rows (the row where viewers\n  leave becomes the next film's training signal)."
FUTURE_NEW = '- **The story-arc instrument, then the rubric** — see STORY ARC above. Nearest build: score a\n  shipped `master.csv` on the sequence-aware candidates and join the retention curve onto the\n  beat rows.'
NEG_OLD = '**IF THE OBJECT IS A DOCUMENT'
NEG_NEW = '> **★ NEVER WRITE "no X" IN A `phenomenon`.** The banned-word gate greps the RAW cell text,\n> so a beat authored "…monumental, no lectern" trips the very ban it was trying to honour — and\n> the image model ignores negatives anyway, often rendering the negated noun. **State the\n> positive that fills the space:** "resting on bare dark stone", "held in two hands", "alone in\n> a hard shaft". Same law as the canon tokens above, applied to the beat cell. *(Cost the WITW\n> grid two mid-render aborts, 21 Jul — the exclusions were authored, then banned.)*\n\n**IF THE OBJECT IS A DOCUMENT'
GATE_OLD = '  in probe mode (cross-film clip_index repeats would false-trip it).'
GATE_NEW = '  in probe mode (cross-film clip_index repeats would false-trip it). **`stills` PRE-GATES every\n  wanted block before rendering any of them** — a gate failure prints the complete list across\n  the whole film and exits with nothing spent, so a full-grid run is safe to leave unattended.\n  The run ends with a completion summary and flags any sub-8KB frame (a fal safety reject).'
FUTURE_ANCHOR = "## FUTURE\n"



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", default=None, help="path to _LEGO.md (default: <repo>/shared/docs/_LEGO.md)")
    a = ap.parse_args()

    if a.doc:
        path = os.path.abspath(a.doc)
    else:
        d = os.path.abspath(os.getcwd()); root = None
        while d != os.path.dirname(d):
            if os.path.isdir(os.path.join(d, ".git")): root = d; break
            d = os.path.dirname(d)
        if not root:
            sys.stderr.write("ERROR: no .git found; pass --doc\n"); sys.exit(1)
        path = os.path.join(root, "shared", "docs", "_LEGO.md")
    if not os.path.isfile(path):
        sys.stderr.write("ERROR: not found: %s\n" % path); sys.exit(1)

    src = open(path, encoding="utf-8").read()
    orig = src

    # EDIT 1 -- STORY ARC inserted before FUTURE
    if "## STORY ARC" in src:
        print("skip (already applied): STORY ARC section")
    else:
        if src.count(FUTURE_ANCHOR) != 1:
            sys.stderr.write("ERROR: '## FUTURE' anchor found %d times (need 1) -- ABORT.\n"
                             % src.count(FUTURE_ANCHOR)); sys.exit(1)
        src = src.replace(FUTURE_ANCHOR, STORY_ARC + FUTURE_ANCHOR, 1)
        print("applied: STORY ARC section")

    # EDIT 2 -- FUTURE time-axis bullet redirected (no duplicate truth)
    if FUTURE_NEW in src:
        print("skip (already applied): FUTURE bullet redirect")
    elif FUTURE_OLD in src:
        src = src.replace(FUTURE_OLD, FUTURE_NEW, 1)
        print("applied: FUTURE bullet redirect")
    else:
        sys.stderr.write("ERROR: FUTURE time-axis bullet not found -- ABORT (no write).\n"); sys.exit(1)

    # EDIT 3 -- words/beat cross-ref in TIMING
    if "WITW shipped at 13.5 words/beat" in src:
        print("skip (already applied): TIMING cross-ref")
    elif TIMING_OLD in src:
        src = src.replace(TIMING_OLD, TIMING_NEW, 1)
        print("applied: TIMING cross-ref")
    else:
        sys.stderr.write("ERROR: TIMING anchor not found -- ABORT (no write).\n"); sys.exit(1)

    # EDIT 4 -- FILM RECORD appended at the end
    if "## FILM RECORD" in src:
        print("skip (already applied): FILM RECORD appendix")
    else:
        src = src.rstrip("\n") + "\n" + FILM_RECORD
        print("applied: FILM RECORD appendix")

    # EDIT 5 -- the negation rule for phenomenon cells
    if 'NEVER WRITE "no X"' in src:
        print("skip (already applied): phenomenon negation rule")
    elif NEG_OLD in src:
        src = src.replace(NEG_OLD, NEG_NEW, 1)
        print("applied: phenomenon negation rule")
    else:
        sys.stderr.write("ERROR: phenomenon-section anchor not found -- ABORT (no write).\n"); sys.exit(1)

    # EDIT 6 -- stills pre-gate stated in the COMMAND CONTRACT
    if "PRE-GATES every" in src:
        print("skip (already applied): stills pre-gate contract")
    elif GATE_OLD in src:
        src = src.replace(GATE_OLD, GATE_NEW, 1)
        print("applied: stills pre-gate contract")
    else:
        sys.stderr.write("ERROR: COMMAND CONTRACT stills anchor not found -- ABORT (no write).\n"); sys.exit(1)

    if src == orig:
        print("no changes."); return

    bak = path + ".pre_filmrecord"
    if not os.path.exists(bak):
        open(bak, "w", encoding="utf-8").write(orig); print("backup:", bak)
    open(path, "w", encoding="utf-8").write(src)
    print("OK: _LEGO.md updated (STORY ARC + FILM RECORD).")


if __name__ == "__main__":
    main()
