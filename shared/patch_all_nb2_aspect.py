#!/usr/bin/env python3
"""Standardise QQrew on ALL-NB2 with correct 16:9.

Two coordinated changes:
1. channel.json: restore image_model:"nano_banana" so crew-absent text beats
   render through NB2 text-to-image (fal-ai/nano-banana), matching the NB2 /edit
   Skeptic beats. ONE model family across all 180 -> consistent look, no
   flux-vs-NB2 texture split.
2. recreation_pipeline.py generate_still(): the args dict hands EVERY model
   "image_size": ASPECT (a {width,height} dict). NB2 text-to-image IGNORES the
   dict and defaults to 1024x1024 square. Fix: send the size param per-model --
   NB2 (nano_banana / seedream) gets aspect_ratio:"16:9" (string, same as the
   /edit path); flux keeps the image_size dict (which it honors).

Result: all beats NB2, all 16:9.
Idempotent + py_compile verified. Backs up both files.
"""
import json, shutil, sys, py_compile, tempfile, os
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "recreation_pipeline.py"
if not SRC.exists():
    SRC = BASE.parent / "shared" / "recreation_pipeline.py"
CH = BASE.parent / "qqrew" / "channel.json"

# --- code change: per-model size param ---
OLD_CODE = '''    model = config.get("image_model", IMAGE_MODEL)
    endpoint = IMAGE_ENDPOINTS[model]
    args = {"prompt": full_prompt, "image_size": ASPECT}
    if negative:
        # Most fal image models accept negative_prompt; harmless if ignored.
        args["negative_prompt"] = negative
    if model == "flux":'''

NEW_CODE = '''    model = config.get("image_model", IMAGE_MODEL)
    endpoint = IMAGE_ENDPOINTS[model]
    # Size param differs by model: flux honors the image_size {w,h} dict; NB2
    # text-to-image (nano_banana) / seedream ignore the dict and default to
    # 1024x1024 square -- they need the aspect_ratio STRING (banked 01 Jul,
    # the all-NB2 standardisation). Match the /edit path's "16:9".
    if model == "flux":
        args = {"prompt": full_prompt, "image_size": ASPECT}
    else:
        _asp = config.get("reference_aspect", "16:9")
        args = {"prompt": full_prompt, "aspect_ratio": _asp}
    if negative:
        # Most fal image models accept negative_prompt; harmless if ignored.
        args["negative_prompt"] = negative
    if model == "flux":'''


def patch_code() -> bool:
    if not SRC.exists():
        print(f"ERROR: {SRC} not found."); return False
    t = SRC.read_text()
    if 'aspect_ratio": _asp' in t:
        print("Code already patched (per-model size param). No-op.")
        return True
    if OLD_CODE not in t:
        print("ERROR: generate_still args block not found verbatim -- drifted. Aborting code patch.")
        return False
    new = t.replace(OLD_CODE, NEW_CODE, 1)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(new); tmp = f.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: would not compile: {e}. Aborting."); os.unlink(tmp); return False
    os.unlink(tmp)
    shutil.copy2(SRC, SRC.with_suffix(".py.bak_all_nb2"))
    SRC.write_text(new)
    print("OK code: per-model size param (NB2->aspect_ratio string, flux->image_size dict).")
    return True


def patch_channel() -> bool:
    if not CH.exists():
        print(f"ERROR: {CH} not found."); return False
    cfg = json.loads(CH.read_text())
    if cfg.get("image_model") == "nano_banana":
        print("channel.json already image_model:nano_banana. No-op.")
        return True
    cfg["image_model"] = "nano_banana"
    shutil.copy2(CH, CH.with_suffix(".json.bak_all_nb2"))
    CH.write_text(json.dumps(cfg, indent=2) + "\n")
    json.loads(CH.read_text())
    print("OK channel.json: image_model restored to nano_banana (all-NB2).")
    return True


def main() -> int:
    ok_code = patch_code()
    ok_ch = patch_channel()
    return 0 if (ok_code and ok_ch) else 1


if __name__ == "__main__":
    sys.exit(main())
