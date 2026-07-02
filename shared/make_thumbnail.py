"""
make_thumbnail.py — channel-agnostic thumbnail compositor
=========================================================
Takes a still, applies the channel's house look (darken + vignette), composites
the headline (heavy stroke + drop shadow so it pops at phone size), and saves as
<project>/thumbnail.png — the exact filename the upload step looks for.

This is a TEMPLATING job, not a design job. The treatment is LOCKED per channel
and never deviates — that consistency IS the brand. What changes per video: which
still, and the headline text.

The look is no longer hardcoded. It resolves from a `thumbnail` block in the
channel's channel.json (same pattern as voice_id / style_suffix). A channel with
no `thumbnail` block renders with the DEFAULTS below — which reproduce the original
Final Hours look exactly, so existing channels are unchanged.

Two composition modes:
  - "centered_subject"  (default / Final Hours): big title centred across the top
                         band, segmented subject pasted on top so it pokes through
                         the letters (head-pokes-through layout). rembg ON.
  - "low_silhouette"    (prehistoric-disasters): catastrophe fills the frame, a tiny
                         human silhouette sits low in the render, headline anchored
                         in a corner over reserved negative space. rembg OFF — the
                         silhouette is part of the Flux render, not a paste.

Usage (standalone test):
    python3 make_thumbnail.py --project projects/toba_ep01/modea \
        --still projects/toba_ep01/modea/thumbnail_still.png \
        --channel prehistoric-disasters \
        --title "ALMOST EXTINCT" --subtitle "74,000 YEARS AGO"

    # or pick a numbered shot as the background instead of an explicit still:
    python3 make_thumbnail.py --project anne_boleyn --shot 4 \
        --channel final-hours --title "ONE DAY TO DIE" --subtitle "ANNE BOLEYN"

Requirements:
    pip install Pillow
    pip install rembg            # only needed for "centered_subject" mode
"""

import argparse
import json
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter


# ── Canvas ────────────────────────────────────────────────────────────────────
THUMBNAIL_SIZE = (1280, 720)   # YouTube standard 16:9


# ── DEFAULT house look = the original Final Hours look ────────────────────────
# A channel.json with no `thumbnail` block renders exactly like this, so nothing
# that exists today changes. Per-channel blocks override key-by-key.
DEFAULTS = {
    "composition":          "centered_subject",   # or "low_silhouette"
    "title_color":          [252, 211, 3],        # bold yellow (FH signature)
    "subtitle_color":       [255, 255, 255],
    "stroke_width":         0,                     # 0 = no outline (FH used shadow only)
    "stroke_color":         [0, 0, 0],
    "shadow":               True,
    "shadow_offset":        [6, 6],
    "shadow_blur":          4,
    "shadow_color":         [0, 0, 0, 220],
    # PATCH_SOLIDMODE: solid_color_character mode (B-variant thumbnails)
    "bg_color":             [237, 106, 34],   # flat fill when no per-render colour given
    "subject_shadow":       True,             # soft drop-shadow behind the cutout (ICE-AGE lift)
    "subject_shadow_offset":[18, 18],
    "subject_shadow_blur":  22,
    "subject_shadow_color": [0, 0, 0, 150],
    "subject_scale":        0.92,             # cutout height as frac of canvas height
    "subject_x_frac":       0.52,             # left edge of cutout as frac of width (pushes right)
    "darken_factor":        0.55,                  # 1.0 = no change, lower = darker
    "vignette_strength":    0.45,                  # 0 = none, 1 = heavy
    "text_anchor":          "top-center",          # top-left | top-right | top-center
    "text_align":           "center",             # left | right | center
    "title_area_pct":       0.90,                  # title spans this frac of width
    "title_max_height_pct": 0.32,                  # title block max frac of height
    "title_start_size":     240,                   # fit search starts here
    "subtitle_area_pct":    0.70,
    "subtitle_max_height_pct": 0.12,
    "subtitle_start_size":  80,
    "margin":               40,                    # px from frame edge to text block
    "line_gap":             10,
    "title_subtitle_gap":   18,
    "uppercase":            True,
    "segment_foreground":   True,                  # rembg poke-through (FH effect)
    "font":                 None,                  # explicit TTF path (repo-relative or absolute)
    "font_fallbacks":       [],                    # extra TTF paths tried before the system list
}

