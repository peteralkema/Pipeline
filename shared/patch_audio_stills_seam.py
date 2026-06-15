#!/usr/bin/env python3
"""
patch_audio_stills_seam.py -- fix the audio-gate->stills false-hang/false-stale (v1.0).

WHY (observed live on scripture_on_screen/esther--1)
  After the audio gate is accepted, orchestrate calls run_modea_leg (stills) but NOTHING
  writes a new phase -- the record stays "gate_audio" through the whole stills leg. Two
  consequences:
    1. the status line can't count stills (its stills branch needs phase running/gate_stills);
    2. WORSE: gate_audio is a stale-checked gate phase, and the heartbeat froze at the
       moment "keep" was clicked (A1 only pulses heartbeat inside await_gate's poll loop,
       not during a work leg) -- so after STALE_SECONDS build_state false-flagged a HEALTHY
       stills run as "stale" ("ended unexpectedly").

WHAT THIS DOES (2 files)
  orchestrate.py:
    - before run_modea_leg, write set_phase("running") (gate_mode == job) -- the missing
      audio->stills seam write. Mirrors the existing assembling/done/stopped writes.
      The record leaves gate_audio -> status line counts, and it is no longer a gate phase.
  pipeline_server.py (build_state, A1 stale check):
    - belt-and-braces: only stale-flag a gate phase if its gate is STILL waiting. A
      "decided" gate means the run moved on, so it must never be called stale for sitting
      there. This alone would have prevented the observed false-stale.
    - APP_VERSION -> v1.0.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `audio->stills seam`). Anchors verified once across
  both files; per-file .pre_seam backups; py_compile both; full rollback on any failure.
  Requires v0.9.
"""
import sys
import shutil
import py_compile
from pathlib import Path

ORCH = Path("shared/orchestrate.py")
PS   = Path("shared/mission_control/pipeline_server.py")
MARKER = "audio->stills seam"

# --- orchestrate: set_phase("running") before run_modea_leg ------------------
ORCH_OLD = '''    if "modeA" in legs:
        if proj_dir is None:
            t.halt("cannot run Mode A leg — channel/project unresolved (need channel.json + --project).")
            sys.exit(1)
        ma = modea_leg.run_modea_leg(ctx)'''
ORCH_NEW = '''    if "modeA" in legs:
        if proj_dir is None:
            t.halt("cannot run Mode A leg — channel/project unresolved (need channel.json + --project).")
            sys.exit(1)
        if ctx["gate_mode"] == "job":
            set_phase(_job_id, "running", ctx["repo_root"])  # audio->stills seam: leave gate_audio so the strip counts + no false-stale
        ma = modea_leg.run_modea_leg(ctx)'''

# --- build_state: only stale-flag a gate that is still waiting ----------------
PS_OLD = '''    if phase in ("gate_audio", "gate_stills"):
        hb = rec.get("heartbeat")
        if hb and (time.time() - float(hb)) > STALE_SECONDS:
            phase = "stale"'''
PS_NEW = '''    if phase in ("gate_audio", "gate_stills") and ((rec.get("gate") or {}).get("status") == "waiting"):
        hb = rec.get("heartbeat")
        if hb and (time.time() - float(hb)) > STALE_SECONDS:
            phase = "stale"'''

PS_OLD_VER = '''APP_VERSION = "v0.9"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
PS_NEW_VER = '''APP_VERSION = "v1.0"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    for p, n in [(ORCH, "orchestrate"), (PS, "pipeline_server")]:
        if not p.exists():
            die(f"{p} not found ({n}) -- run from the repo root on the laptop.")

    orch, ps = ORCH.read_text(), PS.read_text()

    if MARKER in orch:
        print(f"Already patched ({MARKER!r} present in orchestrate) -- no changes.")
        return
    if PS_OLD_VER not in ps:
        die("APP_VERSION v0.9 anchor not found -- apply the v0.9 patches first. Nothing written.")

    edits = [
        (ORCH, orch, "orchestrate seam", ORCH_OLD, ORCH_NEW),
        (PS,   ps,   "stale guard",      PS_OLD,    PS_NEW),
        (PS,   ps,   "version bump",     PS_OLD_VER, PS_NEW_VER),
    ]
    for p, src, label, old, _ in edits:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND in {p.name} -- nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x in {p.name} (expected 1) -- nothing written.")

    new_orch = orch.replace(ORCH_OLD, ORCH_NEW)
    new_ps = ps.replace(PS_OLD, PS_NEW).replace(PS_OLD_VER, PS_NEW_VER)

    backups = []
    try:
        for p, content in [(ORCH, new_orch), (PS, new_ps)]:
            b = p.with_suffix(p.suffix + ".pre_seam")
            shutil.copy2(p, b)
            backups.append((p, b))
            p.write_text(content)
        if 'set_phase(_job_id, "running"' not in ORCH.read_text():
            raise RuntimeError("seam set_phase missing post-write")
        if 'status") == "waiting"' not in PS.read_text():
            raise RuntimeError("stale guard missing post-write")
        if 'APP_VERSION = "v1.0"' not in PS.read_text():
            raise RuntimeError("version bump missing post-write")
        for p in (ORCH, PS):
            py_compile.compile(str(p), doraise=True)
    except Exception as e:
        for p, b in backups:
            shutil.copy2(b, p)
        die(f"post-write check failed -- ALL files restored.\n{e}")

    print("OK patched 2 files:")
    print(f"   {ORCH}  (.pre_seam)  -- set_phase('running') before run_modea_leg")
    print(f"   {PS}  (.pre_seam)  -- decided-gate stale guard + APP_VERSION v1.0")
    print()
    print("AFTER pull on the box: restart, verify v1.0, node-check:")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   curl -s \"http://127.0.0.1:8002/api/state?key=fh2026\" | python3 -c \"import sys,json;d=json.load(sys.stdin);print(d.get('version'),d.get('sha'))\"")
    print("   git rev-parse --short HEAD   # must match; version must read v1.0")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")
    print()
    print("   THEN next from-scratch run: after accepting the audio gate, the strip should")
    print("   read 'running' + count stills (not freeze at gate_audio), and never false-stale.")


if __name__ == "__main__":
    main()
