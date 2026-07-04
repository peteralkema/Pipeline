#!/usr/bin/env python3
"""
patch_mc_inherit_toggle.py — Mission Control control for clip-merge
(inherit_prev in render_policy.json; engine side in patch_clip_inherit.py).
v2.1 -> v2.2.

WHAT (8 anchored edits in shared/mission_control/pipeline_server.py,
anchors are the post-v2.1 text — kb toggle + presets + judge removal applied):
  1. /api/render_policy GET also returns inherit_prev
  2. _handle_kb_toggle: turning KB on removes the beat from inherit_prev
  3. new handler _handle_inherit_toggle (merge-style; turning inherit on
     removes the beat from kb_override — mutual exclusion both ways)
  4. POST route /api/inherit_toggle
  5. motionCell: "Inherit previous clip" button under the KB button
  6. paintKB replaced by state-aware painters (paintKB + paintInherit +
     shared _applyBeatDisable via cell.dataset flags, so turning one off
     never re-enables a cell the other still holds)
  7. GET-paint block paints both states; beat 0's inherit button disabled
     (no predecessor)
  8. click wiring for inherit; kb click also repaints inherit off, and
     APP_VERSION v2.1 -> v2.2

While inherited: motion box, presets, KB button state respected, and
Render-this-clip all grey — the beat renders nothing of its own.

SAFETY: verify-anchors-exactly-once, in-memory patch, py_compile to temp
BEFORE writing, backup to .pre_inherit_mc. Idempotent.

Run from the repo root:  python3 shared/patch_mc_inherit_toggle.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_inherit_mc")

MARKER = "inhbtn"

INHERIT_HANDLER = '''    def _handle_inherit_toggle(self, body):
        """Toggle a beat in render_policy.json "inherit_prev" — clip-merge: the
        beat plays the unused tail of its predecessor's atom (derived in the
        inherit pass; free). MERGE-style, siblings never clobbered. Mutual
        exclusion: turning inherit ON removes the beat from kb_override."""
        import json as _json
        try:
            beat = int(body.get("beat"))
        except Exception:
            self._json(400, {"ok": False, "error": "beat must be an integer"}); return
        if beat == 0:
            self._json(400, {"ok": False, "error": "beat 0 has no predecessor"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        paths = resolve_paths(ch, pr, _REPO)
        rp = paths["project"] / "render_policy.json"
        existing = {}
        if rp.is_file():
            try:
                existing = _json.loads(rp.read_text()) or {}
            except Exception:
                existing = {}
        try:
            inh = sorted({int(x) for x in existing.get("inherit_prev", [])})
        except Exception:
            inh = []
        if beat in inh:
            inh = [b for b in inh if b != beat]
            on = False
        else:
            inh = sorted(inh + [beat])
            on = True
        policy = dict(existing)
        if on:
            try:
                _kb = sorted({int(x) for x in existing.get("kb_override", [])} - {beat})
            except Exception:
                _kb = []
            if _kb:
                policy["kb_override"] = _kb
            else:
                policy.pop("kb_override", None)
        if inh:
            policy["inherit_prev"] = inh
        else:
            policy.pop("inherit_prev", None)
        try:
            rp.write_text(_json.dumps(policy, indent=2))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"write failed: {e}"}); return
        self._json(200, {"ok": True, "on": on, "beat": beat, "inherit_prev": inh}); return

'''

PAINTERS = '''function _applyBeatDisable(cell) {
  // a beat that renders nothing of its own (KB or inherit) takes no motion
  // direction and must not fire a manual Kling render.
  const dis = cell.dataset.kbon === "1" || cell.dataset.inhon === "1";
  const box = cell.querySelector("textarea.motionbox");
  const anim = cell.querySelector("button.animbtn");
  if (box) { box.disabled = dis; box.style.opacity = dis ? "0.45" : "1"; }
  if (anim) { anim.disabled = dis; anim.style.opacity = dis ? "0.45" : "1"; }
  cell.querySelectorAll("button.mpreset").forEach(function(pb) {
    pb.disabled = dis; pb.style.opacity = dis ? "0.45" : "1";
  });
}
function paintKB(cell, on) {
  cell.dataset.kbon = on ? "1" : "0";
  const btn = cell.querySelector("button.kbbtn");
  if (btn) {
    btn.textContent = on ? "Ken-Burns: ON (free)" : "Ken-Burns: off";
    btn.style.background = on ? "#1c7c4a" : "#2a2a36";
  }
  _applyBeatDisable(cell);
}
function paintInherit(cell, on) {
  cell.dataset.inhon = on ? "1" : "0";
  const btn = cell.querySelector("button.inhbtn");
  if (btn) {
    btn.textContent = on ? "Inherit previous clip: ON (free)" : "Inherit previous clip: off";
    btn.style.background = on ? "#1c7c4a" : "#2a2a36";
  }
  _applyBeatDisable(cell);
}'''

EDITS = [
    # 1. GET returns inherit_prev
    (
        '''        n = 40
        static = False
        kb = []
        if rp.is_file():
            try:
                _rpj = _json.loads(rp.read_text())
                n = int(_rpj.get("kling_count", 40))
                static = bool(_rpj.get("static", False))
                kb = sorted({int(x) for x in _rpj.get("kb_override", [])})
            except Exception:
                n = 40; static = False; kb = []
        self._json(200, {"ok": True, "kling_count": n, "static": static,
                         "kb_override": kb, "default": 40}); return''',

        '''        n = 40
        static = False
        kb = []
        inh = []
        if rp.is_file():
            try:
                _rpj = _json.loads(rp.read_text())
                n = int(_rpj.get("kling_count", 40))
                static = bool(_rpj.get("static", False))
                kb = sorted({int(x) for x in _rpj.get("kb_override", [])})
                inh = sorted({int(x) for x in _rpj.get("inherit_prev", [])})
            except Exception:
                n = 40; static = False; kb = []; inh = []
        self._json(200, {"ok": True, "kling_count": n, "static": static,
                         "kb_override": kb, "inherit_prev": inh, "default": 40}); return''',
    ),
    # 2. kb handler: turning KB on removes the beat from inherit_prev
    (
        '''            kb = sorted(kb + [beat])
            on = True
        policy = dict(existing)''',

        '''            kb = sorted(kb + [beat])
            on = True
        policy = dict(existing)
        if on:
            try:
                _inh = sorted({int(x) for x in existing.get("inherit_prev", [])} - {beat})
            except Exception:
                _inh = []
            if _inh:
                policy["inherit_prev"] = _inh
            else:
                policy.pop("inherit_prev", None)''',
    ),
    # 3. inherit handler before _handle_render_policy_post
    (
        "    def _handle_render_policy_post(self, body):",
        INHERIT_HANDLER + "    def _handle_render_policy_post(self, body):",
    ),
    # 4. POST route
    (
        '''        if path == "/api/kb_toggle":
            self._handle_kb_toggle(body); return''',

        '''        if path == "/api/kb_toggle":
            self._handle_kb_toggle(body); return
        if path == "/api/inherit_toggle":
            self._handle_inherit_toggle(body); return''',
    ),
    # 5. inherit button under the KB button in the motion cell
    (
        """    'font:13px ui-monospace,monospace;">Ken-Burns: off</button>' +""",

        """    'font:13px ui-monospace,monospace;">Ken-Burns: off</button>' +
    '<button class="inhbtn" title="Beat plays the unused tail of the previous beat\\'s atom (free; same-scene continuation; derived at render, falls back to Ken Burns if nothing is left)" ' +
    'style="width:100%;margin-top:8px;background:#2a2a36;color:#e8e6e3;' +
    'border:1px solid #32323e;border-radius:6px;padding:8px;cursor:pointer;' +
    'font:13px ui-monospace,monospace;">Inherit previous clip: off</button>' +""",
    ),
    # 6. replace paintKB with the state-aware painter trio
    (
        '''function paintKB(cell, on) {
  // per-beat Ken-Burns override state: green button; motion box + Render-this-clip
  // disabled while ON (that button fires Kling directly — don't contradict the flag).
  const btn = cell.querySelector("button.kbbtn");
  const box = cell.querySelector("textarea.motionbox");
  const anim = cell.querySelector("button.animbtn");
  if (btn) {
    btn.textContent = on ? "Ken-Burns: ON (free)" : "Ken-Burns: off";
    btn.style.background = on ? "#1c7c4a" : "#2a2a36";
  }
  if (box) { box.disabled = on; box.style.opacity = on ? "0.45" : "1"; }
  if (anim) { anim.disabled = on; anim.style.opacity = on ? "0.45" : "1"; }
  cell.querySelectorAll("button.mpreset").forEach(function(pb) {
    pb.disabled = on; pb.style.opacity = on ? "0.45" : "1";
  });
}''',

        PAINTERS,
    ),
    # 7. GET-paint block paints both states; beat 0 inherit disabled
    (
        '''    .then(function(r) {
      const on = {};
      ((r && r.kb_override) || []).forEach(function(b) { on[b] = 1; });
      wrap.querySelectorAll(".motioncell").forEach(function(cell) {
        const bx = cell.querySelector("textarea.motionbox");
        if (!bx) return;
        const bt = parseInt((bx.getAttribute("data-mkey") || "").split("/").pop(), 10);
        if (!isNaN(bt)) paintKB(cell, !!on[bt]);
      });
    }).catch(function() {});''',

        '''    .then(function(r) {
      const kbOn = {}, inhOn = {};
      ((r && r.kb_override) || []).forEach(function(b) { kbOn[b] = 1; });
      ((r && r.inherit_prev) || []).forEach(function(b) { inhOn[b] = 1; });
      wrap.querySelectorAll(".motioncell").forEach(function(cell) {
        const bx = cell.querySelector("textarea.motionbox");
        if (!bx) return;
        const bt = parseInt((bx.getAttribute("data-mkey") || "").split("/").pop(), 10);
        if (isNaN(bt)) return;
        paintKB(cell, !!kbOn[bt]);
        paintInherit(cell, !!inhOn[bt]);
        if (bt === 0) {
          const ib = cell.querySelector("button.inhbtn");
          if (ib) { ib.disabled = true; ib.style.opacity = "0.45"; ib.title = "beat 0 has no predecessor"; }
        }
      });
    }).catch(function() {});''',
    ),
    # 8a. kb click also turns the inherit paint off
    (
        '''          if (r && r.ok) paintKB(cell, r.on);
        } catch (e) { /* leave painted state; next storyboard render re-reads the file */ }''',

        '''          if (r && r.ok) { paintKB(cell, r.on); if (r.on) paintInherit(cell, false); }
        } catch (e) { /* leave painted state; next storyboard render re-reads the file */ }''',
    ),
    # 8b. inherit click wiring, inserted before the presets wiring
    (
        '''      });
    }
    // motion presets: stamp an exact proven direction into the box, then persist''',

        '''      });
    }
    // inherit-prev toggle: clip-merge — beat rides its predecessor's atom.
    const inhbtn = cell.querySelector("button.inhbtn");
    if (inhbtn && box) {
      const ibeat = parseInt((box.getAttribute("data-mkey") || "").split("/").pop(), 10);
      inhbtn.addEventListener("click", async function() {
        if (isNaN(ibeat) || ibeat === 0) return;
        try {
          const r = await api("/api/inherit_toggle", {method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({channel: CH, project: PR, beat: ibeat})});
          if (r && r.ok) { paintInherit(cell, r.on); if (r.on) paintKB(cell, false); }
        } catch (e) { /* next storyboard render re-reads the file */ }
      });
    }
    // motion presets: stamp an exact proven direction into the box, then persist''',
    ),
    # 8c. version bump
    (
        '''APP_VERSION = "v2.1"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v2.2"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (inhbtn present) — no-op.")
        return

    for need, why in [("_handle_kb_toggle", "kb toggle patch"),
                      ("mpreset", "motion presets patch"),
                      ('APP_VERSION = "v2.1"', "judge-removal patch (v2.1)")]:
        if need not in src:
            sys.exit(f"!! prerequisite missing ({why}) — anchors target the post-v2.1 text.")

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
    print("  GET returns inherit_prev; /api/inherit_toggle added (merge-style)")
    print("  mutual exclusion both ways (kb <-> inherit), server-enforced")
    print("  Inherit button in the motion cell; state-aware painters; beat 0 disabled")
    print("  APP_VERSION v2.1 -> v2.2")


if __name__ == "__main__":
    main()
