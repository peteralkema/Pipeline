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

# ---- stills-edit endpoint machinery (ported from serve_review.py) ----------
# These two endpoints (/api/restill, /api/aifix) are the PROVEN stills controls.
# serve_review.py ran them against a boot-pinned single project; here they run
# PER-REQUEST, resolving the project from the active job or ?channel=&project=.
import base64 as _base64

try:
    from restill_from_feedback import (
        resolve_canon_tokens, find_beats_file, load_rulebook_negatives,
        backup_existing_still, generate_still,
    )
    _RESTILL_OK = True
except Exception as _e:
    _RESTILL_OK = False
    _RESTILL_IMPORT_ERR = str(_e)

try:
    from anthropic import Anthropic as _Anthropic
    _ANTHROPIC_AVAILABLE = True
except Exception:
    _ANTHROPIC_AVAILABLE = False

import os as _os
_ANTHROPIC_CLIENT = None
if _ANTHROPIC_AVAILABLE and _os.environ.get("ANTHROPIC_API_KEY"):
    try:
        _ANTHROPIC_CLIENT = _Anthropic(api_key=_os.environ["ANTHROPIC_API_KEY"])
    except Exception:
        _ANTHROPIC_CLIENT = None

try:
    from recreation_pipeline import animate_still as _animate_still
    _ANIMATE_OK = True
except Exception as _ae:
    _ANIMATE_OK = False
    _ANIMATE_IMPORT_ERR = str(_ae)

import threading as _threading
# Per-shot once-off animate status, keyed "channel/project/shot". Module-level
# (not the job record) so animate works with no active job. Values:
#   {"status": "running"|"done"|"error", "error": <str?>}
_ANIMATE_JOBS = {}
_ANIMATE_LOCK = _threading.Lock()

def _animate_key(ch, pr, shot):
    return f"{ch}/{pr}/{shot}"

def _run_animate_bg(key, still_path, motion_prompt, out_path):
    try:
        _animate_still(still_path, motion_prompt, out_path)
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "done"}
    except Exception as e:
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "error", "error": str(e)}

_FLUX_MODEL = "fal-ai/flux-pro/v1.1"
_VISION_MODEL = "claude-sonnet-4-6"
_AIFIX_SYSTEM_PROMPT = (
    "You are a strict art director reviewing an AI-generated still against its "
    "intended prompt and brand rules (faceless where required, no spell-breakers, "
    "period-accurate, drift-safe). Respond with STRICT JSON only, no preamble, no "
    "markdown:\n"
    '{"verdict": "fine" | "fix", "diagnosis": "<one short sentence naming what is '
    'wrong, or why it is fine>", "corrected_prompt": "<the full corrected prompt '
    'if verdict is fix, else empty string>"}'
)

# Per-(channel/project) cache of the restill inputs, so 184 rapid clicks don't
# re-read files 184 times; a project switch loads fresh.
_STILLS_CACHE = {}

def _stills_ctx(channel: str, project: str):
    """Resolve + cache (beats_by_idx, canon, negatives, stills_dir, model) for a
    project, keyed by ENGINE shot number (storyboard index) like serve_review."""
    key = f"{channel}/{project}"
    if key in _STILLS_CACHE:
        return _STILLS_CACHE[key]
    paths = resolve_paths(channel, project, _REPO)
    project_dir = paths["project"]
    # storyboard.json lives under modea/ (not project root); find_beats_file
    # builds <dir>/storyboard.json, so give it the modea dir. negatives below
    # still get the project root so their parent.parent hits the channel root.
    beats_file = find_beats_file(paths["modea"], None)  # storyboard-shaped beats
    import json as _json
    beats_data = _json.loads(Path(beats_file).read_text())
    beats_by_idx = {b["index"]: b for b in beats_data}  # ENGINE shot keyed
    # canon: project data file if present (mirrors serve_review main())
    canon = {}
    canon_file = project_dir / "canon.json"
    if canon_file.is_file():
        try:
            canon = _json.loads(canon_file.read_text()).get("canon", {}) or {}
        except Exception:
            canon = {}
    negatives = load_rulebook_negatives(project_dir)
    ctx = {
        "beats_by_idx": beats_by_idx,
        "canon": canon,
        "negatives": negatives,
        "stills_dir": paths["stills_dir"],
        "model": _FLUX_MODEL,
    }
    _STILLS_CACHE[key] = ctx
    return ctx

def _resolve_request_project(body):
    """Project for a stills POST: explicit channel/project in body, else active job."""
    ch = (body or {}).get("channel")
    pr = (body or {}).get("project")
    if ch and pr:
        return ch, pr
    jid = active_job_id()
    if jid:
        rec = read_job(jid, _REPO)
        return rec.get("channel"), rec.get("project")
    return None, None
