#!/usr/bin/env python3
"""Second-pass style_suffix correction for QQrew (episode 4+).

The first swap (patch_qqrew_photoreal_suffix) killed the flat-cel webcomic look
but leaked the Final-Hours register in via "painterly / atmospheric depth /
warm cinematic color grade / soft shading" -> slightly moody, and a moody-lit
face reads as sullen (the pouty-Skeptic tell). This pass KEEPS the trio fidelity
(semi-realistic, real detailed faces, rich detailed backgrounds, depth, high
detail, polished animated quality) and swaps the moody-cinematic words for the
channel's actual register: bright, funky, high-key, vibrant, energetic, lots of
light. Semi-realistic in FIDELITY, bright/fun in REGISTER. Anti-dark,
anti-candlelight, anti-Victorian.

The MERCATOR1 render (01 Jul) used the interim painterly suffix deliberately
(good enough, not worth re-rendering) -- this corrects EP4 onward.

Idempotent: matches the interim painterly suffix exactly, backs up, validates.
"""
import json, shutil, sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "qqrew" / "channel.json"

OLD = ("semi-realistic cinematic digital illustration, painterly rendered "
       "lighting and soft shading, rich detailed illustrated background, warm "
       "cinematic color grade, atmospheric depth, high detail, polished "
       "animated-film quality, appealing stylized realistic faces, no text, "
       "no letters, 16:9")

NEW = ("semi-realistic modern animated-feature illustration, appealing "
       "realistic detailed faces, rich detailed illustrated backgrounds, "
       "bright high-key lighting, vibrant saturated color, crisp clean and "
       "dynamic, lots of light and energy, polished animated-feature quality, "
       "high detail, inviting and fun, no text, no letters, 16:9")


def main() -> int:
    if not TARGET.exists():
        print(f"ERROR: {TARGET} not found. Run from shared/ with qqrew/ sibling.")
        return 1
    cfg = json.loads(TARGET.read_text())
    cur = cfg.get("style_suffix", "")
    if cur == NEW:
        print("Already patched (bright suffix present). No-op.")
        return 0
    if cur != OLD:
        print("ERROR: current style_suffix is not the interim painterly string.")
        print(f"Found: {cur[:90]}...")
        print("Aborting -- not overwriting an unexpected value.")
        return 1
    cfg["style_suffix"] = NEW
    backup = TARGET.with_suffix(".json.bak_bright_suffix")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(json.dumps(cfg, indent=2) + "\n")
    json.loads(TARGET.read_text())
    print(f"OK patched {TARGET.name} (backup: {backup.name})")
    print(f"style_suffix now: {NEW}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
