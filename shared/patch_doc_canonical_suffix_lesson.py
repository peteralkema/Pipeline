#!/usr/bin/env python3
"""Canonical reference: graduate the durable, channel-agnostic debugging lesson
from the 01 Jul QQrew style_suffix day.

THE LESSON: style_suffix is the highest-leverage lever on channel LOOK. When
renders look wrong, read the actual suffix FIRST — before canon, script, refs.
A NEGATIVE suffix (banning qualities) silently vetoes the model's best output; a
suffix carrying REGISTER words (painterly/atmospheric/cinematic-grade) drags the
whole channel — including facial expression — toward that register.

Inserts a §8 mechanics entry. Idempotent — anchors on the §8 header; no-ops if
the lesson marker is already present.
"""
import shutil, sys
from pathlib import Path

DOC = Path(__file__).resolve().parent / "docs" / "__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md"
if not DOC.exists():
    DOC = Path(__file__).resolve().parent.parent / "shared" / "docs" / "__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md"

MARKER = "STYLE_SUFFIX IS THE HIGHEST-LEVERAGE LEVER ON LOOK"

LESSON = '''
### ★ STYLE_SUFFIX IS THE HIGHEST-LEVERAGE LEVER ON LOOK (banked 01 Jul 2026, QQrew — cost a full day)

The channel.json `style_suffix` is prepended to every text-to-image prompt (`recreation_pipeline.py` ~608-609/645: `full_prompt = f"{style_suffix}. {image_prompt}"`). It is the single strongest control over how a channel LOOKS — stronger than the per-beat VISUAL line, because it leads the prompt and the image model weights the front heaviest.

**The debugging rule (this is the graduated lesson):** when a channel's renders look wrong — wrong style, wrong tier, wrong mood — **READ THE ACTUAL `style_suffix` FIRST**, before touching canon, script, or reference images. A full day was lost on QQrew Ep3 patching canon strings, references, palace-anchors and flux-fallbacks while the real culprit was one config line: a flat-cel/webcomic suffix that hard-banned "painterly, semi-realistic, rendered, 3d" and forced a cheap kids-cartoon on every beat.

**Two failure modes of a bad suffix:**
1. **A NEGATIVE suffix silently vetoes the model.** "NOT photorealistic, NOT rendered, NOT painterly" doesn't just nudge — it bans the model's best output. The model was never failing; the suffix forbade quality.
2. **Register words leak a whole register — including faces.** Words like "painterly / atmospheric depth / warm cinematic color grade / soft shading" drag the entire channel toward a moody-cinematic register, and a moody-lit character reads as sullen. On QQrew this produced a pouty, bored Skeptic — the opposite of her wry character — purely from suffix wording. **Separate FIDELITY words (semi-realistic, detailed faces, rich backgrounds, depth) from REGISTER words (bright/high-key vs moody/painterly); tune them independently.**

**Corollary — reference-render channels bypass the suffix for character beats.** When `render_mode:"reference"`, `{tag}` beats route through `/edit` + the character PNG and do NOT receive the style_suffix (by design — the PNG carries the look). So the suffix governs the CREW-ABSENT/text-to-image beats; the reference PNG governs the character beats. A channel's look is set in TWO places, not one — check both.

'''

def main():
    if not DOC.exists():
        print(f"ERROR: canonical not found at {DOC}. Aborting."); return 1
    t = DOC.read_text()
    if MARKER in t:
        print("Lesson already present. No-op."); return 0
    # Insert after the "## 8" section header if present, else append.
    import re
    m = re.search(r'^## 8\b.*$', t, re.M)
    if m:
        idx = t.index('\n', m.end())
        t = t[:idx+1] + LESSON + t[idx+1:]
        where = "after §8 header"
    else:
        t = t.rstrip() + "\n\n" + LESSON
        where = "appended (no §8 header found)"
    shutil.copy2(DOC, DOC.with_suffix(".md.bak_suffix_lesson"))
    DOC.write_text(t)
    print(f"OK canonical suffix-lesson inserted ({where}).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
