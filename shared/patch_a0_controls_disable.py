#!/usr/bin/env python3
"""
patch_a0_controls_disable.py — disable controls during a run instead of hiding them.

WHY
  A0 hid the Create/Launch panels (display:none) during an active run to keep the
  page clean. In practice that removes your bearings mid-review — the panels just
  vanish. The more honest "one continuous page" is: the layout never changes
  shape, controls just go live or inert. So during an active run we now DISABLE
  the Create/Launch panels in place (greyed, non-interactive) rather than hiding
  them, and dim them slightly so it's obvious they're inert.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  Replaces the body of updateControls(state): instead of toggling
  cp/lp.style.display, it disables every input/select/button/textarea inside the
  Create + Launch panels during an active run (and re-enables them otherwise),
  and sets the panels' opacity to signal inert. The Launch button stays disabled
  during a run and otherwise enables only when a project is picked (unchanged).

DISCIPLINE
  Idempotent (sentinel: `// A0b: disable-in-place`). Single anchor, verified once;
  backs up to .pre_a0disable; re-compiles and rolls back on failure. Run from the
  repo root on the LAPTOP, then commit/push, then pull + restart + node-check.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "// A0b: disable-in-place"

OLD = '''function updateControls(state) {
  const run = isActiveRun(state.phase);
  const cp = document.getElementById("createpanel");
  const lp = document.getElementById("launchpanel");
  if (cp) cp.style.display = run ? "none" : "";
  if (lp) lp.style.display = run ? "none" : "";
  const chan = document.getElementById("chan");
  const proj = document.getElementById("proj");
  const launch = document.getElementById("launch");
  if (launch) launch.disabled = run || !(chan && proj && chan.value && proj.value);
}'''

NEW = '''function updateControls(state) {
  // A0b: disable-in-place — never hide the panels (the page shape stays constant);
  // during an active run they go inert + dimmed, otherwise fully live.
  const run = isActiveRun(state.phase);
  ["createpanel", "launchpanel"].forEach(function(id) {
    const panel = document.getElementById(id);
    if (!panel) return;
    panel.style.opacity = run ? "0.45" : "1";
    panel.querySelectorAll("input,select,button,textarea").forEach(function(elm) {
      elm.disabled = run;
    });
  });
  // Launch stays disabled during a run, and otherwise only enables once a
  // project is picked (overrides the blanket enable above for this one button).
  const chan = document.getElementById("chan");
  const proj = document.getElementById("proj");
  const launch = document.getElementById("launch");
  if (launch) launch.disabled = run || !(chan && proj && chan.value && proj.value);
}'''


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

    n = src.count(OLD)
    if n == 0:
        die("updateControls anchor NOT FOUND — confirm the A0 patch is applied and the box is in sync; nothing written.")
    if n > 1:
        die(f"updateControls anchor found {n}x (expected 1) — ambiguous; nothing written.")

    new = src.replace(OLD, NEW)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_a0disable")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    check = TARGET.read_text()
    if MARKER not in check:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed — restored from backup.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile — restored from backup.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   updateControls now disables (dims) the panels during a run instead of hiding them")
    print()
    print("AFTER you pull on the box, restart + node-check before trusting it:")
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
