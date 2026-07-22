#!/usr/bin/env python3
"""
build_lego.py -- channel-agnostic beat-table pipeline. ONE tool, every channel.

  python3 build_lego.py normalise  --project P     # $0  recompute derived columns, in place
  python3 build_lego.py sweep      --project P      # $0  pre-render gate (banned words from rulebook)
  python3 build_lego.py film       --project P      # $0  the LEGO audit -- video as data
  python3 build_lego.py blocks     --project P [N..]# $0  CSV -> beats.json (gated) for stills
  python3 build_lego.py audio      --project P      #     emit narration -> TTS (provider-routed) -> whisper
  python3 build_lego.py calibrate  --project P W    #     measure whisper.json vs the fixed grid

Run from the CHANNEL dir. Master CSV lives at:  projects/<project>/master.csv
Everything channel-specific is READ FROM CONFIG, never coded in:
  - canon            <- channel.json  "canon"
  - beats_per_block  <- channel.json  "beats_per_block"  (default 40 = 200.000s seam)
  - tts_provider     <- channel.json  (elevenlabs | inworld) -- routed by the engine seam
  - banned words     <- the channel's rulebook.json "negative"  (+ shared/rulebook.json)
There is NO enoch/BANNED_VISUAL/PROBE constant here. Probes are per-film hand-picks the
render path consumes; banned words are per-channel doctrine in the rulebook.

AUTHORED columns (you write):  clip_index, block_id, weight, register, narration, phenomenon
                               (optional: sentence_id, angle, motion, air)
DERIVED  columns (tool writes): setting, words, variants
`phenomenon` carries the {tokens}; the camera angle lives INSIDE the phenomenon text.
`motion` is authored for storyboard-as-data channels (beatsheet) OR derived post-pick
(narration-timed) -- the audit reads it if present, skips it if absent.
"""
import argparse, csv, json, re, subprocess, sys
from pathlib import Path
from collections import Counter

# ------------------------------------------------------------------ config
def find_channel_json(start: Path) -> Path:
    for cand in (start.resolve(), *start.resolve().parents):
        cj = cand / "channel.json"
        if cj.is_file():
            return cj
    raise SystemExit(f"no channel.json found walking up from {start}")

def load_config(project: str):
    """Resolve channel.json by walking up from the project dir (or CWD)."""
    proj = Path("projects") / project if (Path("projects").is_dir()
            and len(Path(project).parts) == 1 and not Path(project).is_absolute()) \
            else Path(project)
    cj = find_channel_json(proj if proj.exists() else Path.cwd())
    cfg = json.loads(cj.read_text())
    cfg["_channel_dir"] = str(cj.parent)
    cfg["_project_dir"] = str(proj)
    cfg.setdefault("beats_per_block", 40)
    # canon: project <project>/canon.json layered OVER channel base_canon
    # (project wins on key collision -- same rule as recreation_pipeline). This
    # is what canon_of(cfg) returns; without it token expansion is a silent no-op.
    _merged_canon = dict(cfg.get("base_canon", {}) or {})
    _cj = proj / "canon.json"
    if _cj.is_file():
        try:
            _merged_canon.update(json.loads(_cj.read_text()))
        except Exception as _e:
            raise SystemExit(f"canon.json parse error ({_cj}): {_e}")
    cfg["canon"] = _merged_canon
    return cfg

def load_banned(cfg) -> list:
    """Banned words = the channel rulebook's negatives (+ shared). Per-channel doctrine.
    A space film's rulebook ALLOWS galaxy/nebula; enoch's bans them. That's the point."""
    terms = []
    for rb in (Path(cfg["_channel_dir"]) / "rulebook.json",
               Path(cfg["_channel_dir"]).parent / "shared" / "rulebook.json"):
        if rb.is_file():
            try:
                terms += json.loads(rb.read_text()).get("negative", [])
            except Exception:
                pass
    # keep only single, gate-able words (multi-word negatives are render-time only)
    return sorted({t.strip().lower() for t in terms if t and " " not in t.strip()})

# ------------------------------------------------------------------ master io
def master_path(cfg) -> Path:
    return Path(cfg["_project_dir"]) / "master.csv"

