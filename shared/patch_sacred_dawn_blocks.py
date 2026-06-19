#!/usr/bin/env python3
# patch_sacred_dawn_blocks.py
#
# Idempotent. Adds the thumbnail + music blocks (and a kling_count default) to
# sacred-dawn/channel.json so Sacred Dawn matches channels built after the
# thumbnail/music systems landed.
#
# It does NOT guess the thumbnail styling: it ports the proven block from
# prehistoric-disasters/channel.json at runtime, then overrides only
# `composition` and `candidate_prompt_suffix` for faceless biblical art.
#
# Safety:
#   - REFUSES unless the resolved channel name is exactly "sacred_dawn".
#   - Backs up once to channel.json.pre_blocks before writing.
#   - Idempotent: re-running is a no-op once the blocks exist.
#   - Validates JSON round-trip before writing.
#
# Workflow: run on the LAPTOP from the repo root, commit, push to GitHub,
# then `git pull --no-edit` on the box. Never hand-edit on the box.

import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # .../shared
REPO = os.path.dirname(HERE)                               # repo root
SD = os.path.join(REPO, "sacred-dawn", "channel.json")
PD = os.path.join(REPO, "prehistoric-disasters", "channel.json")

MUSIC_BLOCK = {"dir": "music", "tracks": 3, "crossfade_seconds": 2, "level": 0.07}

FACELESS_SUFFIX = (
    "Reverent cinematic biblical scene, faceless: silhouettes, figures seen from "
    "behind, hands, or distant forms; never a resolved human face; God is never "
    "depicted, only light or presence; violence and death only by implication. "
    "Deep shadow, volumetric light, painterly realism, muted sacred palette. "
    "Keep one third of the frame dark and near-empty as a text-safe zone."
)


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_name(cfg):
    """Find the channel-name field without assuming the schema."""
    for key in ("name", "channel", "slug", "id", "channel_name"):
        val = cfg.get(key)
        if isinstance(val, str):
            return key, val
    return None, None


def main():
    if not os.path.exists(SD):
        sys.exit("REFUSE: not found: %s (run from repo root on the laptop)" % SD)

    cfg = load(SD)
    key, name = resolve_name(cfg)
    if name != "sacred_dawn":
        sys.exit(
            "REFUSE: resolved channel name is %r (from key %r), expected "
            "'sacred_dawn'. If the name lives under a different key, paste the "
            "head of channel.json and adjust resolve_name()." % (name, key)
        )

    changed = []

    # ---- thumbnail block (ported from prehistoric, overridden for biblical) ----
    if "thumbnail" not in cfg:
        thumb = None
        if os.path.exists(PD):
            try:
                pd = load(PD)
                if isinstance(pd.get("thumbnail"), dict):
                    thumb = json.loads(json.dumps(pd["thumbnail"]))  # deep copy
                    print("ported thumbnail block from prehistoric-disasters")
            except Exception as exc:  # noqa: BLE001
                print("WARN: could not port from prehistoric (%s); using fallback" % exc)
        if thumb is None:
            thumb = {
                "scrim": {"opacity": 0.45, "direction": "left"},
                "font": "Anton",
                "title_color": "#FFFFFF",
                "subtitle_color": "#E8C36B",
            }
            print("used self-contained thumbnail fallback")
        thumb["composition"] = "centered_subject"
        thumb["candidate_prompt_suffix"] = FACELESS_SUFFIX
        cfg["thumbnail"] = thumb
        changed.append("thumbnail")
    else:
        print("skip: thumbnail block already present")

    # ---- music block ----
    if "music" not in cfg:
        cfg["music"] = dict(MUSIC_BLOCK)
        changed.append("music")
    else:
        print("skip: music block already present")

    # ---- kling_count default ----
    if cfg.get("kling_count") != 2:
        cfg["kling_count"] = 2
        changed.append("kling_count")
    else:
        print("skip: kling_count already 2")

    if not changed:
        print("No changes needed -- sacred-dawn/channel.json already patched.")
        return

    bak = SD + ".pre_blocks"
    if not os.path.exists(bak):
        shutil.copy2(SD, bak)
        print("backup: %s" % bak)

    out = json.dumps(cfg, indent=2, ensure_ascii=False)
    json.loads(out)  # validate round-trip before writing
    with open(SD, "w", encoding="utf-8") as f:
        f.write(out + "\n")

    print("PATCHED %s" % SD)
    print("added/updated: %s" % ", ".join(changed))
    print("--- thumbnail / music / kling_count now: ---")
    print(json.dumps(
        {k: cfg.get(k) for k in ("thumbnail", "music", "kling_count")},
        indent=2, ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
