# Troy Drift — ROOT CAUSE LOCATED (diagnosis complete)

*Destination in repo: `shared/docs/TROY-DRIFT-ROOT-CAUSE-FOUND.md`*
*Supersedes the hypotheses in TROY-DRIFT-ANALYSIS-AND-DIAGNOSTIC-PLAN.md. Captured 8 June 2026.*

## THE VERDICT (where the bug is)
The drift is in **the duration TABLE (`durations.json`), built upstream by
`build_beat_durations.py` / `align_with_whisper.py`** — NOT in the video conform, NOT in
concat, NOT in the assembler. Each beat's `audio_start` (and `duration`) is systematically
LARGER than where the beat's words actually occur in the voiceover. The error accumulates,
then the final tail beats collapse to claw the total back to the voice length.

## THE EVIDENCE (how we know)
### Filmora: audio runs AHEAD of video, growing cumulatively
Peter's 4 hand-measured points (where words are HEARD in final_video vs where the matching
shot is SHOWN):
  beat 32:  heard 05:13 (313s) | shown 05:16 — audio ahead ~3s
  beat 70:  heard 11:11 (671s) | shown 11:20 — audio ahead ~9s
  beat 114: heard 18:19 (1099s)| shown 18:51 — audio ahead ~32s
  beat 141: heard 22:44 (1364s)| shown 23:17 — audio ahead ~33s
Plus: the final video is 25:16; shots 152/153/154 (the three 0.3s tail beats) flash by in the
last ~1s. => video LAGS audio throughout, tail beats absorb the accumulated lag at the end.
=> total length matches voice (which masked it), but internal alignment drifts then snaps.

### Conform is FAITHFUL (ruled out)  [diagnose_conform.py]
Re-ran make_video_segment's exact slow-fill ffmpeg on beats 1,32,70,114,141:
overshoot = -0.013, +0.013, +0.013, +0.000, +0.007 s. Mean +0.004s/beat (~0.6s over 154 beats).
=> the conform produces each clip at its intended duration. NOT the bug. (My first script,
diagnose_drift.py, wrongly measured the RAW pooled 5s clips in clips/ — inputs, not output —
and produced an invalid "video is half length" verdict. Disregard that script's verdict.)

### The duration TABLE is mis-distributed (the smoking gun)
`audio_start` (durations.json) vs where Peter HEARD the words:
  beat 32:  audio_start=321.9s  vs heard 313s   => +8.9s
  beat 70:  audio_start=693.5s  vs heard 671s   => +22.5s
  beat 114: audio_start=1139.0s vs heard 1099s  => +40.0s
  beat 141: audio_start=1410.5s vs heard 1364s  => +46.5s
Monotonically growing. And: voiceover words exist 0.0s -> 1515.2s, but beats 151/152/153 all
sit at audio_start=1515.4s (past the last word), each 0.3s — the collapsed tail that absorbs
the accumulated overshoot. sum(durations)=1516.26s ~= voice 1515.94s (totals match; the
DISTRIBUTION is wrong).

## MECHANISM
durations.json allocates each beat MORE time than its words actually occupy in the voiceover.
The cumulative audio_start therefore runs ahead of the real spoken position (reaching ~+46s by
beat 141). Because the assembler faithfully renders each beat for its (inflated) duration and
concatenates them, the VIDEO falls progressively behind the (correct, continuous) VOICE. The
last beats are compressed to 0.3s so the totals still meet at 1516s — the snap-back that
fooled us into thinking it was in sync at the end.

## WHERE TO FIX (next session — its own focused run, fresh eyes)
`build_beat_durations.py` + `align_with_whisper.py`. Something inflates per-beat duration vs
pure Whisper word-boundary timing — candidates: a per-beat additive (a surviving padding
remnant), a words-estimate blended with the Whisper measurement, or a word->beat boundary
mapping that drifts. The continuous-narration cleanup removed holds from the ASSEMBLER but the
duration BUILDER is where audio_start/duration are computed — the remnant likely lives there.

### The fix target (what correct looks like)
For each beat, derive timing PURELY from Whisper word timestamps:
  audio_start[beat] = Whisper start-time of the beat's FIRST spoken word
  duration[beat]    = (next beat's first-word start) - (this beat's first-word start)
No additions, no estimates, no padding. Then audio_start must match where the words are HEARD.

### Confirm-the-fix test
After fixing, re-run the audio_start-vs-heard check on beats 32/70/114/141 — they should match
(gap ~0) instead of +9/+22/+40/+46. Then re-run a SHORT 4-6 beat episode end-to-end and verify
in the player that picture changes land on the words. Only then re-run a long episode.

## TOOLS BUILT THIS SESSION (committed)
- `shared/diagnose_drift.py` — 3-timeline probe. NOTE: measures pooled clips/ (raw inputs);
  its sum(rendered) verdict is INVALID for conformed output. Keep for the audio_start/spoken
  comparison columns, ignore its "half length" conclusion.
- `shared/diagnose_conform.py` — re-conforms sample beats, measures actual vs intended duration.
  CORRECT tool; proved conform is faithful. Use `--all` to sum across every beat.

## REMINDER
Total-length-matches-voice is NOT proof of sync — it can hide internal drift that snaps back at
the end (as here). Always check INTERNAL alignment (audio_start vs heard, per-beat), not just totals.
