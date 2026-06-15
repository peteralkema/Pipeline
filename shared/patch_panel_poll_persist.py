#!/usr/bin/env python3
"""
patch_panel_poll_persist.py -- stop the poll from wiping the selected project's panel (v1.5).

WHY (the flicker: panel shows on select, then vanishes ~2.5s later)
  maybeUpdateBody() runs every poll. For a SELECTED-but-IDLE finished project, state.phase
  is not "done" (there is no active job), so its
      if (state.phase === "done") { renderDonePanel(...) } else { removeDonePanel(); }
  took the else branch and removed the panel that proj.onchange (v1.3) had just rendered.
  Selection drew it; the next poll wiped it. Hence: appears briefly, then disappears.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  Replace that line so the poll is ARTIFACT-aware, matching proj.onchange: always call
  renderDonePanel(t.ch, t.pr). renderDonePanel already fetches /api/meta and shows the video
  iff has_video, else falls to the placeholder -- so a finished project (live-done OR
  idle-selected) keeps its panel across polls, and a project with no video shows the
  placeholder. No more remove-on-every-idle-poll.
  APP_VERSION -> v1.5.

  (removeDonePanel still exists and is still called from the no-selection branch at the top
  of maybeUpdateBody, so leaving base state correctly clears the panel.)

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `panel persists across polls`). Anchor verified once;
  .pre_pollpersist backup; py_compile; rollback on failure. Requires v1.4.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "panel persists across polls"

OLD = '''  if (state.phase === "done") { renderDonePanel(t.ch, t.pr); } else { removeDonePanel(); }
  renderStoryboard(t.ch, t.pr);'''
NEW = '''  renderDonePanel(t.ch, t.pr);  // panel persists across polls: artifact-aware (shows video iff has_video, else placeholder) -- no more flicker-then-wipe
  renderStoryboard(t.ch, t.pr);'''

OLD_VER = '''APP_VERSION = "v1.4"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
NEW_VER = '''APP_VERSION = "v1.5"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


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
        die("APP_VERSION v1.4 anchor not found -- apply patch_api_key_querystring.py (v1.4) first. Nothing written.")

    for label, old in [("maybeUpdateBody done/remove line", OLD), ("version", OLD_VER)]:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND -- file shape changed; nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) -- ambiguous; nothing written.")

    new = src.replace(OLD, NEW).replace(OLD_VER, NEW_VER)

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_pollpersist")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    if MARKER not in chk or 'APP_VERSION = "v1.5"' not in chk:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed -- restored.")
    # guard: the no-selection branch's removeDonePanel must still exist (base-state clear)
    if "if (!t.ch || !t.pr) { clearStoryboard(); removeDonePanel();" not in chk:
        shutil.copy2(backup, TARGET)
        die("no-selection removeDonePanel guard missing post-write -- restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile -- restored.\n{e}")

    print(f"OK patched {TARGET}  (backup {backup.name})")
    print("   the poll no longer wipes the selected project's FINAL VIDEO panel.")
    print()
    print("AFTER pull on the box:")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   verify v1.5 + node-check PAGE_JS_VALID, HARD-REFRESH (Cmd-Shift-R), then:")
    print("   Reset -> pick esther--1 -> panel appears AND stays (watch through a few poll ticks).")


if __name__ == "__main__":
    main()
