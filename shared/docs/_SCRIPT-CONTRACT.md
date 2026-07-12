# _SCRIPT-CONTRACT.md
### The non-negotiable authoring contract for the movie channels
**Governs:** Sacred Dawn · Scripture On Screen · Synthetic Press
**Status:** Binding. Not a spec, not a guide. A script that does not pass this contract does not enter the batch.

---

## 0. HOW TO USE THIS CONTRACT

**Load line (start every scripting session with exactly this):**
> "Load `_SCRIPT-CONTRACT.md`. We are writing **[topic]** for **[channel]**. Go."

**The one rule that makes this a contract:**
> **Contract-passed (§1) is the precondition for batch-eligible.** Batch-of-batches runs unattended and has no gate of its own. Therefore the human gate lives *here*, upstream, at authoring time. A script that has not passed §1 may not be placed in a `batch_inbox/`. No exceptions, no "I'll check it after the run."

**Scope boundary (enforced — this is how this doc avoids becoming the old ante-machinam sprawl):**
> This contract governs **authorship only**. The test for whether anything belongs in this file: **does it change a word, a prompt, or an image on the page?** Beat format, narration, motion direction, character tokens, register — yes. Box IP, restart law, floor-first internals, OAuth, scheduling — **no**. A scripting session never needs to know the pipeline exists. Keep it that way.

**Channel is a parameter, not a fork.** One contract, three channels. The channel selects a register block (§7) and whether the character system (§4) is heavy, light, or off. Everything else is identical.

---

## 1. THE PRE-BATCH CHECKLIST — THE GATE

A script is **batch-eligible only when every box is true.** Run this before it touches an inbox.

- [ ] **Opening interrogated.** The first beat is the most arresting image in the film's first 30 seconds — the point of maximum stakes, **not** the chronological start. (See §5 THE OPENING LAW. This is the beat that earns or loses the next 354. Gate it first, gate it separately.)
- [ ] **First N beats word-counted.** Every KLING beat (default N=40) is authored to **~15 words / ≤5 seconds** so its atom plays as-is. No KLING beat under the channel's word threshold.
- [ ] **Tokens valid.** Every `{Name}` in a VISUAL line resolves to a key in the channel's `base_canon` + `reference_map` (and a real `refs/<name>.png`). No orphan tokens.
- [ ] **Casting pass done** (character channels only). Every recurring `{Name}` has a locked reference PNG in `<channel>/refs/`, eyeballed once. (See §4.)
- [ ] **40 stills carouselled.** After the first render, `scp` the first-40 stills to a local folder and click through them in Finder. React as a viewer — boring? wrong register? drift? Fix at the script, not the grid.
- [ ] **The Final Test passed** (§5 / §6): no beat that fails to increase curiosity, emotion, danger, mystery, consequence, beauty, awe, dread, scale, or urgency. If a beat does none — cut it.

**The gate in one line:** the human review you are *not* doing downstream happens *here* — in the script, the casting pass, and the 40-stills carousel — and batch-of-batches only ever runs scripts that cleared it.

---

## 1A. THE WRITING PROCESS — BUILD A SCRIPT IN PASSES

*How a scripting session is actually run. Read this before writing a single beat — it is the difference between a script that holds quality end to end and one that starts sharp and goes lethargic by the back half.*

### Why long scripts drift (the constraint, stated plainly)
A feature script is long — often several hundred beats. Producing all of it in one unbroken stretch of writing is where quality quietly fails, and it helps to understand *why*, because the fix follows directly from the cause.

The writer (an AI author) is **not forgetting the rules** — everything in this contract stays fully visible the entire time. The problem is different: across a very long single stretch of generation, the writing increasingly takes its cues from **the text already written** rather than from the rules at the top. The momentum of the previous three hundred beats starts to outweigh the contract. Adherence drifts — word counts creep, the prosody flattens back into full-stop see-saw, the hold taper is forgotten, structure turns formulaic and repetitive. This shows up as two opposite failure shapes, and both are the same underlying drift:
- **Too many thin beats** — racing to cover the story, the writer produces a flood of under-written beats.
- **Bloated, lethargic beats** — padding each beat toward some imagined length target, producing long beats that then force stretched, sludgy visuals.

Neither is a knowledge failure. Both are drift under **volume**. So volume is the thing to control.

### The fix: passes, re-anchored, checked
Never write a whole film in one pass. Break it into short passes, each small enough that every rule in this contract holds for the *entire* pass, and re-state the live targets at the start of each one so the contract is re-anchored rather than assumed. The seams:

1. **OUTLINE pass — structure first, zero beats.** Before any beat exists, decide: the title promise; the cold-open image (the peak you open on, never the chronological start); the act structure; where the emotional peaks fall; which handful of moments (~40) earn animation; and the cast list (which named characters recur, so they can be locked *before* scripting). This is a small number of decisions and it becomes the through-line every later pass writes against. Structure decided once, small, does not drift.

