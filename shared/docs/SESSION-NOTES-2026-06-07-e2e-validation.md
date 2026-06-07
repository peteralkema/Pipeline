# Session Notes — 7 June 2026 (late afternoon) — END-TO-END VALIDATION PASSED
## The cleaned pipeline ran script → assembled video on real renders. The morning's first-principles reset is proven in running code.

*Destination in repo: `shared/docs/SESSION-NOTES-2026-06-07-e2e-validation.md`*

**TL;DR:** Authored a tiny 6-beat new-model test script, drove it by hand through the
WHOLE cleaned pipeline (parse → continuous read → Victor → Whisper → durations → Mode B
render → Mode A stills/clips → assemble), and produced a `final_video.mp4` (52.7s) with the
voice flowing UNBROKEN end to end. Every edge case fired correctly. One more cleanup patch
landed mid-run (patch 5, build_audio_script). The orchestrator DRY-RUN proved its decision
logic is correct but surfaced a channel-resolution mismatch that blocks a live run — that
is next session's first task. Then break.

---

## What we proved (the payoff)

The continuous-narration model — designed this morning, implemented as patches 1–5 — WORKS on
real artifacts. Drove every leg by hand against project `synthetic/projects/test-pipeline/`:

1. **parse_script.py** → 6 beats, every one with narration (no wordless beats). Caught + fixed a
   beat-5 narration-ordering wrinkle at the parse step (cheap) before any spend.
2. **build_audio_script.py (2a)** → one continuous read, 164 words, 6 spoken, 0 holds.
3. **generate_episode_vo.py (2b)** → `voiceover.mp3`, **52.78s** (Victor). THE protected track.
4. **whisper** → word timestamps; the read transcribed as ONE unbroken track 00:00→00:52.7,
   continuous ACROSS the Mode B beats (visible proof the old audio-cutting is gone).
5. **build_beat_durations.py (2c)** → `durations.json`: all 6 beats `src=whisper`, 0 no_narration,
   sum 52.72s ≈ voice 52.78s. (Papercut: its `--aligner` default is relative; from repo root must
   pass `--aligner shared/align_with_whisper.py`. Banked fix: resolve aligner via `__file__`.)
6. **dispatch.py (Mode B render)** → 3 Remotion clips at MEASURED frames (84f/59f/120f). Beat 5
   QuoteCard OVERFLOWED (measured 157f > component cap 120f) → rendered at cap, flagged for
   assembler freeze-tail. The eligibility/overflow failsafe firing correctly on a real render.
7. **Mode B review page** → SURVIVED the cleanup, already reads `durations.json`. Served it, it
   worked (autoplay, locked spoken line, Re-render fired + cache-busted). Peter's "would it work?"
   hunch = yes.
8. **modea_beats.py (translate)** → `{"beats":[...]}` wrapper (engine reads it via
   `_load_beats_with_canon` — correct shape, NOT a bug; a throwaway inspection one-liner false-alarmed).
   Index map `{1:0, 2:1, 3:4}` correct (engine shot → original beat).
9. **recreation_pipeline.py stills** → 3 real stills (124–181 KB, NOT 7KB black). Came out
   **1280×704** (~1.81:1, near-16:9 — NOT the 4:3 we feared; aspect closer to target than banked).
10. **recreation_pipeline.py finish --animate-only** → 3 Kling clips, 1292×712, 5.04s each.
11. **assemble_episode.py** → pooled 6 clips into project `clips/`, assembled:
    - **VOICE WINS**: output pinned to 52.8s, voice laid whole + untouched (0.11s video rounding absorbed).
    - Beat 1: 5.0s clip slow-filled to 24.4s (**4.8x** — printed the heavy-stretch warning; the
      "should-have-split" lesson made visible).
    - Beat 5 QuoteCard: 4.05s clip in 5.22s slot → **freeze-tail** filled the gap, voice played through.
    - 6 real clips, 0 placeholders. `final_video.mp4` = 52.7s.

