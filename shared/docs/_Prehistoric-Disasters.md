# Prehistoric Disasters — Channel Doctrine
*The single consolidated channel reference for Prehistoric Disasters (@PrehistoricDisasters). Load this — with the four `_` system docs — on any Prehistoric Disasters session. Built 17 June 2026 from the channel's end-to-end launch session.*
*The `_` prefix floats it to the top of `shared/docs/`; channel-scoped, load-on-demand. Sibling to `_Final-Hours.md`, `_Sacred-Dawn.md`, `_Scripture-On-Screen.md`, `_you-had-to-be-there.md`.*

---

## 1. Identity

- **Name:** Prehistoric Disasters · **Handle:** @PrehistoricDisasters (Brand Account under peteralkema2@gmail.com).
- **Created:** 17 June 2026. **Status:** LIVE — published 17 June eve. Account verified (15-min cap lifted); **two videos public** — Toba (ep1) and Chicxulub (ep2). Fully automated via the batch runner.
- **Format:** faceless; Inworld **Victor** narration at **`speaking_rate` 0.9** (slower, deliberate, for the deep-time register); photoreal-cinematic deep-time stills (fal Flux-pro) on the **Ken-Burns-only floor** (`kling_count:0`, ~$3/video) with an optional per-batch front-2-Kling hook (`--kling-count 2`, ~$0.84); curated crossfaded ominous music bed (random-3 at MUSIC_LEVEL 0.07, `amix normalize=0` so it holds a steady level under the voice).
- **Niche:** AI-recreated deep-time catastrophe documentary — *"the prehistoric disasters that almost ended humanity."* Supervolcanoes, floods, ice ages, mass extinctions, impacts.
- **Display-name principle:** keyword-forward, not brandy — "Prehistoric Disasters" is what the audience searches and what the algorithm reads, and this is a packaging-first channel in a search-and-served lane. The brand is the consistent thumbnail look, not a clever name.
- **Repo:** `prehistoric-disasters/`; `channel:` header `prehistoric-disasters` → resolves to `prehistoric-disasters/` (slug = header = folder, no hyphen/underscore trap).

---

## 2. Thesis

Prehistoric Disasters is the **purest un-filmable-by-definition fit the machine has found** — sharper even than Sacred Dawn on the un-referenced-sublime test (canonical §9.3b). No footage of the Toba supereruption exists; no camera saw Chicxulub or the Permian dying. So the AI image is not competing with a real photograph it can be caught failing against — Flux's photoreal-but-unreal rendering *is* the only way these events can be shown, and reads as awe rather than fakery. The audience is AI-indifferent (deep-time documentary viewers don't carry an archival reference to be offended by) and the topic is permanently warm, evergreen, and served.

The bet here is **packaging + topic + cadence, not motion or render craft** (canonical §9.1 corollary, banked 17 June across three lanes). The breakout competitors in this neighbourhood win on title, thumbnail, and topic selection while running mostly Ken Burns / slideshow visuals. So Prehistoric Disasters deliberately runs the **Ken-Burns-only floor** — a tier-above motion pipeline would be over-built for the lane on the axis that doesn't drive growth here. The saved Kling spend (~$14/video) converts directly into cadence. The pipeline, the locked thumbnail look, the curated music library, and the unattended batch path are the moat; any single video is a cheap at-bat.

What makes it defensible beyond the format:

**The locked thumbnail look.** Per-channel `channel.json` `thumbnail` block (`low_silhouette` composition mode): a left gradient scrim for text contrast (never global darkening — darken only where the headline lands), image at full brightness, near-white title + amber subtitle, heavy stroke + drop shadow, asymmetric candidate prompt (catastrophe right two-thirds, dark empty left for the text). Flux renders N=2 candidates, Sonnet-4-6 vision picks the best substrate on CTR rules, the deterministic Pillow overlay lands the locked house look. Consistency across the channel is the brand signal the slideshow factories can't be bothered to maintain.

**The un-filmable filter as topic discipline.** Every topic must be a catastrophe no camera recorded and no audience can catch us failing against. Refuse creature/predator spectacle-bait — that's a different, more saturated lane with an AI-hostile (creature-design-literate) audience. The register is catastrophe, scale, and the near-miss of human (or life's) existence, not monster spectacle.

