#!/usr/bin/env python3
"""
patch_channel_resolution.py — teach recreation_pipeline.py per-channel resolution.

Makes the render resolution read from channel.json (width/height fields),
defaulting to 1280x720 so Final Hours behaviour is UNCHANGED. Synthetic's
channel.json sets 1920x1080 to match the Mode B Remotion clips.

Edits three resolution-bearing spots:
  1. ASPECT constant -> channel-aware lookup (with 720p default)
  2. _still_to_held_clip scale/pad string -> built from ASPECT
  3. assemble() trim scale/pad string -> built from ASPECT

Run from anywhere; pass the path to recreation_pipeline.py.
Idempotent: refuses to double-patch (checks for the marker).

    python3 patch_channel_resolution.py shared/recreation_pipeline.py
"""
import sys, re, io

PATH = sys.argv[1] if len(sys.argv) > 1 else "shared/recreation_pipeline.py"
src = open(PATH, encoding="utf-8").read()

if "def _channel_aspect(" in src:
    print("Already patched (found _channel_aspect). No changes made.")
    sys.exit(0)

# ---- Edit 1: replace the hardcoded ASPECT constant with a channel-aware resolver ----
old_aspect = 'ASPECT = {"width": 1280, "height": 720}   # 16:9'
if old_aspect not in src:
    print("!! Could not find the ASPECT constant line exactly. Aborting so nothing is half-changed.")
    print("   Expected:", old_aspect)
    sys.exit(1)

new_aspect = '''def _channel_aspect():
    """Render resolution from channel.json (width/height), default 1280x720.
    Final Hours has no width/height in its channel.json so it stays 720p;
    Synthetic sets 1920x1080 to match the Mode B Remotion clips."""
    try:
        cfg = load_channel_config(strict=False)
        w = int(cfg.get("width", 1280))
        h = int(cfg.get("height", 720))
        return {"width": w, "height": h}
    except Exception:
        return {"width": 1280, "height": 720}

ASPECT = _channel_aspect()   # 16:9; per-channel via channel.json width/height'''
src = src.replace(old_aspect, new_aspect, 1)

# ---- Edit 2: _still_to_held_clip -vf ----
old_held = ('"-vf", "scale=1280:720:force_original_aspect_ratio=decrease,'
            'pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1",')
new_held = ('"-vf", f"scale={ASPECT[\'width\']}:{ASPECT[\'height\']}:force_original_aspect_ratio=decrease,'
            'pad={ASPECT[\'width\']}:{ASPECT[\'height\']}:(ow-iw)/2:(oh-ih)/2,setsar=1",')
if old_held in src:
    src = src.replace(old_held, new_held, 1)
    print("  edit 2 (held-clip scale) applied")
else:
    print("  !! edit 2 target not found — held-clip scale string differs; check manually")

# ---- Edit 3: assemble() trim -vf (split across two string literals) ----
old_trim = ('"-vf", "scale=1280:720:force_original_aspect_ratio=decrease,"\n'
            '                       "pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",')
new_trim = ('"-vf", f"scale={ASPECT[\'width\']}:{ASPECT[\'height\']}:force_original_aspect_ratio=decrease,"\n'
            '                       f"pad={ASPECT[\'width\']}:{ASPECT[\'height\']}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",')
if old_trim in src:
    src = src.replace(old_trim, new_trim, 1)
    print("  edit 3 (assemble trim scale) applied")
else:
    print("  !! edit 3 target not found — assemble trim string differs; check manually")
    print("     (look for scale=1280:720 inside assemble() and make it f-string from ASPECT)")

open(PATH, "w", encoding="utf-8").write(src)

# verify it still parses
import ast
try:
    ast.parse(src)
    print("\nsyntax OK")
except SyntaxError as e:
    print(f"\n!! SYNTAX ERROR introduced: {e}\n   Restore from git: git checkout {PATH}")
    sys.exit(1)

# show the three regions so the change is visible
print("\n--- resolution references now in the file ---")
for i, line in enumerate(src.splitlines(), 1):
    if "ASPECT" in line or "1280:720" in line or "_channel_aspect" in line:
        print(f"  {i}: {line.strip()[:96]}")
