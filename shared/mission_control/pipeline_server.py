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
    from recreation_pipeline import (
        animate_still as _animate_still,
        ken_burns_still as _ken_burns_still,
        generate_still as _recp_generate_still,
        _tiered_kling_count, _tiered_beat_index, _tiered_duration,
    )
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

def _run_animate_bg(key, still_path, motion_prompt, out_path, engine="kling", duration=None):
    try:
        if engine == "kenburns":
            _ken_burns_still(still_path, out_path, duration)
        else:
            _animate_still(still_path, motion_prompt, out_path)
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "done", "engine": engine}
    except Exception as e:
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "error", "error": str(e)}

# Per-(channel/project) assemble status, keyed "channel/project". Module-level
# (not the job record) so re-assemble works with no active job.
_ASSEMBLE_JOBS = {}
_ASSEMBLE_LOCK = _threading.Lock()

def _assemble_key(ch, pr):
    return f"{ch}/{pr}"

def _run_assemble_bg(key, project_dir):
    """Re-stitch final_video.mp4 using the SAME aligned assembler the launched run uses
    (assemble_episode.py + _index.json + frozen durations.json) -- NOT recreation_pipeline
    .assemble(), which ignores the beat->shot map and drifts. Re-pools the engine clips
    first so re-rendered clips reach assembly."""
    import subprocess as _sp
    import shutil
    try:
        project_dir = Path(project_dir)
        pool = project_dir / "clips"
        engine_clips = project_dir / "modea" / "clips"
        durations = project_dir / "durations.json"
        index_json = project_dir / "_index.json"
        voiceover = project_dir / "voiceover.mp3"
        final_out = project_dir / "final_video.mp4"

        # preflight the alignment inputs (same set convergence requires)
        missing = [p.name for p in (durations, index_json, voiceover) if not p.exists()]
        if missing:
            with _ASSEMBLE_LOCK:
                _ASSEMBLE_JOBS[key] = {"status": "error",
                    "error": "missing alignment inputs: " + ", ".join(missing)}
            return

        # RE-POOL: copy modea/clips/shot_*.mp4 -> <project>/clips/ (overwrite), mirroring
        # convergence_leg._pool_clips, so re-rendered clips actually reach assembly.
        pool.mkdir(parents=True, exist_ok=True)
        if engine_clips.exists() and engine_clips.resolve() != pool.resolve():
            for f in sorted(engine_clips.glob("shot_*.mp4")):
                shutil.copy2(f, pool / f.name)

        # SHELL the aligned assembler with the exact convergence flagset.
        cmd = [sys.executable, str(Path(_SHARED) / "assemble_episode.py"),
               "--durations", str(durations),
               "--index", str(index_json),
               "--voiceover", str(voiceover),
               "--project", str(project_dir),
               "--clips", str(pool),
               "--out", str(final_out),
               "--no-music"]
        r = _sp.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and final_out.exists():
            with _ASSEMBLE_LOCK:
                _ASSEMBLE_JOBS[key] = {"status": "done"}
        else:
            tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]
            with _ASSEMBLE_LOCK:
                _ASSEMBLE_JOBS[key] = {"status": "error", "error": " / ".join(tail) or "assemble failed"}
    except Exception as e:
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
        out = (r.stdout or "") + "\n" + (r.stderr or "")
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

