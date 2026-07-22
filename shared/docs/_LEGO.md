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
project:       <channel>/projects/<slug>/{package.md, architecture.md, master.csv, canon.json,
                                            narration.txt, voiceover.mp3, voiceover.json,
                                            coldopen.txt, coldopen.mp3, thumbnail.png, observations.md}
               (there is NO blocks/ folder — see Step 2)
grid stills:   <channel>/projects/<slug>/grid/{flat:03d}-{variant:02d}.png   <- ALL beats, ONE folder
probe stills:  <channel>/projects/<slug>/grid-probe/{flat:03d}-{variant:02d}.png
winners:       <channel>/projects/<slug>/winners/{flat:03d}-{variant:02d}.png (the picks, names unchanged)
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

## THE PROCESS — 0 to 10 (this leads; everything hangs off it)

Run in order. Three orderings are load-bearing and cost money if broken: **package first**
(the click decides whether the film is watched), **VO before stills** (measure the cheap
layer, preserve the expensive one), **motion after the pick** (motion is read off a picked
frame). Golden thread: *truth costs nothing — buy it repeatedly; gate before every spend;
observe → bank → feed the next film.*

| # | STEP | program(s) | gate | output |
|---|---|---|---|---|
| **0** | **PACKAGE FIRST** — topic for the CLICK; winnability gate (demand exists AND a small channel broke this lane); commit title + **render the thumbnail FILE, not a concept**; squint-test it at 120px beside the lane leader's tile. Title must obey the channel's attribution rule (an *asserting* title breaks the moat). Flag topic-level render-safety (family-safe/YPP). Un-packageable → **kill here, $0.** | human + NexLev + image gen | **`package.md` EXISTS on disk** — title, thumbnail findings, both winnability verdicts *with their evidence*, render-safety table, truth ledger, metadata | **`<project>/package.md` + `thumbnail.png`** |
| **1** | **ARCHITECT** — runtime → N×200s blocks (200s = the seam unit); per block define its curiosity-gap + HANDOFF to the next; map the spine (cold open → escalation → turn → payoff); **name the SPINE OBJECT and the ANTAGONIST**; **name the canon tokens**; carry a **dated chronology column** if the film has one. ~3,000–3,600 words ≈ 8 blocks. | human | **`architecture.md` EXISTS on disk**; every block has role + gap + handoff + tokens + date; the spine object escalates; the antagonist is named and placed | **`<project>/architecture.md`** |
| **2** | **AUTHOR BLOCK BY BLOCK** — per beat write `phenomenon` + `narration` under the craft law; canon `{token}` on every beat; weight hero/connective; build variety across every axis. Each 40-beat block is a mini-spine (open its question, build, turn, close on the handoff). **Blocks are drafted in CHAT; there are NO per-block CSV files and no `blocks/` folder** — append straight into `master.csv`. | human authoring | **GATE each block**: VISUAL present, ≤55 words (runaway backstop), tokens resolve, no banned words, register/setting sweep. The block gate is a *drafting* check, never the film's gate | rows appended to `master.csv` |
| **3** | **INTERROGATE THE MASTER** — `normalise` fills derived columns; read the film AS DATA (setting mix, register spread, hero/connective balance, word histogram, token×block heatmap, framing-repeat scan on any token >~20% of beats). Adjust. **The project folder was born at Step 0.** | `build_lego normalise`, `sweep` | **RE-GATE THE WHOLE FILM, not N blocks again** — row count, `clip_index` 1..40 per block, hero count per block, no negation in any `phenomenon`, no token in any `narration`, every token defined in `canon.json`. *Per-block passes miss what only the film sees* | gated master CSV + variety audit |
| **4** | **VO CONVERGENCE** — emit ONE whole-film `narration.txt`; render VO (Inworld); whisper; `calibrate` → per-block cumulative drift vs the 200s grid; enrich the CSV to fill toward the grid (see TIMING). | `build_lego audio`, `calibrate` + Inworld + Whisper | — | `voiceover.mp3` rendered, seams measured |
| **5** | **REPEAT 4** until every block lands **~0 cumulative drift** (minor ±overs/unders fine). **VO LOCKED** (output #2). | as Step 4 | every seam near its 200s mark | **VO locked** |
| **6** | **PROBE, THEN THE GRID** — `probe [N]` (self-selecting register sample); read vs the verdict card → name the FAILURE CLASS; **sweep the master film-wide, setting-aware** (two homes: rulebook negatives + `phenomenon`/token geometry); re-probe until clean; THEN `stills` (all blocks) → the variant grid. | `build_lego probe`, `stills`; rulebook / canon / `phenomenon` edits | probe reads clean; first grid frames >7KB (not black rejects) | grid stills |
| **7** | **PICK + AIR + MOVE + MOTION** — hand-pick ONE variant per beat into `winners/`; `place` them into `shot_NNN.png`; `draft_moves` fills `move`; `draft_air` fills `air`+`motion` (sliding quota × motion-want rank × score floor); eye-correct both against the picked frames. | `place.py`; `draft_moves.py`; `draft_air.py` | place = N files, no gaps/dupes/skip-tiles; BOTH drafters `--dry-run` first (a move flatline or a wrong Kling split is free to fix, expensive to render); a Kling beat with no `motion` aborts | placed stills + routing plan |
| **8** | **RENDER CLIPS + GATE THEM** — per beat: `air`=Kling → `animate_still(motion)`, else → `ken_burns_still(move)` (the doctrine-varied free floor). Then ffprobe EVERY output. | `render_clips.py` (`--floor-only`, `--dry-run`); `verify_clips.py` | `--dry-run` shows split + cost before spend; then **`verify_clips.py --expect N --normalise` must PASS — every clip exactly 5.000s** | **`clips/shot_NNN.mp4`** (output #1) |
| **9** | **CUT THE COLD OPEN** — 45–55s in front of block 1. Its own `coldopen.txt`, its own Inworld render at the identical voice and speed, its own clips pulled from ONE already-picked moment. **Not a trailer** (see COLD OPEN below). | human + `build_lego audio` | the seam check: read the last cold-open line and block 1 beat 1 aloud back to back — if you hear a full stop between them, it is not finished | `coldopen.mp3` + its clip list |
| **10** | **ASSEMBLE + SHIP + OBSERVE** — clips + locked VO + cold open in Filmora (music, seam swells, title); export; upload. Read CTR+AVD @48h and the day-14/21 retention curve; **join the curve onto the beat rows** and write it up; **bank every failure as portable law**; feed it back to Step 0 of the next film. | Filmora (human); the retention-join script | **`observations.md` EXISTS on disk** and the FILM RECORD row is filled — a film with no written observation taught the next one nothing | shipped video → observations → next film |

> **The output boundary.** The pipeline ends at Step 8: clips + VO. Everything after is
> Filmora and packaging. The pipeline's whole job is to hand Filmora N×40 clips in beat order
> and one narration track, gated and correct. **The cold open (Step 9) is the one exception** —
> it is a separately authored, separately rendered artifact that never enters `master.csv`, which
> is also why it is the only place breath may be hand-placed without contaminating the repeatable
> path.

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
- **One number runs the whole visual chain: the FLAT FILM INDEX (CSV row order, 1..N).** Grid
  and probe stills are named `{flat}-{variant}.png`, `place.py` parses that flat beat out of the
  filename, and `render_clips.py` enumerates the same rows for `shot_{i:03d}`. Never name a
  still by `clip_index` (it repeats in every block) and never block-prefix it (`place.py`'s
  regex rejects a second dash).
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

> **★ THE SPINE OBJECT — one physical thing carries the film.** Not a theme, not an idea: a
> THING that can be photographed, tended, threatened and finally lost. It appears in the first
> block, recurs in most of them, and its destruction or completion IS the climax. This is what
> converts an abstraction ("God's patience", "the cost of exile") into something the camera can
> hold. *Selection rule: prefer an object that ESCALATES VISUALLY.* A fire looks identical at year
> one hundred and year nine hundred; a field of one stone per year does not — and becomes the
> film's escalation meter, readable by the audience without narration. **The competitor film that
> beat us in this lane is one prop from end to end** (a watch-fire, put out by a single raindrop);
> so is Methuselah (nine hundred and sixty-nine laid stones, drowned).

> **★ THE REFRAIN.** One line, repeated three or four times across the film, meaning something
> different each time because the circumstances moved underneath it. Costs nothing, and it is what
> makes a long film feel composed rather than accumulated. Works on a NUMBER as readily as a line
> (*two hundred*, *nine hundred and sixty-nine*). Place them deliberately at Step 1, not by
> accident at Step 2.

> **★ NAME THE ANTAGONIST — "the world" is not one.** A diffuse villain produces a diffuse middle,
> and the middle is where films die. Step 1 must answer: *who opposes this by name, and in which
> blocks does he appear?* Prefer someone the source already names — an invented antagonist costs
> attribution, a named one is free and defensible. The competitor's film has no antagonist and
> sags for twelve unbroken minutes; that is not a coincidence, it is the same finding from the
> other side.

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
- **A NON-LEADING token is an identity lock.** `setting` derives from the LEADING `{token}`, so a
  token placed mid-cell rides along without corrupting the derivation. Lead with the place, put the
  character inline: `{firsthome} wide, {firstman} sitting motionless on a broad flat stone…`. This
  is the cheap alternative to reference mode for a character confined to one block — a plate is
  overkill for nine beats, and the phrase locks identity the same way.
- **RE-MINT A TOKEN WHEN THE SAME PLACE CHANGES OVER TIME.** A bare summit in block 1 and the same
  summit covered in hundreds of laid stones in block 8 are materially different locations, and one
  token cannot hold both without going to mush. Mint a second (`{highstone}` → `{stonefield}`) and
  retag — the canon-contradiction rule applies to TIME as well as content. On any film spanning
  decades or centuries this is the normal case, not the exception, and the pair is also where the
  spine object's escalation becomes visible.
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

> **WPM IS NOT A RETENTION LEVER — settled 22 Jul, do not re-litigate.** A competitor film that
> did 698K views in eleven days runs 102 WPM against Elliot's measured ~160, which looks like an
> argument for slowing down. It is not. Sacred Dawn's own curves show dense narration costs nothing
> after the open: *Forbidden Books* holds 35%→13% across ninety percent of its runtime at 161 WPM,
> with relative retention 0.70–0.75 mid-film. Inferring a pacing rule from a competitor's
> PRODUCTION figure with no retention curve attached fails the two-signals rule. **Author at
> measured WPM under container-fill.** Breath belongs in the cold open, which is hand-assembled
> anyway. Revisit only if a curve shows mid-film decay correlating with word density.

> **BANKED, NOT BUILT — silence is assembled, never spoken.** No TTS gives a reliable pause
> instruction, so stop asking for one. Make `sentence_id` the TTS RENDER UNIT — one call per group,
> N files back — then concatenate with ffmpeg-generated silence at exact durations. Because the
> container is arithmetic the gap is *subtracted, not estimated*: a group spanning beats 12–14 owns
> 15.000s; render it at 12.4s and the gap is 2.6s. **Cumulative drift would be zero on the first
> pass, always**, which collapses Steps 4–5 entirely and turns `calibrate` into a verifier that
> should print zeros. Two columns: `pause_after` (authored override) and `pause_mode`
> (`grid` | `tight`). Free consequences: hash-cache each group so an enrichment pass re-renders
> thirty utterances rather than the film; and emit `timing.json` (utterance boundaries, gap
> positions, block seams in absolute seconds) as a music cue sheet and a direct feed to the
> retention join. Two hazards: separate calls break prosodic continuity, so group 2–4 sentences
> where the voice must run on; and uniform auto-fill is the §0 blanket, so expect roughly half of
> groups to run `tight`. **Build it when a measurement demands it, never for taste.**

**Inworld hard limit: ≤20 break tags per request** — after the first 20 the rest are SILENTLY
ignored. Count break tags and hard-fail above 20 before render.

**Clip length.** Each clip is trimmed to exactly 120 frames / 5.000s (`-frames:v 120 -c copy`
— a packet copy, not a re-encode; cut at the tail, head keyframe intact). Kling ships 121
frames non-deterministically; the trim normalises it. **Trim never pad** (dropping a frame is
invisible; a freeze-frame isn't). Derive 120 from `r_frame_rate × 5` (a 30fps model would make
120 frames = 4.0s). Ken Burns clips are exactly 5.000s by construction.

---

## THE COLD OPEN — the highest-leverage sixty seconds in the film

> **★ IT IS NOT A TRAILER, AND THE TRAILER VERSION IS MEASURABLY COSTING RETENTION.**
> A trailer is a compression of the whole film. It has its own arc — it builds, peaks, and ENDS.
> When it ends the viewer has completed something, and the film then has to start over. **That
> restart is the seam, and the seam is where the audience leaves.**

**The evidence, two Sacred Dawn films, both curves:**

| film | open | collapse |
|---|---|---|
| *Forbidden Books* (76:10) | 93.5% at 46s | **60.7% at 91s** |
| *200 Taught Us* (37:30) | 97.8% at 22s | **54.8% at 45s → 35.9% at 67s** |

YouTube's own `relativeRetentionPerformance` in that window is **0.22–0.36 — bottom decile** —
against **0.58–0.75 mid-film** on the same videos. The middle of those films is above median. The
first minute is not. **The collapse lands where the cold open ENDS**, which means it is not failing
to hook; it is failing to *transfer*.

A trailer also breaks the curiosity engine at the root: it INFORMS. A viewer who has been shown a
survey of all eight blocks has been told what the film is — the one thing that should stay
unresolved for the whole runtime.

**The spec — 45–55s, ~10 clips, ~145 words at measured WPM.** Not 90; ninety seconds of anything in
front of a film is a trailer by duration alone.

| window | move |
|---|---|
| **0:00–0:08** | **THE DROP.** Open inside the film's most extreme moment, already in progress. No establishing shot, no "long ago". Hard cut in on the loudest frame you own. |
| **0:08–0:20** | **THE NAME.** One sentence of coordinates. Deliver the title's noun here so the viewer knows within twenty seconds they are in the right video. Attribution lands here. |
| **0:20–0:40** | **THE QUESTION.** Widen. Ask the one question the film exists to answer — larger than the moment just shown, and it must stay open for the whole runtime. |
| **0:40–0:55** | **THE HANDOFF.** No summary, no "in this film". One sentence that grammatically REQUIRES block 1 beat 1. Cut mid-momentum. |

**Sourcing.** Pull from ONE moment — six to eight already-picked clips that belong to a single
event, plus two or three elsewhere for the widen. **Never a survey of the best shot of every block**
(that is the trailer error restated as a sourcing rule), and never the film's final payoff shot.
Choose the moment by whether a stranger seeing one frame would ask a question — and it must be the
thing the THUMBNAIL promised. If the thumbnail sells an image the first twenty seconds do not
deliver, the promise breaks on arrival and no craft downstream recovers it.

> **★ THE SEAM IS THE REPAIR, NOT THE HOOK.** A broken seam has three things terminating at the
> same instant: the narration sentence lands, the music phrase resolves, the visual register
> changes. Three simultaneous endings mean one film ended and a different one began. Break the
> simultaneity:
> - **No silence at the cut.** Cold-open VO ends 1.5–2s BEFORE the visual cut; block 1's first
>   line starts on the cut or under the last cold-open frame. Silence at a seam is an exit ramp.
> - **Carry the music across.** One continuous bed from 0:00 through at least 2:00, unresolved
>   under the handoff. No crossfade, no new track at the cut. Cheapest item on this list and
>   probably the highest-yield.
> - **Never fade to black at that cut.**
> - **Match on movement.** Last cold-open clip and first block-1 clip share a motion direction, so
>   the cut reads as one continuous camera.

**Voice.** Pin the identical `voiceId`, `modelId` and speed as the body — a timbre shift at the
seam tells the viewer a different film just started. Render, whisper it, confirm 53–57s before
committing. Prosody law applies harder here than anywhere: a terminal pitch fall on the last
cold-open sentence is the exact acoustic signal for *this has ended*.

**The gate — three free checks.** Could a stranger summarise the film from it? Then it is a trailer;
cut it back. Does it ANSWER anything? Remove the answer. Read the last cold-open line and block 1
beat 1 aloud, back to back — if you hear a full stop between them, the seam is still there.

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
(`sum(variants) × $0.08`), visible before you spend.

> **★ ONE GRID FOLDER, FLAT-INDEX FILENAMES.** Every still of the film lands in a single
> `grid/` folder named `{flat:03d}-{variant:02d}.png`, where **flat is the FILM INDEX 1..N**.
> The folder therefore sorts in exact beat order — you scroll the film start to finish. The
> probe folder uses the same names. Three reasons this is the ONE naming law:
> - **Unique by construction.** `{clip}-{variant}` repeats in every block, so the winners
>   collide the moment they share a folder — a silent overwrite that loses most of the picks.
> - **`place.py`-compatible.** It parses `^(\d{1,4})-(\d+)\.png$` and reads group 1 as the flat
>   beat; a block-prefixed name (`06-019-03.png`) fails that regex outright.
> - **Agrees with `render_clips.py`**, which enumerates CSV rows for `shot_{i:03d}`.
>
> **FLAT IS CSV ROW ORDER, never `(block−1)×40+clip`.** The formula agrees only while every
> block holds exactly 40 rows; one short block would silently misalign every beat after it —
> which you would meet as narration over the wrong image at assembly. `_flat_map()` reads the
> master and enumerates. `consolidate_grid.py` migrates an older per-block layout (`grid-bNN/`)
> into the flat folder — a rename, no re-render, dry-run by default.

### The pick (Step 7)

~4 stills per beat → ONE winner each (≈1,280 → 320 on an 8-block film). **The pick will never be
automated — it is the creative act, and the real ceiling on how many shots you take.**

Review the whole `grid/` folder sorted by name: flat-index names put it in exact beat order, so
you scroll the film in sequence and stop wherever. Copy ONE winner per beat into `winners/`
(filenames unchanged — they are already unique), then place them:

    python3 place.py --winners <project>/winners --out <project>/stills \
                     --skip-tile shared/_skip.png

`place.py` parses the flat beat from each filename and writes `shot_{beat:03d}.png`. It
hard-fails — placing NOTHING — on a skip-tile pick, a doubled beat, or any gap in 1..N, so it
names exactly what to re-pick rather than half-placing. **Pace the pick across sittings (visual
fatigue over ~1,000 stills is real), but that is a PACING rule, not a folder rule** —
enrichment is whole-film in one pass, and so is the grid.

**Variant grammar** (proven on Enoch, 400 beats — wildcard 36% the clear winner, mid 20% the
loser): `a` WIDE (phenomenon dominant, human tiny) · `c` TIGHT (reaction, register-matched
anonymous face) · `d1/d2` WILDCARD (authored hero composition). **The mid dies** — `a,c,d1,d2`
replaces `a,b,c,d`. Allocation off `weight`: hero → 4, connective → 2 (~10 hero + ~30
connective = ~100 stills/block). **Anonymous, never faceless** (never lock one face; a
different anonymous face each time reads as *humanity reacting*).

### Air + Kling (Step 7) — the spend dial

**Air means literal, visible, suspended matter** — dust, smoke, mist, embers, **water**,
drifting cloth. Not pace, not narration pauses. The line: *any beat with visible air is dead as
a still* — a frozen dust shaft or a motionless sea reads as wrong before you can say why. A
genuinely flat beat (a page of Ge'ez, an inscription in close-up) is CORRECT on the free floor;
a slow push is documentary language.

> **★ THE AIR VOCABULARY MUST MATCH THE FILM'S MEDIUM.** An earlier drafter's air nouns were
> dust / smoke / cloud / ash with **no water at all** — so a deep-sea film scored ZERO from
> block 4 on, while a distant "bright parting cloud" in an extreme wide scored high. Water, sea,
> deep, surf, current, bubbles are first-class air. Read the vocabulary against the film you are
> actually making before trusting any draft.

`draft_air.py` fills `air` + `motion`, keeping two decisions deliberately separate:

**HOW MANY — the sliding quota.** A linear front-loaded curve: `--start` (default 0.80) of
block 1 animates, falling to `--end` (0.20) by the last block. Blunt, but definitive and cheap
to reason about — and it spends where distribution is decided, since a viewer who bails at
ninety seconds never reaches block 8. On an 8×40 film: 32/29/25/22/18/15/11/8 ≈ 160 beats.

**WHICH ones — motion-want ranking, within each block.** Every beat is scored on how much the
picked frame wants to move; the top N take the block's quota:

| cue in `phenomenon` | score |
|---|---|
| water / sea / deep / surf / current / bubbles / kelp | **+3** |
| suspended matter (dust, smoke, mist, ash, spray, embers) | +2 |
| cloth, robes, hair, banners, sails in wind | +2 |
| fire, flame, sparks | +2 |
| motion verbs (rising, pouring, striding, churning, collapsing, drifting) | +2 |
| living subjects (figures, crowd, birds, creature, sailors) | +1 |
| **carved stone, relief, inscription, page, text, ink, manuscript** | **−3** |
| **held / motionless / perfectly still / calm / unbroken** | **−2** |

So the Leviathan in its light shaft animates and the wall relief rides the free floor —
automatically, off the film's own `phenomenon` text, with no per-film configuration. That is
the dividend of keeping every per-beat decision in a column: the same tool splits a desert film
and a deep-sea film differently because the films describe themselves differently.

**THE FLEX — `--score-floor` (default 4).** A quota alone starves the back half of a film whose
most motion-hungry images are late. Any beat scoring at or above the floor animates in ANY
block, on top of its quota. On *Women in the Water* this rescued 15 beats — ten of them in
block 8, whose quota was only 8 — so the finale does not end on a slideshow. The curve still
front-loads; a hero motion beat can never be dropped for being late.

> **★ THE MARGINAL KLING DOLLAR BUYS RUN-BREAKING, NOT THE NEXT-HIGHEST SCORE.** The score ranks
> frames in ISOLATION; the viewer experiences SEQUENCE. A run of six consecutive floor beats
> reads as a slideshow however well each frame was chosen, and ONE Kling beat dropped into the
> middle breaks the whole stretch. So when budget is left over, find the longest `air=kb` runs
> and buy the highest-scoring beat INSIDE each. (This is the same blindness STORY ARC names:
> distributional measures cannot see monotony-in-sequence. Run length is sequential.)

> **★ THE SCORE READS YOUR PROSE, SO THE KLING BILL IS SET AT STEP 2.** `draft_air.py` decides
> nothing on its own — it ranks the words you wrote. *"Hard sunlight across the stone"* is dry and
> rides the free floor; *"shafts of light through dust"* is the same light, but the dust scores +2
> and commits the beat. **The tell is almost always the light clause**: name the SURFACE the light
> lands on and the beat is free; name the MEDIUM it travels through and you have bought a clip.
> This is not a reason to write drier — an air-starved film is a slideshow — but it does mean the
> spend curve is an authoring decision that nobody was previously told they were making. Declare
> the intent at Step 1 alongside the block roles, write to it, and let `draft_air` confirm rather
> than surprise you. *(Corollary of the AIR VOCABULARY law above: check the score table against
> the film you are actually making BEFORE you author, not after you render.)*

> **⚠ AIR IS A CLIP DIAL, NOT A STILL DIAL.** Every beat needs a picked still whether it animates
> or not — Ken Burns operates ON a still. Still spend is fixed by `weight` alone (hero 4 /
> connective 2) and `air` cannot move it. Cutting `air` saves Kling money and nothing else.

> **CHECK THE QUOTA AGAINST YOUR BLOCK COUNT.** The 0.80→0.20 default was tuned on an 8-block
> film. On a 12-block film the same curve yields ~244 of 480 beats (51%) — more than double what a
> hand-planned budget would allocate. Run `--dry-run` and read the split before accepting it;
> `--start`/`--end` exist precisely so the curve scales with runtime.

**Get `air` right BEFORE rendering.** `render_clips.py` skips clips already on disk, so a beat
upgraded after a full render needs `--force` or a manual delete. Dry-run, tune, then render once.

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

**Derivation ladder (first match wins), read off the beat's `phenomenon` + `register`** —
drafted by `draft_moves.py`, then eye-corrected against the picked frame. Be honest about the
order: **the tools derive from TEXT, you correct from the IMAGE.** Never hand-invent per beat:
```
1. quiet register/words (grief, aftermath, ash, empty, still) → settle   (never push)
2. vertical force (rising, column, tower, shaft, ascends)      → crane
3. scale/wide (ranked, vast, receding, to the horizon)         → pull
4. everything else                                             → push
```
`static` is NOT auto-derivable — promote specific held beats by eye. **The phenomenon drives
it; register is the tiebreak.** A flatline (all push) is the §0 blanket signal. Validate the
drafter against an already-shipped film's `move` column before trusting it on a new one.
**Front-loading is now a sliding QUOTA, not a contiguous block.** Per-beat control lives in the
`air` column, so the old contiguous front-N `kling_count` is retired — see Air + Kling above for
the quota, the ranking and the score floor.

### The Ken Burns floor (Step 8)

The floor is not a slideshow. `ken_burns_still(move=...)` runs one slow ffmpeg zoompan the full
5s, one move per beat, read off the picked frame exactly like the motion doctrine. Magnitudes
are small (push ~1.16×, pans ~11%) so continuous-across-5s reads as *alive*, not a cliché.
Because the floor is **$0**, iteration is free — render all, eyeball a sample, a bad feel is a
one-number tune + a free re-render. Kling stays available additively: mark a beat `air=kling` +
a `motion` and it upgrades, one beat at a time, only where the retention curve says.

> **⚠ NEVER LEAVE `move` BLANK.** `ken_burns_still` treats blank and `static` as the SAME
> true-static branch, which bypasses zoompan entirely and depends on `-loop 1` being on the
> ffmpeg input. Without that flag a single PNG yields a **one-frame ~0.04s clip** — and ffmpeg
> exits 0, so it looks like a successful render. Write `static` explicitly when you mean it, and
> gate every output (Step 8). `draft_moves.py` fills every row, which is the practical defence.

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
- **`stills [BLOCK...]`** — whole block(s) → the single `grid/` folder, flat-index filenames.
  **`stills beats=b/c,…`** — a manual cross-film sample → `grid-probe/` (same flat names).
  The per-block structural gate runs on block mode and is skipped
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

**The other readers** — all pure-stdlib except the render legs, all `--dry-run` before spend:

- **`place.py`** — winners → `shot_NNN.png`; hard-fails (placing NOTHING) on a skip-tile pick,
  a doubled beat or any gap in 1..N. `--winners` takes a FOLDER of picks **or a `.txt` list of
  filenames** plus `--grid` to source the bytes from the grid already on the box — so only the
  filenames travel, not 1.3GB. `--skip-tile` is required (it byte-compares to reject placeholders).
- **`draft_moves.py`** — fills `move` (`--csv`, `--dry-run`, `--redraft`, `--validate` against a
  shipped film). Blanks-only by default, so eye-corrections survive a re-run.
- **`draft_air.py`** — fills `air` + `motion` (`--csv`, `--start`, `--end`, `--score-floor`,
  `--dry-run`, `--redraft`). The spend dial; see Air + Kling.
- **`render_clips.py`** — Kling(`motion`) if `air`, else `ken_burns_still(move)`; `--floor-only`,
  `--dry-run`, `--force`. Skips clips already on disk (resume-safe).
- **`verify_clips.py`** — the Step-8 gate: ffprobe every clip, `--expect N`, `--normalise` to
  trim over-long clips losslessly.
- **`consolidate_grid.py`** — migrates an older per-block grid into the flat folder.

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
- **A banned REGISTER word may also be an ordinary NOUN, and the gate cannot tell.** Sacred Dawn
  bans `grave` as a register adjective; it is also the plain English word for a burial place, so
  every burial beat aborts. The gate greps raw text and has no part of speech. Either scope the ban
  or write around it (*a mound of turned earth*) — but know that any film with a death in it will
  meet this, and audit the channel's banned list against the film's SUBJECT before authoring.
- **The engine won't import on the laptop** (no dotenv/venv) — anything importing
  `recreation_pipeline` runs on the box; laptop-side edits to engine-owned data are pure-stdlib
  patches. `build_lego` is box-only for the same reason.
- **The skip-tile is channel-agnostic** — `shared/_skip.png` for all channels; a channel may
  override with `characters/_skip.png` (resolve shared first).
- **A blank `move` hits `ken_burns_still`'s true-static branch** (blank and `static` share it).
  It bypasses zoompan and relies on `-loop 1`; without that flag a single PNG produces a
  ONE-FRAME ~0.04s clip that still exits 0. Write `static` explicitly; gate every output.
- **`render_clips.py` does NOT trim Kling output.** Ken Burns is exact by construction
  (`-t 5.000` + `-r 24` → 120 frames); Kling returns a non-deterministic frame count (121 is
  common). `verify_clips.py` is what actually makes all N clips exactly 5.000s.
- **Derive the trim frame count PER CLIP as `round(fps × 5.0)` — never hardcode 120.** A 30fps
  clip trimmed to 120 frames is 4.0 seconds.
- **Machine work batches; human work chunks.** The block boundary buys nothing at render time —
  it exists to protect your eye at the pick.

---

## WORKFLOW & PATCH DISCIPLINE

**All code and config flows laptop → GitHub → box; never hand-edit on the box.** Edit on
LAPTOP → commit → `git pull --no-edit` on box → verify. Assets (media) move by rsync/scp and are
gitignored; code is GitHub-only. Stage explicit named paths — never `git add -A` (it can sweep
large media). BOX uses `python` in the venv; LAPTOP uses `python3`.

**Verify a tool is actually IN the repo before you depend on it.** Two working tools were found
misplaced or untracked mid-film — one sat at the repo root while the doc implied a channel
folder; another existed only as a loose file in `~/Downloads` and had never been committed at
all. "Code is GitHub-only" is a rule nothing enforces: `git ls-files --error-unmatch <tool>`
costs a second and catches it.

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
  **This is now a MEASURED competitive cost, not a footnote.** The film that beat us in the Sacred
  Dawn lane (698K in eleven days) runs two-hander dialogue heavily throughout — its most effective
  retention beats are two people talking. Until the single-call model is solved, compensate in the
  narration: reported speech carried in the witness voice (*"What is this, his son asked him. And
  his father did not look up."*) keeps the exchange and the tension inside one continuous read. It
  is not as good as the real thing; write it knowing what it is standing in for.

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

> **★ BUILD THE JOIN — it is the only unbuilt thing in this doc that makes every future film
> cheaper.** Step 10's observation is currently "read CTR+AVD, bank the failure", which produces no
> file and no format, which is why the FILM RECORD rows sit empty. Two artifacts fix it:
> **(a)** `observations.md` per project — CTR and AVD at 48h, the traffic mix at day 14 and 21, the
> two or three timestamps where the curve actually broke, and the portable law banked from each;
> **(b)** a pure-stdlib join script that takes the exported retention curve and the master, and
> writes the watch-ratio onto every beat row. The arithmetic is already exact — beat *i* of block
> *N* spans `((N−1)×200)+((i−1)×5)` to `+5` seconds, plus the cold-open offset. No other part of
> this pipeline gets ground truth this clean. **The row where viewers left becomes the next film's
> training signal**, and the candidate measures above stop being speculation the moment there are
> two joined films to correlate against.

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

*22 Jul 2026 — flag register 01–18 merged from the Methuselah build (Sacred Dawn, 12 blocks /
480 beats, authored end to end against this doc). `_LEGO-FLAGS.md` is retired; delete it.*

- **THE PROCESS is now 0 to 10.** The cold open was one clause inside the old Step 9 and is now its
  own step with its own section, because two Sacred Dawn retention curves put the channel's whole
  bleed in that seam (bottom-decile first minute against above-median middles). The old instruction
  — *cut it from the best clip of every block* — was the trailer error stated as a sourcing rule.
- **Steps 0, 1 and 10 now produce FILES.** `package.md`, `architecture.md`, `observations.md`. The
  old gates were "a decision to build", "block plan exists" and a prose instruction — all of which
  lived in chat and were gone by the next session. The doc diagnosed this failure in WORKFLOW and
  then committed it in its own first two steps.
- **Step 0 renders the thumbnail file**, not a concept. On a channel whose declared moat is
  packaging, thumbnail production was absent from the pipeline entirely.
- **Per-block CSVs are gone.** No `blocks/` folder, no `bNN.csv` — blocks are drafted in chat and
  appended straight to `master.csv`. And the block gate is demoted to a drafting check: on
  Methuselah the FILM-level gate caught three wrong hero counts, a negation, and per-block word
  totals that had been reported without being measured. Twelve per-block passes are not a film pass.
- **Step 1 carries the chronology, the spine object and the antagonist.** A block plan that assumes
  a time-shape the source contradicts is invisible until you are authoring beat one — it cost three
  separate catches on one film.
- **Craft law gains the spine object, the refrain and the named antagonist** — all three read off
  the competitor teardown, and the antagonist finding is the mid-film sag diagnosed from both sides.
- **WPM is settled and recorded as settled** so it is not re-litigated: a competitor's 102 WPM is a
  production figure with no curve attached, and Sacred Dawn's own curves show density costs nothing
  after the open.
- **Silence-as-assembly is banked with its full spec** (`sentence_id` as TTS render unit + ffmpeg
  gap concat), deliberately unbuilt.
- **`air` gains its authoring-side half.** `draft_air.py` ranks the words you wrote, so the Kling
  bill is set at Step 2 whether or not anyone knew it; and the 0.80→0.20 quota was tuned on eight
  blocks and yields ~51% on twelve.
- **Canon technique:** the non-leading identity token, and re-minting a token when the same place
  changes across time.
- **Also banked:** a banned register word that is also an ordinary noun (`grave`) aborts every
  burial beat and the gate cannot tell them apart; and the single-narrator limit is now a measured
  competitive cost with a stated compensation.

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
- **One grid folder, flat-index filenames** (21 Jul, after the WITW grid). Per-block folders and
  `{clip}-{variant}` names are retired: clip index repeats in every block, so flattening the
  winners collided, and the block-prefix fix used on the probe fails `place.py`'s regex. Flat
  film index (CSV row order) is unique by construction, `place.py`-compatible, and the same
  number `render_clips.py` uses — one naming law for probe, grid, winners and clips.
  `consolidate_grid.py` migrates older films.
- **The air/Kling SPEND DIAL** (22 Jul, WITW clips). `draft_air.py` retires both the contiguous
  front-N `kling_count` and the earlier air drafter: sliding quota (80%→20%) × motion-want
  ranking × score floor. **Water added to the air vocabulary** — its absence had scored a
  deep-sea film at zero from block 4 on. Marginal budget goes to RUN-BREAKING, not the next
  highest score.
- **Step 8 finally has its gate.** `verify_clips.py` implements the "ffprobe every output,
  hard-fail anything not 5.000s" rule the doc has always asserted and nothing implemented —
  plus the Kling trim `render_clips.py` never did, with the frame count derived per clip.
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

### 2 — *Methuselah — The Movie · 969 Years, and He Died the Year the Water Came*
**Sacred Dawn · shipped: (pending) · project `methuselah`**

| | |
|---|---|
| structure | 12 blocks · 480 beats · 40:00 + 55s cold open |
| narration | **6,859 words · 14.29 words/beat** |
| voice | Elliot (Inworld) |
| canon | 18 tokens (16 place-locks + 2 identity locks) |
| spine object | the marked stones — one per year, 969 at the end, drowned |
| antagonist | Lamech of Cain's line (Gen 4:23–24); the two-Lamechs mirror caps at b8 |
| grid | 1,200 real stills · **$96.00** |
| clips | (pending — `draft_air` split not yet run; hand-planned intent was ~22%) |
| **CTR / AVD @48h** | *(pending)* |
| **AVD day-14 / day-21** | *(pending)* |
| arc scores | *(pending)* |

**Notes.** First film authored under the 0–10 process with `package.md` and `architecture.md` as
real artifacts. First to use a spine object and a named antagonist by design rather than by
accident. Authored ~6% above WITW's 13.5 w/beat, so expect `calibrate` to want a trim pass weighted
into blocks 8–12. Three chronology catches during authoring (see flag 16 in the changelog) — all
from Genesis 5 arithmetic, all invisible until beat one.

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
