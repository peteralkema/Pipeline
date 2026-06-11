# Machina
*The machine — the full operational lifecycle from topic to published video, across all channels. (Formerly "Pipeline Playbook"; renamed to pair with `ante-machinam.md`, "before the machine.")*
*Last updated: 11 June 2026 — renamed to Machina; craft references reconciled to ante-machinam v2.0 (which absorbed `script-craft-principles.md`). Prior: 5 June 2026 (late) — PART 2B rewritten as-built + PART 2C (the orchestrator design); PART 2D orchestrator build status (6 June). Earlier: 30 May 2026.*

This is the single source of truth for the **operational / machine** layer — every command, the orchestrator, the legs and gates, troubleshooting. The **craft + pre-machine** layer is its companion, `ante-machinam.md`: read its Part IV for the craft canon and Part VI for the threshold into this machine (ante-machinam absorbed `script-craft-principles.md` at v2.0). Read both before starting any new project. Update this document when banking new *operational* rules from production.

---

## PART 1 — QUICK REFERENCE CARD

The 12-step lifecycle. Use this as muscle memory once you know the system.

### Pre-production (research + script)

**Step 1.** Pick a topic. Use NexLev to validate demand. Check that no direct format competitor exists in the lane. Bank the decision in the channel's backlog document with rationale.

**Step 2.** Research the protagonist and historical/situational facts. For Final Hours, use web search for documented sources, family accounts, and contemporary reporting. For Success Coach, use lived experience and published research.

