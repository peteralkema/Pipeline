# _QQrew.md — CHANNEL DOCTRINE (@Q-Qrew)
*The comprehensive, durable craft + config + strategy brief for @Q-Qrew. Single-underscore = channel doctrine (load per channel); the double-underscore canonical reference is the system. Where this doc and any Final-Hours-derived craft disagree, **THIS DOC WINS for this channel** — see §12 the break-list. (NB: `ante-machinam.md` was RETIRED 30 June — that FH craft now lives in `_Final-Hours.md §11`; the genuinely-universal mechanics are in canonical §8. This channel reads the canonical mechanics and ignores FH craft by design.)*

*v1.0 — POST-RENDER, POST-SHIP. Supersedes `_Crew.md` (which was v0.1 pre-render design). Every section below is now proven by the soap pilot (238-beat full episode, shipped 29 Jun 2026), not speculative. Bump when a render banks a new lesson.*

---

## 1. WHAT THIS CHANNEL IS

A recurring **crew** investigates **the unfilmable** — things no camera could ever capture, across all of time and space: the deep past, the far future, unreachable places (the ocean floor, inside a volcano, two hundred years from now). The crew is the constant; the topic is the infinite variable.

**The thesis bet:** the production system + the recurring cast are the moat. Competitors clone a topic lane in a weekend; they cannot clone a recurring cast with a register. The breadth is deliberate anti-flood insurance.

**The feeling:** bright, curious, wry, propulsive, playful-on-top with real substance underneath. A clever excited friend telling you something wild — NOT a museum docent. The exact opposite of dread-and-dignity. "Skibidi-energy" in delivery, genuine content beneath.

**The identity:** @Q-Qrew. Double-Q = "lots of Questions"; Qrew = Crew on a Quest. Handle claimed 29 Jun 2026. Channel #12 in the Flywheel; the deliberate ANTI-Final-Hours channel.

**The audience:** young-adult coded. NOT Made-For-Kids (revenue death). NOT age-restricted (reach death). The general-audience middle — edgy-but-not-graphic; the cartoon style lets dark topics be handled safely.

---

## 2. ORIGIN & STRATEGIC CONTEXT

Born 29 Jun 2026 from frustration with **Final Hours** (a channel fighting distribution despite good craft). The move was not to grind Final Hours but to **spin the Flywheel into a new lane** — proving the core thesis that the system is the moat and any single channel is a disposable experiment. QQrew is that experiment: same pipeline, new brand/look/register, judged on the 48h CTR+AVD signal. Cheap to roll (≈ low-double-digit dollars/episode), affordable to be wrong, designed to crank-if-it-hits / park-if-flat.

---

## 3. COMPETITIVE ANALYSIS & POSITIONING

