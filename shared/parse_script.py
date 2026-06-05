#!/usr/bin/env python3
"""
parse_script.py - Step 1 of the Synthetic dual-mode pipeline.

Reads a tagged script.md (the source of truth) and emits an ordered list of
beats, each tagged mode "A" (cinematic recreation) or "B" (Remotion graphic).
Mode B beats carry the component name + parsed payload - which IS the render spec.
Spoken found-lines (the > "..." quotes above a QuoteCard) attach as that beat's
narration, so nothing the narrator says is lost.

This step does NO rendering. Run it, read the beats, confirm every B beat has a
complete payload and every QuoteCard carries its spoken found-line. That is the
whole test for Step 1.

Usage:
    python parse_script.py path/to/script.md
    python parse_script.py path/to/script.md --json beats.json
"""

import sys
import re
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import Optional

# The only legal Mode B components - exactly the six built in the prototype.
# A tag outside this set is the deliberate "seventh component" signal.
KNOWN_COMPONENTS = {
    "HighlightedHeadline", "LowerThird", "NumberCounter",
    "ChapterCard", "QuoteCard", "DocumentReveal",
}

BEAT_RE      = re.compile(r"^\s*\*{0,2}\[(A|B):?([^\]]*)\]\*{0,2}\s*(.*)$")
SILENCE_RE   = re.compile(r"^\s*\*{0,2}\[SILENCE[^\]]*\]\*{0,2}", re.IGNORECASE)
HEADING_RE   = re.compile(r"^\s*#")
CUE_RE       = re.compile(r"^\s*\*.*[Nn]arrator.*\*\s*$")          # *Narrator, ...:* stage cue
VERIFY_RE    = re.compile(r"VERIFY", re.IGNORECASE)
BLOCKQUOTE_RE= re.compile(r"^\s*>\s*(.+?)\s*$")
KV_COLON_RE  = re.compile(r"^\s+([a-zA-Z_]\w*):\s*(.+?)\s*$")      # highlight: "x"  /  source: y
KV_EQ_RE     = re.compile(r"([a-zA-Z_]\w*)=(\"[^\"]*\"|'[^']*'|\S+)")
VISUAL_RE    = re.compile(r"\*?\s*VISUAL:\s*(.*?)\*?\s*$", re.IGNORECASE)


@dataclass
class Beat:
    index: int
    mode: str                                   # "A" or "B"
    component: Optional[str] = None             # B only
    payload: dict = field(default_factory=dict) # B only
    narration: str = ""                         # spoken words for this beat
    found_line: str = ""                        # the real quoted line, if any (QuoteCards)
    visual: str = ""                            # A only: the VISUAL: direction
    face_hold: bool = False                     # A only: rationed face-hold
    silence_after: bool = False
    warnings: list = field(default_factory=list)


def _coerce(val: str):
    v = val.strip().strip('"').strip("'")
    low = v.lower()
    if low in ("true", "false"):
        return low == "true"
    cleaned = v.replace(",", "")
    if re.fullmatch(r"-?\d+", cleaned):
        return int(cleaned)
    if re.fullmatch(r"-?\d*\.\d+", cleaned):
        return float(cleaned)
    return v


def _parse_eq(text: str) -> dict:
    return {m.group(1): _coerce(m.group(2)) for m in KV_EQ_RE.finditer(text)}


def _strip_md(s: str) -> str:
    return s.strip().strip("*").strip().lstrip(">").strip()


