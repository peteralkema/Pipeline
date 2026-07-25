# SESSION NOTES — CREW CHANNEL BUILD (working name: crew-wip)
*Faceless YouTube Media Flywheel — new channel #12. Bright, fast-cut, character-driven explainer.
The anti-Final-Hours channel. Pick-up reference: read this first, then `_Crew.md` (doctrine) and
`crew_character_bible.md` (the durable IP).*

*Session date: 29 June 2026. Status: DESIGN COMPLETE, not yet rendered. Next action: lock script →
build runnable config → render pilot → ship → read 48h data.*

---

## 0. ONE-PARAGRAPH SUMMARY

A new channel: a recurring crew investigates "the unfilmable" across all time and space (past,
future, unreachable places). Bright produced flat-cel illustration (NOT photoreal, NOT Final Hours).
Fast-cut Ink/Mack rhythm (1-3s per image). Young-adult, not-made-for-kids, not age-restricted. The
pilot is DRIVER-ONLY (one character; crew added later once single-character consistency is proven).
Flagship pilot script: "200,000 Years Without Soap." Voice locked: Evan @1.05. Leanest config in the
portfolio: static stills, no animation, no music, all Mode A. Everything designed to ride an upgrade
ladder (stills → animation → music → lip-sync → "the movie") on the same pipeline + same crew.

---

## 1. THE STRATEGIC ARC (how we got here, so we don't re-litigate)

- Started from Peter's fatigue with the dark/painterly Final Hours register (real wellbeing + business
  signal to go bright). Validated a BRIGHT curiosity-explainer lane via NexLev.
- Confirmed live winners in the space: Ink Explainer, Mack, First Humans — "when/why did humans first
  X" curiosity-explainers, heating fast. The flat-stick-figure Ink channel does 6-figure views =
  proof that VALUE is in script/hook/packaging, NOT render fidelity.
- **Crew-format white space CONFIRMED OPEN (checked twice via NexLev):** every adjacent channel is
  single-narrator or single-character (Theoretico's animated skeleton = 62M views proves recurring
  animated character works; nobody has a recurring CREW). "@CuriousCrew" exists but is a dead 55-sub
  kid-coded Shorts channel — not a competitor, validates avoiding "Curious" + kid-coding.
- Scope widened beyond human-origins to "the unfilmable across all time/space" (anti-flood insurance:
  the crew/register is constant, topic is the infinite variable). Launch focused, then widen.

---

## 2. LOCKED DECISIONS (do not re-open without reason)

**Concept & positioning:**
- Recurring crew investigates the unfilmable across all time/space.
- Young-adult coded. NOT Made-For-Kids (revenue death). NOT age-restricted (reach death). The
  general-audience middle.
- Fast-cut explainer format. Solo-address-to-viewer is the narration spine; crew are reaction
  punctuation, NOT conversation (protects the second-person retention engine). Full ensemble reserved
  for tentpoles.
- Core of THREE (Brain / Skeptic / Driver). Everyone else = per-episode guests, never core members.
  (Kids' pull toward 4-person frames was diagnosed as a STYLE preference, not a crew-count preference
  — held at 3.)

**Style (kid-validated, 4 independent signals):**
- PRODUCED FLAT CEL-SHADED ILLUSTRATION. Clean dark linework, simplified flat color planes, appealing
  stylized faces, rich illustrated backgrounds, warm lighting.
- EXPLICITLY NOT photorealistic, NOT 3D, NOT realistic-skin. (Photoreal drift = the failure mode; it
  reads "Final Hours" and is rejected.)
- Backgrounds are a FIRST-CLASS element (half the appeal — kids confirmed; rich/warm beats bare).

**Cast (the #5 trio, kid-validated):**
- DRIVER = the guy. Brown tousled hair, denim jacket, grey tee, tan backpack (signature). HAS GLASSES
  (see §3 below — we stopped fighting the model). Energy/launch role. THE PILOT IS DRIVER-ONLY.
- BRAIN = sciency-stylish young woman, dark hair in a messy bun, glasses (her tell), nerdy-focused.
  Locked by Peter's daughter's character-brief. Future video.
- SKEPTIC = blonde, centre, composed/arms-crossed, dry "prove it" (audience stand-in). Future video.

**Voice:** Evan / inworld-tts-2 / speaking_rate 1.05. Chosen for the DRY-HUMOUR SMIRK quality (the
deadpan "Probably" landing) — the channel's defining vocal trait. (Auditioned Derek, Dennis, Evan;
Evan won on the smirk, which is the must-have.)

