#!/usr/bin/env python3
"""
patch_mc_inherit_sum.py — v2.4: decision-support line under the inherit
button: "This beat plus previous beat = X.XXs", colored green when the pair
fits the 5s Kling atom (full merge) and amber when it exceeds it (the tail
runs short -> Ken Burns fallback on the remainder).

4 anchored edits in shared/mission_control/pipeline_server.py (post-v2.3 text):
  1. motionCell carries data-dur (beatRow already has b.duration_s in scope)
  2. .inhsum line under the inherit button
  3. bindAnimateButtons: in-order pass sums each cell with its predecessor
  4. APP_VERSION v2.3 -> v2.4

No apostrophes anywhere in the added JS/HTML (doctrine: two escape decoders,
one character, dead page).

Run from the repo root:  python3 shared/patch_mc_inherit_sum.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_inhsum")

MARKER = "inhsum"

EDITS = [
    # 1. motion cell carries its beat duration
    (
        """    '<div class="motioncell" data-shot="' + (shot==null?'':shot) + '">' +""",

        """    '<div class="motioncell" data-shot="' + (shot==null?'':shot) + '" data-dur="' + (b.duration_s != null ? b.duration_s : '') + '">' +""",
    ),
    # 2. sum line under the inherit button
    (
        """    'font:13px ui-monospace,monospace;">Inherit previous clip: off</button>' +""",

        """    'font:13px ui-monospace,monospace;">Inherit previous clip: off</button>' +
    '<div class="inhsum" style="font-size:11px;margin-top:4px;min-height:13px;color:#55556a;"></div>' +""",
    ),
    # 3. in-order pairwise sum after the state paint
    (
        """      });
    }).catch(function() {});""",

        """      });
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
  });""",
    ),
    # 4. version bump
    (
        '''APP_VERSION = "v2.3"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v2.4"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (inhsum present) — no-op.")
        return

    if "inhbtn" not in src or 'APP_VERSION = "v2.3"' not in src:
        sys.exit("!! prerequisite missing: inherit toggle + hotfix (v2.3) — anchors target that text.")

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
    print("  data-dur on motion cells; sum line under inherit button")
    print("  green = pair fits the 5s atom; amber = tail falls back to KB")
    print("  APP_VERSION v2.3 -> v2.4")


if __name__ == "__main__":
    main()
