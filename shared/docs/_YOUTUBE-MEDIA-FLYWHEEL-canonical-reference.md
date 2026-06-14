# YouTube Media Flywheel — Canonical Project Reference
*The single comprehensive description of the whole operation. Load this first in any new session to get to full context fast.*
*Maintained by Peter + Claude. Last updated: 14 June 2026 (Mission Control at v0.9: status line, A1 heartbeat/false-hang fix, version stamp, and the FINAL VIDEO panel — on top of the tiered-render cost limiter proven on Enoch).*

---

## 0. What this is, in one paragraph

The **YouTube Media Flywheel** is a one-person, fully-automated faceless-YouTube **media business** built as a *content factory*, not a channel. A single channel-agnostic Python pipeline turns a written script into a finished, narrated, scored, packaged video — stills, animation, voiceover, assembly — for a few dollars and a few hours of compute. The same machine serves multiple channels across different genres; a new channel costs one config file and content, not new code. The bet is not on any one video or topic but on **the production system as a compounding asset**: the tools underneath get swapped as they improve, the orchestration lasts years, and the operating discipline is the actual moat. Operated solo by Peter Alkema from The Hague, Netherlands.

The "flywheel": demand research → script → automated production → publish → algorithm signal → learn → better next video, with each turn cheaper and faster than the last, and each banked lesson making every future video across every channel better.

---

## 1. The operator

**Peter Alkema** — solo operator, The Hague / Hoofddorp, Netherlands. Former South African TV presenter (in front of camera), then ~25 years of executive/systems work across consulting, banking, manufacturing; former Udemy course creator with deep instructional-design background. **Vibe-codes in Python; no developers.** Works fast, thinks out loud, iterates. The rare combination the whole thesis leans on: *system operator with creative voice and broadcast taste* — most AI-video people are technologists without taste or artists without systems; Peter is both.

Working style (how Claude should operate with him): direct, skip preamble; full working scripts not snippets; read shared code fully before suggesting changes; match his level, don't over-explain basics; follow rough thinking and reframe when he's stuck; challenge wrong thinking directly and briefly; prose over bullets in strategy; use NexLev proactively for YouTube research; analyse shared screenshots fully.

---

## 2. The core thesis (the "why" — slow-changing)

**Anchoring principle (Altman, Sora briefing):** *"Don't design for the model. Design for continuous and exponential improvement in the models."* Everything else is consequence.

**Three layers, distinguished by half-life:**
- **Fast layer (3–12 months):** the specific models/tools — fal Flux (stills), fal Kling (animation), Inworld (TTS), Whisper, Remotion, the music generator, the cloud host. In active competition, always improving, *designed to be swapped*. Each external service is encapsulated behind one function so a model change is a config edit, never a refactor.
- **Orchestration layer (multi-year):** the pipeline itself — the channel-agnostic conductor, beats.json as sole input, channel.json as identity, the leg system, the canon/rulebook mechanism, the review gates, the per-job look resolver. Survives tool changes. Worth engineering well.
- **Discipline layer (career):** the habits that compound — bank every failure as a *tool-agnostic principle* (not a tool-specific workaround), encapsulate hard-won fixes in code, diagnose the category behind every reshoot, lock the script first, review before paying. **This is the moat.** Competitors copy the surface format in a weekend; they cannot copy two years of banked discipline.

**Two corollaries that govern daily decisions:**
- **Packaging beats production.** Demand-validated topic + a title promising a dramatic arc + a retention hook + a consistent on-brand thumbnail drive distribution more than raw render quality. CTR + AVD in the first 48 hours are the signals the algorithm watches.
- **A principle not in code only runs if a human remembers it.** Push rules from docs into the conductor/scripts wherever worth it.

---

## 3. The business model

A **content factory**: the pipeline generates content on any topic cheaply; channels are distribution vehicles; a portfolio of channels diversifies risk off any single point of failure. Power-law logic — one breakout pays for many duds — so at the early stage **shipping and generating algorithm signal comes before perfect positioning**. Judge on per-video NexLev outlier scores and retention-curve *shape*, never on channel averages (best-first topic ordering drags averages down by construction). Marginal cost per video is low (single-digit dollars of API spend), so experiment aggressively; the cost of being wrong is near zero.

---

## 4. The channel roster

