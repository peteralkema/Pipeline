#!/usr/bin/env python3
"""
patch_floor_all_button.py — floor-first as a one-click MC workflow (v3.9.2).

Adds:
  1. _handle_kling_override_toggle — new endpoint mirroring _handle_kb_toggle:
     add beat to kling_override, drop from kb_override + inherit_prev (one mode
     per beat), and delete the beat's .kbfloor clip so batch animate re-renders
     it as a paid Kling atom (delete-on-upgrade: KB->Kling drops a FREE clip).
  2. _handle_floor_all — sets kling_count:0 and clears kling_override/kb_override/
     inherit_prev, so the whole project floors to free Ken-Burns ($0).
  3. POST routes for /api/kling_override and /api/floor_all.
  4. JS: preset click also enrolls the beat into kling_override (auto-enroll).
  5. JS: a "Floor all (free)" button in the section toolbar.
  6. APP_VERSION -> v3.9.2.

Idempotent (sentinel: FLOOR_ALL_APPLIED). Anchors verified once each; py_compile
before write; backup to pipeline_server.py.pre_floorall. Pure ASCII. No apostrophes
in JS string literals crossing the Python->JS layer.
"""
import sys, py_compile, tempfile, shutil
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_floorall")
SENTINEL = "FLOOR_ALL_APPLIED"

# --- Edit 1+2: two new handlers, inserted before _handle_inherit_toggle. ---
ANCHOR_HANDLER = '''    def _handle_inherit_toggle(self, body):'''

NEW_HANDLER = '''    def _handle_kling_override_toggle(self, body):
        """FLOOR_ALL_APPLIED. Toggle a beat in render_policy.json "kling_override"
        — floor-first additive Kling. Turning ON: add to kling_override, remove
        from kb_override + inherit_prev (one mode per beat), and delete the beat's
        free .kbfloor clip so batch animate re-renders it as a paid atom
        (KB->Kling drops a FREE clip; a paid clip has no marker so Kling->KB never
        deletes). MERGE-style; siblings otherwise untouched."""
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
            kl = sorted({int(x) for x in existing.get("kling_override", [])})
        except Exception:
            kl = []
        if beat in kl:
            kl = [b for b in kl if b != beat]
            on = False
        else:
            kl = sorted(kl + [beat])
            on = True
        policy = dict(existing)
        if on:
            for _sib in ("kb_override", "inherit_prev"):
                try:
                    _v = sorted({int(x) for x in existing.get(_sib, [])} - {beat})
                except Exception:
                    _v = []
                if _v:
                    policy[_sib] = _v
                else:
                    policy.pop(_sib, None)
        if kl:
            policy["kling_override"] = kl
        else:
            policy.pop("kling_override", None)
        try:
            rp.write_text(_json.dumps(policy, indent=2))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"write failed: {e}"}); return
        # delete-on-upgrade: drop the free floor clip so the beat re-renders Kling.
        if on:
            try:
                _shot = beat + 1  # 1-based shot id for a pure Mode A project
                idx = paths["project"] / "_index.json"
                if idx.is_file():
                    _m = _json.loads(idx.read_text())
                    for _k, _v in _m.items():
                        if int(_v) == beat:
                            _shot = int(_k); break
                _clips = paths["project"] / "modea" / "clips"
                _mark = _clips / ("shot_%03d.kbfloor" % _shot)
                _clip = _clips / ("shot_%03d.mp4" % _shot)
                if _mark.exists():
                    _mark.unlink(missing_ok=True)
                    _clip.unlink(missing_ok=True)
            except Exception:
                pass  # non-fatal: the engine also guards delete-on-upgrade at render
        self._json(200, {"ok": True, "on": on, "beat": beat, "kling_override": kl}); return

    def _handle_floor_all(self, body):
        """FLOOR_ALL_APPLIED. Floor-first reset: kling_count:0 + clear
        kling_override/kb_override/inherit_prev. Every beat -> free Ken-Burns,
        project cost $0. Craft (Kling) is then added back per-beat via presets."""
        import json as _json
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

# --- Edit 3: POST routes. Anchor on the launch route block tail. ---
ANCHOR_ROUTE = '''        if path == "/api/launch":
            ch = body.get("channel"); pr = body.get("project")
            dry = bool(body.get("dry", True))
            log = body.get("log", "normal")
            if not ch or not pr:
                self._json(400, {"ok": False, "error": "channel + project required"}); return
            _lr = launch_job(ch, pr, dry, log)
            if _lr.get("ok") is False:
                self._json(409, _lr); return            # refuse-if-live: not a success
            self._json(200, {"ok": True, **_lr}); return'''

NEW_ROUTE = ANCHOR_ROUTE + '''

        if path == "/api/kling_override":   # FLOOR_ALL_APPLIED
            self._handle_kling_override_toggle(body); return
        if path == "/api/floor_all":        # FLOOR_ALL_APPLIED
            self._handle_floor_all(body); return'''

# --- Edit 4: preset click auto-enrolls into kling_override. Anchor the tail of
#     the preset handler, right after the KB/inherit release, before box.value. ---
ANCHOR_PRESET = '''          if (cell.dataset.inhon === "1" && !isNaN(pbeat)) {
            const r2 = await api("/api/inherit_toggle", {method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({channel: CH, project: PR, beat: pbeat})});
            if (r2 && r2.ok) paintInherit(cell, r2.on);
          }
        } catch (e) { /* policy file re-read on next storyboard render */ }'''

NEW_PRESET = '''          if (cell.dataset.inhon === "1" && !isNaN(pbeat)) {
            const r2 = await api("/api/inherit_toggle", {method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({channel: CH, project: PR, beat: pbeat})});
            if (r2 && r2.ok) paintInherit(cell, r2.on);
          }
          // FLOOR_ALL_APPLIED: a preset click enrolls the beat into kling_override
          // (auto-enroll) so under floor-first (kling_count:0) it actually renders
          // Kling. Enroll only if not already on, so a re-click does not toggle off.
          if (!isNaN(pbeat) && !(window.__KLING_SET && window.__KLING_SET[pbeat])) {
            const r3 = await api("/api/kling_override", {method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({channel: CH, project: PR, beat: pbeat})});
            if (r3 && r3.ok) { if (!window.__KLING_SET) window.__KLING_SET = {}; window.__KLING_SET[pbeat] = 1; }
          }
        } catch (e) { /* policy file re-read on next storyboard render */ }'''

# --- Edit 5: paint kling_override set on policy read (so re-click does not toggle
#     off). Anchor the existing kb/inh set assignment. ---
ANCHOR_PAINT = '''      window.__KB_SET = kbOn; window.__INH_SET = inhOn;'''
NEW_PAINT = '''      const klOn = {}; ((r && r.kling_override) || []).forEach(function(b) { klOn[b] = 1; });
      window.__KB_SET = kbOn; window.__INH_SET = inhOn; window.__KLING_SET = klOn;  // FLOOR_ALL_APPLIED'''

