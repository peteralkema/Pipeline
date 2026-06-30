"""
patch_prop_geometry.py -- enforce the QQrew prop geometry doctrine
==================================================================
Upgrades _composite_prop in shared/make_thumbnail.py with two rules from the
thumbnail doctrine, and updates crew-wip/channel.json with the constants:

  1. WIDTH CAP (the square-ish rule): a prop is scaled to `scale` * frame height,
     but if that makes it wider than `max_w_frac` * frame width, it scales DOWN so
     width fits. A too-wide prop shrinks instead of invading the subject zone.
  2. TOP ANCHOR: prop TOP pinned to `prop_top_frac` * frame height (nests just
     under the subtitle) instead of growing up from a fixed bottom margin.

Backward compatible: if the new keys are absent, behaviour is unchanged (falls
back to the old bottom-margin + height-only scaling).

Idempotent. Run from repo root (laptop): python3 patch_prop_geometry.py
"""

import json
import py_compile
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
THUMB = REPO / "shared" / "make_thumbnail.py"
CHANNEL = REPO / "crew-wip" / "channel.json"
MARKER = "__PROP_GEOMETRY__"

# The block that currently computes target_h/target_w + position. We replace the
# sizing+position math with the doctrine-aware version. Anchor on the unique
# resize line that exists in the deployed _composite_prop.
ANCHOR = '''    frame_w, frame_h = bg.size
    scale = float(prop_cfg.get("scale", 0.32))
    margin = int(prop_cfg.get("margin", 40))
    target_h = max(1, int(frame_h * scale))
    ratio = target_h / prop.height
    target_w = max(1, int(prop.width * ratio))
    prop = prop.resize((target_w, target_h), Image.LANCZOS)
'''

REPLACE = '''    frame_w, frame_h = bg.size  # __PROP_GEOMETRY__
    scale = float(prop_cfg.get("scale", 0.32))
    margin = int(prop_cfg.get("margin", 40))
    max_w_frac = float(prop_cfg.get("max_w_frac", 1.0))
    target_h = max(1, int(frame_h * scale))
    ratio = target_h / prop.height
    target_w = max(1, int(prop.width * ratio))
    max_w = int(frame_w * max_w_frac)
    if target_w > max_w:
        target_w = max_w
        ratio = target_w / prop.width
        target_h = max(1, int(prop.height * ratio))
    prop = prop.resize((target_w, target_h), Image.LANCZOS)
'''

# The bottom-left position line: add top-anchor option. The deployed code has:
#   if position == "bottom-left":
#       x, y = margin, frame_h - target_h - margin
POS_ANCHOR = '''    if position == "bottom-left":
        x, y = margin, frame_h - target_h - margin
'''
POS_REPLACE = '''    top_frac = prop_cfg.get("prop_top_frac")  # __PROP_GEOMETRY__
    if position == "bottom-left":
        if top_frac is not None:
            x, y = margin, int(frame_h * float(top_frac))
        else:
            x, y = margin, frame_h - target_h - margin
'''


def patch_thumb():
    if not THUMB.exists():
        sys.exit("NOT FOUND: " + str(THUMB))
    src = THUMB.read_text()
    if MARKER in src:
        print("make_thumbnail.py already has geometry patch -- no-op.")
        return False
    if ANCHOR not in src:
        sys.exit("ANCHOR MISSING: prop sizing block not found (is the prop layer patch applied?)")
    if POS_ANCHOR not in src:
        sys.exit("ANCHOR MISSING: bottom-left position line not found")
    bak = THUMB.with_suffix(".py.pre_geometry")
    if not bak.exists():
        bak.write_text(src)
        print("backup -> " + str(bak))
    src = src.replace(ANCHOR, REPLACE, 1)
    src = src.replace(POS_ANCHOR, POS_REPLACE, 1)
    THUMB.write_text(src)
    try:
        py_compile.compile(str(THUMB), doraise=True)
    except py_compile.PyCompileError as e:
        THUMB.write_text(bak.read_text())
        sys.exit("py_compile FAILED, reverted: " + str(e))
    print("patched + compiled: " + str(THUMB))
    return True


def patch_channel():
    if not CHANNEL.exists():
        print("(channel.json not at " + str(CHANNEL) + " -- skipping)")
        return False
    cfg = json.loads(CHANNEL.read_text())
    prop = cfg.setdefault("thumbnail", {}).setdefault("prop", {})
    changed = False
    desired = {
        "enabled": True,
        "position": "bottom-left",
        "scale": 0.50,
        "max_w_frac": 0.40,
        "prop_top_frac": 0.47,
        "margin": 40,
        "border_px": 14,
        "border_rgb": [255, 255, 255],
    }
    for k, v in desired.items():
        if prop.get(k) != v:
            prop[k] = v
            changed = True
    if changed:
        CHANNEL.write_text(json.dumps(cfg, indent=2) + "\n")
        print("channel.json: prop geometry constants set")
    else:
        print("channel.json: prop geometry already current")
    return changed


if __name__ == "__main__":
    a = patch_thumb()
    b = patch_channel()
    print("DONE -- commit + push, then pull on box." if (a or b) else "Nothing to do.")
