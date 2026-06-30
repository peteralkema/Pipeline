"""
patch_thumbnail_prop.py -- add the prop layer to make_thumbnail.py + channel.json
=================================================================================
Adds the THIRD thumbnail slot (one flat-cel hero prop in the negative space) to the
channel-agnostic compositor. Fully backward compatible: a prop composites ONLY if
<project>/thumbnail_prop.png exists AND the channel's thumbnail config has a `prop`
block with "enabled": true. Channels without either are byte-for-byte unchanged.

Run from repo root (laptop):  python3 patch_thumbnail_prop.py
Idempotent: re-running detects the marker and no-ops. Writes shared/make_thumbnail.py.pre_prop
backup on first apply, validates with py_compile, ASCII-only.

What it does:
  1. shared/make_thumbnail.py: insert _composite_prop() helper + a call inside
     make_thumbnail() right AFTER the scrim layer and BEFORE the headline (so text
     sits on top of the prop).
  2. crew-wip/channel.json: add thumbnail.prop block (position/scale CHANNEL constants).
"""

import json
import py_compile
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
THUMB = REPO / "shared" / "make_thumbnail.py"
CHANNEL = REPO / "crew-wip" / "channel.json"

MARKER = "# __PROP_LAYER__"

# ── the helper function, inserted before make_thumbnail() ─────────────────────
HELPER = '''
def _composite_prop(bg, project, cfg):  # __PROP_LAYER__
    """Composite <project>/thumbnail_prop.png (transparent RGBA) into the configured
    corner. No-op unless the file exists AND cfg['prop'] is enabled. Position + scale
    are channel constants; the prop CONTENT is per-video (rendered by make_prop.py)."""
    prop_cfg = (cfg.get("prop") or {})
    if not prop_cfg.get("enabled"):
        return bg
    prop_path = Path(project) / "thumbnail_prop.png"
    if not prop_path.exists():
        return bg
    try:
        prop = Image.open(prop_path).convert("RGBA")
    except OSError as e:
        print("   (prop layer: could not open " + str(prop_path) + ": " + str(e) + ")")
        return bg

    frame_w, frame_h = bg.size
    scale = float(prop_cfg.get("scale", 0.32))
    margin = int(prop_cfg.get("margin", 40))
    target_h = max(1, int(frame_h * scale))
    ratio = target_h / prop.height
    target_w = max(1, int(prop.width * ratio))
    prop = prop.resize((target_w, target_h), Image.LANCZOS)

    position = prop_cfg.get("position", "bottom-left")
    if position == "bottom-left":
        x, y = margin, frame_h - target_h - margin
    elif position == "bottom-right":
        x, y = frame_w - target_w - margin, frame_h - target_h - margin
    elif position == "top-left":
        x, y = margin, margin
    elif position == "top-right":
        x, y = frame_w - target_w - margin, margin
    else:
        x, y = margin, frame_h - target_h - margin

    out = bg.convert("RGBA")
    out.alpha_composite(prop, (x, y))
    print("   prop layer composited (" + position + ", scale " + str(scale) + ")")
    return out.convert("RGB")

'''

# the anchor we insert the CALL after (the scrim line inside make_thumbnail)
CALL_ANCHOR = "    bg = _apply_scrim(bg, cfg)\n"
CALL_INSERT = (
    "    bg = _apply_scrim(bg, cfg)\n"
    "\n"
    "    # Layer 1c -- prop (one hero object in the negative space, UNDER the text)\n"
    "    bg = _composite_prop(bg, still_path.parent, cfg)  # __PROP_LAYER__\n"
)

# the anchor we insert the HELPER before
HELPER_ANCHOR = "def make_thumbnail(still_path: Path, title: str, subtitle: str,\n"


def patch_thumbnail():
    if not THUMB.exists():
        sys.exit("NOT FOUND: " + str(THUMB))
    src = THUMB.read_text()

    if MARKER in src:
        print("make_thumbnail.py already patched (marker present) -- no-op.")
        return False

    # verify anchors exist before touching anything
    if HELPER_ANCHOR not in src:
        sys.exit("ANCHOR MISSING: make_thumbnail() def not found -- aborting, no change.")
    if CALL_ANCHOR not in src:
        sys.exit("ANCHOR MISSING: scrim line not found -- aborting, no change.")
    if src.count(CALL_ANCHOR) != 1:
        sys.exit("ANCHOR NOT UNIQUE: scrim line appears " + str(src.count(CALL_ANCHOR)) + " times -- aborting.")

    backup = THUMB.with_suffix(".py.pre_prop")
    if not backup.exists():
        backup.write_text(src)
        print("backup -> " + str(backup))

    # insert helper before make_thumbnail(), then the call after the scrim line
    src = src.replace(HELPER_ANCHOR, HELPER + "\n" + HELPER_ANCHOR, 1)
    src = src.replace(CALL_ANCHOR, CALL_INSERT, 1)

    THUMB.write_text(src)
    try:
        py_compile.compile(str(THUMB), doraise=True)
    except py_compile.PyCompileError as e:
        THUMB.write_text(backup.read_text())
        sys.exit("py_compile FAILED, reverted: " + str(e))
    print("patched + compiled: " + str(THUMB))
    return True


def patch_channel():
    if not CHANNEL.exists():
        print("(channel.json not at " + str(CHANNEL) + " -- skipping channel patch)")
        return False
    cfg = json.loads(CHANNEL.read_text())
    thumb = cfg.setdefault("thumbnail", {})
    if "prop" in thumb:
        print("channel.json already has thumbnail.prop -- no-op.")
        return False
    thumb["prop"] = {
        "enabled": True,
        "position": "bottom-left",
        "scale": 0.32,
        "margin": 40
    }
    CHANNEL.write_text(json.dumps(cfg, indent=2) + "\n")
    print("channel.json: added thumbnail.prop (bottom-left, scale 0.32)")
    return True


if __name__ == "__main__":
    a = patch_thumbnail()
    b = patch_channel()
    if a or b:
        print("DONE -- commit + push, then pull on box.")
    else:
        print("Nothing to do (already applied).")
