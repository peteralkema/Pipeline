# SESSION NOTES — 15 Jul 2026
### Sacred Dawn · The Book of Enoch · 1600 stills → 400 picked → 400 Kling clips
**Companion docs:** `_ENOCH-MASTER-SESSION.md` · `_Sacred-Dawn.md` · `_SCRIPT-CONTRACT.md` · `_MOTION-DOCTRINE.md` · `_LEGO-FEATURE-FILM.md`

The session that took Enoch from "ten scripted blocks" to "400 Kling-ready clips with derived motion."
Total spend: **$128 stills + $3.20 probes + ~$168 Kling ≈ $300** for a 30-minute feature.

---

## THE ARC
Started at "render the ten blocks." Immediately hit a doctrine contradiction that would have wasted
the whole $128. Fixed it, probed it, found a second bug (faceless), fixed it, probed again, found a
third (tears-default), fixed it. Then rendered 1600, carouseled to 400, derived 400 camera moves,
found a fourth blanket bug (settle-lull), fixed it, and verified the motion survived all the way into
the file Kling actually reads. **Four bugs, all the same shape: a blanket rule stamped on 100% of beats.**

---

## PART 1 — THE GRADE GATE (before any spend)

**1. The doctrine contradicted itself.** `_Sacred-Dawn.md` §2 welded into `style_suffix`: *"deep indigo
shadow… one unearthly light source… shafts of god-ray light."* `_ENOCH-MASTER-SESSION.md` (one day
later) called that verbatim string **"THE STORM-SHAFT BUG"** — it forced dark-storm onto all 160 stills,
un-selectable. Its replacement swung the other way: *"blue skies and green landscapes… warm golden
sunlight"* — which is Scripture's lane, not Sacred Dawn's.
**Neither was right.** Rendering under either would have taught us nothing.

**2. The reconciliation — palette in the suffix, drama in the beats.**
Keep Sacred Dawn's colour (burnished bronze, aged stone, weathered antiquity, Balrog-real mass,
bright-crisp HDR, heavy air, anti-murk negatives). **Remove** the unearthly light source, god-ray shafts
and blanket indigo from the suffix — those are *content*, and the per-beat prompts already carry their own
light ("shaft of warm light", "in a dim chamber"). Evidence it was right: `build_enoch_all.py`'s own header
already said *"grade lives in the suffix, NO grade words in prompts."* The beats were authored against a
palette-only suffix. The welding was the error.

**3. The box had drifted.** `git pull` on the box **aborted** — an uncommitted local edit to
`sacred-dawn/channel.json` (the warm-daylight suffix, hand-edited during the Enoch session, never committed)
blocked the merge. `git diff` showed the committed HEAD was still the *v1 painterly* suffix. Three versions
of the same key in three places.
→ `git checkout -- sacred-dawn/channel.json` then pull. The abort **saved us** — it forced the discovery.

**4. My verify was too narrow and produced a FALSE PASS.** The first check only screened for storm-shaft
terms. The box's warm-daylight suffix sailed through and reported three PASSes on the *wrong* grade.
**A verify must distinguish every known-bad state, not just the one you're thinking about.** The corrected
4-way check screens: reconciled markers present, warm-daylight terms absent, storm terms absent, image_model
correct. All four green before spend.

**5. `image_model` fork.** Module default is still `flux` (the murk styliser). `nano_banana_2` must be set
explicitly per channel or character-less beats silently fork to a second model = two looks in one film.
Patched into `channel.json` alongside the suffix.

---

## PART 2 — PROBE #1: THE REGISTER (20 stills, $1.60)

**Design: register-spread, not uniform-random.** Per block, take the *most cosmic* beat AND the *most
earthly* beat. A uniform draw can hand you 20 cosmic beats and never test the daylight half — which is the
half the storm-shaft suffix wrecks. Came out 14 cosmic / 6 earthly (blocks 7–10 are genuinely almost all
supernatural — honest to the film). The six earthly ones were the **canaries**.

**Result: PASS on both axes.** Daylight beats rendered bright-warm-real with no storm stamped on them and
no green slop. Cosmic beats held bronze-shadow-massive with real Balrog weight — the giants were the
standout, physical and dust-displacing, zero glowing vapor. Consistent across all 20, no fork, no murk.

