# Pipeline Playbook
*The full lifecycle from topic to published video, across all channels.*
*v2.1 — 5 June 2026. Adds the orchestrator (the conductor) as the operational spine, on top of the v2.0 box-native rewrite. Written after shipping Eyam as the first fully orchestrated video.*

This is the single source of truth for how to make a video. Read it before starting any new project. Update it when banking new rules from production.

This is the **operational** layer. Companion documents (the craft layers) are consolidated in `STARTUP_PACK.md`, which you load alongside this one at the start of any production chat. The deep-reference originals:
- `shared/docs/script-craft-principles.md` — what makes a good script (applied at Step 3)
- `shared/docs/production-patterns-that-work.md` — architectural decisions that minimise stills drift (applied at Step 5/8)
- `shared/docs/hook-craft-library.md` — first-60-seconds corpus + 7-question stress test (applied at Step 4.5)
- `shared/docs/hetzner-runbook.md` — how the production box is built and rebuilt
- `shared/rulebook.json` + `<channel>/rulebook.json` — the accumulated negative-rule moat
- `shared/docs/calibration-reference.md` — channel positioning and retention benchmarks

---

## What changed since v1 (read once)

v1 described the laptop world and the manual step-by-step flow. Two things have changed since:

**1. Everything runs on the Hetzner box (v2.0).** The craft layers are unchanged; the operational layer is box-native.
- Production runs on the box, not the laptop. Long jobs run in **tmux**, not under `caffeinate`. Paths are `~/Pipeline/...`. The governing rule is now *no Hetzner = no videos.*
- The `verify=False` SSL monkey-patch is **gone and must never return.** TLS is correct via certifi + `shared/ssl_compat.py`. Any instruction to disable verification is a security regression.
- `safety_tolerance: "5"` is baked into `recreation_pipeline.py` (gated to flux). No longer a TODO.
- Upload reads `metadata.json` and no longer generates SRT. Flow is metadata.json → unlisted upload → review → schedule.
- Stills review on the box uses an SSH tunnel (the review server binds localhost-only).

**2. The orchestrator now runs the middle of the pipeline (v2.1).** `shared/orchestrate.py` is a thin **conductor** that drives storyboard → audit → canon → stills → finish → true-up as one command, with exactly **two human gates**. It contains zero generation logic — it calls the existing scripts as subprocesses and guards each phase's output. You no longer run Steps 7–11 by hand for a normal video; you run the orchestrator and answer two prompts. The manual steps are preserved in Part 4 for debugging and re-runs.

Also banked this cycle (Eyam, the first orchestrated video):
- **moviepy OOM at assembly is fixed permanently** — ffmpeg-based `assemble()` folded into `recreation_pipeline.py` (streaming concat, low memory). The old moviepy concat is kept as `assemble_moviepy()` fallback.
- **`canon.json` is now a project input file**, not a script header. You write it; the orchestrator consumes it.
- **`build_canon.py`** replaces the old keyword-routing approach: Claude assigns each audited shot to a canon scene **by visual subject**, fixing the subject-vs-mention bug.
- **Shot-grammar variety** is now in the storyboard prompt (framing vocabulary, no-two-consecutive-same-framing, close framings prefer hands/objects).
- **The silent-reject audit reads file sizes, not just the threshold** — real dark/night/water shots trip `-size -200k` as false positives.

---

# PART 1 — QUICK REFERENCE CARD

All commands assume you are SSH'd into the box, inside the channel root (`cd ~/Pipeline/final-hours`), venv active (`source ~/venvs/pipeline/bin/activate`).

```bash
ssh -p 443 peter@116.202.18.68
source ~/venvs/pipeline/bin/activate
cd ~/Pipeline/final-hours
```

### Step 0 — MANDATORY pre-read (every video, no exceptions)

Before any script writing or storyboard generation, read and apply the craft layers (now all in `STARTUP_PACK.md`): the 10 script-craft principles + pre-lock audit table; the 12 production patterns; the hook 7-question stress test; the channel + shared `rulebook.json`; the calibration reference.

**Audit gate before script lock.** Fill in the pre-lock audit table. Any "weak" or "missing" cell → revise before canon or storyboard.

