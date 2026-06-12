"""
Mission Control — Phase 1 proof tool: poke a gate decision into a job record.

This is the stand-in for the future web API. It writes a decision into the job
record on disk; a job blocked in `await_gate(... gate_mode="job")` reads it and
continues. Proves inverted control with NO http, NO UI.

Usage (from a SECOND terminal while a job is waiting at a gate):
  python shared/mission_control/poke_gate.py --list
  python shared/mission_control/poke_gate.py --job <job_id> --show
  python shared/mission_control/poke_gate.py --job <job_id> --decide keep
  python shared/mission_control/poke_gate.py --job <job_id> --decide go
"""

from __future__ import annotations
import argparse
import json
import time
from pathlib import Path

from gate_protocol import jobs_dir, job_path, read_job, write_job


def _list():
    d = jobs_dir()
    jobs = sorted(d.glob("*.json"))
    if not jobs:
        print("(no jobs in", d, ")")
        return
    for p in jobs:
        rec = json.load(open(p))
        gate = rec.get("gate") or {}
        gname = gate.get("name", "-")
        gstatus = gate.get("status", "-")
        print(f"  {rec.get('job_id'):<40} phase={rec.get('phase','-'):<14} "
              f"gate={gname}/{gstatus}")


def _show(job_id):
    rec = read_job(job_id)
    if not rec:
        print(f"no such job: {job_id}")
        return
    print(json.dumps(rec, indent=2, ensure_ascii=False))


def _decide(job_id, decision):
    rec = read_job(job_id)
    if not rec:
        print(f"no such job: {job_id}")
        return
    gate = rec.get("gate")
    if not gate:
        print(f"job {job_id} is not waiting at a gate (gate is null).")
        return
    if gate.get("status") == "decided":
        print(f"gate '{gate.get('name')}' already decided "
              f"({gate.get('decision')}).")
        return
    options = gate.get("options", [])
    if options and decision not in options:
        print(f"'{decision}' not a valid option for gate "
              f"'{gate.get('name')}'. options: {options}")
        return
    gate["decision"] = decision
    rec["gate"] = gate
    write_job(job_id, rec)
    print(f"poked job {job_id}: gate '{gate.get('name')}' <- '{decision}'. "
          f"the waiting job will pick it up within its poll interval.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--job", default=None)
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--decide", default=None)
    args = ap.parse_args()

    if args.list:
        _list(); return
    if args.job and args.show:
        _show(args.job); return
    if args.job and args.decide:
        _decide(args.job, args.decide); return
    ap.print_help()


if __name__ == "__main__":
    main()
