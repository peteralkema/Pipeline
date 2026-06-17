"""
select_thumbnail_still.py — generate N thumbnail candidates, let Sonnet pick the best
=====================================================================================
The thumbnail is the single highest-leverage asset on the channel (it decides the
click), so it's the one place a selection pass is worth the spend. This runs 100%
unattended:

  1. Render N dedicated thumbnail-composition stills with fal Flux-pro (default 2).
     These are composed FOR a thumbnail (catastrophe fills frame, tiny silhouette
     low, reserved negative space where the headline lands) — not reused video beats.
  2. Ask Claude (Sonnet) to judge them on the CTR job a thumbnail must do, BEFORE
     any text is added, so it judges the substrate (incl. where the text will go).
  3. Copy the winner to <project>/thumbnail_still.png for make_thumbnail.py to use.
  4. Log the verdict + reason to <project>/thumbnail_selection.json.

Design rules (banked):
  - N=2 captures most of the variance-reduction; do NOT creep to 5 (cost/latency, no gain).
  - The selection judges the THUMBNAIL JOB, not "which is prettier".
  - It runs on the BARE stills, before overlay, judging the negative space for text.
  - It NEVER halts the pipeline: any error in render-2 or in the vision call falls
    back to candidate 1 and proceeds. A selector that can block an unattended batch
    is worse than no selector.

Env:
    FAL_KEY               fal.ai key (Flux)
    ANTHROPIC_API_KEY     Anthropic key (Sonnet vision)
    THUMB_SELECT_MODEL    optional; defaults below. Set to whatever your hooks/titles
                          step already uses so the whole pipeline is on one model string.

Usage (standalone test):
    python3 select_thumbnail_still.py \
        --project projects/toba_ep01/modea \
        --channel prehistoric-disasters \
        --subject "a towering wall of volcanic ash blotting out the sun over a dead grey plain, one tiny lone human silhouette standing on a low ridge far below, dwarfed"

Requirements:
    pip install fal-client anthropic requests
"""

import argparse
import base64
import json
import os
import shutil
import sys
from pathlib import Path

import requests

FLUX_MODEL = "fal-ai/flux-pro/v1.1"
DEFAULT_VISION_MODEL = os.environ.get("THUMB_SELECT_MODEL", "claude-sonnet-4-6")

# Fallback rules if the channel.json thumbnail block doesn't carry its own.
DEFAULT_SELECTION_RULES = [
    "ONE clear, instantly legible subject that reads at phone-thumbnail size",
    "strong dark, high-contrast, dramatic composition (a thumbnail competes in a dim feed)",
    "an unmistakable focal point with real depth/scale — not flat or muddy",
    "clean, uncluttered negative space in the headline region (see below) so big text will sit cleanly on top",
    "no garbled detail, no accidental text/letterforms, no duplicated or broken subjects",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _find_channel_json(project: Path, channel: str | None) -> Path | None:
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


def _load_channel(project: Path, channel: str | None) -> dict:
    cj = _find_channel_json(project, channel)
    if not cj:
        print("   (no channel.json found — using bare defaults)")
        return {}
    try:
        data = json.loads(cj.read_text())
        print(f"   channel config <- {cj}")
        return data
    except (OSError, json.JSONDecodeError) as e:
        print(f"   (could not read {cj}: {e})")
        return {}


def _text_region_description(thumb_cfg: dict) -> str:
    """Plain-English description of where the headline will be placed, for the judge."""
    anchor = thumb_cfg.get("text_anchor", "top-center")
    pct = int(float(thumb_cfg.get("title_area_pct", 0.9)) * 100)
    where = {
        "top-left": "the TOP-LEFT region",
        "top-right": "the TOP-RIGHT region",
        "top-center": "the TOP band, centred",
    }.get(anchor, "the TOP band")
    return (f"A large headline (a few heavy words) will be placed over {where}, "
            f"spanning roughly {pct}% of the width. Penalise any candidate whose "
            f"main subject, bright areas, or busy detail fall in that region — the "
            f"text needs clean, darker negative space there.")


def _build_prompt(channel_cfg: dict, subject: str) -> str:
    """Flux prompt = subject + channel style_suffix + the channel's thumbnail composition suffix."""
    style = channel_cfg.get("style_suffix", "").strip()
    thumb = channel_cfg.get("thumbnail", {}) or {}
    suffix = thumb.get("candidate_prompt_suffix", "").strip()
    parts = [p for p in (subject.strip(), suffix, style) if p]
    return ", ".join(parts)


def generate_candidates(prompt: str, n: int, out_dir: Path) -> list[Path]:
    """Render N candidates with Flux-pro. Returns the paths that succeeded (>=1 or raises)."""
    import fal_client  # imported here so the file loads even if fal isn't installed yet

    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i in range(1, n + 1):
        try:
            result = fal_client.subscribe(
                FLUX_MODEL,
                arguments={
                    "prompt": prompt,
                    "image_size": "landscape_16_9",
                    "num_images": 1,
                    "safety_tolerance": "5",   # REQUIRED — else silent ~7KB black PNG on reject
                    "output_format": "png",
                },
            )
            url = result["images"][0]["url"]
            data = requests.get(url, timeout=120).content
            p = out_dir / f"candidate_{i}.png"
            p.write_bytes(data)
            paths.append(p)
            print(f"   candidate {i} -> {p} ({len(data)//1024} KB)")
        except Exception as e:   # one bad render must not kill the set
            print(f"   candidate {i} FAILED: {e}")
    if not paths:
        raise SystemExit("All thumbnail candidates failed to render.")
    return paths


def _img_block(path: Path) -> dict:
    b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
    return {"type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": b64}}


