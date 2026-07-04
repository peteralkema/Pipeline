#!/usr/bin/env python3
"""
patch_kenburns_flag_fix.py — make the per-channel ken_burns flag actually take,
replacing the 01 Jul hardcode in ken_burns_still().

THE BUG CHAIN: the flag was read via a CWD walk-up cached inside finish, which
did not take at render time -> 01 Jul hardcoded _z = "1" (true static) into the
SHARED function -> every KB floor clip portfolio-wide became a held frame
(QQrew's channel doctrine silently became engine law — build-order bias).

THE FIX: resolve the flag from the STILL's own path — the artifact always
lives under its channel, so walking still_path.parents to the first
channel.json is deterministic regardless of CWD, per-call, uncached (one tiny
JSON read per clip; negligible next to the encode).

  - channel.json "ken_burns": false  -> true-static held frame (QQrew keeps its floor)
  - absent / true (synthetic etc.)   -> cinematic slow zoom-in, capped
    (z = min(zoom+0.0008, 1.10) — the banked capped-creep craft)

ONE anchored edit in shared/recreation_pipeline.py: the comment block +
hardcode + branch condition. Both vf branches below it are untouched.

SAFETY: anchor verified exactly once, in-memory patch, py_compile to temp
BEFORE writing, backup to .pre_kbflagfix. Idempotent.

Run from the repo root:  python3 shared/patch_kenburns_flag_fix.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "recreation_pipeline.py"
BACKUP = TARGET.with_suffix(".py.pre_kbflagfix")

MARKER = "_kb_zoom"

EDITS = [
    (
        '''    # Per-channel ken_burns flag (banked 01 Jul): true-static channels (QQrew)
    # set "ken_burns": false -> zoompan z=1 (constant, no zoom) = a motionless
    # held frame, same clips/shot_NNN.mp4 artifact, assembly unchanged. Reads the
    # same way _channel_aspect does (walks up from CWD, cached). Defaults True so
    # every cinematic channel keeps the slow zoom-in.
    # HARDCODED static (01 Jul): the ken_burns config flag did not take at render
    # time (load_channel_config cached inside finish), frame-diff proved clips
    # still zoomed. z=1 unconditionally removes the zoom. Revert via .bak if a
    # cinematic channel needs the slow zoom-in restored.
    _z = "1"
    if _z == "1":''',

        '''    # Per-channel ken_burns flag (FIXED 04 Jul): resolved from the STILL's own
    # path. The 01 Jul hardcode existed because the CWD-walk-up + cached config
    # read did not take at render time; walking the artifact's parents to the
    # first channel.json is deterministic regardless of CWD, per-call, uncached
    # (one tiny JSON read per clip — negligible next to the encode).
    # "ken_burns": false -> true-static held frame (QQrew keeps its floor);
    # absent/true -> cinematic slow zoom-in, capped (banked craft).
    _kb_zoom = True
    try:
        import json as _json
        for _p in Path(still_path).resolve().parents:
            _cj = _p / "channel.json"
            if _cj.is_file():
                _kb_zoom = bool(_json.loads(_cj.read_text()).get("ken_burns", True))
                break
    except Exception:
        _kb_zoom = True
    _z = "min(zoom+0.0008,1.10)"  # slow zoom-in, capped — same craft as the assembler's kb-tail
    if not _kb_zoom:''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (_kb_zoom present) — no-op.")
        return

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
    print("  ken_burns flag resolved from the still's path (CWD-independent, uncached)")
    print("  QQrew (ken_burns:false) -> true-static floor unchanged")
    print("  synthetic (no key, default True) -> real slow zoom-in, capped at 1.10")


if __name__ == "__main__":
    main()
