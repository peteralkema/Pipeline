#!/usr/bin/env python3
"""
patch_scripture_on_screen_channel.py

Idempotent channel setup for the new 'Scripture On Screen' channel.
Creates scripture-on-screen/channel.json from the reconciled spec
(schema matched against the live sacred-dawn/channel.json).

Does NOT create the esther project folder (Peter creates that via
Mission Control when placing the script).

Run from repo root:
    laptop:  python3 patch_scripture_on_screen_channel.py
    (then commit, push; pull on box; re-run there to verify idempotency)

Safe to run repeatedly: it writes only if the file is missing or differs,
and verifies against the sibling sacred-dawn schema before writing.
"""

import json
import sys
from pathlib import Path

SLUG_DIR = "scripture-on-screen"
REFERENCE = "sacred-dawn/channel.json"   # schema anchor (must exist)

CHANNEL_JSON = {
    "name": "scripture_on_screen",
    "voice_id": "Ren",
    "style_suffix": (
        "cinematic biblical epic, richly saturated jewel tones, "
        "vivid technicolor-painterly palette, deep oil-painting colour, "
        "luminous golden-hour light, lush fabrics and gold and lapis ornament, "
        "warm dramatic chiaroscuro, period-accurate ancient Near East, Egypt and Persia, "
        "painterly photorealism, expressive single figures, "
        "no text, no modern elements, 16:9"
    ),
    "default_music_prompt": (
        "Warm orchestral storytelling score for a cinematic biblical drama. "
        "Emotive strings and woodwinds, hopeful and humane, swelling brass on moments "
        "of triumph, harp and gentle choir on tender beats, restrained low percussion "
        "only on deliverance and action beats. Melodic but never competing with a narrator. "
        "Intimate and grand by turns. No modern instruments."
    ),
    "base_canon": {},
    "upload": {
        "category_id": "24",
        "privacy_status": "private",
    },
    "default_motion": (
        "dramatic cinematic motion, lively pan and zoom interplay, "
        "expressive movement across the scene, warm dramatic lighting, "
        "intimate slow push-in by default with dramatic reveals"
    ),
}


def main():
    repo_root = Path.cwd()

    # 1) Anchor check: confirm we're at repo root and the reference channel exists.
    ref_path = repo_root / REFERENCE
    if not ref_path.is_file():
        sys.exit(
            f"ABORT: reference '{REFERENCE}' not found from {repo_root}. "
            f"Run this from the repo root."
        )

    # 2) Schema check: our keys must be a subset of the reference's keys.
    try:
        ref = json.loads(ref_path.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"ABORT: could not parse {REFERENCE}: {e}")

    ref_keys = set(ref.keys())
    our_keys = set(CHANNEL_JSON.keys())
    unknown = our_keys - ref_keys
    if unknown:
        sys.exit(
            f"ABORT: keys not present in {REFERENCE} schema: {sorted(unknown)}. "
            f"Resolve schema drift before writing."
        )
    missing = ref_keys - our_keys
    if missing:
        print(f"  NOTE: reference has extra keys we omit (ok if intentional): {sorted(missing)}")

    # 3) Create the channel directory.
    chan_dir = repo_root / SLUG_DIR
    chan_dir.mkdir(parents=True, exist_ok=True)

    # 4) Write channel.json idempotently.
    target = chan_dir / "channel.json"
    new_text = json.dumps(CHANNEL_JSON, indent=2, ensure_ascii=True) + "\n"

    if target.is_file():
        if target.read_text() == new_text:
            print(f"  OK (unchanged): {target.relative_to(repo_root)}")
        else:
            target.write_text(new_text)
            print(f"  UPDATED: {target.relative_to(repo_root)}")
    else:
        target.write_text(new_text)
        print(f"  CREATED: {target.relative_to(repo_root)}")

    # 5) Verify round-trip parse.
    json.loads(target.read_text())
    print(f"  VERIFIED: {target.relative_to(repo_root)} parses cleanly.")
    print("  DONE. (esther project folder intentionally NOT created.)")


if __name__ == "__main__":
    main()
