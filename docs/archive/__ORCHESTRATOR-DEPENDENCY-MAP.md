# Orchestrator Dependency Map (v3.1 — 11 June 2026)

*Destination in repo: `shared/docs/ORCHESTRATOR-DEPENDENCY-MAP.md` (replaces v2).*

Updated after the Sacred Dawn launch proved the **Mode-A path end-to-end live** (audio → modeA → convergence → published video), and after the 9 June pipeline-hardening session (look resolver, audio-continuity QC, tunnel-free review server, project-anchored config). Changes from v2 are marked **[NEW]** / **[CHANGED]**. v3.1: **every edge in this map is now confirmed by grep on the box** — the four edges v3 had inferred (look_resolver call site, audio_qc wiring, review.py vs serve_review, the make_episode_vo/narration_assembler path) are all resolved in §8. No inferred edges remain.

Companion docs: `machina.md` (the operational manual — every command), `ante-machinam.md` (the pre-machine bible — Constitution + craft canon). This map is the *wiring diagram* between the two.

---

## 1. Control flow — the conductor and its legs (Mode-A path PROVEN LIVE)

```
                          script.md
                              |
                              v
                        parse_script.py            -> beats.json (flat) + beats_full.json (header+beats)
                              |
                              v
                        orchestrate.py             resolve channel (hyphen/underscore tolerant);
                              |                     project-anchored config [CHANGED]; decide_legs(); sequence
              +---------------+---------------+
              v               v               v
        audio_leg.py     modeb_leg.py     modea_leg.py
        (timing+voice    (graphics+gate)  (stills,clips,gate)
         + audio QC[NEW])                  (+ look resolver[NEW])
              +---------------+---------------+
                              v
                  convergence_leg.py
                  (pool clips -> assemble_episode -> final_video; optional music)
                              |
                              v
                        final_video.mp4
                        (Mode-A path PROVEN LIVE — Sacred Dawn, 10-11 June [NEW])
```

`orchestrate.py` imports `audio_leg`, `modeb_leg`, `modea_leg`, `convergence_leg`, plus `telemetry`, `banner`.
The whole arc runs in ONE command from the repo root: `python shared/orchestrate.py --project <slug> --beats <…>/beats_full.json`.

`decide_legs` skips legs by composition: **no Mode B beats -> Mode B leg skipped** -> plan `audio -> modeA -> convergence`. This is the proven Final Hours / Sacred Dawn signature. (Sacred Dawn: 52 beats, all Mode A -> exactly this plan, ran to a published `final_video.mp4`.)

**Config resolution is now project-anchored [CHANGED, 9 June]:** channel + look resolve by the *project path*, not the launch CWD, and the cache is keyed per channel dir. The voice/look is decided by *what you're rendering*, not *where you launched from* (root-cause fix for a wrong-voice bug). The channel resolver is hyphen/underscore tolerant (`final_hours`->`final-hours/`, `sacred_dawn`->`sacred-dawn/`); a genuine alias still needs header==folder.

**No `--from` resume:** a re-run re-spends every leg. An orphaned post-stills run is recovered out-of-band via `recreation_pipeline.py finish --project modea --animate-only` (reads existing stills/durations, re-spends nothing) — see §2 / Machina troubleshooting. [NEW, banked at the Sacred Dawn launch]

---

## 2. What each leg shells out to (in run order)

**audio_leg.py -> run_audio_leg(ctx):**
1. `build_audio_script.py`   beats.json -> `<out>.txt` (continuous read) + `<out>.manifest.json`
2. `generate_episode_vo.py`  imports `recreation_pipeline.py` (generate_voiceover, Inworld) -> voiceover.mp3
   - resolves the channel's `voice_id` (snake_case) at runtime; **prints a hardcoded "Victor" label regardless of the resolved voice** [NEW gotcha — listen at the gate, the label lies; on the kill-list]
3. `whisper`                 voiceover.mp3 -> voiceover.json (word timestamps)
4. `build_beat_durations.py` manifest + voiceover.json; shells `align_with_whisper.py` -> durations.json
5. **audio-continuity QC [NEW, 9 June, CONFIRMED]** — `audio_leg.py:158` does `from audio_qc import audio_continuity_check`; standalone module (`shared/audio_qc.py`), shelled by the audio leg at the gate. Auto-scans Whisper output (voiceover.json) for silence holes; read-only, fails soft. Run manually: `python shared/audio_qc.py <project>/voiceover.json`.
-> **AUDIO GATE** (keep / swap = scp human VO + re-whisper)

**modeb_leg.py -> run_modeb_leg(ctx) + modeb_gate(ctx):**
- `dispatch.py` (reads durations.json; `npx remotion render` -> beat_NN_B_*.mp4),
  `make_modeb_review.py` + `serve_modeb_review.py` (the Mode B correctness gate)

