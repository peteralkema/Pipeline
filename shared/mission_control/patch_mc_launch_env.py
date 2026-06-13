#!/usr/bin/env python3
"""
patch_mc_launch_env.py — give the detached orchestrate subprocess the venv PATH.

The crash: launch_job spawns orchestrate with start_new_session=True and NO
env=, so the detached process inherits the service's environment, which does
NOT have the venv's bin on PATH. audio_leg calls bare "whisper" -> FileNotFound.

Fix: build an env for the Popen that prepends the venv bin dir to PATH. The bin
dir is derived from sys.executable (the server runs under the venv python, so
Path(sys.executable).parent IS the venv bin) — correct by construction, no
hardcoded home path. This fixes whisper AND every other venv/system tool the
subprocess needs (ffmpeg, sub-tool pythons, etc.) in one move.

One edit to pipeline_server.py's launch_job: add env= to the Popen call.

Idempotent (marker), backs up to .pre_launchenv.

Run on the box:
  python shared/mission_control/patch_mc_launch_env.py --check
  python shared/mission_control/patch_mc_launch_env.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

EDITS.append(dict(
    marker="_venv_bin =",
    old='''    logf = open(jobs_dir(_REPO) / f"{job_id}.log", "ab")
    subprocess.Popen(
        cmd, cwd=str(_REPO),
        stdout=logf, stderr=subprocess.STDOUT,
        start_new_session=True,        # detach from this process group
    )''',
    new='''    logf = open(jobs_dir(_REPO) / f"{job_id}.log", "ab")
    # The detached subprocess does NOT inherit our interactive shell's venv PATH.
    # sys.executable is the venv python, so its parent IS the venv bin dir —
    # prepend it to PATH so bare tool names (whisper, ffmpeg, ...) resolve.
    _env = dict(_os.environ)
    _venv_bin = str(Path(sys.executable).parent)
    _env["PATH"] = _venv_bin + ":" + _env.get("PATH", "")
    subprocess.Popen(
        cmd, cwd=str(_REPO),
        stdout=logf, stderr=subprocess.STDOUT,
        start_new_session=True,        # detach from this process group
        env=_env,
    )''',
))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if not T.is_file():
        sys.exit(f"missing: {T}")
    text = T.read_text()

    # _os is imported in the stills-controls patch (import os as _os). If that
    # patch isn't applied, fall back to the stdlib os already imported at top.
    if "import os as _os" not in text and "_os." not in text:
        # rewrite the edit to use plain os instead of _os
        EDITS[0]["new"] = EDITS[0]["new"].replace("_os.environ", "os.environ")

    plans, fatal = [], []
    for i, e in enumerate(EDITS, 1):
        if e["marker"] in text:
            plans.append((i, "skip-applied")); continue
        n = text.count(e["old"])
        if n == 1: plans.append((i, "apply"))
        elif n == 0: fatal.append(f"edit {i}: ANCHOR NOT FOUND")
        else: fatal.append(f"edit {i}: anchor x{n}")

    print("=== LAUNCH-ENV PATCH PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_launchenv")
    if not bak.exists():
        bak.write_text(text); print(f"  backup -> {bak.name}")
    for i, e in enumerate(EDITS, 1):
        if i not in to_apply: continue
        text = T.read_text()
        if text.count(e["old"]) != 1:
            print(f"  !! edit {i}: anchor changed — ABORT"); sys.exit(2)
        T.write_text(text.replace(e["old"], e["new"], 1))
        print(f"  applied -> edit {i}")
    print("\n=== DONE === restart: systemctl --user restart mission-control.service")


if __name__ == "__main__":
    main()
