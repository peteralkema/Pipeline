"""
still_to_clip.py — Convert a still PNG into a 5-second MP4 with no motion.

Use this for shots Kling refuses on content-policy grounds (e.g. the Pompeii
casts, which are archaeological but read to moderation as "human in death pose").
A held still over the narration is often more powerful anyway.

Run:
    python3 still_to_clip.py pompeii_v1/stills/shot_028.png pompeii_v1/clips/shot_028.mp4
"""

import sys
import subprocess
from pathlib import Path


def still_to_clip(still_path: Path, out_path: Path, duration: float = 5.0):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(still_path),
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
        "-r", "24",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"OK held still -> {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python3 still_to_clip.py <still.png> <out.mp4>")
    still_to_clip(Path(sys.argv[1]), Path(sys.argv[2]))