**Audit gate before stills lock.** The orchestrator's discipline-audit phase handles face/expression rewrites automatically, but you still eyeball the storyboard for multi-character compositions, group scenes, and fire/storm-as-subject framings — rewrite those in the script/canon before the run burns fal credits.

The cost of reading is 5 minutes. The cost of not reading is a video that ships with documented retention-failure modes (the KLM Tenerife v1 lesson).

**Exception — disposable infrastructure tests.** When the goal is to prove plumbing, not ship a flagship, a compressed Step 0 is legitimate (concrete cold open, clock-anchored dread, one or two silent beats, image-not-explanation close; skip the full audit table). Be deliberate about which mode you're in.

### Pre-production (you do this by hand — the orchestrator starts at Step 7)

**Step 1.** Pick a topic. NexLev to validate demand; check no direct format competitor owns the lane. Bank the decision in the channel backlog.

**Step 2.** Research the protagonist and documented facts (web search for sources, family accounts, contemporary reporting).

**Step 3.** Decide title (channel pattern), protagonist (one specific human or deliberate anonymity), apply the craft principles, run the audit table before locking.

**Step 4.** Write the script as `projects/<project>/script.md` (with production notes and silent-beat markers).

**Step 4.5.** Stress-test the first 60 seconds against the hook 7-question gate. Fix the hook before storyboarding.

**Step 5.** Write canon as **`projects/<project>/canon.json`** — a JSON dict `{token: "scene/character description"}`, one entry per recurring scene or anonymised protagonist. Prefer **scene canons over character canons**; apply **face-never-resolved** for anonymous protagonists; anonymise ensemble via framing, not canon. *This file is the orchestrator's canon input — see Part 2.*

**Step 6.** Extract pure narration to **`projects/<project>/<project>_script.txt`** — prose only, no production notes, no silent-beat markers, no canon block. This is what the pipeline ingests.

### Steps 7–11 — RUN THE ORCHESTRATOR (the conductor)

With `canon.json` and `<project>_script.txt` in place, one command drives the rest:

```bash
tmux new -s render          # so the long render survives disconnect
python ../shared/orchestrate.py --project projects/<project>
```

It runs: **preflight → storyboard → discipline-audit → build_canon → [GATE 1] → stills → silent-reject check → [GATE 2] → finish → true-up.** You answer two prompts (Gate 1 and Gate 2); everything else is automatic. Re-run cheaply from any phase with `--start-phase <storyboard|canon|stills|finish>`. Full detail, gate behaviour, and the Gate-2 copy-paste blocks are in **Part 2**.

### Step 12 — Publication

