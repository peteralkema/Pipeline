#!/usr/bin/env python3
"""Canonical: add a one-line note to the style_suffix lesson that register words
also leak into FACIAL EXPRESSION, and that reference-render channels set
character look in the LOCK not the suffix. Idempotent."""
import shutil, sys
from pathlib import Path

DOC = Path(__file__).resolve().parent / "docs" / "__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md"
if not DOC.exists():
    DOC = Path(__file__).resolve().parent.parent / "shared" / "docs" / "__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md"

MARKER = "**Corollary — reference-render channels bypass the suffix for character beats.**"
ANCHOR = "**Corollary — reference-render channels bypass the suffix for character beats.**"

# If the corollary already exists (it was in the first canonical patch), append a
# sharper sentence about the LOCK being the mood lever. Anchor on the corollary
# paragraph's known ending.
OLD_TAIL = "A channel's look is set in TWO places, not one — check both."
NEW_TAIL = ("A channel's look is set in TWO places, not one — check both. **And on a "
            "reference channel the character's MOOD/EXPRESSION lives in the reference "
            "prompt-lock too** — a lock carrying moody-register words (\"painterly, "
            "warm cinematic lighting\") renders the character dreary/sullen no matter "
            "how bright the suffix is. Fix the lock, not just the suffix. (QQrew 01 Jul: "
            "the pouty-Skeptic tell traced to the lock, not the canon tag.)")

def main():
    if not DOC.exists():
        print(f"ERROR: {DOC} not found."); return 1
    t = DOC.read_text()
    if "the character's MOOD/EXPRESSION lives in the reference" in t:
        print("Canonical mood-lock note already present. No-op."); return 0
    if OLD_TAIL not in t:
        print("WARN: corollary tail not found — the first canonical patch may not have run. Skipping."); return 0
    t = t.replace(OLD_TAIL, NEW_TAIL, 1)
    shutil.copy2(DOC, DOC.with_suffix(".md.bak_mood_lock"))
    DOC.write_text(t)
    print("OK canonical mood-lock note appended.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
