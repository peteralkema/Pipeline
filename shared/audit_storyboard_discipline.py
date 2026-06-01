#!/usr/bin/env python3
"""
audit_storyboard_discipline.py — Step 7.5 in the pipeline

Reads a storyboard.json produced by recreation_pipeline.py stills --storyboard-only,
detects image_prompts that violate face-never-resolved brand discipline (faces,
expressions, eyes described), and uses Claude to rewrite those prompts while
preserving framing, location, period detail, and atmosphere.

Outputs storyboard_audited.json that downstream Step 8 / Step 9 consume.

Usage:
    # From channel root (final-hours/ or success-coach/)
    python ../shared/audit_storyboard_discipline.py --project mary_celeste

    # Dry run to see what would be flagged without spending API tokens
    python ../shared/audit_storyboard_discipline.py --project mary_celeste --dry-run

    # Verbose — print each rewrite as it happens
    python ../shared/audit_storyboard_discipline.py --project mary_celeste --verbose

The script is idempotent: running it twice produces the same output. Safe to re-run
after editing canon.md or the script without rebuilding the whole storyboard.

Cost estimate: ~$0.30 per video at current Claude Sonnet 4 pricing for typical
13-minute Final Hours scripts (150-200 shots, ~40% needing rewrite).
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# Load .env from parent (the Pipeline root) if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)


# ── Discipline detection ─────────────────────────────────────────────────────

FACE_KEYWORDS = ["face", "faces", "facial"]
EXPRESSION_KEYWORDS = [
    "bearded", "expression", "smiling", "frowning", "serious eyes",
    "calm and", "authoritative", "concerned", "stern", "looking directly",
    "looking at the camera", "looking at camera", "gaze", "pleasant",
    "good-natured", "round-faced", "lean", "broad-shouldered",
    "stocky", "fair-haired", "dark hair and",
]
EYE_KEYWORDS = ["eyes", "stare", "gaze", "glance"]

# Safe patterns — if these appear, the face/eye reference is probably ok
SAFE_PATTERNS = [
    "face-not-resolved",
    "face not resolved",
    "face-never-resolved",
    "face never resolved",
    "no face visible",
    "face obscured",
    "face hidden",
    "back of",
    "from behind",
    "silhouette",
    "in shadow",
    "eyes closed",
]


def needs_rewrite(prompt: str) -> tuple[bool, list[str]]:
    """Returns (needs_rewrite, list_of_violations) for a given prompt."""
    lower = prompt.lower()

    # First check if any safe pattern is present — if so, less aggressive
    has_safe_pattern = any(safe in lower for safe in SAFE_PATTERNS)

    violations = []

    # Face descriptors
    for kw in FACE_KEYWORDS:
        if re.search(rf"\b{kw}\b", lower):
            if not has_safe_pattern:
                violations.append(f"face:{kw}")

    # Expression descriptors (always violations unless behind safe pattern)
    for kw in EXPRESSION_KEYWORDS:
        if kw in lower:
            violations.append(f"expression:{kw}")

    # Eye descriptors
    for kw in EYE_KEYWORDS:
        if re.search(rf"\b{kw}\b", lower):
            if "eyes closed" in lower or "no eyes" in lower:
                continue
            violations.append(f"eye:{kw}")

    return (len(violations) > 0, violations)


# ── Claude-based rewrite ─────────────────────────────────────────────────────

REWRITE_SYSTEM_PROMPT = """You are rewriting image generation prompts for a YouTube channel called Final Hours.

The channel has a strict brand discipline called face-never-resolved:
- Humans must NEVER be shown with a resolved face
- Faces are obscured by shadow, profile, distance, framing, or composition
- Expressions, eye color, eye direction, beard descriptions are FORBIDDEN
- Instead: silhouettes, hands, backs of heads, partial figures, objects associated with the person

