# SESSION NOTES — Scripture On Screen craft + engine hardening
**Date:** 13 Jul 2026 · **Scope:** Scripture On Screen (primary), with cross-channel findings for Synthetic Press and Sacred Dawn · **Companion doc:** `_SCRIPT-CONTRACT.md` (updated this session)

---

## 0. TL;DR — what changed and what's proven

- **The character system is confirmed built AND proven on a real render.** Recurring reference-locked cast (Elijah / Elisha / the widow) hold faces and wardrobe across beats; a two-character shot held both; character-less beats render clean with no reference. Not a design — a working capability.
- **The golden-hour "slop" was a MODEL FORK, now closed.** Character beats and character-less beats were rendering on two different image models. Fixed: everything is now on the nano-banana-2 family.
- **The grade is resolved: the enemy is MURK, not saturation.** Lifted Scripture to a Bay-bright-biblical grade (chromatic + crisp + high-contrast + clean light), never soft/dark/painterly. Render-confirmed the lift.
- **Spectacle craft cracked: a miracle is a SEQUENCE of hero shots, not one composite frame.** The 6-shot Mount Carmel cold open turned "a barbecue" into "a scene." The fire-from-heaven gets its own hero beat.
- **Signature register defined: blockbuster scale + reverent smallness — "Bay's surface, Attenborough's soul."** Render the small human beneath the vast phenomenon; the camera worships the phenomenon, never glamorises the hero.
- **Competitive validation is enormous.** A direct incumbent (Unraveling the Scriptures, 576K) runs exactly this strategy to 2.8M-repeatable — proving the vein — and is beatable on consistency, cast continuity, and craft.
- **Doctrine housekeeping:** `_Synthetic2.md` (Synthetic Press = catastrophe/biblical reconstruction) is LIVE; `_Synthetic.md` (the AI-interior "Synthetic" pivot) is DEAD/superseded — archive it, the near-identical names are a hazard.

---

## 1. ENGINE — ground-truth facts (read the code, don't assume)

**The render pipeline entry for stills:** `python shared/recreation_pipeline.py stills --beats <file.json> --project <channel>/projects/<name> [--storyboard-only] [--force]`. `--storyboard-only` = zero-spend dry run (builds storyboard + prints per-beat ref routing). `--force` = re-render existing stills.

**Beats file format** (what `cmd_stills --beats` ingests): a dict `{"beats":[ {"narration","image_prompt","motion_prompt"}, ... ]}`. `{token}` tokens live in `image_prompt`. A beat with no `motion_prompt` renders as a still (Ken-Burns); the `[A]`-markup authoring format is translated into this.

**Character system (all built, confirmed by reading `recreation_pipeline.py`):**
- A `{token}` in a beat's `image_prompt` does TWO things automatically: (1) `_expand_canon` replaces it with the character's description inline; (2) the ref-scan attaches the character's reference image and routes that beat through the `fal-ai/nano-banana-2/edit` path with the channel's `reference_prompt_lock`.
- A beat with NO token renders text-to-image with `style_suffix`. This per-beat conditional (`generate_still`, ~line 642; `cmd_stills`, ~line 1434) is what makes mixed-cast films work.
- **Two hard requirements:** token is **lowercase, exact-match** to the key (`{elijah}` never `{Elijah}`); the description must live in channel **`base_canon`** (the key the engine reads — NOT a `canon` key).
- **Bug found + fixed this session:** Scripture had its descriptions under `canon` (engine-invisible) with `base_canon` empty → any `{token}` would crash "unknown tag." Fixed by moving `canon` → `base_canon`.

