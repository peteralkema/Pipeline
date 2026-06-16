# SESSION NOTES — Mission Control: Stills-Gate Review Surface + Spend Controls + Once-Off Animate
*Sacred Dawn `figures-test-2` live test · 13 June 2026 (afternoon, continuation)*
*Sibling docs: `_YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md` (umbrella), `_SPEC-browser-pipeline-control-panel.md` (the Mission Control spec v2), `_ante-machinam.md` (craft), `_machina.md` (operations). Prior session transcripts: `2026-06-13-10-33-07-mission-control-build-session.txt`, `2026-06-13-11-27-11-mission-control-storyboard-build.txt`.*

---

## 0. One-paragraph summary

This session finished turning the Mission Control stills gate into the **actual human review surface** — not a viewer, the source of truth. The five-column beat row (text · still · still-controls · motion · clip) is live; the two proven spend endpoints (`/api/restill`, `/api/aifix`) were ported from `serve_review.py` into the coordinator **per-request** (no boot-pinned project); a new once-off clip-render endpoint (`/api/animate`) was added and then made **fire-and-poll** so a ~50s Kling call no longer drops the browser connection. A full 10-beat live run of Sacred Dawn `figures-test-2` was driven entirely from the browser: create → Launch → audio gate (Accept) → stills rendered (~$0.30) → stills gate surfaced with the five-column body → once-off directed clip rendered. **God (beat 0) rendered correctly as light-as-presence — doctrine held.** The whole create→gate→render loop is now browser-only on a fresh project. Three hard-won tool-agnostic lessons were banked (see §6). `figures-test-2` is parked at its stills gate; the real production script is deferred to a fresh session.

---

## 1. What got built (in order), with the file each lives in

All patches are idempotent `patch_*.py` under `shared/mission_control/`, applied laptop→GitHub→box, verify-anchor-before-write, back up to a `.pre_*` sidecar.

### 1a. Four-column layout (Phase 3c) — `patch_mc_layout.py`
The beat row became **text · still · motion · clip** with a Mode B strip below (where the future Remotion edit box lives). Added the editable per-beat **motion-direction textarea** (`textarea.motionbox`, persisted in-memory via `window.__MOTION_EDITS` — the future Kling-rerender seam), plus helpers `bindMotionBoxes` and `escapeHtml`.
**IMPORTANT HISTORY:** this patch was drafted in a *prior* session but the laptop step was skipped, so it never reached the box and never applied. That caused the controls patch (3d) to abort on its JS anchors. Re-presented and applied **this** session, before 3d. Lesson: a missing predecessor patch makes a downstream patch's anchors not-found — the abort is correct (all-or-nothing), the cause is upstream.

### 1b. Five-column still-controls + ported spend endpoints (Phase 3d) — `patch_mc_stills_controls.py`
The biggest patch of the session. Two things:
- **Ported `/api/restill` and `/api/aifix`** from `serve_review.py` into `pipeline_server.py`, made **per-request**: each call resolves the project from the request body (`channel`+`project`) or the active job, then loads that project's `beats_by_idx` + `canon` + `negatives` + `stills_dir` fresh (cached per-project in `_STILLS_CACHE` so 184 rapid clicks don't re-read files). The fal path + vision-diagnose flow are byte-faithful to the proven version; only project resolution changed from boot-pinned to per-request. AI Fix uses a **process-wide Anthropic client** built once from `ANTHROPIC_API_KEY` (stateless, safe to reuse).
- **Added the fifth column** = still-controls to the right of the still: Accept/Reject (in-memory judgment via `window.__JUDGED`, survives re-render), **AI Fix**, **Regenerate**, **Notes** textarea (appended as regeneration feedback), **Override** textarea (raw prompt, bypasses canon). On success the still reloads in place, cache-busted.
Five columns: **text · still · controls · motion · clip**, Mode B strip below.

### 1c. Media enlargement (Phase 3e) — `patch_mc_media_size.py`
Cosmetic. Still/clip `max-width` 480 → 1100, grid reweighted so the two media columns dominate (still/clip `2.6fr` each; text `0.7fr`, controls `0.85fr`, motion `0.7fr`), panel cap 2400px. Key insight: making media bigger is a **column-weight** problem, not just a `max-width` — the media grows because its columns grow, which is what lets it be ~2.5× without overflowing the right-half-of-monitor width. Peter works at 100–120% zoom on the right half of an ultra-wide. Result: "thats perfect!!!" Future sizing is a one-number nudge: the two `2.6fr` weights + the `1100` cap.