from ingest import create_project, rich_list_projects


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
    # back-compat: plain slug list (newest-first via rich_list_projects)
    return [p["slug"] for p in rich_list_projects(channel)]


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
    # The detached subprocess does NOT inherit our interactive shell's venv PATH.
    # sys.executable is the venv python, so its parent IS the venv bin dir —
    # prepend it to PATH so bare tool names (whisper, ffmpeg, ...) resolve.
    _env = dict(_os.environ)
    _venv_bin = str(Path(sys.executable).parent)
    _env["PATH"] = _venv_bin + ":" + _env.get("PATH", "")
    subprocess.Popen(
        cmd, cwd=str(_REPO),
        stdout=logf, stderr=subprocess.STDOUT,
        start_new_session=True,        # detach from this process group
        env=_env,
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

async function loadProjectsRich(folder) {
  const r = await api("/api/projects?channel="+encodeURIComponent(folder));
  return r.projects_rich || [];
}
async function renderIdle(state) {
  const app = document.getElementById("app");
  const channels = state.channels || [];
  app.innerHTML = "";

  // ---- CREATE PANEL (paste script.md text OR upload .md, + slug) ----
  const create = el(`<div class="panel">
    <label>New project — paste your script.md, or upload it</label>
    <textarea id="scripttext" rows="6" placeholder="paste the full script.md here (channel: header included)…"
      style="width:100%;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:10px;font:13px/1.4 ui-monospace,monospace;box-sizing:border-box;"></textarea>
    <div class="row" style="margin-top:8px">
      <input type="file" id="scriptfile" accept=".md,text/markdown,text/plain"
        style="color:#8a8a99;font-size:13px;">
    </div>
    <label>Project slug (folder name — lowercase, hyphens)</label>
    <input id="slug" placeholder="watchers-daughters"
      style="background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px 10px;min-width:280px;">
    <div class="row"><button id="create">Create project</button></div>
    <div id="createmsg" class="phase" style="margin-top:10px;white-space:pre-wrap;"></div>
  </div>`);
  app.appendChild(create);

  // ---- LAUNCH PANEL (pick existing project) ----
  const panel = el(`<div class="panel">
    <label>Channel</label>
    <select id="chan"></select>
    <label>Project (newest first)</label>
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
  async function refreshProjects(folder, selectSlug) {
    if (!folder) { proj.innerHTML='<option>—</option>'; launch.disabled=true; return; }
    proj.innerHTML = '<option>loading…</option>';
    const ps = await loadProjectsRich(folder);
    proj.innerHTML = '<option value="">— pick a project —</option>' +
      ps.map(p=>`<option value="${p.slug}">${p.slug} · ${p.created_label} · ${p.stage}</option>`).join("");
    if (selectSlug) { proj.value = selectSlug; }
    launch.disabled = !proj.value;
  }
  chan.onchange = () => { launch.disabled = true; clearStoryboard(); refreshProjects(chan.value); };
  proj.onchange = () => {
    launch.disabled = !(chan.value && proj.value);
    if (chan.value && proj.value) {
      window.__SEL_VIEW = chan.value + "/" + proj.value;
      renderStoryboard(chan.value, proj.value);
    } else { clearStoryboard(); }
  };
  launch.onclick = async () => {
    launch.disabled = true; launch.textContent = "Launching…";
    const mode = panel.querySelector("#mode").value;
    await api("/api/launch", {method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({channel:chan.value, project:proj.value, dry: mode==="dry"})});
    poll();
  };

  // ---- Create wiring ----
  const fileInput = create.querySelector("#scriptfile");
  const textArea = create.querySelector("#scripttext");
  fileInput.onchange = async () => {
    const f = fileInput.files[0]; if (!f) return;
    textArea.value = await f.text();
  };
  const slugInput = create.querySelector("#slug");
  const msg = create.querySelector("#createmsg");
  create.querySelector("#create").onclick = async () => {
    const NL = String.fromCharCode(10);
    msg.textContent = "Creating — parsing + verifying…";
    const r = await api("/api/create", {method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({script: textArea.value, slug: slugInput.value.trim()})});
    if (!r.ok) {
      let m = "✗ " + (r.error || "create failed") + " (stage: " + (r.stage||"?") + ")";
      if (r.verify) m += NL + "  wordless beats: " + JSON.stringify(r.verify.wordless) +
                         NL + "  Mode A no-VISUAL: " + JSON.stringify(r.verify.no_visual);
      msg.textContent = m; return;
    }
    const v = r.verify;
    let g = r.git && r.git.pushed ? "pushed to GitHub" :
            (r.git && r.git.warn ? ("⚠ " + r.git.warn) : "git skipped");
    msg.textContent = "✓ created " + r.folder + "/projects/" + r.slug +
      NL + "  " + v.beats + " beats · modes " + JSON.stringify(v.modes) +
      NL + "  " + g + NL + "  selected below — pick mode and Launch.";
    // select the channel + new project in the launch panel
    chan.value = r.folder;
    await refreshProjects(r.folder, r.slug);
  };
}

function renderRunning(state) {
  const app = document.getElementById("app");
  var _SQ = String.fromCharCode(39);  // single quote, quote-proof (no literal ' in source)
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
    // STILLS GATE BODY — the gate IS the storyboard. Render the five-column
    // body from the view already attached to state (no re-fetch), controls live.
    const view = state.view || {};
    const beats = view.beats || [];
    const ch = state.channel, pr = state.project;
    window.__SEL_VIEW = ch + "/" + pr;  // so bindStillControls posts to this project
    const n = beats.length || (g.payload && g.payload.stills_count) || "?";
    const head = '<div class="panel gate">' +
      '<label>Stills gate — review before clips</label>' +
      '<div>' + n + ' stills rendered. Review (AI Fix / Regenerate any that break), ' +
      'then approve.</div>' +
      '<div class="row">' +
        '<button onclick=' + _SQ + 'gate(' + _SQ + 'go' + _SQ + ')' + _SQ +
          '>Generate Clips (approve stills)</button>' +
        '<button class="secondary" onclick=' + _SQ + 'gate(' + _SQ + 'skip' + _SQ + ')' + _SQ +
          '>Skip</button>' +
      '</div></div>';
    const body = '<div id="storyboard" class="panel" style="max-width:2400px;">' +
      '<label>Storyboard — ' + pr + ' · ' + n + ' beats</label>' +
      beats.map(b => beatRow(b, ch, pr)).join("") + '</div>';
    // buttons appear BOTH above (quick approve) and the body below them.
    gateHtml = head + body;
    window.__BIND_GATE_BODY = true;  // edit 2 binds controls after innerHTML
  }
  app.innerHTML = `<div class="panel">
      <div class="phase">job <code>${state.job_id}</code></div>
      <div class="phase">${state.channel} · ${state.project}</div>
      <div class="phase">phase: <b>${state.phase}</b>
        ${(!g||g.status!=="waiting") ? '<span class="spin"> — working…</span>' : ''}</div>
    </div>` + gateHtml;
  if (window.__BIND_GATE_BODY) {
    window.__BIND_GATE_BODY = false;
    const sb = document.getElementById("storyboard");
    if (sb && typeof bindMotionBoxes === "function") bindMotionBoxes(sb);
  }
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
  // re-render only when something the user SEES changes. Include the idle
  // project selection so picking a project (no job) triggers a body render.
  const g = state.gate || {};
  // gate_view_token: at the stills gate, key on stills_count so the body
  // renders once when the gate opens (controls then drive in-place reloads).
  const gate_view_token = (g.name === "stills" && g.payload)
                          ? ("stills:" + (g.payload.stills_count || "")) : "";
  return [state.phase, state.job_id, g.name, g.status,
          window.__SEL_VIEW || "", gate_view_token].join("|");
}
async function poll() {
  const state = await api("/api/state");
  const key = renderKey(state);
  if (key === LAST_RENDER_KEY) return;   // nothing visible changed -> don't clobber the DOM
  LAST_RENDER_KEY = key;
  if (state.phase === "idle") renderIdle(state);
  else renderRunning(state);
}
function clearStoryboard() {
  const e = document.getElementById("storyboard"); if (e) e.remove();
  window.__SEL_VIEW = "";
}
// per-beat motion edits held in memory for this session (display+persist seam).
// Keyed by "channel/project/beatIndex". A backend save endpoint wires in later.
window.__MOTION_EDITS = window.__MOTION_EDITS || {};
function motionKey(ch, pr, idx) { return ch + "/" + pr + "/" + idx; }

function beatRow(b, ch, pr) {
  const a = b.assets || {};
  const shot = a.still && a.still.engine_shot;
  const hasStill = a.still && a.still.exists;
  const hasClip = a.clip && a.clip.exists;
  const n3 = String(shot).padStart(3,"0");
  const q = "?channel=" + encodeURIComponent(ch) + "&project=" + encodeURIComponent(pr) +
            "&key=" + KEY;
  const dur = (b.duration_s != null) ? (b.duration_s.toFixed(2) + "s") : "—";
  const prompt = b.visual_rendered || b.visual_authored || "";

  // COL 2 — Flux still (fills its column up to a cap)
  let stillCell;
  if (hasStill) {
    stillCell = '<img src="/stills/shot_' + n3 + '.png' + q +
      '" loading="lazy" style="width:100%;max-width:1100px;border-radius:8px;background:#000;display:block;">';
  } else {
    stillCell = '<div style="width:100%;max-width:480px;aspect-ratio:16/9;border-radius:8px;' +
      'background:#1c1c26;display:flex;align-items:center;justify-content:center;' +
      'color:#55556a;font-size:13px;">not rendered</div>';
  }

  // COL 4 — Kling clip
  let clipCell;
  if (hasClip) {
    clipCell = '<video src="/clips/shot_' + n3 + '.mp4' + q +
      '" muted loop autoplay playsinline style="width:100%;max-width:1100px;border-radius:8px;background:#000;display:block;"></video>';
  } else {
    clipCell = '<div style="width:100%;max-width:480px;aspect-ratio:16/9;border-radius:8px;' +
      'background:#1c1c26;display:flex;align-items:center;justify-content:center;' +
      'color:#55556a;font-size:13px;">not rendered</div>';
  }

  // COL 3 — MOTION DIRECTION (editable; pre-filled with stored value or prior edit)
  const mkey = motionKey(ch, pr, b.index);
  const stored = (window.__MOTION_EDITS[mkey] != null)
                 ? window.__MOTION_EDITS[mkey]
                 : (b.motion_prompt || "");
  const _canAnimate = (hasStill && shot != null);
  const motionCell =
    '<div class="motioncell" data-shot="' + (shot==null?'':shot) + '">' +
    '<textarea data-mkey="' + mkey + '" class="motionbox" rows="5" ' +
    'placeholder="motion direction (blank = engine default)…" ' +
    'style="width:100%;box-sizing:border-box;background:#1c1c26;color:#e8e6e3;' +
    'border:1px solid #32323e;border-radius:8px;padding:10px;' +
    'font:13px/1.45 ui-monospace,monospace;resize:vertical;">' +
    escapeHtml(stored) + '</textarea>' +
    '<div style="color:#55556a;font-size:11px;margin-top:4px;">motion direction</div>' +
    (_canAnimate ?
      ('<button class="animbtn" style="width:100%;margin-top:8px;background:#7a4ddb;' +
       'color:#fff;border:0;border-radius:6px;padding:9px;cursor:pointer;' +
       'font:13px ui-monospace,monospace;font-weight:600;">Render this clip</button>' +
       '<div class="animmsg" style="color:#55556a;font-size:11px;margin-top:6px;min-height:14px;"></div>')
      : '') +
    '</div>';

  // COL 1 — TEXT spine
  const textCell =
    '<div style="color:#d4a017;font-size:12px;margin-bottom:8px;">beat ' + b.index +
      ' · shot ' + (shot==null?"—":shot) + ' · ' + (b.stage||"") +
      ' · ' + dur + ' · ' + (b.mode||"") + '</div>' +
    '<div style="color:#e8e6e3;font-size:14px;line-height:1.5;">' + (b.narration||"") + '</div>' +
    '<div style="color:#8a8a99;font-size:12px;margin-top:8px;font-style:italic;line-height:1.45;">' +
      prompt + '</div>' +
    '<div style="color:#55556a;font-size:11px;margin-top:8px;">look: ' + (b.look_resolved||"") + '</div>';

  // COL 3 — STILL CONTROLS (Accept/Reject, AI Fix, Regenerate, Notes, Override).
  // Only meaningful when a still exists and we know the engine shot number.
  let controlsCell;
  if (hasStill && shot != null) {
    const jkey = motionKey(ch, pr, b.index);  // reuse the channel/project/beat key
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
        '<button class="aifix" style="width:100%;margin-top:8px;background:#14a3b8;color:#fff;' +
          'border:0;border-radius:6px;padding:9px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:600;">AI Fix</button>' +
        '<button class="regen" style="width:100%;margin-top:8px;background:#3b5bdb;color:#fff;' +
          'border:0;border-radius:6px;padding:9px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:600;">Regenerate</button>' +
        '<textarea class="note" rows="2" placeholder="Notes — appended to prompt as regeneration feedback" ' +
          'style="width:100%;box-sizing:border-box;margin-top:8px;background:#1c1c26;color:#e8e6e3;' +
          'border:1px solid #32323e;border-radius:6px;padding:8px;font:12px/1.4 ui-monospace,monospace;resize:vertical;"></textarea>' +
        '<textarea class="override" rows="2" placeholder="Override — raw prompt sent straight to fal, bypasses canon" ' +
          'style="width:100%;box-sizing:border-box;margin-top:6px;background:#1c1c26;color:#e8e6e3;' +
          'border:1px solid rgba(168,85,247,0.4);border-radius:6px;padding:8px;font:12px/1.4 ui-monospace,monospace;resize:vertical;"></textarea>' +
        '<div class="ctlmsg" style="color:#55556a;font-size:11px;margin-top:6px;min-height:14px;"></div>' +
      '</div>';
  } else {
    controlsCell = '<div style="color:#55556a;font-size:11px;">no still yet</div>';
  }

  // Five columns: text | still | controls | motion | clip
  const grid =
    '<div style="display:grid;gap:14px;align-items:start;' +
    'grid-template-columns:minmax(180px,0.7fr) minmax(360px,2.6fr) minmax(190px,0.85fr) minmax(160px,0.7fr) minmax(360px,2.6fr);">' +
      '<div>' + textCell + '</div>' +
      '<div>' + stillCell + '<div style="color:#55556a;font-size:11px;margin-top:4px;">Flux still</div></div>' +
      '<div>' + controlsCell + '</div>' +
      '<div>' + motionCell + '</div>' +
      '<div>' + clipCell + '<div style="color:#55556a;font-size:11px;margin-top:4px;">Kling motion</div></div>' +
    '</div>';

  // MODE B strip — full width, beneath the row, ONLY when an overlay exists.
  // Hard rule: at most one Mode B per Mode A beat -> render overlays[0] only.
  let modeB = "";
  const ov = (b.overlays && b.overlays.length) ? b.overlays[0] : null;
  if (ov) {
    modeB =
      '<div style="margin-top:14px;padding:12px 14px;border-left:3px solid #d4a017;' +
      'background:#16161e;border-radius:0 8px 8px 0;">' +
        '<div style="color:#d4a017;font-size:12px;margin-bottom:6px;">' +
          'Mode B · ' + (ov.component || "card") + ' · overlays beat ' + b.index + '</div>' +
        '<div style="color:#e8e6e3;font-size:13px;">“' + (ov.phrase || "") + '”</div>' +
        '<div style="color:#55556a;font-size:11px;margin-top:6px;">' +
          'Remotion edit box wires in here (later).</div>' +
      '</div>';
  }

  return '<div style="padding:18px 0;border-bottom:1px solid #1e1e28;">' +
         grid + modeB + '</div>';
}

function escapeHtml(s) {
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;")
                  .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
async function renderStoryboard(ch, pr) {
  clearStoryboard();
  const app = document.getElementById("app");
  const wrap = document.createElement("div");
  wrap.id = "storyboard";
  wrap.className = "panel";
  wrap.style.maxWidth = "2400px";  // five columns with large media
  wrap.innerHTML = '<span class="spin">loading storyboard…</span>';
  app.appendChild(wrap);
  let view;
  try {
    view = await api("/api/view?channel=" + encodeURIComponent(ch) +
                     "&project=" + encodeURIComponent(pr));
  } catch (e) { wrap.innerHTML = "view error: " + e; return; }
  if (view.error) { wrap.innerHTML = "view error: " + view.error; return; }
  const beats = view.beats || [];
  const head = '<label>Storyboard — ' + pr + ' · ' + beats.length + ' beats · ' +
               (view.has_mode_b ? "dual-mode" : "Mode A") + '</label>';
  wrap.innerHTML = head + beats.map(b => beatRow(b, ch, pr)).join("");
  bindMotionBoxes(wrap);
}
function bindMotionBoxes(wrap) {
  // Keep typed motion direction in the in-memory map so a poll re-render
  // (or scroll) doesn't wipe it. Backend save endpoint wires in a later phase.
  wrap.querySelectorAll("textarea.motionbox").forEach(function(t) {
    t.addEventListener("input", function() {
      window.__MOTION_EDITS[t.getAttribute("data-mkey")] = t.value;
    });
  });
  bindStillControls(wrap);
}
function bindStillControls(wrap) {
  window.__JUDGED = window.__JUDGED || {};
  const CH = (window.__SEL_VIEW || "/").split("/")[0];
  const PR = (window.__SEL_VIEW || "/").split("/").slice(1).join("/");
  function reloadStill(ctl) {
    // bust the cache so the regenerated still shows immediately
    const shot = ctl.getAttribute("data-shot");
    const n3 = String(shot).padStart(3, "0");
    const row = ctl.closest("div");  // controls cell; the still img is a sibling cell
    const grid = ctl.parentElement.parentElement;  // the 5-col grid
    const img = grid.querySelector('img[src*="shot_' + n3 + '.png"]');
    if (img) {
      const base = img.src.split("&_t=")[0];
      img.src = base + "&_t=" + Date.now();
    }
  }
  wrap.querySelectorAll(".stillctl").forEach(function(ctl) {
    const shot = parseInt(ctl.getAttribute("data-shot"), 10);
    const jkey = ctl.getAttribute("data-jkey");
    const msg = ctl.querySelector(".ctlmsg");
    const note = ctl.querySelector("textarea.note");
    const override = ctl.querySelector("textarea.override");
    const acc = ctl.querySelector("button.acc");
    const rej = ctl.querySelector("button.rej");
    const aifix = ctl.querySelector("button.aifix");
    const regen = ctl.querySelector("button.regen");

    acc.addEventListener("click", function() {
      window.__JUDGED[jkey] = "accept";
      acc.style.background = "#1c7c4a"; rej.style.background = "#2a2a36";
    });
    rej.addEventListener("click", function() {
      window.__JUDGED[jkey] = "reject";
      rej.style.background = "#7c1c1c"; acc.style.background = "#2a2a36";
    });

    async function post(endpoint, payload, label) {
      msg.style.color = "#8a8a99"; msg.textContent = label + "...";
      try {
        const r = await api(endpoint, {method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(Object.assign({channel: CH, project: PR}, payload))});
        if (r.ok) {
          if (r.changed === false) {
            msg.style.color = "#8a8a99";
            msg.textContent = "AI: fine — " + (r.diagnosis || "no change");
          } else {
            msg.style.color = "#14a3b8";
            msg.textContent = (r.diagnosis ? ("fixed: " + r.diagnosis) :
                               ("regenerated (" + (r.mode || "ok") + ")"));
            reloadStill(ctl);
          }
        } else {
          msg.style.color = "#d46a6a"; msg.textContent = "error: " + (r.error || "failed");
        }
      } catch (e) {
        msg.style.color = "#d46a6a"; msg.textContent = "error: " + e;
      }
    }

    aifix.addEventListener("click", function() {
      post("/api/aifix", {shot: shot}, "AI Fix diagnosing");
    });
    regen.addEventListener("click", function() {
      post("/api/restill", {shot: shot, note: note.value, override: override.value},
           override.value.trim() ? "Regenerating (override)" : "Regenerating");
    });
  });
  bindAnimateButtons(wrap);
}
function bindAnimateButtons(wrap) {
  const CH = (window.__SEL_VIEW || "/").split("/")[0];
  const PR = (window.__SEL_VIEW || "/").split("/").slice(1).join("/");
  wrap.querySelectorAll(".motioncell").forEach(function(cell) {
    const btn = cell.querySelector("button.animbtn");
    if (!btn) return;
    const shot = parseInt(cell.getAttribute("data-shot"), 10);
    const box = cell.querySelector("textarea.motionbox");
    const msg = cell.querySelector(".animmsg");
    function reloadClip() {
      const n3 = String(shot).padStart(3, "0");
      const grid = cell.parentElement;  // the 5-col grid
      const vid = grid.querySelector('video[src*="shot_' + n3 + '.mp4"]');
      if (vid) {
        const base = vid.src.split("&_t=")[0];
        vid.src = base + "&_t=" + Date.now(); vid.load();
        return true;
      }
      return false;
    }
    function pollAnimate(label0) {
      const url = "/api/animate_status?channel=" + encodeURIComponent(CH) +
                  "&project=" + encodeURIComponent(PR) + "&shot=" + shot;
      const iv = setInterval(async function() {
        let st;
        try { st = await api(url); } catch (e) { return; }  // transient blip: keep polling
        if (st.status === "done") {
          clearInterval(iv);
          msg.style.color = "#7a4ddb";
          msg.textContent = reloadClip() ? "clip rendered" : "clip rendered — refresh to view";
          btn.disabled = false; btn.textContent = label0;
        } else if (st.status === "error") {
          clearInterval(iv);
          msg.style.color = "#d46a6a"; msg.textContent = "error: " + (st.error || "failed");
          btn.disabled = false; btn.textContent = label0;
        }
        // status "running"/"idle": keep waiting (spinner stays)
      }, 3000);
    }
    btn.addEventListener("click", async function() {
      btn.disabled = true; const label0 = btn.textContent;
      btn.textContent = "Rendering (Kling)…";
      msg.style.color = "#8a8a99"; msg.textContent = "animating — this takes a bit…";
      try {
        const r = await api("/api/animate", {method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({channel: CH, project: PR, shot: shot,
                                motion_prompt: box.value})});
        if (r.ok && r.started) {
          pollAnimate(label0);  // fire-and-poll: connection returned, now poll for the file
        } else {
          msg.style.color = "#d46a6a"; msg.textContent = "error: " + (r.error || "failed to start");
          btn.disabled = false; btn.textContent = label0;
        }
      } catch (e) {
        msg.style.color = "#d46a6a"; msg.textContent = "error: " + e;
        btn.disabled = false; btn.textContent = label0;
      }
    });
  });
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
    def _serve_asset(self, kind: str, rel: str, channel=None, project=None):
        # Resolve from explicit channel/project (browse any project) or fall
        # back to the active job. No active job + no params -> 404.
        if not (channel and project):
            jid = active_job_id()
            if not jid:
                self.send_response(404); self.end_headers(); return
            rec = read_job(jid, _REPO)
            channel, project = rec["channel"], rec["project"]
        paths = resolve_paths(channel, project, _REPO)
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
        if path == "/api/animate_status":
            q = parse_qs(parsed.query)
            ch = q.get("channel", [""])[0]
            pr = q.get("project", [""])[0]
            shot = q.get("shot", [""])[0]
            key = _animate_key(ch, pr, shot)
            with _ANIMATE_LOCK:
                st = dict(_ANIMATE_JOBS.get(key, {"status": "idle"}))
            self._json(200, st); return
        if path == "/api/channels":
            self._json(200, {"channels": list_channels()}); return
        if path == "/api/projects":
            q = parse_qs(parsed.query)
            ch = q.get("channel", [""])[0]
            rich = rich_list_projects(ch)
            self._json(200, {"projects": [p["slug"] for p in rich],
                             "projects_rich": rich}); return
        if path == "/api/state":
            self._json(200, build_state()); return
        if path == "/api/view":
            q = parse_qs(parsed.query)
            ch = q.get("channel", [""])[0]; pr = q.get("project", [""])[0]
            if not ch or not pr:
                self._json(400, {"error": "channel + project required"}); return
            try:
                self._json(200, build_beats_view(ch, pr, _REPO))
            except Exception as e:
                self._json(500, {"error": str(e)})
            return
        if path.startswith("/stills/"):
            q = parse_qs(parsed.query)
            self._serve_asset("stills", path[len("/stills/"):],
                              q.get("channel",[None])[0], q.get("project",[None])[0]); return
        if path.startswith("/clips/"):
            q = parse_qs(parsed.query)
            self._serve_asset("clips", path[len("/clips/"):],
                              q.get("channel",[None])[0], q.get("project",[None])[0]); return
        if path.startswith("/video/"):
            q = parse_qs(parsed.query)
            self._serve_asset("video", path[len("/video/"):],
                              q.get("channel",[None])[0], q.get("project",[None])[0]); return

        self.send_response(404); self.end_headers()
        self.wfile.write(b"Not found")

    def _read_json(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            return json.loads(self.rfile.read(n).decode("utf-8")), None
        except Exception as e:
            return None, str(e)

    def _handle_animate(self, body):
        if not _ANIMATE_OK:
            self._json(503, {"ok": False,
                "error": f"animate unavailable: {_ANIMATE_IMPORT_ERR}"}); return
        shot_idx = body.get("shot")
        motion_prompt = (body.get("motion_prompt") or "").strip()
        if not isinstance(shot_idx, int):
            self._json(400, {"ok": False, "error": "shot must be an integer"}); return
        if not motion_prompt:
            motion_prompt = ("Slow, subtle atmospheric motion. Drifting light, "
                             "faint air. No fast movement, no camera shake.")
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        ctx = _stills_ctx(ch, pr)
        stills_dir = ctx["stills_dir"]
        still_path = stills_dir / f"shot_{shot_idx:03d}.png"
        if not still_path.exists():
            self._json(404, {"ok": False, "error": f"still not found: {still_path.name}"}); return
        # clips dir is the sibling of stills under modea/
        clips_dir = stills_dir.parent / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)
        out_path = clips_dir / f"shot_{shot_idx:03d}.mp4"
        sys.stderr.write(f"[Animate] shot {shot_idx:03d} started in background ...\n")
        # Fire-and-poll: start the Kling call in a thread, return immediately.
        key = _animate_key(ch, pr, shot_idx)
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "running"}
        th = _threading.Thread(target=_run_animate_bg,
                               args=(key, still_path, motion_prompt, out_path),
                               daemon=True)
        th.start()
        self._json(200, {"ok": True, "started": True, "shot": shot_idx}); return

    def _handle_restill(self, body):
        if not _RESTILL_OK:
            self._json(503, {"ok": False,
                "error": f"restill unavailable: {_RESTILL_IMPORT_ERR}"}); return
        shot_idx = body.get("shot")
        note = (body.get("note") or "").strip()
        override = (body.get("override") or "").strip()
        if not isinstance(shot_idx, int):
            self._json(400, {"ok": False, "error": "shot must be an integer"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        ctx = _stills_ctx(ch, pr)
        beats_by_idx = ctx["beats_by_idx"]
        if shot_idx not in beats_by_idx:
            self._json(404, {"ok": False, "error": f"shot {shot_idx} not in beats"}); return

        if override:
            final_prompt = override; mode = "OVERRIDE"; negs = []
        else:
            beat = beats_by_idx[shot_idx]
            resolved = resolve_canon_tokens(beat.get("image_prompt", ""), ctx["canon"])
            final_prompt = (f"{resolved.rstrip(' .')}. REGENERATION FEEDBACK: {note}"
                            if note else resolved)
            mode = "NORMAL"; negs = ctx["negatives"]

        sys.stderr.write(f"[Regenerate] shot {shot_idx:03d} [{mode}]\n")
        backup_existing_still(ctx["stills_dir"], shot_idx)
        out = ctx["stills_dir"] / f"shot_{shot_idx:03d}.png"
        ok = generate_still(final_prompt, negs, out, ctx["model"])
        if ok:
            self._json(200, {"ok": True, "shot": shot_idx, "mode": mode})
        else:
            self._json(500, {"ok": False, "error": "fal generation failed"})

    def _handle_aifix(self, body):
        if not _RESTILL_OK:
            self._json(503, {"ok": False,
                "error": f"restill unavailable: {_RESTILL_IMPORT_ERR}"}); return
        if _ANTHROPIC_CLIENT is None:
            self._json(503, {"ok": False, "error":
                "AI fix unavailable: anthropic not installed or ANTHROPIC_API_KEY not set"}); return
        shot_idx = body.get("shot")
        if not isinstance(shot_idx, int):
            self._json(400, {"ok": False, "error": "shot must be an integer"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        ctx = _stills_ctx(ch, pr)
        beats_by_idx = ctx["beats_by_idx"]
        if shot_idx not in beats_by_idx:
            self._json(404, {"ok": False, "error": f"shot {shot_idx} not in beats"}); return
        still_path = ctx["stills_dir"] / f"shot_{shot_idx:03d}.png"
        if not still_path.exists():
            self._json(404, {"ok": False, "error": f"still not found: {still_path.name}"}); return

        beat = beats_by_idx[shot_idx]
        intended = resolve_canon_tokens(beat.get("image_prompt", ""), ctx["canon"])
        sys.stderr.write(f"[AI fix] shot {shot_idx:03d} diagnosing...\n")
        try:
            img = still_path.read_bytes()
            mtype = _sniff_media_type(img[:16])
            b64 = _base64.standard_b64encode(img).decode("ascii")
            resp = _ANTHROPIC_CLIENT.messages.create(
                model=_VISION_MODEL, max_tokens=1024,
                system=_AIFIX_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64",
                        "media_type": mtype, "data": b64}},
                    {"type": "text", "text":
                        f"Intended prompt for this shot:\n\n{intended}\n\n"
                        f"Judge the image against the brand rules and respond with the JSON object."},
                ]}],
            )
            raw = resp.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.strip("`"); raw = raw[raw.find("{"):raw.rfind("}") + 1]
            import json as _json
            verdict = _json.loads(raw)
        except Exception as e:
            self._json(500, {"ok": False, "error": f"vision diagnosis failed: {e}"}); return

        diagnosis = (verdict.get("diagnosis") or "").strip()
        corrected = (verdict.get("corrected_prompt") or "").strip()
        if not (verdict.get("verdict") == "fix" and corrected):
            self._json(200, {"ok": True, "shot": shot_idx, "changed": False,
                "diagnosis": diagnosis or "Image looks consistent with the brand rules."}); return

        backup_existing_still(ctx["stills_dir"], shot_idx)
        ok = generate_still(corrected, [], still_path, ctx["model"])
        if ok:
            self._json(200, {"ok": True, "shot": shot_idx, "changed": True,
                "diagnosis": diagnosis, "corrected_prompt": corrected}); return
        self._json(500, {"ok": False, "error": "fal generation failed after diagnosis",
                         "diagnosis": diagnosis})

    def do_POST(self):
        if not _key_ok(self):
            self.send_response(403); self.end_headers(); return
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        body, err = self._read_json()
        if err:
            self._json(400, {"ok": False, "error": err}); return

        if path == "/api/create":
            script_text = body.get("script", "")
            slug = (body.get("slug") or "").strip()
            if not script_text.strip():
                self._json(400, {"ok": False, "error": "empty script"}); return
            result = create_project(script_text, slug, do_git=True)
            self._json(200 if result.get("ok") else 422, result); return

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

        if path == "/api/restill":
            self._handle_restill(body); return
        if path == "/api/aifix":
            self._handle_aifix(body); return
        if path == "/api/animate":
            self._handle_animate(body); return

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