def wc(s: str) -> int:
    """Standalone punctuation is not a word (em-dashes are prosody, not tokens)."""
    return len([t for t in (s or "").split() if re.search(r"[A-Za-z0-9]", t)])

def load_master(cfg):
    mp = master_path(cfg)
    if not mp.is_file():
        raise SystemExit(f"missing {mp}")
    rows = list(csv.DictReader(mp.open()))
    if not rows:
        raise SystemExit(f"{mp} is empty")
    order = [(int(r["block_id"]), int(r["clip_index"])) for r in rows]
    if order != sorted(order):
        raise SystemExit("master is out of order -- run: build_lego.py normalise")
    for r in rows:                 # normalize weight + setting in memory for every command
        derive(r)
    return rows

def has_col(rows, col): return col in rows[0]

def norm_weight(w):
    """Accept H/hero and C/connective interchangeably. Canonical is hero|connective."""
    w = (w or "").strip().lower()
    if w in ("h", "hero"): return "hero"
    if w in ("c", "connective", "conn"): return "connective"
    return w

def derive(row):
    m = re.findall(r"\{(\w+)\}", row.get("phenomenon", ""))
    if m:
        row["setting"] = m[0]
    elif row.get("setting_token"):        # audit-shaped master: use the explicit column
        row["setting"] = row["setting_token"]
    elif not row.get("setting"):
        row["setting"] = "none"
    row["weight"] = norm_weight(row.get("weight"))
    row["words"] = str(wc(row.get("narration", "")))
    row["variants"] = "4" if row["weight"] == "hero" else "2"
    return row

def cmd_normalise(cfg, argv):
    mp = master_path(cfg)
    rows = list(csv.DictReader(mp.open()))
    rows.sort(key=lambda r: (int(r["block_id"]), int(r["clip_index"])))
    for r in rows:
        derive(r)
    fields = list(rows[0].keys())
    with mp.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"  normalised {len(rows)} rows -> {mp}")

# ------------------------------------------------------------------ canon / gates
def canon_of(cfg): return cfg.get("canon", {})

def check_tokens(text, canon, where):
    for k in re.findall(r"\{(\w+)\}", text or ""):
        if k not in canon:
            raise SystemExit(f"{where}: unknown token {{{k}}} -- add it to channel.json canon")

WORD_CEILING = 55  # LEGO hard ceiling

def gate_block(rows, cfg, banned):
    canon = canon_of(cfg)
    errs = []
    seen = set()
    for r in rows:
        ci = r["clip_index"]
        ph = r.get("phenomenon", "")
        if not ph.strip():
            errs.append(f"beat {ci}: empty phenomenon (VISUAL) -- batch-killer")
        if not re.search(r"\{\w+\}", ph):
            errs.append(f"beat {ci}: no {{token}} in phenomenon")
        for k in re.findall(r"\{(\w+)\}", ph):
            if k not in canon:
                errs.append(f"beat {ci}: unknown token {{{k}}}")
        w = wc(r.get("narration", ""))
        if w > WORD_CEILING:
            errs.append(f"beat {ci}: {w} words > {WORD_CEILING} ceiling")
        if r.get("weight") not in ("hero", "connective"):
            errs.append(f"beat {ci}: weight must be hero|connective, got {r.get('weight')!r}")
        for b in banned:
            if re.search(rf"\b{re.escape(b)}\b", ph, re.I):
                errs.append(f"beat {ci}: banned word '{b}' in phenomenon (channel rulebook)")
        if ci in seen:
            errs.append(f"beat {ci}: duplicate clip_index")
        seen.add(ci)
    return errs

