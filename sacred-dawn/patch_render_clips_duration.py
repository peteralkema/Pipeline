#!/usr/bin/env python3
"""
patch_render_clips_duration.py -- add --duration to render_clips.py.

Lets the Ken Burns floor render each clip at a chosen length (the engine's
ken_burns_still already accepts duration). Default = SHOT_DURATION (5.0). Used for
the uniform stretch so 320 clips sum to the VO length. Idempotent, .pre_<ts> backup,
py_compile, ASCII. Run where render_clips.py is.
"""
import sys, time
from pathlib import Path

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("render_clips.py")
MARKER = "--duration"
A_OLD = '    ap.add_argument("--force", action="store_true", help="re-render clips already on disk")\n'
A_NEW = ('    ap.add_argument("--duration", type=float, default=None,\n'
         '                    help="seconds per clip (Ken Burns only); default SHOT_DURATION")\n'
         '    ap.add_argument("--force", action="store_true", help="re-render clips already on disk")\n')
D_OLD = '    rows = list(csv.DictReader(csv_path.open()))\n'
D_NEW = ('    dur = args.duration if args.duration else DURATION\n'
         '    rows = list(csv.DictReader(csv_path.open()))\n')
C_OLD = '            rp.ken_burns_still(still, dst, DURATION, move=arg)\n'
C_NEW = '            rp.ken_burns_still(still, dst, dur, move=arg)\n'


def die(m):
    print("PATCH ABORTED: " + m); raise SystemExit(1)


def main():
    if not TARGET.exists():
        die("render_clips.py not found.")
    src = TARGET.read_text()
    if MARKER in src:
        print("Already applied (--duration present). No change."); return
    for name, o in (("arg", A_OLD), ("dur", D_OLD), ("call", C_OLD)):
        if src.count(o) != 1:
            die("anchor '%s' found %d times, expected 1." % (name, src.count(o)))
    new = src.replace(A_OLD, A_NEW, 1).replace(D_OLD, D_NEW, 1).replace(C_OLD, C_NEW, 1)
    try:
        compile(new, str(TARGET), "exec")
    except SyntaxError as e:
        die("compile failed: %s" % e)
    ts = time.strftime("%Y%m%d-%H%M%S")
    TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts).write_text(src)
    TARGET.write_text(new)
    print("Patched render_clips.py")
    print("  backup: %s.pre_%s" % (TARGET.name, ts))
    print("  added --duration (Ken Burns per-clip seconds; default SHOT_DURATION)")


if __name__ == "__main__":
    main()
