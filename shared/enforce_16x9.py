#!/usr/bin/env python3
"""Post-render 16:9 backstop. Walks a stills dir and forces every PNG to exactly
1280x720 by scaling-to-fit then padding (no crop, keeps all of the image) on a
blurred fill so bars aren't dead black. Guaranteed uniform 16:9 before assemble.

Use ONLY if the re-render still shows off-ratio reference beats (i.e. NB2 /edit
ignored image_size too). For beats already 16:9 it's a near-no-op (re-saves same).

Usage (BOX):
  python shared/enforce_16x9.py --stills qqrew/projects/MERCATOR1/stills
  python shared/enforce_16x9.py --stills <dir> --crop   # crop-to-fill instead of pad
"""
import argparse, glob, os, sys
from PIL import Image, ImageFilter

W, H = 1280, 720
TARGET = W / H

def fit_pad(im):
    im = im.convert("RGB")
    w, h = im.size
    r = w / h
    if abs(r - TARGET) < 0.01 and (w, h) != (W, H):
        return im.resize((W, H), Image.LANCZOS)
    if abs(r - TARGET) < 0.01:
        return im
    # blurred fill background = the image scaled to COVER, blurred
    cover_scale = max(W / w, H / h)
    bg = im.resize((int(w*cover_scale), int(h*cover_scale)), Image.LANCZOS)
    bx = (bg.width - W)//2; by = (bg.height - H)//2
    bg = bg.crop((bx, by, bx+W, by+H)).filter(ImageFilter.GaussianBlur(24))
    # foreground = image scaled to FIT
    fit_scale = min(W / w, H / h)
    fg = im.resize((int(w*fit_scale), int(h*fit_scale)), Image.LANCZOS)
    ox = (W - fg.width)//2; oy = (H - fg.height)//2
    bg.paste(fg, (ox, oy))
    return bg

def crop_fill(im):
    im = im.convert("RGB")
    w, h = im.size
    scale = max(W / w, H / h)
    im2 = im.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
    cx = (im2.width - W)//2; cy = (im2.height - H)//2
    return im2.crop((cx, cy, cx+W, cy+H))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", required=True)
    ap.add_argument("--crop", action="store_true", help="crop-to-fill instead of pad-to-fit")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(a.stills, "*.png")))
    if not files:
        print(f"no PNGs in {a.stills}"); return 1
    fixed = 0; already = 0
    for f in files:
        im = Image.open(f)
        w, h = im.size
        if (w, h) == (W, H):
            already += 1; continue
        out = crop_fill(im) if a.crop else fit_pad(im)
        out.save(f)
        fixed += 1
    print(f"done. {fixed} converted to {W}x{H}, {already} already correct, {len(files)} total.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
