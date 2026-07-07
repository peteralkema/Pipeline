#!/usr/bin/env python3
"""
patch_paint_floored_kb.py — KB buttons paint ON from the .kbfloor artifact (v3.9.4).

BUG: the storyboard paints a beat's KB button "ON" only if the beat is in
render_policy.json kb_override. On a floor-first project beats are Ken-Burns by
DEFAULT (kling_count:0) and in NO list, so every KB button reads "off" though
every beat rendered a floor. Fix: /api/render_policy also reports `floored`
(beats whose shot_NNN.kbfloor marker exists on disk); the paint loop ORs
`floored` into the KB-on set. Truthful to the artifact; an upgraded-to-Kling beat
(marker deleted) correctly shows off.

Idempotent (sentinel PAINT_FLOORED_KB_APPLIED). Two anchors, each verified once;
py_compile before write; backup .pre_paintflooredkb. Pure ASCII. Bumps APP_VERSION.
"""
import sys, py_compile, tempfile, shutil
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_paintflooredkb")
SENTINEL = "PAINT_FLOORED_KB_APPLIED"

S_ANCHOR = '''        self._json(200, {"ok": True, "kling_count": n, "static": static,
                         "kb_override": kb, "inherit_prev": inh, "default": 40}); return'''

S_NEW = '''        # PAINT_FLOORED_KB_APPLIED: beats whose free .kbfloor clip exists on disk
        # (rendered Ken-Burns floor). Map shot_NNN.kbfloor back to beat via _index.json
        # (shot->beat); default identity (beat = shot-1) if no map.
        floored = []
        try:
            _clips = paths["project"] / "modea" / "clips"
            _idx = paths["project"] / "_index.json"
            _s2b = {}
            if _idx.is_file():
                for _k, _v in (_json.loads(_idx.read_text()) or {}).items():
                    _s2b[int(_k)] = int(_v)
            if _clips.is_dir():
                for _m in _clips.glob("shot_*.kbfloor"):
                    try:
                        _sh = int(_m.stem.split("_")[1])
                    except Exception:
                        continue
                    floored.append(_s2b.get(_sh, _sh - 1))
            floored = sorted(set(floored))
        except Exception:
            floored = []
        self._json(200, {"ok": True, "kling_count": n, "static": static,
                         "kb_override": kb, "inherit_prev": inh, "floored": floored,
                         "default": 40}); return'''

# Client: single-line anchor (6-space indent, verbatim from the file). Insert the
# `floored` forEach on the line immediately after kb_override.
C_ANCHOR = '''      ((r && r.kb_override) || []).forEach(function(b) { kbOn[b] = 1; });'''

C_NEW = '''      ((r && r.kb_override) || []).forEach(function(b) { kbOn[b] = 1; });
      ((r && r.floored) || []).forEach(function(b) { kbOn[b] = 1; });  // PAINT_FLOORED_KB_APPLIED'''


def die(m):
    print(f"FAIL: {m}  Nothing written.", file=sys.stderr); sys.exit(1)


def main():
    if not TARGET.is_file():
        die(f"target not found: {TARGET}")
    src = TARGET.read_text()
    if SENTINEL in src:
        print("Already applied (sentinel present). No-op."); return
    for label, anchor in (("server", S_ANCHOR), ("client", C_ANCHOR)):
        c = src.count(anchor)
        if c != 1:
            die(f"anchor {label} matched {c} times (need 1) — file drifted.")
    new = src.replace(S_ANCHOR, S_NEW, 1).replace(C_ANCHOR, C_NEW, 1)
    new = new.replace('APP_VERSION = "v3.9.3"', 'APP_VERSION = "v3.9.4"', 1)
    for need in (SENTINEL, '"floored": floored', "r.floored", 'APP_VERSION = "v3.9.4"'):
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
    print(f"OK — patched {TARGET.name}  (KB buttons paint ON from .kbfloor; v3.9.4)")
    print(f"     backup: {BACKUP.name}")


if __name__ == "__main__":
    main()
