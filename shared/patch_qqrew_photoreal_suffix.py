#!/usr/bin/env python3
"""Replace QQrew's flat-cel/webcomic style_suffix with a semi-realistic
cinematic one matching the approved trio reference (02_egyptian_tomb.png) and
the NB2 probe look (Mars/Colosseum).

The old suffix HARD-BANNED the exact qualities Peter wants ("NOT painterly, NOT
semi-realistic, NOT rendered") and forced a webcomic cartoon on every
text-to-image beat -> the kids-cartoon stills. The new suffix steers toward the
rich semi-realistic cinematic-illustration look the reference images actually are.

Idempotent: matches the exact current flat-cel string, backs up, validates JSON,
no-ops if already the photoreal suffix.
"""
import json, shutil, sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "qqrew" / "channel.json"

OLD = ("flat 2D cartoon illustration in a clean modern webcomic style, bold "
       "uniform dark ink outlines of even weight, large areas of flat solid "
       "color with hard cel-shadow edges, absolutely no gradients, no soft "
       "shading, no airbrushing, no glossy highlights, no bloom, no depth of "
       "field, simple flat illustrated background, matte, high contrast, "
       "graphic and bold, NOT photorealistic, NOT 3d render, NOT rendered, "
       "NOT painterly, NOT semi-realistic, no text, no letters, 16:9")

NEW = ("semi-realistic cinematic digital illustration, painterly rendered "
       "lighting and soft shading, rich detailed illustrated background, warm "
       "cinematic color grade, atmospheric depth, high detail, polished "
       "animated-film quality, appealing stylized realistic faces, no text, "
       "no letters, 16:9")


def main() -> int:
    if not TARGET.exists():
        print(f"ERROR: {TARGET} not found. Run from shared/ with qqrew/ sibling.")
        return 1
    cfg = json.loads(TARGET.read_text())
    cur = cfg.get("style_suffix", "")
    if cur == NEW:
        print("Already patched (photoreal suffix present). No-op.")
        return 0
    if cur != OLD:
        print("ERROR: current style_suffix does not match the expected flat-cel string.")
        print(f"Found: {cur[:90]}...")
        print("Aborting -- not overwriting an unexpected value.")
        return 1
    cfg["style_suffix"] = NEW
    backup = TARGET.with_suffix(".json.bak_photoreal_suffix")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(json.dumps(cfg, indent=2) + "\n")
    json.loads(TARGET.read_text())  # confirm valid
    print(f"OK patched {TARGET.name} (backup: {backup.name})")
    print(f"style_suffix now: {NEW}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
