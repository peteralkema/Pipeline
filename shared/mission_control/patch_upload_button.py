#!/usr/bin/env python3
"""
patch_upload_button.py - wire the FINAL VIDEO panel's Upload button to a real
/api/upload that shells the proven channel-agnostic upload_episode.py.

WHY
  upload_episode.py is proven end-to-end (gustloff uploaded; five channels have
  Production tokens bound to the right YouTube channel). The only missing piece is
  the server route + button wiring. The panel already shows the assembled video,
  metadata (/api/meta), Download, and Re-assemble; the Upload button is a disabled
  placeholder ("next session"). This makes it live.

WHAT THIS DOES (one file, shared/mission_control/pipeline_server.py)
  backend:
    - _UPLOAD_JOBS dict + _UPLOAD_LOCK + _upload_key(ch,pr)  (mirrors _ASSEMBLE_JOBS)
    - _run_upload_bg(): shells `sys.executable upload_episode.py --project
      <channel>/projects/<slug> --privacy private`, cwd=_REPO; parses the printed
      video ID / Studio URL on success; surfaces the batch-exit-gate message.
    - _handle_upload(body): start-or-already, mirrors _handle_assemble.
    - _handle_upload_status(ch,pr): mirrors _handle_assemble_status.
    - GET  /api/upload_status  and  POST /api/upload  routes.
  frontend (inside renderDonePanel + a new uploadVideo()):
    - the disabled red button becomes an enabled "Upload to YouTube Studio
      (private)" button wired to uploadVideo(ch, pr).
    - uploadVideo(): POST /api/upload, then poll /api/upload_status; on done show
      the Studio link + video id; on batch-exit show the parts message; on error
      show it. Mirrors reassemble().

  SAFETY: privacy is hard-pinned to "private" -- the button can never publish.
  Review + Altered-content=Yes happen in Studio.

DISCIPLINE
  Idempotent (sentinel: `def _run_upload_bg`). Anchors verified x1 on the original
  source before any write; backs up to .pre_uploadbtn; recompiles; node-checks the
  served page JS is not required here (we add matched JS), but we DO re-extract and
  py_compile the module. Rolls back on failure. Run from repo root on the LAPTOP,
  then commit/push, pull on box, then restart mission-control.service.
"""
import sys
import shutil
import py_compile
from pathlib import Path

PS = Path("shared/mission_control/pipeline_server.py")
SENTINEL = "def _run_upload_bg"


# ── 1. backend: jobs dict + bg runner (insert after the assemble bg runner) ──
# Anchor: the end of _run_assemble_bg is its final except block. We insert the
# upload machinery immediately after it, before the _FLUX_MODEL line.
BG_OLD = '''    except Exception as e:
        with _ASSEMBLE_LOCK:
            _ASSEMBLE_JOBS[key] = {"status": "error", "error": str(e)}

_FLUX_MODEL = "fal-ai/flux-pro/v1.1"'''

BG_NEW = '''    except Exception as e:
        with _ASSEMBLE_LOCK:
            _ASSEMBLE_JOBS[key] = {"status": "error", "error": str(e)}

# Per-(channel/project) upload status, keyed "channel/project". Module-level
# (mirrors _ASSEMBLE_JOBS) so upload works against the selected project.
_UPLOAD_JOBS = {}
_UPLOAD_LOCK = _threading.Lock()

def _upload_key(ch, pr):
    return f"{ch}/{pr}"

def _run_upload_bg(key, project_rel):
    """Shell the proven channel-agnostic upload_episode.py for this project.
    project_rel is the repo-relative project path (e.g. final-hours/projects/gustloff).
    Privacy is hard-pinned private here -- the button never publishes; review in Studio.
    Parses the printed video ID + Studio URL on success; surfaces the batch-exit-gate
    (parts>1 -> not uploaded) as a non-error 'skipped' status."""
    import subprocess as _sp
    try:
        cmd = [sys.executable, str(Path(_SHARED) / "upload_episode.py"),
               "--project", project_rel,
               "--privacy", "private"]
        r = _sp.run(cmd, cwd=str(_REPO), capture_output=True, text=True)
        out = (r.stdout or "") + "\\n" + (r.stderr or "")
        # batch-exit-gate: the script prints "batched job (...) -> not uploading"
        if "not uploading" in out.lower():
            line = next((ln.strip() for ln in out.splitlines()
                         if "not uploading" in ln.lower()), "batched job -- not uploaded")
            with _UPLOAD_LOCK:
                _UPLOAD_JOBS[key] = {"status": "skipped", "message": line}
            return
        if r.returncode != 0:
            tail = (r.stderr or r.stdout or "").strip().splitlines()[-4:]
            with _UPLOAD_LOCK:
                _UPLOAD_JOBS[key] = {"status": "error",
                    "error": " / ".join(tail) or "upload failed"}
            return
        # success: pull the video ID and Studio URL out of the output
        video_id = None
        studio = None
        for ln in out.splitlines():
            s = ln.strip()
            if "video ID:" in s:
                video_id = s.split("video ID:", 1)[1].strip()
            if "studio.youtube.com/video/" in s:
                studio = s.split("Studio:", 1)[1].strip() if "Studio:" in s else s
        if not studio and video_id:
            studio = "https://studio.youtube.com/video/" + video_id + "/edit"
        with _UPLOAD_LOCK:
            _UPLOAD_JOBS[key] = {"status": "done", "video_id": video_id, "studio": studio}
    except Exception as e:
        with _UPLOAD_LOCK:
            _UPLOAD_JOBS[key] = {"status": "error", "error": str(e)}

_FLUX_MODEL = "fal-ai/flux-pro/v1.1"'''


