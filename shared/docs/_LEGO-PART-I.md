<!--
  PART I -- THE PROCESS & THE DATA.  Prepend to _LEGO.md; it becomes the lead.
  Consolidated 19 Jul 2026. Leads with the process; the CSV is the heart; the
  session's variant-grid / gravity-well-sweep / Ken-Burns-moves / project-structure
  work is folded in here. The existing craft sections (Opening Law, prosody, variety
  law, spine, timing) remain below as PART II -- the law that hangs off this process.
  SUPERSEDES the old Section 10 pathway (PHASE 0-12): the PROCESS below replaces it.
-->

# _LEGO.md -- the channel-agnostic pathway for cinematic feature videos

**Two outputs, and only two:** `clips/shot_NNN.mp4` (one clip per beat) **+** `voiceover.mp3`
(one continuous narration track). Everything in this document exists to produce those two
artifacts; **Filmora assembles them by hand** (music, seams, title, export). There is no third
output and no automated assembly on this path.

**The heart is the beat CSV.** One row per beat. Every per-beat decision is a **column**; the
programs are **dumb readers** of those columns; per-channel settings live in **three JSON files**,
never in code.

> ### THE ARCHITECTURE IN ONE LAW
> **Per-beat config -> a CSV column. Per-channel config -> the channel's JSON. Nothing in code.**
>
> Dumb code + data-driven parameters is the moat. A new video is a new CSV; a new channel is a new
> folder of JSON. Every fix this pipeline has ever shipped was a **data change, not a code change**
> -- the geometry sweep was 25 cells, the earthrise fix was one token, the motion is one column.
> When you are tempted to add a special case in code, **add a column instead.** The code stays dumb;
> the gates (Section: PRE-SPEND CHECKLIST) keep the dumb code safe by validating the data at the door.
>
> *Stay on CSV until a cell wants to be an object* (nested structure, per-variant sub-fields). That
> shape -- not the number of videos -- is the only signal to move to SQLite/JSON-per-beat, and
> because the code is dumb (it reads named rows, not "a CSV"), that move is a loader swap, not a rewrite.

---

## THE PROCESS -- 0 to 9 (this leads; everything hangs off it)

Run in order. Three orderings are load-bearing and cost money if broken: **package first** (the
click decides whether the film is watched), **VO before stills** (measure the cheap layer, preserve
the expensive one), **motion after the pick** (motion is read off a picked frame). The golden
thread: *truth costs nothing -- buy it repeatedly; gate before every spend; observe -> bank -> feed
the next film.*

