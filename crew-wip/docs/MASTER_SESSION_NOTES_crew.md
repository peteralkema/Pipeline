# ════════════════════════════════════════════════════════════════════════
# MASTER SESSION NOTES — NEW CREW CHANNEL (working name: crew-wip)
# Faceless YouTube Media Flywheel · Channel #12 · 29 June 2026
# ════════════════════════════════════════════════════════════════════════
#
# THE definitive pickup document. Supersedes the earlier SESSION_NOTES_crew.md
# (which is now partial — this one includes the thumbnail breakthrough and the
# full decision history). Read THIS first next session, then _Crew.md (doctrine)
# and crew_character_bible.md (the durable IP).
#
# STATUS: Design + creative direction COMPLETE. Thumbnail formula CRACKED.
# Not yet shipped. A full soap render was kicking off on the box at session end
# (orchestrate.py was running — see §12). Next: confirm that render, lock the
# thumbnail style question, ship, read 48h data.
# ════════════════════════════════════════════════════════════════════════


## ▌1. THE ONE-SCREEN SUMMARY

A new channel: a recurring **crew** investigates **the unfilmable** across all
time and space (deep past, far future, unreachable places). Register: **bright,
fast-cut, wry, polished-but-not-weird** — deliberately the ANTI-Final-Hours
channel. Pilot is **DRIVER-ONLY** (one character; crew added once single-char
consistency is proven). Flagship: **"200,000 Years Without Soap."**

Locked: concept, positioning, cast design, **flat-cel illustration style**,
**Evan voice @1.05**, **fast-cut script** (57 short beats), **leanest config in
the portfolio** (static stills, no animation, no music, all Mode A), and — the
late breakthrough — a **proven thumbnail formula** (flat saturated colour + 9/10
recoil expression + bold two-tier headline).

Deferred deliberately: the channel NAME (the pilot will name itself), the crew
(Brain + Skeptic come in video 2+), Mode B graphics / frame-type variety (video
2+), animation/music/movie (later rungs of the upgrade ladder).

The strategic spine: **diversify cheap at-bats, ship to get signal, crank the
winners.** This build only becomes a real BET when it ships. Don't keep
polishing — ship it and read the data.


## ▌2. WHY THIS CHANNEL EXISTS (the strategic case, so we never re-litigate)

- Peter was fatigued/depressed by the dark painterly Final Hours register — a
  real wellbeing signal AND a business signal to build something bright.
- NexLev validated a live, heating-fast BRIGHT curiosity-explainer lane: Ink
  Explainer (16.4k subs / 9 videos), Mack, First Humans. The "when/why did humans
  first X" format.
- **Ink's flat STICK FIGURES do 700k+ views** (alcohol 3.9x, clothes 1.7x). PROOF
  the value is in SCRIPT + HOOK + PACKAGING, not render fidelity. (This becomes
  the central tension — see §9 the thumbnail story.)
- **Crew-format white space CONFIRMED OPEN (NexLev, checked twice):** every
  adjacent channel is single-narrator or single-CHARACTER. Theoretico's animated
  skeleton = 62M views proves a recurring animated character crushes; NOBODY runs
  a recurring CREW. "@CuriousCrew" exists but is a dead 55-sub kid-coded Shorts
  channel — not a competitor, and a cautionary tale (kid-coded "crew" name = death).
- Scope deliberately widened to "the unfilmable across all time/space" — anti-flood
  insurance. The crew/register is the constant; topic is the infinite variable.


## ▌3. LOCKED DECISIONS (do not re-open without a reason)

### Concept & positioning
- Recurring crew investigates the unfilmable across all time/space.
- Young-adult coded. NOT Made-For-Kids (revenue death). NOT age-restricted (reach
  death). General-audience middle; edgy-but-not-graphic; cartoon style lets dark
  topics stay safe.
- Fast-cut explainer. **Solo-address-to-viewer is the narration spine; crew are
  REACTION cutaways, never conversation** (protects the 2nd-person retention
  engine). Full ensemble = tentpoles only.
