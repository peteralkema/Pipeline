#!/usr/bin/env python3
"""Round 3 corrections for Mary Celeste: shots 3, 5, 19."""

import json
import subprocess
import sys
from pathlib import Path


CORRECTIONS = {
    3: "The Mary Celeste drifting alone on the grey Atlantic Ocean, completely empty of any human figures anywhere — no people on deck, no people visible at any rail, no figures at the wheel, the brigantine entirely deserted, her sails partly set and slack, her wooden hull catching the flat overcast light, a wide cinematic shot with the empty vessel as the sole focus against an empty grey sea and overcast sky, no living soul anywhere in the frame, the ship eerily abandoned.",
    5: "The deck of the Mary Celeste seen from a wide elevated angle, completely empty of any human figures, the wooden deck planks weathered and salt-stained, ropes and lines neatly arranged, the ship's wheel standing alone unattended, the masts rising above frame, the grey Atlantic visible beyond the rails, no people anywhere in the frame, the deck eerily deserted, period maritime composition emphasizing absence.",
    19: "The stern of the Mary Celeste showing the empty davits — iron arms and pulleys clearly visible, the tackle ropes coiled neatly and hanging undamaged from the davits but holding nothing, no small boat or yawl present in the davits or anywhere in the frame, just the bare iron brackets and the neat hanging ropes, the wooden deck planks of the stern beneath, the grey Atlantic visible beyond the rail in the background, a static composition emphasizing the absence of the yawl boat, no other vessels or boats anywhere in the frame.",
}

MOTION_UPDATES = {
    19: "A very slow static composition with only the subtlest atmospheric shift in the grey sky behind the rail, no camera movement downward, no panning through the deck, just held attention on the empty davits and hanging tackle ropes.",
}


def main():
    project_dir = Path("projects/mary_celeste")
    storyboard_path = project_dir / "storyboard.json"
    clips_dir = project_dir / "clips"

    with open(storyboard_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    is_list = isinstance(data, list)
    if is_list:
        shots = data
        storyboard_key = None
    else:
        storyboard_key = "beats" if "beats" in data else "shots"
        shots = data[storyboard_key]

    print(f"Loaded {len(shots)} shots", flush=True)

    applied = []
    for shot_num, new_prompt in CORRECTIONS.items():
        idx = shot_num - 1
        original = shots[idx].get("image_prompt", "")
        shots[idx]["image_prompt"] = new_prompt
        if shot_num in MOTION_UPDATES:
            shots[idx]["motion_prompt"] = MOTION_UPDATES[shot_num]
        prev = shots[idx].get("_audit_correction", {})
        shots[idx]["_audit_correction"] = {
            "previous_prompt": original,
            "previous_correction": prev,
            "correction_reason": "round 3: remove people/objects that violate narrative truth",
            "corrected_at": "01 June 2026 round 3",
        }
        applied.append(shot_num)
        print(f"  Shot {shot_num}: prompt updated", flush=True)

    with open(storyboard_path, "w", encoding="utf-8") as f:
        if is_list:
            json.dump(shots, f, indent=2, ensure_ascii=False)
        else:
            data[storyboard_key] = shots
            json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved storyboard with {len(applied)} corrections", flush=True)

    deleted = []
    if clips_dir.exists():
        for shot_num in applied:
            clip = clips_dir / f"clip_{shot_num:03d}.mp4"
            if clip.exists():
                clip.unlink()
                deleted.append(shot_num)
                print(f"  Deleted {clip.name}", flush=True)

    print(f"\nRestilling {len(applied)} shots...", flush=True)
    for shot_num in applied:
        print(f"--- Restilling shot {shot_num} ---", flush=True)
        subprocess.run(
            ["python", "../shared/recreation_pipeline.py", "restill",
             "--project", "mary_celeste", "--shot", str(shot_num)],
            check=False
        )

    print(f"\nDone. Now review stills and run:", flush=True)
    print(f"  python -u ../shared/recreation_pipeline.py finish --project mary_celeste --no-music")


if __name__ == "__main__":
    main()
