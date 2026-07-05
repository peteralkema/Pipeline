#!/usr/bin/env python3
"""
patch_mc_cost_widget.py — v3.7: persistent ESTIMATED SPEND widget, fixed
bottom-left, always visible while scrolling the storyboard. Counts the
CURRENT per-beat modes exactly as the tiered render will route them:

  Kling  = beat < kling_count AND not KB AND not inherit  -> n x $0.35
  KB     = toggled OR beyond the front-N (the free floor) -> $0
  inherit                                                  -> $0

Also counts Kling-mode beats whose clip already exists on disk (skip-existing
protects them) and shows REMAINING spend — the number that matters mid-review.

Repaints wherever the chain lines repaint (every KB/inherit/preset click and
every storyboard render), so the total tracks each toggle live. kling_count
comes from the /api/render_policy GET the page already makes.

4 anchored edits in shared/mission_control/pipeline_server.py (post-v3.6):
  1. paintCostWidget() added before paintInhSums()
  2. paintInhSums tail calls paintCostWidget (rides every existing repaint)
  3. GET .then stores kling_count on window.__KLING_N
  4. APP_VERSION v3.6 -> v3.7

No apostrophes in added JS (double-decode doctrine); self-checked.

Run from the repo root:  python3 shared/patch_mc_cost_widget.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_costwidget")

MARKER = "costwidget"

WIDGET_FN = '''function paintCostWidget(wrap) {
  // persistent spend estimate: sums CURRENT per-beat modes exactly as the
  // tiered render routes them (kling only if beat < N and not kb/inherit).
  const CLIP_COST = 0.35;  // Kling v2.5-turbo per 5s atom
  const arr = [];
  wrap.querySelectorAll(".motioncell").forEach(function(c) { arr.push(c); });
  let w = document.getElementById("costwidget");
  if (!arr.length) { if (w) w.style.display = "none"; return; }
  if (!w) {
    w = document.createElement("div");
    w.id = "costwidget";
    w.style.cssText = "position:fixed;bottom:24px;left:24px;z-index:9999;" +
      "background:#16161e;border:1px solid #d4a017;border-radius:8px;" +
      "padding:10px 14px;font:12px/1.5 ui-monospace,monospace;color:#e8e6e3;" +
      "box-shadow:0 4px 20px rgba(0,0,0,.5);";
    document.body.appendChild(w);
  }
  const N = (window.__KLING_N != null) ? window.__KLING_N : 40;
  let kling = 0, kb = 0, inh = 0, done = 0;
  for (var i = 0; i < arr.length; i++) {
    const cell = arr[i];
    const bx = cell.querySelector("textarea.motionbox");
    let bt = bx ? parseInt((bx.getAttribute("data-mkey") || "").split("/").pop(), 10) : i;
    if (isNaN(bt)) bt = i;
    if (cell.dataset.inhon === "1") { inh++; continue; }
    if (cell.dataset.kbon === "1" || !(bt < N)) { kb++; continue; }
    kling++;
    const grid = cell.parentElement.parentElement;
    if (grid && grid.querySelector("video")) done++;
  }
  const total = kling * CLIP_COST;
  const remaining = (kling - done) * CLIP_COST;
  w.style.display = "block";
  w.innerHTML =
    '<div style="color:#d4a017;letter-spacing:.06em;margin-bottom:4px;">ESTIMATED SPEND</div>' +
    '<div><b>' + kling + '</b> Kling &times; $' + CLIP_COST.toFixed(2) + ' = <b>$' + total.toFixed(2) + '</b></div>' +
    '<div style="color:#8a8a99;">' + kb + ' Ken-Burns + ' + inh + ' inherit = free</div>' +
    (done ? '<div style="color:#8a8a99;">' + done + ' already rendered &rarr; remaining ~<b style="color:#e8e6e3;">$' +
            remaining.toFixed(2) + '</b></div>' : '');
}
'''

EDITS = [
    # 1. widget painter before paintInhSums
    (
        "\nfunction paintInhSums(wrap) {",
        "\n" + WIDGET_FN + "function paintInhSums(wrap) {",
    ),
    # 2. ride every existing repaint: tail of paintInhSums
    (
        '''    } else {
      el.textContent = "renders its own 5s Kling atom - source for inherit chains";
      el.style.color = "#8a8a99";
    }
  }
}''',

        '''    } else {
      el.textContent = "renders its own 5s Kling atom - source for inherit chains";
      el.style.color = "#8a8a99";
    }
  }
  paintCostWidget(wrap);
}''',
    ),
    # 3. store kling_count from the GET the page already makes
    (
        '''    .then(function(r) {
      const kbOn = {}, inhOn = {};''',

        '''    .then(function(r) {
      window.__KLING_N = (r && r.kling_count != null) ? r.kling_count : 40;
      const kbOn = {}, inhOn = {};''',
    ),
    # 4. version bump
    (
        '''APP_VERSION = "v3.6"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v3.7"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (costwidget present) — no-op.")
        return

    if "paintInhSums" not in src or 'APP_VERSION = "v3.6"' not in src:
        sys.exit("!! prerequisite missing: v3.6 — anchors target that text.")

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
    print("  ESTIMATED SPEND widget, fixed bottom-left, live on every toggle")
    print("  routing-exact: kling only if beat < N and not kb/inherit; remaining-spend line")
    print("  APP_VERSION v3.6 -> v3.7")


if __name__ == "__main__":
    main()
