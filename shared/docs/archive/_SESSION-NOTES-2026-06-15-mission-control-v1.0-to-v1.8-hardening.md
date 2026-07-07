# SESSION NOTES — 15 June 2026: Mission Control v1.0 → v1.8 (seam fix, re-assemble + drift fix, panel persistence, reliability hardening), assemble path fix, doc consolidation

_YouTube Media Flywheel · solo operator · all edits LAPTOP → GitHub → box · never hand-edit on box._
_The big session. Mission Control went **v0.9 → v1.8** across nine shipped patches. Doc set consolidated to two living docs. One live production run (70smusic) survived a stranded-run crisis and drove the reliability hardening._

---

## TL;DR (what shipped, in order)

1. **v1.0 — audio→stills seam fix + decided-gate stale guard.** A healthy stills run was false-flagging as "stale / ended unexpectedly" (caught live on Esther).
2. **v1.1 — Re-assemble button.** Re-stitch the final video from current clips so the per-clip re-render controls finally mean something.
3. **v1.2 (backend) — assemble-only path fix**, then **v1.2 (page) — Re-assemble routed through the ALIGNED assembler.** The second is the important one: it fixed real **drift** in re-assembled video by using `assemble_episode.py` + `_index.json` instead of the index-unaware `assemble()`.
4. **v1.3 / v1.4 / v1.5 — FINAL VIDEO panel persistence** across three layers: show on select; fix the `api()` key-on-querystring bug that 403'd `/api/meta`; stop the poll wiping the panel.
5. **v1.6 / v1.7 / v1.8 — reliability hardening trio (A/B/C):** page locks onto the freshest LIVE run; launch refuses duplicates; dead-process records get reaped. "Close/refresh/restart → always correct state, no duplicates."
6. **Doc consolidation** to two living docs (canonical = system, ante-machinam v3.0 = craft); machina + README to stubs.
7. **Live ops:** recovered a stranded 70smusic run (orphan + duplicate records) by hand; that crisis is exactly what the A/B/C trio now prevents.

---

## PART 1 — The patches (each LAPTOP → push → box → restart → version-check → node-check)

### v1.0 — `patch_audio_stills_seam.py` (orchestrate.py + pipeline_server.py)
- **Bug (live on esther--1):** after the audio gate was accepted, orchestrate ran the stills leg with no phase write between, so the record stayed `phase: gate_audio` through stills. Two consequences: the status line couldn't count stills (its branch needs `running`/`gate_stills`); and `gate_audio` is a stale-checked gate phase whose heartbeat froze at the moment "keep" was clicked → after `STALE_SECONDS` the page false-flagged the healthy run as "ended unexpectedly."
- **Fix 1 (orchestrate):** `set_phase(_job_id, "running", ctx["repo_root"])` immediately before `run_modea_leg`, job-mode guarded — record leaves `gate_audio`, strip counts, no longer a gate phase.
- **Fix 2 (build_state):** stale-check only fires when the gate is still `waiting` — a `decided` gate means the run moved on and can never false-stale.
- Sentinel: `audio->stills seam`.

### v1.1 — `patch_reassemble_button.py` (pipeline_server.py)
- The launched run auto-assembles right after clips, making the per-clip re-render controls moot. Added a **Re-assemble** button next to Download. `_run_assemble_bg` background thread (mirrors `_run_animate_bg`); `/api/assemble` POST + `/api/assemble_status` GET; on done, cache-busts the `<video>`.
- Sentinel: `def _run_assemble_bg`. (Initially shelled `finish --assemble-only` — superseded by v1.2; see below.)

### v1.2 (backend) — `patch_assemble_only_paths.py` (recreation_pipeline.py)
- Re-assemble surfaced a pre-existing bug: assemble-only resolved voiceover/final/music from `p["root"]` = `<slug>/modea` (one level too deep) — they live at the **project root**. Fixed to read from `p["root"].parent`. Clips stay under modea (correct).
- Banked the **root-vs-modea artifact-location principle** (see Part 3). Sentinel: `assemble-only: root-level artifacts`.