# ------------------------------------------------------------------ sweep ($0 gate)
def cmd_sweep(cfg, argv):
    rows = load_master(cfg)
    if not has_col(rows, "phenomenon"):
        raise SystemExit("sweep needs a 'phenomenon' column (the {token}-bearing VISUAL). "
                         "This master is audit-shaped only -- author phenomenon first.")
    banned = load_banned(cfg)
    bpb = int(cfg["beats_per_block"])
    print(f"  banned words (from rulebook): {banned or '(none)'}")
    for block in (sorted({int(r['block_id']) for r in rows})):
        brows = [r for r in rows if int(r["block_id"]) == block]
        setting = Counter(k for r in brows for k in re.findall(r"\{(\w+)\}", r["phenomenon"]))
        ban = [(r["clip_index"], b) for r in brows for b in banned
               if re.search(rf"\b{re.escape(b)}\b", r["phenomenon"], re.I)]
        tokenless = [r["clip_index"] for r in brows if not re.search(r"\{\w+\}", r["phenomenon"])]
        unlit = [r["clip_index"] for r in brows if not re.search(
            r"\b(light|lit|sun|moon|day|blazing|brilliant|bright|star|glow|backlit|rim|"
            r"shadow|silhouette|amber|golden|dawn|dusk|lamp|neon)\w*\b",
            r["phenomenon"], re.I)]
        hero = sum(1 for r in brows if r["weight"] == "hero")
        w = sum(wc(r["narration"]) for r in brows)
        n = len(brows)
        print(f"\n== BLOCK {block} == {n} beats | {w} words ({w/n:.1f}/beat) | hero {hero}/{n} ({100*hero/n:.0f}%)")
        print("   setting mix : " + "  ".join(f"{k} {v}" for k, v in setting.most_common()))
        print(f"   BANNED      : {'none' if not ban else ban}")
        print(f"   tokenless   : {'none' if not tokenless else tokenless}")
        print(f"   unlit beats : {'none' if not unlit else unlit}   (an unlit prompt renders muddy)")

# ------------------------------------------------------------------ film (the audit -- video as data)
GOOD = {"hero_pct": 25, "settle_max_pct": 40}

def cmd_film(cfg, argv):
    rows = load_master(cfg)
    N = len(rows); bpb = int(cfg["beats_per_block"])
    blocks = sorted({int(r["block_id"]) for r in rows})
    print(f"=== {Path(cfg['_project_dir']).name} | {N} beats | {len(blocks)} blocks | "
          f"{N*5/60:.0f}:{(N*5)%60:02.0f} ===")

    H = sum(1 for r in rows if r["weight"] == "hero")
    print(f"\nHERO/CONN  {H} hero / {N-H} conn = {100*H/N:.0f}%   [target ~{GOOD['hero_pct']}%]")

    if has_col(rows, "motion"):
        print("\nMOTION")
        mc = Counter(r["motion"] for r in rows)
        for k, v in mc.most_common(): print(f"   {k:<7} {v:>3} ({100*v/N:.0f}%)")
        for b in blocks:
            br = [r for r in rows if int(r["block_id"]) == b]
            s = sum(1 for r in br if r["motion"] == "SETTLE")
            flag = "  <-- SETTLE-HEAVY" if 100*s/len(br) > GOOD["settle_max_pct"] else ""
            print(f"   block {b} settle: {100*s/len(br):.0f}%{flag}")
    else:
        print("\nMOTION     (no motion column -- derived post-pick; skipped)")

    if has_col(rows, "register"):
        print("\nREGISTER (per block -- flatline = failure)")
        for b in blocks:
            rc = Counter(r["register"] for r in rows if int(r["block_id"]) == b)
            print(f"   block {b} ({len(rc)} distinct): " +
                  ", ".join(f"{k}:{v}" for k, v in rc.most_common(6)))

    # framing-repeat scan: richest signature available
    sig_cols = [c for c in ("setting", "angle", "motion") if has_col(rows, c) or c == "setting"]
    for r in rows:
        derive(r)  # ensure setting present
    reps = []
    for i in range(1, N):
        a, b = rows[i-1], rows[i]
        if all(a.get(c) == b.get(c) for c in sig_cols):
            reps.append((a["clip_index"], b["clip_index"], "/".join(a.get(c, "") for c in sig_cols)))
    print(f"\nFRAMING    signature={sig_cols} | {len(reps)} consecutive repeats"
          + ("" if not reps else ":"))
    for r in reps[:12]: print(f"   beats {r[0]}-{r[1]}  {r[2]}")

    print("\nVO DENSITY (should trend DOWN into the climax = the dimmer)")
    for i in range(0, N, 10):
        ch = rows[i:i+10]; tw = sum(wc(r["narration"]) for r in ch)
        print(f"   beats {ch[0]['clip_index']:>3}-{ch[-1]['clip_index']:>3}: {tw:>3}  {'#'*(tw//5)}")

