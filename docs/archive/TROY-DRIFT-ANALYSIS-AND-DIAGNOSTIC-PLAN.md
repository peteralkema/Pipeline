# Troy Output: Drift Situation + Diagnostic Script Plan

*Destination in repo: `shared/docs/TROY-DRIFT-ANALYSIS-AND-DIAGNOSTIC-PLAN.md`*
*Companion to: `SESSION-BRIEF-troy-drift-diagnosis.md`. Captured 8 June 2026.*

================================================================================
## PART 1 — THE SITUATION (what happened with the Troy final video)
================================================================================

### The output
The first full real episode through the completed orchestrator: project `troy`, channel `final_hours`,
**154 Mode-A beats, 0 Mode B**, final video **1516.03s (25:16), 1920x1080, 747 MB**. The orchestrator
ran the whole arc in one command: audio -> modeA (154 stills reviewed at the gate, 154 Kling clips) ->
convergence (pooled 154 clips -> assemble -> final_video.mp4).

### What was GOOD
The machine worked very well. Many stills and clips were excellent. Structure correct, the voice is one
continuous track, the episode assembled cleanly end to end at full length. The production quality is there.

### The PROBLEM
The audio does not correspond to what is on screen. The spoken narration and the visible still/clip for
a given beat fall out of alignment — what you hear describes something other than what you're seeing at
that moment. Peter had to import the whole 25-min video into Filmora, detach the audio, and manually
slide things back into sync until satisfied. That manual pass defeats the purpose of the automation for
this step — the entire reason to build the pipeline was to NOT do that by hand.

### Why this is strange (and what it rules OUT)
The pipeline timestamps carefully from the written beats -> the allocated still images. The beat->still
MAPPING is built deliberately (the index map `_index.json`, the `durations.json` per-beat table, all
Whisper-measured from the voice). So "the wrong picture is assigned to the wrong words" at the AUTHORING/
MAPPING level is almost certainly NOT the cause. If the mapping itself were scrambled, it would be wrong
from beat 1, uniformly — not "drift."

### Why "DRIFT" is the key word (what it points TO)
Peter described it as drift. Drift = error that ACCUMULATES: small or invisible at the start, worsening
as the video progresses. That signature is diagnostic. It means:

  The timeline the VIDEO is built on is diverging, a little per beat, from the timeline the VOICE
  actually occupies — and over 154 beats those little divergences compound into seconds of visible
  desync.

In other words: the INTENDED per-beat durations (from durations.json, measured from the voice) are
correct, but the ACTUAL rendered duration of each beat's video segment differs slightly from that
intended value. Each beat's video then starts a little earlier or later than its matching audio, and
the gap grows cumulatively down the timeline.

### The leading suspects (where a per-beat duration error could enter)
1. **Slow-fill precision (TOP suspect).** Each Mode A clip is a ~5s Kling clip stretched with
   `setpts=PTS*factor` to fill its beat's measured duration. If ffmpeg's ACTUAL output length comes out
   fractionally different from the requested target (e.g. 8.04s rendered for an 8.00s beat), that small
   error PER BEAT x 154 beats = several seconds of accumulated drift by the end. This matches "fine
   early, increasingly wrong later" precisely.
2. **Concat frame-rounding.** Concatenating 154 segments; if any segment isn't an exact integer number
   of frames at a constant FPS, frame-boundary rounding per segment accumulates across 154 joins.
3. **Float-seconds vs integer-frames.** Durations flow as float seconds (e.g. 8.2167s). Video is frames
   (at 30fps, 8.2167s = 246.5 frames — not a whole frame). However each segment resolves that half-frame,
   the residue per beat can accumulate.
4. **The voice-wins PIN can MASK and DISTORT the picture.** The assembler pins final output to the voice
   length (`-t voice_dur`). So the TOTAL length matches the voice and the END snaps back into alignment.
   That means the worst desync may appear in the MIDDLE (error grows, then is yanked back at the end),
   which can make diagnosis confusing if you only check the start and end.

### The ONE clue we still want from Peter (cheap, narrows everything)
When dragging audio in Filmora to fix it: was the video running consistently AHEAD of the voice, or
BEHIND it? (Equivalently: did you move audio earlier or later?)
- Video AHEAD of voice  => rendered clips are SHORTER than intended (video races ahead).
- Video BEHIND voice    => rendered clips are LONGER than intended (video lags).
And: was it worst in the MIDDLE (supports accumulate-then-pin) or steadily worse to the END (pin not
fully masking)? Either answer points at the mechanism before we run a line of code.

### Reframe (important, true)
This is NOT a fundamental flaw in the architecture. The continuous-narration model and voice-wins are
sound; the beat->still mapping is sound. This is a bounded VIDEO-SIDE duration-precision bug in the
conform/concat math. The Filmora pass was not wasted — it was the bug report that localized the symptom.
Fix the per-beat duration precision once, in the pipeline, and the manual Filmora step disappears forever.

================================================================================
## PART 2 — THE DIAGNOSTIC SCRIPT (how we find exactly where it breaks)
================================================================================

### Strategy: work from both ends, with NUMBERS not playback
We cannot (and need not) watch the video. Timing leaves a numerical trail. We compare, beat by beat:
  - INTENDED timeline  (from durations.json — what the voice says each beat should last)
  - ACTUAL timeline     (ffprobe the real rendered duration of each conformed clip)
  - and cross-check against the VOICE itself (voiceover.json word timestamps, voiceover.mp3 length).
