#!/usr/bin/env python3
"""
convergence_leg.py — the convergence leg. ONE home for assembly.

After audio + Mode B + Mode A have produced their artifacts, convergence pools every
clip into one directory and shells out to the PROVEN assemble_episode.py to lay the
ONE continuous voiceover over the conformed video → final_video.mp4. VOICE WINS.

Same philosophy as every leg: the orchestrator sequences proven black boxes. This leg
does NOT reimplement assembly — it calls assemble_episode.py, which is already validated.

Inputs come from ctx (built by orchestrate.py) + the Mode A leg's return dict:
  ctx["project_dir"]   <channel>/projects/<project>   (durations.json, voiceover.mp3, final_video.mp4 live here)
  ctx["shared"]        shared/ (holds assemble_episode.py)
  ctx["py"]            python executable
  ctx["dry_run"]       plan-only
  modea["index_json"]      authoritative beat→shot index (Mode A leg wrote it)
  modea["engine_project"]  the Mode A engine project NAME (its clips are in <project_dir>/<that>/clips OR <engine_cwd>/<that>/clips)

Clip pooling:
  Mode A → <engine clips>/shot_NNN.mp4   (contiguous; index maps shot→beat)
  Mode B → <project_dir>/clips/beat_NN_B_<Component>.mp4   (named by beat)
  Both are copied into <project_dir>/clips/ (the pool assemble reads via --clips).
  Mode-A-only episodes simply have no Mode B clips — pooling tolerates that.

Music: OFF by default. ctx.get("music") is a hook for the Tier-2 step (Claude reads the
script → fal generates one loopable bed → <project_dir>/music.mp3). Until that ships,
convergence assembles with --no-music.

The orchestrator calls run_convergence_leg(ctx, modea_result).
"""
import os
import json
import sys
import shutil
import subprocess
from pathlib import Path


def _run(cmd, t, label, cwd=None, dry_run=False):
    """Run a subprocess at orchestrator altitude, streaming output (assemble can take
    a while: ffmpeg conform + concat + mux). Halt loudly on failure."""
    t.detail(f"$ {' '.join(str(c) for c in cmd)}  (cwd={cwd or '.'})")
    if dry_run:
        t.info(f"[dry-run] would run: {label}")
        return True
    import time, threading
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    start = time.time()
    last = [start]
    stop = threading.Event()

    def heartbeat():
        while not stop.wait(15):
            if time.time() - last[0] >= 15:
                el = int(time.time() - start)
                t.step_progress(f"still working ({label}, {el // 60}:{el % 60:02d})")
    hb = threading.Thread(target=heartbeat, daemon=True)
    hb.start()
    try:
        for line in proc.stdout:
            last[0] = time.time()
            t.detail(line.rstrip())
        proc.wait()
    finally:
        stop.set()
    if proc.returncode != 0:
        t.halt(f"{label} failed (exit {proc.returncode}).")
        return False
    return True


def _pool_clips(project_dir, engine_clips_dir, t, dry_run):
    """Copy Mode A shot_NNN.mp4 (from the engine clips dir) and Mode B beat_NN_B_*.mp4
    (already under <project_dir>/clips) into the single pool <project_dir>/clips/.
    Returns the pool dir path. Idempotent: re-copies (overwrites) so a re-run is clean."""
    pool = Path(project_dir) / "clips"
    if dry_run:
        t.info(f"[dry-run] would pool clips into {pool} "
               f"(Mode A from {engine_clips_dir}, Mode B already in place)")
        return pool
    pool.mkdir(parents=True, exist_ok=True)
    n_a, n_b = 0, 0
    # Mode A: shot_NNN.mp4 from the engine's clips dir (skip if the dir is the pool itself)
    ecd = Path(engine_clips_dir)
    if ecd.exists() and ecd.resolve() != pool.resolve():
        for f in sorted(ecd.glob("shot_*.mp4")):
            shutil.copy2(f, pool / f.name)
            n_a += 1
    # Mode B: beat_NN_B_*.mp4 — these are written under <project_dir>/clips already in our
    # hand-runs; if a separate Mode B dir is ever used, it would be pooled here too.
    n_b = len(list(pool.glob("beat_*_B_*.mp4")))
    t.ok(f"pooled clips → {pool}  (Mode A: {n_a} copied, Mode B: {n_b} present)")
    return pool


