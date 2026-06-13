#!/usr/bin/env python3
"""
patch_reloadclip_inplace.py — show a once-off clip in place (no refresh needed).

WHY
  Rendering a clip showed "clip rendered — refresh to view", and refreshing then
  dropped you back to base state (selection is memory-only). Root cause: reloadClip
  used `cell.parentElement` as "the 5-col grid", but cell is the .motioncell, so its
  parent is the MOTION COLUMN, not the grid — so the video lookup searched the wrong
  subtree and always failed. Also, the first time a beat gets a clip there is no
  <video> element to update (only the "not rendered" placeholder).

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  Rewrites reloadClip() in bindAnimateButtons:
    - correct grid reference: cell.parentElement.parentElement (matches reloadStill)
    - if a <video> exists -> cache-bust + reload it in place
    - if not (first clip for this beat) -> replace the placeholder in the clip column
      with a fresh <video> pointing at the new clip
  Result: once-off clips appear in place immediately; "refresh to view" no longer
  fires, so you never lose your project selection to a refresh.

DISCIPLINE
  Idempotent (sentinel: `grid.lastElementChild`). Single anchor verified once;
  backs up to .pre_reloadclip; re-compiles + rolls back on failure. Run from the
  repo root on the LAPTOP, then commit/push, then pull + restart + node-check on box.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "grid.lastElementChild"

OLD = '''    function reloadClip() {
      const n3 = String(shot).padStart(3, "0");
      const grid = cell.parentElement;  // the 5-col grid
      const vid = grid.querySelector('video[src*="shot_' + n3 + '.mp4"]');
      if (vid) {
        const base = vid.src.split("&_t=")[0];
        vid.src = base + "&_t=" + Date.now(); vid.load();
        return true;
      }
      return false;
    }'''

NEW = '''    function reloadClip() {
      const n3 = String(shot).padStart(3, "0");
      const grid = cell.parentElement.parentElement;  // the 5-col grid (cell is inside the motion column)
      const q = "?channel=" + encodeURIComponent(CH) + "&project=" + encodeURIComponent(PR) + "&key=" + KEY;
      const src = "/clips/shot_" + n3 + ".mp4" + q + "&_t=" + Date.now();
      const vid = grid.querySelector('video[src*="shot_' + n3 + '.mp4"]');
      if (vid) {
        vid.src = src; vid.load();
        return true;
      }
      const clipCol = grid.lastElementChild;  // column 5 = the clip cell
      if (clipCol) {
        const v = document.createElement("video");
        v.src = src; v.muted = true; v.loop = true; v.autoplay = true;
        v.setAttribute("playsinline", "");
        v.style.cssText = "width:100%;max-width:1100px;border-radius:8px;background:#000;display:block;";
        const ph = clipCol.firstElementChild;
        if (ph) { clipCol.insertBefore(v, ph); ph.remove(); }
        else { clipCol.insertBefore(v, clipCol.firstChild); }
        return true;
      }
      return false;
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
        die("reloadClip anchor NOT FOUND — file shape changed; nothing written.")
    if n > 1:
        die(f"reloadClip anchor found {n}x (expected 1) — ambiguous; nothing written.")

    new = src.replace(OLD, NEW)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_reloadclip")
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
    print("   reloadClip now finds the grid correctly + creates the video on first render")
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
