#!/usr/bin/env python3
"""patch_music_fallback.py -- MUSIC-SOURCE FALLBACK (queued 16 Aug, the
archangel-michael near-miss; every fresh project is born music-less and a
forgotten copy publishes a silent master).

assemble.py reads <project>/music/ only. This patch makes the project
folder an OVERRIDE and falls back to <channel>/music/ when it is absent or
empty. Doctrine-consistent with SS12.5's mood-subfolder ruling: missing
subfolder falls back to the root pool, one level up. No config, no mode.
Idempotent: re-running is a no-op."""
import py_compile, shutil, sys
from pathlib import Path

p = Path.home() / "Projects/Pipeline/shared/v2/assemble.py"
src = p.read_text()
if "MUSIC FALLBACK" in src:
    print("already patched -- no-op"); sys.exit(0)

anchor = '        music_src = _build_music_bed(project_dir / "music", voice_dur, work)'
assert anchor in src, "ANCHOR NOT FOUND -- verify against the box copy first"
new = '''        # MUSIC FALLBACK (v2 patch): project folder is an OVERRIDE; the
        # channel pool is the default. project_dir = <channel>/projects/<slug>
        _mdir = Path(project_dir) / "music"
        _has = _mdir.is_dir() and any(
            _mdir.glob("*.mp3")) or _mdir.is_dir() and any(
            list(_mdir.glob("*.m4a")) + list(_mdir.glob("*.wav")))
        if not _has:
            _chan = Path(project_dir).parent.parent / "music"
            if _chan.is_dir():
                print("   music: project folder empty -- falling back to "
                      "channel pool %s" % _chan)
                _mdir = _chan
        music_src = _build_music_bed(_mdir, voice_dur, work)'''
shutil.copy(p, p.with_suffix(".py.pre_musicfallback"))
p.write_text(src.replace(anchor, new, 1))
py_compile.compile(str(p), doraise=True)
print("patched + compiles:", p)
