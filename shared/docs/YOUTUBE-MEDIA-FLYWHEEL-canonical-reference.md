# YouTube Media Flywheel — Canonical Project Reference
*The single comprehensive description of the whole operation. Load this first in any new session to get to full context fast.*
*Maintained by Peter + Claude. Last updated: 10 June 2026 (after the You Had To Be There gaming-series session + pipeline hardening).*

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
| **You Had To Be There** (@you-had-to-be-there) | Cinematic AI recreation of *vanished lived experience* — un-filmable everyday nostalgia (1970s childhood, gaming-before-internet, etc.) | Mode A, decade-variable look | **Vinny** (warm wry Brooklyn storyteller) | **Live, newest.** First channel to use per-job decade looks in production. |
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
- **audio_leg** (always, first): `build_audio_script.py` → `generate_episode_vo.py` (Inworld) → Whisper align → `build_beat_durations.py` → `durations.json`. **+ audio-continuity QC** (built 2026-06-09) auto-runs at the gate. Then the **audio gate** (keep / swap-in-human-read).
- **modeb_leg** (if Mode B beats): `dispatch.py` → Remotion render at each component's own duration → **Mode B correctness gate** (contact sheet, factual y/n).
- **modea_leg** (if Mode A beats): `modea_beats.py` → `recreation_pipeline.py stills` (fal Flux) → **stills review gate** → `finish --animate-only` (fal Kling).
- **convergence_leg**: pool clips → `assemble_episode.py` (interleave in true beat order via index map, hold each to audio-measured duration, mux ducked music bed) → `final_video.mp4`. (Publish half — thumbnail gate, schedule gate, upload — built for some channels, not all.)

**The two gates** (the only human stops): **stills review** (aesthetic firewall — browser review page) and **Mode B correctness** (factual firewall — numbers/quotes/attributions read right?).

**`durations.json` is the single timing source.** Produced once by the audio leg; consumed by dispatch, assemble, and the Mode B review. Audio is the source of truth; visuals hang off measured audio for both modes.

**`recreation_pipeline.py` is the shared engine** — generate_voiceover (Inworld), stills (Flux), finish/animate (Kling), assemble (ffmpeg). A change ripples into both legs; treat with care.

**Per-job decade look (the look resolver, Phase 1 shipped 2026-06-09):** look resolves **channel-then-project** — `channel.json` gives the default `style_suffix`; a project `look.json` overrides it (`{"look":"hi8_90s"}`). `look_resolver.py` walks up from the still's output path to find it, mirroring how channel config resolves. Registry: `kodachrome_50s`, `color_60s`, `super8_70s`, `vhs_80s`, `hi8_90s`, `digicam_2000s` (decade aliases work). "The channel owns the frame; the job owns the film stock." Phase 1 = stills look only (Flux `style_suffix`); **Phase 2 (not built) = the grade layer** (`film_emulate.py` doesn't yet exist) for true VHS/digicam texture.

**Batched multi-video jobs:** nothing requires one script = one video (the pipeline is beat-based). A script can hold several self-contained parts (each its own cold open + close), run as ONE job, and be cut into N videos in post (Filmora). Constraint: **one look per job** (the resolver caches per project) — batch by shared look. Implication for upload: a batched job must **exit at `final_video.mp4`** and not auto-upload (one job → many videos breaks single-metadata).

---

## 6. The tech stack (the fast layer — swappable)