**The image-model fork (the root of the "golden slop"):**
- `IMAGE_ENDPOINTS` originally held `seedream`, `nano_banana` (orig, $0.039), `flux` ($0.04–0.05). Default `IMAGE_MODEL = "flux"`.
- Character beats route to `nano-banana-2/edit` (grounded, Gemini-family). Character-less beats fell to **flux** (a painterly styliser that renders "cinematic/golden-hour" prompts warm, soft, muddy). Two models = two looks = the fork.
- **Fix:** registered `"nano_banana_2": "fal-ai/nano-banana-2"` in `IMAGE_ENDPOINTS` via `patch_add_nb2_endpoint.py`, then set Scripture `channel.json` `"image_model": "nano_banana_2"`. Now the character-less path is the same family as the character path. (Occasional nano-banana-2 refusal falls back to flux automatically — watch the log for "falling back to flux"; a golden frame among grounded ones is a fallback, just restill it.)

**`reference_style_anchor` — read but NOT wired.** The engine reads a `reference_style_anchor` config key (`cmd_stills` ~line 1420) and only prints it — nothing attaches it. It's a half-built feature intended to attach a grounding *setting* plate to character-less beats via the /edit path. **Wiring it is the priority next engine task** — it fixes BOTH residual register-match AND setting-continuity (see §3, §4). Small patch: if a beat has no character refs and an anchor is set, use `[anchor]` as its reference image.

**Model costs (fal, current as of this session; "subject to change"):** nano-banana (orig) $0.039 · **nano-banana-2 $0.08** (both t2i and /edit; 2K/4K at 1.5×/2×) · nano-banana-pro $0.15 (4K $0.30) · flux-pro/v1.1 ~$0.04–0.05. Kling 2.5 Turbo Pro ~$0.07/s → a 5s clip ≈ $0.42 (Synthetic2 doctrine cites $0.07/s → ~$65 for a 185-beat film).

**Helper:** `probe.sh` was rewritten to be self-locating (`cd "$(dirname "$0")/.."`) and take `<channel> <project> [dry]` args, with a dry-run ref-routing table. **Not yet deployed to the box** (the box still has an older single-arg version — running the tool directly works fine meanwhile). It's in outputs; deploy laptop→git→box when convenient.

---

## 2. THE GRADE SAGA (murk vs saturation) — the most transferable craft lesson

**The problem:** character-less landscapes came out hot-amber-painterly ("Final Hours slop") while character beats looked grounded. **Diagnosed** (by reading the code) as the model fork above — flux vs nano-banana-2 — plus the reference *image* acting as a grade anchor on character beats.

**The over-correction:** first fix de-goldened Scripture's `style_suffix` to neutral. This killed the murk but also killed the *energy* — landscapes went flat and lifeless.

**The resolution (the key insight):** the enemy was never *saturation* — it was *murk* (soft, dark, painterly, muddy, washed-out). Michael Bay is heavily saturated and reads premium because it's **bright, crisp, high-contrast, HDR, clean.** Same saturation, opposite craft. So the fix is to **lift the other direction**, not revert: keep the grounded nano-banana-2 crispness, add back chroma/contrast/light-energy. And now that the model is nano-banana-2 (not flux), the chromatic words render *crisp* instead of *muddy* — they're safe again.

**Final Scripture `style_suffix` (banked):** "cinematic biblical blockbuster film still, photorealistic and grounded, richly saturated but clean colour — desert gold, deep lapis blue, crimson — bright vivid exposure, high contrast, high dynamic range with crisp detail held in the shadows, intense clean directional light, chromatic Bay-Woo trailer-grade energy, sharp crisp focus, high production value, period-accurate ancient Near East, expressive detailed faces, no soft painterly haze, no murk, no muddy shadows, no washed-out wash, no dull flat lighting, no text, no letters, no modern elements, 16:9". Render-confirmed: "definitely more colour, more vivid."

**Two authoring rules banked from this (now in the contract §4/§6):**
- Specify light **BRIGHT** — the model defaults dark/murky when light is unspecified (from Synthetic2 §5c).
- Negations grow **from evidence, never speculation** — add "no murk" etc. only for a failure you've actually seen; speculative negation vetoes the model's best output (from Synthetic2 §5c).

