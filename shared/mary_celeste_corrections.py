#!/usr/bin/env python3
"""
mary_celeste_corrections.py — Apply Peter's shot-level review corrections

Updates image_prompts in projects/mary_celeste/storyboard.json for shots
flagged during human review, then re-runs restill on each corrected shot.

Run from final-hours/ directory:
    python ../shared/mary_celeste_corrections.py

Each restill is independent. If fal blips on one shot, others continue.
Cost: 17 restills * ~$0.15 = ~$2.55 total.

Period accuracy notes:
- Shot 135: Trinity Church spire used (NYC 1872 tallest), NOT Empire State (1931)
- Shot 120: Both figures from behind to avoid character drift
"""

import json
import subprocess
import sys
from pathlib import Path


# Each entry: shot_index (1-based, as the pipeline numbers them) -> new image_prompt
CORRECTIONS = {
    8: "A medium shot of the Mary Celeste's wooden ship's wheel, mounted vertically in its functional housing on the open deck, large and dark-stained, the wooden spokes radiating from a central hub, the wheel turning slowly unattended, the grey Atlantic visible beyond the stern rail, no human figure present, period maritime composition with the wheel in its proper upright mounted position.",

    14: "The cargo hold of the Mary Celeste — a small brigantine's interior space, low wooden ceiling beams pressing close overhead, perhaps thirty to forty wooden barrels of industrial alcohol stacked in tight rows along the wooden ribs of the ship, dim light filtering down from a single open hatch above, water pooled at the bottom planks, an intimate cramped working space appropriate to a 280-ton vessel, not a cavernous hold.",

    35: "A small boy of seven and his grandmother seated together in a Massachusetts farmhouse parlour, both seen partially turned away from the viewer, only two figures in the room — the boy in a wool jacket at her side, the grandmother in a long dark dress and shawl, late afternoon window light falling across the wooden floor, period 1880s domestic interior, just one boy and one older woman in frame.",

    71: "Two ships on the grey Atlantic — only the Dei Gratia leading and the Mary Celeste being towed behind on a long line, both vessels seen from a distance in the flat grey light of the open ocean, the Mary Celeste trailing crewless with her sails partly set, no other vessels visible anywhere on the horizon, an empty sea around them.",

    82: "A period 1870s newspaper laid open on a wooden table, a single main headline reading 'THE MARY CELESTE' in large black blockletter type, the rest of the page filled with small dense column text and small period line illustrations, no subheadings visible, only the one dominant headline, period engraved typography, sepia and cream tones.",

    86: "A wooden writing desk seen from behind the writer's shoulder, an inkwell, a steel-nib pen, and writing paper arranged at the angle a right-handed writer would use, the paper positioned facing toward the writer as he would be writing on it, the writing itself out of focus and illegible as ink strokes flowing across the page, the partially-visible sleeve of a wool jacket holding the pen, lamplight pooling warmly on the paper, Victorian writing scene at a study desk, no large block lettering anywhere in frame.",

    87: "A period 1870s magazine or newspaper page with a single clear heading 'MARY CELESTE' in clean black blockletter type, no other large text visible anywhere in frame, smaller illegible column text below, period typography, sepia and cream tones, lying open on a wooden surface in soft window light.",

    103: "The Mary Celeste as seen from the deck of the Dei Gratia, the empty brigantine drifting at a slight angle on the grey Atlantic, her sails partly set, her hull catching the flat overcast light, no other vessels anywhere in the frame, an empty horizon stretching behind her in all directions, just the one drifting ship.",

    109: "The cargo hold of the Mary Celeste, low intimate space appropriate to a small 280-ton brigantine, perhaps thirty wooden barrels arranged in tight rows along the wooden ribs of the hull, a single lantern hanging from a hook casting amber light across the timbers, water pooled at the deck-bottom, dim and atmospheric, a working ship's hold that is cramped and human-scale, not cavernous.",

    120: "A small boy of seven and his grandmother walking together along a Massachusetts country road, both seen from behind so neither face is visible, the boy in a wool jacket and short trousers walking at her side, the grandmother in a long dark dress and shawl, their hands clasped between them, autumn New England landscape ahead with bare trees on either side, the long perspective of the dirt road stretching away from the viewer, period 1880s rural Massachusetts, both figures viewed from behind.",

    135: "The Mary Celeste sailing out of New York harbour in November 1872, a single brigantine seen from across the harbour water under her working sails, the lower Manhattan shoreline visible in the distance — period accurate 1872 skyline with the spire of Trinity Church rising above the low brick and stone buildings of the time as the tallest structure in the city, masts of other vessels in the foreground at the South Street docks, smoke rising from chimneys along the waterfront, only one ship under sail, period accurate 1872 harbor departure scene.",

    136: "A wide shot of the Mary Celeste sailing alone on the grey Atlantic Ocean, her sails partly set, no human figures visible on her decks, the open sea stretching to a flat overcast horizon, the empty brigantine continuing on her own under wind and current, period maritime composition, dignified and quiet.",

    152: "An older woman seated in a Victorian parlour reading a folded newspaper, her two hands gripping the edges of the paper tightly, her face turned down toward the page in three-quarter profile so her expression is partial and grief-struck, her shoulders tensed in shock, dim afternoon light from a single window beside her, period 1870s domestic interior with patterned wallpaper, only her two hands visible on the newspaper, no other hands anywhere in frame.",

    155: "An older man seated in a leather chair reading a slim hardcover book, the book held up so the title-side cover faces the viewer at an angle, the lettering on the cover deliberately soft and out of focus and illegible, warm lamplight pooling on the book and the man's hands, a side table with a half-empty teacup beside him, late Victorian gentleman's library setting with bookshelves behind, the book cover lettering unreadable.",

    157: "A period 1880s newspaper illustration of the Mary Celeste as a ghost ship, the empty brigantine drifting alone on the Atlantic rendered in soft engraved line-art style, sea swells in patterned cross-hatching beneath her hull, no human figures visible anywhere, no monstrous or supernatural elements, no demonic imagery, a restrained dignified period engraving in the style of Harper's Weekly, the ship as the sole focus, the mood mysterious but never ghoulish, sepia and cream tones, period printed illustration.",

    165: "Captain Briggs's figure standing at the wooden rail of the Mary Celeste, seen from behind with his shoulders and the back of his head silhouetted against the open sea, the wooden deck planks clearly visible beneath his boots stretching toward the rail he stands at, his hands resting on the wooden rail, the brigantine's masts rising above frame, looking out toward a grey Atlantic horizon, the deck firmly under his feet, period maritime composition with the figure properly grounded on the ship.",

    166: "The Mary Celeste in rough November Atlantic weather, dark swells rolling around the brigantine, the bow cutting through the water with spray rising at the rail, the ship sailing well under reduced canvas with most sails reefed, the deck wet but clearly riding above the water, an overcast sky pressing down, period maritime storm composition where the ship is competently riding the waves rather than being overwhelmed by them, atmospheric and tense rather than catastrophic.",

    167: "A wooden table in the captain's cabin showing personal objects — a clean traditional clay pipe lying on its side with intact stem and bowl, a leather-bound logbook closed beside it, a brass compass, a folded nautical chart — the clay pipe rendered as a recognizable period item with proper form, the objects arranged as if recently set down, warm lamplight catching the brass and worn wood, intimate close composition, period 1870s maritime captain's belongings, all objects properly formed and recognizable.",
}


