"""shared/v2/measure.py -- stage 2: frame-accurate per-beat audio measurement.

Reuse provenance: the alignment core is align_with_whisper.py, carried into
shared/v2/ VERBATIM and imported (normalize / words_in / build_sb_time_map --
the Troy-drift fix, difflib with autojunk disabled, interpolation across
mismatch gaps). This wrapper changes ONLY the two ends:
  in : beats rows from the project DB (ORDER BY id) instead of storyboard.json
  out: beats.audio_start / audio_duration / word_timestamps columns instead of
       JSON -- plus the per-word times the v1 flow computed and DISCARDED,
       kept here as word_timestamps JSON per beat (subtitles/lipsync later).

Whisper invocation matches the v1-documented command exactly:
  whisper voiceover.mp3 --model small --output_format json \
          --output_dir <project_dir> --word_timestamps True

Idempotence: if no beat has audio_duration NULL, no-op. Otherwise the whole
alignment recomputes and writes every beat (alignment is global by nature;
rewriting identical values is harmless and keeps the pass logic trivial).
"""
from __future__ import annotations
import difflib
import json
import subprocess
from pathlib import Path

import db as v2db
from align_with_whisper import build_sb_time_map, normalize, words_in

MIN_DURATION = 0.3
WHISPER_MODEL = "small"


def _ensure_whisper_json(project_dir: Path, voiceover_path: Path) -> Path:
    wj = project_dir / "voiceover.json"
    if wj.exists():
        return wj
    if not str(voiceover_path) or not Path(voiceover_path).is_file():
        raise SystemExit("stage 'measure': no voiceover.mp3 file -- run stage "
                         "'audio' first (guard: is_file, teaser receipt -- "
                         "Path('') resolves to '.' and whisper eats a directory)")
    cmd = ["whisper", str(voiceover_path), "--model", WHISPER_MODEL,
           "--output_format", "json", "--output_dir", str(project_dir),
           "--word_timestamps", "True"]
    print("   running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    if not wj.exists():
        raise SystemExit(f"whisper ran but {wj} did not appear")
    return wj


def _flatten_whisper(whisper_path: Path) -> list:
    """Whisper JSON -> flat [{word,start,end}] -- faithful to the v1 main()."""
    data = json.load(open(whisper_path))
    all_words = []
    for seg in data.get("segments", []):
        if seg.get("words"):
            for w in seg["words"]:
                token = normalize(w.get("word", ""))
                if not token:
                    continue
                for t in token.split():
                    all_words.append({"word": t, "start": w["start"], "end": w["end"]})
        else:
            tokens = words_in(seg.get("text", ""))
            if not tokens:
                continue
            dur = seg["end"] - seg["start"]
            per = dur / len(tokens)
            for i, t in enumerate(tokens):
                all_words.append({"word": t,
                                  "start": seg["start"] + i * per,
                                  "end": seg["start"] + (i + 1) * per})
    return all_words


def run(con, project_dir: Path) -> None:
    if not v2db.pending(con, "audio_duration"):
        print("   measure already done for every beat -- no-op")
        return

    proj = con.execute("SELECT * FROM project WHERE id=1").fetchone()
    whisper_path = _ensure_whisper_json(project_dir,
                                        Path(proj["voiceover_path"] or ""))
    all_words = _flatten_whisper(whisper_path)
    print(f"   whisper: {len(all_words)} words")

    beats = con.execute(
        "SELECT id, narration FROM beats ORDER BY id").fetchall()

    sb_tokens, first_idx, beat_token_spans = [], {}, {}
    for b in beats:
        start = len(sb_tokens)
        first_idx[b["id"]] = start
        toks = words_in(b["narration"])
        sb_tokens.extend(toks)
        beat_token_spans[b["id"]] = (start, len(sb_tokens))
    if not sb_tokens:
        raise SystemExit("no narration words in beats")

    last_audio_end = all_words[-1]["end"] if all_words else 0.0
    wh_tokens = [w["word"] for w in all_words]
    wh_times = [w["start"] for w in all_words]

    sb_time = build_sb_time_map(sb_tokens, wh_tokens, wh_times, last_audio_end)

    sm = difflib.SequenceMatcher(None, sb_tokens, wh_tokens, autojunk=False)
    matched = sum(bl.size for bl in sm.get_matching_blocks())
    coverage = matched / len(sb_tokens)

    starts = []
    for b in beats:
        idx = first_idx[b["id"]]
        starts.append(last_audio_end if idx >= len(sb_tokens)
                      else round(sb_time[idx], 3))
    starts[0] = 0.0
    for i in range(1, len(starts)):
        if starts[i] < starts[i - 1]:
            starts[i] = starts[i - 1]

    n_floored = 0
    for i, b in enumerate(beats):
        dur = ((starts[i + 1] if i + 1 < len(beats) else last_audio_end)
               - starts[i])
        dur = round(dur, 3)
        if dur < MIN_DURATION:
            dur = MIN_DURATION
            n_floored += 1
        s0, s1 = beat_token_spans[b["id"]]
        beat_end = starts[i + 1] if i + 1 < len(beats) else last_audio_end
        words = []
        for k in range(s0, s1):
            w_start = round(sb_time[k], 3)
            w_end = round(sb_time[k + 1] if k + 1 < len(sb_tokens)
                          else last_audio_end, 3)
            w_end = min(w_end, round(beat_end, 3)) if k == s1 - 1 else w_end
            words.append({"w": sb_tokens[k], "s": w_start, "e": w_end})
        v2db.mark(con, b["id"],
                  audio_start=starts[i],
                  audio_duration=dur,
                  word_timestamps=json.dumps(words, ensure_ascii=True),
                  status="measured")

    v2db.log_generation(
        con, stage="measure", model=f"whisper-{WHISPER_MODEL}",
        params_json=json.dumps({"coverage": round(coverage, 4),
                                "words": len(all_words),
                                "floored": n_floored}),
        result_path=str(whisper_path))
    con.commit()

    total = last_audio_end
    print(f"   measured {len(beats)} beats | audio {total:.1f}s "
          f"({total/60:.2f} min) | coverage {coverage*100:.1f}% "
          f"| floored {n_floored}")
    if coverage < 0.85:
        print(f"   !! LOW COVERAGE ({coverage*100:.1f}%) -- check the "
              f"voiceover.json belongs to THIS script.")
    if n_floored:
        print(f"   !! {n_floored} beat(s) hit the {MIN_DURATION}s floor -- "
              f"whisper likely dropped a beat's words; inspect them.")