- **The lane:** bright fast-cut curiosity-explainers (the Ink/Mack rhythm — 1-3s cuts, second-person hook, "stranger than you think" payload). A served, evergreen lane with proven demand for the FORMAT (not yet proven for THIS channel — that's the open bet).
- **The differentiation:** QQrew sits **one production tier above** the flat-stick-figure incumbents. The polish IS the moat — produced flat cel-shaded illustration with rich backgrounds and a recurring named cast, vs. the incumbents' disposable stick figures and faceless VO. Same rhythm, higher craft, a face you recognise.
- **The anti-flood logic:** a topic-lane competitor can clone "history of X" in a weekend. They cannot clone a recurring crew with a register and a visual signature that compounds recognition over a catalogue. The cast is the durable IP (see §7, and `crew_character_bible.md`).
- **Why evergreen-not-spike:** the edge is best-execution in served, evergreen lanes — NOT spike-chasing. NexLev / Trends are lagging/detail signals, not topic-pickers. The idea-gate (§5) is the topic filter, not trend data.

---

## 4. STYLE (REVERSED 01 Jul 2026 — flat-cel was the bug)

**PRODUCED SEMI-REALISTIC BRIGHT ANIMATED-FEATURE ILLUSTRATION.** Appealing realistic detailed faces, rich detailed illustrated backgrounds, real depth, high detail, polished animated-feature quality — the fidelity of the approved trio references (`02_egyptian_tomb.png`, `08_mughal_india_palace.png`). This is the tier the audience will actually click.

**Semi-realistic in FIDELITY, bright/funky in REGISTER.** The look is REAL (real faces, real depth, rich backgrounds) but the register is bright, funky, fun, choppy, dynamic, high-key, vibrant, energetic, lots of light. **Explicitly ANTI-dark, ANTI-candlelight, ANTI-Victorian, ANTI-painterly, ANTI-moody-cinematic.** Register words like "painterly / atmospheric / cinematic color grade / soft shading" leak the Final-Hours dread register in through the back door — they drag the whole channel moody, INCLUDING facial expression (a moody-lit Skeptic reads as sullen/pouty, not wry). Keep the fidelity words, ban the register words.

**Backgrounds are a first-class element** — half the appeal. Rich, warm, detailed, inviting, bright. Never bare. The crew always stands somewhere worth visiting.

**channel.json style_suffix (CURRENT — bright, ep4+):**
> "semi-realistic modern animated-feature illustration, appealing realistic detailed faces, rich detailed illustrated backgrounds, bright high-key lighting, vibrant saturated color, crisp clean and dynamic, lots of light and energy, polished animated-feature quality, high detail, inviting and fun, no text, no letters, 16:9"

**⚰ TOMBSTONE — the flat-cel suffix (v1.0, WRONG, cost a full day 01 Jul):**
> ~~"clean flat 2D cel-shaded illustration … NOT photorealistic, NOT 3d render, NOT realistic skin texture …"~~ — a NEGATIVE suffix that hard-banned "painterly, semi-realistic, rendered, 3d" and forced a flat 2D webcomic cartoon on every text-to-image beat (the Bambi fawns, the flat skies). Read as a cheap kids' show; would have tanked CTR. The interim over-correction ("semi-realistic cinematic painterly … warm cinematic color grade, atmospheric depth") fixed the cartoon but leaked the FH moody register → the pouty-Skeptic tell. The MERCATOR1 render (01 Jul, Ep3) shipped on that interim painterly suffix — good enough, not re-rendered; ep4+ uses the bright suffix above. **See §6a for the full misdiagnosis chain.**


### ★ 4b. THE AFTERNOON FIXES (01 Jul — render config, banked)

The §4 suffix reversal was necessary but not sufficient. Four more render-config faults surfaced the same day and were fixed; all four must hold for the channel to render right.

**1. STANDARDISED ON ALL-NB2 (QQrew-only decision).** The channel previously mixed models: NB2 `/edit` for character beats, but `image_model:"nano_banana"` text-to-image for crew-absent beats, with flux as a fallback — and briefly flux for the wides. The mixing caused an aspect-ratio split AND risked a look/texture mismatch between the wides and the character beats. **Decision: one model family — NB2 for everything.** NB2 `/edit` (reference) for `{skeptic}` beats, NB2 text-to-image (`fal-ai/nano-banana`) for crew-absent beats. `image_model:"nano_banana"` in channel.json. The optionality wasn't worth the friction; one model = consistent look across all 180.

**2. THE ASPECT-RATIO BUG (the size param differs by endpoint).** NB2 and flux take DIFFERENT size params, and passing the wrong form silently defaults to 1024×1024 square:
- **NB2 (both `/edit` and text-to-image)** wants `aspect_ratio: "16:9"` (a STRING). It IGNORES an `image_size: {width,height}` dict.
- **flux** wants `image_size: ASPECT` (the DICT). 
- **The bug:** the reference `/edit` path passed only the string but NB2 `/edit` still echoed the PORTRAIT reference PNG's proportions (the `skeptic_ref.png` is 174×450 portrait) → portrait stills. The text path passed the dict to NB2 → square stills. **The fix:** `/edit` path now also sends `image_size: ASPECT` (belt+braces); text path branches per model (NB2 → `aspect_ratio` string, flux → dict). See `patch_ref_image_size.py` + `patch_all_nb2_aspect.py`.
- **Residual:** NB2 rounds "16:9" to its own supported buckets (~1344×768 or 1376×768, ratios 1.75–1.79) — visually 16:9 but not pixel-exact 1280×720. **`enforce_16x9.py` is the post-render pass** that normalises every still to exactly 1280×720 before assemble (pad-to-fit, no crop). Run it after every render, OR rely on assemble's scale-to-frame. Do NOT chase pixel-exact at the endpoint — NB2 won't give it.

**3. THE REFERENCE LOCK IS THE REAL LEVER FOR CHARACTER BEATS (look AND mood).** Reference `/edit` beats BYPASS the channel `style_suffix` entirely — their only style instruction is `REFERENCE_PROMPT_LOCK` + `REFERENCE_PROMPT_TAIL` (in `recreation_pipeline.py`). These hardcoded the FH moody register ("painterly rendered skin", "soft warm lighting", "warm cinematic lighting") → every Skeptic beat rendered dreary AND pouty regardless of the bright suffix. **This is why the suffix work never fixed her face.** The lock is now de-mooded: identity-hold + "semi-realistic modern animated-feature, bright high-key lighting, vibrant color … the character is bright, engaged and lively with a warm easy half-smile — never bored, never pouty, never flat." **Durable rule: on a reference-render channel, the character's look AND expression live in the LOCK, not the suffix and not only the canon tag. Fix the lock first.**

**4. SKEPTIC EXPRESSION CANON.** `base_canon.skeptic` ended "dry deadpan expression" → rendered bored/pouty (the Gen-Z-deadpan-that-reads-as-sulking trap). Changed to "bright engaged expression with a warm easy half-smile, sharp and lively." Keeps her sharp/wry without a goofy grin; the crack-once deadpan character is carried by writing, not by a flat resting face.

---

## 5. THE SCRIPT (the moat — script is king)

**Fast-cut rhythm authored into beat length.** 4-10 spoken words per beat, ~1-3s each. Many short beats, rapid cuts. The pace is in the WRITING, not in animation. This is the Ink/Mack cut rate and the channel's signature.

**THE LENGTH DOCTRINE (the session's headline finding — PROVEN):**
Fast-cut and long-form are NOT in tension. **You write MANY fast beats, not FEW.** A 7-min episode in this lane is ~220-240 beats, not 50. The pilot's first attempt (53 beats → 1:42) was a cold-open scoped as an episode — wrong. The fix is authoring: expand each section into its own hook→detail→turn→payoff mini-arc; the biggest single arc carries the emotional climax and can run 45-55 beats alone (soap: Semmelweis = 55). Target lane: **~6-9 min, lower-middle preferred** (a tight 7:30 that never sags beats a padded 9:00).

**BEAT-LENGTH VARIATION (matters over long form):** a uniform 4-6 word cadence drones past ~3 min. Push ~15-20% of beats to the extremes — 1-2 word gut-punches ("None." "No." "Germs were real.") AND occasional 10-15 word breathers. Rhythm = syncopation, not constant speed. Proven spread (soap v2): 1-15 words; 17% punch / 61% standard / 17% longer / 3% breather.

**CHARACTER PLACEMENT (drift-management via authoring):** concentrate the recurring character at the BOOKENDS (cold open ~75%, close ~68% — where the character bonds with the viewer); pull him back through the dense, object-rich middle (Semmelweis ~27%). Every talking-head beat converted to an object/environment shot does triple duty: less drift risk, more visual variety, lets backgrounds breathe. **Target ~40% character presence overall, lower in object-rich sections.** Convert the interchangeable "{driver} nodding/gesturing to camera" reaction beats first — they're the most drift-exposed and the most replaceable.

**The locked format (from the winning Ink/Mack explainers):**
1. Cold open = second-person present-tense gut-punch (viewer implicated in line one: "Right now, you smell fine.").
2. The "you'd assume X — but no" pivot inside ~20s (opens the retention loop).
3. Chronological evidence-walk pinned to named researchers/places/dates (the credibility scaffold).
4. The inversion payload: "older/weirder/more recent than you think."
5. Ring-close back to "you, right now."
6. ONE thesis, bright-not-morbid, second-person held throughout, no sprawl.

**The idea-gate (score before authoring):** universal behaviour everyone shares + an invertible buried assumption + a present-day reframe + bright-not-morbid. Spread topics across the scope (past / future / unreachable) so the algorithm learns the channel goes anywhere.

**Render-safety at authoring stage:** human-distress verbs (dragged, restrained, screaming) risk classifier rejection. Render dark material via ENVIRONMENT/objects — empty beds, a folded blanket, a single candle, a covered table with no people. (soap's Semmelweis deaths rendered entirely environmentally — under the classifier, and avoids the uncanny-valley face problem.) Assess at authoring, not at render time.

**Numbers spelled out in narration; numerals in metadata. No in-still legible text.**

---

## 6. VISUAL DESIGN — TWO STILL CLASSES (banked 29 Jun)

The channel has **two distinct, deliberate still classes**, and the interplay between them is the visual rhythm:

**(a) CHARACTER-FOREGROUND** — the Driver (or crew) carries the beat. Recognition mechanic, second-person bond, the face people come back for. The default.

**(b) CREW-ABSENT ESTABLISHING-WIDES** — *the world carries the beat, no crew in frame.* (The Roman-bathhouse aerial was the exemplar that triggered this.) High-value, and works BECAUSE the crew is absent. Three jobs at once:
1. **Variety** — the visual exhale between character beats.
2. **Drift-relief** — no face = zero character-drift risk on that beat (free consistency).
3. **Production-polish signal** — a rich, populated, cinematic wide reads "made with care," elevating above stick-figure incumbents.

**Authoring rule:** deploy wides at section-openings / scale-reveals / "behold the place" beats. Spec them explicitly in VISUAL lines (wide aerial / crowd / architecture, NO {driver}). They are NOT a compromise on the recurring-character premise — they're the counterpoint that makes the character beats land. **Use more of these in future videos.**

(Object/detail close-ups — the strigil, the clay tablet, the microscope, the empty ward — are a sub-mode of carrying the dense middle without the character; see §5 character-placement.)

### ★ 6a. PROMPT CONSTRUCTION — canon is an IDENTITY TAG, not a portrait (banked 30 Jun, the Ep3 stills regression)

**The failure (Ep3/pregnancy1, 213 stills):** the rendered set came back as ~20 near-identical beauty-portrait headshots of one blonde woman, most of them PHOTOREAL — the opposite of the bright flat-cel curiosity-explainer the channel is. The script was NOT at fault (the VISUAL lines had real variety — "crouched beside a faint glowing pelvis diagram on the floor, tapping the bone ring," "air-quoting with both hands"). The **prompt construction** was at fault, in two compounding ways:

1. **The channel `style_suffix` was NOT appended to the prompts.** Confirmed: storyboard prompts ended in a thin author-written "animated flat illustration" (3 words), NOT the channel's full suffix ("clean flat 2D cel-shaded illustration … NOT photorealistic, NOT 3d render, NOT realistic skin texture"). Without "NOT photorealistic" in the prompt, flux-pro defaults to its photo prior → the photoreal drift. *(Fix in §11 P0.)*
2. **The canon string ATE the prompt.** Each prompt opened with **~120 words of Skeptic canon** — full face/hair/skin/wardrobe/expression ("softly feminine, smooth skin, soft delicate features, slim build, relaxed confident posture…") — and the actual scene/posture arrived as a starved tail. flux-pro weights the front of the prompt heaviest, so the model spent its attention rendering *a supermodel portrait* and never reached "crouched at the pelvis diagram." Worse, the canon's own words ("smooth skin, soft delicate features, warm friendly face") actively pull toward photoreal, fighting the (missing) cel-shaded suffix.

**THE DOCTRINE (durable, channel-defining):** **on a character channel, canon must be a SHORT identity tag, not a full portrait.** The recurring-character canon-merge mechanism was inherited from Final Hours, where canon describes *places* ("the lamp room") that you WANT dominating every frame — for a character channel, merging a 120-word person-description into all 213 prompts drowns the scene every single time. This is another Final-Hours bias artifact (place-canon logic mis-applied to a character channel). The fix is structural, not per-prompt:

- **Canon = a short tag** carrying ONLY what must stay constant for glance-level recognition: *"Skeptic: late-20s woman, blonde shoulder-length bob, tan camel jacket over white tee, layered gold necklaces, dry deadpan."* (~20 words, not 120.) Drop the photoreal-coded beauty words entirely — "smooth skin / soft delicate features / warm friendly oval face" are both portrait-bait AND realism-bait.
- **Prompt ORDER must be: [STYLE] + [SCENE/POSTURE/ACTION — the beat] + [short canon tag].** The beat leads so the model renders the *action*; canon trails as a consistency anchor; the full flat-cel style suffix is present and weighted. NOT canon-first.
- **The negation lives in the style suffix, not the canon.** "NOT photorealistic, NOT 3d render" must be in every prompt (it's the channel's decisive lever — §4).

**★ CORRECTION (01 Jul 2026 — the misdiagnosis, banked after a full day lost).** The two-fault theory above was HALF WRONG on the primary cause. What actually happened, proven by reading the live code + config:
- **The `style_suffix` WAS reaching the prompts** (`recreation_pipeline.py` lines 608-609 / 645 build `full_prompt = f"{style_suffix}. {image_prompt}"`). Fault 1 ("suffix not appended") was NOT the live fault.
- **The real disaster was the CONTENT of the suffix:** it was a flat-cel / webcomic string that HARD-BANNED "painterly, semi-realistic, rendered, 3d" — so it FORCED a cheap 2D kids-cartoon on every text-to-image beat (the Bambi fawns, the flat skies). The model was never failing; the suffix was vetoing its best output.
- **The canon-tag cut (89w → 18w) was correct but MINOR.** Skeptic beats route through the reference `/edit` path + `skeptic_ref.png` and BYPASS the channel canon entirely; the canon only bites if a `{skeptic}` beat falls to the flux fallback. So Fault 2 ("canon eats the prompt") barely applies on a reference-render channel.
- **THE FIX:** replace the suffix (flat-cel → semi-realistic bright — see §4). Immediately produced the approved trio-tier look. **Second trap found same day:** the first replacement over-corrected into "painterly / atmospheric / cinematic color grade" and leaked the Final-Hours moody register → sullen/pouty Skeptic faces; corrected to bright/high-key (§4).
- **THE DURABLE LESSON (graduated to canonical):** the `style_suffix` is the single highest-leverage lever on channel look. **When renders look wrong, READ THE ACTUAL SUFFIX FIRST — before canon, script, or references.** A negative suffix that bans qualities silently vetoes the model; register words (painterly/atmospheric/cinematic) drag the whole channel — including facial expression — toward that register.

**This is what separated Ep1 (good) from Ep3 (bad):** Ep1 was Driver-solo, and Driver's canon is shorter and less photoreal-coded than the Skeptic's lush portrait string — so it drowned the scene less. The Skeptic's beauty-portrait canon is what tipped a latent fault into a visible disaster. The fault was always there; the richer canon exposed it.

---

## 7. THE CREW (durable IP — full spec in `crew_character_bible.md`)

Core of THREE, never more (guests are per-episode, never core):
- **DRIVER** — "the guy." Energy / launch engine. Backpack signature, dark glasses (accepted, not fought). **THE PILOT IS DRIVER-ONLY.** Voiced by Evan (Inworld) @1.05 — brisk with a dry-humour smirk. He carries the entire solo-address narration. **PROVEN this session:** holds glance-level consistency across 238 beats and wild setting changes, near-zero drift, in flat-cel.
- **BRAIN** — the sciency-stylish young woman (glasses + messy bun = her tells). Knowledge engine. Specced, not yet probe-validated. (Daughter-locked brief — de-biased female-character rater.)
- **SKEPTIC** — the blonde, composed, dry. Audience stand-in; her doubt forces the next evidence beat. Specced; **OPEN GAP: needs a distinct visual signature** beyond "blonde + arms-crossed" (collision risk with Brain).

**Narration architecture (the retention engine — PROTECT THIS):** the default is ONE crew member talking DIRECTLY TO THE VIEWER (second person: "right now, you…"). The other two are REACTION cutaways, NOT a conversation. The moment the crew talk to EACH OTHER, the viewer becomes a spectator instead of the person addressed — which kills the second-person retention spine. Full ensemble is reserved for tentpoles.

**The character-determinism problem (be honest):** this pipeline was BUILT FACELESS (Flux drifts on faces). A recurring visible character is the hardest thing it does. Mitigations: (a) over-specify in base_canon (specificity kills drift); (b) accept the model's strong defaults rather than fight them (glasses, and now possibly the beard — see §8); (c) the durable fix at the animation/movie tier is image-to-image / reference-conditioning, deferred. For fast-cut stills, glance-level consistency is the bar (nobody freeze-frames to compare faces) and it's achievable — proven.

---

## 8. THUMBNAIL DESIGN (tuned to repeatable — PROVEN this session)

The thumbnail is the single most important packaging surface. The system is now a locked config that produces scroll-stoppers automatically.

**Composition:**
- **Subject = a REACTION beat** (huge shocked/disgust/delight expression), NEVER a calm portrait. Emotion stops scrolls.
- **Character pushed RIGHT, left third empty** for the top-left headline.
- **NO ECHO** — the image must never show the headline's noun. "NO SOAP?" over empty shocked hands (no soap in frame) forces the question; a matched image+text pair gives no reason to click. **The gap IS the click.**
- **Flat saturated POP-background > busy scene.** Clean gold pops far better than any cinematic still in the feed. Thumbnail ≠ cinematic still.
- **Headline: two lines, ~13 chars/line max, Anton font.** Short punchy headline, NOT the SEO title. ("NO SOAP?" / "FOR 200,000 YEARS".)

**Config (channel.json thumbnail block — locked values):**
- **margin_x: 40, margin_y: 20, title_area_pct: 0.52, title_start_size: 150** — the proven block, copied from final-hours/you-had-to-be-there/sacred-dawn. (crew's inherited margin_y:48 from success-coach was the float-down bug; margin_y:20 was the "boooom" fix.) **NEVER clone thumbnail config from success-coach.**
- **darken_factor: 1.0, scrim: {width:0, opacity:0}, vignette_strength: 0.0** — ALL THREE darkening sources OFF for flat-pop backgrounds. The "house look" is three-deep and stacks; the white headline's own black text-outline carries legibility over flat bright color. **STYLE-COUPLED:** these return for any busy/dark-scene thumbnail. Diagnosis: A/B composited-thumb vs raw-still; any darkness delta = a layer still firing.

**The model-prior wall (hard lesson, re-confirmed):** flux-pro/v1.1 will NOT remove a strong prior by prompt — the beard survived 3× subject-negation AND a positive-assertion suffix rewrite; centering ignored "push right." **When the model has a strong prior, design WITH it** (accept the beard / make the canon Driver bearded), OR composite from a full-scene video still (clean-shaven, because the close-up portrait genre is what summons the beard), OR fix in post. OPEN DESIGN CALL: accept-bearded-canon-Driver vs composite-from-still as the standard method.

**Title (metadata) vs thumbnail headline are DIFFERENT strings** — full SEO title in the header, short punchy headline on the thumbnail.

---

## 9. PRODUCTION CONFIG (the leanest lane in the portfolio)

- **Stills:** Flux-pro/v1.1, flat-cel style_suffix, `safety_tolerance:"5"`. The only real spend (~238 stills/episode).
- **Animation:** **NONE — TRUE STATIC** (the motion doctrine, proven). Static holds per beat. NO Kling, NO Ken-Burns. The cut IS the motion; pan/zoom is noise at a 1-3s cut rate. (Until Patch B lands natively, render kling_count:0 then post-process with `reassemble_static.py` to strip the Ken-Burns zoompan.)
- **Audio:** Inworld **Evan @1.05** (the dry-humour smirk; record exact settings — voice consistency is brand). **KNOWN ISSUE → P1 fix:** per-beat synthesis causes the "seesaw" voice reset; the fix is continuous section/sentence-group synthesis + Whisper-mapped still cuts (see §11 / session notes P1).
- **Mode:** all Mode A. No Mode B (yet). No music (yet).
- **Character determinism:** **the whole recurring crew lives in `base_canon`, not the per-project `canon.json`** (Driver AND Skeptic both, locked there; auto-merges every beat) + `people_directive` in the rulebook. Specificity kills drift. **WHY base_canon, not the project file (banked 30 June — the canon-precedence bug):** the engine's stills path loaded `base_canon` and *ignored* the project `canon.json`, so a Skeptic-solo episode whose canon sat only in the project file died with `Unknown canon tag(s): ['skeptic']`. The crew are permanent cast, so `base_canon` is their correct home anyway; the per-project `canon.json` is for **per-episode guests / wardrobe overrides only**. (The deeper fix — make the engine *merge* base_canon + project canon, project-wins-on-conflict — is on the canonical code-leakage list, §2B item 3.)
- **Category (metadata):** **Education (ID 27)** — NOT Entertainment (24). Education routes to the right suggested-video pool AND a higher-RPM ad bucket. (channel.json `category_id` should be "27" for the auto-upload step; the `qqrew` channel.json still carries "24" inherited from success-coach — **OPEN: fix to 27**.)

**The render path (proven, reuse):** `ingest.create_project` (zero-spend verify) → inject `canon.json` + `render_policy.json {kling_count:0}` → `orchestrate.py --unattended` (note: still hits a Mode A stills gate, clear with "go") → `reassemble_static.py` for true-static → set thumbnail → upload.

**★ THE FOLDER INVARIANT (banked 30 June — the rename that unblocked Ep3).** This channel lived at `crew-wip/` during bring-up; its projects were at `crew-wip/projects/<slug>`. **That broke the engine** — `_engine_project` resolves a project by `basename`-from-`run_cwd`, which silently assumed the portfolio invariant `<channel>/projects/<slug>` and invented `./<slug>/` for the deeper `crew-wip/` path, so the stills leg loaded the wrong (empty) folder and died before the first PNG. **Fix: the channel folder is now `qqrew/`** (matching the `channel: qqrew` header) and every project sits at `qqrew/projects/<slug>` — the invariant every other channel honours. **Durable rule: a channel folder MUST be named for the channel and hold projects at `<channel>/projects/<slug>`; never run a channel out of a work-in-progress staging folder.** The `_engine_project` basename-collapse that hid this is on the canonical code-leakage list (§2B item 4 — root the engine at the real project dir, fail loud). NB the scripts' source home is still the tracked `qqrew/docs/`/`crew-wip`-era staging → migrate to a clean `qqrew/`-rooted flow (P9).

**The upgrade ladder (config flips, not rebuilds — turn on as the channel earns it):** static stills (now) → continuous-audio sections (P1, next) → per-beat motion (flip kling_count, if ever wanted) → music → Mode B data-graphics → lip-sync (the solo-address format benefits most) → "the Movie" (different name, same crew). The crew bible carries through every tier; renders are disposable, the IP is the asset.

---

## 10. PACKAGING & METADATA

- **Title formula:** curiosity-gap + number/time anchor. "Humans Went 200,000 Years Without Soap. How Did We Survive?" Lead with the gap only the video answers. Hold a 2nd variant (e.g. a climax-forward angle) as the Test & Compare alternate — YouTube optimises for watch-time, so the alternate targets a different audience-slice.
- **Description:** front-load the hook (first 2 lines show before "…more"); keyword-rich evidence-walk below the fold; chapters (first must be 0:00, ≥3, ≥10s apart). **Chapter timestamps must be derived from the ACTUAL render** (read each clip's duration, sum to section boundaries) — estimated timestamps misalign and are worse than none.
- **Tags:** 5-10 recurring channel tags + 5-10 per-video.
- **Visibility:** upload PRIVATE, configure title/thumbnail/description/chapters, THEN publish — never public-on-upload (auto-thumbnail + unconfigured = low CTR from the start).

---

## 11. KNOWN ISSUES & THE BUILD QUEUE (channel-relevant)

0. **✅ RESOLVED 01 Jul 2026 — P0 was a MISDIAGNOSIS; real fix was the style_suffix content (flat-cel → semi-realistic bright, §4/§6a). The canon-tag cut shipped too but was minor. Ep3 (MERCATOR) then rendered trio-tier. Left below for the diagnostic trail.** ★★ P0 — THE PROMPT-CONSTRUCTION FIX (highest; blocks all quality; banked 30 Jun from the Ep3 stills regression — full doctrine §6a).** Ep3's 213 stills rendered as near-identical photoreal beauty-portraits, NOT bright flat-cel curiosity-explainer. Two compounding faults, both in how the prompt string is built — the script's VISUAL lines were good. **This must be fixed and re-rendered before Ep3 ships, and before any further QQrew render.**

   **FAULT 1 — the channel `style_suffix` is not reaching the prompt.** Storyboard prompts ended in a 3-word author hint ("animated flat illustration"), not the channel's full suffix. So "NOT photorealistic, NOT 3d render, NOT realistic skin texture" — the channel's decisive lever — was absent, and flux-pro defaulted to photoreal.
   - **Localise (LAPTOP/BOX, read-only — DO NOT guess the file):** find where prompts are assembled for the Synthetic-Mode-A path and whether `style_suffix` is read there:
     ```
     grep -rn "style_suffix\|image_prompt\|canon" shared/modea_beats.py shared/recreation_pipeline.py | grep -iE "suffix|append|prompt ?=|\+ ?style|format\("
     ```
     Determine whether the suffix is appended in `modea_beats.py translate()` (the Synthetic→engine path QQrew uses) or only in the engine's CLI stills path (which QQrew may bypass). The symptom says QQrew's path never appends it.
   - **Required end-state:** every rendered `image_prompt` carries the FULL `channel.json style_suffix` (the cel-shaded + NOT-photorealistic block), appended by the pipeline, not hand-written per VISUAL line.
   - **Fix shape:** patch the prompt-assembly step (idempotent `patch_*.py`, laptop→git→box) to append `channel["style_suffix"]` to each prompt after the scene+canon. Verify in a fresh storyboard: `grep -c "cel-shaded" modea/storyboard.json` should equal the beat count.

   **FAULT 2 — canon eats the prompt (the structural one — §6a doctrine).** ~120 words of beauty-portrait Skeptic canon led every prompt; the beat (scene/posture) arrived starved at the tail; flux rendered the portrait, never the action. Plus the canon's own words pull photoreal.
   - **Fix A (canon string):** rewrite the Skeptic (and Driver, and future Brain) canon in `base_canon` from a ~120-word portrait to a **~20-word identity tag** — only what must stay constant for glance recognition (build, hair, wardrobe, signature expression), and STRIP the photoreal-coded beauty words ("smooth skin / soft delicate features / warm friendly oval face"). Example Skeptic tag: *"late-20s woman, blonde shoulder-length bob, tan camel jacket over white tee, layered gold necklaces, dry deadpan expression."*
   - **Fix B (prompt order):** the assembled prompt must read **[style suffix lead OR scene-first] → [SCENE/POSTURE/ACTION = the beat] → [short canon tag]**, so the beat gets flux's front-loaded attention. Confirm the order `modea_beats.py` produces and reorder if canon currently leads. (If the order is fixed in code, this is a one-line reorder in the prompt template.)

   **VERIFY BEFORE SPENDING THE FULL 213 (the new-lead probe, mandatory):** after the fix, render a **6-beat probe set** (cold-open / a crouch-at-diagram / a gesture/air-quote / a crew-absent wide / an in-world-number beat / arms-crossed punchline) at ~$0.18 total. Eyeball against the bar: **flat-cel (not photoreal), posture varied (not all headshots), in-world text/diagrams present, reads like Ep1.** Only if the probe clears does the full re-render fire. *(This also finally tests the §6 establishing-wides and in-world-number beats that Ep3 never rendered.)*

   **DIAGNOSTIC TO CONFIRM THE EP1-VS-EP3 THEORY (do first, free):** pull the soap (Ep1) and iceage (Ep2) storyboards and check (a) was `style_suffix` present in THEIR prompts? (b) how long was Driver's canon vs the Skeptic's 120 words?
   ```
   for p in soap iceage1; do echo "=== $p ==="; python3 -c "import json;s=json.load(open('qqrew/projects/$p/modea/storyboard.json'));print('suffix present:', 'cel-shaded' in s[0]['image_prompt'].lower());print('prompt0 len:', len(s[0]['image_prompt']))"; done
   ```
   If Ep1 HAD the suffix and Ep3 doesn't → a regression introduced between them (find what changed). If Ep1 also lacked it but looked okay → confirms Driver's shorter canon was the only thing saving it, and Fix A (short canon tag) is the load-bearing fix.

1. **P1 — AUDIO SEESAW (the continuous-voice fix).** Per-beat TTS → prosody re-attack every beat. Fix: synthesise beat-RUNS (sentence-group, then maybe section) as one Inworld call; Whisper-align to cut stills to word-timestamps. Decouples audio-unit from visual-beat. Portfolio-wide. (Peter's "multiple stills per beat" = right goal, the mechanism is fewer-longer-audio-segments.)
2. **P2 — Patch B: true-static native** in `_still_to_held_clip` (seeded by `reassemble_static.py`).
3. **P3 — Patch A: canon + render_policy auto-write at create** (removes manual injection).
4. **P4 — vision-judge JSONDecodeError** (silent candidate-1 fallback, portfolio-wide).
5. **P5 — channel-agnostic upload step + batch exit-gate** (category 27 for QQrew).
6. **P6 — `--unattended` still hits the stills gate.**
7. **Cast gaps:** Brain tokens lock + voice; Skeptic's distinct visual signature (the one real cast gap) + voice; in-show NAMES for all three (currently role-labels).

---

## 12. WHAT THIS CHANNEL BREAKS FROM CANONICAL (the Final-Hours bias)

The canonical craft that this channel breaks from was the Final-Hours/Sacred-Dawn brief — Final Hours was built first and infected the "channel-agnostic" docs. (As of 30 June it's been de-biased: that craft was moved into `_Final-Hours.md §11` and `ante-machinam.md` retired; the canonical now flags FH-derived rules `[CRAFT: FH-derived]` instead of stating them as law. QQrew is the channel that surfaced the bias.) This channel deliberately breaks:

1. **Beat granularity** (§6: 15-35 words / 5-12s) → **4-10 words / 1-3s. FAST.**
2. **Animatable foreground** (§7) → **no animation; stills are composed pictures, not frames to move.**
3. **Faceless default** (Part III) → **a visible recurring character.**
4. **Slow-dread register** (Part IV) → **bright, wry, propulsive.**
5. **Photoreal cinematic style** → ~~flat-cel illustration~~ **NO LONGER A BREAK (reversed 01 Jul, §4).** QQrew SHARES semi-realistic cinematic FIDELITY with Final Hours; it differs on REGISTER (bright/funky/high-key vs dread/candlelit) and CAST (recurring crew vs faceless). The moat is register + cast, never the art style. Flat-cel was an over-correction that read as a kids' webcomic.
6. **Ken-Burns floor** → **pure static, one notch leaner.**

KEEP (genuinely universal): header format, channel-matches-folder, numbers-spelled-out, one-VISUAL-per-beat, script-is-king, no-legible-text-in-stills, parse-verify-before-spend, safety_tolerance 5, base_canon auto-merge, positive-prompt-is-the-lever, recognition-is-the-retention-mechanic, nothing-publishes-unreviewed.

(Full catalogue: `NOTE_final_hours_bias_in_canonical.md`. The systemic fix: `CANONICAL_PATCH_de_final_hours.md`.)

---

## 13. STATUS

**SHIPPED 29 Jun 2026** — soap pilot live (static 7:22), @Q-Qrew branded + claimed. Channel #12 placed as a bet. **Next:** read 48h CTR+AVD → crank or park. Then P1 (audio) is the headline build before episode #2. Episode #2 should: deploy more wide-angle establishing shots (§6), keep the static default, reuse the locked thumbnail config, and spread the topic across the scope (not another history piece — go future or unreachable to teach the algorithm the channel's breadth).