Peter watched it (scp'd to laptop). Verdict: **voice flows perfectly the whole way through** — the
thing we rebuilt. Beautiful.

## Patch 5 (landed this session, committed)
**build_audio_script.py rewritten** (HEAD `597326d`): removed `SILENT_HOLDS` dict + the silent-beat
classification. Every beat's spoken text = its narration; a wordless beat is an AUTHORING ERROR
(`spoken=false`, halts with exit 1), never handed a hold. This closed the LAST hole — the hold
machinery is now gone from all of: build_audio_script (2a), build_beat_durations, dispatch,
assemble_episode. Validated both ways (real beats → 6 spoken 0 holds exit 0; synthetic wordless
beat → flagged, exit 1). A green run now MEANS something because the spine is genuinely clean.

## Known gap Peter spotted in the output (NOT a regression — a deferred layer)
On the 2 Mode B cards, the WORD on screen lags the spoken word (~3s off): "conforming" is spoken at
~00:30 but the highlight sweep lands at ~00:33. This is **within-card word-sync**, which we
EXPLICITLY DEFERRED this morning. Beat-level sync (clip length = spoken-words length) works and is
proven; WORD-level sync (the on-screen word fires exactly as spoken, karaoke/lip-sync style) is not
built. The card animates on a hardcoded internal timeline (`sweepStart: 30`), not against the voice.
**The data to fix it already exists**: Whisper `voiceover.json` has each word's exact time — thread
each Mode B card the timestamp of ITS key word (relative to card start) and have the Remotion
component fire its sweep/count/reveal at that frame instead of a constant. This is the highest-value
Mode B improvement and pairs with the Mode B page redesign. Its own piece of work, next.

## Orchestrator DRY-RUN — decision logic PROVEN, one blocker found
Ran `python3 shared/orchestrate.py --beats synthetic/projects/test-pipeline/beats_full.json
--log normal --dry-run`. Results:
- ✓ preflight loaded 6 beats, header complete.
- ✓ `decide_legs` correct: **audio → modeB (3 cards + gate) → modeA (3 shots + gate) → convergence**.
- ✗ **HALTED on channel resolution**: `channel.json not found for 'synthetic_press'` — it looked for
  `synthetic_press/channel.json` from repo root. **Root cause: name mismatch.** Script header says
  `channel: synthetic_press` but the channel FOLDER on disk is `synthetic/`. The resolver maps
  channel-name → folder by name; `synthetic_press` ≠ `synthetic`.
- Note: orchestrator has NO skip-existing/resume logic (no `--from`). A live run RE-SPENDS every leg
  and RE-RUNS both interactive gates (Mode B review + Mode A stills) — so a live run is GATED and
  needs Peter's eyes; it is not fire-and-forget.

## NEXT SESSION (in order)
1. **Clear the channel-resolution blocker**, then do the FULL LIVE orchestrator run on test-pipeline
   and confirm it produces the same `final_video.mp4` as the hand-run. Decide the fix: align the
   header value to the folder (`channel: synthetic`), OR rename the folder, OR add a channel
   name→folder alias in the resolver, OR ensure `synthetic/channel.json` exists. (Read
   `resolve_beats_path` + the channel-resolution block ~lines 100–135 of orchestrate.py first.) This
   is a fresh-eyes task — the live run is gated, so do it rested.
2. **Within-card word-sync** for Mode B (use Whisper word timestamps; fire component animation at the
   measured frame). Highest-value Mode B quality fix.
3. **Mode B page "design-lite"** (banked this session): keep component fixed per beat, expand the page
   so every prop field for that component is editable + clearly presented, re-label "design," prove
   the design-control loop on the 3 test clips. (Full version — switch component type + schema-driven
   fields on the page — is the bigger banked build.) Read `make_modeb_review.py` fully first
   (we've seen lines 1–~95 + the CSS/JS; `LOCKED_FIELDS` exists, e.g. QuoteCard.quote).

## Authoring lessons banked (for real scripts)
- **HighlightedHeadline `text` has NO script-side source** under the current parser — the on-screen
  headline must be filled on the review page (or passed explicitly as `text="..."` in the tag).
  Same family as the QuoteCard attribution issue (attribution got set to the full quote). Both are
  evidence FOR the page-based Mode B design, not bugs to patch.
- **QuoteCard phrases must be ≤4s (120f)** or they overflow the component (freeze-tail fallback fires).
- **Mode B authoring:** spoken line goes ABOVE the `[B:...]` tag (parser attaches it as narration);
  write it in correct spoken order; don't rely on a `>` blockquote for spoken words (the parser folds
  found-line BEFORE pending narration → can invert order, as beat 5 originally did).

## Repo state
HEAD `597326d`. All cleanup patches (1–5) committed; box/laptop/GitHub agree. test-pipeline project
(`synthetic/projects/test-pipeline/`) holds: script.md, beats.json, beats_full.json, durations.json,
voiceover.mp3/.json, test_audio.*, modea_engine_beats.json, modea_index.json, modea/ (stills+clips+
storyboard), clips/ (6 pooled), final_video.mp4. These are build artifacts — NOT committed (correct;
repo holds code that produces outputs, not outputs).

## Still-open / carried (unchanged)
- Aspect: confirm exact flux size behavior (stills came 1280×704, not the feared 4:3 nor exact
  1920×1080) + decide if a `image_size:"landscape_16_9"` engine change is needed before a shippable ep.
- Convergence leg's thumbnail gate + DDMM-schedule gate + upload leg; Synthetic OAuth not set up.
- build_beat_durations `--aligner` relative-default papercut (resolve via `__file__`).
- narration_assembler.py minor patch: strip `categorise_empty` silent-beat detection, keep build_narration.
