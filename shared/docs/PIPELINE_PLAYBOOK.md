# Pipeline Playbook
*The full lifecycle from topic to published video, across all channels.*
*Last updated: 5 June 2026 (late) — PART 2B rewritten from design to AS-BUILT (Steps 1–4b proven on hardware); added PART 2C (THE ORCHESTRATOR — the channel-agnostic machine: five design principles, beats.json as sole input, channel.json as complete cross-mode identity, leg-detection, two gates, the new-channel reusability contract, future lip-sync leg). Earlier 5 June: added PART 2B. Prior: 30 May 2026, after shipping Six Minutes (Success Coach video 1) and setting up Hindenburg (Final Hours video 4).*

This is the single source of truth for how to make a video. Read it before starting any new project. Update it when banking new rules from production.

---

## PART 1 — QUICK REFERENCE CARD

The 12-step lifecycle. Use this as muscle memory once you know the system.

### Pre-production (research + script)

**Step 1.** Pick a topic. Use NexLev to validate demand. Check that no direct format competitor exists in the lane. Bank the decision in the channel's backlog document with rationale.

**Step 2.** Research the protagonist and historical/situational facts. For Final Hours, use web search for documented sources, family accounts, and contemporary reporting. For Success Coach, use lived experience and published research.

**Step 3.** Decide the title (use the channel's title pattern), the protagonist (one specific human), and the seven craft principles application. Reference `final-hours/docs/script-craft-principles.md` for Final Hours; equivalent doc for other channels.

**Step 4.** Write the script as a markdown document at `<channel>/projects/<project>/script.md`. Include production notes, silent beats, capability stretches. Keep the canonical script here.

**Step 5.** Write the canon block as a markdown document at `<channel>/projects/<project>/canon.md` if the video has named recurring characters or named locations. Skip for ensemble/atmospheric videos (early Final Hours videos didn't need this).

### Production (stills generation)

**Step 6.** Extract pure narration from script.md, save as `<channel>/projects/<project>/<project>_script.txt` (no production notes, just prose).

**Step 7.** Generate the initial storyboard from the narration. From the channel root:

```bash
python ../shared/recreation_pipeline.py stills --script projects/<project>/<project>_script.txt --project <project> --storyboard-only
```

This calls Claude to slice the narration into ~one shot per 9 words. Saves `storyboard.json`. Costs cents in Claude API. **Important: use `--storyboard-only` to avoid kicking off Flux image generation against canon-unaware prompts.**

**Step 8.** If the video has canon, convert `storyboard.json` to a canon-aware beats file. Insert `{character}` and `{location}` tokens into image_prompts where appropriate. Add the canon block from `canon.md` at the top of the file (in JSON format). Save as `<channel>/beat-scripts/<project>_beats.json`.

**Step 9.** Generate the stills. From the channel root:

```bash
python ../shared/recreation_pipeline.py stills --beats beat-scripts/<project>_beats.json --project <project>
```

This runs Flux against each shot's prompt. Costs $25-30 in fal credits typically. Takes 30-60 minutes. Outputs to `<project>/stills/shot_NNN.png`.

**Step 10.** Review every still. For drifted shots:

```bash
python ../shared/recreation_pipeline.py restill --project <project> --shot N
```

If the same shot fails 3 times with 3 different failure modes, duplicate an adjacent acceptable shot rather than continuing to roll dice. Bank any new rules in the rulebook.

### Animation, audio, assembly

**Step 11.** Run finish to animate stills, generate voiceover, assemble video. From the channel root:

```bash
python ../shared/recreation_pipeline.py finish --project <project> --no-music
```

Wait — verify `channel.json` voice_id matches the channel identity first. About 30-60 minutes of compute. Outputs `<project>/final_video.mp4`.

### Publication

**Step 12.** Generate thumbnail, then upload. From the channel root:

```bash
python make_thumbnail.py --project <project>
python upload.py --project <project>
```

Upload defaults to PRIVATE. Open YouTube Studio, review auto-generated metadata, replace title with your locked version, verify thumbnail loaded, schedule for the target window (typically Sunday/Monday evening US time for cold-start channels). Add the pinned comment after publication.

---

## PART 2 — FULL PLAYBOOK

The detailed walkthrough. Read this on first-time setup, when something breaks, or when launching a new channel.

### Architecture overview

The Pipeline directory at `/03. Pipeline/` contains everything:

```
03. Pipeline/
├── .env                    # API keys (Anthropic, fal, etc.) — shared across channels
├── shared/                 # Python scripts and shared utilities
│   ├── recreation_pipeline.py    # Main pipeline (stills, restill, finish, rulebook)
│   ├── make_thumbnail.py
│   ├── srt_generator.py
│   ├── voice_test.py
│   ├── still_to_clip.py
│   ├── rulebook.json             # Shared moat — accumulated production rules
│   └── docs/                     # Cross-channel reference documents
│       ├── PIPELINE_PLAYBOOK.md  # This document
│       ├── calibration-reference.md
│       ├── competitive-analysis.md
│       └── hetzner-pre-read.md
├── final-hours/            # Channel 1
│   ├── channel.json        # Channel identity, voice_id, base_canon
│   ├── client_secret.json  # OAuth client (Google Cloud Console)
│   ├── token.json          # OAuth token (this channel's YouTube account)
│   ├── auth.py             # OAuth flow script
│   ├── upload.py           # Upload script
│   ├── rulebook.json       # Channel-specific rules layered over shared
│   ├── beat-scripts/       # Canon-aware beats files
│   ├── projects/           # Individual video projects
│   │   ├── hartley/
│   │   ├── pompeii_v2/
│   │   └── hindenburg/
│   │       ├── script.md         # Full script with production notes
│   │       ├── canon.md          # Canon block (markdown form)
│   │       ├── hindenburg_script.txt   # Narration only
│   │       ├── storyboard.json   # Generated by pipeline (Claude slicing)
│   │       ├── stills/           # Generated PNG files
│   │       ├── clips/            # Animated MP4 segments
│   │       ├── voiceover.mp3     # Generated TTS
│   │       └── final_video.mp4   # Final output
│   └── docs/               # Channel-specific reference docs
│       ├── script-craft-principles.md
│       └── strategy.md
├── success-coach/          # Channel 2 — same structure as final-hours
└── channel-3/              # Channel 3 — same structure, launching later
```

**Critical paths to remember:**

- The `.env` file lives at the Pipeline root, *not* in each channel folder
- Channels symlink `.env` into themselves: `ln -s ../.env .env`
- Channels symlink shared utilities they import: `ln -s ../shared/srt_generator.py srt_generator.py`
- The `recreation_pipeline.py` lives in `shared/` and is invoked with relative path from channel roots: `../shared/recreation_pipeline.py`
- Most pipeline commands must be run from the *channel root* (final-hours/ or success-coach/), not from inside the project folder. The pipeline uses CWD to resolve project paths.

### Channel setup (one-time per new channel)

When launching a new channel for the first time:

**1. Create the channel folder structure:**

```bash
mkdir -p channel-3/{beat-scripts,projects,docs,assets}
cd channel-3
touch channel.json rulebook.json
```

**2. Configure channel.json:**

The minimum channel.json has:
- `name` — channel display name
- `voice_id` — TTS voice (e.g. "Reed" for Success Coach, "Ashley" for Final Hours)
- `style_suffix` — appended to every Flux prompt (e.g. "photoreal cinematic")
- `base_canon` — optional channel-level canon entries inherited by all projects

**3. Symlink shared utilities:**

```bash
ln -s ../.env .env
ln -s ../shared/srt_generator.py srt_generator.py
```

**4. Set up OAuth for this channel's YouTube account:**

The OAuth client (`client_secret.json`) can be reused across channels — same Google Cloud project, same OAuth client. But each channel needs its own `token.json` because each channel's YouTube uploads happen under a different Google account.

Copy the OAuth scripts and client from a working channel:

```bash
cp ../final-hours/auth.py .
cp ../final-hours/upload.py .
cp ../final-hours/client_secret.json .
```

Then **add the new channel's Google account as a test user** in Google Cloud Console:
- Go to `console.cloud.google.com`
- Open the project (e.g. `youtube-upload-test-497220`)
- Navigate to Google Auth Platform → Audience
- Add the channel's Google account email under "Test users"

Then make sure your default browser is signed in to the new channel's Google account, and run:

```bash
python auth.py
```

A browser opens. Pick the right Google account, grant the YouTube upload permissions, the script saves `token.json` to the channel folder.

**5. Verify the API key loads:**

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Key loaded:', bool(os.getenv('ANTHROPIC_API_KEY')))"
```

Should print `Key loaded: True`. If False, check the symlink to `../.env` exists and the key is set in the parent .env file.

### Project setup (per video)

For each new video:

**1. Create the project folder under the channel:**

```bash
mkdir -p projects/<project_name>/stills
```

**2. Decide the canon strategy upfront:**

Two types of projects:

- **Atmospheric / ensemble** (early Final Hours videos like Pompeii, Anne Boleyn): no recurring named characters. Skip canon entirely. Run stills with `--script` (auto-slicing).
- **Named-character recurring** (Hartley, Six Minutes, Hindenburg, Channel 3 dramatic adaptations): recurring people who must look consistent across many shots. Build a canon block. Run stills with `--beats` (pre-written canon-aware).

If you're not sure, build the canon. The cost of a canon block is one hour of writing; the cost of no canon when you needed one is hundreds of failed stills.

**3. Write script.md and canon.md in the project folder.**

**4. Extract pure narration to `<project>_script.txt`** — strip production notes, visual cues, silent-beat markers, beat headers. Just prose narration.

### Storyboard generation

Two paths depending on canon strategy:

**Path A — no canon (atmospheric/ensemble video):**

```bash
python ../shared/recreation_pipeline.py stills --script projects/<project>/<project>_script.txt --project <project>
```

This generates the storyboard AND immediately generates all stills. ~$25-30 in fal credits, 30-60 minutes. For projects without canon, this is fine.

**Path B — canon-aware (recurring characters):**

Run in two phases. First, generate the storyboard only:

```bash
python ../shared/recreation_pipeline.py stills --script projects/<project>/<project>_script.txt --project <project> --storyboard-only
```

Saves `storyboard.json`, costs cents in Claude API, no Flux generation. Then review and edit the storyboard:

- Open `storyboard.json` in an editor
- For each shot, identify characters and locations mentioned in the image_prompt
- Replace generic descriptions ("a man," "the dining room") with canon tokens (`{hermann}`, `{dining_room}`)
- Restate wardrobe details per-prompt where they matter (wardrobe drift is a known issue)
- Save the edited file as `beat-scripts/<project>_beats.json`
- Add the canon block at the top of the JSON in the format `{"canon": {...}, "beats": [...]}`

Then run stills against the canon-aware beats:

```bash
python ../shared/recreation_pipeline.py stills --beats beat-scripts/<project>_beats.json --project <project>
```

This generates the actual stills with canon expansion. The pipeline substitutes `{hermann}` with the full canon descriptor at prompt time. ~$25-30 in fal credits, 30-60 minutes.

### Storyboard editing principles

When converting auto-generated storyboard.json to canon-aware beats:

**Canon tokens go in image_prompts only, not motion_prompts** (motion describes the camera/scene, not the subject).

**Restate wardrobe in the prompt body, never trust canon resolution alone for wardrobe.** Known failure: Flux honours wardrobe from canon inconsistently. Always include the specific wardrobe details in each prompt that uses a character canon. (Banked from Six Minutes session.)

**Never prompt for group shots of 4+ characters.** Two-character shots already overwhelm Flux; five-character family shots will fail. Frame multi-character shots as:
- One character foregrounded with others suggested in soft focus
- Back-of-camera composition (one character's back visible, others off-screen)
- No-people detail shots (the wedding ring, the camera, the clock)
- Single-character close-ups with others implied by context

**Restate the era anchor in every image_prompt.** Each prompt should end with the period descriptor (e.g. "1937 photoreal cinematic" or "contemporary 2026 photoreal").

**Watch for expression defaults.** Flux's default for any character is a slight smile. Restate the canon expression baseline per-prompt for emotional moments ("composed and thoughtful," "wide-eyed observant," etc.).

**Estimate the reshoot budget realistically:**
- Adult characters in period clothing: 15-25% reshoot rate
- Child characters: 30-50% reshoot rate
- Multi-character compositions: 50%+ reshoot rate
- Total: budget 110-130 generations to get 80-100 usable stills

### Stills review

Open `<project>/stills/` and look at every shot in order. Things to check:

- **Canon drift**: does the character look like themselves shot-to-shot?
- **Wardrobe drift**: does clothing match canon and stay consistent?
- **Expression**: composed when it should be composed, anguished when it should be anguished
- **Era authenticity**: no modern objects, no modern hairstyles, no modern photography aesthetic
- **Group composition**: faces visible only when intended; soft-focus or back-of-camera for crowd scenes

For drifted shots, use restill:

```bash
python ../shared/recreation_pipeline.py restill --project <project> --shot N
```

If the same shot fails 3 times with 3 different failure modes, duplicate an adjacent acceptable shot:

```bash
cp <project>/stills/shot_038.png <project>/stills/shot_037.png
```

This was the resolution for Six Minutes shot 37. Banked rule: don't continue rolling dice past three attempts.

### Finish (animation + voiceover + assembly)

When all stills are accepted, run finish:

```bash
python ../shared/recreation_pipeline.py finish --project <project> --no-music
```

**Pre-finish checklist:**
- Verify `channel.json` voice_id is correct (Reed for Success Coach, Ashley for Final Hours, etc.) — a wrong voice_id means re-rendering the audio
- Verify all stills exist: `ls <project>/stills/ | wc -l`
- Check fal credit balance — finish typically costs $25-30, sometimes more
- Have laptop plugged in if running locally — finish takes 30-60 minutes

The `--no-music` flag ships clean and you add music in post-edit or YouTube's editor later. Use `--music <path>` if you have a chosen track.

Finish output: `<project>/final_video.mp4` and `<project>/voiceover.mp3` and `<project>/clips/shot_NNN.mp4`.

### Thumbnail generation

```bash
python ../shared/make_thumbnail.py --project <project>
```

Output: `<project>/thumbnail.png`. Review it. If it doesn't land, the thumbnail script is a vibe-codable territory — iterate on the prompt or the source frame until it lands.

### Upload

```bash
python upload.py --project <project>
```

What happens:
1. Reads script, storyboard, final_video.mp4
2. Calls Claude API to generate title/description/tags from the script content
3. Generates SRT subtitles from storyboard timing
4. Uploads video as PRIVATE
5. Uploads SRT as caption track
6. Uploads thumbnail.png
7. Prints YouTube Studio URL

**Known limitation: Claude-generated title may not match your locked title.** Open YouTube Studio after upload, navigate to the video, replace the title with your locked version before publishing. This is the current manual step until the script is upgraded to read a `metadata.json` from the project folder.

### Publication (in YouTube Studio)

After upload completes, open the Studio URL the script prints:

1. **Title** — replace auto-generated with your locked version
2. **Description** — review and edit. Keep the hook in the first 2 lines.
3. **Thumbnail** — verify it loaded; manually upload if not
4. **Tags** — add 5-10 relevant tags
5. **Audience** — Made for Kids: No
6. **Language** — English
7. **Category** — Education or appropriate
8. **Visibility** — Schedule for target window (typically Sunday/Monday evening US Eastern = 01:00 Warsaw next day)
9. **Save**

After publication, return to the video and **add the pinned comment**:
- Final Hours: dignity-register question about the protagonist's choice
- Success Coach: career-applicable question to the viewer
- Channel 3: literary question about the adapted work

Pinned comments generate the early engagement signal the algorithm watches.

---

## PART 2B — DUAL-MODE ARCHITECTURE (MODE A + MODE B)

*Added 5 June 2026 for the Synthetic Press launch series; rewritten same day after the pipeline was actually BUILT and proven end to end. Mode A is the existing stills→clips engine (all Final Hours / Success Coach video). Mode B is Remotion motion-graphics. Synthetic is the first channel to use both; the architecture is general. **Status as of 5 June 2026: Steps 1–4b proven on real hardware. Step 4c (real A render + full-episode audio spine + dual-mode assemble) is specified and not yet built — see the separate 4c spec doc.***

### The four principles (the whole thing hangs off these)

1. **The sentence decides the mode (upstream).** Every beat is born Mode A or Mode B because the *sentence* decides. A sentence describing a place/person/moment is Mode A — it wants a recreated scene. A sentence asserting a fact/number/quote/structure is Mode B — it wants the number drawn, the quote sourced, the structure built. You write in two registers the pipeline understands; you are not annotating after the fact. If you can't decide a beat's mode, it's doing two jobs — split it.

2. **Visual exclusivity (the load-bearing rule).** At any instant the screen belongs to *either* a Mode A recreated scene *or* a Mode B graphic — never both. One renderer owns the frame at a time. This makes the build tractable: exclusivity means the timeline is a pure **sequence** (clips butted end to end), so assemble needs **no compositing**. (Layering graphics *over* live scenes — the "underlay/Vox" look — is Phase 2 and needs a compositing stage. Cutaway-only for launch.) Narration pausing on a Mode B beat is an *editorial* choice, fully decoupled from the visual.

3. **The audio is the source of truth (shared spine).** Generate the voiceover, measure it with Whisper, hang visuals off the measurement — for *both* modes. A beat's measured duration is handed to whichever renderer it routes to: a NumberCounter given 3.1s counts over 3.1s; a recreated shot given 3.1s holds 3.1s. One measurement, two consumers. **WIRED & PROVEN (5 June, late): the audio leg is built end to end — `build_audio_script.py` (2a) assembles the full-episode read incl. found-lines; `generate_episode_vo.py` (2b) produces the real Victor VO; `build_beat_durations.py` (2c) wraps `align_with_whisper.py` to emit real per-beat `durations.json` (39 whisper-measured + 23 silent-hold for E1); `dispatch.py --durations` (2d) consumes it, replacing the word-count proxy. E1 real spoken runtime measured at 588s (9.8min) vs the proxy's 13.3min guess — the ~35% drift is gone. Proxy remains only as a no-durations-file fallback.**

4. **The tagged script IS the pipeline spec (the seam).** Because a Mode B beat is written in the known component vocabulary, scripting it *is* the design — the tag payload is the render spec. `grep '[B:'` on a finished script yields the exact component list the episode needs. Proven literally true: `parse_script.py` reads the tags into a complete beat list where every B beat already carries its full render payload.

### The chain, top to bottom (AS BUILT)

```
script.md  (tagged beats; the source of truth)
  → parse_script.py            → beats.json   (62 beats, mode A/B, full B payloads, found-lines)
  → [Mode B path]  dispatch.py --render   → npx remotion render → clips/beat_NN_B_<Component>.mp4
  → [Mode A path]  modea_beats.py         → synthetic_modeA_beats.json  (+ _index.json map)
                   recreation_pipeline.py stills --beats … → storyboard → stills → REVIEW GATE → Kling
                                                           → clips/shot_NNN.mp4
  → [4c, not yet] full-episode Victor VO over all 62 beats' narration → Whisper-align
  → [4c, not yet] dual-mode assemble: interleave A + B clips in true beat order via index map, 1080p
```

Two renderers feed one timeline. They are not two pipelines that merge — they are two renderers the dispatcher hands work to, both returning ordinary MP4 clips. By assemble time an A clip and a B clip are both just MP4s of known duration and matching resolution.

### THE FILES (as built, all in shared/, all committed)

- **`parse_script.py`** — Step 1. `script.md` → ordered beats. Each B beat carries component + full payload; each QuoteCard carries its spoken found-line (the `> "…"` blockquote above it). Validates against the six KNOWN_COMPONENTS; an unknown tag is the "seventh-component signal." `--json` writes beats.json. Parses only the body (between first `## COLD OPEN`/`## PART` and the spec/ledger/verification sections). E1 output: **62 beats, A:41 B:21**.
- **`dispatch.py`** — Steps 2+3. Routes each beat: A→`render_mode_a()` (stub, prints), B→`render_mode_b()` (REAL: payload→props→temp-JSON→`npx remotion render <CompId> <out> --props=<file> --frames=0-<n>`). `shape_props()` is the registry boundary — translates parsed payloads into the REAL prototype prop schemas. `--render` actually runs Remotion (default = dry-run, prints the command); `--only N,N` filters to specific beats. `REMOTION_DIR` env points at the Remotion project (default `~/Projects/remotion-learning`), so moving it later is one env var.
- **`modea_beats.py`** — Step 4b. Filters beats.json to mode==A, translates each into the recreation engine's `--beats` format (`{beats:[{narration, image_prompt, motion_prompt}]}`): `beat.visual`→`image_prompt`, `beat.narration`→`narration`, default motion (face-hold beats get a near-static motion so Kling won't warp the face). **CRITICAL: also writes `_index.json`** mapping engine shot index → original beat index (engine renders shot_001..shot_041 contiguously and has no idea which beats were Mode B holes; without this map the dual-mode assemble can't reorder). One beat = one shot (decided: the tagged script is already shot-designed).
- **`assemble_test.py`** — Step 4a (plumbing proof). ffmpeg placeholder generator + concat. Proved a real Mode B clip concatenates cleanly between Mode A placeholders. Superseded by the real 4c assemble but kept as the seam test.
- **`patch_channel_resolution.py`** — idempotent in-place patch that taught `recreation_pipeline.py` per-channel resolution: `ASPECT = _channel_aspect()` reads `width`/`height` from channel.json (default 1280×720 so Final Hours is untouched). All three resolution spots (image_size, held-clip scale, assemble trim scale) build from ASPECT.

### The REAL prototype prop schemas (what shape_props must emit)

From the committed Remotion prototype `Root.tsx` — these differ from the script's authoring payload, which is why `shape_props()` exists as a translator:

- **QuoteCard** `{quote, attribution, accentColor}` — RENDERS the quote on screen. ⚠ Conflicts with the no-karaoke/receipt doctrine (card should show attribution only, the line is in VO). Current behaviour: renders the found-line as `quote`. **Component upgrade needed: attribution-only / highlight-only variant.**
- **NumberCounter** `{endValue, prefix, suffix, label, accentColor}` — always counts 0→endValue. ⚠ No `from`/countdown (the $1B→$44M countdown renders 0→44M for now) and no `plainYear` (1997 renders "1,997"). **Two small component props needed: startValue+countdown, and plainYear.**
- **HighlightedHeadline** `{text, highlightPhrase, highlightColor, sweepStart}` — maps cleanly.
- **ChapterCard** `{eyebrow, title, accentColor}` — shape_props splits "Part One — The Dream" on the dash into eyebrow/title.
- **LowerThird** `{primary, secondary, accentColor}` — splits "Ilya Sutskever — co-author…" on the dash.
- **DocumentReveal** `{source, body, highlight, accentColor}` — maps text→source, show_line→body.

All six take `accentColor` (Synthetic `#3b5bdb` indigo, injected by shape_props). All hardcode `durationInFrames` at registration; the renderer overrides per-beat via `--frames`.

### The beat-type notation (authoring)

```
[A] *VISUAL: the jury filing in, from behind.* With those four words, a jury ended the most consequential lawsuit…

*Narrator voices the found line:*
> "We have a verdict."
[B:QuoteCard] the judge · U.S. District Court, Oakland · spring 2026
  highlight: "verdict"

[B:NumberCounter] from=0 to=650000000 prefix=$ label="Google acquires DeepMind, 2014"

[B:NumberCounter] to=1997 plain_year=true label="Deep Blue defeats the world champion"

[B:DocumentReveal] the founding statement · 11 December 2015
  show_line: "to benefit humanity as a whole, unconstrained by a need to generate financial return"
  source: OpenAI founding announcement

[B:ChapterCard] "Part Three — The Promise"
```

Rules:
- **Tag chosen as you write the sentence, not after.** Upstream principle made physical.
- **The narration is the same in both modes; the tag carries what the voice omits.** A QuoteCard's narration *is* the spoken found-line (the `> "…"` above the tag); the payload carries name/source/date. "The spoken line and its receipt": voice = words; card = attribution; `highlight:` = swept phrase. **No-karaoke:** the card never duplicates the full sentence as on-screen text the narrator reads verbatim.
- **Only the six components have tags.** A beat wanting something else is a deliberate decision to build a seventh, surfaced by the parser as a warning — not a thing to write around.
- **Every B beat is a no-fal, no-review beat.** Tag-counting a finished script gives the A/B ratio, fal exposure, and review-gate load before a single render.
- **Ratio is read, not enforced.** Band 60–70% A / 30–40% B is a smell test. E1 is scene-heavy (66% A) and that's correct.

### The true-up IS the human-voice swap

Audio is the source of truth, so swapping Inworld scratch (Victor) for Peter's human read is a **true-up, not a re-render**: drop in the human voiceover, re-run Whisper → match → assemble, and *every* visual timing re-derives for free — Mode A holds and Mode B counts alike. Nothing visual regenerates. Production model for Synthetic: **script → record scratch (Inworld Victor) → build all visuals against it → swap in human read → true-up → final.** (The recreation engine's `finish --assemble-only` already does zero-cost re-assembly; 4c extends this to the dual-mode timeline.)

### Resolution (decided 5 June)

Mode B Remotion renders 1920×1080. Mode A engine historically rendered 1280×720. **Decision: 1080p is the Synthetic master.** Implemented via per-channel resolution in channel.json (`width`/`height`), read by `_channel_aspect()`. Final Hours has no width/height → stays 720p, untouched. So both modes now render 1080p for Synthetic with no per-clip scaling needed at assemble.

### Build status (5 June 2026)

| Step | What | Status |
|---|---|---|
| 1 | tag parser (`parse_script.py`) | ✅ proven on box |
| 2 | dispatch routing (`dispatch.py`) | ✅ proven on box |
| 3 | real Mode B render (`render_mode_b` → Remotion) | ✅ real $650M clip rendered on laptop |
| 4a | assemble plumbing (B clip between A placeholders) | ✅ proven on laptop |
| 4b | Mode A translator + engine ingest under Synthetic channel | ✅ `OK Beat-script ingested: 41 beats` on box |
| 4c-audio | full-episode audio spine: VO + Whisper → real per-beat durations → dispatch consumes | ✅ proven on box (2a/2b/2c/2d) |
| 4c-rest | real A render (stills→gate→Kling) + dual-mode assemble | ⏳ specified, not built |

**Three known component-feature gaps (small Remotion tweaks, not pipeline work):** QuoteCard attribution-only variant; NumberCounter startValue+countdown; NumberCounter plainYear. None block 4c; each makes one beat render exactly as scripted.

The mental model in one line: **the tag is a routing instruction the author writes, the parser carries it, the dispatcher obeys it, two renderers feed one timeline, and (once 4c lands) the measured audio keeps them honest.**

---



## PART 2C — THE ORCHESTRATOR (the channel-agnostic machine)

*Written 5 June 2026 as intentional design BEFORE building, so the orchestrator is built from a settled design rather than discovered by accretion. This part defines the conductor that runs the whole post-script pipeline for ANY channel. The existing `orchestrate.py` (PART 2, six linear phases) is the Mode-A-only ancestor of this; this part describes what it becomes. **Status: designed here, not yet built. The dual-mode pieces it conducts are proven through Step 4b (see PART 2B build-status table); Step 4c builds the legs this conductor will run.***

### The thesis: one machine, many channels

The goal is a **single orchestrator** that is completely **channel-agnostic**. It does not know or care whether it is making Final Hours, Synthetic Press, or Lazarus. It reads one input artifact, discovers from that artifact what work needs doing, loads the relevant channel's identity from one config file, runs the necessary legs around the minimum number of human gates, and produces a finished video.

The payoff this protects: **adding a new channel that reuses existing capabilities costs one config file and zero code.** The machine is the moat — not any single channel. Channel N+1 is a `channel.json` plus content.

### The five design principles (these govern the whole machine)

**1. The sentence decides the mode.** Every beat is born Mode A (cinematic recreation) or Mode B (Remotion graphic) because the *sentence* decides — a place/person/moment wants a recreated scene; a fact/number/quote/structure wants a drawn graphic. Mode is a property of the writing, set by the author, never inferred by the machine. (Full treatment in PART 2B.)

**2. The voice decides the contract.** Audio is not one thing. A beat's audio has two independent axes, and together they decide how the audio leg treats it:
   - *Cardinality:* one voice (narration) vs. many voices (a cast). Carried by an optional `speaker` field per beat (default: `narrator`).
   - *Binding:* swappable vs. locked. **Narration and any off-camera / closed-mouth speech is SWAPPABLE** — it is a timing source only; the visuals are timed to it but not generated from it, so the voice can be replaced and everything re-times for free (the true-up). **Lip-synced on-camera speech is LOCKED** — the audio is a *render input* (mouths are animated to the specific waveform), so the voice must be final before render and a voice swap forces a re-render.
   
   The three live quadrants:
   | | Swappable | Locked |
   |---|---|---|
   | **One voice** | Final Hours, Synthetic | (n/a) |
   | **Many voices** | Lazarus v1 (heard, not seen speaking) | Lazarus v2 (lip-synced dialogue) |
   
   This is why "Lazarus with no lip-sync" rides the existing machine: multi-voice + swappable needs only a `speaker` field and a voice map — no new leg. Only lip-sync (locked) needs the new leg.

**3. The composition decides the legs.** The orchestrator scans the beats and runs only the legs the work requires:
   - Mode A beats present → run the **Mode A leg** (stills → review gate → Kling).
   - Mode B beats present → run the **Mode B leg** (Remotion render) + the **Mode B correctness gate**.
   - Any locked/lip-sync beats present → run the **lip-sync leg** (locked-audio contract).
   - Always → run the **audio leg** first (it is the timing source every other leg depends on).
   
   A channel is a *signature* over these legs, not a category. Final Hours = {audio, A}. Synthetic = {audio, A, B}. Lazarus v1 = {audio (multi-voice), A, optionally B for titles/credits}. Lazarus v2 = {audio (multi-voice, some locked), A, B, lip-sync}. The machine composes legs; the channel is which legs its scripts tend to use.

**4. The channel header decides the look.** The script declares its channel in a header line; `parse_script.py` stamps it into `beats.json`. The orchestrator reads that flag and loads `<channel>/channel.json`, which is the channel's **complete cross-mode identity** in one file: Mode A `style_suffix`, the `voices` map, render `width`/`height`, and a `mode_b` block (accent color, fonts, wordmark asset path, palette tokens). Composition decides the *machinery*; the channel flag decides the *identity*. They are orthogonal: a Final Hours video that happens to use one ChapterCard runs the Mode B leg (machinery) but stays Final Hours (identity) because that is what its header declares. No false positives from auto-detection, because identity is never inferred.

**5. Maximal orchestration around minimal gates.** Everything that can run unattended, does. The only stops are genuine quality firewalls. Run unattended *to* the first gate; run unattended *after* it *to* done. Two gates only:
   - **Stills review gate** (Mode A) — *aesthetic* firewall. The human-in-loop seam that protects recreation quality. Heavy: browser review over the tunnel. Non-negotiable; do not automate away.
   - **Mode B correctness gate** — *factual* firewall. A contact sheet of the rendered cards (numbers, quotes, attributions). Light: "do these read correctly? y/n." Different in kind from the stills gate — it catches a misattributed quote or wrong figure, the errors that most damage a prestige-documentary brand. Cheaper to catch here than after publish.

### The input boundary (precise)

**The orchestrator's sole input is `beats.json`. It never reads `script.md`.**

The script and the beat-writing are the *human-and-Claude phase* — the thinking, tagging, fact-locking, and discussion that happen before any machine runs. That phase produces two artifacts: `script.md` (human-readable source of truth) and, via `parse_script.py`, `beats.json` (the machine spec). The orchestrator begins where the thinking ends.

```
  [ HUMAN + CLAUDE PHASE ]   discuss → write → tag → fact-lock
            script.md  ──parse_script.py──▶  beats.json
                                                  │
  ═══════════════════════════════════════════════╪═════════  ◀── orchestrator input boundary
                                                  │
  [ ORCHESTRATOR PHASE ]   beats.json is the only input
```

`beats.json` is self-sufficient: it carries the `channel` flag, and per beat the mode, payload, narration, found-line, `speaker`, and any lock flag. Everything the machine needs is in it. (The Mode A leg internally produces the recreation engine's own `storyboard.json` from the translated beats — but that is the leg's private business, downstream of the orchestrator's single input.)

Principle: **the thinking produces a spec; the orchestrator executes the spec.** One input artifact, fully produced by the phase before.

### The machine, top to bottom

```
beats.json  (carries `channel`; per-beat mode / speaker / lock / payload)
   │
   ├─▶ read `channel` ──▶ load <channel>/channel.json  (identity: style_suffix, voices, w/h, mode_b tokens)
   │
   ├─▶ scan composition ──▶ decide which legs to run
   │
   ▼
 ┌───────────────── LEGS (run to the stills gate) ─────────────────┐
 │                                                                  │
 │  AUDIO leg (always, FIRST — timing source)                       │
 │    assemble full narration in beat order (incl. found-lines;     │
 │      per-beat speaker via voices map) → VO → Whisper align        │
 │      → per-beat measured durations                               │
 │                                                                  │
 │  MODE B leg (if any B beats; unattended)                          │
 │    payload → props (accent/fonts/wordmark from channel.json)      │
 │      → remotion render → beat_NN_B_*.mp4 (at beat's duration)     │
 │                                                                  │
 │  MODE A leg (if any A beats; up to the gate)                      │
 │    translate → engine storyboard → stills                         │
 │                                                                  │
 └───────────────────────────┬──────────────────────────────────────┘
                             │
                   ╳ STILLS REVIEW GATE (aesthetic; human, heavy)
                             │
                   ╳ MODE B CORRECTNESS GATE (factual; human, light)
                             │
 ┌───────────────── LEGS (run to done) ────────────────────────────┐
 │  MODE A leg (continue): Kling animate → shot_NNN.mp4              │
 │  LIP-SYNC leg (if any locked beats; locked-audio contract)        │
 └───────────────────────────┬──────────────────────────────────────┘
                             │
                   DUAL-MODE ASSEMBLE
            interleave all clips in true beat order (index map),
            each held to its audio-measured duration,
            over the (possibly multi-voice) VO, at channel w/h
                             │
                             ▼
                       final_video.mp4
```

Sequential-unattended is acceptable for the legs that *could* parallelize (audio ∥ Mode B ∥ Mode A-stills) — matches the banked "sequential not parallel" instinct. Expressing them as legs makes the parallelism *available* later without redesign; it is not required now. The discipline that matters is the ordering constraint: **the audio leg runs first because both render legs depend on its durations.** (This is the orchestration consequence of "audio is the source of truth": durations must exist before either renderer is dispatched, or Mode B renders at guessed lengths. The audio leg is now BUILT — see PART 2B principle 3: `build_audio_script.py` → `generate_episode_vo.py` → `build_beat_durations.py` → `dispatch.py --durations`. The orchestrator's job is to sequence these before the render legs.)

### channel.json — the complete cross-mode identity

One file fully describes a channel across both modes. The orchestrator and both render legs read only from here for identity.

```jsonc
{
  "name": "synthetic_press",
  "voices": { "narrator": "Victor" },          // map, not a single id — Lazarus adds characters
  "width": 1920, "height": 1080,               // per-channel resolution (read by _channel_aspect)
  "style_suffix": "...prestige documentary...",// Mode A look (recreation engine prompt suffix)
  "mode_b": {                                  // Mode B look — read by shape_props (replaces hardcoded accent)
    "accent_color": "#3b5bdb",
    "fonts": { "primary": "Inter" },
    "wordmark": "assets/synthetic_wordmark.svg",// designer asset, placed by components
    "palette": { "navy": "#0a1628", "amber": "#d4a017", "bone": "#f4f1ea", "rust": "#8b3a1e" }
  },
  "default_music_prompt": "..."
}
```

The accent color currently hardcoded in `dispatch.py`'s `shape_props` (`#3b5bdb`) moves here, exactly as resolution did. The designer's wordmark (delivered as SVG) is a `mode_b.wordmark` token — components import it and place it; the ChapterCard / end-card / lower-third pull it from channel.json. Brand and machine meet in this one file: the wordmark is not decoration bolted on afterward, it is an asset the pipeline imports through config, like style_suffix and accent.

### Adding a new channel (the reusability contract — stated precisely)

**New channel that reuses existing legs → one new `channel.json` + a channel folder + content. Zero code.**

That is the whole cost, because every piece of the machine reads from `beats.json` and `channel.json` and is channel-agnostic: the parser, the orchestrator, both render legs, the recreation engine, the Remotion components, the audio leg, the assemble. None contains a channel name. A new channel is a new *signature over existing legs* expressed entirely in config.

**The one exception, by design: a new channel that needs a capability no leg provides → build that leg once, then it joins the reusable set forever.** You cannot config your way to a capability that does not exist (declaring `"lipsync": true` does nothing until the lip-sync leg is built). But the architecture guarantees the capability is added *as a leg*, in one place, and is then available to every channel via their channel.json.

The rule in one line: **new sentence from existing words is free; a new word is built once, then free forever.** The legs are the vocabulary; channels are sentences in it.

What is reusable (everything that is machinery): parse, dispatch, translate, orchestrator, recreation engine, Remotion components, audio leg, Whisper alignment, assemble. What is per-channel (everything that is identity): style_suffix, voices map, resolution, Mode B tokens, wordmark — all in `channel.json`. What is per-episode: the script, the beats, the content. Three clean layers; nothing channel-specific leaks into the machinery layer.

### Future legs (anticipated, not built)

- **Lip-sync leg** (Lazarus v2, ~2027–28). Locked-audio contract: voice final before render; a voice swap re-renders synced shots (the true-up is NOT free for this leg). Depends on the Hetzner avatar capability. The `speaker` field and `voices` map are added now so the audio leg is multi-voice-ready before lip-sync exists.
- **Mode B as a universal capability**, not Synthetic-exclusive. Any channel may use it: Lazarus for opening titles and end credits ("just like a real movie"), Final Hours could use a ChapterCard. The mode is not the channel; the *mix* is the channel's fingerprint.
- **Compositing / underlay** (graphics over live scenes — the "Vox" look), which would break visual exclusivity and need a compositing stage. Phase 2+. Cutaway-only until then.

### What to build for the orchestrator (the slice)

This conductor is built on top of the legs from PART 2B's Step 4c. Build order, cheapest-and-safest first:
1. **`channel` header in `script.md`** + `parse_script.py` stamps it into `beats.json`. Tiny.
2. **`speaker` field** plumbed through the parser (default `narrator`) + **`voices` map** in channel.json (one entry for current channels — no behaviour change). Tiny, anticipatory.
3. **Move Mode B identity tokens** (accent, later fonts/wordmark) **into channel.json**; `shape_props` reads them. Small; removes the hardcoded accent.
4. **Leg-detection** in the orchestrator: scan beats → decide legs. Small.
5. **Audio leg to the front** (the 4c audio spine), feeding durations to both renderers. This is the real work — shared with 4c.
6. **Mode B correctness gate** (contact sheet + y/n). Small.
7. **Dual-mode assemble** as the convergence (the 4c assembler).

Final Hours falls through unchanged throughout: a Mode-A-only `beats.json` stamped `final-hours` triggers no Mode B leg, no Mode B gate, single-voice audio — i.e. exactly today's behaviour, now expressed as one signature of the general machine.

The mental model in one line: **the thinking writes a spec; the spec declares its channel and its modes; the machine reads the spec, loads that channel's identity, runs only the legs the spec needs around the two gates that protect quality and truth, and converges every clip onto one audio-timed timeline — and it does this identically for every channel, so the next channel is a config file.**

---

Common issues and resolutions:

**"No module named 'srt_generator'"** when running upload.py
→ Missing symlink. Run `ln -s ../shared/srt_generator.py srt_generator.py` from the channel root.

**"ANTHROPIC_API_KEY not set"** or similar
→ Missing or broken .env symlink. Run `ln -s ../.env .env` from the channel root and verify with `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(bool(os.getenv('ANTHROPIC_API_KEY')))"`.

**"FileNotFoundError: 'six_minutes/clips'"** or similar during finish
→ CWD wrong. The pipeline expects to be run from the channel root, not from inside the project folder. `cd ..` to the channel root and re-run.

**"Missing client_secret.json"** when running auth.py
→ Auth.py has a known variable-swap bug. Lines 34-35 should be `CLIENT_SECRET = "client_secret.json"` and `TOKEN_FILE = "token.json"` — these are sometimes inverted. Check and fix if needed.

**Upload errors with permission denied or no channel found**
→ Wrong Google account active in browser when auth.py was run. Delete `token.json`, switch browser to the correct Google account, re-run `python auth.py`.

**Stills look drifted from canon despite canon being defined**
→ Canon resolution works but wardrobe and expression are notoriously unstable. Restate these explicitly in the prompt body, not just via canon tag. Banked rule.

**Pipeline tries to generate stills against a canon-unaware storyboard**
→ Use `--storyboard-only` flag with `--script` mode to stop after storyboard generation, then edit the storyboard to add canon awareness before re-running with `--beats`.

**fal credits run out mid-render**
→ Auto-top-up should handle this if enabled. If not enabled, set it in the fal dashboard. Re-running finish should resume from where it left off (clips already rendered are not re-rendered).

**Video file too large for YouTube upload (>256GB)**
→ Won't happen at current resolution and length. Not a real concern.

**Voice sounds wrong**
→ Check channel.json voice_id. Reed for Success Coach, Ashley for Final Hours. Banked rule: verify voice_id before every finish run.

**Long single beats (>~10s) hold one Kling clip far past its native length** *(banked 5 June 2026, Synthetic E1 audio leg)*
→ When the audio leg measured E1's real per-beat durations, the longest single recreated beat came out at ~32s (some spoken A beats run 15-19s). Kling clips are only ~5s native. A 32s beat would either freeze on a held frame or stretch one clip well past where it looks good. This is a **4c / dual-mode-assemble concern, not an audio concern** — the audio measurement is correct; it's the *visual* side that has to cover that duration. Options when assembling: hold/slow the clip, loop subtle motion, or (better) break a long beat into 2-3 sub-shots at assemble time so no single Kling clip stretches. The word-count proxy HID this (it spread time evenly); real Whisper durations surface it. Decide the long-beat policy when building the 4c assembler. Note this also argues for the banked "beat-multiples" idea (PART 4) — a long beat is really N visual shots over one narration span.

---

## PART 4 — KNOWN DEFERRED IMPROVEMENTS

Items banked but not yet built. Address when blocking or when time permits.

**Upload script reads metadata.json from project folder before falling back to Claude generation.** Eliminates the manual title-fix step in YouTube Studio. ~30 minutes to build.

**Fix the variable-swap bug in auth.py canonically in shared/, not channel copies.** Move auth.py and upload.py to `shared/`, make them channel-aware via CWD detection of channel.json. ~60 minutes.

**Whisper-based SRT instead of even-spacing.** Current captions drift against spoken words. *Note (5 June 2026): Whisper alignment is no longer merely a captions nicety — it is now the shared spine for the dual-mode architecture (PART 2B): it times both Mode A and Mode B off measured audio and powers the human-voice true-up. Being built for the Synthetic launch. SRT generation should hang off the same Whisper measurement once it exists.*

**Pre-render cost estimate.** Print expected fal spend before finish runs, based on shot count. ~30 lines of code. Soft guardrail against runaway costs.

**Beat-multiples for rhythmic variation.** Allow individual beats to be integer multiples of base unit (peak beats 2×) for rhythmic variation. Probably 50-100 lines of changes. Not urgent.

**Cloud migration to Hetzner.** ~€5/month VPS for unattended overnight rendering. Day-off task. Worth doing before video count is large enough that overnight laptop renders block morning workflow. Install Claude Code on Hetzner as part of provisioning for the agentic workflow.

**Pipeline self-tests.** `rulebook --count`, `--validate` modes for env vars, channel.json structure, token file existence, fal connectivity. Small ergonomic wins, none blocking.

---

## PART 5 — OPERATING REMINDERS

Small things easy to forget across sessions:

- **The venv name is `success-coach`** for historical reasons. Serves both channels. Don't rename it.
- **Channel detection is by `channel.json` marker**, found by walking up from CWD. `cd final-hours/` or `cd success-coach/` before running pipeline commands.
- **Most commands run from the channel root, not the project folder.** The `--project <name>` argument is resolved against CWD.
- **First run of `make_thumbnail.py` after environment reset downloads rembg U2Net model** (~170MB) into `~/.u2net/`. Takes 30-90 seconds the first time, 1-3 seconds thereafter.
- **`grep -c '_expand_canon\|_load_beats_with_canon'` on the pipeline** is a sanity check that the canon mechanism is in place; should return ~6 matches.
- **`shared/rulebook.json.pre_migration_backup`** exists from the 30 May rulebook split — pre-multi-channel snapshot, available if needed.
- **OAuth client `youtube-upload-test-497220` is owned by peteralkema2@gmail.com** but supports test users from other accounts (including peteralkema6 for Success Coach). Add new accounts as test users before running auth flow.

---

## PART 6 — EVOLUTION

This document is a living artefact. Update it when:

- A new failure mode is encountered and resolved
- A new step is added to the workflow
- A pipeline command's interface changes
- A new channel is launched (capture any channel-specific quirks)
- A deferred improvement gets built and changes the workflow

Date the changes at the top of the document. Bank rules in the rulebook for things that affect prompts; bank workflow lessons here.

The goal of this document is that future-Peter (or a future hire) could pick up the system without re-deriving it from chat threads.
