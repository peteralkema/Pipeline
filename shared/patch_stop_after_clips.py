#!/usr/bin/env python3
"""
patch_stop_after_clips.py — add a stop-after-Mode-A-clips exit to orchestrate.py.

WHY: MC launches orchestrate with all legs [audio, (modeB), modeA, convergence].
convergence is appended unconditionally (decide_legs), so every render auto-
assembles final_video.mp4. Floor-first + the assemble/upload discipline need the
run to STOP after clips render, leaving an assemble-READY project that the
operator assembles on the MC Re-assemble button (the aligned assemble_episode.py).

The pipeline already has the exact machinery one leg earlier: the stills gate
STOP (ma.get("stopped") -> sys.exit(0), no convergence). This mirrors it one leg
later: when --stop-after-clips is set, exit cleanly after the Mode A leg returns
its clips, before the convergence block.

Idempotent (sentinel: STOP_AFTER_CLIPS_APPLIED). Two anchors, each verified to
match exactly once; edits applied in memory; py_compile before the target is
touched; original backed up to orchestrate.py.pre_stopafterclips. Pure ASCII.
"""
import sys, py_compile, tempfile, shutil
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "orchestrate.py"
BACKUP = TARGET.with_suffix(".py.pre_stopafterclips")
SENTINEL = "STOP_AFTER_CLIPS_APPLIED"

# --- Anchor 1: the argparse block. Add the flag next to --unattended. ---
ANCHOR_ARG = '''    ap.add_argument("--unattended", action="store_true",
                    help="fully unattended: forces gate-mode=auto + live + normal "
                         "verbosity, so no gate or kickoff prompt ever blocks (batch runs)")'''

NEW_ARG = ANCHOR_ARG + '''
    ap.add_argument("--stop-after-clips", action="store_true",
                    help="STOP_AFTER_CLIPS_APPLIED: render Mode A clips then exit "
                         "cleanly WITHOUT convergence (no assemble). Leaves an "
                         "assemble-ready project; MC assembles on the Re-assemble "
                         "button. The floor-first / manual-cut entry point.")'''

# --- Anchor 2: the post-Mode-A block, just before convergence. Insert the exit. ---
# Anchor on the convergence-leg header comment + guard; insert the stop above it.
ANCHOR_CONV = '''    # ── 3d: CONVERGENCE LEG (pool clips → assemble → final_video) — convergence_leg.py ──
    if "convergence" in legs:'''

NEW_CONV = '''    # ── 3c-stop: STOP_AFTER_CLIPS_APPLIED — end after clips, no convergence ──
    # Mirrors the stills-gate STOP one leg later. When set, the Mode A clips are
    # on disk and the project is assemble-ready; end cleanly so the operator
    # floors/crafts and assembles on the MC Re-assemble button (aligned
    # assemble_episode.py). ma is the Mode A result (None only if modeA didn't run).
    if getattr(args, "stop_after_clips", False) and ma is not None:
        t.info("stop-after-clips — clips are on disk; ending the run cleanly "
               "without convergence. Assemble on the MC Re-assemble button.")
        if ctx["gate_mode"] == "job":
            set_phase(_job_id, "clips_ready", ctx["repo_root"])
        t.ok("run stopped after clips — assemble-ready, nothing assembled.")
        sys.exit(0)

    # ── 3d: CONVERGENCE LEG (pool clips → assemble → final_video) — convergence_leg.py ──
    if "convergence" in legs:'''


def die(msg):
    print(f"FAIL: {msg}  Nothing written.", file=sys.stderr)
    sys.exit(1)


def main():
    if not TARGET.is_file():
        die(f"target not found: {TARGET}")
    src = TARGET.read_text()

    if SENTINEL in src:
        print("Already applied (sentinel present). No-op.")
        return

    for label, anchor in (("argparse", ANCHOR_ARG), ("convergence", ANCHOR_CONV)):
        n = src.count(anchor)
        if n != 1:
            die(f"anchor '{label}' matched {n} times (need exactly 1) — orchestrate.py drifted.")

    new = src.replace(ANCHOR_ARG, NEW_ARG, 1).replace(ANCHOR_CONV, NEW_CONV, 1)

    if new.count(SENTINEL) < 2:
        die("post-edit sentinel check failed (expected the flag help + the stop block).")

    # py_compile the RESULT before touching the target.
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
        tf.write(new); tmp = tf.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        die(f"py_compile failed on the patched result: {e}")
    finally:
        Path(tmp).unlink(missing_ok=True)

    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(new)
    print(f"OK — patched {TARGET.name}")
    print(f"     backup: {BACKUP.name}")
    print("     added --stop-after-clips + pre-convergence exit.")
    print("Verify:  grep -n 'STOP_AFTER_CLIPS_APPLIED' shared/orchestrate.py")


if __name__ == "__main__":
    main()
