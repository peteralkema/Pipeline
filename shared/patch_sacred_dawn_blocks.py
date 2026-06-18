#!/usr/bin/env python3
"""Idempotent: add thumbnail + music + kling_count blocks to sacred-dawn/channel.json.
Safe to re-run. Backs up to channel.json.pre_blocks. Verifies before and after."""
import json, shutil, sys
from pathlib import Path

CJ = Path(__file__).resolve().parent.parent / "sacred-dawn" / "channel.json"

THUMB = {
  "composition": "centered_subject",
  "candidates": 2,
  "candidate_prompt_suffix": "YouTube thumbnail composition, cinematic biblical epic, painterly oil-painting light, dramatic chiaroscuro and volumetric god-rays; ONE dominant faceless silhouette or colossal form massed in the RIGHT TWO-THIRDS of the frame, lit against a vast dramatic sky; the LEFT THIRD deliberately dark, shadowed, low-detail negative space reserved for a headline; warm gold and amber deepening to storm-grey and ash; high contrast, deep shadow, reverent and majestic, weathered antiquity; single subject only, no clutter, faceless, no text, no letters, no modern elements",
  "selection_rules": [
    "ONE reverent, awe-striking biblical subject that reads instantly at phone-thumbnail size",
    "maximum cinematic chiaroscuro drama so it stands out in a dim feed",
    "faceless figures only - no resolved faces, no garbled features",
    "clean darker uncluttered negative space in the TOP-LEFT where the headline lands",
    "no accidental letterforms, no duplicated or broken figures, one subject only"
  ],
  "font": "shared/fonts/Anton-Regular.ttf",
  "font_fallbacks": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "Impact", "Arial Black"],
  "title_color": [245, 240, 235],
  "subtitle_color": [255, 200, 90],
  "stroke_width": 12, "stroke_color": [0, 0, 0],
  "shadow": True, "shadow_offset": [5, 6], "shadow_blur": 6,
  "darken_factor": 1.0, "vignette_strength": 0.0,
  "scrim": {"side": "left", "width": 0.42, "opacity": 0.55, "feather": 0.7},
  "text_anchor": "top-left", "text_align": "left",
  "title_area_pct": 0.52, "title_max_height_pct": 0.34, "title_start_size": 150,
  "subtitle_area_pct": 0.55, "subtitle_max_height_pct": 0.14, "subtitle_start_size": 90,
  "margin": 20, "margin_x": 40, "margin_y": 20,
  "uppercase": True, "segment_foreground": False
}
MUSIC = {"dir": "music", "tracks": 3, "crossfade_seconds": 2, "level": 0.07}

def main():
    if not CJ.exists():
        sys.exit(f"NOT FOUND: {CJ}")
    d = json.loads(CJ.read_text())
    if d.get("name") != "sacred_dawn":
        sys.exit(f"REFUSE: expected name 'sacred_dawn', got {d.get('name')!r}")

    backup = CJ.with_suffix(".json.pre_blocks")
    if not backup.exists():
        shutil.copy2(CJ, backup)
        print(f"backup -> {backup}")
    else:
        print(f"backup already exists -> {backup} (idempotent re-run)")

    changed = []
    if d.get("thumbnail") != THUMB:
        d["thumbnail"] = THUMB; changed.append("thumbnail")
    if d.get("music") != MUSIC:
        d["music"] = MUSIC; changed.append("music")
    if d.get("kling_count") != 2:
        d["kling_count"] = 2; changed.append("kling_count")

    CJ.write_text(json.dumps(d, indent=2) + "\n")

    v = json.loads(CJ.read_text())
    assert v["thumbnail"]["composition"] == "centered_subject"
    assert v["music"]["tracks"] == 3
    assert v["kling_count"] == 2
    assert v["name"] == "sacred_dawn" and v["voice_id"] == "Elliot"
    print(f"changed: {changed or '(nothing - already current)'}")
    print(f"VERIFIED: thumbnail+music+kling_count present, name/voice intact")

if __name__ == "__main__":
    main()