# System fonts tried after any config-provided font + fallbacks, before PIL default.
SYSTEM_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/Library/Fonts/Impact.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "Impact",
    "Arial Black",
]


# ── Config resolution ─────────────────────────────────────────────────────────

def _repo_root() -> Path:
    """Best-effort repo root = parent of the dir this file lives in (shared/)."""
    return Path(__file__).resolve().parent.parent


def _find_channel_json(project: Path, channel: str | None) -> Path | None:
    """
    Resolve the channel.json that owns this thumbnail.
    Priority: explicit --channel (dir name or path) > walk up from the project
    looking for a sibling <name>/channel.json > None (use DEFAULTS).
    Mirrors look_resolver's walk-up behaviour.
    """
    if channel:
        cand = Path(channel)
        if cand.is_file():
            return cand
        # treat as a channel dir name under the repo root or cwd
        for base in (_repo_root(), Path.cwd()):
            cj = base / channel / "channel.json"
            if cj.exists():
                return cj
        # maybe they passed the dir itself
        if (cand / "channel.json").exists():
            return cand / "channel.json"
    # walk up from the project dir; a channel dir contains channel.json
    p = project.resolve()
    for parent in [p, *p.parents]:
        cj = parent / "channel.json"
        if cj.exists():
            return cj
    return None


def _resolve_config(project: Path, channel: str | None) -> dict:
    """Merge DEFAULTS with the channel's `thumbnail` block (block wins key-by-key)."""
    cfg = dict(DEFAULTS)
    cj = _find_channel_json(project, channel)
    if cj:
        try:
            block = json.loads(cj.read_text()).get("thumbnail", {}) or {}
            cfg.update(block)
            print(f"   thumbnail look <- {cj}")
        except (OSError, json.JSONDecodeError) as e:
            print(f"   (could not read {cj}: {e} — using DEFAULTS)")
    else:
        print("   (no channel.json found — using DEFAULTS / Final Hours look)")
    return cfg


def _load_font(size: int, cfg: dict) -> ImageFont.FreeTypeFont:
    """First available font: config font > config fallbacks > system list > PIL default."""
    candidates = []
    if cfg.get("font"):
        f = Path(cfg["font"])
        candidates.append(str(f if f.is_absolute() else _repo_root() / f))
    candidates += list(cfg.get("font_fallbacks", []))
    candidates += SYSTEM_FONT_CANDIDATES
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# ── Image helpers ─────────────────────────────────────────────────────────────

