#!/usr/bin/env python3
"""
modea_leg.py — the Mode A leg (cinematic recreation). ONE home for Mode A.

Step 4. Three phases, all living here (one home, one job):
  stills   run_modea_leg → translate Synthetic beats to the engine's --beats format
           (modea_beats.py, PROVEN) + write _index.json shot→beat map, then run
           recreation_pipeline.py stills to generate storyboard + all stills.
  GATE     modea_gate → the stills review (the heavy aesthetic firewall). Reuses v1's
           serve_review.py ergonomics. Restill the spell-breakers, then continue.
  animate  recreation_pipeline.py --animate-only → animate the REVIEWED stills into
           per-shot clips via Kling. NO narrate, NO score, NO assemble — audio is its
           own leg and assembly belongs to convergence (the dual-mode assembler).

Like every leg: shells out to the PROVEN scripts; does not reimplement them. The
orchestrator calls run_modea_leg(ctx).

──────────────────────── EXTERNAL CONTRACT — READ BEFORE THE FIRST BOX RUN ─────────────
This leg shells to four things. The commands below are what the leg sends. If the real
scripts differ, fix it HERE (one home) — do NOT bend the proven scripts to the leg.
Each is gathered into one helper so there's a single line to reconcile.

  1. modea_beats.py        translate + index map (CONFIRMED against the box). Leg sends:
        python modea_beats.py <beats_list_json> --out <engine_beats.json> --map <index.json>
        Real CLI: positional beats_json, --out (default synthetic_modeA_beats.json),
        --map (default <out stem>_index.json). We pass --map explicitly so the leg
        controls the index path it later hands to convergence. No reconcile needed.
  2. recreation_pipeline.py stills    CONFIRMED by PIPELINE_PLAYBOOK Step 9 + 30-May ref:
        python recreation_pipeline.py stills --project <engine_project> --beats <engine_beats.json>
        Flag order is irrelevant; this form is exact. No reconcile needed.
  3. recreation_pipeline.py finish --animate-only   NEW SEAM — does NOT exist yet.
        python recreation_pipeline.py finish --project <engine_project> --animate-only
        Semantics: animate existing stills → clips, then STOP. No voiceover, no music,
        no assemble. PRECEDENT: cmd_finish already carries `--assemble-only` (re-stitch
        existing clips, skip animate/narrate/score) — confirmed in the real source. So
        `--animate-only` is its mirror: run ONLY animate, return before narrate/score/
        assemble. Ship that engine patch alongside (the one real engine change Mode A needs).
  4. serve_review.py       CONFIRMED against the box. Gate prints:
        python serve_review.py --project <engine_project> --port <port>
        Real CLI: --project (required), --beats (optional), --port (default 8000),
        --model (default flux). Our --project/--port form is exact. No reconcile needed.

ctx keys used: t, shared, project_dir, beats_list_json, dry_run, py, run_cwd, box,
               modea_port, engine_project (optional), engine_cwd (optional).
─────────────────────────────────────────────────────────────────────────────────────
"""
import os, sys, re, json, subprocess
from pathlib import Path


def _stream(cmd, t, label, cwd=None):
    """Run with live child stdout + 15s heartbeat (same liveness discipline as every
    long leg: a stills/animation run can take many minutes; silence reads as death).
    (Kept local to match the per-leg pattern; wants to become shared/proc.py one day.)"""
    import time, threading
    t.detail(f"$ {' '.join(str(c) for c in cmd)}  (cwd={cwd or '.'})")
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1,
                            env=os.environ.copy())
    start = time.time(); last = [start]; stop = threading.Event()
    def hb():
        while not stop.wait(15):
            if time.time() - last[0] >= 15:
                el = int(time.time() - start)
                t.step_progress(f"still working ({label}, {el//60}:{el%60:02d})")
    threading.Thread(target=hb, daemon=True).start()
    for line in proc.stdout:
        line = line.rstrip()
        if line:
            t.detail(line); last[0] = time.time()
    proc.wait(); stop.set()
    if proc.returncode != 0:
        t.halt(f"{label} failed (exit {proc.returncode}).")
        return False
    return True


def _engine_project(ctx):
    """Where the engine works. The engine takes a project NAME and writes <name>/stills,
    <name>/clips, <name>/storyboard.json. Default: a 'modea' subfolder of the Synthetic
    project so Mode A artifacts don't collide with Mode B's clips/. Override via
    ctx['engine_project']. engine_cwd is where that name is rooted (default run_cwd)."""
    proj = Path(ctx["project_dir"])
    name = ctx.get("engine_project") or os.path.join(os.path.basename(str(proj)), "modea")
    cwd = ctx.get("engine_cwd") or ctx.get("run_cwd") or str(proj.parent)
    return name, cwd


