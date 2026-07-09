#!/usr/bin/env python3
"""
patch_mc_ingest_wordless.py — teach Mission Control's ingest gate that silence can be legal.

THE INVARIANT, FOR THE FOURTH TIME
----------------------------------
"A beat with no narration is an authoring error" is encoded independently in four places:

  1. build_audio_script.py   — the continuous-narration doctrine (bypassed: wordless leg)
  2. elevenlabs_tts.py       — the 1.0s concat floor      (parameterized: min_total_duration)
  3. assemble_episode.py     — drops source=no_narration  (satisfied: source="beatsheet")
  4. mission_control/ingest.py — verify_beats() REFUSES   <- THIS PATCH

Each is correct for the voice-led channels it was written for. Each defers, correctly, to
a channel that declares `timing_source: "beatsheet"`. Wordless is a first-class channel
mode, not a special case; every no-silence invariant should ask the channel first.

THE FIX
-------
verify_beats() gains an optional channel_dir. If that channel's channel.json declares
timing_source == "beatsheet", wordless beats stop contributing to `ok` — they remain in
the returned dict so MC still DISPLAYS them, because on a wordless film the silent-beat
inventory is craft information, not noise.

`no_visual` stays a hard error for every channel: a Mode A beat with no VISUAL is a real
authoring bug regardless of doctrine.

Called without the new argument, behaviour is byte-identical to today. Every existing
channel refuses on wordless beats exactly as it does now.

Discipline: verifies its anchors, py_compiles the result before writing, keeps a .pre_*
backup, idempotent.

Run on the BOX from ~/Pipeline (after git pull):
    python shared/mission_control/patch_mc_ingest_wordless.py --dry-run
    python shared/mission_control/patch_mc_ingest_wordless.py

Then restart Mission Control — and confirm the Main PID actually changed:
    systemctl --user restart mission-control.service
    systemctl --user show -p MainPID mission-control.service
"""

from __future__ import annotations

import argparse
import py_compile
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

TARGET = Path("shared/mission_control/ingest.py")
MARKER = "# [wordless] silence is legal when the channel declares timing_source=beatsheet"

# ── 1. verify_beats gains an optional channel_dir and consults it ─────────
ANCHOR_VERIFY = '''def verify_beats(beats_path: Path) -> dict:
    """Return {ok, beats, modes, wordless, no_visual}. ok=False on hard errors."""
    b = json.loads(beats_path.read_text())
    wordless = [x["index"] for x in b if not (x.get("narration") or "").strip()]
    no_visual = [x["index"] for x in b
                 if x.get("mode") == "A" and not (x.get("visual") or "").strip()]
    modes = {}
    for x in b:
        modes[x.get("mode")] = modes.get(x.get("mode"), 0) + 1
    return {
        "ok": not wordless and not no_visual,
        "beats": len(b),
        "modes": modes,
        "wordless": wordless,
        "no_visual": no_visual,
    }'''

NEW_VERIFY = '''def _wordless_is_legal(channel_dir) -> bool:
    """# [wordless] silence is legal when the channel declares timing_source=beatsheet

    A wordless-spine channel (picture + score carry the story; VO is a sparse, removable
    layer) has silent beats BY DESIGN. Its timing is declared in the beat-sheet, not
    measured from narration, so it never enters build_audio_script's continuous-narration
    doctrine. Absent that declaration, a wordless beat remains an authoring error.
    """
    if not channel_dir:
        return False
    try:
        cfg_path = Path(channel_dir) / "channel.json"
        if not cfg_path.is_file():
            return False
        return json.loads(cfg_path.read_text(encoding="utf-8")).get("timing_source") == "beatsheet"
    except Exception:
        return False   # unreadable config -> strict. Never relax a gate on an error.


def verify_beats(beats_path: Path, channel_dir=None) -> dict:
    """Return {ok, beats, modes, wordless, no_visual, wordless_ok}. ok=False on hard errors.

    wordless beats are a hard error EXCEPT on a timing_source=beatsheet channel, where
    they are legal and merely reported (the silent-beat inventory is craft information).
    A Mode A beat with no VISUAL is a hard error on every channel.
    """
    b = json.loads(beats_path.read_text())
    wordless = [x["index"] for x in b if not (x.get("narration") or "").strip()]
    no_visual = [x["index"] for x in b
                 if x.get("mode") == "A" and not (x.get("visual") or "").strip()]
    modes = {}
    for x in b:
        modes[x.get("mode")] = modes.get(x.get("mode"), 0) + 1
    wordless_ok = _wordless_is_legal(channel_dir)
    return {
        "ok": (wordless_ok or not wordless) and not no_visual,
        "beats": len(b),
        "modes": modes,
        "wordless": wordless,
        "wordless_ok": wordless_ok,
        "no_visual": no_visual,
    }'''

# ── 2. the call site — hand it the already-resolved channel folder ────────
ANCHOR_CALL = '''    # 4. verify — REFUSE on hard errors (wordless / missing VISUAL)
    v = verify_beats(beats)'''

NEW_CALL = '''    # 4. verify — REFUSE on hard errors (missing VISUAL always; wordless unless the
    #    channel declares timing_source=beatsheet, where silence is by design)
    v = verify_beats(beats, channel_dir=folder)'''


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

    problems = []
    if ANCHOR_VERIFY not in src:
        problems.append("verify_beats function body anchor not found")
    if ANCHOR_CALL not in src:
        problems.append("verify_beats call-site anchor not found")
    if problems:
        for p in problems:
            print(f"!! {p}", file=sys.stderr)
        return fail("anchors did not verify — ingest.py has moved. "
                    "Re-read it and update this patch. Nothing was written.")
    print("anchors verified: verify_beats body, call site")

    out = src.replace(ANCHOR_VERIFY, NEW_VERIFY, 1)
    out = out.replace(ANCHOR_CALL, NEW_CALL, 1)

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
    backup = target.with_name(f".pre_wordless_{stamp}_{target.name}")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")

    print(f"backup -> {backup}")
    print(f"PATCHED -> {target}")
    print("\nVERIFY:")
    print("  grep -n 'wordless_ok\\|_wordless_is_legal\\|channel_dir=folder' shared/mission_control/ingest.py")
    print("\nRESTART Mission Control — and confirm the PID actually changed "
          "(a restart may not swap the process):")
    print("  systemctl --user show -p MainPID mission-control.service")
    print("  systemctl --user restart mission-control.service")
    print("  systemctl --user show -p MainPID mission-control.service")
    print("\nNEVER restart mid-render. If an orphan holds the port: stop, "
          "pkill -f pipeline_server.py, start.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