def _resize_crop_to(img: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """Cover-resize then centre-crop to exactly target_size."""
    target_w, target_h = target_size
    src_w, src_h = img.size
    src_ratio, target_ratio = src_w / src_h, target_w / target_h
    if src_ratio > target_ratio:
        new_h = target_h
        new_w = int(src_ratio * new_h)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def _apply_vignette(img: Image.Image, strength: float) -> Image.Image:
    if strength <= 0:
        return img
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    steps = 60
    for i in range(steps):
        shrink = i / steps
        x0, y0 = int(w * shrink * 0.5), int(h * shrink * 0.5)
        draw.ellipse([x0, y0, w - x0, h - y0], fill=int(255 * (i / steps)))
    mask = mask.filter(ImageFilter.GaussianBlur(radius=80))
    overlay = Image.new("RGB", (w, h), (0, 0, 0))
    inverted = Image.eval(mask, lambda v: int((255 - v) * strength))
    return Image.composite(overlay, img, inverted)


def _fit_text(text: str, max_width: int, max_height: int,
              cfg: dict, start_size: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Largest font size where `text` (wrapped if needed) fits within the box."""
    gap = cfg["line_gap"]
    size = start_size
    while size > 30:
        font = _load_font(size, cfg)
        words = text.split()
        if not words:
            return font, [""]
        for wrap_chars in range(60, 4, -1):
            lines = textwrap.wrap(text, width=wrap_chars, break_long_words=False, break_on_hyphens=False) or [text]
            widths = [font.getbbox(l)[2] - font.getbbox(l)[0] for l in lines]
            line_h = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
            total_h = line_h * len(lines) + gap * (len(lines) - 1)
            if max(widths) <= max_width and total_h <= max_height:
                return font, lines
        size -= 6
    return _load_font(40, cfg), textwrap.wrap(text, width=20, break_long_words=False, break_on_hyphens=False) or [text]


def _anchor_x(cfg: dict, frame_w: int) -> tuple[int, str]:
    """Return (x_anchor, align) from the configured text_anchor / text_align.
    Horizontal inset uses margin_x, falling back to margin."""
    anchor = cfg["text_anchor"]
    align = cfg["text_align"]
    margin = cfg.get("margin_x", cfg["margin"])
    if anchor == "top-left":
        return margin, (align or "left")
    if anchor == "top-right":
        return frame_w - margin, (align or "right")
    return frame_w // 2, (align or "center")   # top-center


def _apply_scrim(img: Image.Image, cfg: dict) -> Image.Image:
    """
    Lay a directional black gradient ('scrim') over the text side ONLY, so the
    headline gets a dark backing for contrast while the rest of the image keeps
    full brightness. This is the fix for global-darkening washing out the picture.

    Config (under `thumbnail.scrim`):
      side        "left" | "right" | "top" | "bottom"   (where the text lives)
      width       0..1 fraction of the frame the gradient spans (e.g. 0.55)
      opacity     0..1 max darkness at the text edge (e.g. 0.85)
      feather     0..1 how much of `width` is the fade tail vs solid (e.g. 0.7)
    Returns img unchanged if no scrim configured.
    """
    sc = cfg.get("scrim")
    if not sc:
        return img
    side = sc.get("side", "left")
    width = float(sc.get("width", 0.55))
    opacity = float(sc.get("opacity", 0.85))
    feather = float(sc.get("feather", 0.7))   # fraction of width that fades
    w, h = img.size
    max_a = int(max(0.0, min(1.0, opacity)) * 255)

    # Build a 1-D alpha ramp along the span, then project to 2-D.
    horizontal = side in ("left", "right")
    span = int((w if horizontal else h) * max(0.05, min(1.0, width)))
    if span <= 0:
        return img
    solid = int(span * (1.0 - max(0.0, min(1.0, feather))))   # fully-opaque head
    ramp = []
    for i in range(span):
        if i < solid:
            a = max_a
        else:
            # linear fade from max_a -> 0 across the feather tail
            t = (i - solid) / max(1, (span - solid))
            a = int(max_a * (1.0 - t))
        ramp.append(a)
    # For "right"/"bottom" the opaque head is at the far edge, so reverse.
    if side in ("right", "bottom"):
        ramp = ramp[::-1]

    mask = Image.new("L", (w, h), 0)
    px = mask.load()
    if horizontal:
        x0 = 0 if side == "left" else w - span
        for i, a in enumerate(ramp):
            x = x0 + i
            if 0 <= x < w:
                for y in range(h):
                    px[x, y] = a
    else:
        y0 = 0 if side == "top" else h - span
        for i, a in enumerate(ramp):
            y = y0 + i
            if 0 <= y < h:
                for x in range(w):
                    px[x, y] = a

    overlay = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(overlay, img, mask)


def _draw_block(base: Image.Image, lines: list[str], font: ImageFont.FreeTypeFont,
                color: tuple, x_anchor: int, y: int, align: str, cfg: dict) -> Image.Image:
    """Draw `lines` with optional stroke (outline) and a soft, blurred drop shadow."""
    w, h = base.size
    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    text_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    tdraw = ImageDraw.Draw(text_layer)

    line_h = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
    gap = cfg["line_gap"]
    stroke_w = int(cfg.get("stroke_width", 0))
    stroke_fill = tuple(cfg.get("stroke_color", [0, 0, 0])) + (255,)
    shadow_on = bool(cfg.get("shadow", True))
    sox, soy = cfg.get("shadow_offset", [6, 6])
    shadow_color = tuple(cfg.get("shadow_color", [0, 0, 0, 220]))

    for line in lines:
        bbox = font.getbbox(line)
        line_w = bbox[2] - bbox[0]
        if align == "right":
            x = x_anchor - line_w
        elif align == "center":
            x = x_anchor - line_w // 2
        else:
            x = x_anchor
        if shadow_on:
            sdraw.text((x + sox, y + soy), line, font=font, fill=shadow_color,
                       stroke_width=stroke_w, stroke_fill=shadow_color)
        tdraw.text((x, y), line, font=font, fill=tuple(color) + (255,),
                   stroke_width=stroke_w, stroke_fill=stroke_fill)
        y += line_h + gap

    if shadow_on:
        shadow_layer = shadow_layer.filter(
            ImageFilter.GaussianBlur(radius=cfg.get("shadow_blur", 4)))
    composed = Image.alpha_composite(base.convert("RGBA"), shadow_layer)
    composed = Image.alpha_composite(composed, text_layer)
    return composed.convert("RGB")


def _segment_foreground(img: Image.Image):
    """rembg foreground cutout (RGBA) for the poke-through effect. None if unavailable."""
    try:
        from rembg import remove
    except ImportError:
        print("   (rembg not installed — flat composition. pip install rembg)")
        return None
    rgba = remove(img.convert("RGB"))
    if not isinstance(rgba, Image.Image):
        import io
        rgba = Image.open(io.BytesIO(rgba))
    return rgba.convert("RGBA")


# ── Main compositor ───────────────────────────────────────────────────────────


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

    frame_w, frame_h = bg.size  # __PROP_GEOMETRY__
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

    position = prop_cfg.get("position", "bottom-left")
    top_frac = prop_cfg.get("prop_top_frac")  # __PROP_GEOMETRY__
    if position == "bottom-left":
        if top_frac is not None:
            x, y = margin, int(frame_h * float(top_frac))
        else:
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


def make_thumbnail(still_path: Path, title: str, subtitle: str,
                   output_path: Path, cfg: dict | None = None) -> Path:
    """
    Composite <still> + headline into a 1280x720 thumbnail using the resolved
    channel look `cfg` (defaults to the Final Hours look when cfg is None).
    """
    cfg = cfg or dict(DEFAULTS)
    target_w, target_h = THUMBNAIL_SIZE

    original = Image.open(still_path).convert("RGB")
    base = _resize_crop_to(original, THUMBNAIL_SIZE)

    # Layer 1 — darkened, vignetted background
    bg = ImageEnhance.Brightness(base).enhance(cfg["darken_factor"])
    bg = _apply_vignette(bg, cfg["vignette_strength"])

    # Layer 1b — directional scrim on the text side only (keeps the image bright
    # everywhere else; the real fix for global-darkening washing out the picture).
    bg = _apply_scrim(bg, cfg)

    # Layer 1c -- prop (one hero object in the negative space, UNDER the text)
    bg = _composite_prop(bg, still_path.parent, cfg)  # __PROP_LAYER__

    # Layer 2/3 — headline (+ optional subtitle)
    if cfg.get("uppercase", True):
        title = title.upper()
        subtitle = subtitle.upper() if subtitle else subtitle

    title_area_w = int(target_w * cfg["title_area_pct"])
    title_max_h = int(target_h * cfg["title_max_height_pct"])
    title_font, title_lines = _fit_text(title, title_area_w, title_max_h,
                                        cfg, cfg["title_start_size"])

    x_anchor, align = _anchor_x(cfg, target_w)
    title_y = cfg.get("margin_y", cfg["margin"])
    bg = _draw_block(bg, title_lines, title_font, cfg["title_color"],
                     x_anchor, title_y, align, cfg)

    if subtitle and subtitle.strip():
        sub_area_w = int(target_w * cfg["subtitle_area_pct"])
        sub_max_h = int(target_h * cfg["subtitle_max_height_pct"])
        sub_font, sub_lines = _fit_text(subtitle, sub_area_w, sub_max_h,
                                        cfg, cfg["subtitle_start_size"])
        line_h = title_font.getbbox("Ag")[3] - title_font.getbbox("Ag")[1]
        title_block_h = line_h * len(title_lines) + cfg["line_gap"] * (len(title_lines) - 1)
        sub_y = title_y + title_block_h + cfg["title_subtitle_gap"]
        bg = _draw_block(bg, sub_lines, sub_font, cfg["subtitle_color"],
                         x_anchor, sub_y, align, cfg)

    # PATCH_SOLIDMODE: solid_color_character mode -- flat colour + shadowed cutout.
    # Rebuilds `bg` from scratch (ignores the darkened-still base above) so the
    # character render (already on a solid bg) becomes a clean cutout on a flat fill.
    if cfg["composition"] == "solid_color_character":
        _bgc = tuple(cfg.get("bg_color", [237, 106, 34]))[:3]
        flat = Image.new("RGB", (target_w, target_h), _bgc)
        cut = _segment_foreground(base)   # rembg RGBA of the character
        if cut is not None:
            # scale the cutout to subject_scale of canvas height, keep aspect
            sh = int(target_h * float(cfg.get("subject_scale", 0.92)))
            ratio = sh / cut.height
            sw = int(cut.width * ratio)
            cut = cut.resize((sw, sh), Image.LANCZOS)
            px = int(target_w * float(cfg.get("subject_x_frac", 0.52)))
            py = target_h - sh   # sit on the bottom edge
            flat = flat.convert("RGBA")
            if cfg.get("subject_shadow", True):
                sox, soy = cfg.get("subject_shadow_offset", [18, 18])
                scol = tuple(cfg.get("subject_shadow_color", [0, 0, 0, 150]))
                # shadow = the cutout's alpha, filled dark, blurred, offset
                shadow = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
                sil = Image.new("RGBA", (sw, sh), scol)
                shadow.paste(sil, (px + sox, py + soy), cut)
                shadow = shadow.filter(ImageFilter.GaussianBlur(
                    radius=cfg.get("subject_shadow_blur", 22)))
                flat = Image.alpha_composite(flat, shadow)
            flat.alpha_composite(cut, (px, py))
            bg = flat.convert("RGB")
        else:
            bg = flat  # no rembg -> flat colour, headline still lands
        # the shared text block below renders as normal (uses the same cfg keys)

    # Layer 4 — poke-through subject (centered_subject mode only)
    if cfg["composition"] == "centered_subject" and cfg.get("segment_foreground", True):
        print("   segmenting foreground (rembg)...")
        fg = _segment_foreground(base)
        if fg is not None:
            bg = bg.convert("RGBA")
            bg.alpha_composite(fg)
            bg = bg.convert("RGB")
            print("   layered text-behind-subject")
        else:
            print("   flat composition (no segmentation)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    bg.save(output_path, "PNG", optimize=True)
    return output_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Channel-agnostic thumbnail compositor")
    ap.add_argument("--project", required=True,
                    help="project folder (engine form ok, e.g. projects/x/modea)")
    ap.add_argument("--channel", default=None,
                    help="channel dir name or channel.json path (resolves the look). "
                         "If omitted, walks up from --project to find channel.json.")
    ap.add_argument("--still", default=None,
                    help="explicit background still path (default: <project>/thumbnail_still.png)")
    ap.add_argument("--shot", type=int, default=None,
                    help="use <project>/stills/shot_NNN.png as the background instead of --still")
    ap.add_argument("--title", required=True, help='headline, e.g. "ALMOST EXTINCT"')
    ap.add_argument("--subtitle", default="", help='optional second line, e.g. "74,000 YEARS AGO"')
    ap.add_argument("--out", default=None, help="output path (default: <project>/thumbnail.png)")
    ap.add_argument("--composition", default=None,  # PATCH_COMPFLAG
                    help="override the channel's composition mode for this render "
                         "(e.g. solid_color_character). Omit to use channel.json.")
    ap.add_argument("--bg-color", default=None,  # PATCH_COMPFLAG
                    help="override bg_color as 'R,G,B' (solid_color_character mode).")
    args = ap.parse_args()

    project = Path(args.project).expanduser()
    cfg = _resolve_config(project, args.channel)

    if args.shot is not None:
        still = project / "stills" / f"shot_{args.shot:03d}.png"
    elif args.still:
        still = Path(args.still).expanduser()
    else:
        still = project / "thumbnail_still.png"
    if not still.exists():
        raise SystemExit(f"Still not found: {still}")

    out = Path(args.out) if args.out else project / "thumbnail.png"
    if args.composition:            # PATCH_COMPFLAG
        cfg["composition"] = args.composition
    if args.bg_color:               # PATCH_COMPFLAG
        try:
            cfg["bg_color"] = [int(x) for x in args.bg_color.split(",")][:3]
        except Exception:
            print(f"   (ignoring bad --bg-color {args.bg_color!r})")
    result = make_thumbnail(still, args.title, args.subtitle, out, cfg)
    print(f"OK Thumbnail -> {result}")


if __name__ == "__main__":
    main()
