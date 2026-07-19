#!/usr/bin/env python3
"""
render_clips.py -- turn placed stills into clips, floor-first and air-gated.

Reuses the shared engine's animate_still (Kling) and ken_burns_still (free zoompan)
WITHOUT modifying it. Every beat defaults to the Ken Burns FLOOR ($0); a beat is
upgraded to Kling only when its `air` column marks visible suspended matter
(dust/smoke/mist/embers/water/cloth). Kling beats MUST carry a `motion` prompt --
the render aborts before any spend if one is missing (gate before spend).

Reads the master CSV in beat order (row N == beat N == shot_{N:03d}). Writes
clips/shot_NNN.mp4 next to the stills. Resume-safe. Channel-agnostic: the engine
funcs resolve the channel from the paths.

Place in the CHANNEL dir; run from there:
    python render_clips.py --csv projects/<video>/beats/master.csv \\
                           --stills projects/<video>/stills \\
                           --out projects/<video>/clips

`air`  truthy values: kling, air, visible, yes, y, 1, true
`motion` free text (the doctrine move, e.g. "slow push-in, subject locked").
"""
import argparse, csv, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED = HERE.parent / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))
import recreation_pipeline as rp  # noqa: E402

AIR_TRUE = {"kling", "air", "visible", "yes", "y", "1", "true"}
DURATION = getattr(rp, "SHOT_DURATION", 5.0)
KLING_COST = 0.42


def die(msg):
    print("RENDER_CLIPS ABORTED: " + msg)
    raise SystemExit(1)


def main():
    ap = argparse.ArgumentParser(description="Render clips: Ken Burns floor + air-gated Kling.")
    ap.add_argument("--csv", required=True, help="master CSV (row order == beat order)")
    ap.add_argument("--stills", required=True, help="placed stills dir (shot_NNN.png)")
    ap.add_argument("--out", required=True, help="clips output dir")
    ap.add_argument("--force", action="store_true", help="re-render clips already on disk")
    ap.add_argument("--dry-run", action="store_true", help="report the Kling/KenBurns split + cost, render nothing")
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

    # classify every beat + validate BEFORE any spend
    plan = []            # (beat, still, out, is_kling, motion)
    missing_still = []
    kling_no_motion = []
    for i, r in enumerate(rows, 1):
        still = stills / f"shot_{i:03d}.png"
        if not still.is_file():
            missing_still.append(i)
            continue
        air = (r.get("air") or "").strip().lower()
        is_kling = air in AIR_TRUE
        motion = (r.get("motion") or "").strip()
        if is_kling and not motion:
            kling_no_motion.append(i)
        plan.append((i, still, out / f"shot_{i:03d}.mp4", is_kling, motion))

    if missing_still:
        die(f"{len(missing_still)} placed still(s) missing (run place.py first): {missing_still[:20]}")
    if kling_no_motion:
        die(f"{len(kling_no_motion)} beat(s) marked air/Kling with NO motion prompt: "
            f"{kling_no_motion[:20]} -- fill `motion` or clear `air`.")

    kling = [p for p in plan if p[3]]
    burns = [p for p in plan if not p[3]]
    print(f"{len(plan)} beats | Kling {len(kling)} (${len(kling)*KLING_COST:.2f}) | "
          f"Ken Burns {len(burns)} ($0)")
    if args.dry_run:
        print("dry-run: nothing rendered. Kling beats:",
              ", ".join(str(p[0]) for p in kling) or "(none)")
        return

    out.mkdir(parents=True, exist_ok=True)
    made = skipped = 0
    for beat, still, dst, is_kling, motion in plan:
        if dst.exists() and not args.force:
            skipped += 1
            continue
        if is_kling:
            print(f"  [{beat:03d}] KLING  {motion[:56]}")
            rp.animate_still(still, motion, dst)
        else:
            print(f"  [{beat:03d}] ken burns")
            rp.ken_burns_still(still, dst, DURATION)
        made += 1

    print(f"\nOK clips -> {out}")
    print(f"  rendered {made} | already-on-disk {skipped}")
    print("  drop clips/ + the locked VO into Filmora; seam swells at block boundaries.")


if __name__ == "__main__":
    main()
