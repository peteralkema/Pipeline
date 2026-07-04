#!/usr/bin/env python3
"""
patch_mc_inherit_sum_aware.py — v2.5: the inherit decision line now mirrors
the render pass exactly (idiot-proof, max craft, min cash):

  RED    source has no atom: the chain walks back to a Ken-Burns beat
         ("previous renders Ken-Burns - no atom to inherit") or falls off
         the front (beat 0). The render pass would fall back free; the UI
         says so BEFORE you rely on the merge.
  GREEN  chain total fits the 5s Kling atom — full merge, footage recovered.
  AMBER  chain total exceeds the atom — the tail falls back to KB.

Chain-aware: consecutive inherited beats show the TRUE total consumed from
the single source atom, not the pairwise sum. Live: every KB/inherit click
repaints all sum lines, so states can never go stale between toggles.

4 anchored edits in shared/mission_control/pipeline_server.py (post-v2.4):
  1. paintInhSums() added after paintInherit() — dataset-driven, chain walk
  2. GET-paint calls paintInhSums after painting states; the old synchronous
     pairwise block (which ran before the fetch resolved) is removed
  3. both toggle click handlers repaint sums
  4. APP_VERSION v2.4 -> v2.5

No apostrophes in added JS (double-decode doctrine); the patch self-checks.

Run from the repo root:  python3 shared/patch_mc_inherit_sum_aware.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_inhsum_aware")

MARKER = "paintInhSums"

SUMS_FN = '''
function paintInhSums(wrap) {
  // mirrors the inherit render pass: walk each beat back through inherited
  // predecessors to its source atom; red when the source is Ken-Burns or the
  // chain falls off the front; otherwise green/amber by 5s-atom fit.
  const arr = [];
  wrap.querySelectorAll(".motioncell").forEach(function(c) { arr.push(c); });
  for (var i = 0; i < arr.length; i++) {
    const el = arr[i].querySelector(".inhsum");
    if (!el) continue;
    const d = parseFloat(arr[i].getAttribute("data-dur"));
    if (i === 0 || isNaN(d)) { el.textContent = ""; continue; }
    var j = i - 1;
    while (j >= 0 && arr[j].dataset.inhon === "1") j--;
    if (j < 0) {
      el.textContent = "no source atom - inherit chain reaches beat 0 (falls back free)";
      el.style.color = "#c0392b"; continue;
    }
    if (arr[j].dataset.kbon === "1") {
      el.textContent = "previous renders Ken-Burns - no atom to inherit (falls back free)";
      el.style.color = "#c0392b"; continue;
    }
    var total = d, bad = false;
    for (var k = j; k < i; k++) {
      const dk = parseFloat(arr[k].getAttribute("data-dur"));
      if (isNaN(dk)) { bad = true; break; }
      total += dk;
    }
    if (bad) { el.textContent = ""; continue; }
    const fits = total <= 5.0;
    const label = (j === i - 1)
      ? "This beat plus previous beat = "
      : "Chain of " + (i - j + 1) + " beats on one atom = ";
    el.textContent = label + total.toFixed(2) + "s " +
                     (fits ? "(fits the 5s atom)" : "(exceeds the 5s atom - tail falls back)");
    el.style.color = fits ? "#1c7c4a" : "#c98a1a";
  }
}'''

EDITS = [
    # 1. paintInhSums after paintInherit
    (
        '''    btn.textContent = on ? "Inherit previous clip: ON (free)" : "Inherit previous clip: off";
    btn.style.background = on ? "#1c7c4a" : "#2a2a36";
  }
  _applyBeatDisable(cell);
}''',

        '''    btn.textContent = on ? "Inherit previous clip: ON (free)" : "Inherit previous clip: off";
    btn.style.background = on ? "#1c7c4a" : "#2a2a36";
  }
  _applyBeatDisable(cell);
}''' + SUMS_FN,
    ),
    # 2. paint sums INSIDE the .then (after states land); drop the old
    #    synchronous pairwise block that ran before the fetch resolved
    (
        '''      });
    }).catch(function() {});
  // inherit decision support: this beat + previous vs the 5s Kling atom.
  var _prevDur = null;
  wrap.querySelectorAll(".motioncell").forEach(function(cell) {
    const d = parseFloat(cell.getAttribute("data-dur"));
    const el = cell.querySelector(".inhsum");
    if (el && !isNaN(d) && _prevDur != null) {
      const sum = d + _prevDur;
      const fits = sum <= 5.0;
      el.textContent = "This beat plus previous beat = " + sum.toFixed(2) + "s " +
                       (fits ? "(fits the 5s atom)" : "(exceeds the 5s atom - tail falls back)");
      el.style.color = fits ? "#1c7c4a" : "#c98a1a";
    }
    _prevDur = isNaN(d) ? null : d;
  });''',

        '''      });
      paintInhSums(wrap);
    }).catch(function() {});''',
    ),
    # 3a. kb click repaints sums
    (
        '''          if (r && r.ok) { paintKB(cell, r.on); if (r.on) paintInherit(cell, false); }''',
        '''          if (r && r.ok) { paintKB(cell, r.on); if (r.on) paintInherit(cell, false); paintInhSums(wrap); }''',
    ),
    # 3b. inherit click repaints sums
    (
        '''          if (r && r.ok) { paintInherit(cell, r.on); if (r.on) paintKB(cell, false); }''',
        '''          if (r && r.ok) { paintInherit(cell, r.on); if (r.on) paintKB(cell, false); paintInhSums(wrap); }''',
    ),
    # 4. version bump
    (
        '''APP_VERSION = "v2.4"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v2.5"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (paintInhSums present) — no-op.")
        return

    if "inhsum" not in src or 'APP_VERSION = "v2.4"' not in src:
        sys.exit("!! prerequisite missing: sum-line patch (v2.4) — anchors target that text.")

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
    print("  paintInhSums: chain-aware, KB-aware (red), runs after state paint")
    print("  toggle clicks repaint all sum lines live")
    print("  APP_VERSION v2.4 -> v2.5")


if __name__ == "__main__":
    main()
