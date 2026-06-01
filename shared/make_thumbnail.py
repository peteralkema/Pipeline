"""
make_thumbnail.py — Final Hours thumbnail generator
====================================================
Takes a still from a project, applies cinematic darkening and a vignette,
composites the title in bold yellow caps with a heavy shadow so it pops at
small sizes, and saves as <project>/thumbnail.png — the exact filename the
upload script looks for.

This is a templating job, not a design job. Same template every time. What
changes per video: which still, what title text.

Usage (standalone test):
    python3 make_thumbnail.py --project anne_boleyn --shot 4 \
        --title "ONE DAY TO DIE" --subtitle "ANNE BOLEYN"

Once dialled in, the same function gets called from upload_final_hours.py.

Requirements:
    pip install Pillow
"""

import argparse
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter


# ── Channel visual constants (tweak these to tune the house look) ─────────────

THUMBNAIL_SIZE      = (1280, 720)   # YouTube standard 16:9
DARKEN_FACTOR       = 0.55          # 1.0 = no change, lower = darker still
VIGNETTE_STRENGTH   = 0.45          # 0 = none, 1 = heavy edge darkening
TITLE_COLOR         = (252, 211, 3)        # bold yellow (channel signature)
SUBTITLE_COLOR      = (255, 255, 255)      # white below the title
SHADOW_COLOR        = (0, 0, 0, 220)       # near-opaque black shadow
SHADOW_OFFSET       = (6, 6)        # px right and down from text
SHADOW_BLUR         = 4             # gaussian blur radius for the shadow
TITLE_AREA_PCT      = 0.90          # title spans this fraction of frame width
TITLE_TOP_MARGIN    = 40            # px from top of frame to top of title
TITLE_LINE_GAP      = 10            # px between title lines if it has to wrap (rare for 3-word titles)
TITLE_SUBTITLE_GAP  = 18            # px between title block and subtitle
TITLE_MAX_HEIGHT_PCT = 0.32         # title block can occupy up to this fraction of frame height


