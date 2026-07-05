#!/usr/bin/env python3
"""
patch_mc_layout_v35.py — v3.5: finish the CONTENT | PACKAGING layout. The
applied v3.4 was the pre-amendment version (stale Downloads copy), leaving two
gaps this patch closes against the on-disk text:

  1. topgrid still capped at 1500px — the outermost width bottleneck; lifted,
     the two boxes now take the full viewport minus the left column
  2. Title/Description/Tags still in PACKAGING — moved under the video in
     CONTENT, so a rendered thumbnail never pushes them down; PACKAGING is
     pure thumbnail (preview + generate/source/upload)

4 anchored edits in shared/mission_control/pipeline_server.py (post-applied-v3.4):
  1. topgrid max-width removed
  2. T/D/T inserted into contentbox after the buttons row
  3. T/D/T removed from packagingbox
  4. APP_VERSION v3.4 -> v3.5

If the on-disk text differs from expectation, anchors fail loudly and nothing
is written.

Run from the repo root:  python3 shared/patch_mc_layout_v35.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_layout35")

TDT = """      '<div style="margin-top:10px;">' +
      '<label>Title</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
        'background:#1c1c26;padding:8px 10px;margin-bottom:8px;">' + esc(meta.title) + '</div>' +
      '<label>Description</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
        'background:#1c1c26;padding:8px 10px;margin-bottom:8px;white-space:pre-wrap;">' + esc(meta.description) + '</div>' +
      '<label>Tags</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
        'background:#1c1c26;padding:8px 10px;">' + esc(meta.tags) + '</div>' +
      '</div>' +"""

EDITS = [
    # 1. lift the outermost width cap
    (
        '''<div id="topgrid" style="display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start;max-width:1500px;">''',
        '''<div id="topgrid" style="display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start;">''',
    ),
    # 2. T/D/T into CONTENT, after the buttons row
    (
        """        '<span id="reassemblemsg" style="color:#8a8a99;font-size:12px;"></span></div>' +
    '</div>' +
    '<div id="packagingbox" style="border:1px solid #32323e;border-radius:8px;background:#161620;padding:12px;">' +""",

        """        '<span id="reassemblemsg" style="color:#8a8a99;font-size:12px;"></span></div>' +
""" + TDT + """
    '</div>' +
    '<div id="packagingbox" style="border:1px solid #32323e;border-radius:8px;background:#161620;padding:12px;">' +""",
    ),
    # 3. T/D/T out of PACKAGING
    (
        """      '<span id="thumbmsg" style="color:#8a8a99;font-size:12px;"></span>' +
""" + TDT + """
    '</div>' +""",

        """      '<span id="thumbmsg" style="color:#8a8a99;font-size:12px;"></span>' +
    '</div>' +""",
    ),
    # 4. version bump
    (
        '''APP_VERSION = "v3.4"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v3.5"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if 'APP_VERSION = "v3.5"' in src:
        print("already applied (v3.5 present) — no-op.")
        return

    if "packagingbox" not in src or 'APP_VERSION = "v3.4"' not in src:
        sys.exit("!! prerequisite missing: applied v3.4 — anchors target that text.")

    for i, (old, _new) in enumerate(EDITS, 1):
        n = src.count(old)
        if n != 1:
            sys.exit(f"!! anchor {i} matched {n} times (need exactly 1) — on-disk text differs, NOT patched.\n"
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
    print("  topgrid cap lifted — boxes take the full viewport width")
    print("  Title/Description/Tags now live with the video in CONTENT")
    print("  APP_VERSION v3.4 -> v3.5")


if __name__ == "__main__":
    main()
