# _LEGO.md
### The single pathway for cinematic feature films — Sacred Dawn · Scripture On Screen · Synthetic Press

**Supersedes:** `_LEGO-FEATURE-FILM.md`, `_MOTION-DOCTRINE.md`, `_MOTION-VETO.md`, `_SCRIPT-CONTRACT.md` (§5 narrative + §6 visual absorbed into §3A, 17 Jul — **with its genre overlays scrubbed; they were pre-pivot and carried the Final Hours register**).
**Does NOT supersede:** `<channel>/DOCTRINE.md` — grade, register, banned words, slate. Those are **config**. This is **code**.
**Status:** proven end-to-end on Sacred Dawn / *The Book of Enoch* (30 min, 10 blocks, 15 Jul 2026). Timing model rebuilt and measured 17 Jul 2026. Authoring contract folded in 17 Jul 2026.

> **This pathway is channel-agnostic.** Everything here is true of all three movie channels. Channels differ by `channel.json` only — never by code path.

> **This pathway is NOT the batch path.** The low-effort forward-batched maintenance channels run the existing assembly untouched. Separate entry point, separate module. Never modify shared assembly code to serve this document.

---

## 0. THE GOVERNING LAW

> **Any rule that applies to 100% of beats is a bug until proven otherwise.**

This law generated both sessions. Every failure found has been a blanket stamped where content should have earned it — grade, faces, emotion, motion, word count, variant count, animation. When you find yourself writing a rule that fires on every beat: **that's the bug.**

Its corollary, and the whole of the 17 Jul session:

> **Measure both sides. Assume neither.**
> Whisper measures the audio. ffprobe measures the video. Everything that felt like taste was a rule you hadn't written down; everything that felt like negotiation was a number you hadn't measured.

**Drama is earned by content, not stamped by grade.** The same sentence is true of faces, of emotion, of the camera, of the word budget, and of how many stills a beat deserves.

---

## 1. THE HIERARCHY

```
THE CONTAINER IS KING     40 clips × 5.000s = 200.000s. Non-negotiable. Everything serves it.
THE BEAT TABLE IS EMPEROR The only place sequence exists. One row = one clip.
THE SCRIPT IS A COLUMN    The most governed column. Budgeted first, rendered last.
```

**Why the script was dethroned.** "Script is king" meant words came first and everything served them. Now: the clip won, so words fit under a ceiling; and audio renders *last*, after the clips are measured, because it is the only layer that can bend. The script went from the thing everything serves to the thing that serves everything.

**Why the table is emperor.** Not because it contains the script — because **nothing else in the pipeline knows the order.** That is the entire source of its authority, and the reason the rework vanished.

---

## 2. THE BLOCK — THE LEGO UNIT

**One block = 3 minutes of finished film. The block never changes; only the count does.**

| property | value | why |
|---|---|---|
| **beats** | **40** | 40 × 5.000s = **200.000s container** |
| **clips** | 40, trimmed to exactly 5.000s / 120 frames | §4 |
| **stills** | **~100** (variable, §5) | not 160 — variable allocation |
| **VO** | **~380 words** | 143 WPM (Elliot) → ~159s speech, ~41s air |
| **word ceiling** | **10 words per beat** | hard gate |
| **breaks** | **≤20 per request** | Inworld hard limit, §4 |
| **block cost** | **~$25** | ~$8 stills + ~$17 Kling |

**The block is self-contained.** Its VO does not run across the seam. Its clips do not depend on the previous block's frames. Blocks fail and re-render independently. **A bad block is $25, not a film.**

### Block length is set by narrative and pick capacity — never by tooling

The block was never a timing constraint and is not one now. Timing is solved at any length. Blocks are 3 minutes because:

1. **The pick degrades with fatigue.** It is the one thing that will never be automated. 100 stills is a sitting; 800 is a rubber-stamp.
2. **Blast radius.** A failed measurement pass costs a 3-minute re-render.
3. **Blocks are dramaturgy.** Each has a job, an emotional identity, a music track. Chapters map to block boundaries.

*Audio length is not a constraint: Inworld's 20-break cap is per request, and multiple calls concatenate freely (pin the same `voiceId` and `modelId`). But each request lands terminal falling intonation — so **split only on a boundary that was already going to breathe.** A block boundary is the ideal seam.*

### Scaling

| film | blocks | beats | stills | clips | cost |
|---|---|---|---|---|---|
| 15 min | 5 | 200 | ~500 | 200 | ~$125 |
| **24 min** | **8** | **320** | **~800** | **320** | **~$200** |
| 30 min | 10 | 400 | ~1000 | 400 | ~$250 |
| 60 min | 20 | 800 | ~2000 | 800 | ~$500 |

*Incumbent comparison: $400–1,500 per feature. **The metric is shots on goal, not fidelity.** In a niche with a 12:1 average-to-median ratio, the question is never what one video costs — it's how many the same money buys. **If a film takes longer than the last one, the pipeline lost.***

---

## 3. THE BEAT TABLE

One row per clip. Flat, ordered, and the single source of sequence.

| column | values | derived from |
|---|---|---|
| `clip_index` | 1..40 | — |
| `block_id` | 1..N | narrative |
| `sentence_id` | groups contiguous rows | authoring |
| `scene_id` | groups contiguous rows (chained takes only) | authoring |
| `words` | ≤10 | **gate** |
| `narration` | pure spoken text, **no tokens** | authoring |
| `phenomenon` | real verbs: descends, towers, spreads, waits | authoring |
| `weight` | hero \| connective | §5 |
| `variants` | 4 \| 2 | read off `weight` |
| *(canon)* | `{tokens}` **inside `phenomenon`** — never a column | `channel.json` → `canon` |
| `air` | visible \| flat | **read off the picked still** |
| `animator` | kling \| kenburns | read off `air` |
| `register` | awe \| fear \| grief \| wonder … | beat text |
| `picked_variant` | a \| c \| d1 \| d2 | **the human** |
| `motion` | derived | `beat × variant × register`, §7 |
| `seed` | logged at generation | **provenance** |

