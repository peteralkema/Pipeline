# Synthetic Press — Mode B (Remotion) Notes
*What Mode B is, the component vocabulary, the timing architecture, and the principles banked building it.*
*v1.0 — 5 June 2026. Written after a cold-start morning that produced the six Mode B components, the two-layer timing model, and the Whisper voice-sync matcher (sandbox prototype in `shared/synthetic-press/remotion/`).*

This is the design + principles layer for Mode B. The operational pipeline layer (how it dispatches inside a render) is not built yet — this captures the architecture and the lessons so the build, when it comes, doesn't re-derive them.

---

## What Mode B is, and where it sits

Synthetic Press has a two-mode visual architecture:
- **Mode A** — cinematic recreation (stills → clips). The Final Hours engine. Probabilistic (fal generation), reviewed at the stills gate.
- **Mode B** — Remotion-rendered, Vox-style motion graphics. Deterministic (code renders the same output every time). NOT reviewed at the stills gate — correctness is checked as facts-at-script-time and sync-at-final-cut.

Rough split for an AI-documentary episode: Mode A 60–70%, Mode B 30–40%. Mode B carries the explainer beats — the moments where text, data, a quote, or a document needs to be *shown and read*, not recreated.

A third register sits alongside these (discussed but not a "mode"): **archival / real footage as a privileged interruption** — used rarely, only when the real artifact or a real recent face is structurally required. See the archival note at the end.

---

## The Mode B component vocabulary (six components, and there is no seventh fundamental)

Each component teaches one core technique. Everything else you'd ever build (bullet builds, bar charts, diagrams, maps) is a *recombination* of these — there is no further fundamental technique to learn.

1. **HighlightedHeadline** — text + attention direction. Technique: fade + an animated `linear-gradient` "highlight sweep" behind a key phrase (two gradient stops at the same %, animated 0→100, = a hard sweeping edge). The Vox move: line appears, *holds a beat*, then the highlight lands on the stressed phrase. The hold is the craft.
2. **LowerThird** — name/title card sliding in from a corner. Technique: animating **position and size** (translateX, bar height) from the frame, not just opacity; staggered timing (bar grows, then card slides) = choreography.
3. **NumberCounter** — a value counting up ($0→$13B, 0→260 dead). Technique: **the frame drives the displayed data, not just style** — `Math.round(interpolate(...)).toLocaleString()`. Ease-out cubic so the number *arrives* (decelerates) rather than scrolls.
4. **ChapterCard** — act-break / date-stamp. Technique: **reveal-by-mask** (a parent with `overflow:hidden`, child slides up from inside → text wipes up from behind a clean edge) + a self-drawing accent rule. Also: a reusable `MaskedLine` sub-component with a `delay` prop.
5. **QuoteCard** — pull-quote with attribution. Technique: **sequencing-as-meaning** — four elements (quote mark, quote, dash, attribution) arrive in a deliberate offset order that leads the eye. No new motion primitive; the quality is the order and timing.
6. **DocumentReveal** — a "fake real" artifact (tweet/headline/filing) with a box that draws itself around the key line. Technique: compositing a layered card (chrome + body) + **self-drawing SVG line art** via `strokeDasharray` + animated `strokeDashoffset` (dash = full perimeter, offset full→0 = the stroke draws itself). Same trick draws underlines, circles, arrows, connectors.

The techniques, distilled: attention (1) · position/size (2) · frame-drives-data (3) · reveal-by-mask (4) · sequencing-as-meaning (5) · composited artifact + SVG line art (6).

