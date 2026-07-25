# Orchestrator Dependency Map (v2 — 7 June 2026 evening)

*Destination in repo: `shared/docs/ORCHESTRATOR-DEPENDENCY-MAP.md` (replaces v1)*

Updated after wiring the convergence leg and building Tier-2 music. Changes from v1 are marked **[NEW]**.
Every edge was read in source on the box or watched running, except the items flagged at the bottom.

---

## 1. Control flow — the conductor and its legs (convergence now WIRED)

```
                          script.md
                              |
                              v
                        parse_script.py            -> beats.json (flat) + beats_full.json (header+beats)
                              |
                              v
                        orchestrate.py             resolve channel (hyphen/underscore tolerant [NEW]);
                              |                     decide_legs(); sequence
              +---------------+---------------+
              v               v               v
        audio_leg.py     modeb_leg.py     modea_leg.py
        (timing+voice)   (graphics+gate)  (stills,clips,gate)
              +---------------+---------------+
                              v
                  convergence_leg.py  [NEW - WIRED]
                  (pool clips -> assemble_episode -> final_video; optional music)
                              |
                              v
                        final_video.mp4
```

`orchestrate.py` now imports `audio_leg`, `modeb_leg`, `modea_leg`, **`convergence_leg`** [NEW], plus
`telemetry`, `banner`. After Mode A it calls `convergence_leg.run_convergence_leg(ctx, ma)`. The whole
arc runs in ONE command. (The "legs not yet wired" message is gone for convergence.)

`decide_legs` skips legs by composition: no Mode B beats -> Mode B leg skipped (proven on the Final
Hours Mode-A-only test -> plan `audio -> modeA -> convergence`).

---

## 2. What each leg shells out to (in run order)

**audio_leg.py -> run_audio_leg(ctx):**
1. `build_audio_script.py`   beats.json -> `<out>.txt` (continuous read) + `<out>.manifest.json`
2. `generate_episode_vo.py`  imports `recreation_pipeline.py` (generate_voiceover, Inworld) -> voiceover.mp3
3. `whisper`                 voiceover.mp3 -> voiceover.json (word timestamps)
4. `build_beat_durations.py` manifest + voiceover.json; shells `align_with_whisper.py` -> durations.json

**modeb_leg.py -> run_modeb_leg(ctx) + modeb_gate(ctx):**
- `dispatch.py` (reads durations.json; `npx remotion render` -> beat_NN_B_*.mp4),
  `make_modeb_review.py` + `serve_modeb_review.py` (gate)

**modea_leg.py -> run_modea_leg(ctx):**  returns {clips, count, indices, index_json, engine_project}
1. `modea_beats.py`  beats.json -> engine_beats.json + `_index.json` (at project root)
2. `recreation_pipeline.py stills`  -> storyboard.json + stills (fal Flux)  [Mode A stills gate]
3. `recreation_pipeline.py finish --animate-only`  -> modea/clips/shot_NNN.mp4 (fal Kling)

**convergence_leg.py -> run_convergence_leg(ctx, modea):  [NEW]**
- pools Mode A `shot_NNN.mp4` (from `<project>/modea/clips/`, path from modea["engine_project"]) +
  Mode B `beat_NN_B_*.mp4` (from `<project>/clips/`) into `<project>/clips/`
- uses modea["index_json"] as the authoritative beat->shot map
- shells PROVEN `assemble_episode.py` (`--durations --index --voiceover --clips --out`) -> final_video.mp4
- music OFF by default; `ctx["music"]` hook (see section 5)

---

## 3. durations.json - still the SINGLE timing source (unchanged)
```
   build_beat_durations.py -> durations.json -> { dispatch.py | assemble_episode.py | make_modeb_review.py }
```
Produced once by the audio leg; read by three consumers. Shape:
`{str(idx): {duration, frames, source, mode, component}}`.

