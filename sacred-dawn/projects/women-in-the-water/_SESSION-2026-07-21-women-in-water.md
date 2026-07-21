# Session Notes -- 21 Jul 2026 -- "The Women in the Water" (Sacred Dawn)

**Session type:** Full LEGO film authored (Steps 0-3) as a LIVE TEST of `_LEGO.md`.
**Outcome:** 26.7-min feature gated and data-interrogated to the VO-convergence line; the
LEGO doc measurably improved (findings G1-G22 banked); timing model reconciled.

---

## 1. WHAT THIS FILM IS

- **Channel:** Sacred Dawn (`@sacredawn`, text-to-image, Elliot voice, wonder-not-dread).
- **Topic:** the mermaid / "women in the water" convergence, anchored in the Book of Enoch
  (Watchers, the corruption reaching "the things that swim", the daughters, Revelation's
  "the sea was no more"). Learned from a competitor teardown; re-registered dread -> wonder.
- **Project folder:** `sacred-dawn/projects/women-in-the-water/`
- **Runtime:** 8 blocks x 200s = 26.7 min, 320 beats.

## 2. STEP 0 -- PACKAGING (done)

- **Thumbnail (approved ship-candidate):** colossal crowned woman-colossus rising from a
  cobalt sea, cobalt lightning left, gold horizon right, dwarfed fisherman lower-right.
  Baked text: "THE WOMEN IN THE WATER" / banner "ENOCH KNEW WHAT THEY WERE".
  FIGURE RULE held (monumental/uncanny, NOT sexualized -- the critical family-safe/YPP
  requirement on this exact topic). Minor squint-fixes noted (fisherman face too small/dim;
  darken banner bar) but shippable as-is.
- **YouTube title must COMPLEMENT the baked thumbnail text (different nouns), S8.**
  Recommended: "The Daughters of the Watchers -- the Mystery Every Ocean Kept" (or A/B
  "What the Book of Enoch Says the Daughters of the Watchers Became").
- **Winnability:** PASS. Sits in the proven Enoch hot-vein; the sea-women slice is unfarmed.

## 3. STEP 1 -- ARCHITECT (done)

8-block spine (cold open cut LAST in Filmora, $0, plants the "every ocean = same woman"
loop paid off in Block 8):
1. The Object (the book) -> 2. The Descent (Hermon, the oath) [thumb] ->
3. The Corruption Reached the Sea [thumb, PAYLOAD] -> 4. The World Remembers Her [thumb] ->
5. Memory, Not Myth (steel-man) -> 6. The Words Themselves (lilit/tannin/Leviathan) ->
7. The Symmetry (the mirror + Og/iron-bed contradiction) ->
8. The Sea Was No More (payoff + hedge @ ~87% + sequel seed).

## 4. STEP 2 -- AUTHORED ALL 8 BLOCKS (done, all gated GREEN)

