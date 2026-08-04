#!/usr/bin/env python3
"""
run_all_batches.py — the batch-of-batches driver.

Runs run_batch.py once per channel, in SEQUENCE (never parallel — one unattended
pipeline at a time, same reasoning as run_batch itself: no human watching, don't
want N concurrent fal/Inworld bursts). One channel failing never stops the rest.

It is a thin wrapper. All the real work is still run_batch.py; this just loops it
across the channels you list in a plan file so you don't kick off six runs by hand.

PLAN FILE (batch_plan.json, next to this script or at repo root):
    {
      "channels": [
        {"channel": "prehistoric-disasters", "inbox": "~/batch_inbox/prehistoric", "kling_count": 0,
         "publish_start": "2026-06-20T18:00:00-04:00", "publish_interval_hours": 12},
        {"channel": "final-hours",           "inbox": "~/batch_inbox/final-hours",  "kling_count": 40,
         "publish_start": "2026-06-21T18:00:00-04:00"},
        ...
      ]
    }
  - channel  (required): channel dir name, must have a channel.json
  - inbox    (required): folder of <name>.md + <name>.thumb.json pairs for THAT channel
  - kling_count (optional, default 0): per-channel render policy
  - publish_start (optional): ISO-8601 WITH timezone offset; omit for private-immediate
  - publish_interval_hours (optional, default 12)
  - limit (optional): cap projects for testing
  - skip (optional, default false): set true to skip this channel this run

Each channel can have its OWN publish_start so the six channels don't all release
at the same minute. Stagger them by setting different start times.

USAGE (BOX, after sourcing .env):
    python shared/run_all_batches.py --plan-file shared/batch_plan.json --plan      # dry: every channel's plan, zero spend
    python shared/run_all_batches.py --plan-file shared/batch_plan.json             # real: all channels in sequence
    python shared/run_all_batches.py --plan-file shared/batch_plan.json --only final-hours   # just one

The --plan flag here passes through to each run_batch (prep preview, no orchestrator,
no spend). Run --plan FIRST across all six, eyeball every release calendar, then drop
--plan for the real thing — ideally in tmux so closing the laptop can't orphan it.
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _log(msg: str):
    print(f"[all-batches] {msg}", flush=True)


def _runner_path() -> Path:
    p = Path(__file__).resolve().parent / "run_batch.py"
    if not p.exists():
        sys.exit(f"run_batch.py not found next to this script at {p}")
    return p


def _load_plan(plan_file: Path) -> list[dict]:
    if not plan_file.exists():
        sys.exit(f"plan file not found: {plan_file}")
    try:
        data = json.loads(plan_file.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"plan file is not valid JSON: {e}")
    chans = data.get("channels")
    if not isinstance(chans, list) or not chans:
        sys.exit("plan file has no non-empty 'channels' list")
    for i, c in enumerate(chans):
        if not c.get("channel") or not c.get("inbox"):
            sys.exit(f"channels[{i}] missing required 'channel' or 'inbox'")
    return chans


def _build_cmd(runner: Path, entry: dict, plan_mode: bool) -> list[str]:
    inbox = str(Path(entry["inbox"]).expanduser())
    cmd = [sys.executable, str(runner),
           "--inbox", inbox,
           "--channel", entry["channel"],
           "--kling-count", str(int(entry.get("kling_count", 0)))]
    if entry.get("publish_start"):
        cmd += ["--publish-start", str(entry["publish_start"]),
                "--publish-interval-hours", str(float(entry.get("publish_interval_hours", 12)))]
    if entry.get("limit") is not None:
        cmd += ["--limit", str(int(entry["limit"]))]
    if plan_mode:
        cmd.append("--plan")
    return cmd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-file", default=None,
                    help="path to batch_plan.json (default: shared/batch_plan.json or next to this script)")
    ap.add_argument("--plan", action="store_true",
                    help="pass --plan through to every run_batch (prep preview, zero spend)")
    ap.add_argument("--only", default=None,
                    help="run only this one channel from the plan (by channel name)")
    args = ap.parse_args()

    runner = _runner_path()

    # resolve plan file
    if args.plan_file:
        plan_file = Path(args.plan_file).expanduser()
    else:
        cand = Path(__file__).resolve().parent / "batch_plan.json"
        plan_file = cand if cand.exists() else _repo_root() / "shared" / "batch_plan.json"
    channels = _load_plan(plan_file)

    if args.only:
        channels = [c for c in channels if c["channel"] == args.only]
        if not channels:
            sys.exit(f"--only {args.only!r} matched no channel in the plan")

    # filter skips
    active = [c for c in channels if not c.get("skip")]
    skipped = [c["channel"] for c in channels if c.get("skip")]
    if skipped:
        _log(f"skipping (skip=true): {', '.join(skipped)}")

    mode = "PLAN (zero spend)" if args.plan else "REAL RUN"
    _log(f"{mode} — {len(active)} channel(s) in sequence: {', '.join(c['channel'] for c in active)}")
    _log("=" * 64)

    results = []
    t_all = time.time()
    for idx, entry in enumerate(active, 1):
        ch = entry["channel"]
        cmd = _build_cmd(runner, entry, args.plan)
        _log(f"[{idx}/{len(active)}] {ch} — {' '.join(cmd[2:])}")
        t0 = time.time()
        try:
            proc = subprocess.run(cmd)
            ok = (proc.returncode == 0)
            note = "ok" if ok else f"run_batch exit {proc.returncode}"
        except Exception as e:
            ok = False
            note = f"wrapper exception: {e}"
        dt = time.time() - t0
        results.append({"channel": ch, "ok": ok, "note": note, "seconds": round(dt, 1)})
        _log(f"[{idx}/{len(active)}] {ch} — {'DONE' if ok else 'FAILED'} ({note}) in {dt/60:.1f} min")
        _log("-" * 64)

    # combined manifest
    manifest = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "mode": "plan" if args.plan else "real",
        "plan_file": str(plan_file),
        "total_seconds": round(time.time() - t_all, 1),
        "results": results,
    }
    out = _repo_root() / "shared" / f"all_batches_manifest_{int(time.time())}.json"
    try:
        out.write_text(json.dumps(manifest, indent=2))
        _log(f"manifest → {out}")
    except Exception as e:
        _log(f"(could not write manifest: {e})")

    n_ok = sum(1 for r in results if r["ok"])
    n_fail = len(results) - n_ok
    _log("=" * 64)
    _log(f"SUMMARY: {n_ok} ok, {n_fail} failed, {len(results)} total "
         f"({(time.time()-t_all)/60:.1f} min)")
    for r in results:
        _log(f"  {'✓' if r['ok'] else '✗'} {r['channel']:<24} {r['note']}")
    # non-zero exit if any channel failed (so a wrapping script/tmux can tell)
    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()
