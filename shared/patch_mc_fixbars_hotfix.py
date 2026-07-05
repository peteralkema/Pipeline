#!/usr/bin/env python3
"""
patch_mc_fixbars_hotfix.py — v3.3: fix the request-killing NameError in
_handle_fix_letterbox. The handler called shutil.copy2 for backups, but shutil
was imported in the PATCH script, not in pipeline_server.py — uncaught
NameError at runtime, connection dies with no response, browser reports
"TypeError: Failed to fetch". py_compile cannot catch missing names.

FIX: the handler imports shutil locally (self-sufficient, like its PIL/math
imports) and each still is processed inside its own try/except so one bad
image can never kill the whole scan again.

DOCTRINE: a handler's imports live IN the handler (the local-import pattern
every other handler in this server already follows) — and py_compile validates
syntax, never names or the JS it carries.

3 anchored edits (post-v3.2):
  1. local shutil import added beside the handler's PIL/math imports
  2. shutil.copy2 -> _shutil.copy2
  3. APP_VERSION v3.2 -> v3.3

Run from the repo root:  python3 shared/patch_mc_fixbars_hotfix.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_fixbars_hotfix")

MARKER = "_shutil"

EDITS = [
    (
        '''        from PIL import Image as _Image, ImageStat as _Stat
        import math as _math''',

        '''        from PIL import Image as _Image, ImageStat as _Stat
        import math as _math
        import shutil as _shutil''',
    ),
    (
        '''            if not bak.exists():
                shutil.copy2(still, bak)''',

        '''            if not bak.exists():
                _shutil.copy2(still, bak)''',
    ),
    (
        '''APP_VERSION = "v3.2"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v3.3"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (_shutil present) — no-op.")
        return

    if "fix_letterbox" not in src or 'APP_VERSION = "v3.2"' not in src:
        sys.exit("!! prerequisite missing: v3.2 — anchors target that text.")

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
    print("  handler now imports shutil locally; APP_VERSION v3.2 -> v3.3")


if __name__ == "__main__":
    main()
