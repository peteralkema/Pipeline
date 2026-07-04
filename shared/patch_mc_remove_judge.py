#!/usr/bin/env python3
"""
patch_mc_remove_judge.py — remove the dead Accept/Reject buttons from the
review page (v2.0 -> v2.1).

WHY: they write only to window.__JUDGED, an in-memory browser map with no save
endpoint and no consumer — state evaporates on reload and nothing downstream
(render, gates, batch) ever reads it. Verified by grep: written by their own
two click handlers, read only to color themselves. Dead controls on the
operator's most important surface cost craft-attention.

BANKED (deliberate-later): a reject-list driving a one-click "re-render all
rejected" batch action would attack the regen tax — build it WITH a backend
and a batch action, or not at all.

5 anchored edits in shared/mission_control/pipeline_server.py:
  1. beatRow: judge consts + button row out of controlsCell (data-jkey too)
  2. bindStillControls: __JUDGED init out
  3. bindStillControls: orphaned jkey const out
  4. bindStillControls: acc/rej consts + click handlers out
  5. APP_VERSION v2.0 -> v2.1 (anchor doubles as prerequisite: presets patch applied)

SAFETY: verify-anchors-exactly-once, in-memory patch, py_compile to temp
BEFORE writing, backup to .pre_nojudge. Idempotent.

Run from the repo root:  python3 shared/patch_mc_remove_judge.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_nojudge")

EDITS = [
    # 1. beatRow: remove judge paint consts, data-jkey, and the Accept/Reject row
    (
        """    const jkey = motionKey(ch, pr, b.index);  // reuse the channel/project/beat key
    const judged = window.__JUDGED && window.__JUDGED[jkey];
    const accSel = judged === "accept" ? "background:#1c7c4a;" : "";
    const rejSel = judged === "reject" ? "background:#7c1c1c;" : "";
    controlsCell =
      '<div class="stillctl" data-shot="' + shot + '" data-jkey="' + jkey + '">' +
        '<div style="display:flex;gap:8px;">' +
          '<button class="jbtn acc" style="flex:1;background:#2a2a36;' + accSel +
            'color:#e8e6e3;border:0;border-radius:6px;padding:8px;cursor:pointer;font:13px ui-monospace,monospace;">Accept</button>' +
          '<button class="jbtn rej" style="flex:1;background:#2a2a36;' + rejSel +
            'color:#e8e6e3;border:0;border-radius:6px;padding:8px;cursor:pointer;font:13px ui-monospace,monospace;">Reject</button>' +
        '</div>' +
        '<button class="nbfix" style="width:100%;margin-top:8px;background:#c98a1a;color:#fff;' +""",

        """    controlsCell =
      '<div class="stillctl" data-shot="' + shot + '">' +
        '<button class="nbfix" style="width:100%;margin-top:8px;background:#c98a1a;color:#fff;' +""",
    ),
    # 2. drop the __JUDGED init
    (
        """function bindStillControls(wrap) {
  window.__JUDGED = window.__JUDGED || {};""",

        """function bindStillControls(wrap) {""",
    ),
    # 3. drop the orphaned jkey const
    (
        """    const jkey = ctl.getAttribute("data-jkey");
    const msg = ctl.querySelector(".ctlmsg");""",

        """    const msg = ctl.querySelector(".ctlmsg");""",
    ),
    # 4. drop acc/rej consts + their click handlers
    (
        """    const acc = ctl.querySelector("button.acc");
    const rej = ctl.querySelector("button.rej");
    const regen = ctl.querySelector("button.regen");
    const nbfix = ctl.querySelector("button.nbfix");

    acc.addEventListener("click", function() {
      window.__JUDGED[jkey] = "accept";
      acc.style.background = "#1c7c4a"; rej.style.background = "#2a2a36";
    });
    rej.addEventListener("click", function() {
      window.__JUDGED[jkey] = "reject";
      rej.style.background = "#7c1c1c"; acc.style.background = "#2a2a36";
    });""",

        """    const regen = ctl.querySelector("button.regen");
    const nbfix = ctl.querySelector("button.nbfix");""",
    ),
    # 5. version bump (also enforces the presets patch as prerequisite)
    (
        '''APP_VERSION = "v2.0"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v2.1"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if "jbtn" not in src:
        print("already applied (no jbtn present) — no-op.")
        return

    for i, (old, _new) in enumerate(EDITS, 1):
        n = src.count(old)
        if n != 1:
            sys.exit(f"!! anchor {i} matched {n} times (need exactly 1) — file drifted, NOT patched.\n"
                     f"   anchor starts: {old.splitlines()[0]!r}")

    patched = src
    for old, new in EDITS:
        patched = patched.replace(old, new)

    for leftover in ("jbtn", "__JUDGED", "accSel", "rejSel"):
        if leftover in patched:
            sys.exit(f"!! leftover reference {leftover!r} after edits — NOT patched; dump the region.")

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
    print("  Accept/Reject removed (buttons, paint, wiring, data-jkey) — no leftovers")
    print("  APP_VERSION v2.0 -> v2.1")


if __name__ == "__main__":
    main()
