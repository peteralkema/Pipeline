#!/usr/bin/env python3
"""Hardcode z=1 (no zoom) in ken_burns_still — the config-flag approach didn't
take at render time (load_channel_config is cached inside finish and the
ken_burns flag wasn't honored; frame-diff proved clips still zoomed). Rather than
chase the caching interaction, remove the zoom from the code path unconditionally.

QQrew is the only channel currently finishing through this box, and it's
true-static doctrine, so hardcoding z=1 is correct for the immediate need. (If a
cinematic channel later needs the zoom back, revert via the .bak or restore the
flag read once the cache issue is fixed.)

Replaces the flag-based _z with a literal "1". Idempotent + py_compile verified.
"""
import shutil, sys, py_compile, tempfile, os
from pathlib import Path

SRC = Path(__file__).resolve().parent / "recreation_pipeline.py"
if not SRC.exists():
    SRC = Path(__file__).resolve().parent.parent / "shared" / "recreation_pipeline.py"

# The flag-based block from the previous patch:
OLD = '''    try:
        _kb = load_channel_config(strict=False).get("ken_burns", True)
    except Exception:
        _kb = True
    _z = "min(zoom+0.0024,1.50)" if _kb else "1"'''

NEW = '''    # HARDCODED static (01 Jul): the ken_burns config flag did not take at render
    # time (load_channel_config cached inside finish), frame-diff proved clips
    # still zoomed. z=1 unconditionally removes the zoom. Revert via .bak if a
    # cinematic channel needs the slow zoom-in restored.
    _z = "1"'''

def main() -> int:
    if not SRC.exists():
        print(f"ERROR: {SRC} not found."); return 1
    t = SRC.read_text()
    if '_z = "1"\n' in t and 'HARDCODED static' in t:
        print("Already hardcoded static. No-op."); return 0
    if OLD not in t:
        print("ERROR: flag-based _z block not found verbatim -- drifted or prior patch missing. Aborting."); return 1
    new = t.replace(OLD, NEW, 1)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(new); tmp = f.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: would not compile: {e}. Aborting."); os.unlink(tmp); return 1
    os.unlink(tmp)
    shutil.copy2(SRC, SRC.with_suffix(".py.bak_hardcode_static"))
    SRC.write_text(new)
    print("OK ken_burns_still now hardcoded z=1 (no zoom, unconditional).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
