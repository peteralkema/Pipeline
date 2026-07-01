#!/usr/bin/env python3
"""TRUE static: bypass zoompan entirely.

Root cause (frame-diff proved it): even with z=1, the zoompan filter runs on a
4x-upscaled input (scale W*4 x H*4) then windows out W x H. At z=1 the x/y
centering expressions ('iw/2-(iw/zoom/2)') still evaluate per-frame on the 4x
width -> sub-pixel micro-pan every frame = visible motion. z=1 does NOT make it
static because the upscale+zoompan viewport still drifts.

Fix: when _z == "1" (static), replace the whole upscale+zoompan vf with a plain
scale-to-frame + pad, no zoompan at all. A single held frame, zero motion. The
zoom path (cinematic channels) is untouched.

Idempotent + py_compile verified.
"""
import shutil, sys, py_compile, tempfile, os
from pathlib import Path

SRC = Path(__file__).resolve().parent / "recreation_pipeline.py"
if not SRC.exists():
    SRC = Path(__file__).resolve().parent.parent / "shared" / "recreation_pipeline.py"

OLD = '''    _z = "1"
    # Upscale to 4x the target first (smoothness), cover-crop to the 4x frame, then a
    # slow zoom-in (cap 1.25x) OR a static hold (z=1), output at channel aspect.
    up_w, up_h = W * 4, H * 4
    vf = (
        f"scale={up_w}:{up_h}:force_original_aspect_ratio=increase,"
        f"crop={up_w}:{up_h},"
        f"zoompan=z='{_z}':d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"s={W}x{H}:fps={fps},setsar=1"
    )'''

NEW = '''    _z = "1"
    if _z == "1":
        # TRUE STATIC (01 Jul): zoompan micro-pans even at z=1 (the x/y viewport
        # math drifts per-frame on the 4x-upscaled input). Bypass zoompan
        # entirely -- scale-to-fit + pad to the frame, a single held image, ZERO
        # motion. Proven via frame-diff (frame0 == frame100).
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,fps={fps}"
        )
    else:
        # Cinematic slow zoom-in (unchanged): upscale 4x for smoothness, then zoompan.
        up_w, up_h = W * 4, H * 4
        vf = (
            f"scale={up_w}:{up_h}:force_original_aspect_ratio=increase,"
            f"crop={up_w}:{up_h},"
            f"zoompan=z='{_z}':d={total_frames}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"s={W}x{H}:fps={fps},setsar=1"
        )'''

def main() -> int:
    if not SRC.exists():
        print(f"ERROR: {SRC} not found."); return 1
    t = SRC.read_text()
    if 'if _z == "1":' in t and 'TRUE STATIC (01 Jul)' in t:
        print("Already patched (zoompan bypassed for static). No-op."); return 0
    if OLD not in t:
        print("ERROR: hardcoded-z vf block not found verbatim -- drifted. Aborting."); return 1
    new = t.replace(OLD, NEW, 1)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(new); tmp = f.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: would not compile: {e}. Aborting."); os.unlink(tmp); return 1
    os.unlink(tmp)
    shutil.copy2(SRC, SRC.with_suffix(".py.bak_no_zoompan"))
    SRC.write_text(new)
    print("OK static path now bypasses zoompan (scale+pad, zero motion).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
