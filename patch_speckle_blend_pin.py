#!/usr/bin/env python3
"""patch_speckle_blend_pin.py -- pin [base] to rgb24 before the speckle blend.

Box-diagnosed (gospel-of-thomas shot_008, 5 Aug): with [spk] pinned rgb24 and
[base] left to negotiate from the Flux PNG's native pixel format, blend's
format negotiation lands one input in a channel-scrambled planar layout ->
hard magenta (+36R -13G +50B), independent of any color matrix. Plain
(no-speckle) path measures true, field content is neutral -- the blend
negotiation is the sole poison. Fix: pin [base] to rgb24 so both blend
inputs are the same packed format by declaration; the color-law suffix then
performs the one explicit rgb->yuv709 conversion at the graph tail.

Applies on top of patch_color_pipeline.py. Idempotent.
Usage: python3 patch_speckle_blend_pin.py [repo_root]   (default .)
"""
import py_compile, shutil, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
VIS = ROOT / "shared/v2/visuals.py"
MARK = "format=rgb24[base]"

E1_OLD = '''        fc = (f"[0:v]{vf}[base];"
              f"[1:v]crop={W}:{H}:x='mod(t*11,240)':y='mod(t*7,240)',"
              f"format=rgb24[spk];"'''
E1_NEW = '''        fc = (f"[0:v]{vf},format=rgb24[base];"
              f"[1:v]crop={W}:{H}:x='mod(t*11,240)':y='mod(t*7,240)',"
              f"format=rgb24[spk];"'''

E2_OLD = '''            fc = (f"[0:v]{zp}[base];"
                  f"[1:v]crop={W}:{H}:x='mod(t*11,240)':y='mod(t*7,240)',"
                  f"format=rgb24,fade=t=in:st=0:d=0.8[spk];"'''
E2_NEW = '''            fc = (f"[0:v]{zp},format=rgb24[base];"
                  f"[1:v]crop={W}:{H}:x='mod(t*11,240)':y='mod(t*7,240)',"
                  f"format=rgb24,fade=t=in:st=0:d=0.8[spk];"'''


def main():
    if not VIS.exists():
        sys.exit("ABORT: %s not found -- run from repo root" % VIS)
    src = VIS.read_text()
    if MARK in src:
        print("already patched -- nothing to do")
        return
    for name, a in (("E1", E1_OLD), ("E2", E2_OLD)):
        if src.count(a) != 1:
            sys.exit("ABORT: anchor %s matches %d times (need 1) -- apply "
                     "patch_color_pipeline.py first / re-read the file"
                     % (name, src.count(a)))
    out = src.replace(E1_OLD, E1_NEW).replace(E2_OLD, E2_NEW)
    bak = VIS.with_name(VIS.name + ".pre_blend_pin")
    shutil.copy2(VIS, bak)
    tmp = VIS.with_name(VIS.name + ".tmp_blend_pin")
    tmp.write_text(out)
    py_compile.compile(str(tmp), doraise=True)
    tmp.replace(VIS)
    print("patched %s (backup %s)" % (VIS, bak.name))


if __name__ == "__main__":
    main()
