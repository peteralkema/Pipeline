"""shared/v2/visuals.py -- stage 3: stills + clips, born at their exact length.

Extraction provenance (v1 organ donors, decommission map):
  generate_still  -> _gen_still   : flux path verbatim (safety_tolerance '5',
                     negative_prompt, image_size). Config now comes from the
                     project row; the channel.json / rulebook walks are gone.
  ken_burns_still -> _kb_still    : verbatim, including the 29 Jul duration-
                     scaled push/pull fix, the 4x-upscale craft, and the
                     true-static bypass. `move` column drives it.
  animate_still   -> _animate     : verbatim kling call (fal storage upload,
                     content-policy detection).
  make_video_segment (assemble_episode.py) -> _fit_to_duration : the kb-tail
                     path carried verbatim -- last-frame extract at -sseof
                     -0.25, upscale-then-zoompan, concat.

THE NEVER-STRETCH LAW (Peter's ruling B, 30 Jul 2026, permanent):
  motion plays as rendered, ALWAYS. Length is met by Ken Burns WITHIN the
  beat -- native clip in full, then motion hands to motion on the last frame.
  The v1 slow-fill branch (setpts time remapping) is DELETED, not deprecated:
  variable per-beat slowdown factors gave the film an inconsistent motion
  grammar. It does not exist in v2 and never returns.

Two idempotent passes over the beats table:
  Pass A stills : rows where still_path IS NULL -> generate, mark, log ($0.08)
  Pass B clips  : rows where clip_path IS NULL AND still_path set ->
                  method registry dispatch (beats.method):
                    floor -> _kb_still at audio_duration with the beat's move
                    kling -> _animate native, then _fit_to_duration
  Hand-made stills (the playground path) are just pre-filled still_path
  columns: Pass A flows around them, Pass B treats them identically.

Requires stage 2 first: clips are born at audio_duration, so measurement
must exist. Hard-errors otherwise.
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

import requests

import db as v2db

FPS = 24
STILL_COST = 0.08
KLING_COST = 0.42
IMAGE_ENDPOINTS = {
    "seedream": "fal-ai/bytedance/seedream/v3/text-to-image",
    "nano_banana": "fal-ai/nano-banana",
    "nano_banana_2": "fal-ai/nano-banana-2",
    "flux": "fal-ai/flux-pro/v1.1",
}
DEFAULT_VIDEO_ENDPOINT = "fal-ai/kling-video/v2.5-turbo/pro/image-to-video"


def _run(cmd, desc):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True)
    if res.returncode != 0:
        tail = " | ".join(res.stderr.strip().splitlines()[-6:])
        raise RuntimeError(f"{desc} failed: {tail}")


def _probe(path: Path) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        return float(res.stdout.strip())
    except ValueError:
        return 0.0


def _download(url: str, out_path: Path) -> Path:
    r = requests.get(url, stream=True, timeout=300)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 16):
            f.write(chunk)
    return out_path


def _expand_prompt(phenomenon: str, canon: dict, style: str) -> str:
    """'{token} dist, desc' -> canon expansion + variant text (+ style contract)."""
    m = re.match(r"^\{([a-z0-9_]+)\}\s*(.*)$", phenomenon.strip())
    if m and m.group(1) in canon:
        core = f"{canon[m.group(1)]} -- {m.group(2)}" if m.group(2) else canon[m.group(1)]
    else:
        core = phenomenon.strip()
    return f"{style.strip()}. {core}" if style else core


def _gen_still(prompt: str, out_path: Path, proj, negative: str = "") -> Path | None:
    """flux path from generate_still, verbatim in the parts that matter."""
    import fal_client
    model = proj["image_model"] or "flux"
    endpoint = IMAGE_ENDPOINTS[model]
    if model == "flux":
        args = {"prompt": prompt,
                "image_size": {"width": proj["width"], "height": proj["height"]}}
        args["safety_tolerance"] = "5"
    else:
        args = {"prompt": prompt, "aspect_ratio": "16:9"}
        if "nano-banana-2" in endpoint:
            args["resolution"] = "1K"
    if negative:
        args["negative_prompt"] = negative
    try:
        result = fal_client.subscribe(endpoint, arguments=args, with_logs=False)
        images = result.get("images", [])
    except Exception as e:
        print(f"      SKIP (refused): {out_path.name} -- {type(e).__name__}. "
              f"Reword the phenomenon and re-run stage visuals.")
        return None
    if not images:
        print(f"      SKIP (no media): {out_path.name}")
        return None
    return _download(images[0]["url"], out_path)


def _kb_still(still_path: Path, out_path: Path, duration: float,
              move: str, W: int, H: int) -> Path:
    """ken_burns_still, verbatim: doctrine-varied zoompan or true static."""
    dur = float(duration)
    total_frames = max(1, int(round(dur * FPS)))
    d = total_frames
    m = (move or "").strip().lower()
    if m in ("", "static"):
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS}")
    else:
        up_w, up_h = W * 4, H * 4
        cx = "iw/2-(iw/zoom/2)"
        cy = "ih/2-(ih/zoom/2)"
        if m == "pull":
            z, x, y = "if(eq(on,0),1.16,max(1.16-0.16*on/%d,1.0))" % d, cx, cy
        elif m == "crane":
            z, x, y = "1.12", cx, "(ih-ih/zoom)*(1-on/%d)" % d
        elif m == "settle":
            z, x, y = "1.12", cx, "(ih-ih/zoom)*(on/%d)" % d
        else:
            z, x, y = "min(1.0+0.16*on/%d,1.16)" % d, cx, cy
        vf = (f"scale={up_w}:{up_h}:force_original_aspect_ratio=increase,"
              f"crop={up_w}:{up_h},"
              f"zoompan=z='{z}':d={total_frames}:x='{x}':y='{y}':"
              f"s={W}x{H}:fps={FPS},setsar=1")
    _run(["ffmpeg", "-y", "-loop", "1", "-i", str(still_path), "-vf", vf,
          "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium",
          "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), str(out_path)],
         "ken_burns ffmpeg")
    return out_path


def _is_content_policy_error(exc) -> bool:
    s = str(exc).lower()
    return ("content_policy" in s or "content checker" in s
            or "flagged by a content" in s or "unprocessable" in s)


def _animate(still_path: Path, motion_prompt: str, out_path: Path, proj):
    """animate_still verbatim: kling i2v via fal storage. Returns (path, refused)."""
    import fal_client
    endpoint = proj["video_model"] or DEFAULT_VIDEO_ENDPOINT
    try:
        image_url = fal_client.upload_file(str(still_path))
        args = {"image_url": image_url, "prompt": motion_prompt,
                "duration": proj["video_duration"] or "5"}
        if "v2.5-turbo" not in endpoint:
            args["generate_audio"] = False
        result = fal_client.subscribe(endpoint, arguments=args, with_logs=False)
        video = result.get("video") or {}
        url = video.get("url")
        if not url:
            raise RuntimeError(f"No video returned. Result: {result}")
        return _download(url, out_path), False
    except Exception as e:
        if _is_content_policy_error(e):
            print(f"      content-policy refusal -- Ken Burns takes the beat "
                  f"(never-stretch law: motion via KB, not a held frame)")
            return None, True
        raise


def _fit_to_duration(clip: Path, dur: float, out_path: Path,
                     W: int, H: int, work: Path, tag: str) -> str:
    """make_video_segment's law-compliant branches, verbatim. Returns label.
    trim | exact | kb-tail | clone-pad. The slow-fill branch is DELETED."""
    native = _probe(clip)
    scale_pad = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                 f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS}")
    if native >= dur:
        _run(["ffmpeg", "-y", "-i", str(clip), "-t", f"{dur:.3f}",
              "-vf", scale_pad, "-c:v", "libx264", "-preset", "medium",
              "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(out_path)],
             f"trim {tag}")
        return "trim"
    remainder = dur - native
    if native <= 0:
        _run(["ffmpeg", "-y", "-i", str(clip),
              "-vf", f"{scale_pad},tpad=stop_mode=clone:stop_duration={dur:.3f}",
              "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium",
              "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(out_path)],
             f"hold {tag}")
        return "hold(probe-fail)"
    if remainder >= 0.5:
        part1 = work / f"{tag}_native.mp4"
        _run(["ffmpeg", "-y", "-i", str(clip), "-vf", scale_pad,
              "-c:v", "libx264", "-preset", "medium", "-crf", "18",
              "-pix_fmt", "yuv420p", "-an", str(part1)], f"kb-tail native {tag}")
        frame = work / f"{tag}_last.png"
        _run(["ffmpeg", "-y", "-sseof", "-0.25", "-i", str(part1),
              "-frames:v", "1", "-update", "1", str(frame)],
             f"kb-tail frame {tag}")
        tail_frames = max(1, int(round(remainder * FPS)))
        part2 = work / f"{tag}_tail.mp4"
        zp = (f"scale={W*2}:{H*2},"
              f"zoompan=z='min(zoom+0.0008,1.10)':d={tail_frames}:"
              f"s={W}x{H}:fps={FPS}")
        _run(["ffmpeg", "-y", "-loop", "1", "-i", str(frame), "-vf", zp,
              "-t", f"{remainder:.3f}", "-c:v", "libx264", "-preset", "medium",
              "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(part2)],
             f"kb-tail zoom {tag}")
        lf = work / f"{tag}_list.txt"
        lf.write_text(f"file '{part1.resolve()}'\nfile '{part2.resolve()}'\n")
        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lf),
              "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
              "-crf", "18", "-pix_fmt", "yuv420p", str(out_path)],
             f"kb-tail concat {tag}")
        return f"kb-tail({native:.1f}+{remainder:.1f}s)"
    _run(["ffmpeg", "-y", "-i", str(clip),
          "-vf", f"{scale_pad},tpad=stop_mode=clone:stop_duration={remainder:.3f}",
          "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium",
          "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(out_path)],
         f"clone-pad {tag}")
    return "clone-pad(<0.5s)"


def run(con, project_dir: Path) -> None:
    if v2db.pending(con, "audio_duration"):
        raise SystemExit("stage 'visuals': beats lack audio_duration -- "
                         "run stages audio + measure first (clips are born "
                         "at their measured length).")
    proj = con.execute("SELECT * FROM project WHERE id=1").fetchone()
    canon = {r["token"]: r["description"]
             for r in con.execute("SELECT token, description FROM canon")}
    refs = {r["token"]: r["reference_paths"] for r in
            con.execute("SELECT token, reference_paths FROM canon "
                        "WHERE reference_paths IS NOT NULL "
                        "AND reference_paths NOT IN ('', '[]')")}
    style = proj["style_contract"] or ""
    W, H = proj["width"], proj["height"]
    stills_dir = project_dir / "stills"
    clips_dir = project_dir / "clips"
    work = project_dir / "work"
    for d in (stills_dir, clips_dir, work):
        d.mkdir(exist_ok=True)

    todo = v2db.pending(con, "still_path")
    print(f"   pass A stills: {len(todo)} to generate")
    for b in todo:
        m = re.match(r"^\{([a-z0-9_]+)\}", b["phenomenon"].strip())
        if m and m.group(1) in refs:
            raise SystemExit(
                f"beat {b['id']} token '{m.group(1)}' carries a reference "
                f"reference_paths -- the ref-conditioned still path is not wired "
                f"(lands with the Elijah work). Clear ref_path or wait.")
        prompt = _expand_prompt(b["phenomenon"], canon, style)
        out = stills_dir / f"shot_{b['id']:03d}.png"
        got = _gen_still(prompt, out, proj)
        v2db.log_generation(con, stage="stills",
                            model=proj["image_model"] or "flux",
                            prompt=prompt, beat_id=b["id"],
                            cost=STILL_COST if got else 0.0,
                            result_path=str(out) if got else None,
                            status="done" if got else "refused",
                            kept=1 if got else 0)
        if got:
            v2db.mark(con, b["id"], still_path=str(out))
        con.commit()

    todo = v2db.pending(con, "clip_path", "still_path IS NOT NULL")
    print(f"   pass B clips: {len(todo)} to build")
    for b in todo:
        dur = float(b["audio_duration"])
        out = clips_dir / f"shot_{b['id']:03d}.mp4"
        tag = f"b{b['id']:03d}"
        if b["method"] == "kling":
            raw = work / f"{tag}_kling.mp4"
            got, refused = _animate(Path(b["still_path"]),
                                    b["motion_prompt"] or "", raw, proj)
            if refused:
                v2db.log_generation(con, stage="clips", model="kling",
                                    prompt=b["motion_prompt"], beat_id=b["id"],
                                    cost=0.0, status="refused", kept=0)
                _kb_still(Path(b["still_path"]), out, dur, b["move"], W, H)
                label = "kb(refusal-fallback)"
                cost, model = 0.0, "ffmpeg-kb"
            else:
                label = _fit_to_duration(raw, dur, out, W, H, work, tag)
                cost = KLING_COST
                model = proj["video_model"] or DEFAULT_VIDEO_ENDPOINT
            v2db.log_generation(con, stage="clips", model=model,
                                prompt=b["motion_prompt"], beat_id=b["id"],
                                cost=cost, result_path=str(out),
                                params_json=json.dumps({"fit": label,
                                                        "dur": dur}))
        else:
            _kb_still(Path(b["still_path"]), out, dur, b["move"], W, H)
            label = f"kb({b['move'] or 'push'})"
            v2db.log_generation(con, stage="clips", model="ffmpeg-kb",
                                beat_id=b["id"], cost=0.0,
                                result_path=str(out),
                                params_json=json.dumps({"fit": label,
                                                        "dur": dur}))
        v2db.mark(con, b["id"], clip_path=str(out), status="clipped")
        con.commit()
        print(f"      beat {b['id']}: {label} -> {dur:.2f}s")
