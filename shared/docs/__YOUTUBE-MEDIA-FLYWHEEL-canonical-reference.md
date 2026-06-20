# YouTube Media Flywheel — Canonical Project Reference
*The single comprehensive description of the whole operation. Load this first in any new session to get to full context fast.*
*Maintained by Peter + Claude. Last updated: 21 June 2026 (THE READ-SIDE SESSION. Built `dump_channel.py` — a channel-agnostic READ-ONLY YouTube metadata mirror (§5.10): per-channel `channel_dump.json` committed to the repo so the whole portfolio's schedule/metadata is queryable, plus a local-time schedule view and a `--cadence` post-batch verifier for the "post every day, forever" rule. Caught a real orphan from the 19 June batch-of-batches teething — a finished, scheduled, never-reviewed video (the Lady Be Good bomber) queued to auto-publish — and a same-instant collision, both fixed. Banked the operating philosophy on scale vs craft (§2A, up front) and a cluster of analytics laws (§9 #14–#19) from a competitor + Sacred Dawn retention read. Doc set is two: this reference = the system; `ante-machinam.md` = the craft.).*

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

## 2A. Scale, craft, and what wins on YouTube — the operating philosophy

*Banked 21 June 2026, up front by request. The synthesis that resolves the central anxiety of an industrialising solo factory: "do I scale, or do I respect the craft?"*

**The tension is false.** Scale-vs-craft is not a dial to balance. YouTube's enforcement (the "low-effort / spam" bans) does not fall on *automated* content — it falls on *low-value* content. Those are different axes entirely. The platform cannot tell whether a video was assembled by a Python pipeline or a human in Premiere; it reads only the signals that stand in for value — retention, satisfied watch-time, returning viewers, the absence of "not interested." A good story well told does not become spam because ffmpeg stitched it; eleven generic videos nobody finishes are spam despite human effort. So there is no line "how much do I automate before I cross it." The only question is ever: **does the output earn its watch-time?** Automation is neutral on that.

**Therefore: automate the labour, concentrate the craft.** Industrialise the parts that do NOT carry the value — rendering, assembly, scheduling, uploading, the cadence/observability checks — *precisely so* scarce attention pools where value is created: the script, the channel's specific look/prompting, the packaging, the batch-to-batch retention read. A human doing ffmpeg by hand isn't honouring craft; they're spending craft-attention on a mechanical task and will burn out at eleven videos like Wealth Pilot. The machine is what *lets* you be high-effort where effort converts. Scale and craft are not a compromise — automation is the only configuration in which craft survives at scale.

**The actual moat is the learning loop, not the pipeline.** Competitors with cruder stacks win (Dark Ledger, a manual-2D-animation finance channel, was putting up 900K videos on a stack you'd find primitive). Volume alone loses (the graveyard channels had volume). The durable edge is a loop that improves packaging faster than a manual operator can: **every batch teaches the next.** Automation buys the reps; a human reading the first-48h signal and feeding it back is what makes the reps *compound* instead of merely *accumulate*. The effort goes into the loop, not the labour.

**Craft-attention is the bottleneck, not compute — so diversify production, concentrate craft.** Marginal compute per channel is ~free; marginal *packaging-iteration attention* is not, and it does not parallelise across unrelated niches (the retention levers for Sacred Dawn are not the levers for a finance channel). Run the wide channel book — let the machine keep all six alive at near-zero cost so none die the Wealth-Pilot death — but pick ONE channel per cycle as the craft-focus where you actually read the analytics and iterate packaging hard, and rotate that focus toward whichever channel first shows a vein. **Explore-then-exploit:** the machine lets you put horses in the race with no jockey, then assign the jockey to whoever pulls ahead. Diversify *topic risk* (you don't know which lane has the vein) without paying craft-attention on all lanes at once. Spreading the *bets* is right; spreading the *attention* is the trap.

**Promote on a vein, not a spike.** The explore→exploit handoff is only as good as the definition of "winning." A single big number is a spike trap (see §9 #16 — a channel that looked like a 105K-average machine was one 2.4M hit over a ~3K median). The trigger to concentrate attention on a channel is **demonstrated packaging *repeatability*** — two or three videos clustering above the channel's own baseline on the *same* packaging structure in the first-48h window — not peak views. Higher, slower bar; holding it is the discipline.

**Cull without sentiment.** A channel that won't retain after a genuine run with real packaging iteration is consuming roster-attention it hasn't earned. Keeping it is sentimentality, not strategy (Success Coach is already that conversation — excluded from the read-side dump without flinching). Concentrate where the loop compounds; cut where it's flat.

**The real risk at scale is not over-automation — it's shipping what no human reviewed.** This session's orphan proved it: the 19 June batch-of-batches left a finished, scheduled, never-seen video (the Lady Be Good bomber) queued to auto-publish — found only by accident. At volume, the danger is review being outrun: a video publishing without its Altered/AI-content flag (a Studio-UI-only toggle the API cannot set or read — §12), a packaging regression nobody caught because "the batch ran fine." **Craft and safety are the same principle: nothing publishes that a human didn't see.** Build the machine to produce abundantly AND to gate on human review; then scale, craft, and safety are one posture, not three competing ones.

**The whole philosophy in one line:** *automate the labour, concentrate the craft, gate on review, cull without sentiment* — four expressions of a single idea. Not a tightrope between scale and quality; the only kind of machine where quality is what scales.

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
| **Prehistoric Disasters** (@PrehistoricDisasters) | Cinematic deep-time catastrophe documentary — the prehistoric disasters that almost ended humanity (supervolcanoes, floods, ice ages, extinctions); the hottest faceless cold-start lane, purest un-filmable-by-definition fit | Mode A, **Ken-Burns-only** (`kling_count:0`, ~$3/video) | Victor | **LIVE, fully automated.** Stood up + published 17 June: locked `low_silhouette` thumbnail, curated music, batch-runner-produced, Victor at 0.9. **Two videos public** (Toba ep1, Chicxulub ep2). 19-topic slate queued; read ep1+ep2 first-48h data before authoring the rest. Lane benchmark: Wild Horizons (§9 #13). Full doctrine: `_Prehistoric-Disasters.md`. |
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

### 5.9 The batch-of-batches — many channels, one launch (shipped 19 June)

`run_batch.py` (§5.8) ships one channel's inbox. **`run_all_batches.py`** ships *every* channel's inbox in one launch — a thin sequential driver over `run_batch.py` so a multi-channel release doesn't have to be kicked off by hand. All the real work still happens inside `run_batch.py`; the batch-of-batches just loops it.

**The two-level model:** a **batch** = one channel's `batch_inbox` → N videos; a **batch-of-batches** = a list of channels each run as its own batch, **one after another in sequence** (`run_all_batches.py --plan-file <plan>`). Sequential, never parallel — no human watching, and N concurrent channels would mean N concurrent fal/Inworld/encode bursts on a 16GB box. A 4-channel / 20-video run is one long sequential job — run it in `tmux`.

**The inbox convention (the contract):** every channel owns its inbox at **`<channel>/batch_inbox/`** — the channel-local folder of `<name>.md` + `<name>.thumb.json` pairs, so a channel runs identically standalone or inside the batch-of-batches. Create the folder for every channel even if it sits out a run.

**The plan file (`batch_plan.json`):** the driver reads a JSON config so the *script never changes*; you edit the plan (via a `python3 -c` one-liner). Each entry: `channel` (required — must match the channel FOLDER and the `channel:` header inside that channel's scripts), `inbox` (`<channel>/batch_inbox`), `kling_count` (default 0), `publish_start` (ISO-8601 **with tz offset**; omit for private-immediate — each channel carries its OWN start), `publish_interval_hours` (default 12), `limit`, `skip`.

**Invocation — always `--plan` first:**
```
python shared/run_all_batches.py --plan-file shared/batch_plan.json --plan   # dry: every channel, zero spend, prints each calendar
python shared/run_all_batches.py --plan-file shared/batch_plan.json          # real, all active channels in sequence (tmux)
python shared/run_all_batches.py --plan-file shared/batch_plan.json --only <channel>   # one channel
```
`--plan` passes through to each `run_batch.py` (prep preview, no spend) and doubles as a readiness check: a missing/empty inbox or bad plan shows up as a per-channel ✗ with zero spend. **But `--plan` does NOT validate slugs** — it skips the real `create_project`, so a bad filename (see below) sails through as "planned" then prep-fails at real-run time. Run a slug scan before spending: `for f in <inbox>/*.md; do basename "${f%.md}" | grep -qE '^[a-z0-9][a-z0-9-]*$' || echo BAD; done`. (Backlog: fold `validate_slug` into `--plan`.)

**Failure isolation + manifest:** each channel runs in its own try/except; one channel failing is logged ✗ and the driver moves on. Combined `all_batches_manifest_<ts>.json` + ✓/✗ summary; exits non-zero if any failed. (Note: an empty inbox reports ✗ "no .md scripts" — that's "nothing pending," not a breakage.)

**Banked operational lessons (19 June, from the first real multi-channel run):**
- **Slug rule — `^[a-z0-9][a-z0-9-]{0,60}$`.** Project slugs (filenames) must be lowercase letters/numbers/hyphens, start alphanumeric, no underscores, no `NN_` prefixes — `create_project` (`mission_control/ingest.py:validate_slug`) refuses otherwise, at the slug stage BEFORE any spend. Cathedral's `02_ton-618`… and three Sacred Dawn scripts failed this; fix is a `_`→`-` rename of both pair members. (Bake into the authoring checklist.)
- **Slug must match folder AND header.** `cathedral_of_stars` uses an underscore slug because its folder + script `channel:` headers agree; `sacred_dawn` headers auto-resolve to the `sacred-dawn/` folder; the rest are hyphenated. The plan's `channel` matches the FOLDER; the header must match what the orchestrator resolves. Resolve identity explicitly — an empty hyphen-stub created by mistake had to be deleted.
- **The timezone +02:00 summer trap.** A scheduled video is uploaded `privacyStatus: private` WITH `status.publishAt`; YouTube auto-flips it public. `publish_start` is an absolute instant, so **the offset must be the channel's actual wall-clock offset on the publish date** — in summer that is **`+02:00`** (CEST), not winter `+01:00`. `+01:00` in June schedules an hour later than intended (01:00 displays as 02:00). Verify the `--plan` local time is what you want; the UTC line sits the right hours behind.
- **The render-vs-publish race.** A scheduled video only honors `publishAt` if it finishes uploading before that instant. With many videos rendering sequentially, a start too close to "now" means a late video uploads past its slot and YouTube publishes it immediately. Date the earliest start far enough ahead for the queue to clear.

**Open gap — re-ingest (Tier 2):** `run_batch.py` writes a manifest but **does not move shipped pairs out of the inbox**, so a re-run re-renders + re-uploads (duplicates) everything still in `batch_inbox`. Until closed, move a shipped pair to `<inbox>/_shipped/` by hand before re-running. Durable fix: auto-archive on `ok=True` only, built into `run_batch.py` (so it fires for direct single-channel runs too) — belongs at the channel-batch level, not the wrapper.

**Open gap — thumbnail-set fire-once (Tier 2):** `upload_episode.py` uploads the video then sets the thumbnail in a SEPARATE call; if that call fails/skips, the video ships with the auto-grab and nothing errors (hit noahs-flood — thumbnail.png perfect on disk, just never attached). The video ID is also never persisted to the project. Fix: persist the video ID, retry the set call, and a standalone `set_thumbnail.py` (video ID + png → `thumbnails().set()`, no re-upload). For now, re-set by hand in Studio.

**Re-running after a partial/aborted run:** videos already shipped are private+scheduled in Studio AND still in the inbox. Either (A) delete the shipped Studio uploads, leave the pairs for a fresh re-render; or (B) keep the uploads, move their pairs to `_shipped/`, and set the re-run's `publish_start` past the kept slots so the calendar doesn't collide. `ingest.create_project` refuses an existing project, so a true re-render needs `rm -rf <channel>/projects/<slug>` first.

---

### 5.10 The read-side — channel metadata mirror, schedule view, cadence check (shipped 21 June)

Everything above is the WRITE side (produce + publish). `shared/dump_channel.py` is the READ side: a channel-agnostic, **read-only** mirror of what YouTube actually holds, so the whole portfolio's schedule and metadata is queryable — and committed to the repo so Claude can answer "what's scheduled on X" from a file instead of a screenshot.

**What it is.** Point it at a channel folder (the same identity model as everything else — `token.json` lives there). It reuses `upload_episode.get_credentials()` **verbatim** — the existing `force-ssl` scope already grants read, so **no new OAuth consent**. It resolves the channel's uploads playlist (channel-ID `UC…` → `UU…`), walks it via `playlistItems.list` (1 quota unit/page), then `videos.list` with **every readable part** (1 unit/page), and writes the raw response whole to `<channel>/channel_dump.json`. Raw capture, never pre-filtered — future questions are a local read, not a new API trip. `success-coach` is excluded from `--all` (dead channel; still dumpable explicitly).

**Three views over the mirror:**
- **`--scheduled-only-summary`** — the forward calendar, soonest first, in **local time** (default `Europe/Amsterdam`, `--tz` override) with UTC in parens, so it matches Studio. Flags `[PAST]` (elapsed publishAt) and non-private status.
- **`--cadence`** — the post-batch verifier for the **"post every day, forever"** rule (§9 #14): per channel, buckets scheduled videos by local date and flags any **missing day inside the scheduled span**. A same-day double counts as ONE covered day (doubling up doesn't fill the next hole). Run it right after a batch-of-batches; it ends with a single `GAPS FOUND` / `all continuous` verdict.
- (Backlog, for the batch-of-batches pass) read `batch_inbox/` for *true* runway before upload, a **runway alarm** (flag any channel whose span ends within N days — near-empty-but-continuous still trips), and a **golden-hour check** (flag any slot not at 01:00 CEST).

**Quota:** reads are ~1 unit/call; a full seven-channel dump is **under 100 units** against the 10,000/day ceiling — negligible. (Avoid `search.list` — 100 units; the uploads-playlist walk is 1.)

**What the API CANNOT see (stays a manual Studio gate — this is the safety boundary, §2A):** the **Altered/AI-content disclosure flag** (not readable or writable via API), Content ID copyright claims (need the partner `youtubePartner` scope), end screens / cards / Studio editor state. `statistics.*` in the dump is a snapshot at dump time, not live — use NexLev for current performance.

**The workflow it enables:** run batch-of-batches → `python shared/dump_channel.py --all --cadence` → if `GAPS FOUND`, fill in Studio before walking away → commit the refreshed dumps so the schedule is a repo read. It is the cheap automatic verifier that sits *downstream of the unattended orchestrator* — the §2A "gate on review" principle made operational.

**Banked operational lessons (21 June):**
- **Read the schedule in Amsterdam time, always — Studio is ground truth.** A `23:00Z` publishAt is `01:00` the NEXT day CEST; reading raw UTC against Studio's local view invents phantom day-collisions (this burned the first read twice). Golden hour is **01:00 Amsterdam**; the dump renders there by default. The `--tz` flag exists only for scheduling-from-the-road (e.g. `--tz Asia/Kolkata`), but data is always *read* in CET.
- **The half-hour-offset puzzle = a foreign timezone, not a bug.** A slot showing a `:30` past the hour (e.g. 04:30 CEST) is a clean local time set in a `:30` zone — 08:00 IST set from Bangalore reads as 04:30 Amsterdam. To hit 01:00 CEST golden hour from India, set 04:30 IST. The dump-in-CET is the check that a slot landed on golden hour regardless of where it was scheduled from.
- **`publishAt` is reliable only for genuinely-pending private videos.** Cross-check against `privacyStatus` and whether the time is past; a published/rescheduled video can carry a stale `publishAt`. Don't over-theorise a "ghost" — verify the actual `status`/`uploadStatus` from the dump (`grep`/one-liner) and let Studio settle disagreements.
- **The dump is a snapshot — re-run after any Studio change** before trusting a read; the committed JSON is only as fresh as its last run.
- **`git add */channel_dump.json` is the box-side commit** (generated output committed from the box is fine — the no-hand-edit discipline is about *code*, not generated files). `.gitignore` carries `!*/channel_dump.json` (force-in even under a broad `*.json` ignore) + `success-coach/channel_dump.json` (re-ignore the dead one).

---

## 6. The tech stack (the fast layer — swappable)

- **Stills:** fal.ai Flux-pro/v1.1. (Pass `safety_tolerance:"5"` to stop silent ~7KB black-PNG rejections.)
- **Animation:** fal Kling (O3 Standard) for the front *N* beats; **free Ken-Burns floor** (ffmpeg zoompan) for the rest — the tiered-render cost limiter (§5.2). **The animatable-foreground rule** is upstream (ante-machinam Constitution §7). On all-Ken-Burns channels the whole video is the floor (~$3).
- **TTS:** Inworld. *(Model-string contradiction unresolved: doc `inworld-tts-1.5-max` vs code `INWORLD_MODEL = "inworld-tts-2"` — verify against the box.)* Voices: Victor (Final Hours/Synthetic/hooks/**Prehistoric Disasters**), Elliot (Sacred Dawn), Ashley (Success Coach), Vinny (You Had To Be There). `voice_id` snake_case. **Per-channel voice speed (17 June eve, `patch_inworld_speaking_rate.py`):** the payload passes `speakingRate` inside `audioConfig`, read from `channel.json` `speaking_rate` (0.5-1.5, default 1.0 when absent -> other channels unchanged). Prehistoric = 0.9. Baked into `voiceover.mp3` (affects future renders only). The 'we slowed Victor for Final Hours' memory was FALSE — no speed key existed before this; all channels ran at 1.0.
- **Alignment:** Whisper → word timestamps.
- **Mode B graphics:** Remotion (Node 20.20.2, Remotion 4.0.472). Six components.
- **Assembly:** ffmpeg (streaming concat demuxer). `ffprobe` is the only reliable clip-duration source. **The final concat/encode (`-preset medium -crf 18`) is the single heaviest step** — ~20 min for a 20-min Ken-Burns video on the 16GB box (no GPU). For Ken-Burns lanes `-preset fast/veryfast` would roughly halve it with no visible loss (backlog Tier-4 #18) — the biggest batch-throughput lever.
- **Music — CURATED PER-CHANNEL FOLDER (decided 17 June, chosen over fal-generated).** A folder of tracks at `<channel>/music/`; the assembler's **`--music-dir` path** (`patch_music_dir.py`) picks N random tracks (default 3), **crossfades the joins** (`acrossfade`, default 2s — stops the track-changes sounding like a playlist skip), loops the crossfaded sequence to fill the voiceover, and feeds the EXISTING amix mux at **VOICE_LEVEL 1.15 / MUSIC_LEVEL 0.07** untouched. Driven by a `channel.json` `music` block: `{"dir":"music","tracks":3,"crossfade_seconds":2,"level":0.07}` (`patch_convergence_musicdir.py` wires convergence to pass it). Random-N gives variance across renders (two videos won't share a bed). **Two mux bugs fixed 17 June eve (both silently shipping):** (1) the convergence music block referenced an undefined `channel_dir` -> NameError swallowed by a bare try/except -> silently `--no-music` on the batch path; fixed to derive `_channel_dir = proj.parent.parent` and drop the swallow (`patch_convergence_channeldir_fix.py`). (2) the `amix` had no `normalize` option -> ffmpeg's `normalize=1` default ducked music under loud narration and pumped it in pauses (intermittent music + too quiet); fixed with `amix=inputs=2:normalize=0:...` (`patch_amix_normalize.py`). **Validate audio END TO END for level, never a one-listen presence check.** The standalone `make_music.py` (fal-generated single bed) is **superseded** for production by this curated path — a hand-picked library of mood-matched beds beats generated music for atmosphere-not-melody documentary scoring, at zero per-video cost. (Final Hours / Sacred Dawn's earlier Jamendo single-bed at the same levels is the precedent this generalises.) Prehistoric Disasters has 8 ominous deep-time beds loaded.
- **Thumbnails — AUTOMATED, IN-PIPELINE (shipped + locked 17 June).** The thumbnail is generated, selected, and overlaid as a convergence step before upload, fully unattended:
  - **`select_thumbnail_still.py`** renders **N=2** Flux candidates from the per-project `thumbnail.json` `subject` field (+ the channel's `candidate_prompt_suffix` + `style_suffix`), then a **Sonnet-4-6 vision call** judges them *as thumbnail substrate* on the channel's `selection_rules` (clean negative space where the headline lands, strongest catastrophe-at-a-glance, no garbled detail) and picks the best. Fail-safe to candidate 1. Logs the verdict to `thumbnail_selection.json`. (Proven: it correctly rejected a candidate whose bright sky bled into the headline zone.)
  - **`make_thumbnail.py`** overlays the locked house look (deterministic typography — NOT generative; text is a Pillow layer, never baked by Flux, because image models can't render legible type). Two composition modes: `centered_subject` (head-poke-through, rembg on) and `low_silhouette` (text in a corner, rembg off). The locked Prehistoric look: a **left gradient scrim** for text contrast (`scrim:{side,width,opacity,feather}`) instead of global darkening (the fix for the image washing out under the text — **bank: darken only where the text lands, never the whole frame**), `darken_factor 1.0` + `vignette 0` (image at full brightness; the scrim does the contrast), independent `margin_x`/`margin_y`, heavy stroke + drop shadow, near-white title / amber subtitle. Anton font with DejaVu/Impact fallback.
  - **`_maybe_thumbnail()`** (`patch_convergence_thumbnail.py`) runs both before `_maybe_upload()`; reads `thumbnail.json`, fails soft (no spec / error → skip), produces `thumbnail.png` which `upload_episode.py` already attaches.
  - **The doctrine (banked, §9):** design the thumbnail WITH the script — one authoring moment, the packaging decided alongside the words (matches Peter's Clickly-while-speccing habit; Clickly is the *concept/headline testing ground*, the pipeline *produces* the locked-look asset). But store it as a separate `thumbnail.json`, NOT in the script header — the YouTube title (full, SEO) and the thumbnail headline (short, punchy) are different strings. The pair (`.md` + `.thumb.json`) travels together; the separation is the architecture. The text never travels as a passed variable — written once at prep, read once at the end, so nothing in the middle can corrupt it. For the batch, each topic needs its `.thumb.json` authored alongside its script (the `prehistoric-slate-19.md` "thumbnail concept" lines are the seeds). **Silhouette flag:** the "tiny human for scale" motif works for human-era topics but is an anachronism for pre-human deep-time — swap the scale anchor to a lone tree/creature/boat per `thumbnail.json` subject.
- **Publish/upload:** `shared/upload_episode.py` — the ONE channel-agnostic uploader (header=metadata, channel folder=identity). One Google account (`peteralkema2@gmail.com`); one shared OAuth client, **published to Production** so refresh tokens don't expire. Each channel has its own `token.json` (binds to the channel picked in the OAuth chooser). **Six recreation channels authed** + bindings verified: Final Hours, Sacred Dawn, You Had To Be There, Synthetic Press, Scripture On Screen, **Prehistoric Disasters**. (Success Coach is on a separate account.) `--auth-only` mints/refreshes a token on the laptop (needs a real `--project` dir to satisfy its `is_dir()` check — use an `_authstub` project folder if none exists yet), then `scp token.json` + `client_secret.json` to the box. **NEW-CHANNEL HARD GATE: an unverified YouTube account rejects uploads >15 min at processing ("Processing abandoned"). Verify the account (youtube.com/verify, phone) before the first long upload — see §12.** **Quota (confirmed 17 June eve): the old 'six uploads/day' wall is GONE** — Google cut `videos.insert` from ~1,600 to ~100 units on 4 Dec 2025; 10,000/day now covers ~100 uploads/day. Batch uploads are a non-issue; stagger for AUDIENCE, not quota. **Scheduling (designed, not built):** upload private + `status.publishAt` and YouTube auto-publishes — NEVER public+publishAt (rejected); front-48h clock starts at `publishAt`. Design: `run_batch.py --publish-start <ISO+tz> --publish-interval-hours 12`, video N -> start + N*interval, `--plan` prints the calendar; Studio stays the review surface.
- **Research/analytics:** NexLev MCP (`search_niche_finder_channels` with `isFaceless:true`, `sortBy:outlierScore` is the reliable breakout-finder; `search_videos` is unreliable for descriptive queries — use `get_similar_videos` seeded from a known video instead). **Never trust a NexLev average** (§9 #16): both `totals.averageViewDuration` and avg-views-per-video are distorted by a single hit, and the `totals` fields have been observed flat-out wrong (92s where the daily rows give 138s). Compute AVD yourself as `(watch-min × 60) ÷ views`; read the median/spread, not the mean. The READ-side mirror (`dump_channel.py`, §5.10) is the *owned-channel* counterpart — NexLev for live performance + competitor research, the dump for your own metadata/schedule state (snapshot, not live). Google Trends as a manual radar — a lagging detail that confirms or denies, never a topic-picker, and only on quoted exact phrases + YouTube-Search filter (§9 #19).
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
13. **Lane benchmark — flat high-floor beats the jackpot** (17 June eve). The Prehistoric lane benchmark is **Wild Horizons** (`UC0g0WbvanQND4dC1JDaW1_w`) — faceless AI-cinematic deep-time catastrophe, ~$4,300/mo, ~218K avg views/video in under a year, and **no outliers even at 1.3x**: a FLAT high floor (every video clears six figures), not a power-law jackpot. For a factory model a high floor beats a fat tail. Their ~32-min average (72-min biggest hit) says the lane rewards **long-form**. Chicxulub was algorithmically SUGGESTED next to it in Studio -> YouTube has classified the channel into the neighbourhood, positioned to draw its recommendation traffic.
14. **Post every day, forever** (the cadence rule, banked 21 June). On the six active channels, the standing rule is one upload per channel per day, indefinitely. The binding constraint is NOT the scheduler — it's whether batch production stays ahead of consumption across all six at once; a skipped day is what an empty inbox looks like from the schedule side. So "post every day" is really two rules: *schedule* every day (now a machine check — `dump_channel.py --cadence`, §5.10) and *produce enough that there's always something to schedule* (the supply problem the runway-alarm backlog item guards). Same-day doubles do NOT buy runway (two videos on one day still leaves the next empty) — spread them forward.
15. **The flat-no-outlier signal = a packaging machine.** A channel with ZERO outliers (not even at 1.5x) across its whole catalog is not lucky and not topic-driven — its format/packaging carries every video to the same number regardless of subject (confirmed on Nick Invests: every video clustered at ~58K). Reading the *absence* of variance is as informative as reading a spike: it says the win lives in the wrapper, not the topic. This is §9 #1 ("packaging beats production") visible in a competitor's own analytics, and the argument for best-execution-in-a-served-lane over spike-chasing (#5).
16. **The average-distortion trap — never trust a mean, read the distribution.** Avg-views-per-video (`totalViews/videoCount`) is distorted by a single viral hit exactly the way NexLev's `averageViewDuration` is (the banked §6 rule). A channel that looked like a "105K-average machine" was one 2.4M video over a ~3K median — a one-vein hit, not a consistent performer. **Always check the median / the spread before calling a channel (or your own) a winner.** This is the analytics face of #17 (vein not spike). Corollary already banked: for a recently-launched channel compute AVD yourself as `(watch-min × 60) ÷ views`, never the NexLev `totals` field (which has also been observed flat-out wrong — e.g. reporting 92s where the row math gives 138s).
17. **Vein, not spike — promote on repeatability.** A single big number is the spike trap; the signal worth concentrating craft-attention (or declaring a lane validated) on is *repeatable* performance — two or three videos clustering above the channel's own baseline on the SAME packaging structure. The whole explore→exploit handoff (§2A) hinges on this definition; get it wrong and you back lottery winners and call it compounding.
18. **The wide-net / narrow-hook funnel — breadth catches, depth holds, the link is the channel.** Two video types are not a tradeoff to balance but two positions in one funnel. A *wide-net* video (broad marquee hook) wins the click and converts subs but may not hold (Sacred Dawn's *War in Heaven*/Satan: best CTR + most subs, WORST retention — a CTR-without-AVD video). A *narrow-hook* video (a niche, weirder promise) self-selects a committed viewer who stays (Sacred Dawn's *Watchers' Daughters*: 33 min, the channel's best holder). The move is not to balance them but to **wire the net to feed the hook** — the marquee video's job becomes convert + route (end screen / pinned comment to the deep video), not retain for its full length. Judge each on its OWN scoreboard: net = sub-conversion-per-view + click-through to the next video; hook = AVD + watch-time. Tag each batch slot net-or-hook and hold it to its own metric. (For Sacred Dawn specifically, the *vein* is the strange-apocryphal — Watchers / Nephilim / Book of Enoch / forbidden knowledge HOLDS; marquee Bible headlines CLICK but leak. → `_Sacred-Dawn.md`.)
19. **Two independent signals agreeing beats either alone; and Google Trends is a lagging detail, not a topic-picker.** When the recommendation-graph signal (your own retention data) and the search signal (Trends) point at the same vein *independently* — e.g. Sacred Dawn's highest-retention video was a Book-of-Enoch framing AND "book of enoch" is the most durable rising YouTube-search curve in its cluster — that convergence is as close to confirmation as this game offers, far stronger than either alone. Two cautions baked the same day: **(a) generic single-word Trends queries measure the most popular homonym** ("watchers" reads as Weight-Watchers New-Year diet spikes, not fallen angels) — use tightly-quoted exact phrases + the YouTube-Search filter to strip noise; **(b) feed-discovery content is not search-driven** — apocryphal/recommendation-graph topics show flat Trends while demand is real and growing, so a flat Trends line is NOT a red light for a served lane. Trends confirms or denies; it never picks the topic (reinforces #5).

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

**Shipped 17 June eve:** three audio-chain bugs fixed (channel_dir music, amix normalize=0, per-channel speakingRate — §6); Prehistoric LIVE (account verified, chicxulub re-run through the full process with music + 0.9 Victor + front-2 Kling, both Toba + Chicxulub PUBLIC); decisions banked (front-2 Kling = per-batch `--kling-count 2` flag not a baked default; the tiny-human silhouette STAYS, let comments rule it); Wild Horizons benchmark (§9 #13); upload scheduler designed.

**Open (top of next):** read ep1 (Toba) + ep2 (Chicxulub) first-48h CTR + AVD vs the Wild Horizons ~218K floor (front-2-Kling hook lift, tight-vs-long-form decision); build the upload scheduler; then batch validated topics. Let the data drive.

**Specs written, not built:** the upload scheduler (no-state, timestamp-in — designed this session); decade-look Phase 2; Mission Control thumbnail integration; faster final encode.

**Shipped 21 June (the read-side session):**
- **`dump_channel.py`** (§5.10) — channel-agnostic read-only metadata mirror across all seven channels (`channel_dump.json` committed to the repo), a local-time `--scheduled-only-summary` calendar, and a `--cadence` post-batch verifier for the "post every day, forever" rule (§9 #14). Reuses the existing upload token (no new consent), reads cost <100 quota units for the whole portfolio.
- **Caught + fixed a real orphan from the 19 June teething** — the Lady Be Good bomber (Final Hours): a finished, scheduled, never-reviewed video queued to auto-publish, plus a same-instant Final-Hours collision (Pompeii + bomber both at one slot). The bomber was rescheduled to 29 June and **still needs its manual review + AI-content flag before then** (the one live action item this surfaced).
- **Banked:** the operating philosophy on scale vs craft (§2A); analytics laws #14–#19 (post-every-day cadence; flat-no-outlier = packaging machine; average-distortion trap; vein-not-spike; wide-net/narrow-hook funnel; two-signals-agree + Trends-as-lagging-detail); the timezone-display + API-blind-spot + Artlist-clearing gotchas (§12).

**Open (top of next):** review + AI-flag the bomber before 29 June; run `--all --cadence` after each batch-of-batches as standing practice; wire the read-side upgrades when batch-of-batches becomes the routine (inbox-runway, runway alarm, golden-hour check — §5.10). The standing read still holds: ship real videos on the proven economics, concentrate craft-attention on the channel showing a vein, let first-48h data drive (§2A).

**A fresh session starts here:** load the five `_`/`__` docs (this canonical, the worklog, ante-machinam, `_Prehistoric-Disasters.md`, machina). Everything is committed + pushed; the only open external action is reading the first-48h data, then building the scheduler, then a batch.

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
- **channel.json:** `voice_id` is snake_case (`voiceId` → silent Victor fallback); keys are `name`/`voice_id`/`style_suffix`/`default_motion`/`default_music_prompt`/`base_canon`/`upload`/**`thumbnail`**/**`music`**/**`speaking_rate`** (optional float 0.5-1.5, default 1.0; Prehistoric=0.9). Diff a new one against a known-good file before first run.
- **Script format:** bare key:value header (no `---`), `##` double-hash sections, `[A] narration` + `VISUAL:` per beat. Copy a working script's shape; don't author markup from the doc. A bad format parses to zero beats → ZeroDivisionError. Verify with `parse_script.py <md> --json /tmp/b.json --json-full /tmp/f.json` (zero-spend) before any run.
- **Runtime ≈ beat count × ~14s** (Ken-Burns floor stretches short beats), not words-only wpm. 88 beats → 20.7 min.
- **Thumbnail:** per-project `thumbnail.json` `{subject,title,subtitle}`; channel look locked in `channel.json` `thumbnail` block; Sonnet picks the best of N=2 candidates; text is a deterministic overlay (scrim for contrast, not global darkening). Silhouette motif = human-era only; swap the scale anchor for pre-human topics.
- **Music:** `channel.json` `music` block `{dir,tracks,crossfade_seconds,level}`; tracks in `<channel>/music/`; filenames must have no spaces (normalize to `track_NN.mp3` — `acrossfade`/concat choke on spaces); random-N crossfaded bed at MUSIC_LEVEL 0.07.
- **Batch runner:** inbox of `<name>.md` + `<name>.thumb.json` pairs; `python shared/run_batch.py --inbox <dir> --channel <ch> --plan` (zero spend) then `--limit 1` then full; `ingest.create_project` refuses if the project already exists (so re-running a partial inbox needs manual cleanup).
- **`ffprobe`, not the player**, for true duration.
- **OAuth:** one Google account `peteralkema2@gmail.com`; Production app (non-expiring); per-channel `token.json` bound to the channel picked in the chooser; mint via `upload_episode.py --project <ch>/projects/<x> --auth-only` on the LAPTOP (needs a real project dir — use an `_authstub` if none exists), then `scp token.json` + `client_secret.json` to the box. Six channels authed.
- **Mission Control:** `http://116.202.18.68:8002/?key=fh2026`, `mission-control.service`, **v1.9**; version-check the heading SHA against `git rev-parse --short HEAD`.
- **Final encode is the slow step** (`-preset medium`, ~20 min for 20-min Ken-Burns video, CPU-bound). `-preset fast/veryfast` would halve it on Ken-Burns lanes — the biggest batch-throughput lever.
- **Music mux (17 June eve):** the `amix` must carry `normalize=0` (else ffmpeg's `normalize=1` ducks music under the voice). Convergence derives the channel dir from `proj.parent.parent`, NOT a `channel_dir` var (never existed — old code silently ran `--no-music`). Validate audio end to end for level.
- **Voice speed:** `channel.json` `speaking_rate` -> `speakingRate` in the Inworld `audioConfig`; baked into `voiceover.mp3` (audio-leg re-run to change).
- **YouTube quota:** `videos.insert` ~100 units since 4 Dec 2025; ~100 uploads/day. Schedule via private + `status.publishAt` (NEVER public+publishAt).
- **Re-run a project with new settings:** `ingest.create_project` refuses an existing project; `rm -rf` the project + re-ingest via `run_batch.py` (full re-render, ~$4 Ken-Burns — how chicxulub got music+0.9+Kling). For a free re-mux on an existing render use standalone `assemble_episode.py --music-dir …`.
- **Two assemblers:** only `assemble_episode.py` is alignment-safe; `finish --assemble-only` drifts.
- **Slug rule:** project filenames must be `^[a-z0-9][a-z0-9-]{0,60}$` (lowercase/digits/hyphens, start alphanumeric, NO underscores, no `NN_` prefix). `create_project` refuses otherwise at zero spend. `--plan` does NOT catch this — slug-scan the inbox first.
- **Music is box-local:** `*.mp3` is gitignored (`.gitignore:78`), so per-channel `music/` libraries are scp'd to the box, never committed; the repo tracks only the `channel.json` `music` block. The block's `level` key is inert — the mux uses hardcoded `MUSIC_LEVEL = 0.07` in `assemble_episode.py:61`.
- **Thumbnail-set can silently fail:** `upload_episode.py` sets the thumbnail in a separate call after upload; a failed/skipped set ships the video with the auto-grab and does NOT error. Video ID isn't persisted to the project. Re-set by hand in Studio (pull `thumbnail.png` via scp) until the retry + `set_thumbnail.py` fix lands.
- **Read-side mirror (`dump_channel.py`, §5.10):** read-only, reuses the upload token (`force-ssl` already covers reads — no new consent), writes `<channel>/channel_dump.json`, committed to the repo. `--scheduled-only-summary` (local-time calendar) and `--cadence` (missing-day check) are the two views. Reads cost ~1 quota unit/call; full portfolio dump <100 units. Run `--all --cadence` after every batch-of-batches.
- **Always read the schedule in Amsterdam time; Studio is ground truth.** A `23:00Z` publishAt = `01:00` next-day CEST — golden hour. Reading raw UTC against Studio's local view fabricates phantom day-collisions. A `:30`-past-the-hour slot means a clean local time set in a half-hour zone (08:00 IST from Bangalore = 04:30 Amsterdam); to hit 01:00 CEST golden hour from India, set 04:30 IST. `dump_channel.py` renders in `Europe/Amsterdam` by default; `--tz` is only for scheduling-from-the-road.
- **API blind spots (Studio-UI-only, the manual-review boundary — §2A):** the **Altered/AI-content disclosure flag is NOT readable or writable via API** — it stays a manual per-video Studio toggle and is the reason "nothing publishes that a human didn't see" is a hard rule. Also unreadable: Content ID copyright claims (need the partner `youtubePartner` scope, not available on a normal channel), end screens/cards, Studio editor state. `statistics.*` in a dump is a snapshot, not live.
- **Artlist music clearing is CHANNEL-level or per-VIDEO-URL, never per-track.** You do NOT match tracks to videos — Artlist's own Content ID detects its tracks; your job is only to prove ownership of the destination by registering the **channel (up to 3 channels)** or pasting the **video URL**. With more than 3 channels, the channels beyond your 3 whitelist slots must be cleared per-video-URL — and the read-side dump is exactly the source of that URL list (every video URL per channel, including scheduled ones so you can pre-clear before the first-48h window). Give the 3 channel-level whitelist slots to your 3 highest-volume channels so the cheap blanket clearing covers the most output.
- **The orphan risk (proven 19 June teething, caught 21 June):** a batch-of-batches run can leave a finished, scheduled, never-reviewed video queued to auto-publish (the Lady Be Good bomber — real, 6:45, `processed`, private, scheduled, invisible in the operator's normal Studio scan because of sort/filter, never seen). The read-side cadence/schedule view is how you find these *before* they publish. Any video from a troubled batch window needs an explicit Studio review (open it, set the AI flag, eyeball the render) before its slot.
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
- **Read-side mirror / schedule / cadence (`dump_channel.py`, §5.10):** `python shared/dump_channel.py --all --scheduled-only-summary` (forward calendar in Amsterdam time) · `python shared/dump_channel.py --all --cadence` (missing-day check — run after every batch-of-batches) · `--channel <ch>` for one · `--dry-run` (count + quota estimate, no fetch) · `--tz Asia/Kolkata` only when scheduling from another zone. Commit the dumps from the BOX: `git add */channel_dump.json && git commit -m "refresh dumps" && git push` (generated output committed from the box is fine — the no-hand-edit rule is about code). Re-run before trusting any read; a dump is only as fresh as its last run.

---

*This document is the umbrella reference for the whole operation, and one of just two living docs: **this reference (the system)** and **`ante-machinam.md` (the craft)**. Update this file's date + current-state + backlog whenever a session banks something that changes the shape of the operation.*
