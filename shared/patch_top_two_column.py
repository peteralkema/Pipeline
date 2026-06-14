#!/usr/bin/env python3
"""
patch_top_two_column.py -- two-column top: controls left, FINAL VIDEO panel right (v0.8).

WHY
  The FINAL VIDEO panel (v0.7) rendered full-width BELOW the controls. The wireframe
  puts it top-RIGHT, filling the dead space beside the dropdowns -> the page reads as
  a U: initiate top-left, storyboard along the bottom, final video + upload top-right.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  1. ensureShell: after the strip (full-width), build a two-column flex row #topgrid:
       - #topleft  (flex 1)     <- createpanel + launchpanel appended here
       - #toppanel (flex 1.15)  <- persistent right slot for the FINAL VIDEO panel
     flex-wrap so it stacks (not crushes) on narrow windows. Gatebar + storyboard stay
     full-width below.
  2. renderDonePanel: target #toppanel (not #app/insertBefore storyboard). When empty,
     #toppanel shows a faint placeholder so the space never looks broken.
  3. APP_VERSION -> v0.8.

  LAYOUT NOTE: this restructures the persistent shell every phase renders into, so eyeball
  idle / running / gate / done after it lands -- node-check can't validate layout.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `id="topgrid"`). Anchors verified once; .pre_twocol
  backup; py_compile + JS checks; rollback on failure. Requires v0.7.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = 'id="topgrid"'

# --- 1. ensureShell: wrap the two control panels in a two-column top row -----
# The createpanel is appended at `shell.appendChild(create);` and the launchpanel at
# `shell.appendChild(panel);`. We replace both appends so they go into #topleft, and
# build #topgrid (with #topleft + #toppanel) right after the strip's reset wiring.

OLD_CREATE_APPEND = '''  shell.appendChild(create);'''
NEW_CREATE_APPEND = '''  document.getElementById("topleft").appendChild(create);'''

OLD_PANEL_APPEND = '''  shell.appendChild(panel);

  const gatebar = document.createElement("div");'''
NEW_PANEL_APPEND = '''  document.getElementById("topleft").appendChild(panel);

  const gatebar = document.createElement("div");'''

# Build #topgrid right after the strip + reset wiring (anchor on the reset wiring line).
OLD_STRIP_WIRE = '''  const resetbtn = strip.querySelector("#resetbtn");
  if (resetbtn) resetbtn.onclick = resetAll;'''
NEW_STRIP_WIRE = '''  const resetbtn = strip.querySelector("#resetbtn");
  if (resetbtn) resetbtn.onclick = resetAll;

  // v0.8: two-column top -- controls left, FINAL VIDEO panel right (the U layout).
  const topgrid = el(`<div id="topgrid" style="display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start;">
    <div id="topleft" style="flex:1 1 360px;min-width:300px;"></div>
    <div id="toppanel" style="flex:1.15 1 380px;min-width:320px;"></div>
  </div>`);
  shell.appendChild(topgrid);
  renderTopPlaceholder();'''

# --- 2. renderDonePanel: target #toppanel; add a placeholder for the empty slot ---
OLD_INSERT = '''  // insert ABOVE the storyboard (or at the end of #app if no storyboard yet)
  const sb = document.getElementById("storyboard");
  if (sb) { app.insertBefore(panel, sb); } else { app.appendChild(panel); }
}'''
NEW_INSERT = '''  // v0.8: render into the top-right slot (fills the dead space beside the controls)
  const slot = document.getElementById("toppanel");
  if (slot) { slot.innerHTML = ""; slot.appendChild(panel); }
}

function renderTopPlaceholder() {
  const slot = document.getElementById("toppanel");
  if (!slot) return;
  if (document.getElementById("donepanel")) return;  // a real panel is showing -> leave it
  slot.innerHTML =
    '<div class="panel" style="border:1px dashed #32323e;color:#8a8a99;text-align:center;' +
      'padding:28px 18px;">FINAL VIDEO appears here when a run completes.</div>';
}'''

# renderDonePanel currently early-returns on no video via `app`; it references `app`.
# Make sure the no-video path restores the placeholder instead of leaving a stale panel.
OLD_NOVIDEO = '''  if (!meta || !meta.has_video) return;   // no assembled video -> no panel'''
NEW_NOVIDEO = '''  if (!meta || !meta.has_video) { renderTopPlaceholder(); return; }   // no video -> placeholder'''

# renderDonePanel opens with `const app = document.getElementById("app"); if (!app) return;`
# -- that app ref is now unused for insertion; keep it harmless but switch the guard to #toppanel.
OLD_APPGUARD = '''  removeDonePanel();
  const app = document.getElementById("app");
  if (!app) return;'''
NEW_APPGUARD = '''  removeDonePanel();
  const slotEl = document.getElementById("toppanel");
  if (!slotEl) return;'''

# removeDonePanel should restore the placeholder when it strips the panel.
OLD_REMOVE = '''function removeDonePanel() {
  const e = document.getElementById("donepanel"); if (e) e.remove();
}'''
NEW_REMOVE = '''function removeDonePanel() {
  const e = document.getElementById("donepanel"); if (e) e.remove();
  if (typeof renderTopPlaceholder === "function") renderTopPlaceholder();
}'''

# --- 3. version bump ---------------------------------------------------------
OLD_VER = '''APP_VERSION = "v0.7"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
NEW_VER = '''APP_VERSION = "v0.8"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


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
        die("APP_VERSION v0.7 anchor not found -- apply patch_final_video_panel.py (v0.7) first. Nothing written.")

    edits = [
        ("strip wire / topgrid", OLD_STRIP_WIRE, NEW_STRIP_WIRE),
        ("create append",        OLD_CREATE_APPEND, NEW_CREATE_APPEND),
        ("panel append",         OLD_PANEL_APPEND, NEW_PANEL_APPEND),
        ("app guard",            OLD_APPGUARD, NEW_APPGUARD),
        ("no-video path",        OLD_NOVIDEO, NEW_NOVIDEO),
        ("insert -> toppanel",   OLD_INSERT, NEW_INSERT),
        ("removeDonePanel",      OLD_REMOVE, NEW_REMOVE),
        ("version bump",         OLD_VER, NEW_VER),
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

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_twocol")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    problems = []
    if MARKER not in chk: problems.append("topgrid missing")
    if 'getElementById("topleft").appendChild(create)' not in chk: problems.append("create not in topleft")
    if 'getElementById("topleft").appendChild(panel)' not in chk: problems.append("launch not in topleft")
    if "renderTopPlaceholder" not in chk: problems.append("placeholder fn missing")
    if 'slot.appendChild(panel)' not in chk: problems.append("donepanel not retargeted")
    if 'APP_VERSION = "v0.8"' not in chk: problems.append("version not bumped")
    if problems:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed (" + "; ".join(problems) + ") -- restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile -- restored.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   top is now two columns: controls left, FINAL VIDEO panel right (#toppanel)")
    print()
    print("AFTER pull on the box: restart, verify v0.8, node-check:")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   curl -s \"http://127.0.0.1:8002/api/state?key=fh2026\" | python3 -c \"import sys,json;d=json.load(sys.stdin);print(d.get('version'),d.get('sha'))\"")
    print("   git rev-parse --short HEAD   # must match; version must read v0.8")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")
    print()
    print("   THEN eyeball all four states: idle, running, gate_stills, done.")


if __name__ == "__main__":
    main()
