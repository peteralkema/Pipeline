# Pipeline Playbook
*The full lifecycle from topic to published video, across all channels.*
*Last updated: 5 June 2026 — added PART 2B (dual-mode architecture, Mode A + Mode B) ahead of the Synthetic launch series. Prior: 30 May 2026, after shipping Six Minutes (Success Coach video 1) and setting up Hindenburg (Final Hours video 4).*

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

*Added 5 June 2026 for the Synthetic Press launch series. Mode A is the existing stills→clips engine (all current Final Hours / Success Coach video). Mode B is Remotion motion-graphics. This part describes how they coexist in one pipeline. Synthetic is the first channel to use both; the architecture is general.*

### The four principles (the whole thing hangs off these)

1. **The sentence decides the mode (upstream).** Every beat is born Mode A or Mode B because the *sentence* decides. A sentence describing a place/person/moment ("Altman sat across from the man who would later try to destroy him") is Mode A — it wants a recreated scene. A sentence asserting a fact/number/quote/structure ("Microsoft put thirteen billion dollars in") is Mode B — it wants the number drawn, the quote sourced, the structure built. You are not annotating a script for the pipeline; you are writing in two registers the pipeline understands. If you can't decide a beat's mode, it's doing two jobs — split it.

2. **Visual exclusivity (the load-bearing rule).** At any instant the screen belongs to *either* a Mode A recreated scene *or* a Mode B graphic — never both. One renderer owns the frame at a time. This is what makes the launch build tractable: exclusivity means the timeline is a pure **sequence** (clips butted end to end), so assemble needs **no compositing**. (Breaking exclusivity — graphics layered *over* live scenes, the "underlay/Vox" look — is Phase 2 and requires a compositing stage. Cutaway-only for launch.) Narration pausing on a Mode B beat is an *editorial* choice for effect, fully decoupled from the visual — the visual is exclusive either way.

3. **The audio is the source of truth (shared spine).** Generate the voiceover first, measure it with Whisper, hang visuals off the measurement — for *both* modes. Same `voiceover.json`, same finish step, same matcher. A beat's measured duration is handed to whichever renderer it routes to: a NumberCounter given 3.1s counts over 3.1s; a recreated shot given 3.1s holds 3.1s. One measurement, two consumers. Mode A and Mode B share one spine.

4. **The tagged script IS the pipeline spec (the seam).** Because a Mode B beat is written in the known component vocabulary, the act of scripting it *is* the design — the tag payload is the render spec. When the script is done, grepping the B tags yields the exact component list the episode needs. The script tells you what to build, instead of you guessing the wiring and writing to fit it.

### The chain, top to bottom

```
Script (tagged beats)
  → storyboard (one row per beat; `mode` column decides row shape)
  → audio spine generated + Whisper-measured (both modes timed off this)
  → DISPATCH on tag:
        [A]            → stills→clips path (Flux → review gate → Kling → clip)
        [B:Component]  → Remotion path (payload→props→remotion render → clip)
  → assemble: clips in beat order on the voiceover spine (sequence, no compositing)
```

One storyboard, one timeline. The two modes are not two pipelines that merge — they are two renderers the storyboard hands work to, beat by beat, both returning ordinary MP4 clips into the same slot order. By assemble time, an A clip and a B clip are both just MP4s of known duration.

### The beat-type notation (the discipline layer)

Every beat opens with a tag. Mode A stays light (the default). Mode B carries the component name + payload, because the payload *is* the render spec.

```
[A] Altman sat across from the man who would one day try to destroy him.

[B:QuoteCard] "I deeply regret my participation."
  — Ilya Sutskever · public statement · Nov 2023
  highlight: "deeply regret"

[B:NumberCounter] from=0 to=13000000000 prefix=$ label="Microsoft's bet"

[B:DocumentReveal] exhibit: 2017 internal email
  show_line: "we don't really intend to honor the nonprofit structure"
  source: trial exhibit, Musk v. OpenAI

[B:ChapterCard] "Part One — The Promise"
```

