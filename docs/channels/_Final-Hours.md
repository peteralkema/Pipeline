# Final Hours — Channel Doctrine
*The single consolidated channel reference for Final Hours (@FinalHours_history). Load this — with the `_`/`__` system docs — on any Final Hours session.*
*Consolidated 11 June 2026; **updated 18 June 2026** (the 10-video maritime/disaster batch session: real retention data pulled, the two-cliff diagnosis confirmed, the cold-open architecture rebuilt around it, the channel thumbnail block added, the batch shipped through `run_batch.py`).*
***Updated 30 June 2026 — THE ANTE-MACHINAM ABSORPTION (the de-bias).** `ante-machinam.md` was Final-Hours/Sacred-Dawn craft wearing a `__` "channel-agnostic" label — the single biggest structural flaw in the doc set: it kept pulling every other channel's prompting toward dread-slow-faceless-photoreal. It is now **RETIRED.** Its genuine pipeline MECHANICS graduate up into the canonical reference (the Constitution proper, the two modes, the pre-flight); its CRAFT — which is FH craft — is absorbed here as **§11 (The Craft Canon)**. Two ante-machinam "Constitution" items (beat granularity, animatable-foreground) are relabeled on the way in: they were never pipeline physics, they are FH craft, and QQrew (static, no foreground motion, 5-word beats) is the proof. This doc is now self-contained; nothing here points at ante-machinam any more.*
*[Current-reality flags: the channel runs **long-form 10–16 min** (city-catastrophe 20–32 min); Peter is in **The Hague**; the **Hetzner box is live**; the **face-never-resolved / absence-as-subject register won the retention test** and is confirmed by the Mary Celeste data; **Success Coach is out of scope** for this doc. The 31 May "live state" table in §7 is now historical — current live state is §7A.]*

---

## 1. Identity

- **Name:** Final Hours · **Handle:** @FinalHours_history (Brand Account under peteralkema2@gmail.com).
- **Created:** May 2026. **Status:** live, **primary** channel. Working OAuth/upload on the shared Production token (non-expiring).
- **Format:** faceless; Inworld **Victor** narration; photoreal-painterly cinematic stills (fal Flux-pro) animated by fal/Kling on the front beats with a free Ken-Burns floor on the rest; mournful drone-and-strings bed (curated `music/` folder, 3 random tracks crossfaded). Long-form 10–16 min (city-catastrophe sub-series 20–32 min).
- **Niche:** AI-recreated long-form history — *"the last hours of people and places history remembers."*
- **Repo:** `final-hours/`. **Header/folder trap:** the script header says `channel: final_hours` (underscore); the orchestrator auto-resolves that to the `final-hours/` folder. **BUT `run_batch.py` does NOT do that resolution** — its `--channel` flag must be the literal folder name `final-hours` (hyphen), or it exits "channel.json not found." (Banked 18 June.)

---

## 2. Thesis

Final Hours is **not a "history channel."** It is a **dread-and-recognition recreation pipeline** — a system for taking one human story (or one human *absence*) inside a catastrophe and rendering it in slow cinematic photoreal form for a few dollars a video. The frame is consistent: **the camera stays with one named (or deliberately unnamed) human while history happens around them.** Hartley on the deck, the families at the Herculaneum boathouses, the three keepers gone from the Flannan light. The catastrophe is the *setting*; the dignity-or-bewilderment of one person — or the shape of the hole they left — is the *subject*.

Three things make it defensible against trivial format-cloners:

**The rulebook.** An accumulating per-channel list of caught spell-breakers — anatomy, gravity, location/instrument drift, character-consistency failures. Every spell-breaker caught in stills review becomes a permanent negative rule. ~31 Final Hours rules over ~21 universal. Universal rules prevent universal failures; channel rules enforce period discipline (Edwardian uniforms render unreliably → plain black; one ship per frame; engravings illegible → frame obliquely).

**The canon mechanism.** A per-video block of named descriptors (`{hartley}`, `{band_deck}`) for anything recurring in 3+ shots. **[CLARIFIED 18 June] This is a channel-level `base_canon` + rulebook mechanism, NOT a per-script block in the `.md` file.** The script-file contract (the header + beats format, now in the canonical reference and restated in §11.5) is *header + beats, full stop* — there is no `## CANON` section syntax the parser reads. Cross-shot consistency in authoring is carried by **scene-canon discipline written into the VISUAL lines** ("the lamp room," "the iron spiral stair," repeated with the same concrete descriptors), faceless framing, and **object-substitution** for recurring people (the coats on their pegs, three chairs, the trimmed lamp). This is why the absence-as-subject topics render cleanest — the people are mostly out of frame, so empty rooms and objects carry the continuity. (Confirmed on the Flannan Isles build; the Yellowstone/Prehistoric template — no canon block — runs clean through the same batch path.)

