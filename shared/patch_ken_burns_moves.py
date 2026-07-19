#!/usr/bin/env python3
"""
patch_ken_burns_moves.py -- give the Ken Burns floor the five doctrine moves.

The engine's ken_burns_still is hardcoded to true-static (_z="1", a 01-Jul drift
workaround), so the floor is a dead-held frame. This replaces it with a `move`-driven
slow zoompan: push (zoom in), pull (zoom out), crane (rise), settle (drift down),
static (held). The motion doctrine now applies to Ken Burns, so the floor rotates
motion across a film at $0, exactly like Kling would -- one slow move, subject locked.

Backward compatible: move=None keeps the legacy true-static behavior byte-for-byte,
so every existing engine caller is unchanged. Only callers that pass an explicit move
(render_clips.py) get motion. Reusable across channels -- it is a general capability.

Replaces the whole function by boundary (signature -> next def), so it does not depend
on matching the em-dashed comment body. Idempotent, .pre_<ts> backup, py_compile, ASCII.
Run from the dir with recreation_pipeline.py, or pass the path.
"""
import sys, time
from pathlib import Path

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("recreation_pipeline.py")
START = "def ken_burns_still("
NEXT = "\ndef _is_content_policy_error("
MARKER = "move: str = None"

NEW_FUNC = '''def ken_burns_still(still_path: Path, out_path: Path, duration: float = None, move: str = None) -> Path:
    """
    TIERED RENDER -- the free clip floor, DOCTRINE-VARIED.
    `move` drives a slow ffmpeg zoompan on the still so the floor rotates motion
    across a film like the motion doctrine itself:
        push   = slow zoom IN         (one overwhelming subject; the default)
        pull   = slow zoom OUT        (scale / number / how-far)
        crane  = slow rise            (vertical phenomena)
        settle = slow drift DOWN      (reflection / aftermath / grief)
        static = held frame, no move  (eerie stillness / near-locked)
    Writes clips/shot_NNN.mp4 at channel aspect -- the SAME artifact Kling writes, so
    assembly cannot tell them apart. move=None keeps the legacy true-static floor
    byte-for-byte (backward compatible). Every move is SLOW: a weighted 40kg camera.
    Craft (banked): upscale 4x before zoompan or the zoom judders.
    """
    import subprocess
    dur = float(duration or SHOT_DURATION)
    fps = 24
    total_frames = max(1, int(round(dur * fps)))
    W, H = ASPECT["width"], ASPECT["height"]
    d = total_frames
    m = (move or "").strip().lower()

    if m in ("", "static"):
        # TRUE STATIC: bypass zoompan (it micro-drifts even at z=1). scale-to-fit +
        # pad = a single held frame, ZERO motion. move=None keeps the legacy floor.
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,fps={fps}"
        )
    else:
        # MOVING: upscale 4x for smoothness, then a slow move-specific zoompan.
        up_w, up_h = W * 4, H * 4
        cx = "iw/2-(iw/zoom/2)"
        cy = "ih/2-(ih/zoom/2)"
        if m == "pull":
            z, x, y = "if(eq(on,0),1.16,max(zoom-0.0012,1.0))", cx, cy
        elif m == "crane":
            z, x, y = "1.12", cx, "(ih-ih/zoom)*(1-on/%d)" % d
        elif m == "settle":
            z, x, y = "1.12", cx, "(ih-ih/zoom)*(on/%d)" % d
        else:  # push and any unknown move -> safe slow zoom-in
            z, x, y = "min(zoom+0.0012,1.16)", cx, cy
        vf = (
            f"scale={up_w}:{up_h}:force_original_aspect_ratio=increase,"
            f"crop={up_w}:{up_h},"
            f"zoompan=z='{z}':d={total_frames}:"
            f"x='{x}':y='{y}':"
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

'''


def die(msg):
    print("PATCH ABORTED: " + msg)
    raise SystemExit(1)


def main():
    if not TARGET.exists():
        die("recreation_pipeline.py not found. Pass the path or run from its dir.")
    src = TARGET.read_text()
    if MARKER in src:
        print("Already applied (ken_burns_still has move param). No change.")
        return
    if START not in src:
        die("ken_burns_still not found.")
    start = src.index(START)
    nxt = src.find(NEXT, start)
    if nxt == -1:
        die("could not find the next function boundary (_is_content_policy_error).")

    new = src[:start] + NEW_FUNC + src[nxt + 1:]  # +1 drops the leading \n of NEXT; NEW_FUNC ends with \n
    if not NEW_FUNC.isascii():
        die("new function contains non-ASCII bytes.")
    try:
        compile(new, str(TARGET), "exec")
    except SyntaxError as e:
        die("compile check failed: %s" % e)

    ts = time.strftime("%Y%m%d-%H%M%S")
    TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts).write_text(src)
    TARGET.write_text(new)
    print("Patched recreation_pipeline.py")
    print("  backup: %s.pre_%s" % (TARGET.name, ts))
    print("  ken_burns_still now takes move=push|pull|crane|settle|static (move=None = legacy static)")


if __name__ == "__main__":
    main()
