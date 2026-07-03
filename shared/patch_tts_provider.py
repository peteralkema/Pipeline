#!/usr/bin/env python3
"""
patch_tts_provider.py — insert the ElevenLabs provider seam into
recreation_pipeline.generate_voiceover().

Anchor-verified, idempotent, backs up, py_compile-checks, restores on failure.
Run from repo root: python3 shared/patch_tts_provider.py   (LAPTOP)
                    python shared/patch_tts_provider.py    (BOX, after pull)

What it does:
  Inserts a delegation block at the top of generate_voiceover() (immediately
  before `chunks = _chunk_text(script)`). The block walks up from the project
  dir to the nearest channel.json; if tts_provider == "elevenlabs" it delegates
  to elevenlabs_tts.generate_voiceover_elevenlabs() and returns. Any other
  value, or no channel.json, falls through to the existing Inworld path
  UNCHANGED. If the provider IS elevenlabs, failures raise loudly — never a
  silent fallback to the wrong voice.
"""

import py_compile
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "recreation_pipeline.py"
BACKUP = HERE / "recreation_pipeline.py.pre_tts_provider"
MODULE = HERE / "elevenlabs_tts.py"

MARKER = "TTS provider seam (patch_tts_provider)"

ANCHOR = "    chunks = _chunk_text(script)\n    if len(chunks) == 1:"

DEF_LINE = "def generate_voiceover(script: str, out_path: Path) -> Path:"

SEAM = '''    # ── TTS provider seam (patch_tts_provider): ElevenLabs delegation ────────
    # Nearest channel.json (walking up from the project dir) decides the
    # provider. tts_provider == "elevenlabs" -> delegate and return; anything
    # else (or no channel.json) -> the Inworld path below runs untouched.
    # Fail-loudly: if the provider IS elevenlabs, any failure raises — never
    # a silent fallback to the wrong voice.
    import json as _json
    _seam_dir = Path(out_path).parent.resolve()
    for _cand in (_seam_dir, *_seam_dir.parents):
        _cj = _cand / "channel.json"
        if _cj.is_file():
            _cfg = _json.loads(_cj.read_text(encoding="utf-8"))
            if str(_cfg.get("tts_provider", "")).strip().lower() == "elevenlabs":
                print(f"   TTS provider: elevenlabs ({_cj})")
                from elevenlabs_tts import generate_voiceover_elevenlabs
                generate_voiceover_elevenlabs(script, out_path, _cfg)
                return out_path
            break

'''


def die(msg: str) -> None:
    print(f"ABORT: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not TARGET.is_file():
        die(f"{TARGET} not found — run from the repo (patch lives in shared/).")

    source = TARGET.read_text(encoding="utf-8")

    if MARKER in source:
        print("Already applied — no-op.")
        return

    if DEF_LINE not in source:
        die(
            "Expected def line not found:\n"
            f"  {DEF_LINE}\n"
            "generate_voiceover has changed since this patch was written — "
            "re-grep and re-anchor before applying."
        )

    if source.count(ANCHOR) != 1:
        die(
            f"Anchor found {source.count(ANCHOR)} times (need exactly 1):\n"
            f"{ANCHOR}\n"
            "Refusing to write."
        )

    if not MODULE.is_file():
        die(
            f"{MODULE} missing — save elevenlabs_tts.py into shared/ first "
            "(the seam imports it lazily, but patching without it invites a "
            "runtime surprise)."
        )

    shutil.copy2(TARGET, BACKUP)
    print(f"Backup written: {BACKUP}")

    new_source = source.replace(ANCHOR, SEAM + ANCHOR, 1)
    TARGET.write_text(new_source, encoding="utf-8")

    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(BACKUP, TARGET)
        die(f"py_compile FAILED — original restored from backup.\n{e}")

    try:
        py_compile.compile(str(MODULE), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(BACKUP, TARGET)
        die(f"elevenlabs_tts.py failed py_compile — seam patch rolled back.\n{e}")

    print("Applied: ElevenLabs provider seam inserted into generate_voiceover().")
    print("Verify:  grep -n 'TTS provider seam' shared/recreation_pipeline.py")


if __name__ == "__main__":
    main()
