#!/usr/bin/env python3
"""
patch_tiered_routing.py — TIERED RENDER step (b): route the batch animate loop.

WHY
  The Ken Burns producer (step a) is proven. This wires the routing: render the
  first N beats with Kling (motion where attention lives) and the rest with the
  free Ken Burns floor. The cost scales with the channel instead of being a flat
  upfront bet.

WHAT THIS DOES (one file: shared/recreation_pipeline.py)
  1. Three helpers (before cmd_finish):
     _tiered_kling_count(project_root, override) — N from --kling-count > render_policy.json > 40
     _tiered_beat_index(engine_shot, project_root) — 1-based engine shot -> 0-based timeline beat (via _index.json; falls back to shot-1)
     _tiered_duration(beat_index, project_root)   — Whisper duration from durations.json, or None
  2. cmd_finish's animate loop now ROUTES each shot: kling if beat_index < N else
     Ken Burns rendered at the beat's real measured duration. Skip-existing guard
     kept (so raising N never silently re-spends). Prints a routing summary.
  3. finish subparser gains:
     --kling-count N  (override the policy; default 40)
     --plan           (print routing + cost estimate and exit; no render, no cost)

  Policy source order: --kling-count flag > <project_root>/render_policy.json
  {"kling_count": N} > global default 40. The gate field (step c) writes the file;
  the once-off button (step d) reads the same policy — both come next.

  Assembly is UNCHANGED — it cannot tell a Ken Burns clip from a Kling clip.

DISCIPLINE
  Idempotent (sentinel: `def _tiered_kling_count`). Three anchors, each verified
  once; backs up to .pre_tiered; re-compiles + rolls back on failure. Run from the
  repo root on the LAPTOP, then commit/push, then pull on the box. (No restart —
  not the always-on server.)
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/recreation_pipeline.py")
MARKER = "def _tiered_kling_count"

# 1. Helpers before cmd_finish
ANCHOR_HELPERS = "def cmd_finish(args):"
NEW_HELPERS = '''def _tiered_kling_count(project_root, override=None):
    """TIERED RENDER policy N: first N beats Kling, the rest Ken Burns.
    Precedence: --kling-count override > render_policy.json > default 40."""
    import json as _json
    if override is not None:
        return max(0, int(override))
    rp = project_root / "render_policy.json"
    if rp.is_file():
        try:
            return max(0, int(_json.loads(rp.read_text()).get("kling_count", 40)))
        except Exception:
            return 40
    return 40


def _tiered_beat_index(engine_shot, project_root):
    """Map a 1-based engine shot to its 0-based timeline beat index via _index.json.
    Falls back to engine_shot-1 (pure Mode A) when the map is absent."""
    import json as _json
    idx = project_root / "_index.json"
    if idx.is_file():
        try:
            m = _json.loads(idx.read_text())
            if str(engine_shot) in m:
                return int(m[str(engine_shot)])
        except Exception:
            pass
    return engine_shot - 1


def _tiered_duration(beat_index, project_root):
    """Whisper-measured duration for a beat from durations.json, or None if absent."""
    import json as _json
    dp = project_root / "durations.json"
    if dp.is_file():
        try:
            e = _json.loads(dp.read_text()).get(str(beat_index))
            if e and "duration" in e:
                return float(e["duration"])
        except Exception:
            pass
    return None


def cmd_finish(args):'''

# 2. Replace the animate loop with the routed version
ANCHOR_LOOP = '''    print(f"Animating {len(shots)} stills with Kling (this is the expensive part)...")
    clip_paths = []
    for s in shots:
        still = p["stills"] / f"shot_{s['index']:03d}.png"
        clip  = p["clips"] / f"shot_{s['index']:03d}.mp4"
        if clip.exists() and not args.force:
            print(f"  [{s['index']}/{len(shots)}] already done, skipping")
        else:
            print(f"  [{s['index']}/{len(shots)}] animating...")
            animate_still(still, s["motion_prompt"], clip)
        clip_paths.append(clip)'''
NEW_LOOP = '''    project_root = p["root"].parent  # durations.json / _index.json / render_policy.json live one level up
    kling_count = _tiered_kling_count(project_root, getattr(args, "kling_count", None))
    plan = []
    for s in shots:
        bi = _tiered_beat_index(s["index"], project_root)
        engine = "kling" if bi < kling_count else "kenburns"
        plan.append((s, bi, engine))
    n_kling = sum(1 for _, _, e in plan if e == "kling")
    n_kb = len(plan) - n_kling
    print(f"TIERED RENDER: N={kling_count}  ->  {n_kling} Kling (~${n_kling * 0.42:.2f}) "
          f"+ {n_kb} Ken Burns (free)")
    if getattr(args, "plan", False):
        for s, bi, engine in plan:
            dur = _tiered_duration(bi, project_root)
            durtxt = (f"{dur:.2f}s" if dur is not None else "?")
            print(f"  shot {s['index']:03d}  beat {bi:>3}  {durtxt:>7}  -> {engine}")
        print("(--plan: routing only, nothing rendered, no cost)")
        return
    clip_paths = []
    for s, bi, engine in plan:
        still = p["stills"] / f"shot_{s['index']:03d}.png"
        clip  = p["clips"] / f"shot_{s['index']:03d}.mp4"
        if clip.exists() and not args.force:
            print(f"  [{s['index']}/{len(shots)}] already done, skipping")
        elif engine == "kling":
            print(f"  [{s['index']}/{len(shots)}] Kling animating...")
            animate_still(still, s["motion_prompt"], clip)
        else:
            dur = _tiered_duration(bi, project_root) or float(SHOT_DURATION)
            print(f"  [{s['index']}/{len(shots)}] Ken Burns ({dur:.2f}s, free)...")
            ken_burns_still(still, clip, dur)
        clip_paths.append(clip)'''

# 3. Subparser args (between --assemble-only and set_defaults)
ANCHOR_SUB = '''    c.add_argument("--assemble-only", action="store_true",
                   help="re-stitch from existing clips/voice/music only (no rendering, no cost)")
    c.set_defaults(func=cmd_finish)'''
NEW_SUB = '''    c.add_argument("--assemble-only", action="store_true",
                   help="re-stitch from existing clips/voice/music only (no rendering, no cost)")
    c.add_argument("--kling-count", type=int, default=None,
                   help="TIERED RENDER: render the first N beats with Kling, the rest with free "
                        "Ken Burns (overrides render_policy.json; default 40)")
    c.add_argument("--plan", action="store_true",
                   help="TIERED RENDER: print the Kling/Ken-Burns routing and exit (no render, no cost)")
    c.set_defaults(func=cmd_finish)'''


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
        ("tiered helpers", ANCHOR_HELPERS, NEW_HELPERS),
        ("animate loop", ANCHOR_LOOP, NEW_LOOP),
        ("finish subparser", ANCHOR_SUB, NEW_SUB),
    ]
    for label, old, _ in edits:
        n = src.count(old)
        if n == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written. "
                f"(Confirm the kenburns producer patch is applied and the box is in sync.)")
        if n > 1:
            die(f"anchor for {label} found {n}x (expected 1) — ambiguous; nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_tiered")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    check = TARGET.read_text()
    problems = []
    if MARKER not in check:
        problems.append("_tiered_kling_count missing")
    if "ken_burns_still(still, clip, dur)" not in check:
        problems.append("routed loop missing")
    if '"--kling-count"' not in check:
        problems.append("--kling-count arg missing")
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
    print("   animate loop now routes Kling vs Ken Burns by beat index < N")
    print("   added --kling-count N and --plan to `finish`")
    print()
    print("Prove the routing on paper (no cost), e.g. N=3 over figures-test-2's 10 beats:")
    print("   python shared/recreation_pipeline.py finish \\")
    print("     --project sacred-dawn/projects/figures-test-2/modea \\")
    print("     --animate-only --plan --kling-count 3")


if __name__ == "__main__":
    main()
