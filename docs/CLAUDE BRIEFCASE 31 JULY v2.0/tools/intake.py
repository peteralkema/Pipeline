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
    kcol = idx.get("kling")
    placement = [i for i, r in enumerate(data) if kcol is not None
                 and r[kcol].strip().lower() in ("1", "x", "kling", "yes", "true")]
    if placement:
        # Law 28e placement-by-value: authored kling column, contiguity waived.
        kl = placement
        out["kling_contig"] = True
        out["placement_mode"] = True
    else:
        kl = [i for i, r in enumerate(data) if acol is not None and r[acol].strip() == "kling"]
        out["kling_contig"] = kl == list(range(len(kl)))
        out["placement_mode"] = False
    out["kling"] = len(kl)

    # 31 Jul fix-commit hard gates (Laws 25 + 28):
    out["empty_narr"] = [i for i, r in enumerate(data)
                         if ncol is not None and not r[ncol].strip()]
    TAGWORD = re.compile(r"(?i)\b(move|visual|motion)\s*:")
    out["tagword_narr"] = [i for i, r in enumerate(data)
                           if ncol is not None and TAGWORD.search(r[ncol])]
    CONTACT = re.compile(r"(?i)\b(jump\w*|crack\w*|explod\w*|slid\w*\s+out|"
                         r"burst\w*|shatter\w*|strik\w*|smash\w*|collid\w*|"
                         r"impact\w*|crash\w*)\b")
    mcol = idx.get("motion")
    hits = [i for i, r in enumerate(data)
            if mcol is not None and r[mcol].strip() and CONTACT.search(r[mcol])]
    cfg_p = Path(d) / "chop-config.json"
    if cfg_p.exists():
        try:
            km = json.load(open(cfg_p)).get("kling_motion", [])
            hits += [f"cfg#{j}" for j, m in enumerate(km) if CONTACT.search(m)]
        except Exception:
            pass
    out["contact_motion"] = hits

    # Law 32 (1 Aug, the five-burning-pages receipt): monotony is mechanical.
    scol, pcol = idx.get("subject"), idx.get("phenomenon")
    runs_over, run_tok, run_len, run_start = [], None, 0, 0
    if scol is not None:
        for i, r in enumerate(data):
            tok = r[scol].strip()
            if tok == run_tok:
                run_len += 1
            else:
                if run_len > 3:
                    runs_over.append(f"{run_tok}@{run_start}x{run_len}")
                run_tok, run_len, run_start = tok, 1, i
        if run_len > 3:
            runs_over.append(f"{run_tok}@{run_start}x{run_len}")
    out["token_runs_over3"] = runs_over
    import difflib
    dups = []
    if pcol is not None:
        for i in range(1, len(data)):
            a, b = data[i-1][pcol].strip(), data[i][pcol].strip()
            if a and b and (a == b or difflib.SequenceMatcher(None, a, b).ratio() > 0.85):
                dups.append(i)
    out["adjacent_dup_phenomena"] = dups
    bcol = idx.get("block_id")
    # Law 34 (1 Aug, the telephone-pole receipt): positive period lock.
    out["period_missing"], out["highprior_unqualified"] = [], []
    cfg_p2 = Path(d) / "chop-config.json"
    canon_p = Path(d) / "canon.json"
    if cfg_p2.exists():
        try:
            c2 = json.load(open(cfg_p2))
            anchor = c2.get("period_anchor")
            if anchor:
                exempt = set(c2.get("period_exempt_archetypes", []))
                arch = c2.get("token_archetypes", {})
                canon = json.load(open(canon_p)) if canon_p.exists() else {}
                variants = c2.get("variants", {})
                for tok, desc in canon.items():
                    if arch.get(tok) in exempt:
                        continue
                    texts = [desc] + [v[1] for v in variants.get(tok, [])]
                    if any(anchor not in t for t in texts):
                        out["period_missing"].append(tok)
            HIGH = re.compile(r"(?i)\b(road|roads|street|streets|highway|town|city|cities|lights)\b")
            MAT = re.compile(r"(?i)\b(dirt|packed|earth|earthen|stone|mud-brick|dust|unpaved|track|"
                             r"oil-lamp|oil lamp|torch\w*|fire\w*|lamplit|lamp-lit|candle)\b")
            variants2 = c2.get("variants", {})
            canon2 = json.load(open(canon_p)) if canon_p.exists() else {}
            for tok in set(list(canon2.keys()) + list(variants2.keys())):
                texts = [canon2.get(tok, "")] + [v[1] for v in variants2.get(tok, [])]
                for t in texts:
                    if t and HIGH.search(t) and not MAT.search(t):
                        out["highprior_unqualified"].append(tok)
                        break
        except Exception:
            pass
    # Law 35 (2 Aug, the missing-chariots receipt): cast + props per block.
    out["abstract_blocks"], out["castlight_blocks"] = [], []
    if cfg_p2.exists():
        try:
            c3 = json.load(open(cfg_p2))
            chr_cls = set(c3.get("character_archetypes", []))
            obj_cls = set(c3.get("object_archetypes", []))
            arch3 = c3.get("token_archetypes", {})
        except Exception:
            c3, chr_cls, obj_cls, arch3 = {}, set(), set(), {}
        try:
            bcolx = idx.get("block_id")
            if (chr_cls or obj_cls) and scol is not None and bcolx is not None:
                blocks = {}
                for r in data:
                    blocks.setdefault(r[bcolx].strip(), set()).add(r[scol].strip())
                for b, toks in sorted(blocks.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
                    has_c = any(arch3.get(t) in chr_cls for t in toks)
                    has_o = any(arch3.get(t) in obj_cls for t in toks)
                    if not has_c and not has_o:
                        out["abstract_blocks"].append(b)
                    elif not (has_c and has_o):
                        out["castlight_blocks"].append(b)
        except Exception:
            pass
    out["block0_overlong"] = [i for i, r in enumerate(data)
                              if bcol is not None and ncol is not None
                              and r[bcol].strip() == "0"
                              and len(r[ncol].split()) > 26]
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
    # PATCHED 29 Jul (second evening session): the real audit_script.py takes
    # --csv as a named flag (not positional) and has no --json output flag at
    # all -- it only prints to stdout/stderr, which this function already parses
    # for the "ALL HARD GATES PASS" string. Original call would have failed
    # immediately (unrecognized --json argument) had it been run as-shipped.
    cmd = [sys.executable, audit, "--csv", str(Path(d) / "master.csv"),
           "--canon", str(Path(d) / "canon.json")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout + r.stderr
    # PATCHED: the real audit_script.py's actual success string is "AUDIT PASSED."
    # -- "ALL HARD GATES PASS" (the string this function originally checked for)
    # never appears anywhere in its output, pass or fail. As shipped, this check
    # would report FAIL on every run regardless of the real verdict.
    passed = "AUDIT PASSED" in out
    return passed, out


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
    ap.add_argument("--bom-ceiling", type=float, default=25.0,
                    help="max acceptable BOM in $. Default 25 (Line B). For long-form runs "
                         "(70min+ runtime floor, banked 29 Jul evening third session), pass the "
                         "real ceiling explicitly rather than silently exceeding or silently "
                         "lowering the default -- e.g. --bom-ceiling 35 for a stated, conscious override.")
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
            hard_fail.append("kling beats NOT contiguous front-N (Law 8; "
                             "authored `kling` column = the legal exception)")
        if s.get("empty_narr"):
            hard_fail.append("EMPTY NARRATION at beat rows %s (Law 25 / box "
                             "wordless-verify parity)" % s["empty_narr"][:8])
        if s.get("tagword_narr"):
            hard_fail.append("TAG-WORD (move:/visual:/motion:) inside narration "
                             "at rows %s (Law 25 -- parser eats the beat)"
                             % s["tagword_narr"][:8])
        ab = s.get("abstract_blocks") or []
        if ab:
            hard_fail.append("FULLY ABSTRACT BLOCKS %s -- zero character-class "
                             "AND zero object-class tokens (Law 35: every act "
                             "carries cast and props; face-safe staging exists "
                             "for exactly this)" % ab[:8])
        aw = s.get("castlight_blocks") or []
        if aw:
            warn.append("blocks %s carry only one of character/object classes "
                        "(Law 35 soft: prefer both)" % aw[:8])
        pa = s.get("period_missing") or []
        if pa:
            hard_fail.append("PERIOD ANCHOR MISSING from canon/variants of tokens "
                             "%s (Law 34 -- the period is enforced positively; "
                             "every non-exempt token's texts carry the config's "
                             "period_anchor verbatim)" % pa[:6])
        hp = s.get("highprior_unqualified") or []
        if hp:
            hard_fail.append("HIGH-PRIOR NOUN UNQUALIFIED in %s (Law 34 -- "
                             "road/street/town/city/lights never appear without "
                             "their material or light source named: dirt, packed "
                             "earth, stone, mud-brick, oil-lamp, torch)" % hp[:6])
        b0 = s.get("block0_overlong") or []
        if b0:
            hard_fail.append("BLOCK-0 BEATS OVER 26 WORDS at rows %s (Law 33 -- "
                             "the opening ramp: cold-open beats chop at their own "
                             "register, target ~20w, hard 26; add a block-0 "
                             "register override to the chop config)" % b0[:8])
        runs = s.get("token_runs_over3") or []
        if runs:
            hard_fail.append("SAME-TOKEN RUN >3 consecutive beats at %s (Law 32 "
                             "-- a dwell is coverage, not repetition: interleave "
                             "tokens or cut the scene)" % runs[:6])
        dups = s.get("adjacent_dup_phenomena") or []
        if dups:
            hard_fail.append("ADJACENT NEAR-IDENTICAL PHENOMENA at rows %s (Law "
                             "32 -- no two successive beats may read as the same "
                             "frame; vary the variant or the token)" % dups[:8])
        if s.get("contact_motion"):
            hard_fail.append("CONTACT-PHYSICS verbs in motion prompts at %s "
                             "(Law 28 -- i2v morphs, never simulates contact; "
                             "author the event as a cut-pair)"
                             % s["contact_motion"][:8])
        if s["missing_canon"]:
            hard_fail.append("UNRESOLVED tokens (no canon entry): %s" % ", ".join(s["missing_canon"]))
        if s["bom"] > args.bom_ceiling:
            hard_fail.append("BOM $%.2f exceeds $%.2f ceiling" % (s["bom"], args.bom_ceiling))
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
