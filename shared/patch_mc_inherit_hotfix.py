#!/usr/bin/env python3
"""
patch_mc_inherit_hotfix.py — v2.3: fix the page-killing apostrophe in the
inherit button tooltip.

THE BUG: patch_mc_inherit_toggle wrote the tooltip text "previous beat\\'s
atom" into pipeline_server.py. The escape survives the patch layer, but the
page's JS lives inside a PYTHON string in the server source — when the server
parses its own file, \\' collapses to a bare apostrophe, which terminates the
single-quoted JS string mid-tooltip. One JS syntax error kills the whole page
script: static header renders, then "loading..." forever. py_compile cannot
catch it — legal Python, broken JavaScript.

THE FIX: apostrophe-free tooltip. DOCTRINE: no apostrophes in JS string
literals that travel through a Python string layer — two escape decoders, one
character, dead page.

Run from the repo root:  python3 shared/patch_mc_inherit_hotfix.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_inh_hotfix")

# raw strings: the broken anchor really contains a backslash before the quote
OLD = r"""    '<button class="inhbtn" title="Beat plays the unused tail of the previous beat\'s atom (free; same-scene continuation; derived at render, falls back to Ken Burns if nothing is left)" ' +"""
NEW = r"""    '<button class="inhbtn" title="Beat plays the unused tail of the previous clip (free; same-scene continuation; derived at render, falls back to Ken Burns if nothing is left)" ' +"""

VOLD = '''APP_VERSION = "v2.2"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
VNEW = '''APP_VERSION = "v2.3"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if OLD not in src and NEW in src:
        print("already applied — no-op.")
        return

    for i, old in enumerate((OLD, VOLD), 1):
        n = src.count(old)
        if n != 1:
            sys.exit(f"!! anchor {i} matched {n} times (need exactly 1) — file drifted, NOT patched.")

    patched = src.replace(OLD, NEW).replace(VOLD, VNEW)

    if "\\'" in patched:
        sys.exit("!! another escaped apostrophe remains in the file — dump it before shipping.")

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
    print("  tooltip apostrophe removed — served JS valid again; APP_VERSION v2.2 -> v2.3")


if __name__ == "__main__":
    main()
