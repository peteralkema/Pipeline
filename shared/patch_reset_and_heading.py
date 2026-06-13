#!/usr/bin/env python3
"""
patch_reset_and_heading.py — add a Reset button + rename the heading.

WHY
  The only controls are per-still/per-clip plus Generate Clips / Stop. There's no
  way to get back to the base state (no project, no assets) short of an ssh rm.
  This adds a Reset button that does exactly that. Plus a heading rename.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  Backend:
    - _handle_reset(): delete the active job's .json + .log (mirrors the manual
      rm of .mc_jobs/<id>.{json,log}) so build_state() returns idle. A detached
      render keeps running server-side; this only drops the page's handle on it.
    - POST /api/reset.
  Frontend:
    - a Reset button in the (always-visible) status strip. resetAll(): if a render
      is actively in progress it confirms first (the render keeps running on the
      server); then clears the job, empties __SEL_VIEW + body, resets the channel/
      project dropdowns, and polls back to idle base.
    - heading "MISSION CONTROL" -> "AI FILM DIRECTOR STORYBOARD AND CONTROL PANEL"
      (and the browser tab title to match).

DISCIPLINE
  Idempotent (sentinel: `function resetAll`). Six anchors, each verified once;
  backs up to .pre_reset; re-compiles + rolls back on failure. Run from the repo
  root on the LAPTOP, then commit/push, then pull + restart + node-check on the box.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "function resetAll"

EDITS = []

# 1. Heading <h1>
EDITS.append((
    "h1 heading",
    "<h1>MISSION CONTROL</h1>",
    "<h1>AI FILM DIRECTOR STORYBOARD AND CONTROL PANEL</h1>",
))

# 2. Browser tab title
EDITS.append((
    "tab title",
    "<title>Mission Control</title>",
    "<title>AI Film Director Storyboard and Control Panel</title>",
))

# 3. Strip: add a Reset button + wire it
EDITS.append((
    "status strip",
    '''  const strip = el(`<div class="panel" id="strip" style="border-left:4px solid #8a8a99;">
    <div id="stripmain" class="phase" style="font-size:14px;"></div>
    <div id="stripsub" class="phase" style="margin-top:4px;"></div>
  </div>`);
  shell.appendChild(strip);''',
    '''  const strip = el(`<div class="panel" id="strip" style="border-left:4px solid #8a8a99;display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
    <div style="flex:1;min-width:0;">
      <div id="stripmain" class="phase" style="font-size:14px;"></div>
      <div id="stripsub" class="phase" style="margin-top:4px;"></div>
    </div>
    <button id="resetbtn" class="secondary" style="margin-top:0;white-space:nowrap;">Reset</button>
  </div>`);
  shell.appendChild(strip);
  const resetbtn = strip.querySelector("#resetbtn");
  if (resetbtn) resetbtn.onclick = resetAll;''',
))

# 4. resetAll() — inserted before gate()
EDITS.append((
    "resetAll fn",
    "async function gate(decision) {",
    '''async function resetAll() {
  let st;
  try { st = await api("/api/state"); } catch (e) { st = {}; }
  if (isActiveRun(st.phase)) {
    if (!confirm("A render is in progress. Reset clears it from the page (the render keeps running on the server). Continue?")) return;
  }
  try {
    await api("/api/reset", {method: "POST",
      headers: {"Content-Type": "application/json"}, body: "{}"});
  } catch (e) {}
  window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__";
  clearStoryboard();
  const chan = document.getElementById("chan");
  const proj = document.getElementById("proj");
  const launch = document.getElementById("launch");
  if (chan) chan.value = "";
  if (proj) proj.innerHTML = "<option>\\u2014</option>";
  if (launch) launch.disabled = true;
  poll();
}
async function gate(decision) {''',
))

# 5. Backend _handle_reset — inserted before _handle_animate
EDITS.append((
    "backend handler",
    "    def _handle_animate(self, body):",
    '''    def _handle_reset(self):
        """Clear the active job record (+log) so the page returns to idle base.
        Mirrors the manual rm of .mc_jobs/<id>.{json,log}. A detached render keeps
        running server-side; this only drops the page's handle on it."""
        jid = active_job_id()
        if not jid:
            self._json(200, {"ok": True, "cleared": None}); return
        d = jobs_dir(_REPO)
        removed = []
        for ext in (".json", ".log"):
            f = d / f"{jid}{ext}"
            try:
                if f.exists():
                    f.unlink(); removed.append(f.name)
            except Exception:
                pass
        self._json(200, {"ok": True, "cleared": jid, "removed": removed}); return

    def _handle_animate(self, body):''',
))

# 6. POST route for /api/reset
EDITS.append((
    "reset route",
    '''        if path == "/api/animate":
            self._handle_animate(body); return''',
    '''        if path == "/api/animate":
            self._handle_animate(body); return
        if path == "/api/reset":
            self._handle_reset(); return''',
))


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found — run this from the repo root on the laptop.")

    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) — no changes made.")
        return

    for label, old, _ in EDITS:
        n = src.count(old)
        if n == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written. "
                f"(Confirm A0 + the tiered patches are applied and the box is in sync.)")
        if n > 1:
            die(f"anchor for {label} found {n}x (expected 1) — ambiguous; nothing written.")

    new = src
    for _, old, repl in EDITS:
        new = new.replace(old, repl)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_reset")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    check = TARGET.read_text()
    problems = []
    if MARKER not in check:
        problems.append("resetAll missing")
    if "def _handle_reset" not in check:
        problems.append("_handle_reset missing")
    if '"/api/reset"' not in check:
        problems.append("reset route missing")
    if "AI FILM DIRECTOR STORYBOARD AND CONTROL PANEL" not in check:
        problems.append("heading missing")
    if problems:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed (" + "; ".join(problems) + ") — restored from backup.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile — restored from backup.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   1) Reset button + /api/reset")
    print("   2) heading -> AI FILM DIRECTOR STORYBOARD AND CONTROL PANEL")
    print()
    print("AFTER you pull on the box, restart + node-check:")
    print("   systemctl --user restart mission-control.service")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   print(\"script blocks:\", len(b))")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")


if __name__ == "__main__":
    main()
