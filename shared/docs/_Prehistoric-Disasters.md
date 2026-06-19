# Prehistoric Disasters — Channel Doctrine
*The single consolidated channel reference for Prehistoric Disasters (@PrehistoricDisasters). Load this — with the four `_` system docs — on any Prehistoric Disasters session. Built 17 June 2026 from the channel's end-to-end launch session.*
*Updated 19 June 2026 — first full multi-video batch authored, runtime calibration corrected against rendered videos, NexLev connection resolved, rich-beat authoring method banked.*
*The `_` prefix floats it to the top of `shared/docs/`; channel-scoped, load-on-demand. Sibling to `_Final-Hours.md`, `_Sacred-Dawn.md`, `_Scripture-On-Screen.md`, `_you-had-to-be-there.md`.*

---

## 1. Identity

- **Name:** Prehistoric Disasters · **Handle:** @PrehistoricDisasters (Brand Account under peteralkema2@gmail.com).
- **Channel ID:** `UC63KxtSDLJuEvuRYKz2lJmg` (now confirmed; needed for all NexLev `get_my_*` calls).
- **Created:** 17 June 2026. **Status:** LIVE — published 17 June eve. Account verified (15-min cap lifted). Fully automated via the batch runner. As of 19 June: two original videos public (Toba, Chicxulub), several more rendered and scheduled, and a 10-video batch in authoring/staging (see §7–§8).
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

**The slate-then-data discipline.** A ranked topic slate exists (see §8), but the rule is ship early episodes and read first-48h CTR + AVD *before* committing the rest of the queue. The machine makes each at-bat cheap precisely so one or two real retention curves can pick the order and shape of the rest. (See §7 for the one deliberate, reasoned exception — the 10-video "away week" batch.)

Tools (fal Flux + Ken Burns, Inworld, Whisper, ffmpeg, the thumbnail + music + batch legs) are commodity. The moat is the three disciplines above plus the production system.

---

## 3. Economics

