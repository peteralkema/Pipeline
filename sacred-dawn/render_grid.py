#!/usr/bin/env python3
"""
render_grid.py -- render the variant grid for manual pick review.

Reuses the shared engine's generate_still WITHOUT modifying it: generate_still
resolves the channel config, style_suffix and rulebook negatives from the OUTPUT
PATH, so writing into sacred-dawn/projects/<project>/stills/ picks up Sacred Dawn's
grade and the 17 channel negatives automatically.

Per beat it renders `variants` real re-rolls (same prompt; nano_banana_2's
non-determinism yields different frames) named <beat>-<v>.png, then fills the rest
of the 4-slot with copies of the skip tile. Everything lands in ONE folder; the
filename <beat>-<v> maps straight back to GRID-INDEX.csv. Resume-safe: existing
files are skipped unless --force.

Place this in the sacred-dawn CHANNEL dir. Run it from there:

    python render_grid.py --beats projects/moon-grid-finish/beats.json \\
                          --project moon-grid-finish

802 real fal calls (~$64) + 478 skip copies ($0). Use tmux.
"""
import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED = HERE.parent / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

import recreation_pipeline as rp  # noqa: E402


def resolve_skip_tile(explicit, beats_path):
    if explicit:
        p = Path(explicit).expanduser()
        if not p.is_file():
            sys.exit(f"--skip-tile not found: {p}")
        return p
    proj = beats_path.parent
    for cand in (proj / "_skip.png", proj.parent / "_skip.png", Path.cwd() / "_skip.png"):
        if cand.is_file():
            return cand
    return None


def main():
    ap = argparse.ArgumentParser(description="Render the variant grid (manual pick).")
    ap.add_argument("--beats", required=True, help="grid beats.json from build_moon.py grid")
    ap.add_argument("--project", required=True, help="project name, e.g. moon-grid-finish")
    ap.add_argument("--skip-tile", default=None, help="path to _skip.png (auto-found if omitted)")
    ap.add_argument("--force", action="store_true", help="re-render stills already on disk")
    args = ap.parse_args()

    beats_path = Path(args.beats).expanduser().resolve()
    if not beats_path.is_file():
        sys.exit(f"beats.json not found: {beats_path}")

    beats, canon = rp._load_beats_with_canon(beats_path)
    stills = (beats_path.parent / "stills")
    stills.mkdir(parents=True, exist_ok=True)

    needs_skip = any(int(b.get("variants") or 4) < 4 for b in beats)
    skip = resolve_skip_tile(args.skip_tile, beats_path)
    if needs_skip and skip is None:
        sys.exit("connective beats need a skip tile but _skip.png was not found. "
                 "Pass --skip-tile PATH or place _skip.png in the project folder.")

    real_total = sum(int(b.get("variants") or 4) for b in beats)
    print(f"Grid: {len(beats)} beats | {real_total} real stills + "
          f"{len(beats) * 4 - real_total} skip tiles | skip tile: {skip}")

    rendered = filled = skipped_existing = 0
    for i, b in enumerate(beats, 1):
        prompt = rp._expand_canon(b["image_prompt"].strip(), canon)
        n = int(b.get("variants") or 4)
        for v in range(1, 5):
            out = stills / f"{i:03d}-{v}.png"
            if out.exists() and not args.force:
                skipped_existing += 1
                continue
            if v <= n:
                print(f"  [{i:03d}/{len(beats)}] variant {v}/{n}  {prompt[:52]}...")
                rp.generate_still(prompt, out)
                rendered += 1
            else:
                shutil.copyfile(skip, out)
                filled += 1

    print(f"\nOK grid done -> {stills}")
    print(f"  rendered {rendered} | skip-filled {filled} | already-on-disk {skipped_existing}")
    print("  review the folder against GRID-INDEX.csv; <beat>-<v>.png maps to beat <beat>.")


if __name__ == "__main__":
    main()