### 1d. Terminal-phase tracking — `patch_orchestrate_phases.py` (in `shared/orchestrate.py`)
The gates already flip `phase` (via `await_gate`'s `phase=` arg: `gate_audio`, `gate_stills`). But the **non-gate phases had no writer**, so after stills-approval the page never tracked animate/assemble and never returned to idle. This patch (job-mode-only, CLI runs untouched) imports `set_phase` and writes `assembling` at the convergence seam and `done` before run-complete. `animating` deliberately omitted — no clean seam without reading modea_leg internals; cosmetic. No service restart needed (orchestrate is spawned fresh per run).

### 1e. Storyboard body inside the live stills gate (Phase 3f) — `patch_mc_gate_body.py` + quote fixes
The stills gate was showing a bare Phase-2a panel ("rich body lands next phase") instead of the storyboard. This wired `renderRunning`'s stills-gate branch to render the **full five-column body from `state.view.beats`** (already attached by `build_state` at `gate_stills` — no re-fetch), controls live, Generate Clips / Skip above the body. Required **three** attempts because of the quote trap (see §6.1):
- `patch_mc_gate_body.py` — broke the page (JS syntax error).
- `patch_mc_gatebody_quotefix.py` — also broke (escaped doubles collapsed).
- `patch_mc_gatebody_quoteproof.py` — **worked**, using `_SQ = String.fromCharCode(39)` so no literal quote/backslash sits in the served JS.

### 1f. Launch env fix — `patch_mc_launch_env.py`
The 10-beat run crashed in the audio leg: `FileNotFoundError: 'whisper'`. The detached `subprocess.Popen(start_new_session=True)` passed **no `env=`**, so the spawned-from-service process didn't inherit the venv PATH. Fix: pass an `env` that prepends the venv bin (derived from `Path(sys.executable).parent` — correct by construction, no hardcoded home path) to PATH. Fixes whisper and every other venv/system tool the subprocess shells out to. Needs service restart (launch code is in the always-on server).

### 1g. `_stills_ctx` modea fix — `patch_mc_stills_ctx_modea.py`
`/api/animate` (and therefore restill/aifix too, on any MC project) threw `FileNotFoundError: No beats file found`. Root cause: `_stills_ctx` passed the **project root** to `find_beats_file`, which builds `<dir>/storyboard.json` — but `storyboard.json` lives under **`modea/`**. The old `serve_review.py` worked because it was launched with `--project` pointing straight at the modea dir. Fix: pass `paths["modea"]` to `find_beats_file` (storyboard is there) while keeping `paths["project"]` for `load_rulebook_negatives` (its `parent.parent` must hit the channel root for `rulebook.json`). One line; fixes all three spend buttons on MC-driven projects.

### 1h. Once-off animate endpoint (Phase 4) — `patch_mc_animate.py`
The motion-direction → Kling seam Peter wanted. `/api/animate {shot, motion_prompt, channel, project}` resolves per-request like restill, calls `animate_still(still_path, motion_prompt, out_path)` from `recreation_pipeline` (which owns `fal_client` + `FAL_KEY`), writes `clips/shot_NNN.mp4`. A **"Render this clip"** button (purple) under the motion textarea reads the textarea's current value as the prompt. Confirmed signature: `animate_still(still_path, motion_prompt, out_path)` at `recreation_pipeline.py:589`; content-policy refusal auto-falls-back to a held still inside that function.

### 1i. Animate fire-and-poll — `patch_mc_animate_async.py`
The sync `/api/animate` held the HTTP connection ~51s (one Kling call). Box `curl` tolerated it (returned `{"ok": true}` in 50.9s); the **browser timed out → "Failed to fetch."** Fix: same pattern as the gates / detached orchestrate — start the work, return immediately, poll for completion. `/api/animate` now spawns a daemon thread (`_run_animate_bg`) and returns `{ok, started}` instantly; status lives in a module dict `_ANIMATE_JOBS` keyed `channel/project/shot` (NOT the job record — so it works with no active job, e.g. browsing a finished project); new `GET /api/animate_status` reports it; the button fires then `setInterval`-polls every 3s, reloads the clip in place on `done`. Survives browser timeouts, network blips, and closing/reopening the page (the thread keeps working server-side). **Tested working.**

---

## 2. The 10-beat live test — what was proven

Project: `sacred-dawn/projects/figures-test-2` (10 beats, biblical figures, created via the front door in a prior session). Live run, browser-driven:

1. **Launch** (live) → orchestrate spawned detached, `--gate-mode job --job-id`.
2. Audio leg: narration assembled (303 words), Inworld Victor voiceover (1.9 MB), **whisper measured** (this is the slow step — 3–5 min, NOT stuck), durations.json built (10/10 beats, 121s ≈ 2.0 min), continuity clean.
3. **Audio gate surfaced in the browser** (`phase: gate_audio`) → clicked **Accept** (free, audio already made). First time the audio gate fired through the page for real.
4. Stills leg: engine translation → `engine_beats.json` + `_index.json`, then **10 stills rendered on fal (~$0.30, the only pre-decision spend)**, count climbing 2 → 10.
5. **Stills gate surfaced**, page flipped to the **five-column storyboard body** with the 10 fresh stills + live controls (after the gate-body patch).
6. **Once-off directed clip**: typed motion direction on a beat, clicked Render this clip → `animate_still` ran Kling → real 5.47 MB clip landed (not the held-still fallback). Async version polled cleanly to completion in-browser.

**God (beat 0) rendered correctly as light-as-presence** — a shaft of golden-white radiance over the dark primordial deep, no figure, no face. The hardest beat to keep on-doctrine, and Flux respected the "light not a figure" prompt. Milestone moment for the channel.

**Run survived a service restart while parked at a gate** (restarting Mission Control to apply a patch did NOT kill the detached orchestrate — it stayed `waiting`, no respend). The detached-subprocess resilience claim is proven in practice.

**Zero wasted fal spend across all the crashes** — every failure (whisper PATH, the quote breaks, the `_stills_ctx` path bug) happened either in the audio leg (pre-stills) or in the page layer, never after stills spend.

---

## 3. Confirmed machinery (ground truth, do not re-derive)

- `animate_still(still_path: Path, motion_prompt: str, out_path: Path) -> Path` at `recreation_pipeline.py:589`. Uploads still to fal, calls Kling (`VIDEO_ENDPOINT = "fal-ai/kling-video/o3/standard/image-to-video"`), `duration=SHOT_DURATION`, `generate_audio=False`. Content-policy refusal → `_still_to_held_clip` fallback (any other error raises). `recreation_pipeline` owns `fal_client` + `FAL_KEY`.
- **Batch skip-existing**: `recreation_pipeline.py:1319` `if clip.exists() and not args.force: skip`. So a page-rendered once-off clip **survives the batch** (non-`--force` run). `--force` re-animates everything.
- `/api/restill` contract: `{shot:int, note:str, override:str}`. `shot` = **engine shot number** (storyboard 1-based index). `note` → appended as `REGENERATION FEEDBACK`. `override` → raw prompt, bypasses canon + negatives. NORMAL vs OVERRIDE mode.
- `/api/aifix` contract: `{shot:int}`. Vision diagnose (`claude-sonnet-4-6`) → if verdict "fix", regenerate with the corrected prompt through the same fal path; if "fine", report and regenerate nothing.
- `serve_review.py` keys `beats_by_idx = {b["index"]: b for b in beats_data}` by **engine shot number**, and reads `beat["image_prompt"]` (storyboard shape, 1-based `index`) — distinct from `beats_full.json` (0-based `index`, `visual`). `build_beats_view` exposes the engine shot as `assets.still.engine_shot`, so the controls wire `shot: engine_shot` and the keys line up.
- `find_beats_file(project_dir, beats_arg)`: builds `channel_root/beat-scripts/<name>_beats.json` and `project_dir/storyboard.json`. For MC projects the storyboard is at **`<project>/modea/storyboard.json`**, so `_stills_ctx` must pass the **modea** dir.
- `load_rulebook_negatives(project_dir)`: `channel_root = project_dir.parent.parent`, reads `channel_root/rulebook.json` + `pipeline_root/shared/rulebook.json`. Needs the **project root** (so `parent.parent` = channel root).
- `await_gate(..., phase=...)` **does** set phase (gate_protocol.py ~135). `set_phase(job_id, phase, repo_root)` exists. `init_job` starts phase `"running"`.
- `figures-test-2` artifacts: `_index.json`, `beats.json`, `beats_full.json`, `durations.json`, `engine_beats.json`, `ep_audio.manifest.json`, `voiceover.json` at project root; `modea/storyboard.json`, `modea/stills/`, `modea/script.txt`, `modea/clips/`.
- `.env` (loaded by `mission-control.service` via `EnvironmentFile=/home/peter/Pipeline/.env`) has `ANTHROPIC_API_KEY`, `FAL_KEY`, `INWORLD_API_KEY`, `JAMENDO_CLIENT_ID`, `PEXELS_API_KEY`, `YOUTUBE_CLIENT_ID_A/SECRET_A`, `YOUTUBE_CLIENT_ID_B/SECRET_B`.

---

## 4. The daily flow (as it now exists, browser-only)

1. Paste finished script in chat → Claude verifies machine invariants (numbers spelled out, every Mode A beat has a VISUAL, no wordless beats, header `channel:` matches folder, ~55-word ceiling).
2. Front-door **Create** (one paste) → project appears newest-first in the dropdown.
3. Pick channel → project → **Live** → **Launch**.
4. **Audio gate**: Accept (keep) or Swap (record your own → re-whisper + rebuild durations, timing carries through, no fal respend).
5. **Stills gate** = the five-column storyboard body. Review the stills; on any spell-breaker use **AI Fix** (vision diagnose+correct), **Regenerate** (Notes feedback), or **Override** (raw prompt). Optionally direct + render specific clips early via **Render this clip** (survives the later batch).
6. **Generate Clips** (the "go" decision) → batch animate (server-side, detached, no browser timeout) → assemble → `done`.
7. Post-batch: re-render any clip via the once-off button; the restill→motion→re-clip chain composes (each leg reads the prior leg's file off disk).
8. Assembly takes **exactly the on-disk stills/clips** (what the page shows), each held to its beat's `durations.json` duration, joined through `_index.json`. The page IS the visual source of truth — *as long as the voiceover hasn't changed since whisper measured it.* (Swap audio without re-whispering = stale timings; the only way to desync page from cut.)

---

## 5. Service / ops cheatsheet

- URL: `http://116.202.18.68:8002/?key=fh2026` (review.service on :8001 left untouched throughout).
- Restart after a code change: `systemctl --user restart mission-control.service` (loads `.env`).
- **STANDARD GUARD — node-check the served page before every refresh after a JS change:**
  ```
  curl -s "http://127.0.0.1:8002/?key=fh2026" | python3 -c "import sys,re; m=re.search(r'<script>(.*?)</script>', sys.stdin.read(), re.S); open('/tmp/mc.js','w').write(m.group(1))" && node --check /tmp/mc.js && echo "PAGE JS VALID"
  ```
- Diagnose a "stuck"/"working" page: `cat $(ls -t .mc_jobs/*.json | head -1)` (phase/gate) + `tail $(ls -t .mc_jobs/*.log | head -1)` (what orchestrate is doing) + `ps aux | grep [o]rchestrate.py` (alive?).
- Clear a dead/frozen job so the page returns to idle: `rm .mc_jobs/<job_id>.json .mc_jobs/<job_id>.log`.
- Test a spend endpoint without the browser (bypasses client timeout): direct `curl -X POST .../api/animate -H "X-Review-Key: fh2026" ...`.

---

## 6. Tool-agnostic lessons banked (the actual moat)

### 6.1 Never put literal quotes or backslashes in JS served from a Python triple-quoted string
`render_page` returns a `"""..."""` string. Inside it, `\"` and `\'` are escape sequences Python resolves **at import** — the backslash is gone by serve-time, so escaped quotes collapse and collide, breaking the whole `<script>` (page hangs on "loading…"). Two fixes failed this way (`patch_mc_gatebody_quotefix` tried escaped doubles; they collapsed). The robust fix: build quote characters with `String.fromCharCode(39)` (single) / `(34)` (double) so **no literal quote or backslash sits in the JS string** — nothing for Python to eat, nothing to mis-nest. Same family as the earlier `\n`-escaping trap from the ingest-panel session.

### 6.2 Always `node --check` the served page before refreshing
The single command in §5 catches exactly the §6.1 class of break before it ever reaches the browser. Make it reflex after any page-JS change. Better still, round-trip new JS through a triple-quoted Python string and `node --check` it *before shipping the patch* (done for `patch_mc_animate.py` and `patch_mc_animate_async.py` this session — both passed pre-flight).

### 6.3 The page speaks HUMAN, the wire speaks CLI — they meet only in the handler
Peter's own diagnosis of the niggles. Button labels read "Accept (keep this read)" / "Generate Clips"; the wire values are `keep` / `go`. Keeping the CLI tokens (`go`/`keep`/`swap`/`skip`) OUT of the rendered HTML (a) avoids the §6.1 quote breaks entirely and (b) makes the page read like a product, not a terminal. Several remaining gate buttons still leak CLI verbs — convert them next session.

### 6.4 Detached subprocesses don't inherit the interactive-shell PATH
Pass an explicit `env` with the venv bin (derive from `sys.executable`, never hardcode) to any `Popen(start_new_session=True)`. (§1f.)

### 6.5 Long synchronous HTTP = fragile; use fire-and-poll for slow spend ops
A ~50s held connection works under `curl` but the browser drops it. Start the work in a thread, return immediately, poll for completion — the same resilience pattern as the gates and the detached orchestrate. Applies to animate now, and to any future slow op (batch-animate-from-page later). (§1i.)

### 6.6 Patches abort all-or-nothing on a fatal — and a missing predecessor causes downstream anchor-not-found
The controls patch (3d) aborted cleanly because the layout patch (3c) had never been applied (its laptop step was skipped a session earlier, so 3c never reached the box). Fix = sequence the predecessor first. The abort wrote nothing (confirmed by `grep -c`), so state stayed clean. The lesson: when a patch reports ANCHOR NOT FOUND, suspect a skipped predecessor before re-anchoring.

---

## 7. Pending / next session

### 🔴 ACTION FIRST — the unifying refactor that fixes A1+A2+A3 at the root

**A0 — ONE CONTINUOUS PAGE (do this first; it dissolves A1, A2, A3).**
*Peter's own diagnosis (end of session, and it's correct):* "why do we go to a different page for the working mode? surely we can just have this on the same main page."
*What's actually happening:* it is NOT a different page — but `poll()` hard-swaps the entire `app.innerHTML` between two render functions, `renderIdle()` and `renderRunning()`. When a run is active it throws away the idle view (dropdowns, Create panel) and replaces it wholesale. So it READS as a page swap. Worse, `renderRunning` only handles two states well — "waiting at a gate" and an `else` catch-all that prints "— working…". So `running`, `done`, AND dead-run all collapse into the same "— working…" spinner. That single `else` branch is the root cause of A1 (dead run looks like working), A2's confusion, and A3 (done looks like working).
*The right architecture (what the spec actually called for — the timeline-document model):* the page is ALWAYS the same persistent scroll. Run status is a **strip/banner at the top** that changes with phase; the storyboard body below is always whatever project is selected. Idle is not a different layout — it's the same page with the strip saying "idle · pick a project to launch." Running is the same page, strip says "running · audio leg," body shows beats populating. Gate states show their controls inline. Done shows "✓ complete · new run." Dead/stale shows "this run ended · clear."
*The fix (spec):* replace the `renderIdle` / `renderRunning` whole-view swap with **one render that always draws the same shell** (status strip + persistent body), and a small explicit branch per run-state: `idle | running | gate | done | stale/error`. Each state only changes the STRIP and which controls are live — never throws away the page. This is a meaty but high-value refactor; doing it makes A1/A2/A3 fall out for free instead of three separate patches.
*Build A0 first.* If A0 is deferred, A1/A2/A3 below are the individual patches.

---

### 🔴 then — three non-gate-state bugs (subsumed by A0, or patch individually)

All three are the same family: **the page doesn't cleanly handle a run that isn't actively mid-gate.** A1/A2 surfaced when "Skip" at the stills gate did nothing; A3 on the war-in-heaven dry run.

**A1 — DEAD-RUN / FROZEN-GATE (highest priority).**
*Symptom:* the page showed a live `gate_stills / waiting` gate, but clicking Skip OR Generate Clips did nothing.
*Root cause:* the orchestrate process had **died** (no `orchestrate.py` in `ps`), almost certainly killed by a `systemctl restart` mid-run while iterating on patches — the run was still in stills generation (the job log ends at `… still working (engine stills, 1:00)`, never reached the gate banner). But the job record stayed frozen at `phase: gate_stills, status: waiting, decision: null`. So the page faithfully renders a gate for a run that no longer exists; any decision written to that record is read by nobody.
*Why it matters:* this is the "crashed run should write `phase: error`" item, now upgraded from cosmetic to **needed** — a dead run silently presents an un-actionable gate, which reads as "the button is broken." It will happen again any time a run dies (restart, crash, OOM).
*The fix (spec):*
 - `build_state` (and/or a periodic reaper) must detect that the run's process is **not alive** and the job is not at a legitimately-decided terminal state. Mechanism: store the orchestrate **PID** in the job record at `init_job`/launch time (or write a heartbeat timestamp the leg updates), then in `build_state` check `os.kill(pid, 0)` (or staleness of the heartbeat). If the job claims `waiting`/`running` but the PID is gone → surface `phase: "stale"` (or `"error"`) with a **"Clear this run"** button instead of a live gate.
 - Care needed: PID reuse — a bare `os.kill(pid,0)` can match an unrelated recycled PID. Safer: also check the process is actually `orchestrate.py` for this job (e.g. match cmdline) OR use a heartbeat-timestamp staleness window (e.g. no update in >N min while not at a gate → stale). Heartbeat is probably the cleaner choice; decide next session.
 - Immediate manual unblock (used this session): `rm .mc_jobs/<job_id>.json .mc_jobs/<job_id>.log` then refresh → page returns to idle.

**A2 — `skip` / Stop at the stills gate does not actually stop (real, separate from A1).**
*Root cause:* `modea_leg` captures `decision = await_gate(...)`, prints `"Mode A gate cleared ({decision})"`, then `return True` **regardless of the decision** — there is NO branch on `go` vs `skip`. So even with a live run, Skip would proceed identically to Generate Clips. Nothing reads the decision.
*The fix (spec):*
 - `modea_leg` must **branch on `decision`**. On `skip`/stop → return a sentinel that tells orchestrate to **end the run cleanly WITHOUT convergence**, leaving stills on disk; set phase → `done` (or a new `stopped`). On `go` → proceed to animate as now.
 - **Order matters:** confirm the gate decision is read **before** the animate-only (Kling) step so Stop actually prevents clip spend. (This session we couldn't fully confirm the animate-vs-gate ordering — verify it in `modea_leg` / `run_modea_leg` first; the leg's full body past the gate was not read.)
 - **OPEN DESIGN QUESTION for Peter (asked end of session, unanswered):** after Stop, should the run be **resumable** (come back later, approve stills, generate clips from the on-disk stills) or a **full abandon** (relaunch from scratch)? This choice decides whether the leg must checkpoint or just exit. Resumable is more useful but needs a "resume from stills" entry path; abandon is simpler. **Decide this before building A2.**
 - **Relabel the button:** "Skip" → **"Stop here (keep stills, no clips)"**. "Skip" reads ambiguously (sounds like "skip review, proceed"); the intent is "back out without spending on clips." Part of the §6.3 human/wire split.

**A3 — `done` does not return the page to idle (found on the war-in-heaven dry run).**
*Symptom:* after a run completes, the page shows `phase: done — working…` (contradictory) and never returns to the idle dropdown; looks stuck.
*Root cause:* `renderRunning` only suppresses the "— working…" spinner when there's a `waiting` gate. At `phase: done` with `gate: None` it falls through to the catch-all working label. There is no `done → idle` branch in `poll()`/`renderRunning`. A **dry run** hits this every time (dry mode reaches `done` with no gates).
*The fix (spec):* in `poll()`, when `phase === "done"` (and not a batch awaiting manual cut), either drop back to `renderIdle(state)` or show a brief "✓ run complete" with a **"New run"** button. Trivial page-state addition. Manual unblock meanwhile: `rm .mc_jobs/<job_id>.json .mc_jobs/<job_id>.log` then refresh.
*Family note:* A1 (dead run), A2 (skip ignored), and A3 (done not handled) are all the same class — **the page doesn't cleanly handle a run that isn't actively mid-gate.** Worth fixing together as a "non-gate run states" pass: `idle | running | gate | done | stale/error`, each with an explicit render branch.

### 🟢 NEW FEATURE — TIERED RENDER: Ken Burns floor + Kling front-loading (designed this session, ready to build)

**The economic driver:** clip rendering (Kling) is the dominant variable cost, and most of it is spent on the back two-thirds of videos that viewers never reach. The fix: render the **front N beats with Kling** (real motion, where attention lives) and the **rest with a free ffmpeg Ken Burns slow-zoom**. As a channel monetises, raise N and put the money back into proper rendering. Cost scales WITH the channel instead of being a flat upfront bet.

**Confirmed pricing (web-checked this session, June 2026):** the pipeline's endpoint `fal-ai/kling-video/o3/standard/image-to-video` with `generate_audio=False` = **$0.084/second**. Kling renders a fixed ~5s clip then stretches/slows it to fill the beat → **cost is ~$0.42 PER CLIP, fixed, regardless of beat length** (you only ever generate 5s). Stills (Flux-pro) ~$0.03 each. TTS/Whisper/ffmpeg/assembly run on the box ≈ free.

**The cost ladder (all-in per video):**
| Budget | Kling clips (front) | ≈ Kling spend | ≈ front coverage of a 14-min video |
|---|---|---|---|
| ~$10 all-in | ~19 clips | ~$8 | front ~10% (~1.5 min) |
| **~$20 all-in (DEFAULT)** | **40 clips** | **~$16.80** | **front ~third (~4.5–5 min)** |
| full Kling (87-beat) | 87 clips | ~$36 | 100% |
(Front-coverage minutes exceed the raw Kling-seconds because each ~5s Kling clip stretches to fill its real beat length, ~5–9s.)

**THE LOCKED DESIGN (all settled with Peter this session):**

1. **Ken Burns is a clip PRODUCER, not an assembly mode.** It writes the exact same artifact Kling writes: `clips/shot_NNN.mp4`, 16:9, same filename/folder. ffmpeg `zoompan`, **slow zoom-in always** (one default, zero per-beat decisions). **Rendered to the beat's EXACT duration** (from `durations.json` — the same source assembly uses), NOT a fixed clip that gets stretched. (This differs from Kling, which renders fixed-5s-then-stretches; Ken Burns renders-to-length natively, so no slow-mo artifact.) **Assembly is UNCHANGED** — it still globs the clips folder, holds each clip to its beat duration, joins via `_index.json`. It cannot tell Kling from Ken Burns and doesn't need to. *Craft note:* `zoompan` judders if you zoom the source directly — upscale the still first, then zoom, for smoothness.

2. **The policy is a pure function of BEAT INDEX (timeline position), never folder/render order:**
   `render(beat) = "kling" if beat.index < N else "kenburns"`.
   Always positional from the front (viewers always start at the front and drop off; the Kling→Ken-Burns texture change may itself trigger a drop-off — acceptable, and argues for landing the seam at a natural section boundary where attention was already resetting).

3. **N = global default 40.** Override is **per-project, entered at the STILLS GATE** — a number field that **shows the default 40 pre-filled for Peter to override** before clicking Generate Clips. `0` = pure Ken Burns (near-free), `87` = full Kling.

4. **Mechanism = per-beat `render` flag** the animate leg routes on (Kling beat → `animate_still`; Ken Burns beat → new `ken_burns_still(still, out, duration)`). The `kling_count: N` policy stamps the flag on each beat (index < N) before the animate leg runs. Per-beat is the mechanism; one number is the policy.

5. **Both the batch AND the once-off "Render this clip" button consult the same policy.** The button is identical everywhere (in-progress or finished project) — one gesture, "render this beat now"; the routing (Kling vs Ken Burns) is automatic from `beat.index < N`. The button never needs to know which engine it's calling. Project resolved per-request (like restill/animate already do). The page needs to **carry the per-project N** so both the gate and the button know where the line sits.

6. **Changing N affects only NEW renders** (skip-existing leaves clips on disk). Raising N from 40→60 does NOT auto-re-render beats 40–59 as Kling — you deliberately re-render those beats (force, or the once-off button) to upgrade them. This is CORRECT (prevents accidental $-spend from typing a bigger number) and is exactly the monetisation lever: channel earns → raise N → deliberately re-render the gap to Kling.

7. **Per-beat override** (force a specific back-half money-shot to Kling regardless of N) — **banked as the obvious next layer**, NOT v1. The per-beat mechanism (#4) already supports it; v1 is just the positional-N policy.

**Build order when we do it:** (a) `ken_burns_still()` ffmpeg producer + prove a still→duration-correct mp4 in isolation; (b) the `render`-flag mechanism + `kling_count` policy stamping in the animate leg, routing each beat; (c) the N field at the stills gate (default 40, overridable); (d) confirm the once-off button consults the policy. Assembly needs ZERO changes — that's the proof the design is right.

---

**A4 — STILLS-GATE BUTTONS DON'T WRITE THE DECISION (confirmed live on war-in-heaven — this is the one that actually blocks you).**
*Symptom:* clicking **Generate Clips (approve stills)** did nothing. Diagnosis showed the run was perfectly healthy — alive (PID), parked at `gate_stills / waiting`, all 87 stills on disk, process idle (0% CPU, sleeping) — but `gate.decision` stayed `None`. The click never wrote through to the job record, so `await_gate` (polling the record) never woke. Same family as A2's broken Skip button: **the stills-gate decision buttons' POST → `/api/gate/stills` → `decide_gate` write is not landing.**
*Distinguish from A0/A3:* A0/A3 are the *display* ("working…" label); A4 is the *button failing to act*. A4 is higher impact — it stranded a healthy run with $36 of stills waiting.
*Manual workaround (used live, WORKS):* write the decision straight into the job record on the box —
```
python3 - <<'PY'
import json, glob, os
f = sorted(glob.glob(".mc_jobs/<job-glob>*.json"), key=os.path.getmtime)[-1]
d = json.load(open(f)); g = d.get("gate") or {}
assert g.get("name") == "stills" and g.get("status") == "waiting"
g["decision"] = "go"; d["gate"] = g; json.dump(d, open(f,"w"), indent=2)
PY
```
`await_gate` picks it up within ~1.5s and the run proceeds to animate. (Set `"go"` to approve, or the stop value once A2 is built.)
*The fix (spec):* debug why the gate-button POST doesn't write. Likely candidates: (1) the button's `gate(...)` handler isn't sending to `/api/gate/stills` correctly (check the served handler — it goes through the same quote-built path as the broken buttons); (2) `decide_gate` rejects silently (it returns `{ok:false}` JSON the page ignores — check it accepts `go`/`skip` for the stills gate and that `active_job_id()` resolves the right job); (3) the POST fires but to the wrong job/gate name. Add a visible success/error toast on the gate buttons so a failed write isn't silent. **This + A2 + the audio gate's Accept (which DID work) should all share one verified gate-decision path.** Note: the audio gate's Accept worked this session, so the path isn't universally broken — compare the stills-gate button wiring against the working audio-gate button to find the divergence.



3. **Motion-direction text doesn't persist** across re-render — the `window.__MOTION_EDITS` in-memory map isn't wired to a save endpoint, and a poll re-render rebuilds the row, wiping typed motion direction. Cosmetic but noticed in testing. Fix: persist motion edits server-side (a small `/api/motion` save, or fold into the job/view) so the textarea repopulates from saved state on render. **First cosmetic task.**
4. **Gate-button human/wire split** (§6.3) — convert the remaining `go`/`keep`/`swap`/`skip` onclick verbs to human labels + wire values. (A2's relabel is part of this.)
5. **`voice_id` cosmetic** — audio gate shows "the channel voice" instead of "Elliot"; `ctx["voice_id"]` is set `None` at init and never filled. Known, cosmetic.
6. **`figures-test-2` was never finished** — its run died at/after stills (see A1); the clips dir has 2 files (once-off `shot_001` + one other). Superseded by the war-in-heaven live run below.
7. **`war-in-heaven` — the REAL production script — was launched LIVE at the very end of this session and was still IN FLIGHT when the session ended.** Key facts to resume from:
   - **87 beats, 2153 words of narration.** This is a full-length video, not a test. Dry run completed clean (`phase: done`, no halt) — script is structurally sound.
   - When last observed: orchestrate alive (PID 43232), mid **audio leg** generating the Victor voiceover (~1:15 in). Audio leg will be LONG — ~14 min of audio means a long whisper-measure step. Let it run; **do NOT restart the service** (that is the A1 killer).
   - **Stills spend at the gate ≈ 87 × $0.03 ≈ $2.60** (vs $0.30 for the 10-beat test). Review at the stills gate before Generate Clips — spot-check the doctrine-sensitive beats (God/figure/creature/rider beats) rather than all 87 (the scroll is long).
   - **⚠ THE BATCH BACK-HALF IS UNPROVEN.** Once-off animate works; the batch path (Generate Clips → animate all 87 via Kling → assemble → final_video) has NEVER completed end-to-end. 87 Kling calls is a long real run. **This live run is the first real test of the back half** — if there's a bug there, it surfaces AFTER the stills spend. Watch the stretch after Generate Clips closely.
   - **Resume check when back:** `ps aux | grep [o]rchestrate` + `tail .mc_jobs/sacred_dawn__war-in-heaven__*.log` to see where it got to. If alive and parked at a gate → action it. If dead/frozen (A1) → diagnose why it died before relaunching (and note: 87-beat stills cost real money, don't blindly re-spend).
8. **The daily flow** (idle): Paste → verify invariants → Create → Launch → review → Generate Clips → done. **Start from a clean idle page** (clear any stale/done job first: `rm .mc_jobs/<job_id>.json .mc_jobs/<job_id>.log`).

---

## 8. The state in one line

The render core was always solid; this session made the **stills gate the real review surface** — five columns, live AI-Fix/Regenerate/Override on the still, once-off directed clip render on the motion column, all browser-only, all proven on a fresh project, with God rendered correctly as light. **Top priority next session is A0: refactor the page from a whole-view swap (`renderIdle`/`renderRunning`) into one continuous page with a status strip — this dissolves A1 (dead run shows a frozen gate), A2 (Skip doesn't stop), and A3 (done shows "working…") at the root, since all three are the same bug: the page only handles active-gate states, not `running`/`done`/dead.** The real production script `war-in-heaven` (87 beats) was launched LIVE and was still in flight (audio leg) at session end — its batch back-half is the first real end-to-end test. Once-off animate is proven; batch-animate + assembly via the page is NOT. Start next session by checking where war-in-heaven got to (§7.7).

*Maintained by Peter + Claude.*

---

## 9. Designed-this-session, ready-to-build (the headline for next time)

Beyond the A0/A1/A2/A3 page-state fixes, the big NEW feature designed (not yet built) is **TIERED RENDER** (§7, green section): Ken Burns slow-zoom as the free clip floor, Kling front-loaded on the first N=40 beats (≈$20 all-in, front ~third), N overridable per-project at the stills gate, both batch and the once-off button routing automatically by beat index. Assembly unchanged by design. This is the cost lever that lets a new channel ship near-free and scale Kling spend up as it monetises — directly serving the flywheel thesis that the production *system* is the moat. Cost ladder and full spec are in §7.

**Suggested next-session order:** (1) check where the live `war-in-heaven` run got to (§7.7) and get one real video out the door; (2) A0 single-page refactor (dissolves A1/A2/A3); (3) build TIERED RENDER (the cost lever). 1 proves the pipeline end-to-end on real content; 2 makes the surface trustworthy; 3 makes it economically sustainable at cadence.
