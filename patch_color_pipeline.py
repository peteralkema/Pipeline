#!/usr/bin/env python3
"""patch_color_pipeline.py -- the color law: every encode leaving the
pipeline converts to and declares BT.709/tv.

Probe-confirmed diagnosis (gospel-of-thomas, 5 Aug): ALL streams untagged.
Kling encodes with 709 coefficients (untagged, players assume 709 -> shown
right); every still-derived swscale RGB->YUV took the 601 default (untagged,
players assume 709 -> pink cast). The kb-tail seed frame was extracted from
709-coefficient footage with a 601-default decode, so tails were shifted
TWICE -- the seam receipt. Fix, per site class:
  RGB-source encodes  -> explicit out 709/tv conversion + VUI tags
  YUV kling re-encodes -> declared 709/tv in==out passthrough (no pixel
                          change; truthful labeling) + VUI tags
  frame extraction    -> declared 709/tv decode -> correct RGB seed
  concats             -> VUI tags (inputs uniform post-fix)

Idempotent. Usage: python3 patch_color_pipeline.py [repo_root] (default .)
Targets <root>/shared/v2/visuals.py and <root>/shared/v2/assemble.py.
"""
import py_compile, shutil, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
VIS = ROOT / "shared/v2/visuals.py"
ASM = ROOT / "shared/v2/assemble.py"
MARK = "BT709_FLAGS"

V_EDITS = [
# E1 constants
("""def _channel_fx_speckles(project_dir: Path) -> float:""",
 """BT709_FLAGS = ["-colorspace", "bt709", "-color_primaries", "bt709",
               "-color_trc", "bt709", "-color_range", "tv"]
RGB_TO_709 = "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
YUV_PASS_709 = (":in_range=tv:in_color_matrix=bt709"
                ":out_range=tv:out_color_matrix=bt709")


def _channel_fx_speckles(project_dir: Path) -> float:"""),

# E2 ken burns + speckles (RGB source): convert after blend + tags
("""        fc = (f"[0:v]{vf}[base];"
              f"[1:v]crop={W}:{H}:x='mod(t*11,240)':y='mod(t*7,240)',"
              f"format=rgb24[spk];"
              f"[base][spk]blend=all_mode=screen:all_opacity={op:.3f}")
        _run(["ffmpeg", "-y", "-loop", "1", "-i", str(still_path),
              "-loop", "1", "-i", str(speckles),
              "-filter_complex", fc,
              "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium",
              "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
              str(out_path)], "ken_burns+speckles ffmpeg")""",
 """        fc = (f"[0:v]{vf}[base];"
              f"[1:v]crop={W}:{H}:x='mod(t*11,240)':y='mod(t*7,240)',"
              f"format=rgb24[spk];"
              f"[base][spk]blend=all_mode=screen:all_opacity={op:.3f},"
              f"{RGB_TO_709}")
        _run(["ffmpeg", "-y", "-loop", "1", "-i", str(still_path),
              "-loop", "1", "-i", str(speckles),
              "-filter_complex", fc,
              "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium",
              "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
              *BT709_FLAGS,
              str(out_path)], "ken_burns+speckles ffmpeg")"""),

# E3 ken burns plain (RGB source)
("""    _run(["ffmpeg", "-y", "-loop", "1", "-i", str(still_path), "-vf", vf,
          "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium",
          "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), str(out_path)],
         "ken_burns ffmpeg")""",
 """    _run(["ffmpeg", "-y", "-loop", "1", "-i", str(still_path),
          "-vf", vf + "," + RGB_TO_709,
          "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium",
          "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
          *BT709_FLAGS, str(out_path)],
         "ken_burns ffmpeg")"""),

# E4 scale_pad in _fit_to_duration (YUV kling source): declared passthrough
("""    scale_pad = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                 f"crop={W}:{H},setsar=1,fps={FPS}")
    if native >= dur:""",
 """    scale_pad = (f"scale={W}:{H}:force_original_aspect_ratio=increase"
                 f"{YUV_PASS_709},"
                 f"crop={W}:{H},setsar=1,fps={FPS}")
    if native >= dur:"""),

# E5 trim encode tags
("""              "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(out_path)],
             f"trim {tag}")""",
 """              "-crf", "18", "-pix_fmt", "yuv420p", *BT709_FLAGS,
              "-an", str(out_path)],
             f"trim {tag}")"""),

# E6 hold encode tags
("""              "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(out_path)],
             f"hold {tag}")""",
 """              "-crf", "18", "-pix_fmt", "yuv420p", *BT709_FLAGS,
              "-an", str(out_path)],
             f"hold {tag}")"""),

# E7 kb-tail native part1 tags
("""        _run(["ffmpeg", "-y", "-i", str(clip), "-vf", scale_pad,
              "-c:v", "libx264", "-preset", "medium", "-crf", "18",
              "-pix_fmt", "yuv420p", "-an", str(part1)], f"kb-tail native {tag}")""",
 """        _run(["ffmpeg", "-y", "-i", str(clip), "-vf", scale_pad,
              "-c:v", "libx264", "-preset", "medium", "-crf", "18",
              "-pix_fmt", "yuv420p", *BT709_FLAGS,
              "-an", str(part1)], f"kb-tail native {tag}")"""),

# E8 seed-frame extraction: declared 709 decode -> correct RGB
("""        _run(["ffmpeg", "-y", "-sseof", "-0.05", "-i", str(part1),
              "-frames:v", "1", "-update", "1", str(frame)],
             f"kb-tail frame {tag}")""",
 """        _run(["ffmpeg", "-y", "-sseof", "-0.05", "-i", str(part1),
              "-vf", "scale=in_range=tv:in_color_matrix=bt709",
              "-frames:v", "1", "-update", "1", str(frame)],
             f"kb-tail frame {tag}")"""),

# E9 tail + speckles (RGB seed source)
("""            fc = (f"[0:v]{zp}[base];"
                  f"[1:v]crop={W}:{H}:x='mod(t*11,240)':y='mod(t*7,240)',"
                  f"format=rgb24,fade=t=in:st=0:d=0.8[spk];"
                  f"[base][spk]blend=all_mode=screen:all_opacity={op:.3f}")
            _run(["ffmpeg", "-y", "-loop", "1", "-i", str(frame),
                  "-loop", "1", "-i", str(speckles),
                  "-filter_complex", fc,
                  "-t", f"{remainder:.3f}", "-c:v", "libx264",
                  "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                  "-an", str(part2)], f"kb-tail zoom+speckles {tag}")""",
 """            fc = (f"[0:v]{zp}[base];"
                  f"[1:v]crop={W}:{H}:x='mod(t*11,240)':y='mod(t*7,240)',"
                  f"format=rgb24,fade=t=in:st=0:d=0.8[spk];"
                  f"[base][spk]blend=all_mode=screen:all_opacity={op:.3f},"
                  f"{RGB_TO_709}")
            _run(["ffmpeg", "-y", "-loop", "1", "-i", str(frame),
                  "-loop", "1", "-i", str(speckles),
                  "-filter_complex", fc,
                  "-t", f"{remainder:.3f}", "-c:v", "libx264",
                  "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                  *BT709_FLAGS,
                  "-an", str(part2)], f"kb-tail zoom+speckles {tag}")"""),

# E10 tail plain (RGB seed source)
("""            _run(["ffmpeg", "-y", "-loop", "1", "-i", str(frame), "-vf", zp,
                  "-t", f"{remainder:.3f}", "-c:v", "libx264", "-preset", "medium",
                  "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(part2)],
                 f"kb-tail zoom {tag}")""",
 """            _run(["ffmpeg", "-y", "-loop", "1", "-i", str(frame),
                  "-vf", zp + "," + RGB_TO_709,
                  "-t", f"{remainder:.3f}", "-c:v", "libx264", "-preset", "medium",
                  "-crf", "18", "-pix_fmt", "yuv420p", *BT709_FLAGS,
                  "-an", str(part2)],
                 f"kb-tail zoom {tag}")"""),

# E11 kb-tail concat tags
("""        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lf),
              "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
              "-crf", "18", "-pix_fmt", "yuv420p", str(out_path)],
             f"kb-tail concat {tag}")""",
 """        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lf),
              "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
              "-crf", "18", "-pix_fmt", "yuv420p", *BT709_FLAGS,
              str(out_path)],
             f"kb-tail concat {tag}")"""),
]

