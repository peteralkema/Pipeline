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

# ------------------------------------------------------------------ dispatch
CMDS = {"normalise": cmd_normalise, "sweep": cmd_sweep, "film": cmd_film,
        "blocks": cmd_blocks, "audio": cmd_audio, "calibrate": cmd_calibrate}

def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("command", choices=list(CMDS))
    ap.add_argument("--project", required=True)
    ap.add_argument("rest", nargs="*")
    args = ap.parse_args()
    cfg = load_config(args.project)
    CMDS[args.command](cfg, args.rest)

if __name__ == "__main__":
    main()
