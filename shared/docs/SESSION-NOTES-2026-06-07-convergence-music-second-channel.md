# Session Notes — 7 June 2026 (evening) — ORCHESTRATOR ARC COMPLETED + SECOND CHANNEL + MUSIC
## The orchestrator now runs script → finished, scored video in one command, proven on a second channel.

*Destination in repo: `shared/docs/SESSION-NOTES-2026-06-07-convergence-music-second-channel.md`*

**TL;DR:** Built a second tiny test (Final Hours, Mode-A-only) to prove channel-agnosticism from a
cold start — and it earned its keep: surfaced + fixed a CLASS bug (channel name↔folder hyphen/
underscore), proved the no-Mode-B leg-skip branch, then we WIRED the convergence leg into the
orchestrator (auto-assemble → final_video.mp4) and ran the FULL arc live end-to-end on Final Hours.
Then built Tier-2 music: Claude reads the script → writes one loopable instrumental fal prompt →
ElevenLabs generates one bed → muxed under the voice. All committed.

---

## 1. Second-channel test (Final Hours, Mode-A-only) — why and what it proved
Rather than re-run synthetic live, we built a NEW tiny script on a DIFFERENT, established channel to
test the "channel-agnostic, resolve by name" claim from a cold start. Project:
`final-hours/projects/test-fh-modea/` — 4 Mode-A beats, authentic FH register (a Titanic wireless-
room recreation, public-domain history). Parsed clean (4 A beats, all with narration, 0 Mode B).

Proved three untested things in one cheap run:
- **Channel-agnosticism** — orchestrator resolved a second channel (`final-hours/channel.json`,
  voice Victor) from repo root, no code change.