**The slate-then-data discipline.** A ranked 19-topic slate exists (`prehistoric-slate-19.md`), but the rule is ship ep1 + ep2 and read first-48h CTR + AVD *before* authoring the other 18. The machine makes each at-bat cheap precisely so one or two real retention curves can pick the order and shape of the rest. Authoring a full batch before any data exists is the trap the cheap-at-bat economics let us avoid.

Tools (fal Flux + Ken Burns, Inworld, Whisper, ffmpeg, the thumbnail + music + batch legs) are commodity. The moat is the three disciplines above plus the production system.

---

## 3. Economics

- **Cost per video:** ~$3 in fal credits (stills only — no Kling on the Ken-Burns-only floor), plus negligible Inworld/Claude (the Sonnet thumbnail-selection call). ~30–60 min unattended render for a ~20-min video, the bulk of it in the final ffmpeg encode (~20 min, CPU-bound — the faster-encode lever, backlog Tier-4 #18, would roughly halve it).
- **The near-free at-bat principle (banked 17 June):** at ~$3/video and ~10 min of channel setup, a new channel in a hot served lane is a BUY, not a throughput risk. Peter correctly overrode the don't-split-throughput caution — that caution only holds for expensive (Kling-heavy) lanes. The cost floor is now low enough that launching a whole channel to test a lane is cheaper than agonising over whether to.
- **Dud-tolerance is the strategy** — power-law logic, one breakout pays for many duds, and at $3 the cost of a dud is rounding error. Ship, read the curve, let the data drive.
- **Portfolio logic:** the pipeline is channel-agnostic; Prehistoric Disasters is the eighth channel on the shared engine and the first stood up entirely through the unattended batch path. Its thumbnail look, music library, and slate compound independently.

---

## 4. Topic principles

Three filters:
1. **An un-filmable deep-time catastrophe** — a supervolcano, flood, ice age, impact, or mass extinction no camera recorded and no archival reference exists for. This is the un-referenced-sublime fit and it's non-negotiable: if footage or a recognisable real-world reference exists, the topic belongs to a different channel.
2. **Catastrophe-and-scale register** — the near-end of humanity or of life itself; the dread of how close it came; the indifference of deep time. Not monster spectacle, not creature-design showcases, not breaking-news/conspiracy framing. Cinematic, considered, ominous.
3. **Render-friendly by definition** — deep-time landscapes (ash skies, frozen seas, flooded valleys, impact horizons) are exactly what Flux renders cleanly and what Ken Burns animates as slow atmospheric drift. The lane's natural imagery is the pipeline's strength.

The catastrophe should be visible in the title — scale-quantified-dread ("96% DEAD," "ALMOST EXTINCT," "the disaster that almost ended us") or the named near-miss ("The Last Day of the Dinosaurs," "The Day the Mediterranean Refilled").

**Silhouette / scale-anchor note (decided 17 June eve — the silhouette STAYS in-video):** the channel-wide `style_suffix` puts a tiny lone human silhouette in every still. Decided to KEEP it even on pre-human topics: it reads SYMBOLICALLY (a witness / scale-anchor, the dignified-minimum version of the Chloe-vs-History time-traveller), gives a focal point vs a flat National Geographic spread, is distinctive (nobody in the lane does it), and delivers the channel's core job (felt scale). Let the audience rule it — watch comments on pre-human videos for literal-reading complaints; reconsider only if they appear, not on theory. (The THUMBNAIL scale-anchor is a separate, per-`thumbnail.json` choice — still swap to a lone tree/creature/boat for pre-human thumbnails where a human would jar at a glance. Flag slate topics human-era ✅ vs pre-human ⚠️.)

---

## 5. Operating principles (banked)

- **Ken-Burns-only is the deliberate default for this lane**, not a limitation. The lane's winners don't win on motion; the saved Kling budget becomes cadence. Revisit only if a real retention curve shows motion would have held a specific drop-off.
- **fal `safety_tolerance:"5"`** on every Flux call — default safety silently returns ~7KB black-PNG placeholders on rejection with no error. (The 88-still Toba run came back clean, strong evidence the batch first-pass gates it — but confirm in code, canonical backlog.)
- **Script format is copied from a known-good script, never authored from a doc's prose description** (banked hard 17 June — the first Toba draft used YAML fences + `#` headers + `NARRATION:` labels and parsed to ZERO beats → ZeroDivisionError). Bare `key: value` header (no `---` fences), `## COLD OPEN` / `## PART …` double-hash sections, `[A] narration` then `VISUAL:` per beat, blank line between. Verify with `parse_script.py <md> --json … --json-full …` (zero spend) before any run. See ante-machinam Part VI.
- **Runtime is beat-floored, not words-only** — the Ken-Burns minimum hold stretches short beats, so real runtime ≈ beat count × ~14s, longer than a wpm estimate predicts. Toba: 88 beats → 20.7 min (a words-only estimate said ~13). Estimate from beat count for this lane.
- **The thumbnail is authored WITH the script** as one packaging act, but stored as a separate `thumbnail.json` (`{subject,title,subtitle}`) — the YouTube title (full, SEO) and the thumbnail headline (short, punchy) are different strings. The pair (`.md` + `.thumb.json`) travels together through the batch inbox; the separation is the architecture, and it means the text is written once at prep and read once at the end, so nothing in the middle can corrupt it.
- **Audio chain (three fixes banked 17 June eve, see canonical §6):** music reaches the batch path only because convergence now derives the channel dir from `proj.parent.parent` (the old `channel_dir` var was undefined → silent `--no-music`); music holds a steady level because the `amix` carries `normalize=0` (the `normalize=1` default ducked it under the voice); Victor's pace is set per-channel via `speaking_rate` in `channel.json`. Validate audio END TO END for level, not a one-listen presence check.
- **Music tracks must have no spaces in filenames** — `acrossfade` and the ffmpeg concat list both choke on them. Normalize the library to `track_NN.mp3`. Random-N (default 3) crossfaded + looped gives per-video variance so two videos don't share a bed.
- **Banner art is the one place prompt-baked text won** — a full-frame catastrophe collage with a baked cracked-stone title read as intentional (vs the usual rule that text is a deterministic overlay because Flux can't render legible type). Mind the YouTube safe area: only the center ~1546×423 shows on mobile, so the title must sit centered and compact.

---

## 6. Distribution principles (banked / inherited)

- **CTR + AVD in the first 48 hours are the levers; impression curves are not a decision input** (the umbrella packaging doctrine). Read the retention-curve *shape* at 100+ views, never Studio AI summaries on tiny samples.
- **Ship ep1 + ep2, then read before authoring the rest.** The slate is a queue, not a commitment; the first two videos' first-48h data picks the order and shape of the other seventeen. This is the channel's primary strategic discipline (canonical §9.7).
- **Lane strategy over spike-chasing** — ride the permanently-warm deep-time-catastrophe lane, not individual viral moments. The lane has a demand floor (these topics are perennially searched) and is served (the algorithm pushes catastrophe documentary). Best-execution in the warm lane beats chasing a crested spike.
- **Title and thumbnail complement, not echo** — the thumbnail carries the catastrophe-at-a-glance ("96% DEAD" over a poisoned sea), the title carries the why-click ("The Permian Extinction: The Day Earth Almost Died"). Never the same nouns.
- **NEW-CHANNEL HARD GATE — verify the account before the first long upload.** An unverified YouTube account rejects uploads over 15 minutes at processing ("Processing abandoned — video too long"). This bit the Toba launch after a full render. Verify at youtube.com/verify (phone), then re-run the upload — no re-render needed.
- **Schedule for US prime evening** (the `upload_episode.py --schedule-cet-1am` / `--publish-at` path) once cadence starts — pairs with the per-project scheduling backlog item (every ~6h from the latest video for a batch).

---

## 7. Live state (as of 17 June 2026 — evening, LIVE)

| Video | Status | Signal |
|---|---|---|
| **Toba** (ep1, "10 Prehistoric Disasters That Almost Ended Humanity", 88 beats, ~20.7 min) | **PUBLISHED public.** Account verified (15-min cap lifted). | First-48h CTR + AVD pending — read next session. |
| **Chicxulub** (ep2, "The Last Day of the Dinosaurs: The Asteroid They Never Saw Coming", 81 beats, ~8:55) | **PUBLISHED public.** Re-run through the FULL process (delete project → re-ingest → `run_batch.py --kling-count 2 --limit 1`) to bake in music + 0.9 Victor + front-2 Kling. | First-48h CTR + AVD pending. Watch the first 10-15s for the front-2-Kling hook lift specifically. |

**The channel is LIVE with two public videos and zero first-48h data yet.** The distribution principles in §6 are inherited from the umbrella doctrine; the first real diagnostic comes when ep1/ep2 clear 48 hours. **Read both next session via NexLev `get_my_video_analytics` + `get_my_audience_retention`.**

**The lane benchmark — Wild Horizons** (`UC0g0WbvanQND4dC1JDaW1_w`, @WildHorizons6688). This IS the lane: faceless AI-cinematic deep-time catastrophe, Google-Trends keyword `dinosaurs`, even a Toba video ("The 74,000-Year-Old Monster That Killed 99% of Our Ancestors", 326K). Numbers: outlier 6.33, 48.7K subs, ~$4,300/mo, 13.7M total views, **avg ~218K views/video**, and **NO outliers even at 1.3× → a FLAT high-floor curve** (every video clears six figures; the lane delivers reliably, not via jackpots — for a factory model a high floor beats a fat tail). Avg length **~32 min**, biggest hit a 72-min full doc → the lane rewards **long-form**. **It appeared as a SUGGESTED video next to Chicxulub in Studio** → YouTube has classified this channel into the neighbourhood and it's positioned to draw Wild Horizons' recommendation traffic. Compare ep1/ep2 CTR + AVD against the ~218K floor.

**The first open experiment — tight vs long-form:** `toba.md` (88 beats, ~20.7 min) vs `toba-full.md` (~40 min real). The Wild Horizons ~32-min average + 72-min mega-hit leans toward long-form; confirm against ep1/ep2's OWN AVD curves before committing the slate. (Length is source-driven and retention-earned, never padded to a competitor benchmark — but the benchmark is a strong prior.)

---

## 8. The launch backlog — the 19-topic slate

This is the channel's **launch backlog**: the ranked authoring queue (`prehistoric-slate-19.md`), worked top-down. The governing discipline (canonical §9.7): **ship ep1 + ep2, then read first-48h CTR + AVD before authoring the rest.** The slate is a queue, not a commitment — the first two videos' data picks the order and shape of the other seventeen. Build the cluster around whichever of the first two shows life; do not batch blind.

Per-row: format (DEEP-DIVE single-event narrative / LISTICLE countdown), silhouette flag (✅ human-era, the tiny-human scale-anchor works / ⚠️ pre-human, swap the anchor to a lone tree/creature/boat in `thumbnail.json`), and status. Status starts `queued`; move to `authored` → `rendered` → `live` as each ships.

| # | Topic | Title direction | Format | Sil. | Status |
|---|---|---|---|---|---|
| — | **Toba** | "10 Prehistoric Disasters That Almost Ended Humanity" | LISTICLE | ✅ | **ep1 — LIVE (published)** |
| 1 | **Chicxulub** | "The Last Day of the Dinosaurs: The Asteroid They Never Saw Coming" | DEEP-DIVE | ⚠️ | **ep2 — LIVE (published, front-2 Kling)** |
| 2 | **The Permian Great Dying** | "96% DEAD" — the worst extinction in Earth's history; makes Chicxulub look minor | DEEP-DIVE | ⚠️ | queued |
| 3 | **The Lost Human Species** | Neanderthals, Denisovans, floresiensis, naledi; "which one is in your DNA?" | LISTICLE | ✅ | queued |
| 4 | **Snowball Earth** | the planet froze pole to pole, ice at the equator | DEEP-DIVE | ⚠️ | queued |
| 5 | **The Zanclean Flood** | the Mediterranean refilled in years, a waterfall a thousand times the Amazon | DEEP-DIVE | ⚠️ | queued |
| 6 | **"8 Times Earth Nearly Died"** | the anchor listicle, a tour of the near-misses | LISTICLE | ⚠️ | queued |
| 7 | **Yellowstone** | the supervolcano that already erupted three times (present-tense dread) | DEEP-DIVE | ✅ | queued |
| 8 | **Thera / Santorini** | the eruption that may be the seed of the Atlantis myth | DEEP-DIVE | ✅ | queued |
| 9 | **The Green Sahara** | the desert was green grassland with lakes and hippos, and it died | DEEP-DIVE | ✅ | queued |
| 10 | **The Messinian Salinity Crisis** | the Mediterranean dried to a salt desert | DEEP-DIVE | ⚠️ | queued |
| 11 | **The Great Oxygenation Event** | the first mass extinction, caused by oxygen itself | DEEP-DIVE | ⚠️ | queued |
| 12 | **Solar superstorms** | the Carrington-scale events written in the ice and tree rings | LISTICLE | ✅ | queued |
| 13 | **The Ordovician extinction** | the one a gamma-ray burst may have triggered | DEEP-DIVE | ⚠️ | queued |
| 14 | **The Last Mammoths** | still alive when the pyramids stood; the slow death on Wrangel Island | DEEP-DIVE | ✅ | queued |
| 15 | **The Siberian Traps** | the million-year volcanism behind the Great Dying | DEEP-DIVE | ⚠️ | queued |
| 16 | **Australian megafauna** | giant wombats, marsupial lions, and what killed them | LISTICLE | ✅ | queued |
| 17 | **Drowned Worlds** | Doggerland and the coastlines the meltwater swallowed | DEEP-DIVE | ✅ | queued |
| 18 | **The Deccan Traps** | the other catastrophe that hit alongside Chicxulub | DEEP-DIVE | ⚠️ | queued |
| 19 | **The End-Triassic extinction** | the one that cleared the stage for the dinosaurs | DEEP-DIVE | ⚠️ | queued |

**Authoring discipline for each row:** keep the catastrophe-and-scale register; refuse creature/predator spectacle-bait; author the `thumbnail.json` alongside the script (the slate's per-topic thumbnail-concept line is the seed); swap the silhouette scale-anchor for the ⚠️ pre-human rows; run the ante-machinam IV.7 pre-lock audit and the Constitution check before pasting; verify the parse (`parse_script.py … --json-full`) before spending; title and thumbnail complement, not echo.

**Why these and not a fresh NexLev pull each time:** the slate was built against the lane's demand floor (these are perennially-searched deep-time catastrophes) and the un-filmable filter (every row is an event no camera recorded). NexLev stays the *lagging/detail* signal — pull it to validate a specific title's framing or check a competitor's treatment of a topic already on the slate, not to re-pick the queue. Lane strategy over spike-chasing: the queue is the lane; ride it.

---

## 9. Channel-specific files & quirks

- `prehistoric-disasters/channel.json` — `name: prehistoric_disasters`, `voice_id: Victor` (snake_case — `voiceId` silently falls back to Victor), prehistoric `style_suffix` (ash-grey/bone/ember, photoreal, no-modern, 16:9), `kling_count: 0` (Ken-Burns-only), full `thumbnail` block (`low_silhouette`, scrim, margins, candidate suffix, selection rules), `music` block (`{dir:music, tracks:3, crossfade_seconds:2, level:0.07}`), `upload` block (category 24 / private).
- `prehistoric-disasters/music/` — 8 ominous deep-time beds, normalized to `track_NN.mp3` (no spaces).
- `prehistoric-disasters/token.json` + `client_secret.json` — OAuth, bound to @PrehistoricDisasters (Production app, non-expiring); authed via `upload_episode.py --auth-only` using an `_authstub` project-dir to satisfy the `is_dir()` check.
- `prehistoric-disasters/projects/toba/` — the first project (88 beats); `thumbnail.json`, `final_video.mp4` (predates music wiring — re-assemble before publish).
- Banner art: full-frame catastrophe collage with baked cracked-stone title (the prompt-baked-text exception; mind the mobile safe area).
- **The Ken-Burns-only reference signature** — Prehistoric Disasters is the channel that must keep rendering clean at `kling_count:0`, the all-floor case that proves the tiered-render lower bound. The strip's "Animating clips (Kling)…" label is wrong on this channel (cosmetic backlog, canonical Tier-3 #12).
- Standalone tuning (free re-runs): thumbnail via `select_thumbnail_still.py` + `make_thumbnail.py`; music via `assemble_episode.py … --music-dir prehistoric-disasters/music --out <test>.mp4`.

---

*Maintained by Peter + Claude. Strategic framing, topic principles, the slate, and banked production/distribution lessons live here. Operational how-to lives in `_machina.md` / the canonical reference §5; craft in `_ante-machinam.md`; the wider operation in `_YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md`. As the channel ships real videos, replace the inherited distribution principles in §6–§7 with this channel's own validated retention data.*
