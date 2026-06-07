# Session Notes — 7 June 2026 (continued)
## First real convergence assembly → first-principles reset of the audio/timing model → cleanup plan

*Destination in repo: `shared/docs/SESSION-NOTES-2026-06-07-convergence-and-first-principles-reset.md`*

**TL;DR:** Built + validated two convergence fixes (slow-to-fill, music mux), assembled the
first real end-to-end Synthetic ep1 (62 real clips, 10.75 min), watched it, and that surfaced a
deep design error: the pipeline treats SILENCE as a programmatic object (silent beats, holds,
inserted gaps). First-principles correction: **there is ONE continuous, protected voice track;
silence is just the absence of words within it, never something the pipeline makes.** This makes
most of the timing/silence machinery redundant. This session ends with the model written up
(script-craft Part II, committed) and a precise DELETION plan to clean up the now-redundant code.

---

## 1. What got built + proven this session (kept)

- **Slow-to-fill** (patch_episode_slowfill_music.py): short clips slow via setpts instead of
  freezing. Committed + applied on box. Works (Peter confirmed), though heavy stretches look bad
  → real fix is upstream (more beats / shorter narration per beat), see §4.
- **Music mux** (same patch): VOICE 1.15 / MUSIC 0.07, loop-to-cover, defensive (no music.mp3 →
  no-op). Committed + applied. NOT yet exercised (no music.mp3 for ep1 yet; music GENERATION for
  a 62-beat episode is a separate gap — music_score.py reads the 41-shot storyboard, needs
  music_category annotation; deferred).
- **Audio true-up** (patch_episode_audio_trueup.py): single-pass continuous-audio build, validated
  on real ffmpeg (gapless, exact duration). **NOTE: this patch is now SLATED FOR DELETION** — the
  first-principles reset (§3) makes it unnecessary. Good outcome: we proved the *method*, then the
  upstream simplification removed the *need*. Better deleted than carried. (It is committed on the
  box; the cleanup will supersede it.)
- **First real Synthetic ep1 assembled**: 62 real clips, slow-fill, 10.75 min, final_video.mp4.
  Watched. Convergence assembly logic proven.

## 2. What watching the real cut revealed (the six observations)

1. **Aspect**: Mode A clips are 4:3 (1120×820 → flux), Mode B are 16:9 (1920×1080) → pillarbox/
   distortion. ROOT CAUSE FOUND: flux-pro/v1.1 ignores the `{width,height}` dict and defaults to
   landscape_4_3; it needs `image_size: "landscape_16_9"` (confirmed via fal docs). channel.json
   is correct (1920×1080); the engine asked correctly; flux silently downgraded. **Fix = one-line
   engine change + re-render Mode A. Not yet done.** (Mode A clip review never happened — backlog.)
2. **Freeze** → fixed by slow-to-fill (but see §4: real fix is shorter beats).
3/5. **Audio cuts at Mode B beats** → the headline finding, see §3.
4. **No music** → mux added; generation deferred.
6. **Stills review page too small** → trivial make_review_page.py layout fix, deferred.

## 3. THE FIRST-PRINCIPLES RESET (the core of this session)

**The error:** the pipeline treats silence as a programmatic object. Mode B cards were authored as
"silent holds"; align_episode.py / build_beat_durations.py fabricate a 2.5s `default_hold` /
`silent_hold` duration for them; the assembler inserts that silence. Result: narration STOPS at
every silent Mode B card and resumes after — the audible "cut" Peter heard.

**The correction (Peter's, sharper than the assistant's first framing):**
- The spoken narration is ONE continuous, unbroken audio track. It is the SOLE source of truth for
  timing. **The track is never cut.**
- **Silence is not an object.** It is the absence of spoken words *within* the one track — a
  narrator pausing for effect (mic still open, track still running), not a gap the code inserts.
- Therefore the pipeline must **codify nothing about silence** — no holds, no inserted gaps, no
  "silent beat" category. Its only audio job: lay the whole protected voice track over the visuals.
- **Mode B is a TRANSFORMATION of narration, never an addition.** Author the full continuous script
  against pure Mode A first; then PROMOTE phrases to Mode B (the words stay spoken; only the on-
  screen visual changes). Promoting a phrase mid-beat SPLITS the host Mode A beat in two.
- **The Lego rule (Peter):** every beat's final clip duration = that beat's spoken-words duration in
  the protected track. Mode A and Mode B alike. `(beatA words dur = beatA clip dur) + (beatB words
  dur = beatB clip dur) + …` in beats.json order. No special cases.
- **Remotion duration limit = a SCRIPT-STAGE eligibility filter**, not a runtime constraint: a phrase
  may be promoted to Mode B only if its spoken duration fits the component's ceiling. Solved by good
  script design up front. **Failsafe only (avoid by design): freeze the TAIL of a Mode B clip if it
  somehow overflows. Never the happy path.**

