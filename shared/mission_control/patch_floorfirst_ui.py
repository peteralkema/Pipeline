#!/usr/bin/env python3
"""
patch_floorfirst_ui.py — floor-first MC UI, rebuilt clean (v3.9.2).

Combines the two panels that broke on a cssText JS syntax bug, reissued with
individual element.style.prop assignments (NO cssText string literals, which is
what produced 'Unexpected identifier color' and hung the page):

  1. Assemble-at-clips: /api/meta reports has_clips; when a project has clips but
     no final_video, renderDonePanel shows an Assemble panel (reuses reassemble()).
  2. Floor-all button in the section toolbar: POST /api/floor_all -> kling_count:0
     + clear kling_override/kb_override/inherit_prev (whole project -> free floor).
  3. Preset auto-enroll: a Dynamic/Slow-crane click also POSTs /api/kling_override
     to enroll the beat (so under kling_count:0 it actually renders Kling), and
     the server drops the beat's .kbfloor clip (delete-on-upgrade).
  4. Server: _handle_kling_override_toggle, _handle_floor_all, both routes.

Idempotent (sentinel FLOORFIRST_UI_APPLIED). Anchors verified once each; py_compile
before write; backup pipeline_server.py.pre_floorfirstui. Pure ASCII.
"""
import sys, py_compile, tempfile, shutil
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_floorfirstui")
SENTINEL = "FLOORFIRST_UI_APPLIED"

# ---- Edit A: /api/meta -> add has_clips beside has_video ----
A_ANCHOR = '''                "has_video": video.exists(),'''
A_NEW = '''                "has_video": video.exists(),
                "has_clips": bool((Path(paths["project"]) / "modea" / "clips").is_dir() and
                                  any((Path(paths["project"]) / "modea" / "clips").glob("shot_*.mp4"))),  # FLOORFIRST_UI_APPLIED'''

# ---- Edit B: renderDonePanel gate -> offer assemble panel at clips_ready ----
B_ANCHOR = '''  if (!meta || !meta.has_video) { renderTopPlaceholder(); return; }   // no video -> placeholder'''
B_NEW = '''  if (!meta || !meta.has_video) {   // FLOORFIRST_UI_APPLIED
    if (meta && meta.has_clips) { renderAssemblePanel(ch, pr); return; }
    renderTopPlaceholder(); return;
  }'''

# ---- Edit C: define renderAssemblePanel above renderTopPlaceholder (no cssText) ----
C_ANCHOR = '''function renderTopPlaceholder() {'''
C_NEW = '''function renderAssemblePanel(ch, pr) {
  // FLOORFIRST_UI_APPLIED: clips exist, no final_video yet. Offer a deliberate
  // assemble press (reuses reassemble()). Styling via .style.prop = only.
  var slot = document.getElementById("toppanel");
  if (!slot) return;
  var panel = document.createElement("div");
  panel.id = "donepanel";
  panel.className = "panel";
  panel.style.border = "1px solid #32323e";
  panel.style.borderRadius = "8px";
  panel.style.background = "#161620";
  panel.style.padding = "18px";
  panel.style.textAlign = "center";
  var head = document.createElement("div");
  head.textContent = "CLIPS READY";
  head.style.color = "#d4a017";
  head.style.fontSize = "12px";
  head.style.letterSpacing = "0.08em";
  head.style.marginBottom = "8px";
  var sub = document.createElement("div");
  sub.textContent = "Clips are on disk. Assemble to build the final video.";
  sub.style.color = "#c8c8d0";
  sub.style.fontSize = "13px";
  sub.style.marginBottom = "12px";
  var b = document.createElement("button");
  b.id = "reassemblebtn";
  b.textContent = "Assemble from clips";
  b.style.background = "#d4a017";
  b.style.color = "#161620";
  b.style.fontWeight = "600";
  b.style.padding = "9px 16px";
  b.style.fontSize = "13px";
  b.style.border = "none";
  b.style.borderRadius = "6px";
  b.style.cursor = "pointer";
  var msg = document.createElement("span");
  msg.id = "reassemblemsg";
  msg.style.color = "#8a8a99";
  msg.style.fontSize = "12px";
  msg.style.marginLeft = "8px";
  panel.appendChild(head); panel.appendChild(sub); panel.appendChild(b); panel.appendChild(msg);
  slot.innerHTML = "";
  slot.appendChild(panel);
  b.onclick = function() { reassemble(ch, pr); };
}

function renderTopPlaceholder() {'''