**Cross-channel:** this grade logic applies to all three movie channels. Sacred Dawn (cosmic/apocryphal) and Synthetic (catastrophe) each get their OWN grade (Sacred Dawn: distinct apocryphal register; Synthetic: teal-orange Bay/Woo), but the same law holds — bright/chromatic/crisp, murk is the enemy, match the plain-render `style_suffix` to the character/reference render so both paths agree.

---

## 3. SEQUENCING — spectacle is a sequence of hero shots

**The failure:** trying to carry the whole Carmel climax (fire + altar + Elijah + 450 prophets) in ONE still. The fire always shrank to a campfire on the altar ("a barbecue").

**The fix (render-proven):** stage the miracle across ~6 beats, each a distinct hero frame — and give the **phenomenon its own beat with nothing else in it.** The winning 6-shot Carmel cold open:
1. Black storm clouds gathering, an unnatural hole opening — dread, no fire yet.
2. **The money shot:** a vortex of fire tearing down through the hole in the black cloud — no altar, no man, only the phenomenon. (This is the frame the 2.8M incumbent built their video around.)
3. The strike — the column slams the altar, blast/shockwave, too fierce to approach.
4. Elijah, alone, unflinching, lit hard (the locked face).
5. The prophets thrown down in terror.
6. Aftermath — scorched altar, smoke, silence.

**Why it works:** it's the fast-cutting rule (one continuous narration sliced into beats) applied to the peak, and it gives the animation budget more hero beats to sit on. The incumbent renders the fireball as one composite; sequencing is a craft edge they skip.

**Also learned:** daylight + "too hot for even Elijah to approach" (he leans away, shields his face, robes blown by the heat) is what makes fire read as *divine* rather than a bonfire — the human reaction to the fire sells its power.

---

## 4. CONTINUITY — the master principle, and the two locks

**Master principle (from Synthetic2 §5c "period anchor, always"):** *the image model has ZERO memory between prompts — each prompt is its entire universe — so every continuity element must be re-stated in every single beat, and repetition is free.* This is the parent of both locks below.

**Lock 1 — Character (built + proven):** `{token}` + `base_canon` description + `reference_map` image. Locks faces/wardrobe across beats. Works.

**Lock 2 — Setting (NEW this session, contract §4A):** write the place once as a verbatim locked phrase with explicit negatives ("the bare rocky summit of Mount Carmel — pale weathered stone… no buildings, no city, no structures"), paste it word-for-word into EVERY beat of the scene. **Render-learned caveat:** the verbatim phrase pulls beats much closer to one place but does NOT fully eliminate drift (a canyon still crept into one shot). So it's a strong reduction, not a cure — the real fix is the `reference_style_anchor` plate (see §1). New setting = new locked phrase.

**Also from Synthetic2 §5, not yet fully imported (pending the §5 audit):** faces rules (anonymous faces required; famous figures silhouetted to hold identity; no gore ever; youth-adjacent nouns trip the content filter → render the object not the minor); geometry stated never implied; props carry their motion source; the "exemplar law" (copy the shape, never author from memory).

---

## 5. COMPETITIVE INTELLIGENCE — Unraveling the Scriptures

**Channel:** @UnravelingtheScriptures · 576K subs · 542 videos · 62M lifetime views · Brazil · started as "fun facts of mythology," rebranded biblical. Channel avg ~115K/video; the *features* are 2–24× that (power-law: a dozen feature films carry the channel).

**The winning format (copyable):** `[FIGURE/BOOK] – The Movie (2026): [dramatic subtitle] | Complete Full Biblical Film 4K`, 60–82 min (Genesis 2h). Four stacked title levers: pre-loaded **known name** + **"The Movie (2026)"** (positions AI output as a film + freshness) + **"The Film that Shocked the World"** (curiosity/controversy) + **"Complete Full … 4K"** (completeness promise, one sitting).

