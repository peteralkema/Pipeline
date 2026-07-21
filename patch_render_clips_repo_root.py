#!/usr/bin/env python3
"""
patch_render_clips_repo_root.py -- relocate render_clips.py to repo root, make it
resolve shared/ by walking up for .git so ONE copy serves every channel.
Idempotent. ASCII-only.
"""
import py_compile
import shutil
import sys
from pathlib import Path

NEW_SOURCE = r'''#!/usr/bin/env python3
"""
render_clips.py -- turn placed stills into clips, doctrine-varied and floor-first.
ONE copy at repo root serves every channel: resolves shared/ by walking up for .git,
resolves each channel grade/suffix off the OUTPUT PATH (--out) via the engine.

    python render_clips.py \
        --csv sacred-dawn/projects/<slug>/master.csv \
        --stills sacred-dawn/projects/<slug>/stills \
        --out sacred-dawn/projects/<slug>/clips --floor-only

move  push|pull|crane|settle|static   (blank -> push)
air   kling|air|visible|yes|y|1|true  -> Kling (needs motion); else Ken Burns
"""
import argparse, csv, sys
from pathlib import Path


def _repo_root():
    p = Path(__file__).resolve()
    for cand in [p.parent, *p.parents]:
        if (cand / ".git").exists():
            return cand
    return p.parent


REPO = _repo_root()
SHARED = REPO / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))
import recreation_pipeline as rp  # noqa: E402

AIR_TRUE = {"kling", "air", "visible", "yes", "y", "1", "true"}
MOVES = {"push", "pull", "crane", "settle", "static"}
DURATION = getattr(rp, "SHOT_DURATION", 5.0)
KLING_COST = 0.42


def die(msg):
    print("RENDER_CLIPS ABORTED: " + msg)
    raise SystemExit(1)


def main():
    ap = argparse.ArgumentParser(description="Render clips: doctrine Ken Burns floor + optional Kling.")
    ap.add_argument("--csv", required=True)
    ap.add_argument("--stills", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--floor-only", action="store_true", help="force all Ken Burns (ignore air/Kling)")
    ap.add_argument("--force", action="store_true", help="re-render clips already on disk")
    ap.add_argument("--dry-run", action="store_true", help="report the split + cost, render nothing")
    args = ap.parse_args()

    csv_path = Path(args.csv).expanduser()
    stills = Path(args.stills).expanduser()
    out = Path(args.out).expanduser()
    if not csv_path.is_file():
        die(f"CSV not found: {csv_path}")
    if not stills.is_dir():
        die(f"stills dir not found: {stills}")
    rows = list(csv.DictReader(csv_path.open()))
    if not rows:
        die("CSV has no rows.")

    plan = []
    missing_still, kling_no_motion, bad_move = [], [], []
    move_hist = {}
    for i, r in enumerate(rows, 1):
        still = stills / f"shot_{i:03d}.png"
        if not still.is_file():
            missing_still.append(i); continue
        air = (r.get("air") or "").strip().lower()
        move = (r.get("move") or "push").strip().lower()
        if move not in MOVES:
            bad_move.append((i, move)); move = "push"
        if not args.floor_only and air in AIR_TRUE:
            motion = (r.get("motion") or "").strip()
            if not motion:
                kling_no_motion.append(i)
            plan.append((i, still, out / f"shot_{i:03d}.mp4", "kling", motion))
        else:
            move_hist[move] = move_hist.get(move, 0) + 1
            plan.append((i, still, out / f"shot_{i:03d}.mp4", "kb", move))

    if missing_still:
        die(f"{len(missing_still)} placed still(s) missing (run place.py first): {missing_still[:20]}")
    if bad_move:
        die(f"unknown move value(s): {bad_move[:10]} -- use push|pull|crane|settle|static.")
    if kling_no_motion:
        die(f"{len(kling_no_motion)} air/Kling beat(s) with NO motion: {kling_no_motion[:20]} "
            f"-- fill motion, clear air, or use --floor-only.")

    kling = [p for p in plan if p[3] == "kling"]
    print(f"{len(plan)} beats | Kling {len(kling)} (${len(kling)*KLING_COST:.2f}) | "
          f"Ken Burns {len(plan)-len(kling)} ($0)")
    print("  moves: " + ", ".join(f"{m}:{move_hist.get(m,0)}" for m in
                                   ("push", "pull", "crane", "settle", "static")))
    if args.dry_run:
        print("dry-run: nothing rendered.")
        return

    out.mkdir(parents=True, exist_ok=True)
    made = skipped = 0
    for beat, still, dst, kind, arg in plan:
        if dst.exists() and not args.force:
            skipped += 1; continue
        if kind == "kling":
            print(f"  [{beat:03d}] KLING  {arg[:52]}")
            rp.animate_still(still, arg, dst)
        else:
            print(f"  [{beat:03d}] ken burns / {arg}")
            rp.ken_burns_still(still, dst, DURATION, move=arg)
        made += 1

    print(f"\nOK clips -> {out}")
    print(f"  rendered {made} | already-on-disk {skipped}")
    print("  drop clips/ + the locked VO into Filmora; seam swells at block boundaries.")


if __name__ == "__main__":
    main()
'''

MARKER = "def _repo_root():"


def repo_root():
    p = Path(__file__).resolve()
    for cand in [p.parent, *p.parents]:
        if (cand / ".git").exists():
            return cand
    return p.parent


def main():
    root = repo_root()
    target = root / "render_clips.py"
    old_channel_copy = root / "sacred-dawn" / "render_clips.py"

    if target.is_file() and MARKER in target.read_text():
        print("SKIP: repo-root render_clips.py already has the .git-walk resolver.")
        if old_channel_copy.is_file():
            print(f"NOTE: stale channel copy still present: {old_channel_copy}")
        return

    tmp = root / "render_clips.py.new"
    tmp.write_text(NEW_SOURCE)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        tmp.unlink(missing_ok=True)
        print("ABORT: new source failed py_compile:\n" + str(e))
        sys.exit(1)

    if target.is_file():
        bak = root / "render_clips.py.pre_repo_root"
        if not bak.exists():
            shutil.copy2(target, bak)
            print(f"backup -> {bak}")

    tmp.replace(target)
    print(f"WROTE {target}")

    if old_channel_copy.is_file():
        bak2 = old_channel_copy.with_suffix(".py.pre_relocate")
        shutil.copy2(old_channel_copy, bak2)
        old_channel_copy.unlink()
        print(f"backup -> {bak2}")
        print(f"REMOVED per-channel copy: {old_channel_copy}")

    print("OK. Commit + push, then on box: git pull --no-edit, then --dry-run to verify.")


if __name__ == "__main__":
    main()