**The beat architecture.** Authored against the **Constitution** (genuine pipeline mechanics, now in the canonical reference: every beat carries words; header is metadata and `channel` matches the folder; spell out numbers in narration; one VISUAL per Mode A beat; lock the script first) **and the FH craft-grain rules in §11** (beat granularity ~5–12s spoken, ~15–35 words, hard ceiling ~55; every beat carries an animatable foreground subject — *FH craft, not pipeline physics; see §11.1–11.2*). Beats sized to narration; assembly holds each clip to audio-measured duration.

Tools (fal Flux + Kling, Inworld, Whisper, ffmpeg, rembg) are commodity. The moat is the three layers above + accumulated production judgment.

---

## 3. Economics

- **Cost per video:** now governed by the **tiered render / Kling-count cap** (canonical §5.2). The animate step routes per beat: first **N** beats Kling (~$0.42/clip), the rest a free Ken-Burns floor. Default N=40 → ~$16.80/video. **The 10-video batch ran at N=2** (`--kling-count 2`) — a ~$3.84/video cold-open-only motion hook, the "cheap, dial up on signal" setting. The decision banked: **start cheap (front-2), dial Kling up once a curve proves motion earns it.**
- **Comparison:** Chloe vs History (closest format peer) runs an estimated $2,000–5,000/video. Dud-tolerance is the whole strategy — one breakout pays for many. Break-even is a few thousand monetised views (history RPM ~$5–8).
- **Portfolio logic:** the pipeline is format-agnostic; per-channel canon + rulebook compound independently.

---

## 4. Topic principles

Three filters:
1. **One human story (or absence) inside a larger catastrophe** — not "the Titanic," but "Wallace Hartley on the Titanic." Not "the Mary Celeste," but the ten people present only by their absence. The signature framing.
2. **Dread-and-dignity register** — no action, conspiracy, or breezy explanation. Mournful, considered, slow. Sensitive material (cannibalism, falls, mass death) is named **once, at distance, on the human choice** — never the detail. If a topic doesn't fit the register, it's wrong regardless of how interesting.
3. **Render-friendly visual range** — maritime/island/Pompeii/Arctic/desert all now well-supported. Absence topics (empty ships, abandoned rooms, vanished colonies) are the *easiest* to render cleanly because they lean on objects and empty space, not consistent human figures.

The "final hours" framing is the emotional anchor and should be visible in the title.

**The winning title grammar (confirmed by the Mary Celeste data, §7A):** the **two-sentence mystery/absence hook** — an event/normalcy sentence + an absence/wrongness sentence. "He Waved Goodbye in November 1872. They Never Came Back." / "Three Men Tended This Light. One Night in December 1900, They Vanished Without a Trace." The whole batch is written to this grammar.

---

## 5. Operating principles (banked across videos)

- **Three attempts is the line.** Reshot twice and still misbehaving = a learned model prior you're fighting. On attempt three, **reframe the concept**, don't negate the prior harder.
- **Canonise anything in 3+ shots** via scene-canon descriptors + object-substitution in the VISUAL lines (see §2 clarification).
- **Rulebook prevents universal failures; canon enforces per-video continuity.** Don't mix the layers.
- **Auto-fallback makes unattended rendering possible.** Kling content-policy refusals silently downgrade to held-still ffmpeg clips and continue.
- **People are the emotional core**, but **absence is its own subject** — empty rooms, object-substitution, and "name the absence" narration carry the topics where everyone is gone. Don't use broad anatomy negatives ("deformed hands") — they make models avoid people entirely. Use *specific* spell-breakers + a positive `people_directive`.
- **Wide establishing shots fight the documentary prior** — reframe to close detail (hands on strings, the coat on the peg, the lamp in lantern light). Detail keeps the camera with the human experience.
- **Image models can't render small legible text.** Frame text obliquely/illegibly; never rely on specific words. (This is also why thumbnail text is a deterministic Pillow overlay, never baked by Flux — see §6A.)
- **Attribution discipline is the moat.** Where folklore has accreted onto a real event, **name the legend on screen and set it against the record** — Flannan's half-eaten-meal/overturned-chair myth shown as legend vs the NLB's tidy kitchen; Franklin's dismissed-then-vindicated Inuit testimony; the Carroll Deering's hoax bottle named and dismissed. This both protects credibility and writes its own comment-bait.
- **Flux-pro over Seedream** for faces; **fal `safety_tolerance:"5"`** on the Flux call (default safety silently returns ~7KB black-PNG placeholders).

---

## 6. Distribution principles (banked)

