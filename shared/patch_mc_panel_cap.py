#!/usr/bin/env python3
"""
patch_mc_panel_cap.py — v3.6: the last width cap. The .panel CSS class (line
~651) carries max-width:720px, and #donepanel wears that class — so removing
the inline cap in v3.4 handed control straight back to the class rule. Inline
beats class: one override on the done panel, the class stays intact for the
strip and left-column panels that legitimately use it.

2 anchored edits in shared/mission_control/pipeline_server.py (post-v3.5):
  1. donepanel cssText gains max-width:none
  2. APP_VERSION v3.5 -> v3.6

Run from the repo root:  python3 shared/patch_mc_panel_cap.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_panelcap")

EDITS = [
    (
        '''  panel.style.cssText = "border:1px solid #d4a017;";''',
        '''  panel.style.cssText = "border:1px solid #d4a017;max-width:none;";''',
    ),
    (
        '''APP_VERSION = "v3.5"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v3.6"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if "max-width:none" in src:
        print("already applied (max-width:none present) — no-op.")
        return

    if 'APP_VERSION = "v3.5"' not in src:
        sys.exit("!! prerequisite missing: v3.5 — anchors target that text.")

    for i, (old, _new) in enumerate(EDITS, 1):
        n = src.count(old)
        if n != 1:
            sys.exit(f"!! anchor {i} matched {n} times (need exactly 1) — file drifted, NOT patched.\n"
                     f"   anchor starts: {old.splitlines()[0]!r}")

    patched = src
    for old, new in EDITS:
        patched = patched.replace(old, new)

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(patched)
        tmp = tf.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        sys.exit(f"!! patched text does not compile — target NOT modified.\n{e}")
    finally:
        Path(tmp).unlink(missing_ok=True)

    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(patched, encoding="utf-8")
    print(f"patched {TARGET.name} (backup: {BACKUP.name})")
    print("  donepanel escapes the .panel 720px class cap (inline max-width:none)")
    print("  APP_VERSION v3.5 -> v3.6")


if __name__ == "__main__":
    main()