### v1.2 (page) — `patch_reassemble_aligned.py` (pipeline_server.py) — THE DRIFT FIX
- **Bug (found after re-rendering clips with new motion, then Re-assembling): drift between clips and narration.** Root cause: **there are two assemblers and only one honors the beat→shot map.**
  - `assemble_episode.py` (what the launched convergence run uses): iterates BEATS, uses `_index.json` (`rev_map`) to place each beat's clip, holds each to the FROZEN `durations.json`. **Alignment-correct.**
  - `recreation_pipeline.assemble()` (what `finish --assemble-only` calls): pairs clip_paths to durations POSITIONALLY via `zip()`, ignores `_index.json`, and re-derives durations LIVE from `storyboard.json` (re-running Whisper auto-align each call). **Drifts** when shot-order ≠ beat-order or the live re-align shifts targets.
  - The v1.1 button shelled `finish --assemble-only` → the wrong assembler → drift. The motion re-render tripped the live Whisper re-align, shifting positional durations.
- **Fix:** `_run_assemble_bg` now re-pools `modea/clips/` → `<project>/clips/` (so re-rendered clips reach assembly), then shells `assemble_episode.py` with the exact convergence flagset (`--durations --index --voiceover --project --clips --out --no-music`). One assembler now; the two paths can't diverge. (`shutil` imported locally in the bg runner — the module doesn't import it at top.)
- Sentinel: `assemble_episode.py`.

### v1.3 — `patch_panel_on_select.py` (pipeline_server.py)
- After Reset → pick a finished project, the FINAL VIDEO panel didn't show (it only rendered at live `phase==done`). Added `renderDonePanel(chan.value, proj.value)` to `proj.onchange`. `renderDonePanel` already checks `has_video` internally, so finished → video, unfinished → placeholder.
- Sentinel: `panel on select`.

### v1.4 — `patch_api_key_querystring.py` (pipeline_server.py) — the sneaky one
- v1.3 didn't work because `/api/meta` returned **`403 - bad key`**. Root cause in `api()`:
  `fetch(path + (path.includes("?") ? "" : ("?key="+KEY)))` — it appended the key ONLY when the path had no existing `?`, and **nothing** when params were present. So every keyed GET carrying query params (`/api/meta?channel=...`, `/api/render_policy?...`, `/api/assemble_status?...`, `/api/projects?channel=...`) went out with **no key** → 403.
- **Fix:** always append the key with the right separator — `(path.includes("?") ? "&" : "?") + "key=" + KEY`. Unkeyed (local) unchanged. This fixed more than the panel — every param-carrying keyed GET was affected.
- Sentinel: `key always appended`.

### v1.5 — `patch_panel_poll_persist.py` (pipeline_server.py)
- Panel showed on select then **vanished ~2.5s later** — the poll (`maybeUpdateBody`) had `if (phase === "done") renderDonePanel() else removeDonePanel()`, so for a selected-but-idle finished project (phase not "done") every poll wiped the panel selection had drawn. Replaced with an unconditional `renderDonePanel(t.ch, t.pr)` (artifact-aware: shows video iff has_video, else placeholder). Base-state (no selection) still clears.
- Sentinel: `panel persists across polls`.
- _Lesson: a render target with multiple writers (select + poll + done-event) needs all writers to agree on the same source of truth — here, "does a video exist," not "is a job done."_

