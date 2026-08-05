#!/usr/bin/env python3
"""patch_kling_cache_guard.py -- kling raws are cache, not receipts.

Pass B called _animate unconditionally on kling beats: a NULLed clip_path
re-bought a clip whose raw already sat in work/, and a crash between
_animate and mark() re-bought on resume. Guard: raw present and plausibly
whole (>100KB) -> fit-only at $0. Makes the idempotent-resume doctrine true
for the most expensive call in the pipeline, and makes surgical re-renders
(the color-law heal) genuinely free.

Idempotent. Usage: python3 patch_kling_cache_guard.py [repo_root] (default .)
"""
import py_compile, shutil, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
VIS = ROOT / "shared/v2/visuals.py"
MARK = "kling raw cached"

E1_OLD = '''        if b["method"] == "kling":
            raw = work / f"{tag}_kling.mp4"
            got, refused = _animate(Path(b["still_path"]),
                                    b["motion_prompt"] or "", raw, proj)
            if refused:'''
E1_NEW = '''        if b["method"] == "kling":
            raw = work / f"{tag}_kling.mp4"
            cached = raw.exists() and raw.stat().st_size > 100000
            if cached:
                print(f"   {tag}: kling raw cached -- fit only, $0")
                got, refused = raw, False
            else:
                got, refused = _animate(Path(b["still_path"]),
                                        b["motion_prompt"] or "", raw, proj)
            if refused:'''

E2_OLD = '''                label = _fit_to_duration(raw, dur, out, W, H, work, tag,
                                         move=b["move"] or "",
                                         speckles=spk, spk_strength=spk_strength)
                cost = KLING_COST'''
E2_NEW = '''                label = _fit_to_duration(raw, dur, out, W, H, work, tag,
                                         move=b["move"] or "",
                                         speckles=spk, spk_strength=spk_strength)
                cost = 0.0 if cached else KLING_COST'''


def main():
    if not VIS.exists():
        sys.exit("ABORT: %s not found -- run from repo root" % VIS)
    src = VIS.read_text()
    if MARK in src:
        print("already patched -- nothing to do")
        return
    for name, a in (("E1", E1_OLD), ("E2", E2_OLD)):
        if src.count(a) != 1:
            sys.exit("ABORT: anchor %s matches %d times (need 1) -- file has "
                     "drifted; re-read before patching" % (name, src.count(a)))
    out = src.replace(E1_OLD, E1_NEW).replace(E2_OLD, E2_NEW)
    bak = VIS.with_name(VIS.name + ".pre_kling_cache")
    shutil.copy2(VIS, bak)
    tmp = VIS.with_name(VIS.name + ".tmp_kling_cache")
    tmp.write_text(out)
    py_compile.compile(str(tmp), doraise=True)
    tmp.replace(VIS)
    print("patched %s (backup %s)" % (VIS, bak.name))


if __name__ == "__main__":
    main()