# --- Edit 6: the Floor-all button in the section toolbar. Anchor the btn builder. ---
ANCHOR_BTN = '''  const btn = function(label, key, count) {
    const on = (sel === key);'''
NEW_BTN = '''  // FLOOR_ALL_APPLIED: project-level Floor-all action in the sticky toolbar.
  if (!window.__FLOOR_BTN_WIRED) {
    window.__FLOOR_BTN_WIRED = true;
    setTimeout(function() {
      const bar = document.getElementById("sectionbar");
      if (bar && !document.getElementById("floorallbtn")) {
        const fb = document.createElement("button");
        fb.id = "floorallbtn";
        fb.textContent = "Floor all (free)";
        fb.title = "Set every beat to the free Ken-Burns floor (kling_count:0). Add Kling back per-beat with the motion presets.";
        fb.style.cssText = "margin-left:12px;background:#2a2a36;color:#d4a017;border:1px solid #d4a017;border-radius:6px;padding:6px 12px;cursor:pointer;font:12px ui-monospace,monospace;";
        fb.onclick = async function() {
          const c = (window.__SB_CTX || {});
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
  const btn = function(label, key, count) {
    const on = (sel === key);'''


def die(msg):
    print(f"FAIL: {msg}  Nothing written.", file=sys.stderr)
    sys.exit(1)


def main():
    if not TARGET.is_file():
        die(f"target not found: {TARGET}")
    src = TARGET.read_text()
    if SENTINEL in src:
        print("Already applied (sentinel present). No-op.")
        return
    for chunk in (NEW_HANDLER, NEW_PRESET, NEW_PAINT, NEW_BTN):
        if "\\'" in chunk:
            die("apostrophe-in-JS guard tripped in patch source.")
    edits = (("handler", ANCHOR_HANDLER, NEW_HANDLER),
             ("route", ANCHOR_ROUTE, NEW_ROUTE),
             ("preset", ANCHOR_PRESET, NEW_PRESET),
             ("paint", ANCHOR_PAINT, NEW_PAINT),
             ("btn", ANCHOR_BTN, NEW_BTN))
    for label, anchor, _ in edits:
        n = src.count(anchor)
        if n != 1:
            die(f"anchor '{label}' matched {n} times (need exactly 1) — pipeline_server.py drifted.")
    new = src
    for _, anchor, repl in edits:
        new = new.replace(anchor, repl, 1)
    new = new.replace('APP_VERSION = "v3.9.1"', 'APP_VERSION = "v3.9.2"', 1)
    for need in (SENTINEL, "_handle_kling_override_toggle", "_handle_floor_all",
                 "/api/kling_override", "/api/floor_all", "floorallbtn",
                 'APP_VERSION = "v3.9.2"'):
        if need not in new:
            die(f"post-edit check failed (missing {need}).")
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
    print(f"OK — patched {TARGET.name}  (Floor-all + preset auto-enroll; v3.9.2)")
    print(f"     backup: {BACKUP.name}")


if __name__ == "__main__":
    main()