- **Stills:** fal.ai Flux-pro/v1.1. (Pass `safety_tolerance:"5"` to stop silent ~7KB black-PNG rejections.)
- **Animation:** fal Kling (O3 Standard). Clips are ~5s native; beats run 7–21s, so assembly slow-fills/stretches (invisible to ~2–3×, dead past that → split the beat in the script).
- **TTS:** Inworld (`inworld-tts-1.5-max`). Voices: Victor (Final Hours/Synthetic/hooks), Ashley (Success Coach lessons), Vinny (You Had To Be There). Markup performs per-voice — prove it before relying on it.
- **Alignment:** Whisper (local) → word timestamps. Drift fixed via `difflib.SequenceMatcher` coverage matching.
- **Mode B graphics:** Remotion (Node 20.20.2 via nvm, Remotion 4.0.472 on the box). Six components: HighlightedHeadline, LowerThird, NumberCounter, ChapterCard, QuoteCard, DocumentReveal.
- **Assembly:** ffmpeg (streaming concat demuxer; folds into `assemble()` to avoid moviepy OOM). `ffprobe` is the only reliable clip-duration source (concatenated-MP3 header bug makes players show ~2× true length).
- **Music:** `make_music.py` (Claude writes one loopable instrumental prompt → fal ElevenLabs Music → `music.mp3`) — standalone, **not yet wired into convergence**. Or curated Jamendo (Final Hours: VOICE_LEVEL 1.15 / MUSIC_LEVEL 0.07).
- **Research/analytics:** NexLev MCP (`youtube_channel_outliers`, `youtube_search`, `search_videos`); dashboard at dashboard.nexlev.io. Google Trends (served-vs-searched, Rising-Queries) as a manual radar.
- **Success Coach extras:** Pexels (hook footage), Pixabay (lesson footage), Clickly (thumbnails), Claude API (hooks/titles), YouTube Data API.
- **Thumbnails:** Clickly / Nano-Banana-style edits; `make_thumbnail.py` (rembg U2Net).

---

## 7. Infrastructure & workflow discipline

- **Box:** Hetzner `pipeline-prod` at `116.202.18.68`, SSH port 443, user `peter`, venv `~/venvs/pipeline/bin/activate`, 16GB RAM (upgraded June 2026). Repo at `~/Pipeline`.
- **Repo:** `github.com/peteralkema/Pipeline`. Laptop clone `~/Projects/Pipeline`.
- **The strict workflow (non-negotiable):** all code edits on laptop → GitHub → box via **idempotent `patch_*.py` scripts** (or full-file rewrites for deletion-heavy changes); `git pull --no-edit` before every push; **never hand-edit on the box**; verify on box after pull. LAPTOP uses `python3`; BOX uses `python` inside the venv. Terminal identity: `peter@pipeline-prod` = BOX, `peteralkema@NL-L-…` = LAPTOP.
- **Patch discipline that works:** verify-before-run (confirm the code landed AND a query returns real data before spending a render); each idempotent patch verifies its anchor exists exactly once and refuses to half-apply; backs up to a `.pre_*` sidecar.
- **Channel/config resolution is now project-anchored** (fixed 2026-06-09): config resolves by the project path, not the launch directory, and the cache is keyed per channel dir — so the voice/look is decided by *what you're rendering*, not *where you launched from*.

---

## 8. Authoring craft (before the machine)

**`ante-machinam.md` is the canonical pre-write doc.** The Constitution (six machine-enforced truths): every beat carries spoken words (wordless beats halt the build; there is no authored silence — write a short slow line instead); the header carries channel/title/description/tags and `channel` must match the folder; spell out numbers in narration (numerals fine in metadata); one `VISUAL:` line per Mode A beat (it is the image prompt); lock the script first; beat granularity ~5–12s spoken (~15–35 words), hard ceiling ~55 words — split longer or the clip stretches to dead video.

**Pacing reality:** Inworld/Vinny reads ~**190–200 wpm measured** (not the old 135 plan). For a target runtime, spoken words ≈ minutes × ~195. A true 10-min episode ≈ 1,900 spoken words.

**Script-craft spine (channel-agnostic):** cold-open with concrete facts in 10s; sensation not description; clock-anchor the dread; name the surrounding humans (or name the absence); narrator-to-viewer irony at act breaks; plant seeds early, harvest late; end on the image then a moralised closer reflected at the present-day viewer. Run the **hook gate** (7 questions) on the first 60 seconds before lock.

