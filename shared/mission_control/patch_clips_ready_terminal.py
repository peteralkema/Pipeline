#!/usr/bin/env python3
"""
patch_clips_ready_terminal.py — make clips_ready a recognized terminal phase.

WHY: orchestrate's --stop-after-clips exit writes phase "clips_ready" then exits 0
(a CLEAN stop). But _TERMINAL_PHASES did not include it, so the pid-liveness reaper
(build_state) saw "non-terminal phase + dead pid" and relabeled the successful stop
as "dead" — a false crash indicator. With floor-first, clips_ready is the NORMAL end
state of every render, so it must read as success.

Idempotent (sentinel: CLIPS_READY_TERMINAL_APPLIED). One anchor, verified once;
py_compile before write; backup to pipeline_server.py.pre_clipsreadyterminal. Pure ASCII.
"""
import sys, py_compile, tempfile, shutil
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_clipsreadyterminal")
SENTINEL = "CLIPS_READY_TERMINAL_APPLIED"

ANCHOR = '_TERMINAL_PHASES = ("done", "stopped", "error", "stale", "dead")'
NEW = ('_TERMINAL_PHASES = ("done", "stopped", "error", "stale", "dead", "clips_ready")'
       '  # CLIPS_READY_TERMINAL_APPLIED: --stop-after-clips clean stop, not a crash')


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
    n = src.count(ANCHOR)
    if n != 1:
        die(f"anchor matched {n} times (need exactly 1) — pipeline_server.py drifted.")
    new = src.replace(ANCHOR, NEW, 1)
    if SENTINEL not in new or '"clips_ready"' not in new:
        die("post-edit check failed.")
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
        tf.write(new); tmp = tf.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        die(f"py_compile failed: {e}")
    finally:
        Path(tmp).unlink(missing_ok=True)
    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(new)
    print(f"OK — patched {TARGET.name}  (clips_ready now terminal)")
    print(f"     backup: {BACKUP.name}")


if __name__ == "__main__":
    main()
