#!/usr/bin/env python3
"""
patch_mc_stills_ctx_modea.py — point find_beats_file at the modea dir.

The bug (found via /api/animate, but it hits restill + aifix too): _stills_ctx
passed the PROJECT ROOT to find_beats_file, which builds `project_dir/storyboard.json`
-> project root has no storyboard.json (it lives under modea/). The old
serve_review.py worked because it was launched with --project pointing AT the
modea dir; Mission Control resolves the project root, one level up.

But the two helpers want DIFFERENT dirs:
  - find_beats_file needs       modea/   (storyboard.json is there)
  - load_rulebook_negatives needs project root  (its parent.parent must be the
    channel root, where rulebook.json lives — modea would miss it)

Fix: pass paths["modea"] to find_beats_file, keep paths["project"] for negatives.
canon.json stays at project root (unchanged). stills_dir already correct
(paths["stills_dir"] = modea/stills).

One edit. Idempotent (marker), backs up to .pre_ctxmodea.

Run on the box:
  python shared/mission_control/patch_mc_stills_ctx_modea.py --check
  python shared/mission_control/patch_mc_stills_ctx_modea.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

EDITS.append(dict(
    marker='find_beats_file(paths["modea"]',
    old='''    paths = resolve_paths(channel, project, _REPO)
    project_dir = paths["project"]
    beats_file = find_beats_file(project_dir, None)  # storyboard-shaped beats''',
    new='''    paths = resolve_paths(channel, project, _REPO)
    project_dir = paths["project"]
    # storyboard.json lives under modea/ (not project root); find_beats_file
    # builds <dir>/storyboard.json, so give it the modea dir. negatives below
    # still get the project root so their parent.parent hits the channel root.
    beats_file = find_beats_file(paths["modea"], None)  # storyboard-shaped beats''',
))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if not T.is_file():
        sys.exit(f"missing: {T}")
    text = T.read_text()

    plans, fatal = [], []
    for i, e in enumerate(EDITS, 1):
        if e["marker"] in text:
            plans.append((i, "skip-applied")); continue
        n = text.count(e["old"])
        if n == 1: plans.append((i, "apply"))
        elif n == 0: fatal.append(f"edit {i}: ANCHOR NOT FOUND")
        else: fatal.append(f"edit {i}: anchor x{n}")

    print("=== STILLS-CTX MODEA PATCH PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_ctxmodea")
    if not bak.exists():
        bak.write_text(text); print(f"  backup -> {bak.name}")
    for i, e in enumerate(EDITS, 1):
        if i not in to_apply: continue
        text = T.read_text()
        if text.count(e["old"]) != 1:
            print(f"  !! edit {i}: anchor changed — ABORT"); sys.exit(2)
        T.write_text(text.replace(e["old"], e["new"], 1))
        print(f"  applied -> edit {i}")
    print("\n=== DONE === restart: systemctl --user restart mission-control.service")
    print("(clears the _STILLS_CACHE too, so the fixed lookup takes effect)")


if __name__ == "__main__":
    main()
