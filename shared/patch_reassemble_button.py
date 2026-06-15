#!/usr/bin/env python3
"""
patch_reassemble_button.py -- manual Re-assemble button in the FINAL VIDEO panel (v1.1).

WHY
  The launched run auto-assembles right after clips, so the per-clip re-render controls
  are moot unless you can re-stitch afterward. This adds a button (next to Download) that
  re-assembles final_video.mp4 from whatever clips are currently on disk -- so after you
  re-render a clip or two, you click it and the final video updates. No leg split, no gate,
  no orchestrate change: purely additive.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  1. _ASSEMBLE_JOBS/_ASSEMBLE_LOCK + _run_assemble_bg(key, cwd, engine_project): runs
     `python recreation_pipeline.py finish --project <slug>/modea --assemble-only` as a
     subprocess (re-stitch from existing clips/voice/music; no Kling/Inworld/fal/cost),
     updating a status dict -- mirrors _run_animate_bg.
     cwd = project_dir.parent (the channel's projects/ dir); --project = "<slug>/modea"
     -- the exact pair proven by the enoch1 run, so it can't hit the --plan CWD bug.
  2. /api/assemble (POST) -> resolve project, spawn the thread; /api/assemble_status (GET)
     -> poll. Mirrors /api/animate + /api/animate_status.
  3. Page: a "Re-assemble" button in the done-panel next to Download -> POST /api/assemble
     -> poll status -> on done, cache-bust the <video> src so the new cut loads in place.
  4. APP_VERSION -> v1.1.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `def _run_assemble_bg`). Anchors verified once;
  .pre_reassemble backup; py_compile + JS checks; rollback on failure. Requires v1.0.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "def _run_assemble_bg"

# --- 1. background runner + state, placed right after _run_animate_bg's block ----
# Anchor on the _FLUX_MODEL line that immediately follows _run_animate_bg.
OLD_AFTER_ANIM = '''_FLUX_MODEL = "fal-ai/flux-pro/v1.1"'''
NEW_AFTER_ANIM = '''# Per-(channel/project) assemble status, keyed "channel/project". Module-level
# (not the job record) so re-assemble works with no active job.
_ASSEMBLE_JOBS = {}
_ASSEMBLE_LOCK = _threading.Lock()

def _assemble_key(ch, pr):
    return f"{ch}/{pr}"

def _run_assemble_bg(key, cwd, engine_project):
    """Re-stitch final_video.mp4 from existing clips via `finish --assemble-only`
    (no render cost). Subprocess so it uses the same path resolution the legs do."""
    import subprocess as _sp
    try:
        cmd = [sys.executable, str(Path(_SHARED) / "recreation_pipeline.py"),
               "finish", "--project", engine_project, "--assemble-only"]
        r = _sp.run(cmd, cwd=str(cwd), capture_output=True, text=True)
        if r.returncode == 0:
            with _ASSEMBLE_LOCK:
                _ASSEMBLE_JOBS[key] = {"status": "done"}
        else:
            tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]
            with _ASSEMBLE_LOCK:
                _ASSEMBLE_JOBS[key] = {"status": "error", "error": " / ".join(tail) or "assemble failed"}
    except Exception as e:
        with _ASSEMBLE_LOCK:
            _ASSEMBLE_JOBS[key] = {"status": "error", "error": str(e)}

_FLUX_MODEL = "fal-ai/flux-pro/v1.1"'''

# --- 2a. handlers: add _handle_assemble + status, next to _handle_meta_get -------
OLD_META = '''    def _handle_meta_get(self, ch, pr):'''
NEW_META = '''    def _handle_assemble(self, body):
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        try:
            paths = resolve_paths(ch, pr, _REPO)
            project_dir = Path(paths["project"])
            cwd = project_dir.parent                 # the channel's projects/ dir
            engine_project = f"{project_dir.name}/modea"   # <slug>/modea (proven by enoch1)
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)}); return
        key = _assemble_key(ch, pr)
        with _ASSEMBLE_LOCK:
            running = (_ASSEMBLE_JOBS.get(key) or {}).get("status") == "running"
            if not running:
                _ASSEMBLE_JOBS[key] = {"status": "running"}
        if running:
            self._json(200, {"ok": True, "already": True}); return
        th = _threading.Thread(target=_run_assemble_bg,
                               args=(key, cwd, engine_project), daemon=True)
        th.start()
        self._json(200, {"ok": True, "started": True}); return

    def _handle_assemble_status(self, ch, pr):
        key = _assemble_key(ch, pr)
        with _ASSEMBLE_LOCK:
            st = dict(_ASSEMBLE_JOBS.get(key, {"status": "idle"}))
        self._json(200, st); return

    def _handle_meta_get(self, ch, pr):'''

# --- 2b. GET dispatch: add /api/assemble_status (next to /api/meta) --------------
OLD_GET = '''        if path == "/api/meta":
            q = parse_qs(parsed.query)
            self._handle_meta_get(q.get("channel", [None])[0],
                                  q.get("project", [None])[0]); return'''
NEW_GET = '''        if path == "/api/meta":
            q = parse_qs(parsed.query)
            self._handle_meta_get(q.get("channel", [None])[0],
                                  q.get("project", [None])[0]); return
        if path == "/api/assemble_status":
            q = parse_qs(parsed.query)
            self._handle_assemble_status(q.get("channel", [None])[0],
                                         q.get("project", [None])[0]); return'''

# --- 2c. POST dispatch: add /api/assemble (next to /api/animate) -----------------
OLD_POST = '''        if path == "/api/animate":
            self._handle_animate(body); return'''
NEW_POST = '''        if path == "/api/animate":
            self._handle_animate(body); return
        if path == "/api/assemble":
            self._handle_assemble(body); return'''

# --- 3. page: Re-assemble button next to Download in the done-panel ---------------
OLD_DL = '''    '<div style="margin-bottom:14px;">' +
      '<a href="' + vsrc + '" download style="display:inline-block;background:#2a2a36;color:#e8e6e3;' +
        'text-decoration:none;border-radius:6px;padding:8px 14px;font-weight:600;font-size:13px;">' +
        '&#8595; Download final video</a></div>' +'''
NEW_DL = '''    '<div style="margin-bottom:14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;">' +
      '<a href="' + vsrc + '" download style="display:inline-block;background:#2a2a36;color:#e8e6e3;' +
        'text-decoration:none;border-radius:6px;padding:8px 14px;font-weight:600;font-size:13px;">' +
        '&#8595; Download final video</a>' +
      '<button id="reassemblebtn" style="background:#2a2a36;margin-top:0;padding:8px 14px;font-size:13px;">' +
        '&#8635; Re-assemble (latest clips)</button>' +
      '<span id="reassemblemsg" style="color:#8a8a99;font-size:12px;"></span></div>' +'''

# wire the button after the panel is inserted (renderDonePanel inserts into #toppanel).
OLD_WIRE = '''  const slot = document.getElementById("toppanel");
  if (slot) { slot.innerHTML = ""; slot.appendChild(panel); }
}'''
NEW_WIRE = '''  const slot = document.getElementById("toppanel");
  if (slot) { slot.innerHTML = ""; slot.appendChild(panel); }
  const rb = document.getElementById("reassemblebtn");
  if (rb) rb.onclick = function() { reassemble(ch, pr); };
}

async function reassemble(ch, pr) {
  const btn = document.getElementById("reassemblebtn");
  const msg = document.getElementById("reassemblemsg");
  if (btn) btn.disabled = true;
  if (msg) msg.textContent = "assembling from latest clips...";
  try {
    await api("/api/assemble", {method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({channel: ch, project: pr})});
  } catch (e) {
    if (msg) msg.textContent = "failed to start"; if (btn) btn.disabled = false; return;
  }
  const t0 = Date.now();
  const poll = setInterval(async function() {
    let st = {};
    try {
      st = await api("/api/assemble_status?channel=" + encodeURIComponent(ch) +
                     "&project=" + encodeURIComponent(pr));
    } catch (e) { return; }
    if (st.status === "done") {
      clearInterval(poll);
      if (msg) msg.textContent = "re-assembled.";
      if (btn) btn.disabled = false;
      const v = document.querySelector("#donepanel video");
      if (v) { const base = v.src.split("&_t=")[0]; v.src = base + "&_t=" + Date.now(); v.load(); }
    } else if (st.status === "error") {
      clearInterval(poll);
      if (msg) msg.textContent = "error: " + (st.error || "assemble failed");
      if (btn) btn.disabled = false;
    } else if (Date.now() - t0 > 600000) {
      clearInterval(poll);
      if (msg) msg.textContent = "timed out (still running on the box)";
      if (btn) btn.disabled = false;
    }
  }, 2000);
}'''

OLD_VER = '''APP_VERSION = "v1.0"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
NEW_VER = '''APP_VERSION = "v1.1"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found -- run from the repo root on the laptop.")
    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) -- no changes made.")
        return
    if OLD_VER not in src:
        die("APP_VERSION v1.0 anchor not found -- apply patch_audio_stills_seam.py (v1.0) first. Nothing written.")
    # _SHARED must exist (used by the subprocess path).
    if "_SHARED" not in src:
        die("_SHARED not found in pipeline_server.py -- the assemble subprocess needs it to "
            "locate recreation_pipeline.py. Check the module's path constants. Nothing written.")

    edits = [
        ("assemble bg runner", OLD_AFTER_ANIM, NEW_AFTER_ANIM),
        ("assemble handlers",  OLD_META,       NEW_META),
        ("GET dispatch",       OLD_GET,        NEW_GET),
        ("POST dispatch",      OLD_POST,       NEW_POST),
        ("download row",       OLD_DL,         NEW_DL),
        ("panel wire",         OLD_WIRE,       NEW_WIRE),
        ("version bump",       OLD_VER,        NEW_VER),
    ]
    for label, old, _ in edits:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND -- file shape changed; nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) -- ambiguous; nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_reassemble")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    problems = []
    if MARKER not in chk: problems.append("bg runner missing")
    if "def _handle_assemble" not in chk: problems.append("handler missing")
    if "/api/assemble" not in chk: problems.append("route missing")
    if "function reassemble" not in chk: problems.append("button JS missing")
    if 'APP_VERSION = "v1.1"' not in chk: problems.append("version not bumped")
    if problems:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed (" + "; ".join(problems) + ") -- restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile -- restored.\n{e}")

    print(f"OK patched {TARGET}  (backup {backup.name})")
    print("   Re-assemble button added to the FINAL VIDEO panel; /api/assemble runs")
    print("   finish --assemble-only in the background and reloads the video on done.")
    print()
    print("AFTER pull on the box: restart, verify v1.1, node-check:")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   curl -s \"http://127.0.0.1:8002/api/state?key=fh2026\" | python3 -c \"import sys,json;d=json.load(sys.stdin);print(d.get('version'),d.get('sha'))\"")
    print("   git rev-parse --short HEAD")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")


if __name__ == "__main__":
    main()
