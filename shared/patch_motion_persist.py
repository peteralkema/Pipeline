#!/usr/bin/env python3
"""
patch_motion_persist.py — persist typed motion direction (the /api/motion seam).

WHY
  The motion box drove Kling correctly but saved nothing: a body re-render
  repopulated it from storyboard.json's stored motion_prompt, so a typed edit
  vanished. build_beats_view reads motion_prompt fresh from storyboard.json
  every render, so writing the edit BACK to storyboard.json closes the loop — and
  because cmd_finish's batch loop reads the same storyboard.json[shot].motion_prompt,
  a saved edit also drives the BATCH animate, not just the once-off button.

  (Honest limit: a full RELAUNCH re-runs cmd_stills, which rewrites storyboard.json
  from the beat-script and would overwrite a saved motion. Survives re-render and
  batch animate within a run; not a relaunch. Durable fix = write to the beat-script
  too — deliberately out of scope here.)

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  Backend:
    - _handle_motion(body): resolve project per-request (channel+project or active
      job), load resolve_paths(...)["storyboard"], find the shot by 1-based engine
      index, set motion_prompt, write it back. Returns {ok, shot, saved}.
    - route POST /api/motion -> _handle_motion.
  Frontend (bindAnimateButtons):
    - the motion box saves on blur (type, click away -> saved).
    - "Render this clip" saves the current box value BEFORE firing Kling.
  Both post to /api/motion; the in-memory __MOTION_EDITS map still mirrors for
  instant feel, but the durable copy now lives on disk and repopulates the box.

DISCIPLINE
  Idempotent (sentinel: `def _handle_motion`). Anchors verified once each; backs
  up to .pre_motionpersist; re-compiles + rolls back on failure. Run from the repo
  root on the LAPTOP, then commit/push, then pull + restart + node-check on the box.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "def _handle_motion"

# ── Backend: add _handle_motion just before _handle_animate ──────────────────
ANCHOR_HANDLER = "    def _handle_animate(self, body):"
NEW_HANDLER = '''    def _handle_motion(self, body):
        """Persist a typed motion direction into storyboard.json[shot].motion_prompt.
        Resolved per-request like restill/animate. Drives both the once-off button
        and the batch animate, since both read storyboard.json's motion_prompt."""
        import json as _json
        shot_idx = body.get("shot")
        motion = (body.get("motion_prompt") or "").strip()
        if not isinstance(shot_idx, int):
            self._json(400, {"ok": False, "error": "shot must be an integer"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        paths = resolve_paths(ch, pr, _REPO)
        sb_path = paths["storyboard"]
        if not sb_path.is_file():
            self._json(404, {"ok": False, "error": "storyboard.json not found"}); return
        try:
            sb = _json.loads(sb_path.read_text())
        except Exception as e:
            self._json(500, {"ok": False, "error": f"storyboard parse failed: {e}"}); return
        hit = None
        for s in sb:
            if int(s.get("index", -1)) == shot_idx:
                hit = s; break
        if hit is None:
            self._json(404, {"ok": False, "error": f"shot {shot_idx} not in storyboard"}); return
        hit["motion_prompt"] = motion
        try:
            sb_path.write_text(_json.dumps(sb, indent=2))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"storyboard write failed: {e}"}); return
        self._json(200, {"ok": True, "shot": shot_idx, "saved": True}); return

    def _handle_animate(self, body):'''

# ── Backend: route POST /api/motion just before /api/animate ─────────────────
ANCHOR_ROUTE = '''        if path == "/api/animate":
            self._handle_animate(body); return'''
NEW_ROUTE = '''        if path == "/api/motion":
            self._handle_motion(body); return
        if path == "/api/animate":
            self._handle_animate(body); return'''

# ── Frontend: save-on-blur + save-before-render in bindAnimateButtons ────────
# Anchor on the start of the per-cell loop body so we can inject the blur save
# and a saveMotion() helper that the render handler also calls.
ANCHOR_JS = '''  wrap.querySelectorAll(".motioncell").forEach(function(cell) {
    const btn = cell.querySelector("button.animbtn");
    if (!btn) return;
    const shot = parseInt(cell.getAttribute("data-shot"), 10);
    const box = cell.querySelector("textarea.motionbox");
    const msg = cell.querySelector(".animmsg");'''
NEW_JS = '''  wrap.querySelectorAll(".motioncell").forEach(function(cell) {
    const btn = cell.querySelector("button.animbtn");
    const shot = parseInt(cell.getAttribute("data-shot"), 10);
    const box = cell.querySelector("textarea.motionbox");
    // motion-persist: write the typed direction to storyboard.json so it survives
    // a body re-render AND drives the batch animate (both read motion_prompt).
    async function saveMotion() {
      if (!box || isNaN(shot)) return;
      try {
        await api("/api/motion", {method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({channel: CH, project: PR, shot: shot,
                                motion_prompt: box.value})});
      } catch (e) { /* non-fatal: in-memory __MOTION_EDITS still holds it */ }
    }
    if (box) box.addEventListener("blur", saveMotion);
    if (!btn) return;
    const msg = cell.querySelector(".animmsg");'''

# ── Frontend: save before firing the Kling render ────────────────────────────
ANCHOR_FIRE = '''    btn.addEventListener("click", async function() {
      btn.disabled = true; const label0 = btn.textContent;
      btn.textContent = "Rendering (Kling)…";
      msg.style.color = "#8a8a99"; msg.textContent = "animating — this takes a bit…";'''
NEW_FIRE = '''    btn.addEventListener("click", async function() {
      btn.disabled = true; const label0 = btn.textContent;
      btn.textContent = "Rendering (Kling)…";
      msg.style.color = "#8a8a99"; msg.textContent = "animating — this takes a bit…";
      await saveMotion();  // persist the typed direction before it drives the render'''


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
        ("backend handler", ANCHOR_HANDLER, NEW_HANDLER),
        ("backend route", ANCHOR_ROUTE, NEW_ROUTE),
        ("frontend save-on-blur", ANCHOR_JS, NEW_JS),
        ("frontend save-before-render", ANCHOR_FIRE, NEW_FIRE),
    ]

    for label, old, _ in edits:
        n = src.count(old)
        if n == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written. "
                f"(Confirm A0/A4 patches are applied and the box is in sync.)")
        if n > 1:
            die(f"anchor for {label} found {n}x (expected 1) — ambiguous; nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_motionpersist")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    check = TARGET.read_text()
    problems = []
    if MARKER not in check:
        problems.append("_handle_motion missing")
    if '"/api/motion"' not in check:
        problems.append("/api/motion route missing")
    if "async function saveMotion" not in check:
        problems.append("saveMotion missing")
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
    print("   1) /api/motion endpoint writes storyboard.json[shot].motion_prompt")
    print("   2) motion box saves on blur")
    print("   3) Render this clip saves before firing")
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
