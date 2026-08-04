#!/usr/bin/env python3
"""
run_batch.py — unattended batch runner for the content factory.

Takes a folder of scripts (+ matching thumbnail specs) and runs each one through
the FULL pipeline with zero human gates, ending in a private upload. This is the
"set up once, ship the first 20" path.

INPUT LAYOUT (one inbox folder, matched by basename):
    ~/batch_inbox/
        toba.md            toba.thumb.json
        doggerland.md      doggerland.thumb.json
        ...
  - <name>.md         : the locked Ante Machinam beat-script
  - <name>.thumb.json : {"subject": "...", "title": "...", "subtitle": "..."}
                        (subject = what the thumbnail depicts; title/subtitle = the
                        locked headline). A .md with NO sibling .thumb.json is SKIPPED
                        with a warning (so a half-prepped inbox can't ship a video with
                        no thumbnail).

WHAT IT DOES per script (sequential, failure-isolated):
  1. Create the project folder:  <channel>/projects/<name>/
  2. Parse the .md -> beats (calls parse_script.py the same way "create project" does)
  3. Write render_policy.json  -> {"kling_count": N}   (N=0 => all Ken Burns / $3 path)
  4. Copy <name>.thumb.json     -> <project>/thumbnail.json   (convergence picks it up)
  5. Run the orchestrator:  python orchestrate.py --project <name> --unattended
     (gates auto-accept; audio kept; stills accepted; assemble; thumbnail; upload private)
  6. Record outcome in the manifest.

It does NOT parallelise (one unattended run at a time — no human is watching, so we
don't want N concurrent fal/Inworld bursts). It does NOT delete anything. One project
failing never stops the batch.

Scheduling is OUT OF SCOPE here (private-immediate). When added, it lives in
upload_episode.py (publishAt) and the runner passes a per-project datetime.

Run on the BOX (after sourcing .env), e.g.:
    python shared/run_batch.py \
        --inbox ~/batch_inbox \
        --channel prehistoric-disasters \
        --kling-count 0

Dry preview (prep only, no orchestrator):
    python shared/run_batch.py --inbox ~/batch_inbox --channel prehistoric-disasters --plan
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _log(msg: str):
    print(f"[batch] {msg}", flush=True)


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


def _load_ingest(shared: Path):
    """Import the real create_project from mission_control/ingest.py so batch-created
    projects are byte-identical to panel-created ones (mkdir + script.md + parse +
    verify-refuse + scoped git). Returns the module or None."""
    mc = shared / "mission_control"
    if str(mc) not in sys.path:
        sys.path.insert(0, str(mc))
    try:
        import ingest
        return ingest
    except Exception as e:
        _log(f"  !! could not import ingest.py ({e})")
        return None


def prep_project(md: Path, thumb: Path, channel: str, kling_count: int,
                 shared: Path, plan: bool) -> Path | None:
    """Create the project via the REAL panel flow (ingest.create_project), then write
    render_policy.json + thumbnail.json into it. Returns the project dir or None.
    The slug is the .md basename; the channel is resolved from the script HEADER by
    ingest (we pass --channel only to locate the resulting folder + sanity-check)."""
    name = md.stem
    _log(f"prep '{name}'")

    # validate the thumbnail spec BEFORE creating anything (fail fast, no half state)
    try:
        spec = json.loads(thumb.read_text())
    except Exception as e:
        _log(f"  !! {thumb.name} unreadable ({e}) — skipping")
        return None
    if not (spec.get("subject") and spec.get("title")):
        _log(f"  !! {thumb.name} missing 'subject' or 'title' — skipping")
        return None

    if plan:
        _log(f"  [plan] would create_project(slug={name}), write render_policy.json"
             f"(kling_count={kling_count}) + thumbnail.json")
        return _repo_root() / channel / "projects" / name

    ingest = _load_ingest(shared)
    if ingest is None:
        return None

    # create_project: resolves channel from header, mkdir, write script.md, parse,
    # verify (REFUSE on wordless/missing VISUAL), scoped git. Identical to the panel.
    res = ingest.create_project(md.read_text(), name, do_git=True)
    if not res.get("ok"):
        _log(f"  !! create_project refused at stage '{res.get('stage')}': "
             f"{res.get('error')}  verify={res.get('verify')}")
        return None

    folder = res["folder"]
    if folder != channel:
        _log(f"  !! header channel '{folder}' != --channel '{channel}' — skipping "
             f"(check the script header)")
        return None

    proj = _repo_root() / folder / "projects" / res["slug"]
    # tiered render policy (0 = all Ken Burns / $3 path) + thumbnail spec
    (proj / "render_policy.json").write_text(json.dumps({"kling_count": kling_count}, indent=2))
    (proj / "thumbnail.json").write_text(json.dumps(spec, indent=2))
    _log(f"  created {proj}  (beats verified: {res['verify']['beats']} beats, "
         f"render_policy kling_count={kling_count}, thumbnail.json written)")
    return proj


def run_one(name: str, proj: Path, channel: str, shared: Path, py: str) -> tuple[bool, str]:
    """Run the orchestrator unattended on a prepped project. Returns (ok, detail).
    NOTE: orchestrate.py resolves the channel from the SCRIPT HEADER (not a flag),
    so we pass --project and --beats (the parsed {header,beats} wrapper), not --channel."""
    orch = shared / "orchestrate.py"
    beats_full = proj / "beats_full.json"
    cmd = [py, str(orch), "--project", name, "--beats", str(beats_full), "--unattended"]
    _log(f"run  '{name}'  (unattended): {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)
    tail = []
    for line in proc.stdout:
        line = line.rstrip()
        tail.append(line)
        if len(tail) > 60:
            tail.pop(0)
        print(f"    {line}", flush=True)
    proc.wait()
    if proc.returncode != 0:
        return False, f"orchestrator exit {proc.returncode}; last line: {tail[-1] if tail else '—'}"
    return True, "ok"


def main():
    ap = argparse.ArgumentParser(description="Unattended batch runner")
    ap.add_argument("--inbox", required=True, help="folder of <name>.md + <name>.thumb.json pairs")
    ap.add_argument("--channel", required=True, help="channel dir name, e.g. prehistoric-disasters")
    ap.add_argument("--kling-count", type=int, default=0,
                    help="tiered render: first N beats Kling, rest Ken Burns (0 = all Ken Burns)")
    ap.add_argument("--plan", action="store_true", help="prep preview only — no parsing, no orchestrator")
    ap.add_argument("--limit", type=int, default=None, help="process at most this many (testing)")
    ap.add_argument("--publish-start", default=None,
                    help="[scheduler] ISO-8601 timestamp WITH timezone for the FIRST "
                         "video's publishAt, e.g. 2026-06-18T19:00:00-04:00 or ...Z. "
                         "Omit for private-immediate (unchanged behaviour).")
    ap.add_argument("--publish-interval-hours", type=float, default=12.0,
                    help="[scheduler] hours between successive videos' publishAt "
                         "(default 12 = twice daily).")
    args = ap.parse_args()

    py = sys.executable
    shared = Path(__file__).resolve().parent
    inbox = Path(args.inbox).expanduser()
    channel_dir = _repo_root() / args.channel
    if not inbox.is_dir():
        sys.exit(f"inbox not found: {inbox}")
    if not (channel_dir / "channel.json").exists():
        sys.exit(f"channel.json not found under {channel_dir} — is --channel correct?")

    mds = sorted(inbox.glob("*.md"))
    if args.limit:
        mds = mds[:args.limit]
    if not mds:
        sys.exit(f"no .md scripts in {inbox}")

    _log(f"inbox={inbox}  channel={args.channel}  kling_count={args.kling_count}  "
         f"scripts={len(mds)}  plan={args.plan}")

    # [scheduler] optional release schedule (no-state: this batch's calendar starts at
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
        # [archive-on-ship] #11n: move the shipped pair out of the inbox so a
        # re-run cannot re-render/re-upload it. Only on ok=True; never in --plan
        # (plan continues earlier). Failed/skipped pairs stay put for a retry.
        if ok:
            try:
                _shipped = inbox / "_shipped"
                _shipped.mkdir(exist_ok=True)
                for _pf in (md, thumb):
                    if _pf.exists():
                        _pf.rename(_shipped / _pf.name)
                _log(f"  archived -> {_shipped}/ ({md.name} + {thumb.name})")
            except Exception as _e:
                _log(f"  archive skipped for '{name}': {type(_e).__name__}: {_e}")

    # write the manifest
    out = inbox / f"_batch_manifest_{int(time.time())}.json"
    out.write_text(json.dumps(manifest, indent=2))
    done = sum(1 for m in manifest if m["status"] == "done")
    _log(f"BATCH COMPLETE — {done}/{len(manifest)} shipped. Manifest: {out}")
    for m in manifest:
        _log(f"  {m['status']:12} {m['name']}  {m['detail']}")


if __name__ == "__main__":
    main()