Where the cumulative INTENDED-vs-ACTUAL gap starts growing is where drift originates. The shape of the
per-beat error (uniform? one-signed? a jump at one beat?) names the mechanism.

### Inputs (all already on the box, Troy project)
  final-hours/projects/troy/durations.json        # intended per-beat: {idx:{duration,frames,source,mode,component}}
  final-hours/projects/troy/_index.json           # beat -> shot map
  final-hours/projects/troy/voiceover.mp3         # the protected voice track (total length)
  final-hours/projects/troy/voiceover.json        # Whisper word timestamps (when each word is actually spoken)
  final-hours/projects/troy/clips/shot_NNN.mp4    # the 154 POOLED conformed clips (what convergence assembled)
  final-hours/projects/troy/modea/clips/shot_NNN.mp4  # the SOURCE Kling clips, PRE-conform (~5s each)

### What the script computes (the core table)
For each beat in order, a row:
  beat_idx | shot | intended_dur (durations.json) | source_clip_dur (pre-conform, modea/clips)
           | pooled_clip_dur (ffprobe clips/shot_NNN.mp4) | delta = pooled - intended
           | cumulative_drift (running sum of delta)
Plus summary lines:
  - sum(intended)         vs  voiceover.mp3 length        (should match — both derive from the voice)
  - sum(pooled_clip_dur)  vs  voiceover.mp3 length        (the REAL assembled video length pre-pin)
  - max cumulative_drift and the beat index where it peaks
  - mean delta, and whether deltas are mostly one-signed (systematic) or random (rounding noise)

### How to READ the output (decision tree)
- If `delta` is ~constant and one-signed across ALL beats (e.g. every pooled clip ~0.05s longer than
  intended): SYSTEMATIC conform error -> the slow-fill setpts (or trim) is not producing exactly the
  requested duration. FIX in make_video_segment (assemble_episode.py): build to an exact integer FRAME
  count, not a float `-t` seconds.
- If `delta` is ~0 for most beats but spikes at specific beats: those beats have something special
  (very short source clip -> extreme stretch? a placeholder? a probe failure?). Inspect those beats.
- If sum(pooled) ~= voice but cumulative_drift swings POSITIVE then back toward 0: classic
  accumulate-then-pin — the per-beat conform drifts, the final `-t voice_dur` pin yanks the total back.
  Confirms middle-worst desync. FIX = frame-exact per-beat durations so nothing drifts in the first place.
- If `pooled_clip_dur` matches `intended` well BUT desync still observed: the problem is NOT conform —
  look upstream at how durations.json maps to the voice (re-check the Whisper alignment / beat boundary
  mapping in build_beat_durations.py + align_with_whisper.py), or at audio offset in the mux.

### Script behaviour / shape (write it as shared/diagnose_drift.py)
  - Args: --project <dir> (default final-hours/projects/troy), --fps 30.
  - Read durations.json (intended). Read _index.json (beat->shot).
  - ffprobe each clips/shot_NNN.mp4 (pooled) AND each modea/clips/shot_NNN.mp4 (source, if present).
  - Probe voiceover.mp3 total length. Optionally load voiceover.json to also report the spoken-time
    span per beat (cross-check intended durations against actual word timestamps — catches whether the
    INTENDED durations themselves are wrong vs. the VIDEO conform being wrong).
  - Print the per-beat table (or write a CSV for eyeballing in a spreadsheet — 154 rows).
  - Print the summary + the one-signed/random verdict.
  - READ-ONLY: it probes and prints, changes nothing. Safe to run repeatedly.

### Two-ended cross-check (the crucial disambiguation)
The table answers "does the VIDEO match the INTENDED durations?" But we also want "do the INTENDED
durations match the VOICE?" So include a second comparison using voiceover.json:
  - For each beat, from the manifest/word-timestamps, compute the beat's ACTUAL spoken span (first word
    start -> last word end of that beat's narration).
  - Compare that spoken span to durations.json's intended duration for the beat.
  If intended == spoken span (good) but pooled clip != intended (bad) -> the bug is the VIDEO CONFORM.
  If intended != spoken span -> the bug is UPSTREAM in duration-building (Whisper alignment / boundary
  mapping), and the video is faithfully rendering wrong durations.
This split is the whole game: it tells us which END the problem lives at, so we stop guessing.

### After the diagnosis (likely fix themes — decide AFTER the table speaks)
  - Make every conformed segment an exact integer frame count: frames = round(intended_dur * FPS),
    build the segment to exactly `frames` frames (e.g. via `-frames:v` or a setpts factor computed to
    hit that exact frame count), so no float-second residue can accumulate.
  - Ensure constant FPS and frame-exact segments BEFORE concat so concatenation can't round.
  - Optionally let the final beat absorb the tiny total residue so sum == voice exactly WITHOUT a global
    pin that hides mid-video drift.
  - Re-test on a SHORT script first (4-6 beats) where the fixed math should give cumulative_drift ~= 0,
    THEN re-run a long episode. Never debug timing precision on a 154-beat / 25-min / real-money run.

### Guardrails for the session
  - Change ONE thing at a time. Don't touch music / Mode B / anything else during the drift fix.
  - The diagnostic script is read-only — run it freely.
  - Frame-exactness is the probable theme; the model (continuous voice, voice-wins) stays as-is. This is
    precision surgery on the conform/concat math inside assemble_episode.py, not an architecture change.
