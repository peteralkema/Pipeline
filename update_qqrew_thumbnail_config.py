#!/usr/bin/env python3
"""
update_qqrew_thumbnail_config.py -- config-only (no engine code) update to
qqrew/channel.json's thumbnail block for the solid-colour pose-picker.

Adds:
  - bg_palette: 5 on-brand solid background colours (the pose generator picks
    one at random per pose). Warm/high-key to match the ICE-AGE winner ref.
  - character_ref: which reference_map key the pose generator clones (brain).
  - pose_prompt_suffix: photoreal + solid-colour-bg + right-composed + no-text
    (REPLACES the stale flat-cel candidate_prompt_suffix for the pose path;
    candidate_prompt_suffix is left intact so nothing else breaks).
  - a `solid_color_character` sub-block: text layout for the B-variant (reuses
    the existing low_silhouette text keys; only bg handling differs).

Idempotent: re-running is a no-op (checks a sentinel key). Command-line JSON edit,
never a hand-edit. Run on LAPTOP, commit, push, pull on box.

    python3 update_qqrew_thumbnail_config.py --file qqrew/channel.json
"""
import argparse, json, sys
from pathlib import Path

PALETTE = [           # on-brand, high-key, feed-popping — matches ICE-AGE orange family
    [237, 106, 34],   # warm orange (the ICE-AGE ref)
    [22, 163, 184],   # teal (YOU'VE BEEN LIED TO ref)
    [245, 197, 24],   # golden yellow (NO SOAP ref)
    [201, 74, 74],    # warm red
    [79, 122, 189],   # cool blue
]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="qqrew/channel.json")
    a = ap.parse_args()
    p = Path(a.file)
    if not p.is_file():
        print(f"ERROR: not found: {p}", file=sys.stderr); return 2
    d = json.loads(p.read_text())
    tb = d.get("thumbnail")
    if not isinstance(tb, dict):
        print("ERROR: no thumbnail block", file=sys.stderr); return 3
    if tb.get("_pose_picker_v1"):
        print("already applied -> no-op"); return 0

    tb["bg_palette"] = PALETTE
    tb["character_ref"] = "brain"      # reference_map key the pose generator clones
    tb["pose_prompt_suffix"] = (
        "the character from the reference image, waist-up, pushed to the RIGHT side "
        "of the frame, a big clear readable facial expression, both hands kept within "
        "the right portion, the entire LEFT HALF of the frame the solid flat background "
        "colour with no figure and no hands in it for a headline, bright even high-key "
        "studio lighting, crisp photographic detail, natural realistic skin, vivid and "
        "punchy, photorealistic, NOT illustrated, NOT cel-shaded, no text, no letters, "
        "sixteen by nine"
    )
    # B-variant text layout: reuse the channel's existing low_silhouette text keys
    # (top-left, Anton, stroke 8, white/yellow) -- only the background differs, and
    # that's handled by the new make_thumbnail mode. Nothing to duplicate here.
    tb["_pose_picker_v1"] = True

    p.write_text(json.dumps(d, indent=2) + "\n")
    print(f"OK  qqrew thumbnail block updated: bg_palette(5), character_ref=brain, pose_prompt_suffix(photoreal)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
