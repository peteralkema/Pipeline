#!/usr/bin/env python3
"""
patch_crew_channel.py  -  create/verify the crew-wip channel config pair.

Writes two files into <repo>/crew-wip/:
  - channel.json   (identity: voice, style, Driver base_canon lock, thumbnail, upload)
  - rulebook.json  (modern-affirming people_directive that overrides the period-
                    infected shared default via the positive-prompt lever)

DESIGN NOTES (why this is shaped the way it is):
  * base_canon carries the Driver under the key "driver". recreation_pipeline
    _expand_canon is TAG-TRIGGERED: it only injects the Driver into beats whose
    VISUAL references {driver}. Object-only beats (soap bar, empty chair) stay
    clean. Unknown/typo tags fail loudly at zero spend.
  * The shared rulebook (shared/rulebook.json) carries period negatives
    (modern clothing, t-shirt, wristwatch, eyeglasses, ...) that contradict this
    modern channel. load_rulebook merges negatives additively and CANNOT subtract,
    so we do NOT touch shared. Instead we override people_directive (the one field
    with replace-semantics) to affirm modern + flat-cel. On flux-pro the positive
    prompt beats the negatives, so the period terms go inert against our positive.
  * kling_count is NOT a channel.json field. It is per-project in render_policy.json
    (engine default 40!). All-static rendering is forced at render time with
    --kling-count 0, NOT here. Do not add kling_count to channel.json (it would
    fail the schema subset and does nothing here anyway).
  * music is omitted (no library yet; *.mp3 is gitignored / box-local). Upgrade-
    ladder flip later by adding a music block + scp'ing tracks.

Idempotent: re-running writes nothing if the on-disk files already match target.
Pure ASCII. Run on the LAPTOP, then commit -> push -> box pull -> re-run to verify.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent          # shared/ -> repo root
CHANNEL_DIR = REPO / "crew-wip"

# ----------------------------------------------------------------------------
# Documented channel.json schema (canonical reference §12). Any key we emit must
# be in this set, else we have invented a field the pipeline will ignore.
# ----------------------------------------------------------------------------
ALLOWED_CHANNEL_KEYS = {
    "name", "voice_id", "style_suffix", "default_motion", "default_music_prompt",
    "base_canon", "upload", "thumbnail", "music", "speaking_rate",
}

# The Driver, verbatim from crew_character_bible.md "PROMPT TOKENS" (the locked
# tool-agnostic spec). Glasses are HIS and stay (resolved glasses saga).
DRIVER_TOKENS = (
    "a young adult man, early twenties, warm light-tan skin, short tousled brown "
    "hair, dark-framed glasses, friendly open face, slim build, wearing a blue "
    "denim jacket over a grey crew-neck t-shirt, dark jeans, a brown leather watch, "
    "and a tan canvas backpack worn evenly on both shoulders; curious and "
    "expressive, a touch wry"
)

CHANNEL_JSON = {
    "name": "crew_wip",
    "voice_id": "Evan",                # snake_case key; bare-name value (Victor/Reed pattern)
    "speaking_rate": 1.05,             # the dry-humour smirk cadence
    "style_suffix": (
        "clean flat 2D cel-shaded illustration, confident dark linework, "
        "simplified flat color planes, smooth animated-feature style, appealing "
        "stylized characters, rich illustrated background, warm lighting, vibrant "
        "color, NOT photorealistic, NOT 3d render, NOT realistic skin texture, "
        "bright and inviting, no text, no letters, 16:9"
    ),
    "base_canon": {
        "driver": DRIVER_TOKENS,
    },
    "upload": {
        "category_id": "24",           # Entertainment (the algorithm call)
        "privacy_status": "private",
    },
    "thumbnail": {
        # Structural layout mirrors success-coach (the proven modern face template);
        # only the prompt/selection/aesthetic words are swapped to flat-cel/bright.
        "composition": "low_silhouette",
        "candidates": 3,
        "segment_foreground": False,
        "font": "shared/fonts/Anton-Regular.ttf",
        "darken_factor": 1.0,
        "vignette": 0,
        "scrim": {"side": "left", "width": 0.46, "opacity": 0.68, "feather": 0.7},
        "text_anchor": "top-left",
        "text_align": "left",
        "title_area_pct": 0.52,
        "title_max_height_pct": 0.34,
        "title_start_size": 150,
        "subtitle_area_pct": 0.52,
        "subtitle_max_height_pct": 0.16,
        "subtitle_start_size": 64,
        "stroke_width": 8,
        "shadow": True,
        "margin_x": 40,
        "margin_y": 48,
        "title_color": [250, 250, 252],
        "subtitle_color": [255, 200, 60],
        "candidate_prompt_suffix": (
            "a single appealing flat cel-shaded illustrated young man's face and "
            "upper body massed in the right two-thirds, friendly and curious or "
            "wryly amused expression, looking toward camera, bright warm high-key "
            "lighting, clean simple illustrated background, vibrant tasteful color, "
            "confident dark linework, NOT photorealistic, NOT 3d render, the left "
            "third kept a simple uncluttered backdrop for the headline, no text, "
            "no letters, sixteen by nine"
        ),
        "selection_rules": (
            "Pick the candidate with the most appealing, on-model flat cel-shaded "
            "face: reject photoreal drift, malformed hands, extra fingers, dead "
            "eyes, or any 3d / realistic-skin look. Want bright warm lighting, a "
            "clear readable curious or wry expression, confident clean linework, "
            "and the cleanest uncluttered left third where the headline lands. "
            "Bright and inviting, never morbid, never photoreal. If no candidate is "
            "cleanly on-model, pick the most consistent with the channel style."
        ),
    },
}

RULEBOOK_JSON = {
    "negative": [],                    # rely on positive lever + style_suffix anti-realism
    "people_directive": (
        "where a crew character or hands appear, render them clearly and "
        "consistently shot to shot - a friendly expressive young-adult face to "
        "camera, well-formed natural hands - in contemporary modern-day clothing "
        "and settings, flat cel-shaded animated illustration, appealing and "
        "stylized, NOT photorealistic, NOT 3d render"
    ),
    "motion_rules": [],                # no Kling on this channel
}


def _validate():
    bad = set(CHANNEL_JSON) - ALLOWED_CHANNEL_KEYS
    if bad:
        sys.exit("ABORT: channel.json has non-schema key(s): %s" % sorted(bad))


def _write_if_changed(path, target):
    """Write target (pretty JSON) only if on-disk differs. Sidecar-backup first."""
    desired = json.dumps(target, indent=2, ensure_ascii=True) + "\n"
    if path.exists():
        current = path.read_text()
        if current == desired:
            print("skip: %s already correct" % path.name)
            return False
        backup = path.with_suffix(path.suffix + ".pre_crew")
        backup.write_text(current)
        print("backup: %s -> %s" % (path.name, backup.name))
    path.write_text(desired)
    print("wrote: %s" % path)
    return True


def main():
    _validate()
    CHANNEL_DIR.mkdir(parents=True, exist_ok=True)
    _write_if_changed(CHANNEL_DIR / "channel.json", CHANNEL_JSON)
    _write_if_changed(CHANNEL_DIR / "rulebook.json", RULEBOOK_JSON)
    print("--- crew-wip config now: ---")
    print("  channel.json keys :", sorted(CHANNEL_JSON))
    print("  base_canon tags   :", sorted(CHANNEL_JSON["base_canon"]))
    print("  voice_id          :", CHANNEL_JSON["voice_id"],
          "@", CHANNEL_JSON["speaking_rate"])
    print("  upload category   :", CHANNEL_JSON["upload"]["category_id"])
    print("  rulebook negatives:", len(RULEBOOK_JSON["negative"]),
          "| people_directive set:", bool(RULEBOOK_JSON["people_directive"]))


if __name__ == "__main__":
    main()
