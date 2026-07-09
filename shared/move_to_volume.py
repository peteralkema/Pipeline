#!/usr/bin/env python3
"""
move_to_volume.py - relocate fat project artifacts to the mounted volume and
symlink them back, so the on-root directory structure is byte-for-byte what the
code already expects.

Structure preserved: <repo>/<channel>/projects/<slug>/ stays a REAL directory on
root. Only the heavy contents move:
    modea/stills/  modea/clips/  stills/  clips/  thumb_candidates/  final_video.mp4

Every Path.resolve(), .parents walk, channel.json stop-marker and
startswith(_REPO) guard therefore keeps working unchanged.

Idempotent: anything already a symlink is skipped. Safe to re-run.

Usage (BOX):
    python shared/move_to_volume.py --channel lazarus --dry-run
    python shared/move_to_volume.py --channel lazarus
    python shared/move_to_volume.py --all
    python shared/move_to_volume.py --all --dry-run
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VOL = Path("/mnt/HC_Volume_106283770/Pipeline")

FAT = [
    "modea/stills",
    "modea/clips",
    "stills",
    "clips",
    "thumb_candidates",
    "final_video.mp4",
]


def free_root():
    st = os.statvfs("/")
    return st.f_bavail * st.f_frsize / (1024 ** 3)


def channels():
    out = []
    for d in sorted(REPO.iterdir()):
        if (d / "channel.json").is_file() and (d / "projects").is_dir():
            out.append(d.name)
    return out


def move_channel(ch: str, dry: bool) -> tuple[int, int]:
    src_root = REPO / ch / "projects"
    if not src_root.is_dir():
        print(f"  {ch}: no projects dir, skipping")
        return (0, 0)
    moved = skipped = 0
    for proj in sorted(p for p in src_root.iterdir() if p.is_dir()):
        slug = proj.name
        for item in FAT:
            src = proj / item
            if not src.exists() and not src.is_symlink():
                continue
            if src.is_symlink():
                skipped += 1
                continue
            tgt = VOL / ch / slug / item
            if dry:
                print(f"  [dry] {src}  ->  {tgt}")
                moved += 1
                continue
            tgt.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src), str(tgt))
            except Exception as e:
                sys.exit(f"ABORT moving {src}: {e}")
            try:
                src.symlink_to(tgt)
            except Exception as e:
                sys.exit(f"ABORT symlinking {src} -> {tgt}: {e}")
            moved += 1
    return (moved, skipped)


def verify(ch: str) -> bool:
    src_root = REPO / ch / "projects"
    projs = [p for p in src_root.iterdir() if p.is_dir()]
    if not projs:
        return True
    p = projs[0]
    ok = True
    if not str(p.resolve()).startswith(str(REPO.resolve())):
        print(f"  !! {ch}: project no longer resolves under repo: {p.resolve()}")
        ok = False
    if not (p.parent.parent / "channel.json").is_file():
        print(f"  !! {ch}: channel.json not two levels above project")
        ok = False
    for cand in (p / "modea" / "stills", p / "stills"):
        if cand.is_symlink():
            n = len(list(cand.glob("*.png")))
            print(f"  {ch}: {cand.name} symlinked, {n} pngs visible through link")
            if n == 0:
                print(f"  !! {ch}: symlinked stills dir globs empty")
                ok = False
            break
    fv = p / "final_video.mp4"
    if fv.is_symlink():
        if not fv.exists():
            print(f"  !! {ch}: final_video.mp4 symlink is broken")
            ok = False
        else:
            print(f"  {ch}: final_video.mp4 symlinked, {fv.stat().st_size} bytes readable")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", help="single channel folder name")
    ap.add_argument("--all", action="store_true", help="every channel with a channel.json")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not VOL.parent.is_dir():
        sys.exit(f"ABORT: volume not mounted at {VOL.parent}")
    if not a.dry_run:
        VOL.mkdir(parents=True, exist_ok=True)

    if a.all:
        chans = channels()
    elif a.channel:
        chans = [a.channel]
    else:
        sys.exit("give --channel <name> or --all")

    print(f"repo={REPO}  volume={VOL}  free_root={free_root():.1f} GB")
    print(f"channels: {', '.join(chans)}\n")

    for ch in chans:
        moved, skipped = move_channel(ch, a.dry_run)
        print(f"{ch}: moved={moved} skipped(already-linked)={skipped}")
        if not a.dry_run and moved:
            if not verify(ch):
                sys.exit(f"ABORT: verification failed on {ch}")
            print(f"  free_root now {free_root():.1f} GB\n")

    if not a.dry_run:
        print(f"\nDONE. free_root={free_root():.1f} GB")


if __name__ == "__main__":
    main()