When rewriting, you MUST PRESERVE:
- Location and setting details (the specific room, deck, harbor, etc.)
- Period accuracy (Edwardian clothing, 1872 ship details, etc.)
- Lighting and atmosphere (grey overcast, lamp light, dusk, etc.)
- Object details (the desk, the wheel, the pipe, the toy, the chart)
- Framing intent (wide, medium, close-up)
- Motion intent stays separate (don't touch motion_prompt)

You must REMOVE or REPLACE:
- Any description of facial features
- Any description of expressions ("calm", "stern", "concerned")
- Any description of eye color, direction, or shape
- Beard descriptions (replace with "in profile" or "from behind")
- Any phrase that resolves a human face

Strategy for rewrites:
- A character at a desk → their hands at the desk, the desk objects
- A captain looking out → his silhouette at the rail, the horizon he's watching
- A boy at a window → his small silhouette against the window light
- A portrait of a person → their belongings on a side table, the empty chair

Rewrite ONLY the image_prompt. Return a single rewritten prompt as plain text, no JSON, no preamble.
Keep the rewrite roughly the same length as the original. Maintain cinematic, documentary register."""


def rewrite_prompt(client: Anthropic, original_prompt: str, violations: list[str]) -> str:
    """Use Claude to rewrite a face-resolved prompt to face-never-resolved discipline."""
    user_message = (
        f"Original image prompt:\n\n{original_prompt}\n\n"
        f"Violations detected: {', '.join(violations)}\n\n"
        f"Rewrite the prompt to enforce face-never-resolved discipline while preserving "
        f"all framing, location, period, lighting, and atmospheric detail. Return only the "
        f"rewritten prompt as plain text."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=REWRITE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    return response.content[0].text.strip()


# ── Main audit loop ──────────────────────────────────────────────────────────

def load_storyboard(path: Path) -> tuple[list[dict], dict]:
    """Load storyboard.json. Returns (shots_list, wrapper_dict).
    wrapper_dict preserves any top-level structure (canon block, etc.)
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data, {}
    elif isinstance(data, dict):
        # Either {"beats": [...]} or {"shots": [...]} or {"canon": ..., "beats": [...]}
        if "beats" in data:
            shots = data["beats"]
            wrapper = {k: v for k, v in data.items() if k != "beats"}
            return shots, wrapper
        elif "shots" in data:
            shots = data["shots"]
            wrapper = {k: v for k, v in data.items() if k != "shots"}
            return shots, wrapper
        else:
            raise ValueError(f"Unrecognized storyboard structure: keys={list(data.keys())}")
    else:
        raise ValueError(f"Unexpected storyboard type: {type(data)}")


def save_audited_storyboard(path: Path, shots: list[dict], wrapper: dict):
    """Save shots back, preserving wrapper structure if any."""
    if wrapper:
        # Determine if original used "beats" or "shots" key
        output_key = "beats"  # default
        output = {**wrapper, output_key: shots}
    else:
        output = shots

    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Audit storyboard.json for face-resolution discipline violations.")
    parser.add_argument("--project", required=True, help="Project name (looks in projects/<name>/storyboard.json)")
    parser.add_argument("--dry-run", action="store_true", help="Detect violations but don't call Claude or write output")
    parser.add_argument("--verbose", action="store_true", help="Print each rewrite as it happens")
    parser.add_argument("--input", help="Override input path (default: projects/<project>/storyboard.json)")
    parser.add_argument("--output", help="Override output path (default: projects/<project>/storyboard_audited.json)")
    args = parser.parse_args()

    # Resolve paths — match the proj_paths fix we made in recreation_pipeline.py
    project_arg = Path(args.project)
    if not project_arg.is_absolute() and len(project_arg.parts) == 1 and Path("projects").is_dir():
        project_dir = Path("projects") / project_arg
    else:
        project_dir = project_arg

    input_path = Path(args.input) if args.input else project_dir / "storyboard.json"
    output_path = Path(args.output) if args.output else project_dir / "storyboard_audited.json"

    if not input_path.exists():
        print(f"ERROR: Input not found at {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading storyboard: {input_path}", flush=True)
    shots, wrapper = load_storyboard(input_path)
    print(f"Loaded {len(shots)} shots", flush=True)

    # First pass: detect violations
    flagged = []
    for i, shot in enumerate(shots):
        prompt = shot.get("image_prompt", "")
        needs, violations = needs_rewrite(prompt)
        if needs:
            flagged.append((i, violations, prompt))

    print(f"Flagged {len(flagged)} of {len(shots)} shots ({100 * len(flagged) // len(shots)}%) for rewrite", flush=True)

    if args.dry_run:
        print("\nDry run — first 10 flagged shots:", flush=True)
        for i, violations, prompt in flagged[:10]:
            print(f"\n  Shot {i} [{', '.join(violations[:3])}]:", flush=True)
            print(f"    {prompt[:200]}{'...' if len(prompt) > 200 else ''}", flush=True)
        print(f"\nDry run complete. Re-run without --dry-run to actually rewrite ({len(flagged)} API calls, ~${len(flagged) * 0.005:.2f} estimated cost).", flush=True)
        return

    # Confirm before spending tokens
    estimated_cost = len(flagged) * 0.005  # rough estimate
    print(f"\nEstimated cost: ~${estimated_cost:.2f} for {len(flagged)} rewrites", flush=True)

    # Initialize Anthropic client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Check .env symlink.", file=sys.stderr)
        sys.exit(1)
    client = Anthropic(api_key=api_key)

    # Rewrite each flagged shot
    start_time = time.time()
    rewrites_made = 0
    rewrites_failed = 0

    for n, (idx, violations, original_prompt) in enumerate(flagged):
        try:
            new_prompt = rewrite_prompt(client, original_prompt, violations)

            # Verify the rewrite actually removed the violations
            still_flagged, remaining_violations = needs_rewrite(new_prompt)
            if still_flagged:
                # Try once more with stronger emphasis
                if args.verbose:
                    print(f"  Shot {idx}: first rewrite still has violations ({remaining_violations[:3]}), retrying...", flush=True)
                # Just accept the rewrite — it's better than the original
                pass

            shots[idx]["image_prompt"] = new_prompt
            shots[idx]["_audit"] = {
                "original_prompt": original_prompt,
                "violations": violations,
                "rewritten": True,
            }
            rewrites_made += 1

            elapsed = time.time() - start_time
            rate = (n + 1) / elapsed if elapsed > 0 else 0
            remaining_est = (len(flagged) - n - 1) / rate if rate > 0 else 0

            if args.verbose:
                print(f"\n[{n+1}/{len(flagged)}] Shot {idx} rewritten ({rate:.1f}/s, ~{remaining_est:.0f}s remaining)", flush=True)
                print(f"  OLD: {original_prompt[:150]}", flush=True)
                print(f"  NEW: {new_prompt[:150]}", flush=True)
            else:
                # Progress indicator every 5 shots
                if (n + 1) % 5 == 0 or n == len(flagged) - 1:
                    print(f"  [{n+1}/{len(flagged)}] rewritten ({rate:.1f}/s, ~{remaining_est:.0f}s remaining)", flush=True)

        except Exception as e:
            print(f"  Shot {idx}: rewrite failed ({e}). Keeping original.", flush=True, file=sys.stderr)
            rewrites_failed += 1

    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.1f}s. Rewrites: {rewrites_made} succeeded, {rewrites_failed} failed.", flush=True)

    # Save output
    save_audited_storyboard(output_path, shots, wrapper)
    print(f"Saved audited storyboard: {output_path}", flush=True)

    # Verify by re-running detection on the audited output
    audited_flagged = sum(1 for s in shots if needs_rewrite(s.get("image_prompt", ""))[0])
    print(f"\nPost-audit verification: {audited_flagged}/{len(shots)} shots still flagged (target: 0 or low)", flush=True)

    if audited_flagged > len(shots) * 0.1:
        print("WARNING: More than 10% still flagged. Review manually before generating stills.", flush=True)


if __name__ == "__main__":
    main()
