#!/usr/bin/env python3
"""
patch_durations_no_holds.py — remove fabricated silent-hold durations from
build_beat_durations.py, per the continuous-narration model.

Same idempotent style as patch_animate_only.py. Run from repo root:
    python shared/patch_durations_no_holds.py

WHY: build_beat_durations.py currently splits beats into spoken (Whisper-measured)
and silent (a fabricated `default_hold`, 2.5s, source "silent_hold"). Under the
continuous-narration model there is ONE protected voice track and NO codified
silence — every beat carries spoken words, and a wordless beat is an AUTHORING
ERROR, not a hold to invent. This patch deletes the silent-hold fabrication: a
wordless beat gets duration 0.0 and source "no_narration", surfaced loudly, so it
can never be silently held again. (The aligner scaffold still filters to spoken
beats — a wordless beat has no words to align — but the MERGE no longer invents
time for it.)

Idempotent + self-verifying (ast-parse). Backs up to build_beat_durations.py.pre_no_holds.
"""
import sys, ast, shutil
from pathlib import Path

TARGET = Path(__file__).parent / "build_beat_durations.py"

# ── Edit 1: the merge branch (replace silent_hold fabrication) ─────────────
MERGE_ANCHOR = '''    durations = {}
    for m in manifest:
        idx = m["index"]
        if m.get("spoken"):
            d = spoken_dur.get(idx, {"duration": 0.0, "source": "whisper_MISSING"})
        else:
            d = {"duration": round(float(m.get("default_hold", 2.5)), 3), "source": "silent_hold"}
        d["frames"] = round(d["duration"] * args.fps)
        d["mode"] = m["mode"]
        d["component"] = m.get("component")
        durations[str(idx)] = d
'''
MERGE_REPLACE = '''    durations = {}
    n_no_narr = 0
    for m in manifest:
        idx = m["index"]
        if m.get("spoken"):
            d = spoken_dur.get(idx, {"duration": 0.0, "source": "whisper_MISSING"})
        else:
            # Continuous-narration model: every beat MUST carry spoken words. A wordless
            # beat is an AUTHORING ERROR, not a silent hold to fabricate. Assign 0s and
            # mark it loudly rather than inventing time the protected voice track does not
            # contain. (No more default_hold / silent_hold.)
            d = {"duration": 0.0, "source": "no_narration"}
            n_no_narr += 1
        d["frames"] = round(d["duration"] * args.fps)
        d["mode"] = m["mode"]
        d["component"] = m.get("component")
        durations[str(idx)] = d
'''

# ── Edit 2: the summary counts ─────────────────────────────────────────────
SUMMARY_ANCHOR = '''    n_w = sum(1 for d in durations.values() if d["source"] == "whisper")
    n_s = sum(1 for d in durations.values() if d["source"] == "silent_hold")
    n_miss = sum(1 for d in durations.values() if d["source"] == "whisper_MISSING")
    print(f"\\n=== per-beat durations ===")
    print(f"wrote {args.out}")
    print(f"{len(durations)} beats: {n_w} whisper-measured, {n_s} silent-hold"
          + (f", {n_miss} MISSING" if n_miss else ""))
'''
SUMMARY_REPLACE = '''    n_w = sum(1 for d in durations.values() if d["source"] == "whisper")
    n_nn = sum(1 for d in durations.values() if d["source"] == "no_narration")
    n_miss = sum(1 for d in durations.values() if d["source"] == "whisper_MISSING")
    print(f"\\n=== per-beat durations ===")
    print(f"wrote {args.out}")
    print(f"{len(durations)} beats: {n_w} whisper-measured"
          + (f", {n_nn} NO-NARRATION (authoring error)" if n_nn else "")
          + (f", {n_miss} MISSING" if n_miss else ""))
'''

# ── Edit 3: the closing warning (add no-narration warning) ─────────────────
WARN_ANCHOR = '''    if n_miss:
        print("\\n!! some spoken beats got no Whisper match — alignment drift; check word counts.")
'''
WARN_REPLACE = '''    if n_no_narr:
        print(f"\\n!! {n_no_narr} beat(s) have NO narration. The continuous-narration model requires "
              f"every beat to carry spoken words; these are authoring errors (assigned 0s, NOT a hold). "
              f"Fix the script so every beat has narration, or promote/merge the beat.")
    if n_miss:
        print("\\n!! some spoken beats got no Whisper match — alignment drift; check word counts.")
'''

EDITS = [
    ('"no_narration"', MERGE_ANCHOR, MERGE_REPLACE, "merge branch (no silent_hold)"),
    ("NO-NARRATION (authoring error)", SUMMARY_ANCHOR, SUMMARY_REPLACE, "summary counts"),
    ("have NO narration. The continuous-narration", WARN_ANCHOR, WARN_REPLACE, "closing warning"),
]


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found. Run from repo root: python shared/patch_durations_no_holds.py")
    src = TARGET.read_text()
    original = src
    applied = []
    for marker, anchor, replacement, label in EDITS:
        if marker in src:
            print(f"skip: {label} already present.")
            continue
        if anchor not in src:
            sys.exit(f"FAIL: anchor for '{label}' not found — build_beat_durations.py changed. Nothing written.")
        if src.count(anchor) != 1:
            sys.exit(f"FAIL: anchor for '{label}' not unique ({src.count(anchor)}). Nothing written.")
        src = src.replace(anchor, replacement, 1)
        applied.append(label)

    if src == original:
        print("Already fully patched — no changes. No-op.")
        return

    try:
        ast.parse(src)
    except SyntaxError as e:
        sys.exit(f"FAIL: patched source does not parse ({e}). Nothing written.")

    backup = TARGET.with_suffix(".py.pre_no_holds")
    if not backup.exists():
        shutil.copy2(TARGET, backup)
        print(f"Backed up original -> {backup.name}")
    TARGET.write_text(src)
    print(f"OK wrote {TARGET.name} (compiles). Applied: {', '.join(applied)}")


if __name__ == "__main__":
    main()
