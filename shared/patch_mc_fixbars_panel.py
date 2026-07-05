#!/usr/bin/env python3
"""
patch_mc_fixbars_panel.py — v3.2: "Analyse + fix stills" also in the
always-visible project panel (next to Re-assemble). The v3.1 button lives in
the stills-gate bar, which only renders while a job waits at the gate — the
retro workflow (fix stills on a DONE project, re-render flagged clips,
Re-assemble) needs it available on completed projects too. Same endpoint,
distinct element id, injected JS-side like the thumbnail rows.

2 anchored edits in shared/mission_control/pipeline_server.py (post-v3.1):
  1. inject button + wiring after the reassemble wiring (ch/pr in scope)
  2. APP_VERSION v3.1 -> v3.2

Run from the repo root:  python3 shared/patch_mc_fixbars_panel.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_fixbars_panel")

MARKER = "fixbarsbtn2"

PANEL_JS = '''
  // v3.2: retro letterbox fix on completed projects — same endpoint as the
  // stills-gate button, distinct id (both can render at once).
  if (rb && !document.getElementById("fixbarsbtn2")) {
    const fwrap = document.createElement("div");
    fwrap.style.cssText = "margin-top:8px;display:flex;gap:8px;align-items:center;";
    fwrap.innerHTML =
      '<button id="fixbarsbtn2" title="Detect and crop baked-in black letterbox bars across all stills (originals backed up)" ' +
      'style="background:#2a2a36;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;' +
      'padding:8px 10px;cursor:pointer;font:13px ui-monospace,monospace;">Analyse + fix stills</button>' +
      '<span id="fixbarsmsg" style="color:#8a8a99;font:12px ui-monospace,monospace;"></span>';
    rb.parentElement.appendChild(fwrap);
  }
  const fb2 = document.getElementById("fixbarsbtn2");
  if (fb2) fb2.onclick = async function() {
    const fm = document.getElementById("fixbarsmsg");
    fb2.disabled = true; fb2.textContent = "Analysing stills\\u2026";
    try {
      const r = await api("/api/fix_letterbox", {method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({channel: ch, project: pr})});
      if (r && r.ok) {
        let t = "scanned " + r.scanned + ", fixed " + r.fixed.length +
                (r.fixed.length ? ": " + r.fixed.join(", ") : "");
        if (r.have_clips && r.have_clips.length) {
          t += "  \\u26a0 re-render these clips, then Re-assemble: " + r.have_clips.join(", ");
        }
        if (fm) fm.textContent = t;
      } else if (fm) {
        fm.textContent = "fix failed: " + ((r && r.error) || "error");
      }
    } catch (e) { if (fm) fm.textContent = "fix failed: " + e; }
    fb2.disabled = false; fb2.textContent = "Analyse + fix stills";
  };
'''

EDITS = [
    (
        '''  const rb = document.getElementById("reassemblebtn");
  if (rb) rb.onclick = function() { reassemble(ch, pr); };''',

        '''  const rb = document.getElementById("reassemblebtn");
  if (rb) rb.onclick = function() { reassemble(ch, pr); };
''' + PANEL_JS,
    ),
    (
        '''APP_VERSION = "v3.1"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v3.2"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (fixbarsbtn2 present) — no-op.")
        return

    if "fix_letterbox" not in src or 'APP_VERSION = "v3.1"' not in src:
        sys.exit("!! prerequisite missing: fix-letterbox patch (v3.1) — anchors target that text.")

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
    print("  Analyse + fix stills now also in the project panel (next to Re-assemble)")
    print("  APP_VERSION v3.1 -> v3.2")


if __name__ == "__main__":
    main()
