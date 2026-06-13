#!/usr/bin/env python3
"""
patch_kenburns_producer.py — TIERED RENDER step (a): the Ken Burns clip producer.

WHY (the cost lever, from the session notes §7/§9)
  Kling (~$0.42/clip) is the dominant variable cost, mostly spent on the back two
  thirds of a video viewers never reach. TIERED RENDER renders the front N beats
  with Kling and the rest with a FREE ffmpeg Ken Burns slow-zoom. This is step (a)
  ONLY: the Ken Burns PRODUCER, proven in isolation before any routing is wired.

WHAT THIS DOES (one file: shared/recreation_pipeline.py)
  1. ken_burns_still(still_path, out_path, duration): writes the SAME artifact Kling
     writes — clips/shot_NNN.mp4 at the channel aspect — via ffmpeg zoompan, a slow
     zoom-IN always, rendered to the EXACT target duration (no Kling, no stretch, no
     cost). Craft note (banked): zooming the source directly judders, so it upscales
     the still 4x first, then zooms, for smoothness. Assembly needs ZERO changes —
     it can't tell a Ken Burns clip from a Kling clip.
  2. a `kenburns` CLI subcommand to prove the producer in isolation:
       python shared/recreation_pipeline.py kenburns --still <png> --out <mp4> --duration 9
     prints the ffprobe-measured duration so you can confirm length is correct.

  NOT in this patch: the render-flag routing, the per-project N policy, the stills-gate
  N field, the once-off-button routing. Those are steps (b)/(c)/(d), wired only after
  this producer is proven.

DISCIPLINE
  Idempotent (sentinel: `def ken_burns_still`). Three anchors, each verified once;
  backs up to .pre_kenburns; re-compiles + rolls back on failure. Run from the repo
  root on the LAPTOP, then commit/push, then pull on the box. (No service restart —
  this file isn't the always-on server.)
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/recreation_pipeline.py")
MARKER = "def ken_burns_still"

# 1. Insert ken_burns_still() just before _is_content_policy_error()
ANCHOR_FN = "def _is_content_policy_error(exc) -> bool:"
NEW_FN = '''def ken_burns_still(still_path: Path, out_path: Path, duration: float = None) -> Path:
    """
    TIERED RENDER — the free clip floor. Turn a still into a slow zoom-in clip via
    ffmpeg zoompan, rendered to the beat's EXACT duration (no Kling, no stretch, no
    cost). Writes the SAME artifact Kling writes (clips/shot_NNN.mp4, channel aspect),
    so assembly can't tell them apart and needs zero changes.

    Craft (banked): zooming the source directly judders — upscale the still first,
    then zoom, for smoothness. Slow zoom-IN always (one default, zero per-beat
    decisions). Cap the zoom so long beats do not creep too far in.
    """
    import subprocess
    dur = float(duration or SHOT_DURATION)
    fps = 24
    total_frames = max(1, int(round(dur * fps)))
    W, H = ASPECT["width"], ASPECT["height"]
    # Upscale to 4x the target first (smoothness), cover-crop to the 4x frame, then a
    # slow zoom-in (cap 1.25x), output at channel aspect.
    up_w, up_h = W * 4, H * 4
    vf = (
        f"scale={up_w}:{up_h}:force_original_aspect_ratio=increase,"
        f"crop={up_w}:{up_h},"
        f"zoompan=z='min(zoom+0.0006,1.25)':d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"s={W}x{H}:fps={fps},setsar=1"
    )
    cmd = [
        "ffmpeg", "-y", "-i", str(still_path),
        "-vf", vf,
        "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(fps),
        str(out_path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        tail = " | ".join(res.stderr.strip().splitlines()[-6:])
        raise RuntimeError(f"ken_burns ffmpeg failed: {tail}")
    return out_path


def _is_content_policy_error(exc) -> bool:'''

# 2. Insert cmd_kenburns() just before cmd_rulebook()
ANCHOR_CMD = "def cmd_rulebook(args):"
NEW_CMD = '''def cmd_kenburns(args):
    """Isolation test for the Ken Burns producer: still -> duration-correct mp4.
    Free (ffmpeg only). Prints the measured duration so length can be verified."""
    import subprocess
    still = Path(args.still).expanduser()
    out = Path(args.out).expanduser()
    if not still.exists():
        raise SystemExit(f"still not found: {still}")
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"Ken Burns: {still.name} -> {out.name} @ {args.duration:.2f}s ...")
    ken_burns_still(still, out, args.duration)
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(out)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    print(f"OK -> {out}")
    print(f"   measured duration: {r.stdout.strip()}s  (target {args.duration:.2f}s)")


def cmd_rulebook(args):'''

# 3. Register the kenburns subparser just after the finish subparser
ANCHOR_SUB = "    c.set_defaults(func=cmd_finish)\n"
NEW_SUB = '''    c.set_defaults(func=cmd_finish)

    # TIERED RENDER (step a) — isolation test for the Ken Burns producer (no fal, no cost)
    e = sub.add_parser("kenburns",
                       help="still -> ffmpeg ken-burns zoom clip at a target duration (TIERED RENDER floor)")
    e.add_argument("--still", required=True, help="path to the still PNG")
    e.add_argument("--out", required=True, help="output mp4 path")
    e.add_argument("--duration", type=float, default=9.0, help="target clip duration in seconds")
    e.set_defaults(func=cmd_kenburns)
'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found — run this from the repo root on the laptop.")

    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) — no changes made.")
        return

    edits = [
        ("ken_burns_still fn", ANCHOR_FN, NEW_FN),
        ("cmd_kenburns fn", ANCHOR_CMD, NEW_CMD),
        ("kenburns subparser", ANCHOR_SUB, NEW_SUB),
    ]
    for label, old, _ in edits:
        n = src.count(old)
        if n == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written.")
        if n > 1:
            die(f"anchor for {label} found {n}x (expected 1) — ambiguous; nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_kenburns")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    check = TARGET.read_text()
    problems = []
    if MARKER not in check:
        problems.append("ken_burns_still missing")
    if "def cmd_kenburns" not in check:
        problems.append("cmd_kenburns missing")
    if 'sub.add_parser("kenburns"' not in check:
        problems.append("kenburns subparser missing")
    if problems:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed (" + "; ".join(problems) + ") — restored from backup.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile — restored from backup.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   1) ken_burns_still() producer added")
    print("   2) cmd_kenburns() + `kenburns` subcommand added")
    print("Verify on the box after pull:")
    print("   grep -n 'def ken_burns_still' shared/recreation_pipeline.py")


if __name__ == "__main__":
    main()
