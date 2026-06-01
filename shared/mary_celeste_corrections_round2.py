#!/usr/bin/env python3
"""
mary_celeste_corrections_round2.py — Second round of shot fixes after review.

Two specific issues that survived the first correction pass:
- Shot 087: newspaper heading still shows duplicate "MARY"
- Shot 165: man appears to be standing on the outside of the railing

Run from final-hours/ directory:
    python ../shared/mary_celeste_corrections_round2.py

Cost: 2 restills * ~$0.15 = ~$0.30 total.
"""

import json
import subprocess
import sys
from pathlib import Path


CORRECTIONS = {
    87: "A period 1870s magazine or newspaper page lying open on a wooden surface, soft window light falling across it, the page filled with dense columns of small illegible print, a single line illustration at the top of the page, no large headlines or block lettering visible anywhere in the frame, sepia and cream tones, period engraved printed page, just dense small print and one small line-art illustration.",

    165: "Captain Briggs standing on the wooden deck of the Mary Celeste at a midship position, seen from behind, his boots planted firmly on the deck planks which stretch in all directions around him, the wooden rail visible ahead of him at chest height as the boundary between the deck and the open sea beyond, his hands at his sides, the brigantine's masts rising above the frame, the figure properly inside the ship with the rail in front of him as a barrier to the ocean, period maritime composition.",
}


def main():
    storyboard_path = Path("projects/mary_celeste/storyboard.json")

    if not storyboard_path.exists():
        print(f"ERROR: {storyboard_path} not found. Run from final-hours/ directory.", file=sys.stderr)
        sys.exit(1)

    with open(storyboard_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    shots = data if isinstance(data, list) else data.get("beats", data.get("shots", []))

    print(f"Loaded {len(shots)} shots", flush=True)

    applied = []
    for shot_num, new_prompt in CORRECTIONS.items():
        idx = shot_num - 1
        if idx < 0 or idx >= len(shots):
            print(f"  Shot {shot_num}: out of range, skipping", flush=True)
            continue

        original = shots[idx].get("image_prompt", "")
        shots[idx]["image_prompt"] = new_prompt
        prev_corrections = shots[idx].get("_audit_correction", {})
        shots[idx]["_audit_correction"] = {
            "previous_prompt": original,
            "previous_correction": prev_corrections,
            "correction_reason": "round 2 human review fix",
            "corrected_at": "31 May 2026 round 2",
        }
        applied.append(shot_num)
        print(f"  Shot {shot_num}: prompt updated", flush=True)

    with open(storyboard_path, "w", encoding="utf-8") as f:
        if isinstance(data, list):
            json.dump(shots, f, indent=2, ensure_ascii=False)
        else:
            key = "beats" if "beats" in data else "shots"
            data[key] = shots
            json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nNow restilling {len(applied)} shots...", flush=True)

    succeeded = []
    failed = []
    for shot_num in applied:
        print(f"\n--- Restilling shot {shot_num} ---", flush=True)
        result = subprocess.run(
            ["python", "../shared/recreation_pipeline.py", "restill",
             "--project", "mary_celeste", "--shot", str(shot_num)],
            capture_output=False
        )
        if result.returncode == 0:
            succeeded.append(shot_num)
        else:
            failed.append(shot_num)

    print(f"\n=== Summary ===", flush=True)
    print(f"Succeeded: {succeeded}", flush=True)
    print(f"Failed: {failed}", flush=True)


if __name__ == "__main__":
    main()