_FLUX_MODEL = "fal-ai/flux-pro/v1.1"
_VISION_MODEL = "claude-sonnet-4-6"
_AIFIX_SYSTEM_PROMPT = (
    "You are a strict art director reviewing an AI-generated still against its "
    "intended prompt and brand rules (faceless where required, no spell-breakers, "
    "period-accurate, drift-safe). Look FIRST for generative defects: warped or "
    "extra hands, extra or missing fingers, extra or fused limbs, melted or "
    "asymmetric faces, duplicated or merged objects, floating body parts, and "
    "garbled text. When you find one, verdict is \"fix\" and the corrected_prompt "
    "must restate the full intended scene AND explicitly demand correct structure "
    "(e.g. 'exactly two hands, five fingers each, natural anatomy, no extra limbs, "
    "no duplicated objects'). Respond with STRICT JSON only, no preamble, no "
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

_GLOBAL_DEFAULT_MOTION = ("Slow, subtle atmospheric motion. Drifting light, "
                          "faint air. No fast movement, no camera shake.")


def _channel_default_motion(ch, pr):
    """The channel's default_motion (channel.json) for an empty motion box,
    falling back to the global default."""
    try:
        import json as _json
        cj = resolve_paths(ch, pr, _REPO)["channel_json"]
        if cj.is_file():
            v = _json.loads(cj.read_text()).get("default_motion")
            if v and str(v).strip():
                return str(v).strip()
    except Exception:
        pass
    return _GLOBAL_DEFAULT_MOTION


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

# Phases that mean the run is over (terminal). Everything else is a live run.
_TERMINAL_PHASES = ("done", "stopped", "error", "stale", "dead")

def active_job_id() -> str | None:
    """Return the freshest LIVE run, not merely the most-recently-touched file.

    Sorts records by started_at (record content, not file mtime -- a touched `done`
    record must not re-float above the live run), then returns the newest NON-TERMINAL
    record. If none are live, returns the newest overall (so a just-finished run still
    shows its done panel). This is what makes close/refresh/restart always rejoin the
    correct run instead of locking onto a stale `done` ghost.
    """
    recs = []
    for p in jobs_dir(_REPO).glob("*.json"):
        try:
            import json as _json
            d = _json.loads(p.read_text())
        except Exception:
            continue
        recs.append((float(d.get("started_at") or 0.0), str(d.get("phase") or ""), p.stem))
    if not recs:
        return None
    recs.sort(key=lambda r: r[0], reverse=True)  # newest started_at first
    for started, phase, stem in recs:
        if phase not in _TERMINAL_PHASES:
            return stem          # freshest live run wins
    return recs[0][2]            # none live -> newest overall (shows its done panel)


def launch_job(channel_folder: str, project: str, dry_run: bool, log: str) -> dict:
    """Spawn orchestrate.py as a DETACHED subprocess in gate-mode=job.
    Returns {job_id}. The render runs in its own process group, so restarting
    THIS server never kills it.

    Hardening B: refuse if a run is already live (one live run total). A live LAUNCH while
    another run is mid-flight is the duplicate-spawn that stranded an orphan + dup records.
    dry-run is exempt (no spawn, no spend)."""
    header_channel = _channel_header_name(channel_folder)
    if not dry_run:
        _live = active_job_id()
        if _live:
            try:
                import json as _json
                _rec = _json.loads((jobs_dir(_REPO) / f"{_live}.json").read_text())
            except Exception:
                _rec = {}
            _ph = str(_rec.get("phase") or "")
            if _ph and _ph not in _TERMINAL_PHASES:
                return {"ok": False, "already_running": _live, "phase": _ph,
                        "error": f"A run is already live ({_rec.get('project','?')}, phase {_ph}). "
                                 f"Wait for it to finish or reach a gate, or Reset it, before launching another."}
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

APP_VERSION = "v2.7"  # hand-bumped each shipped page change; pairs with the auto git SHA
STALE_SECONDS = 300  # A1: a gate run with no heartbeat for this long is treated as dead


def _build_sha() -> str:
    """Short SHA of the deployed commit — the half of the version that can't lie."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(_REPO), capture_output=True, text=True, timeout=3,
        )
        return out.stdout.strip() or "?"
    except Exception:
        return "?"


def build_state() -> dict:
    jid = active_job_id()
    if not jid:
        return {"phase": "idle", "job_id": None,
                "channels": list_channels(),
                "version": APP_VERSION, "sha": _build_sha()}
    rec = read_job(jid, _REPO)
    phase = rec.get("phase", "running")
    # Hardening C: pid liveness reaping. If the record is non-terminal but its orchestrate
    # process is gone (hard kill / crash -- the case the gate-only heartbeat check below
    # cannot see, e.g. a killed `animating` leg), flip it to terminal "dead" so the page
    # recovers and A/B stop treating it as live. Same-box, same-user: os.kill(pid,0) raises
    # ProcessLookupError iff the pid is gone.
    _pid = rec.get("pid")
    if phase not in _TERMINAL_PHASES and isinstance(_pid, int):
        try:
            os.kill(_pid, 0)
        except ProcessLookupError:
            phase = "dead"
        except PermissionError:
            pass  # alive but not ours -> treat as alive
    # A1: a run parked at a gate pulses a heartbeat every poll; if it has gone silent
    # for STALE_SECONDS the process is dead -> show it as stale so the page recovers.
    # Gate phases only: work legs (animating/assembling) are long blocking calls that
    # do not pulse mid-leg, so we never stale-flag a slow-but-alive render here.
    if phase in ("gate_audio", "gate_stills") and ((rec.get("gate") or {}).get("status") == "waiting"):
        hb = rec.get("heartbeat")
        if hb and (time.time() - float(hb)) > STALE_SECONDS:
            phase = "stale"
    state = {
        "phase": phase,
        "job_id": jid,
        "channel": rec.get("channel"),
        "project": rec.get("project"),
        "gate": rec.get("gate"),
        "channels": list_channels(),
        "version": APP_VERSION,
        "sha": _build_sha(),
    }
    # Once stills exist, attach the beats view so the body can render (2b/3 use it).
    if phase in ("gate_stills", "animating", "assembling", "done"):
        try:
            state["view"] = build_beats_view(rec["channel"], rec["project"], _REPO)
        except Exception as e:
            state["view_error"] = str(e)
    # Live status detail (item 1a): activity + count off disk, or elapsed time.
    try:
        state["status_detail"] = _status_detail(rec, phase)
    except Exception:
        state["status_detail"] = ""
    return state


def _beat_total(paths: dict) -> int:
    """Beat total from durations.json (the timing source). 0 if not found yet."""
    cand = []
    d = paths.get("durations")
    if d:
        cand.append(Path(d))
    # fall back to walking the project root (stills_dir = <project>/modea/stills)
    try:
        root = Path(paths["stills_dir"]).parent.parent
        cand.append(root / "durations.json")
    except Exception:
        pass
    for p in cand:
        try:
            if p and Path(p).exists():
                data = json.load(open(p))
                return len(data) if isinstance(data, (dict, list)) else 0
        except Exception:
            continue
    return 0


def _count_pngs(d) -> int:
    try:
        return sum(1 for _ in Path(d).glob("shot_*.png"))
    except Exception:
        return 0


def _count_mp4s(d) -> int:
    try:
        return sum(1 for _ in Path(d).glob("shot_*.mp4"))
    except Exception:
        return 0


def _elapsed_str(rec: dict) -> str:
    """Elapsed since heartbeat (A1, when present) else started_at."""
    t0 = rec.get("heartbeat") or rec.get("started_at")
    if not t0:
        return ""
    secs = max(0, int(time.time() - float(t0)))
    if secs < 60:
        return f"{secs}s"
    return f"{secs // 60}m"


def _status_detail(rec: dict, phase: str) -> str:
    """One short line: count where artifacts exist, elapsed time where they don't."""
    ch, pr = rec.get("channel"), rec.get("project")
    if not ch or not pr:
        return ""
    try:
        paths = resolve_paths(ch, pr, _REPO)
    except Exception:
        return ""
    total = _beat_total(paths)
    den = f" / {total}" if total else ""

    if phase == "animating":
        return f"clips {_count_mp4s(paths.get('clips_dir'))}{den}"
    if phase == "gate_stills":
        return f"stills {_count_pngs(paths.get('stills_dir'))}{den} ready"
    if phase == "running":
        # running covers the audio leg (no countable artifact yet) AND stills generation.
        # durations.json existing => audio leg done => we're generating stills.
        if total:
            return f"stills {_count_pngs(paths.get('stills_dir'))}{den}"
        e = _elapsed_str(rec)
        return f"audio · working {e}" if e else "audio · working"
    if phase == "assembling":
        e = _elapsed_str(rec)
        return f"assembling {e}" if e else "assembling"
    return ""


# --------------------------------------------------------------------------
# The page (generated dynamically — restart to update, never a baked file)
# --------------------------------------------------------------------------

def render_page(key: str | None) -> str:
    keyq = f"?key={key}" if key else ""
    # Minimal Phase-2a page: dropdowns, Launch, phase line, bare audio gate.
    # Intentionally small — rich panels are 2b/3. State-driven: everything
    # renders from /api/state, nothing stored client-side.
    _verstamp = f"{APP_VERSION} \u00b7 {_build_sha()}"  # e.g. v0.5 \u00b7 2723e25
    _page = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Film Director Storyboard and Control Panel</title>
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
<h1>AI FILM DIRECTOR STORYBOARD AND CONTROL PANEL <span style="font-size:12px;font-weight:400;color:#8a8a99;letter-spacing:0;">@@VERSTAMP@@</span></h1>
<div id="app"><div class="panel"><span class="spin">loading…</span></div></div>
<script>
const KEY = new URLSearchParams(location.search).get("key") || "";
const H = KEY ? {"X-Review-Key": KEY} : {};
const _U0 = new URLSearchParams(location.search);
const URL_CH = _U0.get("channel") || "";
const URL_PR = _U0.get("project") || "";
if (URL_CH && URL_PR) { window.__SEL_VIEW = URL_CH + "/" + URL_PR; }
function setUrlProject(ch, pr) {
  const u = new URL(location.href);
  if (ch && pr) { u.searchParams.set("channel", ch); u.searchParams.set("project", pr); }
  else { u.searchParams.delete("channel"); u.searchParams.delete("project"); }
  history.replaceState(null, "", u.toString());
}
async function api(path, opts={}) {
  opts.headers = Object.assign({}, H, opts.headers||{});
  const _kq = KEY ? ((path.includes("?")?"&":"?") + "key=" + KEY) : "";  // key always appended (right separator)
  const r = await fetch(path + _kq, opts);
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
// ── A0: one continuous page — persistent shell, per-phase strip, always-visible body ──
// Built ONCE by ensureShell, then only UPDATED in place. The status strip changes
// with phase; the gate bar shows controls when a gate is waiting; the storyboard
// body always shows the selected/running project. Nothing is wiped wholesale, so
// idle/running/gate/done/stopped/stale each render cleanly (no "working…" catch-all).

function selCh() { return (window.__SEL_VIEW || "/").split("/")[0]; }
function selPr() { return (window.__SEL_VIEW || "/").split("/").slice(1).join("/"); }

const ACTIVE_PHASES = ["running", "gate_audio", "gate_stills", "animating", "assembling"];
function isActiveRun(phase) { return ACTIVE_PHASES.indexOf(phase) !== -1; }

function phaseStrip(state) {
  const p = state.phase;
  const g = state.gate;
  if (p === "idle") return {text: "Idle — pick a project and Launch.", color: "#8a8a99"};
  if (g && g.status === "waiting" && g.name === "audio")
    return {text: "Audio gate — review the voiceover, then Accept or Swap.", color: "#d4a017"};
  if (g && g.status === "waiting" && g.name === "stills")
    return {text: "Stills gate — review the stills below, then Generate Clips or Stop.", color: "#d4a017"};
  if (p === "running")    return {text: "Running — audio leg (voiceover + timing)…", color: "#5b9bd5"};
  if (p === "animating")  return {text: "Animating clips (Kling)…", color: "#5b9bd5"};
  if (p === "assembling") return {text: "Assembling the final video…", color: "#5b9bd5"};
  if (p === "done")       return {text: "✓ Complete — final video assembled. Pick a project to launch another.", color: "#1c7c4a"};
  if (p === "stopped")    return {text: "■ Stopped at the stills gate — stills kept on disk. Re-launch to resume (existing stills are skipped).", color: "#b58900"};
  if (p === "error" || p === "stale")
    return {text: "⚠ This run ended unexpectedly. Pick a project and Launch to start fresh.", color: "#d46a6a"};
  return {text: "Phase: " + p, color: "#8a8a99"};
}

function ensureShell(state) {
  let shell = document.getElementById("shell");
  if (shell) return shell;
  const app = document.getElementById("app");
  app.innerHTML = "";
  shell = document.createElement("div");
  shell.id = "shell";
  app.appendChild(shell);

  const strip = el(`<div class="panel" id="strip" style="border-left:4px solid #8a8a99;display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
    <div style="flex:1;min-width:0;">
      <div id="stripmain" class="phase" style="font-size:14px;"></div>
      <div id="stripsub" class="phase" style="margin-top:4px;"></div>
    </div>
    <button id="resetbtn" class="secondary" style="margin-top:0;white-space:nowrap;">Reset</button>
  </div>`);
  shell.appendChild(strip);
  const resetbtn = strip.querySelector("#resetbtn");
  if (resetbtn) resetbtn.onclick = resetAll;

  // v0.8: two-column top -- controls left, FINAL VIDEO panel right (the U layout).
  const topgrid = el(`<div id="topgrid" style="display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start;max-width:1500px;">
    <div id="topleft" style="flex:0 1 420px;min-width:300px;"></div>
    <div id="toppanel" style="flex:1 1 560px;min-width:320px;max-width:760px;"></div>
  </div>`);
  shell.appendChild(topgrid);
  renderTopPlaceholder();

  const create = el(`<div class="panel" id="createpanel">
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
  document.getElementById("topleft").appendChild(create);

  const panel = el(`<div class="panel" id="launchpanel">
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
  document.getElementById("topleft").appendChild(panel);

  const gatebar = document.createElement("div");
  gatebar.id = "gatebar";
  shell.appendChild(gatebar);

  const channels = state.channels || [];
  const chan = panel.querySelector("#chan");
  const proj = panel.querySelector("#proj");
  const launch = panel.querySelector("#launch");
  chan.innerHTML = '<option value="">— pick a channel —</option>' +
     channels.map(c => `<option value="${c}">${c}</option>`).join("");
  async function refreshProjects(folder, selectSlug) {
    if (!folder) { proj.innerHTML = '<option>—</option>'; launch.disabled = true; return; }
    proj.innerHTML = '<option>loading…</option>';
    const ps = await loadProjectsRich(folder);
    proj.innerHTML = '<option value="">— pick a project —</option>' +
      ps.map(p => `<option value="${p.slug}">${p.slug} · ${p.created_label} · ${p.stage}</option>`).join("");
    if (selectSlug) { proj.value = selectSlug; }
    launch.disabled = !proj.value;
  }
  chan.onchange = () => {
    launch.disabled = true; window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__";
    setUrlProject("", ""); clearStoryboard(); refreshProjects(chan.value);
  };
  proj.onchange = () => {
    if (chan.value && proj.value) {
      window.__SEL_VIEW = chan.value + "/" + proj.value;
      window.__BODY_KEY = chan.value + "/" + proj.value + "|";  // matches idle poll key -> no double render
      setUrlProject(chan.value, proj.value);
      renderStoryboard(chan.value, proj.value);
      renderDonePanel(chan.value, proj.value);  // panel on select: show final video if one exists (else placeholder)
    } else {
      window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__"; setUrlProject("", ""); clearStoryboard();
    }
    launch.disabled = !(chan.value && proj.value);
  };
  launch.onclick = async () => {
    launch.disabled = true; launch.textContent = "Launching…";
    const mode = panel.querySelector("#mode").value;
    let resp = null;
    try {
      resp = await api("/api/launch", {method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({channel: chan.value, project: proj.value, dry: mode === "dry"})});
    } catch (e) { resp = null; }
    launch.textContent = "Launch";
    if (resp && resp.ok === false && resp.already_running) {
      // refuse if a run is already live: tell the operator, don't silently re-arm into a duplicate
      const cm = document.getElementById("createmsg");
      if (cm) cm.textContent = resp.error || "A run is already live.";
      else alert(resp.error || "A run is already live.");
    }
    poll();   // poll governs the button: it stays disabled while a run is live
  };

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
    const r = await api("/api/create", {method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({script: textArea.value, slug: slugInput.value.trim()})});
    if (!r.ok) {
      let m = "✗ " + (r.error || "create failed") + " (stage: " + (r.stage || "?") + ")";
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
    chan.value = r.folder;
    window.__SEL_VIEW = r.folder + "/" + r.slug;
    window.__BODY_KEY = "__none__";
    setUrlProject(r.folder, r.slug);
    await refreshProjects(r.folder, r.slug);
  };

  if (URL_CH && URL_PR && !isActiveRun(state.phase)) {
    (async function() {
      chan.value = URL_CH;
      await refreshProjects(URL_CH, URL_PR);
      window.__SEL_VIEW = URL_CH + "/" + URL_PR;
      window.__BODY_KEY = "";
      launch.disabled = !(chan.value && proj.value);
    })();
  }

  return shell;
}

function updateControls(state) {
  // A0b: disable-in-place — never hide the panels (the page shape stays constant);
  // during an active run they go inert + dimmed, otherwise fully live.
  const run = isActiveRun(state.phase);
  ["createpanel", "launchpanel"].forEach(function(id) {
    const panel = document.getElementById(id);
    if (!panel) return;
    panel.style.opacity = run ? "0.45" : "1";
    panel.querySelectorAll("input,select,button,textarea").forEach(function(elm) {
      elm.disabled = run;
    });
  });
  // Launch stays disabled during a run, and otherwise only enables once a
  // project is picked (overrides the blanket enable above for this one button).
  const chan = document.getElementById("chan");
  const proj = document.getElementById("proj");
  const launch = document.getElementById("launch");
  if (launch) launch.disabled = run || !(chan && proj && chan.value && proj.value);
}

function updateStrip(state) {
  const s = phaseStrip(state);
  const strip = document.getElementById("strip");
  const main = document.getElementById("stripmain");
  const sub = document.getElementById("stripsub");
  if (!strip || !main) return;
  strip.style.borderLeftColor = s.color;
  main.innerHTML = '<b style="color:' + s.color + ';">' + s.text + '</b>';
  if (sub) {
    if (state.job_id) {
      var base = (state.channel || "") + " · " + (state.project || "") + "  ·  phase: " + state.phase;
      var det = state.status_detail || "";
      sub.textContent = det ? (base + "  ·  " + det) : base;
    } else {
      sub.textContent = "";
    }
  }
}

function updateGatebar(state) {
  const bar = document.getElementById("gatebar");
  if (!bar) return;
  const g = state.gate;
  const waiting = g && g.status === "waiting";
  const token = waiting ? (g.name + ":" + g.status) : "none";
  if (bar.__token === token) return;   // unchanged — leave it (buttons hold no input)
  bar.__token = token;
  if (!waiting) { bar.innerHTML = ""; return; }
  var _SQ = String.fromCharCode(39);
  if (g.name === "audio") {
    const v = (g.payload && g.payload.voice_id) || "the channel voice";
    const m = (g.payload && g.payload.minutes) || "?";
    bar.innerHTML = `<div class="panel gate">
      <label>Audio gate</label>
      <div>Voiceover produced — measured <b>${m}</b> min, voice: <b>${v}</b>.</div>
      <div class="row">
        <button onclick="gate('keep')">Accept (keep this read)</button>
        <button class="secondary" onclick="gate('swap')">Swap (use my own recording)</button>
      </div></div>`;
  } else if (g.name === "stills") {
    const n = (g.payload && g.payload.stills_count) || "";
    bar.innerHTML = '<div class="panel gate">' +
      '<label>Stills gate — review before clips</label>' +
      '<div>' + n + ' stills rendered. Review the body below (Fix this image on any that break), then decide.</div>' +
      '<div class="row" style="margin:10px 0;align-items:center;">' +
        '<label style="margin:0 8px 0 0;text-transform:none;letter-spacing:0;color:#e8e6e3;">Kling clips: first</label>' +
        '<input id="klingn" type="number" min="0" step="1" value="40" style="width:80px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:6px 8px;">' +
        '<span style="color:#8a8a99;margin-left:8px;">beats — the rest render free (Ken Burns zoom). <span id="klingmsg" style="color:#14a3b8;"></span></span>' +
      '</div>' +
      '<div class="row" style="margin:0 0 8px;align-items:center;">' +
        '<button class="secondary" id="allstaticbtn">All static stills (no motion)</button>' +
        '<span id="staticmsg" style="color:#8a8a99;margin-left:8px;"></span>' +
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
      const sb = document.getElementById("allstaticbtn");
      if (sb) sb.addEventListener("click", async function() {
        inp.value = 0;
        const smsg = document.getElementById("staticmsg");
        const kmsg = document.getElementById("klingmsg");
        try {
          const rr = await api("/api/render_policy", {method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({channel: ch, project: pr, kling_count: 0, static: true})});
          if (smsg) smsg.textContent = (rr && rr.ok) ? "set: all static, no Kling" : "save failed";
          if (kmsg) kmsg.textContent = "saved N=0";
        } catch (e) { if (smsg) smsg.textContent = "save failed"; }
      });
    })();
  } else {
    bar.innerHTML = "";
  }
}

function bodyTarget(state) {
  // Active run -> body follows the RUN; otherwise -> the dropdown selection,
  // defaulting to the run's project if nothing is selected.
  if (isActiveRun(state.phase)) return {ch: state.channel, pr: state.project};
  return {ch: selCh() || state.channel, pr: selPr() || state.project};
}

function maybeUpdateBody(state) {
  const t = bodyTarget(state);
  if (!t.ch || !t.pr) { clearStoryboard(); removeDonePanel(); window.__BODY_KEY = "__none__"; return; }
  const sc = (state.gate && state.gate.payload && state.gate.payload.stills_count) || "";
  const key = t.ch + "/" + t.pr + "|" + sc + "|" + (state.phase || "");
  if (window.__BODY_KEY === key) return;   // same project + stills count + phase -> leave the DOM alone
  window.__BODY_KEY = key;
  window.__SEL_VIEW = t.ch + "/" + t.pr;   // so still/motion controls POST to this project
  renderDonePanel(t.ch, t.pr);  // panel persists across polls: artifact-aware (shows video iff has_video, else placeholder) -- no more flicker-then-wipe
  renderStoryboard(t.ch, t.pr);
}

function removeDonePanel() {
  const e = document.getElementById("donepanel"); if (e) e.remove();
  if (typeof renderTopPlaceholder === "function") renderTopPlaceholder();
}

async function renderDonePanel(ch, pr) {
  removeDonePanel();
  const slotEl = document.getElementById("toppanel");
  if (!slotEl) return;
  const q = "?channel=" + encodeURIComponent(ch) + "&project=" + encodeURIComponent(pr) + "&key=" + KEY;
  let meta = {};
  try { meta = await api("/api/meta?channel=" + encodeURIComponent(ch) + "&project=" + encodeURIComponent(pr)); }
  catch (e) { meta = {}; }
  if (!meta || !meta.has_video) { renderTopPlaceholder(); return; }   // no video -> placeholder
  const vsrc = "/video/" + encodeURIComponent(meta.video_name || "final_video.mp4") + q;
  const esc = function(s){ return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); };
  const panel = document.createElement("div");
  panel.id = "donepanel";
  panel.className = "panel";
  panel.style.cssText = "max-width:720px;border:1px solid #d4a017;";
  panel.innerHTML =
    '<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">' +
      '<span style="width:8px;height:8px;border-radius:50%;background:#ff0000;display:inline-block;"></span>' +
      '<b style="letter-spacing:.04em;">FINAL VIDEO &mdash; UPLOAD TO STUDIO</b></div>' +
    '<video src="' + vsrc + '" autoplay muted loop playsinline ' +
      'style="width:100%;border-radius:8px;background:#000;display:block;margin-bottom:8px;"></video>' +
    '<div style="margin-bottom:14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;">' +
      '<a href="' + vsrc + '" download style="display:inline-block;background:#2a2a36;color:#e8e6e3;' +
        'text-decoration:none;border-radius:6px;padding:8px 14px;font-weight:600;font-size:13px;">' +
        '&#8595; Download final video</a>' +
      '<button id="reassemblebtn" style="background:#2a2a36;margin-top:0;padding:8px 14px;font-size:13px;">' +
        '&#8635; Re-assemble (latest clips)</button>' +
      '<span id="reassemblemsg" style="color:#8a8a99;font-size:12px;"></span></div>' +
    '<label>Title</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
      'background:#1c1c26;padding:8px 10px;margin-bottom:8px;">' + esc(meta.title) + '</div>' +
    '<label>Description</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
      'background:#1c1c26;padding:8px 10px;margin-bottom:8px;white-space:pre-wrap;">' + esc(meta.description) + '</div>' +
    '<label>Tags</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
      'background:#1c1c26;padding:8px 10px;margin-bottom:14px;">' + esc(meta.tags) + '</div>' +
    '<label>Thumbnail</label>' +
    '<div style="border:1px solid #32323e;border-radius:8px;background:#161620;padding:10px;margin-bottom:14px;">' +
      '<div style="display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap;align-items:center;">' +
        '<input id="thumbtitle" placeholder="Headline (e.g. 200,000 WENT SILENT)" style="flex:2;min-width:170px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">' +
        '<input id="thumbsub" placeholder="Subtitle (optional)" style="flex:1;min-width:110px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">' +
        '<input id="thumbshot" type="number" min="1" placeholder="still #" style="width:78px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">' +
        '<button id="thumbgen" style="background:#d4a017;margin-top:0;padding:8px 14px;font-size:13px;font-weight:600;">Generate</button>' +
      '</div>' +
      '<span id="thumbmsg" style="color:#8a8a99;font-size:12px;"></span>' +
      '<img id="thumbimg" style="display:none;width:100%;border-radius:6px;margin-top:8px;background:#000;">' +
    '</div>' +
    '<button id="uploadbtn" ' +
      'style="background:#ff0000;">Upload to YouTube Studio (private)</button>' +
    '<span id="uploadmsg" style="color:#8a8a99;font-size:12px;margin-left:10px;"></span>' +
    '<div style="color:#8a8a99;font-size:11px;margin-top:6px;">Uploads as <b>private</b> '+
      '(review + set Altered-content = Yes in Studio before publishing).</div>';
  // v0.8: render into the top-right slot (fills the dead space beside the controls)
  const slot = document.getElementById("toppanel");
  if (slot) { slot.innerHTML = ""; slot.appendChild(panel); }
  const rb = document.getElementById("reassemblebtn");
  if (rb) rb.onclick = function() { reassemble(ch, pr); };
  const ub = document.getElementById("uploadbtn");
  if (ub) ub.onclick = function() { uploadVideo(ch, pr); };  const tg = document.getElementById("thumbgen");
  if (tg) tg.onclick = async function() {
    const t = (document.getElementById("thumbtitle").value || "").trim();
    const s = (document.getElementById("thumbsub").value || "").trim();
    const n = parseInt(document.getElementById("thumbshot").value, 10);
    const tmsg = document.getElementById("thumbmsg");
    const timg = document.getElementById("thumbimg");
    if (!t) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "enter a headline"; return; }
    if (isNaN(n)) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "enter a still number"; return; }
    tmsg.style.color = "#8a8a99"; tmsg.textContent = "generating\u2026";
    try {
      const r = await api("/api/thumbnail", {method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({channel: ch, project: pr, shot: n, title: t, subtitle: s})});
      if (r && r.ok) {
        tmsg.style.color = "#14a3b8"; tmsg.textContent = "thumbnail set (still " + r.shot + ")";
        timg.src = "/video/thumbnail.png" + q + "&_t=" + Date.now();
        timg.style.display = "block";
      } else {
        tmsg.style.color = "#d46a6a"; tmsg.textContent = "error: " + ((r && r.error) || "failed");
      }
    } catch (e) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "error: " + e; }
  };
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
}

