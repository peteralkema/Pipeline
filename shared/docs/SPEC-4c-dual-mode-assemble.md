# SPEC — Step 4c: Real A render + full-episode audio spine + dual-mode assemble

*Written 5 June 2026 as the first task for next session. Audience: a fresh Claude
instance and a rested Peter, both starting cold. Everything needed to execute is here.
Read PART 2B of PIPELINE_PLAYBOOK.md and SESSION-NOTES-2026-06-05.md first for context.*

---

## Where we are (what's already proven)

The Synthetic dual-mode pipeline is built and verified through Step 4b. On real hardware:
- `parse_script.py` turns the tagged `script.md` into `beats.json` (E1: 62 beats, A:41 B:21).
- `dispatch.py --render` renders Mode B beats via real `npx remotion render` (the $650M
  NumberCounter clip is proven).
- `modea_beats.py` translates the 41 Mode A beats into the recreation engine's `--beats`
  format AND writes `synthetic_modeA_beats_index.json` (engine shot index → original beat index).
- `recreation_pipeline.py stills --beats … --storyboard-only` ingests them under the new
  `synthetic/channel.json` (Victor, 1080p, documentary style). Confirmed: "OK Beat-script
  ingested: 41 beats."
- Resolution unified at 1080p via per-channel `width`/`height` in channel.json.

**Nothing about the architecture is in question. 4c is execution: render for real, time it
for real, stitch it for real.**

## What 4c delivers

A complete Episode 1 video: all 62 beats rendered (41 recreated Mode A clips + 21 Remotion
Mode B clips), interleaved in true beat order, over one continuous Victor voiceover,
Whisper-timed, at 1080p. From locked script to watchable episode, one coherent flow.

---

## The three pieces of 4c (in dependency order)

### PIECE 1 — Real Mode A render (run the engine past --storyboard-only)

This is the existing Final Hours flow, now driven by Synthetic's translated beats. It
COSTS MONEY (fal stills ~$0.03 each × 41, then Kling motion ~$0.15–0.20 each × 41) and
has a HUMAN REVIEW GATE. Do it deliberately.

Steps (on the box, inside `~/venvs/pipeline`, from the `synthetic/` channel folder):
1. Regenerate the translated beats fresh (cheap, instant):
   ```
   python ../shared/parse_script.py projects/ep1-the-promise/script.md --json /tmp/ep1_beats.json
   python ../shared/modea_beats.py /tmp/ep1_beats.json --out /tmp/synthetic_modeA_beats.json
   ```
