# SESSION NOTES — 15 June 2026: audio→stills seam fix, Re-assemble button, assemble-only path fix, doc consolidation

_YouTube Media Flywheel · solo operator · all edits LAPTOP → GitHub → box · never hand-edit on box._
_Mission Control went **v0.9 → v1.1** this session. Doc set consolidated from four to two._

---

## TL;DR

- **v1.0 — audio→stills seam fix + decided-gate stale guard.** A healthy stills run was false-flagging as "stale / ended unexpectedly" (caught live on Esther). Two compounding causes fixed: the audio gate handed off to the stills leg without writing a new phase (record frozen at `gate_audio`), and the stale-check fired on a gate whose decision was already made.
- **v1.1 — Re-assemble button.** The launched run auto-assembles right after clips, so the per-clip re-render controls were moot. Added a button next to Download that re-stitches the final video from the current clips (`finish --assemble-only`, no render cost). Review → re-render → rebuild is now a two-click loop.
- **v1.2 backend — assemble-only path fix.** The Re-assemble button surfaced a pre-existing bug: assemble-only resolved voiceover/final/music one level too deep (under `modea/`) when they live at the project root. Banked the root-vs-modea artifact-location principle.
- **Esther** (Scripture on Screen, new channel) ran through to a final video. Motion hot-fixed per project (the dead-default bug, third time).
- **Docs consolidated to two:** the canonical reference (the system) + ante-machinam v3.0 (the craft). `machina.md` and `README.md` retired to stubs.

---

## Shipped (each LAPTOP → push → box → restart → version-check → node-check)

### v1.0 — `patch_audio_stills_seam.py` (2 files: orchestrate.py + pipeline_server.py)
- **The bug, seen live on esther--1:** after accepting the audio gate, the job record stayed `phase: gate_audio` while stills rendered, because orchestrate ran `run_modea_leg` (stills) with no phase write between the audio gate and the stills leg. Two consequences: (1) the status line couldn't count stills (its count branch needs `running`/`gate_stills`); (2) **worse** — `gate_audio` is a stale-checked gate phase, and the heartbeat froze at the moment "keep" was clicked (A1 only pulses heartbeat inside `await_gate`'s poll loop, not during a work leg), so after `STALE_SECONDS` the page false-flagged the healthy run as "ended unexpectedly."
- **Fix 1 (orchestrate, the real fix):** `set_phase(_job_id, "running", ctx["repo_root"])` right before `modea_leg.run_modea_leg(ctx)`, job-mode guarded — the record leaves `gate_audio`, the strip counts, and it's no longer a gate phase.
- **Fix 2 (build_state, the safety net):** the stale-check now only fires on a gate that is still `waiting` — `if phase in ("gate_audio","gate_stills") and (rec.get("gate") or {}).get("status") == "waiting"`. A `decided` gate means the run moved on; it can never false-stale. This alone would have prevented what we watched.
- Verified by simulation: decided gate → never stale; waiting + silent heartbeat → still stale (genuine dead-at-gate still caught); waiting + fresh → fine. Sentinel: `audio->stills seam`.
- **Note:** this didn't change the in-flight esther--1 run (already past the seam); it fixes the next from-scratch run. Restarting `mission-control.service` mid-run is safe — it restarts the web server, not the `orchestrate` process doing the work.