One machine, several channels (each a *signature* over the pipeline's legs, expressed in `channel.json` + content):

| Channel | Premise | Mode | Voice | Status |
|---|---|---|---|---|
| **Final Hours** (@FinalHours_history) | The last hours of people/places history remembers; faceless cinematic recreation; the camera stays with one named person/place while catastrophe happens around them | Mode A only | Victor (Inworld) | **Live, primary.** Long-form 12–16 min (city-catastrophe sub-series 20–32 min). Has working OAuth/upload. |
| **Sacred Dawn** (@sacredawn) | The Bible's cosmic & primeval drama — the Watchers, the Nephilim, the Flood, Creation, the war in heaven — as cinematic recreation. "The Bible's origin story, brought to life through cinematic recreation." Reverent, never sensational | Mode A only | **Elliot** (British, deep, liturgical) | **Live, newest.** Launched 10–11 June with "Before the Flood: The True Story of the Nephilim and the Watchers." Upload manual (Entertainment / private). The highest-fit use of the machine found to date — see §9.3. Full doctrine: `sacred-dawn-creed.md`. |
| **You Had To Be There** (@you-had-to-be-there) | Cinematic AI recreation of *vanished lived experience* — un-filmable everyday nostalgia (1970s childhood, gaming-before-internet, etc.) | Mode A, decade-variable look | **Vinny** (warm wry Brooklyn storyteller) | **Live.** First channel to use per-job decade looks in production. |
| **Success Coach** (@successcoach100, ~6,090 subs) | Professional transformation in the AI era — AI careers, EU AI Act, middle-management survival, cloud skills | Faceless AI VO + stock footage, structured explainers | Ashley (lessons), Victor (hooks) | **Live, monetized but underperforming** — packaging-layer gap, not pipeline gap. Has its own stack (Pexels/Pixabay/Clickly). |
| **Synthetic Press** | AI-era human drama — AI-*drama* not AI-doom; real boardrooms, founding dinners, 2am calls, dramatised as cinema; mouths closed (no lip-sync) | **Dual-mode (A + B)** — cinematic recreation + Remotion motion-graphics for evidence/quotes/numbers | Peter's own broadcast read (marquee) + Victor (scratch) | **Flagship, launching.** Render side proven end-to-end; upload/OAuth not set up. `channel: synthetic` (alias trap). |
| **Lazarus Films** | Dignified cinematic adaptation of public-domain dramatic writing (Saki, Hammett, du Maurier); the counter-position to public-domain slop | Mode A narrated (no lip-sync yet) | Single literary narrator (TBD) | **Designed, not built.** The channel built *on* per-film look overrides. First three sequenced (Sredni Vashtar → Maltese Falcon → The Loving Spirit). |

**Success Coach economics (illustrative of the factory model):** 5 demand-validated courses × 100 lessons (20 sections of 5) → ~100 videos of 12–20 min, ~$2/100-lesson course to generate. High RPM (~$8–13), professional audience. Its diagnosis was the seed of the whole "packaging beats production" thesis — the pipeline was right; titles, thumbnails, hooks, demand-driven topic selection were the entire gap.

---

## 5. The production system (the pipeline — the orchestration layer)

**One channel-agnostic orchestrator** runs the whole post-script arc. It reads ONE input and discovers from it what work to do, loads the relevant channel's identity, runs only the legs the content needs around the minimum gates, and produces a finished video — identically for every channel.

**The five design principles:**
1. **The sentence decides the mode.** Each beat is born Mode A (cinematic recreation) or Mode B (Remotion graphic) because the *sentence* decides — a place/person/moment wants a recreated scene; a fact/number/quote/structure wants a drawn graphic. Author sets it; the machine never infers.
2. **The voice decides the contract.** Audio has two axes: cardinality (one voice vs cast, via a `speaker` field) and binding (narration/off-camera speech is *swappable* — a timing source only; lip-synced on-camera speech is *locked* — a render input). Swappable means a voice swap re-times everything for free (the "true-up").
3. **The composition decides the legs.** Scan the beats → run only needed legs. Mode A present → Mode A leg (stills→gate→Kling). Mode B present → Mode B leg + correctness gate. Always → audio leg first (the timing source everything hangs off).
4. **The channel header decides the look.** The script declares `channel:`; the orchestrator loads `<channel>/channel.json` (the complete cross-mode identity). Composition = machinery; channel flag = identity; orthogonal.
5. **Maximal orchestration around minimal gates.** Everything that can run unattended does; the only stops are quality firewalls.

**The input boundary:** the orchestrator's sole input is `beats_full.json` (header + beats), produced by `parse_script.py` from `script.md`. The human-and-Claude phase (discuss → write → tag → fact-lock) produces the spec; the machine executes the spec. There is no separate `metadata.json` — the header *is* the YouTube title/description/tags.

**The legs (run order):**
- **audio_leg** (always, first): `build_audio_script.py` → `generate_episode_vo.py` (Inworld) → Whisper align → `build_beat_durations.py` → `durations.json`. **+ audio-continuity QC** (built 2026-06-09) auto-runs at the gate. Then the **audio gate** (keep / swap-in-human-read). *Listen at the gate regardless of the printed label — the leg still prints a hardcoded "Victor" string; the real read is whatever the channel's `voice_id` resolves to (confirmed at the Sacred Dawn launch).*
- **modeb_leg** (if Mode B beats): `dispatch.py` → Remotion render at each component's own duration → **Mode B correctness gate** (contact sheet, factual y/n).
- **modea_leg** (if Mode A beats): `modea_beats.py` → `recreation_pipeline.py stills` (fal Flux) → **stills review gate (in Mission Control)** → tiered animate (`finish` — Kling for the front *N* beats, free Ken-Burns floor for the rest; see §5.1).
- **convergence_leg**: pool clips → `assemble_episode.py` (interleave in true beat order via index map, hold each to audio-measured duration, mux ducked music bed) → `final_video.mp4`. (Publish half — thumbnail gate, schedule gate, upload — built for some channels, not all.)

**The two gates** (the only human stops): **stills review** (aesthetic firewall — browser review page) and **Mode B correctness** (factual firewall — numbers/quotes/attributions read right?).

**`durations.json` is the single timing source.** Produced once by the audio leg; consumed by dispatch, assemble, and the Mode B review. Audio is the source of truth; visuals hang off measured audio for both modes.

**`recreation_pipeline.py` is the shared engine** — generate_voiceover (Inworld), stills (Flux), finish/animate (Kling), assemble (ffmpeg). A change ripples into both legs; treat with care. *Standalone animate-recovery (banked at the Sacred Dawn launch, after an SSH drop orphaned a run at the stills gate): from the project dir, `python ~/Pipeline/shared/recreation_pipeline.py finish --project modea --animate-only` reads the existing stills/durations and re-spends nothing already done. Run long box jobs in tmux so a dropped pipe can't orphan them.*

**Per-job decade look (the look resolver, Phase 1 shipped 2026-06-09):** look resolves **channel-then-project** — `channel.json` gives the default `style_suffix`; a project `look.json` overrides it (`{"look":"hi8_90s"}`). `look_resolver.py` walks up from the still's output path to find it, mirroring how channel config resolves. Registry: `kodachrome_50s`, `color_60s`, `super8_70s`, `vhs_80s`, `hi8_90s`, `digicam_2000s` (decade aliases work). "The channel owns the frame; the job owns the film stock." Phase 1 = stills look only (Flux `style_suffix`); **Phase 2 (not built) = the grade layer** (`film_emulate.py` doesn't yet exist) for true VHS/digicam texture.

