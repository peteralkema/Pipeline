"""
patch_prop_border.py -- add a white sticker-border to knocked-out thumbnail props
Idempotent. Modifies shared/make_prop.py: wraps the knockout output with a white
outline (the pro cutout-sticker look) before saving thumbnail_prop.png.
Border width + color read from channel.json thumbnail.prop (border_px, border_rgb),
with defaults. Run from repo root (laptop): python3 patch_prop_border.py
"""
import py_compile
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
PROP = REPO / "shared" / "make_prop.py"
MARKER = "__PROP_BORDER__"

HELPER = '''
def _add_white_border(rgba, border_px=14, border_rgb=(255, 255, 255)):  # __PROP_BORDER__
    """Add a solid sticker-border around the alpha silhouette of a cutout RGBA image."""
    from PIL import Image, ImageFilter
    if border_px <= 0:
        return rgba
    pad = border_px + 4
    w, h = rgba.size
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    canvas.paste(rgba, (pad, pad), rgba)
    alpha = canvas.split()[3]
    grown = alpha.filter(ImageFilter.MaxFilter(border_px * 2 + 1))
    border_layer = Image.new("RGBA", canvas.size, border_rgb + (0,))
    solid = Image.new("RGBA", canvas.size, border_rgb + (255,))
    border_layer = Image.composite(solid, border_layer, grown)
    out = Image.alpha_composite(border_layer, canvas)
    return out

'''

ANCHOR = "    cut = cut.convert(\"RGBA\")\n"
REPLACE = (
    "    cut = cut.convert(\"RGBA\")\n"
    "    _pcfg = {}\n"
    "    try:\n"
    "        import json as _json\n"
    "        for _p in [dest.parent, *dest.parent.parents]:\n"
    "            _cj = _p / \"channel.json\"\n"
    "            if _cj.exists():\n"
    "                _pcfg = (_json.loads(_cj.read_text()).get(\"thumbnail\", {}) or {}).get(\"prop\", {}) or {}\n"
    "                break\n"
    "    except Exception:\n"
    "        _pcfg = {}\n"
    "    _bpx = int(_pcfg.get(\"border_px\", 14))\n"
    "    _brgb = tuple(_pcfg.get(\"border_rgb\", [255, 255, 255]))\n"
    "    cut = _add_white_border(cut, _bpx, _brgb)  # __PROP_BORDER__\n"
)

MAIN_ANCHOR = "def main():\n"

def run():
    if not PROP.exists():
        sys.exit("NOT FOUND: " + str(PROP))
    src = PROP.read_text()
    if MARKER in src:
        print("make_prop.py already has border patch -- no-op.")
        return
    if ANCHOR not in src or src.count(ANCHOR) != 1:
        sys.exit("ANCHOR missing/not unique: cut.convert RGBA line")
    if MAIN_ANCHOR not in src:
        sys.exit("ANCHOR missing: def main()")
    bak = PROP.with_suffix(".py.pre_border")
    if not bak.exists():
        bak.write_text(src)
        print("backup -> " + str(bak))
    src = src.replace(MAIN_ANCHOR, HELPER + "\n" + MAIN_ANCHOR, 1)
    src = src.replace(ANCHOR, REPLACE, 1)
    PROP.write_text(src)
    try:
        py_compile.compile(str(PROP), doraise=True)
    except py_compile.PyCompileError as e:
        PROP.write_text(bak.read_text())
        sys.exit("py_compile FAILED, reverted: " + str(e))
    print("patched + compiled: " + str(PROP))

if __name__ == "__main__":
    run()
