#!/usr/bin/env python3
"""
patch_kb_tail.py — add the NEVER-STRETCH reconciliation path to
assemble_episode.py behind a --kb-tail flag.

Anchor-verified, idempotent, backs up, py_compile-checks, restores on failure.
Run from repo root: python3 shared/patch_kb_tail.py   (LAPTOP)

Behavior:
  DEFAULT (no flag): byte-identical to today — Mode A short clips slow-fill,
  Mode B freeze-tails, long clips trim. No other channel changes.

  WITH --kb-tail: a Mode A clip shorter than its beat plays AT NATIVE SPEED in
  full, then its LAST FRAME continues under a Ken-Burns zoom for the remainder
  (upscale-then-zoompan, the banked smoothness craft). Motion hands off to
  motion: no setpts, no freeze. Remainders < 0.5s use an invisible clone-pad.
  Mode B freeze-tail behavior is unchanged (graphics must never warp).

THE LAW (banked): NEVER STRETCH, ONLY TRIM. Slow motion is a directorial act
that lives in the model prompt; the assembly layer may cut surplus but never
dilate time.
"""

import py_compile
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "assemble_episode.py"
BACKUP = HERE / "assemble_episode.py.pre_kb_tail"

MARKER = "NEVER-STRETCH"

ANCHOR_CONST = 'MUSIC_LEVEL = 0.040  # patched 2026-06-20: -28dB, ~17 LU under voice (was 0.07/-23dB/~14 LU)   # music bed sits low under narration (Jamendo-calibrated)'

REPLACE_CONST = ANCHOR_CONST + '''
KB_TAIL = False  # --kb-tail: NEVER-STRETCH — Mode A short clips play native + Ken-Burns tail'''

ANCHOR_ARG = '''    ap.add_argument("--placeholders", action="store_true",'''

REPLACE_ARG = '''    ap.add_argument("--kb-tail", action="store_true",
                    help="NEVER-STRETCH: Mode A clips shorter than their beat play at native "
                         "speed, then Ken-Burns-zoom their last frame for the remainder "
                         "(no slow-fill). Mode B freeze-tail unchanged.")
    ap.add_argument("--placeholders", action="store_true",'''

ANCHOR_GLOBAL = '''    global MUSIC_LEVEL
    if args.music_level is not None:
        MUSIC_LEVEL = args.music_level
        print(f'  music-level override: MUSIC {MUSIC_LEVEL}')'''

REPLACE_GLOBAL = '''    global MUSIC_LEVEL, KB_TAIL
    if args.music_level is not None:
        MUSIC_LEVEL = args.music_level
        print(f'  music-level override: MUSIC {MUSIC_LEVEL}')
    if args.kb_tail:
        KB_TAIL = True
        print("  kb-tail: NEVER-STRETCH mode — native playback + Ken-Burns tails on short Mode A clips")'''

ANCHOR_BRANCH = '''        else:
            # Mode A: slow-to-fill (cinematic). setpts factor > 1 slows; fps resamples.
            factor = dur / native
            if factor > 2.5:
                print(f"     beat {beat['index']}: slow-fill {native:.1f}s -> {dur:.1f}s "
                      f"({factor:.1f}x — heavy stretch; candidate for more/shorter beats)")
            vf = f"setpts=PTS*{factor:.6f},{scale_pad}"
            label = "slow-fill(A)"'''