- 320 beats, band ~6-13 words (avg 9.1, 366/block, 0 over the 55 backstop).
- **Zero banned words** across 640 narration+phenomenon strings (dread->wonder flip held).
- Attribution moat intact throughout (every supernatural claim tagged "Enoch says / the
  old texts describe", asserted never). Hedge is a spoken beat at Block 8 (~87%).
- **Canon tokens (12), place-locks (text-to-image), to be written to `canon.json`:**
  `{codex}` (book as monument, RESERVED 2/block -- replaced the scroll cliche),
  `{highland}` (Ethiopian monastery), `{antediluvian}` (pre-flood world), `{deep}` (fathomless
  sea), `{hermon}` (the summit), `{relief}` (carved evidence), `{descent}` (Watchers, anti-
  translucence), `{witness}` (the water-woman, anti-seduction clause baked in), `{coast}`
  (bright northern coast, anti-murk), `{leviathan}` (bright light-column, not teal murk),
  `{remnant}` (post-flood giant), `{newearth}` (sealess radiant world).

## 5. STEP 3 -- MERGE + INTERROGATE (done)

`master.csv` written (320 rows + derived setting/words/variants/still_cost; air/move/motion
blank for Step 7). Data read:
- **hero 124 (38.8%) / connective 196** -> 888 real stills ~= **$71 grid spend** whole film.
- register: tension 37% / wonder 23% / curiosity 17% / awe 15% / lean-forward 8% (no flatline).
- token x block heatmap = the spine as data: `{antediluvian}` front-loads 28->0; `{witness}`
  absent B1-2 then carries the back half; `{remnant}` only B7; `{newearth}` only B8;
  `{leviathan}` only B6. Every token lands where its content lives.
- **Two flags -> one acted on now:** `{deep}` was 82/320 beats, 74 wide-open-water (same-sea
  risk). Re-authored 15 empty-wide `{deep}` beats with FOREGROUND anchors (11 human: sailor,
  drowned hand, prow+lookout, net-haul, helmsman hands, diver, swimmer, drifting boat,
  fisherman, sinking figure; 4 non-human: kelp, broken mast, shoal, anchor-stone), Block 5
  weighted heaviest (5) to warm the person-less argument block. Result: distinct subjects
  in `{deep}` 19->24, framing cluster broken. The other flag (43 adjacent same-framing pairs)
  is a Step-6 grid worklist, not a re-author.

## 6. TEST-RUN FINDINGS BANKED -- G1-G22

The deliverable of running the film as a test. Full list lives in `shared/docs/_LEGO.md`
under "TEST-RUN FINDINGS". Fattest three: **G11** (anti-scroll bias: show what the book is
ABOUT, ban the staging in rulebook.json, reserve 2 monument shots -- book beats 18->2),
**G16** (render the IDEA as a monumental image, never a diagram), **G22** (paths are config:
state every artifact's canonical path; patch scripts default to it). G3/G4 (timing model)
reconciled this session. G20 (retention-data-playback / time-axis in Step 3) deferred to the
next major version.

**Method observation:** the % audit catches unmotivated UNIFORMITY well and is blind to
unmotivated MONOTONY-IN-SEQUENCE (the `{deep}` run, the retention curve) -- % flattens time.
Guardrail: a flat distribution is not the goal; a motivated one is. Do NOT balance the
`{antediluvian}` front-load or the tension lead -- the imbalance IS the arc.

## 7. CONFIG / DOC CHANGES MADE THIS SESSION (committed / to commit)

- `shared/docs/_LEGO.md`: TEST-RUN FINDINGS G1-G21 inserted (COMMITTED, a572e4d).
  + this session: REWRITE BRIEF (G22 + 10 rewrite recs) via `patch_lego_rewrite_brief.py`.
- `shared/docs/_Sacred-Dawn.md`: Elliot WPM 143 -> 159, per-block ~430 model flagged
  SUPERSEDED, via `patch_sacreddawn_timing.py` (G3/G4). **Unblocks Step 4.**
- `sacred-dawn/projects/women-in-the-water/`: master.csv, patch_deep_depth.py (COMMITTED).

**WPM decision:** reconciled to **159** because `_LEGO.md` S0.0 (the authoritative override
block) declares 159 as the shipping model and 143 as the retired illustrative number. IF an
actual re-measure of Elliot says otherwise, change `WPM_NEW` in `patch_sacreddawn_timing.py`
and re-run (idempotent) -- one constant.

## 8. OPEN ITEMS / RESUME PLAN (in bite order)

1. **channel.json check (quick):** confirm `sacred-dawn/channel.json` does NOT carry a stale
   hard WPM/words-per-block field. Inspect:
   `python3 -c "import json;print(json.load(open('sacred-dawn/channel.json')))"`
   Also confirm `image_model` == `nano_banana_2` and `style_suffix` is palette-only.
2. **Write `canon.json`** for the project with the 12 tokens above (needed before Step 6).
3. **Add the anti-scroll negatives to `sacred-dawn/rulebook.json`** (G11/G12): no scroll on a
   table, no book on a lectern/stand, no study/library, no window-behind-desk, no quill, no
   scattered pages -- NEVER ban "book" itself.
4. **Step 4 -- VO convergence:** emit ONE whole-film `narration.txt`, render Elliot @159,
   whisper, `calibrate` the 200s seams; repeat until every seam within ~8s; VO LOCKED.
5. Then Step 6 (probe20 -> gravity-well sweep -> grid), Step 7 (pick -> place -> air/move/
   motion), Step 8 (render_clips), Step 9 (Filmora: cold open cut last, music, ship).

## 9. FILE INVENTORY (this project folder)

- `master.csv` -- 320 beats, source table (COMMITTED).
- `beats_data.py`, `normalise.py` -- the consolidation + interrogation scripts (scratch;
  master.csv is the artifact they produce).
- `patch_deep_depth.py` -- the 15-beat foreground pass (COMMITTED).
- `patch_lego_rewrite_brief.py` -- inserts REWRITE BRIEF into _LEGO.md (run laptop-side).
- `patch_sacreddawn_timing.py` -- WPM 143->159 reconcile (run laptop-side).
- `_SESSION-2026-07-21-women-in-water.md` -- this file.

## 10. GIT

- Committed + pushed + pulled-on-box this session: a572e4d
  (findings G1-G21, master.csv, patch_deep_depth.py, patch_lego_testrun.py).
- To commit next: the two new patch scripts + their applied results on
  `shared/docs/_LEGO.md` and `shared/docs/_Sacred-Dawn.md` + this session note.
- Discipline reminder: `git pull --no-edit` before push; explicit named paths, never
  `git add -A`; do NOT stage `.pre_*` backups.
