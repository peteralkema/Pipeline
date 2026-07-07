#!/usr/bin/env python3
"""
patch_perbeat_kling_override.py — per-beat render must honor kling_override (v3.9.3).

BUG: _handle_animate routes a single beat by POSITION only:
    engine = "kling" if beat_index < kling_count else "kenburns"
Under floor-first (kling_count:0) this ALWAYS yields "kenburns", so clicking a
motion preset on a floored beat re-renders Ken-Burns again — the override list is
never consulted. The batch cmd_finish got additive routing on 06 Jul; this per-beat
handler did not. Fix: same additive rule as the engine —
    kling if (beat in kling_override) or (beat < kling_count and beat not in kb_override).

Idempotent (sentinel PERBEAT_KLING_OVERRIDE_APPLIED). One anchor, verified once;
py_compile before write; backup .pre_perbeatklingoverride. Pure ASCII. Bumps APP_VERSION.
"""
import sys, py_compile, tempfile, shutil
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_perbeatklingoverride")
SENTINEL = "PERBEAT_KLING_OVERRIDE_APPLIED"

ANCHOR = '''        kling_count = _tiered_kling_count(project_root)
        beat_index = _tiered_beat_index(shot_idx, project_root)
        engine = "kling" if beat_index < kling_count else "kenburns"'''

NEW = '''        kling_count = _tiered_kling_count(project_root)
        beat_index = _tiered_beat_index(shot_idx, project_root)
        # PERBEAT_KLING_OVERRIDE_APPLIED: additive routing, same rule as the batch
        # engine (cmd_finish). Under floor-first (kling_count:0) a beat renders Kling
        # ONLY if it is in kling_override; positional N still applies when >0.
        import json as _j
        _rp = project_root / "render_policy.json"
        _klo, _kbo = set(), set()
        if _rp.is_file():
            try:
                _pol = _j.loads(_rp.read_text()) or {}
                _klo = {int(x) for x in _pol.get("kling_override", [])}
                _kbo = {int(x) for x in _pol.get("kb_override", [])}
            except Exception:
                _klo, _kbo = set(), set()
        engine = "kling" if (beat_index in _klo) or (beat_index < kling_count and beat_index not in _kbo) else "kenburns"'''


def die(m):
    print(f"FAIL: {m}  Nothing written.", file=sys.stderr); sys.exit(1)


def main():
    if not TARGET.is_file():
        die(f"target not found: {TARGET}")
    src = TARGET.read_text()
    if SENTINEL in src:
        print("Already applied (sentinel present). No-op."); return
    n = src.count(ANCHOR)
    if n != 1:
        die(f"anchor matched {n} times (need 1) — file drifted.")
    new = src.replace(ANCHOR, NEW, 1)
    new = new.replace('APP_VERSION = "v3.9.2"', 'APP_VERSION = "v3.9.3"', 1)
    for need in (SENTINEL, "kling_override", 'APP_VERSION = "v3.9.3"'):
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
    print(f"OK — patched {TARGET.name}  (per-beat render honors kling_override; v3.9.3)")
    print(f"     backup: {BACKUP.name}")


if __name__ == "__main__":
    main()