**Visual/VISUAL-line patterns (so Flux renders clean first pass):** faceless by default (resolve a face only when the audience must bond with one documented person); scene canons over character canons (variety from angle/detail within a locked location); object-substitution for groups (Flux fails on 3+ figures); empty rooms carry meaning; fire/catastrophe as environment not subject; period-accuracy guards; image models can't render legible text (that's a Mode B card's job).

**Per-voice markup allowlist (Vinny, banked 2026-06-09):** `[laughs]` allowed (performs); `[sigh]` banned (doesn't perform — write the exhale into words); `[pause]` capped at two, attached to real spoken words, never standalone, never at a chunk seam. (A four-stack `[pause]` at a seam caused a 44-second silent hole when a failed Inworld chunk concatenated as dead air — the origin of the audio-continuity QC.)

---

## 9. Strategic principles (the durable lessons)

1. **Packaging beats production** (CTR + AVD in 48h drive distribution).
2. **The system is the moat, not any channel** — bank tool-agnostic principles, encapsulate every service behind one function, diagnose the category behind every reshoot.
3. **Un-filmable vs. re-watchable** (the niche-fit filter, banked 2026-06-09): the machine's edge is *un-filmable lived memory* (the room, the feeling), which AI recreation renders legitimately. It's a poor fit for *re-watchable media that exists in crisp HD* (games, shows), where an AI impression reads as wrong to an AI-sensitive audience. → a sixth niche-selection criterion alongside Leo's five (monetized / <100k subs / 20k+ avg views / recent virality / reproducible in a pure-AI machine for an AI-indifferent audience).
4. **Served vs. searched:** generational-identity essays are *served* (algorithm-pushed, saturate fast); some lanes (retro gaming) are genuinely *searched* (demand floor). Trends YouTube-Search = mature demand; Web-Search = fresh demand.
5. **Spike-chasing doesn't suit this operation** (banked 2026-06-09): by the time a spike is visible in Trends/NexLev it has usually crested, and the clone swarm follows a breakout within days — "proven topic with no graveyard" is largely a unicorn (demand and the graveyard are the same signal weeks apart). The edge is best-execution in permanently-warm, evergreen, served lanes. Use Rising-Queries/breakout panels for *detail-mining* authentic era artifacts, not topic-picking.
6. **Title and thumbnail must complement, not echo** — image carries the "what," title carries the "why-click."
7. **Topic clusters beat topic variety; session watch time compounds; volume generates data; ship first, optimise second.**
8. **Two-audience nostalgia thesis** (You Had To Be There): nostalgia serves both recognition viewers (lived it) and discovery viewers (the past is foreign and fascinating) — bolder thumbnails recruit the discovery audience, who can't be disappointed because the era is foreign to them.

---

## 10. Current state (10 June 2026)

**Live channels:** Final Hours (primary), You Had To Be There (newest; gaming series just shipped), Success Coach (monetized, packaging fixes in progress).

**Shipped this session (deployed + confirmed on box):**
- Decade look-override **Phase 1** (`look_resolver.py` + patch; per-job `look.json`; stills-look layer).
- **Audio-continuity QC** built into the audio gate (`audio_qc.py` + patch; auto-scans Whisper for silence holes; read-only, fails soft).
- **Tunnel-free review server** (public bind + token auth; `/stills/` and `/api/` key-exempt so the page and buttons work without an SSH tunnel).
- **Vinny markup rules** (authoring law).
- **Project-anchored config/voice resolution** (root-cause fix for a wrong-voice bug where a render resolved Victor instead of Vinny because config was found by CWD walk-up; now anchored on the project; voice printed at the gate).
- **You Had To Be There gaming series** — 4-part `hi8_90s` batched job ("Gaming Before the Internet": Nintendo Christmas / renting a game / couch co-op / 90s arcade), rendered, cut into four in Filmora, Vinny audio regenerated correctly, thumbnails built (consistent set), titles + descriptions finalised, ready to upload. First full validation of the look-override on a real job.

**Specs written (not built):** decade-look Phase 2 (grade layer); multi-project / daemonized review server (project-in-URL).

---

## 11. Roadmap & backlog

**Near-term backlog (priority):**
1. **Motion-direction on the stills review** — per-beat MOTION control → Kling prompt in the animate leg (do after seeing default motion on the gaming series).
2. **Music** — decide generated (`make_music.py`) vs curated Jamendo for You Had To Be There; wire chosen path into convergence (`make_music.py` needs `.env` sourcing).
3. **Channel-agnostic upload step with a batch exit-gate** — single-video jobs may auto-upload with per-project metadata; **batched jobs must exit at `final_video.mp4`** (header flag, e.g. `parts: 4`). Until built, all uploads manual via Studio (set category=Entertainment not People & Blogs; add tags).
4. **Decade-look Phase 2** — write+commit `film_emulate.py` grade presets, wire a single grade pass into `assemble()`.
5. **Multi-project review server** — project-in-URL refactor (one server serves all projects) → daemonize with home-IP firewall lock. Plus quick wins: the Mode A leg should build `review.html` automatically after stills; the stills-gate prompt text still prints the old tunnel instructions (now wrong); `serve_review.py`'s own `generate_still` should resolve the per-job look.
6. **Inworld-layer:** wire dead `speed` key; fix sentence-chunking voice-drift; **chunk-validation guard** (the *prevention* half — retry/hard-fail a bad chunk instead of shipping a hole; QC is the detection half); kill hardcoded voice/gate labels.
7. **Banked-for-later:** parallel fal animation (semaphore, ~5–8× faster); formalised batch orchestration (split at the stills-review seam); `.gitignore` for `*.bak*/*.pre_*`.

**Long horizon (the real destination):** sustained-character continuity → multi-scene narrative arcs (a tree: film → acts → scenes → beats; never let beat logic assume one file = one video) → layered/multi-voice audio → directable performance → a "cinematographer in the system." Endpoint (~2029–31): a single operator ships a 75-minute "amateur movie" through this pipeline for a few hundred dollars. The technology gets there regardless; the question is *who's positioned* — and the position that wins is system-operator-with-creative-voice, built 5 years early and refined across hundreds of small videos.

---

## 12. Quick-reference facts & gotchas

- **Paths:** box repo `~/Pipeline`; laptop `~/Projects/Pipeline`; venv `~/venvs/pipeline`; channels at `<channel>/`, projects at `<channel>/projects/<slug>/`.
- **Channel header traps:** `final_hours` → `final-hours/` (hyphen/underscore auto-resolved); but a true alias does NOT resolve — Synthetic must use `channel: synthetic`, not `synthetic_press`. When in doubt, set `channel` to the exact folder name.
- **`ffprobe`, not the player**, for true duration (concatenated-MP3 header bug shows ~2×).
- **OAuth:** Final Hours has working auth (under the peteralkema2@gmail.com brand account / `youtube-upload-test-497220`); `auth.py` has a known CLIENT_SECRET/TOKEN_FILE variable-swap bug; OAuth app in 7-day testing mode → weekly token expiry. Synthetic/others: upload not set up.
- **Review server:** kill stale before start (`lsof -ti :8001 | xargs kill -9`); run in a tmux window inside the `orch` session to survive disconnect; key-in-URL is light auth for short sessions.
- **Two pipeline gates** are honor-system / aesthetic + factual; the orchestrator has no `--from` resume (a re-run re-spends every leg).
- **Mac-only SSL:** monkey-patch `httpx.Client.__init__` to `verify=False` before fal imports (corporate Zscaler gateway); not needed on the box.

---

*This document is the umbrella reference for the whole operation. The deeper docs sit beneath it: `PIPELINE_PLAYBOOK.md` (operational layer, every command), `ante-machinam.md` (pre-write craft + the Constitution), `STARTUP_PACK.md` (the two-attachment load-once context + craft), `ORCHESTRATOR-DEPENDENCY-MAP.md` (what shells out to what), `production-system-as-moat.md` (the thesis), the per-channel strategy/backlog docs, and the dated SESSION-NOTES. Update this file's date + the current-state and backlog sections whenever a session banks something that changes the shape of the operation.*
