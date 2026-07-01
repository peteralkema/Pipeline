#!/usr/bin/env python3
"""_QQrew.md — capture the 01 Jul AFTERNOON work (post-§4-reversal):
all-NB2 standardization, the aspect-ratio bug/fix, the reference-lock finding,
and the Skeptic expression canon. Inserts a new consolidated block after §4's
TOMBSTONE (before '## 5'), plus a one-line expression note in §7.

Idempotent: no-ops if the afternoon marker is present.
"""
import shutil, sys
from pathlib import Path

DOC = Path(__file__).resolve().parent / "docs" / "_QQrew.md"
if not DOC.exists():
    DOC = Path(__file__).resolve().parent.parent / "shared" / "docs" / "_QQrew.md"

MARKER = "### ★ 4b. THE AFTERNOON FIXES (01 Jul — render config, banked)"

# Anchor: the blank line + '## 5. THE SCRIPT' that follows §4.
ANCHOR = "\n---\n\n## 5. THE SCRIPT (the moat — script is king)"

BLOCK = '''
### ★ 4b. THE AFTERNOON FIXES (01 Jul — render config, banked)

The §4 suffix reversal was necessary but not sufficient. Four more render-config faults surfaced the same day and were fixed; all four must hold for the channel to render right.

**1. STANDARDISED ON ALL-NB2 (QQrew-only decision).** The channel previously mixed models: NB2 `/edit` for character beats, but `image_model:"nano_banana"` text-to-image for crew-absent beats, with flux as a fallback — and briefly flux for the wides. The mixing caused an aspect-ratio split AND risked a look/texture mismatch between the wides and the character beats. **Decision: one model family — NB2 for everything.** NB2 `/edit` (reference) for `{skeptic}` beats, NB2 text-to-image (`fal-ai/nano-banana`) for crew-absent beats. `image_model:"nano_banana"` in channel.json. The optionality wasn't worth the friction; one model = consistent look across all 180.

**2. THE ASPECT-RATIO BUG (the size param differs by endpoint).** NB2 and flux take DIFFERENT size params, and passing the wrong form silently defaults to 1024×1024 square:
- **NB2 (both `/edit` and text-to-image)** wants `aspect_ratio: "16:9"` (a STRING). It IGNORES an `image_size: {width,height}` dict.
- **flux** wants `image_size: ASPECT` (the DICT). 
- **The bug:** the reference `/edit` path passed only the string but NB2 `/edit` still echoed the PORTRAIT reference PNG's proportions (the `skeptic_ref.png` is 174×450 portrait) → portrait stills. The text path passed the dict to NB2 → square stills. **The fix:** `/edit` path now also sends `image_size: ASPECT` (belt+braces); text path branches per model (NB2 → `aspect_ratio` string, flux → dict). See `patch_ref_image_size.py` + `patch_all_nb2_aspect.py`.
- **Residual:** NB2 rounds "16:9" to its own supported buckets (~1344×768 or 1376×768, ratios 1.75–1.79) — visually 16:9 but not pixel-exact 1280×720. **`enforce_16x9.py` is the post-render pass** that normalises every still to exactly 1280×720 before assemble (pad-to-fit, no crop). Run it after every render, OR rely on assemble's scale-to-frame. Do NOT chase pixel-exact at the endpoint — NB2 won't give it.

**3. THE REFERENCE LOCK IS THE REAL LEVER FOR CHARACTER BEATS (look AND mood).** Reference `/edit` beats BYPASS the channel `style_suffix` entirely — their only style instruction is `REFERENCE_PROMPT_LOCK` + `REFERENCE_PROMPT_TAIL` (in `recreation_pipeline.py`). These hardcoded the FH moody register ("painterly rendered skin", "soft warm lighting", "warm cinematic lighting") → every Skeptic beat rendered dreary AND pouty regardless of the bright suffix. **This is why the suffix work never fixed her face.** The lock is now de-mooded: identity-hold + "semi-realistic modern animated-feature, bright high-key lighting, vibrant color … the character is bright, engaged and lively with a warm easy half-smile — never bored, never pouty, never flat." **Durable rule: on a reference-render channel, the character's look AND expression live in the LOCK, not the suffix and not only the canon tag. Fix the lock first.**

**4. SKEPTIC EXPRESSION CANON.** `base_canon.skeptic` ended "dry deadpan expression" → rendered bored/pouty (the Gen-Z-deadpan-that-reads-as-sulking trap). Changed to "bright engaged expression with a warm easy half-smile, sharp and lively." Keeps her sharp/wry without a goofy grin; the crack-once deadpan character is carried by writing, not by a flat resting face.
'''

def main():
    if not DOC.exists():
        print(f"ERROR: {DOC} not found."); return 1
    t = DOC.read_text()
    if MARKER in t:
        print("Afternoon block already present. No-op."); return 0
    if ANCHOR not in t:
        print("ERROR: §4→§5 anchor not found — doc drifted. Aborting."); return 1
    t = t.replace(ANCHOR, "\n" + BLOCK + ANCHOR, 1)
    shutil.copy2(DOC, DOC.with_suffix(".md.bak_afternoon"))
    DOC.write_text(t)
    print("OK §4b afternoon-fixes block inserted.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
