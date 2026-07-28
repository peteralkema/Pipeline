#!/usr/bin/env python3
"""
intake.py -- the authoring gate. Runs INSIDE the authoring session (pure text/JSON/CSV
processing; no box, no network). Guarantees nothing reaches a batch inbox unless it
passed every mechanical gate.

TWO MODES:
  --self   (default) mechanical gates only. Authoring Claude runs this in a loop, fixes
           defects, re-runs until GREEN, then produces the handover zip. No human.
  --admit  adds the ledger check against a channel shipped-ledger file + prints JUDGMENT
           flags (pool overlap, light kling, long beats) for a human yes/no at the
           authoring->batch boundary. Re-runs the mechanical gates too (cheap).

USAGE (from a folder containing the -src set, or pass a zip):
  python3 intake.py <dir-or-zip> --channel scripture_on_screen
  python3 intake.py forgive.zip  --channel scripture_on_screen --admit --ledger docs/channels/_Scripture-On-Screen.md

REQUIRES in the same container (they ride in the briefcase):
  audit_script.py, csv2script.py  (imported/invoked, never reconstructed)

Exit 0 = GREEN (all hard gates pass). Exit 1 = defects (listed). Stdlib + the two tools only.
"""
import argparse, csv, json, os, re, subprocess, sys, tempfile, zipfile, shutil
from pathlib import Path

SRC_FILES = ["master.csv", "canon.json", "sections.json", "desc.txt", "thumbsubject.txt"]
WORD_BAND = (15, 25)          # doctrine target; >25 is a soft warn (audit hard gate is --max-words 55)
STRAY_GLOBS = [".kling.json"] # invented sidecars: stripped, never delivered


def find_tool(name):
    for base in (".", os.path.dirname(os.path.abspath(__file__)), "packaging", "shared"):
        p = Path(base) / name
        if p.exists():
            return str(p)
    return None


def unpack(src, work):
    """Return the dir holding the -src files (handles zip or dir; strips junk)."""
    if src.endswith(".zip"):
        with zipfile.ZipFile(src) as z:
            z.extractall(work)
    else:
        shutil.copytree(src, work, dirs_exist_ok=True)
    # flatten: find the dir that actually contains master.csv
    for root, _, files in os.walk(work):
        if "__MACOSX" in root:
            continue
        if "master.csv" in files:
            return root
    return work


def strip_strays(d):
    removed = []
    for root, _, files in os.walk(d):
        if "__MACOSX" in root:
            shutil.rmtree(root, ignore_errors=True)
            continue
        for f in files:
            if any(f.endswith(g) for g in STRAY_GLOBS):
                os.remove(os.path.join(root, f))
                removed.append(f)
    return removed


def check_set(d):
    have = [f for f in SRC_FILES if (Path(d) / f).exists()]
    missing = [f for f in SRC_FILES if not (Path(d) / f).exists()]
    return have, missing


def csv_stats(d):
    rows = list(csv.reader(open(Path(d) / "master.csv")))
    hdr, data = rows[0], rows[1:]
    idx = {c: i for i, c in enumerate(hdr)}
    out = {"beats": len(data), "cols": len(hdr), "has_move": "move" in idx}
    ncol, acol, pcol = idx.get("narration"), idx.get("air"), idx.get("phenomenon")
    words = [len(re.sub(r"<break[^>]*/>", "", r[ncol]).split()) for r in data] if ncol is not None else []
    out["words_avg"] = round(sum(words) / len(words), 1) if words else 0
    out["over_band"] = [(i, w) for i, w in enumerate(words) if w > WORD_BAND[1]]
    out["blank_moves"] = sum(1 for r in data if out["has_move"] and not r[idx["move"]].strip())
    kl = [i for i, r in enumerate(data) if acol is not None and r[acol].strip() == "kling"]
    out["kling"] = len(kl)
    out["kling_contig"] = kl == list(range(len(kl)))
    toks = set()
    if pcol is not None:
        for r in data:
            toks |= set(re.findall(r"\{(\w+)\}", r[pcol]))
    canon = json.load(open(Path(d) / "canon.json")) if (Path(d) / "canon.json").exists() else {}
    out["tokens"] = len(toks)
    out["missing_canon"] = sorted(toks - set(canon))
    out["bom"] = round(len(data) * 0.08 + len(kl) * 0.42 + 1, 2)
    return out


