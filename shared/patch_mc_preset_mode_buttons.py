#!/usr/bin/env python3
"""
patch_mc_preset_mode_buttons.py — v2.7: Dynamic / Slow crane-up are full MODE
buttons. Clicking one while Ken-Burns or Inherit is ON releases that toggle
server-side (render_policy.json stays the truth), stamps the exact direction
into the motion box, and takes the green — one click from any mode to Kling.

3 anchored edits in shared/mission_control/pipeline_server.py (post-v2.6):
  1. _applyBeatDisable: presets never disabled or dimmed (mode buttons)
  2. preset click: releases kb/inherit via the toggle endpoints first, then
     stamps + persists + repaints cell and all chain lines
  3. APP_VERSION v2.6 -> v2.7

No apostrophes in added JS (double-decode doctrine); self-checked.

Run from the repo root:  python3 shared/patch_mc_preset_mode_buttons.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_presetmode")

MARKER = "mode buttons: always clickable"

EDITS = [
    # 1. presets stay clickable in every mode
    (
        '''  cell.querySelectorAll("button.mpreset").forEach(function(pb) {
    pb.disabled = dis; pb.style.opacity = dis ? "0.45" : "1";
    const match = !dis && box && box.value.trim() === MPRESETS[pb.getAttribute("data-preset")];
    pb.style.background = match ? "#1c7c4a" : "#2a2a36";
  });''',

        '''  cell.querySelectorAll("button.mpreset").forEach(function(pb) {
    // mode buttons: always clickable — clicking one while KB or inherit is ON
    // switches the beat back to Kling with that exact direction.
    pb.disabled = false; pb.style.opacity = "1";
    const match = !dis && box && box.value.trim() === MPRESETS[pb.getAttribute("data-preset")];
    pb.style.background = match ? "#1c7c4a" : "#2a2a36";
  });''',
    ),
    # 2. preset click releases kb/inherit first, then stamps and repaints
    (
        '''    cell.querySelectorAll("button.mpreset").forEach(function(pb) {
      pb.addEventListener("click", function() {
        if (!box || box.disabled) return;
        const t = MPRESETS[pb.getAttribute("data-preset")];
        if (!t) return;
        box.value = t;
        window.__MOTION_EDITS[box.getAttribute("data-mkey")] = t;
        saveMotion();
        _applyBeatDisable(cell);
      });
    });''',

        '''    cell.querySelectorAll("button.mpreset").forEach(function(pb) {
      pb.addEventListener("click", async function() {
        if (!box) return;
        const t = MPRESETS[pb.getAttribute("data-preset")];
        if (!t) return;
        const pbeat = parseInt((box.getAttribute("data-mkey") || "").split("/").pop(), 10);
        try {
          if (cell.dataset.kbon === "1" && !isNaN(pbeat)) {
            const r = await api("/api/kb_toggle", {method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({channel: CH, project: PR, beat: pbeat})});
            if (r && r.ok) paintKB(cell, r.on);
          }
          if (cell.dataset.inhon === "1" && !isNaN(pbeat)) {
            const r2 = await api("/api/inherit_toggle", {method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({channel: CH, project: PR, beat: pbeat})});
            if (r2 && r2.ok) paintInherit(cell, r2.on);
          }
        } catch (e) { /* policy file re-read on next storyboard render */ }
        box.value = t;
        window.__MOTION_EDITS[box.getAttribute("data-mkey")] = t;
        saveMotion();
        _applyBeatDisable(cell);
        paintInhSums(wrap);
      });
    });''',
    ),
    # 3. version bump
    (
        '''APP_VERSION = "v2.6"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v2.7"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (preset mode buttons present) — no-op.")
        return

    if "mode invariant" not in src or 'APP_VERSION = "v2.6"' not in src:
        sys.exit("!! prerequisite missing: mode-invariant patch (v2.6) — anchors target that text.")

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
    print("  presets = mode buttons: click from KB/inherit straight to Kling")
    print("  release goes through the toggle endpoints — policy file stays the truth")
    print("  APP_VERSION v2.6 -> v2.7")


if __name__ == "__main__":
    main()