### The rules that make it work

- **`narration` stays pure spoken text.** No `{tokens}`, no markup. Whisper measures it and the gate counts it — a token would either get spoken or need stripping, and the arithmetic goes soft. **This is the one column that must never carry markup.**
- **Canon is `{tokens}` in the VISUAL/`phenomenon` text — the mechanism already exists, do not invent a column.** `channel.json` carries a `canon` block; `modea_beats.py --channel-config` emits it alongside the beats; `_expand_canon` attaches the character's reference images **and** expands the tag into the prompt. **It raises on an unknown tag** — so a reference-mode channel MUST ship its canon, and `reference_map` tokens with no canon entry are a hard fail at translate time, before spend. No config or no canon block → identical output to before. *(Recovered from the box 17 Jul; same pattern as Skeptic's locked wardrobe.)*
- **Grouping IDs, never nesting.** Sentences group rows for TTS. Scenes group rows for chained generation. Same shape: contiguous runs that cannot reorder.
- **Symmetry lives in the table, not the filesystem.** `variants: 2` means two files exist. **Never write blank placeholder stills** — a blank collapses "never requested" and "generation failed" into one artifact, and you cannot tell which by looking. With no blanks the invariant is checkable: table says 4, three files exist → gate fails loudly.
- **Log the seed.** Free today, impossible retroactively. Without beat → variant → seed → clip → timestamp, repairing block 5 after assembly means re-picking, and the table's authority leaks.
- **The table is the bill of materials.** Rows × variants = still calls. It gives an exact pre-spend cost, not an estimate — and it makes the two dials (hero/connective split, Ken Burns fraction) visible while it's still text. *Caveat: pick hours are not in it, and they are the scarce resource. And it's a floor — a failed gate doubles a block.*

---

## 3A. AUTHORING THE COLUMNS

*Recovered from `_SCRIPT-CONTRACT.md` 17 Jul. §3 defines the columns; this governs what goes in them. `motion` is §7. Prescriptive — there is no interpretation.*

### 3A.1 · `narration`

> **★ THE OPENING LAW — the highest-leverage rule in the contract.**
> The title makes a promise. The thumbnail amplifies it. **The opening fulfils it in the first frame.** Never delay, never explain first.
> **Open on impact, never on history.** "The Day Jerusalem Fell" → open on Jerusalem burning. A disaster film → open on the sky already on fire, the hand already on the lever — **not** two men writing a letter. Maximum intensity from frame one. No warm-up, no "today we're going to," no throat-clearing. **Drop the viewer into Act III of an epic already in motion.**
> Structure is free to flash back *after* the peak.

> **Reconciling the Opening Law with the block structure (§8).** They look contradictory — "impact frame one" against "block 1 is the object, payload at minute six" — and they are not. **The COLD OPEN is the impact opening.** It carries the Opening Law entire: 45–90s, maximum intensity, cut from the best shot of every block, planting the film's biggest loop. Block 1 then opens on the object, block 2 builds authority, the payload lands at block 3. **The cold open buys the right to be patient.** Without it, block 1 must carry the Opening Law itself — and an object-open with no cold open in front of it is the 2–3% cliff.

**THE CURIOSITY ENGINE.** Never answer a question without opening a larger one. **Curiosity never reaches zero.** Run the loop: question → hint → partial answer → twist → larger question → higher stakes → reward → repeat. **Keep an open-loop stack** — several unanswered questions live at once; as one closes, another opens. **Reveal less, imply more** — information reduces curiosity, discovery increases it. Reveal a fact only when it creates *more* questions. **Never dump facts.** End every section on a lean-forward. **Every 30 seconds is its own trailer** — nothing exists purely to explain.

**ESCALATION — every 20–40 seconds.** The audience must FEEL something every 20–40s. **At 5.000s per beat that is every 4–8 rows — countable in the table.** Rotate states: wonder, fear, hope, shock, awe, relief, disbelief, tension, triumph, reflection. **Every section increases at least one of** scale, danger, mystery, consequence, emotion, urgency, human cost. **If none increase — rewrite.**
Rhythm and contrast: large → small intimate → reflection → escalation → silence → explosion. **Never hold one tempo. Constant loudness goes invisible.** Pair opposites — big/small, hope/despair, silence/chaos, order/collapse.

> **Pace is WORD DENSITY, not clip length.** The contract's shot-length texture (2–4s escalation · 3–6s emotional · 6–10s awe) **cannot survive the fixed 5.000s grid — and does not need to.** A hero beat takes 6 words and a second of air; a rapid sequence carries 13. **The bounded word budget (§4) IS the pace instrument.** Equal words per beat would flatten it — which is why the budget is bounded, never equal.

**THE HUMAN LENS.** People move people, not statistics. **Anchor every epic event through one individual.** Scale-shift constantly: individual → family → city → nation → civilisation. **Disaster is never a number** — show consequence: families, empty streets, ash, the silence afterward.

**THE SENTENCE.** **Visual narration only** — not "many people died" but "a city where even the birds had stopped singing." **One unforgettable trailer line every few paragraphs.** Immersion is sensory: sight, sound, smell, temperature, dust, wind, silence. **Narrate like a witness, not an encyclopedia** — conviction, not hedging.

