#!/usr/bin/env python3
"""_QQrew.md §4 FULL REVERSAL: flat-cel -> semi-realistic bright animated-feature.

01 Jul 2026. The flat-cel doctrine was the bug that cost a full day: the
channel.json style_suffix ordered a flat 2D webcomic cartoon on every
text-to-image beat (Bambi fawns, flat skies) — the opposite of the approved
trio references (02_egyptian_tomb / 08_mughal_india_palace). Fixed by swapping
the suffix to semi-realistic bright animated-feature. The channel's
differentiation from Final Hours is NOW register + recurring cast, NOT art style
— both are semi-realistic; QQrew is the BRIGHT one.

Idempotent: anchors on the exact v1.0 §4 block; no-ops if already reversed.
"""
import shutil, sys
from pathlib import Path

DOC = Path(__file__).resolve().parent / "docs" / "_QQrew.md"
if not DOC.exists():
    DOC = Path(__file__).resolve().parent.parent / "shared" / "docs" / "_QQrew.md"

OLD = '''## 4. STYLE (kid-validated, 4 independent signals)

**PRODUCED FLAT CEL-SHADED ILLUSTRATION.** Clean dark linework, simplified flat color planes, appealing stylized faces, rich illustrated backgrounds, warm lighting. Firmly on the illustrated side — the production polish is the differentiation.

**EXPLICITLY NOT photorealistic, NOT 3D, NOT realistic-skin.** Photoreal drift is the failure mode: it reads "Final Hours," invites AI-realism artifacts (warped straps, stubble), and is wrong for the register. The style suffix must steer DECISIVELY flat-cel and negative the realism.

**Backgrounds are a first-class element** — half the appeal (kid-confirmed twice). Rich, warm, detailed, inviting. Never bare. The crew always stands somewhere worth visiting.

**channel.json style_suffix (current, proven):**
> "clean flat 2D cel-shaded illustration, confident dark linework, simplified flat color planes, smooth animated-feature style, appealing stylized characters, rich illustrated background, warm lighting, vibrant color, NOT photorealistic, NOT 3d render, NOT realistic skin texture, bright and inviting, no text, no letters, 16:9"'''

NEW = '''## 4. STYLE (REVERSED 01 Jul 2026 — flat-cel was the bug)

**PRODUCED SEMI-REALISTIC BRIGHT ANIMATED-FEATURE ILLUSTRATION.** Appealing realistic detailed faces, rich detailed illustrated backgrounds, real depth, high detail, polished animated-feature quality — the fidelity of the approved trio references (`02_egyptian_tomb.png`, `08_mughal_india_palace.png`). This is the tier the audience will actually click.

**Semi-realistic in FIDELITY, bright/funky in REGISTER.** The look is REAL (real faces, real depth, rich backgrounds) but the register is bright, funky, fun, choppy, dynamic, high-key, vibrant, energetic, lots of light. **Explicitly ANTI-dark, ANTI-candlelight, ANTI-Victorian, ANTI-painterly, ANTI-moody-cinematic.** Register words like "painterly / atmospheric / cinematic color grade / soft shading" leak the Final-Hours dread register in through the back door — they drag the whole channel moody, INCLUDING facial expression (a moody-lit Skeptic reads as sullen/pouty, not wry). Keep the fidelity words, ban the register words.

**Backgrounds are a first-class element** — half the appeal. Rich, warm, detailed, inviting, bright. Never bare. The crew always stands somewhere worth visiting.

**channel.json style_suffix (CURRENT — bright, ep4+):**
> "semi-realistic modern animated-feature illustration, appealing realistic detailed faces, rich detailed illustrated backgrounds, bright high-key lighting, vibrant saturated color, crisp clean and dynamic, lots of light and energy, polished animated-feature quality, high detail, inviting and fun, no text, no letters, 16:9"

**⚰ TOMBSTONE — the flat-cel suffix (v1.0, WRONG, cost a full day 01 Jul):**
> ~~"clean flat 2D cel-shaded illustration … NOT photorealistic, NOT 3d render, NOT realistic skin texture …"~~ — a NEGATIVE suffix that hard-banned "painterly, semi-realistic, rendered, 3d" and forced a flat 2D webcomic cartoon on every text-to-image beat (the Bambi fawns, the flat skies). Read as a cheap kids' show; would have tanked CTR. The interim over-correction ("semi-realistic cinematic painterly … warm cinematic color grade, atmospheric depth") fixed the cartoon but leaked the FH moody register → the pouty-Skeptic tell. The MERCATOR1 render (01 Jul, Ep3) shipped on that interim painterly suffix — good enough, not re-rendered; ep4+ uses the bright suffix above. **See §6a for the full misdiagnosis chain.**'''

def main():
    if not DOC.exists():
        print(f"ERROR: _QQrew.md not found at {DOC}. Aborting."); return 1
    t = DOC.read_text()
    if NEW.split("\n")[0] in t:
        print("Already reversed (§4 shows REVERSED header). No-op."); return 0
    if OLD not in t:
        print("ERROR: exact v1.0 §4 block not found — doc drifted. Aborting, will not guess."); return 1
    shutil.copy2(DOC, DOC.with_suffix(".md.bak_s4_reversal"))
    DOC.write_text(t.replace(OLD, NEW))
    print(f"OK §4 reversed to semi-realistic bright (backup written).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