- **Retention-curve *shape* over all other metrics.** Studio AI summaries on small samples are noise; check at 100+ views minimum. The curve shape (where viewers drop, where they re-engage) is the real diagnostic.
- **The two universal cliffs (confirmed 18 June on real FH data, §7A):** (1) the **2–3% cliff** — roughly the first 30–40 seconds, where the cold open stops being a scene and starts explaining; (2) the **mid-video cliff ~50–60%**, where the camera leaves the human for a separate explanation/forensics act. Both are now designed against (§8A).
- **Cross-promote known fires, not new ones.** Let the algorithm cold-test each video 48h before pushing to owned audiences.
- **Format competition is mostly an illusion on a recommendation platform.** Same lane = tailwind if packaging is clearly different. Differentiate by *register* (dread vs vlog) and *length*.
- **Schedule for 01:00 CET** (~19:00 US Eastern) — start of US prime evening. The batch scheduler sets this via `--publish-start <ISO+tz> --publish-interval-hours`.
- **Topic clusters beat topic variety** — the batch is deliberately clustered (maritime/island vanishings + confined slow-catastrophe), because clusters compound algorithmically far more than variety.
- **Ship first, but learn from one before betting on twenty.** The standing tension: the batch shipped all ten before any first-48h curve came back. The discipline going forward is to read ep-1 data against the Mary Celeste baseline before authoring the *next* batch.

---

## 6A. The thumbnail system (Final Hours specifics — banked 18 June)

The automated thumbnail pipeline (canonical §6) is now wired for Final Hours. Key facts:

- **The channel `thumbnail` block was MISSING until 18 June.** Without it, convergence's `_maybe_thumbnail()` soft-skips (the expensive half — Flux candidates + Sonnet selection → `thumbnail_still.png` — still runs; only the final Pillow text overlay is skipped). **The FH block is now in `final-hours/channel.json`** — modeled on the locked Prehistoric block but rewritten for the FH register: `low_silhouette` composition, faceless atmospheric `candidate_prompt_suffix` (dark lighthouse / empty ship / frozen wreck / eruption-across-a-bay, NOT the Prehistoric catastrophe-with-silhouette), left gradient scrim `{side:left, width:0.42, opacity:0.55, feather:0.7}`, near-white title `[245,240,235]`, **cold steel-blue subtitle `[150,240,205]`→ actually `[150,180,205]`** (vs Prehistoric's amber — the FH palette is mournful grey-blue), full-brightness image (`darken_factor 1.0`, scrim does the contrast), Anton font.
- **`make_thumbnail.py` needs the FULL project path** — `--project final-hours/projects/<name>`, NOT the bare slug (the `proj_paths` auto-prefix quirk; bare slug → "Still not found"). Flags: `--project --channel --title --subtitle` (optional `--still`/`--shot`/`--out`).
- **Thumbnail-still segmentation does NOT run on FH** — `_segment_foreground` (rembg poke-through) only fires on `centered_subject` composition; FH is `low_silhouette`, so it's skipped. (A blue-box artifact seen 18 June was a **stale pre-fix PNG**, not a bug — regenerating cleared it.)
- **Per-project `thumbnail.json`** `{subject,title,subtitle}` travels as the `<name>.thumb.json` sibling of each script. The thumbnail headline is a SHORT punchy string, deliberately different from (and complementing, not echoing) the long SEO video title — image carries the "what," title the "why-click."
- **Free regeneration** (no re-render): `make_thumbnail.py` composites text onto the existing `thumbnail_still.png`. The regen-all loop reads each project's `thumbnail.json` for title/subtitle.
- **Already-uploaded videos need a manual/API thumbnail push** — generating `thumbnail.png` locally does NOT attach it to a video already uploaded to YouTube (needs `thumbnails.set`). Carroll Deering uploaded pre-fix → its thumbnail is uploaded by hand in Studio.

---

## 7. Live state — historical (31 May, retained for reference)

| Video | Status | Signal |
|---|---|---|
| Pompeii v2 | Live (28 May) | 51% retention — early high-water mark. |
| Anne Boleyn | Live (29 May) | Cross-promo contaminated the algorithmic read. |
| Hartley (Titanic) | Live (30 May) | ~17% retention; CTR ~2.15%. "He Kept Playing." |
| Hindenburg | Live (30 May) | CTR 2.12%; AVD ~34s = 11.3% retention. |
| Pudding Lane | Live (1 June) | First face-never-resolved anonymous protagonist. "She Wouldn't Jump." |
| Troy | Live (16 June) | 154-beat ~25-min. (Now confirmed a retention catastrophe — see §7A.) |

---

## 7A. Live state & retention data (18 June 2026 — CURRENT)

**Channel scale (23 days old):** ~7 subs, ~633 views, 11 videos. Most per-video data is below the 100-view noise floor — read curve *shape* on the two videos that clear it, not the view rankings (which just track which got pushed).

**The breakout — Mary Celeste** (`Bn4uKhO7Xo4`, "He Waved Goodbye in November 1872"): 192 views (the only video over 100), **207s AVD** (highest), **631 watch-minutes** (3× the next), and **2 of the channel's 7 subs** came from it alone. It is the anonymous-protagonist / absence-as-subject topic the doctrine always flagged as the truest FH fit. **This is the baseline every new video is read against.**