> **★ PROSODY — NON-NEGOTIABLE, AND LOAD-BEARING FOR §4.**
> *The narration is not read — it is spoken. Punctuation is prosody control. It decides whether the voice sounds broadcast or robotic — and it decides what whisper measures.*
> - **Kill the see-saw. Dampen full stops.** Consecutive periods make the voice fall to a terminal pitch again and again — the read pumps up-and-down. **Replace most periods with em-dashes and commas** so the voice holds a continuation contour. **Reserve the full stop for a deliberate, weighted landing — then it means something.**
>   - *See-saw:* "The sky went black. The men advanced. Nobody moved. It was too late." → four terminal falls.
>   - *Flowing:* "The sky went black as the men advanced — and nobody moved, because it was already too late." → one contour, one landing.
> - **Spell every number out.** "Twelve thousand," never "12,000." Digits get mangled by the voice. *(Digits are fine in a VISUAL line — that's for the image, not the voice.)*
> - **Write for the breath.** Read each line aloud in your head. If you stumble, the voice will. **Punctuation is where the voice breathes; place it on purpose.**
>
> **Why this belongs to the timing model, not just the craft.** §4's delta pass measures the *rendered* audio. Prosody decides how it renders — a see-saw script produces terminal falls where you budgeted flow, and the deltas fight you. **The em-dash and the `<break>` are the same instrument at two scales:** the dash shapes the contour inside a sentence, the break buys silence between them. **A prosody-clean script converges in two passes. A see-saw script doesn't converge.**

**TRUTH.** Prove extraordinary claims immediately. **Never exaggerate** — reality is already extraordinary. **Alternate story and fact** — story → fact → story → reveal → emotion. Never long explanatory blocks. *(Attribution discipline: `_CHANNELS.md §0.4`. It binds absolutely and it is what makes the aggression safe.)*

**THE FINAL TEST.** Every paragraph must increase at least one of: curiosity, emotion, danger, mystery, consequence, beauty, awe, scale, urgency. **If it does none — cut it.**
> **Promise · Prove · Escalate · Reveal · Complicate · Reward · Escalate again. Never coast. Never plateau.**

### 3A.2 · `phenomenon` (the VISUAL)

> **★ THE VARIETY LAW — the top visual rule; everything below serves it.**
> **No two consecutive beats may share framing, angle, scale, or pace.** Every beat differs from the one before on **at least one axis**: high/low, close/far, wide/tight, warm/cold, loud/still, subject/environment. **Repetition is invisibility — the eye stops seeing what stops changing.**
> Rotate every axis across the film: extreme-wide → wide → medium → close → extreme-close and back; eye-level → low → high; warm → cold. **Never settle into a groove.**
> **The guardrail: variety is motivated, never mechanical.** Cut wide because the narration *widened*, low because the moment gained *power*. **Timer-driven variety is the metronome problem in a different costume.** *(Same law as §7's motion derivation — and this is why: shot variety IS motion variety, because the move is read off the shot.)*

> ### ★★ EVERY BEAT NAMES ITS OWN LIGHT — THE MISSING HALF OF THE PALETTE-ONLY GATE
> **The model defaults dark and murky when light is left unspecified. An unlit prompt renders muddy.**
> PHASE 1 strips light from the `style_suffix` because a welded light source is a blanket (§0). **That removal is only half the fix.** Light does not disappear — it **moves to the beat**, where content earns it. Every beat names its scene light: *clear gold dawn · blazing clean afterglow · vivid twilight · bright parting cloud · firelit interior.*
> **Strip the blanket and skip this rule and the murk comes back by a different road.** The suffix carries palette; the beat carries light. Both, always.
> *(Live risk on Sacred Dawn as of 17 Jul: the god-ray clause is correctly gone from the suffix, and there is now NO light instruction anywhere unless the beats supply it. **Gate the beat table on it.**)*

**NEGATIONS GROW FROM EVIDENCE, NEVER SPECULATION.** Add a negative ("no murk," "no modern objects") only for a failure class **you have actually seen render wrong.** Speculative negation vetoes the model's best output. Do not pre-emptively ban what hasn't gone wrong.

**COMPOSITION.** **Depth always** — foreground, midground, background. Never one flat plane. **A hero shot every 20–30s** — one composition that could be a poster; the viewer should remember individual frames. **Strong silhouettes.** **Faces retain** — eyes create emotion; when emotion matters, move closer. **Angle with intent:** eye-level = honesty (use most) · low = power (kings, giants, angels, walls of fire) · high = vulnerability (victims, ruins, isolation).

> **⭐ SCALE NEEDS A HUMAN FACE AT THE BOTTOM OF THE FRAME — the signature move, all three channels.**
> Spectacle reads as *majestic* rather than merely big when one small human witnesses it: the vast event filling the frame above and behind, one weathered face or lone silhouette dwarfed beneath. **Never render the fireball, the flood, the collapsing city alone.** The awe lives in the size difference. This is the visual form of the Human Lens — **and the one move the spray-and-pray incumbents skip.**
>
> **🔴 THIS RULE IS FOR FILM FRAMES. IT IS FALSE FOR THUMBNAILS.**
> At 120px the dwarfed human vanishes and the frame reads as texture. Sacred Dawn's doctrine applied it to thumbnails and produced **1.9%**; Scripture had already proven the dwarfed hero loses at feed size. **Dwarf in the wide. Never in the thumbnail.** See `_CHANNELS.md §0.2`.

> **⭐ A SPECTACLE IS A SEQUENCE OF HERO SHOTS, NEVER ONE COMPOSITE FRAME.**
> The instinct is to cram the whole miracle — the fire, the altar, the prophet, the crowd — into one image. **It always fails:** the phenomenon shrinks to a prop (fire on an altar reads as a campfire) and nothing is a hero shot.
> **Stage the moment across several beats, each a distinct hero frame:** the phenomenon gets its **own** beat with nothing else in it (the column of fire tearing down from a hole in black cloud — no altar, no man), then the strike, then the human reaction, then the aftermath.
> *Render-proven on the Mount Carmel cold open: the composite read as a campfire; the six-beat sequence read as a scene.*

> **★ SETTING CONTINUITY — the locked place-phrase.**
> The `canon` block locks WHO. **This locks WHERE.** Place drifts exactly like an unlocked character and it is just as visible. A scene rendered as independent stills will invent several locations — a canyon in one beat, a bare plateau in the next — each internally fine, none agreeing on where we are. **It is the single most common way a multi-shot scene falls apart, and the fix is pure authoring.**
> - **Write the setting once as a locked phrase** — terrain, material, defining features, explicit negatives. *"the bare rocky summit of Mount Carmel — pale weathered stone, dry scrub, scattered grey boulders, open wilderness, no buildings, no city, no structures."*
> - **Paste that exact phrase into every beat in the scene. VERBATIM REPETITION IS THE MECHANISM** — the same way an identical `{token}` re-attaches an identical face. **Do not paraphrase beat to beat.**
> - **Add explicit negatives for what the model wrongly adds.** "Biblical" pulls toward "ancient city," so a wilderness scene must say *no buildings, no city.* **The model omits nothing unless told.**
> - **Let framing vary; keep the identity fixed.** A looking-up shot shows sky, a wide shows the valley — that detail changes per beat; the locked phrase stays word-for-word.
> - **A new setting = a new locked phrase.** One phrase per location, held for the length of the scene.
>
> **Honest limit (render-learned):** the phrase is a real **reduction, not a cure** — a canyon still crept into one shot of a locked-summit scene. The true fix is a locked setting **image**: a `reference_style_anchor` plate attached to every beat, so place is reference-anchored the way a face is. **Same $0.08 edit-path mechanism the character refs already use, currently read-but-unwired in the engine. A priority build, not a someday.**

**DRIFT CONTROL — non-negotiable.** One primary motion per beat plus subtle ambient. **Never everything moving equally — simultaneous complex motion is the #1 hallucination cause.** **Lock the subject, move the camera.** **The subject moves *less*** — large exaggerated body movement increases errors; let cloth, smoke and dust carry it. **Consistency:** same clothing, age, facial structure, hair, direction of travel across a character's beats. **Simple beats complex** — one elegant move looks more expensive than five competing ones.

> **★ CUT BEFORE FAILURE. Clips are strongest in their opening moments. End early — the audience remembers quality.**
> **This is the craft reason for §4's trim.** `-frames:v 120` drops the *tail* frame, never the head. Arithmetic wanted a uniform grid; craft wanted the tail gone. **They agree, and the trim is free.** *(It is also why trim-never-pad: a freeze-frame is the failure the rule exists to prevent.)*

**PROMPTS CARRY ZERO GRADE WORDS.** The look lives in `channel.json`'s `style_suffix`. **Per-beat light is CONTENT and belongs in the beat** (see above) — grade is not. **No literal-metaphor beats:** no keys, globes, hearts, scales. Models render metaphors as corny props and anachronisms. **Render the consequence, not the metaphor.**

**Write phenomena with real verbs** — descends, towers, spreads, waits. The beat text drives the register classifier and the motion derivation (§7); a verbless beat derives nothing.

**THE CINEMATIC TEST.** Pause on any frame. **Could it be mistaken for a still from a $200M feature?** If not — fix composition, light, depth, colour, silhouette, placement, negative space.
> **The audience should think "I feel like I'm there," never "look at the animation." The camera is not the hero. The story is.**

---

## 4. TIMING — THE SOLVED PROBLEM

This was the recursive problem for months. It is arithmetic, not iteration.

### The measured facts (17 Jul 2026, 400 Enoch clips)

```
398 × 5.041667s   (121 frames @ 24fps)
  2 × 5.000000s   (120 frames)
```

**Kling is non-deterministic at the frame level.** Usually 121, occasionally 120, scattered across blocks. One extra frame = 41.67ms = **1.67s drift per block, 16.6s across 400 clips.**

> This is the cause of the "chapters land 20–40s off when estimated" symptom that was already banked in the channel docs. The workaround was written down for months; the cause was one frame.

### The fix: normalise on ingest, trim never pad

**LAPTOP / BOX**
```
for f in *.mp4; do ffmpeg -v error -i "$f" -frames:v 120 -c copy "../trimmed/$f"; done
```

- `-c copy` copies packets **without decoding**. Not a re-encode. Zero generation lost. The quality-decay instinct is satisfied: the enemy was always **re-encoding**, never ffmpeg.
- Works only because the cut is at the **tail** — head keyframe intact.
- Normalises the 121s, passes the 120s through as no-ops. One rule, no special cases.
- **Trim never pad.** Dropping a frame is invisible; a freeze-frame isn't. A short clip is regenerated, never stretched.
- **`-frames:v 120` is a cap, not a guarantee.** If Kling ever returns 118, the command succeeds silently. **Gate every output.**
- **Derive 120 from framerate.** 120 frames = 5.000s *at 24fps*. Read `r_frame_rate` × 5. A 30fps model would silently make 120 frames = 4.0s.

**GATE**
```
for f in *.mp4; do ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of csv=p=0 "$f"; done | sort -n | uniq -c
```
Expect one line: `N 120`. Anything else hard-fails before assembly.

### Consequences

- Block = **200.000s exactly**. Block N starts at **(N−1) × 200.000**. Clip 87 starts at 430.000.
- **Chapters are arithmetic**, not estimates. The §9 estimation warning retires.
- **Never insert silence between blocks.** Pad each block's audio to exactly 200.000s as its final step. The air is already inside the container. Silence between blocks breaks the grid and you are negotiating again.
- **The ffprobe→audio feedback loop is dead code.** It was designed for a drift that the trim eliminates. Do not build it.

### The word budget — bounded, never equal

```
5.000s clip @ 143 WPM = 11.9 words with ZERO air
380 words / 40 clips  = 9.5 words = 4.0s speech = 1.0s air     ← correct
430 words / 40 clips  = 10.75 words = 4.51s = 0.49s air        ← the old number, too tight
```

**430 was the bug.** A hero beat taking 1.5s of air forced its neighbours to the 11.9-word ceiling with zero margin — that is why it always felt like juggling. **380 words, 10-word ceiling per beat.** *(Corollary of §0: 10.75 words in every cell is a blanket.)*

The gate runs one-directional and that is deliberate: 380 words ≈ 159s speech + ~15 breaks ≈ 174s, inside 200s. **The tail is always a pad, never a trim.** If a block needs trimming, the gate failed upstream — fix it there.

### Air as the shim

The pause was never a compromise. **Air is both the craft answer and the arithmetic answer** — the thing that lets hero shots breathe is the thing that snaps speech to the grid. Rare alignment; do not lose it.

Inworld: `<break time="800ms" />`. Well-formed SSML, case-insensitive, ms or s.

> **HARD LIMIT: 20 break tags per request. After the first 20, the rest are SILENTLY IGNORED.** Not an error. A 25-break block renders, sounds nearly right, and drops five. The gate must count break tags and hard-fail above 20 before render. Each break ≤10s (irrelevant at our scale).

Spend air only where doctrine demands it — hero beats, settle, grief. Ordinary beats absorb their remainder as pad.

### The sentence is the TTS unit — never the beat

**One TTS call per block, not 40.** TTS renders each request as a complete utterance: a 6-word fragment gets terminal falling intonation as if it were a sentence. Stitch 40 of those and it is a list being read, not a film being narrated — a worse failure than drift and audible in ten seconds.

Contiguous rows sharing a `sentence_id` are one unit. A 26-word sentence across three beats occupies exactly 15.000s of container. Breaks only ever go **inside** a sentence.

### The loop: two passes, convergent

```
1. render block  →  one Inworld request, breaks in
2. whisper       →  word-level timestamps on the RENDERED AUDIO (not the script)
3. measure       →  each beat's last word vs its 5.000s boundary
4. delta         →  adjust that beat's break by the difference
5. re-render     →  once
```

Breaks are additive and independent, so pass two converges. **A third pass means something else is wrong** — a beat over the word ceiling, or the 20-break cap silently truncating.

**Tolerance ±150ms.** Whisper's word timestamps are ~±50ms. Chasing tighter is chasing noise; Filmora's trim eats the rest.

### Artifacts out, per block

```
block_N.wav          padded to exactly 200.000s
gate.json            pass/fail: words, ceiling, break count, frames, duration
manifest.json        beat → variant → seed → clip → timestamp
```
Plus one stitched master. Emit both — block files are what you re-render when block 5 fails.

---

## 5. VARIANTS — VARIABLE ALLOCATION

### The proven pick distribution (Enoch, 400 beats)

```
a (wide)      100   25%
b (mid)        81   20%   ← the loser
c (face)       75   19%
d (WILDCARD)  144   36%   ← the clear winner
```
Block 8: a=2, d=20. **The authored hero shot beat every formula variant.**

### The grammar

| variant | shot | face |
|---|---|---|
| **a** | **WIDE** — phenomenon dominant, human tiny and dwarfed | none (anonymous *by distance*) |
| **c** | **TIGHT** — the reaction shot | full anonymous face, **register-matched** |
| **d1 / d2** | **WILDCARD** — authored hero composition, unique to this beat | varies |

**The mid dies.** Not a shot size — the formula. `a, c, d1, d2` replaces `a, b, c, d`.

### Allocation is read off `weight`, never flat

| weight | variants | which | typical beats |
|---|---|---|---|
| **hero** | **4** | a, c, d1, d2 | payload beats · block opener · block closer · cold-open candidates · thumbnail candidates |
| **connective** | **2** | a, d1 | bridges · a name · a manuscript · a fragment |

~10 hero + ~30 connective per block = **100 stills, not 160**. 37% less pick load, zero loss where the film is won.

> **A flat 4→2 cut is the wrong instinct** — it deletes shot-size coverage on the beats that need it, and shot variety *is* motion variety (§7). Variable allocation preserves rotation on the beats that drive it. *(§0 again: 4 variants on every beat is a blanket.)*

**Anonymous, never faceless.** Faceless hides every face. Anonymous never locks one. The recurring figure stays turned or distant; every other face shows freely. A different anonymous face each time reads as *humanity reacting*, not continuity breaking.

**The tight's emotion rotates by register, never blanket.** A blanket "deeply moved" collapses to tears on 100% of frames and destroys the emotional-variation lever.

**Ask per group: which of these earns $0.42 of Kling?** — never "which is prettiest."

**Integrity gate, every block:** 40 picks · **no duplicate beats** · **no missing beats**.
> 40 picks does not mean one-per-beat. Two winners on beat 7 + none on beat 23 still counts 40, and silently corrupts beat order — discovered only after the full Kling spend.

---

## 6. AIR — THE ANIMATOR RULE

**Read off the picked still. Not chosen.**

> **Air means literal, visible, suspended matter in the frame.** Dust, smoke, mist, embers, water, drifting cloth. Not pace. Not narration pauses.

| `air` | animator | why |
|---|---|---|
| **visible** | **KLING** | the eye knows what suspended dust does; a frozen dust shaft reads as wrong before you can say why |
| **flat** | **KEN BURNS** | static object, no depth for air to live in — a slow push on a document is documentary language, and correct |

**Ken Burns natively does four of the five moves** — push, pull, settle, near-locked are zoom and drift. Only crane-up it cannot do honestly: a crane needs parallax, and a Ken Burns "crane" is a vertical pan in a crane's clothes.

**What it cannot do is the ambient layer.** Motion exists to give a still a *living* drift. Living comes from the air, not the camera move. And the contrast is the tell: **intercut thirty dead-air clips with ten living ones and the dead ones get more obvious, not less.**

### The floor

> **The floor is not "Ken Burns slideshow." The floor is: any beat with visible air is dead.**

That is the line. Everything above it is a dial, and the dial matters less than it feels like it does. The Balrog principle — mass and consequence, never glow and float — is a composition and grade rule. **It costs nothing and survives at any budget.** The low angle and the dwarfed human do the work, not the render spend.

### The flat set is narrow

Sacred Dawn's grade puts atmosphere in most frames by construction — a manuscript in a dark chapel probably has a dust-lit shaft in it, because the `style_suffix` puts one there. **That frame is Kling.** Genuinely flat: a page of Ge'ez filling the frame, a fragment on a light table, an inscription in close-up.

Two bonuses: Ken Burns clips are exactly 5.000s by construction, shrinking drift proportionally. And ffmpeg `zoompan` off a PNG is a **first** encode, not a re-encode — it does not violate §4.

---

## 7. MOTION

**Motion is a function of the shot, not a choice.** You never think of a nice move — you classify the shot, and the classification names the move. It feels art-directed because it is one rule applied 40 times, not taste applied 40 times.

Motion's only job: **give a still a slow living drift so it reads as a shot, not a slideshow — and let the move quietly amplify what the frame already means.** Not to add action. No characters running, no choreography — that is where AI drift lives.

### Four moves under VO — NEAR-LOCKED is retired

| move | use when | why |
|---|---|---|
| **PUSH-IN** | one overwhelming subject; awe, encounter, a face | increases pressure; pulls the viewer *into* it |
| **PULL-BACK** | the meaning is scale / consequence / number | the scale reveal *in motion* |
| **CRANE-UP** | vertical phenomena; descending fire, a towering figure | the camera rising *with* it amplifies height |
| **SETTLE** | reflection, aftermath, grief | reads as an exhale; closes a section down |

> **NEAR-LOCKED is retired for narrated features.** Under continuous VO a locked frame reads as a stalled slideshow, not a held breath. SETTLE carries the quiet work. *(It remains correct for music-driven montages.)*

> **"Never push-in on silence" re-triggers as "never push on the grief/aftermath beats."** There is no silence — the VO never stops. Same rule, new trigger. **Name the departure; never silently reinterpret.**

### Derivation: `beat × variant × register` — never beat alone

The same beat picked as an `a` wide is a scale-reveal (PULL-BACK); picked as a `c` face it is one overwhelming subject (PUSH-IN). **The picks record is what makes correct derivation possible.**

**Precedence ladder, first match wins:**
```
1. grief/aftermath  → SETTLE      (never push)
2. vertical force   → CRANE-UP    (overrides framing)
3. c tight face     → PUSH-IN
4. a wide           → PULL-BACK
5. d wildcard       → scale→PULL-BACK · vertical→CRANE-UP · else PUSH-IN
```

**Healthy spread** (Enoch's verified 400): `PUSH 178 · PULL 123 · CRANE 72 · SETTLE 27`.
**A flatline is the failure signal.** So is any single block carrying >~15% settles.

### Hard rules

1. **One primary motion per beat.** Never two. Simultaneous complex motion is the #1 hallucination cause.
2. **Slow is fast.** Every move eases in. A weighted 40kg camera, never a snap. Slow reads as expensive and reduces drift.
3. **Lock the subject; move the camera.** A subject drifting through frame reads as error.
4. **Motivated by meaning, never a timer.** Timer-driven variety is the metronome problem in disguise.
5. **The still is locked first.** Kling only adds motion to a picked frame — the framing you chose is safe.

**Read the veto table.** Fix misclassifications by **correcting the register and re-deriving** — never by hand-picking a move.

---

## 8. THE FILM SPINE

**A feature is N blocks on a narrative spine — NOT N montages in a pile.**

```
[ TRAILER COLD-OPEN ]  45–90s · cut LAST · $0 · re-uses the best clip of each block
[ BLOCK 1 ] … [ BLOCK N ]  the escalating spine
[ CLOSING SEED ]  pays off the cold open's loop + hooks the sequel
```

- **Each block answers one question and opens two.**
- **Each block has its own emotional identity.** Never hold one register across blocks — that is viewer fatigue.
- **Thumbnail material in blocks 2–4.** Retention holds in the last three — they must be the strangest content, because that is where viewers leave.
- **The reflective block is the danger zone.** It needs your strangest frames and most motion, precisely because the VO goes quiet there.
- **The cold open is cut LAST.** You can only pick "the best shot of each block" once every block exists. Writing it first means promising something the film may not deliver.

### The proven competitor structure (2 transcripts, 21.4 and 27.0 min)

Winners are **pseudo-academic, not mystical.** They spend the opening third building authority before delivering anything, and **the payload arrives at minute six of twenty-one.**

```
block 1   the object          — a physical thing, not the phenomenon
block 2   authority           — named scholars, editions, dates · SUBSCRIBE ~3:00
block 3-5 payload             — title payoff lands at block 3
block 6   the human/angel     — why the text needs an explainer
block 7   the splice          — ancient text vs modern instrument (the retention engine)
block 8   hedge, then close   — the disclaimer at ~87%, then the sequel hook
```

**The hedge does triple duty:** credibility, a retention beat that resets the skeptic, and advertiser safety.

> **The competitors' authority layer is partly fabricated** — their researchers and measurements do not survive checking. **Do not copy that.** The real scholarship is better material. **Verify every name and date against a source before it enters narration.** A fabricated citation in a 24-minute film is a permanent liability. *This is the §5 attribution moat made operational — the frame flirts with the claim, the narration never asserts it in our own voice.*

Measured comps: **3,000 words / 21.4 min / 140 WPM** and **3,625 / 27.0 / 134**. Elliot at 143 is already matched. **Target 3,000–3,600 words = 8 blocks.**

---

## 9. PIPELINE MAPPING (existing code, no new engine)

| step | command | cost |
|---|---|---|
| ingest beats → storyboard | `stills --beats … --project … --storyboard-only` | **$0** |
| render stills | `stills --beats … --project …` | $0.08 ea |
| re-render one still | `restill` | $0.08 |
| routing/cost preview | `finish --project … --kling-count 40 --plan` | **$0** |
| animate only | `finish --project … --animate-only --kling-count 40 --no-music` | $0.42/clip |
| re-stitch existing | `finish --assemble-only` | $0 |

**Facts you must not re-learn the hard way:**
- **There is no `animate` subcommand.** It's `finish`. `--animate-only` stops after clips — correct when cutting in Filmora.
- **The animate leg reads `storyboard.json`, NOT `beats.json`.** No storyboard → everything animates with `_default_motion` and your derived motion is silently discarded. **`--storyboard-only` ingest is MANDATORY.**
- **`_tiered_kling_count` reads `render_policy.json`, not `channel.json`.** Pass `--kling-count 40` explicitly.
- **`--plan` is the definitive pre-spend answer.** Free. Use it every time.
- Stills cache is **filename-based**. Never re-render into a folder with output — fresh `-vN` folders.
- Module default `IMAGE_MODEL` is `flux` (the murk styliser). `image_model: nano_banana_2` must be explicit in `channel.json`.
- **Never restart `mission-control.service` mid-animate** — the cgroup teardown kills the leg.
- **All config and code flows laptop → git → box.** Never hand-edit on the box.

**New code for this pathway: one script.** Beat table CSV in → block SSML out → whisper measure → delta-adjust → re-render → gate. Everything else exists.

---

## 10. THE PATHWAY

### PHASE 0 — PACKAGING FIRST
**Title and thumbnail before a word of script.** Packaging at the end, tired, is the proven failure. *(See `<channel>/DOCTRINE.md` for the format.)*

### PHASE 1 — GATE THE GRADE ($0)
`style_suffix` = **palette only** (colour, materials, mass, brightness, anti-murk negatives). **No light source, no shafts, no blanket shadow** — those are content and belong in beats. Confirm `image_model: nano_banana_2`. Laptop → commit → push → pull on box. **Verify with a check that distinguishes EVERY known-bad grade**, not just the one you're thinking about — a storm-only check passes a warm-daylight suffix with flying colours.

### PHASE 2 — THE BEAT TABLE ($0)
Write it. All columns except `picked_variant`, `air`, `motion`, `seed`. Gate: word ceiling, sentence grouping, hero/connective split.

### PHASE 3 — PROBE THE REGISTER ($1.60)
20 stills, **2 per block, register-spread** (most-cosmic + most-earthly beat per block). Never uniform-random — it can hand you 20 cosmic beats and never test the daylight half, which is the half a bad suffix wrecks. Any material change since the last probe earns a new probe, **re-weighted toward the change.**

### PHASE 4 — RENDER STILLS, ONE RUN (~$8/block)
Fresh `-vN` folders. Free `--storyboard-only` sweep across all blocks first. One unattended tmux loop.
> **Batch the machine work. Chunk the human work.** The block boundary buys nothing at render time — it exists to protect your eye.

### PHASE 5 — CAROUSEL, ONE BLOCK PER SITTING
100 stills → 40 winners. **The 160→40 pick is gospel and will never be automated — it is the creative act.** Everything else is plumbing. Fill `air` and `picked_variant` as you go — both are reads off the frame in front of you. **Back up the picks record.**

### PHASE 6 — DERIVE + INGEST ($0)
`build_finish.py emit` → derives `beat × variant × register` → `beats.json`, `picks.json`, veto table. **Read the veto table.** `place` copies picked frames in beat order. Then `--storyboard-only` on every finish project and **read `storyboard.json`**: N×40 shots, **zero OTHER/DEFAULT**.

### PHASE 7 — PLAN, THEN FIRE ($0, then ~$17/block)
`--plan` every block. Then tmux: `finish … --animate-only --kling-count 40 --no-music`.

### PHASE 8 — NORMALISE + GATE ($0)
`-frames:v 120 -c copy`. ffprobe every output. **Hard-fail anything not 120 frames / 5.000000s.**

### PHASE 9 — VO, LAST (§4)
**Audio renders after the clips are measured** — it is the only layer that bends. One request per block. Whisper → delta → re-render. Pad to 200.000s. Gate.

### PHASE 10 — FILMORA (the human leg)
> **Dump the clips and the single VO file. Then inspect, adjust, add music, and put craft where it matters.**

Clips land `shot_001..040` in beat order → import a block, they lay themselves out. Drop the block WAV. **No nudging.** If you are adjusting audio timing in Filmora, the gate failed upstream — fix it there.

**Filmora is the creative layer, not the repair layer:** music, transitions, seams, confirmation.

### PHASE 11 — COLD OPEN, CUT LAST ($0)
From the best clip of each block. No new renders.

### PHASE 12 — CHAPTERS
**Arithmetic.** Block N starts at (N−1) × 200.000s. Auto-hyperlink needs first = `0:00`, ≥3 chapters, ≥10s apart. Give chapter titles drama, never production labels.

---

## 11. PRE-SPEND CHECKLIST

**Before stills (~$8/block):**
- [ ] packaging done — title + thumbnail exist
- [ ] `style_suffix` = palette only, no welded light/shafts/shadow
- [ ] **every beat names its own scene light** (§3A.2 — the other half of the palette-only gate; an unlit prompt renders muddy)
- [ ] **locked place-phrase written per setting, pasted VERBATIM into every beat in the scene**
- [ ] `image_model: nano_banana_2` verified **on the box**
- [ ] verify screens **every** known-bad grade
- [ ] register probe passed (spread across the axis)
- [ ] any material change since last probe → **new probe**
- [ ] beat table gate: ≤10 words/beat · ~380 words/block · sentences contiguous · hero/connective assigned
- [ ] **narration prosody: em-dashes over full stops · every number spelled out · read aloud** (§3A.1 — a see-saw script will not converge in §4's delta pass)
- [ ] **variety law: no two consecutive beats share framing, angle or scale**
- [ ] **escalation countable: something changes every 4–8 rows**
- [ ] fresh `-vN` folders
- [ ] `--storyboard-only` sweep clean on all blocks
- [ ] prompts: 0 empty · **0 grade-leak** · **0 literal metaphors** · 100% ASCII · counts match `variants`

**Before Kling (~$17/block):**
- [ ] carousel integrity: 40 picks · **no dupes · no missing** — every block
- [ ] picks record backed up · seeds logged
- [ ] `air` and `picked_variant` filled for all 40
- [ ] veto table read; spread rotates (not flat); no block >~15% settles
- [ ] `place` → 40 files, `shot_001..040`
- [ ] **`--storyboard-only` ingest on every finish project**
- [ ] `storyboard.json`: N×40 shots, **0 OTHER/DEFAULT**
- [ ] `--plan` clean: 40 → 40 Kling
- [ ] tmux; nothing will restart `mission-control.service`

**Before assembly ($0 but load-bearing):**
- [ ] every clip: **120 frames / 5.000000s**
- [ ] break tags **≤20 per request**
- [ ] whisper delta ≤±150ms on every beat
- [ ] block WAV = **200.000s exactly**
- [ ] manifest complete: beat → variant → seed → clip → timestamp

---

## 12. SUPERSEDED — THE LEDGER

**Name the departure; never silently reinterpret.**

| was | now | why |
|---|---|---|
| VO rides *above* the visuals, loosely coupled, deliberately | **Beat table: exact per-clip sequence** | Loose coupling was a workaround for timing you couldn't measure. Whisper retires it — you can afford tight coupling because you can now observe rather than predict. The pick stays free-standing; narration is per-row. |
| ~430 words/block | **~380, 10-word ceiling** | 430 = 0.49s air/clip. A hero beat forced neighbours to the 11.9-word ceiling. This is why it always felt like juggling. |
| 160 stills, 4 variants every beat | **~100, variable by weight** | §0. Pick data: wildcard 36%, mid 20%. |
| `a, b, c, d` | **`a, c, d1, d2`** | The mid is the weakest variant. The authored hero shot beat every formula variant. |
| 100% Kling — no Ken-Burns floor in a feature | **Animator derived from `air`** | §0 — a blanket. Flat air on Ken Burns is correct, not a compromise. |
| NEAR-LOCKED (5 moves) | **4 moves under VO** | A locked frame under continuous VO reads as a stalled slideshow. Retained for montages. |
| Clips are 5s | **Clips are 5.041667s → trimmed to 5.000** | Measured. Kling ships 121 frames, non-deterministically. |
| Compute chapters from `durations.json`, never estimate | **Chapters are arithmetic** | The drift is gone, so the estimate is now exact. |
| Script is king | **Container king · table emperor · script a column** | The clip won; audio renders last. |
| **Shot length 2–4s escalation / 3–6s emotional / 6–10s awe** | **pace is WORD DENSITY, bounded 6–13** | The 5.000s grid is fixed. The bounded word budget is the pace instrument — which is why it is bounded, never equal. |
| **Genre overlay (apocryphal):** half-seen figures, soft movement, let imagination do part of the work | **the Balrog principle — render it physically real and massive** | The register cleanse hit three `channel.json` files and three channel docs and **never touched the shared authoring contract.** "Half-seen" is darkness-hides-model-weakness stated as craft. |
| **Genre overlay (divine):** "reverence over spectacle" · "never reduce a miracle to spectacle" | **wonder and spectacle — "holy cow, look at THAT"** | Pre-pivot. `reverent` is a banned word on Sacred Dawn. Wonder is a magnet; doom is a downer. |
| **Opening Law vs the block structure** — apparent contradiction | **the COLD OPEN carries the Opening Law; block 1 opens on the object** | The cold open buys the right to be patient. Both rules survive intact. |

---

## 13. FUTURE — WHAT THE TABLE ALREADY SURVIVES

- **Canon / characters.** Already built: `{tokens}` in the VISUAL, `canon` block in `channel.json`, `reference_map` for images, `_expand_canon` raising on an unknown tag. **Never a new column, never inline in `narration`.** *(I proposed an `entities` column on 17 Jul before reading the engine — wrong; the existing mechanism is better, because it hard-fails at translate time rather than at render.)*
- **Lip sync.** Works: the grid is arithmetic, so a dialogue WAV drops at a known timestamp with no negotiation. Costs a **rule inversion** — narration must yield, which means a break tag, which spends from the 20. A track problem (narration / dialogue / music) plus a break-budget problem. Not a timing problem.
- **Chained scenes (continuous takes).** `scene_id` groups contiguous rows; one motion move across the group. **But chaining kills the parallel pick** — clip N+1's input depends on your pick of N, so the session goes serial, and compounding drift degrades clip 4 visibly from clip 1. **Buys continuity, spends the scarcest resource. One or two hero sequences. Never a default.**

### The two things this document does not solve

1. **The pick.** 800 stills per film, never automated, and the real ceiling on how many shots you take.
2. **Packaging.** Fixed in one evening for the price of one sentence and one image: **1.4% → 6.3% CTR.** No pipeline work will ever beat that ratio. *Every problem solved here was arithmetic pretending to be craft. The pick and the packaging are the parts that are actually craft.*
