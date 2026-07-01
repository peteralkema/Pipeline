#!/usr/bin/env python3
"""Master worklog: mark QQrew P0 (Tier-1 #0) DONE and add a RECORD entry for the
01 Jul style_suffix day + the Mercator Ep3 build.

Idempotent: anchors on the Tier-1 #0 P0 backlog line and the '# THE RECORD' /
first '### ' record header. No-ops if the 01 Jul entry marker is present.
"""
import shutil, sys, re
from pathlib import Path

DOC = Path(__file__).resolve().parent / "docs" / "__MASTER-WORKLOG.md"
if not DOC.exists():
    DOC = Path(__file__).resolve().parent.parent / "shared" / "docs" / "__MASTER-WORKLOG.md"

MARKER = "01 July 2026 — @Q-Qrew Ep3 (MERCATOR)"

# Flip the Tier-1 #0 backlog line to DONE (anchor on its start).
P0_ANCHOR = "0. **★★ QQrew P0 — THE PROMPT-CONSTRUCTION FIX (ship-blocks Ep3;"
P0_REPLACE = "0. **✅ DONE 01 Jul 2026 — was a MISDIAGNOSIS. Real fix: channel `style_suffix` content (flat-cel webcomic → semi-realistic bright; `_QQrew.md §4/§6a`). Canon-tag cut shipped too, minor. Mercator Ep3 rendered trio-tier. Full lesson graduated to canonical (style_suffix = highest-leverage look lever; read it FIRST).** ~~★★ QQrew P0 — THE PROMPT-CONSTRUCTION FIX (ship-blocks Ep3;"

RECORD_ENTRY = '''
### 01 July 2026 — @Q-Qrew Ep3 (MERCATOR) BUILD + THE STYLE_SUFFIX DAY

The day the flat-cel doctrine died. Scrapped the contaminated pregnancy1 Ep3 (stylistic grab-bag) and wrote a fresh **Mercator** episode ("The Map On Your Wall Is Lying — Greenland Is Not That Big") — Skeptic solo-lead, 180 beats, ONE coherent visual world (maps only) to structurally prevent the grab-bag failure. 62% Skeptic presence (carries the episode, bookends fixed), crew-absent wides forced people-free to stop the model inventing strangers.

**THE HEADLINE (cost a full day, now banked everywhere):** the Ep3 photoreal-portrait "disaster" was MISDIAGNOSED in the §11 P0 spec. Reading the live code proved the `style_suffix` WAS reaching prompts — the real culprit was its CONTENT: a flat-cel/webcomic string that hard-banned "painterly, semi-realistic, rendered, 3d" and forced a cheap kids-cartoon on every text-to-image beat (the Bambi fawns, the flat skies). **Fix = swap the suffix** (flat-cel → semi-realistic bright). Immediately produced the approved trio-tier look. The canon-tag cut (89w→18w) shipped too but was minor — Skeptic beats route through `/edit`+PNG and bypass the canon. **Second trap same day:** the first swap over-corrected into "painterly/atmospheric/cinematic-grade" and leaked the FH moody register → pouty/sullen Skeptic; corrected to bright/high-key. **§4 fully REVERSED** (flat-cel was wrong; the channel is semi-realistic in FIDELITY, bright/funky in REGISTER; differentiation from FH is register + cast, NOT art style). **Durable lesson graduated to canonical §8:** style_suffix is the highest-leverage lever on look — read it FIRST when renders look wrong; negative suffixes veto the model; register words drag the whole channel incl. faces.

**Also banked:** the two approved Skeptic/crew references (`02_egyptian_tomb`, `08_mughal_india_palace` lineage → `skeptic_ref.png`/`driver_ref.png`, semi-realistic) + the model bake-off verdict (NB2 default / NB-Pro hero-splurge / Seedream disqualified for character drift, conditional on those refs). Reference-render is LIVE, not "deferred." MERCATOR1 shipped on the interim painterly suffix (good enough, not re-rendered); ep4+ uses the bright suffix. Still open on Ep3: finish leg (kling 0 → `reassemble_static.py` + ffmpeg Ken-Burns strip), thumbnail, manual upload (category 27, Altered=Yes), `category_id` "24"→"27".
'''

def main():
    if not DOC.exists():
        print(f"ERROR: worklog not found at {DOC}. Aborting."); return 1
    t = DOC.read_text()
    if MARKER in t:
        print("01 Jul record entry already present. No-op."); return 0
    changed = False
    if P0_ANCHOR in t:
        t = t.replace(P0_ANCHOR, P0_REPLACE, 1)
        changed = True
        print("OK Tier-1 #0 flipped to DONE.")
    else:
        print("WARN: P0 backlog anchor not found — skipping the DONE flip.")
    # Insert record entry right after the '# THE RECORD' header if present,
    # else before the first '### ' dated header.
    if "# THE RECORD" in t:
        idx = t.index('\n', t.index("# THE RECORD")) + 1
        t = t[:idx] + RECORD_ENTRY + t[idx:]
        changed = True
        print("OK record entry inserted after # THE RECORD.")
    else:
        m = re.search(r'^### \d', t, re.M)
        if m:
            t = t[:m.start()] + RECORD_ENTRY.lstrip() + "\n" + t[m.start():]
            changed = True
            print("OK record entry inserted before first dated record.")
        else:
            print("WARN: no RECORD location found — appending.")
            t = t.rstrip() + "\n\n" + RECORD_ENTRY
            changed = True
    if changed:
        shutil.copy2(DOC, DOC.with_suffix(".md.bak_ep3_day"))
        DOC.write_text(t)
        print("written.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