# ------------------------------------------------------------------ blocks (CSV -> beats.json)
def to_beat(row):
    return {"narration": row.get("narration", ""), "image_prompt": row["phenomenon"]}

def cmd_blocks(cfg, argv):
    rows = load_master(cfg)
    if not has_col(rows, "phenomenon"):
        raise SystemExit("blocks needs a 'phenomenon' column -- author the visual prompts first.")
    banned = load_banned(cfg)
    canon = canon_of(cfg)
    wanted = [int(a) for a in argv] or sorted({int(r["block_id"]) for r in rows})
    proj = Path(cfg["_project_dir"])
    total_stills = 0
    for block in wanted:
        brows = [r for r in rows if int(r["block_id"]) == block]
        errs = gate_block(brows, cfg, banned)
        if errs:
            print("\n".join("  GATE FAIL: " + e for e in errs)); raise SystemExit(1)
        beats = [to_beat(r) for r in brows]
        out = proj / f"b{block:02d}"
        out.mkdir(parents=True, exist_ok=True)
        (out / "beats.json").write_text(
            json.dumps({"canon": canon, "beats": beats}, indent=2, ensure_ascii=False))
        st = sum(4 if r["weight"] == "hero" else 2 for r in brows)
        total_stills += st
        w = sum(wc(r["narration"]) for r in brows)
        print(f"  block {block}: {len(brows)} beats -> {out}/beats.json | {w} words | {st} stills (${st*0.08:.2f})")
    print(f"\n  gates PASS | {total_stills} stills total (${total_stills*0.08:.2f})")

# ------------------------------------------------------------------ audio (emit -> TTS -> whisper)
def cmd_audio(cfg, argv):
    rows = load_master(cfg)
    proj = Path(cfg["_project_dir"])
    text = " ".join((r.get("narration", "") or "").strip() for r in rows).strip()
    narr = proj / "narration.txt"
    narr.write_text(text + "\n")
    words = sum(wc(r["narration"]) for r in rows)
    print(f"  {len(rows)} beats -> {narr} | {words} words | {len(text)} chars")

    # render VO via the shared engine (seam routes to elevenlabs/inworld by channel.json)
    shared = Path(cfg["_channel_dir"]).parent / "shared"
    sys.path.insert(0, str(shared))
    try:
        import recreation_pipeline as rp
    except Exception as e:
        raise SystemExit(f"cannot import recreation_pipeline from {shared}: {e}")
    voice = proj / "voiceover.mp3"
    print(f"  rendering VO ({cfg.get('tts_provider','inworld')}) -> {voice}")
    rp.generate_voiceover(text, voice)

    # whisper -> word timestamps (measurement only; direction-neutral)
    if not __import__("shutil").which("whisper"):
        print("  WARN: whisper not installed -- skip. pip install openai-whisper --break-system-packages")
        return
    print("  whisper (word timestamps)...")
    subprocess.run(["whisper", str(voice), "--model", "small", "--output_format", "json",
                    "--output_dir", str(proj), "--word_timestamps", "True", "--verbose", "False"],
                   check=True)
    print(f"  -> {proj/'voiceover.json'} | NEXT: build_lego.py calibrate --project {proj.name} {proj/'voiceover.json'}")