**Batched multi-video jobs:** nothing requires one script = one video (the pipeline is beat-based). A script can hold several self-contained parts (each its own cold open + close), run as ONE job, and be cut into N videos in post (Filmora). Constraint: **one look per job** (the resolver caches per project) — batch by shared look. Implication for upload: a batched job must **exit at `final_video.mp4`** and not auto-upload (one job → many videos breaks single-metadata).

---

### 5.1 Mission Control — the operator console (the "AI Film Director Storyboard and Control Panel")

The browser surface matured from the single-purpose stills review server into a **full one-page console** on `:8002` (service `mission-control.service`; the old `review.service` on `:8001` is left untouched). It is the **zero-terminal operator surface** — the whole arc runs from the page; the terminal is for diagnosis only. Shape: channel dropdown → project dropdown → **Launch** → the **gates become page state** (audio: keep / swap-in-human-read; stills: go / stop-here-keep-stills) → a **per-beat storyboard grid** (text · still · controls · motion · clip) → **tiered render** → **assemble** → **Reset**. Persistent shell (one page, controls disable-in-place during a run rather than the layout reshaping). **URL-persisted** (refresh stays in the project; projects are bookmarkable; **Reset** is the explicit way back to base). **In-place clip reload** (a rendered clip appears in the cell without a refresh). **Skip-existing resume** (a relaunch re-spends nothing already on disk; stills and clips both guard). Built through the strict workflow as a series of idempotent `patch_*.py`. **Live status line** (shipped): the strip's sub-line shows activity + artifact count counted off disk — `stills 47 / 132`, `clips 38 / 132` (animating), and elapsed-time for the no-artifact phases (`audio · working 6m`, `assembling`) — *not* a scrolling log. **A1 heartbeat + false-hang fix** (shipped, see §5.4). **Version stamp** (shipped): the heading reads `v0.X · <git-sha>` and `/api/state` returns `version`+`sha`; the displayed SHA must equal `git rev-parse --short HEAD` on the box — if it differs, the browser tab is stale (hard-refresh). `APP_VERSION` is hand-bumped on every shipped page change and pairs with the auto SHA; **as of this session Mission Control is v0.9.** **FINAL VIDEO panel** (shipped, see §5.5). The gate state lives in `<repo>/.mc_jobs/<job_id>.json` under `gate.decision`.

### 5.2 Tiered render — the fixed per-video cost limiter (the <$20 ceiling)

**The lever that makes long-form + multi-channel daily cadence financially coherent at once.** The animate step routes per beat: the **first N beats render with Kling** (true motion, ~$0.42/clip), **the rest fall to a free Ken-Burns floor** (`ken_burns_still()` — ffmpeg slow zoom, 1.5× cap, 4× upscale-first to avoid judder; same `clips/shot_NNN.mp4` artifact at the audio-measured duration, so assembly is unchanged). At **N=40 that's a fixed ~$16.80 of animation per video regardless of length** — vs ~$55 all-Kling on a 132-beat film, a ~70% cut. N is set per project by the **Kling clips: N** field at the stills gate (or `render_policy.json` `{"kling_count":N}`, or `--kling-count N`; default 40). `finish --plan` prints the routing free; `finish --assemble-only` re-stitches from existing clips with no cost. **Proven end-to-end on Enoch (Sacred Dawn, 132 beats):** clean 40/92 split, seam at shot 040→041 invisible in the cut on reverent material — see the front-loaded-effort-curve principle (§9.10). *Current split is **positional** (first N = Kling); v2 routes by which beats **earn** motion (duration/action), since a positional split can spend Kling on long contemplative holds and floor short kinetic beats.*

### 5.3 Motion direction — per-beat field + per-channel default

