"""
make_prop.py -- render ONE thumbnail prop object and knock out its background
=============================================================================
The thumbnail prop is the third slot of the QQrew thumbnail system (subject face +
headline + ONE hero prop in the negative space). The prop is what differentiates one
video from the next and deepens the curiosity gap -- chosen by the no-echo rule: the
object that raises a question the headline does NOT answer, never the one that
illustrates the title.

This script does ONE job: render a single clean flat-cel prop object with fal Flux-pro,
then rembg-knock-out its background to transparent, writing:

    <project>/thumbnail_prop.png      (RGBA, transparent background)

make_thumbnail.py composites that file into the configured corner if it exists.
No prop file => no prop layer => existing channels unchanged.

Design rules (banked):
  - ONE object, flat-cel, on a plain solid background (so rembg cuts clean).
  - Chosen by the no-echo rule (deepen the question, never illustrate the title).
  - Position + scale are CHANNEL constants (channel.json thumbnail.prop); the prop
    SUBJECT is per-video (--prop). Recognition from placement, variety from object.
  - Never halts a batch: any render/knockout failure exits non-zero with a clear
    message but writes no partial file, so the compositor simply runs prop-less.

Env:
    FAL_KEY               fal.ai key (Flux)

Usage:
    python3 make_prop.py \
        --project crew-wip/projects/iceage1 \
        --channel crew-wip \
        --prop "a single cracked open animal leg bone, split lengthwise, exposed marrow inside"

Requirements:
    pip install fal-client requests rembg pillow
"""

import argparse
import io
import json
import os
import sys
from pathlib import Path

import requests
from PIL import Image

FLUX_MODEL = "fal-ai/flux-pro/v1.1"

# Appended to every prop prompt so flux renders ONE clean knock-out-able object,
# not a scene. Solid plain background = clean rembg cut.
PROP_SUFFIX = (
    "rendered as one single clean flat cel-shaded illustrated object, "
    "centered on a plain solid flat background, thick confident dark linework, "
    "bold saturated flat color, smooth animated-feature style, sticker-like, "
    "no scene, no environment, no hands, no person, no text, no letters, "
    "NOT photorealistic, NOT 3d render"
)

PROP_NEGATIVE_HINT = "no scene, no background detail, no hands, no person, no text"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _find_channel_json(project: Path, channel):
    if channel:
        cand = Path(channel)
        if cand.is_file():
            return cand
        for base in (_repo_root(), Path.cwd()):
            cj = base / channel / "channel.json"
            if cj.exists():
                return cj
        if (cand / "channel.json").exists():
            return cand / "channel.json"
    p = project.resolve()
    for parent in [p, *p.parents]:
        cj = parent / "channel.json"
        if cj.exists():
            return cj
    return None


def _load_channel(project: Path, channel) -> dict:
    cj = _find_channel_json(project, channel)
    if not cj:
        print("   (no channel.json found -- using bare defaults)")
        return {}
    try:
        data = json.loads(cj.read_text())
        print("   channel config <- " + str(cj))
        return data
    except (OSError, json.JSONDecodeError) as e:
        print("   (could not read " + str(cj) + ": " + str(e) + ")")
        return {}


def _build_prompt(channel_cfg: dict, prop: str) -> str:
    """Prop prompt = prop subject + the prop suffix. Deliberately does NOT append the
    channel style_suffix's scene/background language -- the prop must stay a lone object."""
    return ", ".join(p for p in (prop.strip(), PROP_SUFFIX) if p)


def render_prop(prompt: str, out_dir: Path) -> Path:
    """Render one prop candidate with Flux-pro. Returns the raw render path or raises."""
    import fal_client

    out_dir.mkdir(parents=True, exist_ok=True)
    result = fal_client.subscribe(
        FLUX_MODEL,
        arguments={
            "prompt": prompt,
            "image_size": "square_hd",
            "num_images": 1,
            "safety_tolerance": "5",   # REQUIRED -- else silent ~7KB black PNG on reject
            "output_format": "png",
        },
    )
    url = result["images"][0]["url"]
    data = requests.get(url, timeout=120).content
    raw = out_dir / "prop_raw.png"
    raw.write_bytes(data)
    print("   prop render -> " + str(raw) + " (" + str(len(data) // 1024) + " KB)")
    return raw


def knockout(raw_path: Path, dest: Path) -> Path:
    """rembg background knockout -> transparent RGBA PNG at dest. Raises on failure."""
    try:
        from rembg import remove
    except ImportError:
        raise SystemExit(
            "rembg not installed -- cannot knock out prop background. "
            "pip install rembg   (then re-run). No prop file written; "
            "the thumbnail compositor will simply run prop-less."
        )
    src = Image.open(raw_path).convert("RGB")
    cut = remove(src)
    if not isinstance(cut, Image.Image):
        cut = Image.open(io.BytesIO(cut))
    cut = cut.convert("RGBA")
    dest.parent.mkdir(parents=True, exist_ok=True)
    cut.save(dest, "PNG")
    print("   knocked out -> " + str(dest))
    return dest


def main():
    ap = argparse.ArgumentParser(description="Render + knock out a thumbnail prop object")
    ap.add_argument("--project", required=True, help="project folder")
    ap.add_argument("--channel", default=None, help="channel dir name or channel.json path")
    ap.add_argument("--prop", required=True,
                    help="the ONE hero prop object (no-echo rule: deepen the question)")
    args = ap.parse_args()

    project = Path(args.project).expanduser()
    channel_cfg = _load_channel(project, args.channel)

    prompt = _build_prompt(channel_cfg, args.prop)
    print("   flux prop prompt: " + prompt[:140] + ("..." if len(prompt) > 140 else ""))

    cand_dir = project / "prop_candidates"
    raw = render_prop(prompt, cand_dir)

    dest = project / "thumbnail_prop.png"
    knockout(raw, dest)

    (project / "prop_selection.json").write_text(json.dumps({
        "prop": args.prop,
        "prompt": prompt,
        "raw_file": raw.name,
        "out_file": dest.name,
    }, indent=2))
    print("OK thumbnail_prop.png written -- make_thumbnail.py will composite it if prop layer is enabled.")
    return dest


if __name__ == "__main__":
    main()