### v1.6 — `patch_active_job_freshest.py` (pipeline_server.py) — Hardening A
- **Bug (the stranded run):** `active_job_id()` did `sorted(glob("*.json"), key=mtime, reverse=True)[0]` — returned the most-recently-TOUCHED file regardless of phase. With several records for one project (a closed-laptop orphan + duplicate Launch clicks), it picked a `done` ghost over the live `running` job → page showed stuck/wrong while the real run worked underneath.
- **Fix:** read each record, sort by `started_at` (content, not mtime — a touched `done` must not re-float), return the newest NON-terminal record (the live run); fall back to newest overall only if none are live. Added `_TERMINAL_PHASES = ("done","stopped","error","stale")`.
- Proven against the exact failure: even when a `done` record had the newest mtime, it returns the running job. **This alone would have prevented the stranded-run confusion.**
- Sentinel: `freshest live run`.

### v1.7 — `patch_launch_idempotent.py` (pipeline_server.py) — Hardening B
- **Bug:** the Launch button disables on click, but the POLL re-enabled it (`launch.disabled = run || ...`); before A, the poll saw "not running" (the `active_job_id` bug), re-enabled the button, a second click spawned a SECOND orchestrate (job_id is `int(time.time())`, so two launches a second apart get distinct ids — nothing stopped a duplicate).
- **Fix (server, the robust one):** `launch_job` consults `active_job_id()`; if a live (non-terminal) run exists, it **refuses** — returns `{"ok": False, "already_running", "phase", "error"}` and does NOT spawn. `/api/launch` returns **409** on refusal. **One live run total (global)** — matches one-video-at-a-time, prevents two whisper/fal processes thrashing the box. **dry-run is exempt** (no spawn, no spend). Page shows the refusal message instead of silently re-arming.
- Blocks duplicates from fast clicks, reloads, AND two tabs.
- Sentinel: `refuse if a run is already live`.