# ── 2. backend: the two handlers (insert after _handle_assemble_status) ──
HANDLERS_OLD = '''    def _handle_assemble_status(self, ch, pr):
        key = _assemble_key(ch, pr)
        with _ASSEMBLE_LOCK:
            st = dict(_ASSEMBLE_JOBS.get(key, {"status": "idle"}))
        self._json(200, st); return'''

HANDLERS_NEW = '''    def _handle_assemble_status(self, ch, pr):
        key = _assemble_key(ch, pr)
        with _ASSEMBLE_LOCK:
            st = dict(_ASSEMBLE_JOBS.get(key, {"status": "idle"}))
        self._json(200, st); return

    def _handle_upload(self, body):
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        try:
            paths = resolve_paths(ch, pr, _REPO)
            project_dir = Path(paths["project"])
            project_rel = str(project_dir.resolve().relative_to(Path(_REPO).resolve()))
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)}); return
        video = project_dir / "final_video.mp4"
        if not video.exists():
            self._json(404, {"ok": False, "error": "no final_video.mp4 to upload"}); return
        key = _upload_key(ch, pr)
        with _UPLOAD_LOCK:
            running = (_UPLOAD_JOBS.get(key) or {}).get("status") == "running"
            if not running:
                _UPLOAD_JOBS[key] = {"status": "running"}
        if running:
            self._json(200, {"ok": True, "already": True}); return
        th = _threading.Thread(target=_run_upload_bg,
                               args=(key, project_rel), daemon=True)
        th.start()
        self._json(200, {"ok": True, "started": True}); return

    def _handle_upload_status(self, ch, pr):
        key = _upload_key(ch, pr)
        with _UPLOAD_LOCK:
            st = dict(_UPLOAD_JOBS.get(key, {"status": "idle"}))
        self._json(200, st); return'''


# ── 3. backend: GET route for /api/upload_status (next to assemble_status) ──
GET_OLD = '''        if path == "/api/assemble_status":
            q = parse_qs(parsed.query)
            self._handle_assemble_status(q.get("channel", [None])[0],
                                         q.get("project", [None])[0]); return'''

GET_NEW = '''        if path == "/api/assemble_status":
            q = parse_qs(parsed.query)
            self._handle_assemble_status(q.get("channel", [None])[0],
                                         q.get("project", [None])[0]); return
        if path == "/api/upload_status":
            q = parse_qs(parsed.query)
            self._handle_upload_status(q.get("channel", [None])[0],
                                       q.get("project", [None])[0]); return'''


# ── 4. backend: POST route for /api/upload (next to /api/assemble) ──
POST_OLD = '''        if path == "/api/assemble":
            self._handle_assemble(body); return'''

POST_NEW = '''        if path == "/api/assemble":
            self._handle_assemble(body); return
        if path == "/api/upload":
            self._handle_upload(body); return'''


# ── 5. frontend: the disabled button -> a live one wired to uploadVideo() ──
BTN_OLD = '''    '<button disabled title="Upload wiring next session (auth + /api/upload)" ' +
      'style="background:#ff0000;opacity:.4;cursor:not-allowed;">Upload to YouTube Studio</button>' +
    '<div style="color:#8a8a99;font-size:11px;margin-top:6px;">Upload goes live once auth + /api/upload are wired ' +
      '(next session). Download works now.</div>';'''

BTN_NEW = '''    '<button id="uploadbtn" ' +
      'style="background:#ff0000;">Upload to YouTube Studio (private)</button>' +
    '<span id="uploadmsg" style="color:#8a8a99;font-size:12px;margin-left:10px;"></span>' +
    '<div style="color:#8a8a99;font-size:11px;margin-top:6px;">Uploads as <b>private</b> '+
      '(review + set Altered-content = Yes in Studio before publishing).</div>';'''


