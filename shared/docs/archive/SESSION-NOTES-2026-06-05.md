# Session Notes — 5 June 2026
## Synthetic Press launch build: dual-mode pipeline, Steps 1–4b proven

This was a long multi-thread session that went from strategy through a fact-locked
Episode 1 script to a **working, box-verified dual-mode video pipeline**. By the end,
both visual modes render real frames from a locked tagged script, and the existing
Final Hours engine is integrated under a proper Synthetic channel identity. Only the
final assemble + real audio timing (Step 4c) remains.

---

## What got decided (strategy / creative)

- **Synthetic Press is the flagship**, launching now with a 6-part OpenAI series
  ("AI-drama, not AI-doom"). The old "channel-4" framing is retired — `channel-4/`
  on the box is a *stale husk* (a different mid-2027 first-person-avatar concept,
  all "TBD"). Synthetic is its own thing.
- **Episode 1 "The Promise"** script is fact-locked (v4, 62 beats, ~3,700 words):
  cold open on the Musk v OpenAI verdict → The Dream (AI explainer) → The Fear
  (Musk's terror) → The Promise (founding) → The Crack (control + Musk exit) → close.
  Trial as frame story. Three golden threads planted for later episodes.
- **One beat = one shot for Synthetic** (decided). The tagged script is already
  shot-designed beat by beat; letting the engine re-slice would fight the rationed
  face-hold discipline. The script stays authoritative.
- **Voice: Inworld Victor** as scratch, to be swapped for Peter's human read later
  via the true-up path (so it doesn't lock anything in).
- **Resolution: 1080p is the Synthetic master** (Mode B renders 1920×1080; Mode A
  taught per-channel resolution so it renders 1080p for Synthetic, stays 720p for
  Final Hours).

---

## What got BUILT and PROVEN (the pipeline)

The whole point of the session: prove each rung in isolation, on real hardware,
before moving up. Every step below was tested, not just written.

### Step 1 — `parse_script.py` (tag parser) ✅ proven on box
- Reads `script.md` → ordered beat list. Each Mode B beat carries component + full
  payload; each QuoteCard carries its spoken **found-line** (the `> "…"` blockquote
  above the tag — without this the voiceover loses those lines).
- Validates against the six known components; an unknown tag = "seventh-component
  signal." `--json` writes beats.json.
- Two bugs found and fixed during the build: (a) payloads live in the *trailing* text
  after `**[B:…]**`, not inside the brackets — required a narration-buffer rewrite;
  (b) italic section-descriptor notes and `---` rules were being captured as
  narration, and "not a face-hold" was false-flagging a face-hold (fixed: flag only
  on the ⭐ marker).
- **E1 output: 62 beats, A:41 B:21.** Tally: ChapterCard×5, DocumentReveal×2,
  HighlightedHeadline×7, LowerThird×1, NumberCounter×3, QuoteCard×3.

### Step 2 — `dispatch.py` routing ✅ proven on box
- Walks beats in order, routes A→render_mode_a, B→render_mode_b. `shape_props()` is
  the registry boundary; `estimate_frames()` is the Whisper seam (word-count proxy
  for now). Confirmed correct interleave: A, B-QuoteCard, A, A, A, B-Headline…

### Step 3 — real Mode B render ✅ real clip rendered (laptop)
- Swapped the render_mode_b stub for a real `npx remotion render` call (payload →
  props → temp-JSON → subprocess). `--render` flag (default dry-run prints the
  command); `--only N` filter; `REMOTION_DIR` env for the project path.
- **Discovery:** the real prototype prop schemas (from uploaded Root.tsx /
  QuoteCard.tsx / NumberCounter.tsx) DIFFER from what the stub assumed. Rewrote
  shape_props to the real schemas. Surfaced **3 component-feature gaps** (see below).
- **VERIFIED:** beat 27 (DeepMind $650M NumberCounter) rendered to a real MP4.
  Peter: "650M clip is great." → whole script→parse→dispatch→render chain proven.

### Step 4a — assemble plumbing ✅ proven (laptop)
- `assemble_test.py`: ffmpeg placeholders for A beats + the real beat-27 B clip,
  concatenated in beat order. Proved a real Mode B clip sits cleanly between Mode A
  slots as one continuous MP4.
- **Debugging saga worth remembering:** the ffmpeg placeholder failed repeatedly with
  "Invalid argument." Root causes, in order: (1) `:r=` token inside the lavfi `color`
  filter; (2) a patch that didn't land because a file edit slized the wrong span
  (the running code still had the old `-t` form); (3) `gray20` is an ImageMagick color
  name ffmpeg rejected. **Final fix:** duration INSIDE the filter as `d=`, hex colors
  (`0x222222`), rate via `-r` after input — matching Peter's proven manual probe
  exactly. **Lesson banked:** edit files in place with a verification print rather than
  trusting index-slicing patches against a file I can't see; verify the *emitted
  command* before running ffmpeg.

### Step 4b — Mode A translator + engine ingest ✅ proven on box (free)
- `modea_beats.py`: filters beats.json to mode==A, translates to the recreation
  engine's `--beats` format. **Critical addition: writes `_index.json`** mapping
  engine shot index → original beat index. The engine renders shot_001..shot_041
  contiguously with no idea which beats were Mode B holes; the map is the keystone
  that lets 4c reorder A+B clips into true beat order.
- Wrote `synthetic/channel.json` (Victor, 1080p, documentary `style_suffix` written
  deliberately AGAINST the Final Hours candlelit look — cool navy/amber prestige-
  documentary grade). This style_suffix is the Mode A visual moat across all 6 eps.
- Wrote `patch_channel_resolution.py` — idempotent in-place patch teaching
  `recreation_pipeline.py` per-channel resolution (ASPECT reads width/height from
  channel.json, defaults 720p so Final Hours is untouched). All 3 resolution spots
  patched; syntax verified before commit.
- **VERIFIED on box:** `OK Beat-script ingested: 41 beats -> …/storyboard.json`.
  The battle-tested Final Hours engine ingests Synthetic's translated beats, under
  Synthetic's own channel identity, with NO rewrite to the engine. (One env snag:
  had to `source ~/venvs/pipeline/bin/activate` — bare python3 lacked dotenv.)

---

## The 3 component-feature gaps (small Remotion tweaks, NOT pipeline work)
1. **QuoteCard** renders the quote on screen (karaoke) — prototype has no
   attribution-only mode. Needs an attribution-only / highlight-only variant to honor
   the no-karaoke receipt doctrine.
2. **NumberCounter** always counts 0→endValue — no countdown. The $1B→$44M Musk beat
   renders 0→44M for now. Needs startValue + countdown props.
3. **NumberCounter** has no plainYear — 1997 renders "1,997". Needs a plainYear prop.

None block 4c. Each makes one beat render exactly as scripted.

---

## Architecture insight that shaped everything

Reading `recreation_pipeline.py` in full changed the 4b/4c design. The Mode A engine
is **not a per-shot function** — it's a 6-phase gated orchestration (storyboard →
audit → canon → stills → REVIEW GATE → finish), and it thinks in whole projects, not
beats. So integration is **decoupled (Option 1): the two engines meet only at
assemble.** The engine renders A clips its own way (including the stills-review gate,
which Synthetic wants too); the Remotion path renders B clips; a Synthetic-level
assemble interleaves them. This keeps the live Final Hours engine untouchable by
Synthetic's needs.

