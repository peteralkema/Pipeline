#!/usr/bin/env python3
"""
patch_tiered_button.py — TIERED RENDER step (d): the once-off button consults N.

WHY
  "Render this clip" always called Kling, regardless of where the beat sits. Now it
  routes by the SAME per-project policy as the batch: Kling if the beat is under N,
  free Ken Burns if at/after. The button becomes honest with the N you set at the
  gate — one gesture, automatic routing, no engine choice to make.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py — backend only)
  1. Extend the recreation_pipeline import: also bring in ken_burns_still and the
     tiered helpers (_tiered_kling_count / _tiered_beat_index / _tiered_duration).
  2. _run_animate_bg gains engine="kling"/duration args and branches: kenburns ->
     ken_burns_still(still, out, duration); else -> animate_still (Kling). Reports
     the engine in the done status.
  3. _handle_animate computes the engine from <project>/render_policy.json N
     (stills_dir.parent.parent is the project root, where render_policy/durations/
     _index live), maps the shot to its beat index, and passes engine+duration to
     the thread. Response now includes "engine".

  No JS change — the button is unchanged; it just routes server-side. After this,
  TIERED RENDER is fully wired: gate field sets N, batch and button both obey it.

DISCIPLINE
  Idempotent (sentinel: `ken_burns_still as _ken_burns_still`). Three anchors, each
  verified once; backs up to .pre_tieredbtn; re-compiles + rolls back on failure.
  Run from the repo root on the LAPTOP, then commit/push, then pull + restart on the
  box. (JS unchanged, but restart is needed since the handler changed; a node-check
  is included for hygiene.)
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "ken_burns_still as _ken_burns_still"

# 1. Import: pull in ken_burns_still + the tiered helpers
ANCHOR_IMPORT = '''try:
    from recreation_pipeline import animate_still as _animate_still
    _ANIMATE_OK = True
except Exception as _ae:
    _ANIMATE_OK = False
    _ANIMATE_IMPORT_ERR = str(_ae)'''
NEW_IMPORT = '''try:
    from recreation_pipeline import (
        animate_still as _animate_still,
        ken_burns_still as _ken_burns_still,
        _tiered_kling_count, _tiered_beat_index, _tiered_duration,
    )
    _ANIMATE_OK = True
except Exception as _ae:
    _ANIMATE_OK = False
    _ANIMATE_IMPORT_ERR = str(_ae)'''

# 2. _run_animate_bg: branch on engine
ANCHOR_BG = '''def _run_animate_bg(key, still_path, motion_prompt, out_path):
    try:
        _animate_still(still_path, motion_prompt, out_path)
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "done"}
    except Exception as e:
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "error", "error": str(e)}'''
NEW_BG = '''def _run_animate_bg(key, still_path, motion_prompt, out_path, engine="kling", duration=None):
    try:
        if engine == "kenburns":
            _ken_burns_still(still_path, out_path, duration)
        else:
            _animate_still(still_path, motion_prompt, out_path)
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "done", "engine": engine}
    except Exception as e:
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "error", "error": str(e)}'''

# 3. _handle_animate: compute engine from the project's N and pass it to the thread
ANCHOR_HANDLE = '''        key = _animate_key(ch, pr, shot_idx)
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "running"}
        th = _threading.Thread(target=_run_animate_bg,
                               args=(key, still_path, motion_prompt, out_path),
                               daemon=True)
        th.start()
        self._json(200, {"ok": True, "started": True, "shot": shot_idx}); return'''
NEW_HANDLE = '''        # TIERED RENDER (d): route this single beat by the same policy as the batch.
        project_root = stills_dir.parent.parent  # <project>/ — render_policy/durations/_index live here
        kling_count = _tiered_kling_count(project_root)
        beat_index = _tiered_beat_index(shot_idx, project_root)
        engine = "kling" if beat_index < kling_count else "kenburns"
        duration = _tiered_duration(beat_index, project_root)
        sys.stderr.write(f"[Animate] shot {shot_idx:03d} -> {engine} (beat {beat_index}, N={kling_count})\\n")
        key = _animate_key(ch, pr, shot_idx)
        with _ANIMATE_LOCK:
            _ANIMATE_JOBS[key] = {"status": "running"}
        th = _threading.Thread(target=_run_animate_bg,
                               args=(key, still_path, motion_prompt, out_path, engine, duration),
                               daemon=True)
        th.start()
        self._json(200, {"ok": True, "started": True, "shot": shot_idx, "engine": engine}); return'''


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
        ("recreation_pipeline import", ANCHOR_IMPORT, NEW_IMPORT),
        ("_run_animate_bg", ANCHOR_BG, NEW_BG),
        ("_handle_animate tail", ANCHOR_HANDLE, NEW_HANDLE),
    ]
    for label, old, _ in edits:
        n = src.count(old)
        if n == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written. "
                f"(Confirm the tiered-routing patch is applied to recreation_pipeline.py and the box is in sync.)")
        if n > 1:
            die(f"anchor for {label} found {n}x (expected 1) — ambiguous; nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_tieredbtn")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    check = TARGET.read_text()
    problems = []
    if MARKER not in check:
        problems.append("import missing")
    if 'engine == "kenburns"' not in check:
        problems.append("_run_animate_bg routing missing")
    if 'beat_index < kling_count' not in check:
        problems.append("_handle_animate routing missing")
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
    print("   once-off button now routes Kling vs Ken Burns by the project's N")
    print()
    print("AFTER you pull on the box, restart + node-check:")
    print("   systemctl --user restart mission-control.service")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   print(\"script blocks:\", len(b))")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")


if __name__ == "__main__":
    main()
