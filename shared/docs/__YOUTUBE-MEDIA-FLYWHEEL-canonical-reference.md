# YouTube Media Flywheel — Canonical Project Reference
*The single comprehensive description of the whole operation. Load this first in any new session to get to full context fast.*
*Maintained by Peter + Claude. Last updated: 17 June 2026 (Mission Control at v1.9. This session: a whole new channel — **Prehistoric Disasters** — stood up and proven end to end through a **fully-unattended batch path**; the **automated thumbnail pipeline** (Flux candidates → Sonnet-selects-the-best-substrate → locked overlay) shipped and locked; **music wired into convergence** as a curated per-channel crossfaded random-N bed; and the **batch runner** (`run_batch.py` + `--unattended` gate-mode) shipped. Doc set is two: this reference = the system; `ante-machinam.md` = the craft.).*

---

## 0. What this is, in one paragraph

The **YouTube Media Flywheel** is a one-person, fully-automated faceless-YouTube **media business** built as a *content factory*, not a channel. A single channel-agnostic Python pipeline turns a written script into a finished, narrated, scored, **packaged** video — stills, animation, voiceover, assembly, thumbnail, upload — for a few dollars and a few hours of compute. The same machine serves multiple channels across different genres; a new channel costs one config file and content, not new code. The bet is not on any one video or topic but on **the production system as a compounding asset**: the tools underneath get swapped as they improve, the orchestration lasts years, and the operating discipline is the actual moat. Operated solo by Peter Alkema from The Hague, Netherlands.

The "flywheel": demand research → script → automated production → publish → algorithm signal → learn → better next video, with each turn cheaper and faster than the last, and each banked lesson making every future video across every channel better.

---

## 1. The operator

**Peter Alkema** — solo operator, The Hague / Hoofddorp, Netherlands. Former South African TV presenter (in front of camera), then ~25 years of executive/systems work across consulting, banking, manufacturing; former Udemy course creator with deep instructional-design background. **Vibe-codes in Python; no developers.** Works fast, thinks out loud, iterates. The rare combination the whole thesis leans on: *system operator with creative voice and broadcast taste* — most AI-video people are technologists without taste or artists without systems; Peter is both.

Working style (how Claude should operate with him): direct, skip preamble; full working scripts not snippets; read shared code fully before suggesting changes; match his level, don't over-explain basics; follow rough thinking and reframe when he's stuck; challenge wrong thinking directly and briefly; prose over bullets in strategy; use NexLev proactively for YouTube research; analyse shared screenshots fully. **Command-line only — Peter does not hand-edit files; config changes go via command (a `python3 -c` JSON one-liner), code via idempotent `patch_*.py`.**

---

## 2. The core thesis (the "why" — slow-changing)

**Anchoring principle (Altman, Sora briefing):** *"Don't design for the model. Design for continuous and exponential improvement in the models."* Everything else is consequence.

**Three layers, distinguished by half-life:**
- **Fast layer (3–12 months):** the specific models/tools — fal Flux (stills), fal Kling (animation), Inworld (TTS), Whisper, Remotion, the music library, the cloud host. In active competition, always improving, *designed to be swapped*. Each external service is encapsulated behind one function so a model change is a config edit, never a refactor.
- **Orchestration layer (multi-year):** the pipeline itself — the channel-agnostic conductor, beats.json as sole input, channel.json as identity, the leg system, the canon/rulebook mechanism, the review gates, the per-job look resolver, the thumbnail leg, the batch runner. Survives tool changes. Worth engineering well.
- **Discipline layer (career):** the habits that compound — bank every failure as a *tool-agnostic principle* (not a tool-specific workaround), encapsulate hard-won fixes in code, diagnose the category behind every reshoot, lock the script first, review before paying. **This is the moat.** Competitors copy the surface format in a weekend; they cannot copy two years of banked discipline.

**Two corollaries that govern daily decisions:**
- **Packaging beats production.** Demand-validated topic + a title promising a dramatic arc + a retention hook + a consistent on-brand thumbnail drive distribution more than raw render quality. CTR + AVD in the first 48 hours are the signals the algorithm watches.
- **A principle not in code only runs if a human remembers it.** Push rules from docs into the conductor/scripts wherever worth it.

---

## 3. The business model

