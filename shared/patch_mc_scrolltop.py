#!/usr/bin/env python3
"""
patch_mc_scrolltop.py — v2.8: fixed scroll-to-top button, bottom-right.
A 185-beat storyboard makes the scroll-back a hand-cramp; one tap returns to
the gate bar. Pure template patch, no engine touch, no endpoints.

2 anchored edits in shared/mission_control/pipeline_server.py (post-v2.7):
  1. fixed-position button after the page h1
  2. APP_VERSION v2.7 -> v2.8

Run from the repo root:  python3 shared/patch_mc_scrolltop.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_scrolltop")

MARKER = "scrolltop"

EDITS = [
    (
        '''<h1>AI FILM DIRECTOR STORYBOARD AND CONTROL PANEL <span style="font-size:12px;font-weight:400;color:#8a8a99;letter-spacing:0;">@@VERSTAMP@@</span></h1>''',

        '''<h1>AI FILM DIRECTOR STORYBOARD AND CONTROL PANEL <span style="font-size:12px;font-weight:400;color:#8a8a99;letter-spacing:0;">@@VERSTAMP@@</span></h1>
<button id="scrolltop" onclick="window.scrollTo({top:0,behavior:'smooth'})" title="Back to top" style="position:fixed;bottom:24px;right:24px;z-index:9999;background:#2a2a36;color:#e8e6e3;border:1px solid #32323e;border-radius:8px;padding:10px 14px;cursor:pointer;font:13px ui-monospace,monospace;">&#8679; Top</button>''',
    ),
    (
        '''APP_VERSION = "v2.7"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v2.8"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (scrolltop present) — no-op.")
        return

    if 'APP_VERSION = "v2.7"' not in src:
        sys.exit("!! prerequisite missing: v2.7 — anchors target that text.")

    for i, (old, _new) in enumerate(EDITS, 1):
        n = src.count(old)
        if n != 1:
            sys.exit(f"!! anchor {i} matched {n} times (need exactly 1) — file drifted, NOT patched.\n"
                     f"   anchor starts: {old.splitlines()[0]!r}")

    patched = src
    for old, new in EDITS:
        patched = patched.replace(old, new)

    if "\\'" in patched:
        sys.exit("!! escaped apostrophe found — refusing (JS double-decode doctrine).")

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
    print("  fixed scroll-to-top button, bottom-right; APP_VERSION v2.7 -> v2.8")


if __name__ == "__main__":
    main()
