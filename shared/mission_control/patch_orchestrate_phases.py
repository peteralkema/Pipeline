#!/usr/bin/env python3
"""
patch_orchestrate_phases.py — write the terminal phases into the job record.

The two gates already flip phase (gate_audio, gate_stills via await_gate's
phase= arg). But the NON-gate phases have no writer: after stills are approved
the run animates + assembles + finishes, and the page never learns. Result:
page stuck on gate_stills forever, never returns to idle.

This patch adds set_phase writes at the leg seams in orchestrate.py:
  - "animating"  — right after the Mode A leg returns (stills approved, Kling ran)
  - "assembling" — at the convergence seam
  - "done"       — just before "run complete"

All writes are job-mode-only (guarded by ctx["gate_mode"] == "job"), so CLI
runs are completely unaffected (set_phase is a no-op without a job record).

Three edits to orchestrate.py:
  1. extend the gate_protocol import to include set_phase
  2. set "assembling" before the convergence leg + "animating" after Mode A
  3. set "done" before the final "run complete" ok

Idempotent (markers), backs up to .pre_phases.

Run on the box:
  python shared/mission_control/patch_orchestrate_phases.py --check
  python shared/mission_control/patch_orchestrate_phases.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "orchestrate.py"

EDITS = []

# --- 1. import set_phase alongside init_job ---
EDITS.append(dict(
    marker="from gate_protocol import init_job, set_phase",
    old="        from gate_protocol import init_job",
    new="        from gate_protocol import init_job, set_phase",
))

# --- 2. animating (after Mode A leg) + assembling (before convergence) ---
# Anchor: the Mode A success block + the convergence seam.
EDITS.append(dict(
    marker='set_phase(_job_id, "assembling"',
    old='''        ma = modea_leg.run_modea_leg(ctx)
        if ma is None:
            t.halt("Mode A leg halted. Fix the reported issue and re-run.")
            sys.exit(1)
    else:
        ma = None

    # ── 3d: CONVERGENCE LEG (pool clips → assemble → final_video) — convergence_leg.py ──
    if "convergence" in legs:
        cv = convergence_leg.run_convergence_leg(ctx, ma)''',
    new='''        ma = modea_leg.run_modea_leg(ctx)
        if ma is None:
            t.halt("Mode A leg halted. Fix the reported issue and re-run.")
            sys.exit(1)
    else:
        ma = None

    # ── 3d: CONVERGENCE LEG (pool clips → assemble → final_video) — convergence_leg.py ──
    if "convergence" in legs:
        if ctx["gate_mode"] == "job":
            set_phase(_job_id, "assembling", ctx["repo_root"])
        cv = convergence_leg.run_convergence_leg(ctx, ma)''',
))

# --- 3. done (before run complete) ---
EDITS.append(dict(
    marker='set_phase(_job_id, "done"',
    old='''    if "audio" in legs and not dry:
        t.ok("audio leg complete — voiceover + real per-beat durations produced.")
    t.ok("run complete. ✦")''',
    new='''    if "audio" in legs and not dry:
        t.ok("audio leg complete — voiceover + real per-beat durations produced.")
    if ctx["gate_mode"] == "job":
        set_phase(_job_id, "done", ctx["repo_root"])
    t.ok("run complete. ✦")''',
))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if not T.is_file():
        sys.exit(f"missing: {T}")
    text = T.read_text()

    plans, fatal = [], []
    for i, e in enumerate(EDITS, 1):
        if e["marker"] in text:
            plans.append((i, "skip-applied")); continue
        n = text.count(e["old"])
        if n == 1: plans.append((i, "apply"))
        elif n == 0: fatal.append(f"edit {i}: ANCHOR NOT FOUND")
        else: fatal.append(f"edit {i}: anchor x{n}")

    print("=== ORCHESTRATE PHASES PATCH PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_phases")
    if not bak.exists():
        bak.write_text(text); print(f"  backup -> {bak.name}")
    for i, e in enumerate(EDITS, 1):
        if i not in to_apply: continue
        text = T.read_text()
        if text.count(e["old"]) != 1:
            print(f"  !! edit {i}: anchor changed — ABORT"); sys.exit(2)
        T.write_text(text.replace(e["old"], e["new"], 1))
        print(f"  applied -> edit {i}")
    print("\n=== DONE === restart not needed (orchestrate is spawned fresh per run)")


if __name__ == "__main__":
    main()