**Their outlier slate:** Elijah 2.8M · Enoch 2.5M · World After Death of Jesus 1.6M · Nephilim 1.5M · Daniel 1.5M · Revelation 1M · Sodom & Gomorrah 692K · Genesis 653K · Elisha 360K · Moses 260K · Job 200K · Samson 175K. (Note: Elijah 2.8M vs Moses 260K from the same machine — "mystery + dread + magnitude beat fame," per Synthetic2 §13.)

**Where they're beatable (three real gaps):** (1) **look consistency** — their fire vortex is great but their altar-strike frames are AI-slop (oversaturated golden mushroom-clouds — the exact murk we engineered out); (2) **no recurring locked cast** — they regenerate faces per film; we have reference-locked continuity they structurally lack; (3) **spray-and-pray** — 542 videos, unfocused. A focused channel doing fewer/better biblical features with a consistent grounded-bright look and a recurring cast is a differentiated position.

**Topic overlap:** heavy — they've done Elijah, Elisha, Nephilim, Enoch, Revelation, Genesis, Daniel (overlaps both Scripture and Sacred Dawn). This is validation, not a wall: the biblical AI-movie lane is a **rising-format wave with multi-winner tolerance** (two Elijahs both >2.7M; two Enochs; two Revelations — the graph feeds the FORMAT, not one winner). Entrant wins on tier-above craft + cadence, not incumbent weakness. Open ground still large: Ezekiel, Exodus-plagues-as-film, David, Joseph, Jonah, Isaiah's apocalypse, the Watchers-war angle specifically.

---

## 6. ECONOMICS & STRATEGY — the flywheel

**Cost comparison (their Elijah vs ours):**
- **Theirs (67 min, 100% animated + lip-sync):** ~700–1,000 clips × video rates, plus a lip-sync pass. Defensible range **~$400 lean / $1,000–$1,500 realistic / higher on premium video models.**
- **Ours (40-Kling feature + rest KB stills):** 40 Kling × $0.42 ≈ $17 + ~700 stills × $0.08 (nano-banana-2) ≈ $56 + voice/music/assembly (tens) → **~$75–90 all-in.**
- Ratio: **~1/10th to 1/20th of their cost.** The whole delta is animation coverage + lip-sync — the two things we're either climbing toward on a dial or deliberately declining.

**The flywheel thesis:** their model only works because millions of views pay back a four-figure render — expensive bets that must hit. Ours prints for under $100, so **break-even is a rounding error**: ship, read the 48h signal (CTR + AVD; Browse/Suggested% off zero = graph opening), reinvest only where retention proves the gap. Peter's frame: *"1/10th the cost, happy with 1/100th their views."* Don't need to beat any single film — out-consistency and out-volume them at a cost where being wrong is free.

