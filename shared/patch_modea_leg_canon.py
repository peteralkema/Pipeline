#!/usr/bin/env python3
"""
patch_modea_leg_canon.py — make the Mode A leg pass the channel config to the translator.

Companion to patch_modea_beats_canon.py, which taught modea_beats.py to emit a canon
block when given --channel-config. This patch makes the leg actually supply it.

Without this, the flag exists but is never used on the MC route, and a reference-mode
channel's {tokens} hard-fail at _expand_canon.

The flag is only added when the channel dir is known and its channel.json exists, so the
change is a no-op for any channel or context lacking one. Every existing channel's
translate step is unaffected: modea_beats.py without a canon block emits exactly what it
emits today.

Discipline: verifies its anchor, py_compiles the result before writing, keeps a .pre_*
backup, idempotent. Requires patch_modea_beats_canon.py to have run first.

Run on the BOX from ~/Pipeline (after git pull):
    python shared/patch_modea_leg_canon.py --dry-run
    python shared/patch_modea_leg_canon.py
"""

from __future__ import annotations

import argparse
import py_compile
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

TARGET = Path("shared/modea_leg.py")
MARKER = "# [canon] hand the translator the channel config"

ANCHOR = '''    cmd = [py, str(Path(ctx["shared"]) / "modea_beats.py"), ctx["beats_list_json"],
           "--out", engine_beats, "--map", index_json]'''

NEW = '''    cmd = [py, str(Path(ctx["shared"]) / "modea_beats.py"), ctx["beats_list_json"],
           "--out", engine_beats, "--map", index_json]
    # [canon] hand the translator the channel config
    # A reference-mode channel's VISUAL lines carry {tokens} that must expand via the
    # channel's canon block; modea_beats.py emits it when handed the config. No config
    # (or no canon in it) -> identical output to before, for every other channel.
    _chcfg = Path(ctx.get("channel_dir") or ".") / "channel.json"
    if _chcfg.is_file():
        cmd += ["--channel-config", str(_chcfg)]'''


def fail(msg: str) -> int:
    print(f"!! {msg}", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--target", default=str(TARGET))
    args = ap.parse_args()

    target = Path(args.target)
    if not target.is_file():
        return fail(f"{target} not found. Run from ~/Pipeline (repo root).")

    src = target.read_text(encoding="utf-8")

    if MARKER in src:
        print(f"OK  already applied (marker present in {target}); nothing to do.")
        return 0

    if "--channel-config" not in Path("shared/modea_beats.py").read_text(encoding="utf-8"):
        return fail("prerequisite missing: run patch_modea_beats_canon.py first "
                    "(modea_beats.py does not accept --channel-config yet). Nothing written.")

    if ANCHOR not in src:
        return fail("modea_beats.py cmd anchor not found in modea_leg.py — it has moved. "
                    "Re-read it and update this patch. Nothing was written.")
    print("anchors verified: modea_beats cmd construction")

    out = src.replace(ANCHOR, NEW, 1)
    if out == src:
        return fail("no change produced — refusing to write.")

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(out)
        tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        tmp.unlink(missing_ok=True)
        return fail(f"patched source does not compile; nothing written.\n{e}")
    tmp.unlink(missing_ok=True)
    print("py_compile OK on the patched source")

    if args.dry_run:
        print("\n--dry-run: anchors verified, result compiles, nothing written.")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = target.with_name(f".pre_canon_{stamp}_{target.name}")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")

    print(f"backup -> {backup}")
    print(f"PATCHED -> {target}")
    print("\nVERIFY:")
    print("  grep -n 'channel-config\\|canon' shared/modea_leg.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
