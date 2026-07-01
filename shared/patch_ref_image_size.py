#!/usr/bin/env python3
"""Force 16:9 on the reference /edit path.

The reference /edit call (recreation_pipeline.py ~line 573) passes only a STRING
"aspect_ratio": aspect. NB2 /edit ignores that string when a PORTRAIT reference
image is attached and echoes the reference's proportions -> every {skeptic} beat
came out portrait/square. The text-to-image path passes "image_size": ASPECT
(explicit width/height dict) and is correctly 16:9.

Fix: add "image_size": ASPECT to the reference args dict too (belt), keeping
aspect_ratio (braces). Gives NB2 a hard pixel target it can't echo away.

If NB2 /edit ALSO ignores image_size (possible for an edit endpoint), run the
companion post-render enforce_16x9.py as the guaranteed backstop.

Idempotent: anchors on the exact args dict; no-ops if image_size already there.
"""
import shutil, sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "recreation_pipeline.py"
if not SRC.exists():
    SRC = Path(__file__).resolve().parent.parent / "shared" / "recreation_pipeline.py"

OLD = '''    args = {
        "prompt": prompt,
        "image_urls": urls,
        "num_images": 1,
        "aspect_ratio": aspect,
        "output_format": "png",
        "safety_tolerance": "5",
        "limit_generations": True,
    }'''

NEW = '''    args = {
        "prompt": prompt,
        "image_urls": urls,
        "num_images": 1,
        "aspect_ratio": aspect,
        "image_size": ASPECT,  # explicit w/h dict: NB2 /edit ignores the aspect_ratio string when a portrait ref is attached (banked 01 Jul)
        "output_format": "png",
        "safety_tolerance": "5",
        "limit_generations": True,
    }'''

def main():
    if not SRC.exists():
        print(f"ERROR: recreation_pipeline.py not found at {SRC}."); return 1
    t = SRC.read_text()
    if '"image_size": ASPECT,  # explicit w/h dict: NB2 /edit ignores' in t:
        print("Already patched (image_size in reference args). No-op."); return 0
    if OLD not in t:
        print("ERROR: reference args block not found verbatim — code drifted. Aborting."); return 1
    import py_compile, tempfile, os
    new_text = t.replace(OLD, NEW, 1)
    # verify it compiles before writing
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(new_text); tmp = f.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: patched file would not compile: {e}. Aborting."); os.unlink(tmp); return 1
    os.unlink(tmp)
    shutil.copy2(SRC, SRC.with_suffix(".py.bak_ref_image_size"))
    SRC.write_text(new_text)
    print("OK reference args now pass image_size: ASPECT (backup written).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
