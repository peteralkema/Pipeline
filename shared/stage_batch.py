#!/usr/bin/env python3
"""
stage_batch.py - the front door for the batch-of-batches.

Takes a ZIP of <name>.md + <name>.thumb.json pairs (any mix of channels),
runs every gate the real run would, AUTO-FIXES the mechanical problems
(filename slug + non-ASCII content), REJECTS the ones that need authoring
fixes, and on --commit routes the clean pairs into each <channel>/batch_inbox/.

By default it is REPORT-ONLY (stages nothing). Read the report, fix the
rejects, re-run; pass --commit to actually move the clean pairs into the
inboxes. A green report is a real guarantee: it reuses ingest.validate_slug,
ingest.verify_beats, ingest._resolve_channel_folder, ingest._parse_header_channel
and the real parse_script.py, so "staged & ready" == "the batch won't prep-fail".

The zip is throwaway transport: auto-fixes are applied to the staged copies on
the box only; nothing is written back to your source.

Usage (BOX):
    python shared/stage_batch.py --zip ~/incoming/batch.zip            # report only
    python shared/stage_batch.py --zip ~/incoming/batch.zip --commit   # stage the clean pairs
    python shared/stage_batch.py --zip ~/incoming/batch.zip --commit --plan-out shared/plan_next.json
"""
import argparse
import json
import re
import shutil
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path

# --- locate the repo + import the REAL ingest helpers -----------------------
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "shared"))
try:
    from mission_control import ingest
except Exception as e:  # pragma: no cover
    sys.stderr.write(f"FATAL: cannot import mission_control.ingest: {e}\n")
    sys.exit(2)

PARSE_SCRIPT = REPO / "shared" / "parse_script.py"

# --- content normalisation (the "auto-fix non-ASCII" rule) ------------------
# Map the common script-choking characters to ASCII. Em/en dashes -> the
# escaped em-dash the scripts use elsewhere is "-"; we go to plain hyphen here
# because narration should be plain ASCII. Smart quotes -> straight.
_CHAR_MAP = {
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"',
    "\u2013": "-", "\u2014": "-", "\u2015": "-",
    "\u2026": "...", "\u00a0": " ", "\u00ab": '"', "\u00bb": '"',
    "\u2032": "'", "\u2033": '"', "\u2212": "-",
}


def normalise_content(text: str):
    """Return (clean_text, changed_bool). Maps known smart chars, then strips
    any remaining non-ASCII, reporting whether anything changed."""
    original = text
    for bad, good in _CHAR_MAP.items():
        text = text.replace(bad, good)
    # strip any other non-ASCII that survived (accents -> base where possible)
    if any(ord(c) > 127 for c in text):
        text = (unicodedata.normalize("NFKD", text)
                .encode("ascii", "ignore").decode("ascii"))
    return text, (text != original)


# --- filename slug normalisation (the "auto-rename" rule) -------------------
def normalise_slug(stem: str):
    """Return (clean_slug, changed_bool). Lowercase, underscores/spaces->hyphen,
    strip other illegal chars, collapse repeats, trim edge hyphens."""
    s = stem.lower()
    s = s.replace("_", "-").replace(" ", "-")
    s = re.sub(r"[^a-z0-9-]", "", s)   # drop anything not allowed
    s = re.sub(r"-{2,}", "-", s)        # collapse runs of hyphens
    s = s.strip("-")                    # no leading/trailing hyphen
    return s, (s != stem)


# --- one pair's verdict -----------------------------------------------------
class Pair:
    def __init__(self, stem):
        self.orig_stem = stem
        self.slug = stem
        self.src_zip = None          # which zip this pair came from
        self.md = None
        self.thumb = None
        self.channel = None          # resolved folder name
        self.beats = None
        self.notes = []              # auto-fixes applied (informational)
        self.errors = []             # rejections (must fix at source)
        self.clean_md_text = None    # normalised content, staged on commit
        self.clean_thumb_text = None

    @property
    def ok(self):
        return not self.errors


