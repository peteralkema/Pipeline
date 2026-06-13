#!/usr/bin/env python3
"""
patch_a2_stop_gate.py — make the stills-gate STOP actually stop.

WHY
  modea_gate captured the gate decision, printed it, then `return True` no matter
  what — and run_modea_leg didn't even capture the return. So "skip"/Stop walked
  straight into the Kling animate step (clip spend) exactly like "go". And
  orchestrate ran convergence unconditionally after the Mode A leg, so there was
  no clean "ended at the gate, don't assemble" path.

WHAT THIS DOES (one coupled change, two files, all-or-nothing)
  shared/modea_leg.py
    1. modea_gate dry-run early-return: True  -> "go"   (proceed semantics)
    2. modea_gate final return:        True  -> decision
    3. run_modea_leg: capture the decision; on "skip" leave stills on disk and
       return {"stopped": True, ...} WITHOUT animating (no clip spend).
  shared/orchestrate.py
    4. after the Mode A leg: if the leg returned {"stopped": True}, set phase
       "stopped" (job mode), print a clean message, exit 0 — convergence never runs.

  Result: Stop ends the run cleanly with stills preserved. Re-launch later and
  (with the skip-existing stills guard) it skips the rendered stills for free and
  resumes from the missing ones. No state store.

NOT IN SCOPE
  The browser Stop BUTTON (its human label + making it send "skip") and the
  A4 gate-decision-write fix are page-layer changes in pipeline_server.py — a
  separate patch. This patch makes the BACKEND honour "skip" from any source
  (CLI prompt today; the page button once A4 lands).

DISCIPLINE
  Idempotent. Verifies every anchor exists exactly once across BOTH files before
  writing anything; refuses to half-apply; backs each file up to a .pre_a2stop
  sidecar; re-compiles both and rolls BOTH back on any failure. Unique marker
  comments (not substrings of any other line) so a re-run is a clean no-op.
  Run from the repo root on the LAPTOP, then commit/push, then pull on the box.
"""
import sys
import shutil
import py_compile
from pathlib import Path

MODEA = Path("shared/modea_leg.py")
ORCH = Path("shared/orchestrate.py")

MARK_MODEA = "A2 Stop: keep stills on disk"
MARK_ORCH = "A2 Stop at the stills gate"

# ── modea_leg.py edits ───────────────────────────────────────────────────────

M1_OLD = '''    if ctx["dry_run"]:
        t.info("[dry-run] Mode A gate would wait for stills review here.")
        return True
'''
M1_NEW = '''    if ctx["dry_run"]:
        t.info("[dry-run] Mode A gate would wait for stills review here.")
        return "go"
'''

M2_OLD = '''    t.ok(f"Mode A gate cleared ({decision}).")
    return True
'''
M2_NEW = '''    t.ok(f"Mode A gate cleared ({decision}).")
    return decision
'''

M3_OLD = '''    # Phase 2: the aesthetic firewall
    modea_gate(ctx, engine_project, engine_cwd, stills_count)

    # Phase 3: animate-only
    clips = _animate(ctx, engine_project, engine_cwd)
'''
M3_NEW = '''    # Phase 2: the aesthetic firewall
    decision = modea_gate(ctx, engine_project, engine_cwd, stills_count)
    if decision == "skip":  # A2 Stop: keep stills on disk, end run without clips/convergence
        t.info("stills gate STOP — stills are on disk; ending without clips or convergence. "
               "Re-launch later to resume (existing stills are skipped).")
        return {"stopped": True, "engine_project": engine_project,
                "engine_cwd": engine_cwd, "index_json": index_json}

    # Phase 3: animate-only
    clips = _animate(ctx, engine_project, engine_cwd)
'''

# ── orchestrate.py edit ──────────────────────────────────────────────────────

O1_OLD = '''        ma = modea_leg.run_modea_leg(ctx)
        if ma is None:
            t.halt("Mode A leg halted. Fix the reported issue and re-run.")
            sys.exit(1)
    else:
        ma = None
'''
O1_NEW = '''        ma = modea_leg.run_modea_leg(ctx)
        if ma is None:
            t.halt("Mode A leg halted. Fix the reported issue and re-run.")
            sys.exit(1)
        if ma.get("stopped"):  # A2 Stop at the stills gate: end cleanly, no convergence
            t.info("Mode A gate STOP — stills are on disk; ending the run cleanly without "
                   "convergence. Re-launch later to resume (existing stills are skipped).")
            if ctx["gate_mode"] == "job":
                set_phase(_job_id, "stopped", ctx["repo_root"])
            t.ok("run stopped at stills gate — stills preserved.")
            sys.exit(0)
    else:
        ma = None
'''

PLAN = {
    MODEA: (MARK_MODEA, [(M1_OLD, M1_NEW), (M2_OLD, M2_NEW), (M3_OLD, M3_NEW)]),
    ORCH:  (MARK_ORCH,  [(O1_OLD, O1_NEW)]),
}


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    # 1. existence
    for path in PLAN:
        if not path.exists():
            die(f"{path} not found — run this from the repo root on the laptop.")

    srcs = {path: path.read_text() for path in PLAN}

    # 2. idempotency — both markers present = already applied; exactly one = partial (bad)
    present = [path for path, (mark, _) in PLAN.items() if mark in srcs[path]]
    if len(present) == len(PLAN):
        print("Already patched (both markers present) — no changes made.")
        return
    if present:
        die(f"partial prior application detected — {[str(p) for p in present]} already "
            f"carries its marker but the other file does not. Inspect manually; nothing written.")

    # 3. verify every anchor exists exactly once, in every file, BEFORE writing anything
    for path, (_, edits) in PLAN.items():
        for i, (old, _) in enumerate(edits, 1):
            n = srcs[path].count(old)
            if n == 0:
                die(f"{path}: anchor #{i} NOT FOUND — file shape changed; nothing written. "
                    f"(Suspect an out-of-sync box or a skipped predecessor.)")
            if n > 1:
                die(f"{path}: anchor #{i} found {n}x (expected 1) — ambiguous; nothing written.")

    # 4. build new contents in memory
    new_srcs = {}
    for path, (_, edits) in PLAN.items():
        s = srcs[path]
        for old, new in edits:
            s = s.replace(old, new)
        if s == srcs[path]:
            die(f"{path}: replace produced no change — nothing written.")
        new_srcs[path] = s

    # 5. back up both, then write both
    backups = {}
    for path in PLAN:
        bak = path.with_suffix(path.suffix + ".pre_a2stop")
        shutil.copy2(path, bak)
        backups[path] = bak
        path.write_text(new_srcs[path])

    # 6. verify markers landed + both files compile; roll BOTH back on any failure
    def rollback(reason):
        for path, bak in backups.items():
            shutil.copy2(bak, path)
        die(f"{reason} — restored BOTH files from backup.")

    for path, (mark, _) in PLAN.items():
        if mark not in path.read_text():
            rollback(f"{path}: marker missing after write")
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as e:
            rollback(f"{path}: result does not compile\n{e}")

    print("OK patched both files:")
    for path, bak in backups.items():
        print(f"   {path}   (backup: {bak.name})")
    print("Verify:")
    print("   grep -n 'A2 Stop' shared/modea_leg.py shared/orchestrate.py")
    print("   (expect 2 lines in modea_leg.py — the comment + nothing else — and 1 in orchestrate.py)")


if __name__ == "__main__":
    main()
