# -*- coding: utf-8 -*-
# patch_sacreddawn_timing.py
# G3/G4 reconcile on shared/docs/_Sacred-Dawn.md: Elliot WPM 143 -> 159 (the value
# _LEGO.md S0.0 already declares as the shipping model), and flag the retired
# per-block ~430-word model. This unblocks Step 4 (VO) -- narration renders at the
# WPM the calibrate pass then measures against; a stale 143 makes pass one fight you.
#
# IF your actual re-measure of Elliot differs from 159, change WPM_NEW below and re-run
# (it is idempotent by content: it only edits lines still carrying "143").
#
# G22 dogfood: no argument -> self-locate repo root, target canonical path. Arg overrides.
# Idempotent, anchor-verified (each exact stale string), .pre_ backup, ASCII payload.
import io, os, sys

CANON_REL = "shared/docs/_Sacred-Dawn.md"
WPM_NEW = "159"

# (exact stale anchor) -> (exact replacement).  Anchors are ASCII substrings unique
# to their line; payloads are ASCII.
EDITS = [
    # S10 config-facts line
    ("measured **143 WPM** at speed 1.0.",
     "measured **" + WPM_NEW + " WPM** at speed 1.0 (supersedes the earlier 143; "
     "re-measured -- see _LEGO.md section 0.0)."),
    # S6 strategy line: fix the number
    ("**143 WPM** (measured)",
     "**" + WPM_NEW + " WPM** (measured)"),
    # S6 strategy line: flag the retired per-block ~430 model
    ("script each block to **~430 words** (~3:00 of speech, ~15s breathing room).",
     "script each block to **~430 words** (~3:00 of speech, ~15s breathing room). "
     "[TIMING SUPERSEDED by _LEGO.md section 0.0: the shipping model is ONE continuous "
     "whole-film narration.txt and a ~6-13 word/beat band calibrated to the 200s seams, "
     "not a per-block ~430-word target.]"),
]


def repo_root(start="."):
    p = os.path.abspath(start)
    while p != "/":
        if os.path.isdir(os.path.join(p, ".git")):
            return p
        p = os.path.dirname(p)
    return None


def resolve_target():
    if len(sys.argv) > 1:
        return sys.argv[1]
    root = repo_root()
    return os.path.join(root, CANON_REL) if root else CANON_REL


def main():
    target = resolve_target()
    if not os.path.exists(target):
        print("ERROR: target not found:", target, "(pass a path to override)"); sys.exit(1)
    src = io.open(target, encoding="utf-8").read()

    for _, new in EDITS:
        try:
            new.encode("ascii")
        except UnicodeEncodeError as e:
            print("ERROR: payload not ASCII:", e); sys.exit(1)

    applied = skipped = 0
    out = src
    for old, new in EDITS:
        if new in out:
            skipped += 1; continue          # desired end-state already present -> idempotent
        if old not in out:
            print("ERROR: anchor not found (doc diverged?):", repr(old[:40])); sys.exit(1)
        if out.count(old) != 1:
            print("ERROR: anchor not unique:", repr(old[:40]), "count=", out.count(old)); sys.exit(1)
        out = out.replace(old, new, 1); applied += 1

    if applied == 0:
        print("skipped: already reconciled (idempotent) ->", target); return
    io.open(target + ".pre_timing", "w", encoding="utf-8").write(src)
    io.open(target, "w", encoding="utf-8").write(out)
    print(f"applied={applied} skipped={skipped}  WPM->{WPM_NEW}  ->", target)


if __name__ == "__main__":
    main()
