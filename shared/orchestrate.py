#!/usr/bin/env python3
"""
orchestrate.py — Peter's Pipeline Orchestrator v1.0
The master, singular, channel-agnostic conductor. SKELETON (build step 1):
banner → kickoff prompt → read beats.json → run-context → decide_legs() → narrate plan.
No legs run yet; this proves the decision logic + the telemetry voice, costs nothing.

Build path: this is the new Path-2 leg-based conductor. Legs get wired in later steps.

Usage:
    python3 orchestrate.py --project ep1-the-promise [--beats path] [--log L] [--dry-run/--live]
"""
import os, sys, json, argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from telemetry import Telemetry
from banner import BANNER


def parse_args():
    ap = argparse.ArgumentParser(description="Peter's Pipeline Orchestrator v1.0")
    ap.add_argument("--project", help="project name (beats default: projects/<p>/beats.json)")
    ap.add_argument("--beats", default=None, help="explicit beats.json path")
    ap.add_argument("--log", choices=["quiet", "normal", "verbose"], default=None,
                    help="verbosity (skips the kickoff prompt if given)")
    ap.add_argument("--dry-run", action="store_true", help="plan only, render nothing")
    ap.add_argument("--live", action="store_true", help="actually run (skips kickoff prompt if given)")
    return ap.parse_args()


def kickoff_prompt(args):
    """Interactive launch menu — verbosity + dry/live. Flags bypass it. Extensible block."""
    # verbosity
    if args.log:
        level = args.log
    else:
        ans = input("  ▸ verbosity?  [1] quiet  [2] normal  [3] verbose   (default 2): ").strip()
        level = {"1": "quiet", "2": "normal", "3": "verbose", "": "normal"}.get(ans, "normal")
    # mode
    if args.live:
        dry = False
    elif args.dry_run:
        dry = True
    else:
        ans = input("  ▸ mode?  [1] dry-run (plan + cost, render nothing)  [2] live   (default dry-run): ").strip()
        dry = {"1": True, "2": False, "": True}.get(ans, True)
    return level, dry


def resolve_beats_path(args):
    if args.beats:
        return args.beats
    if args.project:
        # prefer the {header,beats} wrapper; fall back to a plain beats.json
        for name in ("beats_full.json", "beats.json"):
            cand = os.path.join("projects", args.project, name)
            if os.path.exists(cand):
                return cand
        return os.path.join("projects", args.project, "beats_full.json")
    return None


def load_beats(path, t):
    """Accepts the {header, beats} wrapper (orchestrator input from --json-full) OR a
    bare list (back-compat). Returns (header, beats_list)."""
    if not path or not os.path.exists(path):
        t.halt(f"beats file not found at {path or '(no path)'} — run parse_script.py "
               f"--json-full first, or pass --beats <path>.")
        sys.exit(1)
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        t.halt(f"beats file did not parse: {e}")
        sys.exit(1)
    if isinstance(data, dict) and "beats" in data:
        header, beats = data.get("header", {}), data["beats"]
    elif isinstance(data, list):
        header, beats = {}, data
    else:
        t.halt("beats file is neither a {header,beats} wrapper nor a list.")
        sys.exit(1)
    if not beats:
        t.halt("beats file has no beats.")
        sys.exit(1)
    return header, beats


def load_resolved_config(channel, t):
    """Load <channel>/channel.json, resolve <project>/look.json override ON TOP.
    Channel defaults -> project overrides. Most channels have no look.json; Lazarus
    is the channel built on it. Returns the resolved config dict (or None if no channel)."""
    if not channel:
        return None
    # walk: we run from the channel folder, so channel.json is at ./channel.json,
    # but also accept <channel>/channel.json from repo root.
    candidates = ["channel.json", os.path.join(channel, "channel.json")]
    cfg_path = next((c for c in candidates if os.path.exists(c)), None)
    if not cfg_path:
        t.warn(f"channel.json not found for '{channel}' (looked: {candidates}). "
               f"Run from the channel folder, or check the channel name.")
        return None
    try:
        cfg = json.load(open(cfg_path, encoding="utf-8"))
    except Exception as e:
        t.halt(f"channel.json did not parse: {e}")
        sys.exit(1)
    t.ok(f"channel identity loaded → {cfg_path} (voice={cfg.get('voices', {}).get('narrator', cfg.get('voice_id','?'))}, "
         f"{cfg.get('width','?')}x{cfg.get('height','?')})")
    return cfg


