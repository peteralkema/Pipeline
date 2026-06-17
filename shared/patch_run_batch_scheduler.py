#!/usr/bin/env python3
"""
patch_run_batch_scheduler.py - add the no-state upload scheduler to run_batch.py.

WHAT IT DOES (idempotent; sentinel '# [scheduler]'):
  1. import datetime/timedelta/timezone
  2. add two module helpers: _parse_publish_start (tz-aware, rejects naive) and
     _publish_at_for_slot (slot N -> (utc_rfc3339, local_iso))
  3. add --publish-start <ISO+tz> and --publish-interval-hours (default 12) args
  4. rewrite the batch loop so each successfully-prepped video gets the next release
     slot, writes <proj>/publish.json {"publish_at": <utc>}, and --plan prints the
     full release calendar (local tz AND UTC) before any spend.

NO-STATE: nothing persists across batches. Each invocation's calendar starts at the
--publish-start you give; set the next batch's start past the last batch's tail
(Studio's Scheduled tab is the collision check). Omit --publish-start entirely and the
runner behaves exactly as before (private-immediate). Scheduling is opt-in.

The publishAt reaches the uploader via the per-project publish.json (read by
convergence's _maybe_upload, see patch_convergence_publish_at.py) -- written once at
prep, read once at upload, nothing in between can corrupt it (the render_policy.json /
thumbnail.json pattern). upload_episode.py --publish-at already forces private+publishAt;
no change needed there.

Run on the LAPTOP from the repo root:  python3 shared/patch_run_batch_scheduler.py
"""
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "run_batch.py"
SENTINEL = "# [scheduler]"

IMPORT_ANCHOR = "import time\nfrom pathlib import Path\n"
IMPORT_NEW = "import time\nfrom datetime import datetime, timedelta, timezone\nfrom pathlib import Path\n"

HELPER_ANCHOR = (
    'def _log(msg: str):\n'
    '    print(f"[batch] {msg}", flush=True)\n'
)
HELPER_NEW = HELPER_ANCHOR + '''

def _parse_publish_start(s: str) -> "datetime":
    """[scheduler] Parse --publish-start to a tz-AWARE datetime. Reject naive (a release
    calendar with no timezone is ambiguous). Accepts a trailing 'Z' for UTC."""
    raw = s.strip()
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        sys.exit(f"--publish-start not ISO-8601: {s!r} "
                 f"(want e.g. 2026-06-18T19:00:00-04:00 or 2026-06-18T23:00:00Z)")
    if dt.tzinfo is None or dt.utcoffset() is None:
        sys.exit(f"--publish-start has no timezone: {s!r} -- include an offset "
                 f"(e.g. -04:00) or 'Z'. A release calendar must be unambiguous.")
    return dt


def _publish_at_for_slot(start: "datetime", interval: "timedelta", slot: int):
    """[scheduler] (utc_rfc3339, local_iso) for video index `slot`. YouTube's publishAt
    must be RFC3339 UTC; the local string is for the human-readable calendar."""
    local_dt = start + slot * interval
    utc = local_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return utc, local_dt.isoformat()
'''

ARGS_ANCHOR = (
    '    ap.add_argument("--limit", type=int, default=None, help="process at most this many (testing)")\n'
    '    args = ap.parse_args()\n'
)
ARGS_NEW = (
    '    ap.add_argument("--limit", type=int, default=None, help="process at most this many (testing)")\n'
    '    ap.add_argument("--publish-start", default=None,\n'
    '                    help="[scheduler] ISO-8601 timestamp WITH timezone for the FIRST "\n'
    '                         "video\'s publishAt, e.g. 2026-06-18T19:00:00-04:00 or ...Z. "\n'
    '                         "Omit for private-immediate (unchanged behaviour).")\n'
    '    ap.add_argument("--publish-interval-hours", type=float, default=12.0,\n'
    '                    help="[scheduler] hours between successive videos\' publishAt "\n'
    '                         "(default 12 = twice daily).")\n'
    '    args = ap.parse_args()\n'
)

LOOP_ANCHOR = '''    manifest = []
    for md in mds:
        name = md.stem
        thumb = md.with_suffix(".thumb.json")
        if not thumb.exists():
            _log(f"SKIP '{name}': no sibling {thumb.name}")
            manifest.append({"name": name, "status": "skipped", "detail": "no .thumb.json"})
            continue

        proj = prep_project(md, thumb, args.channel, args.kling_count, shared, args.plan)
        if proj is None:
            manifest.append({"name": name, "status": "prep_failed", "detail": "see log"})
            continue
        if args.plan:
            manifest.append({"name": name, "status": "planned", "detail": str(proj)})
            continue

        try:
            ok, detail = run_one(name, proj, args.channel, shared, py)
        except Exception as e:  # isolation: one job's crash never kills the batch
            ok, detail = False, f"exception: {type(e).__name__}: {e}"
        manifest.append({"name": name, "status": "done" if ok else "failed", "detail": detail})
        _log(f"{'DONE' if ok else 'FAILED'} '{name}': {detail}")
'''

