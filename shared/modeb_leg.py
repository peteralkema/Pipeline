#!/usr/bin/env python3
"""
modeb_leg.py — the Mode B render leg, wired for the orchestrator. ONE home for Mode B.

Half 1 of step 3b: render. Calls the PROVEN dispatch.py to render the Mode B beats
(Remotion motion-graphics cards), now fed the REAL durations.json from the audio leg
so each card renders at its measured frame count (no more word-count proxy).

Half 2 (the autoplay/live-edit gate) is built next, as its own piece.

Like every leg: shells out to the proven script (dispatch.py), does not reimplement it.
The orchestrator calls run_modeb_leg(ctx).
"""
import os, sys, re, json, subprocess
from pathlib import Path


def _stream(cmd, t, label, cwd=None):
    """Run with live child stdout + heartbeat (same liveness discipline as the audio leg:
    a render leg can run minutes; silence reads as death)."""
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
                t.step_progress(f"still rendering ({label}, {el//60}:{el%60:02d})")
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


def run_modeb_leg(ctx):
    """ctx: t, shared, project_dir, beats_list_json, durations(path), dry_run, py.
    Returns dict of rendered clip info, or None on halt."""
    t = ctx["t"]
    shared = ctx["shared"]
    proj = Path(ctx["project_dir"])
    py = ctx.get("py", sys.executable)
    dry = ctx["dry_run"]
    beats_json = ctx["beats_list_json"]
    durations = ctx.get("durations") or str(proj / "durations.json")

    t.phase("MODE B LEG")

    # which beats are Mode B? compute their indices for --only
    beats = json.load(open(beats_json, encoding="utf-8"))
    b_idx = [b["index"] for b in beats if b.get("mode") == "B" and b.get("component")]
    if not b_idx:
        t.info("no Mode B beats — leg is a no-op")
        return {"clips": [], "count": 0}

    t.decision(f"{len(b_idx)} Mode B beats → rendering with REAL durations "
               f"(measured frames, not the proxy)")
    if not os.path.exists(durations):
        t.warn(f"durations.json not found at {durations} — Mode B would render at "
               f"proxy lengths. Run the audio leg first.")

    # verify Remotion is runnable: REMOTION_DIR must be set and point at a real project.
    remotion_dir = os.environ.get("REMOTION_DIR")
    if not dry:
        if not remotion_dir or not os.path.isdir(remotion_dir):
            t.halt(f"REMOTION_DIR not set or not a directory (got: {remotion_dir!r}). "
                   f"On the box: export REMOTION_DIR=$HOME/Pipeline/remotion "
                   f"(and add it to ~/.bashrc). Mode B renders there.")
            return None
        t.detail(f"REMOTION_DIR = {remotion_dir}")

    only = ",".join(str(i) for i in b_idx)
    cmd = [py, str(Path(shared) / "dispatch.py"), beats_json,
           "--render", "--only", only, "--durations", durations]

    if dry:
        t.info(f"[dry-run] would render {len(b_idx)} Mode B clips: beats {b_idx}")
        t.detail(f"$ {' '.join(cmd)}")
        if remotion_dir:
            t.detail(f"REMOTION_DIR = {remotion_dir}")
        return {"clips": [], "count": len(b_idx), "dry": True}

    t.info(f"rendering {len(b_idx)} Mode B clips via Remotion (measured durations)")
    if not _stream(cmd, t, "dispatch Mode B render", cwd=ctx.get("run_cwd")):
        return None

    # collect what landed — clips may go to <proj>/clips OR the engine's default clips/ dir
    search_dirs = [proj / "clips", Path("clips"), Path(ctx.get("run_cwd") or ".") / "clips"]
    rendered = []
    for d in search_dirs:
        if d.exists():
            rendered += [str(p) for p in d.glob("beat_*_B*.mp4")]
    rendered = sorted(set(rendered))

    # HALT-ON-MISSING-OUTPUT (§12): figure out WHICH beats are missing and report precisely.
    expected = len(b_idx)
    got_indices = set()
    for p in rendered:
        m = re.search(r"beat_(\d+)_B", os.path.basename(p))
        if m:
            got_indices.add(int(m.group(1)))
    missing = [i for i in b_idx if i not in got_indices]

    if len(rendered) == 0:
        t.halt("Mode B rendered 0 clips. Likely Node/Remotion not runnable here: check "
               "'npx not found' in the log, REMOTION_DIR, and `npx remotion versions`.")
        return None

    if missing:
        # SOME rendered — Node is clearly fine. Name the specific failures.
        t.warn(f"Mode B rendered {len(rendered)}/{expected} — these beats FAILED: {missing}")
        t.halt(f"beats {missing} did not render (the other {len(rendered)} did, so Node/Remotion "
               f"work). Render one directly to see its real error, e.g.:\n"
               f"    cd $REMOTION_DIR && npx remotion render <Component> /tmp/x.mp4 "
               f"--props='<json>' --frames=0-<n>\n"
               f"Common causes: a very long frame count (a card given a long spoken duration), "
               f"or a component prop it can't handle. Fix, then re-run.")
        return None

    t.ok(f"Mode B render complete → {len(rendered)} clips")
    for p in rendered[:6]:
        t.detail(os.path.basename(p))
    return {"clips": rendered, "count": len(rendered), "indices": b_idx}


def modeb_gate(ctx, rendered_count):
    """The Mode B gate: print DEAD-SIMPLE, copy-paste, which-window-labelled instructions
    to get the autoplay/live-edit review page up, then wait for the user to finish.
    Two terminals are unavoidable (box serves, laptop tunnels) — so we make BOTH blocks
    fully pre-filled and labelled. Assume the user remembers nothing."""
    t = ctx["t"]
    proj = ctx["project_dir"]
    shared = ctx["shared"]
    beats = ctx["beats_list_json"]
    durations = ctx.get("durations") or ""
    clips = ctx.get("clips_dir") or os.path.join(os.path.dirname(shared), "clips")
    box = ctx.get("box", "peter@116.202.18.68")
    port = ctx.get("review_port", 8000)
    dur_arg = f" --durations {durations}" if durations else ""

    t.gate("MODE B GATE — review the cards")
    print(f"""
  ┌─ MODE B REVIEW — 3 steps, copy-paste each block ──────────────────────┐
  │                                                                        │
  │  STEP 1 ▸ In your BOX window (prompt: peter@pipeline-prod), paste:     │
  │                                                                        │
        source ~/venvs/pipeline/bin/activate
        export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
        python {shared}/serve_modeb_review.py --project {proj} --beats {beats} --clips {clips}{dur_arg} --port {port}
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
  │  Scroll top→bottom. Clips autoplay. Edit a payload + click            │
  │  "Re-render this beat" to fix. Click "Flag" if a beat is wrong in     │
  │  a way you can't fix here (audio-affecting / bug).                     │
  │                                                                        │
  │  When done: Ctrl-C the BOX server, then come back HERE and type go.   │
  └────────────────────────────────────────────────────────────────────────┘
  ({rendered_count} cards rendered and waiting in the review page.)""")
    if ctx["dry_run"]:
        t.info("[dry-run] Mode B gate would wait for review here.")
        return True
    while True:
        ans = input("  >>> type 'go' when you've finished reviewing (or 'skip'): ").strip().lower()
        if ans in ("go", "skip"):
            t.ok(f"Mode B gate cleared ({ans}).")
            return True