REPLACE_BRANCH = '''        elif KB_TAIL and (dur - native) >= 0.5:
            # NEVER-STRETCH LAW: play the clip at native speed in full, then
            # continue the motion with a Ken-Burns zoom on the clip's LAST FRAME
            # for the remainder. No setpts, no freeze — motion hands to motion.
            remainder = dur - native
            part1 = work / f"v_{i:03d}_native.mp4"
            run(["ffmpeg", "-y", "-i", str(src),
                 "-vf", scale_pad, "-c:v", "libx264", "-preset", "medium",
                 "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(part1)],
                f"kb-tail native part beat {beat['index']}")
            frame = work / f"v_{i:03d}_last.png"
            run(["ffmpeg", "-y", "-sseof", "-0.25", "-i", str(part1),
                 "-frames:v", "1", "-update", "1", str(frame)],
                f"kb-tail last frame beat {beat['index']}")
            tail_frames = max(1, int(round(remainder * FPS)))
            part2 = work / f"v_{i:03d}_tail.mp4"
            # banked craft: upscale first, then zoompan, for smoothness
            zp = (f"scale={W*2}:{H*2},"
                  f"zoompan=z='min(zoom+0.0008,1.10)':d={tail_frames}:"
                  f"s={W}x{H}:fps={FPS}")
            run(["ffmpeg", "-y", "-loop", "1", "-i", str(frame),
                 "-vf", zp, "-t", f"{remainder:.3f}",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                 "-pix_fmt", "yuv420p", "-an", str(part2)],
                f"kb-tail zoom part beat {beat['index']}")
            lf = work / f"v_{i:03d}_list.txt"
            lf.write_text(f"file '{part1.resolve()}'\\nfile '{part2.resolve()}'\\n")
            run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lf),
                 "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
                 "-crf", "18", "-pix_fmt", "yuv420p", str(dst)],
                f"kb-tail concat beat {beat['index']}")
            print(f"     beat {beat['index']}: kb-tail {native:.1f}s native + "
                  f"{remainder:.1f}s ken-burns (never-stretch)")
            return dst
        elif KB_TAIL:
            # remainder < 0.5s: invisible clone-pad instead of a zoom stub
            vf = f"{scale_pad},tpad=stop_mode=clone:stop_duration={dur - native:.3f}"
            label = "clone-pad(A,<0.5s)"
        else:
            # Mode A legacy: slow-to-fill (cinematic). setpts factor > 1 slows; fps resamples.
            factor = dur / native
            if factor > 2.5:
                print(f"     beat {beat['index']}: slow-fill {native:.1f}s -> {dur:.1f}s "
                      f"({factor:.1f}x — heavy stretch; candidate for more/shorter beats)")
            vf = f"setpts=PTS*{factor:.6f},{scale_pad}"
            label = "slow-fill(A)"'''


def die(msg: str) -> None:
    print(f"ABORT: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not TARGET.is_file():
        die(f"{TARGET} not found — run from the repo (patch lives in shared/).")

    source = TARGET.read_text(encoding="utf-8")

    if MARKER in source:
        print("Already applied — no-op.")
        return

    for name, anchor in (("ANCHOR_CONST (MUSIC_LEVEL line)", ANCHOR_CONST),
                         ("ANCHOR_ARG (--placeholders argparse)", ANCHOR_ARG),
                         ("ANCHOR_GLOBAL (music-level override block)", ANCHOR_GLOBAL),
                         ("ANCHOR_BRANCH (Mode A slow-fill branch)", ANCHOR_BRANCH)):
        n = source.count(anchor)
        if n != 1:
            die(f"{name} found {n} times (need exactly 1) — assemble_episode.py has "
                "drifted from what this patch was written against. Re-grep and "
                "re-anchor. Nothing written.")

    shutil.copy2(TARGET, BACKUP)
    print(f"Backup written: {BACKUP}")

    new_source = source.replace(ANCHOR_CONST, REPLACE_CONST, 1)
    new_source = new_source.replace(ANCHOR_ARG, REPLACE_ARG, 1)
    new_source = new_source.replace(ANCHOR_GLOBAL, REPLACE_GLOBAL, 1)
    new_source = new_source.replace(ANCHOR_BRANCH, REPLACE_BRANCH, 1)
    TARGET.write_text(new_source, encoding="utf-8")

    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(BACKUP, TARGET)
        die(f"py_compile FAILED — original restored from backup.\n{e}")

    print("Applied: --kb-tail (NEVER-STRETCH) reconciliation in assemble_episode.py.")
    print("Default behavior unchanged; opt in per run with --kb-tail.")
    print("Verify:  grep -n 'NEVER-STRETCH\\|kb-tail\\|kb_tail' shared/assemble_episode.py")


if __name__ == "__main__":
    main()
