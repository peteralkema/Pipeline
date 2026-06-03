# Pipeline Playbook
*The full lifecycle from topic to published video, across all channels.*
*Last updated: 31 May 2026 — after shipping Pudding Lane (Final Hours video 5) through one clean stills generation pass.*

This is the single source of truth for how to make a video. Read it before starting any new project. Update it when banking new rules from production.

This document is the *operational* layer. Two companion documents:
- `shared/docs/script-craft-principles.md` — what makes a good Final Hours script (read at step 3)
- `shared/docs/production-patterns-that-work.md` — architectural decisions that minimize stills drift (read at step 5)

---

## PART 1 — QUICK REFERENCE CARD

The 12-step lifecycle. Use this as muscle memory once you know the system.

### Step 0 — MANDATORY pre-read (every video, no exceptions)

Before any script writing or storyboard generation begins, Claude must read and apply these documents. Banked from the KLM Tenerife v1 lesson on 2 June 2026 — where the script was written from generic instinct without applying the documented craft principles, resulting in violations of Principles 1, 2, 8 of script-craft (the exact Hindenburg 11% retention failure mode).

For any Final Hours / Synthetic Press / Lazarus Films video, Claude reads:

1. **`shared/docs/script-craft-principles.md`** — the 10+ craft principles + pre-lock audit table. Cold-open structure, trust line, sensation-not-description, clock-anchored dread, named surrounding humans, silent beats, ending on image not explanation, Principle 8 cold-open contract + 2-minute tension renewal, anonymity as craft, seeds-planted-early-harvested-late, pace-aware sensory density.

2. **`shared/docs/production-patterns-that-work.md`** — the 12 production principles. Face-never-resolved as canon strategy, ensemble anonymization via framing, object-substitution for group composition, empty-room shots carry meaning, scene canons over character canons, fire-as-environment never as subject, thumbnail design starts at script lock, architectural period-accuracy, canon block before shots in beats.json, per-location shot cap, voiceover duration audit before finish, angle variation within canon.

3. **`shared/docs/hook-craft-library.md`** — first 60 seconds corpus + 7-question stress-test protocol. Specific anchor, named protagonist, scale numbers, comparative anchoring, catastrophe foreshadow at 40-55s, mid-sentence cliffhanger, present-tense immersion, dramatic irony, contrast structure.

4. **`shared/rulebook.json` and `<channel>/rulebook.json`** — banked production rules (universal + channel-specific). The accumulated moat from prior video failures.

5. **`shared/docs/calibration-reference.md`** — channel positioning and retention benchmarks. Where this channel sits in the competitive landscape and what its retention curve should look like.

**Audit gate before script lock.** After writing the script, fill in the pre-lock audit table from script-craft-principles.md. If any cell reads "weak" or "missing," revise before going to canon or storyboard generation. If any production pattern would be violated by the script's locations or character density, restructure the script before storyboard.

**Audit gate before stills lock.** After storyboard generation, audit it against production-patterns-that-work.md before fal generation. Face-heavy shots, two-character cockpit/office shots, group compositions of 4+, fire-as-subject framings — flag and rewrite before burning fal credits. The audit is cheap; the reshoots are expensive.

This discipline is non-negotiable for every video on every channel. The cost of reading is 5 minutes. The cost of NOT reading is a video that ships with documented retention failure modes.

### Pre-production (research + script)

**Step 1.** Pick a topic. Use NexLev to validate demand. Check that no direct format competitor exists in the lane. Bank the decision in the channel's backlog document with rationale.

**Step 2.** Research the protagonist and historical/situational facts. For Final Hours, use web search for documented sources, family accounts, and contemporary reporting. For Success Coach, use lived experience and published research.