Each beat carries a `motion_prompt` that drives its Kling animation. Two layers now feed it: an **interactive per-beat motion field** on the Mission Control storyboard (typed at review time, persisted to `storyboard.json`, drives that shot's Kling prompt and survives into the batch animate), and a **per-channel `default_motion`** in `channel.json` (with a global slow-atmospheric fallback). **Proven on Sacred Dawn:** a dramatic default ("dramatic motion, maximise elements of movement and interplay on scene, dramatic lighting effects. pan and zoom in") read markedly better than the global slow default — fast/dramatic motion is the right register for the channel; yellow/slow is not. *Known bug to fix (banked): the per-channel `default_motion` is currently **inert** because the storyboard-authoring step always populates per-beat `motion_prompt` (slow) and the build prefers the beat's own value over the channel default — the `or` never reaches it. Principle: **a per-channel default is dead if an upstream step always fills the field it defaults.** Fix = make the authoring guidance channel-aware. (`pan` only acts on Kling clips, not Ken-Burns floor clips.)*

### 5.4 A1 — heartbeat, false-hang fix, dead-run detection

Two bugs, one root cause: the job record not reflecting reality. **The false-hang:** `run_modea_leg` went gate(`go`) → animate with nothing writing `phase: animating` in between, so the record sat at `gate_stills` through the entire animate — a healthy run *looked* hung at the gate (seconds on a 4-beat run; ~30 min on a 132-beat Kling run). Fixed: `set_phase("animating")` between the gate clearing and the animate loop. **Dead-run detection:** `set_phase` now stamps `heartbeat = time.time()` on every call, and `await_gate`'s JOB-mode poll loop pulses a heartbeat every 1.5s while blocked — so a run *parked at a gate* keeps proving liveness **because the live process is polling** (liveness is process-paced, not human-paced); a dead process simply stops pulsing. `build_state` flips a gate run to phase `stale` if its heartbeat goes silent for `STALE_SECONDS` (300); `phaseStrip` already renders `stale`, and `stale` is deliberately not in `ACTIVE_PHASES` so the page treats it as recoverable. **Scope (deliberate):** stale-detection covers gate phases only — work legs (`animating`/`assembling`) are single long blocking subprocess calls that can't pulse mid-leg, so time-checking them would false-flag a slow-but-alive render; that needs mid-leg pulsing threaded through `_stream`, a later change.

### 5.5 FINAL VIDEO panel — the first piece of the upload surface

When a run reaches `done` (or a finished project is opened), a **FINAL VIDEO — UPLOAD TO STUDIO** panel fills the page's top-right (the wireframe's third corner of the U). The top region is a two-column flex row (`#topgrid`, capped at 1500px): controls (create + launch) left, the panel slot (`#toppanel`) right; storyboard stays full-width below. The panel shows the **assembled video autoplaying** in-page (served by the existing `/video/` route, base corrected to the project root where `final_video.mp4` lives), **title / description / tags** pulled live from the `beats_full.json` header via a new `/api/meta` route, and a **working Download button** (no auth needed). The **Upload button is present but disabled** — it needs `auth.py` fixed + `/api/upload`, which is the next session's build. When no finished video exists the slot shows a faint placeholder so the space never reads as broken.

---

## 6. The tech stack (the fast layer — swappable)