**modea_leg.py -> run_modea_leg(ctx):**  returns {clips, count, indices, index_json, engine_project}
1. `modea_beats.py`  beats.json -> engine_beats.json + `_index.json` (at project root)
2. `recreation_pipeline.py stills`  -> storyboard.json + stills (fal Flux)   [Mode A stills gate]
   - **look resolved channel-then-project via `look_resolver.py` [NEW, 9 June, CONFIRMED]** — imported INSIDE the engine at `recreation_pipeline.py:532` (`from look_resolver import resolve_look`), NOT in the leg wrapper. So the look resolves inside the engine's stills step: project `look.json` (`{"look":"hi8_90s"}`) overrides channel `style_suffix`; resolver walks up from the still's output path.
3. **stills gate** -> review server `review.py` **[CHANGED — was mislabelled serve_review.py in v2; CONFIRMED]**:
   the live Mode A gate prints `/home/peter/venvs/pipeline/bin/python {shared}/review.py --project {engine_cwd}/{engine_project}` (modea_leg.py:195).
   public-bind + token auth, tunnel-free [NEW, 9 June]; honor-system (`go` not verified).
   ⚠ `serve_review.py` still co-exists: it's the older v1 server, referenced by the **Mode B gate** (`serve_modeb_review.py` "reuses v1's serve_review.py", modea_leg.py:181) and lingering in **stale comments** in modea_leg.py (lines 10, 38-39 still show the old `serve_review.py --project … --port …` invocation). Two servers, two modes — don't delete serve_review.py thinking it's dead.
4. `recreation_pipeline.py finish --animate-only`  -> modea/clips/shot_NNN.mp4 (fal Kling)
   - **standalone-recoverable**: run directly from the project dir to resume an orphaned post-stills run [NEW]

**convergence_leg.py -> run_convergence_leg(ctx, modea):**
- pools Mode A `shot_NNN.mp4` (from `<project>/modea/clips/`, path from modea["engine_project"]) +
  Mode B `beat_NN_B_*.mp4` (from `<project>/clips/`) into `<project>/clips/`
- uses modea["index_json"] as the authoritative beat->shot map
- shells PROVEN `assemble_episode.py` (`--durations --index --voiceover --clips --out`) -> final_video.mp4
- music: `ctx["music"]` hook; **still wires make_music manually for now** (see §5)
- **PROVEN LIVE on the Mode-A path** (Sacred Dawn `final_video.mp4`); dual-mode interleave (A+B together) still the open 4c item. The publish half (thumbnail gate, convergence/schedule gate, uploader) NOT wired -> upload manual. [CHANGED]

---

## 3. durations.json — still the SINGLE timing source (unchanged)
```
   build_beat_durations.py -> durations.json -> { dispatch.py | assemble_episode.py | make_modeb_review.py }
```
Produced once by the audio leg; read by three consumers. Shape:
`{str(idx): {duration, frames, source, mode, component}}`.

## 4. recreation_pipeline.py — still the SHARED engine (unchanged)
- audio leg -> generate_episode_vo.py -> `recreation_pipeline.generate_voiceover()` (Inworld)
- Mode A leg -> `recreation_pipeline.py stills` (fal Flux) + `finish --animate-only` (fal Kling)
- convergence -> the music-mux + `assemble()` ffmpeg logic historically lives here (the dual-mode assembler must port it)
A change to it ripples into BOTH render legs AND assemble. Treat with the most care of any file.

**fal gotcha (banked):** Flux at default safety silently returns ~7KB black-PNG placeholders on rejection; the engine passes `safety_tolerance:"5"` to stop this.

## 5. make_music.py — Tier-2 music (standalone; not yet wired)
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
Standalone for now (run before convergence). `--print-prompt-only` = stages 1+2, no fal spend. Model swappable via `--model`. **NOT YET wired into convergence_leg** — the decision (generated make_music vs curated Jamendo bed) is still open per channel; until wired, music is added manually or via a curated track. **Papercut: needs shell-sourced `.env` (no `load_dotenv()` yet).** Final Hours / Sacred Dawn curated levels: `VOICE_LEVEL 1.15` / `MUSIC_LEVEL 0.07`.

---

## 6. Shared data spine (artifacts touched by more than 1 program)

| Artifact | Produced by | Read by |
|---|---|---|
| beats.json (flat) | parse_script.py | build_audio_script.py, dispatch.py, modea_beats.py, make_music.py (fallback) |
| beats_full.json | parse_script.py | orchestrate.py (header preflight) |
| voiceover.mp3 | generate_episode_vo.py | whisper, assemble_episode.py, make_music.py (sizing) |
| voiceover.json | whisper | build_beat_durations.py, audio_qc.py [NEW] |
| durations.json | build_beat_durations.py | dispatch.py, assemble_episode.py, make_modeb_review.py |
| storyboard.json | recreation_pipeline.py stills | review.py (gate page), recreation_pipeline finish |
| engine_beats.json | modea_beats.py | recreation_pipeline.py stills |
| _index.json | modea_beats.py (leg returns path) | convergence_leg.py -> assemble_episode.py |
| look.json (per-project) [NEW] | (authored) | look_resolver.py -> recreation_pipeline stills |
| clips/ (pooled) | dispatch.py (B) + recreation_pipeline.py (A); pooled by convergence_leg.py | assemble_episode.py |
| music.mp3 | make_music.py (Claude+fal) | assemble_episode.py / convergence_leg.py (mux) |
| final_video.mp4 | assemble_episode.py (via convergence_leg.py) | (output — Mode-A path live) |