- **Core of THREE** (Brain / Skeptic / Driver). Everyone else = per-episode guests.
  (Kids' pull toward 4-person frames diagnosed as a STYLE preference, not a
  crew-count preference — held at 3.)

### Register (THE identity call, made consciously at session end)
- **Polished, NOT weird.** Peter's explicit decision: "I won't spend the next 2
  years being weird just because that's what works." Ink wins on crude-weird;
  Peter chooses a sustainable polished lane. The risk named honestly: "polished"
  can drift into "tasteful = invisible." The discipline: polished AND high-energy,
  never polished-and-restrained.
- The EDGE that's compatible with polished (the answer to "how do I not fade into
  the background without being weird"): **maximal facial expression + the recurring
  character's face as the brand + bold gap-text + high-contrast pop.** None require
  weird; the recurring-face moat COMPOUNDS in a way Ink's random scribbles cannot.

### Style (kid-validated — 4 independent signals across the session)
- **PRODUCED FLAT CEL-SHADED ILLUSTRATION.** Clean dark linework, simplified flat
  color planes, appealing stylized faces, rich illustrated backgrounds, warm light.
- **NOT photorealistic, NOT 3D, NOT realistic-skin.** Photoreal drift = the failure
  mode (reads "Final Hours," invites AI-realism artifacts). Suffix must steer
  DECISIVELY flat-cel.
- Backgrounds are first-class IN THE VIDEO (rich/warm beats bare). BUT NOTE the
  thumbnail reversal in §9 — flat bold colour for THUMBNAILS, rich scenes for FRAMES.

### Cast (the "#5 trio," kid-validated)
- **DRIVER** = the guy. Brown tousled hair, denim jacket, grey tee, tan backpack
  (signature), HAS GLASSES (we stopped fighting the model — see §6). Energy/launch
  role. PILOT IS DRIVER-ONLY.
- **BRAIN** = sciency-stylish woman, dark messy bun, glasses (her tell), nerdy-
  focused. Locked by Peter's DAUGHTER's character-brief. Video 2+.
- **SKEPTIC** = blonde, composed, arms-crossed, dry "prove it." Video 2+. OPEN GAP:
  needs a distinct VISUAL signature beyond "blonde + arms-crossed."

### Voice
- **Evan / inworld-tts-2 / speaking_rate 1.05.** Chosen for the DRY-HUMOUR SMIRK
  (the deadpan "Probably" landing) — the channel's defining vocal trait. Beat
  Derek & Dennis on that one axis, which is the must-have. Settings confirmed in
  the Inworld UI: Evan, "creative"-ish delivery, talking speed 1.05. Record exact
  settings in channel.json (speaking_rate) — voice consistency = brand.

### Production config (the LEANEST lane in the whole portfolio)
- Stills: Flux-pro/v1.1, flat-cel style_suffix, `safety_tolerance:"5"`. Only spend.
- Animation: **NONE.** Static holds per beat (`_still_to_held_clip`). No Kling, no
  Ken-Burns. (Pan/zoom is invisible/janky at a 1-3s cut rate — static cut fast is
  correct AND cheapest.)
- Audio: Inworld Evan @1.05.
- Mode: all Mode A. No Mode B yet. No music yet.
- Determinism: Driver lock in `base_canon` (auto-merges every beat) + rulebook
  `people_directive`. Specificity kills drift.


## ▌4. THE SCRIPT (locked pending Peter's final read)

**`soap_script_fast.md`** — "200,000 Years Without Soap." 57 FAST beats (4-10 words
each, ~1-3s). Driver-only solo-address, all Mode A, numbers spelled out, no in-still
text. Arc: cold open (2nd-person "right now you smell fine. Probably.") → first soap
(Babylon, ~2800 BC, was for cloth not bodies) → Romans (oil + scraper, no soap) →
medieval got-worse (bathing "dangerous," perfume hid the stink) → **Semmelweis**
(told them wash hands, mocked, died disgraced, proven right — the gripping spine) →
close (the soap on your sink is one of the NEWEST things about being human).

