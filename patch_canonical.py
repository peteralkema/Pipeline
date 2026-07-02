#!/usr/bin/env python3
"""
patch_canonical.py -- add the 2026-07-02 tool-agnostic lesson to the canonical
reference §8 (authoring craft), as the sibling of the already-banked style_suffix
and reference-lock lessons.

Anchored to the §8 style_suffix corollary block. The new lesson: the people_directive
is the THIRD place a reference channel's content is governed, and the anonymous-human
failure is the textbook both-layers-fix moat pattern.

Additive only. Idempotent, backup.
    python3 patch_canonical.py --file shared/docs/__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md
"""
from __future__ import annotations
import argparse, shutil, sys
from pathlib import Path

SENTINEL = "banked 02 Jul 2026, QQrew Fire/ep5"

# Anchor: the last sentence of the §8 style_suffix corollary (from the live grep,
# the reference-lock / pouty-Skeptic line). Append the new lesson right after it.
ANCHOR = "(QQrew 01 Jul: the pouty-Skeptic tell traced to the lock, not the canon tag.)"

ADD = ANCHOR + '''

### ★ THE ANONYMOUS-HUMAN GATE + THE BOTH-LAYERS FIX PATTERN (banked 02 Jul 2026, QQrew Fire/ep5)

A reference-render channel's look/content is governed in a THIRD place beyond the style_suffix and the reference prompt-lock: the rulebook **`people_directive`**, appended to every text-to-image prompt. On a `render_mode:"reference"` channel this actively harms person-free beats — a text-to-image model handed an UNANCHORED human ("a lone figure / silhouette / someone / a huddle / people") renders a **modern smiling cartoon character** and discards the scene, and the people_directive was summoning humans onto clean plates (empty wides, object close-ups, predator-eyes) whose wording missed a narrow no-people phrase-guard. Fire/ep5 first-rendered ~25 stills this way.

**The fix — and the pattern worth repeating (the moat compounding):** a failure class is closed PROPERLY only when fixed on BOTH layers:
- **ENGINE (so it cannot recur regardless of input):** on `render_mode:"reference"`, a beat reaching the text path has no `{tag}` → no reference → it is person-free by definition, so strip the people_directive unconditionally. (`patch_nopeople_default`; supersedes the narrow phrase-guard that missed "no face"/"no clear animal".)
- **AUTHORING (so it is never written in the first place):** a human in frame is a crew member (a `{tag}` → `/edit`) or does not exist; person-free beats carry the humans in narration. Banned words at write time: figure, silhouette, someone, early-human, huddle, a lone X, depicted people.

Neither layer alone is sufficient; both together make the failure structurally impossible. This is the moat thesis in action — **bank a failure as a tool-agnostic principle AND enforce it in the engine.** (Full channel-side doctrine: `_QQrew.md §6b`.)

**Corollary — teaching/human content on a reference channel is DIEGETIC:** put the explainer and the people IN the scene via a crew member's body and props (fingers, ground-writing, a field notebook held to camera), not as abstract graphics or anonymous figures. Hand-drawn in-world text is garble-tolerant by design.'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="shared/docs/__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md")
    a = ap.parse_args()
    t = Path(a.file)
    if not t.is_file():
        print(f"ERROR: not found: {t}", file=sys.stderr); return 2
    src = t.read_text(encoding="utf-8")
    if SENTINEL in src:
        print(f"already applied -> no-op: {t}"); return 0
    if src.count(ANCHOR) != 1:
        print(f"ERROR: §8 anchor found {src.count(ANCHOR)}x (need 1). Refusing.", file=sys.stderr); return 3
    out = src.replace(ANCHOR, ADD, 1)
    b = t.with_suffix(t.suffix + ".pre_0702")
    shutil.copy2(t, b); t.write_text(out, encoding="utf-8")
    print(f"OK patched {t} (backup {b.name}) — anonymous-human gate + both-layers pattern added to §8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
