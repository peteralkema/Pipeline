#!/usr/bin/env python3
"""patch_add_nb2_endpoint.py — register nano-banana-2 as a text-to-image model.

Idempotent; safe to run repeatedly. Run on the LAPTOP, then git -> box.

Adds "nano_banana_2": "fal-ai/nano-banana-2" to IMAGE_ENDPOINTS so a channel can
set "image_model": "nano_banana_2" and render its character-LESS beats on the same
model family as the nano-banana-2/edit character path. This closes the render fork
that made landscape beats (flux) go painterly-golden while character beats
(nano-banana-2/edit) stayed grounded.
"""
import pathlib
import sys

p = pathlib.Path("shared/recreation_pipeline.py")
src = p.read_text()

if '"nano_banana_2"' in src:
    print("already patched: nano_banana_2 endpoint present")
    sys.exit(0)

lines = src.splitlines(keepends=True)
out = []
inserted = False
for ln in lines:
    out.append(ln)
    if (not inserted
            and '"nano_banana"' in ln
            and 'fal-ai/nano-banana"' in ln):
        indent = ln[:len(ln) - len(ln.lstrip())]
        out.append(f'{indent}"nano_banana_2": "fal-ai/nano-banana-2",\n')
        inserted = True

if not inserted:
    sys.exit("ERROR: could not find the nano_banana endpoint line to anchor on")

p.write_text("".join(out))
print("patched: added nano_banana_2 -> fal-ai/nano-banana-2 to IMAGE_ENDPOINTS")
