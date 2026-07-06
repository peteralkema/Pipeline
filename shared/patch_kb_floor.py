#!/usr/bin/env python3
"""
patch_kb_floor.py — FLOOR-FIRST routing in recreation_pipeline.py (policy-only).

Turns "Kling by default (front-N)" into "free Ken-Burns floor by default, add Kling
per-beat from zero." Driven entirely by render_policy.json:
  kling_count: 0            -> nothing routes to Kling except the override list
  kling_override: [beat...] -> these beats render Kling atoms (additive)
No new CLI flag. MC's "Floor all (free)" button writes kling_count:0 + kling_override:[].

Four edits:
  1. _kling_override_set() reader (mirrors _kb_override_set()).
  2. additive routing in cmd_finish's plan loop:
       kling if (bi in kling_override) OR (bi < kling_count and bi not in kb_override)
     Backward-compatible: no kling_override key -> empty set -> identical to today.
  3. floor marker: the Ken-Burns branch touches clips/shot_NNN.kbfloor beside the clip
     (assembly globs shot_*.mp4, never the sidecar) so a floored clip is identifiable.
  4. delete-on-upgrade: before skip-if-exists, a beat now in kling_override whose clip
     is a marked KB floor gets clip+marker removed, so cmd_finish re-renders it Kling.
     KB->Kling deletes a FREE marked clip; Kling->KB never deletes (a paid clip has no
     marker; downgrading just drops it from kling_override, its atom stays on disk).

Idempotent (sentinel: KB_FLOOR_APPLIED). Each anchor verified to match exactly once;
py_compile before the target is touched; backup to recreation_pipeline.py.pre_kbfloor.
Pure ASCII.
"""
import sys, py_compile, tempfile, shutil
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "recreation_pipeline.py"
BACKUP = TARGET.with_suffix(".py.pre_kbfloor")
SENTINEL = "KB_FLOOR_APPLIED"

# --- Edit 1: add _kling_override_set() right after _kb_override_set(). Anchor on
#     the start of _inherit_prev_set so we insert between the two readers. ---
ANCHOR_READER = '''def _inherit_prev_set(project_root):'''

NEW_READER = '''def _kling_override_set(project_root):
    """FLOOR-FIRST additive Kling: render_policy.json {"kling_override": [beat,...]}.
    KB_FLOOR_APPLIED. A beat listed here renders a Kling atom regardless of
    kling_count (floor-first runs kling_count:0, so ONLY these turn Kling on).
    Empty set when absent -> routing identical to pre-floor behaviour."""
    import json as _json
    rp = project_root / "render_policy.json"
    if rp.is_file():
        try:
            return {int(x) for x in _json.loads(rp.read_text()).get("kling_override", [])}
        except Exception:
            return set()
    return set()


def _inherit_prev_set(project_root):'''

# --- Edit 2: routing. The plan loop reads kb_over/inherit_prev; add kling_over and
#     make the kling branch additive. Anchor the exact plan-build block. ---
ANCHOR_PLAN = '''    kb_over = _kb_override_set(project_root)
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
        plan.append((s, bi, engine))'''

NEW_PLAN = '''    kb_over = _kb_override_set(project_root)
    inherit_prev = _inherit_prev_set(project_root)
    kling_over = _kling_override_set(project_root)  # KB_FLOOR_APPLIED (additive)
    plan = []
    for s in shots:
        bi = _tiered_beat_index(s["index"], project_root)
        if bi in inherit_prev:
            engine = "inherit"
        elif (bi in kling_over) or (bi < kling_count and bi not in kb_over):
            engine = "kling"
        else:
            engine = "kenburns"
        plan.append((s, bi, engine))'''

# --- Edit 3+4: the render loop. Add delete-on-upgrade before skip-if-exists, and a
#     floor marker after the Ken-Burns render. Anchor the whole loop body. ---
ANCHOR_LOOP = '''    clip_paths = []
    for s, bi, engine in plan:
        still = p["stills"] / f"shot_{s['index']:03d}.png"
        clip  = p["clips"] / f"shot_{s['index']:03d}.mp4"
        if clip.exists() and not args.force:
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
        clip_paths.append(clip)'''

NEW_LOOP = '''    clip_paths = []
    for s, bi, engine in plan:
        still = p["stills"] / f"shot_{s['index']:03d}.png"
        clip  = p["clips"] / f"shot_{s['index']:03d}.mp4"
        _kbmark = p["clips"] / f"shot_{s['index']:03d}.kbfloor"  # KB_FLOOR_APPLIED
        # delete-on-upgrade: a beat now routed to Kling whose existing clip is a
        # MARKED free floor gets discarded so it re-renders as a paid atom.
        # KB->Kling deletes a free clip; a paid Kling clip carries no marker, so
        # Kling->KB never deletes (the beat simply leaves kling_override).
        if engine == "kling" and clip.exists() and _kbmark.exists() and not args.force:
            print(f"  [{s['index']}/{len(shots)}] upgrade KB->Kling: dropping free floor clip")
            clip.unlink(missing_ok=True)
            _kbmark.unlink(missing_ok=True)
        if clip.exists() and not args.force:
            print(f"  [{s['index']}/{len(shots)}] already done, skipping")
        elif engine == "inherit":
            print(f"  [{s['index']}/{len(shots)}] inherit — deferred to the inherit pass (free)")
        elif engine == "kling":
            print(f"  [{s['index']}/{len(shots)}] Kling animating...")
            animate_still(still, s["motion_prompt"], clip)
            _kbmark.unlink(missing_ok=True)  # paid atom carries no floor marker
        else:
            dur = _tiered_duration(bi, project_root) or float(SHOT_DURATION)
            print(f"  [{s['index']}/{len(shots)}] Ken Burns ({dur:.2f}s, free)...")
            ken_burns_still(still, clip, dur)
            _kbmark.write_text("kbfloor")  # mark as a free, regenerable floor clip
        clip_paths.append(clip)'''


def die(msg):
    print(f"FAIL: {msg}  Nothing written.", file=sys.stderr)
    sys.exit(1)


def main():
    if not TARGET.is_file():
        die(f"target not found: {TARGET}")
    src = TARGET.read_text()
    if SENTINEL in src:
        print("Already applied (sentinel present). No-op.")
        return
    for label, anchor in (("reader", ANCHOR_READER), ("plan", ANCHOR_PLAN), ("loop", ANCHOR_LOOP)):
        n = src.count(anchor)
        if n != 1:
            die(f"anchor '{label}' matched {n} times (need exactly 1) — recreation_pipeline.py drifted.")
    new = (src.replace(ANCHOR_READER, NEW_READER, 1)
              .replace(ANCHOR_PLAN, NEW_PLAN, 1)
              .replace(ANCHOR_LOOP, NEW_LOOP, 1))
    for need in (SENTINEL, "_kling_override_set", "kling_over", ".kbfloor"):
        if need not in new:
            die(f"post-edit check failed (missing {need}).")
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
        tf.write(new); tmp = tf.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        die(f"py_compile failed: {e}")
    finally:
        Path(tmp).unlink(missing_ok=True)
    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(new)
    print(f"OK — patched {TARGET.name}  (floor-first routing + delete-on-upgrade)")
    print(f"     backup: {BACKUP.name}")
    print("Verify:  grep -n 'KB_FLOOR_APPLIED' shared/recreation_pipeline.py")


if __name__ == "__main__":
    main()