A_EDITS = [
# E12 final master concat tags
("""def _concat_video(segments, out: Path, work: Path) -> Path:
    listfile = work / "concat_v.txt"
    listfile.write_text("".join(f"file '{Path(s).resolve()}'\\n" for s in segments))
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
          "-c:v", "libx264", "-preset", "medium", "-crf", "18",
          "-pix_fmt", "yuv420p", "-r", str(FPS), str(out)], "concat video")""",
 """BT709_FLAGS = ["-colorspace", "bt709", "-color_primaries", "bt709",
               "-color_trc", "bt709", "-color_range", "tv"]


def _concat_video(segments, out: Path, work: Path) -> Path:
    listfile = work / "concat_v.txt"
    listfile.write_text("".join(f"file '{Path(s).resolve()}'\\n" for s in segments))
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
          "-c:v", "libx264", "-preset", "medium", "-crf", "18",
          "-pix_fmt", "yuv420p", "-r", str(FPS), *BT709_FLAGS,
          str(out)], "concat video")"""),
]


def apply(path: Path, edits, label: str):
    src = path.read_text()
    if MARK in src:
        print("%s already patched -- nothing to do" % label)
        return
    for i, (old, _new) in enumerate(edits, 1):
        n = src.count(old)
        if n != 1:
            sys.exit("ABORT: %s edit %d anchor matches %d times (need 1) -- "
                     "file has drifted; re-read before patching" % (label, i, n))
    for old, new in edits:
        src = src.replace(old, new)
    bak = path.with_name(path.name + ".pre_color_law")
    shutil.copy2(path, bak)
    tmp = path.with_name(path.name + ".tmp_color_law")
    tmp.write_text(src)
    py_compile.compile(str(tmp), doraise=True)
    tmp.replace(path)
    print("patched %s (%d edits, backup %s)" % (path, len(edits), bak.name))


def main():
    for p in (VIS, ASM):
        if not p.exists():
            sys.exit("ABORT: %s not found -- run from repo root" % p)
    apply(VIS, V_EDITS, "visuals.py")
    apply(ASM, A_EDITS, "assemble.py")


if __name__ == "__main__":
    main()
