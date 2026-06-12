"""
Mission Control — Phase 2a: the coordinator service.

A SEPARATE always-on server (port 8002 by default) from the existing
serve_review.py / review.service (8001) — which we leave completely untouched
until Mission Control is proven. This server:

  - serves the control-panel page DYNAMICALLY (generated in-process, not a baked
    review.html) — so feature changes appear on a service RESTART, not a
    per-project regenerate;
  - resolves the active channel/project PER REQUEST from the job record
    (no boot-pinned project, no symlink cache — the stale-server bug can't exist);
  - reuses serve_review.py's proven auth (_key_ok: stateless X-Review-Key /
    ?key=, NO sessions, NO expiry) and image sniff — shared, not forked;
  - spawns the orchestrator as a DETACHED SUBPROCESS (--gate-mode job --job-id),
    so a server restart never kills a running render (the spec's §3.1 resilience);
  - exposes a small JSON API: /api/state, /api/launch, /api/gate/<name>,
    /api/channels, /api/projects.

Run (box):
  python shared/mission_control/pipeline_server.py --host 0.0.0.0 --port 8002 --key fh2026

Then open  http://116.202.18.68:8002/?key=fh2026

This is Phase 2a: dropdowns + Launch + phase polling + a BARE audio gate
(Accept/Swap). No stills body yet, no rich panels — that's 2b/3. The point of
2a is to prove the loop: pick -> Launch -> watch phase advance -> decide a gate
over HTTP -> run continues, against the REAL orchestrator, detached.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

# --- path setup so we can reuse serve_review + our own modules as siblings ---
_SHARED = Path(__file__).resolve().parents[1]          # shared/
_MC = Path(__file__).resolve().parent                   # shared/mission_control/
_REPO = _SHARED.parent                                  # repo root
for p in (str(_SHARED), str(_MC)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Reuse the PROVEN auth + image sniff from serve_review (one copy, never forked).
try:
    from serve_review import _key_ok as _sr_key_ok, _sniff_media_type, SERVER_KEY as _SR_KEY  # noqa
except Exception:
    _sr_key_ok = None
    def _sniff_media_type(data: bytes) -> str:
        if data[:8] == b"\x89PNG\r\n\x1a\n": return "image/png"
        if data[:3] == b"\xff\xd8\xff": return "image/jpeg"
        return "image/png"

from gate_protocol import (
    read_job, write_job, init_job, jobs_dir, job_path,
)
from build_view import build_beats_view, resolve_paths


# Module-global key, set by main(). Our own _key_ok mirrors serve_review's
# stateless model exactly (no sessions, no expiry — a hard spec constraint).
SERVER_KEY = None


def _key_ok(handler) -> bool:
    if not SERVER_KEY:
        return True
    parsed = urlparse(handler.path)
    p = unquote(parsed.path)
    # static assets + health are exempt (carry no key in <img>/<video> tags)
    if p.startswith("/stills/") or p.startswith("/clips/") or p.startswith("/video/") or p == "/api/health":
        return True
    q = parse_qs(parsed.query)
    if q.get("key", [""])[0] == SERVER_KEY:
        return True
    return handler.headers.get("X-Review-Key", "") == SERVER_KEY


# --------------------------------------------------------------------------
# Discovery: channels (folders with channel.json) and their projects
# --------------------------------------------------------------------------

def list_channels() -> list[str]:
    out = []
    for d in sorted(_REPO.iterdir()):
        if d.is_dir() and (d / "channel.json").is_file():
            out.append(d.name)
    return out


def list_projects(channel: str) -> list[str]:
    # channel here is a folder name (hyphen form). projects live under projects/.
    pdir = _REPO / channel / "projects"
    if not pdir.is_dir():
        return []
    return sorted(d.name for d in pdir.iterdir()
                  if d.is_dir() and (d / "beats_full.json").is_file()
                  or (d.is_dir() and (d / "script.md").is_file()))


def _channel_header_name(channel_folder: str) -> str:
    """The `channel:` header value scripts use (underscore form) for a folder."""
    return channel_folder.replace("-", "_")


# --------------------------------------------------------------------------
# Job lifecycle: the "active job" is just the most-recent job record.
# (One operator, one run at a time — Phase 2a keeps this simple and honest.)
# --------------------------------------------------------------------------

def active_job_id() -> str | None:
    jobs = sorted(jobs_dir(_REPO).glob("*.json"),
                  key=lambda p: p.stat().st_mtime, reverse=True)
    return jobs[0].stem if jobs else None


def launch_job(channel_folder: str, project: str, dry_run: bool, log: str) -> dict:
    """Spawn orchestrate.py as a DETACHED subprocess in gate-mode=job.
    Returns {job_id}. The render runs in its own process group, so restarting
    THIS server never kills it."""
    header_channel = _channel_header_name(channel_folder)
    beats_full = _REPO / channel_folder / "projects" / project / "beats_full.json"
    job_id = f"{header_channel}__{project}__{int(time.time())}"

    # Pre-create the job record so /api/state has something immediately.
    init_job(job_id, header_channel, project, _REPO)

    py = sys.executable  # the venv python running this server
    cmd = [
        py, str(_SHARED / "orchestrate.py"),
        "--project", project,
        "--beats", str(beats_full),
        "--log", log,
        "--gate-mode", "job",
        "--job-id", job_id,
    ]
    if dry_run:
        cmd.append("--dry-run")
    else:
        cmd.append("--live")  # skip the interactive kickoff prompt

    # Detach: new session so it survives this server restarting. Logs to a file
    # in the job dir so we can surface them later (no live streaming in v1).
    logf = open(jobs_dir(_REPO) / f"{job_id}.log", "ab")
    subprocess.Popen(
        cmd, cwd=str(_REPO),
        stdout=logf, stderr=subprocess.STDOUT,
        start_new_session=True,        # detach from this process group
    )
    return {"job_id": job_id, "cmd": " ".join(cmd)}


def decide_gate(job_id: str, decision: str) -> dict:
    """HTTP version of poke_gate: write the decision into the job record."""
    rec = read_job(job_id, _REPO)
    if not rec:
        return {"ok": False, "error": f"no such job: {job_id}"}
    gate = rec.get("gate")
    if not gate:
        return {"ok": False, "error": "job is not waiting at a gate"}
    if gate.get("status") == "decided":
        return {"ok": False, "error": f"gate already decided ({gate.get('decision')})"}
    options = gate.get("options", [])
    if options and decision not in options:
        return {"ok": False, "error": f"'{decision}' not in {options}"}
    gate["decision"] = decision
    rec["gate"] = gate
    write_job(job_id, rec, _REPO)
    return {"ok": True, "job_id": job_id, "decision": decision}


# --------------------------------------------------------------------------
# The /api/state payload — the single source the page renders from
# --------------------------------------------------------------------------

def build_state() -> dict:
    jid = active_job_id()
    if not jid:
        return {"phase": "idle", "job_id": None,
                "channels": list_channels()}
    rec = read_job(jid, _REPO)
    phase = rec.get("phase", "running")
    state = {
        "phase": phase,
        "job_id": jid,
        "channel": rec.get("channel"),
        "project": rec.get("project"),
        "gate": rec.get("gate"),
        "channels": list_channels(),
    }
    # Once stills exist, attach the beats view so the body can render (2b/3 use it).
    if phase in ("gate_stills", "animating", "assembling", "done"):
        try:
            state["view"] = build_beats_view(rec["channel"], rec["project"], _REPO)
        except Exception as e:
            state["view_error"] = str(e)
    return state


# --------------------------------------------------------------------------
# The page (generated dynamically — restart to update, never a baked file)
# --------------------------------------------------------------------------

def render_page(key: str | None) -> str:
    keyq = f"?key={key}" if key else ""
    # Minimal Phase-2a page: dropdowns, Launch, phase line, bare audio gate.
    # Intentionally small — rich panels are 2b/3. State-driven: everything
    # renders from /api/state, nothing stored client-side.
    return """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mission Control</title>
