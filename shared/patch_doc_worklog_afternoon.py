#!/usr/bin/env python3
"""Master worklog: append the 01 Jul AFTERNOON work to today's record entry +
update the Ep3 close-out list. Idempotent."""
import shutil, sys
from pathlib import Path

DOC = Path(__file__).resolve().parent / "docs" / "__MASTER-WORKLOG.md"
if not DOC.exists():
    DOC = Path(__file__).resolve().parent.parent / "shared" / "docs" / "__MASTER-WORKLOG.md"

MARKER = "**AFTERNOON (same day) — the render-config gauntlet"
# Anchor: end of the morning record entry's last sentence (the category_id line).
ANCHOR = 'Still open on Ep3: finish leg (kling 0 → `reassemble_static.py` + ffmpeg Ken-Burns strip), thumbnail, manual upload (category 27, Altered=Yes), `category_id` "24"→"27".'

APPEND = ANCHOR + '''

**AFTERNOON (same day) — the render-config gauntlet (four more fixes after the suffix reversal).** The §4 suffix swap fixed the cartoon but four more faults surfaced, all now banked to `_QQrew.md §4b`: (1) **interim→bright suffix** — the first swap over-corrected into "painterly/atmospheric/cinematic-grade" and leaked the FH moody register (dreary scenes + pouty Skeptic); corrected to bright/high-key/vibrant. (2) **ALL-NB2 standardisation** (QQrew-only) — dropped the flux/nano_banana model mixing; one model family (NB2 `/edit` for character, NB2 text for wides) for a consistent look; the optionality wasn't worth the friction. (3) **aspect-ratio bug** — NB2 wants `aspect_ratio` STRING, flux wants `image_size` DICT; wrong form → 1024² square, and `/edit` echoed the portrait `skeptic_ref.png` → portrait stills. Fixed per-model; NB2 rounds to ~1344-1376 wide so **`enforce_16x9.py` is the post-render pixel-exact pass** (or assemble scale-to-frame). (4) **the reference LOCK is the real lever for character beats** — `/edit` beats bypass the style_suffix; `REFERENCE_PROMPT_LOCK`+`TAIL` hardcoded "painterly rendered skin / warm cinematic lighting" → dreary+pouty Skeptic; de-mooded to bright + "never bored/pouty/flat." (5) Skeptic canon expression deadpan→"bright engaged, warm easy half-smile, sharp and lively." **Probe confirmed all four: bright, consistent NB2 look, 16:9, Skeptic smiling.** Ep3 close-out now also includes an `enforce_16x9.py` pass before assemble.'''

def main():
    if not DOC.exists():
        print(f"ERROR: {DOC} not found."); return 1
    t = DOC.read_text()
    if MARKER in t:
        print("Afternoon append already present. No-op."); return 0
    if ANCHOR not in t:
        print("ERROR: morning-entry anchor not found — doc drifted. Aborting."); return 1
    t = t.replace(ANCHOR, APPEND, 1)
    shutil.copy2(DOC, DOC.with_suffix(".md.bak_pm"))
    DOC.write_text(t)
    print("OK worklog afternoon append written.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
