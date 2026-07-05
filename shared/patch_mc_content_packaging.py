#!/usr/bin/env python3
"""
patch_mc_content_packaging.py — v3.4: the FINAL VIDEO panel becomes two equal
boxes — CONTENT (video, Download, Re-assemble, Analyse + fix stills) and
PACKAGING (thumbnail preview promoted to the top, generate/source/upload
controls, Title, Description, Tags) — with Upload to YouTube Studio spanning
full width beneath both. Equal size, equal focus: CTR lives in the right box.

Every element id is unchanged, so all existing wiring lands in the right box
untouched: fixbars appends to the reassemble row (CONTENT); the v3.0
source-mode rows insert before thumbmsg (PACKAGING).

4 anchored edits in shared/mission_control/pipeline_server.py (post-v3.3):
  1. #toppanel slot: 760px cap lifted (the black space, cause one)
  2. donepanel: 720px cap lifted (cause two)
  3. panel innerHTML rebuilt as the CONTENT | PACKAGING grid
  4. APP_VERSION v3.3 -> v3.4

Run from the repo root:  python3 shared/patch_mc_content_packaging.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_contentpkg")

MARKER = "packagingbox"

OLD_HTML = """  panel.innerHTML =
    '<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">' +
      '<span style="width:8px;height:8px;border-radius:50%;background:#ff0000;display:inline-block;"></span>' +
      '<b style="letter-spacing:.04em;">FINAL VIDEO &mdash; UPLOAD TO STUDIO</b></div>' +
    '<video src="' + vsrc + '" autoplay muted loop playsinline ' +
      'style="width:100%;border-radius:8px;background:#000;display:block;margin-bottom:8px;"></video>' +
    '<div style="margin-bottom:14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;">' +
      '<a href="' + vsrc + '" download style="display:inline-block;background:#2a2a36;color:#e8e6e3;' +
        'text-decoration:none;border-radius:6px;padding:8px 14px;font-weight:600;font-size:13px;">' +
        '&#8595; Download final video</a>' +
      '<button id="reassemblebtn" style="background:#2a2a36;margin-top:0;padding:8px 14px;font-size:13px;">' +
        '&#8635; Re-assemble (latest clips)</button>' +
      '<span id="reassemblemsg" style="color:#8a8a99;font-size:12px;"></span></div>' +
    '<label>Title</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
      'background:#1c1c26;padding:8px 10px;margin-bottom:8px;">' + esc(meta.title) + '</div>' +
    '<label>Description</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
      'background:#1c1c26;padding:8px 10px;margin-bottom:8px;white-space:pre-wrap;">' + esc(meta.description) + '</div>' +
    '<label>Tags</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
      'background:#1c1c26;padding:8px 10px;margin-bottom:14px;">' + esc(meta.tags) + '</div>' +
    '<label>Thumbnail</label>' +
    '<div style="border:1px solid #32323e;border-radius:8px;background:#161620;padding:10px;margin-bottom:14px;">' +
      '<div style="display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap;align-items:center;">' +
        '<input id="thumbtitle" placeholder="Headline (e.g. 200,000 WENT SILENT)" style="flex:2;min-width:170px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">' +
        '<input id="thumbsub" placeholder="Subtitle (optional)" style="flex:1;min-width:110px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">' +
        '<input id="thumbshot" type="number" min="1" placeholder="still #" style="width:78px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">' +
        '<button id="thumbgen" style="background:#d4a017;margin-top:0;padding:8px 14px;font-size:13px;font-weight:600;">Generate</button>' +
      '</div>' +
      '<span id="thumbmsg" style="color:#8a8a99;font-size:12px;"></span>' +
      '<img id="thumbimg" style="display:none;width:100%;border-radius:6px;margin-top:8px;background:#000;">' +
    '</div>' +
    '<button id="uploadbtn" ' +
      'style="background:#ff0000;">Upload to YouTube Studio (private)</button>' +
    '<span id="uploadmsg" style="color:#8a8a99;font-size:12px;margin-left:10px;"></span>' +
    '<div style="color:#8a8a99;font-size:11px;margin-top:6px;">Uploads as <b>private</b> '+
      '(review + set Altered-content = Yes in Studio before publishing).</div>';"""

NEW_HTML = """  panel.innerHTML =
    '<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">' +
      '<span style="width:8px;height:8px;border-radius:50%;background:#ff0000;display:inline-block;"></span>' +
      '<b style="letter-spacing:.04em;">FINAL VIDEO &mdash; UPLOAD TO STUDIO</b></div>' +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;margin-bottom:14px;">' +
    '<div id="contentbox" style="border:1px solid #32323e;border-radius:8px;background:#161620;padding:12px;">' +
      '<div style="color:#d4a017;font-size:12px;letter-spacing:.08em;margin-bottom:8px;">CONTENT</div>' +
      '<video src="' + vsrc + '" autoplay muted loop playsinline ' +
        'style="width:100%;border-radius:8px;background:#000;display:block;margin-bottom:8px;"></video>' +
      '<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">' +
        '<a href="' + vsrc + '" download style="display:inline-block;background:#2a2a36;color:#e8e6e3;' +
          'text-decoration:none;border-radius:6px;padding:8px 14px;font-weight:600;font-size:13px;">' +
          '&#8595; Download final video</a>' +
        '<button id="reassemblebtn" style="background:#2a2a36;margin-top:0;padding:8px 14px;font-size:13px;">' +
          '&#8635; Re-assemble (latest clips)</button>' +
        '<span id="reassemblemsg" style="color:#8a8a99;font-size:12px;"></span></div>' +
    '</div>' +
    '<div id="packagingbox" style="border:1px solid #32323e;border-radius:8px;background:#161620;padding:12px;">' +
      '<div style="color:#d4a017;font-size:12px;letter-spacing:.08em;margin-bottom:8px;">PACKAGING</div>' +
      '<img id="thumbimg" style="display:none;width:100%;border-radius:6px;margin-bottom:8px;background:#000;">' +
      '<div style="display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap;align-items:center;">' +
        '<input id="thumbtitle" placeholder="Headline (e.g. 200,000 WENT SILENT)" style="flex:2;min-width:170px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">' +
        '<input id="thumbsub" placeholder="Subtitle (optional)" style="flex:1;min-width:110px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">' +
        '<input id="thumbshot" type="number" min="1" placeholder="still #" style="width:78px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">' +
        '<button id="thumbgen" style="background:#d4a017;margin-top:0;padding:8px 14px;font-size:13px;font-weight:600;">Generate</button>' +
      '</div>' +
      '<span id="thumbmsg" style="color:#8a8a99;font-size:12px;"></span>' +
      '<div style="margin-top:10px;">' +
      '<label>Title</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
        'background:#1c1c26;padding:8px 10px;margin-bottom:8px;">' + esc(meta.title) + '</div>' +
      '<label>Description</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
        'background:#1c1c26;padding:8px 10px;margin-bottom:8px;white-space:pre-wrap;">' + esc(meta.description) + '</div>' +
      '<label>Tags</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
        'background:#1c1c26;padding:8px 10px;">' + esc(meta.tags) + '</div>' +
      '</div>' +
    '</div>' +
    '</div>' +
    '<button id="uploadbtn" ' +
      'style="background:#ff0000;width:100%;">Upload to YouTube Studio (private)</button>' +
    '<span id="uploadmsg" style="color:#8a8a99;font-size:12px;margin-left:10px;"></span>' +
    '<div style="color:#8a8a99;font-size:11px;margin-top:6px;">Uploads as <b>private</b> '+
      '(review + set Altered-content = Yes in Studio before publishing).</div>';"""

EDITS = [
    # 1. lift the slot cap (black-space cause one)
    (
        '''<div id="toppanel" style="flex:1 1 560px;min-width:320px;max-width:760px;"></div>''',
        '''<div id="toppanel" style="flex:1 1 560px;min-width:320px;"></div>''',
    ),
    # 2. lift the panel cap (cause two)
    (
        '''  panel.style.cssText = "max-width:720px;border:1px solid #d4a017;";''',
        '''  panel.style.cssText = "border:1px solid #d4a017;";''',
    ),
    # 3. CONTENT | PACKAGING grid
    (OLD_HTML, NEW_HTML),
    # 4. version bump
    (
        '''APP_VERSION = "v3.3"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v3.4"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (packagingbox present) — no-op.")
        return

    if 'APP_VERSION = "v3.3"' not in src:
        sys.exit("!! prerequisite missing: v3.3 hotfix — anchors target that text.")

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
    print("  CONTENT | PACKAGING equal boxes; thumb preview promoted; upload full-width")
    print("  width caps lifted (toppanel 760px, panel 720px)")
    print("  APP_VERSION v3.3 -> v3.4")


if __name__ == "__main__":
    main()
