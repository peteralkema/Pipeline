#!/usr/bin/env python3
"""
patch_topgrid_tuck.py -- tuck the two-column top in neatly (v0.9).

WHY
  v0.8 put the FINAL VIDEO panel on the right, but #topgrid had no max-width, so on a
  wide monitor the two 720px-capped columns flung to opposite edges with a canyon of
  dead space between them. Cap the row and tighten the columns so they sit side by side.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  - #topgrid: add max-width 1500px so the row doesn't span the whole screen (it already
    sits left-aligned inside #app).
  - #topleft: flex 0 1 420px (sized to the controls, doesn't grow to fling).
  - #toppanel: flex 1 1 560px, max-width 760px (takes the remaining share, capped so the
    video doesn't balloon).
  - APP_VERSION -> v0.9.

  Pure CSS in the #topgrid template; no structure change. Eyeball done + idle after.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `max-width:1500px`). Anchor verified once;
  .pre_tuck backup; py_compile; rollback on failure. Requires v0.8.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "max-width:1500px"

OLD_GRID = '''  const topgrid = el(`<div id="topgrid" style="display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start;">
    <div id="topleft" style="flex:1 1 360px;min-width:300px;"></div>
    <div id="toppanel" style="flex:1.15 1 380px;min-width:320px;"></div>
  </div>`);'''
NEW_GRID = '''  const topgrid = el(`<div id="topgrid" style="display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start;max-width:1500px;">
    <div id="topleft" style="flex:0 1 420px;min-width:300px;"></div>
    <div id="toppanel" style="flex:1 1 560px;min-width:320px;max-width:760px;"></div>
  </div>`);'''

OLD_VER = '''APP_VERSION = "v0.8"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
NEW_VER = '''APP_VERSION = "v0.9"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


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
        die("APP_VERSION v0.8 anchor not found -- apply patch_top_two_column.py (v0.8) first. Nothing written.")

    for label, old in [("topgrid", OLD_GRID), ("version", OLD_VER)]:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND -- file shape changed; nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) -- ambiguous; nothing written.")

    new = src.replace(OLD_GRID, NEW_GRID).replace(OLD_VER, NEW_VER)

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_tuck")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    if MARKER not in chk or 'APP_VERSION = "v0.9"' not in chk:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed -- restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile -- restored.\n{e}")

    print(f"OK patched {TARGET}  (backup {backup.name})")
    print("   #topgrid capped at 1500px; columns tightened so they sit side by side")
    print()
    print("AFTER pull on the box:")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   curl -s \"http://127.0.0.1:8002/api/state?key=fh2026\" | python3 -c \"import sys,json;d=json.load(sys.stdin);print(d.get('version'),d.get('sha'))\"")
    print("   git rev-parse --short HEAD")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")
    print("   # then hard-refresh; controls + panel should tuck side by side, no canyon.")


if __name__ == "__main__":
    main()