def _collect(dirs, pattern):
    """Glob across candidate dirs, dedup by RESOLVED real path (never by string — the
    same physical dir can appear under relative + absolute forms; the Mode B leg learned
    this the hard way). Returns sorted real paths."""
    out, seen = [], set()
    for d in dirs:
        d = Path(d)
        if d.exists():
            for p in d.glob(pattern):
                rp = os.path.realpath(str(p))
                if rp not in seen:
                    seen.add(rp); out.append(rp)
    return sorted(out)


def _modea_indices(ctx):
    beats = json.load(open(ctx["beats_list_json"], encoding="utf-8"))
    return [b["index"] for b in beats if b.get("mode") == "A"]


def _translate(ctx, engine_beats, index_json):
    """Phase 1a: Synthetic beats → engine --beats format + _index.json (modea_beats.py)."""
    t = ctx["t"]; py = ctx.get("py", sys.executable)
    cmd = [py, str(Path(ctx["shared"]) / "modea_beats.py"), ctx["beats_list_json"],
           "--out", engine_beats, "--map", index_json]
    if ctx["dry_run"]:
        t.info("[dry-run] would translate Synthetic beats → engine format + write index")
        t.detail(f"$ {' '.join(cmd)}")
        return True
    t.info("translating Synthetic Mode A beats → engine --beats + shot→beat index")
    if not _stream(cmd, t, "modea_beats translate", cwd=ctx.get("run_cwd")):
        return False
    if not os.path.exists(engine_beats) or not os.path.exists(index_json):
        t.halt(f"translate ran but outputs missing (engine_beats={engine_beats}, "
               f"index={index_json}). Check modea_beats.py's --out/--map flags.")
        return False
    t.ok(f"translated → {os.path.basename(engine_beats)} + {os.path.basename(index_json)}")
    return True


def _stills(ctx, engine_project, engine_cwd, engine_beats, n_beats):
    """Phase 1b: engine stills generation. Returns count of stills, or None on halt."""
    t = ctx["t"]; py = ctx.get("py", sys.executable)
    cmd = [py, str(Path(ctx["shared"]) / "recreation_pipeline.py"), "stills",
           "--project", engine_project, "--beats", engine_beats]
    if ctx["dry_run"]:
        est = n_beats * 0.03  # ~$0.03/still (engine reference); a pre-run cost estimate
        t.info(f"[dry-run] would generate ~{n_beats} stills via the engine "
               f"(est. fal spend ≈ ${est:.2f})")
        t.detail(f"$ {' '.join(cmd)}  (cwd={engine_cwd})")
        return n_beats
    t.info(f"generating stills via recreation_pipeline.py (engine project '{engine_project}')")
    if not _stream(cmd, t, "engine stills", cwd=engine_cwd):
        return None
    stills_dir = Path(engine_cwd) / engine_project / "stills"
    stills = _collect([stills_dir], "*.png")
    if not stills:
        t.halt(f"engine produced 0 stills in {stills_dir}. Check the engine log above "
               f"(canon tag error? fal key? black-placeholder safety reject?).")
        return None
    t.ok(f"stills complete → {len(stills)} stills in {stills_dir}")
    return len(stills)


def _animate(ctx, engine_project, engine_cwd):
    """Phase 3: animate-only (NEW engine seam). Animate reviewed stills → per-shot clips,
    NO assemble. Returns list of clip paths, or None on halt."""
    t = ctx["t"]; py = ctx.get("py", sys.executable)
    cmd = [py, str(Path(ctx["shared"]) / "recreation_pipeline.py"), "finish",
           "--project", engine_project, "--animate-only"]
    if ctx["dry_run"]:
        t.info("[dry-run] would animate reviewed stills → per-shot clips (Kling), no assemble")
        t.detail(f"$ {' '.join(cmd)}  (cwd={engine_cwd})")
        return []
    t.info("animating reviewed stills → clips via Kling (--animate-only: no narrate/score/assemble)")
    if not _stream(cmd, t, "engine animate-only", cwd=engine_cwd):
        return None
    clips_dir = Path(engine_cwd) / engine_project / "clips"
    clips = _collect([clips_dir], "shot_*.mp4")
    if not clips:
        t.halt(f"animate-only produced 0 clips in {clips_dir}. If stills exist but clips "
               f"don't, check Kling (content-policy refusals should auto-fallback to held "
               f"clips — confirm --animate-only preserves that fallback).")
        return None
    t.ok(f"animate-only complete → {len(clips)} clips")
    for p in clips[:6]:
        t.detail(os.path.basename(p))
    return clips