## 7. External tools / engines
Inworld TTS (Victor / Elliot[NEW Sacred Dawn] / Vinny[YHTBT] / Ashley[Success Coach]) via recreation_pipeline;
Whisper (local, drift fixed via `difflib.SequenceMatcher` coverage); fal Flux (stills, `safety_tolerance:"5"`);
fal Kling O3 Standard (animate, ~5s native); fal ElevenLabs music (make_music); Remotion 4.0.472 (dispatch, Mode B);
ffmpeg (assemble; `ffprobe` is the only reliable clip-duration source); Claude API (recreation_pipeline storyboard —
skipped on `--beats` path; AND make_music prompt-writing). NexLev MCP is research-side, not in the render graph.

## 8. Honesty flags / inferred edges / still-open

**[RESOLVED 11 June — all edges now confirmed by grep on the box]:**
- **`look_resolver.py` call site — CONFIRMED:** imported inside the engine at `recreation_pipeline.py:532`, not in the leg. The look resolves inside the stills step.
- **`audio_qc.py` wiring — CONFIRMED:** standalone module imported by `audio_leg.py:158`; runs at the audio gate, read-only.
- **review server — CONFIRMED + nuance:** the live Mode A gate calls `review.py` (modea_leg.py:195). `serve_review.py` is NOT dead — it's the older v1 server still used by the Mode B gate (modea_leg.py:181) and still named in stale Mode-A comments (modea_leg.py:10, 38-39). Both files are live; the stale comments are a cleanup item, not a missing file.
- **`make_episode_vo.py` / `narration_assembler.py` — CONFIRMED not legacy:** these are the **Synthetic 4c dual-mode audio scaffolding** (file headers: "Piece 2, step 1/2 of Synthetic 4c"). `narration_assembler.py` builds `ep1_narration.txt` → `make_episode_vo.py` voices it. They are the *not-yet-wired dual-mode siblings* of the live single-mode path (`build_audio_script.py` → `generate_episode_vo.py`), waiting on 4c — parallel, not dead. (The `categorise_empty` silent-beat detection inside `narration_assembler.py` is the one banked strip — see §9.)

**Still-open (not wired):**
- **PUBLISH half of convergence** — thumbnail gate, convergence/schedule gate, channel-agnostic uploader with batch exit-gate: NOT built. convergence_leg auto-ASSEMBLES only. Uploads are manual (category Entertainment, add tags). Sacred Dawn upload is manual.
- **make_music NOT wired into convergence_leg** — standalone; needs `.env` sourcing; per-channel generated-vs-curated decision still open.
- **Auto-launch review server** — the gate banner claims "always on" but the operator still pastes the `review.py` command by hand; should launch in modea_leg before the gate (kill stale `:8001` first, tear down on `go`).
- **Channel alias vs hyphen-swap** — resolver tolerates `_`<->`-`, but genuine aliases (synthetic -> synthetic_press) still need header==folder. `synthetic/channel.json` `name` still says `synthetic_press`.

## 9. Known papercuts
- `build_beat_durations.py` `--aligner` relative default — pass `shared/align_with_whisper.py` from repo root.
- `make_music.py` needs shell-sourced `.env` (no `load_dotenv()` yet) — add when next touched.
- Mode A stills gate is honor-system (accepts `go` without verifying review). Stills page small; **the stills-gate prompt still prints the OLD tunnel instructions** (now wrong — the server is tunnel-free); Mode A clip review never built.
- `review.py`'s own `generate_still` (the in-page restill button) should resolve the per-job look via `look_resolver` the same way `recreation_pipeline.py:532` does — confirm it imports the resolver, not a hardcoded suffix.
- `narration_assembler.py` still has `categorise_empty` silent-beat detection — banked strip (keep build_narration); silent beats no longer exist (ante-machinam Constitution §1).
- Audio-leg + audio gate print a hardcoded "Victor" voice label regardless of the resolved `voice_id` — on the kill-list; until fixed, listen at the gate, don't trust the label.

---

## 10. The #1 coupled change on the backlog (for when you wire it)

**Per-shot motion-direction on the stills review page** (the corrected scope). An interactive field per shot on the `review.py` page, entered at review time, that feeds the Kling prompt in `finish --animate-only`. Touches three files as one coupled change:
- `review.py` — add the input + persist it (cleanest: a `motion` field per shot in `storyboard.json`)
- storyboard schema — carry the per-shot `motion` string
- `recreation_pipeline.py` `animate_still` — read `storyboard[shot].motion` as the Kling motion prompt; blank -> current default

Read first: `sed -n '561,620p' shared/recreation_pipeline.py`; `grep -n "motion\|storyboard\|def animate_still" shared/recreation_pipeline.py`; `sed -n '1,60p' shared/review.py`.
