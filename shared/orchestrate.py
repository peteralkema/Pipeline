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
import audio_leg
import modeb_leg
import modea_leg
import convergence_leg


def parse_args():
    ap = argparse.ArgumentParser(description="Peter's Pipeline Orchestrator v1.0")
    ap.add_argument("--project", help="project name (beats default: projects/<p>/beats.json)")
    ap.add_argument("--beats", default=None, help="explicit beats.json path")
    ap.add_argument("--log", choices=["quiet", "normal", "verbose"], default=None,
                    help="verbosity (skips the kickoff prompt if given)")
    ap.add_argument("--dry-run", action="store_true", help="plan only, render nothing")
    ap.add_argument("--live", action="store_true", help="actually run (skips kickoff prompt if given)")
    ap.add_argument("--gate-mode", choices=["cli", "job"], default="cli",
                    help="cli = terminal input() gates (default, unchanged); "
                         "job = drive gates via the job record (Mission Control)")
    ap.add_argument("--job-id", default=None,
                    help="job record id (Mission Control passes this; manual runs mint one)")
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
        # from repo root we don't yet know the channel (it's in the header), so search
        # each channel's projects/<project>/ for the wrapper. Explicit --beats avoids this.
        import glob as _glob
        for name in ("beats_full.json", "beats.json"):
            hits = _glob.glob(os.path.join("*", "projects", args.project, name))
            if hits:
                return hits[0]
        return None
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


