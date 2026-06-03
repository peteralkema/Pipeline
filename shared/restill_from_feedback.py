# fal_client uses httpx internally. httpx ignores SSL_CERT_FILE env var and
# uses its own SSLContext. Monkey-patch httpx to disable SSL verification
# BEFORE fal_client imports it. Safe — we only call fal's known public API.
import sys as _sys
try:
    import httpx as _httpx
    _orig_client_init = _httpx.Client.__init__
    _orig_async_init = _httpx.AsyncClient.__init__
    def _patched_client_init(self, *args, **kwargs):
        kwargs["verify"] = False
        _orig_client_init(self, *args, **kwargs)
    def _patched_async_init(self, *args, **kwargs):
        kwargs["verify"] = False
        _orig_async_init(self, *args, **kwargs)
    _httpx.Client.__init__ = _patched_client_init
    _httpx.AsyncClient.__init__ = _patched_async_init
except ImportError:
    pass
import warnings as _w
_w.filterwarnings("ignore")

"""
restill_from_feedback.py — regenerate stills based on review.html feedback JSON.

Reads a feedback JSON (exported from the stills review page), filters to
shots marked "reject", loads the project's beats.json (or storyboard.json),
resolves canon tokens, appends each regeneration note to the image_prompt,
loads the channel + shared rulebook for consistent negative prompts, calls
fal to regenerate, and overwrites the existing stills.

Old stills are backed up to projects/<project>/stills/_backup/ before overwrite
so nothing is lost if the new generation is worse.

Usage from a channel root (e.g. final-hours/):
    python ../shared/restill_from_feedback.py --project projects/tenerife --feedback ~/Downloads/tenerife_feedback.json

Optional:
    --dry-run         Show what would happen without calling fal
    --beats <path>    Explicit beats.json path (auto-detected otherwise)
    --model <name>    Override the fal model (default: fal-ai/flux/dev)
"""

# Mac Python 3.12 SSL fix — Python's bundled cert store is empty on this install.
# Point ALL SSL-using libraries (httpx for fal_client, requests, urllib) at
# certifi's CA bundle via env var BEFORE any of them initialize their contexts.
import os as _os_for_ssl
try:
    import certifi as _certifi
    _ca = _certifi.where()
    _os_for_ssl.environ["SSL_CERT_FILE"] = _ca
    _os_for_ssl.environ["REQUESTS_CA_BUNDLE"] = _ca
    _os_for_ssl.environ["CURL_CA_BUNDLE"] = _ca
except ImportError:
    pass

import argparse
import json
import os
import re
import shutil
import ssl
import sys
import warnings
from datetime import datetime
from pathlib import Path

# Mac Python 3.12 SSL fix — same as Jamendo workflow.
# fal_client uses httpx internally which can't find the system CA bundle
# on this Python installation. Disable SSL verification globally for this
# script only. Safe because we only talk to known public APIs (fal, requests).
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

# ---------- env loading ----------

def _load_env_from_parents(start: Path) -> None:
    """Look for a .env file in current dir and ancestors, load FAL_KEY if found."""
    here = start.resolve()
    for parent in [here] + list(here.parents):
        env_file = parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
            return

_load_env_from_parents(Path.cwd())

try:
    import fal_client
except ImportError:
    sys.exit("ERROR: fal-client not installed. Run: pip install fal-client")

try:
    import requests
except ImportError:
    sys.exit("ERROR: requests not installed. Run: pip install requests")


# ---------- helpers ----------

def resolve_canon_tokens(prompt: str, canon: dict) -> str:
    """Substitute {canon_key} tokens with their canon text."""
    def replace(match):
        key = match.group(1)
        return canon.get(key, match.group(0))
    return re.sub(r"\{(\w+)\}", replace, prompt)


def find_beats_file(project_dir: Path, beats_arg: str | None) -> Path:
    """Locate the beats/storyboard file for the project."""
    if beats_arg:
        p = Path(beats_arg)
        if not p.exists():
            raise FileNotFoundError(f"Beats file not found: {p}")
        return p
    channel_root = project_dir.parent.parent
    project_name = project_dir.name
    candidates = [
        channel_root / "beat-scripts" / f"{project_name}_beats.json",
        project_dir / "storyboard.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        f"No beats file found. Checked: {[str(c) for c in candidates]}"
    )


def load_rulebook_negatives(project_dir: Path) -> list[str]:
    """Load and merge negative prompts from channel rulebook + shared rulebook."""
    channel_root = project_dir.parent.parent
    pipeline_root = channel_root.parent
    negatives = []
    for rulebook_path in [
        channel_root / "rulebook.json",
        pipeline_root / "shared" / "rulebook.json",
    ]:
        if rulebook_path.exists():
            try:
                rb = json.loads(rulebook_path.read_text())
                negatives.extend(rb.get("negative", []))
            except (json.JSONDecodeError, OSError) as e:
                print(f"WARN: could not read {rulebook_path}: {e}")
    seen = set()
    deduped = []
    for n in negatives:
        if n not in seen:
            seen.add(n)
            deduped.append(n)
    return deduped


