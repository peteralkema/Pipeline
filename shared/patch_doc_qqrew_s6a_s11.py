#!/usr/bin/env python3
"""_QQrew.md §6a + §11 P0: correct the Ep3 misdiagnosis and mark P0 RESOLVED.

The v1.0 §6a/§11 doctrine blamed the photoreal-portrait failure on (1) missing
style_suffix and (2) the 120-word canon eating the prompt. 01 Jul proved that was
the WRONG primary. Real chain:
  - the style_suffix WAS reaching prompts (lines 608-609) — but it was a
    flat-cel/webcomic suffix that BANNED painterly/semi-realistic/rendered,
    forcing a kids-cartoon. THAT was the disaster, not a missing suffix.
  - the canon-tag cut (89w -> 18w) was real but MINOR — Skeptic beats route
    through /edit + the reference PNG and bypass the canon entirely; the canon
    only bites on a flux fallback.
  - the FIX was replacing the suffix (flat-cel -> semi-realistic bright).

Appends a correction block to §6a and flips §11 P0 to RESOLVED. Idempotent.
"""
import shutil, sys
from pathlib import Path

DOC = Path(__file__).resolve().parent / "docs" / "_QQrew.md"
if not DOC.exists():
    DOC = Path(__file__).resolve().parent.parent / "shared" / "docs" / "_QQrew.md"

# Anchor: the §6a doctrine bold line (present in v1.0).
S6A_ANCHOR = "**This is what separated Ep1 (good) from Ep3 (bad):**"
S6A_ADDENDUM = '''**★ CORRECTION (01 Jul 2026 — the misdiagnosis, banked after a full day lost).** The two-fault theory above was HALF WRONG on the primary cause. What actually happened, proven by reading the live code + config:
- **The `style_suffix` WAS reaching the prompts** (`recreation_pipeline.py` lines 608-609 / 645 build `full_prompt = f"{style_suffix}. {image_prompt}"`). Fault 1 ("suffix not appended") was NOT the live fault.
- **The real disaster was the CONTENT of the suffix:** it was a flat-cel / webcomic string that HARD-BANNED "painterly, semi-realistic, rendered, 3d" — so it FORCED a cheap 2D kids-cartoon on every text-to-image beat (the Bambi fawns, the flat skies). The model was never failing; the suffix was vetoing its best output.
- **The canon-tag cut (89w → 18w) was correct but MINOR.** Skeptic beats route through the reference `/edit` path + `skeptic_ref.png` and BYPASS the channel canon entirely; the canon only bites if a `{skeptic}` beat falls to the flux fallback. So Fault 2 ("canon eats the prompt") barely applies on a reference-render channel.
- **THE FIX:** replace the suffix (flat-cel → semi-realistic bright — see §4). Immediately produced the approved trio-tier look. **Second trap found same day:** the first replacement over-corrected into "painterly / atmospheric / cinematic color grade" and leaked the Final-Hours moody register → sullen/pouty Skeptic faces; corrected to bright/high-key (§4).
- **THE DURABLE LESSON (graduated to canonical):** the `style_suffix` is the single highest-leverage lever on channel look. **When renders look wrong, READ THE ACTUAL SUFFIX FIRST — before canon, script, or references.** A negative suffix that bans qualities silently vetoes the model; register words (painterly/atmospheric/cinematic) drag the whole channel — including facial expression — toward that register.

'''

# Anchor: the §11 P0 opening bold (present in v1.0).
S11_ANCHOR = "0. **★★ P0 — THE PROMPT-CONSTRUCTION FIX (highest; blocks all quality;"
S11_PREFIX = "0. **✅ RESOLVED 01 Jul 2026 — P0 was a MISDIAGNOSIS; real fix was the style_suffix content (flat-cel → semi-realistic bright, §4/§6a). The canon-tag cut shipped too but was minor. Ep3 (MERCATOR) then rendered trio-tier. Left below for the diagnostic trail.** ★★ P0 — THE PROMPT-CONSTRUCTION FIX (highest; blocks all quality;"

def main():
    if not DOC.exists():
        print(f"ERROR: {DOC} not found."); return 1
    t = DOC.read_text()
    changed = False
    if "CORRECTION (01 Jul 2026 — the misdiagnosis" in t:
        print("§6a addendum already present.")
    elif S6A_ANCHOR in t:
        t = t.replace(S6A_ANCHOR, S6A_ADDENDUM + S6A_ANCHOR, 1)
        changed = True
        print("OK §6a correction block inserted.")
    else:
        print("WARN: §6a anchor not found — skipping §6a (doc drifted).")
    if "✅ RESOLVED 01 Jul 2026 — P0 was a MISDIAGNOSIS" in t:
        print("§11 P0 already marked resolved.")
    elif S11_ANCHOR in t:
        t = t.replace(S11_ANCHOR, S11_PREFIX, 1)
        changed = True
        print("OK §11 P0 marked RESOLVED.")
    else:
        print("WARN: §11 P0 anchor not found — skipping (doc drifted).")
    if changed:
        shutil.copy2(DOC, DOC.with_suffix(".md.bak_s6a_s11"))
        DOC.write_text(t)
        print("written.")
    else:
        print("no changes.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