**Step 3.** Decide the title (use the channel's title pattern), the protagonist (one specific human), and apply the craft principles. Reference `shared/docs/script-craft-principles.md` for Final Hours. Run the 10-principle audit table before locking the script.

**Step 4.** Write the script as a markdown document at `<channel>/projects/<project>/script.md`. Include production notes, silent beats, capability stretches. Keep the canonical script here.

**Step 4.5.** Stress-test the first 60 seconds against `shared/docs/hook-craft-library.md`. Run the 7-question gate (Section 4 of that document). If it fails 2+ checks, revise the opening before storyboarding — fixing the hook later means regenerating storyboard, stills, and voiceover.

**Step 5.** Write the canon block as a markdown document at `<channel>/projects/<project>/canon.md` if the video has named recurring characters or named locations. Reference `shared/docs/production-patterns-that-work.md` for canon strategy — prefer scene canons over character canons, apply face-never-resolved for anonymous protagonists, anonymize ensemble via framing not canon.

### Production (stills generation)

**Step 6.** Extract pure narration from script.md, save as `<channel>/projects/<project>/<project>_script.txt` (no production notes, just prose).

**Step 7.** Generate the initial storyboard from the narration. From the channel root:

```
python ../shared/recreation_pipeline.py stills --script projects/<project>/<project>_script.txt --project projects/<project> --storyboard-only
```

This calls Claude to slice the narration into ~one shot per 9 words. Saves `storyboard.json` inside the project folder. Costs cents in Claude API. **Important: use `--storyboard-only` to avoid kicking off Flux image generation against canon-unaware prompts.**

**Note on `--project` argument.** Use `projects/<name>` (e.g. `projects/pudding_lane`), not just `<name>`. Using the bare name creates stray folders at the channel root.

**Step 8.** If the video has canon, convert `storyboard.json` to a canon-aware beats file. Insert `{character}` and `{location}` tokens into image_prompts where appropriate. Save as `<channel>/beat-scripts/<project>_beats.json` with the format `{"canon": {...}, "beats": [...]}` — see step 8 details below.

**Step 9.** Generate the stills. From the channel root:

```
python ../shared/recreation_pipeline.py stills --beats beat-scripts/<project>_beats.json --project projects/<project>
```

This runs Flux against each shot's prompt. Costs $25-30 in fal credits typically. Takes 30-60 minutes. Outputs to `<project>/stills/shot_NNN.png`.

**Step 10.** Review every still. For drifted shots:

```
python ../shared/recreation_pipeline.py restill --project projects/<project> --shot N
```

If the same shot fails 3 times with 3 different failure modes, duplicate an adjacent acceptable shot rather than continuing to roll dice. Bank any new rules in the rulebook.

### Animation, audio, assembly

**Step 11.** Run finish to animate stills, generate voiceover, assemble video. From the channel root:

```
caffeinate -d -i python ../shared/recreation_pipeline.py finish --project projects/<project> --no-music 2>&1 | tee <project>_finish.log
```

Wait — verify `channel.json` voice_id matches the channel identity first. About 30-60 minutes of compute. Outputs `<project>/final_video.mp4`.

**Note on silent terminal.** Finish render can go silent for 30-60 seconds at a time between clips printing. Check `<project>/clips/` folder count to verify progress. Silent terminal does NOT mean stalled.

### Publication

**Step 12.** Thumbnail design starts at script lock-in (step 3 / 4), not at this step. Generate via Clickly in parallel with stills generation (during step 9). By the time finish completes (step 11), thumbnail should be ready. Then upload:

```
python upload.py --project projects/<project>
```

Upload defaults to PRIVATE. Open YouTube Studio, review auto-generated metadata, replace title with your locked version, verify thumbnail loaded, schedule for the target window (typically Sunday/Monday evening US time for cold-start channels). Add the pinned comment after publication.

---

## PART 2 — FULL PLAYBOOK

The detailed walkthrough. Read this on first-time setup, when something breaks, or when launching a new channel.

### Architecture overview

The Pipeline directory at `/03. Pipeline/` contains everything. Key structural rules:

- The `.env` file lives at the Pipeline root, *not* in each channel folder
- Channels symlink `.env` into themselves: `ln -s ../.env .env`
- Channels symlink shared utilities they import: `ln -s ../shared/srt_generator.py srt_generator.py`
- The `recreation_pipeline.py` lives in `shared/` and is invoked with relative path from channel roots: `../shared/recreation_pipeline.py`
- Most pipeline commands must be run from the *channel root* (final-hours/ or success-coach/), not from inside the project folder. The pipeline uses CWD to resolve project paths.
- Final-hours uses `projects/<name>/` subdirectory; success-coach uses `<name>/` directly. Inconsistency banked for cleanup.

### Channel setup (one-time per new channel)

When launching a new channel for the first time:

**1. Create the channel folder structure:**

```
mkdir -p channel-3/{beat-scripts,projects,docs,assets}
cd channel-3
touch channel.json rulebook.json
```

**2. Configure channel.json:**

The minimum channel.json has:
- `name` — channel display name
- `voice_id` — TTS voice (Reed for Success Coach, Victor for Final Hours)
- `style_suffix` — appended to every Flux prompt (e.g. "photoreal cinematic")
- `base_canon` — optional channel-level canon entries inherited by all projects

**3. Symlink shared utilities:**

```
ln -s ../.env .env
ln -s ../shared/srt_generator.py srt_generator.py
```

**4. Set up OAuth for this channel's YouTube account:**

The OAuth client (`client_secret.json`) can be reused across channels. But each channel needs its own `token.json` because each channel's YouTube uploads happen under a different Google account.

Copy the OAuth scripts and client from a working channel:

```
cp ../final-hours/auth.py .
cp ../final-hours/upload.py .
cp ../final-hours/client_secret.json .
```

Then **add the new channel's Google account as a test user** in Google Cloud Console:
- Go to `console.cloud.google.com`
- Open the project (e.g. `youtube-upload-test-497220`)
- Navigate to Google Auth Platform → Audience
- Add the channel's Google account email under "Test users"

Make sure your default browser is signed in to the new channel's Google account, then run:

```
python auth.py
```

A browser opens. Pick the right Google account, grant the YouTube upload permissions, the script saves `token.json` to the channel folder.

**5. Verify the API key loads:**

```
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Key loaded:', bool(os.getenv('ANTHROPIC_API_KEY')))"
```

Should print `Key loaded: True`. If False, check the symlink to `../.env` exists.

### Project setup (per video)

**1. Create the project folder under the channel:**

```
mkdir -p projects/<project_name>/stills
```

**2. Decide the canon strategy upfront.**

Reference `shared/docs/production-patterns-that-work.md` before writing canon. The key questions:
- Is the protagonist's identity historically documented? If no, apply face-never-resolved (Principle 1) and the canon needs only one anonymized character entry.
- Are there 3-5 recurring named characters? Multi-character canons cost real production time and have historically caused drift. Consider anonymizing supporting cast via framing rather than canon (Principle 2).
- Are there group composition shots in the script? Plan object-substitution at canon time (Principle 3).
- How many distinct scene locations? Scene canons are reliable; build one per location (Principle 5).

Two types of projects:

- **Atmospheric / ensemble** (early Final Hours videos like Pompeii, Anne Boleyn): no recurring named characters. Skip canon entirely. Run stills with `--script` (auto-slicing).
- **Named-character or anonymized-protagonist recurring** (Hartley, Six Minutes, Hindenburg, Pudding Lane): recurring people or recurring scenes that must look consistent across many shots. Build a canon block. Run stills with `--beats` (pre-written canon-aware).

If you're not sure, build the canon. The cost of a canon block is one hour of writing; the cost of no canon when you needed one is hundreds of failed stills.

**3. Write script.md and canon.md in the project folder.**

**4. Extract pure narration to `<project>_script.txt`** — strip production notes, visual cues, silent-beat markers, beat headers. Just prose narration.

### Storyboard generation (step 7)

Two paths depending on canon strategy:

**Path A — no canon (atmospheric/ensemble video):**

```
python ../shared/recreation_pipeline.py stills --script projects/<project>/<project>_script.txt --project projects/<project>
```

Generates the storyboard AND immediately generates all stills. ~$25-30 in fal credits, 30-60 minutes.

**Path B — canon-aware:**

Run in two phases. First, generate the storyboard only:

```
python ../shared/recreation_pipeline.py stills --script projects/<project>/<project>_script.txt --project projects/<project> --storyboard-only
```

Saves `storyboard.json`, costs cents in Claude API, no Flux generation.

### Step 7 troubleshooting — streaming patch

If the storyboard generation fails with a JSON parse error or unterminated string, the issue is `max_tokens` truncation. Claude's response exceeded the limit before completing the JSON array.

Bumping max_tokens above ~16000 triggers a different failure: the Anthropic SDK refuses non-streaming requests that might take longer than 10 minutes. The error is `ValueError: Streaming is required for operations that may take longer than 10 minutes`.

The proper fix is to use streaming mode in `build_storyboard`. The function in `shared/recreation_pipeline.py` around line 470 should use `messages.stream()` with the `text_stream` iterator, not `messages.create()`:

```
raw_parts = []
with claude().messages.stream(
    model=CLAUDE_MODEL,
    max_tokens=32000,
    messages=[{"role": "user", "content": prompt}],
) as stream:
    for text in stream.text_stream:
        raw_parts.append(text)
raw = "".join(raw_parts).strip()
```

This is the permanent fix. The patch was applied 31 May 2026 during Pudding Lane production. If you see a regression to non-streaming code, the streaming patch was reverted and needs to go back in.

### Storyboard editing principles (step 8)

When converting auto-generated `storyboard.json` to canon-aware `beats.json`:

**The schema conversion is non-obvious.**

The auto-generated `storyboard.json` is a flat list:
```
[{"narration": "...", "image_prompt": "...", "motion_prompt": "...", "index": 1}, ...]
```

The canon-aware `beats.json` must be a dict with `canon` and `beats` keys:
```
{
  "canon": {
    "token_name": "Full descriptor...",
    ...
  },
  "beats": [
    {"narration": "...", "image_prompt": "Inside {bakehouse}...", ...},
    ...
  ]
}
```

**The key is `beats`, not `shots`.** The pipeline error message on schema mismatch is unhelpful. If you see "Unrecognised beats format... Expected either a list of beats, or a dict with 'beats' (and optional 'canon') keys", rename the top-level `shots` key to `beats`:

```
python3 -c "
import json
path = 'beat-scripts/<project>_beats.json'
with open(path) as f: data = json.load(f)
if 'shots' in data: data['beats'] = data.pop('shots')
with open(path, 'w') as f: json.dump(data, f, indent=2)
print('Renamed shots -> beats')
"
```

**Canon insertion rules.**

Canon tokens go in image_prompts only, not motion_prompts (motion describes the camera/scene, not the subject).

Restate wardrobe in the prompt body when it matters, even when using canon. Flux honours wardrobe from canon inconsistently.

For face-never-resolved protagonists (Pudding Lane pattern), specify the framing rule in EVERY shot that includes the character: "photographed from behind", "in silhouette against firelight", "face in deep shadow, never resolved". Do not trust the canon block alone to enforce this.

For anonymized ensemble (Pudding Lane's Farriner, Hanna, Dagger), specify the framing rule in the image_prompt without a canon token. "Photographed from behind so only the back of his head and the curve of his shoulder are visible. Face never visible."

For group composition shots in the auto-generated storyboard, rewrite as object-substitution before generating stills. A "family of displaced Londoners" shot becomes an abandoned spinning wheel, torn shawl, broken bowl, child's leather shoe in the ash. See production-patterns-that-work.md Principle 3.

Restate the era anchor in every image_prompt. Each prompt should end with the period descriptor (e.g. "1666 photoreal cinematic" or "1937 photoreal cinematic").

Watch for expression defaults. Flux's default for any character is a slight smile. Restate the canon expression baseline per-prompt for emotional moments.

Watch for architectural period drift. Old St Paul's medieval cathedral is NOT the modern Wren dome. Always include the explicit "NOT the modern X" guard in any shot that references a famous landmark.

**Estimate the reshoot budget realistically:**

- Atmospheric/ensemble (Pompeii-style): 5-10% reshoot rate
- Anonymized-protagonist (Pudding Lane-style with face-never-resolved): 5-10% reshoot rate
- Single-named-character: 15-25% reshoot rate
- Multi-named-character ensemble: 30-50% reshoot rate
- Total: budget 105-150 generations to get 90-100 usable stills, depending on canon complexity

### Stills review (step 10)

Open `<project>/stills/` and look at every shot in order. Things to check:

- **Canon drift**: does the character look like themselves shot-to-shot? (For anonymized protagonists: does the framing rule hold? Face never visible?)
- **Wardrobe drift**: does clothing match canon and stay consistent?
- **Expression**: composed when it should be composed, anguished when it should be anguished
- **Era authenticity**: no modern objects, no modern hairstyles, no modern photography aesthetic
- **Architectural period accuracy**: medieval cathedrals not Wren domes, gas lamps not electric bulbs
- **Group composition**: faces visible only when intended; soft-focus or back-of-camera for crowd scenes; object-substitution where you planned it

For drifted shots, use restill:

```
python ../shared/recreation_pipeline.py restill --project projects/<project> --shot N
```

If the same shot fails 3 times with 3 different failure modes, duplicate an adjacent acceptable shot:

```
cp <project>/stills/shot_038.png <project>/stills/shot_037.png
```

Banked rule: don't continue rolling dice past three attempts.

**The artistic-license fallback.** When restill cycles produce different forms of drift each time without converging, accept what you have. Final Hours is recreation, not facsimile. Period authenticity comes from costume, light, behaviour, atmosphere — not 1:1 architectural fidelity. This was the resolution for Hindenburg's dining-room canon drift (13 shots that drifted differently across attempts).

### Finish (step 11)

When all stills are accepted, run finish:

```
caffeinate -d -i python ../shared/recreation_pipeline.py finish --project projects/<project> --no-music 2>&1 | tee <project>_finish.log
```

**Pre-finish checklist:**
- Verify `channel.json` voice_id is correct (Reed for Success Coach, Victor for Final Hours)
- Verify all stills exist: `ls projects/<project>/stills/ | wc -l`
- Check fal credit balance — finish typically costs $25-30, sometimes more
- Have laptop plugged in if running locally
- Use `caffeinate -d -i` to keep the laptop awake without sleeping
- Pipe through `tee` to capture a log file

The `--no-music` flag ships clean and you add music in post-edit. Use `--music <path>` if you have a chosen track.

**Step 11 troubleshooting — silent clip generation.**

Finish render can go silent for 30-60 seconds at a time between clips printing. This is normal — moviepy and fal's async clients don't always print to terminal in real-time. To verify progress without interrupting the run, open a second terminal:

```
ls projects/<project>/clips/ | wc -l
```

If the count is climbing every few minutes, the pipeline is healthy. If the count has not changed in 5+ minutes AND the main terminal is silent, the run may have stalled.

### Thumbnail generation (parallel with stills)

Thumbnail design should start at script lock-in (step 3 / 4), not at the end of production.

```
python ../shared/make_thumbnail.py --project projects/<project>
```

The make_thumbnail.py output is a starting point only. The current state of the script produces MrBeast-school clickbait by default (shocked face, bright text). For Final Hours specifically, this is off-brand. The right move is to generate the thumbnail in Clickly with a brand-specific prompt:

```
A young woman in her late teens dressed as a [period] servant — [specific clothing details from canon] — standing at [story-specific location] photographed from outside the building looking in. She is silhouetted against the orange firelight inside the room behind her. Her face is in deep shadow, not clearly visible. Photoreal cinematic, [period], dignified period drama register, no modern elements.
```

Expect two Clickly iterations before the thumbnail lands. First attempt usually has period-accuracy drift (modern St Paul's dome instead of medieval cathedral, grinning protagonist instead of dignified). Plan for v1 + v2.

For the text overlay, the working architecture is:
- Left third: bold yellow text on dark background, two-line stack ("GREAT FIRE OF LONDON" + "SHE WOULDN'T JUMP")
- Right two-thirds: the protagonist + period setting + atmospheric fire/light

Drop exclamation points from titles. Final Hours register is quiet declarative ("She Wouldn't Jump.") not clickbait emphatic ("SHE WOULDN'T JUMP!"). Pompeii's "They Waited" is the template.

### Upload (step 12)

```
python upload.py --project projects/<project>
```

What happens:
1. Reads script, storyboard, final_video.mp4
2. Calls Claude API to generate title/description/tags from the script content
3. Generates SRT subtitles from storyboard timing
4. Uploads video as PRIVATE
5. Uploads SRT as caption track
6. Uploads thumbnail.png
7. Prints YouTube Studio URL

**Known limitation: Claude-generated title may not match your locked title.** Open YouTube Studio after upload, navigate to the video, replace the title with your locked version before publishing.

### Publication (in YouTube Studio)

1. **Title** — replace auto-generated with your locked version
2. **Description** — review and edit. Keep the hook in the first 2 lines.
3. **Thumbnail** — verify it loaded; manually upload if not
4. **Tags** — add 5-10 relevant tags
5. **Audience** — Made for Kids: No
6. **Language** — English
7. **Category** — Education or appropriate
8. **Visibility** — Schedule for target window (typically Sunday/Monday evening US Eastern)
9. **Save**

After publication, return to the video and **add the pinned comment**. Pinned comments generate the early engagement signal the algorithm watches.

### A/B thumbnail testing

When in doubt about thumbnail register (brand-faithful vs clickbait-aggressive), use YouTube's built-in A/B test:
- Studio → Content → select the video → Edit thumbnail → "Test thumbnail"
- Pick two thumbnails representing different strategic approaches
- 13-day test duration, watch-time share is the metric (not just CTR)

The result, whichever way it lands, should be weighed against brand-consistency: stick with the on-brand option even if MrBeast-style wins by 5-10% on raw CTR. The brand is the moat that compounds across all future videos.

---

## PART 3 — TROUBLESHOOTING

**"No module named 'srt_generator'"** when running upload.py
→ Missing symlink. Run `ln -s ../shared/srt_generator.py srt_generator.py` from the channel root.

**"ANTHROPIC_API_KEY not set"**
→ Missing or broken .env symlink. Run `ln -s ../.env .env` from the channel root.

**"FileNotFoundError: 'six_minutes/clips'"** during finish
→ CWD wrong. Pipeline expects channel root, not inside project folder. `cd ..` and re-run.

**"Missing client_secret.json"** when running auth.py
→ Auth.py has a known variable-swap bug. Lines 34-35 should be `CLIENT_SECRET = "client_secret.json"` and `TOKEN_FILE = "token.json"` — these are sometimes inverted. Check and fix if needed.

**Upload errors with permission denied or no channel found**
→ Wrong Google account active in browser when auth.py was run. Delete `token.json`, switch browser, re-run `python auth.py`.

**Stills look drifted from canon despite canon being defined**
→ Canon resolution works but wardrobe and expression are notoriously unstable. Restate explicitly in the prompt body. For face-never-resolved protagonists, restate the framing rule per-shot too.

**Pipeline tries to generate stills against a canon-unaware storyboard**
→ Use `--storyboard-only` flag with `--script` mode to stop after storyboard generation.

**"Unrecognised beats format in beat-scripts/<project>_beats.json"**
→ Schema mismatch. The file's top-level key is probably `shots` (from auto-storyboard format). Rename to `beats`. See Step 8 conversion script above.

**JSON parse error / unterminated string in build_storyboard**
→ `max_tokens` truncation. Bump to 32000. Will then hit streaming requirement.

**"ValueError: Streaming is required for operations that may take longer than 10 minutes"**
→ The Anthropic SDK requires `messages.stream()` for max_tokens >= ~16000. Apply the streaming patch to `build_storyboard` (see Step 7 troubleshooting above).

**Finish render goes silent for minutes at a time**
→ Normal. Check `<project>/clips/` folder count. Silent does NOT mean stalled.

**fal credits run out mid-render**
→ Auto-top-up should handle this if enabled. Re-running finish resumes from where it left off.

**Voice sounds wrong**
→ Check channel.json voice_id. Reed for Success Coach, Victor for Final Hours.

**Thumbnail looks like generic AI clickbait**
→ make_thumbnail.py output is a starting point, not the final thumbnail. Move to Clickly with a brand-specific prompt. Expect 2 Clickly iterations.

---

## PART 4 — KNOWN DEFERRED IMPROVEMENTS

**Upload script reads metadata.json from project folder before falling back to Claude generation.** Eliminates the manual title-fix step in YouTube Studio. ~30 minutes to build.

**Fix the variable-swap bug in auth.py canonically in shared/, not channel copies.** Move auth.py and upload.py to `shared/`, make them channel-aware via CWD detection of channel.json. ~60 minutes.

**Whisper-based SRT instead of even-spacing.** Current captions drift against spoken words. Worth building when captioned-watching audience becomes meaningful.

**Pre-render cost estimate.** Print expected fal spend before finish runs, based on shot count. ~30 lines of code.

**Beat-multiples for rhythmic variation.** Allow individual beats to be integer multiples of base unit (peak beats 2×) for rhythmic variation. 50-100 lines of changes. Not urgent.

**Normalise channel project structure.** Final-hours uses `projects/<name>/`, success-coach uses `<name>/` directly. Standardise on `projects/<name>/` across channels. ~30 minutes.

**Cloud migration to Hetzner.** See Part 6 below. Planned for week of 7 June 2026.

**HTTP-invokable pipeline operations.** Currently CLI-only. Building Hetzner with future web UI in mind means pipeline operations should be invokable via HTTP requests for eventual phone-based execution. Bank as Hetzner architecture principle.

---

## PART 5 — OPERATING REMINDERS

### Banked principles (hard-won from real production failures)

**Flux-pro silent safety-rejection mode.** `fal-ai/flux-pro/v1.1` at default safety_tolerance (~2) silently returns black ~7KB PNGs when its safety filter triggers. No exception, no warning, no log. About 50% of typical Final Hours generations fail this way on the original pass. **Always pass `"safety_tolerance": "5"` in fal args.** This is the single most important fal hygiene fix. The `restill_from_feedback.py` already does this; verify your `recreation_pipeline.py` does too.

**Mandatory silent-rejection audit after every stills generation.** Run `find projects/<name>/stills -maxdepth 1 -name "shot_*.png" -size -200k` immediately after the stills pass completes. Any results are silent rejects. Either restill them via `restill_from_feedback.py` or accept them as held-still fallbacks during finish.

**Flux trigger-word vocabulary that fails even at safety_tolerance 5.** Word combinations matter more than individual words. Confirmed trigger stacks: `fire + survivor + wreckage` (crash sequences), `hand + finger + dial` (body-parts-near-objects — Flux's people filter), `emergency + vehicles + disaster` (aftermath aerials), `eyes + close up + person` (face-too-close). Neutralize with: `warm light` instead of fire, `lone figure` instead of survivor, `industrial cylindrical metal` instead of aircraft engine, `product photograph` instead of office scene.

**Mac Python 3.12 SSL fix for fal_client.** fal_client uses httpx internally; httpx ignores `SSL_CERT_FILE` env var and `ssl._create_default_https_context` — it uses its own SSL context. Standard CA bundle fixes don't work. The proven pattern is to monkey-patch `httpx.Client.__init__` to default `verify=False` BEFORE fal_client imports it:

```python
import httpx as _httpx
_orig = _httpx.Client.__init__
def _patched(self, *a, **kw):
    kw["verify"] = False
    _orig(self, *a, **kw)
_httpx.Client.__init__ = _patched
```

Must be at the TOP of the file (line 1), before any other imports. httpx caches its SSL context at import time, so patching after fal_client imports doesn't work. This pattern is already in `restill_from_feedback.py` and `serve_review.py`.

**Override mode > Notes mode for hard corrections.** When Notes mode (REGENERATION FEEDBACK: ... appended) keeps producing the same wrong result, Flux is weighting the early canon and original-prompt tokens too heavily. Switch to Override mode — provide ONLY the new prompt, no canon, no original. Lands in 1-2 retries instead of 4-6. Cost: you lose canon consistency for that shot. Trade is worth it for stubborn problem shots.

**Flux text-rendering limits.** Flux can render SHORT all-caps text (3-5 words max per block) reasonably well. Anything longer mangles. For thumbnails on Clickly: use short hook phrases like "8 SECONDS" + "583 DEAD" rather than full titles. The full video title goes in YouTube's title field (which is what viewers READ next to the thumbnail anyway). The thumbnail just needs to hook the click.

**Step 0 mandatory pre-read discipline.** For any Final Hours / Synthetic Press / Lazarus Films video, Claude must read these documents BEFORE script writing or storyboard generation begins: `script-craft-principles.md`, `production-patterns-that-work.md`, `hook-craft-library.md`, `rulebook.json` (channel + shared), `calibration-reference.md`. Banked from the KLM Tenerife v1 lesson on 2 June 2026 where writing from generic instinct without applying the documented principles produced a script with 3-4 principle violations (Hindenburg 11% retention failure mode).



- **The venv name is `pipeline`** at `~/venvs/pipeline`. Renamed from `success-coach` on 2 June 2026. Activate with `source ~/venvs/pipeline/bin/activate`.
- **Channel detection is by `channel.json` marker**, found by walking up from CWD. `cd final-hours/` or `cd success-coach/` before running pipeline commands.
- **Most commands run from the channel root**, not the project folder. The `--project <path>` argument is resolved against CWD. Use `projects/<name>` not bare `<name>`.
- **First run of `make_thumbnail.py` after environment reset downloads rembg U2Net model** (~170MB) into `~/.u2net/`.
- **`grep -c '_expand_canon\|_load_beats_with_canon'` on the pipeline** is a sanity check that the canon mechanism is in place; should return ~6 matches.
- **`shared/rulebook.json.pre_migration_backup`** exists from the 30 May rulebook split — pre-multi-channel snapshot, available if needed.
- **OAuth client `youtube-upload-test-497220` is owned by peteralkema2@gmail.com** but supports test users from other accounts (including peteralkema6 for Success Coach). Add new accounts as test users before running auth flow.
- **Thumbnail design starts at script lock**, not after stills. Parallel work compresses time-to-ship by 30-60 minutes per video.
- **Pre-lock script audit table.** Fill in the 10-principle table from `shared/docs/script-craft-principles.md` before going to canon.

---

## PART 6 — HETZNER MIGRATION (placeholder)

Migration to Hetzner VPS planned for week of 7 June 2026. Details in `shared/docs/hetzner-pre-read.md`.

Sections to add to this playbook after migration:

- Git-based code deployment (Pipeline directory becomes a private GitHub repo)
- SSH access patterns from laptop and from phone
- Credential migration discipline (.env, OAuth tokens, fal keys)
- Long-running render patterns (tmux, systemd services, log file conventions)
- Cost monitoring (Hetzner billing, fal credit alerts)
- Backup strategy (Hetzner snapshots, encrypted .env in 1Password)
- File transfer patterns (scp, rsync, eventually web UI uploads)

Specific operational changes expected:

- Pipeline commands invoked via SSH rather than local terminal
- Scripts running in tmux/screen for unattended overnight rendering
- Phone can initiate runs via SSH but writing scripts stays on laptop
- Eventually: web UI for phone-friendly execution (Phase 2, not at migration time)

To be filled in after the migration weekend with actual operational lessons.

---

## PART 7 — EVOLUTION

This document is a living artefact. Update it when:

- A new failure mode is encountered and resolved
- A new step is added to the workflow
- A pipeline command's interface changes
- A new channel is launched (capture any channel-specific quirks)
- A deferred improvement gets built and changes the workflow
- A new production principle is banked from script-craft-principles.md or production-patterns-that-work.md

Date the changes at the top of the document. Bank rules in the rulebook for things that affect prompts; bank workflow lessons here.

The goal of this document is that future-Peter (or a future hire) could pick up the system without re-deriving it from chat threads.

---

## PATCH NOTE — 31 May 2026

Fixed `proj_paths()` in `recreation_pipeline.py` to auto-prepend `projects/` when given a bare project name and `projects/` directory exists. Before this fix, `--project mary_celeste` would write outputs to `<channel>/mary_celeste/` instead of `<channel>/projects/mary_celeste/`. The architecture in PART 2 was correct; the pipeline was lying about it.

Backward compatible — absolute paths and already-prefixed paths are unchanged.


---

## Known issue — discipline audit needed (banked 31 May 2026)

Step 7 (storyboard generation) produces prompts that violate brand discipline when the script names humans. The slicer responds to script content with descriptive prompts ("a bearded man", "her serious eyes") that conflict with face-never-resolved canon.

Mary Celeste storyboard generation showed 70/168 shots (42%) with face/expression/eyes descriptors needing rewrite.

**Phase 2 backlog: build `shared/audit_storyboard_discipline.py`** — runs between Step 7 and Step 8, rewrites face-resolved prompts to preserve framing/object/location detail while stripping face/expression/eye descriptors. Costs ~$0.30 per video in Claude API. Outputs auditied_storyboard.json that Step 8 then consumes.

For Mary Celeste tonight: detected the issue, banked the fix, generation deferred until script exists.


---

## Auto-Whisper alignment — banked 01 June 2026

The `assemble()` step now auto-runs Whisper + alignment whenever a project's storyboard.json doesn't already have audio_duration on every shot. Adds 3-5 min to the first render of any video, then cached forever. Idempotent on subsequent runs.

Architectural shift: **measurement over prediction.** Word-count proxy was a prediction of per-shot duration. Whisper measures the actual rendered audio. Prediction drifts; measurement doesn't.

Same capability serves Lazarus Films multi-genre dialogue: Whisper can identify when each speaker's line starts and ends, which is the data the multi-genre architecture needs to cut between speakers. This was always going to be required for Maltese Falcon. Building it now for Mary Celeste banks it for Lazarus.

Manual debugging path remains available: `python ../shared/align_with_whisper.py --project NAME --verbose`. Useful after editing the storyboard or for spot-checking specific shot timings.


---

## True-up step — baked-in principle (01 June 2026)

Every video render ends with a Whisper true-up before publish. Not optional, not debug-only — standard.

Why: voiceover.mp3 can regenerate at any finish run, animation can regenerate clips, prompts can change between rounds. Any of these can stale-out the existing Whisper alignment. Cheap to refresh, expensive to ship drifted.

The true-up sequence (3 commands, ~5 minutes, $0):

1. whisper projects/NAME/voiceover.mp3 --model small --output_format json --output_dir projects/NAME/ --word_timestamps True
2. python ../shared/align_with_whisper.py --project NAME --verbose
3. python -u ../shared/recreation_pipeline.py finish --project NAME --no-music --assemble-only

When to run it:
- After every finish that regenerated voiceover.mp3
- After any correction round that touched clips or stills
- As a final QA step before publishing — even if nothing seems wrong
- ALWAYS for Lazarus dramatic content (dialogue scenes require frame-accurate sync)
- Optionally for Final Hours documentary content (0.5s drift tolerable but not preferred)

What's normal: the assembler trades small per-shot pacing for zero global drift. Narration micro-stretches or micro-compresses within individual shots. This is the system absorbing slack at the shot level instead of accumulating drift across the whole video. Correct behavior — do not "fix" it.

Spell-breaker register principle: documentary tolerates near-accurate sync because viewers attribute small gaps to documentary pacing. Drama collapses on any sync gap because audiences decode emotion from voice+visual simultaneously. Lazarus protocol = full true-up + end-to-end script-in-hand listen + zero drift accepted.


---

## SRT generator uses old timing — banked 01 June 2026

upload.py generates subtitles.srt from storyboard's even-spacing timing, not the Whisper-measured audio_duration. Result: SRT timestamps are wrong even when the assembled video is sync-correct.

Fix: rewrite the SRT generator to use Whisper word-level timestamps from voiceover.json directly. Each storyboard shot's narration text maps to a span of Whisper words; SRT cue start/end times come from the first and last word's timestamps. Frame-accurate captions for free.

Workaround until fixed: skip SRT upload (YouTube auto-captions are acceptable for documentary register).


---

## PART 7 — UPDATES (1 June 2026)

Operational lessons banked after shipping Mary Celeste (Final Hours video 6, 15:54 runtime, 168 shots).

### Whisper-based frame-accurate sync — built and baked in

Built `shared/align_with_whisper.py` to measure per-shot audio duration from Whisper word-level timestamps. Patched `assemble()` in `shared/recreation_pipeline.py` to read `audio_duration` per-shot from storyboard.json when present, with three-tier priority: Whisper-measured → word-count proxy → uniform fallback.

Auto-Whisper hook injected into `assemble()` — runs Whisper + alignment automatically when storyboard lacks `audio_duration` on every shot. Idempotent. Graceful fallback if whisper not installed. Adds 3-5 min to first render, then cached.

**True-up principle — every render ends with Whisper true-up before publish.** Not optional, not debug-only — standard. The three commands:

```
whisper projects/NAME/voiceover.mp3 --model small --output_format json --output_dir projects/NAME/ --word_timestamps True
python ../shared/align_with_whisper.py --project NAME --verbose
python -u ../shared/recreation_pipeline.py finish --project NAME --no-music --assemble-only
```

When to run:
- After every finish that regenerated voiceover.mp3
- After any correction round that touched clips or stills
- As final QA before publishing — even if nothing seems wrong
- ALWAYS for Lazarus dramatic content (dialogue scenes require frame-accurate sync)
- Optionally for Final Hours documentary content (0.5s drift tolerable but not preferred)

What's normal: the assembler trades small per-shot pacing for zero global drift. Narration micro-stretches or micro-compresses within individual shots. Correct behaviour — do not "fix" it.

**Spell-breaker register principle.** Documentary tolerates near-accurate sync because viewers attribute small gaps to documentary pacing. Drama collapses on any sync gap because audiences decode emotion from voice+visual simultaneously. Lazarus protocol: full true-up + end-to-end script-in-hand listen + zero drift accepted.

### Storyboard discipline auditor — built

Built `shared/audit_storyboard_discipline.py` as Step 7.5 in the pipeline. Detects face-resolution violations via keyword+regex (face/faces/expression keywords/eyes), uses Claude Sonnet 4.6 to rewrite while preserving framing/location/period/atmosphere. Outputs `storyboard_audited.json`. Supports `--dry-run`, `--verbose`. Costs ~$0.39 per video. Mary Celeste audit: 77/168 shots rewritten. False positives occur on "stern" of ship, body posture "lean", "face turned away" — needs cleanup pass.

### proj_paths convention — patched

`recreation_pipeline.py` (line 765) and `upload.py` (line 323) both now auto-prepend `projects/` when given a bare project name. Backward compatible. Future pipeline scripts must inherit the same convention.

### Clip filename convention — `shot_NNN.mp4` not `clip_NNN.mp4`

Animation outputs land as `shot_NNN.mp4`. Corrections scripts must reference this filename pattern. Was the source of Mary Celeste round-3/4/5 corrections silently deleting nothing because they referenced `clip_NNN.mp4` which never existed.

### Voiceover regeneration discovery

The `finish` step regenerates voiceover.mp3 every run unless explicitly told not to. This stales any prior Whisper alignment. Phase 2 fix: detect existing voiceover.mp3 and skip Inworld call (saves cost AND preserves alignment). Until then, always re-run Whisper true-up after any finish.

### SRT generator timing

upload.py generates subtitles.srt from storyboard's even-spacing timing, not the Whisper-measured audio_duration. SRT timestamps are wrong even when video sync is correct. Workaround until Phase 2 fix: skip SRT upload, let YouTube auto-caption.

### Animation step skip-existing bug

`cmd_finish` reports "[NNN/168] already done, skipping" even when the clip file doesn't exist. Source of wasted Mary Celeste round-4 finish run. Phase 2 fix: verify file actually exists on disk before skipping.

### Foreign-language pronunciation hints

Inworld respects phonetic spellings in brackets. For Latin, French, Cornish place names, or any foreign proper noun, write `"Dei Gratia [DAY-ee GRAH-tsee-ah]"` to lock pronunciation deterministically. Avoids TTS lottery on terms that signal dignified-documentary register correctness.

### Named-narrator companion register

Five registers now distinguished in the AI-recreation lane:
1. Third-person reverent, no host (Final Hours current state)
2. Second-person coaching, you ARE the host (Success Coach)
3. Second-person documentary, "you are there" (History Vault Retold)
4. First-person on-camera protagonist (Chloe, Emma, Mira)
5. Named-narrator companion, voice IS the host (Arthur Revives the Past — 48.8K subs, 4.36M views in 4 months)

For Final Hours: name the narrator. Open every video around 0:15-0:20 (AFTER the cold open, never before) with: "I'm [name]. This is Final Hours. Walk with me through what happened next." Preserves the spell-breaker discipline. Adds the parasocial warmth layer the current third-person-reverent register lacks.

Name shortlist: Edmund or Walter (period-British scholarly), Daniel or James (period-neutral dignified). Final selection deferred until first script using the pattern (likely Eyam — see channel-4-hypothesis.md and arthur-revives-script-craft-analysis.md for context).

### Phase 2 pipeline backlog (additions from today)

- Skip-existing logic in stills command (3 lines, line ~926 in recreation_pipeline.py)
- fal retry-on-error with exponential backoff (line ~409)
- `--start-shot N` argument for stills command
- Centralise Claude model IDs in shared/models.json
- Inworld speed parameter for Attenborough-pace pivot (currently 155 wpm vs 120-130 wpm target)
- Discipline auditor false-positive cleanup (stern of ship, body posture lean, face-turned-away)
- Pipeline writes log file by default
- SRT generator rewrite using Whisper word-level timestamps
- Pipeline files reorganisation: move auth.py + upload.py to `shared/`
- Voiceover regeneration skip-existing logic in finish step
- Animation step skip-existing bug: verify file exists on disk before skipping

---

## PART 7 — STILLS REVIEW SYSTEM (added 3 June 2026)

After stills generation completes, run the browser-based review workflow before finish.

### Step 9.5 — Audit for silent safety rejections

Flux-pro at default `safety_tolerance` silently returns black ~7KB PNGs when its safety filter triggers. No exception, no warning. About 50% of typical Final Hours generations fail this way on the original pass. Always audit:

```bash
find projects/<project>/stills -maxdepth 1 -name "shot_*.png" -size -200k
```

Any results are silent rejects. Either restill them via `restill_from_feedback.py` or accept them as held-still fallbacks during finish.

### Step 9.6 — Generate the HTML review page

```bash
python ../shared/make_review_page.py --project projects/<project>
```

Writes `projects/<project>/review.html`. Each shot renders as a card showing the still, narration, canon-resolved image prompt, Accept/Reject buttons, Notes textarea, and (when the server is running) Override prompt textarea + Regenerate button. State auto-saves to localStorage.

### Step 9.7 — Start the local review server

```bash
python ../shared/serve_review.py --project projects/<project>
```

Server runs on `http://localhost:8000/` (127.0.0.1 only, not LAN-exposed). Open that URL. The Server live badge turns green and the Regenerate buttons unhide.

### Two regeneration modes

**Notes mode (default).** Notes textarea appends "REGENERATION FEEDBACK: <note>" to the canon-resolved beat prompt. Soft guidance. ~80% of regenerations.

**Override mode (new).** Override textarea (purple border) REPLACES the prompt entirely — no canon, no original prompt, no rulebook negatives. Surgical control when Notes mode can't fight Flux's bias toward early tokens. ~20% of regenerations, the stubborn ones.

### Freelancer handoff variant

Zip the project folder with stills + review.html. Freelancer opens static HTML, does accept/reject + writes notes, hits Export JSON, sends back. Run `python ../shared/restill_from_feedback.py --project projects/<project> --feedback <theirs>.json` to batch-restill from their feedback. Their machine never touches your fal credentials.

### Backups

Every regeneration backs up the existing still to `projects/<project>/stills/_backup/shot_NNN_<timestamp>.png` before overwriting. Restore older versions if a regen is worse than what it replaced.

---

## PART 8 — BANKED PRINCIPLES (hard-won)

### Flux-pro safety_tolerance default

`fal-ai/flux-pro/v1.1` defaults to `safety_tolerance: 2` (strictest) and silently returns ~7KB black PNGs on rejection. Always pass `"safety_tolerance": "5"` in fal args. Banked in `restill_from_feedback.py`. **TODO: patch `recreation_pipeline.py` to match — current default still triggers ~50% silent failure rate on original generation pass.**

### Mandatory silent-rejection audit

After every stills generation, run `find projects/<name>/stills -maxdepth 1 -name "shot_*.png" -size -200k`. Any results are silent rejects. 30-second check, prevents shipping a half-broken video.

### Flux trigger-word vocabulary

Word combinations that trigger silent safety rejection even at tolerance 5:
- `fire + survivor + wreckage` (crash sequences)
- `hand + finger + dial` (body-parts-near-objects)
- `emergency + vehicles + disaster` (aftermath aerials)
- `eyes + close up + person` (face-too-close)

Neutralize with: `warm light` not fire, `lone figure` not survivor, `industrial cylindrical metal` not aircraft engine, `product photograph` not office scene.

### Mac Python 3.12 SSL fix for fal_client

fal_client uses httpx internally; httpx ignores `SSL_CERT_FILE` env var. Standard CA bundle fixes don't work. Monkey-patch `httpx.Client.__init__` to default `verify=False` BEFORE fal_client imports:

```python
import httpx as _httpx
_orig = _httpx.Client.__init__
def _patched(self, *a, **kw):
    kw["verify"] = False
    _orig(self, *a, **kw)
_httpx.Client.__init__ = _patched
```

Must be at the TOP of the file (line 1). httpx caches its SSL context at import time. Pattern banked in `restill_from_feedback.py` and `serve_review.py`.

### Override > Notes for hard corrections

When Notes mode keeps producing the same wrong result, Flux is weighting the early canon and original-prompt tokens too heavily. Switch to Override mode — provide ONLY the new prompt. Lands in 1-2 retries instead of 4-6.

### Flux text rendering

Flux can render SHORT all-caps text (3-5 words max per block). Longer text mangles. For thumbnails: use short hook phrases ("8 SECONDS" + "583 DEAD") rather than full titles. Full title goes in YouTube's title field next to the thumbnail.

### Step 0 mandatory pre-read

For any video production session, Claude reads before script writing begins:
- `script-craft-principles.md`
- `production-patterns-that-work.md`
- `hook-craft-library.md`
- `rulebook.json` (channel + shared)
- `calibration-reference.md`

Banked 2 June 2026 after KLM Tenerife v1 failure where writing from generic instinct produced a script with 3-4 principle violations.

---

*Full session notes for the 3 June 2026 session that built this system are at `shared/docs/session-notes-2026-06-03.md` — includes KLM Tenerife ship details, Mary Celeste performance analysis, Synthetic Press architecture banking, and banked-for-tomorrow items.*
