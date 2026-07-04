#!/usr/bin/env python3
"""
patch_clip_inherit.py — CLIP-MERGE, engine side: a beat toggled "inherit"
renders NO clip of its own; it plays the unused tail of its predecessor's
already-paid Kling atom. Recovers the footage all-trim throws away, and an
inherited beat can never black-frame, mis-dimension, or need a re-render.

DESIGN (derived clip, not index surgery — the assembler is UNTOUCHED):
  - render_policy.json gains "inherit_prev": [beat,...]
  - routing precedence: inherit > kb_override > front-N Kling
  - main render loop SKIPS inherit beats (no fal call); a second pass runs
    after all source atoms exist and derives shot_<B>.mp4 via ffmpeg -ss
  - chains supported: walk back to the nearest non-inherited ancestor,
    summing consumed durations from durations.json (frozen timing source)
  - every failure is benign: no predecessor / source missing / nothing left
    in the atom -> ken_burns_still on B's OWN still (free) with a warning.
    Timing never derives from any of this; sync cannot drift.

5 anchored edits in shared/recreation_pipeline.py (post-kb-toggle text):
  1. helper _inherit_prev_set() after _kb_override_set()
  2. helper inherit_prev_clip() before _is_content_policy_error()
  3. cmd_finish routing: three-way engine choice
  4. banner + --plan awareness of inherit beats
  5. main loop defers inherit beats; second (derive) pass inserted after it

SAFETY: verify-anchors-exactly-once, in-memory patch, py_compile to temp
BEFORE writing, backup to .pre_inherit. Idempotent.

Run from the repo root:  python3 shared/patch_clip_inherit.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "recreation_pipeline.py"
BACKUP = TARGET.with_suffix(".py.pre_inherit")

MARKER = "_inherit_prev_set"

HELPER_SET = '''def _inherit_prev_set(project_root):
    """Per-beat clip-merge: render_policy.json {"inherit_prev": [beat,...]}.
    A beat listed here renders NO clip of its own — it plays the unused tail
    of its predecessor's atom (derived in the inherit pass of cmd_finish).
    Precedence above kb_override. Empty set when absent."""
    import json as _json
    rp = project_root / "render_policy.json"
    if rp.is_file():
        try:
            return {int(x) for x in _json.loads(rp.read_text()).get("inherit_prev", [])}
        except Exception:
            return set()
    return set()


'''

HELPER_CLIP = '''def inherit_prev_clip(src_clip: Path, out_path: Path, offset: float) -> Path:
    """CLIP-MERGE derivation — write out_path as src_clip seeked from `offset`
    onward (the unused tail of an already-paid atom). The assembler then treats
    it as an ordinary clip: trims to the beat's frozen duration, or fills if the
    tail runs short. Raises when the source is missing or (checked via ffprobe)
    the offset leaves under 0.3s, so the caller can fall back to the free
    Ken-Burns floor instead of shipping a near-empty clip."""
    import subprocess
    src_clip = Path(src_clip)
    if not src_clip.exists():
        raise RuntimeError(f"source clip missing: {src_clip.name}")
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", str(src_clip)],
                        capture_output=True, text=True)
    try:
        native = float(pr.stdout.strip())
    except ValueError:
        native = 0.0
    if native - offset < 0.30:
        raise RuntimeError(f"nothing left in the atom (native {native:.2f}s, offset {offset:.2f}s)")
    cmd = ["ffmpeg", "-y", "-ss", f"{offset:.3f}", "-i", str(src_clip),
           "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-an", str(out_path)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        tail = " | ".join(res.stderr.strip().splitlines()[-4:])
        raise RuntimeError(f"inherit ffmpeg failed: {tail}")
    return out_path


'''

INHERIT_PASS = '''
    # ── inherit pass: derive clip-merge beats from their source atoms ──────────
    # Runs AFTER the main loop so every source clip exists. Walks chains back to
    # the nearest non-inherited ancestor, summing consumed span from the frozen
    # durations.json. All failures fall back to the free Ken-Burns floor on the
    # beat's OWN still — the cut always assembles, timing is never touched.
    _inh_beats = [(s, bi) for s, bi, e in plan if e == "inherit"]
    if _inh_beats:
        _b2s = {b: s["index"] for s, b, _e in plan}
        for s, bi in _inh_beats:
            clip = p["clips"] / f"shot_{s['index']:03d}.mp4"
            if clip.exists() and not args.force:
                print(f"  [inherit] shot {s['index']:03d} already done, skipping")
                continue
            still = p["stills"] / f"shot_{s['index']:03d}.png"
            dur_b = _tiered_duration(bi, project_root) or float(SHOT_DURATION)
            j = bi - 1
            offset = 0.0
            while j >= 0 and j in inherit_prev:
                offset += _tiered_duration(j, project_root) or float(SHOT_DURATION)
                j -= 1
            if j < 0:
                print(f"  [inherit] beat {bi}: no predecessor — Ken Burns fallback (free)")
                ken_burns_still(still, clip, dur_b)
                continue
            offset += _tiered_duration(j, project_root) or float(SHOT_DURATION)
            src = p["clips"] / f"shot_{_b2s.get(j, j + 1):03d}.mp4"
            try:
                inherit_prev_clip(src, clip, offset)
                print(f"  [inherit] shot {s['index']:03d} <- beat {j}'s atom @ {offset:.2f}s (free)")
            except Exception as e:
                print(f"  [inherit] beat {bi}: {e} — Ken Burns fallback (free)")
                ken_burns_still(still, clip, dur_b)
'''

EDITS = [
    # 1. _inherit_prev_set after _kb_override_set
    (
        "    return set()\n"
        "\n"
        "\n"
        "def _tiered_beat_index(engine_shot, project_root):",

        "    return set()\n"
        "\n"
        "\n"
        + HELPER_SET +
        "def _tiered_beat_index(engine_shot, project_root):",
    ),
    # 2. inherit_prev_clip before the content-policy helper
    (
        'def _is_content_policy_error(exc) -> bool:',
        HELPER_CLIP + 'def _is_content_policy_error(exc) -> bool:',
    ),
    # 3. routing: three-way precedence inherit > kb_override > front-N
    (
        '''    kling_count = _tiered_kling_count(project_root, getattr(args, "kling_count", None))
    kb_over = _kb_override_set(project_root)
    plan = []
    for s in shots:
        bi = _tiered_beat_index(s["index"], project_root)
        engine = "kling" if (bi < kling_count and bi not in kb_over) else "kenburns"
        plan.append((s, bi, engine))''',

        '''    kling_count = _tiered_kling_count(project_root, getattr(args, "kling_count", None))
    kb_over = _kb_override_set(project_root)
    inherit_prev = _inherit_prev_set(project_root)
    plan = []
    for s in shots:
        bi = _tiered_beat_index(s["index"], project_root)
        if bi in inherit_prev:
            engine = "inherit"
        elif bi < kling_count and bi not in kb_over:
            engine = "kling"
        else:
            engine = "kenburns"
        plan.append((s, bi, engine))''',
    ),
    # 4. banner counts inherit beats separately
    (
        '''    n_kling = sum(1 for _, _, e in plan if e == "kling")
    n_kb = len(plan) - n_kling
    _clip_cost = 0.35 if "v2.5-turbo" in VIDEO_ENDPOINT else 0.42
    print(f"TIERED RENDER: N={kling_count}  ->  {n_kling} Kling (~${n_kling * _clip_cost:.2f}) "
          f"+ {n_kb} Ken Burns (free)")''',

        '''    n_kling = sum(1 for _, _, e in plan if e == "kling")
    n_inherit = sum(1 for _, _, e in plan if e == "inherit")
    n_kb = len(plan) - n_kling - n_inherit
    _clip_cost = 0.35 if "v2.5-turbo" in VIDEO_ENDPOINT else 0.42
    print(f"TIERED RENDER: N={kling_count}  ->  {n_kling} Kling (~${n_kling * _clip_cost:.2f}) "
          f"+ {n_kb} Ken Burns (free)")
    if n_inherit:
        print(f"  inherit-prev: {n_inherit} beat(s) ride their predecessor's atom "
              f"(free; recovered footage)")''',
    ),
    # 5. main loop defers inherit beats; derive pass inserted after the loop
    (
        '''        if clip.exists() and not args.force:
            print(f"  [{s['index']}/{len(shots)}] already done, skipping")
        elif engine == "kling":
            print(f"  [{s['index']}/{len(shots)}] Kling animating...")
            animate_still(still, s["motion_prompt"], clip)
        else:
            dur = _tiered_duration(bi, project_root) or float(SHOT_DURATION)
            print(f"  [{s['index']}/{len(shots)}] Ken Burns ({dur:.2f}s, free)...")
            ken_burns_still(still, clip, dur)
        clip_paths.append(clip)

    if getattr(args, "animate_only", False):''',

        '''        if clip.exists() and not args.force:
            print(f"  [{s['index']}/{len(shots)}] already done, skipping")
        elif engine == "inherit":
            print(f"  [{s['index']}/{len(shots)}] inherit — deferred to the inherit pass (free)")
        elif engine == "kling":
            print(f"  [{s['index']}/{len(shots)}] Kling animating...")
            animate_still(still, s["motion_prompt"], clip)
        else:
            dur = _tiered_duration(bi, project_root) or float(SHOT_DURATION)
            print(f"  [{s['index']}/{len(shots)}] Ken Burns ({dur:.2f}s, free)...")
            ken_burns_still(still, clip, dur)
        clip_paths.append(clip)
''' + INHERIT_PASS + '''
    if getattr(args, "animate_only", False):''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (_inherit_prev_set present) — no-op.")
        return

    if "_kb_override_set" not in src:
        sys.exit("!! prerequisite missing: patch_kenburns_toggle not applied — anchors target the post-kb text.")

    for i, (old, _new) in enumerate(EDITS, 1):
        n = src.count(old)
        if n != 1:
            sys.exit(f"!! anchor {i} matched {n} times (need exactly 1) — file drifted, NOT patched.\n"
                     f"   anchor starts: {old.splitlines()[0]!r}")

    patched = src
    for old, new in EDITS:
        patched = patched.replace(old, new)

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(patched)
        tmp = tf.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        sys.exit(f"!! patched text does not compile — target NOT modified.\n{e}")
    finally:
        Path(tmp).unlink(missing_ok=True)

    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(patched, encoding="utf-8")
    print(f"patched {TARGET.name} (backup: {BACKUP.name})")
    print("  1. _inherit_prev_set() helper")
    print("  2. inherit_prev_clip() derivation (ffprobe guard, benign failures)")
    print("  3. routing: inherit > kb_override > front-N")
    print("  4. banner + inherit count")
    print("  5. main loop defers; inherit pass derives after all atoms exist")


if __name__ == "__main__":
    main()
