#!/usr/bin/env python3
"""
patch_music_loop_codec.py -- fix the assemble music-loop mux crash.

BUG: shared/assemble_episode.py step (2) loops the music sequence into music_bed.m4a
with `-c copy`. When the sequence source is an mp3 (the --music single-file path or the
default <project>/music.mp3), copying mp3 packets into an m4a/ipod container fails:
  "Could not find tag for codec mp3 in stream #0 ... Could not write header"
This halted the assemble leg (die video, 26 Jul).

FIX: re-encode the looped bed to aac instead of stream-copying. Normalizes ANY input
codec (mp3 or m4a) into the m4a container. Costs a few seconds CPU; kills the crash for
every music path.

Idempotent: anchor-verified, .pre_ backup, py_compile before write, ASCII-only.
Run on the BOX from repo root:  python patch_music_loop_codec.py
"""
import py_compile, shutil, sys
from pathlib import Path

TARGET = Path("shared/assemble_episode.py")

OLD = (
    '    run_fn(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(mlist),\n'
    '            "-c", "copy", str(looped)], "loop music bed")\n'
)
NEW = (
    '    run_fn(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(mlist),\n'
    '            "-c:a", "aac", "-b:a", "192k", str(looped)], "loop music bed")\n'
)


def main():
    if not TARGET.exists():
        print("ABORT: %s not found (run from repo root)" % TARGET)
        sys.exit(1)
    src = TARGET.read_text()

    if NEW in src:
        print("Already patched (aac re-encode present). No change.")
        return
    if OLD not in src:
        print("ABORT: anchor not found -- file differs from expected. No change made.")
        print("Expected to find the `-c`, `copy` loop-music-bed call verbatim.")
        sys.exit(1)

    backup = TARGET.with_suffix(".py.pre_music_loop_codec")
    shutil.copy2(TARGET, backup)

    patched = src.replace(OLD, NEW, 1)
    tmp = TARGET.with_suffix(".py.tmp_patch")
    tmp.write_text(patched)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        print("ABORT: patched file fails py_compile, not written:\n%s" % e)
        tmp.unlink(missing_ok=True)
        sys.exit(1)

    tmp.replace(TARGET)
    print("Patched %s  (loop music bed now re-encodes to aac)" % TARGET)
    print("Backup: %s" % backup)


if __name__ == "__main__":
    main()