def load_resolved_config(channel, project, t):
    """Resolve identity from the channel NAME (declared in the script header), so you
    run from the repo root and NEVER think about which folder you're in. The header is
    the single source of truth for which channel; the machine finds <channel>/channel.json
    by name. Then resolve <project>/look.json override ON TOP (channel defaults ->
    project overrides; most channels have none, Lazarus is built on it).
    Returns (cfg, channel_dir) or (None, None)."""
    if not channel:
        return None, None
    # Channel NAME (header / channel.json) uses underscores; the FOLDER on disk uses
    # hyphens (final_hours -> final-hours/, synthetic_press -> synthetic/ via alias).
    # Try the name as-given, then the '-'/'_' swaps, and use whichever folder has a
    # channel.json. (channel-agnostic: you never think about which spelling you used.)
    candidates = []
    for cand in (channel, channel.replace("_", "-"), channel.replace("-", "_")):
        if cand not in candidates:
            candidates.append(cand)
    channel_dir = None
    cfg_path = None
    for cand in candidates:
        p = os.path.join(cand, "channel.json")
        if os.path.exists(p):
            channel_dir, cfg_path = cand, p
            break
    if cfg_path is None:
        # tolerate being run from inside the channel folder too (./channel.json)
        if os.path.exists("channel.json"):
            cfg_path, channel_dir = "channel.json", "."
        else:
            t.warn(f"channel.json not found for '{channel}' "
                   f"(tried {', '.join(c + '/channel.json' for c in candidates)} from repo root). "
                   f"Run from ~/Pipeline, or check the channel name in the script header.")
            return None, None
    try:
        cfg = json.load(open(cfg_path, encoding="utf-8"))
    except Exception as e:
        t.halt(f"channel.json did not parse: {e}")
        sys.exit(1)
    # per-film look override (Lazarus): <channel>/projects/<project>/look.json on top
    if project:
        look_path = os.path.join(channel_dir, "projects", project, "look.json")
        if os.path.exists(look_path):
            try:
                look = json.load(open(look_path, encoding="utf-8"))
                cfg = {**cfg, **look}  # project overrides channel defaults
                t.ok(f"per-film look override applied → {look_path}")
            except Exception as e:
                t.warn(f"look.json present but did not parse ({e}); using channel defaults")
    voice = cfg.get("voices", {}).get("narrator", cfg.get("voice_id", "?"))
    t.ok(f"channel identity loaded → {cfg_path} (voice={voice}, "
         f"{cfg.get('width','?')}x{cfg.get('height','?')})")
    return cfg, channel_dir


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
    cfg, channel_dir = load_resolved_config(header.get("channel"), args.project, t)
    if cfg is None:
        t.warn("proceeding without resolved channel identity (skeleton tolerates it; "
               "legs will require it).")
    else:
        t.info(f"channel folder → {channel_dir}/  (legs will run here; you stay in repo root)")

    t.phase("DECIDE LEGS (composition scan)")
    legs, modes = decide_legs(beats, t)

    t.phase("PLAN")
    t.info(f"legs to run, in order: {' → '.join(legs)}")

    # Build the run context the legs receive.
    shared_dir = os.path.dirname(os.path.abspath(__file__))
    # resolve project dir under the channel folder; need the flat beats list for leg tools
    proj_dir = None
    if channel_dir and args.project:
        proj_dir = os.path.join(channel_dir, "projects", args.project)
    # the flat beats list (leg tools expect a list, not the wrapper) — write it next to the wrapper
    beats_list_json = None
    if proj_dir:
        os.makedirs(proj_dir, exist_ok=True)
        beats_list_json = os.path.join(proj_dir, "beats.json")
        # always write it (cheap local file; legs read it to plan, even in dry-run)
        with open(beats_list_json, "w", encoding="utf-8") as f:
            json.dump(beats, f, indent=2, ensure_ascii=False)
        t.detail(f"wrote flat beats list for leg tools → {beats_list_json}")

    import time as _time
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
        from gate_protocol import init_job, set_phase
        init_job(_job_id, channel, args.project, ctx["repo_root"])
        t.info(f"gate-mode=job · job_id={_job_id}")

    # ── 3a: AUDIO LEG (wired) ─────────────────────────────────────────────
    if "audio" in legs:
        if proj_dir is None:
            t.halt("cannot run audio leg — channel/project unresolved (need channel.json + --project).")
            sys.exit(1)
        result = audio_leg.run_audio_leg(ctx)
        if result is None:
            t.halt("audio leg halted. Fix the reported issue and re-run.")
            sys.exit(1)

    # ── 3b: MODE B LEG (render) + MODE B GATE — both live in modeb_leg.py ──
    if "modeB" in legs:
        mb = modeb_leg.run_modeb_leg(ctx)
        if mb is None:
            t.halt("Mode B leg halted. Fix the reported issue and re-run.")
            sys.exit(1)
        modeb_leg.modeb_gate(ctx, mb["count"])

    # ── 3c: MODE A LEG (stills → gate → animate-only) — lives in modea_leg.py ──
    if "modeA" in legs:
        if proj_dir is None:
            t.halt("cannot run Mode A leg — channel/project unresolved (need channel.json + --project).")
            sys.exit(1)
        ma = modea_leg.run_modea_leg(ctx)
        if ma is None:
            t.halt("Mode A leg halted. Fix the reported issue and re-run.")
            sys.exit(1)
    else:
        ma = None

    # ── 3d: CONVERGENCE LEG (pool clips → assemble → final_video) — convergence_leg.py ──
    if "convergence" in legs:
        if ctx["gate_mode"] == "job":
            set_phase(_job_id, "assembling", ctx["repo_root"])
        cv = convergence_leg.run_convergence_leg(ctx, ma)
        if cv is None:
            t.halt("convergence leg halted. Fix the reported issue and re-run.")
            sys.exit(1)

    # ── legs not yet wired (step 5) ───────────────────────────────────────
    pending = [l for l in legs if l not in ("audio", "modeB", "modeA", "convergence")]
    if pending:
        t.phase("LEGS NOT YET WIRED")
        for l in pending:
            t.info(f"· {l} — wiring is a later build step (5 convergence; lip-sync future)")

    t.phase("RUN SUMMARY")
    t.info(f"channel {channel} · {project}")
    t.info(f"beats {n} (A:{n_a} B:{n_b}) · legs planned: {', '.join(legs)}")
    if "audio" in legs and not dry:
        t.ok("audio leg complete — voiceover + real per-beat durations produced.")
    if ctx["gate_mode"] == "job":
        set_phase(_job_id, "done", ctx["repo_root"])
    t.ok("run complete. ✦")


if __name__ == "__main__":
    main()
