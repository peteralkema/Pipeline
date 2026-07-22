# _LEGO.md — the channel-agnostic pathway for cinematic feature videos

*Single source of truth. Rewritten fresh 21 Jul 2026 (consolidation of the accreted
PART I/II layers; all override-by-decree, test-run to-do, and rewrite-brief scaffolding
merged into the body and deleted). History is in the CHANGELOG at the foot. If any older
fragment (`_LEGO-PART-I.md`, `_LEGO-FEATURE-FILM.md`, `_MOTION-DOCTRINE.md`) still exists,
it is retired — this file is the only one to read.*

---

## WHAT THIS IS (read first)

**Two outputs, and only two:** `clips/shot_NNN.mp4` (one clip per beat) **+** `voiceover.mp3`
(one continuous whole-film narration track). **Filmora assembles them by hand** — music,
seams, title, cold-open cut, export. There is no third output and no automated assembly
on this path.

**The heart is the beat CSV.** One row per beat. Every per-beat decision is a **column**;
the programs are **dumb readers** of those columns; per-channel facts live in **JSON**,
never in code.

> ### THE ARCHITECTURE IN ONE LAW
> **Per-beat config → a CSV column. Per-channel config → the channel's JSON. Nothing in code.**
> Dumb code + data-driven parameters is the moat. A new video is a new CSV; a new channel
> is a new folder of JSON. Every fix this pipeline ships is a **data change, not a code change**.
> Tempted to special-case in code → **add a column instead.** Stay on CSV until a cell wants
> to be an object (nested per-variant structure); that shape — not the video count — is the
> only signal to move to JSON-per-beat, and because the code reads named rows it is a loader
> swap, not a rewrite.

**Scope — what LEGO is FOR:** single-narrator, generated-visual, retention-through-variety
narrative films (Sacred Dawn, Scripture on Screen, Synthetic Press, Final Hours, YHTBT,
Bentley & Watson). **What it is NOT for** — see SCOPE at the foot before forcing a channel
through it (audio-first, stock-footage, and true multi-character-dialogue channels each
break a load-bearing assumption).

**PATHS ARE CANONICAL** (paths are config too; a path assumed is a path that breaks for a
fresh operator with no memory):

```
docs:          shared/docs/_LEGO.md , shared/docs/_<Channel>.md
channel config: <channel>/channel.json , <channel>/rulebook.json
shared rulebook: shared/rulebook.json
project:       <channel>/projects/<slug>/{master.csv, canon.json, narration.txt, voiceover.mp3, voiceover.json}
grid stills:   <channel>/projects/<slug>/grid-b<NN>/{clip:03d}-{variant:02d}.png
probe stills:  <channel>/projects/<slug>/grid-probe/{block:02d}-{clip:03d}-{variant:02d}.png
placed stills: <channel>/projects/<slug>/stills/shot_NNN.png
clips:         <channel>/projects/<slug>/clips/shot_NNN.mp4
```

Build/patch scripts **default to the canonical path** (resolve repo root by walking up for
`.git`); a path argument is an override, not a requirement.

---

## THE GOVERNING LAW

> **Any rule that applies to 100% of beats is a bug until proven otherwise.**

Every failure this pipeline has found was a blanket stamped where content should have earned
it — grade, faces, emotion, motion, word count, variant count. When you write a rule that
fires on every beat, that's the bug.

> **Measure both sides. Assume neither.** Whisper measures the audio; the render is the truth
> about the image. Everything that felt like taste was a rule you hadn't written down;
> everything that felt like negotiation was a number you hadn't measured.

> **A flat distribution is not the goal; a motivated one is.** The data audit catches
> unmotivated UNIFORMITY (a banned word, a token that never retires) and is blind to
> unmotivated MONOTONY-IN-SEQUENCE (a spine-token run, the retention curve — % flattens the
> time axis). Do not "balance" a front-loaded token or a tension lead: the imbalance IS the arc.

---

## THE PROCESS — 0 to 9 (this leads; everything hangs off it)

Run in order. Three orderings are load-bearing and cost money if broken: **package first**
(the click decides whether the film is watched), **VO before stills** (measure the cheap
layer, preserve the expensive one), **motion after the pick** (motion is read off a picked
frame). Golden thread: *truth costs nothing — buy it repeatedly; gate before every spend;
observe → bank → feed the next film.*