<style>
  :root { color-scheme: dark; }
  body { background:#0a0a0f; color:#e8e6e3; font:15px/1.5 -apple-system,system-ui,sans-serif;
         margin:0; padding:24px; }
  h1 { font-size:18px; font-weight:600; letter-spacing:.02em; margin:0 0 20px; color:#d4a017; }
  .panel { background:#14141c; border:1px solid #23232e; border-radius:10px;
           padding:18px 20px; margin-bottom:16px; max-width:720px; }
  label { display:block; font-size:12px; text-transform:uppercase; letter-spacing:.06em;
          color:#8a8a99; margin:12px 0 4px; }
  select, button { font:inherit; }
  select { background:#1c1c26; color:#e8e6e3; border:1px solid #32323e; border-radius:6px;
           padding:8px 10px; min-width:280px; }
  select:disabled { opacity:.5; }
  button { background:#3b5bdb; color:#fff; border:0; border-radius:6px; padding:10px 18px;
           cursor:pointer; font-weight:600; margin-top:16px; }
  button.secondary { background:#2a2a36; }
  button:disabled { opacity:.4; cursor:not-allowed; }
  .phase { font-size:13px; color:#8a8a99; }
  .phase b { color:#d4a017; }
  .gate { border:1px solid #d4a017; }
  .row { display:flex; gap:12px; align-items:center; }
  .spin { color:#8a8a99; }
  code { background:#1c1c26; padding:1px 6px; border-radius:4px; font-size:13px; }
</style></head><body>
<h1>MISSION CONTROL</h1>
<div id="app"><div class="panel"><span class="spin">loading…</span></div></div>
<script>
const KEY = new URLSearchParams(location.search).get("key") || "";
const H = KEY ? {"X-Review-Key": KEY} : {};
async function api(path, opts={}) {
  opts.headers = Object.assign({}, H, opts.headers||{});
  const r = await fetch(path + (path.includes("?")?"":("?key="+KEY)), opts);
  return r.json();
}
let CH_PROJECTS = {};
async function loadProjects(folder) {
  if (CH_PROJECTS[folder]) return CH_PROJECTS[folder];
  const r = await api("/api/projects?channel="+encodeURIComponent(folder));
  CH_PROJECTS[folder] = r.projects || [];
  return CH_PROJECTS[folder];
}
function el(html){ const d=document.createElement("div"); d.innerHTML=html.trim(); return d.firstChild; }

async function renderIdle(state) {
  const app = document.getElementById("app");
  const channels = state.channels || [];
  app.innerHTML = "";
  const panel = el(`<div class="panel">
    <label>Channel</label>
    <select id="chan"></select>
    <label>Project</label>
    <select id="proj"><option>—</option></select>
    <label>Mode</label>
    <select id="mode">
      <option value="dry">Dry-run (plan only, no spend)</option>
      <option value="live">Live (renders — spends fal credits)</option>
    </select>
    <div class="row"><button id="launch" disabled>Launch</button></div>
  </div>`);
  app.appendChild(panel);
  const chan = panel.querySelector("#chan");
  const proj = panel.querySelector("#proj");
  const launch = panel.querySelector("#launch");
  chan.innerHTML = '<option value="">— pick a channel —</option>' +
     channels.map(c=>`<option value="${c}">${c}</option>`).join("");
  chan.onchange = async () => {
    proj.innerHTML = '<option>loading…</option>';
    launch.disabled = true;
    if (!chan.value) { proj.innerHTML='<option>—</option>'; return; }
    const ps = await loadProjects(chan.value);
    proj.innerHTML = '<option value="">— pick a project —</option>' +
      ps.map(p=>`<option value="${p}">${p}</option>`).join("");
  };
  proj.onchange = () => { launch.disabled = !(chan.value && proj.value); };
  launch.onclick = async () => {
    launch.disabled = true; launch.textContent = "Launching…";
    const mode = panel.querySelector("#mode").value;
    await api("/api/launch", {method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({channel:chan.value, project:proj.value, dry: mode==="dry"})});
    poll();
  };
}

function renderRunning(state) {
  const app = document.getElementById("app");
  const g = state.gate;
  let gateHtml = "";
  if (g && g.status === "waiting" && g.name === "audio") {
    const v = (g.payload && g.payload.voice_id) || "the channel voice";
    const m = (g.payload && g.payload.minutes) || "?";
    gateHtml = `<div class="panel gate">
      <label>Audio gate</label>
      <div>Voiceover produced — measured <b>${m}</b> min, voice: <b>${v}</b>.</div>
      <div class="row">
        <button onclick="gate('keep')">Accept (keep this read)</button>
        <button class="secondary" onclick="gate('swap')">Swap (use my own recording)</button>
      </div></div>`;
  } else if (g && g.status === "waiting" && g.name === "stills") {
    const n = (g.payload && g.payload.stills_count) || "?";
    gateHtml = `<div class="panel gate">
      <label>Stills gate</label>
      <div>${n} stills rendered. (Rich review body lands in the next phase.)</div>
      <div class="row">
        <button onclick="gate('go')">Generate Clips (approve stills)</button>
        <button class="secondary" onclick="gate('skip')">Skip</button>
      </div></div>`;
  }
  app.innerHTML = `<div class="panel">
      <div class="phase">job <code>${state.job_id}</code></div>
      <div class="phase">${state.channel} · ${state.project}</div>
      <div class="phase">phase: <b>${state.phase}</b>
        ${(!g||g.status!=="waiting") ? '<span class="spin"> — working…</span>' : ''}</div>
    </div>` + gateHtml;
}

async function gate(decision) {
  const s = await api("/api/state");
  await api("/api/gate/"+ (s.gate?s.gate.name:"") , {method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({decision})});
  poll();
}

let LAST_RENDER_KEY = null;
function renderKey(state) {
  // re-render only when something the user SEES changes:
  // phase, or which gate is waiting, or its status.
  const g = state.gate || {};
  return [state.phase, state.job_id, g.name, g.status].join("|");
}
async function poll() {
  const state = await api("/api/state");
  const key = renderKey(state);
  if (key === LAST_RENDER_KEY) return;   // nothing visible changed -> don't clobber the DOM
  LAST_RENDER_KEY = key;
  if (state.phase === "idle") renderIdle(state);
  else renderRunning(state);
}
poll();
setInterval(poll, 2500);
</script>
</body></html>"""


# --------------------------------------------------------------------------
# HTTP handler
# --------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write(f"  {self.address_string()} - {fmt % args}\n")

    def _json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _html(self, html: str):
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str):
        try:
            data = path.read_bytes()
        except (OSError, FileNotFoundError):
            self.send_response(404); self.end_headers()
            self.wfile.write(b"Not found"); return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(data)

    # --- per-request active-project asset resolution (no boot pin) ---
    def _serve_asset(self, kind: str, rel: str):
        jid = active_job_id()
        if not jid:
            self.send_response(404); self.end_headers(); return
        rec = read_job(jid, _REPO)
        paths = resolve_paths(rec["channel"], rec["project"], _REPO)
        base = {"stills": paths["stills_dir"], "clips": paths["clips_dir"],
                "video": paths["modea"]}.get(kind)
        if base is None:
            self.send_response(404); self.end_headers(); return
        fp = (Path(base) / rel).resolve()
        if not str(fp).startswith(str(Path(base).resolve())):
            self.send_response(403); self.end_headers(); return
        ctype = "video/mp4" if fp.suffix == ".mp4" else _sniff_media_type(
            fp.read_bytes()[:16] if fp.exists() else b"")
        self._send_file(fp, ctype)

    def do_GET(self):
        if not _key_ok(self):
            self.send_response(403); self.end_headers()
            self.wfile.write(b"403 - bad key"); return
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path in ("/", "/index.html"):
            self._html(render_page(SERVER_KEY)); return
        if path == "/api/health":
            self._json(200, {"ok": True, "service": "mission-control"}); return
        if path == "/api/channels":
            self._json(200, {"channels": list_channels()}); return
        if path == "/api/projects":
            q = parse_qs(parsed.query)
            ch = q.get("channel", [""])[0]
            self._json(200, {"projects": list_projects(ch)}); return
        if path == "/api/state":
            self._json(200, build_state()); return
        if path.startswith("/stills/"):
            self._serve_asset("stills", path[len("/stills/"):]); return
        if path.startswith("/clips/"):
            self._serve_asset("clips", path[len("/clips/"):]); return
        if path.startswith("/video/"):
            self._serve_asset("video", path[len("/video/"):]); return

        self.send_response(404); self.end_headers()
        self.wfile.write(b"Not found")

    def _read_json(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            return json.loads(self.rfile.read(n).decode("utf-8")), None
        except Exception as e:
            return None, str(e)

    def do_POST(self):
        if not _key_ok(self):
            self.send_response(403); self.end_headers(); return
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        body, err = self._read_json()
        if err:
            self._json(400, {"ok": False, "error": err}); return

        if path == "/api/launch":
            ch = body.get("channel"); pr = body.get("project")
            dry = bool(body.get("dry", True))
            log = body.get("log", "normal")
            if not ch or not pr:
                self._json(400, {"ok": False, "error": "channel + project required"}); return
            self._json(200, {"ok": True, **launch_job(ch, pr, dry, log)}); return

        if path.startswith("/api/gate/"):
            name = path[len("/api/gate/"):]
            jid = active_job_id()
            decision = body.get("decision")
            self._json(200, decide_gate(jid, decision)); return

        self.send_response(404); self.end_headers()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8002)
    ap.add_argument("--key", default=None)
    args = ap.parse_args()

    global SERVER_KEY
    if args.host not in ("127.0.0.1", "localhost") and not args.key:
        sys.exit("ERROR: refusing to bind public without --key.")
    SERVER_KEY = args.key

    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    q = f"?key={args.key}" if args.key else ""
    print(f"Mission Control on http://{args.host}:{args.port}/{q}")
    print(f"  jobs dir: {jobs_dir(_REPO)}")
    print(f"  (serve_review.py / review.service on :8001 left untouched)")
    print("  Ctrl+C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down…"); srv.server_close()


if __name__ == "__main__":
    main()
