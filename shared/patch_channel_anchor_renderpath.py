#!/usr/bin/env python3
"""
patch_channel_anchor_renderpath.py

Anchors the THREE render-path load_channel_config(strict=False) calls that must
resolve the real channel, leaving the legitimately context-free calls alone.

Root cause (canonical 2B code-leak, made literal): load_channel_config() walks
up from CWD when anchor=None. Run from ~/Pipeline (cwd above the channel
folder), the render-path calls find no channel.json and silently return
CHANNEL_DEFAULTS -- the Final Hours photoreal style_suffix + empty base_canon.
That rendered QQrew's Skeptic photoreal and dropped her lean base_canon.

THREE sites anchored (strict=True so a future miss crashes, never silent FH):
  535  generate_still(out_path)        -> anchor=out_path   (style_suffix leak)
  1204 _load_beats_with_canon(beats_path) -> anchor=beats_path (base_canon merge)
  1259 cmd_stills(args)                -> anchor=Path(args.project) (default_motion)

LEFT ALONE (correct as-is): 349 load_rulebook + 380 _active_rulebook_path
(deliberately resolve channel-vs-shared rulebook; outside-a-channel is the
intended path), 226 _channel_aspect (module load, no path), 670 _synthesize_chunk
(already anchored), 761 generate_music (separate audio-leg pass).

Each edit matches on UNIQUE surrounding context (the repeated bare line text is
never used as the anchor). Idempotent via per-edit sentinel. Backs up to
.pre_renderpath. ASCII-only. py_compile-gated with auto-revert.
"""
import sys, shutil, py_compile
from pathlib import Path

TARGET = Path("shared/recreation_pipeline.py")

EDITS = [
    {
        "name": "generate_still",
        "old": (
            "def generate_still(image_prompt: str, out_path: Path) -> Path:\n"
            "    rb = load_rulebook()\n"
            "    config = load_channel_config(strict=False)\n"
        ),
        "new": (
            "def generate_still(image_prompt: str, out_path: Path) -> Path:\n"
            "    rb = load_rulebook()\n"
            "    config = load_channel_config(strict=True, anchor=out_path)\n"
        ),
    },
    {
        "name": "_load_beats_with_canon",
        "old": (
            "    # Layer channel base_canon underneath beat-script canon (beat-script wins on key collision).\n"
            "    channel_config = load_channel_config(strict=False)\n"
        ),
        "new": (
            "    # Layer channel base_canon underneath beat-script canon (beat-script wins on key collision).\n"
            "    channel_config = load_channel_config(strict=True, anchor=beats_path)\n"
        ),
    },
    {
        "name": "cmd_stills_default_motion",
        "old": (
            "    _default_motion = (load_channel_config(strict=False).get(\"default_motion\")\n"
        ),
        "new": (
            "    _default_motion = (load_channel_config(strict=True, anchor=Path(args.project)).get(\"default_motion\")\n"
        ),
    },
]


def main():
    if not TARGET.exists():
        sys.exit("ERROR: run from repo root (shared/recreation_pipeline.py not found).")

    src = TARGET.read_text()

    # Idempotency: if all three new lines are already present, no-op.
    if all(e["new"].strip().splitlines()[-1] in src for e in EDITS):
        print("Already patched (all three render-path anchors present). No-op.")
        return

    # Verify every old block matches exactly once BEFORE writing anything.
    for e in EDITS:
        if e["new"] in src:
            continue  # this one already done; skip in the apply loop too
        c = src.count(e["old"])
        if c != 1:
            sys.exit(f"ERROR: [{e['name']}] context block found {c} times, expected 1. "
                     "Aborting (no write) -- file shape changed, inspect manually.")

    backup = TARGET.with_suffix(".py.pre_renderpath")
    shutil.copy2(TARGET, backup)
    print(f"Backup: {backup}")

    applied = []
    for e in EDITS:
        if e["new"] in src:
            print(f"  [{e['name']}] already present, skipping")
            continue
        src = src.replace(e["old"], e["new"], 1)
        applied.append(e["name"])

    TARGET.write_text(src)

    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as ex:
        shutil.copy2(backup, TARGET)
        sys.exit(f"ERROR: py_compile failed, reverted from backup.\n{ex}")

    print("Anchored:", ", ".join(applied) if applied else "(none)")
    print("py_compile OK.")


if __name__ == "__main__":
    main()