**Three findings, none of them register failures:**
- **The literal-metaphor bug (banked as a rule).** "The keys to the world" rendered as a literal glowing key
  handed to people holding a **modern blue-marble Earth globe** — corny, and a straight "no modern elements"
  violation. → **No literal-metaphor beats. Render the consequence, not the metaphor.** Models render
  metaphors as corny props and anachronisms.
- **Angels default to statues.** Massive, bronze, on-grade — but stone and static on pedestals. If you want
  them alive, the beat must say *living, flesh, moving*.
- **Period drift.** Greco-Roman columns, Egyptian reliefs, near-Renaissance towers in an antediluvian-
  Mesopotamian world. Per-beat tightening, not systemic.

---

## PART 3 — FACELESS → ANONYMOUS (bug #2)

**The bug:** the generator stapled one tag — `(seen from behind or in silhouette, face not visible)` — onto
**all four variants of all 1600 stills**. That's *faceless*, and it kills the thing that carries a story arc:
a human face loading the emotion of the beat.

**The distinction, banked:**
> **Faceless hides every face. Anonymous just never locks one.**
> The drift risk came from repeating *one* Enoch face with no reference canon. The fix isn't hiding faces —
> it's (1) keep the recurring lone figure turned or distant so *he* never needs a consistent face, and
> (2) let faces show freely on everyone else. **A different anonymous face each time reads as humanity
> reacting, not as continuity breaking.** Faces become a variety axis, not a thing to suppress.

**The fix — a face-visibility gradient per variant (not one blanket):**
| variant | framing | face |
|---|---|---|
| **a** WIDE | phenomenon dominant, human tiny | none — anonymous *by distance* |
| **b** MID | human larger, low frame | partial — three-quarter or profile |
| **c** TIGHT | the reaction shot | **full anonymous face + emotion** ← the story-load frame |
| **d** WILDCARD | authored hero | varies |

Validated 400/400 on each rung before regenerating.

---

## PART 4 — PROBE #2: THE FACES (20 stills, $1.60)

**Design: face-weighted** — 10 tight (c), 5 mid (b), 3 wide (a), 2 wildcard (d), still spread across all ten
blocks and both registers. Register was already answered; this probe tested only the new thing.

**Result: PASS.** The c-rows rendered genuinely expressive faces carrying the beat. The a-rows stayed
faceless-by-distance — gradient holds. **Anonymity held**: men and women, different ages, clearly different
individuals, no recurring Enoch face, and the protagonist was never the tight-face subject. Bonus: the
literal-metaphor bug was gone (the keys beat rendered as a reacting face), and angels came back as *living*
armored figures rather than statues.

