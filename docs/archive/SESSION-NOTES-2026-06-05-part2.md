# Session Notes — 5 June 2026 (later session)
## Synthetic 4c: audio spine built end-to-end + dual-mode assembler proven on a full placeholder cut

Continues from SESSION-NOTES-2026-06-05.md (the earlier session that proved Steps 1–4b).
This session built Piece 2 of 4c (the whole-episode audio spine) and Piece 3 (the
dual-mode assembler), and ran them on real hardware against the locked Episode 1 script.
By the end there is a complete 62-beat **placeholder** pacing cut — every beat in true
order, real Victor voiceover, real silences, real timing, 10.75 min — with grey/navy
blocks standing in for the not-yet-rendered Mode A scenes. The only paid stream (Mode A
stills + Kling) has NOT been run; that's deliberate.

---

## The headline numbers (Episode 1, measured this session)

- **62 beats, A:41 B:21** (unchanged, reconfirmed from script).
- **1,789 spoken words** in the assembled narration (Whisper transcribed 1,793 — 4-word
  drift, well under the 5% warning bar; alignment is sound).
- **Voiceover length: 573.4s = 9.6 min.** Victor reads at ~187 wpm — markedly FASTER
  than the 135-wpm proxy that predicted 13.3 min. First true timing signal.
- **Episode runtime: 645.3s = 10.75 min** = 9.53 min spoken + 1.23 min inserted silence.
- **23 of 62 beats carry no spoken words** (untimable by Whisper — durations ASSIGNED,
  not measured): 1 cold open + 16 held Mode B cards + 6 silent Mode A holds.
