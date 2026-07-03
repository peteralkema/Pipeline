#!/usr/bin/env python3
"""
patch_animate_model.py — swap the animate default to Kling 2.5 Turbo Pro and
lift the endpoint into channel.json as "animate_model".

Anchor-verified, idempotent, backs up, py_compile-checks, restores on failure.
Run from repo root: python3 shared/patch_animate_model.py   (LAPTOP)

Three edits to shared/recreation_pipeline.py:
  1. VIDEO_ENDPOINT constant block -> DEFAULT_VIDEO_ENDPOINT (2.5 Turbo Pro,
     $0.07/s vs O3's $0.084/s) + _video_endpoint() resolver reading
     channel.json "animate_model" (absent key = default; old O3 string or a
     v3 endpoint are valid override values).
  2. VIDEO_ENDPOINT resolved right after ASPECT (same load_channel_config
     pattern, same import-time semantics).
  3. animate_still payload: strip generate_audio on v2.5-turbo (no audio in
     that model's schema); other endpoints unchanged.
  4. TIERED RENDER --plan cost print: $0.35/clip on 2.5T, $0.42 otherwise.
"""

import py_compile
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "recreation_pipeline.py"
BACKUP = HERE / "recreation_pipeline.py.pre_animate_model"

MARKER = "DEFAULT_VIDEO_ENDPOINT"

ANCHOR_1 = '''# O3 Standard: ~3x faster + cheaper than Pro. Good default for the channel.
# Uses image_url (NOT start_image_url — that's the v3 endpoints).
VIDEO_ENDPOINT = "fal-ai/kling-video/o3/standard/image-to-video"
'''

REPLACE_1 = '''# Animate model (fast layer, swappable). Default: Kling 2.5 Turbo Pro —
# $0.07/s ($0.35 per 5s clip) vs O3 Standard's $0.084/s ($0.42), newer motion.
# Per-channel override: channel.json "animate_model" = full fal endpoint, e.g.
#   "fal-ai/kling-video/o3/standard/image-to-video"   (the old default)
#   "fal-ai/kling-video/v3/pro/image-to-video"        (hero-shot trials)
# Uses image_url (NOT start_image_url — that's the v3 endpoints).
DEFAULT_VIDEO_ENDPOINT = "fal-ai/kling-video/v2.5-turbo/pro/image-to-video"

def _video_endpoint():
    """Resolve the animate endpoint: channel.json animate_model, else default."""
    try:
        cfg = load_channel_config(strict=False)
        ep = str(cfg.get("animate_model", "") or "").strip()
        return ep or DEFAULT_VIDEO_ENDPOINT
    except Exception:
        return DEFAULT_VIDEO_ENDPOINT
'''

ANCHOR_2 = "ASPECT = _channel_aspect()   # 16:9; per-channel via channel.json width/height"

REPLACE_2 = (
    "ASPECT = _channel_aspect()   # 16:9; per-channel via channel.json width/height\n"
    "VIDEO_ENDPOINT = _video_endpoint()  # animate model, resolved like ASPECT"
)

ANCHOR_3 = '''        result = fal_client.subscribe(
            VIDEO_ENDPOINT,
            arguments={
                "image_url": image_url,
                "prompt": motion_prompt,
                "duration": SHOT_DURATION,
                "generate_audio": False,
            },
'''

REPLACE_3 = '''        _args = {
            "image_url": image_url,
            "prompt": motion_prompt,
            "duration": SHOT_DURATION,
        }
        if "v2.5-turbo" not in VIDEO_ENDPOINT:
            # 2.5 Turbo Pro has no audio track — the flag isn't in its schema.
            _args["generate_audio"] = False
        result = fal_client.subscribe(
            VIDEO_ENDPOINT,
            arguments=_args,
'''

ANCHOR_4 = '''    print(f"TIERED RENDER: N={kling_count}  ->  {n_kling} Kling (~${n_kling * 0.42:.2f}) "
'''

REPLACE_4 = '''    _clip_cost = 0.35 if "v2.5-turbo" in VIDEO_ENDPOINT else 0.42
    print(f"TIERED RENDER: N={kling_count}  ->  {n_kling} Kling (~${n_kling * _clip_cost:.2f}) "
'''


def die(msg: str) -> None:
    print(f"ABORT: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not TARGET.is_file():
        die(f"{TARGET} not found — run from the repo (patch lives in shared/).")

    source = TARGET.read_text(encoding="utf-8")

    if MARKER in source:
        print("Already applied — no-op.")
        return

    for name, anchor in (("ANCHOR_1 (endpoint block)", ANCHOR_1),
                         ("ANCHOR_2 (ASPECT line)", ANCHOR_2),
                         ("ANCHOR_3 (animate payload)", ANCHOR_3),
                         ("ANCHOR_4 (plan cost print)", ANCHOR_4)):
        n = source.count(anchor)
        if n != 1:
            die(f"{name} found {n} times (need exactly 1) — recreation_pipeline.py "
                "has drifted from what this patch was written against. Re-grep "
                "and re-anchor before applying. Nothing written.")

    shutil.copy2(TARGET, BACKUP)
    print(f"Backup written: {BACKUP}")

    new_source = source.replace(ANCHOR_1, REPLACE_1, 1)
    new_source = new_source.replace(ANCHOR_2, REPLACE_2, 1)
    new_source = new_source.replace(ANCHOR_3, REPLACE_3, 1)
    new_source = new_source.replace(ANCHOR_4, REPLACE_4, 1)
    TARGET.write_text(new_source, encoding="utf-8")

    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(BACKUP, TARGET)
        die(f"py_compile FAILED — original restored from backup.\n{e}")

    print("Applied: Kling 2.5 Turbo Pro default + animate_model channel override "
          "+ model-aware plan cost.")
    print("Verify:  grep -n 'DEFAULT_VIDEO_ENDPOINT\\|animate_model\\|_clip_cost' "
          "shared/recreation_pipeline.py")


if __name__ == "__main__":
    main()
