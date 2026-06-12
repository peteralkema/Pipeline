#!/usr/bin/env python3
"""
patch_mc_phase2.py — idempotent patcher for Mission Control Phase 1 + 2a.

Applies FIVE edits across three files:
  orchestrate.py : (1) --gate-mode + --job-id flags
                   (2) ctx dict gains gate_mode/job_id/repo_root/voice_id + init_job
  audio_leg.py   : (3) import await_gate
                   (4) keep/swap input() -> await_gate ; branch "== 2" -> "== swap"
  modea_leg.py   : (5) import await_gate
                   (6) go/skip while-loop input() -> await_gate

Discipline:
  - verifies each anchor exists EXACTLY ONCE before writing anything;
  - if an edit is already applied (marker present), it is SKIPPED (idempotent);
  - if ANY required anchor is missing, the whole patch ABORTS (no half-apply);
  - backs up each touched file to <file>.pre_mc2 before writing.

Run on the box from repo root:
  python shared/mission_control/patch_mc_phase2.py
  python shared/mission_control/patch_mc_phase2.py --check     # dry, report only
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

ORCH = REPO / "shared" / "orchestrate.py"
AUDIO = REPO / "shared" / "audio_leg.py"
MODEA = REPO / "shared" / "modea_leg.py"


# ---- each edit: (file, anchor_must_exist_once, already_applied_marker, old, new) ----

EDIT_1_ORCH_FLAGS = dict(
    file=ORCH,
    marker='--gate-mode',
    old='''    ap.add_argument("--live", action="store_true", help="actually run (skips kickoff prompt if given)")
    return ap.parse_args()''',
    new='''    ap.add_argument("--live", action="store_true", help="actually run (skips kickoff prompt if given)")
    ap.add_argument("--gate-mode", choices=["cli", "job"], default="cli",
                    help="cli = terminal input() gates (default, unchanged); "
                         "job = drive gates via the job record (Mission Control)")
    ap.add_argument("--job-id", default=None,
                    help="job record id (Mission Control passes this; manual runs mint one)")
    return ap.parse_args()''',
)

EDIT_2_ORCH_CTX = dict(
    file=ORCH,
    marker='"gate_mode": getattr(args',
    old='''    ctx = {
        "t": t, "shared": shared_dir, "channel_dir": channel_dir,
        "project_dir": proj_dir, "beats_list_json": beats_list_json,
        "durations": os.path.join(proj_dir, "durations.json") if proj_dir else None,
        "clips_dir": os.path.join(os.path.dirname(shared_dir), "clips"),
        "box": "peter@116.202.18.68", "modeb_port": 8000, "modea_port": 8001,
        "run_cwd": None, "script_md": None, "dry_run": dry, "py": sys.executable,
    }''',
    new='''    import time as _time
    _repo_root = os.path.dirname(shared_dir)
    _job_id = args.job_id or f"{channel}__{args.project}__{int(_time.time())}"
    ctx = {
        "t": t, "shared": shared_dir, "channel_dir": channel_dir,
        "project_dir": proj_dir, "beats_list_json": beats_list_json,
        "durations": os.path.join(proj_dir, "durations.json") if proj_dir else None,
        "clips_dir": os.path.join(os.path.dirname(shared_dir), "clips"),
        "box": "peter@116.202.18.68", "modeb_port": 8000, "modea_port": 8001,
        "run_cwd": None, "script_md": None, "dry_run": dry, "py": sys.executable,
        "gate_mode": getattr(args, "gate_mode", "cli"),
        "job_id": _job_id,
        "repo_root": __import__("pathlib").Path(_repo_root),
        "voice_id": None,
    }
    if ctx["gate_mode"] == "job":
        sys.path.insert(0, os.path.join(shared_dir, "mission_control"))
        from gate_protocol import init_job
        init_job(_job_id, channel, args.project, ctx["repo_root"])
        t.info(f"gate-mode=job · job_id={_job_id}")''',
)

EDIT_3_AUDIO_IMPORT = dict(
    file=AUDIO,
    marker='from gate_protocol import await_gate',
    old='''import os, sys, subprocess
from pathlib import Path''',
    new='''import os, sys, subprocess
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mission_control"))
from gate_protocol import await_gate''',
)

EDIT_4_AUDIO_GATE = dict(
    file=AUDIO,
    marker='name="audio"',
    old='''    choice = input("  >>> [1] keep / [2] swap: ").strip()

    if choice == "2":''',
    new='''    choice = await_gate(
        ctx, name="audio",
        payload={"voiceover": str(proj / "voiceover.mp3"),
                 "minutes": dur_min,
                 "voice_id": ctx.get("voice_id")},
        options=["keep", "swap"],
        cli_prompt="  >>> [1] keep / [2] swap: ",
        cli_map={"1": "keep", "2": "swap", "keep": "keep", "swap": "swap"},
        phase="gate_audio",
    )

    if choice == "swap":''',
)

EDIT_5_MODEA_IMPORT = dict(
    file=MODEA,
    marker='from gate_protocol import await_gate',
    old='''import os, sys, re, json, subprocess
from pathlib import Path''',
    new='''import os, sys, re, json, subprocess
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mission_control"))
from gate_protocol import await_gate''',
)

EDIT_6_MODEA_GATE = dict(
    file=MODEA,
    marker='name="stills"',
    old='''    while True:
        ans = input("  >>> type 'go' when you've finished reviewing the stills (or 'skip'): ").strip().lower()
        if ans in ("go", "skip", "continue", "c", "done", "y", "yes"):
            t.ok(f"Mode A gate cleared ({ans}).")
            return True
        t.info("(type 'go' when the stills pass the aesthetic firewall)")''',
    new='''    decision = await_gate(
        ctx, name="stills",
        payload={"stills_count": stills_count,
                 "stills_dir": stills_dir,
                 "engine_project": engine_project},
        options=["go", "skip"],
        cli_prompt="  >>> type 'go' when you've finished reviewing the stills (or 'skip'): ",
        cli_map={"go": "go", "skip": "skip", "continue": "go", "c": "go",
                 "done": "go", "y": "go", "yes": "go"},
        phase="gate_stills",
    )
    t.ok(f"Mode A gate cleared ({decision}).")
    return True''',
)

EDITS = [
    ("orchestrate: --gate-mode/--job-id flags", EDIT_1_ORCH_FLAGS),
    ("orchestrate: ctx gate fields + init_job", EDIT_2_ORCH_CTX),
    ("audio_leg: import await_gate",            EDIT_3_AUDIO_IMPORT),
    ("audio_leg: keep/swap gate",               EDIT_4_AUDIO_GATE),
    ("modea_leg: import await_gate",            EDIT_5_MODEA_IMPORT),
    ("modea_leg: go/skip gate",                 EDIT_6_MODEA_GATE),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    # ---- Phase 1: verify every file exists and analyse each edit ----
    plans = []   # (name, edit, action)  action in {"apply","skip-applied","ABORT"}
    fatal = []
    for name, e in EDITS:
        f = e["file"]
        if not f.is_file():
            fatal.append(f"{name}: file missing: {f}")
            continue
        text = f.read_text()
        if e["marker"] in text:
            plans.append((name, e, "skip-applied"))
            continue
        n = text.count(e["old"])
        if n == 1:
            plans.append((name, e, "apply"))
        elif n == 0:
            fatal.append(f"{name}: ANCHOR NOT FOUND in {f.name} "
                         f"(and not already applied)")
        else:
            fatal.append(f"{name}: anchor appears {n}x in {f.name} (must be exactly 1)")

    print("=== PATCH PLAN ===")
    for name, e, action in plans:
        print(f"  [{action:<13}] {name}")
    if fatal:
        print("\n=== ABORT — cannot safely apply ===")
        for m in fatal:
            print("  !!", m)
        sys.exit(1)

    to_apply = [(n, e) for (n, e, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all edits already applied. (idempotent)")
        return
    if args.check:
        print(f"\n--check: {len(to_apply)} edit(s) WOULD apply. No files written.")
        return

    # ---- Phase 2: back up each touched file once, then apply ----
    touched = {e["file"] for _, e in to_apply}
    for f in touched:
        bak = f.with_suffix(f.suffix + ".pre_mc2")
        if not bak.exists():
            bak.write_text(f.read_text())
            print(f"  backup -> {bak.name}")

    for name, e in to_apply:
        f = e["file"]
        text = f.read_text()
        # re-verify uniqueness at write time (paranoia: file unchanged since plan)
        if text.count(e["old"]) != 1:
            print(f"  !! {name}: anchor count changed at write time — ABORTING")
            sys.exit(2)
        f.write_text(text.replace(e["old"], e["new"], 1))
        print(f"  applied -> {name}")

    print("\n=== DONE ===")
    print("Re-run with --check to confirm idempotency (should say 'all already applied').")


if __name__ == "__main__":
    main()
