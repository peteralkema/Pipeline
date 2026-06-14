#!/usr/bin/env python3
"""
patch_version_stamp.py — visible version in the Mission Control heading (v0.5).

WHY
  Today's status-line loop was lost to a stale browser tab (server had new code,
  tab ran old JS). A visible version makes "is my tab current?" a one-glance check:
  the SHA in the heading must equal `git rev-parse --short HEAD` on the box.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  1. APP_VERSION = "v0.5" — hand-bumped each shipped page change (readable tag).
  2. _build_sha() — `git rev-parse --short HEAD` at request time (auto, can't lie).
  3. render_page: the page is a PLAIN triple-quoted string with CSS braces, so we do
     NOT f-string it — we .replace() the literal <h1> text with the stamped heading,
     interpolating APP_VERSION + the live SHA at render time.
  4. /api/state (build_state, both idle + active returns): adds "version" and "sha".

DISCIPLINE
  Idempotent (sentinel: `APP_VERSION =`). Four anchors verified once; backs up to
  .pre_version; re-compiles + rolls back on failure. Confirmed against real code:
  one line; build_state has one idle dict + one active dict.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "APP_VERSION ="

# 1. constant + sha helper, just above build_state
OLD_DEF = "def build_state() -> dict:"
NEW_DEF = '''APP_VERSION = "v0.5"  # hand-bumped each shipped page change; pairs with the auto git SHA


def _build_sha() -> str:
    """Short SHA of the deployed commit — the half of the version that can't lie."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(_REPO), capture_output=True, text=True, timeout=3,
        )
        return out.stdout.strip() or "?"
    except Exception:
        return "?"


def build_state() -> dict:'''

# 2a. idle return — add version + sha
OLD_IDLE = '''    if not jid:
        return {"phase": "idle", "job_id": None,
                "channels": list_channels()}'''
NEW_IDLE = '''    if not jid:
        return {"phase": "idle", "job_id": None,
                "channels": list_channels(),
                "version": APP_VERSION, "sha": _build_sha()}'''

# 2b. active state dict — add version + sha
OLD_ACTIVE = '''    state = {
        "phase": phase,
        "job_id": jid,
        "channel": rec.get("channel"),
        "project": rec.get("project"),
        "gate": rec.get("gate"),
        "channels": list_channels(),
    }'''
NEW_ACTIVE = '''    state = {
        "phase": phase,
        "job_id": jid,
        "channel": rec.get("channel"),
        "project": rec.get("project"),
        "gate": rec.get("gate"),
        "channels": list_channels(),
        "version": APP_VERSION,
        "sha": _build_sha(),
    }'''

# 3. render_page: build the page, then .replace the heading with the stamped one.
#    Anchor on the existing `return """<!doctype...` opener so we can inject the
#    page-into-variable + replace without touching the (brace-laden) CSS body.
OLD_RP = '''    # Minimal Phase-2a page: dropdowns, Launch, phase line, bare audio gate.
    # Intentionally small — rich panels are 2b/3. State-driven: everything
    # renders from /api/state, nothing stored client-side.
    return """<!doctype html><html><head><meta charset="utf-8">'''
NEW_RP = '''    # Minimal Phase-2a page: dropdowns, Launch, phase line, bare audio gate.
    # Intentionally small — rich panels are 2b/3. State-driven: everything
    # renders from /api/state, nothing stored client-side.
    _verstamp = f"{APP_VERSION} \\u00b7 {_build_sha()}"  # e.g. v0.5 \\u00b7 2723e25
    _page = """<!doctype html><html><head><meta charset="utf-8">'''

# close: the page string ends with `</html>` then the function returns it. We turn
# the trailing literal into an assignment-then-return that stamps the heading.
OLD_RP_TAIL = '''<h1>AI FILM DIRECTOR STORYBOARD AND CONTROL PANEL</h1>'''
NEW_RP_TAIL = '''<h1>AI FILM DIRECTOR STORYBOARD AND CONTROL PANEL <span style="font-size:12px;font-weight:400;color:#8a8a99;letter-spacing:0;">@@VERSTAMP@@</span></h1>'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found — run from the repo root on the laptop.")
    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) — no changes made.")
        return

    edits = [
        ("build_state def", OLD_DEF, NEW_DEF),
        ("idle return", OLD_IDLE, NEW_IDLE),
        ("active state dict", OLD_ACTIVE, NEW_ACTIVE),
        ("render_page open", OLD_RP, NEW_RP),
        ("heading", OLD_RP_TAIL, NEW_RP_TAIL),
    ]
    for label, old, _ in edits:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) — ambiguous; nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)

    # We renamed the returned literal to `_page = """..."""`. Now find the matching
    # close of render_page's string + its (now-absent) return. The original ended the
    # function with the big string as the return value; since we changed `return """`
    # to `_page = """`, we must add the actual return AFTER the string closes.
    # The string closes with `</html>"""` (the only `</html>"""` in the file).
    close_token = '</html>"""'
    if new.count(close_token) != 1:
        die(f"page-close token `{close_token}` found {new.count(close_token)}x (expected 1) — nothing written.")
    new = new.replace(
        close_token,
        '</html>"""\n    return _page.replace("@@VERSTAMP@@", _verstamp)'
    )

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_version")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    problems = []
    if MARKER not in chk:
        problems.append("APP_VERSION missing")
    if "@@VERSTAMP@@" not in chk:
        problems.append("verstamp placeholder missing")
    if "_page.replace(\"@@VERSTAMP@@\", _verstamp)" not in chk:
        problems.append("return-time swap missing")
    if '"version": APP_VERSION' not in chk:
        problems.append("state version missing")
    if problems:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed (" + "; ".join(problems) + ") — restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile — restored.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   heading now shows: v0.5 · <sha>   ·   /api/state returns version + sha")
    print()
    print("AFTER you pull on the box, restart + node-check, then verify the stamp:")
    print("   systemctl --user restart mission-control.service")
    print("   curl -s \"http://127.0.0.1:8002/api/state?key=fh2026\" | python3 -c \"import sys,json;d=json.load(sys.stdin);print(d.get('version'),d.get('sha'))\"")
    print("   git rev-parse --short HEAD   # must match the sha above")
    print("   # then node-check the page JS:")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")


if __name__ == "__main__":
    main()
