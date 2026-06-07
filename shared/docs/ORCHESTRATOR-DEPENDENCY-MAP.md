# Orchestrator Dependency Map

*Destination in repo: `shared/docs/ORCHESTRATOR-DEPENDENCY-MAP.md`*

Reconstructed from direct observation during the 7 June 2026 end-to-end validation run — every
edge below was either read in the source on the box or watched running, EXCEPT the two flagged as
inferred/unwired at the bottom. This is the map we built one grep at a time; here it is in one place.

---

## 1. Control flow — the conductor and its four legs

```
                          script.md
                              │
                              ▼
                        parse_script.py            → beats.json (flat list, for leg tools)
                              │                     → beats_full.json (header + beats, orchestrator input)
                              ▼
                        orchestrate.py             reads beats_full.json; decide_legs(); sequences the legs
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        audio_leg.py     modeb_leg.py     modea_leg.py
        (timing +        (graphics +      (stills, clips,
         voiceover)       gate)            gate)
              └───────────────┼───────────────┘
                              ▼
                       assemble_episode.py          reads durations + voiceover + index + clips
                              │
                              ▼
                        final_video.mp4
```

`orchestrate.py` imports `audio_leg`, `modeb_leg`, `modea_leg`, plus `telemetry` and `banner`.
Each leg SHELLS OUT to proven scripts rather than reimplementing them — the orchestrator just
sequences proven black boxes.

---

## 2. What each leg shells out to (in run order)

**audio_leg.py → run_audio_leg(ctx):**
1. `build_audio_script.py`   reads `beats.json` → `<out>.txt` (one continuous read) + `<out>.manifest.json`
2. `generate_episode_vo.py`  imports `recreation_pipeline.py` (`generate_voiceover`, Inworld/Victor) → `voiceover.mp3`
3. `whisper`                 `voiceover.mp3` → `voiceover.json` (word timestamps)
4. `build_beat_durations.py` reads manifest + `voiceover.json`; shells `align_with_whisper.py` → `durations.json`
   - (audio keep/swap gate)

**modeb_leg.py → run_modeb_leg(ctx) + modeb_gate(ctx):**
- `dispatch.py`              reads `beats.json` + `durations.json`; shells `npx remotion render` → `clips/beat_NN_B_*.mp4`
- `make_modeb_review.py`     builds the review page (imports `dispatch` for shape_props; reads `durations.json`)
- `serve_modeb_review.py`    serves the page (imports `make_modeb_review`; re-render POST → `dispatch`)

**modea_leg.py → run_modea_leg(ctx):**
1. `modea_beats.py`                          translate `beats.json` → `modea_engine_beats.json` + `modea_index.json`
2. `recreation_pipeline.py stills`           reads engine beats (via `_load_beats_with_canon`) → `storyboard.json` + stills (fal Flux)
   - (Mode A stills gate)
3. `recreation_pipeline.py finish --animate-only`  reviewed stills → `clips/shot_NNN.mp4` (fal Kling)

**convergence (assemble_episode.py):**
- reads `durations.json` (timing+mode+component+order) + `modea_index.json` (beat→shot) + `voiceover.mp3`
  + pooled `clips/` → `final_video.mp4` (direct ffmpeg). VOICE WINS: output pinned to voice length.

---

## 3. The two cross-cutting dependencies (the hard-won discoveries)

### a) durations.json is the SINGLE timing source
```
        build_beat_durations.py   (audio leg · via whisper + align_with_whisper.py)
                  │
                  ▼
           durations.json   ── single source of timing + mode + component + order ──
                  │
        ┌─────────┼─────────────────────┐
        ▼         ▼                     ▼
   dispatch.py  assemble_episode.py  make_modeb_review.py
   (Mode B      (beat durations,     (shows each
    frames)      voice-wins)          beat's duration)
```
Produced ONCE by the audio leg; read by three downstream consumers. This is the architecture the
continuous-narration cleanup created — no holds, no silence objects, every beat measured from the
voice. Shape: `{str(idx): {duration, frames, source, mode, component}}`.

