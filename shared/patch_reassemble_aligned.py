#!/usr/bin/env python3
"""
patch_reassemble_aligned.py -- route Re-assemble through the ALIGNED assembler (v1.2).

WHY (drift found after re-render + Re-assemble on esther--1)
  There are TWO assemblers in the codebase and only one honors the beat->shot map:
    * assemble_episode.py  -- iterates BEATS, uses _index.json (rev_map) to place each
      beat's clip, holds each to the FROZEN durations.json. This is what the launched
      convergence run uses. ALIGNMENT-CORRECT.
    * recreation_pipeline.assemble() -- pairs clip_paths to durations POSITIONALLY via
      zip(), ignores _index.json, and re-derives durations LIVE from storyboard.json
      (re-running Whisper auto-align each call). DRIFTS the moment shot-order != beat-order
      or the live re-align shifts targets.
  The v1.1 Re-assemble button shelled `finish --assemble-only`, which calls the SECOND
  (wrong) assembler -> drift. This routes the button through the FIRST (correct) one,
  the exact call convergence_leg makes, so the two paths can never diverge again.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  Rewrites _run_assemble_bg to do what convergence does:
    1. RE-POOL: copy <project>/modea/clips/shot_*.mp4 -> <project>/clips/ (overwrite), so
       re-rendered clips actually reach assembly (assemble_episode reads the pool, not modea).
    2. SHELL assemble_episode.py with the convergence flagset:
         --durations <project>/durations.json   (frozen audio-leg truth)
         --index     <project>/_index.json       (authoritative beat->shot map)
         --voiceover <project>/voiceover.mp3
         --project   <project>
         --clips     <project>/clips
         --out       <project>/final_video.mp4
         --no-music
  _handle_assemble already resolves the project; it now passes project_dir so the bg
  runner can locate durations/_index/voiceover/clips. No page-JS change (button + polling
  unchanged); APP_VERSION bumped to v1.2 for traceability.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `assemble_episode.py`). Anchors verified once;
  .pre_aligned backup; py_compile; rollback on failure. Requires v1.1.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "assemble_episode.py"  # appears only after this patch (the button never referenced it before)

# --- 1. replace the body of _run_assemble_bg ---------------------------------
OLD_BG = '''def _run_assemble_bg(key, cwd, engine_project):
    """Re-stitch final_video.mp4 from existing clips via `finish --assemble-only`
    (no render cost). Subprocess so it uses the same path resolution the legs do."""
    import subprocess as _sp
    try:
        cmd = [sys.executable, str(Path(_SHARED) / "recreation_pipeline.py"),
               "finish", "--project", engine_project, "--assemble-only"]
        r = _sp.run(cmd, cwd=str(cwd), capture_output=True, text=True)
        if r.returncode == 0:
            with _ASSEMBLE_LOCK:
                _ASSEMBLE_JOBS[key] = {"status": "done"}
        else:
            tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]
            with _ASSEMBLE_LOCK:
                _ASSEMBLE_JOBS[key] = {"status": "error", "error": " / ".join(tail) or "assemble failed"}
    except Exception as e:
        with _ASSEMBLE_LOCK:
            _ASSEMBLE_JOBS[key] = {"status": "error", "error": str(e)}'''

NEW_BG = '''def _run_assemble_bg(key, project_dir):
    """Re-stitch final_video.mp4 using the SAME aligned assembler the launched run uses
    (assemble_episode.py + _index.json + frozen durations.json) -- NOT recreation_pipeline
    .assemble(), which ignores the beat->shot map and drifts. Re-pools the engine clips
    first so re-rendered clips reach assembly."""
    import subprocess as _sp
    import shutil
    try:
        project_dir = Path(project_dir)
        pool = project_dir / "clips"
        engine_clips = project_dir / "modea" / "clips"
        durations = project_dir / "durations.json"
        index_json = project_dir / "_index.json"
        voiceover = project_dir / "voiceover.mp3"
        final_out = project_dir / "final_video.mp4"

        # preflight the alignment inputs (same set convergence requires)
        missing = [p.name for p in (durations, index_json, voiceover) if not p.exists()]
        if missing:
            with _ASSEMBLE_LOCK:
                _ASSEMBLE_JOBS[key] = {"status": "error",
                    "error": "missing alignment inputs: " + ", ".join(missing)}
            return

        # RE-POOL: copy modea/clips/shot_*.mp4 -> <project>/clips/ (overwrite), mirroring
        # convergence_leg._pool_clips, so re-rendered clips actually reach assembly.
        pool.mkdir(parents=True, exist_ok=True)
        if engine_clips.exists() and engine_clips.resolve() != pool.resolve():
            for f in sorted(engine_clips.glob("shot_*.mp4")):
                shutil.copy2(f, pool / f.name)

        # SHELL the aligned assembler with the exact convergence flagset.
        cmd = [sys.executable, str(Path(_SHARED) / "assemble_episode.py"),
               "--durations", str(durations),
               "--index", str(index_json),
               "--voiceover", str(voiceover),
               "--project", str(project_dir),
               "--clips", str(pool),
               "--out", str(final_out),
               "--no-music"]
        r = _sp.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and final_out.exists():
            with _ASSEMBLE_LOCK:
                _ASSEMBLE_JOBS[key] = {"status": "done"}
        else:
            tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]
            with _ASSEMBLE_LOCK:
                _ASSEMBLE_JOBS[key] = {"status": "error", "error": " / ".join(tail) or "assemble failed"}
    except Exception as e:
        with _ASSEMBLE_LOCK:
            _ASSEMBLE_JOBS[key] = {"status": "error", "error": str(e)}'''

# need shutil imported in the module (used by the re-pool). Check + add if absent handled in main.

# --- 2. update _handle_assemble to pass project_dir, not cwd/engine_project ---
OLD_HANDLE = '''        try:
            paths = resolve_paths(ch, pr, _REPO)
            project_dir = Path(paths["project"])
            cwd = project_dir.parent                 # the channel's projects/ dir
            engine_project = f"{project_dir.name}/modea"   # <slug>/modea (proven by enoch1)
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)}); return
        key = _assemble_key(ch, pr)
        with _ASSEMBLE_LOCK:
            running = (_ASSEMBLE_JOBS.get(key) or {}).get("status") == "running"
            if not running:
                _ASSEMBLE_JOBS[key] = {"status": "running"}
        if running:
            self._json(200, {"ok": True, "already": True}); return
        th = _threading.Thread(target=_run_assemble_bg,
                               args=(key, cwd, engine_project), daemon=True)
        th.start()'''

NEW_HANDLE = '''        try:
            paths = resolve_paths(ch, pr, _REPO)
            project_dir = Path(paths["project"])
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)}); return
        key = _assemble_key(ch, pr)
        with _ASSEMBLE_LOCK:
            running = (_ASSEMBLE_JOBS.get(key) or {}).get("status") == "running"
            if not running:
                _ASSEMBLE_JOBS[key] = {"status": "running"}
        if running:
            self._json(200, {"ok": True, "already": True}); return
        th = _threading.Thread(target=_run_assemble_bg,
                               args=(key, project_dir), daemon=True)
        th.start()'''

OLD_VER = '''APP_VERSION = "v1.1"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
NEW_VER = '''APP_VERSION = "v1.2"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found -- run from the repo root on the laptop.")
    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) -- no changes made.")
        return
    if OLD_VER not in src:
        die("APP_VERSION v1.1 anchor not found -- apply patch_reassemble_button.py (v1.1) first. Nothing written.")
    if "_SHARED" not in src:
        die("_SHARED not found -- needed to locate assemble_episode.py. Nothing written.")

    edits = [
        ("bg runner", OLD_BG, NEW_BG),
        ("handler",   OLD_HANDLE, NEW_HANDLE),
        ("version",   OLD_VER, NEW_VER),
    ]
    for label, old, _ in edits:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND -- file shape changed; nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) -- ambiguous; nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_aligned")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    problems = []
    if "assemble_episode.py" not in chk: problems.append("aligned assembler not wired")
    if "_index.json" not in chk: problems.append("index map not referenced")
    if "def _run_assemble_bg(key, project_dir)" not in chk: problems.append("bg signature not updated")
    if "args=(key, project_dir)" not in chk: problems.append("handler not passing project_dir")
    if 'APP_VERSION = "v1.2"' not in chk: problems.append("version not bumped")
    if "import subprocess as _sp\n    import shutil" not in chk: problems.append("local shutil import missing in bg runner")
    if problems:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed (" + "; ".join(problems) + ") -- restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile -- restored.\\n{e}")

    print(f"OK patched {TARGET}  (backup {backup.name})")
    print("   Re-assemble now routes through assemble_episode.py (+ _index.json + frozen")
    print("   durations.json) -- the SAME aligned assembler the launched run uses. No more drift.")
    print("")
    print("AFTER pull on the box: restart, verify v1.2, node-check, then RE-TEST on esther--1.")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   (then the usual version-check + node-check; want v1.2, matching sha, PAGE_JS_VALID)")
    print("   Then click Re-assemble on esther--1 and confirm alignment is restored.")

if __name__ == "__main__":
    main()