A **content factory**: the pipeline generates content on any topic cheaply; channels are distribution vehicles; a portfolio of channels diversifies risk off any single point of failure. Power-law logic — one breakout pays for many duds — so at the early stage **shipping and generating algorithm signal comes before perfect positioning**. Judge on per-video NexLev outlier scores and retention-curve *shape*, never on channel averages. Marginal cost per video is low (single-digit dollars of API spend — and on the Ken-Burns-only lanes, ~$3), so experiment aggressively; the cost of being wrong is near zero. **The cost floor is now low enough that a whole new channel is a near-free at-bat** — proven 17 June with Prehistoric Disasters: ~10 min of setup + ~$3/video on the Ken-Burns path, so a new channel in the hottest cold-start lane is a BUY, not a throughput risk (Peter correctly overrode the don't-split-throughput caution, which only holds for expensive lanes).

---

## 4. The channel roster

One machine, several channels (each a *signature* over the pipeline's legs, expressed in `channel.json` + content):

| Channel | Premise | Mode | Voice | Status |
|---|---|---|---|---|
| **Final Hours** (@FinalHours_history) | The last hours of people/places history remembers; faceless cinematic recreation; the camera stays with one named person/place while catastrophe happens around them | Mode A only | Victor (Inworld) | **Live, primary.** Long-form 12–16 min (city-catastrophe sub-series 20–32 min). Has working OAuth/upload. |
| **Sacred Dawn** (@sacredawn) | The Bible's cosmic & primeval drama — the Watchers, the Nephilim, the Flood, Creation, the war in heaven — as cinematic recreation | Mode A only | **Elliot** (British, deep, liturgical) | **Live.** Highest-fit use of the machine found to date — see §9.3. Full doctrine: `sacred-dawn-creed.md`. |
| **Scripture on Screen** (@scripture_on_screen) | Scripture rendered as cinematic recreation — narrative books of the Bible brought to life beat by beat | Mode A only | dramatic `default_motion` | **In production.** First project: Esther (119 beats). Upload token authed (Production). |
| **You Had To Be There** (@you-had-to-be-there) | Cinematic AI recreation of *vanished lived experience* — un-filmable everyday nostalgia | Mode A, decade-variable look | **Vinny** (warm wry Brooklyn storyteller) | **Live.** First channel to use per-job decade looks in production. |
| **Prehistoric Disasters** (@PrehistoricDisasters) | Cinematic deep-time catastrophe documentary — the prehistoric disasters that almost ended humanity (supervolcanoes, floods, ice ages, extinctions); the hottest faceless cold-start lane, purest un-filmable-by-definition fit | Mode A, **Ken-Burns-only** (`kling_count:0`, ~$3/video) | Victor | **Launched, fully automated.** Stood up end to end 17 June: locked thumbnail look (`low_silhouette`), curated music library, batch-runner-produced. First video (Toba, 88 beats, 20.7 min) rendered + packaged + uploaded private — pending account verification (15-min cap) to publish. Slate of 19 topics queued (`prehistoric-slate-19.md`); ship Chicxulub as ep2, read data, then batch. |
| **Success Coach** (@successcoach100, ~6,090 subs) | Professional transformation in the AI era | Faceless AI VO + stock footage | Ashley (lessons), Victor (hooks) | **Live, monetized but underperforming** — packaging-layer gap, not pipeline gap. On a separate Google account. |
| **Synthetic Press** | AI-era human drama — real boardrooms dramatised as cinema; mouths closed (no lip-sync) | **Dual-mode (A + B)** | Peter's own broadcast read + Victor (scratch) | **Flagship, launching.** Render side proven; upload token authed. `channel: synthetic` (alias trap). |
| **Lazarus Films** | Dignified cinematic adaptation of public-domain dramatic writing | Mode A narrated (no lip-sync yet) | Single literary narrator (TBD) | **Designed, not built.** Built *on* per-film look overrides. |

**Success Coach economics (illustrative of the factory model):** 5 demand-validated courses × 100 lessons → ~100 videos of 12–20 min, ~$2/100-lesson course to generate. High RPM (~$8–13). Its diagnosis was the seed of the "packaging beats production" thesis.

---

## 5. The production system (the pipeline — the orchestration layer)

**One channel-agnostic orchestrator** runs the whole post-script arc. It reads ONE input and discovers from it what work to do, loads the relevant channel's identity, runs only the legs the content needs around the minimum gates, and produces a finished video — identically for every channel.

**The five design principles:**
1. **The sentence decides the mode.** Each beat is born Mode A (cinematic recreation) or Mode B (Remotion graphic) because the *sentence* decides. Author sets it; the machine never infers.
2. **The voice decides the contract.** Narration/off-camera speech is *swappable* (a timing source); lip-synced on-camera speech is *locked* (a render input). Swappable means a voice swap re-times everything for free (the "true-up").
3. **The composition decides the legs.** Scan the beats → run only needed legs. Always → audio leg first.
4. **The channel header decides the look.** The script declares `channel:`; the orchestrator loads `<channel>/channel.json`. Composition = machinery; channel flag = identity; orthogonal.
5. **Maximal orchestration around minimal gates.** Everything that can run unattended does; the only stops are quality firewalls — **and those stops are themselves now skippable for batch (the `auto` gate-mode, §5.8).**

**The input boundary:** the orchestrator's sole input is `beats_full.json` (header + beats), produced by `parse_script.py` from `script.md`. There is no separate `metadata.json` — the header *is* the YouTube title/description/tags.

**`channel.json` — the complete cross-mode identity (the reusability contract).** A new channel costs one config file and content, not new code. `channel.json` keys: `name`, `voice_id` (snake_case — `voiceId` silently falls back to Victor), `style_suffix` (the default look), `default_motion`, `default_music_prompt`, `base_canon`, the `upload` block, and now the **`thumbnail` block** (§6) and the **`music` block** (§6). The orchestrator resolves it **by the `channel:` header name**, not by where you launched. Adding a channel: create `<channel>/channel.json` (diff its keys against a known-good file first — a single typo silently rendered Victor on the Sacred Dawn first dry-run), set the voice/look/motion/thumbnail/music, and the same machine produces a completely different film.

**The load-bearing architectural principle (a design law): resolve identity explicitly, fail loudly, never assume.** Subprocesses don't inherit the interactive shell's environment (hit on REMOTION_DIR, node PATH, and — 17 June — on `FAL_KEY`/`ANTHROPIC_API_KEY` not being exported into a fresh shell: the `.env` exists but must be `set -a; source .env; set +a`'d before a standalone script run, and the orchestrator's subprocess must have them in its environment too). Don't assume a config key's casing (`voice_id`/`voiceId`). Don't assume a default label is the truth. Every one of these was the same bug: an identity assumed instead of resolved.

**The legs (run order):**
- **audio_leg** (always, first): Inworld VO → Whisper align → `durations.json`. + audio-continuity QC. Then the **audio gate** (keep / swap-in-human-read).
- **modeb_leg** (if Mode B beats): `dispatch.py` → Remotion render → **Mode B correctness gate**.
- **modea_leg** (if Mode A beats): `modea_beats.py` → Flux stills → **stills review gate** → tiered animate (Kling front-N, free Ken-Burns floor).
- **convergence_leg**: pool clips → `assemble_episode.py` (interleave in true beat order via `_index.json`, hold each to audio-measured duration, **mux the crossfaded music bed**, §6) → `final_video.mp4` → **thumbnail step** (`_maybe_thumbnail()`, §6) → **upload** (`upload_episode.py`, §5.5/§5.7).

**The two gates** (the only human stops): **stills review** and **Mode B correctness** — both bypassed by the `auto` gate-mode in batch runs (§5.8).

**`durations.json` is the single timing source.** Produced once by the audio leg; consumed by dispatch, assemble, and the Mode B review.

**`recreation_pipeline.py` is the shared engine** — generate_voiceover (Inworld), stills (Flux), finish/animate (Kling), assemble (ffmpeg). *Standalone animate-recovery: from the project dir, `python ~/Pipeline/shared/recreation_pipeline.py finish --project modea --animate-only` re-spends nothing already done. Run long box jobs in tmux.*

**Per-job decade look (the look resolver, Phase 1):** look resolves channel-then-project; `look_resolver.py` walks up from the still's output path. Registry of decade looks. Phase 2 (the grade layer, `film_emulate.py`) not built.

**Batched multi-video jobs:** a script can hold several self-contained parts, run as ONE job, cut into N videos in post. Constraint: one look per job. A batched job (`header.parts > 1`) must **exit at `final_video.mp4`** and not auto-upload. (Distinct from the BATCH RUNNER, §5.8, which runs many separate single-video projects unattended.)

### 5.1 Mission Control — the operator console

The browser surface on `:8002` (service `mission-control.service`): channel dropdown → project dropdown → **Launch** → gates-as-page-state → per-beat storyboard grid → tiered render → assemble → Reset. URL-persisted, in-place clip reload, skip-existing resume. Live status line (counts off disk). A1 heartbeat + false-hang fix (§5.4). Version stamp (`v0.X · <sha>`; must equal `git rev-parse --short HEAD` on the box). FINAL VIDEO panel (§5.5) with aligned Re-assemble + live Upload (private-only). **Currently v1.9.** *Open (§5 backlog): the panel does NOT yet capture thumbnail text at create time or preview the generated thumbnail at review time — the batch path has the thumbnail, the panel path doesn't (Tier-3 #11).*

### 5.2 Tiered render — the fixed per-video cost limiter

The animate step routes per beat: **first N beats Kling** (~$0.42/clip), **the rest free Ken-Burns floor** (`ken_burns_still()`). At N=40 that's a fixed ~$16.80/video regardless of length. N is set per project (the **Kling clips: N** field at the stills gate, or `render_policy.json` `{"kling_count":N}`, or `--kling-count N`; default 40). **A channel can set N=0 for an all-Ken-Burns lane (~$3/video)** — Prehistoric Disasters runs this way; the batch runner writes `render_policy.json {"kling_count":0}` into every project. Banked 17 June across three lanes (mythology, death, prehistoric): the cold-start winners win on **packaging + topic + cadence, not motion** — motion is a brand tiebreaker, not a growth driver, so served-evergreen lanes should run Ken-Burns-only and convert the saved Kling spend into cadence. *Split is positional; v2 routes by which beats earn motion.*

### 5.3 Motion direction — per-beat field + per-channel default

Each beat carries a `motion_prompt`. Layers: interactive per-beat field on the storyboard + per-channel `default_motion` in `channel.json`. **FIXED 16 June** (`patch_modea_beats_motion_omit.py`): the dead-default lived in the PRODUCER (`modea_beats.py translate()` stamped every non-face-hold beat), so the consumer's correct fall-through never fired. Fix: `translate()` OMITS `motion_prompt` on normal beats. **Durable principle: a per-channel default is dead if any upstream step unconditionally fills the field it defaults — make "nothing authored" representable as ABSENT, not a placeholder.** (Ken-Burns floor clips ignore motion, so on an all-Ken-Burns channel this is moot — but it stays correct for any channel that turns Kling on.)

### 5.4 A1 — heartbeat, false-hang fix, dead-run detection

`set_phase("animating")` between the gate clearing and the animate loop (a healthy run no longer looks hung at the gate). `set_phase` stamps `heartbeat`; `await_gate`'s poll loop pulses every 1.5s. `build_state` flips a silent gate run to `stale` after 300s. Stale-detection covers gate phases only.

### 5.5 FINAL VIDEO panel — the upload surface

On `done`, the panel shows the assembled video autoplaying, title/description/tags from the header, a Download button, the aligned Re-assemble button, and a **live Upload button** (v1.9, private-only — shells `upload_episode.py --privacy private`; can never publish). `/api/upload` + `/api/upload_status` mirror the Re-assemble fire-and-poll pattern.

### 5.6 Artifact locations — root vs. modea

**Root-level artifacts live at the PROJECT ROOT** — `voiceover.mp3`, `final_video.mp4`, `durations.json`, `_index.json`, `render_policy.json`, `music.mp3`, **`thumbnail.json`, `thumbnail.png`, `thumbnail_still.png`, `thumbnail_selection.json`, `thumb_candidates/`**; only `stills/`, `clips/`, `storyboard.json` live under `modea/`. (Note: stills can sit deeper — Sacred Dawn's were at `<project>/modea/stills/`, confirmed 17 June. The channel-resolution walk-up climbs parents to find `channel.json`, so it works from either level.) Any code taking the engine-form `--project <slug>/modea` must step up one level for the root artifacts.

### 5.7 The v1.2–v1.9 arc — aligned re-assemble, reliability, live upload

**Two assemblers, only one aligned.** `assemble_episode.py` (iterates BEATS, places each via `_index.json`, holds to the FROZEN `durations.json`) is alignment-correct and is what convergence uses. `recreation_pipeline.assemble()` (positional `zip`, ignores `_index.json`) **drifts**. **Anything that assembles MUST use `assemble_episode.py`.** `finish --assemble-only` (calls the unsafe one) is a CLI footgun, un-retired (backlog).

**Run-record liveness is three signals:** phase, heartbeat (gate-phase), pid-alive. A: freshest LIVE run by `started_at`. B: launch refuses if a run is live (409). C: `build_state` reaps a non-terminal record whose pid is dead. `_TERMINAL_PHASES = ("done","stopped","error","stale","dead")`.

### 5.8 The unattended batch path (shipped 17 June)

The launch path for fully-automated channels: scripts + thumbnail specs in an inbox → private packaged videos out, no human at any gate. Three pieces:

- **`auto` gate-mode** (`patch_gate_auto.py`): `await_gate(ctx, ...)` gained a third branch beside `cli` and `job`. When `ctx["gate_mode"] == "auto"` it returns the accept default — `ctx["auto_decisions"][name]` if set, else `options[0]` (which is the proceed path for both real gates: `keep` for audio, `go` for stills) — with no prompt and no poll. One edit makes every gate (and any future gate) non-blocking.
- **`--unattended` flag** (`patch_orchestrate_unattended.py`): adds `auto` to the `--gate-mode` choices and a `--unattended` flag that, right after `parse_args()`, forces `gate_mode=auto` + `live=True` + `log="normal"` — so both kickoff `input()` prompts are skipped and no gate blocks.
- **`run_batch.py`**: for each `<name>.md` + `<name>.thumb.json` pair in an inbox folder, calls the REAL `ingest.create_project()` (so batch projects are byte-identical to panel projects — same mkdir, `script.md`, parse, and crucially the same **verify-refuse on wordless/missing-VISUAL beats**, the guard you want most when no human is watching), then writes `render_policy.json` (`kling_count`, default 0) + `thumbnail.json`, then runs the orchestrator `--project <name> --beats <beats_full.json> --unattended`. Sequential (no human watching → don't want N concurrent fal/Inworld bursts), per-project try/except isolation, manifest log. `--plan` mode is a zero-spend prep preview. The orchestrator reads the channel from the script HEADER, not a `--channel` flag.

Input layout: one inbox folder, matched pairs by basename (`toba.md` + `toba.thumb.json`); a `.md` with no sibling `.thumb.json` is skipped with a warning (a half-prepped inbox can't ship a thumbnail-less video). Proven end to end on Toba 17 June. *Scheduling is deferred and belongs in `upload_episode.py` (`--publish-at`), with the runner passing a per-project datetime (Peter's design: every 6h from the latest).*

---

## 6. The tech stack (the fast layer — swappable)

- **Stills:** fal.ai Flux-pro/v1.1. (Pass `safety_tolerance:"5"` to stop silent ~7KB black-PNG rejections.)
- **Animation:** fal Kling (O3 Standard) for the front *N* beats; **free Ken-Burns floor** (ffmpeg zoompan) for the rest — the tiered-render cost limiter (§5.2). **The animatable-foreground rule** is upstream (ante-machinam Constitution §7). On all-Ken-Burns channels the whole video is the floor (~$3).
- **TTS:** Inworld. *(Model-string contradiction unresolved: doc `inworld-tts-1.5-max` vs code `INWORLD_MODEL = "inworld-tts-2"` — verify against the box.)* Voices: Victor (Final Hours/Synthetic/hooks/**Prehistoric Disasters**), Elliot (Sacred Dawn), Ashley (Success Coach), Vinny (You Had To Be There). `voice_id` snake_case.
- **Alignment:** Whisper → word timestamps.
- **Mode B graphics:** Remotion (Node 20.20.2, Remotion 4.0.472). Six components.
- **Assembly:** ffmpeg (streaming concat demuxer). `ffprobe` is the only reliable clip-duration source. **The final concat/encode (`-preset medium -crf 18`) is the single heaviest step** — ~20 min for a 20-min Ken-Burns video on the 16GB box (no GPU). For Ken-Burns lanes `-preset fast/veryfast` would roughly halve it with no visible loss (backlog Tier-4 #18) — the biggest batch-throughput lever.
- **Music — CURATED PER-CHANNEL FOLDER (decided 17 June, chosen over fal-generated).** A folder of tracks at `<channel>/music/`; the assembler's **`--music-dir` path** (`patch_music_dir.py`) picks N random tracks (default 3), **crossfades the joins** (`acrossfade`, default 2s — stops the track-changes sounding like a playlist skip), loops the crossfaded sequence to fill the voiceover, and feeds the EXISTING amix mux at **VOICE_LEVEL 1.15 / MUSIC_LEVEL 0.07** untouched. Driven by a `channel.json` `music` block: `{"dir":"music","tracks":3,"crossfade_seconds":2,"level":0.07}` (`patch_convergence_musicdir.py` wires convergence to pass it). Random-N gives variance across renders (two videos won't share a bed). The standalone `make_music.py` (fal-generated single bed) is **superseded** for production by this curated path — a hand-picked library of mood-matched beds beats generated music for atmosphere-not-melody documentary scoring, at zero per-video cost. (Final Hours / Sacred Dawn's earlier Jamendo single-bed at the same levels is the precedent this generalises.) Prehistoric Disasters has 8 ominous deep-time beds loaded.
- **Thumbnails — AUTOMATED, IN-PIPELINE (shipped + locked 17 June).** The thumbnail is generated, selected, and overlaid as a convergence step before upload, fully unattended:
  - **`select_thumbnail_still.py`** renders **N=2** Flux candidates from the per-project `thumbnail.json` `subject` field (+ the channel's `candidate_prompt_suffix` + `style_suffix`), then a **Sonnet-4-6 vision call** judges them *as thumbnail substrate* on the channel's `selection_rules` (clean negative space where the headline lands, strongest catastrophe-at-a-glance, no garbled detail) and picks the best. Fail-safe to candidate 1. Logs the verdict to `thumbnail_selection.json`. (Proven: it correctly rejected a candidate whose bright sky bled into the headline zone.)
  - **`make_thumbnail.py`** overlays the locked house look (deterministic typography — NOT generative; text is a Pillow layer, never baked by Flux, because image models can't render legible type). Two composition modes: `centered_subject` (head-poke-through, rembg on) and `low_silhouette` (text in a corner, rembg off). The locked Prehistoric look: a **left gradient scrim** for text contrast (`scrim:{side,width,opacity,feather}`) instead of global darkening (the fix for the image washing out under the text — **bank: darken only where the text lands, never the whole frame**), `darken_factor 1.0` + `vignette 0` (image at full brightness; the scrim does the contrast), independent `margin_x`/`margin_y`, heavy stroke + drop shadow, near-white title / amber subtitle. Anton font with DejaVu/Impact fallback.
  - **`_maybe_thumbnail()`** (`patch_convergence_thumbnail.py`) runs both before `_maybe_upload()`; reads `thumbnail.json`, fails soft (no spec / error → skip), produces `thumbnail.png` which `upload_episode.py` already attaches.
  - **The doctrine (banked, §9):** design the thumbnail WITH the script — one authoring moment, the packaging decided alongside the words (matches Peter's Clickly-while-speccing habit; Clickly is the *concept/headline testing ground*, the pipeline *produces* the locked-look asset). But store it as a separate `thumbnail.json`, NOT in the script header — the YouTube title (full, SEO) and the thumbnail headline (short, punchy) are different strings. The pair (`.md` + `.thumb.json`) travels together; the separation is the architecture. The text never travels as a passed variable — written once at prep, read once at the end, so nothing in the middle can corrupt it. For the batch, each topic needs its `.thumb.json` authored alongside its script (the `prehistoric-slate-19.md` "thumbnail concept" lines are the seeds). **Silhouette flag:** the "tiny human for scale" motif works for human-era topics but is an anachronism for pre-human deep-time — swap the scale anchor to a lone tree/creature/boat per `thumbnail.json` subject.
- **Publish/upload:** `shared/upload_episode.py` — the ONE channel-agnostic uploader (header=metadata, channel folder=identity). One Google account (`peteralkema2@gmail.com`); one shared OAuth client, **published to Production** so refresh tokens don't expire. Each channel has its own `token.json` (binds to the channel picked in the OAuth chooser). **Six recreation channels authed** + bindings verified: Final Hours, Sacred Dawn, You Had To Be There, Synthetic Press, Scripture On Screen, **Prehistoric Disasters**. (Success Coach is on a separate account.) `--auth-only` mints/refreshes a token on the laptop (needs a real `--project` dir to satisfy its `is_dir()` check — use an `_authstub` project folder if none exists yet), then `scp token.json` + `client_secret.json` to the box. **NEW-CHANNEL HARD GATE: an unverified YouTube account rejects uploads >15 min at processing ("Processing abandoned"). Verify the account (youtube.com/verify, phone) before the first long upload — see §12.**
- **Research/analytics:** NexLev MCP (`search_niche_finder_channels` with `isFaceless:true`, `sortBy:outlierScore` is the reliable breakout-finder; `search_videos` is unreliable for descriptive queries — use `get_similar_videos` seeded from a known video instead). Google Trends as a manual radar.
- **Thumbnails (manual/concept):** Clickly for testing headline wording + concept before locking the `thumbnail.json` values.

---

## 7. Infrastructure & workflow discipline

- **Box:** Hetzner `pipeline-prod` at `116.202.18.68`, SSH port 443, user `peter`, venv `~/venvs/pipeline/bin/activate`, 16GB RAM. Repo at `~/Pipeline`. **Before any standalone script run that touches fal/Anthropic/Inworld, load the env: `set -a; source .env; set +a`** (a fresh shell does not have the keys exported; the `.env` holds them).
- **Repo:** `github.com/peteralkema/Pipeline`. Laptop clone `~/Projects/Pipeline`.
- **The strict workflow (non-negotiable):** all code edits on laptop → GitHub → box via **idempotent `patch_*.py` scripts** (or full-file rewrites for deletion-heavy/prose changes); config changes via a `python3 -c` JSON one-liner (Peter doesn't hand-edit); `git pull --no-edit` before every push; **never hand-edit on the box**; verify on box after pull. LAPTOP uses `python3`; BOX uses `python` inside the venv. Terminal identity: `peter@pipeline-prod` = BOX, `peteralkema@NL-L-…` = LAPTOP. *(Recurring failure mode: running a BOX command block on the LAPTOP — `cd ~/Pipeline` fails. Always confirm the prompt first.)*
- **Patch discipline that works:** each idempotent patch verifies its anchor exists exactly once and refuses to half-apply; backs up to a `.pre_*` sidecar; sentinel string makes re-runs no-ops. Patch source stays pure ASCII. **When a patch references a variable in the target (e.g. `channel_dir` in convergence), confirm it exists before relying on it — flag the assumption.**
- **scp media files** (run from the LAPTOP, capital `-P`): `scp -P 443 peter@116.202.18.68:~/Pipeline/<channel>/projects/<slug>/final_video.mp4 ~/Downloads/`. A box-to-itself scp fails (publickey) — media-pull commands run on the laptop, not the box.
- **Channel/config resolution is project-anchored.**
- **Long box jobs run in `tmux`.**

---

## 8. Authoring craft (before the machine)

**`ante-machinam.md` (v3.x) is the craft companion — the single source of truth for authoring.** This reference = the system; ante-machinam = the craft (the Constitution, the VISUAL-line patterns, the retention canon, the channel briefs).

**The Constitution (seven machine-enforced truths):** every beat carries spoken words (wordless beats halt the build); the header carries channel/title/description/tags and `channel` must match the folder; spell out numbers in narration; one `VISUAL:` line per Mode A beat; lock the script first; beat granularity ~5–12s spoken (~15–35 words), hard ceiling ~55 words; every beat carries an animatable foreground subject.

**Script format (the exact shape `parse_script.py` accepts — banked 17 June):** a **bare key:value header** (NO `---` YAML fences), then `## COLD OPEN` / `## PART …` / `## NUMBER …` **double-hash** section headers, then each beat as **`[A] <narration on one line>`** followed by **`VISUAL: <prompt>`** on the next line, blank line between beats. Authoring from the doc's prose description instead of copying a working script's exact markup produced a ZERO-beat parse (YAML fences + single-`#` headers + `NARRATION:` labels → ZeroDivisionError). **The reusable fix and the rule: copy a known-good script's structure and swap the content; never author the markup from memory.** A mechanical reformatter (strip fences, `#`→`##`, reorder VISUAL/NARRATION into `[A]`+`VISUAL:`) is the converter pattern for bulk-prepping scripts.

**Pacing reality:** Inworld reads ~190–200 wpm. BUT **runtime is beat-floored, not words-only (banked 17 June):** the Ken-Burns minimum hold stretches short beats, so real runtime ≈ **~14s/beat**, longer than the word count predicts. 88 beats → 20.7 min measured (a words-only estimate would have said ~13). A ~28-min words-estimate script lands closer to ~40 min. Estimate runtime from beat count × ~14s as a sanity check, not from wpm alone.

**Visual/VISUAL-line patterns:** faceless by default; scene canons over character canons; object-substitution for groups; fire/catastrophe as environment not subject; period-accuracy guards; image models can't render legible text (a Mode B card's job — and the reason thumbnail text is a deterministic overlay, not baked).

---

## 9. Strategic principles (the durable lessons)

1. **Packaging beats production** (CTR + AVD in 48h drive distribution). **Corollary (banked 17 June): in served-evergreen cold-start lanes the winners win on packaging + topic + cadence, not motion or render craft** — confirmed by watching the breakout competitors across three lanes (mythology, death, prehistoric); they run mostly Ken Burns / slideshow. So a tier-above pipeline is over-built for these lanes on the motion axis; convert the saved Kling spend into cadence, and compete on packaging.
2. **The system is the moat, not any channel.**
3. **Un-filmable vs. re-watchable** (the niche-fit filter). **3b. The un-referenced sublime** — the decisive test for a new channel: is there a reference the audience can catch us failing against? No-reference (scripture, mythology, deep past, imagined future, **deep-time prehistory**) = open water; the engine does what only it can. Prehistoric catastrophe passes this hard — no footage of the Toba eruption exists, so the AI image isn't competing with a photo it can be caught failing against.
4. **Served vs. searched.**
5. **Spike-chasing doesn't suit this operation** — the edge is best-execution in permanently-warm, evergreen, served lanes. **Lane strategy over spike-chasing: ride the lane, not the individual viral moment.**
6. **Title and thumbnail must complement, not echo** — image carries the "what," title the "why-click."
7. **Topic clusters beat topic variety; ship first, optimise second; volume generates data — but learn from one before betting on twenty.** The machine makes each at-bat cheap *so that* you can read one video's first-48h data before authoring the next nineteen. Authoring a full batch before any retention curve exists is the trap this principle guards against.
8. **Two-audience nostalgia thesis** (You Had To Be There).
9. **Attribution discipline as moat** (Sacred Dawn).
10. **The front-loaded effort curve** — spend the expensive signal (Kling) on the front ~40 beats where the retention decision is made, floor the rest. Fixed per-video motion budget. (On an all-Ken-Burns channel the budget is the floor everywhere; the principle still says *if* you turn Kling on, spend it on the front.)
11. **Name and package for the promise the machine can actually keep** (fidelity-of-intent over fidelity-of-detail).
12. **Thumbnail doctrine** (banked 17 June): the thumbnail is packaging, authored WITH the script as one act; the text lives in its own artifact (`thumbnail.json`), not the script header; the look is locked per-channel in `channel.json` and never fiddled per-video (consistency is the brand, your attention is the scarce resource); and for legible text over a bright image, **darken only the text zone with a directional gradient scrim, never the whole frame.**

---

## 10. Current state (17 June 2026)

**Live channels:** Final Hours (primary), Sacred Dawn, You Had To Be There, **Prehistoric Disasters (new, fully automated)**, Success Coach. **Six recreation channels now upload on non-expiring Production tokens.**

**Shipped 17 June (the Prehistoric Disasters end-to-end session):**
- **A whole new channel stood up and proven in one session** — `@PrehistoricDisasters`, Ken-Burns-only (~$3/video), Victor voice, locked thumbnail look, 8-track curated music library, banner art. First video (Toba, 88 beats, 20.7 min) rendered → packaged → uploaded private via the batch runner. Only YouTube's 15-min unverified-account cap stopped publication ("Processing abandoned").
- **Automated thumbnail pipeline** (§6) — Flux N=2 candidates → Sonnet-4-6 selects the best substrate on CTR rules → locked Pillow overlay (scrim, margins, house look) → `thumbnail.png`, wired into convergence before upload. Tuned + LOCKED.
- **Unattended batch runner** (§5.8) — `auto` gate-mode + `--unattended` + `run_batch.py` (via the real `ingest.create_project`). Proven `--plan` then `--limit 1`.
- **Music into convergence** (§6) — curated per-channel `--music-dir` (random-N + crossfade + loop), driven by a `channel.json` `music` block. Resolves the long-open generated-vs-curated decision in favour of curated.
- **Deliverables:** `prehistoric-slate-19.md` (ranked 19-topic queue), `toba-full.md` (expanded ~28-min version held for the real publish).

**Open (top of next):** verify the Prehistoric account + publish Toba (the one external gate); ship Chicxulub as ep2; read ep1+ep2 first-48h CTR+AVD before authoring the other 18. The standing read holds: ship real videos on the proven economics and let the data drive what's next — not grind the backlog.

**Specs written, not built:** decade-look Phase 2 (grade layer); Mission Control thumbnail integration (panel create-flow capture + review-time preview); per-project `publishAt` scheduling.

---

## 11. Roadmap & backlog

See `__MASTER-WORKLOG.md` for the live prioritised backlog. Near-term: verify+publish Toba and ship Chicxulub (Tier 1); the Mission Control thumbnail panel integration (Tier 3 #11, the manual-workflow half of the thumbnail system); the faster-encode lever (Tier 4 #18, biggest batch-throughput win); per-project scheduling (Tier 3 #16). **Long horizon:** sustained-character continuity → multi-scene narrative arcs → layered/multi-voice audio → a "cinematographer in the system." Endpoint (~2029–31): a single operator ships a 75-minute film through this pipeline for a few hundred dollars.

---

## 12. Quick-reference facts & gotchas

- **Paths:** box repo `~/Pipeline`; laptop `~/Projects/Pipeline`; venv `~/venvs/pipeline`; channels at `<channel>/`, projects at `<channel>/projects/<slug>/`.
- **Load the env before standalone runs:** `set -a; source .env; set +a` (a fresh shell lacks `FAL_KEY`/`ANTHROPIC_API_KEY`/`INWORLD_API_KEY`; the `.env` has them). Subprocesses launched by the orchestrator must also have them exported.
- **NEW-CHANNEL 15-MIN CAP (hard gate):** an unverified YouTube account rejects uploads longer than 15 minutes at processing — the video uploads, then shows "Processing abandoned — video too long." Fix: verify the account at youtube.com/verify (phone), then re-run the upload (no re-render needed). **Add account-verification to the new-channel setup checklist** — this bit the Prehistoric launch after a full render.
- **No `modea/` folder = an un-rendered project, NOT a broken one.** Stills can live at `<project>/modea/stills/` (deeper than the project root).
- **Channel header traps:** `final_hours` → `final-hours/`, `sacred_dawn` → `sacred-dawn/` (auto-resolved); a true alias does NOT — Synthetic must use `channel: synthetic`. Prehistoric uses `prehistoric-disasters` (slug = header = folder, no trap).
- **channel.json:** `voice_id` is snake_case (`voiceId` → silent Victor fallback); keys are `name`/`voice_id`/`style_suffix`/`default_motion`/`default_music_prompt`/`base_canon`/`upload`/**`thumbnail`**/**`music`**. Diff a new one against a known-good file before first run.
- **Script format:** bare key:value header (no `---`), `##` double-hash sections, `[A] narration` + `VISUAL:` per beat. Copy a working script's shape; don't author markup from the doc. A bad format parses to zero beats → ZeroDivisionError. Verify with `parse_script.py <md> --json /tmp/b.json --json-full /tmp/f.json` (zero-spend) before any run.
- **Runtime ≈ beat count × ~14s** (Ken-Burns floor stretches short beats), not words-only wpm. 88 beats → 20.7 min.
- **Thumbnail:** per-project `thumbnail.json` `{subject,title,subtitle}`; channel look locked in `channel.json` `thumbnail` block; Sonnet picks the best of N=2 candidates; text is a deterministic overlay (scrim for contrast, not global darkening). Silhouette motif = human-era only; swap the scale anchor for pre-human topics.
- **Music:** `channel.json` `music` block `{dir,tracks,crossfade_seconds,level}`; tracks in `<channel>/music/`; filenames must have no spaces (normalize to `track_NN.mp3` — `acrossfade`/concat choke on spaces); random-N crossfaded bed at MUSIC_LEVEL 0.07.
- **Batch runner:** inbox of `<name>.md` + `<name>.thumb.json` pairs; `python shared/run_batch.py --inbox <dir> --channel <ch> --plan` (zero spend) then `--limit 1` then full; `ingest.create_project` refuses if the project already exists (so re-running a partial inbox needs manual cleanup).
- **`ffprobe`, not the player**, for true duration.
- **OAuth:** one Google account `peteralkema2@gmail.com`; Production app (non-expiring); per-channel `token.json` bound to the channel picked in the chooser; mint via `upload_episode.py --project <ch>/projects/<x> --auth-only` on the LAPTOP (needs a real project dir — use an `_authstub` if none exists), then `scp token.json` + `client_secret.json` to the box. Six channels authed.
- **Mission Control:** `http://116.202.18.68:8002/?key=fh2026`, `mission-control.service`, **v1.9**; version-check the heading SHA against `git rev-parse --short HEAD`.
- **Final encode is the slow step** (`-preset medium`, ~20 min for 20-min Ken-Burns video, CPU-bound). `-preset fast/veryfast` would halve it on Ken-Burns lanes — the biggest batch-throughput lever.
- **Two assemblers:** only `assemble_episode.py` is alignment-safe; `finish --assemble-only` drifts.
- **Mac-only SSL:** monkey-patch `httpx.Client.__init__` to `verify=False` before fal imports; not needed on the box.

---

## 13. Surviving box commands (the terminal gaps the console hasn't closed yet)

- **SSH + venv + env:** `ssh -p 443 peter@116.202.18.68` → `source ~/venvs/pipeline/bin/activate` → `cd ~/Pipeline` → `set -a; source .env; set +a`.
- **scp the final video to the laptop** (run from the LAPTOP): `scp -P 443 peter@116.202.18.68:~/Pipeline/<channel>/projects/<slug>/final_video.mp4 ~/Downloads/<name>.mp4`.
- **Auth / token-minting (one-time per channel):** `upload_episode.py --project <ch>/projects/<x> --auth-only` on the LAPTOP (pick the matching channel) → `scp token.json` + `client_secret.json` to the box → verify the binding. Then verify the YouTube account (15-min cap) before the first long upload.
- **Batch runner:** `python shared/run_batch.py --inbox ~/batch_inbox --channel <ch> --plan` → `--limit 1` → full.
- **Standalone thumbnail test:** `python shared/select_thumbnail_still.py --project <p> --channel <ch> --subject "…"` then `make_thumbnail.py --project <p> --channel <ch> --title "…" --subtitle "…"` (free overlay re-runs to tune).
- **Standalone music test:** re-run `assemble_episode.py … --music-dir <ch>/music --music-tracks 3 --music-crossfade 2 --out <test>.mp4` (free re-mux, clips cached).
- **Mission Control service:** `systemctl --user restart mission-control.service` after any page change.

---

*This document is the umbrella reference for the whole operation, and one of just two living docs: **this reference (the system)** and **`ante-machinam.md` (the craft)**. Update this file's date + current-state + backlog whenever a session banks something that changes the shape of the operation.*
