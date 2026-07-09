#!/usr/bin/env python3
"""
wordless_leg.py — the audio leg's sibling for WORDLESS-SPINE channels.

Runs INSTEAD of audio_leg.py when channel.json declares `timing_source: "beatsheet"`.
Same contract, same altitude, same philosophy: SHELL OUT to proven black boxes, never
reimplement them. The orchestrator calls run_wordless_leg(ctx) and gets back the same
two artifacts every downstream leg already expects:

    <project>/durations.json   per-beat timing + structure
    <project>/voiceover.mp3    one full-length track (silence + VO clips at timecodes)

After this leg, NOTHING downstream knows anything unusual happened. Mode A, Mode B and
convergence run unchanged; assemble_episode.py mixes its own music bed under the track.

WHY IT EXISTS
-------------
The standard leg is four steps and enforces the continuous-narration doctrine:
    2a build_audio_script.py   -> full read + manifest   (a wordless beat is an ERROR here)
    2b generate_episode_vo.py  -> one voice, one read
       whisper                 -> measure the words
    2c build_beat_durations.py -> durations FROM the measured words

A wordless channel has no continuous read to measure. Its timing is DECLARED in the
beat-sheet and its VO is a sparse, removable layer. So this leg is two steps, and it
skips the two slowest ones (Whisper alone is a 3–5 minute tax on the box):

    W1 generate_twovoice_vo.py  -> one clip per spoken beat, per-character voice
    W2 build_wordless_audio.py  -> durations.json + the full-length voiceover.mp3

Script-is-king is preserved: the script is still the sole source of truth AND of timing.
Only WHERE the timing lives has changed — declared per beat rather than measured from
narration. durations.json remains the single timing+structure source.

CHANNEL-AGNOSTIC: nothing here names a channel. Any channel with
`timing_source: "beatsheet"` + an `elevenlabs_voices` map uses this leg.
"""
import os, sys, subprocess
from pathlib import Path


def _run(cmd, t, label, cwd=None, dry_run=False, stream=False):
    """Run a subprocess at orchestrator altitude — mirrors audio_leg._run.

    Captured for fast steps; streamed for long ones so the screen never goes silent
    (a step that can run >~10s MUST stream or heartbeat; silence reads as death).
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

    import time, threading
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    start = time.time()
    last_line = [start]
    stop = threading.Event()

    def heartbeat():
        while not stop.wait(15):
            if time.time() - last_line[0] >= 15:
                el = int(time.time() - start)
                t.step_progress(f"still working ({label}, {el//60}:{el%60:02d})")
    hb = threading.Thread(target=heartbeat, daemon=True); hb.start()

    for line in proc.stdout:
        line = line.rstrip()
        if line:
            t.detail(line)
            last_line[0] = time.time()
    proc.wait()
    stop.set()
    if proc.returncode != 0:
        t.halt(f"{label} failed (exit {proc.returncode}).")
        return False
    return True


def run_wordless_leg(ctx):
    """ctx: same keys as run_audio_leg — t, shared, channel_dir, project_dir,
    beats_list_json, dry_run, py. Returns dict of artifact paths, or None on halt."""
    t = ctx["t"]
    shared = ctx["shared"]
    proj = Path(ctx["project_dir"])
    py = ctx.get("py", sys.executable)
    dry = ctx["dry_run"]
    channel_dir = ctx.get("channel_dir") or "."
    beats_json = ctx["beats_list_json"]

    channel_cfg = Path(channel_dir) / "channel.json"

    t.phase("WORDLESS LEG")
    t.decision("timing_source=beatsheet — timing is DECLARED in the beat-sheet, not "
               "measured from narration. VO is a sparse, removable layer.")
    t.decision("no build_audio_script (its no-silence doctrine does not apply here); "
               "no Whisper (nothing to measure) — this leg is two steps, not four.")

    vo_map    = proj / "vo_map.json"
    durations = proj / "durations.json"
    voiceover = proj / "voiceover.mp3"

    # W1 — one clip per spoken beat, routed to its character's voice
    t.info("W1 · rendering per-character VO clips (ElevenLabs; silent beats are legal)")
    if not _run([py, str(Path(shared) / "generate_twovoice_vo.py"),
                 "--beats", str(beats_json),
                 "--project", str(proj),
                 "--channel-config", str(channel_cfg),
                 "--shared", str(shared)],
                t, "generate_twovoice_vo (W1)", dry_run=dry, stream=True):
        return None

    if not dry and vo_map.exists():
        import json
        vm = json.loads(vo_map.read_text(encoding="utf-8"))
        speakers = sorted({v["speaker"] for v in vm.values()})
        total = sum(v["duration"] for v in vm.values())
        t.ok(f"W1 · {len(vm)} VO clip(s) · voices: {', '.join(speakers) or '(none)'} "
             f"· {total:.1f}s of speech")

    # W2 — declared durations + the full-length voice track (silence + clips at timecodes)
    t.info("W2 · writing durations.json and laying VO clips onto the voice track")
    cmd = [py, str(Path(shared) / "build_wordless_audio.py"),
           "--beats", str(beats_json),
           "--project", str(proj),
           "--channel-config", str(channel_cfg)]
    if not dry and vo_map.exists():
        cmd += ["--vo-map", str(vo_map)]
    if not _run(cmd, t, "build_wordless_audio (W2)", dry_run=dry):
        return None

    if not dry:
        if not durations.exists() or not voiceover.exists():
            t.halt("wordless leg produced no durations.json / voiceover.mp3 — "
                   "downstream legs cannot run.")
            return None
        import json
        d = json.loads(durations.read_text(encoding="utf-8"))
        bad = [k for k, v in d.items()
               if v.get("source") == "no_narration" or float(v.get("duration", 0)) <= 0]
        if bad:
            t.halt(f"{len(bad)} beat(s) would be DROPPED by assemble_episode.py "
                   f"(zero duration or no_narration source): {bad[:6]}")
            return None
        total = sum(float(v["duration"]) for v in d.values())
        t.ok(f"W2 · {len(d)} beats · {total:.1f}s ({total/60:.1f} min) · "
             f"voiceover.mp3 {voiceover.stat().st_size/1_000_000:.1f} MB")
        t.decision("convergence point reached — durations.json + voiceover.mp3 are "
                   "ordinary artifacts; every downstream leg is unchanged.")

    return {
        "durations": str(durations),
        "voiceover": str(voiceover),
        "vo_map": str(vo_map),
    }