def run_audit(d, audit):
    rep = Path(d) / "_audit.json"
    cmd = [sys.executable, audit, str(Path(d) / "master.csv"),
           "--canon", str(Path(d) / "canon.json"), "--json", str(rep)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    passed = "ALL HARD GATES PASS" in (r.stdout + r.stderr)
    return passed, r.stdout + r.stderr


def visual_monotony(d):
    """The 'no 16 wheat fields' gate. Returns (hard_fails, warns).
    HARD: a bare token (token is the entire visual, no framing after it) repeated,
          or a run of >=4 beats with identical token-stripped visual text.
    WARN: a single bare token even once (author should add framing)."""
    rows = list(csv.reader(open(Path(d) / "master.csv")))
    hdr, data = rows[0], rows[1:]
    ix = {c: i for i, c in enumerate(hdr)}
    pcol = ix.get("phenomenon")
    if pcol is None:
        return [], []
    hard, warn = [], []
    tok_re = re.compile(r"\{(\w+)\}")
    # bare token = phenomenon is ONLY a token (optionally whitespace)
    bare = []
    for i, r in enumerate(data):
        p = r[pcol].strip()
        stripped = tok_re.sub("", p).strip()
        if tok_re.search(p) and not stripped:
            bare.append(i)
    if bare:
        # consecutive bare-token runs are the hard fail
        runs = []
        s = bare[0]; prev = bare[0]
        for b in bare[1:]:
            if b == prev + 1:
                prev = b
            else:
                runs.append((s, prev)); s = b; prev = b
        runs.append((s, prev))
        for a, b in runs:
            n = b - a + 1
            if n >= 2:
                hard.append("BARE-TOKEN RUN beats %d-%d (%d beats, no per-beat framing) -- the 16-wheat-fields failure" % (a, b, n))
            else:
                warn.append("bare token at beat %d (add framing after the token)" % a)
    # identical token-stripped visual runs
    sigs = [tok_re.sub("", r[pcol]).strip().lower()[:60] for r in data]
    i = 0
    while i < len(sigs):
        j = i
        while j + 1 < len(sigs) and sigs[j + 1] == sigs[i] and sigs[i]:
            j += 1
        if j - i + 1 >= 4:
            hard.append("IDENTICAL-VISUAL RUN beats %d-%d (%d beats same frame) -- vary framing per beat" % (i, j, j - i + 1))
        i = j + 1
    # TABLEAU BUDGET (the Job ash-heap gate, 27 Jul): a tableau = the beat's first token.
    # Varied framing text does NOT rescue a dominant tableau: AI re-rolls the actor per
    # still, so long dwells render as a carousel of strangers, not coverage.
    firsts = []
    for r in data:
        m = tok_re.findall(r[pcol])
        firsts.append(m[0] if m else None)
    n = len(data)
    counts = {}
    for t in firsts:
        if t:
            counts[t] = counts.get(t, 0) + 1
    for t, cnt in sorted(counts.items(), key=lambda kv: -kv[1]):
        share = cnt / float(n)
        if share > 0.15:
            hard.append("TABLEAU SHARE: {%s} on %d/%d beats (%.0f%%) -- max 15%%. Redistribute; mine the source catalogue for cutaways" % (t, cnt, n, 100 * share))
        elif share > 0.10:
            warn.append("tableau {%s} at %.0f%% of beats (soft ceiling 10%%) -- confirm intended" % (t, 100 * share))
    i = 0
    while i < len(firsts):
        j = i
        while j + 1 < len(firsts) and firsts[j + 1] == firsts[i] and firsts[i]:
            j += 1
        rl = j - i + 1
        if firsts[i] and rl > 6:
            hard.append("TABLEAU RUN: {%s} beats %d-%d (%d consecutive) -- max 6; dwell 4-6 then cut away" % (firsts[i], i, j, rl))
        elif firsts[i] and rl > 4:
            warn.append("tableau {%s} run of %d (beats %d-%d) -- soft ceiling 4" % (firsts[i], rl, i, j))
        i = j + 1
    return hard, warn


def ledger_flags(d, ledger_path):
    """Warn (never fail) if this title's key nouns collide with a shipped-ledger pool."""
    if not ledger_path or not Path(ledger_path).exists():
        return ["(no ledger file given -- pool-overlap check skipped)"]
    text = Path(ledger_path).read_text().lower()
    # crude but useful: pull the shipped-ledger table region and compare subject words
    desc = (Path(d) / "desc.txt").read_text().lower() if (Path(d) / "desc.txt").exists() else ""
    subjects = set(re.findall(r"[a-z]{5,}", desc))
    hot = [w for w in ("resurrection", "altar", "lazarus", "chamber", "afterlife",
                       "sleep", "grave", "heaven", "hades", "sheol", "judgment")
           if w in subjects and w in text]
    flags = []
    if hot:
        flags.append("POOL-OVERLAP: desc shares afterlife-pool terms with shipped ledger (%s) -- confirm re-entry angle / space in drip" % ", ".join(hot))
    return flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="dir or .zip holding the -src set")
    ap.add_argument("--channel", required=True, help="underscore form, e.g. scripture_on_screen")
    ap.add_argument("--admit", action="store_true", help="boundary mode: add ledger + judgment flags")
    ap.add_argument("--ledger", help="path to channel doctrine .md (for --admit pool check)")
    args = ap.parse_args()

    audit = find_tool("audit_script.py")
    if not audit:
        print("ABORT: audit_script.py not in container -- it must ride in the briefcase.")
        sys.exit(1)

    work = tempfile.mkdtemp(prefix="intake_")
    d = unpack(args.src, work)

    print("=" * 70)
    print("INTAKE  %s  [%s]  mode=%s" % (os.path.basename(args.src), args.channel,
                                         "admit" if args.admit else "self"))
    print("=" * 70)

    hard_fail = []

    stray = strip_strays(d)
    if stray:
        print("  stripped strays (not delivered): %s" % ", ".join(sorted(set(stray))))

    have, missing = check_set(d)
    if missing:
        hard_fail.append("INCOMPLETE SET -- missing: %s" % ", ".join(missing))
    else:
        print("  set complete: all 5 source files present")

    if "master.csv" in have:
        s = csv_stats(d)
        print("  beats:%d  move_col:%s  blank_moves:%d  kling:%d(contig=%s)  words_avg:%s  BOM:$%.2f"
              % (s["beats"], s["has_move"], s["blank_moves"], s["kling"], s["kling_contig"],
                 s["words_avg"], s["bom"]))
        if not s["has_move"]:
            hard_fail.append("NO move COLUMN (directed-motion floor absent)")
        if s["blank_moves"]:
            hard_fail.append("%d beats with blank move" % s["blank_moves"])
        if not s["kling_contig"]:
            hard_fail.append("kling beats NOT contiguous front-N (Law 8)")
        if s["missing_canon"]:
            hard_fail.append("UNRESOLVED tokens (no canon entry): %s" % ", ".join(s["missing_canon"]))
        if s["bom"] > 25:
            hard_fail.append("BOM $%.2f exceeds $25 ceiling" % s["bom"])
        if s["over_band"]:
            print("  WARN  %d beats over %d words (band target): %s"
                  % (len(s["over_band"]), WORD_BAND[1], s["over_band"][:6]))

    if "canon.json" in have and "master.csv" in have:
        ok, log = run_audit(d, audit)
        print("  audit_script: %s" % ("ALL HARD GATES PASS" if ok else "FAIL"))
        if not ok:
            hard_fail.append("audit_script.py hard-gate failure (run it directly to see which)")

    if "master.csv" in have:
        mono_hard, mono_warn = visual_monotony(d)
        if mono_hard:
            for m in mono_hard:
                hard_fail.append(m)
        else:
            print("  visual-monotony: clean (no bare-token or identical-visual runs)")
        for w in mono_warn:
            print("  WARN  " + w)

    if args.admit:
        print("  -- ADMIT judgment flags (human call, not auto-fail) --")
        for f in ledger_flags(d, args.ledger):
            print("    FLAG: " + f)
        s = csv_stats(d) if "master.csv" in have else {}
        if s.get("kling", 99) < 15:
            print("    FLAG: light kling (%d) -- confirm cold-open front-load is intended" % s["kling"])

    print("-" * 70)
    if hard_fail:
        print("RESULT: DEFECTS (%d) -- nothing admitted. Fix and re-run:" % len(hard_fail))
        for f in hard_fail:
            print("  x " + f)
        shutil.rmtree(work, ignore_errors=True)
        sys.exit(1)
    print("RESULT: GREEN -- all hard gates pass." + (" Review flags above before batch." if args.admit else " Ready to compile + hand over."))
    shutil.rmtree(work, ignore_errors=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