## 4. recreation_pipeline.py - still the SHARED engine (unchanged)
- audio leg -> generate_episode_vo.py -> `recreation_pipeline.generate_voiceover()` (Inworld)
- Mode A leg -> `recreation_pipeline.py stills` (fal Flux) + `finish --animate-only` (fal Kling)
A change to it ripples into BOTH legs. Treat with care.

## 5. make_music.py - Tier-2 music [NEW]
```
   narration (<out>.txt or beats.json)
        |
        v
   make_music.py
     stage 1: read narration
     stage 2: Claude (claude-sonnet-4-6) writes ONE loopable instrumental prompt (per-episode)
     stage 3: fal (fal-ai/elevenlabs/music) generates ONE bed -> <project>/music.mp3
        |
        v
   assemble_episode.py / convergence_leg.py  (muxes music.mp3 under voice; loops if shorter)
```
Standalone for now (run before convergence). Reuses anthropic + fal_client plumbing. `--print-prompt-only`
= stages 1+2, no fal spend. Model swappable via `--model`. NOT YET wired into convergence_leg (next session).

---

## 6. Shared data spine (artifacts touched by more than 1 program)

| Artifact | Produced by | Read by |
|---|---|---|
| beats.json (flat) | parse_script.py | build_audio_script.py, dispatch.py, modea_beats.py, make_music.py (fallback) |
| beats_full.json | parse_script.py | orchestrate.py (header preflight) |
| voiceover.mp3 | generate_episode_vo.py | whisper, assemble_episode.py, make_music.py (sizing) |
| voiceover.json | whisper | build_beat_durations.py (future: word-sync) |
| durations.json | build_beat_durations.py | dispatch.py, assemble_episode.py, make_modeb_review.py |
| _index.json | modea_beats.py (leg returns path) | convergence_leg.py -> assemble_episode.py |
| clips/ (pooled) | dispatch.py (B) + recreation_pipeline.py (A); pooled by convergence_leg.py [NEW] | assemble_episode.py |
| music.mp3 [NEW] | make_music.py (Claude+fal) | assemble_episode.py / convergence_leg.py (mux) |
| final_video.mp4 | assemble_episode.py (via convergence_leg.py) | (output) |

## 7. External tools / engines
Inworld TTS (Victor) via recreation_pipeline; Whisper (local); fal Flux (stills); fal Kling (animate);
fal ElevenLabs music [NEW] (make_music); Remotion (dispatch, Mode B); ffmpeg (assemble); Claude API
(recreation_pipeline storyboard - skipped on --beats path; AND make_music prompt-writing [NEW]).

## 8. Honesty flags / still-open
- **PUBLISH half of convergence NOT wired:** thumbnail gate, convergence gate, upload/OAuth are still
  unbuilt. convergence_leg does auto-ASSEMBLE only. (FH has auth.py + client_secret.json; Synthetic OAuth absent.)
- **make_music NOT yet wired into convergence_leg** - it's standalone; next session connects it so
  `--music` on the orchestrator runs Claude->fal->mux automatically.
- **One INFERRED edge (still unverified):** narration_assembler.py -> make_episode_vo.py may be a
  legacy/alternate path (active leg uses generate_episode_vo.py). One grep settles it.
- **Channel alias vs hyphen-swap:** resolver now tolerates `_`<->`-`, but genuine aliases (synthetic->
  synthetic_press) still need header==folder. synthetic/channel.json `name` still says synthetic_press.

## 9. Known papercuts
- `build_beat_durations.py` `--aligner` relative default - pass `shared/align_with_whisper.py` from repo root.
- `make_music.py` needs shell-sourced `.env` (no `load_dotenv()` yet) - add it when next touched.
- Mode A stills gate is honor-system (accepts `go` without verifying review). Stills page too small;
  Mode A clip review never built.
- narration_assembler.py still has `categorise_empty` silent-beat detection - banked strip (keep build_narration).
