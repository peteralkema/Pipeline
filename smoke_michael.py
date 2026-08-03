#!/usr/bin/env python3
"""smoke_michael.py -- probe before the rig spend (Law 12).

Reads assets.json, pulls one @-token's frozen reference_urls, fires ONE seedream
v5 pro edit (P3 shape, FAL_KEY), downloads the result. ~$0.10. Proves identity
renders from the frozen snapshot before committing to the 10-beat rig. Standalone:
no db, no visuals import -- it tests the fal edit call and the URLs, nothing else.

Usage:
  python smoke_michael.py <assets.json> [@id] [out.png] ["prompt override"]
"""
import json
import os
import sys

import requests

ENDPOINT = "https://fal.run/bytedance/seedream/v5/pro/edit"


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python smoke_michael.py <assets.json> [@id] [out.png] [prompt]")
    assets_path = sys.argv[1]
    at = sys.argv[2] if len(sys.argv) > 2 else "@michael"
    out = sys.argv[3] if len(sys.argv) > 3 else "smoke_michael.png"

    assets = json.loads(open(assets_path).read())
    bare = at.lstrip("@")
    rec = assets.get(at) or assets.get("@" + bare) or assets.get(bare)
    if not rec:
        sys.exit("no %s in %s" % (at, assets_path))
    urls = rec.get("reference_urls") or []
    if not urls:
        sys.exit("%s has no reference_urls" % at)
    name = rec.get("name", bare)

    default_prompt = ("bright cinematic photoreal, %s in his reference armor "
                      "raises a spear of white light, low three-quarter angle, "
                      "ordered ranks of winged figures receding behind" % name)
    prompt = sys.argv[4] if len(sys.argv) > 4 else default_prompt

    key = os.environ.get("FAL_KEY")
    if not key:
        sys.exit("FAL_KEY not in environment (set -a && source .env && set +a)")

    body = {"prompt": prompt, "image_urls": urls, "image_size": "landscape_16_9"}
    print("refs: %d | prompt: %s" % (len(urls), prompt))
    r = requests.post(ENDPOINT,
                      headers={"Authorization": "Key " + key,
                               "Content-Type": "application/json"},
                      json=body, timeout=300)
    print("HTTP", r.status_code)
    if r.status_code != 200:
        sys.exit(r.text[:800])
    data = r.json()
    imgs = data.get("images") or []
    if not imgs or "url" not in imgs[0]:
        sys.exit("no media; keys=%s body=%s" % (list(data), str(data)[:400]))
    img_url = imgs[0]["url"]
    print("image:", img_url)
    blob = requests.get(img_url, timeout=300).content
    open(out, "wb").write(blob)
    print("wrote %s (%d bytes)" % (out, len(blob)))


if __name__ == "__main__":
    main()