def decide_legs(beats, t):
    """Scan composition → which legs fire. Pure logic; logs each decision (teaching lines)."""
    modes = [b.get("mode") for b in beats if isinstance(b, dict) and "mode" in b]
    has_a = "A" in modes
    has_b = "B" in modes
    has_lock = any(b.get("lock") or b.get("lipsync") for b in beats if isinstance(b, dict))

    legs = ["audio"]  # always — timing source
    t.decision("audio leg WILL run (always — it is the timing source)")

    if has_b:
        legs.append("modeB")
        n = modes.count("B")
        t.decision(f"composition has {n} Mode B beats → Mode B leg WILL run (+ Mode B gate)")
    else:
        t.decision("no Mode B beats → Mode B leg skipped")

    if has_a:
        legs.append("modeA")
        n = modes.count("A")
        t.decision(f"composition has {n} Mode A beats → Mode A leg WILL run (+ Mode A gate)")
    else:
        t.decision("no Mode A beats → Mode A leg skipped")

    if has_lock:
        legs.append("lipsync")
        t.decision("locked/lip-sync beats present → lip-sync leg WILL run (FUTURE — not built)")
    else:
        t.decision("no locked beats → lip-sync leg skipped")

    legs.append("convergence")
    t.decision("convergence WILL run (assemble → thumbnail gate → convergence gate → upload)")
    return legs, modes


def main():
    args = parse_args()
    print(BANNER)
    level, dry = kickoff_prompt(args)
    t = Telemetry(level)
    t.info(f"verbosity={level}   mode={'DRY-RUN (nothing renders)' if dry else 'LIVE'}")

    beats_path = resolve_beats_path(args)
    header, beats = load_beats(beats_path, t)
    channel = header.get("channel") or "(unknown — no channel in header)"
    project = args.project or "(unnamed)"
    n = len(beats)
    n_a = sum(1 for b in beats if isinstance(b, dict) and b.get("mode") == "A")
    n_b = sum(1 for b in beats if isinstance(b, dict) and b.get("mode") == "B")
    when = datetime.now().strftime("%Y-%m-%d %H:%M")

    t.rule()
    t.context(channel, project, n, n_a, n_b, when)
    t.rule()

    t.phase("PREFLIGHT")
    t.ok(f"beats loaded → {n} beats from {beats_path}")
    # metadata lives in the script header (single input, no metadata.json). Halt EARLY
    # (before any leg, before any spend) if the header is incomplete.
    required = ("channel", "title", "description", "tags")
    missing = [k for k in required if not header.get(k)]
    if missing:
        t.halt(f"script header missing {missing}. Add them to the top of script.md and "
               f"re-run parse_script.py --json-full. (Halting now — before any render/spend.)")
        sys.exit(1)
    t.ok(f"header complete → title, description, tags, channel all present")
    cfg = load_resolved_config(header.get("channel"), t)
    if cfg is None:
        t.warn("proceeding without resolved channel identity (skeleton tolerates it; "
               "legs will require it).")

    t.phase("DECIDE LEGS (composition scan)")
    legs, modes = decide_legs(beats, t)

    t.phase("PLAN")
    t.info(f"legs to run, in order: {' → '.join(legs)}")
    if dry:
        t.ok("DRY-RUN — plan only. No legs executed, nothing rendered, no cost.")
        t.info("(Legs are not wired yet — this is the skeleton. Next build steps add them.)")
    else:
        t.warn("LIVE mode selected, but legs are not wired in the skeleton yet — "
               "nothing to execute. Build steps 3-5 add the real legs.")

    t.phase("RUN SUMMARY")
    t.info(f"channel {channel} · {project}")
    t.info(f"beats {n} (A:{n_a} B:{n_b}) · legs planned: {', '.join(legs)}")
    t.ok("skeleton run complete — the machine speaks. ✦")


if __name__ == "__main__":
    main()