def parse_script(path: str):
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f.readlines()]

    # Parse only the body: from the first COLD OPEN / PART heading...
    start = 0
    for i, ln in enumerate(lines):
        if re.match(r"^\s*##\s+(COLD OPEN|PART )", ln, re.IGNORECASE):
            start = i
            break
    # ...to before the trailing spec/ledger/verification sections.
    end = len(lines)
    for i in range(start, len(lines)):
        if re.match(r"^\s*##\s+(Mode B component spec|Thread\s*/\s*debt|Verification)",
                    lines[i], re.IGNORECASE):
            end = i
            break

    beats = []
    pending_narr = []   # plain narration seen since the last beat tag
    pending_found = []  # blockquote found-lines seen since the last beat tag
    idx = 0
    i = start

    def flush_into(beat: Beat):
        # pre-tag buffered lines belong to this beat
        if pending_found:
            beat.found_line = " ".join(pending_found).strip()
        pre = pending_found + pending_narr
        if pre:
            beat.narration = (" ".join(pre) + (" " + beat.narration if beat.narration else "")).strip()
        pending_found.clear()
        pending_narr.clear()

    while i < end:
        line = lines[i]
        stripped = line.strip()

        # blank line - boundary only; buffer persists
        if stripped == "":
            i += 1
            continue

        # silence marker - attach to most recent beat
        if SILENCE_RE.match(line):
            if beats:
                beats[-1].silence_after = True
            i += 1
            continue

        # narrator stage cue - not spoken, skip
        if CUE_RE.match(line):
            i += 1
            continue

        # heading (not a beat) - skip
        if HEADING_RE.match(line) and not BEAT_RE.match(line):
            i += 1
            continue

        m = BEAT_RE.match(line)
        if not m:
            # orphan content line: a found-line (blockquote) or plain narration
            bq = BLOCKQUOTE_RE.match(line)
            if bq:
                pending_found.append(_strip_md(bq.group(1)).strip('"'))
            elif re.fullmatch(r"[-*_]{3,}", stripped):
                pass  # horizontal rule
            elif stripped.startswith("*") and stripped.endswith("*"):
                pass  # italic production note / section descriptor - never spoken
            elif stripped.startswith("(") and VERIFY_RE.search(stripped):
                pass  # stray verify note
            else:
                pending_narr.append(_strip_md(line))
            i += 1
            continue

        # --- a beat tag ---
        mode = m.group(1)
        comp = m.group(2).strip().split()[0] if m.group(2).strip() else ""
        trailing = m.group(3).strip()

        beat = Beat(index=idx, mode=mode)

        if mode == "B":
            beat.component = comp
            if comp not in KNOWN_COMPONENTS:
                beat.warnings.append(
                    f"UNKNOWN COMPONENT '{comp}' - not one of the six (seventh-component signal)."
                )
            # payload from the tag line's trailing text
            if "=" in trailing:
                beat.payload.update(_parse_eq(trailing))
            elif trailing.startswith('"'):
                q = re.match(r'"([^"]+)"', trailing)
                if q:
                    beat.payload["text"] = q.group(1)
            elif trailing:
                beat.payload["text"] = trailing  # bare title (LowerThird, DocumentReveal, end card)

            # payload from indented continuation lines
            j = i + 1
            while j < end:
                nxt = lines[j]
                if nxt.strip() == "" or BEAT_RE.match(nxt) or HEADING_RE.match(nxt) or SILENCE_RE.match(nxt):
                    break
                ns = nxt.strip().strip("*").strip()
                if ns.startswith("(") and VERIFY_RE.search(ns):   # verify note - skip
                    j += 1
                    continue
                cm = KV_COLON_RE.match(nxt)
                if cm:
                    beat.payload[cm.group(1)] = _coerce(cm.group(2))
                elif "=" in nxt:
                    beat.payload.update(_parse_eq(nxt))
                j += 1
            i = j
            flush_into(beat)   # attach any spoken found-line buffered before this card

        else:  # mode == "A"
            block = [trailing] if trailing else []
            j = i + 1
            while j < end:
                nxt = lines[j]
                if nxt.strip() == "" or BEAT_RE.match(nxt) or HEADING_RE.match(nxt) or SILENCE_RE.match(nxt):
                    break
                block.append(nxt.strip())
                j += 1
            i = j
            flush_into(beat)   # pre-tag narration ("With those four words...") attaches here
            for seg in block:
                vm = VISUAL_RE.search(seg)
                if vm and not beat.visual:
                    beat.visual = _strip_md(vm.group(1))
                    if "\u2b50" in seg:
                        beat.face_hold = True
                else:
                    clean = _strip_md(seg)
                    if clean and not clean.upper().startswith("VISUAL:"):
                        beat.narration = (beat.narration + " " + clean).strip()

        beats.append(beat)
        idx += 1

    return beats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--json")
    args = ap.parse_args()

    beats = parse_script(args.script)
    a  = sum(1 for b in beats if b.mode == "A")
    bb = sum(1 for b in beats if b.mode == "B")
    comp_counts, warnings = {}, []
    for b in beats:
        if b.mode == "B":
            comp_counts[b.component] = comp_counts.get(b.component, 0) + 1
        for w in b.warnings:
            warnings.append((b.index, w))

    print(f"\n=== {args.script} ===")
    print(f"{len(beats)} beats  |  A: {a}  B: {bb}  ({bb/len(beats)*100:.0f}% Mode B)\n")
    for b in beats:
        tag = b.mode if b.mode == "A" else f"B:{b.component}"
        star = " FACE" if b.face_hold else ""
        sil = " ...silence" if b.silence_after else ""
        print(f"[{b.index:02d}] ({tag}){star}{sil}")
        if b.mode == "B":
            print(f"     payload: {b.payload}")
            if b.found_line:
                print(f"     spoken : \"{b.found_line}\"")
        else:
            if b.visual:
                print(f"     visual : {b.visual[:78]}")
            if b.narration:
                print(f"     narr   : {b.narration[:88]}{'...' if len(b.narration) > 88 else ''}")
        for w in b.warnings:
            print(f"     !! {w}")
        print()

    print("--- Mode B component tally (this IS the wiring list) ---")
    for comp, n in sorted(comp_counts.items()):
        flag = "" if comp in KNOWN_COMPONENTS else "   XX UNKNOWN"
        print(f"  {comp:20s} x{n}{flag}")
    if warnings:
        print("\n--- WARNINGS ---")
        for idx, w in warnings:
            print(f"  beat {idx}: {w}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump([asdict(b) for b in beats], f, indent=2, ensure_ascii=False)
        print(f"\nWrote {args.json}")


if __name__ == "__main__":
    main()