### v1.1 — `patch_reassemble_button.py` (pipeline_server.py)
- `_run_assemble_bg` (background thread, mirrors `_run_animate_bg`) shells `python recreation_pipeline.py finish --project <slug>/modea --assemble-only` with `cwd = project_dir.parent` (the channel's `projects/` dir) — the exact cwd/`--project` pair proven by the enoch1 run, so it can't hit the `--plan` CWD bug.
- New `/api/assemble` (POST) + `/api/assemble_status` (GET), mirroring the animate endpoints. Button in the FINAL VIDEO panel next to Download → "assembling from latest clips…" → on done, cache-busts the `<video>` src so the new cut loads in place.
- Sentinel: `def _run_assemble_bg`. The future home for music options.

### v1.2 backend — `patch_assemble_only_paths.py` (recreation_pipeline.py, no page-version bump)
- **Surfaced by the Re-assemble button on esther--1:** assemble failed with "missing voiceover: esther--1/modea/voiceover.mp3". The assemble-only branch of `cmd_finish` used `p["voice"]`/`p["final"]`/`p["root"]/music.mp3` — but with `--project esther--1/modea`, `proj_paths` sets `p["root"] = esther--1/modea`, so those resolved one level too deep. The voiceover (and final_video, and music) live at the **project root**.
- **Fix:** in the assemble-only branch, resolve voice/final/music from `p["root"].parent` (`_asm_root`) — the same place the normal finish path computes `project_root = p["root"].parent`. Clips stay under `modea/` (correct). Sentinel: `assemble-only: root-level artifacts`.
- **Banked principle (now §5.6 of the canonical):** root-level artifacts (voiceover, final_video, durations.json, _index.json, render_policy.json, music.mp3) live at the PROJECT ROOT; only stills/clips/storyboard live under `modea/`. This is the **second** bug from that confusion (the first was the v0.7 `/video/` base bug) — so it earned a named principle. When a path bug appears, check this distinction first.

---

## Esther production run (Scripture on Screen)

- New channel `scripture_on_screen` in production; project esther--1 (119 beats, ~26 min audio).
- The audio gate → stills leg false-stale happened live here — proved the run was healthy (stills climbing on disk every refresh) while the page lied. Confirmed via disk + the `.mc_jobs` record (phase `gate_audio`, gate `decided`, heartbeat frozen at `decided_at`). This run is what drove the v1.0 fix.
- `scripture-on-screen/channel.json` **has** a good dramatic `default_motion`, but all 119 beats still carried the slow string — the `default_motion` dead-default bug, third project (Enoch, test runs, now Esther). Hot-fixed per project with the storyboard `motion_prompt` rewrite (reads the channel default, backs up to `.pre_motion_*`). Root fix is backlog item 2.
- Final video at `~/Pipeline/scripture-on-screen/projects/esther--1/final_video.mp4` (project root — §5.6).

---

## Doc consolidation (executed this session)

The control plane obsoleted the terminal-era operational docs. Recommendation made and executed: **collapse four docs to two self-contained ones + two stubs.** Test for survival: *does Mission Control do this for me now?* yes → dead; no (craft) → keep.

- **`_YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md` = the system** (kept, extended). Absorbed machina's architectural survivors into §5 (the `channel.json` identity contract, adding-a-channel, the per-film look override, and the *resolve-identity-explicitly-fail-loudly* design law). Updated §5.1 to v1.1 (+ Re-assemble + seam fix), added §5.6 (the root-vs-modea path principle), added the Scripture on Screen channel, and added **§13 — surviving box commands** (SSH/venv, scp the final video, the motion hot-fix heredoc, the free assemble-only sanity command, auth, the service restart) kept until each becomes a button. Bumped to 15 June.
- **`_ante-machinam.md` = the craft** (slimmed to v3.0). Stripped Part VI's terminal mechanics (parse/verify/dry-run/launch/babysit) down to a two-paragraph **paste-and-Launch** bridge pointing at the canonical §5. Kept everything that makes a script land: Part I Constitution, Part III VISUAL writing, Part IV retention canon + the IV.7 audit, Part V channel briefs. This is the half the console can't do for you.
- **`_machina.md` → stub** (~700 of 752 lines were terminal-era command cards / playbook / orchestrator build-status; all obsolete). Points at the two living docs.
- **`_README.md` → ~15-line map** of the two-doc set (its old job was navigating four+ docs).

---

## Ground-truth facts touched this session (do not re-derive)

- **orchestrate.py:** audio gate fires in `audio_leg.run_audio_leg` (~276); Mode A block at ~290 with `set_phase("running")` now before `run_modea_leg` (~296, job-mode guarded); the `stopped` path (skip convergence) at ~300; convergence/assemble leg at ~311 (`set_phase("assembling")`); `done` at ~330. Phase writes live in orchestrate.
- **build_state stale check:** gate phases only, and now only when the gate is still `waiting`. `STALE_SECONDS = 300`. `stale` is rendered by `phaseStrip` and excluded from `ACTIVE_PHASES`.
- **`cmd_finish` assemble-only branch (~1379):** resolves clips from `p["clips"]` (under modea, correct) but root artifacts now from `p["root"].parent`. The normal path computes `project_root = p["root"].parent` at ~1414 for the same reason.
- **`proj_paths(project)` (~1128):** returns root/script/storyboard/stills/clips/voice/final, all `project / …`; auto-prepends `projects/` to a bare name. So `--project <slug>/modea` makes `root` the modea level → root artifacts need `.parent`.
- **`_run_animate_bg` / `_ANIMATE_JOBS` (~107–125):** the module-level background-thread + status-dict pattern; `_run_assemble_bg` mirrors it. `_resolve_request_project(body)` resolves channel+project from a POST.
- **Re-assemble invocation (proven):** `cwd = resolve_paths(...)["project"].parent`, `--project = "<slug>/modea"` — matches the enoch1 run, avoids the `--plan` CWD bug.
- Mission Control: `:8002`, `mission-control.service`. Version check = heading SHA vs `git rev-parse --short HEAD`. Restart safe mid-run (restarts the web server, not orchestrate).

---

## Standing read + next session

The system is shippable browser-only end to end, with the review→re-render→re-assemble loop now closed. Highest-leverage move stays: **ship real videos** on the proven tiered economics and let first-48h CTR + AVD drive the backlog — not grind it.

**Next session (canonical §11 order):**
1. **Finish the upload** — `auth.py` fix (CLIENT_SECRET/TOKEN_FILE swap; headless OAuth → `scp token.json`; correct Final Hours brand account; 7-day testing token expiry) → `/api/upload` (wire `shared/upload_episode.py`) + schedule/visibility fields → enable the panel's Upload button.
2. **`default_motion` dead-default root fix** — channel-aware authoring guidance so the per-channel default fires (stops the per-project hot-fix; read `recreation_pipeline.py` ~95–115 / ~470–485 / ~1245–1275 first).
3. Cheap correctness: tiered-aware strip label (says "Kling" regardless of split), `safety_tolerance:"5"` on first stills pass, `finish --plan` CWD bug, freshest-record in build_state.

**Pending publish:** Esther (rendered), Enoch (packaging + thumbnail).
**Cleanup (box):** test-run-line{1,2,3} plumbing-test projects + `figures-test-2/modea/clips/kbtest.mp4`.
