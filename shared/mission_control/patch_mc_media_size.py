#!/usr/bin/env python3
"""
patch_mc_media_size.py — Phase 3e: make still + clip ~2.5x bigger.

Two cosmetic edits to pipeline_server.py's beatRow:
  1. lift the still/clip max-width 480 -> 1100 (so the media can actually grow).
  2. reweight the five-column grid so the two MEDIA columns dominate the row,
     text/controls/motion shrink to what they need. Media grows because its
     columns grow — this is what lets it be big WITHOUT overflowing the
     right-half-of-monitor width.

Also widens the storyboard panel cap so the bigger row has room.

Idempotent (markers), backs up to .pre_mediasize, no JS logic change.

Run on the box:
  python shared/mission_control/patch_mc_media_size.py --check
  python shared/mission_control/patch_mc_media_size.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

# --- 1. still cell max-width 480 -> 1100 ---
EDITS.append(dict(
    marker="max-width:1100px;border-radius:8px;background:#000;display:block;\">';\n  } else {\n    stillCell",
    old='''    stillCell = '<img src="/stills/shot_' + n3 + '.png' + q +
      '" loading="lazy" style="width:100%;max-width:480px;border-radius:8px;background:#000;display:block;">';''',
    new='''    stillCell = '<img src="/stills/shot_' + n3 + '.png' + q +
      '" loading="lazy" style="width:100%;max-width:1100px;border-radius:8px;background:#000;display:block;">';''',
))

# --- 2. clip cell max-width 480 -> 1100 ---
EDITS.append(dict(
    marker="max-width:1100px;border-radius:8px;background:#000;display:block;\"></video>",
    old='''    clipCell = '<video src="/clips/shot_' + n3 + '.mp4' + q +
      '" muted loop autoplay playsinline style="width:100%;max-width:480px;border-radius:8px;background:#000;display:block;"></video>';''',
    new='''    clipCell = '<video src="/clips/shot_' + n3 + '.mp4' + q +
      '" muted loop autoplay playsinline style="width:100%;max-width:1100px;border-radius:8px;background:#000;display:block;"></video>';''',
))

# --- 3. reweight the grid: media columns dominate ---
# text 1.1 -> 0.7 | still 1.3 -> 2.6 | controls 0.9 -> 0.85 | motion 0.9 -> 0.7 | clip 1.3 -> 2.6
EDITS.append(dict(
    marker="minmax(360px,2.6fr)",
    old='''    'grid-template-columns:minmax(200px,1.1fr) minmax(220px,1.3fr) minmax(190px,0.9fr) minmax(180px,0.9fr) minmax(220px,1.3fr);">' +''',
    new='''    'grid-template-columns:minmax(180px,0.7fr) minmax(360px,2.6fr) minmax(190px,0.85fr) minmax(160px,0.7fr) minmax(360px,2.6fr);">' +''',
))

# --- 4. widen the storyboard panel so the bigger row isn't clipped ---
EDITS.append(dict(
    marker='maxWidth = "2400px"',
    old='''  wrap.style.maxWidth = "1600px";  // four columns: text | still | motion | clip''',
    new='''  wrap.style.maxWidth = "2400px";  // five columns with large media''',
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

    print("=== MEDIA-SIZE PATCH PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_mediasize")
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


if __name__ == "__main__":
    main()
