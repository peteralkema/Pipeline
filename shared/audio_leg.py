#!/usr/bin/env python3
"""
audio_leg.py — the audio leg, wired for the orchestrator. ONE home for the audio spine.

Runs the proven 4-piece sequence, then presents the AUDIO GATE (keep/swap):
  2a build_audio_script.py  -> full read (.txt) + manifest (.manifest.json)
  2b generate_episode_vo.py -> voiceover.mp3   (Inworld Victor)
     whisper                -> voiceover.json   (word timestamps)
  2c build_beat_durations.py-> durations.json   (+ captions.srt, step 3a adds)
  AUDIO GATE: keep this Victor read, OR swap in a human recording (scp + re-whisper).

The orchestrator calls run_audio_leg(ctx). ctx carries channel_dir, project, paths,
the telemetry object, and dry_run. Everything is logged at orchestrator altitude.

This module SHELLS OUT to the existing proven scripts (does not reimplement them) —
same philosophy as every leg: the orchestrator sequences proven black boxes.
"""
import os, sys, subprocess
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mission_control"))
from gate_protocol import await_gate


def _run(cmd, t, label, cwd=None, dry_run=False, stream=False):
    """Run a subprocess at orchestrator altitude. Two modes:
      - captured (default): buffer output, surface at verbose, halt loudly on fail.
        Fine for FAST steps (2a, 2c).
      - stream=True: for LONG steps (2b Inworld, whisper) — let the child's stdout
        flow through live, line by line, so the screen never goes silent. A step that
        can run >~10s MUST stream or heartbeat; silence reads as death. (banked principle)
    """
    t.detail(f"$ {' '.join(str(c) for c in cmd)}  (cwd={cwd or '.'})")
    if dry_run:
        t.info(f"[dry-run] would run: {label}")
        return True

    if not stream:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if r.returncode != 0:
            tail = (r.stderr or r.stdout).strip().splitlines()
            t.halt(f"{label} failed (exit {r.returncode}): {tail[-1] if tail else '?'}")
            return False
        for line in (r.stdout or "").splitlines():
            t.detail(line)
        return True

    # streamed: live child output + heartbeat so long quiet stretches still pulse
    import time, threading
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    start = time.time()
    last_line = [start]
    stop = threading.Event()

    def heartbeat():
        while not stop.wait(15):
            quiet = time.time() - last_line[0]
            if quiet >= 15:
                el = int(time.time() - start)
                t.step_progress(f"still working ({label}, {el//60}:{el%60:02d})")
    hb = threading.Thread(target=heartbeat, daemon=True); hb.start()

    for line in proc.stdout:
        line = line.rstrip()
        if line:
            t.detail(line)          # the child narrates itself (chunk 1/6, whisper %, …)
            last_line[0] = time.time()
    proc.wait()
    stop.set()
    if proc.returncode != 0:
        t.halt(f"{label} failed (exit {proc.returncode}).")
        return False
    return True


def run_audio_leg(ctx):
    """ctx: dict with keys: t (Telemetry), shared (path to shared/), channel_dir,
    project_dir (abs), script_md, dry_run, py (python exe). Returns dict of artifact
    paths on success, or None on halt."""
    t = ctx["t"]
    shared = ctx["shared"]
    proj = Path(ctx["project_dir"])
    py = ctx.get("py", sys.executable)
    dry = ctx["dry_run"]

    t.phase("AUDIO LEG")
    t.decision("audio runs first — it is the timing source both render legs depend on")

    audio_txt = proj / "ep_audio.txt"
    manifest  = proj / "ep_audio.manifest.json"
    voiceover = proj / "voiceover.mp3"
    whisper_json = proj / "voiceover.json"
    durations = proj / "durations.json"
    beats_json = ctx["beats_list_json"]   # the flat list for the leg tools

    # 2a — assemble the full read + manifest
    t.info("2a · assembling full-episode narration (in beat order, incl. found-lines)")
    if not _run([py, str(Path(shared)/"build_audio_script.py"), str(beats_json),
                 "--out", str(proj/"ep_audio")], t, "build_audio_script (2a)", dry_run=dry):
        return None
    if not dry:
        words = len(Path(audio_txt).read_text(encoding="utf-8").split()) if audio_txt.exists() else 0
        t.ok(f"2a · narration assembled → {words} words")

    # 2b — generate Victor VO
    t.info("2b · generating Victor voiceover (Inworld)")
    if not _run([py, str(Path(shared)/"generate_episode_vo.py"),
                 "--text", str(audio_txt), "--project", str(proj),
                 "--shared", str(shared)], t, "generate_episode_vo (2b)", dry_run=dry, stream=True):
        return None
    if not dry and voiceover.exists():
        t.ok(f"2b · voiceover.mp3 → {voiceover.stat().st_size/1_000_000:.1f} MB")

    # whisper — measure it
    t.info("whisper · measuring real word timestamps (3-5 min on box)")
    if not _run(["whisper", str(voiceover), "--model", "small", "--output_format", "json",
                 "--output_dir", str(proj), "--word_timestamps", "True"],
                t, "whisper", dry_run=dry, stream=True):
        return None

    # 2c — build real per-beat durations (+ captions.srt in 3a extension)
    t.info("2c · building real per-beat durations from measured audio")
    if not _run([py, str(Path(shared)/"build_beat_durations.py"),
                 "--manifest", str(manifest), "--whisper", str(whisper_json),
                 "--out", str(durations),
                 "--aligner", str(Path(shared)/"align_with_whisper.py")],
                t, "build_beat_durations (2c)", dry_run=dry):
        return None
    if not dry and durations.exists():
        import json
        d = json.load(open(durations))
        total = sum(x["duration"] for x in d.values())
        measured = sum(1 for x in d.values() if x.get("source") == "whisper")
        t.ok(f"2c · durations.json → {len(d)} beats, {measured} measured, "
             f"{total:.0f}s ({total/60:.1f} min) total")

    # AUDIO GATE — keep or swap
    artifacts = {"voiceover": voiceover, "durations": durations,
                 "manifest": manifest, "whisper": whisper_json}
    return audio_gate(ctx, artifacts)