### v1.8 — `patch_pid_reaping.py` (gate_protocol.py + pipeline_server.py) — Hardening C
- **Gap:** A1's heartbeat-stale check fires on GATE phases only (work legs can't pulse mid-leg). A hard-killed orchestrate mid-`animating` (today's orphan) leaves a non-terminal record with a frozen heartbeat the gate-check ignores → still looks live → A keeps selecting it, B refuses launches against it. Missing signal: **is the orchestrate process actually alive?**
- **Fix Part 1 (gate_protocol.set_phase):** also stamp `rec["pid"] = os.getpid()`. set_phase runs INSIDE orchestrate (called early as `set_phase("running")`), so it's orchestrate's real pid.
- **Fix Part 2 (build_state):** if phase is non-terminal and the record's pid is NOT alive (`os.kill(pid, 0)` → `ProcessLookupError`), flip to `dead` (terminal). Covers work legs. Added `dead` to `_TERMINAL_PHASES`. `PermissionError` (alive-but-not-ours) is treated as alive — safe default.
- Existing records (incl. the live 70smusic) have no pid until their next `set_phase`; no-pid records are left untouched (back-compat). Verified against a real recently-dead pid: `animating + dead-pid → dead`, `animating + live-pid → kept`, `done → untouched`, `no-pid → untouched`.
- Sentinel: `pid liveness reaping`.

**Net of A+B+C:** close the laptop → run continues on the box → reopen/refresh/restart the server → the page rejoins the live run correctly; you cannot spawn duplicates; a dead process is reaped instead of lingering as a live-looking ghost. The exact failure that cost an SSH-and-kill session today now self-heals.

---

## PART 2 — Live ops: the stranded-run recovery (what drove A/B/C)

Closed the laptop ~5 min into the 70smusic (You Had To Be There, 105 beats) audio leg, then new page → Reset → dry-run → live launch. Result looked "stuck" at `phase: running · stills 0/105` with the text saying "audio leg."

Diagnosis via SSH:
- `ps` showed THREE relevant processes: a **2-hour orphan** orchestrate (PID from the interrupted first launch, 0% CPU, parked), the **real live run** (6 min, with a whisper child at 768% CPU actively transcribing), confirming work WAS happening.
- `.mc_jobs/` had **four records** for 70smusic: three `done` (duplicate launch clicks + the interrupted run) and one `running` (`...8201`, the live one). `active_job_id` (pre-A) was reading a `done` ghost → page lied.

Recovery (manual, the thing A/B/C now automate):
- `kill <orphan-pid>` (left the live run + its whisper untouched).
- Confirmed the live run was the sole remaining orchestrate.
- Moved the three `done` records to `~/Pipeline/.mc_jobs/_stale/` (move, not delete — reversible). Left only `...8201`.
- Refreshed → page locked onto the live run. It had already progressed to `animating` (clips 8/105) — fully intact.

Then built A (page would have shown `...8201` automatically), B (the duplicate clicks couldn't have spawned), C (the orphan would have been reaped). `.mc_jobs/_stale/` is safe to delete anytime (`rm -rf`).

---

## PART 3 — Banked principles & ground-truth (do not re-derive)

**Two assemblers, only one aligned (the drift lesson).** `assemble_episode.py` (beats + `_index.json` `rev_map` + frozen `durations.json`) is alignment-correct and is what the launched run uses. `recreation_pipeline.assemble()` (positional `zip`, no index, live Whisper re-align) drifts. **Anything that assembles MUST use `assemble_episode.py`.** `finish --assemble-only` (which calls the wrong one) is a footgun still reachable from the CLI — **retire or guard it** (open backlog). The clip→narration alignment is the control plane's core guarantee; never route assembly around the index map.

**Root vs modea artifact locations.** Root-level: `voiceover.mp3`, `final_video.mp4`, `durations.json`, `_index.json`, `render_policy.json`, `music.mp3` — at the PROJECT ROOT. Under `modea/`: `stills/`, `clips/`, `storyboard.json`. Code taking `--project <slug>/modea` (so clips resolve) must step up (`p["root"].parent`) for root artifacts. This caused TWO bugs (v0.7 `/video/` base, v1.2 assemble-only voiceover). Check this first on any path bug.

**`api()` key on query strings.** A key-appender that skips when a `?` already exists silently drops auth on every param-carrying GET. Rule: **always append, choose the separator** (`&` if `?` present, else `?`).

**Run-record liveness is three signals, not one.** Phase (what the run says it's doing), heartbeat (gate-phase liveness — A1), and pid-alive (process liveness — C). Gate phases use heartbeat; work legs use pid; terminal phases use neither. `active_job_id` must prefer the freshest LIVE record by `started_at` (not file mtime — a touched terminal record re-floats).

**One live run total (global).** Single-operator, one-video-at-a-time: refuse a second live launch. Prevents resource thrash and the duplicate-record mess. dry-run exempt.

**Multiple writers must share one source of truth.** The panel flicker was select + poll + done-event disagreeing. Make every writer key off the same fact (here: "does a final video exist") rather than a transient (a live `done` phase).

**Ground-truth facts touched:**
- `active_job_id` (pipeline_server ~317), `build_state` (~445), `launch_job` (~346), `/api/launch` handler (~1828–1834).
- `gate_protocol.py` lives at `shared/mission_control/gate_protocol.py`. `set_phase` (~94) stamps phase+heartbeat (+pid now); `touch_heartbeat` (~102) pulses; `await_gate` (~165) calls touch_heartbeat each poll. `os` imported (~37).
- `assemble_episode.py` flags: `--durations --index --voiceover --project --clips --out --no-music` (`clip_for(b, rev_map, clips_dir, …)` = the index-mapped lookup). `convergence_leg._pool_clips` copies `modea/clips/shot_*.mp4` → `<project>/clips/` (idempotent, overwrite).
- `cmd_finish` assemble-only branch (~1379); `proj_paths` (~1128) auto-prepends `projects/` to a bare name → `--project <slug>/modea` makes `root` the modea level.
- Mission Control v1.8. Version check = heading SHA vs `git rev-parse --short HEAD`. Restart safe mid-run (restarts the web server, not orchestrate). `_TERMINAL_PHASES = ("done","stopped","error","stale","dead")`.

---

## PART 4 — Doc consolidation (executed this session)

Four docs → two living + two stubs. Test for survival: *does Mission Control do this for me now?* yes → dead; no (craft) → keep.
- **`__PIPELINE-CANONICAL.md` = the system** (kept, extended): absorbed machina's architecture into §5 (channel.json identity contract, adding-a-channel, per-film look override, resolve-identity-explicitly-fail-loudly); §5.6 root-vs-modea principle; §13 surviving box commands; Scripture on Screen added.
- **`_ante-machinam.md` v3.0 = the craft** (slimmed): Part VI terminal mechanics → a paste-and-Launch bridge; Parts I/III/IV/V (Constitution, VISUAL writing, retention canon + IV.7 audit, channel briefs) intact.
- **`_machina.md` / `_README.md` → stubs** pointing at the two.
- (NOTE: this notes file post-dates that consolidation; the canonical should get a v1.8 + A/B/C update next session — see below.)

---

## PART 5 — Patch discipline reaffirmed this session

- **Pure ASCII** patch source; **no `"""` inside a `"""` docstring**; **simple print footers** — over-escaped quotes (`\\"`) in a trailing `print()` block broke `patch_reassemble_aligned.py` on first run (cosmetic instructions only; fixed by simplifying to single-quoted strings, no nesting).
- **Local imports for bg-runner deps:** the re-pool needed `shutil`, which the module doesn't import at top → imported it locally inside `_run_assemble_bg` (like the existing local `import subprocess as _sp`), rather than a fragile module-level insertion.
- **Simulate before shipping:** every patch this session was anchor-counted (×1), compiled, and logic-simulated (the drift fix's index mapping, the api() key separator across URL shapes, A's freshest-pick against the real record set, B's refuse logic, C's reap against a real dead pid). The sims caught a brace miscount and a bad test harness before they reached the box.

---

## NEXT SESSION (priority order)

1. **Finish the upload** (canonical §11 item 1) — `auth.py` fix (CLIENT_SECRET/TOKEN_FILE swap; headless OAuth → `scp token.json`; correct Final Hours brand account; 7-day testing token expiry) → `/api/upload` (wire `shared/upload_episode.py`) + schedule/visibility → enable the panel's Upload button. The panel, Download, and aligned Re-assemble all ship now.
2. **Retire/guard `finish --assemble-only`** — it calls the alignment-unsafe `assemble()`. Either make it route through `assemble_episode.py` too, or have it refuse with a pointer to the aligned path. (The wrong assembler is still reachable from the CLI.)
3. **`default_motion` dead-default root fix** — channel-aware authoring guidance so the per-channel default fires (stops the per-project hot-fix; read `recreation_pipeline.py` ~95–115 / ~470–485 / ~1245–1275 first).
4. **Update the canonical** to v1.8: add §5.7-ish for the A/B/C run-lifecycle hardening + the two-assemblers ground-truth; bump the Mission Control version history.
5. Cheap correctness: tiered-aware strip label (says "Kling" regardless of split), `safety_tolerance:"5"` on first stills pass, `finish --plan` CWD bug.

**Pending publish:** Esther (rendered, downloaded), Enoch (packaging + thumbnail). **In flight:** 70smusic (You Had To Be There, 105 beats) — was `animating` at session end; check it reached the stills→done and is publishable.

**Cleanup (box, anytime):** `rm -rf ~/Pipeline/.mc_jobs/_stale`; test-run-line{1,2,3} + `figures-test-2/modea/clips/kbtest.mp4`.

**Standing read (unchanged):** the system is shippable browser-only end to end, now reliability-hardened against close/refresh/restart and duplicate launches. Highest-leverage move stays: **ship real videos** on the proven tiered economics and let first-48h CTR + AVD drive the backlog — not grind it.