2. Generate stills (real fal cost, ~41 images):
   ```
   python ../shared/recreation_pipeline.py stills \
       --beats /tmp/synthetic_modeA_beats.json \
       --project projects/ep1-the-promise
   ```
   (Drop `--storyboard-only` — that's what makes it actually generate.)
3. **Auto silent-reject check then HUMAN REVIEW GATE** — the engine flags <10KB black
   PNGs (flux safety rejects). Review every still in the browser (make_review_page.py +
   serve_review.py over the ssh tunnel, exactly as Final Hours). Fix/restill/override as
   needed. **Synthetic WANTS this gate** — the recreation look matters as much here.
4. Animate via Kling (the expensive part):
   ```
   python ../shared/recreation_pipeline.py finish --project projects/ep1-the-promise --no-music
   ```
   **BUT WAIT — see the seam problem below. You do NOT want the engine's `finish` to
   narrate and assemble. You want it to animate ONLY.** This is the first thing to build.

**The seam problem (the key 4c design decision).** The engine's `finish` does:
animate → generate Victor VO over the Mode-A-narration-only → Whisper-align → assemble.
That is WRONG for a dual-mode episode, because:
- the VO would cover only the 41 A beats' narration, missing every Mode B beat's
  narration AND every QuoteCard found-line (recall beat 00's empty narration — the
  cold-open's words live on the Mode B QuoteCard at beat 01);
- the assemble would stitch only the 41 A clips, with no B clips and wrong timing.

So 4c's FIRST build task is **"animate but don't assemble"**: a way to run the engine's
Kling animation step and stop. The engine is close — `finish` already has
`--assemble-only` (assemble without rendering). We need the inverse: `--animate-only`
(render clips, skip VO + assemble), OR factor the animate loop so the Synthetic
orchestrator can call it directly. Recommended: add a small `--animate-only` flag to
`cmd_finish` that runs the clip loop and returns before `generate_voiceover`. Minimal,
in keeping with the existing flag style, and leaves Final Hours' `finish` untouched.

After Piece 1: `projects/ep1-the-promise/clips/shot_001.mp4 … shot_041.mp4` exist at 1080p.

### PIECE 2 — Full-episode audio spine (the real timing)

> **✅ DONE & PROVEN ON BOX (5 June 2026, late).** Built as four scripts, all committed:
> `build_audio_script.py` (2a: full read + manifest + silent-hold policy), `generate_episode_vo.py`
> (2b: real Victor VO, reuses `generate_voiceover`), `build_beat_durations.py` (2c: wraps
> `align_with_whisper.py`, emits `durations.json` — 39 whisper-measured + 23 silent-hold for E1),
> and `dispatch.py --durations` (2d: consumes real frames, proxy is fallback-only). E1 measured at
> 588s / 9.8min spoken vs the proxy's 13.3min guess — the ~35% drift is dead. The text below is kept
> as the design record; it is built, not pending. Remaining 4c work is PIECE 1 (real A render) and
> PIECE 3 (dual-mode assemble).


This replaces the word-count proxy in `dispatch.py`'s `estimate_frames()` with real
Whisper-measured per-beat durations, over ALL 62 beats.

1. **Assemble the full narration text in beat order**, A and B together. For each beat
   0..61: its `narration`, plus for QuoteCard beats the `found_line` (the spoken line).
   This is the script the narrator actually reads. Source it from `beats.json` (it has
   both fields per beat). Write it to one text file in order.
   - NOTE the cold open: beat 00 (A) has empty narration; beat 01 (QuoteCard) has the
     found-line "We have a verdict." So the VO order is: [00 silence/nothing] →
     [01 "We have a verdict."] → [02 "With those four words…"] … The text file is the
     concatenation of every beat's spoken words in beat order.
2. **Generate one Victor voiceover** over that whole text (Inworld, chunked at sentence
   boundaries — `recreation_pipeline.generate_voiceover` already does this and handles
   the 1800-char limit). One MP3 for the whole episode.
3. **Whisper-align** it. The engine already has `_auto_align_with_whisper` +
   `align_with_whisper.py`. But it aligns against a *storyboard* of shots. For 4c we need
   per-BEAT durations (all 62), not per-shot (41). Decide: either (a) build a 62-beat
   "storyboard" (every beat, A and B, with its narration) and run the existing aligner
   against it, or (b) write a small Synthetic-level aligner that maps Whisper word
   timestamps onto beat boundaries using each beat's narration text. Option (a) reuses
   proven code and is recommended — make a beats-as-storyboard JSON where each entry has
   `narration` (and found_line folded in), run whisper + align, read back `audio_duration`
   per beat.
4. **Feed real durations into both renderers.** Once each beat has a measured duration:
   - Mode B: `dispatch.py` uses it directly as frames (duration × 30).
   - Mode A: the engine's assemble already prefers `audio_duration` from the storyboard;
     but in the dual-mode assemble (Piece 3) we control timing ourselves, so each A clip
     is trimmed/held to its beat's measured duration.

After Piece 2: every one of the 62 beats has a real duration, and there's one episode VO.

### PIECE 3 — Dual-mode assemble (interleave A+B in true order at 1080p)

This is the real version of `assemble_test.py`, scaled to the whole episode.

1. **Build the ordered clip list** for all 62 beats:
   - For each beat in order 0..61:
     - if Mode B: `clips/beat_NN_B_<Component>.mp4` (from dispatch.py --render)
     - if Mode A: the engine clip. Use `synthetic_modeA_beats_index.json` REVERSED:
       it maps engine_shot_index → beat_index, so build beat_index → shot_index, then
       the clip is `projects/ep1-the-promise/clips/shot_<shot_index:03d>.mp4`.
2. **Trim/hold each clip to its beat's measured duration** (from Piece 2). Mode B clips
   were rendered at their frame count already; Mode A clips (Kling ~5s) get trimmed to
   the beat duration, or held if shorter (the engine's assemble has this logic to copy:
   trim to `min(target, native)`, ffmpeg streaming).
3. **Concatenate in beat order** (ffmpeg concat demuxer, re-encode to uniform 1080p/30fps
   — both modes are already 1080p so no scaling, but re-encode guarantees clean seams,
   exactly as assemble_test.py proved at 720p).
4. **Mux the episode Victor VO** over the silent concatenated video, then **the music
   bed under it.** IMPORTANT — music ownership: music is added at ASSEMBLE, not in the
   audio leg. The audio leg (Pieces 2a–2d) only produces the VO + durations; it has NO
   music. The music-mux logic currently lives INSIDE `recreation_pipeline.py`'s
   `assemble()` and must be PORTED into the dual-mode assembler — it does not come for
   free, because Synthetic does not use the engine's assemble. What to lift across (it's
   self-contained ffmpeg, ports cleanly):
     - voice + music `amix` with the calibrated levels: `VOICE_LEVEL = 1.15`,
       `MUSIC_LEVEL = 0.07` (the low bed tuned for Jamendo tracks);
     - loop the music to cover full length (concat-repeat then trim — avoids the
       music-stops-early bug);
     - source the bed from Synthetic's `channel.json` `default_music_prompt` (cool, tense
       underscore — distinct from Final Hours' funereal one), or `--music <file>` / skip
       with `--no-music`.
   Music is independent of per-beat timing (it's a bed over the finished timeline), so it
   does not interact with the durations — but its HOME is the assembler. Bank this so it
   is not lost between the audio leg and the engine.
5. Output `projects/ep1-the-promise/final_video.mp4` at 1080p.

After Piece 3: the complete Episode 1, watchable end to end.

### Then: the true-up (human voice) — already designed, comes free
Swap the Victor MP3 for Peter's human read, re-run Whisper-align (Piece 2 step 3) → all
62 durations re-derive → re-run Piece 3 assemble. No re-render of any clip. Build a
`--voiceover <path>` override so the human read drops in cleanly.

---

## Build order recommendation for the session
1. **First, the cheap/free scaffolding** (no fal, no Kling): build the full-narration
   text assembler from beats.json, and the beats-as-storyboard for alignment (Piece 2
   steps 1 + the alignment plumbing). Test the VO generation on the real text (Inworld
   cost is tiny). Get real durations for all 62 beats. This de-risks timing before
   spending on stills.
2. **Then `--animate-only`** flag on the engine (Piece 1 seam fix). Small, testable.
3. **Then the dual-mode assembler** (Piece 3) — test it FIRST with the existing single
   real B clip + placeholders for A (like assemble_test did) but driven by REAL beat
   durations and the real index map, to prove ordering+timing before spending on 41
   stills.
4. **Only then spend** on the real Mode A render (Piece 1 stills + Kling) and run the
   real full assemble.

This order means the one expensive step (41 stills + 41 Kling animations) happens LAST,
after timing, ordering, and assembly are all proven on placeholders + the free pieces.
Consistent with "ship fast, phase deliberately, spend last."

---

## The 3 component-feature gaps (decide whether to fix before or after first full render)
- QuoteCard attribution-only variant (kill karaoke) — 3 QuoteCard beats affected.
- NumberCounter startValue+countdown — the $1B→$44M beat (currently renders 0→44M).
- NumberCounter plainYear — the 1997 beat (currently "1,997").
Recommendation: fix all three FIRST (they're small Remotion edits) so the first full
render is correct, rather than rendering a known-wrong version. But none block assembly —
they can be done in parallel with Piece 1/2 scaffolding.

## Key facts / paths for cold start
- Box repo: `~/Pipeline`. Laptop repo: `~/Projects/Pipeline`. venv: `~/venvs/pipeline`
  (bare python3 lacks deps). Run pipeline from inside `synthetic/` channel folder.
- Remotion project: `~/Projects/remotion-learning` (laptop). `REMOTION_DIR` env in dispatch.py.
- E1 script: `synthetic/projects/ep1-the-promise/script.md` (62 beats, A:41 B:21).
- Index map: regenerate via modea_beats.py; it's `*_index.json`, engine_shot→beat.
- Accent color: `#3b5bdb` (indigo, in shape_props). Channel palette navy #0a1628 /
  amber #d4a017 / bone #f4f1ea / rust #8b3a1e.
- Everything is committed in shared/. Repo flow: laptop edit → push → box pull.
