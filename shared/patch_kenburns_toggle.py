#!/usr/bin/env python3
"""
patch_kenburns_toggle.py — per-beat Ken-Burns override in the tiered render.

WHAT: render_policy.json gains an optional "kb_override": [beat_index, ...].
A beat listed there renders on the free Ken-Burns floor even when it sits
inside the Kling front-N. The freed slot is SAVED (spend deleted), not slid
to the next beat. The assembler is untouched — a KB clip is duration-exact
and rides the existing trim path.

WHERE: shared/recreation_pipeline.py
  1. new helper _kb_override_set() after _tiered_kling_count()
  2. cmd_finish routing: engine = kling only if bi < N AND bi not overridden
  3. TIERED RENDER banner prints how many front-N beats were flipped
  4. --plan listing marks each overridden beat

SAFETY: verifies every anchor appears exactly once, applies edits in memory,
py_compiles the result to a temp file BEFORE touching the target, backs up
the original to .pre_kbtoggle. Idempotent — re-running is a no-op.

Run from the repo root:  python3 shared/patch_kenburns_toggle.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "recreation_pipeline.py"
BACKUP = TARGET.with_suffix(".py.pre_kbtoggle")

MARKER = "_kb_override_set"  # presence anywhere in target == already applied

HELPER = '''def _kb_override_set(project_root):
    """Per-beat Ken-Burns overrides: render_policy.json {"kb_override": [beat,...]}.
    A beat listed here renders on the free Ken-Burns floor even inside the
    Kling front-N (per-beat craft control from the MC review page). The freed
    Kling slot is SAVED, not slid to the next beat. Empty set when absent."""
    import json as _json
    rp = project_root / "render_policy.json"
    if rp.is_file():
        try:
            return {int(x) for x in _json.loads(rp.read_text()).get("kb_override", [])}
        except Exception:
            return set()
    return set()


'''

EDITS = [
    # 1. insert helper between _tiered_kling_count and _tiered_beat_index
    (
        "    return 40\n"
        "\n"
        "\n"
        "def _tiered_beat_index(engine_shot, project_root):",

        "    return 40\n"
        "\n"
        "\n"
        + HELPER +
        "def _tiered_beat_index(engine_shot, project_root):",
    ),
    # 2. routing: consult the override set
    (
        '    kling_count = _tiered_kling_count(project_root, getattr(args, "kling_count", None))\n'
        "    plan = []\n"
        "    for s in shots:\n"
        '        bi = _tiered_beat_index(s["index"], project_root)\n'
        '        engine = "kling" if bi < kling_count else "kenburns"\n'
        "        plan.append((s, bi, engine))",

        '    kling_count = _tiered_kling_count(project_root, getattr(args, "kling_count", None))\n'
        "    kb_over = _kb_override_set(project_root)\n"
        "    plan = []\n"
        "    for s in shots:\n"
        '        bi = _tiered_beat_index(s["index"], project_root)\n'
        '        engine = "kling" if (bi < kling_count and bi not in kb_over) else "kenburns"\n'
        "        plan.append((s, bi, engine))",
    ),
    # 3. banner: surface applied overrides (only those that actually flip a front-N beat)
    (
        '    print(f"TIERED RENDER: N={kling_count}  ->  {n_kling} Kling (~${n_kling * _clip_cost:.2f}) "\n'
        '          f"+ {n_kb} Ken Burns (free)")',

        '    print(f"TIERED RENDER: N={kling_count}  ->  {n_kling} Kling (~${n_kling * _clip_cost:.2f}) "\n'
        '          f"+ {n_kb} Ken Burns (free)")\n'
        "    _kb_applied = sorted(b for b in kb_over if b < kling_count)\n"
        "    if _kb_applied:\n"
        '        print(f"  kb-override: {len(_kb_applied)} front-N beat(s) flipped to Ken Burns "\n'
        '              f"(slot saved, not slid): {_kb_applied}")',
    ),
    # 4. --plan listing: mark overridden beats
    (
        '            print(f"  shot {s[\'index\']:03d}  beat {bi:>3}  {durtxt:>7}  -> {engine}")',

        '            _mark = "  (kb-override)" if (bi in kb_over and bi < kling_count) else ""\n'
        '            print(f"  shot {s[\'index\']:03d}  beat {bi:>3}  {durtxt:>7}  -> {engine}{_mark}")',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (kb_override present) — no-op.")
        return

    # verify every anchor exactly once BEFORE any write
    for i, (old, _new) in enumerate(EDITS, 1):
        n = src.count(old)
        if n != 1:
            sys.exit(f"!! anchor {i} matched {n} times (need exactly 1) — file drifted, NOT patched.\n"
                     f"   anchor starts: {old.splitlines()[0]!r}")

    patched = src
    for old, new in EDITS:
        patched = patched.replace(old, new)

    # py_compile the patched text in a temp file before touching the target
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
    print("  1. helper _kb_override_set() added")
    print("  2. cmd_finish routing consults kb_override (slot saved, not slid)")
    print("  3. TIERED RENDER banner reports applied overrides")
    print("  4. --plan listing marks overridden beats")


if __name__ == "__main__":
    main()