**Production config (the leanest lane in the portfolio):**
- Stills: Flux-pro/v1.1, flat-cel style via channel.json style_suffix.
- Animation: NONE. Static holds per beat (`_still_to_held_clip`), no Kling, no Ken-Burns. (Ken-Burns
  pan/zoom is invisible/janky at a 1-3s cut rate — pure static cut fast is correct and cheapest.)
- Audio: Inworld Evan @1.05.
- Mode: all Mode A. No Mode B (yet). No music (yet).
- Cost: lowest possible — stills are the only real spend.

**Naming:** DEFERRED. The pilot will name itself. Working slug "crew-wip" / name "crew_wip". Principle:
NAME it don't describe it (Mack is just Mack); avoid "Curious" (over-crowded token). Survivors banked
for the out-loud kid-test: Last Seen, The Last Time, Quest, Trove, Kove, Vyse, Fathom. (Lists of 300+
candidates generated across 5 lists if needed — but name AFTER the pilot.)

---

## 3. THE GLASSES SAGA (resolved — don't re-fight)

Flux-pro/v1.1 puts glasses on the Driver relentlessly (the "clever young man" archetype summons
them). Confirmed across ~4 probe rounds that the model IGNORES negative prompts AND ignores "NO
glasses" in the positive (diffusion negation failure — naming "glasses" at all can summon them).
**DECISION: the Driver HAS glasses.** Stop paying the tax of fighting the model every frame. The Brain
gets a different signature when she arrives (glasses become one tell among several, or she gets a
distinctive hair/beanie/tool). This is locked; do not re-open.

Banked lesson: on flux-pro/v1.1, negatives are weak-to-useless; the POSITIVE prompt is the only
reliable lever; and you cannot reliably remove a strongly-associated feature — design WITH the model's
defaults, not against them.

---

## 4. STYLE-PROBE FINDINGS (banked engineering)

- Model: `fal-ai/flux-pro/v1.1` (hardcoded `_FLUX_MODEL` in the pipeline; does illustration AND
  photoreal — style is driven by the prompt/suffix, NOT the model). No different model needed.
- Safety: use `safety_tolerance:"5"` (NOT `enable_safety_checker:False`). This is what the real
  pipeline uses to stop flux's silent ~7KB black-frame rejects. (The old trio probe used the wrong
  method.)
- Style oscillation: the FIRST probe suffix ("produced semi-realistic" + "cinematic") oscillated
  between flat-illustrated (good) and photoreal (bad, reads Final Hours). FIX: push the suffix
  DECISIVELY to flat-cel, and the photoreal drift carries the AI-realism artifacts (warped backpack
  straps, stubble) WITH it — fixing the style fixes the artifacts for free (flat style is forgiving).
- Cast vocabulary: describe as "young adult" NEVER "teen" (the word "teen" + bodies trips the safety
  classifier → blank frame). Banked from earlier sessions, still holds.
- Reference frames Peter approved for the flat-cel target: the 3 "flat/animated, not trying to be
  real" frames (cave, Egyptian tomb, blue-bg portrait) and the earlier denim-jacket Driver. Uploaded
  this session.

---

## 5. THE FINAL-HOURS-BIAS INSIGHT (meta-lesson — see NOTE_final_hours_bias_in_canonical.md)