**Curve shape (the diagnosis):**
- Mary Celeste: **2–3% cliff** 85%→58% (first ~30s), then a respectable ~24% plateau through the mid-section, then a **second cliff ~52–61%** (23%→14%) at the explanation act. `relativeRetentionPerformance` ~0.3–0.4 — i.e. it WON on **packaging + topic**, not retention craft (it retains *below* median for its length). This is the channel thesis stated back: packaging beats production.
- Troy (`sSgWM7OA4mo`, 22-min named-ensemble myth): same 2–3% cliff but no plateau — falls to ~5% by the 3-minute mark and flatlines for the whole rest of the runtime. The contrast (absence-mystery vs sprawling known-ending myth; 16 min vs 22 min) argues hard for the Mary Celeste register and tighter length.

**The register verdict:** anonymous / absence / genuine-mystery / real-history / tighter-length beats named-ensemble / known-ending-myth / sprawling-length. The face-never-resolved register is confirmed, not just adopted.

**AVD ranking (cleaner than views at this scale):** Mary Celeste 207s > Gustloff 187s > Pompeii 155s > Tenerife/KLM 136s > … > Hindenburg 74s > Hartley 70s. The slow contemplative absence/confined-disaster topics top it; the fast/violent/short ones bottom it.

---

## 7B. The 10-video batch (shipped 18 June via `run_batch.py`)

Ten matched `<name>.md` + `<name>.thumb.json` pairs, `--channel final-hours --kling-count 2`, scheduled nightly 01:00 CET **20–29 June 2026**. Clustered on the two registers the data rewarded.

**Maritime / island vanishings (the Mary Celeste lane — the spine):**
1. **Flannan Isles** (1900) — the exemplar; three keepers vanished, the cleanest Mary Celeste twin. *Lead-tuned; ended up alphabetically at slot 2.*
2. **Franklin Expedition** (1845) — two ships, 129 men; absence-at-scale; Inuit-testimony attribution thread.
3. **SS Waratah** (1909) — vanished liner, 211 aboard; anchored on Claude Sawyer, who left over a dream.
4. **Carroll A. Deering** (1921) — ghost ship, crew gone, food on the stove. *Slot 0 — first to publish (20 Jun, ID `odvRcUYLP50`).*

**Confined slow-catastrophe single-fate (the Pompeii/Gustloff high-AVD lane):**
5. **Herculaneum boat houses** (AD 79) — the families who waited for boats; Pompeii cluster.
6. **Pliny the Younger / Vesuvius** (AD 79) — named witness; the only eyewitness account; Pompeii cluster (cross-references Herculaneum in its close).
7. **Donner Party** (1846) — the shortcut, the snowbound camp; cannibalism handled at distance.
8. **Triangle Shirtwaist Fire** (1911) — locked doors, ~18 minutes; the falls handled at distance.

**Land / found-record absence (variety within the theme):**
9. **Roanoke** (1587) — the lost colony; John White returns to "CROATOAN."
10. **Lady Be Good** (1943) — bomber found preserved after 16 years; crew walked into the Sahara; diary as recurring spine.

**Cross-cluster cross-promotion is built in** — Herculaneum and Pliny seed each other; every close ends with a sequel hook into "other silent ships and empty rooms."

---

## 8. Video-direction principles & candidate topics

**Choosing the next video:** build a topical cluster around whichever video shows life; use scene-canon/object-substitution from inception; apply the banked pacing discipline (distribute sensory density across 3+ locations, cap shots per scene canon ~10, audit voiceover duration with `ffprobe` before finish).

**Candidate topics for the NEXT batch** (pick on the first-48h data from this batch):
- Second maritime-vanishing wave if the cluster fires: the Octavius, the Ourang Medan, the Eilean (other lighthouse/keeper vanishings), the *Marie Céleste*-adjacent abandonments.
- Pompeii cluster deepening if Herculaneum/Pliny retain: the House of Menander, the Pompeii children at the Stabian baths, the Villa of the Mysteries.
- Arctic/expedition cluster if Franklin/Lady Be Good fire: Shackleton's *Endurance*, the Greely expedition, the Karluk drift.

---

## 8A. The cold-open architecture (rebuilt 18 June against the two cliffs)

Every batch script is built to this shape — the direct counter to the §6/§7A cliffs:

- **Cold open = ~8 beats of escalating *wrongness*, ~30–40s.** Hook line → straight into the scene, present-tense, the subject already in motion. **NO date/place/biographical throat-clearing in the first ~30s** — identity and context braid in around beats 4–5, *after* the scene has its hook in. (The Craft Canon's §11.4 IV.1 already named this: "a context block over ~45–90s without renewing tension causes drop-off.")
- **Kling on beats 1–2 only** (the N=2 budget) — spent on the two most arresting, faceless, motion-rich, drift-safe spectacle shots in the script (the night wave, the dark tower, the eruption column), landing exactly on the 2–3% kill zone.
- **The body holds the human thread** — recurring spine object planted early and harvested at the climax (Flannan's coat on the peg; Lady Be Good's diary; the Deering's set sails); clock-anchored dread; one human (or one named absence) present *through* the explanation, never a separate forensics act that abandons them (the mid-cliff fix).
- **Close:** end on the image → moralised closer aimed at the present-day viewer → comment-bait question → sequel hook into the cluster.
- **Length target: ~10–13 min (~45–55 beats)** while on cheap front-2 Kling and still proving the cold-open fix; dial length up once a curve confirms it holds.

---

## 9. Channel-specific files & quirks

- `final-hours/channel.json` — voice Victor, `style_suffix`, `music` block, **now the `thumbnail` block (added 18 June, §6A)**. `rulebook.json`, OAuth (`token.json`/`client_secret.json`), `projects/`, `batch_inbox/`.
- **OAuth:** working under peteralkema2@gmail.com on the shared **Production** token (non-expiring — the old 7-day testing-mode expiry is retired). Known `auth.py` CLIENT_SECRET/TOKEN_FILE variable-swap bug (legacy; the shared `upload_episode.py` path is the live one).
- **`run_batch.py` channel flag:** literal folder name `final-hours` (hyphen), NOT `final_hours` (it skips the orchestrator's hyphen/underscore resolution).
- **`make_thumbnail.py`:** full project path required (§6A).
- **Batch inbox:** `final-hours/batch_inbox/`, matched `<name>.md` + `<name>.thumb.json` pairs; a `.md` with no sibling thumb is skipped. `--plan` is zero-spend; verify scripts parse first (`parse_script.py <md> --json … --json-full …`).
- Final Hours is the **Mode-A-only reference signature** — `audio → modeA → convergence`, no Mode B leg. Must keep falling through the orchestrator unchanged as features land.

---

## 10. Open items & watch-list (top of next session)

1. **Read the first-48h CTR + AVD on the batch** as videos publish (Carroll Deering first, 20 Jun) — via NexLev `get_my_video_analytics` + `get_my_audience_retention`, **against the Mary Celeste baseline** (192 views / 207s AVD). Does the rebuilt cold open beat the 2–3% cliff? This decides the next batch.
2. **RUNTIME UNDERSHOOT — open flag.** Carroll Deering rendered to **6:15**, well under the ~10–13 min (~45–55 beat) target. Check the duration on the next 1–2 as they land; if they're all ~6 min the script-to-runtime is undershooting and needs diagnosis before more publish. (Possible causes to check: beat count actually parsed vs authored; per-beat audio shorter than the ~14s estimate; a truncation in convergence.)
3. **Carroll Deering thumbnail** — upload the corrected `thumbnail.png` by hand in Studio (`odvRcUYLP50`) before it publishes 20 Jun (only video that uploaded pre-thumbnail-fix).
4. **Confirm the FH `thumbnail` block saved intact** — a heredoc mangled on paste during the session; the keys list confirmed it landed, but eyeball it: `python3 -c "import json;print(list(json.load(open('final-hours/channel.json'))['thumbnail'].keys()))"`. (Also reconcile the subtitle colour note in §6A — intended `[150,180,205]` steel-blue.)
5. **Stragglers check** — the per-project `substrate`/`overlay` status loop tells which videos cleared the thumbnail step pre-fix (need manual regen) vs which self-heal on the new config.

---

## 11. The Craft Canon (absorbed from the retired `ante-machinam.md`, 30 June 2026)

*This is the authoring craft — what makes a Final Hours script LAND, as opposed to the mechanics (now in the canonical) that make it RUN. It was the bulk of `ante-machinam.md`, mislabeled "channel-agnostic"; it is Final Hours / Sacred Dawn craft, and it lives here now. Every principle below was pressure-tested in a shipped FH video (Pudding Lane, Hindenburg, Pompeii, Mary Celeste). Sacred Dawn's overlapping lessons (the Watchers) live in `_Sacred-Dawn.md`; where a principle is genuinely portable, the canonical's craft-menu may offer it as an option — but here it is FH doctrine, not universal law.*

**Spine in one sentence:** *win the click with the package, hook the first sixty seconds, hold the body with recognition and a recurring beat, land a close that converts a viewer into a subscriber.*

### 11.0 — The de-bias note (why two of these were NOT mechanics)
`ante-machinam.md` put **beat granularity** and **animatable-foreground** in *the Constitution* — "the physics of the pipeline," "a physics constraint, not a style preference." That was the bias in its purest form: FH craft dressed as a universal law, and it pulled every other channel's authoring toward FH's grain. They are **not** physics. QQrew runs true-static (no foreground motion ever needs to animate) at 5–6 words/beat and breaks both without the pipeline caring. So §11.1 and §11.2 are **FH craft** — load-bearing *for this channel's photoreal-Kling-cinematic look*, irrelevant to a flat-cel static channel. Author to them for Final Hours; do not export them as law.

### 11.1 — Beat granularity (FH craft — was Constitution §6)
One beat → one still → one ~5-second animated clip, slow-filled to the beat's measured spoken duration. Stretch up to ~2–3× is invisible; past ~4× it reads as dead, stretched video (the Sacred Dawn launch confirmed it — a 52-beat / 17.7-min cut averaged ~4× and read as slow motion). The fix is never in the assembler — **it is authored, by writing shorter beats.** Author each beat so its spoken words run ~**5–12 seconds**, hard ceiling ~**15s (~55 words)**. Punchy single-sentence lines earn their own short beat. The pipeline measures true duration with Whisper at the audio gate; these numbers plan the *grain*, not the sync.

| Spoken words | ≈ sec @150 wpm | Stretch over ~5s clip | Verdict |
|---|---|---|---|
| 8–18 | ~3–7 s | ~1–1.5× | Ideal motion |
| 18–35 | ~7–14 s | ~1.5–3× | Good; the workable default |
| 35–55 | ~14–22 s | ~3–4× | Acceptable only for a deliberately still, weighty beat |
| 55+ | 22 s+ | >4× | **Split it.** Two beats, two visuals. |

A 25–31 min episode at this grain ≈ 110–160 beats. *(Caveat banked 17 June: runtime is beat-floored, not words-only — the Ken-Burns minimum hold stretches short beats, so real runtime ≈ beat count × ~14s; a words-only estimate undershoots. Toba: 88 beats → 20.7 min. And the wpm floor itself is wrong at length — see §11.4 IV.6.)*

### 11.2 — Author for motion: the animatable foreground (FH craft — was Constitution §7)
Kling can only move what is in the frame. A wide hills-and-valley shot has no foreground subject, so it animates as a slow zoom across a postcard — technically motion, emotionally dead. A beat whose still carries a **foreground subject in mid-action** converts into real movement: the blade turns and catches the light, the hand drives the hammer, the wave crests. You cannot fix an inert clip at the animation gate — there is nothing to move; the fix is authored, upstream, in the VISUAL line, *before the still renders*.

The one-line test before lock: **"What in this frame moves, and is it close enough to see it move?"** If the honest answer is "a slow drift across scenery," rewrite it. Wide establishing shots stay allowed but become the **minority**, kept short (a ~5s wide stretched ~2× is a fine breath; stretched ~4× it's the dead postcard).

**The two goals (clean stills vs. motion) only fight if you reach for the wrong subject.** A clear-faced figure walking at camera is full of motion *and* full of drift. Choose foreground subjects that are inherently animatable *and* inherently drift-safe — three classes, author the bulk of every episode from these:
1. **The body, without the face.** A figure from behind, low-angle at the legs, or as a silhouette is faceless (no drift) yet a huge moving subject: the giant's foot into wet clay, a massive hand closing, a robed back turning.
2. **Objects and hands.** Highest motion-conversion, lowest drift. Flux renders a single object or a pair of hands cleanly; Kling animates them vividly: the hammer striking sparks, the blade quenched and hissing, fingers tracing stars, a cup trembling as footsteps approach.
3. **The environment as an active force.** Catastrophe-as-environment as *motion in progress*: not "a flooded valley" but "the water surges across the threshold and climbs the loom's legs."

**The drift dial, not switch:** foreground-action up, face-resolution down, both at once — faces resolved-away, one figure not three, objects and partial bodies over full clear figures. **Embed the motion in the VISUAL line** as a verb the animator can perform in ~5s. *(On an all-Ken-Burns FH lane this is moot — but it stays correct whenever Kling is on.)*

### 11.3 — Writing the VISUAL line (so stills come out clean on the first pass)
Production patterns that make Flux render reliably for the FH photoreal look. *(Several of these also appear operationally in §5; this is the craft statement.)*
- **Faceless by default; resolve a face only when you must.** When identity is unknown/marginal/anonymous, never resolve the face — frame from behind, in profile, silhouetted, in deep shadow, soft focus, turned away. Mirrors the dignity register **and** eliminates Flux's hardest drift problem. Foreground a face only when the audience must bond with one specific, named, documented person.
- **Build canon around places, not people.** A scene canon ("the lamp room," "the citadel at golden hour") renders consistently across twenty shots; a character canon drifts. Get variety from angle and detail within a locked location.
- **Substitute objects for groups.** Flux fails on three-plus figures. A family becomes an empty table, four settings, one chair pushed back; a crowd becomes a single abandoned object.
- **Empty rooms carry meaning and render perfectly** — the empty landing after the people ran, the wall after the death.
- **Fire (and any catastrophe) is environment, not subject.** Write what the fire *does* ("orange glow pulsing on the wall," "smoke rolling across the ceiling"), never a close-up of flames consuming a person. Same for serpents, eruptions, drownings — at distance.
- **Period accuracy is the watermark.** Write the explicit guard into the VISUAL ("the medieval pre-Wren cathedral, NOT the modern dome").
- **Image models cannot render legible text.** Frame engravings, signs, document text obliquely, in shadow, or out of focus. If specific text must be legible, that is a Mode B card's job, not a still's.
- **Distribute sensory detail across locations.** Six details stacked in one room → twenty near-identical shots and breathless pacing. Spread the richness across kitchen, lane, river, rooftops.
- **Aspect:** ask for `landscape_16_9` explicitly (the model defaults narrower); flag 4:3 output.

### 11.4 — The retention canon (what makes the writing land)

**IV.0 — The two truths everything serves.**
- **CTR is won by the package; distribution is won by retention.** Title + thumbnail win the click; AVD and the first-48h curve decide whether the algorithm pushes the video cold.
- **Recognition is the retention mechanic.** Studio lean-in spikes land at *personal recognition* — a named, specific, physically-precise thing the viewer holds in their body. Vague beats get no spike; named vivid specifics do. The most transferable lesson; it reappears below.

**IV.1 — The first sixty-to-ninety seconds (the gate).** Run every cold open through this.
- **Drop the viewer inside a scene, present-tense and sensory — never brief them.** "Feel it before you see it. The water trembling in the cup." Never "in this video we'll look at…"
- **Three concrete anchors in the first ten seconds** — date, place, person, amount, object, number; falsifiable, front-loaded. (Year-only acceptable for deep antiquity.) If you can't find three, the topic may be wrong for the channel.
- **A named anchor within fifteen seconds** — the specific human or named place the viewer commits to following.
- **Announce the dramatic arc in the first minute** — [date/place locked] + [scale in concrete numbers] + [stakes promise explicit] + [tease of the worst still to come]. The single biggest separator between a 1.1M and a 600K video. The tour-guide open is the failure mode.
- **Deliver the title's contract by ~20s — then keep delivering tension through two minutes.** A context block over ~45–90s without renewing tension causes drop-off (Hindenburg → 11.3%; Pompeii interleaved → 51%). Audit 0:20–2:00; gaps over ~45s get a tension beat woven in or cut.
- **Front-load the payload — compress the runway.** Reach a visceral, concrete payload fast; don't throat-clear with meta.
- **Plant the recurring spine and the emotional thesis in the open** — name the recurring payoff beat, seed the thesis you'll harvest at the close.
- **Foreshadow pivot at ~40–55s; cliffhanger at ~60s, cut mid-thought.**

**IV.2 — Through the body.**
- **Sensation, not description** — supply the senses the image can't: smell, texture, sound, weight, temperature. Never "she felt afraid." Makes AI visuals feel lived rather than illustrated.
- **Pace-aware sensory density — distribute across locations.** If more than three details land in one location, redistribute. (Confined-location stories where the confinement *is* the weight are the deliberate exception.)
- **Recognition as the retention mechanic** — land beats on one universal, physically-precise, vivid specific. Engineer those moments; don't let the recognisable thing pass as a flat mention.
- **A recurring payoff beat as spine** — a repeated resolution the viewer learns to anticipate turns disconnected beats into one running bit. Anticipation is retention.
- **Clock-anchor the dread** — specific times before specific events; tighten intervals as the catastrophe nears. (Time-passing-with-nothing-happening is a short weighty line now, not a wordless hold — see the canonical Constitution.)
- **Name the surrounding humans — and name the absence when the record lost it.** Named reads as documented; anonymous reads as generic. When the record kept no name, never invent one — name the absence as a refrain, three times. This is the dignity register and it unlocks the face-never-resolved production win.
- **Narrator-to-viewer irony at act transitions** — once, the narrator steps outside the frame to name what the viewer knows that the characters don't. A scalpel, not a tic.
- **Plant seeds early, harvest late** — specific facts dropped as incidental early, returned to with weight at the close. Plant only facts that gain weight when revisited.

**IV.3 — The close (where a view becomes a subscriber).**
- **End on the image, then reflect — sequential, not contradictory.** The final beat is one image held by a weighty line (a ring, a clock, ash, the ark on grey water). Then the most-missed move: a **moralised closer that reflects the event back at the present-day viewer** (the 1.1M London 1300: "we're still living in the world they created… cities survive"). The viewer leaves holding something they didn't have at the start — that converts a watcher into a commenter/subscriber.
- **The over-deliver must accelerate, not decelerate.** Exceed the promise only with your *strongest* material — one killer bonus, then stop. For a film, accelerate into the sequel hook.

**IV.4 — Packaging is craft (title + thumbnail + comment).**
- **Lead the package with tension, not warmth — the then-vs-now / transgression hook.** "London 1300: The Apocalypse Happened in 1348" beats "Pompeii: Before the Disaster." Lead with the tension, stakes, or question.
- **Title and thumbnail complement, not echo.** Image carries the *what*; title carries the *why-click*; never the same nouns. (FH winning grammar: the two-sentence mystery/absence hook — see §4.)
- **Comment-bait built into the subject, not bolted on.** A recognition-rich topic writes its own pinned comment. Thumbnail-asks → video-stages → comment-harvests is one loop.
- **The act structure is a retention scaffold** — clear acts with forward-pulling act-turn hooks; the viewer always knows there's a destination.

**IV.5 — The narrator is a retention device.** A characterful, intimate narrator is itself a reason to stay, and a differentiator in a niche full of flat AI TTS. FH register: Victor's mournful dread. Write *to* the voice; direct address ("you know them, even if no one ever told you this part") creates presence — deploy at the open, the act seams, the close.

**IV.6 — Production realities that shape the writing.**
- **Acknowledge the recreation once, early, single line** — a museum-placard sentence naming real sources ("recreated from the household accounts, the British Library letter, and the parliamentary investigation"). Specific, never apologetic, never a tech disclaimer. For attribution-sensitive material it doubles as the fidelity guard (see §5).
- **Inworld renders faster than you plan — write long.** Measured ~165–178 wpm at the reverent channels (NOT the old 120 wpm floor, which overshot the two features by ~30 min). Author a long piece TO a target at ~165–178 wpm — a 90-min feature ≈ 15,000 words, not ~11,000. Doesn't affect sync (Whisper measures real audio); does affect runtime. **But runtime is also beat-floored** (the ~14s/beat Ken-Burns hold), so a words-only estimate undershoots short scripts. Verify completeness by `final_video.mp4` duration == `voiceover.mp3` duration, NEVER against the estimate.

**IV.7 — The pre-lock audit table.** Before any FH script is locked, fill this; any "weak/missing" → revise.

| # | Principle | Status |
|---|---|---|
| 1 | Dropped inside a scene, present-tense + sensory open (not "in this video") | |
| 2 | Three concrete anchors in 10s; named anchor by 15s | |
| 3 | Dramatic arc announced in the first minute (scale + stakes + tease) | |
| 4 | Title contract delivered by ~20s AND tension sustained through 2:00 | |
| 5 | Payload front-loaded; recurring spine + thesis planted in the open | |
| 6 | Foreshadow pivot ~40–55s; cliffhanger ~60s cut mid-thought | |
| 7 | Sensation not description, distributed across locations | |
| 8 | Recognition beats — one vivid universal/famous specific per key moment | |
| 9 | A recurring payoff beat as spine | |
| 10 | Clock-anchored dread, tightening intervals | |
| 11 | Surrounding humans named; absence named as refrain when applicable | |
| 12 | Narrator-to-viewer irony at ≥1 act transition | |
| 13 | Seeds planted early, harvested late | |
| 14 | End on the image, then moralised closer reflecting at the present-day viewer | |
| 15 | Over-deliver accelerates (or ends clean) — no trailing leftovers | |
| 16 | Package: tension/transgression hook; title & thumbnail complement not echo | |
| 17 | Comment-bait built into the subject (planted → asked → pinnable) | |
| 18 | Recreation acknowledged once, early, single line | |
| 19 | Written to target at ~165–178 wpm (not the old 120 floor) | |
| 20 | Constitution check (canonical): no wordless beats; numbers spelled out; ≤~55 words/beat; animatable foreground per beat | |

### 11.5 — The FH positioning brief (was ante-machinam Part V.1)
Most of this already lives in §2 (thesis) and §4 (topic principles); held here for completeness. **Premise:** the last hours of one human story inside a larger catastrophe; the camera stays with one named (or deliberately unnamed) human while history happens around them. **Mode A only. Register:** dread-and-dignity, mournful, present-tense third-person witness; never action/mystery/conspiracy. **Runtime:** long-form 10–16 min; city-catastrophe sub-series 20–32 min (the 7-min grid is superseded). **City sub-series grammar:** title `[Place] [Year]: [doom hook] (AI Reconstruction)`; the six-beat hook; callback frame (open on the catastrophe image = thumbnail, return near the end); recreation acknowledgment woven as "what's in the ground." **Anonymity-as-refrain** and **the moralised closer** are the most-missed beats. **Channel header trap:** `channel: final_hours` → resolves to `final-hours/`; `run_batch.py --channel` needs the literal `final-hours`.

---

*Maintained by Peter + Claude. Operational how-to lives in the canonical reference (`_PIPELINE-CANONICAL.md`); the wider operation lives there too. **Craft now lives HERE (§11) — `ante-machinam.md` is retired.** This doc carries Final Hours strategy, the retention data, the batch, the thumbnail specifics, the full craft canon, and the forward queue.*