# ── 6. frontend: bind the button after the re-assemble bind, + add uploadVideo() ──
BIND_OLD = '''  const rb = document.getElementById("reassemblebtn");
  if (rb) rb.onclick = function() { reassemble(ch, pr); };
}'''

BIND_NEW = '''  const rb = document.getElementById("reassemblebtn");
  if (rb) rb.onclick = function() { reassemble(ch, pr); };
  const ub = document.getElementById("uploadbtn");
  if (ub) ub.onclick = function() { uploadVideo(ch, pr); };
}

async function uploadVideo(ch, pr) {
  const btn = document.getElementById("uploadbtn");
  const msg = document.getElementById("uploadmsg");
  if (btn) { btn.disabled = true; btn.textContent = "Uploading…"; }
  if (msg) { msg.style.color = "#8a8a99"; msg.textContent = "starting upload…"; }
  try {
    await api("/api/upload", {method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({channel: ch, project: pr})});
  } catch (e) {
    if (msg) { msg.style.color = "#d46a6a"; msg.textContent = "failed to start"; }
    if (btn) { btn.disabled = false; btn.textContent = "Upload to YouTube Studio (private)"; }
    return;
  }
  const t0 = Date.now();
  const poll = setInterval(async function() {
    let st = {};
    try {
      st = await api("/api/upload_status?channel=" + encodeURIComponent(ch) +
                     "&project=" + encodeURIComponent(pr));
    } catch (e) { return; }
    if (st.status === "done") {
      clearInterval(poll);
      if (btn) { btn.disabled = true; btn.textContent = "✓ Uploaded (private)"; }
      if (msg) {
        msg.style.color = "#1c7c4a";
        const link = st.studio
          ? ('<a href="' + st.studio + '" target="_blank" style="color:#5b9bd5;">open in Studio</a>')
          : "";
        msg.innerHTML = "uploaded — " + (st.video_id || "") + "  " + link +
          "  · set Altered-content = Yes before publishing.";
      }
    } else if (st.status === "skipped") {
      clearInterval(poll);
      if (btn) { btn.disabled = false; btn.textContent = "Upload to YouTube Studio (private)"; }
      if (msg) { msg.style.color = "#b58900"; msg.textContent = st.message || "batched job — not uploaded"; }
    } else if (st.status === "error") {
      clearInterval(poll);
      if (btn) { btn.disabled = false; btn.textContent = "Upload to YouTube Studio (private)"; }
      if (msg) { msg.style.color = "#d46a6a"; msg.textContent = "error: " + (st.error || "upload failed"); }
    } else if (Date.now() - t0 > 1800000) {
      clearInterval(poll);
      if (msg) { msg.style.color = "#b58900"; msg.textContent = "timed out (may still be running on the box)"; }
      if (btn) { btn.disabled = false; btn.textContent = "Upload to YouTube Studio (private)"; }
    }
  }, 3000);
}'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not PS.exists():
        die(f"{PS} not found - run from the repo root on the laptop.")

    src = PS.read_text()
    if SENTINEL in src:
        print("Already applied (sentinel present) - no changes made.")
        return

    edits = [
        ("backend bg runner", BG_OLD, BG_NEW),
        ("backend handlers", HANDLERS_OLD, HANDLERS_NEW),
        ("GET route", GET_OLD, GET_NEW),
        ("POST route", POST_OLD, POST_NEW),
        ("frontend button", BTN_OLD, BTN_NEW),
        ("frontend bind + uploadVideo", BIND_OLD, BIND_NEW),
    ]

    for label, old, _ in edits:
        c = src.count(old)
        if c != 1:
            die(f"{label} anchor found {c}x (expected 1) - nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)

    if SENTINEL not in new:
        die("sentinel not present after edits - aborting.")

    bak = PS.with_suffix(PS.suffix + ".pre_uploadbtn")
    shutil.copy2(PS, bak)
    PS.write_text(new)

    try:
        py_compile.compile(str(PS), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(bak, PS)
        die(f"{PS} does not compile - restored from backup.\n{e}")

    print("OK patched:")
    print(f"   {PS}   (backup: {bak.name})")
    print("Upload button is now live (private-only). Bump APP_VERSION and restart on the box.")
    print()
    print("AFTER pull on the box:")
    print("   systemctl --user restart mission-control.service")
    print("   then hard-refresh the tab and version-check the heading SHA.")


if __name__ == "__main__":
    main()