### Shared component conventions (current prototype)
- Background `#0a0a0f` (cold near-black), text `#f5f5f5`, muted `#9aa0aa`, accent `#3b5bdb` (cold indigo — Synthetic register, deliberately not Vox yellow).
- Inter via `@remotion/google-fonts/Inter`, `loadFont()` called once at module level.
- `interpolate(...)` always with `extrapolateLeft/Right: "clamp"` (un-clamped is the #1 beginner bug — flicker/invisible elements).
- Easing: smoothstep `t*t*(3-2*t)` or ease-out cubic `1-(1-t)^3` — linear feels clinical; eased feels considered. This is the register dial.
- Defensive guard on text props (`text ? text.indexOf(...) : -1`) so a missing/empty beat renders blank instead of crashing the whole render.

**Deferred:** a universal/configurable Synthetic Mode B **design system** — factor the shared tokens (background, Inter load, accent, easing) out of the six components into one module, so the visual identity is defined once. Do this at repo-port time, *after* the components are proven and synced — premature before that.

---

## The timing architecture (two layers)

The central realization. Two different timing questions, answered by two different mechanisms:

**Layer 1 — placement: `<Sequence from={X}>`.** Drops a component onto the master timeline at frame X *and resets that component's internal clock to 0*. So components animate from their own zero and don't change for placement — the sequencer just wraps each one. Master-timeline position and a component's local clock are independent.

**Layer 2 — internal emphasis: a prop-driven frame.** The sweep/box/counter fires at a frame passed *in* (e.g. `sweepStart`), relative to the beat's own clock — not a hardcoded constant. This is the hook voice-sync drives.

Worked example: a beat at `from={90}` with `sweepStart={42}` → the beat appears at master-frame 90, its sweep fires at master-frame 132. Placement (`from`) and emphasis (`sweepStart`) are independent knobs — which is exactly what sync needs, because Whisper supplies both numbers.

### The data contract: `beats.json` + a registry
- A flat object per beat: orchestration fields (`component`, `from`, `durationInFrames`) + the rest are the component's own props.
- `SyntheticSequence` reads `beats.json`, maps `beat.component` (a string) → real component via a **REGISTRY** lookup, spreads the remaining fields as props, wraps in `<Sequence>`.
- The registry is the single mechanism that lets a *data file* choose what code renders. Every new component = one line in the registry. This is exactly how the eventual Synthetic orchestrator picks components per beat.

Full chain, end to end: **script phrase + `voiceover.json` → `match_beats.py` → `beats.json` → SyntheticSequence (registry + `<Sequence>`) → synced render.** Every link built and seen working in the sandbox.

---

## THE PRINCIPLE: the audio is the source of truth

Everything else in the pipeline is a prediction until the audio exists — the script *estimates* duration (words ÷ 135), the storyboard *estimates* shots, hand-typed frames are *guesses*. Guesses drift (Pudding Lane: Inworld rendered 13% faster than predicted, the video felt rushed). **The voiceover is the one artifact that is not a prediction** — it's the actual audio the viewer hears, measured to the millisecond by Whisper.

So: **visuals follow measured audio, never the reverse.** You don't time narration to fit a nice animation; you render the voice, measure it, and hang the visuals off the measurement.

This is the *same* principle already banked as "measurement over prediction" in the playbook's true-up note (Mode A shot durations) — now applied a second time, to Mode B emphasis timing. **Mode A and Mode B share one spine:** generate the voice → measure it (Whisper) → hang everything off the measurement. That unification is the point.

Consequence for workflow: in any Mode B beat, the voiceover is produced *first*, then matched, then visuals placed. Same ordering as Mode A's Whisper-align finish step.

### Application: "the spoken line and its receipt" (the quoted-moment pattern)
The flagship use of QuoteCard + HighlightedHeadline + voice-sync. When the narrator voices a real line for impact, **the visual carries the attribution so the voice doesn't have to.** Three layers, no redundancy: **voice** = the words (the narrator just says the line — never "as X wrote, quote… end quote"); **card** (QuoteCard / DocumentReveal) = the words *plus* name/source/date, the citation the voice omits; **highlight** (HighlightedHeadline sweep) = the stressed phrase, voice-synced via the matcher so it lands as spoken. A narrator *claiming* a quote is an assertion; saying it *while the sourced card builds* is the assertion plus its receipt, in one beat — the documentary-witness credibility move, mechanical. **No-karaoke rule:** the card never duplicates the full sentence as text the narrator is also reading verbatim (eyes + ears doing the identical thing is redundant). This is why the matcher matters beyond emphasis timing: it's what lets the receipt build *as the line is spoken*. (Banked in full in the Synthetic series doc; the script-craft side is a sub-note under Principle 8.)

---

## The Whisper matcher (`match_beats.py`)

Turns hand-typed timings into audio-derived ones. Reads a Whisper `voiceover.json` (word-level timestamps — the format the true-up already produces) + a beat spec (which phrase to emphasize per beat); writes `beats.json` with computed `from` (beat's words begin) and `sweepStart` (emphasis phrase spoken, relative to the beat).

**The only hard part is fuzzy matching.** Spoken ≠ written: "thirteen billion dollars" vs "$13 billion", lowercasing, dropped punctuation, split contractions. The matcher normalizes (lowercase, strip punctuation, collapse whitespace) and slides a variable-width window using `difflib.SequenceMatcher` to find the best span. A naïve `indexOf` on the joined transcript would miss constantly.

**Design = computed-default + human-confirmable (Option B), same philosophy as the canon gate.** The matcher emits a confidence score per match and flags low-confidence ones for REVIEW. It does the work; you only eyeball the ~10% it's unsure about and hand-edit frames in `beats.json`. Never ship an unreviewed timestamp — a sweep firing on "the" instead of "deceive."

It's a standalone Python script (lives with `align_with_whisper.py`), not TS inside Remotion: Python computes, the render layer reads. Same seam as the rest of the pipeline.

**Whisper transcribes human audio fine** — better than TTS, in fact (natural prosody gives clearer word boundaries). The synthetic-voice case is the slightly harder one.

---

## Human voice as an evidentiary register (marquee episodes)

A synthetic voice says "this is a recreation." A *named, credible human* voice says "a real person is telling you this and vouches for it." For an AI-industry channel whose credibility problem is "is this just AI slop," a human narrator on flagship Synthetic episodes is a costly, uncopyable trust signal — the audio equivalent of the on-brand thumbnail discipline. (Inspiration: Karen Hao reading her own *Empire of AI* audiobook.) Reserve it for the marquee pieces, like reserving real archival for the one irreplaceable moment. Same principle, applied to voice: generate the ordinary, bring the human for the moments that carry the weight.

### Swapping Inworld → human voice after a video is "done"
Because audio is the source of truth, swapping the voice re-derives everything that hangs off it; nothing visual regenerates. It's a **true-up triggered deliberately**, not a re-render.
- **Changes:** the voiceover file → Whisper align → per-shot Mode A durations AND Mode B `from`/`sweepStart`. A human read differs *locally* in rhythm (lingers, breathes), not just globally, so timings shift per-shot/per-beat — the assembler already absorbs this (trim-to-audio_duration, zero global drift).
- **Does NOT change:** stills, clips, component code, script, canon, thumbnail. No fal spend.
- **Non-negotiable:** re-run `match_beats.py` for Mode B beats, not just re-assemble — otherwise visuals play at old emphasis frames over new audio and drift.
- Sequence: swap file → Whisper → `align_with_whisper.py` → `match_beats.py` → `finish --assemble-only`.

**Build a `--voiceover <path>` override on `finish`** that skips the Inworld call and feeds a provided file into the Whisper-align-assemble tail. Makes the human swap "just run finish with `--voiceover human.mp3`," and doubles as the fix for the backlog item "finish regenerates voiceover every run and stales alignment."

---

## Archival / real footage — the third register (banked, not built)

Not a "Mode C." Archival is a **privileged interruption**, used rarely, for *evidentiary* weight the generated image can't carry. Rule: **recreate the experience (generate), show the evidence (archival) — and only show evidence you can prove you're allowed to show.**

When the real thing is genuinely the only thing:
- the iconic real artifact the story is partly *about* (the actual Hindenburg photo);
- a real, named, recent person's face (you can't generate Sam Altman — structurally required for Synthetic, the big divergence from Final Hours' face-never-resolved);
- a document/screen where its *realness* matters (a deleted tweet) — though usually Mode B *recreation* of a document is better (controllable, branded, no rights issue).

**Rights reality:** "fair use" is a narrow legal *defence*, not permission, and on YouTube it's adjudicated by Content ID (automated, owner-friendly) — a claim silently diverts the breakout video's revenue, which is the exact catastrophe to avoid for a power-law channel. Bias hard to **public domain** (pre-1929 US, most pre-WWI photography, US-gov/NASA/NARA/LoC) and **explicitly licensed** (checked Wikimedia/CC0). If built, the production pattern needs a **provenance/clearance step** (a `sources.json` recording URL + licence + rights basis) — the step with no Mode A equivalent and the one that protects you.

Preference order when more than one register could do a job (control + moat, high→low): **Mode A (generate) → Mode B (Remotion) → licensed/public-domain archival → claimed/fair-use archival.** Go down the list, stop at the first that can honestly do the job. Mostly 1 or 2; occasionally 3; almost never 4. That ordering keeps the "strung-together clips" feel away by construction.

---

## Status & next steps (as of 5 June 2026)

**Built and proven in the sandbox** (`shared/synthetic-press/remotion/`): six components, the two-layer timing model, `SyntheticSequence` reading `beats.json` via a registry, `match_beats.py` with fuzzy matching + confidence flags. Every link of the chain seen working with a fake voiceover.

**Not yet done (each a clean standalone session, needs the box / real assets):**
1. Run `match_beats.py` against a *real* Inworld voiceover (`voiceover.json`) — prove the fuzzy matcher survives real Whisper drift.
2. Build the real Remotion project inside the repo (its own `Root.tsx`); render an actual synced multi-beat clip over real audio.
3. Factor the shared tokens into the universal Synthetic Mode B **design system**.
4. The Synthetic **orchestrator** (separate from the Final Hours conductor): mode dispatch (A vs B per beat), Mode B beats skipped at the stills gate, `--voiceover` override, renderer-interface seam designed on paper first.
5. Decide archival policy if/when a real face or iconic artifact is genuinely required (provenance step).

The components are a sandbox prototype copied into the repo for safekeeping — not yet wired into any pipeline. Porting + the design system is step 2–3 above.
