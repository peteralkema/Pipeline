#!/usr/bin/env python3
"""Drop image_model:nano_banana from qqrew/channel.json -> falls back to the
module default IMAGE_MODEL="flux".

Two reasons:
1. FIXES 16:9 on crew-absent text beats. nano_banana (fal-ai/nano-banana
   text-to-image) ignores the image_size {width,height} DICT and defaults to
   1024x1024 square (probe beats 1 & 4). flux-pro/v1.1 honors the dict -> 16:9.
2. MATCHES TIER. nano_banana was a flat-cel-era / flooding-cost choice; the
   channel is now semi-realistic cinematic, so the crew-absent wides should use
   the same flux engine as the reference-tier channels, not a cheaper model.

Skeptic beats are unaffected (they route through NB2 /edit regardless).
Idempotent: no-ops if image_model already absent.
"""
import json, shutil, sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "qqrew" / "channel.json"

def main() -> int:
    if not TARGET.exists():
        print(f"ERROR: {TARGET} not found."); return 1
    cfg = json.loads(TARGET.read_text())
    if "image_model" not in cfg:
        print("Already dropped (no image_model key). No-op."); return 0
    old = cfg.pop("image_model")
    backup = TARGET.with_suffix(".json.bak_drop_image_model")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(json.dumps(cfg, indent=2) + "\n")
    json.loads(TARGET.read_text())
    print(f"OK dropped image_model (was: {old!r}) -> falls back to flux. Backup: {backup.name}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