The fast-cut rhythm is authored IN the beat length — **script is king**, pacing
lives in the writing.

**SUPERSEDED:** `soap_script.md` (the slow version) — it reverted to Final Hours
15-35-word beats. REJECTED. The fast version is the channel.


## ▌5. THE FINAL-HOURS-BIAS INSIGHT (a durable meta-lesson — see NOTE file)

Peter spotted that reading the canonical doc was making us REVERT to patterns we're
trying to break. Diagnosis: **Final Hours was built first, so its craft infected the
"channel-agnostic" canonical docs.** The MECHANICS generalise (header format,
numbers-spelled-out, no-text-in-stills, the leg system, parse-verify, base_canon).
The CRAFT in `ante-machinam.md` Part IV is really the Final-Hours/Sacred-Dawn brief.

This channel deliberately BREAKS six rules: (1) beat granularity §6 (slow→fast),
(2) animatable-foreground §7 (we don't animate), (3) faceless-default Part III (we
have a visible character), (4) slow-dread register Part IV (we're bright/wry), (5)
photoreal style, (6) Ken-Burns floor (we go static, one notch leaner).

**Meta-principle: BUILD ORDER ENCODES BIAS.** Each genuinely-different channel needs
its own "here's what we break" brief. Full catalogue: `NOTE_final_hours_bias_in
_canonical.md`. Peter's framing: "we built Final Hours first so it infected
everything. No matter. The learning was the gift."


## ▌6. THE GLASSES SAGA (resolved — do not re-fight)

Across ~4 probe rounds, flux-pro/v1.1 put glasses on the Driver relentlessly (the
"clever young man" archetype summons them). Confirmed the model IGNORES negative
prompts AND ignores "NO glasses" in the positive (diffusion negation failure —
naming "glasses" can SUMMON it). **DECISION: the Driver HAS glasses.** Stop paying
the per-frame tax. Brain gets a different signature when she arrives.

Banked: on flux-pro/v1.1, negatives are weak-to-useless; the POSITIVE prompt is the
only reliable lever; you cannot reliably REMOVE a strongly-associated feature —
**design WITH the model's defaults, not against them.**


## ▌7. STYLE-PROBE FINDINGS (banked engineering)

- Model `fal-ai/flux-pro/v1.1` does illustration AND photoreal — style driven by
  prompt/suffix, NOT the model. No different model needed.
- Use `safety_tolerance:"5"` (NOT `enable_safety_checker:False`) — what the real
  pipeline uses to stop flux's silent ~7KB black-frame rejects.
- First style suffix oscillated flat↔photoreal per seed; the photoreal frames
  carried the AI-realism artifacts (warped backpack straps, stubble) WITH them.
  Fixing the style toward decisive flat-cel fixes the artifacts for free (flat is
  forgiving).
- v1≈v2 "identical output" scare: ruled out seed-cache + wrong-folder via ls -la
  (genuinely different bytes). Real cause: the long character description was
  OVERPOWERING the style suffix — style words drowned. Lesson: **prompt balance/order
  matters; the style needs to lead or the character desc dominates.**
- Cast described as "young adult" NEVER "teen" (the word "teen" + bodies trips the
  safety classifier → blank frame).


## ▌8. KEY PIPELINE FACTS (learned from reading the real code + canonical doc)

- **Authoring is a `script.md`, NOT hand-built JSON.** Header (bare key:value, NO
  `---`) + `## SECTION` + `[A] narration` line + `VISUAL: ...` line + blank line
  between beats. `parse_script.py` → beats_full.json. COPY a working script's markup.
- **Zero-spend verify before render:** `python parse_script.py <md> --json /tmp/b.json
  --json-full /tmp/f.json` (prints beat count; number=good, crash/0=bad).
- **channel.json keys (exact):** name / voice_id (snake_case! `voiceId`→silent Victor
  fallback) / style_suffix / default_motion / default_music_prompt / base_canon /
  upload / thumbnail / music / speaking_rate.
- **base_canon auto-merges into every beat** → Driver lock goes here.
- **people_directive (positive) is the real lever; negatives weak on flux-pro.**
- **Channel creation = an idempotent `patch_*.py`** modeled on
  `patch_scripture_on_screen_channel.py` (schema-checks our keys as a SUBSET of a
  reference channel's keys, then writes `<slug>/channel.json`). laptop→commit→push→
  box pull→re-run to verify. Does NOT create the project folder (Mission Control does).
- **Rulebook:** each channel has `rulebook.json` (`negative` list + `people_directive`
  + `motion_rules`); `load_rulebook_negatives()` reads it. **STILL OUTSTANDING:**
  `cat ~/Pipeline/rulebook.json` (shared default) to build ours.
- **Static-hold EXISTS:** `_still_to_held_clip` ("static video clip via ffmpeg, no AI
  motion") — currently a Kling-refusal fallback; for THIS channel it becomes the
  DEFAULT. **STILL OUTSTANDING:** `grep -rn "_still_to_held_clip\|kling_count\|zoompan"
  ~/Pipeline --include=*.py` to learn how to set it as default.
- Gotchas: slug `^[a-z0-9][a-z0-9-]{0,60}$` (hyphens not underscores); channel header
  must match folder; YouTube account phone-verify needed for >15min uploads (soap
  ~6min, fine); CEST `+02:00` in summer for scheduling.


## ▌9. ⭐ THE THUMBNAIL BREAKTHROUGH (the most valuable thing from late session)

Peter's gut, looking at his first polished soap thumbnail next to Ink's row: **"won't
people just think 'oh another travel vlogger'? Maybe Ink works BECAUSE it's
off-the-wall."** This was the sharpest strategic catch of the day. The first soap
thumbnail (handsome guy shrugging in a desert) read GENERIC — competent = invisible.
Ink's crude weird thumbnails are arresting precisely because they're weird.

The resolution (Peter's call): **don't go weird (unsustainable for 2 years) — find
the edge that's compatible with polished.** Then a probe answered it.

**THE PROBE:** three expression variants of the Driver, flat colour backgrounds:
- `var_A_recoil` (yellow, hands up, jaw-dropped, wide-eyed shock) → **WINNER.** Reads
  at thumbnail size, promises something shocking, matches the "ew really?" soap hook.
- `var_B_delight` (purple, grin-laugh, one hand out) → strong #2; "wonder" energy,
  keep for wonder-topics (ocean floor, future-flip).
- `var_C_grin` (yellow, thumbs-up, mild smile) → WEAKEST; 4/10 expression = the
  "polished but tasteful = invisible" trap. Proved flat-bg ALONE isn't enough.

**THE LOCKED THUMBNAIL FORMULA (bankable, channel-wide):**
> **flat saturated colour background  +  the Driver doing a 9/10 reaction  +
> two-tier bold headline (white gap-line + gold anchor-line)  +  character RIGHT,
> text LEFT.**
> Recoil/shock for "ew/no-way" topics; delight for wonder topics. SAME recurring face
> every time = the compounding recognition moat Ink CANNOT build with random scribbles.

**Key reversals banked here:**
- "Boring desert" → **flat bold colour makes the character POP.** Rich scenes are
  for VIDEO FRAMES; flat colour is for THUMBNAILS. Opposite jobs. (Claude had earlier
  pushed rich backgrounds; the thumbnail context flips it.)
- Expression must be pushed to 9/10. The mild shrug/thumbs-up is the invisible trap.
  Polished AND BIG, never polished-and-restrained. (Pixar, not corporate.)
- The recurring character's face IS the differentiation — use it as the consistent
  thumbnail anchor and it compounds (MrBeast model).

**The final composited thumbnail** ("NO SOAP?" white + "FOR 200,000 YEARS" gold, recoil
Driver on yellow) — Peter's reaction: it stops the scroll. SHIP-WORTHY.

**THE ONE OPEN THUMBNAIL QUESTION (last real decision):** the winning thumbnails
rendered PHOTOREAL, but the video is FLAT-CEL. Mismatch risks (a) a sliver of
first-second retention loss (clicked face ≠ video face) and (b) breaking the
recurring-face recognition. DECISION NEEDED: render the thumbnail in flat-cel for
consistency, OR accept photoreal because it pops harder. **Cheap test:** regenerate
the exact winning pose/bg/text in flat-cel, put side by side — if flat-cel pops
nearly as hard, take it (pop + consistency + moat, no tradeoff). If it noticeably
loses punch, weigh consciously. NOT yet settled.


## ▌10. FILE INVENTORY (all in /mnt/user-data/outputs/)

| File | What | Status |
|---|---|---|
| `soap_script_fast.md` | THE pilot script, fast-cut, real format | LOCK pending final read |
| `soap_script.md` | Slow version | SUPERSEDED — ignore |
| `_Crew.md` | Channel doctrine doc | v0.1 |
| `crew_character_bible.md` | The durable IP (Driver locked, Brain/Skeptic specced) | v0.1 |
| `NOTE_final_hours_bias_in_canonical.md` | The bias catalogue | Keep |
| `patch_crew_channel.py` | Channel-creation patch | Draft — needs finalising (§11) |
| `channel.json` | Standalone draft | Superseded by the patch |
| `flux_driver_probe_v2.py` | Production-accurate style probe | Ran; findings banked §7 |
| `flux_driver_probe.py` | v1 probe | Superseded |
| `SOAP_SHOTLIST_v1.md` | Frame-typed shot-list (the 7 frame-types) | Reference (see §13) |
| `THREE_MVP_SCRIPTS.md` | Original 3 MVP scripts | Reference |
| `beats_full_coldopen.json` | Hand-built JSON cold-open | Superseded (use .md→parse) |
| `SESSION_NOTES_crew.md` | Earlier partial notes | Superseded by THIS file |
| `MASTER_SESSION_NOTES_crew.md` | THIS file | Current |


## ▌11. NEXT ACTIONS (priority order — start here next session)

1. **Confirm the soap render** that was kicking off on the box at session end (§12).
   Check `crew-wip/projects/soap-full/render.log` and the output. This may already
   answer the big questions (flat-cel style in-pipeline, Driver consistency, Evan
   sync, pacing).
2. **PETER: final read + LOCK** `soap_script_fast.md` (script is king).
3. **Settle the thumbnail style question** (§9): flat-cel vs photoreal — one-render
   test, side by side.
4. **Two outstanding file reads** (only things blocking complete config):
   - `cat ~/Pipeline/rulebook.json`
   - `grep -rn "_still_to_held_clip\|kling_count\|zoompan" ~/Pipeline --include=*.py`
5. **Finalise `patch_crew_channel.py`:** add `speaking_rate:1.05` + `default_motion`
   + Driver-lock in `base_canon`; pick `category_id` (27 Education vs 24 Entertainment
   — Peter's call); schema-check against a NON-Final-Hours reference channel.
6. **Build `crew-wip/rulebook.json`** (from the shared template): Driver in
   people_directive (glasses OK), flat-cel + anti-realism terms in negative.
7. **Run the channel patch** (laptop→commit→push→box pull→verify idempotency).
8. **Parse-verify** the script zero-spend, then render (cold open first as a cheap
   in-pipeline test if not already done by the §12 run, else the full 57).
9. **Build the locked thumbnail** with the §9 formula.
10. **SHIP IT.** Publish, set the AI-disclosure flag manually, category Entertainment/
    Education + tags. Shipping is what turns this BUILD into a BET.
11. **Read first-48h CTR + AVD** → crank (animation/music/crew/movie) or park.


## ▌12. WHAT WAS RUNNING ON THE BOX AT SESSION END

The terminal in the last screenshot showed `orchestrate.py --project soap-full
--beats ... --unattended` running, with "2a · narration assembled → 1246 words",
"voiceover (Inworld)", and a project at `crew-wip/projects/soap-full/`. So a full
soap render appears to have been STARTED. **First thing next session: check whether
it completed, and what the stills/video look like.** Files referenced: `canon.json`,
`render_policy.json`, `render.log`. NOTE: this means a `crew-wip` channel + project
may ALREADY exist on the box — verify state before re-running the patch (it's
idempotent, so safe, but check).


## ▌13. THE FRAME-TYPE VOCABULARY (banked for video 2+, NOT the pilot)

The "max variation" idea — stress-test every frame kind in one video. The 7 types:
**SCENE, CREW, TIMELINE, CHART/COMPARISON, DIAGRAM/CALLOUT, PORTRAIT, MAP.** These
map onto the pipeline's Mode A (SCENE/CREW/PORTRAIT stills) + Mode B (TIMELINE/CHART/
numbers as Remotion graphics). DECISION: the PILOT is all-Mode-A lean (no Mode B);
the frame-type variety is the **video-2 upgrade** once the basics are proven (one
variable at a time — don't test 7 frame-types + character-consistency + new style +
new voice in one render). The full typed shot-list is in `SOAP_SHOTLIST_v1.md` for
when we promote data-beats to Mode B.


## ▌14. DURABLE STRATEGIC PRINCIPLES BANKED TODAY (cross-channel)

- **Diversify cheap at-bats, concentrate craft on winners, crank the dials post-data.**
  A build becomes a BET only when it SHIPS and generates signal. Unshipped = horse in
  the stable. Cure for "did I waste this build?" = ship and get data, not build more.
- **Build order encodes bias** (Final Hours infected the canonical). Each channel needs
  its own break-list.
- **The durable asset is the CHARACTER BIBLE, not renders.** Renders get regenerated up
  the ladder; the tool-agnostic crew spec carries from stills→animation→lip-sync→movie.
  Future-proofing effort → the bible, not over-building the pilot.
- **Design lean now on infra that already scales.** Animation/music/Mode-B/movie
  capability ALREADY EXISTS in the channel-agnostic pipeline — turn on by config flip,
  not rebuild. Future-proofing is INHERITED from the architecture.
- **Polished is a sustainable register choice; tasteful-invisible is its failure mode.**
  Win without weird via: maximal expression + recurring-face brand + bold gap-text +
  high-contrast pop. The recurring face COMPOUNDS where random scribbles can't.
- **Thumbnail ≠ video, on purpose:** flat bold colour + huge expression for thumbnails;
  rich scenes for frames. Opposite jobs.
- **Kids = de-biased focus group:** weight raters by least-confounded variable (daughter
  on female chars, sons on male); judge CHARACTER not looks; isolate ONE variable per
  test.
- **Specificity kills render-drift; vagueness summons it.**
- **flux-pro: design WITH the model's defaults (glasses), not against them; positive
  prompt is the lever, negatives are weak.**
- **Name it don't describe it; defer the name until the pilot names itself.**
- **Script is king** — pacing lives in beat length; lock the script before anything binds.


## ▌15. DEFERRED / BANKED IDEAS (not for the pilot, don't lose them)

- Channel NAME — after the pilot. Survivors for the out-loud kid-test: Last Seen, The
  Last Time, Quest (secretly "question"+quest), Trove, Kove, Vyse, Fathom. Wide scope
  argues for an empty-vessel name. Avoid "Curious" (over-crowded). 300+ candidates
  generated across 5 lists if needed.
- The first-10 topic slate (idea-gated, scope-spread): Soap (flagship), Before Phones,
  Why We Cry, First Embarrassment, Last Mammoth, Sleep in the Dark, First Lie, 200-yrs-
  future Last Coin, Scared of the Dark, Bottom of the Ocean, First to Wonder What's Up
  There.
- Brain + Skeptic introduction (video 2+); Skeptic needs a distinct visual signature;
  all three need in-show NAMES (currently role-labels only).
- Mode B frame-type variety (video 2+); the upgrade ladder (motion→music→lip-sync→movie).
- The "delight" thumbnail expression (var_B) for wonder-topics.

# ════════════════ END — rest well. Ship it next time. ════════════════
