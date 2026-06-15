#!/usr/bin/env python3
"""
patch_active_job_freshest.py -- active_job_id prefers the newest LIVE run (Hardening A, v1.6).

WHY (today's stranded-run confusion)
  active_job_id() did:
      jobs = sorted(glob("*.json"), key=mtime, reverse=True); return jobs[0].stem
  i.e. it returned the most-recently-TOUCHED record regardless of phase. With several
  records for one project (a closed-laptop orphan + duplicate Launch clicks), it picked a
  `done` ghost instead of the live `running` job -> the page showed a stuck/wrong state
  while the real run worked underneath, and recovery needed an SSH session.

  Two faults: (1) no preference for a non-terminal (live) run over a terminal (done/stopped/
  error/stale) one; (2) mtime is unreliable -- touching a `done` record re-floats it above
  the live run.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  Rewrite active_job_id to:
    - read each record, sort by started_at (content, not file mtime) descending;
    - return the newest record whose phase is NON-TERMINAL (the live run);
    - if none are live, return the newest record overall (so a just-finished run still
      shows its done panel).
  This makes the page lock onto the live run no matter how many done ghosts litter
  .mc_jobs/, and is the keystone of "close/refresh/restart -> always correct state."
  (It also subsumes part of C: a done/dead record is no longer chosen while a live one exists.)
  APP_VERSION -> v1.6.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `freshest live run`). Anchor verified once;
  .pre_freshest backup; py_compile; rollback on failure. Requires v1.5.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "freshest live run"

OLD = '''def active_job_id() -> str | None:
    jobs = sorted(jobs_dir(_REPO).glob("*.json"),
                  key=lambda p: p.stat().st_mtime, reverse=True)
    return jobs[0].stem if jobs else None'''

NEW = '''# Phases that mean the run is over (terminal). Everything else is a live run.
_TERMINAL_PHASES = ("done", "stopped", "error", "stale")

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
    return recs[0][2]            # none live -> newest overall (shows its done panel)'''

OLD_VER = '''APP_VERSION = "v1.5"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
NEW_VER = '''APP_VERSION = "v1.6"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


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
        die("APP_VERSION v1.5 anchor not found -- apply patch_panel_poll_persist.py (v1.5) first. Nothing written.")

    for label, old in [("active_job_id", OLD), ("version", OLD_VER)]:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND -- file shape changed; nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) -- ambiguous; nothing written.")

    new = src.replace(OLD, NEW).replace(OLD_VER, NEW_VER)

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_freshest")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    if MARKER not in chk or 'APP_VERSION = "v1.6"' not in chk or "_TERMINAL_PHASES" not in chk:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed -- restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile -- restored.\n{e}")

    print(f"OK patched {TARGET}  (backup {backup.name})")
    print("   active_job_id now returns the freshest LIVE run (by started_at), not the")
    print("   most-recently-touched file -> page rejoins the correct run after close/refresh.")
    print()
    print("AFTER pull on the box:")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   verify v1.6 + that the live 70smusic run shows correctly:")
    print("   curl -s \"http://127.0.0.1:8002/api/state?key=fh2026\" | python3 -c \"import sys,json;d=json.load(sys.stdin);print(d.get('phase'),d.get('job_id'),d.get('status_detail'))\"")
    print("   -> should report the RUNNING 70smusic job (...8201), not a done ghost.")
    print("   (the .mc_jobs/_stale/ records you moved are now irrelevant; even un-moved, done")
    print("    ghosts would be ignored while a live run exists.)")


if __name__ == "__main__":
    main()
