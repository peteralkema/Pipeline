#!/usr/bin/env python3
"""patch_intake_cast_gate.py -- the unknown-@ HARD gate for intake.py.

Registry law (boot Part 4 remaining-work item): an @-film cannot pass intake
unless every @identifier in the phenomenon column resolves to a citizen in the
channel's assets.json with frozen reference_urls. Reads the manifest from disk
ONLY -- never the network. Mirrors the resolver byte-for-byte: same token
regex, same key lookup ("@id" then bare id), same parent.parent discovery.

Idempotent: re-running detects the gate and exits 0 unchanged.
Usage: python3 patch_intake_cast_gate.py [path/to/intake.py]   (default ./intake.py)
"""
import py_compile, shutil, sys
from pathlib import Path

TARGET = Path(sys.argv[1] if len(sys.argv) > 1 else "intake.py")
MARK = "at_tokens"

A1_OLD = '''    canon = json.load(open(Path(d) / "canon.json")) if (Path(d) / "canon.json").exists() else {}
    out["tokens"] = len(toks)
    out["missing_canon"] = sorted(toks - set(canon))'''
A1_NEW = '''    canon = json.load(open(Path(d) / "canon.json")) if (Path(d) / "canon.json").exists() else {}
    out["tokens"] = len(toks)
    out["missing_canon"] = sorted(toks - set(canon))
    # CAST GATE collection (registry law): @identifiers in phenomenon, the
    # resolver's exact grammar (shared/v2/visuals.py _detect_ats). Ruled: @
    # creates NO canon rows -- canon.json stays environmental-only, so @ids
    # are deliberately NOT in the missing_canon universe above.
    ats = set()
    if pcol is not None:
        for r in data:
            ats |= set(re.findall(r"@([a-z][a-z_]*)", r[pcol]))
    out["at_tokens"] = sorted(ats)'''

A2_OLD = '''    ap.add_argument("--bom-ceiling", type=float, default=25.0,'''
A2_NEW = '''    ap.add_argument("--assets", help="channel assets.json (cast registry); "
                    "auto-discovered at <src>/../../assets.json when omitted")
    ap.add_argument("--bom-ceiling", type=float, default=25.0,'''

A3_OLD = '''        if s["missing_canon"]:
            hard_fail.append("UNRESOLVED tokens (no canon entry): %s" % ", ".join(s["missing_canon"]))'''
A3_NEW = '''        if s["missing_canon"]:
            hard_fail.append("UNRESOLVED tokens (no canon entry): %s" % ", ".join(s["missing_canon"]))
        # CAST GATE judgment (registry law, HARD): every @id must be a locked
        # citizen with frozen reference_urls. Disk read only -- NEVER network.
        if s.get("at_tokens"):
            apath = Path(args.assets) if args.assets else None
            if apath is None:
                cand = Path(args.src).resolve().parent.parent / "assets.json"
                apath = cand if cand.exists() else None
            if apath is None or not apath.exists():
                hard_fail.append("CAST TOKENS %s but NO assets.json found "
                                 "(pass --assets or place the src at "
                                 "<channel>/projects/<slug>-src) -- an @-film "
                                 "cannot be gated without the registry"
                                 % ["@" + a for a in s["at_tokens"]])
            else:
                try:
                    reg = json.load(open(apath))
                except Exception as e:
                    reg = None
                    hard_fail.append("assets.json UNREADABLE at %s (%s)"
                                     % (apath, type(e).__name__))
                if reg is not None:
                    bad_unknown, bad_nourls, cast = [], [], []
                    for a in s["at_tokens"]:
                        rec = reg.get("@" + a) or reg.get(a)
                        if not rec:
                            bad_unknown.append("@" + a)
                        elif not rec.get("reference_urls"):
                            bad_nourls.append("@" + a)
                        else:
                            cast.append("@%s(%d refs%s)"
                                        % (a, len(rec["reference_urls"]),
                                           ", density_exempt"
                                           if rec.get("density_exempt") else ""))
                    if bad_unknown:
                        hard_fail.append("UNKNOWN CAST %s -- not in %s. Lock "
                                         "them (S3) or fix the mention."
                                         % (bad_unknown, apath))
                    if bad_nourls:
                        hard_fail.append("CAST WITHOUT FROZEN REFS %s -- run "
                                         "the registry --refresh to freeze "
                                         "the fal snapshot." % bad_nourls)
                    if cast:
                        print("  cast: %s [%s]" % (", ".join(cast), apath))'''

def main():
    if not TARGET.exists():
        sys.exit("ABORT: %s not found" % TARGET)
    src = TARGET.read_text()
    if MARK in src:
        print("already patched (%s present) -- nothing to do" % MARK)
        return
    for name, anchor in (("A1", A1_OLD), ("A2", A2_OLD), ("A3", A3_OLD)):
        if src.count(anchor) != 1:
            sys.exit("ABORT: anchor %s matches %d times (need exactly 1) -- "
                     "intake.py has drifted; re-read before patching"
                     % (name, src.count(anchor)))
    out = (src.replace(A1_OLD, A1_NEW)
              .replace(A2_OLD, A2_NEW)
              .replace(A3_OLD, A3_NEW))
    bak = TARGET.with_name(TARGET.name + ".pre_cast_gate")
    shutil.copy2(TARGET, bak)
    tmp = TARGET.with_name(TARGET.name + ".tmp_cast_gate")
    tmp.write_text(out)
    py_compile.compile(str(tmp), doraise=True)
    tmp.replace(TARGET)
    print("patched %s (backup %s)" % (TARGET, bak.name))

if __name__ == "__main__":
    main()
