#!/usr/bin/env python3
"""Fix REFERENCE_PROMPT_LOCK + TAIL: strip the Final-Hours moody-register leak.

Reference /edit beats ({skeptic}) BYPASS the channel style_suffix -- their ONLY
style instruction is REFERENCE_PROMPT_LOCK + REFERENCE_PROMPT_TAIL. Both hardcode
FH-register words ("painterly rendered skin", "soft warm lighting", "warm
cinematic lighting") -> every Skeptic beat rendered dreary/moody regardless of
the bright suffix. This is the real lever for the pouty, dim Skeptic.

Anchors on the exact multi-line source (parenthesized implicit-concat strings).
Idempotent + py_compile verified.
"""
import shutil, sys, py_compile, tempfile, os
from pathlib import Path

SRC = Path(__file__).resolve().parent / "recreation_pipeline.py"
if not SRC.exists():
    SRC = Path(__file__).resolve().parent.parent / "shared" / "recreation_pipeline.py"

OLD_LOCK = '''REFERENCE_PROMPT_LOCK = (
    "Use the reference image(s) as the exact visual template. Preserve their art "
    "style precisely -- semi-realistic cinematic illustration, soft warm lighting, "
    "painterly rendered skin, clean rich illustrated backgrounds. If a reference shows "
    "a person, keep that EXACT character: same face, same hair, same wardrobe, same "
    "personality; do not change their identity. Do not change the art style. "
    "Render this new scene: "
)'''

NEW_LOCK = '''REFERENCE_PROMPT_LOCK = (
    "Use the reference image(s) as the exact visual template for the CHARACTER: "
    "keep that EXACT person -- same face, same hair, same wardrobe; do not change "
    "their identity. Render in a semi-realistic modern animated-feature illustration "
    "style: bright high-key lighting, vibrant saturated color, crisp clean detail, "
    "rich detailed backgrounds, lots of light and energy, lively and appealing. The "
    "character is bright, engaged and lively with a warm easy half-smile -- never "
    "bored, never pouty, never flat. Render this new scene: "
)'''

OLD_TAIL = '''REFERENCE_PROMPT_TAIL = (
    " Rich illustrated background, warm cinematic lighting, 16:9 wide composition, "
    "no on-image text, no letters, no captions."
)'''

NEW_TAIL = '''REFERENCE_PROMPT_TAIL = (
    " Rich detailed background, bright high-key lighting, vibrant color, 16:9 wide "
    "composition, no on-image text, no letters, no captions."
)'''


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: {SRC} not found."); return 1
    t = SRC.read_text()
    if NEW_LOCK in t and NEW_TAIL in t:
        print("Already patched (bright lock + tail present). No-op."); return 0
    changed = t
    hits = 0
    if OLD_LOCK in changed:
        changed = changed.replace(OLD_LOCK, NEW_LOCK, 1); hits += 1
    else:
        print("WARN: OLD_LOCK not found verbatim.")
    if OLD_TAIL in changed:
        changed = changed.replace(OLD_TAIL, NEW_TAIL, 1); hits += 1
    else:
        print("WARN: OLD_TAIL not found verbatim.")
    if hits < 2:
        print(f"ERROR: matched {hits}/2 -- refusing partial apply. Aborting."); return 1
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(changed); tmp = f.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: would not compile: {e}. Aborting."); os.unlink(tmp); return 1
    os.unlink(tmp)
    shutil.copy2(SRC, SRC.with_suffix(".py.bak_ref_lock_bright"))
    SRC.write_text(changed)
    print("OK reference LOCK+TAIL de-mooded (2/2 replaced, backup written).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