def modea_gate(ctx, engine_project, engine_cwd, stills_count):
    """The Mode A gate — the stills review (heavy aesthetic firewall). Same idiot-proof,
    window-labelled, copy-paste shape as the Mode B gate; reuses v1's serve_review.py.
    Owns its own dry-run behaviour."""
    t = ctx["t"]
    shared = ctx["shared"]
    box = ctx.get("box", "peter@116.202.18.68")
    port = ctx.get("modea_port", 8001)  # 8001 so it never collides with Mode B's 8000
    stills_dir = os.path.join(engine_cwd, engine_project, "stills")

    t.gate("MODE A GATE — review the stills (the aesthetic firewall)")
    print(f"""
  ┌─ MODE A REVIEW — 3 steps, copy-paste each block ──────────────────────┐
  │                                                                        │
  │  STEP 1 ▸ In your BOX window (prompt: peter@pipeline-prod), paste:     │
  │                                                                        │
        source ~/venvs/pipeline/bin/activate
        python {os.path.join(shared, 'make_review_page.py')} --project {engine_project}
        python {os.path.join(shared, 'serve_review.py')} --project {engine_project} --port {port}
  │                                                                        │
  │  STEP 2 ▸ In your LAPTOP window (prompt: your-name@laptop), paste:     │
  │                                                                        │
        lsof -ti :{port} | xargs kill 2>/dev/null; true
        ssh -p 443 -L {port}:localhost:{port} {box}
  │                                                                        │
  │  STEP 3 ▸ Open this in your browser:                                   │
  │                                                                        │
        http://localhost:{port}
  │                                                                        │
  │  Scroll top→bottom. Spell-breakers (modern clothing, extra hands,      │
  │  illegible text, anachronisms) → edit the prompt + Restill. Three      │
  │  attempts max per shot, then reframe the concept rather than retry.    │
  │                                                                        │
  │  When done: Ctrl-C the BOX server, then come back HERE and type go.   │
  └────────────────────────────────────────────────────────────────────────┘
  ({stills_count} stills rendered and waiting in the review page.)
  (stills on the box at: {stills_dir})""")
    if ctx["dry_run"]:
        t.info("[dry-run] Mode A gate would wait for stills review here.")
        return True
    while True:
        ans = input("  >>> type 'go' when you've finished reviewing the stills (or 'skip'): ").strip().lower()
        if ans in ("go", "skip", "continue", "c", "done", "y", "yes"):
            t.ok(f"Mode A gate cleared ({ans}).")
            return True
        t.info("(type 'go' when the stills pass the aesthetic firewall)")


def run_modea_leg(ctx):
    """ctx: t, shared, project_dir, beats_list_json, dry_run, py, run_cwd.
    Drives stills → gate → animate-only. Returns dict of clips, or None on halt."""
    t = ctx["t"]
    proj = Path(ctx["project_dir"])

    t.phase("MODE A LEG")

    a_idx = _modea_indices(ctx)
    if not a_idx:
        t.info("no Mode A beats — leg is a no-op")
        return {"clips": [], "count": 0}
    t.decision(f"{len(a_idx)} Mode A beats → stills → review gate → animate-only")

    engine_project, engine_cwd = _engine_project(ctx)
    # absolute paths cross the cwd boundary safely: the engine runs in engine_cwd, not the
    # orchestrator's cwd, so a repo-root-relative path would not resolve there (§3 principle).
    engine_beats = os.path.abspath(str(proj / "engine_beats.json"))
    index_json = os.path.abspath(str(proj / "_index.json"))
    t.detail(f"engine project = {engine_project}  (cwd={engine_cwd})")

    # Phase 1a: translate Synthetic beats → engine format + shot→beat index
    if not _translate(ctx, engine_beats, index_json):
        return None

    # Phase 1b: stills
    stills_count = _stills(ctx, engine_project, engine_cwd, engine_beats, len(a_idx))
    if stills_count is None:
        return None

    # Phase 2: the aesthetic firewall
    modea_gate(ctx, engine_project, engine_cwd, stills_count)

    # Phase 3: animate-only
    clips = _animate(ctx, engine_project, engine_cwd)
    if clips is None:
        return None

    return {"clips": clips, "count": len(clips), "indices": a_idx,
            "index_json": index_json, "engine_project": engine_project,
            "engine_cwd": engine_cwd}
