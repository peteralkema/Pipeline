#!/usr/bin/env python3
"""
patch_tiered_gate_field.py — TIERED RENDER step (c): the N field at the stills gate.

WHY
  Routing (step b) reads render_policy.json {"kling_count": N} (default 40). This
  lets you SET that N per-project from the stills gate before Generate Clips — the
  cost lever becomes a daily control instead of a default.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  Backend:
    - _handle_render_policy_get(ch, pr): read N from <project>/render_policy.json
      (default 40).
    - _handle_render_policy_post(body): write {"kling_count": N} to <project>/
      render_policy.json (the exact file the engine's _tiered_kling_count reads,
      next to durations.json).
    - GET  /api/render_policy?channel=&project=
    - POST /api/render_policy {channel, project, kling_count}
  Frontend:
    - the stills gate bar gains a number field "Kling clips: first [N] beats — the
      rest render free (Ken Burns zoom)", pre-filled with the current N and saved
      on change (with a small saved/failed confirmation).

  The saved N drives the NEXT Generate Clips run (the batch loop reads the file).
  Step (d) — the once-off button consulting the same N — comes next.

DISCIPLINE
  Idempotent (sentinel: `def _handle_render_policy_get`). Four anchors, each
  verified once; backs up to .pre_tieredgate; re-compiles + rolls back on failure.
  Run from the repo root on the LAPTOP, then commit/push, then pull + restart +
  node-check on the box (this IS the always-on server, and the JS changed).
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "def _handle_render_policy_get"

# 1. Backend handlers (before _handle_animate)
ANCHOR_HANDLERS = "    def _handle_animate(self, body):"
NEW_HANDLERS = '''    def _handle_render_policy_get(self, ch, pr):
        """Read TIERED RENDER N for a project: render_policy.json kling_count (default 40)."""
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "channel + project required"}); return
        import json as _json
        paths = resolve_paths(ch, pr, _REPO)
        rp = paths["project"] / "render_policy.json"
        n = 40
        if rp.is_file():
            try:
                n = int(_json.loads(rp.read_text()).get("kling_count", 40))
            except Exception:
                n = 40
        self._json(200, {"ok": True, "kling_count": n, "default": 40}); return

    def _handle_render_policy_post(self, body):
        """Write TIERED RENDER N to render_policy.json at the project root (next to durations.json)."""
        import json as _json
        try:
            kc = max(0, int(body.get("kling_count")))
        except Exception:
            self._json(400, {"ok": False, "error": "kling_count must be a non-negative integer"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        paths = resolve_paths(ch, pr, _REPO)
        rp = paths["project"] / "render_policy.json"
        try:
            rp.write_text(_json.dumps({"kling_count": kc}, indent=2))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"write failed: {e}"}); return
        self._json(200, {"ok": True, "kling_count": kc}); return

    def _handle_animate(self, body):'''

# 2. GET route (after /api/state)
ANCHOR_GET = '''        if path == "/api/state":
            self._json(200, build_state()); return'''
NEW_GET = '''        if path == "/api/state":
            self._json(200, build_state()); return
        if path == "/api/render_policy":
            q = parse_qs(parsed.query)
            self._handle_render_policy_get(q.get("channel", [None])[0],
                                           q.get("project", [None])[0]); return'''

# 3. POST route (before /api/restill)
ANCHOR_POST = '''        if path == "/api/restill":
            self._handle_restill(body); return'''
NEW_POST = '''        if path == "/api/render_policy":
            self._handle_render_policy_post(body); return
        if path == "/api/restill":
            self._handle_restill(body); return'''

# 4. Frontend: add the N field + prefill/save to the stills gate bar
ANCHOR_JS = '''  } else if (g.name === "stills") {
    const n = (g.payload && g.payload.stills_count) || "";
    bar.innerHTML = '<div class="panel gate">' +
      '<label>Stills gate — review before clips</label>' +
      '<div>' + n + ' stills rendered. Review the body below (AI Fix / Regenerate any that break), then decide.</div>' +
      '<div class="row">' +
        '<button onclick="gate(' + _SQ + 'go' + _SQ + ')">Generate Clips (approve stills)</button>' +
        '<button class="secondary" onclick="gate(' + _SQ + 'skip' + _SQ + ')">Stop here (keep stills, no clips)</button>' +
      '</div></div>';'''
NEW_JS = '''  } else if (g.name === "stills") {
    const n = (g.payload && g.payload.stills_count) || "";
    bar.innerHTML = '<div class="panel gate">' +
      '<label>Stills gate — review before clips</label>' +
      '<div>' + n + ' stills rendered. Review the body below (AI Fix / Regenerate any that break), then decide.</div>' +
      '<div class="row" style="margin:10px 0;align-items:center;">' +
        '<label style="margin:0 8px 0 0;text-transform:none;letter-spacing:0;color:#e8e6e3;">Kling clips: first</label>' +
        '<input id="klingn" type="number" min="0" step="1" value="40" style="width:80px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:6px 8px;">' +
        '<span style="color:#8a8a99;margin-left:8px;">beats — the rest render free (Ken Burns zoom). <span id="klingmsg" style="color:#14a3b8;"></span></span>' +
      '</div>' +
      '<div class="row">' +
        '<button onclick="gate(' + _SQ + 'go' + _SQ + ')">Generate Clips (approve stills)</button>' +
        '<button class="secondary" onclick="gate(' + _SQ + 'skip' + _SQ + ')">Stop here (keep stills, no clips)</button>' +
      '</div></div>';
    (async function() {
      const inp = document.getElementById("klingn");
      if (!inp) return;
      const ch = state.channel, pr = state.project;
      try {
        const r = await api("/api/render_policy?channel=" + encodeURIComponent(ch) +
                            "&project=" + encodeURIComponent(pr));
        if (r && r.ok && typeof r.kling_count === "number") inp.value = r.kling_count;
      } catch (e) {}
      inp.addEventListener("change", async function() {
        const v = parseInt(inp.value, 10);
        const msg = document.getElementById("klingmsg");
        if (isNaN(v) || v < 0) { if (msg) msg.textContent = "?"; return; }
        try {
          const rr = await api("/api/render_policy", {method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({channel: ch, project: pr, kling_count: v})});
          if (msg) msg.textContent = (rr && rr.ok) ? ("saved N=" + rr.kling_count) : "save failed";
        } catch (e) { if (msg) msg.textContent = "save failed"; }
      });
    })();'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found — run this from the repo root on the laptop.")

    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) — no changes made.")
        return

    edits = [
        ("backend handlers", ANCHOR_HANDLERS, NEW_HANDLERS),
        ("GET route", ANCHOR_GET, NEW_GET),
        ("POST route", ANCHOR_POST, NEW_POST),
        ("stills gate field", ANCHOR_JS, NEW_JS),
    ]
    for label, old, _ in edits:
        n = src.count(old)
        if n == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written. "
                f"(Confirm A0/A4/motion patches are applied and the box is in sync.)")
        if n > 1:
            die(f"anchor for {label} found {n}x (expected 1) — ambiguous; nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_tieredgate")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    check = TARGET.read_text()
    problems = []
    if MARKER not in check:
        problems.append("_handle_render_policy_get missing")
    if check.count('"/api/render_policy"') < 2:
        problems.append("render_policy routes missing")
    if 'id="klingn"' not in check:
        problems.append("gate field missing")
    if problems:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed (" + "; ".join(problems) + ") — restored from backup.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile — restored from backup.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   /api/render_policy read+write + N field at the stills gate")
    print()
    print("AFTER you pull on the box, restart + node-check before trusting it:")
    print("   systemctl --user restart mission-control.service")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   print(\"script blocks:\", len(b))")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")


if __name__ == "__main__":
    main()
