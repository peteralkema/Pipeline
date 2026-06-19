# Final Hours — Channel Doctrine
*The single consolidated channel reference for Final Hours (@FinalHours_history). Load this — with the `_`/`__` system docs — on any Final Hours session.*
*Consolidated 11 June 2026; **updated 18 June 2026** (the 10-video maritime/disaster batch session: real retention data pulled, the two-cliff diagnosis confirmed, the cold-open architecture rebuilt around it, the channel thumbnail block added, the batch shipped through `run_batch.py`).*
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

**The canon mechanism.** A per-video block of named descriptors (`{hartley}`, `{band_deck}`) for anything recurring in 3+ shots. **[CLARIFIED 18 June] This is a channel-level `base_canon` + rulebook mechanism, NOT a per-script block in the `.md` file.** The script-file contract (per ante-machinam Part VI) is *header + beats, full stop* — there is no `## CANON` section syntax the parser reads. Cross-shot consistency in authoring is carried by **scene-canon discipline written into the VISUAL lines** ("the lamp room," "the iron spiral stair," repeated with the same concrete descriptors), faceless framing, and **object-substitution** for recurring people (the coats on their pegs, three chairs, the trimmed lamp). This is why the absence-as-subject topics render cleanest — the people are mostly out of frame, so empty rooms and objects carry the continuity. (Confirmed on the Flannan Isles build; the Yellowstone/Prehistoric template — no canon block — runs clean through the same batch path.)

**The beat architecture.** Authored against the **ante-machinam Constitution** (beat granularity ~5–12s spoken, ~15–35 words, hard ceiling ~55; one VISUAL per beat; spell out numbers in narration; lock the script first; every beat carries an animatable foreground subject). Beats sized to narration; assembly holds each clip to audio-measured duration.

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

- **Cold open = ~8 beats of escalating *wrongness*, ~30–40s.** Hook line → straight into the scene, present-tense, the subject already in motion. **NO date/place/biographical throat-clearing in the first ~30s** — identity and context braid in around beats 4–5, *after* the scene has its hook in. (The doctrine's IV.1 already named this: "a context block over ~45–90s without renewing tension causes drop-off.")
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

*Maintained by Peter + Claude. Operational how-to lives in `__machina`/canonical; craft in `__ante-machinam.md`; the wider operation in `__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md`. This doc carries Final Hours strategy, the retention data, the batch, the thumbnail specifics, and the forward queue.*
