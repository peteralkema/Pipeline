# SESSION NOTES — 06 July 2026 — FLOOR-FIRST shipped (engine + UI), auto-assemble removed, MC v3.8 → v3.9.2
## The ten-animal button-test rig · stop-at-clips · the KB-floor engine · the cssText afternoon · floor-first one-click

_Continuation of the 05 Jul floor-first-scoped arc (`SESSION-NOTES-2026-07-05-mc-widget-sectionbar-floorfirst.md`). This is the build session that turned the 05 Jul floor-first SCOPE into shipped, proven code — engine and UI. Long session, one long detour (a JS syntax bug that hung MC for ~2h), and a hard-won process lesson banked at the end. Doctrine graduations marked → ._

---

## 1. Where the session opened

MC at v3.8 (section bar + spend widget + per-beat craft surface all shipped). Floor-first was fully SCOPED in the 05 Jul notes but not built. The stated task order for the session: (1) 48h read on Gettysburg, (2) build floor-first, (3) inherit artifact proof, (4) Elijah reference-lock guard, (5) doctrine graduation. What actually happened: the read ran first (partial — see §2), then the build swallowed the rest of the session and grew a fourth task nobody planned (auto-assemble removal + a UI rebuild after a syntax bug). Floor-first shipped end to end; the Elijah guard and doctrine graduation carried.

## 2. The 48h read — ran, but the window wasn't fully open

Pulled Synthetic Press via NexLev owned-channel tools (`list_my_youtube_channels` → `get_my_channel_overview` → `get_my_top_videos` / `get_my_channel_analytics` / `get_my_audience_retention` / `get_my_traffic_sources`). Channel: `UCoiObjaF56A_dn4ZlN1V5jw`, 9 subs at read time, 308 total views, the Gettysburg film (`H9U5xi_KRfc`, 7:03) live since 4 Jul, trailer (`ZsA8FnX28lM`, 45s) since 3 Jul.

**The reporting API lagged to 3 Jul** — the film's own day-1 (4 Jul) daily reporting wasn't in the API yet, so the true 48h read (film CTR / day-level AVD / Browse%) was NOT available. What WAS available and banked:

- **The AVD-field trap re-confirmed LIVE.** Channel `totals.averageViewDuration` returned **7.22s**; the 3-Jul per-day row read **65s**; honest recompute `153 watch-min × 60 ÷ 141 views = 65.1s`. The totals field had divided 65 across all 9 calendar rows (65 ÷ 9 ≈ 7.2) — exactly the pre-launch-dilution artifact the canonical warns about. **Never read the totals AVD field on a young channel; the per-day row (or the manual recompute) is truth.**
- **The film retention curve (lifetime data → not date-lagged, so readable).** n≈16 viewers (audienceWatchRatio quantized in 1/16 steps → shape-only). Shape: holds ~94% through 0:30; first real step to 81% at ~0:34; 75% through ~1:29; 69% to ~1:33–2:03; trough **56% at ~2:28**; a genuine **mid-film re-engagement swell back to ~62.5% at ~3:24–3:53**; then **dead flat 56.25% from ~3:57 to the 7:03 end** — no further loss across the entire back half. Mean watch-ratio ≈ 0.642 → implied AVD ≈ **4:31 on a 7:03 film**. Relative-to-peers band 0.63–0.93, weakest at the trough, strongest through the tail.
- **Traffic (through 3 Jul, trailer-weighted, channel-total):** search + channel-page viewers watch longest (search 2.1 min/view, channel-page 1.9); **Browse/home still absent** — the cold-start feed hasn't activated. Consistent with the portfolio's known browse gap.

**Read verdict (banked, one partial signal, NOT two):** the all-trim register HOLDS at 7 min, and the *shape* of the hold — flat back half — is the encouraging part: survivors of the 2:28 dip are locked in, so a LONGER cut wouldn't keep shedding them. That is the first real evidence the 25–35 min Elijah bridge is viable. **But it is one partial signal at n≈16 with no 48h daily.** Two-signals rule NOT met → Elijah length stays a green-light-to-PLAN, not a green-light-to-SPEND. The one soft spot to design an Elijah cold open against is the 0:34→2:28 slide (94%→56%). **Re-pull the evening of 6 Jul / 7 Jul for the real film CTR + Browse% + de-quantized curve.**

## 3. The ten-animal button-test rig — the session's best instrument

