#!/usr/bin/env python3
"""
patch_mc_animate_async.py — make once-off animate fire-and-poll.

The sync /api/animate held the HTTP connection ~51s (one Kling call). The box
curl tolerated it; the browser timed out ("Failed to fetch"). Fix: same pattern
as the gates/detached-orchestrate — start the work, return immediately, poll for
completion. Survives browser timeouts, network blips, and closing/reopening the
page (the thread keeps working server-side).

FOUR edits to pipeline_server.py:
  1. import threading + a module-level _ANIMATE_JOBS status dict.
  2. _handle_animate: validate, set status "running", spawn a thread that runs
     animate_still and flips status to "done"/"error", return {ok, started}
     IMMEDIATELY (no blocking).
  3. GET /api/animate_status?channel=&project=&shot= -> the status dict.
  4. bindAnimateButtons: POST to start, then setInterval-poll the status every
     3s; on "done" reload the clip in place + stop; on "error" show it + stop.

Status key = "channel/project/shot". Lives in a module dict (not the job record)
so once-off animate works with NO active job (browsing a finished project).

All JS is plain single-quoted concatenation (no nested quotes) — node-verified
round-trip. Verify the served page with node --check before refreshing.

Idempotent (markers), backs up to .pre_animateasync.

Run on the box:
  python shared/mission_control/patch_mc_animate_async.py --check
  python shared/mission_control/patch_mc_animate_async.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

# ---- EDIT 1: import threading + the status dict (anchor: the animate import) ----
EDITS.append(dict(
    marker="_ANIMATE_JOBS",
    old='''try:
    from recreation_pipeline import animate_still as _animate_still
    _ANIMATE_OK = True
except Exception as _ae:
    _ANIMATE_OK = False
    _ANIMATE_IMPORT_ERR = str(_ae)''',
    new='''try:
    from recreation_pipeline import animate_still as _animate_still
    _ANIMATE_OK = True
except Exception as _ae:
    _ANIMATE_OK = False
    _ANIMATE_IMPORT_ERR = str(_ae)

import threading as _threading
# Per-shot once-off animate status, keyed "channel/project/shot". Module-level
# (not the job record) so animate works with no active job. Values:
#   {"status": "running"|"done"|"error", "error": <str?>}
_ANIMATE_JOBS = {}
_ANIMATE_LOCK = _threading.Lock()

def _animate_key(ch, pr, shot):
    return f"{ch}/{pr}/{shot}"

def _run_animate_bg(key, still_path, motion_prompt, out_path):
    try:
        _animate_still(still_path, motion_prompt, out_path)
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "done"}
    except Exception as e:
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "error", "error": str(e)}'''
))

# ---- EDIT 2: _handle_animate becomes fire-and-return ----
EDITS.append(dict(
    marker="started in background",
    old='''        # clips dir is the sibling of stills under modea/
        clips_dir = stills_dir.parent / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)
        out_path = clips_dir / f"shot_{shot_idx:03d}.mp4"
        sys.stderr.write(f"[Animate] shot {shot_idx:03d} (once-off) ...\\n")
        try:
            _animate_still(still_path, motion_prompt, out_path)
        except Exception as e:
            self._json(500, {"ok": False, "error": f"animate failed: {e}"}); return
        self._json(200, {"ok": True, "shot": shot_idx}); return''',
    new='''        # clips dir is the sibling of stills under modea/
        clips_dir = stills_dir.parent / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)
        out_path = clips_dir / f"shot_{shot_idx:03d}.mp4"
        sys.stderr.write(f"[Animate] shot {shot_idx:03d} started in background ...\\n")
        # Fire-and-poll: start the Kling call in a thread, return immediately.
        key = _animate_key(ch, pr, shot_idx)
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "running"}
        th = _threading.Thread(target=_run_animate_bg,
                               args=(key, still_path, motion_prompt, out_path),
                               daemon=True)
        th.start()
        self._json(200, {"ok": True, "started": True, "shot": shot_idx}); return'''
))

# ---- EDIT 3: GET /api/animate_status route (anchor: the health route) ----
EDITS.append(dict(
    marker='path == "/api/animate_status"',
    old='''        if path == "/api/health":
            self._json(200, {"ok": True, "service": "mission-control"}); return''',
    new='''        if path == "/api/health":
            self._json(200, {"ok": True, "service": "mission-control"}); return
        if path == "/api/animate_status":
            q = parse_qs(parsed.query)
            ch = q.get("channel", [""])[0]
            pr = q.get("project", [""])[0]
            shot = q.get("shot", [""])[0]
            key = _animate_key(ch, pr, shot)
            with _ANIMATE_LOCK:
                st = dict(_ANIMATE_JOBS.get(key, {"status": "idle"}))
            self._json(200, st); return'''
))

# ---- EDIT 4: bindAnimateButtons fires then polls ----
EDITS.append(dict(
    marker="pollAnimate",
    old='''    btn.addEventListener("click", async function() {
      btn.disabled = true; const label0 = btn.textContent;
      btn.textContent = "Rendering (Kling)…";
      msg.style.color = "#8a8a99"; msg.textContent = "animating — this takes a bit…";
      try {
        const r = await api("/api/animate", {method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({channel: CH, project: PR, shot: shot,
                                motion_prompt: box.value})});
        if (r.ok) {
          msg.style.color = "#7a4ddb"; msg.textContent = "clip rendered";
          // reload the clip <video> in this row, cache-busted
          const n3 = String(shot).padStart(3, "0");
          const grid = cell.parentElement;  // the 5-col grid
          const vid = grid.querySelector('video[src*="shot_' + n3 + '.mp4"]');
          if (vid) {
            const base = vid.src.split("&_t=")[0];
            vid.src = base + "&_t=" + Date.now(); vid.load();
          } else {
            // no clip cell existed yet (still-only beat) — soft refresh on next poll
            msg.textContent = "clip rendered — refresh to view";
          }
        } else {
          msg.style.color = "#d46a6a"; msg.textContent = "error: " + (r.error || "failed");
        }
      } catch (e) {
        msg.style.color = "#d46a6a"; msg.textContent = "error: " + e;
      }
      btn.disabled = false; btn.textContent = label0;
    });''',
    new='''    function reloadClip() {
      const n3 = String(shot).padStart(3, "0");
      const grid = cell.parentElement;  // the 5-col grid
      const vid = grid.querySelector('video[src*="shot_' + n3 + '.mp4"]');
      if (vid) {
        const base = vid.src.split("&_t=")[0];
        vid.src = base + "&_t=" + Date.now(); vid.load();
        return true;
      }
      return false;
    }
    function pollAnimate(label0) {
      const url = "/api/animate_status?channel=" + encodeURIComponent(CH) +
                  "&project=" + encodeURIComponent(PR) + "&shot=" + shot;
      const iv = setInterval(async function() {
        let st;
        try { st = await api(url); } catch (e) { return; }  // transient blip: keep polling
        if (st.status === "done") {
          clearInterval(iv);
          msg.style.color = "#7a4ddb";
          msg.textContent = reloadClip() ? "clip rendered" : "clip rendered — refresh to view";
          btn.disabled = false; btn.textContent = label0;
        } else if (st.status === "error") {
          clearInterval(iv);
          msg.style.color = "#d46a6a"; msg.textContent = "error: " + (st.error || "failed");
          btn.disabled = false; btn.textContent = label0;
        }
        // status "running"/"idle": keep waiting (spinner stays)
      }, 3000);
    }
    btn.addEventListener("click", async function() {
      btn.disabled = true; const label0 = btn.textContent;
      btn.textContent = "Rendering (Kling)…";
      msg.style.color = "#8a8a99"; msg.textContent = "animating — this takes a bit…";
      try {
        const r = await api("/api/animate", {method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({channel: CH, project: PR, shot: shot,
                                motion_prompt: box.value})});
        if (r.ok && r.started) {
          pollAnimate(label0);  // fire-and-poll: connection returned, now poll for the file
        } else {
          msg.style.color = "#d46a6a"; msg.textContent = "error: " + (r.error || "failed to start");
          btn.disabled = false; btn.textContent = label0;
        }
      } catch (e) {
        msg.style.color = "#d46a6a"; msg.textContent = "error: " + e;
        btn.disabled = false; btn.textContent = label0;
      }
    });'''
))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if not T.is_file():
        sys.exit(f"missing: {T}")
    text = T.read_text()

    plans, fatal = [], []
    for i, e in enumerate(EDITS, 1):
        if e["marker"] in text:
            plans.append((i, "skip-applied")); continue
        n = text.count(e["old"])
        if n == 1: plans.append((i, "apply"))
        elif n == 0: fatal.append(f"edit {i}: ANCHOR NOT FOUND")
        else: fatal.append(f"edit {i}: anchor x{n}")

    print("=== ANIMATE-ASYNC PATCH PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_animateasync")
    if not bak.exists():
        bak.write_text(text); print(f"  backup -> {bak.name}")
    for i, e in enumerate(EDITS, 1):
        if i not in to_apply: continue
        text = T.read_text()
        if text.count(e["old"]) != 1:
            print(f"  !! edit {i}: anchor changed — ABORT"); sys.exit(2)
        T.write_text(text.replace(e["old"], e["new"], 1))
        print(f"  applied -> edit {i}")
    print("\n=== DONE === restart, THEN node --check the served page before refreshing:")
    print("  systemctl --user restart mission-control.service")


if __name__ == "__main__":
    main()
