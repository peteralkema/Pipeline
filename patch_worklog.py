#!/usr/bin/env python3
"""
patch_worklog.py -- prepend the 2026-07-02 Fire entry to __MASTER-WORKLOG.md's
THE RECORD (newest-first), matching the existing dated-### entry format.

Anchored to "# THE RECORD (compressed, newest first)" — inserts the new entry
immediately after that header, above the 01 July entry. Idempotent, backup.
    python3 patch_worklog.py --file shared/docs/__MASTER-WORKLOG.md
"""
from __future__ import annotations
import argparse, shutil, sys
from pathlib import Path

SENTINEL = "### 02 July 2026 — @Q-Qrew Ep5 (FIRE) SHIPPED"
ANCHOR = "# THE RECORD (compressed, newest first)"

ENTRY = '''# THE RECORD (compressed, newest first)

### 02 July 2026 — @Q-Qrew Ep5 (FIRE) SHIPPED + the anonymous-human failure class CLOSED + the flat-colour thumbnail method

Brain's solo debut. **Fire** ("Why Early Humans Would've Died Without Fire") — 155 beats, ~6-7 min, uploaded private to @Q-Qrew. First episode authored FROM doctrine, not memory. Project `qqrew/projects/fire1/modea` (the `1` suffix = the v2 grammar rewrite; `fire` = dead v1 — **fingerprint projects by content, never by name**, bit us twice now incl. maracanazo1).

**THE HEADLINE (the core lesson, now banked both layers):** Fire first-rendered with ~25 stills as MODERN CARTOON PEOPLE — beanie kids, cafe strangers, one beat put the real scene in a thought-bubble. Root cause: **NB2 text-to-image renders any UNANCHORED human as a modern cartoon character**, and the rulebook `people_directive` was being stapled onto person-free beats whose wording ("no face", "no clear animal") slipped the narrow phrase-guard. **Closed on BOTH layers:** (1) ENGINE — `patch_nopeople_default`: on a reference channel, a text-path beat has no ref → is person-free by definition → strip the people_directive unconditionally (cannot be defeated by wording); (2) AUTHORING — the v2 rewrite removed every anonymous-human beat (→ crew `/edit` beat or person-free landscape, narration carries the humans). **This is the moat pattern: a failure closed on the engine layer AND the authoring layer is structurally impossible to recur. Fire is the last script that can hit this class.** Banked to `_QQrew.md §6b` + canonical §8.

**Diegetic-teaching upgrade (fell out of the bug):** abstract flat teaching-graphics JAR against immersive scenes → teaching is now IN-SCENE by default via crew body/props — fingers, sand/dirt-writing, twigs, and ★ **Brain's FIELD NOTEBOOK** (jots a finding, holds to camera; her signature). Notebook is garble-tolerant BY DESIGN — hand-drawn field-notes are meant to be loose, so NB2 text-garble reads as authentic. Proven: the notebook renders were a highlight.

**Thumbnail method PROVEN — direct-render on flat colour, NOT cutout-composite.** We over-built first (a `solid_color_character` rembg-cut+composite mode, 4 patches, positioning bugs) — then Peter's question "how did the reference thumbs get it perfect?" reframed it: they were generated directly ON the solid colour in one shot. `make_character_ref.py --ref brain_ref.png --prompt "...on a solid flat [colour] background..."` → existing `low_silhouette` text overlay. Excellent result. The cutout mode is DEAD CODE (retire); `--composition`/`--bg-color` CLI flags kept. Banked `_QQrew.md §8`.

**Brain fully specced:** Lauren @1.0 EXPRESSIVE; discovery epistemology (arc engine: Driver=action, Skeptic=proof, Brain=discovery); inward self-deprecating humour ("that floored me") vs Skeptic's outward; contact beats + notebook; grandma-texture (1/ep); canon warmed vs the flat-expression trap.

**Also banked:** the 01 Jul "all-NB2" decision was DOCTRINE-only — `image_model` was still v1 in config until tonight (`patch_nb2_text` implemented it). Ops lessons: anchor patches to LIVE box code (a patch REFUSED tonight on a stale anchor — the check saved us); engine caches config+module at launch (relaunch/restill fresh to pick up patches; never restart the review service mid-render — cgroup teardown kills the run); `restill --project <dir>/modea --shot N` uses ENGINE shot index, not the MC gate's beat-label; Fix-this-image repairs defects but can't beat a genre prior or fix object-word language.

**OPEN / NEXT:** MC "Generate 5 poses" button (design locked — direct-render path); Salt (ep6) held for Fire's 48h CTR+AVD, inherits full grammar → should render clean first-pass; fold the two `_qqrew_*_DRAFT.md` into `_QQrew.md` and delete; retire `solid_color_character` dead code; confirm upload API 2nd-thumbnail (prior: no, Test & Compare is Studio-side).'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="shared/docs/__MASTER-WORKLOG.md")
    a = ap.parse_args()
    t = Path(a.file)
    if not t.is_file():
        print(f"ERROR: not found: {t}", file=sys.stderr); return 2
    src = t.read_text(encoding="utf-8")
    if SENTINEL in src:
        print(f"already applied -> no-op: {t}"); return 0
    if src.count(ANCHOR) != 1:
        print(f"ERROR: THE RECORD anchor found {src.count(ANCHOR)}x (need 1). Refusing.", file=sys.stderr); return 3
    out = src.replace(ANCHOR, ENTRY, 1)
    b = t.with_suffix(t.suffix + ".pre_0702")
    shutil.copy2(t, b); t.write_text(out, encoding="utf-8")
    print(f"OK patched {t} (backup {b.name}) — Fire entry prepended to THE RECORD")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