LOOP_NEW = '''    # [scheduler] optional release schedule (no-state: this batch's calendar starts at
    # --publish-start; set the next batch's start past this one's tail by hand).
    publish_start = None
    interval = None
    if args.publish_start:
        publish_start = _parse_publish_start(args.publish_start)
        interval = timedelta(hours=args.publish_interval_hours)
        _log(f"schedule ON  start={publish_start.isoformat()}  "
             f"interval={args.publish_interval_hours}h  "
             f"(upload PRIVATE + publishAt; YouTube auto-publishes; front-48h clock starts at publishAt)")
    else:
        _log("schedule OFF  (private-immediate; pass --publish-start <ISO+tz> to schedule)")

    manifest = []
    scheduled = 0  # [scheduler] gap-free slot index; increments only on a successful prep
    for md in mds:
        name = md.stem
        thumb = md.with_suffix(".thumb.json")
        if not thumb.exists():
            _log(f"SKIP '{name}': no sibling {thumb.name}")
            manifest.append({"name": name, "status": "skipped", "detail": "no .thumb.json"})
            continue

        proj = prep_project(md, thumb, args.channel, args.kling_count, shared, args.plan)
        if proj is None:
            manifest.append({"name": name, "status": "prep_failed", "detail": "see log"})
            continue

        # [scheduler] this video gets the next release slot (only reached on a good prep,
        # so the calendar has no gaps for shipped videos).
        pub_utc = pub_local = None
        if publish_start is not None:
            pub_utc, pub_local = _publish_at_for_slot(publish_start, interval, scheduled)
        slot = scheduled
        scheduled += 1

        if args.plan:
            if pub_utc:
                _log(f"  [plan] slot {slot}: publish {pub_local}  (UTC {pub_utc})")
            manifest.append({"name": name, "status": "planned",
                             "detail": str(proj) + (f"  publishAt={pub_utc}" if pub_utc else "")})
            continue

        if pub_utc:
            (proj / "publish.json").write_text(json.dumps({"publish_at": pub_utc}, indent=2))
            _log(f"  scheduled -> publish.json publish_at={pub_utc}  ({pub_local} local)")

        try:
            ok, detail = run_one(name, proj, args.channel, shared, py)
        except Exception as e:  # isolation: one job's crash never kills the batch
            ok, detail = False, f"exception: {type(e).__name__}: {e}"
        manifest.append({"name": name, "status": "done" if ok else "failed", "detail": detail})
        _log(f"{'DONE' if ok else 'FAILED'} '{name}': {detail}")
'''


def main():
    if not TARGET.exists():
        sys.exit(f"target not found: {TARGET}")
    src = TARGET.read_text()

    if SENTINEL in src:
        print(f"[patch] sentinel present -- {TARGET.name} already patched. No-op.")
        return

    for label, anchor in (("import", IMPORT_ANCHOR), ("helper", HELPER_ANCHOR),
                          ("args", ARGS_ANCHOR), ("loop", LOOP_ANCHOR)):
        n = src.count(anchor)
        if n != 1:
            sys.exit(f"[patch] ABORT: {label} anchor found {n} times (expected 1). "
                     f"Source drifted -- inspect before patching.")

    backup = TARGET.with_suffix(".py.pre_scheduler")
    if not backup.exists():
        backup.write_text(src)
        print(f"[patch] backup -> {backup.name}")

    out = src
    out = out.replace(IMPORT_ANCHOR, IMPORT_NEW, 1)
    out = out.replace(HELPER_ANCHOR, HELPER_NEW, 1)
    out = out.replace(ARGS_ANCHOR, ARGS_NEW, 1)
    out = out.replace(LOOP_ANCHOR, LOOP_NEW, 1)

    if SENTINEL not in out:
        sys.exit("[patch] ABORT: sentinel missing after edit -- nothing written.")

    TARGET.write_text(out)
    print(f"[patch] OK -- scheduler wired into {TARGET.name}")
    print("[patch] verify:  python3 -c \"import ast; ast.parse(open('shared/run_batch.py').read())\"")


if __name__ == "__main__":
    main()