**Step 3.** Decide the title (use the channel's title pattern), the protagonist or subject (one specific human or place), and apply the craft canon. Reference `shared/docs/ante-machinam.md` — Part IV is the full craft canon (formerly `script-craft-principles.md`), Part V carries the per-channel register. Audit the script against the Part IV pre-lock table (IV.7) before lock.

**Step 4.** Write the script as a markdown document at `<channel>/projects/<project>/script.md`. Include production notes and capability stretches. (Note: there are no authored "silent beats" under the current machine — a wordless beat halts the build; see ante-machinam Constitution §1.) Keep the canonical script here.

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
│       ├── machina.md            # This document (the machine — operational reference)
│       ├── ante-machinam.md      # The pre-machine bible (Constitution + craft canon + threshold)
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
│       ├── script-craft-principles.md   # RETIRED → stub → shared/docs/ante-machinam.md Part IV
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

**4. Extract pure narration to `<project>_script.txt`** — strip production notes, visual cues, beat headers. Just prose narration.

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

*(For motion-conversion — making the stills actually animate rather than slow-zoom — see ante-machinam Constitution §7 + Part III "Author for motion": author a kinetic, drift-safe foreground subject into every VISUAL line. Banked at the Sacred Dawn launch.)*

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

*Written 5 June 2026 as intentional design BEFORE building, so the orchestrator is built from a settled design rather than discovered by accretion. This part defines the conductor that runs the whole post-script pipeline for ANY channel. The existing `orchestrate.py` (PART 2, six linear phases) is the Mode-A-only ancestor of this; this part describes what it becomes. **Status: designed here, then largely built — see PART 2D for the as-of-6-June build status. The five live channels (Final Hours, Sacred Dawn, You Had To Be There, Success Coach, plus Synthetic launching) run through this conductor.***

### The thesis: one machine, many channels

The goal is a **single orchestrator** that is completely **channel-agnostic**. It does not know or care whether it is making Final Hours, Sacred Dawn, or Lazarus. It reads one input artifact, discovers from that artifact what work needs doing, loads the relevant channel's identity from one config file, runs the necessary legs around the minimum number of human gates, and produces a finished video.

The payoff this protects: **adding a new channel that reuses existing capabilities costs one config file and zero code.** The machine is the moat — not any single channel. Channel N+1 is a `channel.json` plus content. (Proven again at the Sacred Dawn launch: a fifth live channel added with one `channel.json` and a script, zero code.)

### The five design principles (these govern the whole machine)

**1. The sentence decides the mode.** Every beat is born Mode A (cinematic recreation) or Mode B (Remotion graphic) because the *sentence* decides — a place/person/moment wants a recreated scene; a fact/number/quote/structure wants a drawn graphic. Mode is a property of the writing, set by the author, never inferred by the machine. (Full treatment in PART 2B.)

**2. The voice decides the contract.** Audio is not one thing. A beat's audio has two independent axes, and together they decide how the audio leg treats it:
   - *Cardinality:* one voice (narration) vs. many voices (a cast). Carried by an optional `speaker` field per beat (default: `narrator`).
   - *Binding:* swappable vs. locked. **Narration and any off-camera / closed-mouth speech is SWAPPABLE** — it is a timing source only; the visuals are timed to it but not generated from it, so the voice can be replaced and everything re-times for free (the true-up). **Lip-synced on-camera speech is LOCKED** — the audio is a *render input* (mouths are animated to the specific waveform), so the voice must be final before render and a voice swap forces a re-render.
   
   The three live quadrants:
   | | Swappable | Locked |
   |---|---|---|
   | **One voice** | Final Hours, Sacred Dawn, Synthetic | (n/a) |
   | **Many voices** | Lazarus v1 (heard, not seen speaking) | Lazarus v2 (lip-synced dialogue) |
   
   This is why "Lazarus with no lip-sync" rides the existing machine: multi-voice + swappable needs only a `speaker` field and a voice map — no new leg. Only lip-sync (locked) needs the new leg.

**3. The composition decides the legs.** The orchestrator scans the beats and runs only the legs the work requires:
   - Mode A beats present → run the **Mode A leg** (stills → review gate → Kling).
   - Mode B beats present → run the **Mode B leg** (Remotion render) + the **Mode B correctness gate**.
   - Any locked/lip-sync beats present → run the **lip-sync leg** (locked-audio contract).
   - Always → run the **audio leg** first (it is the timing source every other leg depends on).
   
   A channel is a *signature* over these legs, not a category. Final Hours / Sacred Dawn = {audio, A}. Synthetic = {audio, A, B}. Lazarus v1 = {audio (multi-voice), A, optionally B for titles/credits}. Lazarus v2 = {audio (multi-voice, some locked), A, B, lip-sync}. The machine composes legs; the channel is which legs its scripts tend to use.

**4. The channel header decides the look.** The script declares its channel in a header line; `parse_script.py` stamps it into `beats.json`. The orchestrator reads that flag and loads `<channel>/channel.json`, which is the channel's **complete cross-mode identity** in one file: Mode A `style_suffix`, the `voices` map (or `voice_id`), render `width`/`height`, and a `mode_b` block (accent color, fonts, wordmark asset path, palette tokens). Composition decides the *machinery*; the channel flag decides the *identity*. They are orthogonal. *(Gotcha banked at the Sacred Dawn launch: the voice key is snake_case `voice_id` — a `voiceId` typo silently falls back to Victor. Diff a new channel.json against a known-good one before the first run.)*

**5. Maximal orchestration around minimal gates.** Everything that can run unattended, does. The only stops are genuine quality firewalls. Run unattended *to* the first gate; run unattended *after* it *to* done. Two gates only:
   - **Stills review gate** (Mode A) — *aesthetic* firewall. The human-in-loop seam that protects recreation quality. Non-negotiable; do not automate away.
   - **Mode B correctness gate** — *factual* firewall. A contact sheet of the rendered cards (numbers, quotes, attributions). Light: "do these read correctly? y/n." Catches a misattributed quote or wrong figure — the errors that most damage a prestige-documentary brand. Cheaper to catch here than after publish.

### The input boundary (precise)

**The orchestrator's sole input is `beats.json` (the `{header,beats}` wrapper, `beats_full.json`). It never reads `script.md`.**

The script and the beat-writing are the *human-and-Claude phase* — the thinking, tagging, fact-locking, and discussion that happen before any machine runs (the ante-machinam layer). That phase produces two artifacts: `script.md` (human-readable source of truth) and, via `parse_script.py`, `beats.json` (the machine spec). The orchestrator begins where the thinking ends.

```
  [ HUMAN + CLAUDE PHASE ]   discuss → write → tag → fact-lock   (ante-machinam layer)
            script.md  ──parse_script.py──▶  beats.json
                                                  │
  ═══════════════════════════════════════════════╪═════════  ◀── orchestrator input boundary (Machina)
                                                  │
  [ ORCHESTRATOR PHASE ]   beats.json is the only input
```

`beats.json` is self-sufficient: it carries the `channel` flag, and per beat the mode, payload, narration, found-line, `speaker`, and any lock flag. Everything the machine needs is in it.

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
 │  AUDIO leg (always, FIRST — timing source)                       │
 │    assemble full narration in beat order → VO → Whisper align    │
 │      → per-beat measured durations  (+ audio-continuity QC)       │
 │  MODE B leg (if any B beats; unattended)                          │
 │    payload → props (accent/fonts/wordmark from channel.json)      │
 │      → remotion render → beat_NN_B_*.mp4 (at beat's duration)     │
 │  MODE A leg (if any A beats; up to the gate)                      │
 │    translate → engine storyboard → stills                         │
 └───────────────────────────┬──────────────────────────────────────┘
                             │
                   ╳ STILLS REVIEW GATE (aesthetic; human, heavy)
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
            over the (possibly multi-voice) VO + ducked music bed, at channel w/h
                             │
                             ▼
                       final_video.mp4
```

The ordering constraint that matters: **the audio leg runs first because both render legs depend on its durations.** (Durations must exist before either renderer is dispatched, or Mode B renders at guessed lengths.)

**Music belongs to ASSEMBLE, not the audio leg.** The audio leg produces ONLY the voiceover + per-beat durations; it has no music. Music is a ducked bed laid *under* the finished VO at assemble time, independent of per-beat timing. The mux logic lives inside `recreation_pipeline.py`'s `assemble()`; the dual-mode (Synthetic) assembler must PORT it in — the voice+music `amix` at `VOICE_LEVEL = 1.15` / `MUSIC_LEVEL = 0.07`; loop-to-cover (concat-repeat then trim); bed from the channel's `default_music_prompt`, with `--music <file>` to override or `--no-music` to skip. Per-channel music identity lives in channel.json, like style_suffix.

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
    "wordmark": "assets/synthetic_wordmark.svg",
    "palette": { "navy": "#0a1628", "amber": "#d4a017", "bone": "#f4f1ea", "rust": "#8b3a1e" }
  },
  "default_music_prompt": "..."
}
```

*(Mode-A-only channels carry the simpler shape proven at the Sacred Dawn launch: `name`, `voice_id` (snake_case), `style_suffix`, `default_music_prompt`, `base_canon`, `upload` — no `width`/`height` needed, the default works; no `mode_b` block needed.)*

The accent color currently hardcoded in `dispatch.py`'s `shape_props` (`#3b5bdb`) moves here, exactly as resolution did. Brand and machine meet in this one file.

### Adding a new channel (the reusability contract — stated precisely)

**New channel that reuses existing legs → one new `channel.json` + a channel folder + content. Zero code.**

That is the whole cost, because every piece of the machine reads from `beats.json` and `channel.json` and is channel-agnostic: the parser, the orchestrator, both render legs, the recreation engine, the Remotion components, the audio leg, the assemble. None contains a channel name. A new channel is a new *signature over existing legs* expressed entirely in config. (Sacred Dawn proved this on 10–11 June: conceived, configured, and shipped its first video with no code change.)

**The one exception, by design: a new channel that needs a capability no leg provides → build that leg once, then it joins the reusable set forever.** You cannot config your way to a capability that does not exist (declaring `"lipsync": true` does nothing until the lip-sync leg is built).

The rule in one line: **new sentence from existing words is free; a new word is built once, then free forever.** The legs are the vocabulary; channels are sentences in it.

### Per-film look: the channel owns the frame, the film owns the interior

*(Design principle banked 6 June 2026, prompted by Lazarus Films. Shipped as the look-resolver Phase 1 for You Had To Be There on 9 June — per-job `look.json` overrides the channel `style_suffix`. Final Hours, Sacred Dawn, and Synthetic use a uniform per-channel look.)*

Look resolves **channel-then-project.** `channel.json` provides the *default* identity (style_suffix, Mode B tokens, palette). A film/job may carry a per-project **`look.json`** (`{"look":"hi8_90s"}`) that *overrides* those defaults. `look_resolver.py` walks up from the still's output path to find it. Resolution order: channel defaults → project overrides → resolved look handed to the legs. The machinery is unchanged (it still reads a resolved config); it resolves two layers instead of one.

- **Most channels never use the override** — Final Hours, Sacred Dawn, Synthetic set one look in channel.json.
- **You Had To Be There and Lazarus are built on the override** — per-job decade looks / per-film art direction in the content layer.

**What stays constant vs. what varies (for Lazarus, the line that protects the brand):** the channel owns **the frame and the signature** (wordmark, lockup, title-card frame, end-card); the film owns **the interior** (palette, in-content type, grade, style_suffix). The prestige-anthology pattern (Black Mirror, Criterion): interiors vary, connective tissue is rigorously constant. Phase 1 = stills look only; **Phase 2 (not built) = the grade layer** (`film_emulate.py`) for true VHS/digicam texture.

### Future legs (anticipated, not built)

- **Lip-sync leg** (Lazarus v2, ~2027–28). Locked-audio contract: voice final before render; a voice swap re-renders synced shots. Depends on the Hetzner avatar capability. The `speaker` field and `voices` map are added now so the audio leg is multi-voice-ready before lip-sync exists.
- **Mode B as a universal capability**, not Synthetic-exclusive. Any channel may use it (Lazarus titles/credits; a Final Hours ChapterCard). The mode is not the channel; the *mix* is the channel's fingerprint.
- **Compositing / underlay** (graphics over live scenes — the "Vox" look), which would break visual exclusivity and need a compositing stage. Phase 2+. Cutaway-only until then.

The mental model in one line: **the thinking writes a spec; the spec declares its channel and its modes; the machine reads the spec, loads that channel's identity, runs only the legs the spec needs around the two gates that protect quality and truth, and converges every clip onto one audio-timed timeline — identically for every channel, so the next channel is a config file.**

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

**Voice sounds wrong / log says a different voice than expected**
→ Check channel.json `voice_id` (snake_case — `voiceId` silently falls back to Victor). Banked rule: verify voice_id before every finish run, and **listen at the audio gate** regardless of the printed label — the audio leg prints a hardcoded "Victor" string; the real read is whatever `voice_id` resolves to (confirmed at the Sacred Dawn launch, where Elliot rendered correctly while the log said Victor).

**A long box run got orphaned by a dropped SSH pipe (e.g. at the stills gate)**
→ Run long box jobs inside `tmux` (`tmux new -s orch`; `tmux attach -t orch` to recover). If a run is orphaned *after* the stills are approved, recover the animate step standalone from the project dir: `python ~/Pipeline/shared/recreation_pipeline.py finish --project modea --animate-only` — it reads the existing stills/durations and re-spends nothing already done. (Banked at the Sacred Dawn launch.)

**Clips look static / slow-motion**
→ Two different problems, fixed in this order. (1) Slow-motion = over-stretch: too few beats for the runtime (a clip slow-filled past ~3× reads as dead). Fix by authoring shorter beats (ante-machinam Constitution §6). (2) Static = no foreground subject for Kling to move (a wide landscape animates as a dead slow-zoom). Fix by authoring a kinetic, drift-safe foreground subject into every VISUAL line (ante-machinam Constitution §7 + Part III "Author for motion"). Fix granularity first — motion in an over-stretched clip smears worse.

**Long single beats (>~10s) hold one Kling clip far past its native length** *(banked 5 June 2026, Synthetic E1 audio leg)*
→ When the audio leg measured E1's real per-beat durations, the longest single recreated beat came out at ~32s (some spoken A beats run 15-19s). Kling clips are only ~5s native. Options when assembling: hold/slow the clip, loop subtle motion, or (better) break a long beat into 2-3 sub-shots so no single Kling clip stretches. The word-count proxy HID this; real Whisper durations surface it. This is the same root cause as the over-stretch issue above — the authored fix (shorter beats) is upstream of the assemble-time fix.

---

## PART 4 — KNOWN DEFERRED IMPROVEMENTS

Items banked but not yet built. Address when blocking or when time permits.

**Channel-agnostic upload step with a batch exit-gate.** Single-video jobs auto-upload with per-project metadata; batched (multi-video) jobs must exit at `final_video.mp4` (header flag, e.g. `parts: 4`). Until built, all uploads are manual via Studio (category = Entertainment, add tags). *(Sacred Dawn uploads are manual until this lands.)*

**Upload script reads metadata.json from project folder before falling back to Claude generation.** Eliminates the manual title-fix step in YouTube Studio. (Largely superseded by the header-as-metadata model — the header *is* the title/description/tags — but the per-channel uploader still needs wiring.)

**Fix the variable-swap bug in auth.py canonically in shared/, not channel copies.** Move auth.py and upload.py to `shared/`, make them channel-aware via CWD detection of channel.json. ~60 minutes.

**Auto-launch the review server** in the Mode A leg before the stills gate (kill stale on :8001 first via `lsof -ti :8001 | xargs kill -9`, tear down on `go`). The gate banner already *claims* "always on" but the operator still pastes the `review.py` command by hand. Also: the stills-gate prompt still prints the old tunnel instructions.

**Whisper-based SRT instead of even-spacing.** Whisper alignment is now the shared spine (PART 2B); SRT generation should hang off the same measurement.

**Pre-render cost estimate.** Print expected fal spend before finish runs, based on shot count. Soft guardrail.

**Beat-multiples for rhythmic variation.** Allow individual beats to be integer multiples of base unit (peak beats 2×).

**Pipeline self-tests.** `rulebook --count`, `--validate` for env vars, channel.json structure, token file existence, fal connectivity.

---

## PART 5 — OPERATING REMINDERS

Small things easy to forget across sessions:

- **The venv name is `success-coach`** (laptop) / `pipeline` (Hetzner box). Don't rename.
- **Channel detection is by `channel.json` marker**; resolution is now project-anchored (the voice/look is decided by *what you're rendering*, not *where you launched from* — fixed 9 June).
- **Most commands run from the channel root, not the project folder.** The `--project <name>` argument is resolved against CWD; the orchestrator (`orchestrate.py`) is run from the repo root with `--project <slug>`.
- **Run long box jobs in `tmux`** (`orch` session) so a dropped SSH pipe can't orphan a run parked at a gate.
- **No `--from` resume** — a re-run re-spends every leg from the top. Review carefully at the stills gate; recover an orphaned post-stills run with `finish --animate-only`.
- **First run of `make_thumbnail.py` after environment reset downloads rembg U2Net model** (~170MB) into `~/.u2net/`. 30-90s first time, 1-3s thereafter.
- **OAuth client `youtube-upload-test-497220` is owned by peteralkema2@gmail.com**; supports test users from other accounts. Add new accounts as test users before running the auth flow. (Final Hours has working auth; Sacred Dawn / Synthetic / others: not set up.)

---

## PART 6 — EVOLUTION

This document is a living artefact. Update it when:
- A new failure mode is encountered and resolved
- A new step is added to the workflow
- A pipeline command's interface changes
- A new channel is launched (capture any channel-specific quirks)
- A deferred improvement gets built and changes the workflow

Date the changes at the top. Bank rules in the rulebook for things that affect prompts; bank *operational* workflow lessons here, and *craft/authoring* lessons in `ante-machinam.md`. The goal: future-Peter (or a future hire) could pick up the system without re-deriving it from chat threads.

---

# PART 2D — ORCHESTRATOR BUILD STATUS (as of 6 June 2026)

*Records what is actually BUILT and PROVEN of the orchestrator, so future-Peter never wonders "did we finish that?". Update the status markers as legs land. Full cold-start detail: `shared/docs/SESSION-NOTES-2026-06-06-orchestrator.md`. (Note: since this snapshot, the Mode A leg + stills gate + animate are proven live — Sacred Dawn shipped end-to-end through them on 10–11 June.)*

## The machine, leg by leg — current status

| Stage | What it does | Status |
|---|---|---|
| **Kickoff + banner** | `orchestrate.py` run from repo root; banner; interactive prompt (verbosity 1/2/3 + dry/live) | ✅ PROVEN on box |
| **Single input + preflight** | reads `{header,beats}` wrapper from `parse_script.py --json-full`; halts EARLY if header (channel/title/description/tags) incomplete | ✅ PROVEN |
| **Two reads** | channel resolved BY NAME from header → `<channel>/channel.json` + `<project>/look.json` override; composition scan decides legs | ✅ PROVEN |
| **Audio leg + audio gate** | 2a→2b→whisper→2c→durations.json (+ audio-continuity QC); keep/swap gate (swap = scp human VO + re-whisper); long steps stream + heartbeat | ✅ PROVEN end-to-end on box (Final Hours, Sacred Dawn) |
| **Mode B leg (render)** | renders all Mode B cards via dispatch.py at each component's OWN duration, real durations.json fed | ✅ PROVEN — 21/21 clips render on box |
| **Mode B gate (review)** | autoplay/loop/muted scrollable page; shaped props shown; audio-locked fields read-only; edit payload + one-click Re-render + Flag | ✅ BUILT + tested |
| **Mode A leg + Mode A gate** | stills → stills review gate → Kling animate (`finish --animate-only`) | ✅ PROVEN live (Sacred Dawn, 10–11 June) — was the "next" item at the 6 June snapshot |
| **Convergence** | assemble → music mux → `final_video.mp4` → thumbnail gate → convergence gate → uploader | ⏳ assemble proven (Mode-A path); publish half (thumbnail/schedule/upload) built for some channels, not all |
| **Resume / polish** | `--from <leg>`, verbosity polish, end-run summary | ⏳ `--from` not built (a re-run re-spends every leg) |

## Box environment (DONE — do not re-debug)
Node 20.20.2 (nvm) + Remotion 4.0.472 (linux compositor) + Remotion project IN the repo at `~/Pipeline/remotion/` + `REMOTION_DIR` in bashrc/profile + headless-Chromium system libs installed (libnspr4 et al.). See session notes §3.

## Principles banked while building (now load-bearing)
- **Mode B renders each component at its OWN durationInFrames** (queried from `npx remotion compositions`), never audio-derived frames. The assembler freeze-fills the gap to the measured slot. Render is therefore unbreakable.
- **The orchestrator must not assume the interactive shell's environment.** Subprocesses don't inherit `.bashrc`. Resolve needed things (node bin, REMOTION_DIR) in code or fail loudly. (Hit twice: REMOTION_DIR, node PATH.) *(Same family of bug as the `voice_id` snake_case trap and the cosmetic "Victor" gate label — resolve identity explicitly, fail loudly, never assume.)*
- **Mode B script-craft limit** (in `ante-machinam.md` Part II): cards carry ≤~12-15 words; silent cards no longer exist — a wordless beat halts the build (Constitution §1); more words → it's a Mode A beat. Resilience in pipeline, quality judgment with the writer.
- **A step that can run >~10s must emit liveness** (stream child stdout or heartbeat); silence reads as death.
- **Audio-locked fields are read-only in the Mode B gate** (e.g. QuoteCard.quote = the spoken found_line). Card-vs-audio distinction = load-bearing-script principle made mechanical.

## Build discipline that worked
Leg-by-leg, each rung tested on the box before the next. The verify-before-run rule broke the debugging circle: confirm the code landed AND the query returns real data BEFORE spending a run. The biggest non-code time-sink was box environment setup (Remotion headless) and laptop↔box file-sync.