**The finding — tears-default (bug #3).** Nearly every face was weeping. *"Awe, fear, or grief as the scene
demands"* collapsed to grief. That kills the emotional-variation lever precisely where it matters: the
storehouses-of-stars and city-of-light beats want dry-eyed **wonder**; the giants want **fear**. If all 400
tights cry, you're forced at pick-time to drop the face on a wonder beat and fall back to a wide.

---

## PART 5 — EMOTION ROTATION BY REGISTER (fix #3)

Wired a classifier into the generator: score each beat against awe-words / fear-words / grief-words, then
select the tight's emotion phrase from the winner. Same mechanism as the cosmic/earthly probe scoring.

**Result across 400 tight shots: fear 199 / awe 161 / grief 40** — and it maps to content exactly:
| block | awe | fear | grief | why |
|---|---|---|---|---|
| 4 (giants) | 0 | 38 | 2 | pure horror block |
| 7 (heaven) | 34 | 6 | 0 | pure wonder |
| 8 (the moon) | 37 | 3 | 0 | pure wonder |
| 9 (the dead) | 15 | 8 | 17 | the grief block |

That's the retention principle from the external script critique — *emotional variation between chapters* —
now living in the reaction shots rather than in the prose.

---

## PART 6 — THE 1600 RENDER ($128)

**Batch the machine work, chunk the human work.** The block boundary buys nothing at the *render* step —
same spend, one unattended tmux run is less babysitting than ten. The block existed to protect the **pick**,
not the render: 160 is one coherent carousel you can hold in your head; 1600 is a slog that flattens your eye
by frame 600, and a tired pick is a weak clip you pay $0.42 to animate.
→ **Render all 1600 in one run. Review in ten sittings of 160.**

**The cache trap (cost: a wasted partial run).** Re-running into the *existing* `enoch-blockNN` folders
printed *"already done, skipping"* on 155/160 — the pipeline caches by **filename**, not by prompt content.
Every prompt had changed (faceless→anonymous→emotion) and it skipped them all. Stale frames would have gone
to carousel.
→ **Fresh `-v2` project folders.** Zero chance of stale state, old stills preserved for comparison, identical
cost. **Never re-render into a folder that already has stills.**

**Pre-flight battery (all green before firing):** 10 files × 160 beats = 1600; 0 empty prompts;
1600/1600 anonymous; 0 grade-leak into prompts; 100% ASCII (em-dashes normalized — they inflate word counts
and are the only non-ASCII the authoring produces); ten clean `--storyboard-only` ingests.

Ran in tmux, ~$128, no crashes, no flux fallbacks.

---

## PART 7 — THE CAROUSEL (the taste signal)

400 winners, 40 per block. Integrity gate: **40 picks, no duplicate beats, no missing beats** — on all ten.
> 40 picks does NOT guarantee one-per-beat. You can hit 40 with two winners on beat 7 and none on beat 23.
> That silently corrupts the beat order in the finish project and you'd only find out after $168 of Kling.

**The variant spread — the session's most interesting finding:**
```
a(wide)=100   b(mid)=81   c(face)=75   d(wildcard)=144
```
- **d wins by a mile (36%).** The *authored per-beat hero shot* was chosen more than any formula variant.
  Block 8 is the proof: a=2, d=20. **The a/b/c grammar is a safety net that guarantees every beat has a
  usable frame; the bespoke wildcard is what the eye actually reaches for.**
  → **Next film: weight generation toward more authored wildcards, fewer mechanical variants. Better picks
  for the same $128.**
- **c=75 (one reaction face every ~24 seconds)** — the faces are doing real work. The two probes and the
  rewrite reached the viewer.
- **Block 10 flagged:** a=17, c=4. The apocalyptic climax — highest-retention moment in the film — is 43%
  wides with four faces in 3.5 minutes. Playing as spectacle at the moment the film most needs a face to tell
  the viewer how to feel. Left as-is (a re-pick is free, a re-Kling isn't) but flagged for the next read.

---

## PART 8 — DERIVED MOTION (the assembler)

**The crux: motion derives from beat × variant × register — NOT beat alone.**
Beat 12 picked as an `a` wide is a scale-reveal → PULL-BACK. The *same beat* picked as a `c` tight face is one
overwhelming subject → PUSH-IN. Deriving from beat text alone would be wrong half the time. The picks record
(`beat → shot → variant`) is what makes correct derivation possible.

**The precedence ladder (first match wins):**
1. **grief/aftermath → SETTLE** (never push)
2. **vertical force → CRANE-UP** (overrides framing)
3. **c tight face → PUSH-IN** (a face *is* the single overwhelming subject)
4. **a wide → PULL-BACK** (that framing's meaning IS scale)
5. **b mid → PUSH-IN**
6. **d wildcard →** read off beat text (scale→pull, vertical→crane, else push)

**The VO adaptation (a conscious departure from the doctrine as written).** `_MOTION-DOCTRINE.md` was written
for a *music-driven montage* where silence is structural. Enoch has Elliot riding above all 400 clips —
**there is no silence.**
- *"Never push-in on silence"* re-reads as **"never push on the grief/aftermath beats."** Same rule, new trigger.
- **NEAR-LOCKED is retired for narrated features.** Under continuous VO a locked frame reads as a stalled
  slideshow, not a held breath. SETTLE carries the quiet work.

**Bug #4 — the settle-lull.** First derivation gave block 9 **17 SETTLEs out of 40** (every other block: 0–5).
43% of the film's softest retention block — sitting between the moon and the finale — barely moving.
**Cause: the grief classifier fired on "the dead / souls / waits" and overrode everything**, so cosmic-wonder
beats that merely *concern* the dead ("The chambers vast and deep", "A map of the afterlife", "The angel over
the dead") were classified as mourning and settled.
**Fix: correct the register of the 13 misclassified beats, then RE-DERIVE with the normal rules.** Motion stays
derived, never hand-picked. Kept 4 genuine settles — *if nothing settles, nothing pushes.*
`17 → 4`. Block 9 now rotates like every other block.

**Final verified spread (400 clips, read from `storyboard.json` — the file Kling actually reads):**
```
PUSH-IN 178   PULL-BACK 123   CRANE-UP 72   SETTLE 27   OTHER/DEFAULT 0
```
Zero defaults = every clip carries our derived prompt, not `_default_motion`.
The rotation is real and motivated: block 1 crane-heavy (15) where the world establishes vertically;
block 8 push-dominant (27) driving into cosmic architecture; block 10 pull-heavy (19) opening for the
apocalypse; blocks 7–8 zero settles because they have zero grief beats.

---

## PART 9 — READING THE ACTUAL CODE (the step that prevented the $168 mistake)

Refused to guess the animate CLI. `grep` on `recreation_pipeline.py` revealed:
- **There is no `animate` subcommand** — it's **`finish`** ("animate + narrate + assemble").
- `animate_still(still_path, motion_prompt, out_path)` (L864) → per-still motion **is wired**, not a thing to build.
- Beat-script ingest (L1528) reads `motion_prompt` from beats.json, falls back to `_default_motion` if blank,
  and writes it per-shot into **`storyboard.json`** (L1547).
- **The animate leg reads `storyboard.json`, NOT `beats.json`.** Our finish projects had no storyboard —
  `build_finish.py` placed frames and copied beats.json, and nothing ever ran ingest.
  → **Without the ingest step, all 400 clips would have animated with `_default_motion`** and the entire
  derivation, veto table and block-9 fix would have evaporated silently. **$168 for 400 identical moves.**
  → Fix: `stills --storyboard-only` on each finish project (ingests beats→storyboard, explicitly skips still
  generation, never touches the 400 picks).
- `_tiered_kling_count` (L1605) reads **`render_policy.json`**, not `channel.json` — the `channel.json`
  `kling_count` edit did nothing. Default is 40; `--kling-count 40` overrides both. **Pass it explicitly.**
- `finish --animate-only` = animate then STOP (no narrate/score/assemble) — exactly right when cutting in Filmora.
- `finish --plan` = print the Kling/Ken-Burns routing and cost, then exit. **Free, definitive answer to
  "will all 400 get Kling?"** — beats reasoning about it.

---

## THE LESSONS (tool-agnostic — this is the moat)

**1. Any rule that applies to 100% of beats is a bug until proven otherwise.**
Four instances this session, four different layers:
| # | layer | the blanket | the fix |
|---|---|---|---|
| 1 | grade | storm-shaft welded into `style_suffix` | palette in suffix, drama in beats |
| 2 | faces | faceless tag on all 1600 | per-variant gradient |
| 3 | emotion | "deeply moved" on all 400 tights | register-rotated per beat |
| 4 | motion | SETTLE on all 17 "grief" beats | corrected register, re-derived |
> Drama is earned by content, not stamped by grade. The same sentence is true of faces, emotion and motion.

**2. Read the source, don't reconstruct from memory.** Every fix this session came from reading actual code or
actual docs. Every error came from assuming. The `storyboard.json` discovery alone saved $168.

**3. A verify must distinguish every known-bad state.** A check that screens for one failure mode will
happily pass a different one. My storm-shaft-only check gave three green PASSes on the warm-daylight grade.

**4. Probes are absurdly cheap insurance.** $1.60 twice = $3.20 to de-risk $128 of stills and $168 of Kling.
Probe design matters as much as probing: **spread the sample across the axis you're testing**, and re-weight
the probe toward whatever changed since the last one.

**5. Free gates exist — use every one.** `--storyboard-only`, `--dry-run`, `--plan`, integrity checks,
`git diff` before commit. Every one of them costs nothing and each caught something real.

**6. Box drift is a live landmine.** Uncommitted hand-edits on the box block pulls at the worst possible
moment and hide the true state of a file. **Edit on laptop → commit → push → pull.** Always.

**7. Caches are filename-based.** Never re-render into a folder that already has output. Fresh folders cost
nothing and remove a whole class of silent staleness.

**8. Taste is selection, not specification** — reconfirmed, with a twist. The human picks, the machine
generates wide. But **the authored wildcard beat the formula 36% of the time**: generate wide *and* author
the hero. The picks record is the only artifact of the taste signal — the session forgets it. **Back it up.**

**9. Batch the machine work, chunk the human work.** Render 1600 in one unattended run; carousel in ten
sittings of 160. The block was always protecting your eye, not your wallet.

**10. Doctrine transfers by re-reading, not by copying.** `_MOTION-DOCTRINE.md` was written for a silent
montage. Two of its rules needed re-triggering for a narrated feature (silence→grief; near-locked retired).
**Name the departure explicitly** — never silently reinterpret, never blindly apply.

---

## THE RUNBOOK (what we actually ran, in order)

```
# 0. GRADE GATE — laptop
python3 patch_sacred_dawn_suffix.py          # reconciled suffix + nano_banana_2
git diff sacred-dawn/channel.json            # only 2 keys change
git pull --no-edit && git add … && git commit && git push
# box
git checkout -- sacred-dawn/channel.json     # discard drift ONLY after reading git diff
git pull --no-edit
<4-way verify: reconciled markers / no warm / no storm / nano_banana_2>

# 1. PROBE #1 (register)  — 20 stills, $1.60
# 2. FIX: anonymous face gradient  → regenerate
# 3. PROBE #2 (faces)     — 20 stills, $1.60
# 4. FIX: emotion rotation by register → regenerate

# 5. THE 1600 — box, fresh -v2 folders, tmux
for n in 01..10; do python shared/recreation_pipeline.py stills \
  --beats sacred-dawn/projects/enoch-block$n-v2/beats.json \
  --project sacred-dawn/projects/enoch-block$n-v2 --storyboard-only; done   # free
for n in 01..10; do python shared/recreation_pipeline.py stills … ; done     # $128

# 6. PULL + CAROUSEL — laptop, per block, Winners/ folder
<integrity: 40 picks, no dupes, no missing — all ten>

# 7. ASSEMBLE — laptop
python3 build_finish.py emit                 # derives motion, writes veto table
python3 patch_block09_motion.py              # settle-lull fix 17→4
git add -f build_finish.py enoch-finish/ && git commit && git push

# 8. PLACE + INGEST — box  (ingest is MANDATORY; animate reads storyboard.json)
python build_finish.py place
for n in 01..10; do python shared/recreation_pipeline.py stills \
  --beats sacred-dawn/projects/enoch-block$n-finish/beats.json \
  --project sacred-dawn/projects/enoch-block$n-finish --storyboard-only; done
<verify: 400 shots, 0 OTHER/DEFAULT, block09 SETTLE=4>

# 9. PLAN then FIRE — box
for n in 01..10; do python shared/recreation_pipeline.py finish \
  --project sacred-dawn/projects/enoch-block$n-finish --kling-count 40 --plan; done   # free
tmux new -s enochkling
for n in 01..10; do python shared/recreation_pipeline.py finish \
  --project sacred-dawn/projects/enoch-block$n-finish --animate-only --kling-count 40 --no-music; done
```

---

## STILL OPEN
- Fire the 400 Kling clips (~$168) after a clean `--plan`.
- Ten block MP3s from `enoch-narration-script-v2.md` (Elliot, 1.0, ~28:42 total).
- Filmora: 10 blocks laid end-to-end, VO over, seams by hand.
- **Cold open cut LAST** from the best shot of each block (see `_ENOCH-OPENER.md`).
- Thumbnail: render a **clean plate** (no text instruction at all — mentioning text summons text; the model
  added a hallucinated "4K ULTRA HD" badge three times) and lay the ENOCH lockup in yourself. Identical type
  across every Sacred Dawn video **is** the series branding — a generative model can't give you identical twice.
- Backlog: `reference_style_anchor` still read-but-unwired; module default `IMAGE_MODEL` still `flux`;
  `.pre_block09motion_*` backup swept into the repo (`git rm --cached`).
