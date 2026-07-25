# SESSION NOTES — Mission Control: in-place clip reload, URL persistence, upload-panel wireframe

_YouTube Media Flywheel · solo operator · all edits LAPTOP → GitHub → box · never hand-edit on box._

---

## TL;DR

- Shipped two Mission Control page fixes: **clips now appear in place** when rendered (no "refresh to view"), and **a refresh now stays in the project** (URL persistence); **Reset** is the explicit way back to base state.
- Designed (wireframe + spec, **not built**) the **FINAL VIDEO UPLOAD TO STUDIO** panel that fills the top-right blank space, completing the U-flow: initiate top-left → storyboard along the bottom → final video + one-click upload, top-right.
- Next action: push the **Enoch** (Final Hours) script through the cost-limited tiered render — Kling as first-clip producer, **Ken Burns as the second producer joining the team** for the remainder.

---

## Shipped this session (both LAPTOP → push → box → restart → node-check, PAGE_JS_VALID)

### 1. `patch_reloadclip_inplace.py` — once-off clips render in place
- **Root cause:** in `bindAnimateButtons` the helper did `const grid = cell.parentElement` and called it "the 5-col grid", but `cell` is the `.motioncell`, so its parent is the **motion column wrapper**, not the grid. The `video[src*="shot_NNN.mp4"]` lookup searched the wrong subtree and always returned false → always "clip rendered — refresh to view". The sibling `reloadStill` does it correctly with `parentElement.parentElement`.
- Second cause: on the **first** clip for a beat there is no `<video>` element at all, only the "not rendered" placeholder — nothing to update.
- **Fix:** corrected the grid reference; on first render, replace the placeholder in the clip column (`grid.lastElementChild`) with a fresh `<video>` pointing at the new clip. Result: clips appear in place immediately; "refresh to view" effectively never fires.
- Sentinel: `grid.lastElementChild`. Backup: `.pre_reloadclip`.

### 2. `patch_url_persist.py` — refresh stays in the project, Reset clears it
- Project selection lived only in `window.__SEL_VIEW` (browser memory), so any refresh dropped to base.
- **Fix (6 edits):** added `setUrlProject(ch, pr)` (writes `?channel=&project=` via `history.replaceState`, preserves `?key=`); seed `__SEL_VIEW` from the URL at load; write the URL on `proj.onchange` and on create; clear it on `chan.onchange` and `resetAll`; in `ensureShell` first build, if the URL names a project **and no run is active** (`!isActiveRun(state.phase)`), restore the dropdown selection (chan → `refreshProjects` → proj).
- Model locked: **refresh = stay put, Reset = leave.** Active runs unaffected — the job record drives the page during a render; URL persistence only covers the idle/browsing case. Projects are now bookmarkable.
- Sentinel: `function setUrlProject`. Backup: `.pre_urlpersist`.

---

## Designed, NOT built — FINAL VIDEO UPLOAD TO STUDIO panel (next session, first task)

Wireframe: `wireframe-final-video-upload.html`. Fills the top-right blank space so the page becomes a full U:
**① initiate (top-left)** → **② storyboard & assets (down + across bottom)** → **③ final video → one-click upload (back up, top-right).**

Panel contents, top to bottom:
1. **Assembled video** — `final_video.mp4`, autoplay muted/loop, with duration · resolution · size, reload/download.
2. **Thumbnail** — 16:9 slot, **manual for now** (Clickly), drop/pick; auto-generate later.
3. **Title** + **Tags** — pre-filled from the `beats_full.json` header, editable inline.
4. **Description** — pre-filled from header, editable.
5. **Schedule & visibility** — Private / Public / Scheduled + date + time; Category (Entertainment); optional playlist.
6. **Altered content = Yes** toggle **surfaced on the panel** — so the Final Hours / YHTBT requirement (currently set by hand in Studio every upload) travels with the metadata and can't be forgotten. _(New idea this session — confirm keep.)_
7. **One-click UPLOAD TO YOUTUBE STUDIO** — single-video jobs upload per metadata; **batched jobs have no button** (exit at `final_video.mp4` for manual cutting).

