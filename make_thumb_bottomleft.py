#!/usr/bin/env python3
"""
ONE-OFF: composite the Sacred Dawn house look but anchor the headline BOTTOM-LEFT.
Reads channel.json so the look (font, colors, stroke, shadow, scrim) matches the
locked house style exactly. Only the text anchor changes. Not part of the engine.

  python make_thumb_bottomleft.py --channel sacred-dawn \
    --in sacred-dawn/projects/satan-morning-star/thumb_candidates/candidate_1.png \
    --out sacred-dawn/projects/satan-morning-star/thumbnail_botleft.png \
    --title "SATAN" --subtitle "FALL FROM GLORY"
"""
import argparse, json, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    import numpy as np
    HAVE_NP = True
except Exception:
    HAVE_NP = False


def load_font(path, size, fallbacks):
    for p in [path] + list(fallbacks or []):
        if not p:
            continue
        try:
            return ImageFont.truetype(p, size), p
        except Exception:
            continue
    return ImageFont.load_default(), "PIL-default"


def fit(draw, text, path, fallbacks, max_w, max_h, start, stroke):
    size = start
    while size > 12:
        f, used = load_font(path, size, fallbacks)
        b = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
        if (b[2] - b[0]) <= max_w and (b[3] - b[1]) <= max_h:
            return f, used, (b[2] - b[0]), (b[3] - b[1])
        size -= 4
    f, used = load_font(path, 12, fallbacks)
    b = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
    return f, used, (b[2] - b[0]), (b[3] - b[1])


def darken_left_and_bottom(img, scrim):
    """Left vertical scrim (faithful to channel) + a soft bottom-left gradient under the text."""
    W, H = img.size
    if not HAVE_NP:
        return img  # scrim skipped without numpy; text stroke/shadow still carries legibility
    arr = np.asarray(img).astype(np.float32)

    # --- left scrim, exactly as channel.json configures it ---
    sw = scrim.get("width", 0.42)
    op = scrim.get("opacity", 0.55)
    feather = scrim.get("feather", 0.7)
    spx = max(1, int(W * sw))
    solid = spx * (1.0 - feather)
    xs = np.arange(W, dtype=np.float32)
    la = np.where(
        xs < solid, op,
        np.where(xs < spx, op * (1.0 - (xs - solid) / max(1.0, spx - solid)), 0.0),
    ).astype(np.float32)
    arr *= (1.0 - la[None, :, None])

    # --- extra soft bottom gradient, strongest at the lower-left, to seat the text ---
    band = int(H * 0.45)
    ys = np.arange(H, dtype=np.float32)
    yv = np.clip((ys - (H - band)) / band, 0, 1)            # 0 -> 1 toward bottom
    xv = np.clip(1.0 - xs / (W * 0.62), 0, 1)               # 1 at left edge -> 0 at 62% width
    ba = (0.60 * yv[:, None]) * (0.40 + 0.60 * xv[None, :])  # peak ~0.60 bottom-left
    arr *= (1.0 - ba[:, :, None])

    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", required=True, help="channel folder holding channel.json")
    ap.add_argument("--in", dest="inp", required=True, help="clean base still (no text)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", required=True)
    a = ap.parse_args()

    cfg = json.load(open(os.path.join(a.channel, "channel.json")))
    t = cfg["thumbnail"]
    font_path = t.get("font")
    fb = t.get("font_fallbacks", [])
    title_color = tuple(t.get("title_color", [245, 240, 235]))
    sub_color = tuple(t.get("subtitle_color", [255, 200, 90]))
    stroke = int(t.get("stroke_width", 12))
    stroke_color = tuple(t.get("stroke_color", [0, 0, 0]))
    shadow = bool(t.get("shadow", True))
    sx, sy = t.get("shadow_offset", [5, 6])
    sblur = int(t.get("shadow_blur", 6))
    mx = int(t.get("margin_x", 40))
    my = int(t.get("margin_y", 20))
    upper = bool(t.get("uppercase", True))

    title = a.title.upper() if upper else a.title
    sub = a.subtitle.upper() if upper else a.subtitle

    img = Image.open(a.inp).convert("RGB")
    W, H = img.size
    img = darken_left_and_bottom(img, t.get("scrim", {}))

    draw = ImageDraw.Draw(img)
    tf, tused, tw, th = fit(draw, title, font_path, fb,
                            int(W * t.get("title_area_pct", 0.52)),
                            int(H * t.get("title_max_height_pct", 0.34)),
                            int(t.get("title_start_size", 150)), stroke)
    sf, sused, sw_, sh_ = fit(draw, sub, font_path, fb,
                              int(W * t.get("subtitle_area_pct", 0.55)),
                              int(H * t.get("subtitle_max_height_pct", 0.14)),
                              int(t.get("subtitle_start_size", 90)), stroke)
    print("   fonts:", os.path.basename(tused), "/", os.path.basename(sused))

    gap = int(th * 0.14)
    block_h = th + gap + sh_
    x = mx
    y_title = H - my - block_h
    y_sub = y_title + th + gap

    def render(text, font, xy, color):
        px, py = xy
        if shadow:
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            d.text((px + sx, py + sy), text, font=font, fill=(0, 0, 0, 230),
                   stroke_width=stroke, stroke_fill=(0, 0, 0, 230))
            lay = lay.filter(ImageFilter.GaussianBlur(sblur))
            img.paste(lay, (0, 0), lay)
        ImageDraw.Draw(img).text((px, py), text, font=font, fill=color,
                                 stroke_width=stroke, stroke_fill=stroke_color)

    render(title, tf, (x, y_title), title_color)
    render(sub, sf, (x, y_sub), sub_color)

    img.save(a.out, quality=95)
    print("OK ->", a.out, img.size)


if __name__ == "__main__":
    main()
