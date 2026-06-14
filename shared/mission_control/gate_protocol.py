"""
Mission Control — Phase 1: the gate protocol (inverted control at the gates).

ONE function the gates call instead of input(). Behaviour is chosen by
ctx["gate_mode"]:

  "cli"  (DEFAULT) — does exactly what input() did before. Byte-identical
                     terminal behaviour. The safety net / headless fallback.
  "job"            — writes the gate state into the job record on disk, then
                     POLLS the record for a decision (blocking the JOB, not a
                     terminal). The decision is written by some other client:
                     poke_gate.py now, the web API later. Terminal and browser
                     become two clients of the same gate STATE.

The job record is a small JSON file at:
    <repo_root>/.mc_jobs/<job_id>.json

This module has NO http, NO UI. It only reads/writes that file. That is the
whole point of Phase 1 — prove the seam in isolation before any server exists.

Job record shape (the gate-relevant slice):
{
  "job_id": "...", "channel": "...", "project": "...",
  "phase": "gate_audio",
  "gate": {
    "name": "audio",
    "status": "waiting",          # waiting | decided
    "payload": { ... },           # what the human needs to decide (voice, minutes, ...)
    "options": ["keep", "swap"],
    "decision": null,             # set by poke_gate.py / web API -> e.g. "keep"
    "decided_at": null
  }
}
"""

from __future__ import annotations
import os
import json
import time
from pathlib import Path


# --------------------------------------------------------------------------
# Job-record location + IO
# --------------------------------------------------------------------------

def jobs_dir(repo_root: Path | None = None) -> Path:
    root = repo_root or Path(__file__).resolve().parents[2]
    d = root / ".mc_jobs"
    d.mkdir(exist_ok=True)
    return d


def job_path(job_id: str, repo_root: Path | None = None) -> Path:
    return jobs_dir(repo_root) / f"{job_id}.json"


def read_job(job_id: str, repo_root: Path | None = None) -> dict:
    p = job_path(job_id, repo_root)
    if not p.is_file():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def write_job(job_id: str, record: dict, repo_root: Path | None = None) -> None:
    """Atomic-ish write: write to a temp file then replace, so a reader never
    sees a half-written record."""
    p = job_path(job_id, repo_root)
    tmp = p.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    os.replace(tmp, p)


def init_job(job_id: str, channel: str, project: str,
             repo_root: Path | None = None) -> dict:
    """Create (or load) the job record at run start. phase starts 'running'."""
    existing = read_job(job_id, repo_root)
    if existing:
        return existing
    rec = {
        "job_id": job_id,
        "channel": channel,
        "project": project,
        "phase": "running",
        "gate": None,
        "started_at": time.time(),
    }
    write_job(job_id, rec, repo_root)
    return rec


def set_phase(job_id: str, phase: str, repo_root: Path | None = None) -> None:
    rec = read_job(job_id, repo_root)
    if rec:
        rec["phase"] = phase
        rec["heartbeat"] = time.time()
        write_job(job_id, rec, repo_root)


def touch_heartbeat(job_id: str, repo_root: Path | None = None) -> None:
    """Pulse the record's liveness clock without changing phase. Called every poll
    while a JOB-mode gate is blocking, so a run parked at a gate keeps proving the
    process is alive (a dead process simply stops pulsing). Atomic read-modify-write,
    same as set_phase; safe against the page writing a decision concurrently."""
    rec = read_job(job_id, repo_root)
    if rec:
        rec["heartbeat"] = time.time()
        write_job(job_id, rec, repo_root)


# --------------------------------------------------------------------------
# The gate itself
# --------------------------------------------------------------------------

def await_gate(ctx, name: str, payload: dict, options: list[str],
               cli_prompt: str, cli_map: dict | None = None,
               poll_seconds: float = 1.5, phase: str | None = None) -> str:
    """Reach a gate; return the decision string (one of `options`).

    cli mode  : print cli_prompt, read input(), map it via cli_map -> a canonical
                option, loop until valid. (cli_map lets "1"->"keep", "2"->"swap",
                "go"/"y"/"done"->"go", etc., preserving today's accepted inputs.)
    job mode  : write {gate:{name,status:waiting,payload,options,decision:null}}
                into the job record, set phase, then poll until decision is set.

    ctx keys used: "gate_mode" (default "cli"), "job_id", "repo_root" (optional).
    """
    gate_mode = ctx.get("gate_mode", "cli")
    cli_map = cli_map or {}

    # ---- CLI mode: exactly today's behaviour -----------------------------
    if gate_mode == "cli":
        while True:
            raw = input(cli_prompt).strip().lower()
            if raw in cli_map:
                return cli_map[raw]
            if raw in options:
                return raw
            # unrecognised -> loop (matches the old gates' re-prompt behaviour)
            print("  (didn't catch that — try again)")

    # ---- JOB mode: write gate state, poll for a decision -----------------
    job_id = ctx["job_id"]
    repo_root = ctx.get("repo_root")
    if phase:
        set_phase(job_id, phase, repo_root)

    rec = read_job(job_id, repo_root)
    rec["gate"] = {
        "name": name,
        "status": "waiting",
        "payload": payload,
        "options": options,
        "decision": None,
        "decided_at": None,
    }
    if phase:
        rec["phase"] = phase
    write_job(job_id, rec, repo_root)

    # Block the JOB (not a terminal) until a decision appears in the record.
    while True:
        touch_heartbeat(job_id, repo_root)  # A1: prove the process is alive each poll
        rec = read_job(job_id, repo_root)
        gate = rec.get("gate") or {}
        decision = gate.get("decision")
        if decision in options:
            # clear the gate, mark decided, hand back the decision
            gate["status"] = "decided"
            gate["decided_at"] = time.time()
            rec["gate"] = gate
            write_job(job_id, rec, repo_root)
            return decision
        time.sleep(poll_seconds)