def _maybe_upload(ctx, proj, t, py, shared, dry):
    """Channel-agnostic publish: shell out to upload_episode.py (header = metadata,
    channel folder = identity). Batch-exit-gate and parts-skip live inside that script.
    An upload FAILURE never discards the finished video — warn and carry on."""
    up = Path(shared) / "upload_episode.py"
    if not up.exists():
        t.warn(f"upload step skipped — {up} not found (final_video.mp4 is safe; upload manually).")
        return
    if dry:
        t.info(f"[dry-run] would publish via upload_episode.py --project {proj} (private)")
        return
    if not _run([py, str(up), "--project", str(proj)], t, "upload_episode", cwd=None, dry_run=False):
        t.warn("upload failed — final_video.mp4 is complete and safe. Re-run:  "
               f"python shared/upload_episode.py --project {proj}")



def _maybe_thumbnail(ctx, proj, t, py, shared, dry):
    """Auto thumbnail before upload. If <proj>/thumbnail.json exists, generate
    candidate stills, let Sonnet pick the best on the CTR job, overlay the locked
    headline -> thumbnail.png (upload_episode.py attaches it). Graceful + idempotent:
    a missing spec or any failure ships final_video.mp4 + upload untouched; an existing
    thumbnail.png is left in place (no fal re-spend). channel.json look resolves by
    walk-up from the project dir, same pattern as look_resolver."""
    proj = Path(proj)
    spec_file = proj / "thumbnail.json"
    out_png = proj / "thumbnail.png"
    if out_png.exists():
        t.info(f"thumbnail.png present — skipping generation ({out_png})")
        return
    if not spec_file.exists():
        t.info("no thumbnail.json — skipping auto-thumbnail (upload ships without a custom one).")
        return
    if dry:
        t.info(f"[dry-run] would generate + select + overlay thumbnail from {spec_file}")
        return
    try:
        spec = json.loads(spec_file.read_text())
    except Exception as e:
        t.warn(f"thumbnail.json unreadable ({e}) — skipping thumbnail.")
        return
    subject = (spec.get("subject") or "").strip()
    title = (spec.get("title") or "").strip()
    subtitle = (spec.get("subtitle") or "").strip()
    if not subject or not title:
        t.warn("thumbnail.json missing 'subject' or 'title' — skipping thumbnail.")
        return
    sel = Path(shared) / "select_thumbnail_still.py"
    mk = Path(shared) / "make_thumbnail.py"
    if not sel.exists() or not mk.exists():
        t.warn("select_thumbnail_still.py / make_thumbnail.py missing — skipping thumbnail.")
        return
    # 1) generate candidates + Sonnet-select -> <proj>/thumbnail_still.png
    if not _run([py, str(sel), "--project", str(proj), "--subject", subject],
                t, "select_thumbnail_still", cwd=None, dry_run=False):
        t.warn("thumbnail selection failed — shipping without a custom thumbnail.")
        return
    still = proj / "thumbnail_still.png"
    if not still.exists():
        t.warn("thumbnail_still.png not produced — skipping overlay.")
        return
    # 2) overlay the locked headline -> <proj>/thumbnail.png
    cmd = [py, str(mk), "--project", str(proj), "--still", str(still), "--title", title]
    if subtitle:
        cmd += ["--subtitle", subtitle]
    if not _run(cmd, t, "make_thumbnail", cwd=None, dry_run=False):
        t.warn("thumbnail overlay failed — shipping without a custom thumbnail.")
        return
    t.ok(f"thumbnail → {out_png}")


