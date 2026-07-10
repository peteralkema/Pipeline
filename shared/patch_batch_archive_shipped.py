#!/usr/bin/env python3
"""
patch_batch_archive_shipped.py  --  #11n: auto-archive shipped pairs

Adds an archive step to run_batch.py so a successfully-shipped pair is moved
out of the inbox into <inbox>/_shipped/ the moment it ships. A re-run then
cannot re-render/re-upload it. Fires ONLY on ok=True; --plan never reaches it.
Idempotent: sentinel comment -> re-run no-op; anchor must match exactly once;
result is py_compiled BEFORE the target is touched; original backed up.
"""
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "run_batch.py"
SENTINEL = "[archive-on-ship] #11n"

ANCHOR = '''        _log(f"{'DONE' if ok else 'FAILED'} '{name}': {detail}")'''

BLOCK = """
        # [archive-on-ship] #11n: move the shipped pair out of the inbox so a
        # re-run cannot re-render/re-upload it. Only on ok=True; never in --plan
        # (plan continues earlier). Failed/skipped pairs stay put for a retry.
        if ok:
            try:
                _shipped = inbox / "_shipped"
                _shipped.mkdir(exist_ok=True)
                for _pf in (md, thumb):
                    if _pf.exists():
                        _pf.rename(_shipped / _pf.name)
                _log(f"  archived -> {_shipped}/ ({md.name} + {thumb.name})")
            except Exception as _e:
                _log(f"  archive skipped for '{name}': {type(_e).__name__}: {_e}")"""


def die(msg):
    sys.stderr.write("REFUSED: " + msg + "\n")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"target not found: {TARGET}")
    text = TARGET.read_text(encoding="utf-8")
    if SENTINEL in text:
        print("already applied (sentinel present) -- no-op")
        return
    n = text.count(ANCHOR)
    if n != 1:
        die(f"anchor matched {n} times (need exactly 1); file drifted -- wrote nothing")
    new = text.replace(ANCHOR, ANCHOR + BLOCK)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(new)
        tmp = tf.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        die(f"result does not compile -- wrote nothing:\n{e}")
    finally:
        Path(tmp).unlink(missing_ok=True)
    backup = TARGET.with_name(TARGET.name + ".pre_archive")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new, encoding="utf-8")
    print(f"OK: archive-on-ship added to {TARGET.name}  (backup: {backup.name})")


if __name__ == "__main__":
    main()
