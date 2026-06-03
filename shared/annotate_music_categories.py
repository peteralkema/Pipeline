"""
Music Category Annotator — Backfill music_category for Existing Storyboards
============================================================================
Use this ONCE to add music_category fields to a storyboard.json that was
generated before the slicing prompt was updated. After the slicing prompt
update, new storyboards include music_category natively and this script
is no longer needed for them.

Usage (run from channel root):
    python3 ../shared/annotate_music_categories.py --project projects/mary_celeste

What it does:
1. Reads project/storyboard.json
2. If music_category already present on all shots, prints status and exits
3. Otherwise, asks Claude to assign music_category per shot with continuity bias
4. Writes back to storyboard.json (creates .bak backup first)

Categories used:
- opening-portent: cold open, dread, sets stakes
- exposition-restrained: context build, named protagonist intro
- rising-stakes: things going wrong, building tension
- climactic-stillness: the dramatic moment, restrained NOT crescendo
- aftermath-reflection: closer, meaning lingers, solo piano

Continuity bias: Claude is instructed to STRONGLY prefer the same category
as the previous shot unless the narration clearly signals an emotional shift.
This produces 4-7 contiguous regions per video naturally.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
import anthropic


_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    load_dotenv()


CLAUDE_MODEL = "claude-sonnet-4-6"


PROMPT_TEMPLATE = """You are annotating a documentary storyboard with scene-emotion music categories.
Each shot already has narration text. Your job: add ONE music_category per shot.

Use these five categories. Pick the one that best fits the EMOTIONAL register of
that shot's narration:

- opening-portent: cold open atmospheric dread, establishment of place and stakes,
  the feeling that something is wrong or about to be
- exposition-restrained: historical context build, character introduction,
  factual delivery with sparse emotional underbed
- rising-stakes: things going wrong, complications mounting, controlled tension
  building. Use sparingly in Final Hours — the channel is meditative, not thriller.
- climactic-stillness: the dramatic moment the whole video is about. Discovery,
  collapse, decision. RESTRAINED-stillness register, NOT crescendo. Mary Celeste
  boarding the empty deck. The Hindenburg igniting. The boardroom vote.
- aftermath-reflection: the closer, the meaning landing, what we learn from this.
  Solo piano register. Quiet finality.

CRITICAL RULE — CONTINUITY BIAS:
Strongly prefer the SAME category as the previous shot. Only change category
when the narration clearly signals an emotional or scene-level shift. A typical
15-minute Final Hours video has 4-7 category transitions total, not 20+.

Here is the storyboard (each entry has index and narration; ignore image_prompt):

{shots_json}

Return a JSON array with one object per shot in the SAME ORDER:
[
  {{"index": 1, "music_category": "opening-portent"}},
  {{"index": 2, "music_category": "opening-portent"}},
  ...
]

Return ONLY the JSON array. No preamble, no markdown fences. Length must match
the input ({n_shots} shots)."""


def annotate(project_path):
    project_path = Path(project_path).expanduser()
    if not project_path.is_absolute() and len(project_path.parts) == 1 and Path("projects").is_dir():
        project_path = Path("projects") / project_path

    storyboard_path = project_path / "storyboard.json"
    if not storyboard_path.exists():
        raise SystemExit(f"No storyboard at {storyboard_path}")

    shots = json.loads(storyboard_path.read_text())
    if not isinstance(shots, list):
        raise SystemExit("Expected storyboard.json to be a JSON array of shots")

    # Check if already annotated
    if all("music_category" in s for s in shots):
        print(f"All {len(shots)} shots already have music_category. Nothing to do.")
        print("Categories present:")
        from collections import Counter
        counts = Counter(s["music_category"] for s in shots)
        for cat, n in counts.most_common():
            print(f"  {cat}: {n} shots")
        return

    # Build the slim shot list for Claude (just index + narration)
    slim = [{"index": s["index"], "narration": s.get("narration", "")} for s in shots]
    shots_json = json.dumps(slim, indent=2)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Missing ANTHROPIC_API_KEY in .env")

    client = anthropic.Anthropic(api_key=api_key)

    print(f"Asking Claude to annotate {len(shots)} shots with music categories...")
    prompt = PROMPT_TEMPLATE.format(shots_json=shots_json, n_shots=len(shots))

    raw_parts = []
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            raw_parts.append(text)
    raw = "".join(raw_parts).strip()

    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        annotations = json.loads(raw)
    except json.JSONDecodeError as e:
        print("ERROR: Claude returned non-JSON output. First 500 chars:")
        print(raw[:500])
        raise SystemExit(f"JSON decode failed: {e}")

    if len(annotations) != len(shots):
        raise SystemExit(
            f"Annotation count mismatch: got {len(annotations)} for {len(shots)} shots"
        )

    # Build a quick lookup by index
    by_index = {a["index"]: a["music_category"] for a in annotations}

    # Validate vocabulary
    valid_cats = {"opening-portent", "exposition-restrained", "rising-stakes",
                  "climactic-stillness", "aftermath-reflection"}
    for idx, cat in by_index.items():
        if cat not in valid_cats:
            raise SystemExit(f"Shot {idx} got invalid category '{cat}'. "
                             f"Valid: {sorted(valid_cats)}")

    # Backup and write
    bak_path = storyboard_path.with_suffix(".json.bak")
    bak_path.write_text(storyboard_path.read_text())
    print(f"Backed up original to {bak_path.name}")

    for s in shots:
        s["music_category"] = by_index[s["index"]]

    storyboard_path.write_text(json.dumps(shots, indent=2))
    print(f"OK Wrote music_category for {len(shots)} shots -> {storyboard_path.name}")

    # Summary
    from collections import Counter
    counts = Counter(s["music_category"] for s in shots)
    print("\nCategory distribution:")
    for cat, n in counts.most_common():
        print(f"  {cat}: {n} shots")

    # Show region structure
    print("\nRegion structure (consecutive same-category groups):")
    regions = []
    cur = {"cat": shots[0]["music_category"], "start_idx": shots[0]["index"], "end_idx": shots[0]["index"]}
    for s in shots[1:]:
        if s["music_category"] == cur["cat"]:
            cur["end_idx"] = s["index"]
        else:
            regions.append(cur)
            cur = {"cat": s["music_category"], "start_idx": s["index"], "end_idx": s["index"]}
    regions.append(cur)
    for i, r in enumerate(regions, 1):
        print(f"  [{i}] {r['cat']:25s}  shots {r['start_idx']}-{r['end_idx']}")
    print(f"\nTotal: {len(regions)} regions")


def main():
    ap = argparse.ArgumentParser(description="Annotate existing storyboard with music_category")
    ap.add_argument("--project", required=True,
                    help="Project path (e.g. projects/mary_celeste)")
    args = ap.parse_args()
    annotate(args.project)


if __name__ == "__main__":
    main()
