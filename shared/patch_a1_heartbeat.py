#!/usr/bin/env python3
"""
patch_a1_heartbeat.py -- A1: heartbeat + dead/frozen-run detection, and the
                         post-gate "animating" phase fix (v0.6).

WHY (two bugs, one root cause: the job record not reflecting reality)
  1. FALSE-HANG: run_modea_leg goes gate(go) -> _animate, but NOTHING writes
     phase "animating" in between, so the record sits at gate_stills through the
     ENTIRE animate. On a 4-beat run that looked like a hang; on a 132-beat Kling
     run the page would show a live gate for 30 min of healthy animation.
  2. DEAD/FROZEN RUN: a killed orchestrate leaves the record frozen at a gate
     phase, so the page renders a live gate for a process that is gone.

WHAT THIS DOES (3 files)
  gate_protocol.py:
    - set_phase() also stamps heartbeat = time.time() (every phase change pulses).
    - new touch_heartbeat(job_id, repo_root): same atomic read-modify-write.
    - await_gate JOB-mode poll loop calls touch_heartbeat() every poll, so a run
      PARKED AT A GATE pulses continuously *because the live process is polling* --
      liveness is process-paced, not human-paced. A dead process stops pulsing.
  modea_leg.py:
    - import set_phase; after the gate returns "go", before _animate, write
      phase "animating" (gate_mode == job only). Fixes the false-hang.
  pipeline_server.py (build_state):
    - if an active run is at a GATE phase and now - heartbeat > STALE_SECONDS,
      override phase -> "stale". Gate phases only (they pulse reliably); work legs
      (animating/assembling) are single long blocking calls and are NOT stale-checked
      here, so a slow-but-alive render never false-flags. phaseStrip already renders
      "stale"; STALE_SECONDS = 300.
    - APP_VERSION -> v0.6.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `def touch_heartbeat`). Every anchor verified
  exactly once across all three files BEFORE writing any; per-file .pre_a1 backups;
  all files py_compile-checked; full rollback if any check fails.
"""
import sys
import shutil
import py_compile
from pathlib import Path

GP   = Path("shared/mission_control/gate_protocol.py")
MA   = Path("shared/modea_leg.py")
PS   = Path("shared/mission_control/pipeline_server.py")
MARKER = "def touch_heartbeat"

# ---------------------------------------------------------------- gate_protocol
GP_OLD_SETPHASE = '''def set_phase(job_id: str, phase: str, repo_root: Path | None = None) -> None:
    rec = read_job(job_id, repo_root)
    if rec:
        rec["phase"] = phase
        write_job(job_id, rec, repo_root)'''

GP_NEW_SETPHASE = '''def set_phase(job_id: str, phase: str, repo_root: Path | None = None) -> None:
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
        write_job(job_id, rec, repo_root)'''

# await_gate poll loop: add a heartbeat pulse each iteration.
GP_OLD_POLL = '''    # Block the JOB (not a terminal) until a decision appears in the record.
    while True:
        rec = read_job(job_id, repo_root)
        gate = rec.get("gate") or {}
        decision = gate.get("decision")
        if decision in options:'''

GP_NEW_POLL = '''    # Block the JOB (not a terminal) until a decision appears in the record.
    while True:
        touch_heartbeat(job_id, repo_root)  # A1: prove the process is alive each poll
        rec = read_job(job_id, repo_root)
        gate = rec.get("gate") or {}
        decision = gate.get("decision")
        if decision in options:'''

# ---------------------------------------------------------------- modea_leg
# import line: pull in set_phase alongside await_gate.
MA_OLD_IMPORT = '''from gate_protocol import await_gate'''
MA_NEW_IMPORT = '''from gate_protocol import await_gate, set_phase'''

# after the gate returns "go", before _animate: write phase "animating".
MA_OLD_ANIM = '''    # Phase 3: animate-only
    clips = _animate(ctx, engine_project, engine_cwd)'''
MA_NEW_ANIM = '''    # A1: the gate cleared with "go" -> we are about to animate. Update the record so
    # the page stops showing a live stills gate during the (possibly long) animate.
    if ctx.get("gate_mode") == "job" and ctx.get("job_id"):
        set_phase(ctx["job_id"], "animating", ctx.get("repo_root"))
    # Phase 3: animate-only
    clips = _animate(ctx, engine_project, engine_cwd)'''

# ---------------------------------------------------------------- pipeline_server
PS_OLD_VER = '''APP_VERSION = "v0.5"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
PS_NEW_VER = '''APP_VERSION = "v0.6"  # hand-bumped each shipped page change; pairs with the auto git SHA
STALE_SECONDS = 300  # A1: a gate run with no heartbeat for this long is treated as dead'''

