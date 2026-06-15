#!/usr/bin/env python3
"""
patch_launch_idempotent.py -- refuse a launch while a run is already live (Hardening B, v1.7).

WHY (duplicate orchestrates today)
  The Launch button disables on click, but the POLL re-enabled it (line ~811:
  launch.disabled = run || ...). Before A, the poll often saw "not running" (active_job_id
  returned a done ghost), re-enabled the button, and a second click spawned a SECOND
  orchestrate -- job_id is int(time.time()), so two launches a second apart get distinct
  ids and nothing stopped a duplicate. Result today: an orphan + duplicate records.

  A (v1.6) makes the poll see the live run correctly, which already reduces this. But the
  ROBUST fix is server-side: launch_job must REFUSE if a run is already live -- that blocks
  duplicates from fast clicks, page reloads, AND two browser tabs alike.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  1. launch_job: before spawning, consult active_job_id() (A makes this the freshest LIVE
     run). If a live (non-terminal) run exists, return
        {"ok": False, "error": "...", "already_running": <job_id>, "phase": <phase>}
     and DO NOT spawn. One live run total (global) -- matches one-video-at-a-time and stops
     two whisper/fal processes thrashing the box. (dry-run is exempt: it spends nothing and
     does not spawn a long render -- a dry-run never blocks and is never blocked.)
  2. /api/launch handler: if launch_job returns ok:False, respond 409 (not 200) with the
     payload, so the page can tell "refused" from "started."
  3. Page launch.onclick: read the response; on refusal show the message in #createmsg-style
     feedback and keep the button state honest (poll governs re-enable). On success, proceed.
  APP_VERSION -> v1.7.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `refuse if a run is already live`). Anchors verified once;
  .pre_launchguard backup; py_compile + JS brace/paren note; rollback on failure. Requires v1.6.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "refuse if a run is already live"

# --- 1. launch_job guard (server) --------------------------------------------
OLD_LAUNCH = '''def launch_job(channel_folder: str, project: str, dry_run: bool, log: str) -> dict:
    """Spawn orchestrate.py as a DETACHED subprocess in gate-mode=job.
    Returns {job_id}. The render runs in its own process group, so restarting
    THIS server never kills it."""
    header_channel = _channel_header_name(channel_folder)
    beats_full = _REPO / channel_folder / "projects" / project / "beats_full.json"
    job_id = f"{header_channel}__{project}__{int(time.time())}"'''
NEW_LAUNCH = '''def launch_job(channel_folder: str, project: str, dry_run: bool, log: str) -> dict:
    """Spawn orchestrate.py as a DETACHED subprocess in gate-mode=job.
    Returns {job_id}. The render runs in its own process group, so restarting
    THIS server never kills it.

    Hardening B: refuse if a run is already live (one live run total). A live LAUNCH while
    another run is mid-flight is the duplicate-spawn that stranded an orphan + dup records.
    dry-run is exempt (no spawn, no spend)."""
    header_channel = _channel_header_name(channel_folder)
    if not dry_run:
        _live = active_job_id()
        if _live:
            try:
                import json as _json
                _rec = _json.loads((jobs_dir(_REPO) / f"{_live}.json").read_text())
            except Exception:
                _rec = {}
            _ph = str(_rec.get("phase") or "")
            if _ph and _ph not in _TERMINAL_PHASES:
                return {"ok": False, "already_running": _live, "phase": _ph,
                        "error": f"A run is already live ({_rec.get('project','?')}, phase {_ph}). "
                                 f"Wait for it to finish or reach a gate, or Reset it, before launching another."}
    beats_full = _REPO / channel_folder / "projects" / project / "beats_full.json"
    job_id = f"{header_channel}__{project}__{int(time.time())}"'''

# --- 2. /api/launch handler: 409 on refusal ----------------------------------
OLD_HANDLER = '''            self._json(200, {"ok": True, **launch_job(ch, pr, dry, log)}); return'''
NEW_HANDLER = '''            _lr = launch_job(ch, pr, dry, log)
            if _lr.get("ok") is False:
                self._json(409, _lr); return            # refuse-if-live: not a success
            self._json(200, {"ok": True, **_lr}); return'''

# --- 3. page launch.onclick: handle refusal ----------------------------------
OLD_ONCLICK = '''  launch.onclick = async () => {
    launch.disabled = true; launch.textContent = "Launching…";
    const mode = panel.querySelector("#mode").value;
    await api("/api/launch", {method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({channel: chan.value, project: proj.value, dry: mode === "dry"})});
    launch.textContent = "Launch";
    poll();
  };'''
NEW_ONCLICK = '''  launch.onclick = async () => {
    launch.disabled = true; launch.textContent = "Launching…";
    const mode = panel.querySelector("#mode").value;
    let resp = null;
    try {
      resp = await api("/api/launch", {method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({channel: chan.value, project: proj.value, dry: mode === "dry"})});
    } catch (e) { resp = null; }
    launch.textContent = "Launch";
    if (resp && resp.ok === false && resp.already_running) {
      // refuse if a run is already live: tell the operator, don't silently re-arm into a duplicate
      const cm = document.getElementById("createmsg");
      if (cm) cm.textContent = resp.error || "A run is already live.";
      else alert(resp.error || "A run is already live.");
    }
    poll();   // poll governs the button: it stays disabled while a run is live
  };'''

OLD_VER = '''APP_VERSION = "v1.6"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
NEW_VER = '''APP_VERSION = "v1.7"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found -- run from the repo root on the laptop.")
    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) -- no changes made.")
        return
    if OLD_VER not in src:
        die("APP_VERSION v1.6 anchor not found -- apply patch_active_job_freshest.py (v1.6) first. Nothing written.")
    if "_TERMINAL_PHASES" not in src:
        die("_TERMINAL_PHASES not found -- A (v1.6) must be applied first. Nothing written.")

    edits = [
        ("launch_job guard", OLD_LAUNCH, NEW_LAUNCH),
        ("api/launch handler", OLD_HANDLER, NEW_HANDLER),
        ("launch.onclick", OLD_ONCLICK, NEW_ONCLICK),
        ("version", OLD_VER, NEW_VER),
    ]
    for label, old, _ in edits:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND -- file shape changed; nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) -- ambiguous; nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_launchguard")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    problems = []
    if MARKER not in chk: problems.append("guard marker missing")
    if "self._json(409, _lr)" not in chk: problems.append("409 handler missing")
    if "resp.already_running" not in chk: problems.append("onclick refusal handling missing")
    if 'APP_VERSION = "v1.7"' not in chk: problems.append("version not bumped")
    if problems:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed (" + "; ".join(problems) + ") -- restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile -- restored.\n{e}")

    print(f"OK patched {TARGET}  (backup {backup.name})")
    print("   launch refuses while a run is live (one live run total); page shows the refusal.")
    print()
    print("AFTER pull on the box:")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   verify v1.7 + node-check PAGE_JS_VALID. (The live 70smusic run keeps going.)")
    print("   Test: while 70smusic is animating, try Launch -> should be refused with a message,")
    print("   NOT spawn a second orchestrate. (dry-run still allowed.)")


if __name__ == "__main__":
    main()