def audio_gate(ctx, artifacts):
    """KEEP the pipeline Victor read, or SWAP in a human recording (then re-whisper)."""
    t = ctx["t"]
    proj = Path(ctx["project_dir"])
    py = ctx.get("py", sys.executable)
    shared = ctx["shared"]
    dry = ctx["dry_run"]

    dur_min = "?"
    if artifacts["durations"].exists():
        import json
        d = json.load(open(artifacts["durations"]))
        dur_min = f"{sum(x['duration'] for x in d.values())/60:.1f}"

    # --- audio continuity QC (read-only; fails soft) -------------------
    if not dry:
        try:
            from audio_qc import audio_continuity_check
            _ok, _msg = audio_continuity_check(artifacts["whisper"])
            if _ok:
                t.ok(_msg)
            else:
                # loud, unmissable — a detected hole means re-run audio, not swap
                t.gate("AUDIO CONTINUITY WARNING")
                print("  !! " + _msg)
        except Exception as _e:
            t.info(f"continuity check unavailable ({_e}) — proceeding without it.")
    # -------------------------------------------------------------------
    t.gate("AUDIO GATE")
    box = ctx.get("box", "peter@116.202.18.68")
    print(f"""
  ┌─ AUDIO GATE ──────────────────────────────────────────────┐
  │ Pipeline produced voiceover.mp3 — measured {dur_min} min.
  │ [1] KEEP  — use this Victor read, carry on.
  │ [2] SWAP  — replace with your own (human) recording.
  └────────────────────────────────────────────────────────────┘""")
    if dry:
        t.info("[dry-run] audio gate would prompt KEEP/SWAP here.")
        return artifacts
    choice = await_gate(
        ctx, name="audio",
        payload={"voiceover": str(proj / "voiceover.mp3"),
                 "minutes": dur_min,
                 "voice_id": ctx.get("voice_id")},
        options=["keep", "swap"],
        cli_prompt="  >>> [1] keep / [2] swap: ",
        cli_map={"1": "keep", "2": "swap", "keep": "keep", "swap": "swap"},
        phase="gate_audio",
    )

    if choice == "swap":
        print(f"""
  SWAP — get your human recording onto the box. On your LAPTOP, paste:

    scp -P 443 ~/Downloads/voiceover.mp3 \\
      {box}:{(proj/'voiceover.mp3')}

  This OVERWRITES the Victor read. Then come back here.""")
        input("  >>> type ENTER once the human voiceover.mp3 is in place: ")
        # re-measure: whisper the human read, rebuild durations (timing carries through)
        t.info("re-measuring human audio — re-running whisper + rebuilding durations")
        if not _run(["whisper", str(proj/"voiceover.mp3"), "--model", "small",
                     "--output_format", "json", "--output_dir", str(proj),
                     "--word_timestamps", "True"], t, "whisper (human swap)", stream=True):
            return None
        if not _run([py, str(Path(shared)/"build_beat_durations.py"),
                     "--manifest", str(artifacts["manifest"]),
                     "--whisper", str(proj/"voiceover.json"),
                     "--out", str(artifacts["durations"]),
                     "--aligner", str(Path(shared)/"align_with_whisper.py")],
                    t, "build_beat_durations (human swap)"):
            return None
        t.ok("human audio measured → durations rebuilt. Timing now carries from the human read.")
    else:
        t.ok("KEEP — using the Victor read. Durations stand.")

    return artifacts
