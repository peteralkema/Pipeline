#!/usr/bin/env python3
"""
patch_mc_kb_toggle.py — Mission Control review-page control for the per-beat
Ken-Burns override (kb_override in render_policy.json; engine side shipped in
patch_kenburns_toggle.py).

WHAT (6 anchored edits in shared/mission_control/pipeline_server.py):
  1. /api/render_policy GET also returns the kb_override list
  2. new handler _handle_kb_toggle: toggles a beat in kb_override, MERGE-style
     (same discipline as _handle_render_policy_post — never clobbers siblings)
  3. POST route /api/kb_toggle
  4. beatRow motionCell gains a "Ken-Burns" button under the motion box
  5. paintKB() + initial state paint from /api/render_policy on storyboard bind
  6. per-cell click wiring; while ON, the motion textarea AND "Render this
     clip" are disabled (that button fires Kling directly — the guard stops a
     manual clip contradicting the flag)

The truth lives in render_policy.json — the button paints from the file on
every storyboard render, so state survives reloads and re-renders.

SAFETY: verifies every anchor exactly once, patches in memory, py_compiles to
a temp file BEFORE touching the target, backs up to .pre_kbtoggle_mc.
Idempotent — re-running is a no-op.

Run from the repo root:  python3 shared/patch_mc_kb_toggle.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_kbtoggle_mc")

MARKER = "_handle_kb_toggle"

# ── 2. the new server handler, inserted before _handle_render_policy_post ──
HANDLER = '''    def _handle_kb_toggle(self, body):
        """Toggle a beat in render_policy.json "kb_override" — the per-beat
        Ken-Burns override (beat renders on the free floor even inside the
        Kling front-N; the freed slot is SAVED, not slid). MERGES with the
        existing file, same discipline as _handle_render_policy_post: no
        sibling key is ever clobbered. Returns the new state."""
        import json as _json
        try:
            beat = int(body.get("beat"))
        except Exception:
            self._json(400, {"ok": False, "error": "beat must be an integer"}); return
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
            kb = sorted({int(x) for x in existing.get("kb_override", [])})
        except Exception:
            kb = []
        if beat in kb:
            kb = [b for b in kb if b != beat]
            on = False
        else:
            kb = sorted(kb + [beat])
            on = True
        policy = dict(existing)
        if kb:
            policy["kb_override"] = kb
        else:
            policy.pop("kb_override", None)
        try:
            rp.write_text(_json.dumps(policy, indent=2))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"write failed: {e}"}); return
        self._json(200, {"ok": True, "on": on, "beat": beat, "kb_override": kb}); return

'''

EDITS = [
    # 1. GET handler: parse + return kb_override alongside kling_count/static
    (
        '''        n = 40
        static = False
        if rp.is_file():
            try:
                _rpj = _json.loads(rp.read_text())
                n = int(_rpj.get("kling_count", 40))
                static = bool(_rpj.get("static", False))
            except Exception:
                n = 40; static = False
        self._json(200, {"ok": True, "kling_count": n, "static": static, "default": 40}); return''',

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
    ),
    # 2. insert the handler before _handle_render_policy_post
    (
        "    def _handle_render_policy_post(self, body):",
        HANDLER + "    def _handle_render_policy_post(self, body):",
    ),
    # 3. POST route
    (
        '''        if path == "/api/render_policy":
            self._handle_render_policy_post(body); return''',

        '''        if path == "/api/render_policy":
            self._handle_render_policy_post(body); return
        if path == "/api/kb_toggle":
            self._handle_kb_toggle(body); return''',
    ),
    # 4. motionCell: KB button under the motion-direction label
    (
        """    '<div style="color:#55556a;font-size:11px;margin-top:4px;">motion direction</div>' +""",

        """    '<div style="color:#55556a;font-size:11px;margin-top:4px;">motion direction</div>' +
    '<button class="kbbtn" title="Flip this beat to the free Ken-Burns floor (kb_override; slot saved, not slid)" ' +
    'style="width:100%;margin-top:8px;background:#2a2a36;color:#e8e6e3;' +
    'border:1px solid #32323e;border-radius:6px;padding:8px;cursor:pointer;' +
    'font:13px ui-monospace,monospace;">Ken-Burns: off</button>' +""",
    ),
    # 5. paintKB + initial state paint at the head of bindAnimateButtons
    (
        '''function bindAnimateButtons(wrap) {
  const CH = (window.__SEL_VIEW || "/").split("/")[0];
  const PR = (window.__SEL_VIEW || "/").split("/").slice(1).join("/");''',

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
}
function bindAnimateButtons(wrap) {
  const CH = (window.__SEL_VIEW || "/").split("/")[0];
  const PR = (window.__SEL_VIEW || "/").split("/").slice(1).join("/");
  // paint KB state from the policy file (the truth) on every storyboard render
  api("/api/render_policy?channel=" + encodeURIComponent(CH) +
      "&project=" + encodeURIComponent(PR))
    .then(function(r) {
      const on = {};
      ((r && r.kb_override) || []).forEach(function(b) { on[b] = 1; });
      wrap.querySelectorAll(".motioncell").forEach(function(cell) {
        const bx = cell.querySelector("textarea.motionbox");
        if (!bx) return;
        const bt = parseInt((bx.getAttribute("data-mkey") || "").split("/").pop(), 10);
        if (!isNaN(bt)) paintKB(cell, !!on[bt]);
      });
    }).catch(function() {});''',
    ),
    # 6. per-cell click wiring (beat index parsed off the motion box's data-mkey)
    (
        '''    const box = cell.querySelector("textarea.motionbox");
    // motion-persist: write the typed direction to storyboard.json so it survives''',

        '''    const box = cell.querySelector("textarea.motionbox");
    // KB toggle: flip this beat's kb_override in render_policy.json (server merges).
    const kbbtn = cell.querySelector("button.kbbtn");
    if (kbbtn && box) {
      const kbeat = parseInt((box.getAttribute("data-mkey") || "").split("/").pop(), 10);
      kbbtn.addEventListener("click", async function() {
        if (isNaN(kbeat)) return;
        try {
          const r = await api("/api/kb_toggle", {method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({channel: CH, project: PR, beat: kbeat})});
          if (r && r.ok) paintKB(cell, r.on);
        } catch (e) { /* leave painted state; next storyboard render re-reads the file */ }
      });
    }
    // motion-persist: write the typed direction to storyboard.json so it survives''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (_handle_kb_toggle present) — no-op.")
        return

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
    print("  1. /api/render_policy GET returns kb_override")
    print("  2. _handle_kb_toggle added (merge-style, siblings never clobbered)")
    print("  3. POST route /api/kb_toggle")
    print("  4. KB button in the motion cell")
    print("  5. paintKB + state painted from the policy file on every render")
    print("  6. click wiring; motion box + Render-this-clip disabled while ON")


if __name__ == "__main__":
    main()
