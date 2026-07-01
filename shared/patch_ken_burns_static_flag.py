#!/usr/bin/env python3
"""Add a per-channel ken_burns flag; when false, ken_burns_still produces a
STATIC held clip (zoompan z=1, no zoom) instead of the slow zoom-in.

This is the clean "zero-zoom Ken-Burns = true static" fix (banked 01 Jul). QQrew
is true-static doctrine (§9): no Kling, no Ken-Burns. Rather than a separate
reassemble_static.py detour or an outside-the-pipeline ffmpeg strip, we set the
zoom to a constant so the SAME ken_burns_still function writes a motionless
clips/shot_NNN.mp4 -- assembly is unchanged.

Two edits:
1. qqrew/channel.json: add "ken_burns": false.
2. recreation_pipeline.py ken_burns_still(): read the flag via
   load_channel_config(strict=False) (same pattern as _channel_aspect, line 226,
   walks up from CWD, cached). When false, build the zoompan with z=1.

Every other channel omits the flag -> defaults True -> unchanged.
Idempotent + py_compile verified. Backs up both files.
"""
import json, shutil, sys, py_compile, tempfile, os
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "recreation_pipeline.py"
if not SRC.exists():
    SRC = BASE.parent / "shared" / "recreation_pipeline.py"
CH = BASE.parent / "qqrew" / "channel.json"

OLD_CODE = '''    W, H = ASPECT["width"], ASPECT["height"]
    # Upscale to 4x the target first (smoothness), cover-crop to the 4x frame, then a
    # slow zoom-in (cap 1.25x), output at channel aspect.
    up_w, up_h = W * 4, H * 4
    vf = (
        f"scale={up_w}:{up_h}:force_original_aspect_ratio=increase,"
        f"crop={up_w}:{up_h},"
        f"zoompan=z='min(zoom+0.0024,1.50)':d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"s={W}x{H}:fps={fps},setsar=1"
    )'''

NEW_CODE = '''    W, H = ASPECT["width"], ASPECT["height"]
    # Per-channel ken_burns flag (banked 01 Jul): true-static channels (QQrew)
    # set "ken_burns": false -> zoompan z=1 (constant, no zoom) = a motionless
    # held frame, same clips/shot_NNN.mp4 artifact, assembly unchanged. Reads the
    # same way _channel_aspect does (walks up from CWD, cached). Defaults True so
    # every cinematic channel keeps the slow zoom-in.
    try:
        _kb = load_channel_config(strict=False).get("ken_burns", True)
    except Exception:
        _kb = True
    _z = "min(zoom+0.0024,1.50)" if _kb else "1"
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


def patch_code() -> bool:
    if not SRC.exists():
        print(f"ERROR: {SRC} not found."); return False
    t = SRC.read_text()
    if 'get("ken_burns", True)' in t:
        print("Code already patched (ken_burns flag). No-op."); return True
    if OLD_CODE not in t:
        print("ERROR: ken_burns_still vf block not found verbatim -- drifted. Aborting."); return False
    new = t.replace(OLD_CODE, NEW_CODE, 1)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(new); tmp = f.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: would not compile: {e}. Aborting."); os.unlink(tmp); return False
    os.unlink(tmp)
    shutil.copy2(SRC, SRC.with_suffix(".py.bak_kenburns_flag"))
    SRC.write_text(new)
    print("OK code: ken_burns_still reads ken_burns flag (z=1 when false).")
    return True


def patch_channel() -> bool:
    if not CH.exists():
        print(f"ERROR: {CH} not found."); return False
    cfg = json.loads(CH.read_text())
    if cfg.get("ken_burns") is False:
        print("channel.json already ken_burns:false. No-op."); return True
    cfg["ken_burns"] = False
    shutil.copy2(CH, CH.with_suffix(".json.bak_kenburns"))
    CH.write_text(json.dumps(cfg, indent=2) + "\n")
    json.loads(CH.read_text())
    print("OK channel.json: ken_burns=false (true-static).")
    return True


def main() -> int:
    ok_c = patch_code()
    ok_j = patch_channel()
    return 0 if (ok_c and ok_j) else 1


if __name__ == "__main__":
    sys.exit(main())