def run_convergence_leg(ctx, modea=None):
    """Assemble the episode: pool clips, lay the whole voiceover over the conformed
    video via assemble_episode.py → <project_dir>/final_video.mp4. Returns
    {"final": <path>} or None on halt."""
    t = ctx["t"]
    py = ctx.get("py", sys.executable)
    shared = Path(ctx["shared"])
    dry = ctx["dry_run"]
    proj_dir = ctx.get("project_dir")

    t.phase("CONVERGENCE LEG (assemble → final_video)")

    if not proj_dir:
        t.halt("cannot run convergence — project unresolved (need channel.json + --project).")
        return None
    proj = Path(proj_dir)

    durations = proj / "durations.json"
    voiceover = proj / "voiceover.mp3"
    final_out = proj / "final_video.mp4"

    # The Mode A leg hands us the authoritative index path + engine project name.
    # Fall back to the leg's known convention if the dict wasn't passed (e.g. resumed run).
    if modea and modea.get("index_json"):
        index_json = Path(modea["index_json"])
    else:
        index_json = proj / "_index.json"
    engine_project = (modea or {}).get("engine_project") or os.path.join(proj.name, "modea")
    # engine clips live under <engine_cwd>/<engine_project>/clips; engine_cwd defaults to
    # the project's PARENT (run_cwd), so <channel>/projects/<project>/modea/clips. We resolve
    # relative to proj when engine_project is the bare 'modea' subfolder name.
    ep = Path(engine_project)
    if ep.is_absolute():
        engine_clips_dir = ep / "clips"
    elif str(ep).startswith(proj.name + os.sep) or str(ep).startswith(proj.name + "/"):
        engine_clips_dir = proj.parent / ep / "clips"
    else:
        engine_clips_dir = proj / "modea" / "clips"

    # Preflight the inputs that MUST exist (unless dry-run, where legs upstream were skipped).
    if not dry:
        missing = [str(p) for p in (durations, voiceover, index_json) if not p.exists()]
        if missing:
            t.halt(f"convergence missing required inputs: {missing}. "
                   f"(Audio leg writes durations.json + voiceover.mp3; Mode A writes _index.json.)")
            return None

    pool = _pool_clips(proj_dir, engine_clips_dir, t, dry)

    # Music: channel music-dir wiring takes precedence, then single bed, then off.
    music_flag = "--no-music"
    music_dir_args = None
    # proj is <channel>/projects/<project>, so the channel folder is two up.
    _channel_dir = proj.parent.parent
    _mcfg = (ctx.get("channel_cfg") or {}).get("music") if isinstance(ctx.get("channel_cfg"), dict) else None
    if not _mcfg:
        import json as _json
        _cj = (_channel_dir / "channel.json")
        if _cj.exists():
            _mcfg = _json.loads(_cj.read_text()).get("music")
        else:
            t.warn(f"no channel.json at {_cj} -- music block not resolved")
    if _mcfg and _mcfg.get("dir"):
        _mdir = (_channel_dir / _mcfg["dir"])
        if _mdir.is_dir():
            music_dir_args = ["--music-dir", str(_mdir),
                              "--music-tracks", str(int(_mcfg.get("tracks", 3))),
                              "--music-crossfade", str(float(_mcfg.get("crossfade_seconds", 2)))]
            t.info(f"music dir → {_mdir.name}/ (random {_mcfg.get('tracks', 3)}, "
                   f"crossfade {_mcfg.get('crossfade_seconds', 2)}s)")
    if music_dir_args is None and ctx.get("music"):
        cand = proj / "music.mp3"
        if cand.exists():
            music_flag = f"--music {cand}"  # split below
            t.info(f"music bed present → {cand.name} (will mux under voice)")
        else:
            t.warn("ctx['music'] set but music.mp3 not found — assembling without music")

    cmd = [py, str(shared / "assemble_episode.py"),
           "--durations", str(durations),
           "--index", str(index_json),
           "--voiceover", str(voiceover),
           "--project", str(proj),
           "--clips", str(pool),
           "--out", str(final_out)]
    if music_dir_args is not None:
        cmd += music_dir_args
    elif music_flag == "--no-music":
        cmd.append("--no-music")
    else:
        cmd += ["--music", str(proj / "music.mp3")]

    if not _run(cmd, t, "assemble_episode", cwd=None, dry_run=dry):
        return None

    if dry:
        t.info(f"[dry-run] would write {final_out}")
        return {"final": str(final_out)}

    if not final_out.exists():
        t.halt(f"assemble ran but {final_out} was not produced. Check the assemble log above.")
        return None
    t.ok(f"convergence complete → {final_out}")

    # ── THUMBNAIL (auto-generate + Sonnet-select + overlay; graceful skip) ──
    _maybe_thumbnail(ctx, proj, t, py, shared, dry)

    # ── PUBLISH (channel-agnostic upload; private by default) ──
    _maybe_upload(ctx, proj, t, py, shared, dry)

    return {"final": str(final_out)}