| # | STEP | program(s) | columns touched | gate | output |
|---|---|---|---|---|---|
| **0** | **PACKAGE FIRST** -- topic for the CLICK; winnability gate (demand exists AND a small channel broke this lane); commit title + thumbnail CONCEPT (curiosity gap). Un-packageable -> **kill here, $0.** | (human + NexLev) | -- | title + thumbnail exist | a title, a thumbnail concept, a winnability verdict |
| **1** | **ARCHITECT** -- runtime -> N x 200s blocks (200s = the seam unit); per block define its curiosity-gap + HANDOFF to the next; map the spine (cold open -> escalation -> turn -> payoff); **name the canon tokens** the film needs. | (human) | `block_id` | block plan exists | N blocks, each with role + gap + handoff + token set |
| **2** | **AUTHOR BLOCK BY BLOCK** -- per beat write `phenomenon` + `narration` under the craft grammar (PART II 3A); canon `{token}` on every beat; ~12-word draft aim; weight hero/connective; build variety across every axis. **Per-block CSVs live in CHAT, not on disk.** | (human authoring) | `phenomenon` `narration` `weight` `register` `sentence_id` | **GATE each block**: VISUAL present, <=55 words, tokens resolve, no banned words, register/setting sweep | one gated block CSV (in chat) |
| **3** | **MERGE + INTERROGATE THE MASTER** -- merge block CSVs -> ONE master; `normalise` fills the derived columns; then read the film AS DATA (setting mix, register spread, axis ratio, hero/connective balance, word histogram, repeated-composition scan). Adjust. | `build_beats normalise`, `sweep` | fills `setting` `words` `variants` `*_cost` | RE-GATE the master | gated master CSV + variety audit; **the project folder is born here (or at the Step-0 thumbnail)** |
| **4** | **VO CONVERGENCE** -- emit one `narration.txt` (whole film, one Inworld call); render VO; whisper; `calibrate` -> per-beat over/under + seam drift; edit the CSV **both directions** and sharpen punch/hero-lines/facts each pass. | `build_beats audio`, `calibrate` + Inworld + Whisper | reads `narration` `block_id` | -- | `voiceover.mp3` rendered, seams measured |
| **5** | **REPEAT 4** (~twice) -- stop when every seam is within ~8s of its 200s mark. **VO LOCKED** (output #2). | as Step 4 | `narration` | every seam within ~8s | **VO locked** |
| **6** | **PROBE, THEN THE GRID** -- `probe20` (20-beat register sample); read vs the verdict card -> name the FAILURE CLASS; **sweep the master film-wide, setting-aware** (two homes: rulebook negatives + `phenomenon` geometry); re-probe `--force` until clean; THEN `grid` -> `render_grid` -> the variant grid (4 real re-rolls/hero, 2 real + 2 `_skip.png`/connective), one folder + `GRID-INDEX.csv`. | `build_beats probe20`, `grid`; `render_grid.py`; rulebook edits | reads `phenomenon` `variants`; sweep edits `phenomenon`, `setting` | probe reads clean; first ~10 grid frames >> 7KB (not black rejects) | grid stills `{beat}-{variant}.png` |
| **7** | **PICK + AIR + MOVE + MOTION** -- hand-pick ONE variant per beat (a skip-tile pick = hard fail); `place` the winners into `shot_NNN.png`; assign `air` (Kling vs Ken Burns) and the doctrine `move` off the PICKED frame; write `motion` only on Kling beats. | `place.py`; `render_clips.py`; move drafter | fills `air` `move` `motion`; reads all three | place = N files, no gaps/dupes/skip-tiles; a Kling beat with no `motion` aborts | placed stills + the routing plan |
| **8** | **RENDER CLIPS** -- `render_clips` per beat: `air`=Kling -> `animate_still(motion)`, else -> `ken_burns_still(move)` (the doctrine-varied free floor). `--floor-only` forces all Ken Burns. | `render_clips.py` -> engine `animate_still` / `ken_burns_still` | reads `air` `move` `motion` | `--dry-run` shows split + cost before spend | **`clips/shot_NNN.mp4`** (output #1) |
| **9** | **ASSEMBLE + SHIP + OBSERVE** -- clips + locked VO in Filmora (music, seam swells, title); export; thumbnail from Step 0; upload. Then read CTR+AVD @48h, day-14/21 traffic; **bank every failure as portable law here**; feed it back to Step 0 of the next film. | Filmora (human) | -- | -- | shipped video -> observations -> next film's Step 0 |

> **The output boundary.** The pipeline ends at Step 8: **clips + VO**. Everything after is Filmora
> and packaging -- the human/craft layer. The pipeline's whole job is to hand Filmora 320 clips in
> beat order and one narration track, gated and correct.

---

## THE BEAT CSV -- THE HEART (the column dictionary)

One row per beat, flat, ordered -- the single source of sequence. **Authored** columns are written
by the human; **derived** columns are computed by `build_beats normalise` from the authored ones
(never hand-edited). Read this as: *which step fills it, which program consumes it, what it does.*

| column | kind | filled at | read by | what it does / inputs |
|---|---|---|---|---|
| `block_id` | authored | Step 1-2 | `build_beats` (all), `render_clips` order | which 200s block -- the seam/retention/chapter unit |
| `clip_index` | authored | Step 2 | `build_beats` | beat position within its block (1..40) |
| `sentence_id` | authored | Step 2 | `calibrate` | groups contiguous rows for TTS/timing; never reorders |
| `weight` | authored | Step 2 | `build_beats grid` | `hero` \| `connective` -> the variant COUNT |
| `register` | authored | Step 2 | move drafter; authoring | emotional register (awe/dread/grief/wonder) -> drives `move` + tone |
| `narration` | authored | Step 2, sharpened 4-5 | `build_beats audio` -> `narration.txt` | the spoken line. **HALF the final output.** Pure text, NO tokens, NO markup (whisper measures it, the gate counts it) |
| `phenomenon` | authored | Step 2, swept Step 6 | `render_grid` -> `generate_still` | the image prompt -> the still -> the clip. Carries the canon `{token}` inline. Names its own scene light. |
| `setting` | **derived** (leading `{token}` of `phenomenon`) | `normalise` | `gate_canon`, `_expand_canon` | which canon place-lock the beat uses -> the grade/anti-drift; **the sweep is setting-aware off this** |
| `words` | **derived** (from `narration`) | `normalise` | audit / `calibrate` | word count -- the ~12/beat draft *measurement* (not a gate) |
| `variants` | **derived** (from `weight`) | `normalise` | `render_grid` | how many REAL re-rolls to fal (hero 4 / connective 2); the rest fill with `_skip.png` |
| `still_cost` `clip_cost` `beat_cost` | **derived** | `normalise` | audit | the bill of materials -- exact pre-spend cost, visible while still text |
| `air` | authored | Step 7 (off picked frame) | `render_clips` | `kling` (visible suspended matter) \| `kb` (flat -> Ken Burns floor). **Independent of `weight`.** |
| `move` | authored/drafted | Step 7 (off picked frame) | `render_clips` -> `ken_burns_still(move)` | the doctrine move: `push` \| `pull` \| `crane` \| `settle` \| `static`. **Applies to the Ken Burns floor now; the same read frames Kling later.** Drafted by the move drafter, corrected by eye. |
| `motion` | authored (conditional) | Step 7 | `render_clips` -> `animate_still(motion)` | free-text Kling motion prompt. **Only used when `air`=kling**; a Kling beat with a blank `motion` aborts before spend. |

**The pick is encoded in the winner FILENAME, not a column.** `place.py` reads the winners folder
(`{beat}-{variant}.png`) directly; there is no `picked_variant` column to keep in sync. The winner
files ARE the pick manifest.

**The invariants the dumb readers depend on (enforced at the door, PART II checklist):**
- `narration` never carries a token or markup -- it is the one column that must stay pure.
- The canon is `{tokens}` INSIDE `phenomenon`, never its own column (Section 13 / engine already does this).
- Every beat resolves to exactly `variants` real files + `_skip.png` fill to 4; a **skip-tile pick is a hard fail**.
- `move` in {push,pull,crane,settle,static}; a Kling `air` beat has a non-empty `motion`.
- Derived columns are NEVER hand-edited -- edit the authored source, re-run `normalise`.

---

## THE PROGRAMS & THEIR INPUTS (dumb readers, one per stage)

All are channel-agnostic: they read the video's CSV/beats.json and resolve the *channel* from the
output path (`generate_still`/`ken_burns_still` anchor config, `style_suffix`, and rulebook
negatives on `out_path`). A new video = new paths; a new channel = new JSON. No program knows "moon".

| program | reads | writes | notes |
|---|---|---|---|
| **`build_beats`** *(today `build_moon.py`; lift to `shared/` at video two)* | master CSV, `canon.json` | -- / beats.json / narration.txt | subcommands: `normalise` (fill derived), `sweep` (audit), `audio` (emit narration.txt), `calibrate` (whisper vs 200s seams), `probe20` (auto-select 20 canaries), `grid` (whole-film beats.json + GRID-INDEX.csv), `blocks` (per-block) |
| **`render_grid.py`** | grid beats.json, `canon.json`, `_skip.png` | `stills/{beat}-{variant}.png` | renders `variants` real re-rolls per beat + `cp _skip.png` to 4. Reuses `generate_still`. Resume-safe. |
| **`place.py`** | winners (folder or filename list), grid stills, `_skip.png` | `stills/shot_NNN.png` | pure stdlib; hard-fails on skip-tile pick, gap, or dupe. Sources bytes from the grid stills by filename. |
| **`render_clips.py`** | master CSV (`air`/`move`/`motion`), placed stills | `clips/shot_NNN.mp4` | per beat: Kling(`motion`) if `air`, else `ken_burns_still(move)`. `--floor-only`, `--dry-run`. Reuses engine funcs. |
| *(engine)* `generate_still` / `animate_still` / `ken_burns_still` | prompt/still + `out_path` | png / mp4 | shared, UNMODIFIED by the movie path except the additive `ken_burns_still(move=...)`. Config resolves from `out_path`. |

---

## PER-CHANNEL CONFIG (the three JSON files -- NOT the CSV)

Per-*channel* facts live once per channel, shared across all its videos. Per-*beat* facts are CSV
columns. Nothing is in code.

| file | holds | read by |
|---|---|---|
| **`<channel>/channel.json`** | grade / `style_suffix`, `voice_id`, aspect, `image_model`, `ken_burns` flag | resolved from `out_path` by every render func |
| **`<channel>/projects/<video>/canon.json`** | the `{token}` DEFINITIONS (what each `{place}` IS) -- the anti-drift place-locks. Which token a beat uses is the CSV `setting`/`phenomenon`. | `_expand_canon`, `gate_canon` (greps token TEXT for banned words -- never put a banned word, even negated, in a token) |
| **`<channel>/rulebook.json`** (+ universal `shared/rulebook.json`) | `negative` (spell-breakers -- kills what renders UNPROMPTED: gears, galaxies, door furniture). CWD-scoped: edit from the channel dir. | merged into every prompt by the render funcs |

> **Project structure.** One folder = one final video (its whole life: master CSV, canon, VO, grid
> stills, picks, clips, thumbnail). Render outputs are SUBFOLDERS inside it, never siblings. The
> folder is triggered by the ready-to-build master CSV or the Step-0 thumbnail, never grown per block.
> Per-block CSVs are chat-only drafts (Step 2).

---

## THE GRAVITY-WELL SWEEP (Step 6 -- probe discovers, sweep fixes)

> **The probe FINDS the failure class; the sweep FIXES it film-wide. Different jobs.** The 20-beat
> probe (~$1.60) is a sampler -- it caught the door-well on ONE beat that lived on EIGHT. Fix only the
> probed beats and you ship the disease in the ones it never sampled.

- **Two homes for every fix.** What the model renders **unprompted** (gears, galaxies) -> the
  **rulebook `negative`** (word-removal can't touch what was never in the prompt). Wrong **geometry**
  (a door where a shaft belongs) -> the **`phenomenon`** column (a door and an opening-in-rock are the
  same negative space; only re-authoring the light direction fixes it). Neither alone is enough.
- **Setting-aware.** "Light through the opening" is a bug on `{heavens}` (surface pits) but correct on
  `{interior}`/`{winds}` (see-through) and `{chapel}` (a window). Classify every hit by its token
  before rewriting, or a blind regex wrecks the beats that were right.
- **Never negative the subject.** Banning "gate"/"opening" makes the model render empty rock (the
  Pompeii empty-rooms lesson). Ban door furniture / wrong mechanism / stray astronomy -- never the
  openings themselves.
- **A canon-token contradiction is a well.** A beat authoring what its token forbids (`{heavens}` says
  "no earth", the beat says "the bright curve of the earth") drifts to mush. Fix with a NEW token that
  permits it (`{limb}`) + retag those beats -- never relax the shared token (it leaks to all its beats).

---

## THE VARIANT GRID (Step 6e -- the pick candidates)

**The 4 variants are 4 RE-ROLLS of one prompt, not four framings.** Same `phenomenon`, four fal calls,
non-determinism gives four frames of the one composition; you pick the cleanest render. (Four
different framings would need four prompts per beat -- unbuilt; the CSV `variants` column is a COUNT.)

- **Every beat has exactly 4 files:** hero = 4 real; connective = 2 real + 2 `_skip.png`. Cost is the
  count of REAL stills (`sum(variants) x $0.08`), visible in the table before you spend.
- **Filename = `{beat:03d}-{variant}.png`, one folder, mapped by `GRID-INDEX.csv`.** No pick surface --
  dump and review manually. A pick that lands on a skip tile is a hard fail (`place` catches it).

---

## THE KEN BURNS DOCTRINE MOVES (Step 8 -- the motion doctrine applies to the free floor)

The floor is not a slideshow. `ken_burns_still(move=...)` runs one slow ffmpeg zoompan the **full 5s**,
one move per beat, read off the picked frame exactly like the motion doctrine (PART II Section 7):

| move | camera | doctrine trigger |
|---|---|---|
| `push` | slow zoom IN | one overwhelming subject (the default) |
| `pull` | slow zoom OUT | scale / number / how-far |
| `crane` | slow rise | vertical phenomena (rising, columns, towers) |
| `settle` | slow drift DOWN | reflection / aftermath / grief |
| `static` | held frame | eerie stillness / near-locked (use sparingly) |

Magnitudes are deliberately small (push -> 1.16x, crane/settle pan ~11%) so continuous-across-5s reads
as *alive*, not as a Ken Burns cliche. Because the floor is **$0**, iteration is free: render all, eyeball
a sample, and a bad *feel* is a one-number tune + a free `--force` re-render -- the probe discipline
inverts (no sample needed, just render). **Kling stays available additively:** mark a beat's `air`=kling
+ a `motion` and it upgrades, one beat at a time, only where the data (or a sagging retention curve) says.

---

## ENGINE FACTS (do not re-learn the hard way -- folds into PART II Section 9)

- **Render funcs anchor config on the OUTPUT PATH, not CWD.** Write into the channel's project tree and
  the grade + `style_suffix` + negatives attach automatically -- this is what makes the standalone
  renderers possible with zero engine changes.
- **The rulebook is two-layer, CWD-scoped.** Channel dir -> `<channel>/rulebook.json`; repo root ->
  universal `shared/rulebook.json` (bans on EVERY channel). Edit channel negatives from the channel dir.
- **`gate_canon` greps token TEXT for banned words** and can't read a negation -- never put a banned
  word (even "no galaxy") inside a canon token; ban it in the rulebook.
- **The engine won't import on the laptop** (no dotenv/venv). Anything importing `recreation_pipeline`
  runs on the box; laptop-side edits to engine-owned data (the rulebook) are pure-stdlib patches.
- **`probe20` does NOT call `gate_canon`; `grid`/`blocks` do.** A canon bug passes the probe and fails
  the grid -- run `grid` before the big spend.
- **`ken_burns_still` was hardcoded true-static** (a drift-bug workaround); the `move` param revives
  motion. `move=None` keeps the legacy static, so other channels are unaffected.

---

<!-- PART II -- THE CRAFT follows: the existing sections (Governing Law, Hierarchy, Block, Beat
     Table, 3A Authoring, Timing, Variants, Air, Motion, Spine, Pipeline, Checklist, Superseded,
     Future). They are the detailed law that hangs off the PROCESS above and are preserved intact.
     NOTE: the old Section 10 pathway (PHASE 0-12) is SUPERSEDED by THE PROCESS above -- delete it,
     or leave it flagged as superseded. Sections 3A (authoring), 4 (timing), 5 (variants), 6 (air),
     7 (motion), 8 (spine) remain the authority for their craft. -->