- **Stills:** fal.ai Flux-pro/v1.1. (Pass `safety_tolerance:"5"` to stop silent ~7KB black-PNG rejections.)
- **Animation:** fal Kling (O3 Standard) for the front *N* beats; **free Ken-Burns floor** (ffmpeg zoompan, 1.5× cap, in `recreation_pipeline.py:ken_burns_still`) for the rest — the tiered-render cost limiter (§5.2). Clips are ~5s native; beats run 5–21s, so assembly slow-fills/stretches (invisible to ~2–3×, dead past that → split the beat in the script). **The animatable-foreground rule (banked at the Sacred Dawn launch) is upstream of this:** a wide landscape gives Kling nothing to move and animates as a dead slow-zoom; author a kinetic, drift-safe foreground subject (body-without-face / objects-and-hands / environment-as-active-force) into every VISUAL line — see ante-machinam Constitution §7 + Part III "Author for motion". (Ken-Burns floor clips don't pan/move — that's why motion budget is front-loaded where it earns retention.)
- **TTS:** Inworld (`inworld-tts-1.5-max`). Voices: Victor (Final Hours/Synthetic/hooks), Elliot (Sacred Dawn), Ashley (Success Coach lessons), Vinny (You Had To Be There). `voice_id` is snake_case in channel.json — `voiceId` silently falls back to Victor. Markup performs per-voice — prove it before relying on it.
- **Alignment:** Whisper (local) → word timestamps. Drift fixed via `difflib.SequenceMatcher` coverage matching.
- **Mode B graphics:** Remotion (Node 20.20.2 via nvm, Remotion 4.0.472 on the box). Six components: HighlightedHeadline, LowerThird, NumberCounter, ChapterCard, QuoteCard, DocumentReveal.
- **Assembly:** ffmpeg (streaming concat demuxer; folds into `assemble()` to avoid moviepy OOM). `ffprobe` is the only reliable clip-duration source (concatenated-MP3 header bug makes players show ~2× true length).
- **Music:** `make_music.py` (Claude writes one loopable instrumental prompt → fal ElevenLabs Music → `music.mp3`) — standalone, **not yet wired into convergence**. Or curated Jamendo (Final Hours / Sacred Dawn: VOICE_LEVEL 1.15 / MUSIC_LEVEL 0.07).
- **Research/analytics:** NexLev MCP (`youtube_channel_outliers`, `youtube_search`, `search_videos`, `search_niche_finder_channels`); dashboard at dashboard.nexlev.io. Google Trends (served-vs-searched, Rising-Queries) as a manual radar. *(Note: the video-level `search_videos` endpoint returned corrupted data in the Sacred Dawn session — motorcycle/casino results with fake billion-view counts; cross-check against the channel-level niche-finder before trusting it.)*
- **Success Coach extras:** Pexels (hook footage), Pixabay (lesson footage), Clickly (thumbnails), Claude API (hooks/titles), YouTube Data API.
- **Thumbnails:** Clickly / Nano-Banana-style edits; `make_thumbnail.py` (rembg U2Net). Generate the image clean (no text — models can't render legible type), add the headline as a layer.

---

## 7. Infrastructure & workflow discipline

- **Box:** Hetzner `pipeline-prod` at `116.202.18.68`, SSH port 443, user `peter`, venv `~/venvs/pipeline/bin/activate`, 16GB RAM (upgraded June 2026). Repo at `~/Pipeline`.
- **Repo:** `github.com/peteralkema/Pipeline`. Laptop clone `~/Projects/Pipeline`.
- **The strict workflow (non-negotiable):** all code edits on laptop → GitHub → box via **idempotent `patch_*.py` scripts** (or full-file rewrites for deletion-heavy changes); `git pull --no-edit` before every push; **never hand-edit on the box**; verify on box after pull. LAPTOP uses `python3`; BOX uses `python` inside the venv. Terminal identity: `peter@pipeline-prod` = BOX, `peteralkema@NL-L-…` = LAPTOP.
- **Patch discipline that works:** verify-before-run (confirm the code landed AND a query returns real data before spending a render); each idempotent patch verifies its anchor exists exactly once and refuses to half-apply; backs up to a `.pre_*` sidecar.
- **Channel/config resolution is project-anchored** (fixed 2026-06-09): config resolves by the project path, not the launch directory, and the cache is keyed per channel dir — so the voice/look is decided by *what you're rendering*, not *where you launched from*. (When adding a new channel.json, diff its keys against a known-good one — a `voice_id` → `voiceId` typo silently rendered Victor on the Sacred Dawn first dry-run.)
- **Long box jobs run in `tmux`** (`tmux new -s orch`) so a dropped SSH pipe can't orphan a run parked at a gate; `tmux attach -t orch` recovers the live gate.

---

## 8. Authoring craft (before the machine)

**`ante-machinam.md` (v2.0) is the canonical pre-write doc — and the single craft source of truth.** As of v2.0 it absorbed the former `script-craft-principles.md`; that file is retired to a stub pointing here. ante-machinam is now four things in one: the Constitution, the VISUAL-line patterns (Part III), the full craft canon (Part IV), and the threshold into the machine (Part VI).

**The Constitution (seven machine-enforced truths):** every beat carries spoken words (wordless beats halt the build; there is no authored silence — write a short slow line instead); the header carries channel/title/description/tags and `channel` must match the folder; spell out numbers in narration (numerals fine in metadata); one `VISUAL:` line per Mode A beat (it is the image prompt); lock the script first; beat granularity ~5–12s spoken (~15–35 words), hard ceiling ~55 words — split longer or the clip stretches to dead video; **every beat carries an animatable foreground subject (§7) — the still is a frame to be moved, not a picture to be admired (wides are the short minority).**

**Pacing reality:** Inworld reads ~**190–200 wpm measured** (not the old 135 plan). For a target runtime, spoken words ≈ minutes × ~195. A true 10-min episode ≈ 1,900 spoken words. (Sacred Dawn's "Watchers": 2,716 words → 17.7 min.)

**Script-craft canon (channel-agnostic, ante-machinam Part IV — the full treatment):** win the click with a tension/transgression package (title & thumbnail complement, not echo) → cold-open dropped inside a scene with concrete anchors in 10s, arc announced in the first minute, payload front-loaded → hold the body with **recognition beats** (the retention mechanic — one vivid universal/famous specific per key moment), a recurring payoff beat as spine, clock-anchored dread, named humans (or named absence), narrator-to-viewer irony at act breaks, seeds planted early/harvested late → end on the image then a moralised closer reflected at the present-day viewer → comment-bait built into the subject → write ~10–15% long for Inworld's faster read. Run the **hook gate** on the first 60s and the **IV.7 pre-lock audit table** before lock.

**Visual/VISUAL-line patterns (so Flux renders clean first pass):** faceless by default; scene canons over character canons; object-substitution for groups (Flux fails on 3+ figures); empty rooms carry meaning; fire/catastrophe as environment not subject; period-accuracy guards; image models can't render legible text (that's a Mode B card's job). Plus **"Author for motion"** (Part III): the drift-safe foreground-action vocabulary that makes clips actually move without reopening Flux's face/hand/crowd drift.

**Per-voice markup allowlist (Vinny, banked 2026-06-09):** `[laughs]` allowed; `[sigh]` banned (write the exhale into words); `[pause]` capped at two, attached to real spoken words, never standalone, never at a chunk seam.

---

## 9. Strategic principles (the durable lessons)

1. **Packaging beats production** (CTR + AVD in 48h drive distribution).
2. **The system is the moat, not any channel** — bank tool-agnostic principles, encapsulate every service behind one function, diagnose the category behind every reshoot.
3. **Un-filmable vs. re-watchable** (the niche-fit filter, banked 2026-06-09): the machine's edge is *un-filmable lived memory* (the room, the feeling), which AI recreation renders legitimately. Poor fit for *re-watchable media that exists in crisp HD* (games, shows), where an AI impression reads as wrong to an AI-sensitive audience.

   **3b. The un-referenced sublime** (the sharper form of the filter, banked at the Sacred Dawn launch). The decisive test for any new channel: **is there a reference the audience can catch us failing against?** Military failed it twice over — most of it exists in archival footage the engine can't fake, AND the war-buff audience is the most AI-hostile on the platform. Biblical cosmic-primeval *passes it hardest*: no footage of the Watchers descending or the Flood exists, so the AI image isn't competing with a real photo it can be caught failing against — Flux's painterly unreality reads as *awe/the sacred*, the model's weakness becomes the genre's requirement. And the reverent register *wants* the faceless silhouette and object-substitution, closing Flux's face/hand/crowd drift at the same time. → *Yes-reference = knife fight (military, HD history, recognizable places/people); no-reference = open water (scripture, mythology, deep past, imagined future), and the engine does what only it can.* This is now the primary channel-selection filter, alongside Leo's five (monetized / <100k subs / 20k+ avg views / recent virality / reproducible in a pure-AI machine for an AI-indifferent audience).

4. **Served vs. searched:** generational-identity essays are *served* (algorithm-pushed, saturate fast); some lanes (retro gaming) are genuinely *searched* (demand floor). Trends YouTube-Search = mature demand; Web-Search = fresh demand.
5. **Spike-chasing doesn't suit this operation** (banked 2026-06-09): by the time a spike is visible it has usually crested, and the clone swarm follows a breakout within days. The edge is best-execution in permanently-warm, evergreen, served lanes. *Biblical canon is the extreme case: a fixed, finite, public-domain corpus with permanent non-seasonal demand — you cannot saturate the Flood; the only saturation risk is in the packaging treadmill, which you opt out of by anchoring on the canon (reverent curiosity, not shock-bait).*
6. **Title and thumbnail must complement, not echo** — image carries the "what," title carries the "why-click."
7. **Topic clusters beat topic variety; session watch time compounds; volume generates data; ship first, optimise second.**
8. **Two-audience nostalgia thesis** (You Had To Be There): nostalgia serves both recognition viewers (lived it) and discovery viewers (the past is foreign and fascinating) — bolder thumbnails recruit the discovery audience.
9. **Attribution discipline as moat** (Sacred Dawn): in any lane where the audience is AI-indifferent but not quality- or accuracy-indifferent (faith, history), reverent best-execution + visible sourcing is the differentiator the slideshow/shock-bait factories can't match — and it doubles as the demonetization/credibility guard.
10. **The front-loaded effort curve** (banked at the Enoch tiered-render proof). Engagement is front-weighted: viewers decide to stay in the opening, and once committed, voice + narrative carry the back half. So **spend the expensive signal (true Kling motion) on the front ~40 beats where the retention decision is made, and floor the rest** (Ken-Burns) where attention is already won. This gives a **fixed per-video motion budget (~$16.80) independent of runtime** — the thing that makes long-form *and* multi-channel daily cadence affordable simultaneously — with no felt loss of quality (the Enoch seam was invisible; concentrating the budget even made the front motion read as *more* generous). **Provenance is why it's trustworthy, not a guess:** Peter learned the identical law on Udemy — front-loaded high-effort "human" lessons, back-loaded stock footage; ratings never suffered, minutes-consumed (= revenue) climbed. Same law, two media. The portable instructional-design instinct — knowing *where* in a piece effort converts to retention — is itself a moat the pure-technologist operators don't have. *Open: mine the rest of the Udemy completion-data instincts (hook specificity, cost of a slow open, re-watch vs skip points) as testable packaging-layer hypotheses. And validate the N=40 split against real AVD — if retention dips at the seam, tune N per format (Final Hours may want 50; Sacred Dawn held at 40).*

---

## 10. Current state (14 June 2026)

**Live channels:** Final Hours (primary), Sacred Dawn, You Had To Be There, Success Coach (packaging fixes in progress).

**Shipped since the 11 June Sacred Dawn launch (the Mission Control + tiered-render arc):**
- **Mission Control matured into the full operator console** (§5.1) — the "AI Film Director Storyboard and Control Panel" on `:8002`. Now browser-only end to end: create → launch → gates-as-page-state → per-beat storyboard → tiered render → assemble → reset. URL-persisted (refresh stays in project; Reset = base), in-place clip reload, stop-at-stills gate, skip-existing resume, per-channel default motion, render-policy field, Reset recovery. ~14 idempotent patches through the strict workflow.
- **TIERED RENDER cost limiter proven** (§5.2) — Kling front *N* / free Ken-Burns floor for the rest; fixed ~$16.80/video at N=40 regardless of length (~70% under all-Kling).
- **Motion direction** (§5.3) — per-beat motion field on the storyboard + per-channel `default_motion`; fast/dramatic motion proved the right register on Sacred Dawn.
- **Enoch shipped** — first full **132-beat** video through the tiered render (Sacred Dawn). Peter's verdict: best-looking yet (colour, graphics, fast motion), the 40→41 Kling→Ken-Burns handoff **hardly noticeable**, and the front-loaded Kling "felt much longer." Validated the lever *and* the front-loaded-effort-curve principle (§9.10). Upload manual (Entertainment, tags, Altered-content = Yes in Studio).

**Banked this session (full detail in `_SESSION-NOTES-mission-control-statusline-a1-final-video-panel.md`):**
- **Live status line** (§5.1) shipped + proven (counts off disk; elapsed for audio/assemble).
- **Version stamp** (§5.1) shipped — heading shows `v0.X · <sha>`; **Mission Control is now v0.9.** Caught a real stale-deploy (code on disk, not committed) the same session it was built.
- **A1 + false-hang fix** (§5.4) shipped — the gate→animating phase write (a healthy run no longer looks hung at the stills gate) + heartbeat/stale detection.
- **FINAL VIDEO panel** (§5.5) shipped — two-column top, autoplaying assembled video, header metadata, working Download; Upload disabled pending auth.
- Earlier in the session: **clip-reload-in-place** and **URL persistence** (refresh stays in project, Reset leaves).
- **New bugs banked:** the strip's animate label is hardcoded "Kling" and doesn't reflect the tiered split (cosmetic); the `default_motion` dead-default (§5.3); `finish --plan` not side-effect-free (mkdirs before the early-exit, CWD-relative path); open question whether `cmd_stills` passes `safety_tolerance:"5"` on the first stills pass; the double-job-record gotcha (a relaunch leaves a stale record in `.mc_jobs/`; build_state should prefer the freshest active one). Plus the discipline note: **patch source stays pure ASCII** (a stray ellipsis/`"""`-in-docstring broke a patch on the laptop this session).
- **Data points:** audio leg ~30 min / ~14s per beat on 132 beats; Kling ~30–60s + $0.42 vs Ken-Burns ~1–2s free.

**Specs written, not built:** the **upload wiring** behind the FINAL VIDEO panel's disabled button — `auth.py` fix + `/api/upload` (next session). Also still: decade-look Phase 2 (grade layer); multi-project / daemonized review server.

**Open from this session (top of next):** the **live status line** + **A1 heartbeat** (both in `build_state`, ship together); the vanished storyboard body at `gate_stills` to check; then the upload panel (needs `auth.py` fixed + `/api/upload` first).

---

## 11. Roadmap & backlog

**Near-term backlog (priority):**
1. **Upload wiring — finish the FINAL VIDEO panel** (the panel + Download shipped; the Upload button is disabled). The dependency chain: **fix `auth.py`** (CLIENT_SECRET/TOKEN_FILE variable-swap; headless OAuth → auth on laptop, `scp token.json` to box; correct Final Hours brand account `peteralkema2@gmail.com`; 7-day-testing token expiry) → add **`/api/upload`** (wire the existing `shared/upload_episode.py`) + GET/POST schedule/visibility fields (mirror `/api/meta` + `render_policy`) → enable the panel's Upload button. Single-video auto-upload; **batched jobs exit at `final_video.mp4`** (header flag, e.g. `parts: 4`). Until then, uploads manual via Studio (Entertainment, tags, Altered-content = Yes).
2. **`default_motion` dead-default fix** (§5.3) — make the storyboard-authoring guidance channel-aware so the per-channel default fires instead of being overridden by the slow string baked into every beat. Read `recreation_pipeline.py` ~95–115 / ~470–485 / ~1245–1275 first. (Enoch was hot-fixed per-project this session; this is the root-cause fix.)
3. **Cheap correctness items:** strip animate label says "Kling" regardless of the tiered split — make it reflect Kling-≤N / Ken-Burns->N; confirm `cmd_stills` passes `safety_tolerance:"5"` on the first stills pass (stops black frames at the gate); fix `finish --plan` (mkdir-before-exit + CWD-relative path); build_state should prefer the freshest `.mc_jobs` record (double-job gotcha).
4. **v2 motion routing** (§5.2) — route Kling-vs-Ken-Burns by which beats *earn* motion (duration/action), not the positional first-N split.
5. **Music** — decide generated (`make_music.py`) vs curated Jamendo; wire chosen path into convergence. (`finish` already has `--music`/`--no-music`; generates a bed unless `--no-music`.)
6. **Decade-look Phase 2** — write+commit `film_emulate.py` grade presets, wire a single grade pass into `assemble()`.
7. **Inworld-layer:** wire dead `speed` key; fix sentence-chunking voice-drift; **chunk-validation guard**; kill hardcoded voice/gate labels (leg prints "Victor" regardless of resolved voice).
8. **Beat-granularity discipline** — bake "~8–12s/beat, ~90–110 beats for a ~20-min film" into authoring.
9. **Banked-for-later:** parallel fal animation (semaphore, ~5–8× faster); formalised batch orchestration (split at the stills-review seam); `.gitignore` for `*.bak*/*.pre_*`; move the **Kling-count field into the always-visible controls strip** (currently only at the stills gate — breaks the always-visible-but-disabled rule).

**Long horizon (the real destination):** sustained-character continuity → multi-scene narrative arcs (a tree: film → acts → scenes → beats; never let beat logic assume one file = one video) → layered/multi-voice audio → directable performance → a "cinematographer in the system." Endpoint (~2029–31): a single operator ships a 75-minute "amateur movie" through this pipeline for a few hundred dollars. The technology gets there regardless; the question is *who's positioned* — and the position that wins is system-operator-with-creative-voice, built 5 years early and refined across hundreds of small videos.

---

## 12. Quick-reference facts & gotchas

- **Paths:** box repo `~/Pipeline`; laptop `~/Projects/Pipeline`; venv `~/venvs/pipeline`; channels at `<channel>/`, projects at `<channel>/projects/<slug>/`.
- **Channel header traps:** `final_hours` → `final-hours/`, `sacred_dawn` → `sacred-dawn/` (hyphen/underscore auto-resolved); but a true alias does NOT resolve — Synthetic must use `channel: synthetic`, not `synthetic_press`. When in doubt, set `channel` to the exact folder name.
- **channel.json:** `voice_id` is snake_case (`voiceId` → silent Victor fallback); Final Hours has no resolution key (default works); keys are `name`/`voice_id`/`style_suffix`/`default_music_prompt`/`base_canon`/`upload`. Diff a new one against a known-good file before first run.
- **`ffprobe`, not the player**, for true duration (concatenated-MP3 header bug shows ~2×).
- **OAuth:** Final Hours has working auth (under peteralkema2@gmail.com / `youtube-upload-test-497220`); `auth.py` has a known CLIENT_SECRET/TOKEN_FILE variable-swap bug; OAuth app in 7-day testing mode → weekly token expiry. Sacred Dawn / Synthetic / others: upload not set up.
- **Mission Control:** `http://116.202.18.68:8002/?key=fh2026`, service `mission-control.service`, restart `systemctl --user restart mission-control.service`. **Version check:** the heading reads `v0.X · <sha>`; that SHA must equal `git rev-parse --short HEAD` on the box — if not, the tab is stale (hard-refresh). `/api/state` also returns `version`+`sha`. **Currently v0.9.** After any page-JS change, node-check the served page before trusting it (extract the last `<script>` block, `node --check` → `PAGE_JS_VALID`). Gate state lives in `<repo>/.mc_jobs/<job_id>.json` (`gate.decision`); a relaunch leaves a stale prior record there (harmless). `state.channel` = header (underscore) name; the dropdown/`__SEL_VIEW` use the folder (hyphen) name; `resolve_paths` is tolerant. The old `review.service` on `:8001` is separate and untouched.
- **Patch discipline (banked this session):** patch source stays **pure ASCII** — a stray unicode ellipsis and a `"""` inside a `"""` docstring each broke a patch on the laptop before it could run. Simulate Python edits before handing a patch over.
- **Tiered render flags:** `finish --kling-count N` (Kling for first N beats, Ken-Burns floor for the rest; overrides `render_policy.json` `{"kling_count":N}`; default 40), `--plan` (print routing, no cost — *currently must be run from `~/Pipeline/sacred-dawn/projects` due to a CWD-relative bug*), `--assemble-only` (free re-stitch from existing clips), `--animate-only`, `--force`, `--music MP3` / `--no-music`. Real `finish` signature takes `--project` only (no `--beats`). N=40 ≈ $16.80/video.
- **Review server (legacy):** kill stale before start (`lsof -ti :8001 | xargs kill -9`); superseded for live operation by Mission Control (:8002).
- **Two pipeline gates** are honor-system / aesthetic + factual; the orchestrator has **no `--from` resume** (a re-run re-spends every leg). Recover an orphaned post-stills run with `finish --project modea --animate-only` (re-spends nothing).
- **Audio gate:** listen before keep/swap — the printed "Victor" label is cosmetic; the real read is the resolved `voice_id`.
- **Mac-only SSL:** monkey-patch `httpx.Client.__init__` to `verify=False` before fal imports (corporate Zscaler gateway); not needed on the box.

---

*This document is the umbrella reference for the whole operation. The deeper docs sit beneath it: `ante-machinam.md` (the pre-write bible — Constitution + the full craft canon + the threshold; absorbed `script-craft-principles.md` at v2.0), `PIPELINE_PLAYBOOK.md` (operational layer, every command), `production-system-as-moat.md` (the thesis), the per-channel docs (`sacred-dawn-creed.md`, the strategy/backlog docs), and the dated SESSION-NOTES. Update this file's date + the current-state and backlog sections whenever a session banks something that changes the shape of the operation.*