2. **COLD-OPEN pass — the opening, alone.** Write only the opening stretch that has to hook. It is the highest-stakes writing in the film and holds most of the animation budget, so it gets its own dedicated, unhurried pass. Then render its stills and click through them in a plain folder view, reacting as a viewer — arresting? on-register? drift-free? Fix at the script. The opening earns the rest of the film; treat it that way.

3. **ACT passes — one act at a time.** Write the body one act per pass, against the outline — roughly **thirty to fifty beats per pass**. Keep passes this size on purpose: it is the volume at which full compliance holds. At the top of each act pass, restate the live targets — words per animation beat, the prosody rule, and the hold length for where you are in the film (longer early, tighter late) — so the contract is re-anchored, not drifting.

4. **COMPLIANCE check after every pass — cheap, before moving on.** Scan the pass just written: are the animation beats within the word target? Is the narration flowing on dashes and commas, not pumping on full stops? Are the holds tapering? Any character token with no locked reference? Catching drift *per pass* stops it compounding — a slip that enters in act two and is caught in act two never reaches act five.

### The human rhythm, and the rule of thumb
Between passes, the human reviews and re-anchors; the writer does not barrel from outline to final beat unattended. **Short passes, a check between each, the contract restated at the top of every one.** That rhythm is how a long film gets written at full quality instead of decaying by the back half — it is the same anti-lethargy principle the hold-taper and tight-beat rules enforce inside the film, now applied to the act of writing it.

**Rule of thumb: if one pass is producing more than ~50 beats, it is too big — split it.** Volume is the enemy of compliance; passes are how you beat it.

---

## 2. THE BEAT TEMPLATE — THE FORMAT CONTRACT

**The live grammar is `[A]`.** Every cinematic beat (still or Kling) is a **Mode A** beat, tagged `[A]`. (`[B:Component]` = Remotion graphic overlay — Synthetic only; Scripture and Sacred Dawn do not use Mode B.) There is **no `[BEAT NN]` / `KLING` / `KB` tag** — the parser only understands `[A]` and `[B:...]`, and anything else mis-parses. KLING-vs-KB is **not** a tag; it is decided two ways below.

**How a beat becomes KLING (animated) vs KB (still):**
1. **Positional (v1 routing):** the first N beats (N=40) render Kling via floor-first / `kling_count`; the rest fall to the free Ken-Burns still floor. This is existing engine behaviour — no change.
2. **Per-beat signal:** a beat that carries a **`MOTION:` line** is authored as an animate beat; a beat with **no `MOTION:` line** is a still. The parser already extracts `MOTION:` per beat and treats an authored motion as a deliberate override. (v2 option: route Kling by "has MOTION line" instead of position — deferred.)

**A KLING (animate) beat** — an `[A]` beat, within the first N, authored to ~15 words, **with** a MOTION line:
```
[A]
Narration text sits on its own line(s) — ~15 words, authored to fill ~5 seconds.
VISUAL: shot size, angle, light, subject, register suffix; use {Name} to mark a registered character.
MOTION: one primary camera/subject move — see §6 CAMERA MOVES.
```

**A KB (still) beat** — an `[A]` beat with **no** MOTION line:
```
[A]
Narration text — written for the image and the sentence, sized to its hold.
VISUAL: a SELF-CARRYING frame (see below); shot size, angle, light, subject, register suffix; {Name} to mark a character.
```
- No `MOTION:` line → a slow programmatic push (Ken-Burns) is applied automatically.
- **Hold taper: 6–10 s early → 2–6 s by the end.** Open with longer holds (6–10 s) on the awe and reflection beats you want the viewer to sit inside; then tighten holds steadily as the film runs, down to 2–6 s through the back half. A long film stays alive on a *quickening cut-rate* — the back end is carried by stills changing faster, never by longer holds and never by motion.
- **Never stretch a clip or add slow-motion to fill time.** If a stretch of narration runs long, that is the signal to break it into more beats (more stills) — not to hold one still longer or slow an animation to cover the words. Stretched clips and slow-motion reads as lethargy and kills pace. The cure for a long, sludgy passage is always *more beats*, never *slower ones*.
- **A still beat's narration fits its hold — never a wall of text on one image.** At a normal speaking pace a 2–10 s hold is roughly **6–28 words**; that is the working band. If a still beat pushes past ~28 words, split it into two beats (two stills). A high word-count on a single beat is the classic way a script goes lethargic — long beats force stretched visuals.
- **THE SELF-CARRYING STILL (the prompting discipline for every KB beat).** A still cannot lean on motion — so composition does 100% of the work. Prompt every still as a **single frame that must stop the scroll on its own**: one clear subject · strong silhouette · decisive light on the story point · real foreground/midground/background depth · negative space that frames the subject. **The test, applied per still: could this frame be the thumbnail?** If it couldn't survive as a poster, it is under-composed — fix it before it ships. (The §6 hero-shot rule is this pushed hardest on the peak beats; but *every* still gets poster-grade intent.)