### b) recreation_pipeline.py is the SHARED engine (two callers)
- audio leg → `generate_episode_vo.py` → `recreation_pipeline.generate_voiceover()` (Inworld/Victor)
- Mode A leg → `recreation_pipeline.py stills` (fal Flux) AND `recreation_pipeline.py finish --animate-only` (fal Kling)

A change to `recreation_pipeline.py` ripples into BOTH the audio leg and the Mode A leg. Treat edits
to it with extra care.

---

## 4. Shared data spine (artifacts touched by more than one program)

| Artifact | Produced by | Read by |
|---|---|---|
| `beats.json` (flat) | parse_script.py | build_audio_script.py, dispatch.py, modea_beats.py |
| `beats_full.json` (wrapper) | parse_script.py | orchestrate.py (header preflight) |
| `voiceover.mp3` | generate_episode_vo.py | whisper, assemble_episode.py |
| `voiceover.json` | whisper | build_beat_durations.py (and the source of word timestamps for future word-sync) |
| `durations.json` | build_beat_durations.py | dispatch.py, assemble_episode.py, make_modeb_review.py |
| `modea_index.json` | modea_beats.py | assemble_episode.py (reunites contiguous shot_NNN clips with their beats) |
| `clips/` (pooled) | dispatch.py (Mode B) + recreation_pipeline.py (Mode A) | assemble_episode.py |

---

## 5. External tools / engines (the "how", reached via the scripts above)

| Tool | Reached via | Used for |
|---|---|---|
| Inworld TTS (Victor) | recreation_pipeline.generate_voiceover (called by generate_episode_vo.py) | voiceover.mp3 |
| Whisper (local) | audio leg directly | word timestamps → durations |
| fal.ai Flux (flux-pro/v1.1) | recreation_pipeline.py stills | Mode A stills |
| fal.ai Kling | recreation_pipeline.py finish --animate-only | Mode A clips |
| Remotion (npx) | dispatch.py | Mode B clips |
| ffmpeg (direct) | assemble_episode.py | concat + conform + mux |
| Claude API | recreation_pipeline.build_storyboard | ONLY on the prose-script path; SKIPPED when --beats is supplied (our path) |

---

## 6. Honesty flags — verify these next session

- **Convergence tail not fully wired.** `assemble_episode.py` is proven and standalone, but the
  orchestrator's convergence leg (thumbnail gate → schedule gate → upload) is still a STUB. Diagram §1
  shows the intended flow to `final_video.mp4`; the upload leg beyond it is not built, and Synthetic's
  OAuth is not set up.
- **One INFERRED edge, not directly verified:** `make_episode_vo.py` depends on `narration_assembler.py`
  (this is WHY we kept narration_assembler rather than retiring it). But it was NOT confirmed that
  `make_episode_vo.py` is in the ACTIVE leg path — the audio leg we ran uses `generate_episode_vo.py`,
  not `make_episode_vo.py`. So `narration_assembler.py → make_episode_vo.py` may be an alternate/legacy
  path. One grep next session settles it: `grep -rn "make_episode_vo" shared/ --include=*.py`.
- **Channel resolution blocker (from the orchestrator dry-run):** header says `channel: synthetic_press`
  but the channel folder on disk is `synthetic/`. orchestrate.py resolves channel→folder by name and
  halts. Fix before any live orchestrator run (align header to folder, rename folder, add an alias in
  the resolver, or ensure `synthetic/channel.json` exists).

---

## 7. Known papercuts on these dependencies

- `build_beat_durations.py` `--aligner` default is RELATIVE (`../shared/align_with_whisper.py`) — breaks
  when run from repo root; pass `--aligner shared/align_with_whisper.py`. Banked fix: resolve via `__file__`.
- Mode A gate / various scripts have cwd assumptions (run from channel root). Banked: cwd-proofing pass.
- `narration_assembler.py` still carries `categorise_empty` silent-beat detection — banked minor patch to
  strip it (keep `build_narration`), consistent with the no-silence model.
