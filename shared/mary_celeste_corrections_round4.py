#!/usr/bin/env python3
"""Round 4 corrections: shots 3 (add ripped sails, remove people) and 5 (remove last person)."""

import json
import subprocess
from pathlib import Path


CORRECTIONS = {
    3: "The Mary Celeste drifting alone on the grey Atlantic Ocean, completely empty of any human figures anywhere — no people on deck, no people visible at any rail, no figures at the wheel, the brigantine entirely deserted. Her sails are still hanging from the masts but torn and ragged — large rips and tears in the canvas sails, edges frayed, some panels hanging loose in the wind, the rigging mostly intact but the canvas itself battered, several sails still partly set in disarray. Her wooden hull catches the flat overcast light. A wide cinematic shot with the empty vessel as the sole focus against an empty grey sea and overcast sky, no living soul anywhere in the frame, the ship eerily abandoned but still under sail with damaged canvas.",

    5: "The deck of the Mary Celeste seen from a wide elevated angle, completely empty of any human figures whatsoever — no people anywhere in the frame, no figures by the wheel, no figures by the masts, no figures by the rails, no figures in any corner of the composition, absolutely deserted. The wooden deck planks are weathered and salt-stained, ropes and lines neatly arranged across the planking, the ship's wheel stands alone unattended at center, the masts rise above frame, the grey Atlantic visible beyond the rails on all sides, period maritime composition emphasizing absolute absence of any human presence.",
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

    print(f"Loaded {len(shots)} shots", flush=True)

    applied = []
    for shot_num, new_prompt in CORRECTIONS.items():
        idx = shot_num - 1
        original = shots[idx].get("image_prompt", "")
        shots[idx]["image_prompt"] = new_prompt
        prev = shots[idx].get("_audit_correction", {})
        shots[idx]["_audit_correction"] = {
            "previous_prompt": original,
            "previous_correction": prev,
            "correction_reason": "round 4: shot 3 add ripped sails + remove people, shot 5 remove last person",
            "corrected_at": "01 June 2026 round 4",
        }
        applied.append(shot_num)
        print(f"  Shot {shot_num}: prompt updated", flush=True)

    with open(storyboard_path, "w", encoding="utf-8") as f:
        if is_list:
            json.dump(shots, f, indent=2, ensure_ascii=False)
        else:
            data[key] = shots
            json.dump(data, f, indent=2, ensure_ascii=False)

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

    print(f"\nDone. {len(deleted)} clips deleted, will re-animate on next finish run.")


if __name__ == "__main__":
    main()