**Fast cutting = one flowing narration, broken into beats at the punctuation.** This is the single most important authoring mechanic in the contract, and it does three jobs at once. Write a passage of narration as **one continuous thought — clauses joined by dashes and commas** (this is also the prosody rule, §5) — then **break it into beats at those connectors.** Each beat carries one clause and gets its own still or clip; the dashes hold the voice in one unbroken contour across all of them, so the *visuals* cut rapidly while the *narration* flows as a single breath. **One beat = one still; the beats are Lego blocks of a larger narration block.** This is how you get montage-speed cutting with no special mechanism — the renderer makes one still per beat, and the writing does everything else.
- **Break only at a real connector — a dash, a comma, the end of a clause. Never mid-phrase.** The connector is both the join (for the voice) and the legal cut point (for the visual). Splitting mid-phrase makes the audio and the picture fight.
- **Example.** One narration block — *"The sky over the field turned black — twelve thousand men rose from the treeline — and stepped into the open, straight into the guns"* — becomes three beats: [black sky] / [the line rising] / [the advance into fire]. Three stills, three cuts, one unbroken spoken breath.

**Field discipline:**
- Every `[A]` beat has a `VISUAL:`. A beat with narration and no visual is a hard error (nothing to render — the engine's verify refuses it).
- `{Name}` tokens appear **in `VISUAL:` only** (they mark which registered character is in the shot). Write character names as **plain prose in narration** ("Elijah sat down…") — no tokens in narration, so nothing brace-shaped ever reaches TTS. See §4.

---


## 3. THE ALLOCATION RULE — KLING vs KB vs DURATION

**The whole allocation is decided by two numbers you author per beat: word count and visual count. It is arithmetic, not judgment.**

**The atom:** one Kling clip = **5.04 s**. At measured ~170 wpm (2.83 words/s), one atom ≈ **14 words**. Author KLING beats slightly over the line (~15 words / ~5.2 s) so they reliably clear one atom and play *as-is* — no stretch, no slow-motion distortion. The atom's own final-frame hold absorbs any sub-second tail. That held frame is the **only** clip micro-mechanism retained; all clip-stretching, mid-beat freezes, and wordless-beat surgery are **deleted** — authoring-to-the-atom makes them unnecessary.

**The default rule (v1 — the version you can debug tired):**
- **Beats 1–40 → KLING**, each ≤5 s / ~15 words, each with `VISUAL:` + `MOTION:`.
- **Beats 41–end → KB stills**, each holding 2–10 s on its own narration.
- Everything after beat 40 is written *however the story reads*; the measured window sets the hold. No word-counting on still beats.

**Placement (the one refinement that keeps "first 40" honest):** the 40 are fixed in **count, not position**. Tag KLING on the **cold open + each structural peak + the finale** (≈5–7 places marked at *outline* level — seven decisions, not 355), not merely the first 40 slots. Same budget, same cost, aimed where the story actually needs motion. "First 40" is a legitimate blunt v1; the day a beat-250 climax feels flat, the fix is moving three or four atoms to it, not new machinery.

**The dial (monetisation path):** N=40 (~$17 Kling) → 80 → 200 → full animation. Same "write fat + add MOTION" discipline, larger N. Full animation = every beat KLING. Raise the dial as revenue justifies it; the number is the only thing that changes.

**⚠ THE EXTEND-CHAIN — v2, NOT v1. Do not build or use for the first films.** A separate mechanism, filed with N=80+ as a later-when-monetised concern. When a scene needs >5 s of *continuous* motion (one sustained moment, not a cut to a new shot), chain atoms — atom A's last frame becomes atom B's init frame with a continuing motion prompt. When it lands in v2, the rules are:
- Use **only** for a sustained continuous moment (one crane over a battlefield, a slow walk to camera). If the next thing is a new composition, that is a new beat, not a link.
- **2–4 links max (~10–20 s).** Drift compounds per link; beyond ~4 the face will not survive.
- **Flagship emotional peaks only** — the opening crane, the finale that must breathe. The most expensive and most drift-prone tool in the kit. **v1 does not touch it.**

---

## 4. THE CHARACTER SYSTEM — `{Name}`

**Per-channel dial:** Scripture On Screen = **heavy** (recurring named cast, continuity across episodes). Sacred Dawn = **light/off** (anonymous cosmic drama). Synthetic Press = **light** (one-off named figures — Lee once on the horse). Same resolver, different registry depth.

**Register a character ONLY if they recur.** One appearance = inline prompt in that beat's `VISUAL:` (a character who appears once cannot drift from himself). Multiple appearances (same episode or across episodes) = a registry entry, because that is the only case where cross-instance drift is possible.

**The mechanism — it already exists in your engine (this is how QQrew renders its cast). Two keyed blocks inside `channel.json` + a `refs/` folder.**
```
<channel>/
  channel.json           ← holds base_canon (desc text) + reference_map (ref paths)
  refs/                   ← flat folder of locked reference PNGs (the REAL box layout)
    elijah.png            ← locked reference image, created once; key = filename basename
    elisha.png
    widow.png
```
In `channel.json` — the character's short description in `base_canon`, its ref path in `reference_map`, same keys in both:
```json
"base_canon": {
  "elijah": "Elijah, a weathered ancient Hebrew prophet with a grey-streaked dark beard in a rough camel-hair cloak",
  "elisha": "Elisha, a young ancient Hebrew man with a short dark beard in a plain homespun robe",
  "widow":  "the widow, a careworn older Phoenician woman in a worn headscarf and plain robes"
},
"reference_map": {
  "elijah": "refs/elijah.png",
  "elisha": "refs/elisha.png",
  "widow":  "refs/widow.png"
}
```
(Lead each description with the character's own name so it reads naturally when expanded inline into a prompt.)
**Convention: `base_canon` key = `reference_map` key = ref PNG basename = the lowercase `{token}`** (`{elijah}` ↔ `base_canon.elijah` ↔ `reference_map.elijah` ↔ `refs/elijah.png`). Identical everywhere, always lowercase, so a mismatch is obvious. (The engine loads `base_canon`, expands the `{token}` inline, and attaches the `reference_map` image down the `/edit` path — all already built.)

**⚠ `desc` is a SHORT identity TAG (~20 words MAX), not a portrait.** This is a hard, expensive lesson: a long character description *swamps the render* — the image model paints a static portrait of the person and never renders the action of the beat. Put only what must stay constant for glance recognition — build, hair, wardrobe, signature expression — and **strip photoreal/beauty words** ("smooth skin," "soft delicate features," "warm oval face"), which drag the render toward a still portrait. The reference image carries the face; the `desc` carries the wardrobe and silhouette in as few words as possible.

**⚠ Prompt order: put the SHOT FRAMING at the START of the VISUAL, the `{token}` in natural position.** The engine expands `{elijah}` into its description **inline, exactly where you place it** in the VISUAL line — so lead the VISUAL with the framing (shot size, angle, light), then let `{elijah}` sit in its natural place in the scene ("Wide low shot of {elijah} on the ridge…"). Never lead the VISUAL with the character. A description that leads starves the action and renders a static portrait — which is the whole reason the `desc` is kept short. The engine adds the look/style itself (it prepends `style_suffix` on plain beats, and wraps character beats in the reference lock), so you never write the style into a VISUAL line.

**Conditional per-beat reference — CONFIRMED in the engine.** The renderer already does exactly what mixed-cast films need: a beat whose VISUAL contains a `{token}` matching `reference_map` attaches that character's reference and renders through the `/edit` path with the channel's reverent reference-lock; a beat with **no** token renders through normal text-to-image with `style_suffix`. So character beats and character-less beats (the sea, a city, a dead riverbed) both work, automatically, off the presence or absence of a `{token}`. The `{token}` in the VISUAL is the selector — it is not cosmetic. **Two hard requirements for it to fire:** the token must be **lowercase and exactly match the key** in `base_canon` + `reference_map` (`{elijah}`, never `{Elijah}`), and every recurring character's description must live in **`base_canon`** (the key the engine reads), not any other key.

**Token resolution — `{Name}` lives in `VISUAL:` only:**
- **In `VISUAL:`** → `{elijah}` marks that a registered character is in the shot. The engine injects that character's **`desc`** into the render prompt **and** attaches that character's **`ref` image** down the `fal-ai/nano-banana-2/edit` reference path (the same mechanism that renders QQrew's cast from `base_canon` + `reference_map`).
- **In `NARRATION:`** → **do not use tokens.** Write the name as plain prose ("Elijah sat down beside Elisha"). Narration goes straight to TTS, so nothing brace-shaped may ever appear there.
- **Convention:** the token, the registry key, the `base_canon` key, and the ref basename are all the same lowercased name (`{elijah}` → `elijah` → `refs/elijah.png`).

**The casting pass (the one craft step, done once per film, before scripting is "done"):** generate candidates for each recurring character, pick the one that *is* them, save as `<name>.png`, eyeball once. This is the highest-value probe you will do — get the face right here and every beat inherits it. It is the character equivalent of the look-probe: cheap, upstream, one-time.

**Drift watchlist (the only places consistency can break):**
- **Multi-character shared frames** (two locked refs in one call) drift harder than one. Prefer single-character framing and CUT between them; reserve the shared frame for beats where the two-shot *is* the point, and eyeball those on the carousel.
- **Order matters** in a two-shot: keep visual token order matching the composition ("left figure {elijah}, right figure {elisha}").
- **Long extend-chains** — drift compounds per link (see §3).
- Everything anonymous is safe by default. Density is not the enemy of coherence — a *missing reference-lock* is. Reference-lock on = hundreds of stills stay coherent.

**✅ STATUS (confirmed against the code, not assumed).** The engine fully supports this — conditional per-beat reference works, the `{token}` mechanism works, no new engine code is needed. For **Scripture On Screen** specifically, everything is already wired (locked reference images, `reference_map`, reverent reference-lock, reverent `style_suffix`) **except one config bug**: the character descriptions currently sit under a key the engine does not read, so they must be moved into **`base_canon`**. Until that one key is fixed, any `{token}` in a Scripture VISUAL will crash with "unknown tag." **Synthetic and Sacred Dawn are anonymous-cinematic** and use no character tokens at all — they can author and batch against this contract right now, no character work required.

---

## 5. NARRATIVE PRINCIPLES — GOVERN `NARRATION`
*(Distilled from the First 40 Beats Playbook. Prescriptive. There is no interpretation.)*

### THE OPENING LAW (the highest-leverage rule in the whole contract)
- The title makes a promise. The thumbnail amplifies it. **The opening fulfils it in the first frame.** Never delay. Never explain first.
- **Open on impact, never on history.** Title "The Day Jerusalem Fell" → open on Jerusalem burning. "The Angels Who Fell" → open on the rebellion. A disaster film → open on the sky already on fire, the hand already on the lever — **not** two men writing a letter.
- **DEFCON 1.** Start at maximum intensity. No warm-up. No "today we're going to." No thanks, no apology, no throat-clearing. Drop the viewer into Act III of an epic already in motion.
- Structure is free to flash back *after* the peak — open on the collision, then earn the right to explain how it came.

### THE CURIOSITY ENGINE (the golden rule)
- **Never answer a question without opening a larger one.** Every reveal raises the stakes; every payoff earns a new gap. Curiosity never reaches zero.
- Run the loop: create question → hint → partial answer → unexpected twist → larger question → higher stakes → reward → repeat. Never fully close the loop.
- **Maintain an open-loop stack** — several unanswered questions live at once (What happened? Why? Who caused it? Who survived? Could it have been prevented? How bad does this get? Why has nobody told this? Can it happen again?). As one closes, another opens.
- **Reveal less, imply more.** Information reduces curiosity; discovery increases it. Only reveal a fact when it creates *more* questions. Never dump facts — weave them into drama.
- **End every section on a lean-forward:** "But then…" / "Nobody expected…" / "Everything was about to change."

### ESCALATION & EMOTION (every 20–40 seconds)
- **The audience must FEEL something every 20–40 seconds.** Rotate emotional states — wonder, fear, hope, shock, awe, dread, relief, disbelief, tension, triumph, reflection. Never hold one emotion long; the change refreshes attention.
- **Every section increases at least one:** scale, danger, mystery, consequence, emotion, urgency, spiritual/historical significance, human cost. If none increase — rewrite.
- **Reward constantly** — a shocking fact, a revelation, a cinematic line, a beautiful image — then immediately raise the next question. Never ask the viewer to wait.
- **Rhythm and contrast:** large moment → small intimate moment → reflection → escalation → silence → explosion. Constant loudness goes invisible. Pair opposites — big/small, hope/despair, silence/chaos, faith/fear, order/collapse. The greater the contrast, the greater the impact.
- **Dread over surprise:** let the audience know something terrible is coming before the characters do. **Inevitability:** build the sense of history moving toward an unavoidable collision the viewer must witness.

### THE HUMAN LENS
- **People move people, not statistics.** Anchor every epic event through one individual — one mother, soldier, priest, child, witness, survivor, prophet, disciple, angel, family.
- **Scale-shift** constantly: individual → family → city → nation → civilisation → humanity. The viewer keeps realising "this is bigger than I thought."
- **Disaster is never a number.** Show consequence — families, empty streets, ash, silence afterward. The emotional arc matters more than the destruction.

### THE SENTENCE & THE IMAGE
- **Visual narration only.** Not "many people died" but "a city where even the birds had stopped singing." Concrete imagery creates memory.
- **One unforgettable sentence every few paragraphs** — a trailer line: "The sky turned into fire." "The mountain answered." "An empire collapsed before breakfast."
- **Immersion is sensory:** sight, sound, smell, temperature, light, dust, smoke, wind, silence. Don't describe history — make them experience it.
- **Narrate like a witness, not Wikipedia.** Conviction, not hedging. Avoid uncertainty unless uncertainty is the point.

### NARRATION FOR THE EAR — PROSODY (VO-QUALITY, NON-NEGOTIABLE)
*The narration is not read — it is spoken by TTS. Punctuation is prosody control. These rules are as binding as the story rules; they decide whether the voice sounds broadcast or robotic.*
- **Kill the see-saw. Dampen full stops.** Too many periods in a row make TTS fall to a terminal (sentence-final) pitch again and again — the read pumps up-and-down, the "see-saw." **Replace most periods with em-dashes and commas** so the voice holds a continuation contour and flows. One long flowing sentence with dashes reads far better than four short stops. Reserve the full stop for a deliberate, weighted landing — then it *means* something.
  - *See-saw:* "The sky went black. The men advanced. Nobody moved. It was too late." → four terminal falls.
  - *Flowing:* "The sky went black as the men advanced — and nobody moved, because it was already too late." → one contour, one landing.
- **This is the *punctuation* see-saw, which you fix on the page.** It is distinct from a separate *architectural* see-saw (where the voice engine re-attacks its prosody at every beat boundary because beats are voiced one at a time) — that one is fixed at the engine level by synthesising longer continuous voice runs, not by the writer. Author for the punctuation see-saw; both matter.
- **Spell every number out in narration.** "Twelve thousand," not "12,000"; "the ninth century," not "the 9th." Digits get mangled or misread by TTS. (Numbers may appear as digits in a VISUAL line — that's for the image, not the voice.)
- **Write for the breath.** Read each line aloud in your head. If you run out of breath or stumble, the TTS will too — break it or re-dash it. Punctuation is where the voice breathes; place it on purpose.

### TRUTH & AUTHORITY
- **Prove extraordinary claims immediately** — historical evidence, eyewitness accounts, ancient texts, archaeology, scripture, contemporary records. Show it is grounded.
- **Never exaggerate.** Reality is already extraordinary; truth told cinematically beats fiction exaggerated.
- **Alternate story and fact** — story → fact → story → reveal → emotion. Never long explanatory blocks.

### GENRE OVERLAYS
- **Biblical — Spiritual Awe:** never reduce a miracle to spectacle. Reverence, mystery, grandeur, weight. The viewer should feel small before the event.
- **Apocryphal:** lean into mystery — forbidden texts, hidden history, lost knowledge — but clearly distinguish established history from tradition/interpretation.
- **Disaster:** the arc, not the blast — normality → recognition → fear → impact → silence → aftermath → human response.

### THE FIVE-MINUTE MAP
1. **0–15 s** — immediate visual payoff; biggest promise; highest stakes; massive curiosity.
2. **15–45 s** — prove the promise; establish credibility; increase mystery.
3. **45–90 s** — introduce the central conflict; open several loops.
4. **90–150 s** — first reveal; replace it with a larger mystery.
5. **150–240 s** — expand scale dramatically; raise emotional investment; introduce the human anchor.
6. **240–300 s** — a satisfying emotional payoff; open the next chapter; make leaving psychologically expensive.

### THE FINAL TEST
> Every paragraph must increase at least one of: curiosity, emotion, danger, mystery, consequence, beauty, awe, dread, scale, urgency. **If it does none — cut it.** The 40-beats mantra: Promise · Prove · Escalate · Reveal · Complicate · Reward · Escalate again. Never coast. Never plateau.

---

## 6. VISUAL PRINCIPLES — GOVERN `VISUAL` + `MOTION`
*(Distilled from the Cinematic Motion Playbook. Prescriptive.)*

### THE VARIETY LAW (the top rule — everything below serves it)
- **No two consecutive beats may share framing, angle, scale, or pace.** Every beat must differ from the one before it on **at least one axis**: high/low, close/far, wide/tight, fast/slow, warm/cold, loud/still, subject/environment. Repetition is invisibility — the eye stops seeing what stops changing.
- **Rotate every axis across the film:** extreme-wide → wide → medium → close → extreme-close and back; eye-level → low → high; hold → cut → motion; warm → cold. Never settle into a groove.
- **The one guardrail — variety is motivated, never mechanical.** You cut wide because the narration *widened*, low because the moment gained *power*, fast because the story *accelerated* — not on a timer. Variety serves the sentence. Timer-driven variety is just the metronome problem wearing a different costume.
- **Motion has purpose or it does not happen.** Every camera move answers one question: *what emotion should the audience feel?* No emotional purpose → no move (write it as KB).
- **The camera is invisible.** Move with intention, as a real 40 kg camera on a precision dolly would — never because the AI *can*. Natural beats spectacular.
- **Physically possible by default.** Reserve impossible movement for the supernatural — miracles, angelic appearances, visions, apocalypse, divine encounter.
- **Slow is fast.** Slow movement reads as expensive, gives the eye time to absorb, *and* reduces AI hallucination. The camera breathes — eases in, accelerates gently, settles. Never start or stop abruptly.

### CAMERA MOVES (the `MOTION:` vocabulary — pick ONE primary per beat)
- **Push-in** — the single most powerful move. Revelations, prophecies, dread, divine encounters, emotional speeches. Quietly increases pressure.
- **Pull-back** — reveal scale/consequence: armies, cities, destruction, heaven, apocalypse. "This is bigger than I imagined."
- **Crane** — vertical = emotional scale. Ascending = epic; descending = intimate. Reserve big cranes for major peaks.
- **Orbit** — slow arcs only, ~20–30° max. Fast circles read synthetic.
- **Track / dolly / gentle parallax** — measured, weighted, purposeful.

### COMPOSITION
- **Depth always.** Foreground, midground, background — columns, smoke, people, dust, clouds. Never one flat plane. Parallax makes worlds believable.
- **Hero shot every 20–30 s** — one composition that could be a movie poster, thumbnail, or painting. The viewer should remember individual frames.
- **Strong silhouettes** for angels, prophets, kings, cities, crosses, mountains, ships, temples. Simple shapes are remembered.
- **Faces retain.** Eyes create emotion. When emotion matters, move closer and let the audience read the expression — faces outperform landscapes emotionally.
- **Alternate scale and framing** constantly: extreme-wide → wide → medium → close → extreme-close → wide. Never repeat the same framing back-to-back.
- **Angle with intent:** eye-level = honesty (use most). Low angle = power (kings, giants, angels, tsunamis, walls of fire). High angle = vulnerability (victims, survivors, ruins, isolation). POV sparingly, for immersion.

### LIGHT, COLOUR, ATMOSPHERE
- **Light guides the eye.** Brightest point = story point. Faces usually carry the strongest readable light unless another object is the intentional focal point. Never compete with your own subject.
- **Colour evolves with the narrative** — warm hope, cold uncertainty, fiery climax, quiet ash-grey aftermath. Colour is emotional storytelling.
- **Air is never empty** — dust, mist, snow, rain, smoke, ash, embers, fog, light rays. Atmosphere creates depth and scale.
- **Cloth and environment move** — robes, capes, flags, hair, smoke, ash, drifting light. Small ambient motion makes a still feel alive (and is drift-safe).

### RHYTHM & IMPACT
- **Stillness is a weapon.** Before every major event, slow down — almost stop. Silence increases impact; the motion after feels larger.
- **Don't animate explosions continuously.** Sequence it: stillness → impact → shockwave → aftermath → recovery. Contrast creates power.
- **Match-cut on visual similarity** — a torch becomes a burning city; a tear becomes rain; a feather becomes falling ash. Elegant transitions reduce fatigue.
- **Sync major camera moves to audio** — music builds, percussion hits, revelations, silence.

### DRIFT CONTROL (the AI-stability rules — non-negotiable)
- **One primary motion per beat**, plus subtle secondary ambient motion. Never everything moving equally — simultaneous complex motion is the #1 hallucination cause.
- **Lock the subject, move the camera.** A stable anchored subject reads as intentional; a subject drifting through frame reads as error.
- **The subject moves *less*.** Large exaggerated body movement increases AI errors — let the environment (cloth, smoke, dust) carry the motion.
- **Consistency:** same clothing, age, facial structure, hair, armour, lighting logic, direction of travel across a character's beats.
- **Cut before failure.** AI shots are strongest in their opening moments. End early — the audience remembers quality. (This is why the atom plays as-is and the tail holds on the final frame.)
- **Simple beats complex.** One elegant move almost always looks more expensive than five competing ones.

### SHOT LENGTH (per beat texture)
- **3–6 s** emotionally rich scenes · **2–4 s** escalation · **6–10 s** awe / reflection. Avoid long static AI shots unless pristine.

### GENRE OVERLAYS
- **Divine (biblical):** God is not frantic motion — immense scale, light, silence, slow movement, weight, majesty. Reverence over spectacle.
- **Apocryphal:** half-seen figures, ancient ruins, dust-filled libraries, moonlit mountains, soft movement, unknown shapes. Let imagination do part of the work.
- **Disaster:** show normality → recognition → fear → impact → silence → aftermath, not only the destruction.

### THE CINEMATIC TEST
> Pause on any frame. Could it be mistaken for a still from a $200M feature? If not — fix composition, light, depth, colour, silhouette, subject placement, negative space. **Final doctrine: the audience should think "I feel like I'm there," never "look at the animation." The camera is not the hero. The story is.**

---

## 7. THE GOLD-STANDARD REFERENCE SCENE
*A worked cold open. Every element correct: DEFCON-1 opening, flash-back-after-peak structure, `{Name}` resolution, KLING word-counting, KB stills, purpose-driven motion, human anchor, cinematic sentence, open loops. Copy this shape.*

**Channel:** Scripture On Screen · **Film:** *The Prophet Who Declared War on the Sky* · **Register (§7 block):** Ren voice; liturgical-cinematic; teal-gold biblical grade; reverence over spectacle.

> **WRONG opening** (chronological, low-stakes — the Hiroshima error): "In the ninth century BC, the kingdom of Israel was ruled by a king named Ahab…" — history first. Delete.
> **RIGHT opening** (open on the peak, DEFCON 1): fire falling from heaven on Mount Carmel — the film's climax, teased cold — *then* flash back.

```
[A]
Fire fell from a cloudless sky and swallowed the altar whole — stone, water, and the dust beneath it.
VISUAL: Extreme low angle, night. A column of white fire descending onto a stone altar on a mountaintop; awestruck crowd in silhouette below; teal-gold grade, embers in the air.
MOTION: Slow push-in on the falling fire; embers drifting upward; subtle heat shimmer.
  # animate beat (has MOTION); 18 words → ~6.4 s → clears the 5.04 s atom, plays as-is

[A]
A thousand people fell on their faces in the same instant.
VISUAL: High angle, wide. A vast crowd prostrate on scorched rock, faces to the ground, one figure still standing among them. Firelight raking across them, deep shadows.
  # still beat (no MOTION line) → Ken-Burns floor

[A]
Elijah did not flinch as the flames roared past him, close enough to feel their breath.
VISUAL: Medium, eye-level. {elijah} standing motionless before the wall of white fire, camel-hair cloak whipping, face lit gold, unafraid.
MOTION: Locked subject; the fire and cloak move, he does not. Slow, almost imperceptible push.
  # animate beat; 15 words → ~5.3 s. Narration = plain "Elijah"; VISUAL {elijah} pulls his desc + ref

[A]
But three years before this mountain, before the fire, there was only silence — and a sky that had forgotten how to rain.
VISUAL: Extreme wide, high angle, muted grey-ochre. A cracked, dead riverbed winding through a starving kingdom; a lone figure walking its length. Dust haze, no green anywhere.
  # still beat

[A]
The land was dying. The people were dying. And no one knew why.
VISUAL: Close, eye-level. A child's cracked lips and hollow eyes, a dry clay water jar tipped empty beside her. Harsh flat light, dust on skin.
  # still beat

[A]
Elijah walked into the throne room and told the most powerful king in Israel it would not rain.
VISUAL: Wide two-shot, low angle favouring the throne. Left figure {elijah}, ragged and calm; right figure a heavy-bearded king enthroned in gold, half-risen in fury. Shafts of hard light, deep parallax of columns behind.
MOTION: Slow track from Elijah toward the throne across the hall — one continuous move, camera weighted.
  # animate beat; 18 words → ~6.4 s. {elijah} is registered (desc+ref). The king is plain prose — NOT tokened — because he has no locked ref; register him only if he recurs enough to matter (then cast an ahab.png)

[A]
The king's face changed. He had heard threats before. He had never heard one delivered like a sentence already carried out.
VISUAL: Extreme close, low angle. The king's eyes — fury curdling into fear. Gold and shadow, a single catchlight.
  # still beat; king still inline-prose (no ref) — accept mild cross-beat drift, or cast him

[A]
Elijah turned, walked out of the palace, and vanished into the wilderness for three burning years.
VISUAL: Wide, eye-level, silhouette. {elijah} walking out through a blazing palace doorway into white desert light, back to camera, robe trailing dust.
MOTION: Slow pull-back as he recedes into the light — revealing the scale of the emptiness he walks into.
  # animate beat; 16 words → ~5.6 s
```

**Why this passes the contract:** opens on the peak (fire), not the chronology; every animate beat carries a MOTION line and clears the atom by word count; still beats hold on image + sentence with no MOTION line; `{Name}` appears in VISUAL only while narration keeps plain names, so nothing brace-shaped reaches TTS; the registered cast ({elijah}) is tokened, the un-cast king is inline prose; the two-shot (throne beat) flagged for a carousel drift-check; one cinematic sentence per stretch; open loops stacked (why the drought? who is this man? what happens on that mountain?); reverence over spectacle throughout; one primary motion per animate beat with the subject locked and the environment carrying the movement.

---

*This contract is loaded at the start of every scripting session and is the sole gate on batch-eligibility. It governs authorship only. When a scripting session banks a genuinely new authoring rule, graduate it into this file — and keep it ruthlessly scoped, or it becomes the sprawl it replaced.*
