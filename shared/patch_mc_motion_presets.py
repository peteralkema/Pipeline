#!/usr/bin/env python3
"""
patch_mc_motion_presets.py — two proven motion-direction presets in the MC
motion cell (Gettysburg-banked wording, verbatim):

  Dynamic:       "dynamic cinematic camera movement, powerful momentum,
                  natural realistic motion, dramatic atmosphere"
  Slow crane-up: "slow cinematic camera movement, crane-up to wide angle
                  powerful momentum, natural realistic motion, dramatic atmosphere"

A preset button stamps its exact text into the motion box and persists it
through the EXISTING seam (in-memory edit map + /api/motion -> storyboard.json),
so the batch animate and per-beat Render-this-clip both pick it up with zero
engine changes. The text stays visible and editable after stamping.

4 anchored edits in shared/mission_control/pipeline_server.py
(anchors are the POST-kb-toggle text — requires patch_mc_kb_toggle applied):
  1. motionCell: preset button row between the label and the KB button
  2. paintKB: presets grey out with the box while Ken-Burns is ON
  3. bindAnimateButtons: click wiring (stamp -> edit map -> saveMotion)

SAFETY: verify-anchors-exactly-once, in-memory patch, py_compile to temp
BEFORE writing, backup to .pre_mpresets. Idempotent.

Run from the repo root:  python3 shared/patch_mc_motion_presets.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_mpresets")

MARKER = "mpreset"

EDITS = [
    # 1. motionCell: preset row between the motion-direction label and the KB button
    (
        """    '<div style="color:#55556a;font-size:11px;margin-top:4px;">motion direction</div>' +
    '<button class="kbbtn" title="Flip this beat to the free Ken-Burns floor (kb_override; slot saved, not slid)" ' +""",

        """    '<div style="color:#55556a;font-size:11px;margin-top:4px;">motion direction</div>' +
    '<div style="display:flex;gap:6px;margin-top:6px;">' +
    '<button class="mpreset" data-preset="dynamic" title="dynamic cinematic camera movement, powerful momentum, natural realistic motion, dramatic atmosphere" ' +
    'style="flex:1;background:#2a2a36;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;' +
    'padding:7px 4px;cursor:pointer;font:12px ui-monospace,monospace;">Dynamic</button>' +
    '<button class="mpreset" data-preset="slowcrane" title="slow cinematic camera movement, crane-up to wide angle powerful momentum, natural realistic motion, dramatic atmosphere" ' +
    'style="flex:1;background:#2a2a36;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;' +
    'padding:7px 4px;cursor:pointer;font:12px ui-monospace,monospace;">Slow crane-up</button>' +
    '</div>' +
    '<button class="kbbtn" title="Flip this beat to the free Ken-Burns floor (kb_override; slot saved, not slid)" ' +""",
    ),
    # 2. paintKB: presets follow the box's disabled state while KB is ON
    (
        """  if (box) { box.disabled = on; box.style.opacity = on ? "0.45" : "1"; }
  if (anim) { anim.disabled = on; anim.style.opacity = on ? "0.45" : "1"; }""",

        """  if (box) { box.disabled = on; box.style.opacity = on ? "0.45" : "1"; }
  if (anim) { anim.disabled = on; anim.style.opacity = on ? "0.45" : "1"; }
  cell.querySelectorAll("button.mpreset").forEach(function(pb) {
    pb.disabled = on; pb.style.opacity = on ? "0.45" : "1";
  });""",
    ),
    # 3. click wiring: stamp exact preset text, mirror to the edit map, persist
    (
        """        } catch (e) { /* leave painted state; next storyboard render re-reads the file */ }
      });
    }
    // motion-persist: write the typed direction to storyboard.json so it survives""",

        """        } catch (e) { /* leave painted state; next storyboard render re-reads the file */ }
      });
    }
    // motion presets: stamp an exact proven direction into the box, then persist
    // through the same seam as typing (edit map + saveMotion -> storyboard.json).
    const MPRESETS = {
      dynamic: "dynamic cinematic camera movement, powerful momentum, natural realistic motion, dramatic atmosphere",
      slowcrane: "slow cinematic camera movement, crane-up to wide angle powerful momentum, natural realistic motion, dramatic atmosphere"
    };
    cell.querySelectorAll("button.mpreset").forEach(function(pb) {
      pb.addEventListener("click", function() {
        if (!box || box.disabled) return;
        const t = MPRESETS[pb.getAttribute("data-preset")];
        if (!t) return;
        box.value = t;
        window.__MOTION_EDITS[box.getAttribute("data-mkey")] = t;
        saveMotion();
      });
    });
    // motion-persist: write the typed direction to storyboard.json so it survives""",
    ),
    # 4. version bump: v1.9 -> v2.0 (KB toggle + motion presets = a shipped page change)
    (
        '''APP_VERSION = "v1.9"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v2.0"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (mpreset present) — no-op.")
        return

    if "_handle_kb_toggle" not in src:
        sys.exit("!! prerequisite missing: patch_mc_kb_toggle not applied — anchors target the post-KB text.")

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
    print("  1. Dynamic / Slow crane-up preset buttons in the motion cell")
    print("  2. presets grey with the motion box while Ken-Burns is ON")
    print("  3. click stamps exact wording + persists via the existing motion seam")
    print("  4. APP_VERSION v1.9 -> v2.0")


if __name__ == "__main__":
    main()