- **Silent Mode A holds: beats 20, 25, 31, 43, 52, 54** — all carry `silence_after=True`,
  all are deliberate decision-point pauses (empty chair after the firing, door closing on
  Altman, Musk's stillness). NOT a bug. The script is asking for these silences.
- **~12 beats run longer than 15s; longest is beat 55 at 33.6s, beat 26 at 29s, beat 32
  at 27.6s.** These are genuine dense paragraphs, NOT misalignments. They drive the one
  real open problem this session surfaced (see "The shot-density problem" below).

---

## What got BUILT this session (all in shared/, all committed)

### `narration_assembler.py` — Piece 2, step 1 (free)
Pure transform of `beats.json`. Emits `ep1_narration.txt` (the whole-episode VO script,
beat order) and `ep1_beats_storyboard.json` (62-entry alignment scaffold, flat-list shape
the Whisper aligner accepts — DISTINCT name so it never collides with the engine's 41-shot
`storyboard.json`). Reports the untimable-beat breakdown.

### `make_episode_vo.py` — Piece 2, step 2 (cheap: Inworld cents + free Whisper)
`ep1_narration.txt` → one continuous Victor VO via the engine's `generate_voiceover`
(single TTS path, no duplication). Verifies voice_id==Victor + Inworld key BEFORE spending.
`--whisper` runs Whisper with the engine's EXACT invocation (model=small, word timestamps)
→ `voiceover.json` placed where the aligner expects it. Run from inside `synthetic/`, in
`~/venvs/pipeline`.

### `align_with_whisper.py` — PATCHED (minimal)
Added optional `--storyboard`/`--whisper` path overrides so it can align our named scaffold.
Default `--project` path is byte-identical — **Final Hours is untouched.** This is the only
change to the proven shared aligner.

### `align_episode.py` — Piece 2, step 3 (free) — the timing table
Runs the patched aligner on the scaffold (subprocess) to MEASURE the 39 spoken beats, then
ASSIGNS deliberate holds to the 23 silent beats, and records each beat's VO window
(`vo_start`/`vo_span`) so the assembler can slice the audio. Writes `ep1_beats_timed.json`
— the ONE timing table both the dispatcher and the assembler consume (principle 3: one
measurement, two consumers). Hold constants are at the top of the file, TUNABLE:
`cold_open 2.0`, `card 2.5`, `silent_a 3.0`, `silence_after bonus +1.5`.

### `assemble_episode.py` — Piece 3 (free in placeholder mode) — the dual-mode assemble
Walks all 62 beats in order. Video: each clip conformed to its timing-table duration
(Mode A via reversed index map → shot_NNN.mp4; Mode B via beat_NN_B_*.mp4; missing or
`--placeholders` → solid colour block). Audio: per beat, the real VO sliced at
[vo_start, vo_start+vo_span] then padded with silence to the beat's full duration; silent
beats are pure silence. Concatenated, this is the VO with the holds' silence INSERTED in
the right places — video length == audio length, perfectly synced. `--placeholders` gives
a free pacing cut. The SAME command without `--placeholders` makes the real episode once
clips exist. Tested in-container with real ffmpeg (8-beat fixture: durations matched, audio
confirmed silent during holds / voiced during speech).

### `PIPELINE_PLAYBOOK.md` — UPDATED
Added a "4c progress" subsection to PART 2B (the two Piece-2 files, three banked lessons,
a 4c sub-status table) + bumped the top date line and the build-status row to "in progress."

---

## The three banked lessons (the ones that will save the next session time)

1. **`found_line` is already folded into `narration`.** `parse_script.flush_into()` writes
   the spoken quote into BOTH fields. The VO uses `narration` ALONE — following the SPEC's
   literal "narration + found_line" would make Victor read every QuoteCard line TWICE.
   Verified: each QuoteCard line appears exactly once in the assembled text.

2. **The VO contains NO silence for the silent beats** — we only fed Inworld the spoken
   words. So the episode is LONGER than the voiceover by the total of all assigned holds
   (here, 73.5s). Piece 3 must INSERT silence into the audio at each silent beat's position,
   NOT just "mux the VO over the video and trim to VO length." This is the gap the SPEC
   glossed; `assemble_episode.py` handles it and it's proven in the audio-sync test.

3. **The long-held-beat numbers are real, not drift.** Beats 26/32/55 (29/28/34s) have full
   dense paragraphs of narration — Whisper measured them correctly. The problem isn't the
   timing; it's that one still can't hold 30 seconds of screen. See below.

---

## The one real open problem: SHOT DENSITY (decide + build before any Mode A spend)

One-beat-one-shot is right for SHORT beats but breaks at the visual layer for the ~12 beats
over 15s. A single recreated still held for 25–34s reads as dead air (the exact "video
freezes before narration ends" failure the Final Hours playbook warns about).

**The fix (not yet built): a sub-slicer at the `modea_beats` stage.** For any Mode A beat
whose narration exceeds ~9–10s (~25 words), split it into 2–4 shots that SHARE the beat's
measured duration — each gets its own still and its own slice of the time. The beat stays
ONE idea / one timing-table entry; it just renders as several images. This touches:
- `modea_beats.py` — do the splitting, emit N shots for a long beat.
- the index map — one beat now maps to several engine shot indices (currently 1:1).
- `assemble_episode.py` — distribute a long beat's duration across its shots.
Still free to build and prove on placeholders. **This is the gate before spending on stills**
— generating 41 stills now and then splitting would mean paying to redraw some.

---

## The runtime decision (deferred to Peter's ear — NOT yet made)

10.75 min vs the strategy doc's locked **15–20 min** target. Explicit guidance given:
do NOT close the gap by inflating the hold constants — padding silence reads as slow, not
weighty, and betrays the register. It's a script/packaging question, two honest options:
(a) accept E1 as a tight 10.75 min and revise the target (defensible for a cold-open ep), or
(b) treat the gap as a signal the arc wants another scene or two (the strategy doc's
candidate beats: capped-profit pivot, Microsoft contingency weekend) — added BEFORE the
Mode A spend.

**Peter is to watch/listen to the placeholder cut and judge:** does 10.75 min of Victor
breathe? Do the silent holds land or feel dead? That judgment unlocks the spend decision.
(Note from end of session: Peter watched — correctly observed it's a blank screen with
audio and colour changes. That IS the placeholder cut working; it's judged by EAR, eyes
closed. The colour changes are the edit; the long single-colour stretches are the long
beats made audible.)

---

## Where we stopped / NEXT SESSION pick-up order

Everything from here to the stills is FREE and reversible. Suggested order:

1. **DECIDE runtime** (Peter's ear on `pacing_cut.mp4`): lock 10.75 min, or add a scene.
2. **BUILD the shot sub-slicer** for long Mode A beats (the real blocker). Free, placeholder-
   provable. Touches modea_beats + index map + assembler.
3. **(Optional) tune hold constants** in `align_episode.py` if the silent beats feel wrong,
   re-run `align_episode` (free, instant).
4. **FREE: render the 21 Remotion graphics.** First rewire `dispatch.py` to read durations
   from `ep1_beats_timed.json` (replaces `estimate_frames`), then `dispatch.py --render`.
   Re-run `assemble_episode.py --placeholders` to watch a cut with REAL cards in the B slots.
5. **Fix the 1.1s video/audio drift** at the final mux (trim video to audio length; rounding
   accumulates across 62 concatenated segments — cosmetic now, tighten for the real cut).
6. **THEN SPEND (last):** `modea_beats` → `recreation_pipeline stills` (~$1–2 fal) → review
   in the HTML page (make_review_page + serve_review over the 443 ssh tunnel) → `finish`
   (Kling, ~$7) → `assemble_episode.py` WITHOUT `--placeholders` = the real episode.

---

## Two operational flags for later (not blocking, but real)

- **Synthetic has NO YouTube auth on the box.** The runbook's as-is status lists only
  final-hours + success-coach tokens. Before PUBLISHING E1: add the Synthetic Google account
  as a test user, run auth on the laptop, scp `token.json`/`client_secret.json` to
  `~/Pipeline/synthetic/`. (All work so far is render-side, so this hasn't mattered yet.)
- **Runbook Phase 5 is still `[UNVERIFIED]`** — no full render / no fal call has run on the
  box. The first real Mode A `stills` run will be the first time fal is exercised on the box.
  When it works, flip Phase 5 to PROVEN and update the runbook.

---

## Files this session (commit state)

Committed to `shared/`: `narration_assembler.py`, `make_episode_vo.py`,
`align_with_whisper.py` (patched), `align_episode.py`, `assemble_episode.py`.
Updated: `shared/docs/PIPELINE_PLAYBOOK.md`.

Regenerable artifacts (NOT worth committing — rebuilt from beats.json + VO):
`ep1_narration.txt`, `ep1_beats_storyboard.json`, `ep1_beats_timed.json`,
`synthetic_modeA_beats_index.json`, `projects/ep1-the-promise/voiceover.mp3` + `.json`,
`projects/ep1-the-promise/pacing_cut.mp4`.

## Repo flow reminder
Author on laptop (`~/Projects/Pipeline`) → commit → push → on box (`~/Pipeline`)
`git pull origin main`. Run from inside `synthetic/`, in `~/venvs/pipeline`. Box is
`116.202.18.68`, SSH on port **443**. Pull results back with `scp -P 443`.

## The full chain, one line
`script.md → parse_script → beats.json →` then three streams: **audio spine**
(`narration_assembler → make_episode_vo → align_episode → timing table`), **Mode A**
(`modea_beats → recreation_pipeline stills → review → finish → A clips`), **Mode B**
(`dispatch --render → B clips`) → all meet at **`assemble_episode`** → episode.
Audio spine + assembler are DONE; Mode B render is free-and-next; Mode A is the spend, last.
