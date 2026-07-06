#!/usr/bin/env python3
"""
patch_launch_stopafterclips.py — MC always launches renders with --stop-after-clips.
Kills auto-assemble: every render makes clips then exits assemble-ready; operator
assembles on the MC Re-assemble button. Pairs with orchestrate.py --stop-after-clips.
Idempotent (sentinel: LAUNCH_STOPAFTERCLIPS_APPLIED); two anchors each verified once;
py_compile before write; backup to pipeline_server.py.pre_launchstopafterclips. Pure ASCII.
"""
import sys, py_compile, tempfile, shutil
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_launchstopafterclips")
SENTINEL = "LAUNCH_STOPAFTERCLIPS_APPLIED"

ANCHOR_ARGV = '''    if dry_run:
        cmd.append("--dry-run")
    else:
        cmd.append("--live")  # skip the interactive kickoff prompt'''

NEW_ARGV = '''    # LAUNCH_STOPAFTERCLIPS_APPLIED: every render stops after Mode A clips (no
    # convergence). Assemble is a deliberate press on the MC Re-assemble button.
    cmd.append("--stop-after-clips")
    if dry_run:
        cmd.append("--dry-run")
    else:
        cmd.append("--live")  # skip the interactive kickoff prompt'''

ANCHOR_VER = 'APP_VERSION = "v3.8"  # hand-bumped each shipped page change; pairs with the auto git SHA'
NEW_VER = 'APP_VERSION = "v3.9"  # hand-bumped each shipped page change; pairs with the auto git SHA'


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
    for label, anchor in (("argv", ANCHOR_ARGV), ("version", ANCHOR_VER)):
        n = src.count(anchor)
        if n != 1:
            die(f"anchor '{label}' matched {n} times (need exactly 1) — pipeline_server.py drifted.")
    new = src.replace(ANCHOR_ARGV, NEW_ARGV, 1).replace(ANCHOR_VER, NEW_VER, 1)
    if SENTINEL not in new or 'cmd.append("--stop-after-clips")' not in new:
        die("post-edit check failed (sentinel or flag append missing).")
    if 'APP_VERSION = "v3.9"' not in new:
        die("post-edit check failed (version not bumped).")
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
    print("     launch_job now always passes --stop-after-clips; APP_VERSION -> v3.9")


if __name__ == "__main__":
    main()