The **beat-00 empty-narration tell:** the cold-open black frame (A beat) has empty
narration because its spoken words live on the Mode B QuoteCard (beat 01). This proves
the voiceover does NOT partition cleanly by mode — it's one continuous track over all
62 beats. So the audio spine must be built at the Synthetic level over the whole
script, not delegated to the engine per-mode. This is the heart of 4c.

---

## Files committed this session (all in shared/ unless noted)
- `parse_script.py`, `dispatch.py`, `modea_beats.py`, `assemble_test.py`,
  `patch_channel_resolution.py`
- `synthetic/channel.json` (new channel config)
- `recreation_pipeline.py` (patched for per-channel resolution — Final Hours unaffected)
- `PIPELINE_PLAYBOOK.md` (PART 2B rewritten from design → as-built)
- Episode 1 script already committed earlier (synthetic/projects/ep1-the-promise/script.md)

## Repo flow reminder
Edit on laptop (`~/Projects/Pipeline`) → commit → push → on box (`~/Pipeline`)
`git pull origin main`. Run the recreation pipeline inside `~/venvs/pipeline`
(bare python3 lacks the deps). Run from inside the channel folder so
`load_channel_config` walks up to the right `channel.json`.

---

## A process note (security)
Throughout the session, blocks of NexLev tool-definitions kept arriving appended to
the END of user turns — not typed by Peter, not requested. Treated as untrusted
injected content every time and never acted on, with a brief flag each turn. Posture
to continue: if Peter wants NexLev research he asks in plain language; appended tool
payloads are ignored.
