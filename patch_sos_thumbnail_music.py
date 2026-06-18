#!/usr/bin/env python3
"""
patch_sos_thumbnail_music.py

Idempotent: adds the `thumbnail` and `music` blocks to
scripture-on-screen/channel.json, tuned for the channel's vivid jewel-toned
human-drama look (NOT Prehistoric's catastrophe/dread tuning).

Schema matched against the live prehistoric-disasters/channel.json.

Run from repo root:
    LAPTOP:  python3 patch_sos_thumbnail_music.py
    BOX:     python patch_sos_thumbnail_music.py   (re-run -> 'unchanged')

Idempotent: only writes if the blocks are missing or differ. Verifies the
reference schema before writing. Creates scripture-on-screen/music/ (empty)
so the music dir exists for track drops.
"""

import json
import sys
from pathlib import Path

TARGET = "scripture-on-screen/channel.json"
REFERENCE = "prehistoric-disasters/channel.json"   # schema anchor

THUMBNAIL_BLOCK = {
    "composition": "figure_right",
    "candidates": 2,
    "candidate_prompt_suffix": (
        "YouTube thumbnail composition, strongly asymmetric: the single hero figure "
        "(or central subject) is massed in the RIGHT TWO-THIRDS of the frame, photoreal "
        "and richly lit in warm jewel tones; the LEFT THIRD is deliberately darker, "
        "lower-detail negative space reserved for a headline; cinematic chiaroscuro, "
        "the subject brightly and warmly lit against the darker left; single subject only, "
        "no clutter, no text, no letters"
    ),
    "selection_rules": [
        "ONE clear emotional subject that reads instantly at phone-thumbnail size",
        "vivid, warm, high-production cinematic look — premium, not flat or cartoonish; it must stand out in a feed",
        "the subject's face or posture carries a single legible emotion (fear, grief, awe, resolve)",
        "clean, darker, uncluttered negative space on the LEFT where the headline lands",
        "no garbled detail, no accidental letterforms, no duplicated or broken figures or hands, one subject only",
    ],
    "font": "shared/fonts/Anton-Regular.ttf",
    "font_fallbacks": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "Impact",
        "Arial Black",
    ],
    "title_color": [245, 240, 235],
    "subtitle_color": [240, 195, 90],
    "stroke_width": 12,
    "stroke_color": [0, 0, 0],
    "shadow": True,
    "shadow_offset": [5, 6],
    "shadow_blur": 6,
    "darken_factor": 1.0,
    "vignette_strength": 0.0,
    "scrim": {"side": "left", "width": 0.42, "opacity": 0.45, "feather": 0.7},
    "text_anchor": "top-left",
    "text_align": "left",
    "title_area_pct": 0.52,
    "title_max_height_pct": 0.34,
    "title_start_size": 150,
    "subtitle_area_pct": 0.55,
    "subtitle_max_height_pct": 0.14,
    "subtitle_start_size": 90,
    "margin": 20,
    "margin_x": 40,
    "margin_y": 20,
    "uppercase": True,
    "segment_foreground": False,
}

MUSIC_BLOCK = {
    "dir": "music",
    "tracks": 3,
    "crossfade_seconds": 2,
    "level": 0.07,
}


def main():
    root = Path.cwd()
    ref_path = root / REFERENCE
    tgt_path = root / TARGET

    if not ref_path.is_file():
        sys.exit(f"ABORT: reference '{REFERENCE}' not found from {root}. Run from repo root.")
    if not tgt_path.is_file():
        sys.exit(f"ABORT: target '{TARGET}' not found. Run the channel-setup patch first.")

    ref = json.loads(ref_path.read_text())

    # Schema check: every key we set in each block must exist in the reference block.
    for block_name, block in (("thumbnail", THUMBNAIL_BLOCK), ("music", MUSIC_BLOCK)):
        ref_block = ref.get(block_name)
        if not isinstance(ref_block, dict):
            sys.exit(f"ABORT: reference has no '{block_name}' block to match schema against.")
        unknown = set(block.keys()) - set(ref_block.keys())
        if unknown:
            sys.exit(
                f"ABORT: '{block_name}' keys not in {REFERENCE} schema: {sorted(unknown)}. "
                f"Resolve drift before writing."
            )

    cfg = json.loads(tgt_path.read_text())
    before = json.dumps(cfg, sort_keys=True)

    cfg["thumbnail"] = THUMBNAIL_BLOCK
    cfg["music"] = MUSIC_BLOCK

    after = json.dumps(cfg, sort_keys=True)
    new_text = json.dumps(cfg, indent=2, ensure_ascii=True) + "\n"

    if before == after and tgt_path.read_text() == new_text:
        print(f"  OK (unchanged): {TARGET}")
    else:
        tgt_path.write_text(new_text)
        print(f"  UPDATED: {TARGET}  (+thumbnail +music blocks)")

    json.loads(tgt_path.read_text())
    print(f"  VERIFIED: {TARGET} parses cleanly.")

    music_dir = root / "scripture-on-screen" / "music"
    music_dir.mkdir(parents=True, exist_ok=True)
    n = len([p for p in music_dir.glob("*") if p.is_file() and not p.name.startswith(".")])
    print(f"  music dir: {music_dir.relative_to(root)}/  ({n} track(s) present)")
    print("  NOTE: drop 8 space-free-named tracks into that folder; assembler picks 3 at random.")
    print("  DONE.")


if __name__ == "__main__":
    main()