# ---- Edit D: floor-all button in the section toolbar (no cssText) ----
D_ANCHOR = '''  const btn = function(label, key, count) {'''
D_NEW = '''  if (!window.__FLOOR_BTN_WIRED) {
    window.__FLOOR_BTN_WIRED = true;
    setTimeout(function() {   // FLOORFIRST_UI_APPLIED
      var bar = document.getElementById("sectionbar");
      if (bar && !document.getElementById("floorallbtn")) {
        var fb = document.createElement("button");
        fb.id = "floorallbtn";
        fb.textContent = "Floor all (free)";
        fb.title = "Every beat -> free Ken-Burns floor (kling_count:0). Add Kling back per-beat with the motion presets.";
        fb.style.marginLeft = "12px";
        fb.style.background = "#2a2a36";
        fb.style.color = "#d4a017";
        fb.style.border = "1px solid #d4a017";
        fb.style.borderRadius = "6px";
        fb.style.padding = "6px 12px";
        fb.style.cursor = "pointer";
        fb.style.font = "12px ui-monospace,monospace";
        fb.onclick = async function() {
          var c = (window.__SB_CTX || {});
          if (!c.ch || !c.pr) return;
          fb.disabled = true; fb.textContent = "flooring...";
          try {
            await api("/api/floor_all", {method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({channel: c.ch, project: c.pr})});
          } catch (e) {}
          window.__FLOOR_BTN_WIRED = false;
          renderStoryboard(c.ch, c.pr);
        };
        bar.appendChild(fb);
      } else {
        window.__FLOOR_BTN_WIRED = false;
      }
    }, 50);
  }
  const btn = function(label, key, count) {'''

# ---- Edit E: preset auto-enroll into kling_override ----
E_ANCHOR = '''        saveMotion();'''
E_NEW = '''        (async function() {   // FLOORFIRST_UI_APPLIED: enroll beat into kling_override
          var pbeat = parseInt((box.getAttribute("data-mkey") || "").split("/").pop(), 10);
          if (!isNaN(pbeat) && !(window.__KLING_SET && window.__KLING_SET[pbeat])) {
            try {
              var r3 = await api("/api/kling_override", {method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({channel: CH, project: PR, beat: pbeat})});
              if (r3 && r3.ok) { if (!window.__KLING_SET) window.__KLING_SET = {}; window.__KLING_SET[pbeat] = 1; }
            } catch (e) {}
          }
        })();
        saveMotion();'''