function renderTopPlaceholder() {
  const slot = document.getElementById("toppanel");
  if (!slot) return;
  if (document.getElementById("donepanel")) return;  // a real panel is showing -> leave it
  slot.innerHTML =
    '<div class="panel" style="border:1px dashed #32323e;color:#8a8a99;text-align:center;' +
      'padding:28px 18px;">FINAL VIDEO appears here when a run completes.</div>';
}

async function poll() {
  let state;
  try { state = await api("/api/state"); }
  catch (e) { return; }   // transient blip — keep the page as-is, retry next tick
  ensureShell(state);
  updateStrip(state);
  updateGatebar(state);
  updateControls(state);
  maybeUpdateBody(state);
}

function clearStoryboard() {
  const e = document.getElementById("storyboard"); if (e) e.remove();
}

async function resetAll() {
  let st;
  try { st = await api("/api/state"); } catch (e) { st = {}; }
  if (isActiveRun(st.phase)) {
    if (!confirm("A render is in progress. Reset clears it from the page (the render keeps running on the server). Continue?")) return;
  }
  try {
    await api("/api/reset", {method: "POST",
      headers: {"Content-Type": "application/json"}, body: "{}"});
  } catch (e) {}
  window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__";
  setUrlProject("", "");
  clearStoryboard();
  const chan = document.getElementById("chan");
  const proj = document.getElementById("proj");
  const launch = document.getElementById("launch");
  if (chan) chan.value = "";
  if (proj) proj.innerHTML = "<option>\u2014</option>";
  if (launch) launch.disabled = true;
  poll();
}
async function gate(decision) {
  const s = await api("/api/state");
  const name = s.gate ? s.gate.name : "";
  const r = await api("/api/gate/" + name, {method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({decision})});
  if (r && r.ok === false) { toast("gate error: " + (r.error || "write failed")); }
  else { toast("decision sent: " + decision); }
  poll();
}
function toast(text) {
  let tt = document.getElementById("mc_toast");
  if (!tt) {
    tt = document.createElement("div");
    tt.id = "mc_toast";
    tt.style.cssText = "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);" +
      "background:#1c1c26;color:#e8e6e3;border:1px solid #d4a017;border-radius:8px;" +
      "padding:10px 16px;font-size:13px;z-index:9999;max-width:80vw;box-shadow:0 4px 20px rgba(0,0,0,.5);";
    document.body.appendChild(tt);
  }
  tt.textContent = text;
  tt.style.opacity = "1";
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(function(){ tt.style.opacity = "0"; }, 4000);
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
    '<div class="motioncell" data-shot="' + (shot==null?'':shot) + '" data-dur="' + (b.duration_s != null ? b.duration_s : '') + '">' +
    '<textarea data-mkey="' + mkey + '" class="motionbox" rows="5" ' +
    'placeholder="motion direction (blank = engine default)…" ' +
    'style="width:100%;box-sizing:border-box;background:#1c1c26;color:#e8e6e3;' +
    'border:1px solid #32323e;border-radius:8px;padding:10px;' +
    'font:13px/1.45 ui-monospace,monospace;resize:vertical;">' +
    escapeHtml(stored) + '</textarea>' +
    '<div style="color:#55556a;font-size:11px;margin-top:4px;">motion direction</div>' +
    '<div style="display:flex;gap:6px;margin-top:6px;">' +
    '<button class="mpreset" data-preset="dynamic" title="dynamic cinematic camera movement, powerful momentum, natural realistic motion, dramatic atmosphere" ' +
    'style="flex:1;background:#2a2a36;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;' +
    'padding:7px 4px;cursor:pointer;font:12px ui-monospace,monospace;">Dynamic</button>' +
    '<button class="mpreset" data-preset="slowcrane" title="slow cinematic camera movement, crane-up to wide angle powerful momentum, natural realistic motion, dramatic atmosphere" ' +
    'style="flex:1;background:#2a2a36;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;' +
    'padding:7px 4px;cursor:pointer;font:12px ui-monospace,monospace;">Slow crane-up</button>' +
    '</div>' +
    '<button class="kbbtn" title="Flip this beat to the free Ken-Burns floor (kb_override; slot saved, not slid)" ' +
    'style="width:100%;margin-top:8px;background:#2a2a36;color:#e8e6e3;' +
    'border:1px solid #32323e;border-radius:6px;padding:8px;cursor:pointer;' +
    'font:13px ui-monospace,monospace;">Ken-Burns: off</button>' +
    '<button class="inhbtn" title="Beat plays the unused tail of the previous clip (free; same-scene continuation; derived at render, falls back to Ken Burns if nothing is left)" ' +
    'style="width:100%;margin-top:8px;background:#2a2a36;color:#e8e6e3;' +
    'border:1px solid #32323e;border-radius:6px;padding:8px;cursor:pointer;' +
    'font:13px ui-monospace,monospace;">Inherit previous clip: off</button>' +
    '<div class="inhsum" style="font-size:11px;margin-top:4px;min-height:13px;color:#55556a;"></div>' +
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
    controlsCell =
      '<div class="stillctl" data-shot="' + shot + '">' +
        '<button class="nbfix" style="width:100%;margin-top:8px;background:#c98a1a;color:#fff;' +
          'border:0;border-radius:6px;padding:11px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:700;">&#128295; Fix this image</button>' +
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
      '<div>' + stillCell + '<div style="color:#55556a;font-size:11px;margin-top:4px;">' + ((b && b.render_path) || "still") + '</div></div>' +
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
      const mc = t.closest(".motioncell");
      if (mc) _applyBeatDisable(mc);
    });
  });
  bindStillControls(wrap);
}
function bindStillControls(wrap) {
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
    const msg = ctl.querySelector(".ctlmsg");
    const note = ctl.querySelector("textarea.note");
    const override = ctl.querySelector("textarea.override");
    const regen = ctl.querySelector("button.regen");
    const nbfix = ctl.querySelector("button.nbfix");

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

    regen.addEventListener("click", function() {
      post("/api/restill", {shot: shot, note: note.value, override: override.value},
           override.value.trim() ? "Regenerating (override)" : "Regenerating");
    });
    if (nbfix) nbfix.addEventListener("click", function() {
      post("/api/nbfix", {shot: shot}, "Inspecting &amp; fixing");
    });
  });
  bindAnimateButtons(wrap);
}
const MPRESETS = {
  dynamic: "dynamic cinematic camera movement, powerful momentum, natural realistic motion, dramatic atmosphere",
  slowcrane: "slow cinematic camera movement, crane-up to wide angle powerful momentum, natural realistic motion, dramatic atmosphere"
};
function _applyBeatDisable(cell) {
  // mode invariant: exactly one mode visibly active per beat — Kling (green
  // box border + matching preset green), Ken-Burns (green button), or
  // inherit (green button). KB/inherit beats take no motion direction and
  // must not fire a manual Kling render.
  const dis = cell.dataset.kbon === "1" || cell.dataset.inhon === "1";
  const box = cell.querySelector("textarea.motionbox");
  const anim = cell.querySelector("button.animbtn");
  if (box) {
    box.disabled = dis; box.style.opacity = dis ? "0.45" : "1";
    box.style.border = dis ? "1px solid #32323e" : "1px solid #1c7c4a";
  }
  if (anim) { anim.disabled = dis; anim.style.opacity = dis ? "0.45" : "1"; }
  cell.querySelectorAll("button.mpreset").forEach(function(pb) {
    // mode buttons: always clickable — clicking one while KB or inherit is ON
    // switches the beat back to Kling with that exact direction.
    pb.disabled = false; pb.style.opacity = "1";
    const match = !dis && box && box.value.trim() === MPRESETS[pb.getAttribute("data-preset")];
    pb.style.background = match ? "#1c7c4a" : "#2a2a36";
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
}
function paintInhSums(wrap) {
  // per-mode status line, mirroring the render pass exactly.
  const arr = [];
  wrap.querySelectorAll(".motioncell").forEach(function(c) { arr.push(c); });
  function beatOf(cell) {
    const bx = cell.querySelector("textarea.motionbox");
    return bx ? parseInt((bx.getAttribute("data-mkey") || "").split("/").pop(), 10) : NaN;
  }
  for (var i = 0; i < arr.length; i++) {
    const el = arr[i].querySelector(".inhsum");
    if (!el) continue;
    if (arr[i].dataset.inhon === "1") {
      var j = i - 1;
      while (j >= 0 && arr[j].dataset.inhon === "1") j--;
      if (j < 0) {
        el.textContent = "no source atom - inherit chain reaches beat 0 (falls back free)";
        el.style.color = "#c0392b"; continue;
      }
      if (arr[j].dataset.kbon === "1") {
        el.textContent = "source beat " + beatOf(arr[j]) + " renders Ken-Burns - no atom to inherit (falls back free)";
        el.style.color = "#c0392b"; continue;
      }
      var d = parseFloat(arr[i].getAttribute("data-dur"));
      var total = d, bad = isNaN(d);
      for (var k = j; k < i && !bad; k++) {
        const dk = parseFloat(arr[k].getAttribute("data-dur"));
        if (isNaN(dk)) bad = true; else total += dk;
      }
      if (bad) {
        el.textContent = "Inheriting beat " + beatOf(arr[j]) + " (durations pending)";
        el.style.color = "#8a8a99"; continue;
      }
      const fits = total <= 5.0;
      el.textContent = "Inheriting beat " + beatOf(arr[j]) + " - chain of " + (i - j + 1) +
                       " beats on one atom = " + total.toFixed(2) + "s " +
                       (fits ? "(fits the 5s atom)" : "(exceeds the 5s atom - tail falls back)");
      el.style.color = fits ? "#1c7c4a" : "#c98a1a";
    } else if (arr[i].dataset.kbon === "1") {
      el.textContent = "free Ken-Burns push on its own still - no atom, nothing to inherit from";
      el.style.color = "#8a8a99";
    } else {
      el.textContent = "renders its own 5s Kling atom - source for inherit chains";
      el.style.color = "#8a8a99";
    }
  }
}
function bindAnimateButtons(wrap) {
  const CH = (window.__SEL_VIEW || "/").split("/")[0];
  const PR = (window.__SEL_VIEW || "/").split("/").slice(1).join("/");
  // paint KB state from the policy file (the truth) on every storyboard render
  api("/api/render_policy?channel=" + encodeURIComponent(CH) +
      "&project=" + encodeURIComponent(PR))
    .then(function(r) {
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
      paintInhSums(wrap);
    }).catch(function() {});
  wrap.querySelectorAll(".motioncell").forEach(function(cell) {
    const btn = cell.querySelector("button.animbtn");
    const shot = parseInt(cell.getAttribute("data-shot"), 10);
    const box = cell.querySelector("textarea.motionbox");
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
          if (r && r.ok) { paintKB(cell, r.on); if (r.on) paintInherit(cell, false); paintInhSums(wrap); }
        } catch (e) { /* leave painted state; next storyboard render re-reads the file */ }
      });
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
          if (r && r.ok) { paintInherit(cell, r.on); if (r.on) paintKB(cell, false); paintInhSums(wrap); }
        } catch (e) { /* next storyboard render re-reads the file */ }
      });
    }
    // motion presets: stamp an exact proven direction into the box, then persist
    // through the same seam as typing (edit map + saveMotion -> storyboard.json).
    cell.querySelectorAll("button.mpreset").forEach(function(pb) {
      pb.addEventListener("click", async function() {
        if (!box) return;
        const t = MPRESETS[pb.getAttribute("data-preset")];
        if (!t) return;
        const pbeat = parseInt((box.getAttribute("data-mkey") || "").split("/").pop(), 10);
        try {
          if (cell.dataset.kbon === "1" && !isNaN(pbeat)) {
            const r = await api("/api/kb_toggle", {method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({channel: CH, project: PR, beat: pbeat})});
            if (r && r.ok) paintKB(cell, r.on);
          }
          if (cell.dataset.inhon === "1" && !isNaN(pbeat)) {
            const r2 = await api("/api/inherit_toggle", {method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({channel: CH, project: PR, beat: pbeat})});
            if (r2 && r2.ok) paintInherit(cell, r2.on);
          }
        } catch (e) { /* policy file re-read on next storyboard render */ }
        box.value = t;
        window.__MOTION_EDITS[box.getAttribute("data-mkey")] = t;
        saveMotion();
        _applyBeatDisable(cell);
        paintInhSums(wrap);
      });
    });
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
    const msg = cell.querySelector(".animmsg");
    function reloadClip() {
      const n3 = String(shot).padStart(3, "0");
      const grid = cell.parentElement.parentElement;  // the 5-col grid (cell is inside the motion column)
      const q = "?channel=" + encodeURIComponent(CH) + "&project=" + encodeURIComponent(PR) + "&key=" + KEY;
      const src = "/clips/shot_" + n3 + ".mp4" + q + "&_t=" + Date.now();
      const vid = grid.querySelector('video[src*="shot_' + n3 + '.mp4"]');
      if (vid) {
        vid.src = src; vid.load();
        return true;
      }
      const clipCol = grid.lastElementChild;  // column 5 = the clip cell
      if (clipCol) {
        const v = document.createElement("video");
        v.src = src; v.muted = true; v.loop = true; v.autoplay = true;
        v.setAttribute("playsinline", "");
        v.style.cssText = "width:100%;max-width:1100px;border-radius:8px;background:#000;display:block;";
        const ph = clipCol.firstElementChild;
        if (ph) { clipCol.insertBefore(v, ph); ph.remove(); }
        else { clipCol.insertBefore(v, clipCol.firstChild); }
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
      await saveMotion();  // persist the typed direction before it drives the render
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
    return _page.replace("@@VERSTAMP@@", _verstamp)


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
                "video": paths["project"]}.get(kind)
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
        if path == "/api/render_policy":
            q = parse_qs(parsed.query)
            self._handle_render_policy_get(q.get("channel", [None])[0],
                                           q.get("project", [None])[0]); return
        if path == "/api/meta":
            q = parse_qs(parsed.query)
            self._handle_meta_get(q.get("channel", [None])[0],
                                  q.get("project", [None])[0]); return
        if path == "/api/assemble_status":
            q = parse_qs(parsed.query)
            self._handle_assemble_status(q.get("channel", [None])[0],
                                         q.get("project", [None])[0]); return
        if path == "/api/upload_status":
            q = parse_qs(parsed.query)
            self._handle_upload_status(q.get("channel", [None])[0],
                                       q.get("project", [None])[0]); return
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

    def _handle_motion(self, body):
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

    def _handle_assemble(self, body):
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        try:
            paths = resolve_paths(ch, pr, _REPO)
            project_dir = Path(paths["project"])
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
                               args=(key, project_dir), daemon=True)
        th.start()
        self._json(200, {"ok": True, "started": True}); return

    def _handle_assemble_status(self, ch, pr):
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
        self._json(200, st); return

    def _handle_meta_get(self, ch, pr):
        """Read the YouTube metadata (title/description/tags) from the project's
        beats_full.json header. Also reports whether final_video.mp4 exists."""
        if not (ch and pr):
            self._json(400, {"error": "channel + project required"}); return
        try:
            paths = resolve_paths(ch, pr, _REPO)
            bf = Path(paths["project"]) / "beats_full.json"
            header = {}
            if bf.exists():
                data = json.load(open(bf))
                header = data.get("header", {}) if isinstance(data, dict) else {}
            tags = header.get("tags", [])
            if isinstance(tags, list):
                tags = ", ".join(str(t) for t in tags)
            video = Path(paths["project"]) / "final_video.mp4"
            self._json(200, {
                "ok": True,
                "title": header.get("title", ""),
                "description": header.get("description", ""),
                "tags": tags,
                "has_video": video.exists(),
                "video_name": "final_video.mp4",
            })
        except Exception as e:
            self._json(500, {"error": str(e)})

    def _handle_render_policy_get(self, ch, pr):
        """Read TIERED RENDER N for a project: render_policy.json kling_count (default 40)."""
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "channel + project required"}); return
        import json as _json
        paths = resolve_paths(ch, pr, _REPO)
        rp = paths["project"] / "render_policy.json"
        n = 40
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
                         "kb_override": kb, "inherit_prev": inh, "default": 40}); return

    def _handle_kb_toggle(self, body):
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
        if on:
            try:
                _inh = sorted({int(x) for x in existing.get("inherit_prev", [])} - {beat})
            except Exception:
                _inh = []
            if _inh:
                policy["inherit_prev"] = _inh
            else:
                policy.pop("inherit_prev", None)
        if kb:
            policy["kb_override"] = kb
        else:
            policy.pop("kb_override", None)
        try:
            rp.write_text(_json.dumps(policy, indent=2))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"write failed: {e}"}); return
        self._json(200, {"ok": True, "on": on, "beat": beat, "kb_override": kb}); return

    def _handle_inherit_toggle(self, body):
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

    def _handle_render_policy_post(self, body):
        """Write TIERED RENDER policy to render_policy.json at the project root.
        MERGES with any existing file: kling_count and static are each updated
        only when present in the body, so a plain N-change never clobbers static
        and setting static never clobbers N. (PATCH_STATIC_BUTTON_APPLIED)"""
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
        existing = {}
        if rp.is_file():
            try:
                existing = _json.loads(rp.read_text()) or {}
            except Exception:
                existing = {}
        policy = dict(existing)
        policy["kling_count"] = kc
        if "static" in (body or {}):
            policy["static"] = bool(body.get("static"))
        try:
            rp.write_text(_json.dumps(policy, indent=2))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"write failed: {e}"}); return
        self._json(200, {"ok": True, "kling_count": kc,
                         "static": bool(policy.get("static", False))}); return

    def _handle_reset(self):
        """Clear the active job record (+log) so the page returns to idle base.
        Mirrors the manual rm of .mc_jobs/<id>.{json,log}. A detached render keeps
        running server-side; this only drops the page's handle on it."""
        jid = active_job_id()
        if not jid:
            self._json(200, {"ok": True, "cleared": None}); return
        d = jobs_dir(_REPO)
        removed = []
        for ext in (".json", ".log"):
            f = d / f"{jid}{ext}"
            try:
                if f.exists():
                    f.unlink(); removed.append(f.name)
            except Exception:
                pass
        self._json(200, {"ok": True, "cleared": jid, "removed": removed}); return

    def _handle_animate(self, body):
        if not _ANIMATE_OK:
            self._json(503, {"ok": False,
                "error": f"animate unavailable: {_ANIMATE_IMPORT_ERR}"}); return
        shot_idx = body.get("shot")
        motion_prompt = (body.get("motion_prompt") or "").strip()
        if not isinstance(shot_idx, int):
            self._json(400, {"ok": False, "error": "shot must be an integer"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        if not motion_prompt:
            motion_prompt = _channel_default_motion(ch, pr)
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
        # TIERED RENDER (d): route this single beat by the same policy as the batch.
        project_root = stills_dir.parent.parent  # <project>/ — render_policy/durations/_index live here
        kling_count = _tiered_kling_count(project_root)
        beat_index = _tiered_beat_index(shot_idx, project_root)
        engine = "kling" if beat_index < kling_count else "kenburns"
        duration = _tiered_duration(beat_index, project_root)
        sys.stderr.write(f"[Animate] shot {shot_idx:03d} -> {engine} (beat {beat_index}, N={kling_count})\n")
        key = _animate_key(ch, pr, shot_idx)
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "running"}
        th = _threading.Thread(target=_run_animate_bg,
                               args=(key, still_path, motion_prompt, out_path, engine, duration),
                               daemon=True)
        th.start()
        self._json(200, {"ok": True, "started": True, "shot": shot_idx, "engine": engine}); return

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

        beat = beats_by_idx[shot_idx]
        refs = beat.get("_reference_images") or None
        if override:
            final_prompt = override; mode = "OVERRIDE"
        else:
            resolved = resolve_canon_tokens(beat.get("image_prompt", ""), ctx["canon"])
            final_prompt = (f"{resolved.rstrip(' .')}. REGENERATION FEEDBACK: {note}"
                            if note else resolved)
            mode = "NORMAL"
        # PATCH_FIXBTN_APPLIED: channel-aware re-render. Routes through
        # recreation_pipeline.generate_still so reference beats keep their ref
        # sheet(s) and every channel renders on its own model (flux only as the
        # engine's own refusal fallback). The old path was flux-hardwired and
        # silently stripped reference identity on {skeptic}/{driver}/{brain} beats.
        sys.stderr.write(f"[Regenerate] shot {shot_idx:03d} [{mode}] "
                         f"(refs={len(refs) if refs else 0})\n")
        backup_existing_still(ctx["stills_dir"], shot_idx)
        out = ctx["stills_dir"] / f"shot_{shot_idx:03d}.png"
        try:
            ok = bool(_recp_generate_still(final_prompt, out, reference_images=refs))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"channel-model render failed: {e}"}); return
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

    def _handle_nbfix(self, body):
        """Nano-Banana Fix: Claude Sonnet vision INSPECTS the still and names the
        flaw (warped/extra hands, extra fingers, melted or duplicated features, ...),
        then re-renders the CORRECTED prompt through the engine's channel-aware
        generate_still with the shot's _reference_images from storyboard.json -- NB2
        /edit (reference) for {skeptic} beats on QQrew, NB2 text for wides, flux only
        on refusal. Not a blind re-roll: the diagnosis targets the warp.
        (PATCH_NBFIX_BUTTON_APPLIED) (PATCH_NBFIX_VISION_APPLIED)"""
        if not _ANIMATE_OK:
            self._json(503, {"ok": False,
                "error": f"nano-banana fix unavailable: {_ANIMATE_IMPORT_ERR}"}); return
        if not _RESTILL_OK:
            self._json(503, {"ok": False,
                "error": f"restill helpers unavailable: {_RESTILL_IMPORT_ERR}"}); return
        if _ANTHROPIC_CLIENT is None:
            self._json(503, {"ok": False, "error":
                "nano-banana fix needs vision: anthropic not installed or ANTHROPIC_API_KEY not set"}); return
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
        beat = beats_by_idx[shot_idx]
        out = ctx["stills_dir"] / f"shot_{shot_idx:03d}.png"
        if not out.exists():
            self._json(404, {"ok": False, "error": f"still not found: {out.name}"}); return
        intended = (beat.get("image_prompt") or "").strip()
        refs = beat.get("_reference_images") or None

        # 1. VISION DIAGNOSIS (same art-director pass as AI Fix)
        sys.stderr.write(f"[NB fix] shot {shot_idx:03d} diagnosing...\n")
        try:
            img = out.read_bytes()
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

        # 2. RE-RENDER the corrected prompt on the CHANNEL model, reference-aware
        sys.stderr.write(f"[NB fix] shot {shot_idx:03d} re-render on channel model "
                         f"(refs={len(refs) if refs else 0}) -> {diagnosis[:60]}\n")
        backup_existing_still(ctx["stills_dir"], shot_idx)
        try:
            res = _recp_generate_still(corrected, out, reference_images=refs)
        except Exception as e:
            self._json(500, {"ok": False,
                "error": f"channel-model render failed: {e}", "diagnosis": diagnosis}); return
        if res:
            self._json(200, {"ok": True, "shot": shot_idx, "changed": True,
                "diagnosis": diagnosis,
                "mode": ("NB2 /edit" if refs else "NB2 text")}); return
        self._json(500, {"ok": False,
            "error": "channel-model generation failed after diagnosis", "diagnosis": diagnosis})

    def _handle_thumbnail(self, body):
        """Composite a thumbnail from a chosen still + headline/subtitle, using the
        channel's locked thumbnail block (make_thumbnail.py). --project points at
        modea (so --shot finds modea/stills/shot_NNN.png); --out writes thumbnail.png
        at the PROJECT ROOT where upload_episode.py looks. Free PIL re-composite:
        iterate still-number + text as often as you like. (PATCH_THUMBNAIL_PANEL_APPLIED)"""
        shot = body.get("shot")
        title = (body.get("title") or "").strip()
        subtitle = (body.get("subtitle") or "").strip()
        try:
            shot = int(shot)
        except Exception:
            self._json(400, {"ok": False, "error": "shot must be an integer"}); return
        if not title:
            self._json(400, {"ok": False, "error": "headline (title) is required"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        paths = resolve_paths(ch, pr, _REPO)
        modea = Path(paths["modea"])
        root = Path(paths["project"])
        still = modea / "stills" / f"shot_{shot:03d}.png"
        if not still.exists():
            self._json(404, {"ok": False,
                "error": f"still not found: shot_{shot:03d}.png (check the number)"}); return
        out = root / "thumbnail.png"
        import subprocess as _sp
        cmd = [sys.executable, str(Path(_SHARED) / "make_thumbnail.py"),
               "--project", str(modea),
               "--shot", str(shot),
               "--channel", ch,
               "--title", title,
               "--out", str(out)]
        if subtitle:
            cmd += ["--subtitle", subtitle]
        try:
            r = _sp.run(cmd, cwd=str(_REPO), capture_output=True, text=True)
        except Exception as e:
            self._json(500, {"ok": False, "error": f"thumbnail failed: {e}"}); return
        if r.returncode != 0 or not out.exists():
            tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]
            self._json(500, {"ok": False, "error": " / ".join(tail) or "make_thumbnail failed"}); return
        self._json(200, {"ok": True, "shot": shot}); return

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
            _lr = launch_job(ch, pr, dry, log)
            if _lr.get("ok") is False:
                self._json(409, _lr); return            # refuse-if-live: not a success
            self._json(200, {"ok": True, **_lr}); return

        if path.startswith("/api/gate/"):
            name = path[len("/api/gate/"):]
            jid = active_job_id()
            decision = body.get("decision")
            self._json(200, decide_gate(jid, decision)); return

        if path == "/api/render_policy":
            self._handle_render_policy_post(body); return
        if path == "/api/kb_toggle":
            self._handle_kb_toggle(body); return
        if path == "/api/inherit_toggle":
            self._handle_inherit_toggle(body); return
        if path == "/api/restill":
            self._handle_restill(body); return
        if path == "/api/aifix":
            self._handle_aifix(body); return
        if path == "/api/nbfix":
            self._handle_nbfix(body); return
        if path == "/api/motion":
            self._handle_motion(body); return
        if path == "/api/animate":
            self._handle_animate(body); return
        if path == "/api/assemble":
            self._handle_assemble(body); return
        if path == "/api/upload":
            self._handle_upload(body); return
        if path == "/api/thumbnail":
            self._handle_thumbnail(body); return
        if path == "/api/reset":
            self._handle_reset(); return

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