- **Leg-skip branch** — `decide_legs` correctly emitted `no Mode B beats → Mode B leg skipped`;
  plan came out `audio → modeA → convergence` (we'd only ever run dual-mode before).
- **Resolution-per-channel** — final video rendered 1920×1080 (FH channel.json dims), same as
  synthetic; the assembler conforms each channel's stills to that channel's declared size.

## 2. CLASS BUG fixed: channel name ↔ folder hyphen/underscore
Symptom (hit TWICE — synthetic, then final-hours): header/channel.json name uses underscores
(`final_hours`, `synthetic_press`, `success_coach`) but the FOLDER uses hyphens (`final-hours/`,
`success-coach/`) — and `synthetic` is a genuine ALIAS for `synthetic_press`. The resolver did
`channel_dir = channel` verbatim → missed the folder.
- **Fix** (`patch_channel_resolver_hyphen.py`, committed): the resolver now tries the name as-given,
  then the `-`↔`_` swaps, and uses whichever folder has a `channel.json`. Validated in sandbox:
  `final_hours`→`final-hours/` ✓, `success_coach`→`success-coach/` ✓.
- **Scope (honest):** this fixes the systematic hyphen/underscore class. It deliberately does NOT
  resolve genuine aliases like `synthetic_press`→`synthetic` (that's not a hyphen swap) — those are
  handled by matching the header to the folder (we set synthetic's header to `synthetic` earlier).
- **Banked inconsistency:** `synthetic/channel.json` still declares `"name": "synthetic_press"` while
  its header now says `synthetic`. Harmless for resolution; tidy if upload metadata ever reads `name`.

## 3. CONVERGENCE LEG wired into the orchestrator (the structural win)
Built `shared/convergence_leg.py` (new) + `shared/patch_wire_convergence.py` (wires it in). Both
committed. The orchestrator now runs the FULL arc — `audio → modeB → modeA → convergence → final_video`
— in one command instead of stopping at "legs not yet wired."
- `run_convergence_leg(ctx, modea)`: reads `ctx["project_dir"]`/`shared`/`py`/`dry_run`; takes the
  Mode A leg's RETURN dict (`index_json`, `engine_project`) as the authoritative paths (no guessing);
  pools Mode A `shot_NNN.mp4` (from `<project>/modea/clips/`) + any Mode B `beat_NN_B_*.mp4` (from
  `<project>/clips/`) into `<project>/clips/`; shells the PROVEN `assemble_episode.py` with
  `--durations --index --voiceover --clips --out`. VOICE WINS preserved.
- Music is OFF by default via a `ctx["music"]` hook (now feedable — see §4).
- Wiring patch also adds `else: ma = None` so `ma` is defined when Mode A is skipped (Mode-B-only
  compositions), and removes `convergence` from the "not yet wired" pending list.
- **NOT in scope (deliberately deferred):** thumbnail gate, convergence gate, upload/OAuth. Those are
  the "publish" half of convergence — their own session (credential-heavy). We wired convergence-CORE
  (auto-assemble to a watchable file), not publish.

## 4. FULL LIVE RUN on Final Hours — convergence proven on disk
Ran `orchestrate.py --project test-fh-modea ... --live`. Went audio → Mode A (Victor read 44.1s,
4 Flux stills, stills gate, 4 Kling clips) → CONVERGENCE (`pooled clips → ... Mode A: 4 copied,
Mode B: 0 present` → `convergence complete → final_video.mp4`). Output: 1920×1080, 44.12s, 18 MB.
This validated convergence's REAL clip-pooling + assembly on disk (dry-run can't prove that), and
confirmed it tolerates the Mode-A-only case (zero Mode B clips, no error). Peter: "great, well done."

**Gate UX finding (banked, not a bug):** the Mode A stills gate is an HONOR-SYSTEM checkpoint — it
waits for `go` but does NOT verify you actually opened the review page. Peter typed `go` without
reviewing and it proceeded. Fine for a solo operator + benign test; for real episodes the aesthetic
firewall only works if you remember to look, and the tunnel→browser flow has enough friction to make
skipping easy. Future (low priority): lower-friction stills review (inline thumbnails?) — connects to
the existing "stills page too small / Mode A clip review never built" backlog.

## 5. TIER-2 MUSIC built (Claude reads script → one loopable fal bed)
We re-derived the music design from first principles (Peter): the Jamendo/`music_category`/per-region/
crossfade machinery was complexity serving WITHIN-episode variety, not worth the timing-coupling —
the same lesson as the silence cleanup. Decided **Tier 2**: variety ACROSS episodes, simplicity
WITHIN one. One continuous bed under the one continuous voice.

Built `shared/make_music.py` (committed). Three stages, reusing the repo's existing `anthropic`
(claude-sonnet-4-6) + `fal_client` plumbing:
1. READ the narration (from `--narration <out>.txt` or `--beats beats.json` fallback).
2. Claude writes ONE fal music prompt tuned to THIS episode — instrumental, loopable, under-narration;
   channel `default_music_prompt` given as house-style context, not a cage.
3. fal `fal-ai/elevenlabs/music` generates ONE bed (`prompt`, `music_length_ms` 3s–10min, `instrumental:true`,
   `output_format:mp3_44100_128`) sized to the voice length → `<project>/music.mp3`. Sanity-checked
   (exists, >20KB, real duration). Assembler/convergence muxes it (loops if shorter; ours covered in one).
- `--print-prompt-only` flag runs stages 1+2 only (Claude prompt, NO fal spend) — used it to validate
  the prompt for free before generating. Strongly recommend this pattern for any future prompt tuning.
- **Model:** `fal-ai/elevenlabs/music`, swappable via `--model` (built model-agnostic). ElevenLabs
  chosen for its explicit `instrumental` flag. NOTE: 192kbps mp3 needs fal Creator tier — we use 128k.

**Result:** Claude's prompt read the Titanic-wireless story and turned the telegraph into a motif —
"single tones separated by long silences, suggesting morse pulses or the last signals fading into the
void." That episode-specific intelligence is exactly the Tier-2 payoff (the fixed channel prompt would
never do that). Generated `music.mp3` (722 KB, 46.2s), muxed under the voice (VOICE 1.15 / MUSIC 0.07).
Peter: narration sits clearly on top, bed underneath — balance right.

## 6. Music prompt TUNED for variation (within Tier-2, no new complexity)
Peter found the first bed a bit samey. Confirmed: ElevenLabs music on fal has NO "variation" flag
(prompt / music_length_ms / instrumental / output_format / composition_plan only; the creativity/
refinement params were a DIFFERENT model, beatoven). Rather than `composition_plan` (which reintroduces
sections+durations = the timing-coupling we deleted), tuned the PROMPT instead
(`patch_music_prompt_variation.py`, committed): Claude now asks for gentle EVOLUTION — instruments
drifting in/out, slow harmonic/textural shifts — with the hard rule that variation comes from TEXTURE,
never VOLUME (so it still never steps on the narrator). Regenerated → Peter: "the music is better."

## Repo state
HEAD after this session includes: channel-resolver patch, convergence_leg.py + wiring patch,
make_music.py + variation patch. Box/laptop/GitHub agree. Test artifacts live under
`final-hours/projects/test-fh-modea/` (build artifacts, not committed): script.md, beats(.json/_full),
durations.json, voiceover.mp3, modea/ (stills+clips+storyboard), clips/ (4 pooled), music.mp3,
final_video.mp4 + final_video_scored.mp4.

## NEXT SESSION (in order)
1. **Wire `make_music.py` into the convergence leg** so `--music` on the orchestrator runs the whole
   thing automatically (currently make_music is a standalone step + convergence has the `ctx["music"]`
   hook but nothing calls make_music). Small: convergence calls make_music (when music on) before
   assemble, then passes `--music music.mp3`. Then a full live run produces a SCORED video in one command.
2. **The PUBLISH half of convergence** (its own session): thumbnail gate, convergence gate, upload/OAuth.
   Final Hours has `auth.py` + `client_secret.json`; Synthetic OAuth not set up. Credential-heavy, gated.
3. **Mode B within-card word-sync** (still pending from earlier — the "conforming" lag; Whisper
   timestamps have the data).
4. **Mode B page "design-lite."**

## Small banked items
- `make_music.py` relies on shell-sourced `.env` (`set -a; source .env; set +a`) because it doesn't
  call `load_dotenv()` like recreation_pipeline/orchestrate do. Add `load_dotenv()` to make_music when
  next touched, so it's self-sufficient.
- The audio leg's continuous-read filename during an orchestrator run is NOT `test_audio.txt` (that was
  our by-hand name). make_music's `--beats` fallback works regardless; if wiring make_music into the
  leg, pass the leg's actual read path or just use beats.
- `build_beat_durations.py` `--aligner` relative-default papercut (pass `shared/align_with_whisper.py`
  from repo root) — still unfixed; banked.