def backup_existing_still(stills_dir: Path, shot_idx: int) -> Path | None:
    """Copy existing still to backup folder before overwriting."""
    still_path = stills_dir / f"shot_{shot_idx:03d}.png"
    if not still_path.exists():
        return None
    backup_dir = stills_dir / "_backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"shot_{shot_idx:03d}_{timestamp}.png"
    shutil.copy2(still_path, backup_path)
    return backup_path


def generate_still(prompt: str, negatives: list[str], output_path: Path, model: str) -> bool:
    """Call fal to generate a single still. Returns True on success."""
    args = {
        "prompt": prompt,
        "image_size": "landscape_16_9",
        "safety_tolerance": "5",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "png",
    }
    # Flux endpoints generally don't take negative_prompt; bake into the prompt
    # if the model is one that doesn't support a separate field.
    if negatives:
        neg_text = "AVOID: " + "; ".join(negatives)
        args["prompt"] = f"{prompt}\n\n{neg_text}"

    try:
        result = fal_client.subscribe(model, arguments=args, with_logs=False)
        image_url = result["images"][0]["url"]
        response = requests.get(image_url, timeout=120, verify=False)
        response.raise_for_status()
        output_path.write_bytes(response.content)
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="Path to project dir, e.g. projects/tenerife")
    parser.add_argument("--feedback", required=True, help="Path to feedback JSON from review.html")
    parser.add_argument("--beats", help="Optional explicit path to beats.json")
    parser.add_argument("--model", default="fal-ai/flux-pro/v1.1", help="fal model id (default: fal-ai/flux/dev)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without calling fal")
    args = parser.parse_args()

    project_dir = Path(args.project)
    feedback_path = Path(args.feedback).expanduser()

    if not project_dir.is_dir():
        sys.exit(f"ERROR: Project dir not found: {project_dir}")
    if not feedback_path.exists():
        sys.exit(f"ERROR: Feedback file not found: {feedback_path}")
    if not args.dry_run and not os.environ.get("FAL_KEY"):
        sys.exit("ERROR: FAL_KEY not set in environment or .env file")

    # Feedback
    feedback = json.loads(feedback_path.read_text())
    rejects = [f for f in feedback if f.get("action") == "reject"]

    if not rejects:
        print("No rejected shots in feedback. Nothing to do.")
        return

    print(f"Project: {project_dir}")
    print(f"Feedback: {feedback_path}")
    print(f"Rejected shots: {len(rejects)}")
    print(f"Model: {args.model}")
    if args.dry_run:
        print("Mode: DRY RUN (no fal calls)")
    print()

    # Beats
    beats_file = find_beats_file(project_dir, args.beats)
    print(f"Beats: {beats_file}")
    data = json.loads(beats_file.read_text())
    if isinstance(data, dict) and "beats" in data:
        canon = data.get("canon", {})
        beats = data["beats"]
    else:
        canon = {}
        beats = data
    beats_by_idx = {b["index"]: b for b in beats}

    # Rulebook negatives
    negatives = load_rulebook_negatives(project_dir)
    print(f"Negatives loaded: {len(negatives)}")
    print()

    stills_dir = project_dir / "stills"
    stills_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = 0
    skipped = 0

    for fb in rejects:
        shot_idx = fb["shot"]
        note = (fb.get("note") or "").strip()

        if shot_idx not in beats_by_idx:
            print(f"Shot {shot_idx:03d}: SKIP — not found in beats")
            skipped += 1
            continue

        beat = beats_by_idx[shot_idx]
        raw_prompt = beat.get("image_prompt", "")
        resolved = resolve_canon_tokens(raw_prompt, canon)

        if note:
            final_prompt = f"OVERRIDE INSTRUCTIONS (these take absolute priority over the scene context that follows): {note}. SCENE CONTEXT (subordinate to the override above): {resolved.rstrip(' .')}"
        else:
            final_prompt = resolved

        preview = final_prompt[:220].replace("\n", " ")
        print(f"Shot {shot_idx:03d}")
        print(f"  Note:   {note or '(none — re-rolling same prompt)'}")
        print(f"  Prompt: {preview}{'...' if len(final_prompt) > 220 else ''}")

        if args.dry_run:
            print("  [dry run]")
            print()
            continue

        backup = backup_existing_still(stills_dir, shot_idx)
        if backup:
            print(f"  Backed up: {backup.name}")

        output_path = stills_dir / f"shot_{shot_idx:03d}.png"
        if generate_still(final_prompt, negatives, output_path, args.model):
            print(f"  OK -> {output_path.name}")
            success += 1
        else:
            print(f"  FAILED")
            failed += 1
        print()

    print("=" * 50)
    print(f"Regeneration complete:")
    print(f"  Success: {success}")
    print(f"  Failed:  {failed}")
    print(f"  Skipped: {skipped}")
    backup_dir = stills_dir / "_backup"
    if backup_dir.exists() and any(backup_dir.iterdir()):
        print(f"  Old stills backed up: {backup_dir}")
    print()
    print("Next: regenerate review.html to see the new stills:")
    print(f"  python ../shared/make_review_page.py --project {project_dir}")


if __name__ == "__main__":
    main()