| # | STEP | program(s) | gate | output |
|---|---|---|---|---|
| **0** | **PACKAGE FIRST** — topic for the CLICK; winnability gate (demand exists AND a small channel broke this lane); commit title + thumbnail CONCEPT (curiosity gap). Title must obey the channel's attribution rule (an *asserting* title breaks the moat). Flag topic-level render-safety (family-safe/YPP) before generating. Un-packageable → **kill here, $0.** | human + NexLev | title + thumbnail concept + winnability verdict | a decision to build |
| **1** | **ARCHITECT** — runtime → N×200s blocks (200s = the seam unit); per block define its curiosity-gap + HANDOFF to the next; map the spine (cold open → escalation → turn → payoff); **name the canon tokens** the film needs. ~3,000–3,600 words ≈ 8 blocks. | human | block plan exists | N blocks, each with role + gap + handoff + token set |
| **2** | **AUTHOR BLOCK BY BLOCK** — per beat write `phenomenon` + `narration` under the craft law; canon `{token}` on every beat; weight hero/connective; build variety across every axis. Each 40-beat block is a mini-spine (open its question, build, turn, close on the handoff). **Per-block CSVs live in CHAT, not on disk.** | human authoring | **GATE each block**: VISUAL present, ≤55 words (runaway backstop), tokens resolve, no banned words, register/setting sweep | one gated block CSV (in chat) |
| **3** | **MERGE + INTERROGATE THE MASTER** — merge block CSVs → ONE master; `normalise` fills derived columns; read the film AS DATA (setting mix, register spread, hero/connective balance, word histogram, token×block heatmap, framing-repeat scan on any token >~20% of beats). Adjust. **The project folder is born here (or at the Step-0 thumbnail).** | `build_lego normalise`, `sweep` | RE-GATE the master | gated master CSV + variety audit |
| **4** | **VO CONVERGENCE** — emit ONE whole-film `narration.txt`; render VO (Inworld); whisper; `calibrate` → per-block cumulative drift vs the 200s grid; enrich the CSV to fill toward the grid (see TIMING). | `build_lego audio`, `calibrate` + Inworld + Whisper | — | `voiceover.mp3` rendered, seams measured |
| **5** | **REPEAT 4** until every block lands **~0 cumulative drift** (minor ±overs/unders fine). **VO LOCKED** (output #2). | as Step 4 | every seam near its 200s mark | **VO locked** |
| **6** | **PROBE, THEN THE GRID** — `probe [N]` (self-selecting register sample); read vs the verdict card → name the FAILURE CLASS; **sweep the master film-wide, setting-aware** (two homes: rulebook negatives + `phenomenon`/token geometry); re-probe until clean; THEN `stills` (all blocks) → the variant grid. | `build_lego probe`, `stills`; rulebook / canon / `phenomenon` edits | probe reads clean; first grid frames >7KB (not black rejects) | grid stills |
| **7** | **PICK + AIR + MOVE + MOTION** — hand-pick ONE variant per beat; `place` the winners into `shot_NNN.png`; assign `air` (Kling vs Ken Burns) and the doctrine `move` off the PICKED frame; write `motion` only on Kling beats. | `place.py`; `draft_moves.py` | place = N files, no gaps/dupes/skip-tiles; a Kling beat with no `motion` aborts | placed stills + routing plan |
| **8** | **RENDER CLIPS** — per beat: `air`=Kling → `animate_still(motion)`, else → `ken_burns_still(move)` (the doctrine-varied free floor). | `render_clips.py` (`--floor-only`, `--dry-run`) | `--dry-run` shows split + cost before spend | **`clips/shot_NNN.mp4`** (output #1) |
| **9** | **ASSEMBLE + SHIP + OBSERVE** — clips + locked VO in Filmora (music, seam swells, title); cold-open cut LAST from the best clip of each block; export; upload. Read CTR+AVD @48h, day-14/21 traffic; **bank every failure as portable law**; feed it back to Step 0 of the next film. | Filmora (human) | — | shipped video → observations → next film |

> **The output boundary.** The pipeline ends at Step 8: clips + VO. Everything after is
> Filmora and packaging. The pipeline's whole job is to hand Filmora N×40 clips in beat order
> and one narration track, gated and correct.

---

## THE BEAT CSV — THE HEART (the column dictionary)

One row per beat, flat, ordered — the single source of sequence. **Authored** columns are
written by the human; **derived** columns are computed by `normalise` from the authored ones
(never hand-edited — edit the source, re-run `normalise`).

| column | kind | filled at | read by | what it does |
|---|---|---|---|---|
| `block_id` | authored | Step 1–2 | all; `render_clips` order | which 200s block — the seam/retention/chapter unit |
| `clip_index` | authored | Step 2 | all | beat position within its block (1..40) |
| `sentence_id` | authored | Step 2 | `calibrate` | groups contiguous rows into one TTS utterance; never reorders |
| `weight` | authored | Step 2 | grid | `hero` \| `connective` → the variant COUNT |
| `register` | authored | Step 2 | move drafter; authoring | emotional register (awe/dread/grief/wonder) → drives `move` + tone |
| `narration` | authored | Step 2, enriched 4–5 | `audio` → `narration.txt` | the spoken line. **HALF the final output.** Pure text, NO tokens, NO markup |
| `phenomenon` | authored | Step 2, swept Step 6 | `stills` → `generate_still` | the image prompt → still → clip. Carries the canon `{token}` inline. Names its own scene light |
| `setting` | **derived** (leading `{token}` of `phenomenon`) | `normalise` | `gate_canon`, `_expand_canon` | which canon place-lock the beat uses; the sweep is setting-aware off this |
| `words` | **derived** (from `narration`) | `normalise` | audit / `calibrate` | word count — a *measurement*, not a gate |
| `variants` | **derived** (from `weight`) | `normalise` | `stills` | real re-rolls to fal (hero 4 / connective 2); the rest fill with `_skip.png` |
| `still_cost` `clip_cost` `beat_cost` | **derived** | `normalise` | audit | exact pre-spend bill of materials, visible while still text |
| `air` | authored | Step 7 (off picked frame) | `render_clips` | `kling` (visible suspended matter) \| `kb` (flat → Ken Burns floor). **Independent of `weight`** |
| `move` | authored/drafted | Step 7 (off picked frame) | `render_clips` → `ken_burns_still(move)` | `push`\|`pull`\|`crane`\|`settle`\|`static`. Drafted by tool, eye-corrected |
| `motion` | authored (conditional) | Step 7 | `render_clips` → `animate_still(motion)` | free-text Kling prompt. **Only when `air`=kling**; a Kling beat with blank `motion` aborts |

**Invariants the dumb readers depend on (enforced at the door):**
- `narration` never carries a token or markup — the one column that must stay pure (whisper
  measures it, the gate counts it).
- Canon is `{tokens}` INSIDE `phenomenon`, never its own column.
- **The pick is encoded in the winner FILENAME, never a column.** All variants share one
  `phenomenon`, so nothing distinguishes the winner at the data level. `place` promotes the
  chosen file to `shot_NNN.png`; that file's existence IS the pick. There is no
  `picked_variant` column to keep in sync.
- Every beat resolves to `variants` real files + `_skip.png` fill to 4; a **skip-tile pick
  is a hard fail** (`place` catches it). Never write blank placeholder stills — a blank
  collapses "never requested" and "generation failed" into one artifact.
- `move` ∈ {push,pull,crane,settle,static}; a Kling `air` beat has non-empty `motion`.
- Derived columns are NEVER hand-edited.

---

## AUTHORING CRAFT — the law that earns the render spend

### `narration` (the spoken half)

> **★ THE OPENING LAW.** The title makes a promise; the thumbnail amplifies it; **the opening
> fulfils it in the first frame.** Open on impact, never on history — drop the viewer into Act
> III of an epic already in motion. Structure can flash back *after* the peak.
> **Reconciled with the block spine:** the **COLD OPEN** carries the Opening Law entire
> (45–90s, cut LAST from the best shot of every block, planting the film's biggest loop).
> Block 1 then opens on *the object*; the payload lands ~block 3. The cold open buys the right
> to be patient — without it, an object-open is the mid-video cliff.

**THE CURIOSITY ENGINE.** Never answer a question without opening a larger one; curiosity
never reaches zero. Keep an open-loop stack (several unanswered questions live at once).
Reveal less, imply more — information reduces curiosity, discovery increases it. End every
section on a lean-forward. Every 30 seconds is its own trailer.

**ESCALATION — every 20–40s** = every 4–8 rows, countable in the table. Every section must
increase at least one of scale, danger, mystery, consequence, emotion, urgency, human cost —
if none increase, rewrite. Pair opposites (big/small, hope/despair, silence/chaos). Never
hold one tempo; constant loudness goes invisible.

**THE HUMAN LENS.** People move people, not statistics. Anchor every epic event through one
individual; scale-shift constantly (individual → family → city → civilisation). Disaster is
never a number — show consequence. **An abstract/argument block must keep a human foreground
thread — at least one person every few beats — or it hits the mid-video cliff.** The person
is the retention anchor the argument cannot be.

**THE SENTENCE.** Visual narration only — not "many people died" but "a city where even the
birds had stopped singing." One unforgettable trailer line every few paragraphs. Narrate like
a witness, not an encyclopedia.

> **★ PROSODY — non-negotiable, and load-bearing for the timing model.**
> - **Kill the see-saw. Dampen full stops.** Consecutive periods make the voice fall to a
>   terminal pitch again and again. Replace most periods with em-dashes and commas to hold a
>   continuation contour; reserve the full stop for a weighted landing.
> - **Spell every number out.** "Twelve thousand," never "12,000" (digits are fine in a
>   VISUAL line — that's for the image, not the voice).
> - **Write for the breath.** Read each line aloud; if you stumble, the voice will.
> - *Why it belongs to timing:* `calibrate` measures the RENDERED audio. A see-saw script
>   produces terminal falls where you budgeted flow, and the enrichment passes fight you.
>   Note: **em-dashes count as standalone tokens in Python's `.split()`** — they inflate raw
>   word counts; measure with an alnum filter.

**TRUTH / attribution moat.** Prove extraordinary claims immediately; reality is already
extraordinary. **Verify every name and date against a source before it enters narration** — a
fabricated citation in a 24-minute film is a permanent liability. The frame may flirt with the
claim; the narration never asserts it in our own voice. (This is what makes the aggression safe.)

### `phenomenon` (the visual half)

> **★ THE VARIETY LAW — the top visual rule.** No two consecutive beats may share framing,
> angle, scale, or pace — every beat differs from the one before on at least one axis. Rotate
> every axis across the film. Repetition is invisibility. *Motivated, never mechanical:* cut
> wide because the narration widened, not on a timer.

> **★ EVERY BEAT NAMES ITS OWN LIGHT.** The model defaults dark and murky when light is left
> unspecified. The `style_suffix` carries palette only — light **moves to the beat**, where
> content earns it (clear gold dawn · blazing afterglow · bright parting cloud · firelit
> interior). Strip the blanket and skip this and the murk returns by another road. Gate the
> beat table on it.

**COMPOSITION.** Depth always (foreground/midground/background — never one flat plane). A
hero shot every 20–30s (a frame that could be a poster). Angle with intent: eye-level =
honesty (use most) · low = power (kings, giants, angels) · high = vulnerability.

> **⭐ SCALE NEEDS A HUMAN FACE AT THE BOTTOM OF THE FRAME** — the signature move. Spectacle
> reads as *majestic* rather than merely big when one small human witnesses it. Never render
> the fireball/flood/collapse alone. **FALSE FOR THUMBNAILS** — at 120px the dwarfed human
> vanishes; dwarf in the wide, never in the thumbnail.

> **⭐ A SPECTACLE IS A SEQUENCE OF HERO SHOTS, NEVER ONE COMPOSITE FRAME.** Cramming the whole
> miracle into one image always fails (the phenomenon shrinks to a prop). Stage the moment
> across several beats, each a distinct hero frame. A COMPARATIVE sequence (N cultures / N
> examples) is likewise a sequence of monumental hero frames — never an info-graphic, chart,
> or corkboard (that is the Mode-B trap).

> **★ SETTING CONTINUITY — the locked place-phrase.** The canon `{token}` locks WHERE the way
> a face-ref locks WHO. A multi-shot scene rendered as independent stills invents several
> locations. Write the setting once as a locked phrase (terrain, material, features, explicit
> negatives) and let the `{token}` carry it verbatim into every beat; framing varies, identity
> stays fixed. "Biblical" pulls toward "ancient city" — a wilderness scene must positively
> say what IS there.

**RENDER THE REFERENT, NOT THE SYMBOL.** An abstract/argument beat renders its referent as a
monumental physical image (the archetype → a colossal figure over a tiny human), never a chart
or metaphor-prop. No literal-metaphor beats (keys, globes, hearts, scales) — models render
metaphors as corny anachronisms. Write phenomena with real verbs (descends, towers, spreads,
waits); a verbless beat derives no motion.

> **★ NEVER WRITE "no X" IN A `phenomenon`.** The banned-word gate greps the RAW cell text,
> so a beat authored "…monumental, no lectern" trips the very ban it was trying to honour — and
> the image model ignores negatives anyway, often rendering the negated noun. **State the
> positive that fills the space:** "resting on bare dark stone", "held in two hands", "alone in
> a hard shaft". Same law as the canon tokens above, applied to the beat cell. *(Cost the WITW
> grid two mid-render aborts, 21 Jul — the exclusions were authored, then banned.)*

**IF THE OBJECT IS A DOCUMENT, do NOT render the document when the narration names it** (that
is captioning), and do NOT let the model default to scroll/lectern/window furniture. Show what
the book is ABOUT; reserve 1–2 MONUMENTAL hero shots of the object itself (a bound book in a
hard shaft, no stand). Ban the STAGING in `rulebook.json` (no scroll on a table, no lectern,
no quill, no scattered pages) — **never ban "book" itself.**

**DRIFT CONTROL.** One primary motion per beat plus subtle ambient — never everything moving
equally (simultaneous complex motion is the #1 hallucination cause). Lock the subject, move
the camera; the subject moves *less* (let cloth, smoke, dust carry it). Simple beats complex.

**THE CINEMATIC TEST.** Pause on any frame — could it be a still from a $200M feature? The
audience should think "I'm there," never "look at the animation."

### The canon `{token}` — anti-drift place-locks

On **text-to-image** channels a `{token}` is a SETTING place-lock defined once in the project
`canon.json` and expanded inline by `_expand_canon`. **Author the token, define the phrase
once** — never hand-paste the full phrase per beat, never a column (kills 40-cell bloat and
drift). On **reference** channels the token is a character/object plate via `reference_map`
(see REFERENCE MODE).

- **Enforce anti-drift POSITIVELY, never as a negation.** `gate_canon` greps token TEXT for
  banned words and cannot read a negation — and the image model ignores negatives unreliably.
  A supernatural subject (Watchers, Leviathan, the water-woman) gets an anti-glow/anti-vapor
  clause stated positively — **"solid, opaque, massive, hard shadow"** (the Balrog principle:
  render mass and weight, never glow and float). A safety-critical subject (a water-woman) gets
  its modesty stated positively — **"fully and modestly draped in heavy concealing cloth,
  statuesque, austere"** — never via "not sexual".
- **A token that renders generic needs glory-as-SUBSTANCE, and absence via positive fullness.**
  Brightness adjectives alone ("radiant, bright, clean") read as a bright *desert*. Give the
  token specific substance ("everything glowing as if lit from within, white-and-gold light")
  and close out unwanted elements positively ("a shining unbroken ground to a bright horizon"),
  never "no sea" — the model renders the negated noun. *(newearth, 21 Jul: the desert→glory
  flip came entirely from the token, no phenomenon re-authoring — because the token leads every
  beat that uses it.)*
- **A high-frequency spine token (>~20% of beats)** gets a framing-repeat scan: vary the
  SUBJECT within the locked place (a prow, a hand, wreckage, a shoal), never the place — the
  variation is motivated by what the beat reveals, not a new location.

---

## TIMING — VO CONVERGENCE (container-fill to zero drift)

**Model:** ONE continuous whole-film `narration.txt` (not per-block MP3s), rendered by Inworld
in chunks that concatenate freely (pin the same `voiceId`/`modelId`; split only on a block
boundary that was already going to breathe), then measured by whisper + `calibrate` against the
5.000s grid.

**The container is king.** 40 beats × 5.000s = **200.000s per block**, non-negotiable. **Fill
it.** The old model built ~41s of air into every block by design; that air is not breath, it is
Filmora misalignment you then hand-fix, and pauses belong where you place them deliberately
(a `<break>` on a specific hero beat, counted into the 200s), not inherited as trailing
block-slack. **The convergence target is ~0 cumulative drift per block**, minor ±overs/unders
fine (an over trims trivially; an under is silence you place on purpose).

**WPM is emergent, measured, never asserted.** It rises with density (Elliot: ~156 sparse →
~161 dense, measured across the 21 Jul WITW passes). Never author to a WPM constant — render,
run `calibrate`, read the drift. At ~160 WPM a full 200s block is **~530 words** (~13.3
words/beat to fill a 5s slot). Beats may still vary for craft (a hero beat sparse, a dense
neighbour fuller) so long as the BLOCK totals ~530. *(WITW shipped at 13.5 words/beat
measured — see FILM RECORD.)*

**Blocks read at different speeds.** Same word count, different duration: proper nouns,
em-dashes and short clauses slow the TTS (measured 151–171 WPM across WITW blocks). So compute
each block's word-add from **its own measured words-per-second**, never the film average:
`words_to_add(block) = drift_seconds × (block_words ÷ block_duration)`.

**Under-fill is resolved by ENRICHMENT, never padding.** Frozen across passes: beat count,
order, `sentence_id` groups, phenomena, visuals. You improve HOW a beat speaks (fold in
concrete detail from its OWN referent), never WHAT it refers to. It is constrained polish.

**The convergence loop is iterative BY DESIGN — overshoot and multiple passes are the process
working, not failing.** Render is the cheapest leg (pennies); run the loop on rendered truth,
not predicted counts, as many times as the writing keeps improving. A useful shape is three
moves: (1) enrich thin fragments to full lines, (2) enrich to grid-fill words, (3) container-
fill each block to ~0 drift using per-block WPS. Exit when the writing is as good as it gets
AND every block lands on the grid — **not** when a formula says "two passes."

**Inworld hard limit: ≤20 break tags per request** — after the first 20 the rest are SILENTLY
ignored. Count break tags and hard-fail above 20 before render.

**Clip length.** Each clip is trimmed to exactly 120 frames / 5.000s (`-frames:v 120 -c copy`
— a packet copy, not a re-encode; cut at the tail, head keyframe intact). Kling ships 121
frames non-deterministically; the trim normalises it. **Trim never pad** (dropping a frame is
invisible; a freeze-frame isn't). Derive 120 from `r_frame_rate × 5` (a 30fps model would make
120 frames = 4.0s). Ken Burns clips are exactly 5.000s by construction.

---

## THE VISUAL STAGE

### The probe — self-selecting, zero numbering decisions

`build_lego probe [N] --project <slug>` (default N=20). It reads `canon.json`, auto-selects
one beat per token present (doubling the fail-hardest — witness, descent, leviathan, remnant,
deep, codex), spread across blocks, renders the 4-variant grid into `grid-probe/`, and prints
the verdict card. **You type no beat numbers.**

> **The probe FINDS the failure class; the sweep FIXES it film-wide.** The sample caught a
> door-well on ONE beat that lived on EIGHT — fix only the probed beats and you ship the disease
> in the ones it never sampled. The probe is VISUAL-only and runs in parallel with VO
> convergence (it reads `phenomenon`, which enrichment never touches).
>
> Probe cost = beats × ~2.5 × $0.08 (the full 4-variant pick-set per beat, hero 4 / connective
> 2+2 skip), i.e. ~$4 for 20 beats — not beats × $0.08.

**Verdict card** (eyeball before the full grid): witness → draped/austere/statuesque, NOT
sexualised · descent → solid/opaque/hard-shadow, NOT glowing · leviathan → massive/bright-lit,
NOT murk · remnant → giant-vs-tiny-human scale reads · deep → foreground anchor reads against
the depth · codex → monumental book, no scroll/lectern · relief → sharp carved stone, bright.
Spell-breakers: text, watermarks, extra limbs, modern objects.

**Manual probe** (a specific set): `stills beats=1/1,2/3,6/20 --project <slug>` — block/clip
pairs, dashless token (see COMMAND CONTRACT). Also renders into `grid-probe/`.

### The gravity-well sweep (Step 6 — fixes what the probe finds)

- **Two homes for every fix.** What the model renders **unprompted** (gears, galaxies, door
  furniture) → the **rulebook `negative`** (word-removal can't touch what was never in the
  prompt). Wrong **geometry/register** → the **`phenomenon`** or the **`{token}`** text.
  Neither alone is enough.
- **Setting-aware.** Classify every hit by its `{token}` before rewriting, or a blind regex
  wrecks the beats that were right ("light through the opening" is a bug on one token, correct
  on another).
- **Never negative the subject.** Banning "gate"/"opening" makes the model render empty rock.
  Ban the furniture / wrong mechanism / stray astronomy — never the subject itself.
- **A canon-token contradiction is a well.** A beat authoring what its token forbids drifts to
  mush. Fix with a NEW token that permits it + retag those beats — never relax the shared token
  (it leaks to all its beats).

### The variant grid (Step 6 — the pick candidates)

The 4 variants are **4 re-rolls of one prompt**, not four framings — same `phenomenon`, four
fal calls, non-determinism gives four frames of the one composition; pick the cleanest.
Hero = 4 real; connective = 2 real + 2 `_skip.png`. Cost = REAL stills only
(`sum(variants) × $0.08`), visible before you spend. Per-block grid folders are `grid-b<NN>/`,
filenames `{clip:03d}-{variant:02d}.png` (clip-only — unique within a block). Probe folders are
`grid-probe/`, filenames block-PREFIXED `{block:02d}-{clip:03d}-{variant:02d}.png` (clip_index
repeats across blocks and would otherwise collide).

### The pick (Step 7)

100 stills/block → 40 winners. **The pick will never be automated — it is the creative act,
and the real ceiling on how many shots you take.** `place.py` promotes the chosen file to
`shot_NNN.png`; hard-fails on a skip-tile pick, gap, or dupe. **Block-at-a-time is a PICK rule
(visual fatigue over ~800 stills), not a text rule** — enrichment is whole-film in one pass;
the pick is one block per sitting.

**Variant grammar** (proven on Enoch, 400 beats — wildcard 36% the clear winner, mid 20% the
loser): `a` WIDE (phenomenon dominant, human tiny) · `c` TIGHT (reaction, register-matched
anonymous face) · `d1/d2` WILDCARD (authored hero composition). **The mid dies** — `a,c,d1,d2`
replaces `a,b,c,d`. Allocation off `weight`: hero → 4, connective → 2 (~10 hero + ~30
connective = ~100 stills/block). **Anonymous, never faceless** (never lock one face; a
different anonymous face each time reads as *humanity reacting*).

### Air (Step 7) — read off the picked still, not chosen

**Air means literal, visible, suspended matter** — dust, smoke, mist, embers, water, drifting
cloth. Not pace, not narration pauses. `visible` → **KLING** (a frozen dust shaft reads as
wrong before you can say why). `flat` → **KEN BURNS** (a page of Ge'ez, an inscription in
close-up — a slow push is documentary language and correct). The line: *any beat with visible
air is dead as a still.*

### Motion (Step 7) — a function of the shot, not a choice

Motion gives a still a slow living drift so it reads as a shot, not a slideshow — never to add
action (no running, no choreography; that is where AI drift lives).

| move | use when |
|---|---|
| **push** | one overwhelming subject; awe, a face (the default) |
| **pull** | the meaning is scale / consequence / number |
| **crane** | vertical phenomena; descending fire, a towering figure |
| **settle** | reflection, aftermath, grief (an exhale; closes a section) |
| **static** | eerie stillness (hand-placed, sparingly) |

**Derivation ladder (first match wins), read off `phenomenon` + `register` of the PICKED
frame** — drafted by `draft_moves.py`, eye-corrected, never hand-invented per beat:
```
1. quiet register/words (grief, aftermath, ash, empty, still) → settle   (never push)
2. vertical force (rising, column, tower, shaft, ascends)      → crane
3. scale/wide (ranked, vast, receding, to the horizon)         → pull
4. everything else                                             → push
```
`static` is NOT auto-derivable — promote specific held beats by eye. **The phenomenon drives
it; register is the tiebreak.** A flatline (all push) is the §0 blanket signal. Validate the
drafter against an already-shipped film's `move` column before trusting it on a new one.
**Front-load Kling** — the `kling_count` is a contiguous front-N block until per-beat MOTION
control; a viewer who bails at 90s never reaches later beats, so animate the gate.

### The Ken Burns floor (Step 8)

The floor is not a slideshow. `ken_burns_still(move=...)` runs one slow ffmpeg zoompan the full
5s, one move per beat, read off the picked frame exactly like the motion doctrine. Magnitudes
are small (push ~1.16×, pans ~11%) so continuous-across-5s reads as *alive*, not a cliché.
Because the floor is **$0**, iteration is free — render all, eyeball a sample, a bad feel is a
one-number tune + a free re-render. Kling stays available additively: mark a beat `air=kling` +
a `motion` and it upgrades, one beat at a time, only where the retention curve says.

### Reference mode — the `/edit` path (character & object plates)

`channel.json` sets `"render_mode": "reference"` and a `reference_map` of `{token} → plate.png`.
A beat whose `phenomenon` contains a mapped token renders via the fal `/edit` endpoint
conditioned on that plate; token-free beats fall through to text-to-image. **Ref = identity;
text = angle** — the model extrapolates unseen viewpoints from one plate within a render, so
you do NOT need an angle-specific plate per shot; the angle lives in the `phenomenon`, the plate
locks identity. Add a NEW token only for a *surface the ref cannot show*, never for an angle.

- **Multi-ref fragility (quantified):** 1 ref reliable · 2 refs (object+character) works but
  higher refusal + occasional identity softening · **3 refs refuses outright.** Interior/
  character-subject → character ref only, set as TEXT; exterior/object-subject → object ref
  alone. Never stack three.
- **Refusals are per-CALL, not per-BEAT** — a hero beat re-rolls 4 calls; a refused slot
  silently falls back to flux (ignores BOTH the ref and the unbranded canon → off-model faces
  and re-introduced logos). Every flux-fallback frame gets a logo/identity QA pass; don't pick
  it if a clean `/edit` variant exists. Resume-safe: re-run to refill refused slots.
- **Opaque where a face must not appear** ("opaque, fully reflective, no face visible") — also
  the rights-safe default for an anonymous figure.
- **The growing-library moat.** Promote your own best outputs into new reference plates —
  identity tightens across a film; same compounding-asset logic as the CSV.

---

## CONFIG — the JSON contract (never code)

| file | holds | read by |
|---|---|---|
| **`<channel>/channel.json`** | `style_suffix`/grade (**palette only** — no light/shafts/shadow; those are per-beat content), `voice_id`, `image_model`, aspect, `ken_burns` flag, `render_mode`, `reference_map`, optional `base_canon`, `tts_provider` | resolved from the OUTPUT PATH by every render func |
| **`<channel>/projects/<slug>/canon.json`** | the per-film `{token}` DEFINITIONS (flat `{token: phrase}`) — the anti-drift place-locks | `load_config` (merged OVER channel `base_canon`, **project wins**), `_expand_canon`, `gate_canon` |
| **`<channel>/rulebook.json`** (+ universal `shared/rulebook.json`) | `negative` spell-breakers (kills what renders UNPROMPTED). Two-layer, CWD-scoped: edit channel negatives from the channel dir | merged into every prompt by the render funcs |

> **Canon lives in the PROJECT, layered over the channel.** `build_lego`'s `load_config`
> loads `<project>/canon.json` and merges the channel `base_canon` underneath (project wins on
> collision). Without this the token expansion is a silent no-op and every `{token}` renders
> literally or aborts the gate — verify `len(cfg["canon"])` before any spend on a new project.

> **Project structure.** One folder = one final video (its whole life: master CSV, canon, VO,
> grid stills, picks, clips, thumbnail). Render outputs are SUBFOLDERS, never siblings. The
> folder is born from the ready-to-build master CSV or the Step-0 thumbnail, never grown per
> block. Per-block CSVs are chat-only drafts (Step 2).

---

## COMMAND CONTRACT — build_lego and the dumb readers

**`build_lego.py`** (channel-agnostic; `build_moon.py` and the `build_beats` alias are RETIRED).
Verbs: `normalise` · `sweep` · `film` · `blocks` · `stills` · `probe` · `clips` · `audio` ·
`calibrate`. Master CSV at `projects/<slug>/master.csv`.

**Invocation form:** `build_lego.py <verb> <rest...> --project <slug>`. Argument order no longer
matters — the top-level parser uses `parse_known_args` and folds extras into `rest`, so
`probe 20 --project P` and `probe --project P 20` both work. (Historically the parser was
order-sensitive and rejected trailing positionals; that is fixed. Per-verb options are dashless
`key=value` positionals, e.g. `beats=1/1,2/3` — a `--flag` gets eaten by the top-level parser.)

- **`probe [N]`** — self-selecting register sample → `grid-probe/` + verdict card (above).
- **`stills [BLOCK...]`** — whole block(s) → `grid-b<NN>/` (unprefixed filenames; pick/place
  reads these). **`stills beats=b/c,…`** — a manual cross-film sample → `grid-probe/`
  (block-prefixed filenames). The per-block structural gate runs on block mode and is skipped
  in probe mode (cross-film clip_index repeats would false-trip it). **`stills` PRE-GATES every
  wanted block before rendering any of them** — a gate failure prints the complete list across
  the whole film and exits with nothing spent, so a full-grid run is safe to leave unattended.
  The run ends with a completion summary and flags any sub-8KB frame (a fal safety reject).
- **`audio`** — emit whole-film `narration.txt`, render Inworld VO (chunked), whisper →
  `voiceover.json`.
- **`calibrate <voiceover.json>`** — per-block cumulative drift vs the 200s grid.
- **`normalise`** fills derived columns; **`sweep`** audits; **`blocks`**/**`film`** operate
  per-block / whole-film.
- **Avoid the `clips` verb inside build_lego for real clips** unless verified — the documented
  clips leg is `render_clips.py` (reads `air`/`move`/`motion`; `--floor-only`, `--dry-run`).

**The other readers:** `place.py` (winners folder/list → `shot_NNN.png`; hard-fails on
skip-tile/gap/dupe) · `render_clips.py` (Kling(`motion`) if `air`, else `ken_burns_still(move)`)
· `draft_moves.py` (`--csv`, `--dry-run`, `--validate` against a shipped film).

---

## ENGINE FACTS & GOTCHAS (do not re-learn the hard way)

- **Render funcs anchor config on the OUTPUT PATH, not CWD** — write into the channel's project
  tree and grade + `style_suffix` + negatives attach automatically. This is what lets the
  standalone renderers work with zero engine changes.
- **`load_config` resolves the channel by walking UP from the project dir** — `--project` is a
  bare slug only when you run from the channel dir (`~/Pipeline/<channel>`, which has `projects/`).
- **`safety_tolerance:"5"` is required on fal Flux** — the default silently returns ~7KB black
  PNG placeholders on rejection. Gate the first grid frames >7KB.
- **`image_model: nano_banana_2` must be explicit in `channel.json`** — the module default is
  `flux` (the murk styliser).
- **The rulebook is two-layer, CWD-scoped** — channel dir → `<channel>/rulebook.json`; repo
  root → universal `shared/rulebook.json`. Edit channel negatives from the channel dir.
- **`gate_canon` greps token TEXT for banned words and can't read a negation** — never put a
  banned word (even "no galaxy") inside a canon token; ban it in the rulebook.
- **The engine won't import on the laptop** (no dotenv/venv) — anything importing
  `recreation_pipeline` runs on the box; laptop-side edits to engine-owned data are pure-stdlib
  patches. `build_lego` is box-only for the same reason.
- **The skip-tile is channel-agnostic** — `shared/_skip.png` for all channels; a channel may
  override with `characters/_skip.png` (resolve shared first).
- **Machine work batches; human work chunks.** The block boundary buys nothing at render time —
  it exists to protect your eye at the pick.

---

## WORKFLOW & PATCH DISCIPLINE

**All code and config flows laptop → GitHub → box; never hand-edit on the box.** Edit on
LAPTOP → commit → `git pull --no-edit` on box → verify. Assets (media) move by rsync/scp and are
gitignored; code is GitHub-only. Stage explicit named paths — never `git add -A` (it can sweep
large media). BOX uses `python` in the venv; LAPTOP uses `python3`.

**Patches are idempotent `patch_*.py`:** verify the anchor before writing, `.pre_*` backup once,
`py_compile` the patched source before touching the target, ASCII-only, print applied/skip per
edit. Config changes go via a `python3 -c` JSON one-liner or a JSON-key overwrite (parse → set
→ dump), never a string-anchor on a data file.

- **Idempotency markers must be unique to the NEW code** — a marker that is also a substring of
  a prior version false-skips and half-heals a re-patch.
- **For a code file that may be partially patched** (laptop/box drift mid-session), prefer a
  surgical `str_replace` against the verbatim CURRENT text, or **reset from the `.pre_` backup
  to pristine and apply once**, over accumulating escaped alternate anchors. Escaping (`\n` vs
  `\\n`) breaks anchor matching across the patch-writes-code boundary.
- **A tool that makes the operator choose structural numbers is a design smell** — push the
  operation into a self-selecting verb (like `probe`) and capture the invariant in this
  COMMAND CONTRACT, not in chat. "Feels like from-scratch every session" is the signature of a
  rule that lives only in conversation. Fix it in code.

---

## SCOPE

### Mode overrides — distribution vs festival (name the mode; never silently reinterpret)

| rule | DISTRIBUTION (browse/feed) | FESTIVAL (jury, watched end-to-end) |
|---|---|---|
| Ken Burns on flat beats | craft (invisible, free) | **OFF** — a pan on a still reads as "couldn't animate" |
| retention cold-open / front-load | required (the click decides) | **OFF** — spends best shots up front |
| advertiser hedge / subscribe beat | present | **OFF** |

The festival cut and the channel-launch cut of the same film may be different edits — decide up
front whether they are one file or a re-edit.

### What LEGO is NOT for

- **Audio-first channels (Sacred Soak).** The audit flags a register flatline as failure; a
  sleep/meditation read *wants* the flatline. Audio-first is a different product (visuals-as-
  wallpaper).
- **Stock-footage channels (Success Coach).** LEGO assumes you *author* the image; stock
  channels *select* licensed clips — no canon, no render. The NARRATION half (whole-film VO +
  calibrate) transfers; the visual half is a different pipeline.
- **True multi-character dialogue.** The VO model is ONE continuous narrator. Two characters in
  dialogue break the single-call model. Bentley dodges it (Watson silent); Synthetic Press's
  dual-mode drama will hit it. Unsolved.

Browse/evergreen channels (Woodworking) use LEGO's *machinery* (CSV, calibrate, variety, data
surface) but NOT its narrative craft (spine, escalation) — the pipeline and the storytelling
doctrine are separable; apply only what fits.

---

## STORY ARC — THE UNSOLVED MEASURE (build the instrument, then the rubric)

**The gap, stated plainly.** The CSV measures *structure* — register distribution, word
density, hero/connective balance, token mix, escalation-countable-every-4-8-rows. A film is
judged on something else: the **arc it produces in the viewer** — does tension rise, does a
question stay open, does the viewer lean forward at minute fourteen. Nothing in this pipeline
currently measures or designs for that. Structural counts are proxies, and the audit that reads
them **flattens the time axis** (see GOVERNING LAW) — a perfect distribution can still be a
flat film.

This section is a **named open problem**, not a solved spec. It is written down so the next
films test it rather than re-discover it.

### It must eventually be BOTH

| mode | what it is | when |
|---|---|---|
| **post-hoc instrument** | score a finished `master.csv`, join the shipped retention curve onto the beat rows, learn which measures predict where viewers actually left | **build first** — you cannot validate a rubric you have never correlated against real retention |
| **authoring rubric** | score the arc at Step 2–3 and gate on it, the way the variety law is gated today | **graduates from the instrument** — a measure is promoted to a gate only once it has predicted a real drop |

### The ground truth is exact, and that is the unlock

Because the container is arithmetic (40 beats × 5.000s = 200.000s, block N starts at
(N−1)×200), **a retention timestamp maps onto a beat row with no estimation**: beat *i* of the
film spans `(i−1)×5.000` to `i×5.000` seconds. YouTube's retention curve can be joined directly
onto the CSV. **The row where viewers leave becomes the next film's training signal.** No other
part of this pipeline gets ground truth that clean — use it.

### Candidate measures (sequence-aware, not distributional)

All of these are computable from the existing master CSV. None is yet proven to predict
retention — that is exactly what the instrument is for.

- **Escalation delta, block over block.** Does at least one of scale / danger / mystery /
  consequence / emotion / urgency / human-cost increase from block N to N+1? A film that
  plateaus in the middle should show it here. *(The craft law already demands this; nothing
  measures it.)*
- **Open-loop count at each beat.** How many questions are live and unanswered. The curiosity
  engine says the stack never empties — this counts it. Would need an authored column
  (`opens` / `closes`); **unbuilt, and the only candidate that costs new authoring**.
- **Longest human-absent run.** Consecutive beats with no person in `phenomenon`. The known
  mid-video cliff on argument blocks is a human-absence failure — this is its early warning.
- **Longest single-token run.** Consecutive beats sharing one `setting` token — same-place
  monotony that a per-beat variety gate misses entirely.
- **Register trajectory, not register mix.** The *sequence* of registers, read as a curve;
  a flatline over several blocks is viewer fatigue even when the distribution looks healthy.
- **Hero-beat spacing.** Gap between hero beats vs. the 20–30s doctrine — measured in rows.

### The protocol

1. Score every shipped film's `master.csv` on the candidates above (cheap, pure-stdlib, no spend).
2. When day-14/21 retention lands, join the curve onto the beat rows and record it in FILM RECORD.
3. Correlate: at the beats where viewers actually left, which measures were already flashing red?
4. **Promote what predicts; drop what does not.** A measure that survives two or three films
   graduates from instrument to authoring rubric and gets a gate at Step 3.

> **Do not gate on any of these yet.** Gating on an unvalidated proxy is exactly the blanket
> the GOVERNING LAW warns about — it would enforce a shape no evidence supports.

---

## FUTURE

- **The story-arc instrument, then the rubric** — see STORY ARC above. Nearest build: score a
  shipped `master.csv` on the sequence-aware candidates and join the retention curve onto the
  beat rows.
- **`{token:label}` per-beat reference selector** — pick a specific library member per beat
  (documented next-build in `build_lego`).
- **`make_shorts.py`** — cuts from `final_video.mp4`, square-centre-blur vertical.
- **Parallel fal animation** — bounded concurrency (~5–10 semaphore) cuts animation time ~5–8×.

---

## CHANGELOG — what this rewrite superseded (history preserved)

*21 Jul 2026 — full consolidation after running WITW (Sacred Dawn, 8 blocks / 320 beats)
end-to-end as the live test of this doc.*

- **Air-by-design → container-fill.** The old Block spec (~380 words/block @ 143 WPM, ~41s air)
  is retired. Blocks now fill to ~0 cumulative drift (~530 words @ measured ~160 WPM); breath is
  placed deliberately, not inherited as block-slack. *(Reverses the earlier "~15–20% air suits
  the register" position — air is Filmora misalignment, not breath.)*
- **WPM reconciled to measured/emergent.** The 143 and 159 constants are gone; Elliot measures
  ~156–161 (density-dependent). Compute per-block word-adds from each block's own measured WPS,
  never the film average.
- **The probe is one self-selecting verb.** The `probe20`/flat-index/`--flag`/block-clip
  ordering saga is gone: `probe [N]` picks its own register spread; `parse_known_args` makes
  argument order irrelevant; probe filenames are block-prefixed (no cross-film collision);
  probe cost is beats × ~2.5 × $0.08.
- **Canon lives in the project, layered over the channel** (`load_config` merges project
  `canon.json` over `base_canon`, project wins). The "canon in channel.json" references are
  retired.
- **Token glory-as-substance + positive fullness** folded into the canon craft (the newearth
  desert→glory flip).
- **Deleted:** the QUICK-START override-by-decree layer, the TEST-RUN FINDINGS (G1–G21) and
  REWRITE-BRIEF (G22) to-do layers (folded into the body), the LEDGER ADDITIONS block, the
  PHASE 0–12 pathway, and the legacy `finish`/`storyboard.json`/`mission-control` pipeline
  mapping (that is the older recreation-pipeline path, not the current `build_lego` path).
- **The pick is a filename, never a `picked_variant` column** (settled the duplicate beat-table).
- **Note:** `shared/docs/_Sacred-Dawn.md` may still carry a stale 143-WPM / god-ray-in-suffix
  line — fix at that file, out of scope here.

*Prior milestones: proven end-to-end on Sacred Dawn / Book of Enoch (30 min, 15 Jul 2026);
timing model rebuilt and measured 17 Jul; authoring contract absorbed from `_SCRIPT-CONTRACT.md`
17 Jul (genre overlays scrubbed — they carried the pre-pivot Final Hours register).*

---

## FILM RECORD — shipped films, facts and figures

One block per completed film. Authoring/production figures are filled at ship; the distribution
figures are filled when the data lands (48h, then day 14/21). The point is **comparison across
films** — the questions no single film can answer (does higher word density help or hurt
retention? does a heavier Kling count pay? does a tighter arc score predict a flatter curve?).
Add STORY ARC scores here as the instrument comes online.

### 1 — *The Daughters of the Watchers — the Mystery Every Ocean Kept*
**Sacred Dawn · shipped: (pending) · project `women-in-the-water`**

| | |
|---|---|
| structure | 8 blocks · 320 beats · ~26.7 min |
| narration | **4,318 words · 13.5 words/beat** |
| voice | Elliot (Inworld) · **161 WPM measured** |
| VO passes | 3 — 2,734 w (156 WPM) → 3,464 w (158) → 4,318 w (161) |
| drift at lock | b1 +5.3 · b2 −2.4 · b3 +5.7 · b4 −12.3 · b5 +0.3 · b6 +5.5 · b7 −15.1 · b8 +19.4 (seconds, per block) |
| canon | 12 tokens (project `canon.json`) |
| probe | 20 beats / 62 real stills / ~$5 |
| grid | ~800 real stills / ~$71 |
| clips | (pending — floor + additive Kling) |
| **CTR @48h** | *(pending)* |
| **AVD @48h** | *(pending)* |
| **AVD day-14 / day-21** | *(pending)* |
| traffic mix @day-14 | *(pending)* |
| arc scores | *(pending — see STORY ARC)* |

**Notes.** First film authored under **container-fill** (blocks filled to ~0 drift rather than
carrying ~20% air) — 13.5 w/beat against the ~13.3 predicted by 161 WPM on a 5.000s slot, so
the model held. Six of eight blocks landed within ±6s; b7 (−15s) and b8 (+19s) were accepted
rather than chasing a fourth pass. First film to use the self-selecting `probe` verb and the
project-`canon.json` load. `{newearth}` initially rendered as bright desert and was fixed at
the **token** (glory-as-substance + positive fullness), not by re-authoring phenomena.