### Why it wasn't built this session (the honest call)
A one-click upload with no backend is theatre. Build order next session:
1. **Fix `auth.py`** — (a) variable-swap bug: read `CLIENT_SECRET="client_secret.json"`, `TOKEN_FILE="token.json"` (currently inverted); (b) headless OAuth (box has no browser) — auth on laptop, `scp token.json` to box; (c) correct Final Hours brand account (`peteralkema2@gmail.com`, test user); (d) root cause: OAuth app in 7-day testing mode → weekly token expiry; move app out of testing or accept weekly re-auth.
2. **Add `/api/upload`** — the channel-agnostic uploader (`shared/upload_episode.py`, wired into `convergence_leg.py`) already exists; wire it to an endpoint. Add GET/POST for the metadata fields, mirroring the `render_policy` pattern.
3. **Patch the panel** into the top-right of `pipeline_server.py` — **read the current top-section HTML first** (grep the real code, don't guess), idempotent patch, node-check.

---

## Cleanup pending (box)

```
rm -f sacred-dawn/projects/figures-test-2/modea/clips/kbtest.mp4
```
(Ken-Burns isolation-test leftover.)

---

## Backlog (priority order, after the upload panel)

1. **A1 — heartbeat dead-run detection** (last correctness gap, now polish): a dead/killed `orchestrate` leaves the job frozen at a phase, so the page renders a live gate for a dead run. Fix: orchestrate writes a heartbeat timestamp into the job record; `build_state` flips a run with no heartbeat in N min to phase `stale` (A0 strip already has the branch). **Heartbeat-timestamp, not PID-check** (PID reuse). Lives in `gate_protocol.py` + a small `build_state` touch. Reset already makes a frozen run a one-click recovery, so this is polish.
2. **Music** — decide generated (`make_music.py`) vs curated bed; wire into convergence.
3. **Move the Kling-count field into the always-visible controls strip** (consistency fix): the `Kling clips: N` field currently lives in the **stills gate bar**, so it only appears at phase `gate_stills` — it breaks the "everything always visible, just disabled when not usable" rule that the rest of the controls follow. Mirror it into the persistent controls strip, disabled from idle, going live at the stills gate (pre-filled from `render_policy.json` else default 40, save-on-change). Cheap; read the current gate-bar field markup first, then patch the controls strip.
4. **Decade-look Phase 2** — `film_emulate.py` grade layer.
5. **Multi-project / daemonized review server.**
6. **Inworld chunk-validation guard.**

Standing read: with tiered render in, the system is shippable browser-only end to end (create → launch → gate → tiered render → assemble → reset). The highest-leverage move is shipping real videos on the new Ken-Burns-floor economics, not more plumbing. Judge everything on CTR + AVD in the first 48 hours.

---

## NEXT ACTION

Kick off the **Enoch** (Final Hours) script through the cost-limited tiered approach:
- **Kling = first-clip producer** (first N beats), **Ken Burns = second producer** for the remainder (the cost floor).
- Set the **Kling clips: N** field in the stills gate (or `render_policy.json` / `--kling-count N`) for the Enoch project.
- Final Hours upload still **manual** this session (Category = Entertainment, add tags, **Altered content = Yes** in Studio).

---

## Ground-truth facts touched this session (do not re-derive)

- `reloadClip` / `reloadStill` live in `bindAnimateButtons` / `bindStillControls` in `pipeline_server.py`. The beat row is a 5-col grid: text · still · controls · motion · clip. `.motioncell` is inside the **motion** column wrapper, so the grid is `cell.parentElement.parentElement`. The clip cell is `grid.lastElementChild`.
- Selection state: `window.__SEL_VIEW = "<folder>/<slug>"` (folder = hyphen form from the dropdown; `resolve_paths` is hyphen/underscore tolerant). `build_state` returns `state.channel` as the **header** name (underscore). During an active run the job record drives the body; `__SEL_VIEW` only matters when idle.
- URL params now in use on the page: `?key=` (existing, read by `KEY` and `api()`), plus `?channel=&project=` (new, read only by the page-JS restore — does **not** affect `api()` calls).
- `isActiveRun(phase)` already exists and is reused by the URL restore guard.
- Mission Control: `http://116.202.18.68:8002/?key=fh2026`, service `mission-control.service`, restart `systemctl --user restart mission-control.service`. `review.service` on :8001 untouched.
- Standard node-check after any page-JS change: extract the last `<script>` block and `node --check` it → want `PAGE_JS_VALID`.