Write `metadata.json`, attach a thumbnail (made in Clickly on the laptop, scp'd over), upload unlisted, review, then schedule:

```bash
# metadata.json: {"title": "...", "description": "...", "tags": [...]}
python upload.py --project projects/<project> --privacy unlisted
```

Open the returned `youtu.be` link on the laptop, review the finished video, then in YouTube Studio set the schedule (01:00 Europe/Warsaw ≈ 19:00 US Eastern), confirm the locked title/thumbnail, and add the pinned comment after publish.

---

# PART 2 — THE ORCHESTRATOR (the conductor)

`shared/orchestrate.py` is a **thin conductor**: it owns sequencing and the two human gates, and contains **zero generation logic**. Every phase shells out to the existing, separately-tested scripts (`recreation_pipeline.py`, `audit_storyboard_discipline.py`, `build_canon.py`). This is deliberate — the conductor stays simple and the generation primitives stay independently runnable (and debuggable) by hand.

### The phase pipeline

```
preflight → storyboard → discipline-audit → build_canon → [GATE 1] →
stills → silent-reject check → [GATE 2] → finish → true-up
```

1. **preflight** — checks the project folder, that `canon.json` exists and parses to a non-empty `{token: description}` dict, that `<project>_script.txt` exists, and that `.env` has the needed keys. Fails fast and loud before spending anything.
2. **storyboard** — `recreation_pipeline.py stills --script ... --storyboard-only`. Claude slices the narration (~one shot per 9 words; shot-grammar variety now baked into the prompt). Writes `storyboard.json`. Costs cents.
3. **discipline-audit** — `audit_storyboard_discipline.py`. Strips face/eye/expression descriptors that collide with face-never-resolved, preserving framing/location/period/atmosphere. Writes `storyboard_audited.json`. ~$0.40.
4. **build_canon** — `build_canon.py`. Reads `storyboard_audited.json` + `canon.json`, uses Claude (sonnet-4-6) to assign **each shot to a canon scene by visual subject** (not keyword match — this fixes the bug where narration *about* a place pulled shots toward the wrong canon), prepends the `{token}` to each image_prompt, writes `beat-scripts/<project>_beats.json`, and prints the per-canon distribution.
5. **GATE 1 — canon distribution (y/n).** The orchestrator prints how many shots landed in each canon and waits. Eyeball it: the dominant visual subject should dominate the distribution. If a scene is wildly under/over-represented, that's a misassignment — fix it (or re-run this phase) before paying for stills. `y` to proceed.
6. **stills** — `recreation_pipeline.py stills --beats ...`. fal generation, ~$15–25, 20–60 min.
7. **silent-reject check (automatic).** flux-pro returns black ~7KB PNGs on safety triggers. The orchestrator scans for these. **It halts only on true blacks (<10 KB);** files in the 10–200 KB band that are merely *dark but real* (night, water) are reported as an FYI, not treated as rejects. (This is the dark-video false-positive lesson, encoded.)
8. **GATE 2 — human stills review (y/n).** The orchestrator pauses and **prints two labelled, copy-paste command blocks** so review can't fumble — see below. Review every shot in the browser, restill the genuine spell-breakers, then type `y` to continue into clips + voiceover + assembly + true-up.
9. **finish** — `recreation_pipeline.py finish --no-music`. Animates stills → clips (Kling), generates voiceover (Inworld), auto-runs Whisper alignment, assembles `final_video.mp4` via the **ffmpeg `assemble()`** (low-memory streaming concat — this is the permanent fix for the moviepy OOM that killed Eyam's first assembly).
10. **true-up** — refreshes Whisper alignment and re-assembles so sync is frame-accurate regardless of any voiceover regeneration during finish.

### Invocation and flags

```bash
python ../shared/orchestrate.py --project projects/<project>
```

- **`--project projects/<name>`** — required. Use the `projects/` prefix, not the bare name.
- **`--canon <path>`** — defaults to `projects/<project>/canon.json`. The orchestrator does **not** generate canon; you write `canon.json` first (Step 5).
- **`--start-phase <phase>`** — resume from a phase without redoing the earlier (paid) ones. Valid: `storyboard`, `canon` (re-runs build_canon assignment from scratch), `stills`, `finish`. Examples:
  - `--start-phase canon` — you edited `canon.json` or want a fresh assignment; reuses the audited storyboard.
  - `--start-phase stills` — beats are final; skip straight to generation.
  - `--start-phase finish` — stills are reviewed and accepted; go straight to clips/voice/assembly.
- **`--box`** — the box address for the printed Gate-2 blocks; defaults to `peter@116.202.18.68`.

Run it inside **tmux** so the long render survives an SSH disconnect. Silent terminal for 30–60s between clips is normal — check progress from a second shell with `ls projects/<project>/clips/ | wc -l`.

### The Gate-2 review blocks (what the orchestrator prints)

At Gate 2 the orchestrator prints two clearly labelled blocks so the box-native review never trips on the two things that bit us before — the missing make-page step, and a stale tunnel port:

**WINDOW A — BOX** (run on the box, in the orchestrator's paused session or a second box shell):
```bash
python ../shared/make_review_page.py --project projects/<project>   # builds review.html FIRST
python ../shared/serve_review.py    --project projects/<project>   # then serves it (binds localhost:8000)
```

**WINDOW B — LAPTOP** (opens a shell on the box AND forwards the port):
```bash
lsof -ti :8000 | xargs kill 2>/dev/null   # kill any leftover tunnel from a previous session
ssh -p 443 -L 8000:localhost:8000 peter@116.202.18.68
```

Then open **`http://localhost:8000`** in the laptop browser — the tunnel routes it to the box, the live badge goes green, Regenerate/Override activate, and fal credentials never leave the box. Review, restill spell-breakers, then return to the orchestrator and type `y`.

### What the orchestrator does NOT do

- It does not write `canon.json` (you do — Step 5).
- It does not select topics, write scripts, or design thumbnails (Steps 1–5, 12 are yours).
- For **Mode B / Synthetic Press explainer beats** (Remotion motion-graphics), the dispatch is different and is **not** part of this orchestrator. Mode B is deterministic, not probabilistic — it is not reviewed at the stills gate; correctness is checked as facts-at-script-time and sync-at-final-cut. When the Synthetic orchestrator is built it will be a separate conductor; beat-processing steps there must skip `mode:"explainer"` beats. (Banked; not built.)

---

# PART 3 — INFRASTRUCTURE (the box-native reality)

Full build/rebuild detail is in `shared/docs/hetzner-runbook.md`. This is the day-to-day mental model.

### The two machines

- **The box (Hetzner) is the runtime.** It renders, uploads, holds the repo, makes every real API call. Headless — no screen, no GUI. The only way in is SSH.
- **The laptop is the control surface.** Edit code, write scripts, design thumbnails (Clickly), `git push`, `scp`, review final cuts. Never a production runtime.

Prompt tells you where you are: laptop ends `%` (zsh); box ends `$` (bash) and shows `pipeline-prod`.

### Access

```bash
ssh -p 443 peter@116.202.18.68
```

SSH is on **port 443**, not 22 (the work network blocks 22). The **Hetzner web console** (console.hetzner.cloud → pipeline-prod → `>_`) is the emergency door — it works even if SSH, firewall, or network all fail.

### Sessions model

A **tmux session ≠ a terminal window.** The tmux session lives on the box and keeps running whether or not you're attached. Detach with Ctrl-b then d; reattach with `tmux attach -t render`. Pattern: one window holds the render (the orchestrator); other SSH windows are free shells for quick checks. If two windows both show the render, they're attached to the same tmux session — detach one to get a free shell back.

### Moving files (no clicking)

```bash
# laptop → box (e.g. thumbnail up)
scp -P 443 ~/Downloads/thumbnail.png peter@116.202.18.68:~/Pipeline/final-hours/projects/<project>/thumbnail.png
# box → laptop (e.g. final cut down to watch)
scp -P 443 peter@116.202.18.68:~/Pipeline/final-hours/projects/<project>/final_video.mp4 ~/Downloads/<project>.mp4
```

Capital `-P 443` for the port (lowercase `-p` preserves timestamps — wrong flag).

### Code flow

The box reads from git, never writes to it. Edit on the laptop → `git push` → `git pull` on the box. Never edit repo files only on the box — they become orphaned/untracked (the exact `upload.py` drift we had to reconcile). The laptop clone is at `~/Projects/Pipeline`; the box repo is `~/Pipeline`. `git fetch && git status` confirms laptop = git = box before trusting a doc or running a build.

---

# PART 4 — FULL MANUAL WALKTHROUGH (for debugging and re-runs)

The orchestrator automates Steps 7–11. Run them by hand when debugging a single phase or when you want finer control. These are the exact subprocesses the conductor calls.

### Architecture

- `.env` at `~/Pipeline/.env` (chmod 600). Five real keys: `ANTHROPIC_API_KEY`, `FAL_KEY`, `INWORLD_API_KEY` (not `INWORLD_TTS_API_KEY`), `JAMENDO_CLIENT_ID` (required if `music_score.py` is in the run path), `PEXELS_API_KEY`.
- `recreation_pipeline.py` lives in `shared/`, invoked as `../shared/recreation_pipeline.py` from a channel root.
- Most commands run from the **channel root**, not inside the project folder — `--project` resolves against CWD. Use `projects/<name>`.
- Channel detection is by the `channel.json` marker (walked up from CWD).
- final-hours uses `projects/<name>/`; success-coach uses `<name>/` directly (inconsistency banked for cleanup).

### Storyboard (Step 7)

```bash
python ../shared/recreation_pipeline.py stills --script projects/<project>/<project>_script.txt --project projects/<project> --storyboard-only
```

Slices into ~one shot per 9 words; shot-grammar variety is in the prompt now (framing vocabulary; no two consecutive same-framing shots; close framings prefer hands/objects). Writes `storyboard.json`.

*Streaming requirement:* `build_storyboard` uses `messages.stream()` with `max_tokens=32000`. If you see a JSON parse error or "Streaming is required…", the streaming code was reverted — restore it (permanent fix, 31 May 2026).

*Shot density (tuning knob):* total duration = word count ÷ ~135 wpm; shot count = word count ÷ words-per-shot. For a calmer, cheaper video, raise words-per-shot and lean on angle-variation-within-canon. (`--words-per-shot N` flag queued in Phase 2.)

### Discipline audit (Step 7.5)

```bash
python ../shared/audit_storyboard_discipline.py --project projects/<project> --verbose
```

Writes `storyboard_audited.json`; ~$0.40; `--verbose` shows the rewrite count.

### Build canon-aware beats (Step 8)

Write `canon.json` first (`{token: description}`), then:

```bash
python ../shared/build_canon.py --project projects/<project>   # reads storyboard_audited.json + canon.json
```

Claude assigns each shot to a canon scene **by visual subject**, prepends `{token}`, writes `beat-scripts/<project>_beats.json`, prints the distribution. Schema is a dict with `canon` and `beats` keys (top-level key is `beats`, not `shots`). Canon tokens go in image_prompts only, never motion_prompts.

Banked editing rules (carried into build_canon's behaviour, still worth knowing for hand-edits):
- Restate wardrobe in the prompt body even with canon — flux honours canon wardrobe inconsistently.
- For face-never-resolved protagonists, restate the framing rule in *every* shot ("from behind", "in silhouette", "face never resolved").
- Rewrite group compositions as object-substitution before generating.
- Restate the era anchor in every prompt ("1666 photoreal cinematic").
- For famous landmarks, add the explicit "NOT the modern X" guard.

**Check the canon distribution before generating stills** (this is Gate 1 in the orchestrator). Narration *about* a place is not a shot *of* it.

### Stills (Step 9) + silent-reject audit (9.5)

```bash
python ../shared/recreation_pipeline.py stills --beats beat-scripts/<project>_beats.json --project projects/<project>
find projects/<project>/stills -maxdepth 1 -name "shot_*.png" -size -200k -printf "%f  %k KB\n" | sort
```

Read the **sizes**: a true reject is ~4–10 KB; a real night/water/dark shot can legitimately be 130–200 KB and trip the `-size -200k` filter — that's a false positive, not a reject. (Brightness-check fix queued in Phase 2.) Reshoot budget: atmospheric / anonymised-protagonist 5–10%; single named character 15–25%; multi-named ensemble 30–50%. Disaster/storm/water scripts run hotter on silent rejects regardless of canon (see Part 6).

### Review (Steps 9.6–10)

```bash
python ../shared/make_review_page.py --project projects/<project>
python ../shared/serve_review.py --project projects/<project>     # binds localhost:8000
# from the LAPTOP, separate terminal: ssh -p 443 -L 8000:localhost:8000 peter@116.202.18.68
```

Open `http://localhost:8000` on the laptop. Reject genuine spell-breakers; accept atmospheric-but-imperfect. Notes mode for soft guidance (~80%); Override mode replaces the prompt entirely for stubborn shots (~20%, lands in 1–2 tries vs 4–6, at the cost of canon consistency for that shot). Every regen backs up the prior still to `stills/_backup/`. Three failures → duplicate an adjacent acceptable shot. *Freelancer handoff:* zip stills + `review.html`; they accept/reject/note and export JSON; run `restill_from_feedback.py --feedback <theirs>.json` on the box — their machine never touches fal credentials.

### Finish (Step 11) + true-up

```bash
tmux new -s render   # or: tmux attach -t render
python -u ../shared/recreation_pipeline.py finish --project projects/<project> --no-music 2>&1 | tee <project>_finish.log
```

Verify `channel.json` voice_id first (Victor for Final Hours, Reed for Success Coach). Animates clips (Kling) → voiceover (Inworld) → Whisper align (downloads `small` model ~470MB once) → **ffmpeg `assemble()`** → `final_video.mp4`. Silent terminal between clips is normal.

*Assembly is now ffmpeg, not moviepy.* `assemble()` trims each clip to its Whisper audio_duration, concatenates via the demuxer (streaming, low-memory), and muxes voice (+ optional music). This is the permanent fix for the moviepy `concatenate_videoclips` OOM that killed Eyam's first assembly even at 16 GB. The old path survives as `assemble_moviepy()` (fallback only).

*True-up before publish (standard, not optional):*
```bash
whisper projects/<project>/voiceover.mp3 --model small --output_format json --output_dir projects/<project>/ --word_timestamps True
python ../shared/align_with_whisper.py --project <project> --verbose
python -u ../shared/recreation_pipeline.py finish --project projects/<project> --no-music --assemble-only
```
The assembler trades small per-shot pacing for zero global drift (narration micro-stretches within a shot) — correct behaviour, don't "fix" it. Documentary tolerates near-accurate sync; dramatic/dialogue content requires a full true-up and zero accepted drift.

*Voiceover duration audit (Principle 11):* `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 projects/<project>/voiceover.mp3`. Inworld renders ~85–90% of the 135-wpm estimate. Write 10–15% more script than the runtime target.

### Thumbnail (parallel with stills) and upload (Step 12)

Thumbnail design starts at script lock; build it in Clickly on the laptop *while stills render on the box*; scp over before upload. `upload.py` attaches `thumbnail.jpg`/`.png` if present, else lets YouTube auto-generate.

**On-brand thumbnail spec.** Default generators produce MrBeast clickbait (shocked face, exclamation) — off-brand for Final Hours, never ship it. On-brand uses the **place or object as subject, never a reaction face**:
> "A cinematic, photorealistic thumbnail of [EVENT/PLACE] in [YEAR], [time/weather]. [SUBJECT: the structure/place/object, period-accurate, with an explicit 'NOT the modern X' guard]. [Catastrophe shown through environment + a single focal point of warm light against a cold dark palette — never faces or bodies]. Wide, monumental, dignified, atmospheric period-drama register. No people, no faces, no figures anywhere. Historically accurate [period] detail."

Text overlay (Clickly text layer, not image-generated): 2–5 words, declarative, no exclamation, no rhetorical question (e.g. "260 DEAD", "THEY STAYED", "THE LIGHTS WENT OUT"). The full dramatic title lives in YouTube's title field. **Brand-over-CTR:** if off-brand clickbait beats on-brand by a small CTR margin, keep on-brand — brand consistency is the compounding moat. A/B test only at real impression volume.

```bash
python upload.py --project projects/<project> --privacy unlisted
```

Reads `metadata.json`, attaches the thumbnail, uploads unlisted, prints the watch URL. **Unlisted-first** for new infra / first-of-its-kind renders — review on the laptop, then in Studio set Scheduled (01:00 Europe/Warsaw), confirm the locked title/thumbnail, add the pinned comment after publish. (`--schedule-cet-1am` exists but forces `private` and skips the unlisted-review window.)

*Retention diagnosis after publish:* pull the curve at 48–72h (Studio → per-video → Audience retention). The curve *shape* is the diagnostic, not view count, and not at <100 views.

---

# PART 5 — TROUBLESHOOTING

**Orchestrator halts at the silent-reject check** → it found true-black (<10 KB) stills. Restill those via the review page; dark-but-real (10–200 KB) are reported as FYI, not halts.

**`canon.json missing` / `not valid JSON` at preflight** → write `canon.json` in the project folder as a non-empty `{token: description}` dict before running the orchestrator.

**Re-run a phase without redoing paid work** → `--start-phase <storyboard|canon|stills|finish>`.

**Render must survive disconnect** → run the orchestrator (or `finish`) in tmux.

**Can't reach the box** → SSH is on 443, not 22. If that fails, the Hetzner web console is the always-available door.

**Review page won't load / badge red** → the tunnel isn't up, or a stale one holds the port. On the laptop: `lsof -ti :8000 | xargs kill`, then `ssh -p 443 -L 8000:localhost:8000 peter@116.202.18.68`, run `serve_review.py` in that session, open `localhost:8000` on the laptop.

**Assembly killed with exit -9 / "Killed"** → that was the moviepy OOM; it's fixed (ffmpeg `assemble()`). If you somehow hit it again, confirm the ffmpeg `assemble()` is the active one (`assemble_moviepy()` is the fallback, should not be called).

**JSON parse error / "Streaming is required…" in storyboard** → the `build_storyboard` streaming patch was reverted; restore `messages.stream()` with `max_tokens=32000`.

**"No module named 'srt_generator'" / "ANTHROPIC_API_KEY not set"** → missing symlink. From the channel root: `ln -s ../.env .env` (env) or the relevant `ln -s ../shared/...`.

**Voice sounds wrong** → check `channel.json` voice_id (Victor / Reed).

**Thumbnail looks like generic AI clickbait** → the default generator is a starting point only; use the on-brand Clickly spec above. Expect two iterations (Clickly drifts to modern landmarks; push the "NOT the modern X" guard to the front).

---

# PART 6 — BANKED PRINCIPLES (one authoritative list)

Hard-won from real production failures. (v1 repeated these across appended sections; consolidated here.)

**Flux-pro silent safety-rejection.** `fal-ai/flux-pro/v1.1` silently returns black ~7KB PNGs on a safety trip — no exception, no log. `safety_tolerance: "5"` is baked in (gated to flux) and the orchestrator audits for blacks. Even at tolerance 5, **disaster/storm/water/collapse-into-water scripts** run a high silent-reject rate (Tay Bridge: ~37% of 48) — that's content trigger-density, not a config miss. Neutralize trigger stacks in Override mode: glint not sparks; empty dark water not plunge; salvage boats not divers-on-bodies; lone structure + faint light not violent storm. Known stacks that fail even at 5: `fire+survivor+wreckage`, `hand+finger+dial`, `emergency+vehicles+disaster`, `eyes+close up+person`.

**Dark-video false positive.** The `-size -200k` silent-reject filter flags legitimate night/water shots (130–200 KB). Read sizes; only ~4–10 KB is a true black. The orchestrator encodes this (halt <10 KB, FYI 10–200 KB).

**moviepy OOM → ffmpeg assembly.** moviepy `concatenate_videoclips` balloons past RAM on ~100+ clips and gets OS-killed (exit -9) even at 16 GB. Fixed by the ffmpeg `assemble()` (streaming concat). RAM upgrades don't fix this — the model was the memory shape, not the ceiling.

**Canon by visual subject, not keyword.** Narration *about* a location is not a shot *of* it. `build_canon.py` uses Claude to assign by subject; still confirm the distribution at Gate 1.

**Scene canons over character canons** (~3–5× more reliable under flux). **Face-never-resolved** for undocumented protagonists eliminates the hardest drift problem and serves the dignity register. **Object-substitution** for group compositions. **Angle-variation-within-canon** for visual variety without exploding canon count. **Per-location shot cap** (~10/scene in a 7-min video). **Fire/storm-as-environment, never as subject.**

**Shot-grammar variety.** The storyboard prompt now enforces a framing vocabulary (establishing/wide/medium/close-detail/extreme-CU/low/high-drone/from-behind), no two consecutive same-framing shots, and close framings preferring hands/objects (cooperates with face-never-resolved). Honest open question: whether this is doing real work or manual rescue would suffice — judge on variety-in-motion in finished videos.

**True-up is standard, not debug.** Every render ends with a Whisper true-up before publish.

**Measurement over prediction.** Per-shot duration comes from Whisper-measured audio, not a word-count proxy.

**TLS is correct, not bypassed.** No `verify=False` anywhere in the render/upload path. The httpx monkey-patch lives only in the review-server utilities and is gated. Never reintroduce a global bypass.

**Foreign-language pronunciation hints.** Inworld respects bracketed phonetics: `"Dei Gratia [DAY-ee GRAH-tsee-ah]"`.

**Flux text-rendering limit.** Short all-caps only (3–5 words). Thumbnails use short hooks; the full title is YouTube's title field.

**Step 0 pre-read is non-negotiable** for any narrative video (KLM Tenerife v1 lesson).

---

# PART 7 — DEFERRED IMPROVEMENTS (Phase 2 backlog)

- **Parallel/concurrent fal animation** — `finish` animates clips sequentially; bounded concurrency (semaphore ~5–10) cuts animation wall-clock ~5–8× and is free (Kling runs remote on fal; the box isn't the bottleneck). Needs per-clip content-policy fallback working concurrently. *The real speedup lever.* Design deliberately; build after more single videos.
- **Batch processing** — split the orchestrator at the stills-review seam into `prep` (unattended → stills) + `finish-batch` (unattended back half), with async review between and per-project failure isolation. Batched canon review (print all distributions, single y/n). Sequential-unattended, not truly parallel. Build after a few more single videos.
- **Synthetic Press Mode B** — separate orchestrator; Remotion explainer beats skipped at the stills gate; renderer-interface seam designed on paper first.
- Brightness-based silent-reject check (replace `-size` heuristic).
- `--words-per-shot N` flag (shot density without editing code).
- Skip-existing logic that verifies the file exists on disk before skipping (clips and stills).
- fal retry-on-error with exponential backoff.
- Centralise Claude model IDs in `shared/models.json`.
- Unify `upload.py` into `shared/` (currently duplicated per channel and drifted) — at channel 3.
- Move OAuth app out of "testing" status to stop weekly token expiry (or accept the ~5-min Path-A re-auth chore).
- `.gitignore` additions: `*.pre_*` backups, `*TEMP_MPY*`, `*_finish.log`; delete redundant `shared/assemble_ffmpeg.py`; delete the old Google Drive repo copy.

---

# PART 8 — THE STANDING AUDIT: are our principles in code or only in docs?

A principle written in a doc but not enforced in code only executes if a human remembers to apply it. Every such gap is a quality risk that depends on attention. This section is the running ledger of where each craft/production principle currently lives, so we can drive principles **from docs → into the conductor/scripts** over time. (Full audit deferred — this is the scaffold to fill in.)

| Principle | Enforced where | Gap? |
|---|---|---|
| Face/expression discipline | `audit_storyboard_discipline.py` (orchestrator phase) | In code ✓ |
| Canon assignment by visual subject | `build_canon.py` (orchestrator phase) | In code ✓ |
| `safety_tolerance: "5"` | `recreation_pipeline.py` (gated to flux) | In code ✓ |
| Silent-reject / dark-video handling | orchestrator silent-reject check | In code ✓ |
| Shot-grammar variety | storyboard prompt | In code ✓ (effectiveness unproven) |
| ffmpeg low-memory assembly | `recreation_pipeline.py assemble()` | In code ✓ |
| Whisper true-up before publish | manual (orchestrator runs it as a phase) | Partly — verify the orchestrator's true-up phase always runs |
| Pre-lock script audit (10 principles) | **human only** | **Gap** — lives in docs; applied by judgement at Step 3 |
| Hook 7-question gate | **human only** | **Gap** — docs; Step 4.5 |
| Per-location shot cap (~10/scene) | partially via Gate-1 distribution check | **Gap** — no hard cap in code |
| Object-substitution for groups | **human only** (script/canon authoring) | **Gap** |
| "NOT the modern X" period guard | **human only** (canon/prompt authoring) | **Gap** |
| Voiceover duration audit (Principle 11) | manual ffprobe | **Gap** — could be an automatic finish-time check |
| On-brand thumbnail spec | **human only** (Clickly) | **Gap** — inherently laptop-in-the-loop |

The bottom rows are where craft currently depends on attention. The deliberate next move (not now): pick the highest-leverage gaps — likely the pre-lock audit and the hook gate — and decide whether each becomes an automatic check the orchestrator runs (printing pass/fail before it lets you proceed) or stays a human judgement we accept as such. The point of this table is to make the choice explicit rather than letting principles quietly decay into "we wrote that down once."

---

## Evolution

Update this document when a failure mode is resolved, a phase or flag changes, a new channel launches, a deferred improvement ships, or a new principle is banked. Date changes at the top. The goal: future-Peter (or a future hire) could pick up the system without re-deriving it from chat threads.