# ---- Edit F: server handlers, inserted before _handle_inherit_toggle ----
F_ANCHOR = '''    def _handle_inherit_toggle(self, body):'''
F_NEW = '''    def _handle_kling_override_toggle(self, body):
        """FLOORFIRST_UI_APPLIED. Add/remove a beat in kling_override; on ADD,
        remove from kb_override + inherit_prev (one mode per beat) and delete the
        beat's free .kbfloor clip so batch animate re-renders it Kling."""
        import json as _json
        try:
            beat = int(body.get("beat"))
        except Exception:
            self._json(400, {"ok": False, "error": "beat must be an integer"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project"}); return
        paths = resolve_paths(ch, pr, _REPO)
        rp = paths["project"] / "render_policy.json"
        existing = {}
        if rp.is_file():
            try:
                existing = _json.loads(rp.read_text()) or {}
            except Exception:
                existing = {}
        try:
            kl = sorted({int(x) for x in existing.get("kling_override", [])})
        except Exception:
            kl = []
        if beat in kl:
            kl = [b for b in kl if b != beat]; on = False
        else:
            kl = sorted(kl + [beat]); on = True
        policy = dict(existing)
        if on:
            for _sib in ("kb_override", "inherit_prev"):
                try:
                    _v = sorted({int(x) for x in existing.get(_sib, [])} - {beat})
                except Exception:
                    _v = []
                if _v: policy[_sib] = _v
                else: policy.pop(_sib, None)
        if kl: policy["kling_override"] = kl
        else: policy.pop("kling_override", None)
        try:
            rp.write_text(_json.dumps(policy, indent=2))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"write failed: {e}"}); return
        if on:
            try:
                _shot = beat + 1
                idx = paths["project"] / "_index.json"
                if idx.is_file():
                    _m = _json.loads(idx.read_text())
                    for _k, _v in _m.items():
                        if int(_v) == beat: _shot = int(_k); break
                _c = paths["project"] / "modea" / "clips"
                _mk = _c / ("shot_%03d.kbfloor" % _shot)
                if _mk.exists():
                    _mk.unlink(missing_ok=True)
                    (_c / ("shot_%03d.mp4" % _shot)).unlink(missing_ok=True)
            except Exception:
                pass
        self._json(200, {"ok": True, "on": on, "beat": beat, "kling_override": kl}); return

    def _handle_floor_all(self, body):
        """FLOORFIRST_UI_APPLIED. kling_count:0 + clear the three per-beat lists."""
        import json as _json
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project"}); return
        paths = resolve_paths(ch, pr, _REPO)
        rp = paths["project"] / "render_policy.json"
        existing = {}
        if rp.is_file():
            try:
                existing = _json.loads(rp.read_text()) or {}
            except Exception:
                existing = {}
        policy = dict(existing)
        policy["kling_count"] = 0
        for _k in ("kling_override", "kb_override", "inherit_prev"):
            policy.pop(_k, None)
        try:
            rp.write_text(_json.dumps(policy, indent=2))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"write failed: {e}"}); return
        self._json(200, {"ok": True, "floored": True, "kling_count": 0}); return

    def _handle_inherit_toggle(self, body):'''

# ---- Edit G: POST routes ----
G_ANCHOR = '''        if path == "/api/kb_toggle":
            self._handle_kb_toggle(body); return'''
G_NEW = '''        if path == "/api/kling_override":   # FLOORFIRST_UI_APPLIED
            self._handle_kling_override_toggle(body); return
        if path == "/api/floor_all":        # FLOORFIRST_UI_APPLIED
            self._handle_floor_all(body); return
        if path == "/api/kb_toggle":
            self._handle_kb_toggle(body); return'''


def die(m):
    print(f"FAIL: {m}  Nothing written.", file=sys.stderr); sys.exit(1)


def main():
    if not TARGET.is_file():
        die(f"target not found: {TARGET}")
    src = TARGET.read_text()
    if SENTINEL in src:
        print("Already applied (sentinel present). No-op."); return
    edits = [("A", A_ANCHOR, A_NEW), ("B", B_ANCHOR, B_NEW), ("C", C_ANCHOR, C_NEW),
             ("D", D_ANCHOR, D_NEW), ("E", E_ANCHOR, E_NEW), ("F", F_ANCHOR, F_NEW),
             ("G", G_ANCHOR, G_NEW)]
    for label, anchor, _ in edits:
        n = src.count(anchor)
        if n != 1:
            die(f"anchor {label} matched {n} times (need 1) — file drifted.")
    new = src
    for _, anchor, repl in edits:
        new = new.replace(anchor, repl, 1)
    new = new.replace('APP_VERSION = "v3.9"', 'APP_VERSION = "v3.9.2"', 1)
    for need in (SENTINEL, "renderAssemblePanel", "floorallbtn", "_handle_floor_all",
                 "/api/floor_all", "/api/kling_override", 'APP_VERSION = "v3.9.2"'):
        if need not in new:
            die(f"post-edit check failed (missing {need}).")
    if "cssText" in new[new.index("renderAssemblePanel"):new.index("renderTopPlaceholder")]:
        die("cssText found in new panel code — must use .style.prop assignments.")
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
        tf.write(new); tmp = tf.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        die(f"py_compile failed: {e}")
    finally:
        Path(tmp).unlink(missing_ok=True)
    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(new)
    print(f"OK — patched {TARGET.name}  (floor-first UI, no cssText; v3.9.2)")
    print(f"     backup: {BACKUP.name}")


if __name__ == "__main__":
    main()
