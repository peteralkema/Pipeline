#!/usr/bin/env python3
"""
patch_assemble_only_paths.py -- fix assemble-only root-artifact paths (v1.2 backend).

WHY (surfaced by the v1.1 Re-assemble button on esther--1)
  `finish --assemble-only` is invoked with --project "<slug>/modea" (the engine form, so
  clips under modea/ resolve). But proj_paths then sets p["root"] = "<slug>/modea", so
  p["voice"] and p["final"] land UNDER modea/ -- whereas voiceover.mp3 and final_video.mp4
  actually live at the PROJECT ROOT (one level up), which is exactly why the normal finish
  path computes `project_root = p["root"].parent`. Result: assemble-only fails with
  "missing voiceover: <slug>/modea/voiceover.mp3" and (if it got further) would write the
  final video under modea/ instead of the root.

WHAT THIS DOES (one file: shared/recreation_pipeline.py)
  In the assemble-only branch only, resolve the ROOT-level artifacts from p["root"].parent:
    - voiceover : <root>/voiceover.mp3   (was p["voice"] = <root>/modea/voiceover.mp3)
    - final     : <root>/final_video.mp4 (was p["final"])
    - music     : <root>/music.mp3       (was p["root"]/music.mp3 = modea/music.mp3)
  Clips stay p["clips"] (= <root>/modea/clips) -- those ARE under modea and were correct.
  This matches where the launched convergence_leg already reads voice + writes final.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `assemble-only: root-level artifacts`). Single anchor
  verified once; .pre_asmpaths backup; py_compile; rollback on failure. recreation_pipeline
  change only (no page change -> Mission Control version unchanged).
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/recreation_pipeline.py")
MARKER = "assemble-only: root-level artifacts"

OLD = '''        if not p["voice"].exists():
            raise SystemExit(f"Cannot assemble — missing voiceover: {p['voice']}")

        music = None
        if args.music:
            music = Path(args.music).expanduser()
        elif not args.no_music:
            music_path = p["root"] / "music.mp3"
            if music_path.exists():
                music = music_path
            else:
                print("   (no music.mp3 found — assembling without music bed)")

        print("\\nAssembling final video...")
        assemble(clip_paths, p["voice"], p["final"], music_path=music)
        print(f"\\nDONE -> {p['final']}")
        return'''

NEW = '''        # assemble-only: root-level artifacts (voiceover, final, music) live at the
        # PROJECT ROOT, one level above p["root"] when --project is "<slug>/modea"
        # (same as the normal path's project_root = p["root"].parent). Clips stay under modea.
        _asm_root = p["root"].parent
        _voice = _asm_root / "voiceover.mp3"
        _final = _asm_root / "final_video.mp4"
        if not _voice.exists():
            raise SystemExit(f"Cannot assemble — missing voiceover: {_voice}")

        music = None
        if args.music:
            music = Path(args.music).expanduser()
        elif not args.no_music:
            music_path = _asm_root / "music.mp3"
            if music_path.exists():
                music = music_path
            else:
                print("   (no music.mp3 found — assembling without music bed)")

        print("\\nAssembling final video...")
        assemble(clip_paths, _voice, _final, music_path=music)
        print(f"\\nDONE -> {_final}")
        return'''


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

    c = src.count(OLD)
    if c == 0:
        die("assemble-only block anchor NOT FOUND -- file shape changed; nothing written.")
    if c > 1:
        die(f"anchor found {c}x (expected 1) -- ambiguous; nothing written.")

    new = src.replace(OLD, NEW)
    backup = TARGET.with_suffix(TARGET.suffix + ".pre_asmpaths")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    if MARKER not in chk or "_asm_root = p[\"root\"].parent" not in chk:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed -- restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile -- restored.\\n{e}")

    print(f"OK patched {TARGET}  (backup {backup.name})")
    print("   assemble-only now reads voiceover/final/music from the project root.")
    print()
    print("This is a recreation_pipeline.py change (no page change) -- after pull on the box,")
    print("NO restart needed for the file itself, but the Re-assemble button shells out to it,")
    print("so just pull and re-test the button on esther--1:")
    print("   (box) cd ~/Pipeline && git pull --no-edit")
    print("   then in the page: Re-assemble -> should now find the voiceover and rebuild.")
    print("   sanity (box, free): cd ~/Pipeline/scripture-on-screen/projects && \\\\")
    print("     python ~/Pipeline/shared/recreation_pipeline.py finish --project esther--1/modea --assemble-only")


if __name__ == "__main__":
    main()
