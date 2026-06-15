#!/usr/bin/env python3
"""
patch_pid_reaping.py -- reap dead-process records (Hardening C, v1.8).

WHY (the last gap in "always correct state")
  A1's stale-check only fires on GATE phases (work legs are long blocking calls that can't
  pulse a heartbeat mid-leg, so we must not time-flag them). But a hard-killed orchestrate
  mid-`animating` (exactly today's 2-hour orphan, or a crash) leaves a non-terminal record
  with NO terminal phase and a frozen heartbeat that the gate-only stale-check ignores ->
  it still looks live. A then keeps selecting it; B then refuses new launches against it.
  The missing signal: is the orchestrate PROCESS actually alive?

WHAT THIS DOES (2 files)
  gate_protocol.set_phase: also stamp rec["pid"] = os.getpid(). set_phase runs INSIDE
    orchestrate (orchestrate calls set_phase('running') early), so this is orchestrate's
    real pid -- the thing whose liveness we can check.
  pipeline_server.build_state: after reading the record, if phase is NON-terminal and the
    record carries a pid that is NOT alive (os.kill(pid, 0) -> ProcessLookupError), flip
    phase to "dead" (terminal). Covers work legs too. So a killed orchestrate is reaped:
    A (active_job_id) skips it as terminal, B (launch guard) won't refuse against it, and
    the page shows it recoverable (rendered like stale).
  Adds "dead" to _TERMINAL_PHASES so A and B treat it as over.
  APP_VERSION -> v1.8.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `pid liveness reaping`). Anchors verified once across
  both files; per-file .pre_pidreap backups; py_compile both; full rollback on any failure.
  Requires v1.7.
"""
import sys
import shutil
import py_compile
from pathlib import Path

GP = Path("shared/mission_control/gate_protocol.py")
PS = Path("shared/mission_control/pipeline_server.py")
MARKER = "pid liveness reaping"

# --- 1. set_phase stamps pid (gate_protocol) ---------------------------------
GP_OLD = '''def set_phase(job_id: str, phase: str, repo_root: Path | None = None) -> None:
    rec = read_job(job_id, repo_root)
    if rec:
        rec["phase"] = phase
        rec["heartbeat"] = time.time()
        write_job(job_id, rec, repo_root)'''
GP_NEW = '''def set_phase(job_id: str, phase: str, repo_root: Path | None = None) -> None:
    rec = read_job(job_id, repo_root)
    if rec:
        rec["phase"] = phase
        rec["heartbeat"] = time.time()
        rec["pid"] = os.getpid()  # pid liveness reaping: orchestrate's real pid (set_phase runs in it)
        write_job(job_id, rec, repo_root)'''

# --- 2. build_state reaps a dead-pid non-terminal record (pipeline_server) ----
PS_OLD = '''    rec = read_job(jid, _REPO)
    phase = rec.get("phase", "running")
    # A1: a run parked at a gate pulses a heartbeat every poll; if it has gone silent'''
PS_NEW = '''    rec = read_job(jid, _REPO)
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
    # A1: a run parked at a gate pulses a heartbeat every poll; if it has gone silent'''

# add "dead" to the terminal set (A's tuple)
PS_OLD_TERM = '''_TERMINAL_PHASES = ("done", "stopped", "error", "stale")'''
PS_NEW_TERM = '''_TERMINAL_PHASES = ("done", "stopped", "error", "stale", "dead")'''

PS_OLD_VER = '''APP_VERSION = "v1.7"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
PS_NEW_VER = '''APP_VERSION = "v1.8"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    for p, n in [(GP, "gate_protocol"), (PS, "pipeline_server")]:
        if not p.exists():
            die(f"{p} not found ({n}) -- run from the repo root on the laptop.")

    gp, ps = GP.read_text(), PS.read_text()

    if MARKER in gp or MARKER in ps:
        print(f"Already patched ({MARKER!r} present) -- no changes made.")
        return
    if PS_OLD_VER not in ps:
        die("APP_VERSION v1.7 anchor not found -- apply patch_launch_idempotent.py (v1.7) first. Nothing written.")
    if "_TERMINAL_PHASES" not in ps:
        die("_TERMINAL_PHASES not found -- A (v1.6) must be applied first. Nothing written.")
    if "import os" not in gp:
        die("`import os` not found in gate_protocol.py -- needed for os.getpid(). Nothing written.")

    edits = [
        (GP, gp, "set_phase pid", GP_OLD, GP_NEW),
        (PS, ps, "build_state reap", PS_OLD, PS_NEW),
        (PS, ps, "terminal set", PS_OLD_TERM, PS_NEW_TERM),
        (PS, ps, "version", PS_OLD_VER, PS_NEW_VER),
    ]
    for p, src, label, old, _ in edits:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND in {p.name} -- nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x in {p.name} (expected 1) -- nothing written.")

    new_gp = gp.replace(GP_OLD, GP_NEW)
    new_ps = ps.replace(PS_OLD, PS_NEW).replace(PS_OLD_TERM, PS_NEW_TERM).replace(PS_OLD_VER, PS_NEW_VER)

    backups = []
    try:
        for p, content in [(GP, new_gp), (PS, new_ps)]:
            b = p.with_suffix(p.suffix + ".pre_pidreap")
            shutil.copy2(p, b)
            backups.append((p, b))
            p.write_text(content)
        if 'rec["pid"] = os.getpid()' not in GP.read_text():
            raise RuntimeError("pid stamp missing in gate_protocol")
        chk = PS.read_text()
        if "ProcessLookupError" not in chk: raise RuntimeError("reap check missing")
        if '"dead"' not in chk: raise RuntimeError("dead not in terminal set")
        if 'APP_VERSION = "v1.8"' not in chk: raise RuntimeError("version not bumped")
        for p in (GP, PS):
            py_compile.compile(str(p), doraise=True)
    except Exception as e:
        for p, b in backups:
            shutil.copy2(b, p)
        die(f"post-write check failed -- ALL files restored.\n{e}")

    print("OK patched 2 files:")
    print(f"   {GP}  (.pre_pidreap)  -- set_phase stamps pid")
    print(f"   {PS}  (.pre_pidreap)  -- build_state reaps dead-pid records + APP_VERSION v1.8")
    print()
    print("NOTE: existing records (incl the live 70smusic run) have no pid yet -- it gets")
    print("stamped on the NEXT set_phase call. The live run keeps working; reaping applies")
    print("to runs going forward. No restart of orchestrate needed.")
    print()
    print("AFTER pull on the box:")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   verify v1.8 + that 70smusic still shows running:")
    print("   curl -s \"http://127.0.0.1:8002/api/state?key=fh2026\" | python3 -c \"import sys,json;d=json.load(sys.stdin);print(d.get('version'),d.get('phase'),d.get('job_id'))\"")
    print("   git rev-parse --short HEAD   # must match; version v1.8")


if __name__ == "__main__":
    main()