# ------------------------------------------------------------------ calibrate (words flex to the FIXED grid)
def cmd_calibrate(cfg, argv):
    if not argv:
        raise SystemExit("usage: build_lego.py calibrate --project P <whisper.json>")
    wj = json.loads(Path(argv[0]).read_text())
    words = [w for seg in wj.get("segments", []) for w in seg.get("words", [])]
    if not words:
        raise SystemExit("no word timestamps -- render whisper with --word_timestamps True")
    norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
    stream = [(norm(w["word"]), w.get("start"), w.get("end")) for w in words if norm(w["word"])]
    rows = load_master(cfg)
    bpb = int(cfg["beats_per_block"])

    si = 0; measured = []
    for r in rows:
        n = wc(r.get("narration", ""))
        if si + n > len(stream):
            measured.append((r, None, None)); continue
        measured.append((r, stream[si][1], stream[si+n-1][2] if n else stream[si][1]))
        si += n

    spoken = sum(wc(r["narration"]) for r, s, e in measured if s is not None)
    span = next((e for r, s, e in reversed(measured) if e is not None), None)
    first = next((s for r, s, e in measured if s is not None), 0.0)
    per_word = ((span - first) / spoken) if (span and spoken) else 60.0/184.0
    if span:
        print(f"  MEASURED: {spoken} words in {span-first:.1f}s = {spoken/((span-first)/60):.0f} WPM "
              f"| 1 word ~= {per_word:.2f}s")

    print(f"\n  {'beat':>7} {'words':>5} {'measured':>9} {'target':>7} {'over/under':>11} {'fix':>12}")
    cum = 0.0
    for i, (r, s, e) in enumerate(measured):
        tag = f"{r['block_id']}/{r['clip_index']}"
        if s is None:
            print(f"  {tag:>7}   -- unmeasured --"); continue
        dur = e - s; delta = dur - 5.0
        if abs(delta) < 0.25: fix = "ok"
        else:
            dw = round(delta / per_word)
            fix = f"{'cut' if dw>0 else 'add'} {abs(dw)}w"
        print(f"  {tag:>7} {wc(r['narration']):>5} {dur:>7.2f}s {5.0:>6.1f}s {delta:>+9.2f}s {fix:>12}")
        cum += delta
        if (i+1) % bpb == 0:
            print(f"  ----- seam {(i+1)//bpb}: cumulative drift {cum:+.2f}s "
                  f"(should land on {(i+1)*5.0:.0f}.0s) -----")
            cum = 0.0

# ------------------------------------------------------------------ stills (ref-aware 4x grid)
def _flat_map(rows):
    """(block, clip) -> FLAT FILM INDEX (CSV row order, 1-based).

    Flat index is row ORDER, never (block-1)*40+clip: the formula only agrees when
    every block holds exactly 40 rows, and a short block would silently misalign every
    beat after it. This is the number place.py parses out of {flat}-{variant}.png and
    the number render_clips.py uses for shot_{i:03d}.
    """
    return {(int(r["block_id"]), int(r["clip_index"])): i for i, r in enumerate(rows, 1)}


def _stills_render(cfg, brows, out_dir, flat_map, label):
    """Render the 4-variant pick-set for a list of rows into out_dir.

    Per beat: 4 real re-rolls if hero, else 2 real + 2 skip-tiles. Filenames are
    {clip:03d}-{v:02d}.png normally, or {block:02d}-{clip:03d}-{v:02d}.png when
    prefix_block is True (cross-film probe -- clip_index repeats across blocks and
    would collide). Resume-safe. Returns (real_count, index_rows).
    """
    import re as _re, shutil as _sh
    canon = canon_of(cfg)
    shared = Path(cfg["_channel_dir"]).parent / "shared"
    sys.path.insert(0, str(shared))
    try:
        import recreation_pipeline as rp
    except Exception as e:
        raise SystemExit("cannot import recreation_pipeline from %s: %s" % (shared, e))
    ref_mode = cfg.get("render_mode") == "reference"
    ref_map = cfg.get("reference_map", {}) if ref_mode else {}
    ref_chdir = Path(cfg["_channel_dir"])
    _shared_skip = shared / "_skip.png"
    _chan_skip = ref_chdir / "characters" / "_skip.png"
    skip_tile = _chan_skip if _chan_skip.exists() else _shared_skip
    out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    real = 0
    for r in brows:
        b = int(r["block_id"]); ci = int(r["clip_index"])
        raw = r["phenomenon"].strip()
        prompt = rp._expand_canon(raw, canon)
        refs = []
        if ref_mode:
            seen = set()
            for t in _re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", raw):
                if t in ref_map and t not in seen:
                    seen.add(t)
                    entry = ref_map[t]
                    for f in (entry if isinstance(entry, list) else [entry]):
                        refs.append(str(ref_chdir / f))
        n_real = 4 if r["weight"] == "hero" else 2
        for v in range(1, 5):
            name = "%03d-%02d.png" % (flat_map[(b, ci)], v)
            out = out_dir / name
            index.append((b, ci, v, "real" if v <= n_real else "skip", name))
            if out.exists():
                continue
            if v <= n_real:
                tag = ("[ref:%d] " % len(refs)) if refs else ""
                print("  [%d/%d v%d] %s%s..." % (b, ci, v, tag, prompt[:50]))
                rp.generate_still(prompt, out, reference_images=(refs or None))
                real += 1
            else:
                if skip_tile.exists():
                    _sh.copy(skip_tile, out)
                else:
                    out.write_bytes(b"")
    return real, index