# Font candidates in preference order — first one that exists on the system wins.
# On macOS Impact and Arial Black are usually installed; fall back to PIL default
# if absolutely nothing is available.
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/Library/Fonts/Impact.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "Impact",
    "Arial Black",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Find the first available bold display font and load it at `size`."""
    for candidate in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(candidate, size)
        except (OSError, IOError):
            continue
    # Last resort — PIL default is tiny and not great, but won't crash
    return ImageFont.load_default()


def _apply_vignette(img: Image.Image, strength: float) -> Image.Image:
    """Darken the corners radially to focus the eye on the centre/text area."""
    w, h = img.size
    # Build a soft radial mask: white centre, black corners
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    # Concentric ellipses brightening toward the centre
    steps = 60
    for i in range(steps):
        # 0 -> full size, steps -> tiny centre
        shrink = i / steps
        x0 = int(w * shrink * 0.5)
        y0 = int(h * shrink * 0.5)
        x1 = w - x0
        y1 = h - y0
        # Brightness ramps from edge (dim) to centre (bright)
        brightness = int(255 * (i / steps))
        draw.ellipse([x0, y0, x1, y1], fill=brightness)
    # Blur the mask so the vignette is smooth
    mask = mask.filter(ImageFilter.GaussianBlur(radius=80))

    # Build a black overlay and composite it using the inverted mask
    overlay = Image.new("RGB", (w, h), (0, 0, 0))
    inverted = Image.eval(mask, lambda v: int((255 - v) * strength))
    return Image.composite(overlay, img, inverted)


def _fit_text(text: str, max_width: int, max_height: int,
              start_size: int = 140) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """
    Find the largest font size where `text` (wrapped if necessary) fits within
    max_width × max_height. Returns the font and the wrapped lines.
    """
    size = start_size
    while size > 30:
        font = _load_font(size)
        # Try widths from 1 word up: pick wrap that fits horizontally
        words = text.split()
        if not words:
            return font, [""]
        # Try progressively narrower wraps until the widest line fits
        for wrap_chars in range(60, 4, -1):
            lines = textwrap.wrap(text, width=wrap_chars) or [text]
            widths = [font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines]
            max_w = max(widths)
            line_h = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
            total_h = line_h * len(lines) + TITLE_LINE_GAP * (len(lines) - 1)
            if max_w <= max_width and total_h <= max_height:
                return font, lines
        size -= 6
    # Fallback — shouldn't happen unless inputs are extreme
    return _load_font(40), textwrap.wrap(text, width=20) or [text]


def _draw_text_with_shadow(base: Image.Image, lines: list[str],
                           font: ImageFont.FreeTypeFont, color: tuple,
                           anchor_xy: tuple[int, int], align: str = "right"):
    """
    Render `lines` of text with a soft drop shadow. Shadow is drawn on a
    separate RGBA layer and blurred for a clean cinematic look.

    `align` controls horizontal positioning of each line relative to anchor_xy:
      - "right": anchor_xy.x is the right edge of each line
      - "left":  anchor_xy.x is the left edge of each line
      - "center": anchor_xy.x is the centre x of each line
    """
    w, h = base.size
    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    text_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)

    x_anchor, y = anchor_xy
    line_h = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]

    for line in lines:
        bbox = font.getbbox(line)
        line_w = bbox[2] - bbox[0]
        if align == "right":
            x = x_anchor - line_w
        elif align == "center":
            x = x_anchor - line_w // 2
        else:  # left
            x = x_anchor
        # Shadow first (offset and blurred)
        shadow_draw.text((x + SHADOW_OFFSET[0], y + SHADOW_OFFSET[1]),
                         line, font=font, fill=SHADOW_COLOR)
        # Then the text itself, crisp
        text_draw.text((x, y), line, font=font, fill=color + (255,))
        y += line_h + TITLE_LINE_GAP

    # Blur the shadow layer only, then composite both onto the base
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=SHADOW_BLUR))
    composed = Image.alpha_composite(base.convert("RGBA"), shadow_layer)
    composed = Image.alpha_composite(composed, text_layer)
    return composed.convert("RGB")


def _resize_crop_to(img: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """Cover-resize then centre-crop to exactly target_size (1280x720)."""
    target_w, target_h = target_size
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h
    if src_ratio > target_ratio:
        new_h = target_h
        new_w = int(src_ratio * new_h)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top  = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def _segment_foreground(img: Image.Image) -> Image.Image | None:
    """
    Use rembg to extract the foreground subject (person, object) from `img`
    and return an RGBA image with the background transparent. Returns None
    if rembg isn't installed — caller should treat that as "skip the
    text-behind-subject effect and use flat composition instead".

    rembg downloads its model (~170MB) on first call and caches it. The first
    segmentation can take 30-60 seconds; subsequent ones are 1-3 seconds.
    """
    try:
        from rembg import remove
    except ImportError:
        print("   (rembg not installed — using flat composition. "
              "For text-behind-subject layering: pip install rembg)")
        return None
    # rembg accepts and returns PIL images directly; ensure RGB input
    rgba = remove(img.convert("RGB"))
    # rembg may return either PIL or bytes depending on version — normalise
    if not isinstance(rgba, Image.Image):
        import io
        rgba = Image.open(io.BytesIO(rgba))
    return rgba.convert("RGBA")


def make_thumbnail(still_path: Path, title: str, subtitle: str,
                   output_path: Path) -> Path:
    """
    Build a thumbnail with text-behind-subject layering (when rembg is
    installed), or flat composition (when it isn't).

    Layer order, top to bottom:
      4. Foreground subject (person), segmented from the original still
      3. Subtitle text
      2. Title text
      1. Darkened + vignetted background (the same still)

    The title and subtitle are drawn ON the darkened background; then the
    segmented subject is pasted on top, hiding any text behind them. The
    effect is the title 'wrapping' around the figure — text in the middle,
    person emerging in front of it — like the Anne Boleyn reference.

    If rembg isn't installed, the foreground paste is skipped and the
    output is flat-composition (current behaviour pre-segmentation).
    """
    original = Image.open(still_path).convert("RGB")
    base = _resize_crop_to(original, THUMBNAIL_SIZE)
    target_w, target_h = THUMBNAIL_SIZE

    # Layer 1: darkened background
    bg = ImageEnhance.Brightness(base).enhance(DARKEN_FACTOR)
    bg = _apply_vignette(bg, VIGNETTE_STRENGTH)

    # Layers 2 + 3: title (large, centred across top) and optional subtitle.
    # The text lives in the top band of the frame so the segmented subject
    # below it can poke up through the letters — head-pokes-through layout.
    title_area_w = int(target_w * TITLE_AREA_PCT)
    title_max_h  = int(target_h * TITLE_MAX_HEIGHT_PCT)

    title_font, title_lines = _fit_text(
        title.upper(), title_area_w, title_max_h, start_size=240,
    )

    centre_x = target_w // 2
    title_y = TITLE_TOP_MARGIN
    bg = _draw_text_with_shadow(bg, title_lines, title_font,
                                TITLE_COLOR, (centre_x, title_y),
                                align="center")

    if subtitle.strip():
        # Subtitle width capped narrower than title (it's smaller text but
        # we want it visually contained, like a tagline under the headline).
        subtitle_area_w = int(target_w * 0.70)
        subtitle_max_h  = int(target_h * 0.12)
        subtitle_font, subtitle_lines = _fit_text(
            subtitle.upper(), subtitle_area_w, subtitle_max_h, start_size=80,
        )
        line_h = title_font.getbbox("Ag")[3] - title_font.getbbox("Ag")[1]
        title_block_h = line_h * len(title_lines) + TITLE_LINE_GAP * (len(title_lines) - 1)
        subtitle_y = title_y + title_block_h + TITLE_SUBTITLE_GAP
        bg = _draw_text_with_shadow(bg, subtitle_lines, subtitle_font,
                                    SUBTITLE_COLOR, (centre_x, subtitle_y),
                                    align="center")

    # Layer 4: segment the original still and paste foreground on top, so
    # the figure occludes whatever text it overlaps with — text-behind-subject.
    print("   segmenting foreground (rembg)...")
    foreground = _segment_foreground(base)
    if foreground is not None:
        # foreground was segmented from `base` which is already 1280x720,
        # so pixel-aligned paste with no scaling.
        bg = bg.convert("RGBA")
        bg.alpha_composite(foreground)
        bg = bg.convert("RGB")
        print("   layered with text-behind-subject")
    else:
        print("   flat composition (no segmentation)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    bg.save(output_path, "PNG", optimize=True)
    return output_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Generate a Final Hours thumbnail")
    ap.add_argument("--project", required=True,
                    help="project folder, e.g. anne_boleyn")
    ap.add_argument("--shot", type=int, required=True,
                    help="shot number to use as the background still (1-based)")
    ap.add_argument("--title", required=True,
                    help='main title text, e.g. "ONE DAY TO DIE"')
    ap.add_argument("--subtitle", default="",
                    help='subtitle text, e.g. "ANNE BOLEYN"')
    ap.add_argument("--out", default=None,
                    help="output path (default: <project>/thumbnail.png)")
    args = ap.parse_args()

    project = Path(args.project).expanduser()
    still = project / "stills" / f"shot_{args.shot:03d}.png"
    if not still.exists():
        raise SystemExit(f"Still not found: {still}")

    out = Path(args.out) if args.out else project / "thumbnail.png"
    result = make_thumbnail(still, args.title, args.subtitle, out)
    print(f"OK Thumbnail -> {result}")


if __name__ == "__main__":
    main()