Rules:
- **Tag chosen as you write the sentence, not after.** Upstream principle made physical.
- **The narration line is the same in both modes; the tag carries what the voice omits.** In a `[B:QuoteCard]` the narration *is* the quote (you say it); the payload carries name/source/date. This is "the spoken line and its receipt" (banked in the series doc, script-craft Principle 8, and the Mode B notes): voice = the words; card = words + attribution; `highlight:` = the swept phrase. **No-karaoke rule:** the card never duplicates the full sentence as text the narrator is also reading verbatim.
- **Only components that exist get tags.** Legal vocabulary is exactly the six built: `HighlightedHeadline`, `LowerThird`, `NumberCounter`, `ChapterCard`, `QuoteCard`, `DocumentReveal`. A beat wanting something outside the six is a *deliberate* decision to build a seventh component, not a thing to write around — the tag vocabulary won't let you invent a renderer.
- **Every B beat is a no-fal, no-stills-gate beat.** So tag-counting a finished script gives the A/B ratio, the fal exposure, and the review-gate load *before* a single render. The script becomes the production estimate. Mode B is cheaper and more deterministic than Mode A (no model call, no review, just props → render).
- **Ratio is read, not enforced, per episode.** Target band 60–70% A / 30–40% B is a smell test against what the story is made of, not a quota. E1 (founding, scene-heavy) runs A-heavy and that's correct; if it comes out 95% A, that's the signal you skipped the charter DocumentReveal, the founding-cast LowerThirds, the "for all of humanity" QuoteCard — Mode B beats the story actually contains.

### Inside the Mode B render step (spec → props → clip)

You are **not** generating new Remotion code per beat. The six components are written once and parameterized. The Mode B renderer is a small translator:
1. Look up the tag's component name in the **registry** (string→component map, already built in the prototype): `"NumberCounter"` → the NumberCounter component.
2. Spread the payload fields as **props**; pass the beat's measured duration as the frame count (duration × 30fps).
3. `remotion render` that one beat to a clip.

So `[B:NumberCounter] from=0 to=13e9 prefix=$` becomes `<NumberCounter from={0} to={13e9} prefix="$" durationInFrames={93} />` → rendered clip. Deterministic, cheap, no review gate.

### The true-up IS the human-voice swap

Because audio is the source of truth, swapping the Inworld scratch narration for Peter's human read is a **true-up, not a re-render**: drop in the human `voiceover`, re-run Whisper → match → assemble, and *every* visual timing re-derives for free — Mode A shot holds *and* Mode B component timings alike. Nothing visual regenerates. This is the same true-up mechanism already banked for Mode A shot durations, now doing double duty as the production model for Synthetic: **script + record scratch (Inworld) → build all visuals against it → swap in the human read → true-up → final.** Build the `finish --voiceover <path>` override so the human read can be supplied at true-up time (this also fixes the old "finish regenerates voiceover" behaviour).

### What to build for the Episode 1 launch (the thin slice)

Build only what E1 demands, proven end to end:
1. **Tag parser** — read `[A]` / `[B:Component]` into storyboard rows of the right shape. Small.
2. **Dispatch branch** — the `if mode=="A" … else …` routing each row to a renderer. Small.
3. **Mode B render step** — payload → props (via the existing registry) → `remotion render` → clip. Medium; the hard part (the components) is done. Start with **two live components**: `QuoteCard` (needed for the cold open's "We have a verdict" receipt) and `NumberCounter` (needed at the first valuation). The other four are then just more registry entries, not new plumbing.
4. **Assemble accepts both clip types** — mostly already true; a clip is a clip by timeline time.

**Do NOT build for launch:** automatic mode *inference* (tagging is by hand — the human decides the mode, correctly); compositing/underlay (Phase 2); batch/parallel rendering (Phase 2); any component beyond the six (and if E1's script demands a seventh, that's a deliberate decision surfaced *by* the script).

The mental model in one line: **the tag is a routing instruction the author writes, the storyboard carries it, the dispatcher obeys it, two renderers feed one timeline, and the measured audio keeps them honest.**

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