Written up as **script-craft-principles.md Part II — "The Synthetic Press Dual-Mode Authoring
Model"** (committed this session). That doc is now the authoring reference.

**Retained downstream alignment (the only one):** a beat's clip is conformed to its beat's spoken
duration (Whisper-measured). Word-level highlight-sync (the on-screen word lighting up exactly as
spoken, à la future lip-sync) is the SAME principle but NOT built now — explicitly deferred; for
now just align beat-clip-duration to beat-words-duration.

## 4. THE CLEANUP / DELETION PLAN (next execution)

Pure deletions, each a validated patch riding LAPTOP→GitHub→BOX, in order:

1. **build_beat_durations.py** — every beat is measured; DELETE the `silent_hold` / `default_hold`
   fabrication. A wordless beat becomes a loud authoring ERROR (0s, source "no_narration"), not a
   hold. *(This session: patch built + tested — see §5.)*
2. **dispatch.py** — Mode B renders at the beat's MEASURED duration (delete `component_durations()`
   "render at component's own length" logic + the `silence_after` +1.5s bonus in estimate_frames).
   Add freeze-tail failsafe only for overflow. (Leave shape_props/registry FOR NOW — dies in the
   element-choice-on-page build, see §6; removing now would break rendering before the page replaces it.)
3. **assemble_episode.py** — read durations.json directly; DROP the ep1_beats_timed.json dependency
   AND the audio true-up machinery (lay the whole protected voiceover.mp3 over the conformed video,
   untouched). The true-up patch is superseded here.
4. **Retire align_episode.py + narration_assembler.py** — under the continuous-track model their job
   (fabricate a hold-polluted timing table) is gone; durations.json from the audio leg already IS the
   timing table. Confirm no other consumer first.

**durations.json simplification (approved):** keep the dict shape + `source` field; just stop ever
writing `silent_hold`. Safest (no consumer breakage).

**audio_leg.py largely SURVIVES** — it already produces the continuous voiceover.mp3 + whisper +
durations.json (the spine). Mostly clean under the new model.

**COUPLING TO KNOW:** the cleanup implements the NEW model (every beat has words), but current ep1
was authored under the OLD model (silent Mode B beats). So the cleaned pipeline can only be fully
end-to-end tested against a NEW-MODEL script. → the tiny TEST SCRIPT (next) must be authored under
the new model: every beat has narration; Mode B beats are promoted phrases; include edge cases
(a mid-beat promotion that forces a split; a Mode B phrase near the Remotion limit; two adjacent
Mode B beats; a long passage that should split into multiple Mode A beats). Run the cleaned pipeline
end-to-end on it — fast + cheap.

## 5. Done this session toward the cleanup
- **Patch 1 (build_beat_durations.py)** built + sandbox-tested (compile, idempotency, anchors).
  Ready to ride the git path. Deletes silent-hold fabrication; wordless beat → loud "no_narration"
  error at 0s.

## 6. BANKED FOR LATER (Peter's idea — "very powerful but simple")
**Choose + design the Remotion element for Mode B beats ON THE HTML PAGE.** Remove ALL codification
of the element choice from the script/parser/dispatch. A Mode B beat at script stage carries only:
its spoken words, its measured duration, and a "this is Mode B" flag. The Mode B review/serve/make
HTML page becomes the DESIGN surface: pick the component, finalise on-screen content, render. This
DELETES shape_props / KNOWN_COMPONENTS registry / component prop-shaping from dispatch.py and the
`[B:Component]` parsing from parse_script.py — and turns make_modeb_review.py / serve_modeb_review.py
into a design tool (additive build). NOT scoped yet — needs reading those page files; its own
dedicated design pass (give it the same first-principles care as the silence reset).

## 7. Other banked items (carried)
- Aspect re-render: flux `image_size:"landscape_16_9"` + re-render Mode A 16:9 (gates a shippable ep1).
- Mode A CLIP review (not just stills) — backlog.
- Upload leg: header-driven metadata (orchestrator already enforces header), DDMM @ 01:00 CET,
  thumbnail as LAPTOP breakout gate. Synthetic OAuth NOT set up (channel exists, zero uploads) —
  Peter must do Google Cloud OAuth client + authorize; assistant writes code + setup steps. auth.py
  has NO variable-swap bug (memory was stale — confirmed by reading it).
- Heavy-stretch beats: the real fix is shorter beats / more beats per passage (authoring), not the
  assembler. The split rule (§3) addresses this.
- script-craft-principles.md path question: doc footer says final-hours/docs/ but it's now cross-
  channel (has Synthetic Part II) — may want to move to shared/docs/ later. Not a blocker.
- Logged-but-deferred bugs from earlier today: Mode B gate serve cwd-proofing; Mode A gate missing
  make_review_page step + cwd; "simple start" launcher; beats.json input-contract doc.