Final Hours was built first, so its craft infected the "channel-agnostic" canonical docs. The
MECHANICS are universal; the CRAFT in `ante-machinam.md` Part IV is really the Final-Hours/Sacred-Dawn
brief. This channel deliberately BREAKS: beat-granularity (§6 slow beats → we go fast), animatable-
foreground (§7 → we don't animate), faceless-default (Part III → we have a visible character),
slow-dread register (Part IV → we're bright/wry), photoreal style, and Ken-Burns floor. Full catalogue
in the separate NOTE file. Meta-principle: BUILD ORDER ENCODES BIAS; each genuinely-different channel
needs its own "here's what we break" brief.

---

## 6. KEY PIPELINE FACTS LEARNED THIS SESSION (from reading the real code + canonical doc)

- **Authoring format is a `script.md`, NOT hand-built JSON.** Header (bare key:value, NO `---` fences)
  + `## SECTION` + `[A] narration` on one line + `VISUAL: ...` on the next + blank line between beats.
  `parse_script.py` turns the .md into beats_full.json. COPY a working script's markup, never author
  from prose (banked: wrong markup → 0 beats → ZeroDivisionError).
- **Verify zero-spend before any render:** `python parse_script.py <md> --json /tmp/b.json
  --json-full /tmp/f.json` — prints beat count; a number = good, crash/zero = bad format.
- **channel.json keys (exact):** name / voice_id (snake_case! `voiceId` → silent Victor fallback) /
  style_suffix / default_motion / default_music_prompt / base_canon / upload / thumbnail / music /
  speaking_rate (optional float 0.5-1.5, default 1.0).
- **base_canon auto-merges into every beat's canon** (confirmed by code comment) → this is where the
  Driver character-lock goes (channel-level determinism / drift-killer).
- **people_directive (positive prompt) is the real consistency lever; negatives are weak on flux-pro.**
  Confirmed by the glasses fight AND the canonical doc ("quality through the POSITIVE prompt").
- **Channel creation pattern:** an idempotent `patch_*.py` (modeled on
  `patch_scripture_on_screen_channel.py`) that schema-checks our keys as a SUBSET of a reference
  channel's keys, then writes `<slug>/channel.json`. Discipline: laptop → commit → push → box pull →
  re-run to verify idempotency. Does NOT create the project folder (done via Mission Control).
- **Rulebook:** each channel has a `rulebook.json` with `negative` (list) + `people_directive` +
  `motion_rules`. `load_rulebook_negatives()` reads it. STILL NEED TO READ
  `~/Pipeline/rulebook.json` (the shared default) to build ours correctly — this is the one
  outstanding file read.
- **Static-hold capability EXISTS:** `_still_to_held_clip` ("turn a still PNG into a static video
  clip via ffmpeg, no AI motion") — currently a Kling-refusal fallback; for this channel it becomes
  the DEFAULT. Need to confirm how to set it as default (likely `kling_count:0` + a no-zoompan flag,
  or a tiny patch). STILL NEED:
  `grep -rn "_still_to_held_clip\|kling_count\|zoompan" ~/Pipeline --include=*.py`
- **New-channel gotchas:** (a) YouTube account must be phone-verified before uploads >15min (soap is
  ~6min, fine); (b) slug rule `^[a-z0-9][a-z0-9-]{0,60}$` — hyphens not underscores; (c) channel
  header must match folder name (hyphen/underscore auto-resolves, true alias does not).
- **Inworld:** code says `INWORLD_MODEL = "inworld-tts-2"`. speaking_rate → speakingRate in audioConfig,
  read from channel.json.

---

## 7. THE PILOT SCRIPT (LOCKED PENDING PETER'S FINAL READ)

`soap_script_fast.md` — "200,000 Years Without Soap." 57 fast beats (4-10 words each, ~1-3s).
Driver-only, all Mode A, numbers spelled out, no in-still text. Cold open → first soap (Babylon) →
Romans → medieval-got-worse → Semmelweis (the mocked-then-vindicated doctor, the gripping spine) →
close (the soap on your sink is one of the newest things about being human). The fast-cut rhythm is
authored IN the beat length (script is king). THIS IS THE NEXT THING TO LOCK before building config.

Earlier slow version (`soap_script.md`) is SUPERSEDED — it reverted to Final Hours slow-beat pacing;
rejected. The fast version is the channel.

---

## 8. FILE INVENTORY (all delivered this session, in /mnt/user-data/outputs/)

| File | What it is | Status |
|---|---|---|
| `soap_script_fast.md` | THE pilot script, fast-cut, real .md format | Lock pending final read |
| `soap_script.md` | Slow version | SUPERSEDED — ignore |
| `patch_crew_channel.py` | Channel-creation patch (needs updating: add speaking_rate 1.05, default_motion, base_canon Driver-lock, confirm category_id) | Draft, not yet run |
| `channel.json` | Standalone draft (superseded by the patch approach) | Reference only |
| `flux_driver_probe_v2.py` | Production-accurate style/consistency probe | Ran; findings banked |
| `THREE_MVP_SCRIPTS.md` | Original 3 MVP scripts (soap/phones/crying) | Reference |
| `SOAP_SHOTLIST_v1.md` | The frame-typed shot-list (frame-types map to Mode A/B; superseded by the .md) | Reference |
| `NOTE_final_hours_bias_in_canonical.md` | The bias catalogue | Keep |
| `_Crew.md` | Channel doctrine doc (this session) | First version |
| `crew_character_bible.md` | The durable IP — the crew defined tool-agnostically | First version |
| `SESSION_NOTES_crew.md` | This file | — |

---

## 9. OPEN ITEMS / NEXT ACTIONS (priority order)

1. **PETER: final read + LOCK the script** (`soap_script_fast.md`). Script is king — lock before any
   render. Read it out loud at pace; confirm the cut rate works and the Semmelweis arc holds when
   chopped fast.
2. **Read 2 outstanding files** (the only things blocking a complete runnable config):
   - `cat ~/Pipeline/rulebook.json` (shared default — to build the crew rulebook)
   - `grep -rn "_still_to_held_clip\|kling_count\|zoompan" ~/Pipeline --include=*.py` (to set the
     no-motion default)
3. **Finalise `patch_crew_channel.py`**: add `speaking_rate:1.05`, `default_motion`, the Driver-lock
   in `base_canon`, pick `category_id` (27 Education vs 24 Entertainment — Peter's call), schema-check
   against a non-Final-Hours reference channel.
4. **Build `crew-wip/rulebook.json`** (from the shared template): Driver in people_directive (glasses
   OK), flat-cel + anti-realism terms in negative.
5. **Run the channel patch** (laptop → commit → push → box pull → verify).
6. **Parse-verify the script** zero-spend.
7. **Render the COLD OPEN first (~11 beats)** as a cheap in-pipeline test before the full 57 — confirms
   the channel config + flat-cel style + Driver consistency + Evan sync all work TOGETHER in the real
   pipeline (the probes were standalone). If good → full render.
8. **Watch the pilot.** Then SHIP it (publish, set the AI-disclosure flag manually, schedule). Shipping
   is what turns this build into a real BET that generates 48h signal.
9. **Read first-48h data** → decide if this is a dial to CRANK (animation/music/crew/movie) or a lane
   to PARK. Diversify-then-crank: you don't need THIS channel to win, you need enough at-bats that
   SOMETHING wins.

---

## 10. STRATEGIC PRINCIPLES BANKED THIS SESSION (durable, cross-channel)

- **Diversify the bets, concentrate the craft, crank the winners.** A build only becomes a BET when it
  SHIPS and generates signal. An unshipped channel is a horse in the stable, not the race. The cure for
  "did I waste this build" is to ship and get data — not to build more.
- **Build order encodes bias** (the Final Hours infection). Each different channel needs its own
  break-list.
- **The durable asset is the CHARACTER BIBLE, not the renders.** Renders are thrown away and
  regenerated up the ladder; the tool-agnostic crew definition carries from stills → animation →
  lip-sync → movie. Future-proofing effort goes into the bible, not into over-building the pilot.
- **Design lean now on infrastructure that already scales.** The animation/music/Mode-B/movie
  capabilities ALREADY EXIST in the channel-agnostic pipeline — this channel runs lean by config and
  turns them on later by flipping flags. Future-proofing is inherited from the architecture, not built.
- **Kids = de-biased focus group.** Weight raters by least-confounded variable (daughter on female
  chars — sons bias to attractiveness; sons on male chars). Judge CHARACTER not looks ("who'd you
  watch"). Isolate ONE variable per test (the crew-vs-background confound; specify "ignore the
  background").
- **Specificity kills render-drift; vagueness summons it.** (The under-specified 3rd character drifted;
  the tightly-specified Driver held.)
- **Name it, don't describe it; defer the name until the pilot names itself.**
- **flux-pro negatives are weak — design WITH the model's defaults (glasses), not against them.**
- **Script is king** — the pacing lives in beat length; lock the script before anything binds to it.
