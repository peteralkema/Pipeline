#!/usr/bin/env python3
"""
place.py -- lay the picked variants into beat-order stills the clip render expects.

Reads your winners (a folder of picked {beat}-{variant}.png, OR a .txt list of those
filenames) and copies each into <out>/shot_{beat:03d}.png. When you pass a plain
filename list, it sources the actual bytes from the grid stills (--grid) that are
already on disk -- so no 1.3GB round-trip; only the filenames need to travel.

HARD-FAILS (no partial placement) if: a pick is a skip tile (byte-identical to the
skip tile, or ~15KB), a beat appears twice, or any beat in 1..N is missing.

Pure stdlib -- runs on laptop or box. Channel-agnostic: --out is any video folder's
stills dir.

    python3 place.py --winners winners.txt --grid <grid>/stills \\
                     --out <video>/stills --skip-tile <video-or-project>/_skip.png
    python3 place.py --winners ~/Downloads/grid-stills/winners \\
                     --out <video>/stills --skip-tile .../_skip.png
"""
import argparse, re, shutil, sys
from pathlib import Path

NAME = re.compile(r"^(\d{1,4})-(\d+)\.png$")


def die(msg):
    print("PLACE ABORTED: " + msg)
    raise SystemExit(1)


def collect(winners: Path):
    """Return {beat:int -> filename:str} from a dir of picks or a .txt list."""
    if winners.is_dir():
        names = [p.name for p in winners.iterdir() if p.suffix == ".png"]
        src_dir = winners
    elif winners.is_file():
        names = [ln.strip() for ln in winners.read_text().splitlines() if ln.strip()]
        names = [Path(n).name for n in names]
        src_dir = None
    else:
        die(f"--winners not found: {winners}")
    picks = {}
    for n in names:
        m = NAME.match(n)
        if not m:
            die(f"filename not <beat>-<variant>.png: {n}")
        beat = int(m.group(1))
        if beat in picks:
            die(f"beat {beat} picked twice: {picks[beat]} and {n}")
        picks[beat] = n
    return picks, src_dir


def main():
    ap = argparse.ArgumentParser(description="Place picked winners into beat-order stills.")
    ap.add_argument("--winners", required=True, help="dir of picked PNGs OR a .txt list of filenames")
    ap.add_argument("--grid", help="grid stills dir to source bytes from (needed if --winners is a list)")
    ap.add_argument("--out", required=True, help="destination stills dir (video folder)")
    ap.add_argument("--skip-tile", required=True, help="path to _skip.png (to reject picked placeholders)")
    ap.add_argument("--force", action="store_true", help="overwrite existing shot_NNN.png")
    args = ap.parse_args()

    winners = Path(args.winners).expanduser()
    out = Path(args.out).expanduser()
    skip = Path(args.skip_tile).expanduser()
    if not skip.is_file():
        die(f"--skip-tile not found: {skip}")
    skip_bytes = skip.read_bytes()
    skip_size = len(skip_bytes)

    picks, src_dir = collect(winners)
    if src_dir is None:
        if not args.grid:
            die("--winners is a list, so --grid <grid>/stills is required for the bytes.")
        src_dir = Path(args.grid).expanduser()
    if not src_dir.is_dir():
        die(f"source stills dir not found: {src_dir}")

    beats = sorted(picks)
    n = max(beats)
    missing = [b for b in range(1, n + 1) if b not in picks]
    if missing:
        die(f"{len(missing)} beat(s) missing from picks: {missing[:20]}")

    # validate every source exists and none is a skip tile, BEFORE writing anything
    plan = []
    for beat in beats:
        src = src_dir / picks[beat]
        if not src.is_file():
            die(f"source still not found for beat {beat}: {src}")
        b = src.read_bytes()
        if b == skip_bytes or len(b) == skip_size:
            die(f"beat {beat} pick is a SKIP TILE ({picks[beat]}) -- re-pick this beat.")
        plan.append((beat, src))

    out.mkdir(parents=True, exist_ok=True)
    placed = skipped = 0
    for beat, src in plan:
        dst = out / f"shot_{beat:03d}.png"
        if dst.exists() and not args.force:
            skipped += 1
            continue
        shutil.copyfile(src, dst)
        placed += 1

    print(f"Placed {placed} stills -> {out}  (existing skipped: {skipped})")
    print(f"  {n} beats, 1..{n}, no gaps, no dupes, no skip tiles.")


if __name__ == "__main__":
    main()