Peter's call (correcting my proposed order): build a neutral regression rig and debug the mode buttons on it BEFORE flipping KB-to-default. Right call — on real content a glitch and a craft judgment look identical; on throwaway footage only the mechanism is under test.

**`ten-animals-buttontest` on Scripture on Screen** (deliberately the Elijah target channel, so the rig also dry-runs the exact channel we're about to trust with Elijah). Ten beats, dog→rabbit, **mixed narration lengths BY DESIGN** — the short beats (cow 8w, sheep 6w, duck 5w, rabbit 6w) leave inheritable tail; the long beats (29–31w) force the tail-runs-out fallback. Each beat targets a specific button scenario:

| # | Animal | Scenario | Proven at artifact |
|---|--------|----------|--------------------|
| 0 | Dog | Kling/Dynamic | 5.04s atom ✓ |
| 1 | Horse | Kling/Slow-crane | 5.04s atom — inherit source ✓ |
| 2 | Cow | inherit ← 1 | 2.33s derived tail ✓ |
| 3 | Sheep | inherit ← 2 (chain of 3) | 2.00s derived ✓ |
| 4 | Pig | KB override | **8.13s duration-exact** — KB longer than a 5s atom, can't black-frame ✓ |
| 5 | Chicken | Kling (upgrade-path demo) | 5.04s ✓ |
| 6 | Duck | (intended inherit; policy ran it as Kling) | fresh atom — setup gap, not a bug |
| 7 | Goat | Kling/Slow-crane | 5.04s ✓ |
| 8 | Cat (asleep) | **KB "wheat field"** | 6.83s duration-exact static ✓ |
| 9 | Rabbit | **inherit ← 8 (KB source) → must reject** | **2.25s free KB fallback on rabbit's OWN still ✓** |

**The rabbit was the ballgame and it came back clean.** Frame-0 of `shot_010.mp4` (rabbit's clip) vs `shot_009.mp4` (cat's clip): different images — rabbit's own still, NOT a slice of the cat's KB tail. So the **"you can only inherit from a horse, never a wheat field" invariant is proven at the artifact** — a KB-source inherit goes red and falls back FREE to Ken-Burns on the beat's own still, an entire failure class confirmed guarded, on neutral footage, before it ever touched Elijah. → **This rig is now the permanent floor-first / mode regression harness.**

**Inherit ARTIFACT proof — finally banked.** The one shipped control never verified at the assembled cut. Peter eyeballed the assembled ten-animal loop: horse→cow→sheep is ONE continuous camera move across both narration handoffs (cow and sheep riding the tail of horse's single Kling atom). "Looks great." → **Inherit is proven at the assembled cut; the derived-clip design holds end-to-end (sync doesn't drift, assembler + `_index.json` untouched).** The 05 Jul outstanding-item #2 is closed.

**A two-assembler footgun caught live.** A CLI `finish --assemble-only` on the rig printed `uniform 57.8s / 10 = 5.78s per clip` — the drift signature of `recreation_pipeline.assemble()` (positional, ignores durations.json). The aligned `assemble_episode.py` (reads durations.json, holds each beat to measured audio) is the only safe one; the MC Re-assemble button already shells it. **Banked: the CLI `finish --assemble-only` remains a drift footgun; only the MC button (or `assemble_episode.py` directly) is alignment-safe.** Also learned: `recreation_pipeline.py finish` does NOT take `--music-dir` (that's `assemble_episode.py`'s flag) — the engine's assemble-only reads `music.mp3` from the project root.

## 4. Auto-assemble removal — a backlog item that jumped forward because floor-first needs it

Peter's backlog framing (banked as its own doctrine, see §7 "box-folder-is-truth"): the box project folder must be the source of truth for what actually shipped. Four parts: (1) kill auto-assemble on first clip render, (2) upload-final-video path for externally-cut videos, (3) upload-only-from-MC with the committed video+thumbnail frozen and the prior archived, (4) a schedule date/time picker. Only part (1) built this session; (2)–(4) carried.

**The grep-first hunt (textbook, worth remembering the shape):** the render launch isn't a `finish` shell — MC's `launch_job` (pipeline_server.py) spawns `orchestrate.py` detached (`--gate-mode job`). `decide_legs` unconditionally appends `convergence` (assemble) after Mode A. The orchestrator ALREADY had the exact stop one leg earlier: the stills-gate `skip` → `ma.get("stopped")` → `sys.exit(0)`, no convergence. So "stop after clips" = mirror that exit one leg later, before the convergence block.

**Patch #1 — `patch_stop_after_clips.py` (orchestrate.py):** adds `--stop-after-clips`; after Mode A returns clips, `set_phase("clips_ready")` + `sys.exit(0)` before convergence. Pure capability — changes nothing until MC passes the flag.

**Patch #2 — `patch_launch_stopafterclips.py` (pipeline_server.py):** `launch_job` always passes `--stop-after-clips`; `APP_VERSION → v3.9`. This is the actual auto-assemble kill. (Peter's decision: **always stop at clips**, not a toggle — every `final_video.mp4` becomes a deliberate press, enforcing box-folder-is-truth.)

**Patch #3 — `patch_clips_ready_terminal.py` (pipeline_server.py):** `clips_ready` was mislabeled **dead** by the pid-liveness reaper (`build_state`, ~L520) because it wasn't in `_TERMINAL_PHASES`. The stop-after-clips run had SUCCEEDED (log: "run stopped after clips — assemble-ready, nothing assembled"; record phase `clips_ready`) — only the status string lied. Fix: add `clips_ready` to `_TERMINAL_PHASES`. **Verified via a dry-run launch: orchestrate hit the new exit, wrote `clips_ready`, exited 0.** (The dry-run also confirmed the flag threads through the dry path.)

**Patch #4 — assemble-at-clips (the chicken-and-egg):** killing auto-assemble orphaned the assemble control. The Re-assemble button lived only in the FINAL VIDEO panel, which renders only when `has_video`. With stop-at-clips a run ends at `clips_ready` with NO `final_video.mp4` → the panel never shows → the button that CREATES the first video is hidden behind the file it makes. Fix: `/api/meta` also reports `has_clips`; `renderDonePanel` shows an Assemble panel when `has_clips && !has_video`; `reassemble()` already works without a pre-existing video (only touches `#donepanel video` after success, guarded). **THIS PATCH CARRIED THE cssText BUG that broke the afternoon — see §6.**

## 5. FLOOR-FIRST engine — shipped and proven (`059ad73`)

`patch_kb_floor.py` on `recreation_pipeline.py`, policy-only (no new CLI flag — Peter's decision; MC writes the policy, the existing readers do the rest, keeping policy-file-is-truth). Four edits, all against the real `cmd_finish` plan loop:

1. **`_kling_override_set()`** — reader mirroring `_kb_override_set()`, reads `render_policy.json` `{"kling_override":[...]}`.
2. **Additive routing** in the plan loop: `elif (bi in kling_over) or (bi < kling_count and bi not in kb_over): engine="kling"`. Backward-compatible — no key → empty set → identical to pre-floor. Floor-first projects run `kling_count:0`, so ONLY the override list turns Kling on.
3. **`--kb-floor` = the existing `else:` branch** — a non-Kling non-inherit beat already routes to `ken_burns_still(still, clip, dur)` at its `_tiered_duration`. So the "floor pass" is the loop the engine already runs; floor-first is just routing everything there by default. Duration-exact, free.
4. **Delete-on-upgrade + `.kbfloor` sidecar marker.** The disk problem: KB and Kling both write `shot_NNN.mp4`, indistinguishable. Solution: the Ken-Burns branch writes a `shot_NNN.kbfloor` sidecar (assembly globs `shot_*.mp4`, never the sidecar). Delete-on-upgrade: a beat entering `kling_override` whose clip has a `.kbfloor` marker gets clip+marker deleted so `cmd_finish` re-renders it Kling. **KB→Kling deletes a FREE marked clip; a paid Kling clip carries no marker, so Kling→KB never deletes.** The Kling branch also unlinks any stale marker (a paid atom carries no floor marker).

**Proven at `--plan` on the committed box engine:** policy `{kling_count:0, kling_override:[0,5]}` → `N=0 → 2 Kling (~$0.70) + 8 Ken Burns (free)`, beats 0 and 5 → kling, the other eight → kenburns. The inversion works: default free floor, Kling additive per beat, spend opens at $0 and ticks up $0.35/beat. Backward-compatible (existing projects have no `kling_override`/`kling_count:0` → unchanged).

## 6. The cssText afternoon — the long detour and its lesson

**Patch #5 — the "Floor all (free)" button + preset auto-enroll (v3.9.2)** — broke the page. Symptom: MC stuck at "loading…". Console (eventually): `Uncaught SyntaxError: Unexpected identifier 'color'`. Cause: an inline JS `style` string built with `cssText = "...color:#d4a017;..."` — a quote/escape collapse across the Python→JS-string boundary terminated the JS string early, so the whole `<script>` died at parse. `py_compile` PASSED (Python valid) — it cannot see broken JS. The page compiled, shipped, and hung silently.

**Why it took ~2 hours to kill (the painful part, banked so it never repeats):**
- Chased cache and stale-process theories first (both real failure modes, both wrong here). systemd `restart` reported success but an earlier orphan process kept serving the broken JS on :8002 — a hard `stop` + `pkill -f pipeline_server.py` + `start` was needed to actually swap the process. (**Banked: `systemctl --user restart` is not always sufficient; confirm the Main PID changed, and pkill the orphan if the port is still bound to the old one.**)
- `git checkout HEAD~1 -- pipeline_server.py` reverted only the `APP_VERSION` line region, leaving the broken button JS in the file — a `grep -c "floorallbtn\|FLOOR_ALL_APPLIED"` returned **16**, not 0, proving the file was never actually clean. (**Banked: after any revert, GREP THE FILE for the offending strings; trust the grep, not the version stamp.**)
- The FIRST broken commit was not the floor-all button (`dfa9e3c`) but the **assemble-at-clips panel (`6b9fef5`)** — it used the same `cssText` pattern and was the real origin. Reverting to `6b9fef5` still served the bug. The last truly-clean MC page was `358f746` (clips_ready terminal phase, before ANY panel JS). (**Banked: to find the first bad commit, bisect by the served artifact, not by which patch you THINK broke it. `curl localhost:8002/?key=... | grep -c "Unexpected"` reads the served bytes and bypasses the browser entirely — the fastest box-side truth.**)

**The recovery (clean):** reverted the box file to `358f746`, committed the revert forward (`3f5da6f`, "revert to clean 358f746 page") so HEAD/GitHub/box all agree, synced the laptop. Then rewrote BOTH panels in ONE combined patch — `patch_floorfirst_ui.py` — with every style set via individual `element.style.prop = "..."` assignments and ZERO `cssText` string literals, plus a build-time guard (`if "cssText" in new[panel-region]: die(...)`). Deployed with a real box-side gate this time: `curl localhost:8002/?key=... | grep -c "Unexpected"` must read **0** before the browser is ever opened. It read 0. v3.9.2, `a640fa6`.

**THE PROCESS LESSON (the actual moat contribution of the day):** we shipped four MC patches WITHOUT ever loading the page and clicking the button, then the fifth hung MC for two hours over a bug a single page-load would have caught in ten seconds. `py_compile` proves syntax; it does NOT prove the JS parses or the handler runs. **The verify is compile → LOAD THE PAGE → CLICK THE THING, before commit. The `.style.prop=` change fixed the symptom; the click-before-commit discipline is the real fix.** Banked to §7.

## 7. FLOOR-FIRST UI — shipped and proven at the click (v3.9.2, `a640fa6`)

The combined `patch_floorfirst_ui.py` (seven anchored edits, no cssText):
- **`/api/meta` → `has_clips`** (clips dir holds `shot_*.mp4`).
- **`renderAssemblePanel`** — CLIPS READY panel with an "Assemble from clips" button when `has_clips && !has_video`; reuses `reassemble()`.
- **"Floor all (free)" button** in the sticky section bar — POSTs `/api/floor_all`.
- **Preset auto-enroll** — a Dynamic/Slow-crane click also POSTs `/api/kling_override` to enroll the beat (Peter's decision: **auto-enroll**, because under floor-first a motion preset that doesn't turn the beat Kling is a confusing no-op; picking a motion IS choosing to spend).
- **`_handle_kling_override_toggle`** — add to `kling_override`, drop from `kb_override`+`inherit_prev` (one mode per beat, mirroring the kb_toggle mutual-exclusion), delete the beat's `.kbfloor` clip (delete-on-upgrade).
- **`_handle_floor_all`** — `kling_count:0` + clear all three per-beat lists.
- **Routes** for `/api/kling_override` and `/api/floor_all`.

**Proven at the artifact (the click-test):** on `animals-test1`, clicking **Floor all (free)** wrote `render_policy.json` → `{"kling_count": 0}` (all three per-beat lists cleared, whole project floored to free). [Dog-Dynamic enroll test → expected `{"kling_count":0,"kling_override":[0]}` — confirm in session close.] Floor-first is now one click: floor everything to $0, then add motion per-beat with the presets, spend ticking up from zero.

## 8. What shipped today (the ledger)

Commits, laptop→GitHub→box, all idempotent `patch_*.py`, all verified:
- `f90ecf0` — MC launch always `--stop-after-clips` (kill auto-assemble); v3.9
- `358f746` — `clips_ready` is a terminal phase (clean stop, not "dead")
- `6b9fef5` — assemble-at-clips button [carried the cssText bug; superseded]
- `059ad73` — **floor-first engine** (kling_override additive routing, kling_count:0, delete-on-upgrade marker) — proven at `--plan`
- `dfa9e3c` — floor-all button v3.9.2 [cssText bug; reverted]
- `3f5da6f` — revert to clean 358f746 page
- `a640fa6` — **floor-first UI rebuilt clean** (assemble-at-clips + floor-all + preset auto-enroll, no cssText); v3.9.2 — proven at the click

Net: **auto-assemble removed, floor-first shipped end-to-end (engine + UI), MC at a clean v3.9.2, inherit proven at the assembled cut, the ten-animal regression harness banked.**

## 9. Doctrine graduations (→ candidates for canonical §7)

- **Click-before-commit for any MC page change.** compile proves syntax; only a page-load + button-click proves the JS parses and the handler runs. This session cost 2h to the gap.
- **No `cssText` string literals in server-emitted JS.** Build UI DOM via individual `element.style.prop =` assignments; the colon-and-quote-laden `cssText` string is a Python→JS boundary landmine. Add a build-time guard in the patch.
- **`curl localhost:8002/?key=... | grep -c "Unexpected"` is the box-side JS-parse gate.** Reads the served bytes, bypasses the browser, must be 0 before trusting a deploy.
- **After any revert, grep the file for the offending strings** — trust the grep, not the version stamp; a partial checkout can leave the bug in with a reverted version line.
- **`systemctl --user restart` may not swap the process** — confirm the Main PID changed; `stop` + `pkill -f pipeline_server.py` + `start` if the orphan still holds the port.
- **Floor-first psychology, now realized in UI:** floor everything free ($0, assemble-ready), then craft is additive spend you ADD per beat with the presets, widget ticking from zero. The $3-KB video and the $17-cinematic video are the same project at different craft depths.
- **`.kbfloor` sidecar** distinguishes a free floor clip from a paid atom on disk (same `shot_NNN.mp4` filename); delete-on-upgrade is direction-asymmetric (KB→Kling deletes free; Kling→KB never deletes paid).
- **Two-assembler footgun** re-confirmed: CLI `finish --assemble-only` drifts (uniform-slice signature); only `assemble_episode.py` / the MC button is aligned.

## 10. Outstanding (carried, in order)

1. **The film 48h read, for real** — re-pull Synthetic evening 6/7 Jul: film CTR, Browse%, de-quantized retention curve. Tonight's read was one partial signal (retention shape favors Elijah length; NOT two signals; hold doctrine).
2. **Dog-Dynamic enroll confirm** — verify `{"kling_count":0,"kling_override":[0]}` writes on the preset click (Floor-all half already proven). Closes the floor-first click-test.
3. **⚠ ELIJAH GUARD — still unaddressed.** `scripture-on-screen/projects/elijah-trailer-test/` exists on the box; the engine reference is QQrew-registered, so Elijah renders Pixar-cheerful without a per-channel reference-lock. Do NOT spend on Elijah stills until the lock is verified at the artifact (probe render). Reference-lock + parallel-fal semaphore are the two hard Elijah prerequisites.
4. **Doctrine graduation into `_Synthetic2.md`** — §5f parser marker whitelist (`## COLD OPEN`/`PART`/`ACT` only) + §7 three-tier motion rule ("animate the galloping horse, never the wheat field"; "you can only inherit from a horse").
5. **Auto-assemble backlog parts 2–4** — upload-final-video path; upload-only-from-MC with committed video+thumbnail frozen and prior archived; schedule date/time picker (default next 01:00 CEST golden-hour slot).
6. **`make_shorts.py`** — reads the committed `final_video.mp4`; needs the box-folder-is-truth discipline (parts 2–3 above) so Shorts cut from the exact shipped video.
7. Daemonize-runs (restart survives in-flight renders) — still open, matters more each MC iteration. Note the process-swap lesson from §6 (pkill the orphan).
8. Untracked-cruft cleanup on laptop + box (`*_from_box.*`, `looktest-*.json`, `success-coach/new_thumbs/`, etc.) — don't `git add -A`.