def select_best(candidates: list[Path], rules: list[str], text_region: str,
                model: str) -> tuple[int, str]:
    """
    Sonnet vision verdict. Returns (winner_index_1based, reason).
    Fail-safe: any error or unparseable response -> (1, "fallback: <why>").
    """
    if len(candidates) == 1:
        return 1, "only one candidate rendered"

    try:
        import anthropic
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

        rules_txt = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(rules))
        instructions = (
            "You are a YouTube thumbnail art director. You are NOT judging which image "
            "is the prettiest or most artistic — you are judging which works harder as a "
            "THUMBNAIL: which will earn more clicks in a small, dim, crowded feed, mostly "
            "on phones.\n\n"
            f"Judge ONLY on these criteria:\n{rules_txt}\n\n"
            f"{text_region}\n\n"
            "Both images are the BARE background — the headline text is NOT added yet, so "
            "judge the empty space where it will go.\n\n"
            "Reply with STRICT JSON only, no prose, no markdown fences:\n"
            '{\"winner\": <1 or 2>, \"reason\": \"<one sentence, thumbnail-CTR specific>\"}'
        )

        content = [{"type": "text", "text": instructions}]
        for i, path in enumerate(candidates[:2], start=1):
            content.append({"type": "text", "text": f"Candidate {i}:"})
            content.append(_img_block(path))

        resp = client.messages.create(
            model=model,
            max_tokens=300,
            messages=[{"role": "user", "content": content}],
        )
        raw = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        verdict = json.loads(clean)
        winner = int(verdict.get("winner", 1))
        if winner not in (1, 2):
            return 1, f"fallback: winner out of range ({winner})"
        return winner, str(verdict.get("reason", "")).strip() or "no reason given"
    except Exception as e:
        return 1, f"fallback: {type(e).__name__}: {e}"


def main():
    ap = argparse.ArgumentParser(description="Generate + auto-select a thumbnail still")
    ap.add_argument("--project", required=True, help="project folder")
    ap.add_argument("--channel", default=None, help="channel dir name or channel.json path")
    ap.add_argument("--subject", required=True,
                    help="what this video's thumbnail depicts (the per-video catastrophe)")
    ap.add_argument("--candidates", type=int, default=None,
                    help="override candidate count (default: channel thumbnail.candidates or 2)")
    ap.add_argument("--model", default=DEFAULT_VISION_MODEL, help="vision model string")
    args = ap.parse_args()

    project = Path(args.project).expanduser()
    channel_cfg = _load_channel(project, args.channel)
    thumb_cfg = channel_cfg.get("thumbnail", {}) or {}

    n = args.candidates or int(thumb_cfg.get("candidates", 2))
    rules = thumb_cfg.get("selection_rules") or DEFAULT_SELECTION_RULES
    text_region = _text_region_description(thumb_cfg)
    prompt = _build_prompt(channel_cfg, args.subject)
    print(f"   flux prompt: {prompt[:140]}{'...' if len(prompt) > 140 else ''}")

    cand_dir = project / "thumb_candidates"
    candidates = generate_candidates(prompt, n, cand_dir)

    winner, reason = select_best(candidates, rules, text_region, args.model)
    print(f"   WINNER: candidate {winner} — {reason}")

    chosen = candidates[winner - 1]
    dest = project / "thumbnail_still.png"
    shutil.copyfile(chosen, dest)

    (project / "thumbnail_selection.json").write_text(json.dumps({
        "winner": winner,
        "reason": reason,
        "model": args.model,
        "candidate_count": len(candidates),
        "subject": args.subject,
        "prompt": prompt,
        "chosen_file": chosen.name,
    }, indent=2))
    print(f"OK thumbnail_still.png <- {chosen.name}  (verdict logged)")
    return dest


if __name__ == "__main__":
    main()
