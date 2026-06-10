"""Deterministic film-stock emulation applied at assembly time.

One grade per decade, applied uniformly to every clip (or to the final cut)
so all beats share a single stock instead of begging a stochastic video model
for consistency. Pure ffmpeg filters, no external LUT files required.

Usage:
    from shared.film_emulate import film_emulate
    film_emulate("in.mp4", "out.mp4", preset="super8_70s")
"""

import shutil
import subprocess

PRESETS = {
    "super8_70s": (
        "curves=preset=vintage,"
        "eq=saturation=0.82:contrast=0.96:brightness=0.015:gamma=1.02,"
        "colorbalance=rs=0.03:gm=0.02:bs=-0.05,"
        "gblur=sigma=0.5,"
        "noise=alls=11:allf=t,"
        "vignette=PI/5"
    ),
    "sixteen_mm_50s": (
        "curves=preset=vintage,"
        "eq=saturation=0.88:contrast=0.98:brightness=0.02:gamma=1.01,"
        "colorbalance=rs=0.04:gm=0.03:bs=-0.03,"
        "gblur=sigma=0.35,"
        "noise=alls=7:allf=t,"
        "vignette=PI/6"
    ),
    "vhs_80s": (
        "curves=preset=vintage,"
        "eq=saturation=1.06:contrast=1.05:brightness=0.0,"
        "colorbalance=rs=0.02:bs=0.04,"
        "gblur=sigma=0.8,"
        "noise=alls=8:allf=t,"
        "vignette=PI/7"
    ),
}


def film_emulate(input_path, output_path, preset="super8_70s", crf=18, vf_override=None):
    """Grade one video file and write the result. Returns output_path.

    preset      key into PRESETS
    crf         x264 quality (lower is higher quality)
    vf_override pass a raw -vf chain to bypass the preset entirely
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found on PATH")

    vf = vf_override if vf_override is not None else PRESETS.get(preset)
    if vf is None:
        raise ValueError("unknown preset '%s' (have: %s)" % (preset, ", ".join(PRESETS)))

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("ffmpeg film grade failed:\n" + result.stderr[-2000:])
    return output_path
