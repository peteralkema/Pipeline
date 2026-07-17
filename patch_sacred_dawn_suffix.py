#!/usr/bin/env python3
"""Set Sacred Dawn's reconciled palette-only style_suffix and enforce image_model.
Run from repo root on the LAPTOP (~/Projects/Pipeline). Idempotent: no write if
both keys already match. Backs up channel.json before any write. ASCII-only suffix.

Reconciliation: Sacred Dawn palette stays in the suffix (bronze / aged stone /
weathered / Balrog-real mass / bright-crisp HDR / heavy air / anti-murk). The
supernatural-only elements the storm-shaft bug welded in -- deep indigo shadow,
one unearthly light source, god-ray shafts -- are REMOVED from the suffix and left
to the per-beat prompts, where genuinely supernatural content earns them.
"""
import json, pathlib, sys, shutil, datetime

CH = pathlib.Path("sacred-dawn/channel.json")

SUFFIX = (
    "cinematic biblical epic film still, photorealistic and grounded, "
    "epic mythic scale, ancient burnished bronze and weathered aged stone, "
    "the impossible rendered physically real and massive with weight and shadow, "
    "bright vivid exposure, high contrast, high dynamic range with crisp clean detail held in the shadows, "
    "sharp crisp focus, heavy atmospheric air with dust and drifting light, "
    "expressive faces, high production value, period-accurate ancient world, "
    "no modern architecture, no soft painterly haze, no murk, no muddy shadows, "
    "no washed-out wash, no glowing cartoon fantasy, no text, no modern elements, 16:9"
)


def main():
    SUFFIX.encode("ascii")  # hard guard: refuse to write a non-ASCII suffix

    if not CH.exists():
        sys.exit(f"ERROR: {CH} not found -- run from repo root (~/Projects/Pipeline)")

    cfg = json.loads(CH.read_text(encoding="utf-8"))
    old_suffix = cfg.get("style_suffix", "")
    old_model = cfg.get("image_model", "")

    if old_suffix == SUFFIX and old_model == "nano_banana_2":
        print("already live -- no change")
        print(f"  image_model : {old_model}")
        print(f"  style_suffix: {old_suffix[:60]}...")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = CH.with_name(f"channel.json.pre_suffix_{stamp}")
    shutil.copy2(CH, backup)

    cfg["style_suffix"] = SUFFIX
    cfg["image_model"] = "nano_banana_2"
    CH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    v = json.loads(CH.read_text(encoding="utf-8"))
    assert v["style_suffix"] == SUFFIX, "suffix did not persist"
    assert v["image_model"] == "nano_banana_2", "image_model did not persist"

    print(f"backup      : {backup.name}")
    print(f"image_model : {old_model or '(unset)'} -> nano_banana_2")
    print("style_suffix: SET (reconciled palette-only Sacred Dawn grade)")
    print(f"other keys  : {len(cfg) - 2} untouched")
    print("verify OK")


if __name__ == "__main__":
    main()
