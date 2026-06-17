#!/usr/bin/env python3
"""
patch_convergence_channeldir_fix.py — fix the phantom `channel_dir` in the music
block of convergence_leg.py.

THE BUG (found 17 June, batch of 4 shipped with no music):
  The music block references `channel_dir` (channel_dir / "channel.json",
  channel_dir / _mcfg["dir"]) but `channel_dir` is NEVER defined in
  run_convergence_leg(). It throws NameError, the bare try/except swallows it,
  `_mcfg` stays None, and convergence silently passes --no-music. No error, no log.

THE FIX:
  `proj` is <channel>/projects/<project> (docstring line 13), so the channel folder
  is proj.parent.parent. Define `_channel_dir` from that and use it. Also drop the
  blanket try/except so a real failure surfaces instead of hiding (the whole reason
  this went unnoticed across a 4-video batch).

Sentinel: '_channel_dir = proj.parent.parent'. Backs up to .pre_channeldir_fix.
Idempotent. Pure ASCII anchors.

Run on LAPTOP:  python3 shared/patch_convergence_channeldir_fix.py
"""
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "convergence_leg.py"
SENTINEL = "_channel_dir = proj.parent.parent"

# The exact buggy block as it sits on the box (lines ~218-230). ASCII arrows in the
# t.info string are unicode in the file, so we anchor on the structural lines that
# are ASCII-only and unambiguous.

OLD = '''    _mcfg = (ctx.get("channel_cfg") or {}).get("music") if isinstance(ctx.get("channel_cfg"), dict) else None
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
        _mdir = (channel_dir / _mcfg["dir"])'''

NEW = '''    # proj is <channel>/projects/<project>, so the channel folder is two up.
    _channel_dir = proj.parent.parent
    _mcfg = (ctx.get("channel_cfg") or {}).get("music") if isinstance(ctx.get("channel_cfg"), dict) else None
    if not _mcfg:
        import json as _json
        _cj = (_channel_dir / "channel.json")
        if _cj.exists():
            _mcfg = _json.loads(_cj.read_text()).get("music")
        else:
            t.warn(f"no channel.json at {_cj} -- music block not resolved")
    if _mcfg and _mcfg.get("dir"):
        _mdir = (_channel_dir / _mcfg["dir"])'''


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found.")
    text = TARGET.read_text()
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present).")
        return
    if text.count(OLD) != 1:
        sys.exit(f"FAIL: buggy block found {text.count(OLD)} times (expected 1) -- "
                 "paste lines 218-235 of convergence_leg.py and I'll re-cut.")
    new = text.replace(OLD, NEW, 1)
    if new == text or SENTINEL not in new:
        sys.exit("FAIL: edit produced no change -- aborting.")
    backup = TARGET.with_suffix(TARGET.suffix + ".pre_channeldir_fix")
    if not backup.exists():
        backup.write_text(text)
    TARGET.write_text(new)
    print(f"OK: patched {TARGET.name} (backup: {backup.name}).")
    print("    Verify:  grep -n '_channel_dir' shared/convergence_leg.py")


if __name__ == "__main__":
    main()