def _write_grid_index(grid, index):
    with open(grid / "GRID-INDEX.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["block_id", "clip_index", "variant", "kind", "file"])
        w.writerows(index)


def cmd_stills(cfg, argv):
    """Render the variant grid.

      build_lego.py stills --project P [BLOCK ...]     # whole block(s) -> grid-bNN
      build_lego.py stills beats=1/1,2/3 --project P   # cross-film sample -> grid-probe
    """
    rows = load_master(cfg)
    if not has_col(rows, "phenomenon"):
        raise SystemExit("stills needs a 'phenomenon' column -- author first.")
    proj = Path(cfg["_project_dir"])
    flat_map = _flat_map(rows)
    beats = None
    for a in list(argv):
        if a.startswith("beats="):
            beats = set()
            for tok in a.split("=", 1)[1].split(","):
                tok = tok.strip()
                if not tok:
                    continue
                if "/" not in tok:
                    raise SystemExit("beats= needs block/clip pairs, e.g. beats=1/1,2/3")
                bb, cc = tok.split("/", 1)
                beats.add((int(bb), int(cc)))
            argv = [x for x in argv if x != a]
            break
    if beats is not None:
        have = {(int(r["block_id"]), int(r["clip_index"])) for r in rows}
        oob = sorted(p for p in beats if p not in have)
        if oob:
            raise SystemExit("beats= not in master: " + ", ".join("%d/%d" % p for p in oob))
        brows = [r for r in rows if (int(r["block_id"]), int(r["clip_index"])) in beats]
        real, index = _stills_render(cfg, brows, proj / "grid-probe", flat_map, "probe")
        _write_grid_index(proj / "grid-probe", index)
        print("  probe: %d beats -> %s | %d real stills ($%.2f)" % (len(brows), proj / "grid-probe", real, real * 0.08))
        return
    wanted = [int(a) for a in argv] or sorted({int(r["block_id"]) for r in rows})
    # PRE-GATE THE WHOLE FILM BEFORE ANY SPEND. Gating just-in-time inside the render
    # loop means a bad beat in block 6 only surfaces after blocks 1-5 have spent -- so
    # the run cannot be left unattended. Every input needed to validate all N blocks
    # exists before the first fal call: validate them all, report every failure at once,
    # spend nothing. An unattended run now either refuses at second zero or completes.
    banned = load_banned(cfg)
    pregate = []
    for block in wanted:
        brows = [r for r in rows if int(r["block_id"]) == block]
        for e in gate_block(brows, cfg, banned):
            pregate.append("block %d: %s" % (block, e))
    if pregate:
        print("GATE FAIL -- %d issue(s) across %d block(s). NOTHING RENDERED, $0 spent:"
              % (len(pregate), len(wanted)))
        print("\n".join("  " + e for e in pregate))
        raise SystemExit(1)
    print("pre-gate OK: %d block(s) clean -- rendering." % len(wanted))

    total_real = 0
    checked = []
    for block in wanted:
        brows = [r for r in rows if int(r["block_id"]) == block]
        grid = proj / "grid"
        real, index = _stills_render(cfg, brows, grid, flat_map, "block %d" % block)
        _write_grid_index(grid, index)
        total_real += real
        for row in index:
            if row[3] == "real":
                checked.append(grid / row[4])
        print("  block %d: grid -> %s | %d real stills ($%.2f) | GRID-INDEX.csv" % (block, grid, real, real * 0.08))

    # fal safety rejects land as ~7KB black placeholders and do NOT raise -- surface them
    rejects = []
    for f in checked:
        try:
            if f.exists() and f.stat().st_size < 8192:
                rejects.append(f)
        except OSError:
            pass
    print("\nDONE: %d block(s) | %d real stills ($%.2f)" % (len(wanted), total_real, total_real * 0.08))
    if rejects:
        print("WARNING: %d frame(s) under 8KB -- likely fal safety rejects (black placeholders):" % len(rejects))
        for f in rejects[:20]:
            print("  %s" % f)
        if len(rejects) > 20:
            print("  ... and %d more" % (len(rejects) - 20))
        print("  check safety_tolerance, DELETE the listed files, then re-run (resume-safe refill).")
    print("\nNEXT: review each grid folder, promote ONE winner per beat to shot_NNN.png (the pick).")


PROBE_PRIORITY = ("witness", "descent", "leviathan", "remnant", "deep", "codex")

def _primary_token(phenomenon):
    m = re.match(r"\s*\{([a-zA-Z_][a-zA-Z0-9_]*)\}", phenomenon or "")
    return m.group(1) if m else None

def cmd_probe(cfg, argv):
    """Self-selecting visual probe -- NO numbering decisions.

      build_lego.py probe --project P        # 20-beat register spread
      build_lego.py probe 30 --project P     # N-beat spread

    Picks one beat per canon token present (doubling the fail-hardest tokens),
    spread across blocks, renders the 4-variant grid into grid-probe, prints the
    verdict card. Block-prefixed filenames -- never collides.
    """
    n = 20
    for a in argv:
        if a.isdigit():
            n = int(a); break
    rows = load_master(cfg)
    if not has_col(rows, "phenomenon"):
        raise SystemExit("probe needs a 'phenomenon' column -- author first.")
    by_tok = {}
    for r in rows:
        t = _primary_token(r["phenomenon"])
        if t:
            by_tok.setdefault(t, []).append(r)
    for t in by_tok:
        by_tok[t].sort(key=lambda r: (int(r["block_id"]), int(r["clip_index"])))
    tokens = sorted(by_tok)
    if not tokens:
        raise SystemExit("probe: no canon tokens found in phenomena.")

    def _spread(lst, k):
        k = min(k, len(lst))
        if k <= 0:
            return []
        if k == 1:
            return [lst[len(lst) // 2]]
        step = (len(lst) - 1) / (k - 1)
        return [lst[round(i * step)] for i in range(k)]

    picks = []
    seen = set()
    for t in tokens:
        want = 2 if t in PROBE_PRIORITY else 1
        for r in _spread(by_tok[t], want):
            key = (int(r["block_id"]), int(r["clip_index"]))
            if key not in seen:
                seen.add(key); picks.append(r)
    order = [t for t in PROBE_PRIORITY if t in by_tok] + [t for t in tokens if t not in PROBE_PRIORITY]
    i = 2
    while len(picks) < n:
        added = False
        for t in order:
            if len(picks) >= n:
                break
            for r in _spread(by_tok[t], i):
                key = (int(r["block_id"]), int(r["clip_index"]))
                if key not in seen:
                    seen.add(key); picks.append(r); added = True; break
        i += 1
        if not added:
            break
    picks.sort(key=lambda r: (int(r["block_id"]), int(r["clip_index"])))
    picks = picks[:n]

    proj = Path(cfg["_project_dir"])
    real, index = _stills_render(cfg, picks, proj / "grid-probe", _flat_map(rows), "probe")
    _write_grid_index(proj / "grid-probe", index)
    sel = ", ".join("%d/%d" % (int(r["block_id"]), int(r["clip_index"])) for r in picks)
    nblocks = len({int(r["block_id"]) for r in picks})
    print("\n  probe: %d beats across %d blocks -> %s" % (len(picks), nblocks, proj / "grid-probe"))
    print("  beats: %s" % sel)
    print("  %d real stills ($%.2f)" % (real, real * 0.08))
    print("\n  VERDICT CARD -- eyeball before the $71 grid:")
    print("    witness   : draped, austere, statuesque -- NOT sexualised")
    print("    descent   : solid, opaque, hard shadow -- NOT glowing/translucent")
    print("    leviathan : massive, bright-lit deep -- NOT murk")
    print("    remnant   : giant vs tiny human -- scale reads")
    print("    deep      : foreground anchor reads against the depth")
    print("    codex     : monumental book -- NO scroll, NO lectern")
    print("    relief    : sharp carved stone, bright -- NO murk")
    print("  spell-breakers: text, watermarks, extra limbs, modern objects.")


# ------------------------------------------------------------------ clips (picked stills -> animated clips)
def cmd_clips(cfg, argv):
    """Animate the PICKED stills into clips. Reads shot_NNN.png (the promoted
    winners) + the CSV's air/move/motion; routes each beat:
        air=kling -> animate_still(motion)   (Kling image->video)
        else      -> ken_burns_still(move)   (the free ffmpeg floor)
    Writes clips/shot_NNN.mp4. Resume-safe. A picked-still-missing beat aborts.

      build_lego.py clips --project P [N ...]
    """
    rows = load_master(cfg)
    wanted = [int(a) for a in argv] or sorted({int(r["block_id"]) for r in rows})
    proj = Path(cfg["_project_dir"])
    stills = proj / "stills"
    clips = proj / "clips"; clips.mkdir(parents=True, exist_ok=True)

    shared = Path(cfg["_channel_dir"]).parent / "shared"
    sys.path.insert(0, str(shared))
    try:
        import recreation_pipeline as rp
    except Exception as e:
        raise SystemExit(f"cannot import recreation_pipeline from {shared}: {e}")

    todo = [r for r in rows if int(r["block_id"]) in wanted]
    # verify every beat has a picked still before spending on any
    missing = [r["clip_index"] for r in todo
               if not (stills / f"shot_{int(r['clip_index']):03d}.png").exists()]
    if missing:
        raise SystemExit(f"no picked still for beats {missing} -- promote a grid winner "
                         f"to stills/shot_NNN.png (the pick) before clips.")

    kling = sum(1 for r in todo if r.get("air", "").lower() == "kling")
    print(f"  {len(todo)} beats | {kling} kling / {len(todo)-kling} floor "
          f"| ~${kling*0.42:.2f} kling")
    for r in todo:
        ci = int(r["clip_index"])
        still = stills / f"shot_{ci:03d}.png"
        out = clips / f"shot_{ci:03d}.mp4"
        if out.exists():
            print(f"  [{ci}] already done"); continue
        air = r.get("air", "").lower()
        if air == "kling":
            motion = (r.get("motion") or "").strip()
            if not motion:
                raise SystemExit(f"beat {ci}: air=kling but no motion prompt -- aborting before spend")
            print(f"  [{ci}] kling: {motion[:48]}...")
            rp.animate_still(still, motion, out)
        else:
            print(f"  [{ci}] floor (ken burns)")
            rp.ken_burns_still(still, out)
    print(f"\nOK clips -> {clips}  (output #1; VO is output #2, from `audio`)")


# ------------------------------------------------------------------ dispatch
CMDS = {"normalise": cmd_normalise, "sweep": cmd_sweep, "film": cmd_film,
        "blocks": cmd_blocks, "stills": cmd_stills, "probe": cmd_probe, "clips": cmd_clips,
        "audio": cmd_audio, "calibrate": cmd_calibrate}

def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("command", choices=list(CMDS))
    ap.add_argument("--project", required=True)
    ap.add_argument("rest", nargs="*")
    args, _extra = ap.parse_known_args()
    rest = list(args.rest) + list(_extra)
    cfg = load_config(args.project)
    CMDS[args.command](cfg, rest)

if __name__ == "__main__":
    main()
