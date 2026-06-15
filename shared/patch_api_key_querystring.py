#!/usr/bin/env python3
"""
patch_api_key_querystring.py -- api() must send the key even when the path has params (v1.4).

WHY (root cause of the FINAL VIDEO panel not showing on select)
  api() built its fetch URL as:
      path + (path.includes("?") ? "" : ("?key=" + KEY))
  i.e. it appended "?key=" ONLY when the path had no existing "?", and appended NOTHING
  when the path already had query params. So every keyed GET that carries params
  (/api/meta?channel=..., /api/render_policy?channel=..., /api/assemble_status?channel=...)
  was sent with NO key -> server returns "403 - bad key" -> the JSON parse fails / the call
  bails. renderDonePanel's /api/meta call was 403ing, so the panel fell to the placeholder
  every time. (The header X-Review-Key only rides along when opts carries H, which these
  bare api(path) calls don't pass.)

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  Rewrite the URL build so the key is ALWAYS appended, with the right separator:
      path + (path.includes("?") ? "&" : "?") + "key=" + KEY     (when KEY is set)
  Unkeyed (local, no KEY) behaves as before (appends nothing).
  APP_VERSION -> v1.4.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `key always appended`). Anchor verified once;
  .pre_apikey backup; py_compile + JS brace/paren note; rollback on failure. Requires v1.3.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "key always appended"

OLD = '''  const r = await fetch(path + (path.includes("?")?"":("?key="+KEY)), opts);'''
NEW = '''  const _kq = KEY ? ((path.includes("?")?"&":"?") + "key=" + KEY) : "";  // key always appended (right separator)
  const r = await fetch(path + _kq, opts);'''

OLD_VER = '''APP_VERSION = "v1.3"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
NEW_VER = '''APP_VERSION = "v1.4"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


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
        die("APP_VERSION v1.3 anchor not found -- apply patch_panel_on_select.py (v1.3) first. Nothing written.")

    for label, old in [("api() fetch line", OLD), ("version", OLD_VER)]:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND -- file shape changed; nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) -- ambiguous; nothing written.")

    new = src.replace(OLD, NEW).replace(OLD_VER, NEW_VER)

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_apikey")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    if MARKER not in chk or 'APP_VERSION = "v1.4"' not in chk or "const _kq = KEY" not in chk:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed -- restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile -- restored.\n{e}")

    print(f"OK patched {TARGET}  (backup {backup.name})")
    print("   api() now always sends the key (& when the path has params, ? otherwise).")
    print("   fixes /api/meta + /api/render_policy + /api/assemble_status 403s.")
    print()
    print("AFTER pull on the box:")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   verify v1.4 + node-check PAGE_JS_VALID, hard-refresh, then:")
    print("   Reset -> pick esther--1 -> the FINAL VIDEO panel should now appear.")


if __name__ == "__main__":
    main()