**The two things they beat us on, and the ruling:**
- **Lip-sync — DECLINE (it's a trap, and doctrine already bans it).** Most expensive, most fragile, most uncanny thing in AI video; narrated-documentary (voiceover over cinematic scenes) sidesteps it entirely and is *cleaner*. It's a liability they took on, not an edge.
- **100% animation — REAL gap, close it on the dial.** Not by matching day-one; by animating **where it earns its place** (the galloping horse, never the wheat field). 40 well-chosen Kling among strong stills, cut fast, can read more cinematic than everything-animated mush. Climb 40 → 80 → 200 → full as revenue justifies.

**Monetization structural note (Synthetic2 §5a):** earn at least **8:01 runtime** for the mid-roll threshold — permanent ad inventory on every future view for ~$10–13 marginal.

---

## 7. THE DISTINCTIVE REGISTER — "Bay's surface, Attenborough's soul"

The differentiation nobody in the lane hits: **marry Michael Bay's surface (grade, scale, production-value energy, orange-teal/desert-gold blockbuster snap) to Attenborough/Planet Earth's soul (patience, stillness, the small living thing against a vast indifferent force).**

- **Signature composition (now contract §6, all 3 movie channels): scale needs a human face at the bottom of the frame.** The vast event fills the frame above/behind; one weathered face or lone silhouette is dwarfed beneath it. The awe lives in the size difference.
- **The inversion that keeps it reverent:** Bay's *grade*, yes — Bay's *hero treatment*, NO. Elijah is weathered, grave, dwarfed, NOT in control of the fire — the witness to a power vastly larger than him. Bay's camera worships the hero; ours worships the phenomenon and shows the human humbled before it. **Blockbuster scale, reverent smallness.**
- **Consistency is the premium signal.** Planet Earth's majesty IS its consistency — nothing ever looks cheap. Grounded one-register look + locked recurring cast is the single thing that reads "Hollywood/Attenborough" where the incumbent reads "very good AI."
- **Reverence through patience** (stillness before the miracle, silence, score swelling) is nearly free — a pacing + music choice.
- **The score carries the majesty** (Childlike Media's "Bible in 90s" is majestic largely *because of* Zimmer-scale orchestral). The channel `default_music_prompt` is a big, cheap majesty lever — tune it toward swelling Planet-Earth-grade orchestral.

---

## 8. DOCTRINE RECONCILIATION

- **`_Synthetic2.md` (Synthetic Press — catastrophe/biblical reconstruction, v1.2, 4 Jul, LIVE) is the operative doctrine.** `_Synthetic.md` (the "Synthetic" AI-interior pivot, v2, 20 Jun) is **DEAD/superseded** — archive or rename it; both claim folder `synthetic/` and the near-identical names are an operational hazard (loading the dead one = authoring against an abandoned direction).
- **Two §13 divergences resolved in favour of this session's proven work** (per the additive/forward-only reconciliation law now in the contract):
  1. §13 says "reference-lock **Elijah only**," secondaries by costume tags + shadowed faces. We reference-locked **three** (Elijah/Elisha/widow) and the render proved all three hold. **Keep the three-lock** — supersedes the doctrine's older caution. (§13 should be updated to match.)
  2. §13 specifies a "desert-gold/deep-lapis" grade; we resolved the grade to Bay-bright-biblical (grounded + chromatic + crisp). **Not in conflict** — that IS desert-gold/lapis, done crisp not murky. Keep our resolution.
- **Word ceiling:** Synthetic2 §5b uses 11-word ceiling / 5–10 target (for its 2–4s all-animated cuts); our movie contract keeps **~15 words / ≤5s** for a Kling beat (Peter confirmed). Both consistent given different clip lengths.
- **STILL PENDING (Peter's explicit request, deferred by the grade work): the full enumerate-and-veto audit of Synthetic2 §5 (script authoring doctrine) and §13 against `_SCRIPT-CONTRACT.md`** — rule by rule, place-verbatim or flag-the-drop. Several §5 craft rules (faces/gore/youth-filter, geometry-stated, props-carry-motion, exemplar-law, the number-weight split formula) are not yet imported. Do this as its own pass; do NOT silently half-merge.

---

## 9. PROCESS & DISCIPLINE LESSONS (the meta-layer)

- **Read the source, don't reconstruct from memory.** Three failures this session shared one root — the golden fork, the character system "already built," the setting rule — all had the truth sitting in the code or a doc, and the error was answering from memory-of-having-read-it. The engine work (where the code was read line by line) had none of these gaps. **Applies to docs as much as code.**
- **Doctrine transfer = checklist, not summary.** When folding a doctrine into the contract, enumerate every source rule and either place it verbatim or explicitly flag "dropping, here's why" for veto. Summarizing silently drops rules. (This method, applied to the two 40-Beats playbooks, showed the transfer was actually ~faithful and pinned the exact gaps.)
- **Files reused for different content.** `_Synthetic.md`/`_Synthetic2.md` held the 40-Beats playbooks one turn and the channel doctrines the next — same filenames. Always read fresh.
- **Machine discipline (laptop→git→box).** Recurring friction: config/code edits must originate on the LAPTOP (`~/Projects/Pipeline`), flow through git, then `git pull` on the BOX (`~/Pipeline`, prompt `peter@pipeline-prod`). The prompt tells you which machine you're on; when a `cd ~/Projects/Pipeline` errors, you're on the box — STOP, don't let the rest of the block run. (Happened this session; the grade edit landed on the box and had to be pushed up from there.)
- **Timestamped scp folders** (`~/Downloads/carmel-$(date +%Y%m%d-%H%M%S)/`) so render batches don't overwrite each other for A/B comparison.

---

## 10. BOX HYGIENE — flagged, not yet done

- **Five uncommitted engine files live only on the box, unversioned:** `shared/elevenlabs_tts.py`, `shared/mission_control/ingest.py`, `shared/modea_beats.py`, `shared/modea_leg.py`, `shared/orchestrate.py`, plus modified `sacred-dawn/channel.json`. Real work, one `git checkout` from gone. **Commit these (from the laptop side ideally) before more box work.**
- **`.gitignore` is leaky** — `clips/`, `modea/`, `thumb_candidates/`, `stills/` show as untracked, making `git status` a wall of noise. Add them to `.gitignore` so status is readable.

---

## 11. NEXT STEPS / BUILD QUEUE

**Scripture (immediate):**
1. Judge the lifted-grade Carmel six (done — confirmed vivid). Optionally run the full `finish` on the six to see the first ~30s Elijah cold open WITH motion + voice + music.
2. **Wire `reference_style_anchor`** — the priority engine task; fixes setting-continuity AND residual register-match.
3. Author the full Elijah cold open, then the full 40-Kling feature. Adopt the "[X] – The Movie (2026): … | Complete Full Biblical Film 4K" title formula.

**Cross-channel (Synthetic Press + Sacred Dawn):**
4. Apply the grade law (murk is the enemy; bright/chromatic/crisp; match style_suffix to reference render) to each — Synthetic keeps teal-orange Bay/Woo; Sacred Dawn gets its apocryphal grade.
5. Apply the signature "human face at the bottom of the frame" + sequencing rules — they're cross-channel (already in the contract).
6. Sacred Dawn is anonymous-cinematic (no character tokens) — the character system is off; setting-lock and grade still apply.
7. Confirm each channel's `image_model` (should be a nano-banana-2-family, not flux, to avoid the fork).

**Doctrine/contract:**
8. The full Synthetic2 §5/§13 enumerate-and-veto audit (deferred this session).
9. Update `_Synthetic2.md` §13 to match the three-character-lock and resolved grade.
10. Archive/rename dead `_Synthetic.md`.

**Ops:**
11. Deploy the rewritten `probe.sh` (laptop→git→box).
12. Commit the five box-only engine files; fix `.gitignore`.
13. The batch-of-batches runbook (`_BATCH-RUNBOOK.md`) — still needs `run_all_batches.py` / `run_batch.py` / current `batch_plan.json` to write correctly.

---

## 12. KEY STATE (quick reference)

- **Box:** `ssh -p 443 peter@116.202.18.68`, repo `~/Pipeline`, venv `source ~/venvs/pipeline/bin/activate`, prompt `pipeline-prod`.
- **Laptop:** `~/Projects/Pipeline`.
- **Scripture cast (base_canon + reference_map, refs in `scripture-on-screen/refs/`):** elijah, elisha, widow — all lowercase keys.
- **Scripture image_model:** `nano_banana_2` (character-less path); character path uses `nano-banana-2/edit` via reference lock.
- **Render command:** `python shared/recreation_pipeline.py stills --beats <beats.json> --project <path> [--force]`.
- **Active movie channels:** Scripture On Screen (character, live), Sacred Dawn (anonymous-cinematic), Synthetic Press (catastrophe reconstruction). Keep-maintain/park/kill list per the consolidation plan.
