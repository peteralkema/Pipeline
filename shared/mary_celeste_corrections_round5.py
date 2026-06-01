#!/usr/bin/env python3
"""Round 5: shot 3 - harder anti-people prompt with kept ripped sails."""

import json
import subprocess
from pathlib import Path


CORRECTIONS = {
    3: "An empty abandoned ghost ship drifting alone on the grey Atlantic Ocean — a 19th century brigantine entirely deserted with absolutely zero human beings in the image, no crew, no figures, no silhouettes, no people anywhere on the deck or rigging or rails, completely uninhabited and abandoned. The masts and rigging are still standing but the canvas sails are torn, ripped, and ragged with frayed edges and large tears, several sails hanging loose and damaged in the wind, the rigging tangled in places. The wooden hull cuts slowly through grey swells beneath an overcast sky. Wide cinematic shot of the desolate vessel from a moderate distance, the lonely abandoned ship as the sole subject of the frame, an empty grey horizon all around, the feeling of a ghost ship found drifting with no living soul aboard, only the damaged ship and the empty ocean. NO PEOPLE. NO FIGURES. NO HUMANS. NO CREW. The deck is bare except for ropes and ship fittings.",
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
        key = None
    else:
        key = "beats" if "beats" in data else "shots"
        shots = data[key]

    for shot_num, new_prompt in CORRECTIONS.items():
        idx = shot_num - 1
        original = shots[idx].get("image_prompt", "")
        shots[idx]["image_prompt"] = new_prompt
        prev = shots[idx].get("_audit_correction", {})
        shots[idx]["_audit_correction"] = {
            "previous_prompt": original,
            "previous_correction": prev,
            "correction_reason": "round 5: harder anti-people language while keeping ripped sails",
            "corrected_at": "01 June 2026 round 5",
        }
        print(f"  Shot {shot_num}: prompt updated", flush=True)

    with open(storyboard_path, "w", encoding="utf-8") as f:
        if is_list:
            json.dump(shots, f, indent=2, ensure_ascii=False)
        else:
            data[key] = shots
            json.dump(data, f, indent=2, ensure_ascii=False)

    for shot_num in CORRECTIONS:
        clip = clips_dir / f"clip_{shot_num:03d}.mp4"
        if clip.exists():
            clip.unlink()
            print(f"  Deleted {clip.name}", flush=True)

    for shot_num in CORRECTIONS:
        print(f"--- Restilling shot {shot_num} ---", flush=True)
        subprocess.run(
            ["python", "../shared/recreation_pipeline.py", "restill",
             "--project", "mary_celeste", "--shot", str(shot_num)],
            check=False
        )


if __name__ == "__main__":
    main()
