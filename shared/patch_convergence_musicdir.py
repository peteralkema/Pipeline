#!/usr/bin/env python3
"""
patch_convergence_musicdir.py — wire convergence_leg.py to drive the new
--music-dir path from a channel.json "music" block.

Today convergence sets music_flag = "--no-music" unless ctx["music"] AND a
project music.mp3 exist. This adds: if the resolved channel.json has a "music"
block with a "dir", pass --music-dir (+ tracks/crossfade) to assemble_episode.py.

channel.json block (per channel):
  "music": { "dir": "music", "tracks": 3, "crossfade_seconds": 2 }
  ( "dir" is relative to the channel folder, e.g. prehistoric-disasters/music )

Precedence: channel music-dir > ctx["music"] single bed > --no-music.
Sentinel: 'music-dir wiring'. Backs up to .pre_musicdir. Idempotent.

Requires patch_music_dir.py applied to assemble_episode.py first.

Run on LAPTOP:  python3 shared/patch_convergence_musicdir.py
"""
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "convergence_leg.py"
SENTINEL = "music-dir wiring"

ANCHOR = '''    # Music: OFF by default. Hook for the Tier-2 step (Claude\u2192fal one loopable bed).
    music_flag = "--no-music"
    if ctx.get("music"):
        cand = proj / "music.mp3"
        if cand.exists():
            music_flag = f"--music {cand}"  # split below
            t.info(f"music bed present \u2192 {cand.name} (will mux under voice)")
        else:
            t.warn("ctx['music'] set but music.mp3 not found \u2014 assembling without music")'''

# Fallback anchor without the unicode arrows, in case the file uses ASCII.
ANCHOR_ASCII = '''    music_flag = "--no-music"
    if ctx.get("music"):
        cand = proj / "music.mp3"
        if cand.exists():
            music_flag = f"--music {cand}"  # split below'''

NEW = '''    # Music: channel music-dir wiring takes precedence, then single bed, then off.
    music_flag = "--no-music"
    music_dir_args = None
    _mcfg = (ctx.get("channel_cfg") or {}).get("music") if isinstance(ctx.get("channel_cfg"), dict) else None
    if not _mcfg:
        # try to read it off channel.json directly via the channel dir
        try:
            import json as _json
            _cj = (channel_dir / "channel.json")
            if _cj.exists():
                _mcfg = _json.loads(_cj.read_text()).get("music")
        except Exception:
            _mcfg = None
    if _mcfg and _mcfg.get("dir"):
        _mdir = (channel_dir / _mcfg["dir"])
        if _mdir.is_dir():
            music_dir_args = ["--music-dir", str(_mdir),
                              "--music-tracks", str(int(_mcfg.get("tracks", 3))),
                              "--music-crossfade", str(float(_mcfg.get("crossfade_seconds", 2)))]
            t.info(f"music dir \u2192 {_mdir.name}/ (random {_mcfg.get('tracks', 3)}, "
                   f"crossfade {_mcfg.get('crossfade_seconds', 2)}s)")
    if music_dir_args is None and ctx.get("music"):
        cand = proj / "music.mp3"
        if cand.exists():
            music_flag = f"--music {cand}"  # split below
            t.info(f"music bed present \u2192 {cand.name} (will mux under voice)")
        else:
            t.warn("ctx['music'] set but music.mp3 not found \u2014 assembling without music")'''

# add the music_dir_args to the command (anchor on the existing music append block)
ANCHOR_CMD = '''    if music_flag == "--no-music":
        cmd.append("--no-music")
    else:
        cmd += ["--music", str(proj / "music.mp3")]'''
NEW_CMD = '''    if music_dir_args is not None:
        cmd += music_dir_args
    elif music_flag == "--no-music":
        cmd.append("--no-music")
    else:
        cmd += ["--music", str(proj / "music.mp3")]'''


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found.")
    text = TARGET.read_text()
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present).")
        return

    anchor = ANCHOR if ANCHOR in text else (ANCHOR_ASCII if ANCHOR_ASCII in text else None)
    if anchor is None:
        sys.exit("FAIL: music-block anchor not found — paste convergence_leg.py lines 215-240 and I'll re-cut.")
    if text.count(ANCHOR_CMD) != 1:
        sys.exit(f"FAIL: CMD anchor found {text.count(ANCHOR_CMD)} times (expected 1) — refusing.")

    new = text.replace(anchor, NEW, 1)
    new = new.replace(ANCHOR_CMD, NEW_CMD, 1)

    if new == text or SENTINEL not in new:
        sys.exit("FAIL: edit produced no change — aborting.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_musicdir")
    if not backup.exists():
        backup.write_text(text)
    TARGET.write_text(new)
    print(f"OK: patched {TARGET.name} (backup: {backup.name}).")
    print("    Verify:  grep -n 'music-dir wiring\\|music_dir_args' shared/convergence_leg.py")


if __name__ == "__main__":
    main()
