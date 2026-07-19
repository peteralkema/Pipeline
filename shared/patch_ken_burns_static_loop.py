#!/usr/bin/env python3
"""
patch_ken_burns_static_loop.py -- fix ken_burns_still static branch emitting 1 frame.

The static path (scale+pad+fps, no zoompan) decodes the single PNG once and stops at
1 frame (0.041667s) -- every `static` beat collapsed. Fix: add `-loop 1` to the
ffmpeg INPUT inside ken_burns_still so the still is held for the full -t. Harmless to
the moving path (zoompan still owns the frame count).

SCOPED to the ken_burns_still function span only -- the engine has an unrelated
`-loop 1` ffmpeg elsewhere, so a global check would false-positive. Idempotent
(checks within the function), .pre_<ts> backup, py_compile, ASCII.
Run where recreation_pipeline.py is.
"""
import sys, time
from pathlib import Path

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("recreation_pipeline.py")
START = "def ken_burns_still("
NEXT = "\ndef _is_content_policy_error("
OLD = '        "ffmpeg", "-y", "-i", str(still_path),\n'
NEW = '        "ffmpeg", "-y", "-loop", "1", "-i", str(still_path),\n'


def die(m):
    print("PATCH ABORTED: " + m); raise SystemExit(1)


def main():
    if not TARGET.exists():
        die("recreation_pipeline.py not found.")
    src = TARGET.read_text()
    if START not in src:
        die("ken_burns_still not found.")
    s = src.index(START)
    e = src.find(NEXT, s)
    if e == -1:
        die("could not bound ken_burns_still (missing _is_content_policy_error).")
    span = src[s:e]
    if '"-loop"' in span:
        print("Already applied (ken_burns_still has -loop). No change."); return
    if span.count(OLD) != 1:
        die("ffmpeg-input anchor found %d times inside ken_burns_still, expected 1." % span.count(OLD))
    new_span = span.replace(OLD, NEW, 1)
    new = src[:s] + new_span + src[e:]
    try:
        compile(new, str(TARGET), "exec")
    except SyntaxError as ex:
        die("compile failed: %s" % ex)
    ts = time.strftime("%Y%m%d-%H%M%S")
    TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts).write_text(src)
    TARGET.write_text(new)
    print("Patched recreation_pipeline.py")
    print("  backup: %s.pre_%s" % (TARGET.name, ts))
    print("  ken_burns_still input now -loop 1 (static holds 5s / 120 frames)")


if __name__ == "__main__":
    main()