- **Cost per video:** ~$3 in fal credits (stills only — no Kling on the Ken-Burns-only floor), plus negligible Inworld/Claude (the Sonnet thumbnail-selection call). **Beat count does NOT drive cost** — a 125-beat rich script costs the same ~$3 as an 80-beat one, because Ken Burns is free and only the Flux stills are billed (one per beat at trivial per-image cost). Stop framing higher-beat scripts as a fal-spend concern; the spend ceiling is flat under ~$20 regardless of length. ~30–60 min unattended render for a ~20-min video, the bulk of it in the final ffmpeg encode (~20 min, CPU-bound — the faster-encode lever, backlog Tier-4 #18, would roughly halve it).
- **The near-free at-bat principle (banked 17 June):** at ~$3/video and ~10 min of channel setup, a new channel in a hot served lane is a BUY, not a throughput risk. The cost floor is low enough that launching a whole channel to test a lane is cheaper than agonising over whether to.
- **Dud-tolerance is the strategy** — power-law logic, one breakout pays for many duds, and at $3 the cost of a dud is rounding error. Ship, read the curve, let the data drive.
- **Portfolio logic:** the pipeline is channel-agnostic; Prehistoric Disasters is the eighth channel on the shared engine and the first stood up entirely through the unattended batch path. Its thumbnail look, music library, and slate compound independently.

---

## 4. Topic principles

Three filters:
1. **An un-filmable deep-time catastrophe** — a supervolcano, flood, ice age, impact, or mass extinction no camera recorded and no archival reference exists for. This is the un-referenced-sublime fit and it's non-negotiable: if footage or a recognisable real-world reference exists, the topic belongs to a different channel.
2. **Catastrophe-and-scale register** — the near-end of humanity or of life itself; the dread of how close it came; the indifference of deep time. Not monster spectacle, not creature-design showcases, not breaking-news/conspiracy framing. Cinematic, considered, ominous.
3. **Render-friendly by definition** — deep-time landscapes (ash skies, frozen seas, flooded valleys, impact horizons) are exactly what Flux renders cleanly and what Ken Burns animates as slow atmospheric drift. The lane's natural imagery is the pipeline's strength.

The catastrophe should be visible in the title — scale-quantified-dread ("96% DEAD," "ALMOST EXTINCT," "the disaster that almost ended us") or the named near-miss ("The Last Day of the Dinosaurs," "The Day the Mediterranean Refilled").

**Human-era ✅ vs pre-human ⚠️ flag.** Tag every slate topic. It governs the THUMBNAIL scale-anchor only (see below). It does NOT change the in-video silhouette, which stays on every topic.

**The register flexes within the lane (banked 19 June).** Not every catastrophe is fire-and-blast. The Green Sahara is a *quiet, elegiac* catastrophe — a green, watered, peopled world that dried out over centuries with no eruption and no impact, just the slow turning of the rains. The dread there is slow loss, not violence, and the script carries a rare *"and here is the gift"* turn (the drying drove people to the Nile and may have helped seed ancient Egypt). Worth holding as a distinct register-and-shape, and worth watching whether the hopeful-pivot close retains better or worse than straight-loss closes once data lands (cheap to A/B inside an evergreen batch).

**Silhouette / scale-anchor note (decided 17 June eve — the silhouette STAYS in-video):** the channel-wide `style_suffix` puts a tiny lone human silhouette in every still. Decided to KEEP it even on pre-human topics: it reads SYMBOLICALLY (a witness / scale-anchor), gives a focal point vs a flat National Geographic spread, is distinctive (nobody in the lane does it), and delivers the channel's core job (felt scale). Let the audience rule it — watch comments on pre-human videos for literal-reading complaints; reconsider only if they appear, not on theory. (The THUMBNAIL scale-anchor is a separate, per-`thumb.json` choice — still swap to a lone tree/creature/boat/feature for pre-human ⚠️ thumbnails where a human would jar at a glance; human-era ✅ thumbnails keep the human silhouette anchor.)

---

## 5. Operating principles (banked)

- **Ken-Burns-only is the deliberate default for this lane**, not a limitation. The lane's winners don't win on motion; the saved Kling budget becomes cadence. Revisit only if a real retention curve shows motion would have held a specific drop-off.
- **fal `safety_tolerance:"5"`** on every Flux call — default safety silently returns ~7KB black-PNG placeholders on rejection with no error. (The 88-still Toba run came back clean, strong evidence the batch first-pass gates it — but confirm in code, canonical backlog.)
- **Script format is copied from a known-good script, never authored from a doc's prose description** (banked hard 17 June — the first Toba draft used YAML fences + `#` headers + `NARRATION:` labels and parsed to ZERO beats → ZeroDivisionError). Bare `key: value` header (no `---` fences), `## COLD OPEN` / `## PART …` double-hash sections, `[A] narration` then `VISUAL:` per beat, blank line between. **Numbers spelled out in narration** (numerals fine in the header). One VISUAL per beat, each with an animatable foreground. Verify with `parse_script.py <md> --json … --json-full …` (zero spend) before any run. See ante-machinam Part VI.

### 5a. Runtime calibration — CORRECTED 19 June (supersedes the old flat ~14s/beat note)
There is **no single seconds-per-beat constant** — real runtime depends on *words-per-beat*, not beat count alone, because the Ken-Burns minimum hold only floors short beats. Observed across rendered videos:

| Video | Beats | Runtime | s/beat |
|---|---|---|---|
| Chicxulub (short beats) | 81 | 8:55 | ~6.6 |
| Zanclean (rich beats) | 96 | 14:59 | **~9.4** |
| Toba (long beats / full) | 88 | 20.7 min | ~14.1 |
| Yellowstone | (count pending) | 18:22 | — read the count next session |

**Working rule for the current rich-beat authoring style (~38–45 words/beat):** use **Zanclean's ~9.4 s/beat**, so **~120–130 beats → ~19–20 min**. This is the calibration all the new batch scripts were authored against. Confirm/refine it when Yellowstone's beat count is read (the pending third data point). The early deep-dives (Chicxulub, Snowball, the Great Dying) came in **short** (~9 min) against the **~32-min lane benchmark** (Wild Horizons, §7) — hence the deliberate move to longer scripts.

### 5b. Authoring method — rich beats, then genuine top-up (banked 19 June)
- **Author rich AND author more of them.** Peter's explicit steer: author on the shorter side per beat *but add genuine material, never pad.* Aim for substantive beats (~38–45 words, hard ceiling ~54) and enough of them to clear ~19–20 min.
- **The idempotent insert-script top-up.** When a draft lands short of target, top it up with genuine beats via a Python heredoc that `assert`s each anchor (an existing unique `VISUAL:` line) appears exactly once before inserting after it. Same discipline as the patch_*.py philosophy: anchor-verified, refuses on a miss, idempotent. This added real content (volcanic lightning, days-of-darkness, the Akrotiri rediscovery, the Minotaur echo, the Mega-Chad heart, the Nile flood, etc.) rather than stretching existing beats.
- **Per-script validation harness (run before presenting each pair):**
  - beat count == VISUAL count (1:1)
  - no bare digits in narration: `grep '^\[A\]' file.md | grep -E '[0-9]'` → must be empty
  - thumb JSON parses and has `{subject, title, subtitle}`
  - no beat over ~54 words
  - est runtime = beats × 9.4 / 60

### 5c. Thumbnail + batch file conventions
- **The thumbnail is authored WITH the script** as one packaging act, but stored as a separate **`<name>.thumb.json`** (`{subject,title,subtitle}`). **Dot-naming is mandatory** — `name.thumb.json`, NOT `name_thumb.json`, or the batch runner silently skips the pair. The YouTube title (full, SEO) and the thumbnail headline (short, punchy) are different strings and must **complement, not echo** (different nouns — e.g. Thera: title carries "Atlantis," thumb carries "THE ISLAND THAT SANK").
- **Inbox is a flat folder of matched pairs** `<name>.md` + `<name>.thumb.json`, paired by basename (basename = project slug). The pair travels together; text is written once at prep and read once at the end, so nothing in the middle can corrupt it.
- **Inbox hygiene:** the inbox should contain ONLY the current batch's files. `ingest.create_project` **refuses to recreate an existing project**, so move shipped pairs to `~/batch_done/` before a new run. Files reach the box via `scp -P 443 ~/Downloads/batch_inbox/* peter@116.202.18.68:~/batch_inbox/`.

### 5d. Audio chain (three fixes banked 17 June eve, see canonical §6)
- Music reaches the batch path only because convergence now derives the channel dir from `proj.parent.parent` (the old `channel_dir` var was undefined → silent `--no-music`).
- Music holds a steady level because the `amix` carries `normalize=0` (the `normalize=1` default ducked it under the voice).
- Victor's pace is set per-channel via `speaking_rate` in `channel.json`.
- Validate audio END TO END for level, not a one-listen presence check. **Music level 0.07 is now proven** on Prehistoric Disasters and Scripture On Screen.
- **Music filenames must have no spaces** — `acrossfade` and the ffmpeg concat list both choke on them. Normalize the library to `track_NN.mp3`. Random-N (default 3) crossfaded + looped gives per-video variance so two videos don't share a bed. Music files are gitignored — scp directly to the box; only the `channel.json` music block travels laptop → GitHub → box.

### 5e. Batch runner mechanics
On the BOX, inside tmux (tmux survives the laptop closing):
```
ssh -p 443 peter@116.202.18.68
tmux new -s batch          # reattach later: tmux attach -t batch
source ~/venvs/pipeline/bin/activate
cd ~/Pipeline
set -a; source .env; set +a
python shared/run_batch.py --inbox ~/batch_inbox --channel prehistoric-disasters --plan      # zero-spend dry run
python shared/run_batch.py --inbox ~/batch_inbox --channel prehistoric-disasters --limit 1   # one full video
python shared/run_batch.py --inbox ~/batch_inbox --channel prehistoric-disasters             # full batch
```
Flags: `--inbox`, `--channel`, `--kling-count` (front-N Kling hook), `--plan` (dry run), `--limit N`, `--publish-start` (ISO-8601 **with mandatory timezone**), `--publish-interval-hours` (default 12). One batch at a time on the box — Whisper and ffmpeg are CPU-bound and contend under parallel batches.

### 5f. Banner art
The one place prompt-baked text won — a full-frame catastrophe collage with a baked cracked-stone title read as intentional (vs the usual rule that text is a deterministic overlay because Flux can't render legible type). Mind the YouTube safe area: only the center ~1546×423 shows on mobile, so the title must sit centered and compact.

---

## 6. Distribution principles (banked / inherited)

- **CTR + AVD in the first 48 hours are the levers; impression curves are not a decision input** (the umbrella packaging doctrine). Read the retention-curve *shape* at 100+ views, never Studio AI summaries on tiny samples.
- **Length is source-driven and retention-earned, but the lane benchmark is a strong prior.** Wild Horizons averages ~32 min with a 72-min mega-hit → the lane rewards long-form. The early ~9-min deep-dives were under-built for the lane; the corrected target is ~19–20 min (~120–130 rich beats). Add genuine material to get there — never pad.
- **Lane strategy over spike-chasing** — ride the permanently-warm deep-time-catastrophe lane, not individual viral moments. Best-execution in the warm, served lane beats chasing a crested spike.
- **Title and thumbnail complement, not echo** — the thumbnail carries the catastrophe-at-a-glance, the title carries the why-click. Never the same nouns.
- **NEW-CHANNEL HARD GATE — verify the account before the first long upload.** An unverified YouTube account rejects uploads over 15 minutes at processing ("Processing abandoned — video too long"). This bit the Toba launch. Verify at youtube.com/verify (phone), then re-run the upload — no re-render needed. (Already cleared for this channel.)
- **Schedule for US prime evening** via the runner's `--publish-start` / `--publish-interval-hours` (ISO-8601 with timezone). The 10-video batch stages at ~24h intervals from 22 June.
- **Copyright / Content-ID watch:** the Great Dying (Permian) render carries a **COPYRIGHT flag** in Studio — most likely a music-library track hitting Content ID. **Investigate and clear before its scheduled publish date.** General principle: spot-check Studio's copyright status on each rendered video before it goes public.

---

## 7. Live state (as of 19 June 2026)

**NexLev connection — RESOLVED.** Prehistoric Disasters is now connected to NexLev (channel ID `UC63KxtSDLJuEvuRYKz2lJmg`), the 8th connected channel. *However,* as of 19 June the channel is still **statistically empty** — overview reports **0 subscribers, 1 view, 3 public videos**, and `get_my_top_videos` returns nothing, because most of the batch is future-scheduled and the public videos are too fresh to have accrued traffic. So the connection gap is closed, but the **first-48h CTR/AVD reads are still genuinely pending** until views accrue. Re-pull `get_my_video_analytics` + `get_my_audience_retention` once Toba/Chicxulub clear real view counts. **Reminder (analytics discipline):** for a freshly launched channel the NexLev/Studio AVD field averages across pre-launch days and is unreliable — derive AVD as `(total watch-minutes × 60) ÷ total views` instead, and verify durations at source.

**Rendered / scheduled (in YouTube Studio):**

| Video | Beats | Runtime | Status |
|---|---|---|---|
| **Toba** (ep1, "10 Prehistoric Disasters That Almost Ended Humanity") | 88 | 20:45 | **PUBLISHED public** |
| **Chicxulub** (ep2, "The Last Day of the Dinosaurs") | 81 | 8:55 | **PUBLISHED public** |
| **Permian / Great Dying** | — | 8:57 | SCHEDULED — ⚠️ **COPYRIGHT flag, clear before publish** |
| **Snowball Earth** | — | 9:06 | SCHEDULED |
| **Zanclean Flood** | 96 | 14:59 | SCHEDULED (the runtime-calibration anchor) |
| **Yellowstone** | (read it) | 18:22 | SCHEDULED (read beat count → calibration tiebreak) |
| **"8 Times Earth Almost Died"** | — | 12:59 | SCHEDULED |

**The lane benchmark — Wild Horizons** (`UC0g0WbvanQND4dC1JDaW1_w`, @WildHorizons6688). This IS the lane: faceless AI-cinematic deep-time catastrophe. Numbers: outlier 6.33, 48.7K subs, ~$4,300/mo, 13.7M total views, **avg ~218K views/video**, **NO outliers even at 1.3× → a FLAT high-floor curve** (every video clears six figures; for a factory model a high floor beats a fat tail). Avg length **~32 min**, biggest hit a 72-min full doc → the lane rewards **long-form**. **It appeared as a SUGGESTED video next to Chicxulub** → YouTube has classified this channel into the neighbourhood. Compare our CTR + AVD against the ~218K floor once data exists.

### 7a. The 10-video "away week" batch (in authoring / staging)
A deliberate, reasoned exception to ship-two-then-read: Peter committed to a **batch of 10** to stage at ~24h intervals from **22 June** while away for a week, reviewing the data on return. Defensible because the economics make each at-bat ~$3, the lane is evergreen and served, and power-law/high-floor logic means a 10-deep queue in a warm lane is a buy, not a gamble. Flagged once for data-discipline + length risk, then proceeded.

**The batch is also a deliberate variety probe** — it spreads format and register so the returning data can show which *kind* of topic the audience rewards:
- pure deep-time (Great Oxygenation, Ordovician)
- human-era catastrophe (Thera, Drowned Worlds, Last Mammoths)
- listicle (Lost Human Species, Solar Superstorms)
- elegiac / "gift-turn" (Green Sahara)

**Authored this session (each ~125 beats, ~19–20 min, validated, in `~/batch_inbox/`):**
- **Lost Human Species** — re-authored LONG (120 beats; the original ~80-beat short version was overwritten). Listicle, 6-species countdown, "which one is in your DNA?" spine. ✅
- **Great Oxygenation Event** — 127 beats. Deep-time (2.4 Ga), pure un-filmable; the first mass extinction, caused by oxygen itself; endosymbiosis/mitochondria thread. ⚠️
- **Thera** — 125 beats. Human-era (~1600 BCE Minoan eruption); may seed the Atlantis legend; lightning/darkness/Akrotiri-rediscovery/Minotaur-echo beats. ✅
- **Green Sahara** — 125 beats. Human-era; African Humid Period; Mega-Chad, rock art, the swimmers; the drying via orbital wobble; the Nile/Egypt gift-turn. Elegiac register. ✅

**Pending (still to author, one at a time, ~120–130 rich beats each):**
- **Last Mammoths** — human-era ✅; still alive on Wrangel Island when the pyramids stood; the lonely dwindling end of a species.
- **Solar Superstorms** — listicle ✅; Carrington-scale events written in ice and tree rings.
- **Drowned Worlds** — human-era ✅; Doggerland and the coastlines the meltwater swallowed.
- **Ordovician Extinction** — pre-human ⚠️; possible gamma-ray-burst trigger.

---

## 8. The topic slate

The channel's authoring queue. The governing discipline normally is **ship ep1 + ep2, then read first-48h CTR + AVD before authoring the rest** — the active 10-video batch (§7a) is the one reasoned exception. Per-row: format, silhouette flag (✅ human-era / ⚠️ pre-human), status updated through this session.

| # | Topic | Title direction | Format | Sil. | Status |
|---|---|---|---|---|---|
| — | **Toba** | "10 Prehistoric Disasters That Almost Ended Humanity" | LISTICLE | ✅ | **LIVE (published)** |
| 1 | **Chicxulub** | "The Last Day of the Dinosaurs: The Asteroid They Never Saw Coming" | DEEP-DIVE | ⚠️ | **LIVE (published, front-2 Kling)** |
| 2 | **The Permian Great Dying** | "96% DEAD" — the worst extinction in Earth's history | DEEP-DIVE | ⚠️ | **rendered — SCHEDULED (⚠️ copyright flag)** |
| 3 | **The Lost Human Species** | "which one is in your DNA?" | LISTICLE | ✅ | **authored long (120 beats) — in batch** |
| 4 | **Snowball Earth** | the planet froze pole to pole | DEEP-DIVE | ⚠️ | **rendered — SCHEDULED** |
| 5 | **The Zanclean Flood** | the Mediterranean refilled in years | DEEP-DIVE | ⚠️ | **rendered — SCHEDULED** |
| 6 | **"8 Times Earth Nearly Died"** | the anchor listicle | LISTICLE | ⚠️ | **rendered — SCHEDULED** |
| 7 | **Yellowstone** | the supervolcano that already erupted three times | DEEP-DIVE | ✅ | **rendered — SCHEDULED** |
| 8 | **Thera / Santorini** | the eruption that may be the seed of the Atlantis myth | DEEP-DIVE | ✅ | **authored (125 beats) — in batch** |
| 9 | **The Green Sahara** | green grassland with lakes and hippos, and it died | DEEP-DIVE | ✅ | **authored (125 beats) — in batch** |
| 10 | **The Messinian Salinity Crisis** | the Mediterranean dried to a salt desert | DEEP-DIVE | ⚠️ | queued |
| 11 | **The Great Oxygenation Event** | the first mass extinction, caused by oxygen itself | DEEP-DIVE | ⚠️ | **authored (127 beats) — in batch** |
| 12 | **Solar superstorms** | Carrington-scale events in ice and tree rings | LISTICLE | ✅ | **pending — in batch** |
| 13 | **The Ordovician extinction** | the one a gamma-ray burst may have triggered | DEEP-DIVE | ⚠️ | **pending — in batch** |
| 14 | **The Last Mammoths** | still alive when the pyramids stood; Wrangel Island | DEEP-DIVE | ✅ | **pending — in batch** |
| 15 | **The Siberian Traps** | the million-year volcanism behind the Great Dying | DEEP-DIVE | ⚠️ | queued |
| 16 | **Australian megafauna** | giant wombats, marsupial lions, what killed them | LISTICLE | ✅ | queued |
| 17 | **Drowned Worlds** | Doggerland and the coastlines the meltwater swallowed | DEEP-DIVE | ✅ | **pending — in batch** |
| 18 | **The Deccan Traps** | the other catastrophe alongside Chicxulub | DEEP-DIVE | ⚠️ | queued |
| 19 | **The End-Triassic extinction** | the one that cleared the stage for the dinosaurs | DEEP-DIVE | ⚠️ | queued |

**Authoring discipline for each row:** keep the catastrophe-and-scale register (flexing to elegiac where the topic earns it); refuse creature/predator spectacle-bait; author the `.thumb.json` alongside the script; swap the thumbnail scale-anchor for ⚠️ pre-human rows; run the rich-beat + insert-top-up method (§5b) to ~120–130 beats; run the validation harness; verify the parse before spending; title and thumbnail complement, not echo.

**Why the slate, not a fresh NexLev pull each time:** the slate was built against the lane's demand floor (perennially-searched deep-time catastrophes) and the un-filmable filter. NexLev stays the *lagging/detail* signal — pull it to validate a specific title's framing, check a competitor's treatment, or (now that the channel is connected) read our own retention once it exists. Lane strategy over spike-chasing.

---

## 9. Channel-specific files & quirks

- **NexLev:** connected, channel ID `UC63KxtSDLJuEvuRYKz2lJmg`. Use full namespaced tool names (`NexLev:get_my_video_analytics`, `NexLev:get_my_audience_retention`) once views accrue.
- `prehistoric-disasters/channel.json` — `name: prehistoric_disasters`, `voice_id: Victor` (snake_case — `voiceId` silently falls back to Victor), prehistoric `style_suffix` (ash-grey/bone/ember, photoreal, no-modern, 16:9, tiny lone silhouette), `kling_count: 0` (Ken-Burns-only), full `thumbnail` block (`low_silhouette`, scrim, margins, candidate suffix, selection rules), `music` block (`{dir:music, tracks:3, crossfade_seconds:2, level:0.07}`), `upload` block (category 24 / private).
- `prehistoric-disasters/music/` — 8 ominous deep-time beds, normalized to `track_NN.mp3` (no spaces). Gitignored; scp directly to box.
- `prehistoric-disasters/token.json` + `client_secret.json` — OAuth, bound to @PrehistoricDisasters (Production app, non-expiring); authed via `upload_episode.py --auth-only` using an `_authstub` project-dir to satisfy the `is_dir()` check.
- `~/batch_inbox/` (box) ← matched `<name>.md` + `<name>.thumb.json` pairs for the current batch only. `~/batch_done/` ← move shipped pairs here so `create_project` won't refuse a re-ingest. Laptop staging dir: `~/Downloads/batch_inbox/`.
- Banner art: full-frame catastrophe collage with baked cracked-stone title (the prompt-baked-text exception; mind the mobile safe area).
- **The Ken-Burns-only reference signature** — Prehistoric Disasters is the channel that must keep rendering clean at `kling_count:0`, the all-floor case that proves the tiered-render lower bound. The strip's "Animating clips (Kling)…" label is wrong on this channel (cosmetic backlog, canonical Tier-3 #12).
- `assemble_episode.py` is the only safe assembler (it honours the beat→shot `_index.json` map); `recreation_pipeline.assemble()` via `finish --assemble-only` is alignment-unsafe.
- Standalone tuning (free re-runs): thumbnail via `select_thumbnail_still.py` + `make_thumbnail.py`; music via `assemble_episode.py … --music-dir prehistoric-disasters/music --out <test>.mp4`.

---

## 10. Open actions / next session

1. **Clear the Permian copyright flag** before its scheduled publish (likely a music-library Content-ID hit — swap the track or confirm clearance).
2. **Finish the batch:** author Last Mammoths, Solar Superstorms, Drowned Worlds, Ordovician (~125 beats each), then stage all 10 via `run_batch.py … --publish-start <ISO+TZ> --publish-interval-hours 24` from 22 June.
3. **Read Yellowstone's beat count** (18:22) to firm up the runtime calibration (third data point against Chicxulub's ~6.6 and Zanclean's ~9.4 s/beat).
4. **Once traffic accrues:** pull Toba + Chicxulub via `get_my_video_analytics` + `get_my_audience_retention`; compare CTR + AVD against the Wild Horizons ~218K floor; read the two universal retention cliffs (the 30–40s context-dump cliff and the ~50–60% mid-video cliff). Derive AVD by hand, not from the unreliable launch-window field.
5. **Watch the variety probe:** which register/format retains best (deep-time vs human-era vs listicle vs elegiac gift-turn), and whether Green Sahara's hopeful close out-retains straight-loss closes.

---

*Maintained by Peter + Claude. Strategic framing, topic principles, the slate, and banked production/distribution lessons live here. Operational how-to lives in `_machina.md` / the canonical reference §5; craft in `_ante-machinam.md`; the wider operation in `_YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md`. As the channel accrues real first-48h data, replace the inherited/pending distribution notes in §6–§7 with this channel's own validated retention curves.*