def main():
    storyboard_path = Path("projects/mary_celeste/storyboard.json")

    if not storyboard_path.exists():
        print(f"ERROR: {storyboard_path} not found. Run from final-hours/ directory.", file=sys.stderr)
        sys.exit(1)

    # Load
    with open(storyboard_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    shots = data if isinstance(data, list) else data.get("beats", data.get("shots", []))

    print(f"Loaded {len(shots)} shots from {storyboard_path}", flush=True)
    print(f"Applying {len(CORRECTIONS)} corrections...", flush=True)

    # Apply corrections (shots are 0-indexed in the list but pipeline displays 1-indexed)
    applied = []
    for shot_num, new_prompt in CORRECTIONS.items():
        idx = shot_num - 1  # convert 1-indexed display number to 0-indexed list position
        if idx < 0 or idx >= len(shots):
            print(f"  Shot {shot_num}: out of range, skipping", flush=True)
            continue

        original = shots[idx].get("image_prompt", "")
        shots[idx]["image_prompt"] = new_prompt
        shots[idx]["_audit_correction"] = {
            "previous_prompt": original,
            "correction_reason": "human-review shot-level fix",
            "corrected_at": "31 May 2026",
        }
        applied.append(shot_num)
        print(f"  Shot {shot_num}: prompt updated", flush=True)

    # Save updated storyboard
    with open(storyboard_path, "w", encoding="utf-8") as f:
        json.dump(data if isinstance(data, list) else {**data, ("beats" if "beats" in data else "shots"): shots}, f, indent=2, ensure_ascii=False)

    print(f"\nSaved updated storyboard with {len(applied)} corrections", flush=True)
    print(f"\nNow restilling {len(applied)} shots...", flush=True)

    # Restill each corrected shot
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
            print(f"  Shot {shot_num}: restill failed (return code {result.returncode})", flush=True)

    print(f"\n=== Summary ===", flush=True)
    print(f"Corrections applied: {len(applied)}", flush=True)
    print(f"Restills succeeded: {len(succeeded)}", flush=True)
    print(f"Restills failed: {len(failed)}", flush=True)
    if failed:
        print(f"Failed shots (rerun individually): {failed}", flush=True)


if __name__ == "__main__":
    main()
