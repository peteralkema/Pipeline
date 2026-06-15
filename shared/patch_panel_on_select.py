#!/usr/bin/env python3
"""
patch_panel_on_select.py -- show the FINAL VIDEO panel on project selection (v1.3).

WHY
  After Reset, picking a channel + project that already has a finished video did NOT show
  the FINAL VIDEO panel. The panel only rendered on a LIVE job hitting phase==done
  (line ~883). Selecting an existing project starts no job, so renderDonePanel never fired
  even though final_video.mp4 is on disk -> panel stayed empty.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  In proj.onchange, right after renderStoryboard(ch, pr), also call renderDonePanel(ch, pr).
  renderDonePanel already fetches /api/meta and shows the video if has_video, else falls to
  the placeholder -- so this needs no extra gating: pick a finished project -> its video
  shows; pick one without -> placeholder. (Reset still clears, because Reset drops the
  selection; this only fires on an actual project pick.)
  APP_VERSION -> v1.3.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `panel on select`). Anchors verified once;
  .pre_panelselect backup; py_compile; rollback on failure. Requires v1.2.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "panel on select"

OLD = '''  proj.onchange = () => {
    if (chan.value && proj.value) {
      window.__SEL_VIEW = chan.value + "/" + proj.value;
      window.__BODY_KEY = chan.value + "/" + proj.value + "|";  // matches idle poll key -> no double render
      setUrlProject(chan.value, proj.value);
      renderStoryboard(chan.value, proj.value);'''
NEW = '''  proj.onchange = () => {
    if (chan.value && proj.value) {
      window.__SEL_VIEW = chan.value + "/" + proj.value;
      window.__BODY_KEY = chan.value + "/" + proj.value + "|";  // matches idle poll key -> no double render
      setUrlProject(chan.value, proj.value);
      renderStoryboard(chan.value, proj.value);
      renderDonePanel(chan.value, proj.value);  // panel on select: show final video if one exists (else placeholder)'''

OLD_VER = '''APP_VERSION = "v1.2"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
NEW_VER = '''APP_VERSION = "v1.3"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


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
        die("APP_VERSION v1.2 anchor not found -- apply patch_reassemble_aligned.py (v1.2) first. Nothing written.")

    for label, old in [("proj.onchange", OLD), ("version", OLD_VER)]:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND -- file shape changed; nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) -- ambiguous; nothing written.")

    new = src.replace(OLD, NEW).replace(OLD_VER, NEW_VER)

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_panelselect")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    if MARKER not in chk or 'APP_VERSION = "v1.3"' not in chk:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed -- restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile -- restored.\n{e}")

    print(f"OK patched {TARGET}  (backup {backup.name})")
    print("   picking a channel+project now shows its FINAL VIDEO panel if a video exists.")
    print()
    print("AFTER pull on the box:")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   then verify v1.3 + node-check PAGE_JS_VALID, hard-refresh, and:")
    print("   Reset -> pick a finished project (e.g. esther--1) -> the video panel should appear.")


if __name__ == "__main__":
    main()
