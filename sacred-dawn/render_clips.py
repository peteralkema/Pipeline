#!/usr/bin/env python3
"""
render_clips.py -- turn placed stills into clips, doctrine-varied and floor-first.

Every beat rides the Ken Burns floor with its own doctrine MOVE (push/pull/crane/
settle/static) read from the `move` column -- so the floor rotates motion across the
film at $0, never a uniform slideshow. A beat is upgraded to Kling only when its `air`
column marks visible suspended matter AND it carries a `motion` prompt (gate before
spend). `--floor-only` forces every beat to Ken Burns regardless of `air` (the
all-floor cut); drop it later and mark specific air beats to add Kling additively.

Reuses the shared engine's ken_burns_still(move=...) and animate_still WITHOUT
modifying them. Reads the master CSV in beat order (row N == shot_{N:03d}).
Resume-safe. Channel-agnostic. Place in the CHANNEL dir; run from there.

    python render_clips.py --csv projects/<v>/beats/master.csv \
        --stills projects/<v>/stills --out projects/<v>/clips --floor-only

`move`  push|pull|crane|settle|static   (blank -> push)
`air`   kling|air|visible|yes|y|1|true  -> Kling (needs `motion`); else Ken Burns
"""
import argparse, csv, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED = HERE.parent / "shared"
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
            f"-- fill `motion`, clear `air`, or use --floor-only.")

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
