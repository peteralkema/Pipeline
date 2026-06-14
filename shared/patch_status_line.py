#!/usr/bin/env python3
"""
patch_status_line.py — live status line in the Mission Control strip (item 1a).

WHY
  The strip shows a bare phase name ("phase: running" / "phase: animating") with
  no sign of whether work is happening or how far along — this is what made the
  audio gate read as "hung" for 30 min and gate_stills look broken. We rejected a
  scrolling log; this is the right thing: ONE live line, activity + count, counted
  off disk. No logging, no orchestrate changes.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  1. build_state(): compute state["status_detail"] for the active job:
       - clips on disk vs beat total while animating        -> "clips 38 / 132"
       - stills on disk vs beat total while stills generate  -> "stills 47 / 132"
       - elapsed minutes for phases with no countable artifact (audio leg, assemble)
         -> "working 6m"  (uses rec heartbeat if present, else started_at)
     Path resolution reuses resolve_paths(); the beat total comes from durations.json
     (defensive: tries the resolve_paths key, then walks the project root). All wrapped
     so a miss degrades to "" or a bare count and can NEVER crash build_state.
  2. updateStrip(): append status_detail to the existing stripsub line, in place
     (A0 shell rule — no layout change, no new element).

  HONEST SCOPE: the audio leg is one long Inworld pass and assemble is one ffmpeg
  pass — nothing per-beat to count — so those show elapsed time, not a fake count.
  (A1 heartbeat ships next and upgrades the elapsed source; this reads started_at
  until then.)

DISCIPLINE
  Idempotent (sentinel: `def _status_detail`). Two anchors verified once; backs up
  to .pre_statusline; re-compiles + rolls back on failure. Run from repo root on the
  LAPTOP, then commit/push, then pull + restart + node-check on box.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "def _status_detail"

# ---- edit 1: add the helper + call it in build_state ----------------------
# Anchor: the build_state body from the view-attach block through the return.
OLD_STATE = '''    # Once stills exist, attach the beats view so the body can render (2b/3 use it).
    if phase in ("gate_stills", "animating", "assembling", "done"):
        try:
            state["view"] = build_beats_view(rec["channel"], rec["project"], _REPO)
        except Exception as e:
            state["view_error"] = str(e)
    return state'''

NEW_STATE = '''    # Once stills exist, attach the beats view so the body can render (2b/3 use it).
    if phase in ("gate_stills", "animating", "assembling", "done"):
        try:
            state["view"] = build_beats_view(rec["channel"], rec["project"], _REPO)
        except Exception as e:
            state["view_error"] = str(e)
    # Live status detail (item 1a): activity + count off disk, or elapsed time.
    try:
        state["status_detail"] = _status_detail(rec, phase)
    except Exception:
        state["status_detail"] = ""
    return state


def _beat_total(paths: dict) -> int:
    """Beat total from durations.json (the timing source). 0 if not found yet."""
    cand = []
    d = paths.get("durations")
    if d:
        cand.append(Path(d))
    # fall back to walking the project root (stills_dir = <project>/modea/stills)
    try:
        root = Path(paths["stills_dir"]).parent.parent
        cand.append(root / "durations.json")
    except Exception:
        pass
    for p in cand:
        try:
            if p and Path(p).exists():
                data = json.load(open(p))
                return len(data) if isinstance(data, (dict, list)) else 0
        except Exception:
            continue
    return 0


def _count_pngs(d) -> int:
    try:
        return sum(1 for _ in Path(d).glob("shot_*.png"))
    except Exception:
        return 0


def _count_mp4s(d) -> int:
    try:
        return sum(1 for _ in Path(d).glob("shot_*.mp4"))
    except Exception:
        return 0


def _elapsed_str(rec: dict) -> str:
    """Elapsed since heartbeat (A1, when present) else started_at."""
    t0 = rec.get("heartbeat") or rec.get("started_at")
    if not t0:
        return ""
    secs = max(0, int(time.time() - float(t0)))
    if secs < 60:
        return f"{secs}s"
    return f"{secs // 60}m"


def _status_detail(rec: dict, phase: str) -> str:
    """One short line: count where artifacts exist, elapsed time where they don't."""
    ch, pr = rec.get("channel"), rec.get("project")
    if not ch or not pr:
        return ""
    try:
        paths = resolve_paths(ch, pr, _REPO)
    except Exception:
        return ""
    total = _beat_total(paths)
    den = f" / {total}" if total else ""

    if phase == "animating":
        return f"clips {_count_mp4s(paths.get('clips_dir'))}{den}"
    if phase == "gate_stills":
        return f"stills {_count_pngs(paths.get('stills_dir'))}{den} ready"
    if phase == "running":
        # running covers the audio leg (no countable artifact yet) AND stills generation.
        # durations.json existing => audio leg done => we're generating stills.
        if total:
            return f"stills {_count_pngs(paths.get('stills_dir'))}{den}"
        e = _elapsed_str(rec)
        return f"audio · working {e}" if e else "audio · working"
    if phase == "assembling":
        e = _elapsed_str(rec)
        return f"assembling {e}" if e else "assembling"
    return ""'''

# ---- edit 2: render status_detail on the strip sub-line --------------------
OLD_STRIP = '''  if (sub) {
    sub.textContent = state.job_id
      ? ((state.channel || "") + " · " + (state.project || "") + "  ·  phase: " + state.phase)
      : "";
  }'''

NEW_STRIP = '''  if (sub) {
    if (state.job_id) {
      var base = (state.channel || "") + " · " + (state.project || "") + "  ·  phase: " + state.phase;
      var det = state.status_detail || "";
      sub.textContent = det ? (base + "  ·  " + det) : base;
    } else {
      sub.textContent = "";
    }
  }'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found — run from the repo root on the laptop.")
    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) — no changes made.")
        return

    for label, old in [("build_state", OLD_STATE), ("updateStrip sub", OLD_STRIP)]:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) — ambiguous; nothing written.")

    new = src.replace(OLD_STATE, NEW_STATE).replace(OLD_STRIP, NEW_STRIP)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_statusline")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    if MARKER not in chk or "state.status_detail" not in chk:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed — restored from backup.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile — restored from backup.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   strip sub-line now shows: clips N/total (animating), stills N/total")
    print("   (gate_stills + running), elapsed time (audio + assembling)")
    print()
    print("AFTER you pull on the box, restart + node-check:")
    print("   systemctl --user restart mission-control.service")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   print(\"script blocks:\", len(b))")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")


if __name__ == "__main__":
    main()
