#!/usr/bin/env python3
"""
patch_crew_thumb_suffix.py - rewrite crew-wip thumbnail candidate_prompt_suffix.

The inherited suffix fights every reaction-thumbnail subject on three axes, proven
across multiple re-rolls 29 Jun:
  1. "a single appealing young man's face" - no clean-shaven assertion, so flux
     defaults to a beard/stubble on close-ups. The subject's "no beard" negation
     can't beat it (same lesson as the glasses: positive prompt is the only lever).
  2. "massed in the right two-thirds ... left third backdrop" - reads as CENTERED
     with a thin left margin, overriding any "push him right" in the subject.
  3. "friendly and curious or wryly amused expression" - actively pulls the face
     back toward mild, fighting the HUGE reaction expression a thumbnail needs.

New suffix fixes all three POSITIVELY (the only reliable lever on flux-pro):
  - asserts clean-shaven / smooth face / no facial hair
  - pushes the character to the RIGHT, the LEFT HALF empty for the headline
  - drops the expression constraint (lets the subject drive the emotion)
  - keeps the flat-cel anti-realism and no-text rules

Idempotent (compares to target). Pure ASCII. Backup sidecar. Run on LAPTOP,
commit -> push -> box pull. Safe mid-render: only affects NEW thumbnail generations.
"""
import json
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "crew-wip" / "channel.json"

NEW_SUFFIX = (
    "a single appealing flat cel-shaded illustrated young man, clean-shaven with a "
    "smooth bare face, no beard, no stubble, no facial hair, big expressive cartoon "
    "face and upper body pushed to the RIGHT side of the frame, the character and "
    "both hands kept within the right portion, the entire LEFT HALF of the frame a "
    "clean simple uncluttered background for a headline with no figure and no hands "
    "in it, bright warm high-key lighting, vivid saturated punchy color that pops in "
    "a feed, bold rim lighting on the character, confident dark linework, smooth "
    "animated-feature style, NOT photorealistic, NOT 3d render, NOT realistic skin, "
    "no text, no letters, sixteen by nine"
)


def main():
    if not TARGET.exists():
        sys.exit(f"channel.json not found: {TARGET}")
    original_text = TARGET.read_text()
    cfg = json.loads(original_text)
    thumb = cfg.get("thumbnail")
    if not isinstance(thumb, dict):
        sys.exit("ABORT: channel.json has no thumbnail block")

    if thumb.get("candidate_prompt_suffix") == NEW_SUFFIX:
        print("skip: candidate_prompt_suffix already updated. Idempotent OK.")
        return

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_thumbsuffix")
    if not backup.exists():
        backup.write_text(original_text)
        print(f"backup -> {backup.name}")

    old = thumb.get("candidate_prompt_suffix", "")
    thumb["candidate_prompt_suffix"] = NEW_SUFFIX
    TARGET.write_text(json.dumps(cfg, indent=2, ensure_ascii=True) + "\n")
    print("patched candidate_prompt_suffix")
    print(f"  old len {len(old)} -> new len {len(NEW_SUFFIX)}")


if __name__ == "__main__":
    main()