# build_state: after phase is read from rec, flip gate phases to stale if heartbeat is old.
PS_OLD_STALE = '''    rec = read_job(jid, _REPO)
    phase = rec.get("phase", "running")'''
PS_NEW_STALE = '''    rec = read_job(jid, _REPO)
    phase = rec.get("phase", "running")
    # A1: a run parked at a gate pulses a heartbeat every poll; if it has gone silent
    # for STALE_SECONDS the process is dead -> show it as stale so the page recovers.
    # Gate phases only: work legs (animating/assembling) are long blocking calls that
    # do not pulse mid-leg, so we never stale-flag a slow-but-alive render here.
    if phase in ("gate_audio", "gate_stills"):
        hb = rec.get("heartbeat")
        if hb and (time.time() - float(hb)) > STALE_SECONDS:
            phase = "stale"'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    files = {GP: "gate_protocol", MA: "modea_leg", PS: "pipeline_server"}
    for p, n in files.items():
        if not p.exists():
            die(f"{p} not found ({n}) -- run from the repo root on the laptop.")

    gp, ma, ps = GP.read_text(), MA.read_text(), PS.read_text()

    if MARKER in gp:
        print(f"Already patched ({MARKER!r} present in gate_protocol) -- no changes.")
        return

    # Preconditions: APP_VERSION must be v0.5 (version stamp patch applied first).
    if PS_OLD_VER not in ps:
        die("APP_VERSION v0.5 anchor not found -- apply patch_version_stamp.py first, "
            "or the heading/version state isn't where A1 expects it. Nothing written.")

    edits = [
        (GP, gp, "set_phase",       GP_OLD_SETPHASE, GP_NEW_SETPHASE),
        (GP, gp, "await_gate poll", GP_OLD_POLL,     GP_NEW_POLL),
        (MA, ma, "modea import",    MA_OLD_IMPORT,   MA_NEW_IMPORT),
        (MA, ma, "modea animating", MA_OLD_ANIM,     MA_NEW_ANIM),
        (PS, ps, "version bump",    PS_OLD_VER,      PS_NEW_VER),
        (PS, ps, "stale flip",      PS_OLD_STALE,    PS_NEW_STALE),
    ]
    for p, src, label, old, _ in edits:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND in {p.name} -- nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x in {p.name} (expected 1) -- nothing written.")

    new_gp = gp.replace(GP_OLD_SETPHASE, GP_NEW_SETPHASE).replace(GP_OLD_POLL, GP_NEW_POLL)
    new_ma = ma.replace(MA_OLD_IMPORT, MA_NEW_IMPORT).replace(MA_OLD_ANIM, MA_NEW_ANIM)
    new_ps = ps.replace(PS_OLD_VER, PS_NEW_VER).replace(PS_OLD_STALE, PS_NEW_STALE)

    # 'time' must be importable in gate_protocol (set_phase/await_gate now use it).
    if "import time" not in new_gp:
        die("gate_protocol.py does not import time -- set_phase heartbeat would NameError. "
            "Nothing written. (await_gate already uses time.time(), so this should pass.)")

    backups = []
    try:
        for p, content in [(GP, new_gp), (MA, new_ma), (PS, new_ps)]:
            b = p.with_suffix(p.suffix + ".pre_a1")
            shutil.copy2(p, b)
            backups.append((p, b))
            p.write_text(content)
        # verify + compile all three
        if MARKER not in GP.read_text():
            raise RuntimeError("touch_heartbeat missing post-write")
        if 'set_phase(ctx["job_id"], "animating"' not in MA.read_text():
            raise RuntimeError("animating set_phase missing post-write")
        if 'phase = "stale"' not in PS.read_text() or 'APP_VERSION = "v0.6"' not in PS.read_text():
            raise RuntimeError("stale flip or version bump missing post-write")
        for p in (GP, MA, PS):
            py_compile.compile(str(p), doraise=True)
    except Exception as e:
        for p, b in backups:
            shutil.copy2(b, p)
        die(f"post-write check failed -- ALL files restored from backup.\n{e}")

    print("OK patched 3 files:")
    print(f"   {GP}  (.pre_a1)  -- heartbeat in set_phase + await_gate poll")
    print(f"   {MA}  (.pre_a1)  -- set_phase animating after the gate (false-hang fix)")
    print(f"   {PS}  (.pre_a1)  -- stale flip for dead gate runs + APP_VERSION v0.6")
    print()
    print("AFTER you pull on the box, restart + verify version + node-check:")
    print("   systemctl --user restart mission-control.service")
    print("   curl -s \"http://127.0.0.1:8002/api/state?key=fh2026\" | python3 -c \"import sys,json;d=json.load(sys.stdin);print(d.get('version'),d.get('sha'))\"")
    print("   git rev-parse --short HEAD   # must match the sha above; version must read v0.6")
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
