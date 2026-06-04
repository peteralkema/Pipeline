#!/usr/bin/env python3
"""
build_canon.py — bridge between the discipline-audited storyboard and the
canon-aware beats file the stills pipeline consumes.

Takes:
  - storyboard_audited.json  (flat list of shots, face-disciplined prompts)
  - canon.json               (dict: {token: scene/character description})

Produces:
  - beat-scripts/<project>_beats.json  ({"canon": {...}, "beats": [...]})
    with each shot's image_prompt prefixed by its assigned {token}.

Canon assignment uses Claude (not keyword matching). Keyword routing cannot tell
"a shot OF the bridge" from "narration that MENTIONS water" — that mis-routed the
Tay Bridge build (bridge shots landed in the firth canon because the prompt said
"seventy feet above the water"). Claude reads each shot's prompt and the canon
descriptions and picks the canon whose VISUAL SUBJECT the shot depicts.

The human still confirms the distribution (the orchestrator gates on it). Claude
gets it right far more often than keywords, so the gate is usually a confirm,
not a fix.

Usage (from channel root):
    python ../shared/build_canon.py --project tay_bridge --canon projects/tay_bridge/canon.json

    # explicit storyboard override (default is storyboard_audited.json, falling
    # back to storyboard.json if the audited one is absent):
    python ../shared/build_canon.py --project tay_bridge --canon projects/tay_bridge/canon.json \
        --storyboard projects/tay_bridge/storyboard_audited.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic not installed. pip install anthropic --break-system-packages", file=sys.stderr)
    sys.exit(1)

CLAUDE_MODEL = "claude-sonnet-4-6"


def resolve_project_dir(project_arg: str) -> Path:
    """Match the proj_paths convention: bare name -> projects/<name> from channel root."""
    p = Path(project_arg)
    if not p.is_absolute() and len(p.parts) == 1 and Path("projects").is_dir():
        return Path("projects") / p
    return p


def find_storyboard(project_dir: Path, override: str | None) -> Path:
    if override:
        return Path(override)
    audited = project_dir / "storyboard_audited.json"
    raw = project_dir / "storyboard.json"
    if audited.exists():
        return audited
    if raw.exists():
        print(f"WARNING: {audited.name} not found — using {raw.name}. "
              f"Face-discipline audit may not have run.", file=sys.stderr)
        return raw
    sys.exit(f"No storyboard found in {project_dir} (looked for storyboard_audited.json, storyboard.json)")


def load_shots(storyboard_path: Path) -> list:
    data = json.loads(storyboard_path.read_text())
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "beats" in data:
            return data["beats"]
        if "shots" in data:
            return data["shots"]
    sys.exit(f"Unrecognised storyboard structure in {storyboard_path}")


def assign_canons_with_claude(client: Anthropic, shots: list, canon: dict) -> dict:
    """
    Ask Claude to assign each shot to the canon whose VISUAL SUBJECT it depicts.
    Returns {shot_index (int): canon_token (str)}.
    Falls back to the first canon key for any shot Claude omits or mis-labels.
    """
    tokens = list(canon.keys())
    canon_desc = "\n".join(f'- "{k}": {v[:300]}' for k, v in canon.items())

    # Compact shot list: index + the image prompt (what's actually depicted).
    shot_lines = []
    for i, s in enumerate(shots):
        prompt = (s.get("image_prompt", "") or "")[:280]
        shot_lines.append(f"{i}: {prompt}")
    shots_block = "\n".join(shot_lines)

    system = (
        "You assign each storyboard shot to exactly one CANON scene. A canon is a "
        "locked visual setting. Assign each shot to the canon whose VISUAL SUBJECT the "
        "shot actually depicts — what the camera is looking at — NOT merely what the "
        "narration mentions. Example: a shot of a bridge described as 'seventy feet "
        "above the water' depicts the BRIDGE, not the water. Choose the single best-fit "
        "canon for every shot. You must use only the provided canon tokens."
    )
    user = (
        f"CANON SCENES (token: description):\n{canon_desc}\n\n"
        f"SHOTS (index: image prompt):\n{shots_block}\n\n"
        f"Return STRICT JSON only: an object mapping every shot index (as a string) to "
        f"one canon token from this list: {tokens}. No preamble, no markdown.\n"
        f'Example: {{"0": "{tokens[0]}", "1": "{tokens[0]}"}}'
    )

    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw[raw.find("{"):raw.rfind("}") + 1]
    mapping_raw = json.loads(raw)

    # Normalise to {int: valid_token}, fall back to first token on anything odd.
    fallback = tokens[0]
    assignment = {}
    for i in range(len(shots)):
        tok = mapping_raw.get(str(i), fallback)
        if tok not in canon:
            tok = fallback
        assignment[i] = tok
    return assignment


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--canon", required=True, help="path to canon.json ({token: description})")
    ap.add_argument("--storyboard", default=None, help="override storyboard path")
    ap.add_argument("--output", default=None, help="override output beats path")
    args = ap.parse_args()

    project_dir = resolve_project_dir(args.project)
    if not project_dir.is_dir():
        sys.exit(f"Project dir not found: {project_dir}")

    canon_path = Path(args.canon)
    if not canon_path.exists():
        sys.exit(f"Canon file not found: {canon_path}")
    canon = json.loads(canon_path.read_text())
    if not isinstance(canon, dict) or not canon:
        sys.exit(f"Canon file must be a non-empty JSON object of token->description: {canon_path}")

    storyboard_path = find_storyboard(project_dir, args.storyboard)
    shots = load_shots(storyboard_path)
    print(f"Loaded {len(shots)} shots from {storyboard_path.name}")
    print(f"Canon tokens: {list(canon.keys())}")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY not set (check .env).")
    client = Anthropic(api_key=api_key)

    print("Assigning shots to canon scenes (Claude reads visual subject)...")
    assignment = assign_canons_with_claude(client, shots, canon)

    # Build the beats: prepend {token} to each shot's image_prompt.
    beats, counts = [], {}
    for i, s in enumerate(shots):
        tok = assignment[i]
        counts[tok] = counts.get(tok, 0) + 1
        b = dict(s)
        # strip the internal audit metadata if present — keep the file clean
        b.pop("_audit", None)
        b["image_prompt"] = "{" + tok + "} " + (s.get("image_prompt", "") or "")
        beats.append(b)

    out = {"canon": canon, "beats": beats}

    # Default output: beat-scripts/<project>_beats.json from channel root.
    if args.output:
        out_path = Path(args.output)
    else:
        beat_dir = Path("beat-scripts")
        beat_dir.mkdir(exist_ok=True)
        out_path = beat_dir / f"{project_dir.name}_beats.json"
    out_path.write_text(json.dumps(out, indent=2))

    print(f"\nWrote {len(beats)} beats -> {out_path}")
    print("Canon distribution:")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {k:16s} {v}")
    print("\nReview the distribution. The dominant visual subject should dominate.")
    print("If a scene is over/under-represented, the shot's prompt may be mis-routed —")
    print("edit the {token} prefix in the beats file before generating stills.")


if __name__ == "__main__":
    main()