def main():
    ap = argparse.ArgumentParser(description="Stage zip(s) of script/thumb pairs into batch inboxes.")
    ap.add_argument("--zip", nargs="+", default=None,
                    help="one or more .zip files of <name>.md + <name>.thumb.json pairs (one per channel is fine)")
    ap.add_argument("--zip-dir", default=None,
                    help="a directory; every *.zip inside it is processed together")
    ap.add_argument("--commit", action="store_true",
                    help="actually route clean pairs into <channel>/batch_inbox/ (default: report only)")
    ap.add_argument("--plan-out", default=None,
                    help="optional: write a run_all_batches plan file skeleton for the staged channels")
    args = ap.parse_args()

    # resolve the set of zips from --zip and/or --zip-dir
    zip_paths = []
    if args.zip:
        zip_paths += [Path(z).expanduser() for z in args.zip]
    if args.zip_dir:
        d = Path(args.zip_dir).expanduser()
        if not d.is_dir():
            sys.stderr.write(f"FATAL: --zip-dir not a directory: {d}\n")
            sys.exit(2)
        zip_paths += sorted(d.glob("*.zip"))
    if not zip_paths:
        sys.stderr.write("FATAL: give --zip <file...> and/or --zip-dir <dir>\n")
        sys.exit(2)
    # dedupe, preserve order
    seen = set()
    zip_paths = [z for z in zip_paths if not (z in seen or seen.add(z))]
    for z in zip_paths:
        if not z.is_file():
            sys.stderr.write(f"FATAL: zip not found: {z}\n")
            sys.exit(2)

    work = Path(tempfile.mkdtemp(prefix="stage_batch_"))
    # extract every zip into its OWN subdir of work, so we can track provenance
    # and so identical stems in different zips don't clobber each other on disk.
    extracted = []  # list of (zip_name, extract_root)
    for z in zip_paths:
        sub = work / f"_z{len(extracted)}_{z.stem}"
        sub.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(z) as zf:
                zf.extractall(sub)
        except zipfile.BadZipFile:
            sys.stderr.write(f"FATAL: not a valid zip: {z}\n")
            shutil.rmtree(work, ignore_errors=True)
            sys.exit(2)
        extracted.append((z.name, sub))

    # gather all .md and .thumb.json across all zips, keyed by stem.
    # track which zip each came from (provenance) and flag cross-zip stem clashes.
    mds, thumbs, src = {}, {}, {}
    stem_zips = {}  # stem -> set of zip names it appeared in
    for zip_name, root in extracted:
        for p in root.rglob("*"):
            if p.is_file():
                n = p.name
                if n.endswith(".thumb.json"):
                    stem = n[:-len(".thumb.json")]
                elif n.endswith(".md"):
                    stem = n[:-len(".md")]
                else:
                    continue
                stem_zips.setdefault(stem, set()).add(zip_name)
                if n.endswith(".thumb.json"):
                    thumbs[stem] = p
                else:
                    mds[stem] = p
                src[stem] = zip_name

    stems = sorted(set(mds) | set(thumbs))
    if not stems:
        sys.stderr.write("FATAL: no .md or .thumb.json files found in the zip(s)\n")
        shutil.rmtree(work, ignore_errors=True)
        sys.exit(2)

    pairs = []
    for stem in stems:
        pr = Pair(stem)
        pr.src_zip = src.get(stem)
        pr.md = mds.get(stem)
        pr.thumb = thumbs.get(stem)

        # cross-zip clash: the same stem appeared in more than one zip
        if len(stem_zips.get(stem, ())) > 1:
            pr.errors.append("same name appears in more than one zip - rename one")
            pairs.append(pr); continue

        # GATE: pairing
        if pr.md is None:
            pr.errors.append(f"orphan thumb (no {stem}.md)")
            pairs.append(pr); continue
        if pr.thumb is None:
            pr.errors.append(f"orphan script (no {stem}.thumb.json)")
            pairs.append(pr); continue

        # AUTO-FIX: filename slug
        clean_slug, slug_changed = normalise_slug(stem)
        slug_err = ingest.validate_slug(clean_slug)
        if slug_err:
            pr.errors.append(f"filename cannot be normalised to a valid slug: {slug_err}")
            pairs.append(pr); continue
        pr.slug = clean_slug
        if slug_changed:
            pr.notes.append(f"renamed '{stem}' -> '{clean_slug}'")

        # AUTO-FIX: content non-ASCII (both files)
        md_text = pr.md.read_text(encoding="utf-8", errors="replace")
        clean_md, md_changed = normalise_content(md_text)
        pr.clean_md_text = clean_md
        if md_changed:
            pr.notes.append("normalised non-ASCII in script")

        thumb_text = pr.thumb.read_text(encoding="utf-8", errors="replace")
        clean_thumb, th_changed = normalise_content(thumb_text)
        pr.clean_thumb_text = clean_thumb
        if th_changed:
            pr.notes.append("normalised non-ASCII in thumb")

        # GATE: thumb schema (subject + title non-empty) -- create_project does NOT check this
        try:
            tj = json.loads(clean_thumb)
        except json.JSONDecodeError as e:
            pr.errors.append(f"thumb.json is not valid JSON: {e}")
            pairs.append(pr); continue
        for key in ("subject", "title"):
            if not (tj.get(key) or "").strip():
                pr.errors.append(f"thumb.json missing '{key}'")
        if pr.errors:
            pairs.append(pr); continue

        # GATE: channel header resolves to a real folder
        header_channel = ingest._parse_header_channel(clean_md)
        if not header_channel:
            pr.errors.append("no 'channel:' line in script header")
            pairs.append(pr); continue
        folder = ingest._resolve_channel_folder(header_channel)
        if not folder:
            pr.errors.append(f"channel '{header_channel}' has no channel.json folder")
            pairs.append(pr); continue
        pr.channel = folder

        # GATE: slug collision with an existing project
        if (REPO / folder / "projects" / pr.slug).is_dir():
            pr.errors.append(f"project '{pr.slug}' already exists in {folder}/projects/")
            pairs.append(pr); continue

        # GATE: parse + verify_beats (the REAL no_visual/wordless check)
        tmp_md = work / f"_check_{pr.slug}.md"
        tmp_md.write_text(clean_md, encoding="utf-8")
        tmp_full = work / f"_check_{pr.slug}.full.json"
        import subprocess
        proc = subprocess.run(
            [sys.executable, str(PARSE_SCRIPT), str(tmp_md),
             "--json-full", str(tmp_full)],
            capture_output=True, text=True)
        if proc.returncode != 0:
            msg = (proc.stderr or proc.stdout or "parse failed").strip().splitlines()[-1]
            pr.errors.append(f"parse failed: {msg}")
            pairs.append(pr); continue
        try:
            full = json.loads(tmp_full.read_text())
            beats_only = work / f"_check_{pr.slug}.beats.json"
            beats_only.write_text(json.dumps(full["beats"]))
            v = ingest.verify_beats(beats_only)
        except Exception as e:
            pr.errors.append(f"verify failed: {e}")
            pairs.append(pr); continue
        pr.beats = v["beats"]
        if not v["ok"]:
            if v["wordless"]:
                pr.errors.append(f"{len(v['wordless'])} wordless beats: {v['wordless'][:12]}")
            if v["no_visual"]:
                pr.errors.append(f"{len(v['no_visual'])} no_visual beats: {v['no_visual'][:12]}")
            pairs.append(pr); continue

        pairs.append(pr)

    # ---- COMMIT (route clean pairs into inboxes) ----
    staged_by_channel = {}
    if args.commit:
        for pr in pairs:
            if not pr.ok:
                continue
            inbox = REPO / pr.channel / "batch_inbox"
            inbox.mkdir(parents=True, exist_ok=True)
            (inbox / f"{pr.slug}.md").write_text(pr.clean_md_text, encoding="utf-8")
            (inbox / f"{pr.slug}.thumb.json").write_text(pr.clean_thumb_text, encoding="utf-8")
            staged_by_channel.setdefault(pr.channel, []).append(pr.slug)
    else:
        for pr in pairs:
            if pr.ok:
                staged_by_channel.setdefault(pr.channel, []).append(pr.slug)

    shutil.rmtree(work, ignore_errors=True)

    # ---- REPORT ----
    clean = [p for p in pairs if p.ok]
    bad = [p for p in pairs if not p.ok]
    fixes = [p for p in clean if p.notes]

    print("=" * 64)
    src_label = (f"{len(zip_paths)} zips" if len(zip_paths) > 1
                 else zip_paths[0].name)
    print(f"STAGE BATCH  -  {src_label}  -  {'COMMITTED' if args.commit else 'REPORT ONLY (nothing staged)'}")
    print("=" * 64)

    if fixes:
        print("\nAUTO-FIXES APPLIED (staged copies only; source untouched):")
        for p in fixes:
            for n in p.notes:
                print(f"  [{p.slug}] {n}")

    verb = "STAGED & READY" if args.commit else "READY TO STAGE"
    print(f"\n{verb} (per channel):")
    if staged_by_channel:
        width = max(len(c) for c in staged_by_channel)
        total = 0
        for ch in sorted(staged_by_channel):
            n = len(staged_by_channel[ch])
            total += n
            print(f"  {ch.ljust(width)} ..  {n}")
        print(f"  {'-' * (width + 8)}")
        print(f"  {'TOTAL'.ljust(width)} ..  {total}  across {len(staged_by_channel)} channel(s)")
    else:
        print("  (none - every pair was rejected)")

    if bad:
        print(f"\nREJECTED ({len(bad)}) - fix at source and re-run (nothing from these staged):")
        for p in bad:
            print(f"  {p.orig_stem}")
            for e in p.errors:
                print(f"       - {e}")

    print()
    if args.commit and staged_by_channel:
        chans = ", ".join(sorted(staged_by_channel))
        print(f"Staged into: {chans}")
        print("Next: build/point a plan file at these channels, then")
        print("      python shared/run_all_batches.py --plan-file <plan> --plan   (dry run)")
        print("      python shared/run_all_batches.py --plan-file <plan>          (real, in tmux)")
    elif not args.commit and not bad:
        print("All pairs clean. Re-run with --commit to stage them into the inboxes.")
    elif not args.commit and bad:
        print("Fix the REJECTED pairs at source, re-zip, and re-run. (--commit stages only when all-clean is your call;")
        print("clean pairs WILL stage on --commit even if others are rejected - rejected ones are simply skipped.)")

    # optional plan skeleton
    if args.plan_out and staged_by_channel:
        plan = {"_comment": f"auto-generated by stage_batch from {src_label} - SET publish_start/kling_count per channel",
                "channels": [
                    {"channel": ch, "inbox": f"{ch}/batch_inbox",
                     "kling_count": 2, "publish_start": "REPLACE_ME+02:00",
                     "publish_interval_hours": 24}
                    for ch in sorted(staged_by_channel)]}
        Path(args.plan_out).write_text(json.dumps(plan, indent=2))
        print(f"\nPlan skeleton written: {args.plan_out}  (edit publish_start + kling_count before running)")

    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
