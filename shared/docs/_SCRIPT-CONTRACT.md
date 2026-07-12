# _SCRIPT-CONTRACT.md
### The non-negotiable authoring contract for the movie channels
**Governs:** Sacred Dawn · Scripture On Screen · Synthetic Press
**Status:** Binding. Not a spec, not a guide. A script that does not pass this contract does not enter the batch.
**Proven:** the beat format, the character system, and the per-beat routing in this contract were validated end to end on a real 10-still render. What follows is how the machine actually behaves, not a proposal.

---

## 0. HOW TO USE THIS CONTRACT

**Load line — start every scripting session with exactly this:**
> "Load `_SCRIPT-CONTRACT.md`. We are writing **[topic]** for **[channel]**. Go."

That one paste is the whole setup. It carries the format, the rules, and a worked example — everything needed to go straight to writing. No other context is required, and none should be pasted in.

**The one rule that makes this a contract:**
> **Contract-passed (§1) is the precondition for batch-eligible.** The batch runner is unattended and has no quality gate of its own. Therefore the human gate lives *here*, upstream, at authoring time. A script that has not passed the §1 checklist may not be placed in an inbox. No exceptions, no "I'll check it after the run."

**Scope boundary — the discipline that keeps this file lean:**
> This contract governs **authorship only**. The test for whether anything belongs in it: **does it change a word, a prompt, or an image on the page?** Beat format, narration, motion direction, character tokens, register — yes. Server details, deployment, scheduling, upload plumbing — **no**. A scripting session never needs to know how the pipeline runs. Keep it that way, or this doc rots into the sprawl it replaced.

**Channel is a parameter, not a fork.** One contract, three channels. The channel selects a register (voice, look, grade) and how heavily the character system (§4) is used. Everything else is identical.

---

## 1. THE PRE-BATCH CHECKLIST — THE GATE

A script is **batch-eligible only when every box is true.** Run this before it touches an inbox.

- [ ] **Opening interrogated.** The first beat is the most arresting image in the film's first 30 seconds — the point of maximum stakes, **not** the chronological start. (See §5 THE OPENING LAW. This one beat earns or loses the whole film — gate it first, gate it separately.)
- [ ] **Animation beats word-counted.** Every animate beat (default: the first 40) is authored to **~15 words / ≤5 seconds** so its clip plays as-is. No animate beat under the word threshold.
- [ ] **Tokens valid.** Every `{token}` in a VISUAL line is lowercase and matches a registered character key exactly (and a real reference image exists for it). No orphan tokens.
- [ ] **Casting locked** (character films only). Every recurring character has a locked reference image, eyeballed once. (See §4.)
- [ ] **Probe passed.** The first 40 beats have been rendered and reviewed as stills in a plain folder carousel — reacting as a viewer: arresting? on-register? faces holding? Character beats and landscape beats reading as *one film*? Fix at the script. (See §1A for the probe mechanic.)
- [ ] **The Final Test passed** (§5): no beat that fails to increase curiosity, emotion, danger, mystery, consequence, beauty, awe, dread, scale, or urgency. If a beat does none — cut it.

**The gate in one line:** the review you are *not* doing downstream happens *here* — in the script, the casting, and the stills carousel — and the batch only ever runs scripts that cleared it.

---

## 1A. THE WRITING PROCESS — BUILD A SCRIPT IN PASSES

*How a scripting session is actually run. Read this before writing a single beat — it is the difference between a script that holds quality end to end and one that starts sharp and goes lethargic by the back half.*

### Why long scripts drift (the constraint, stated plainly)
A feature script is long — often several hundred beats. Producing all of it in one unbroken stretch of writing is where quality quietly fails, and it helps to understand *why*, because the fix follows directly from the cause.

The writer (an AI author) is **not forgetting the rules** — everything in this contract stays fully visible the entire time. The problem is different: across a very long single stretch of generation, the writing increasingly takes its cues from **the text already written** rather than from the rules at the top. The momentum of the previous three hundred beats starts to outweigh the contract. Adherence drifts — word counts creep, the prosody flattens back into full-stop see-saw, the hold taper is forgotten, structure turns formulaic. This shows up as two opposite failure shapes, and both are the same underlying drift:
- **Too many thin beats** — racing to cover the story, the writer floods out under-written beats.
- **Bloated, lethargic beats** — padding each beat toward an imagined length target, forcing long beats and stretched, sludgy visuals.

Neither is a knowledge failure. Both are drift under **volume**. So volume is the thing to control.

### The fix: passes, re-anchored, checked
Never write a whole film in one pass. Break it into short passes, each small enough that every rule holds for the *entire* pass, and re-state the live targets at the top of each one so the contract is re-anchored, not assumed. The seams:

1. **OUTLINE pass — structure first, zero beats.** Decide: the title promise; the cold-open image (the peak you open on, never the chronological start); the act structure; where the emotional peaks fall; which ~40 moments earn animation; and the cast list (which named characters recur, so they can be locked *before* scripting). A small number of decisions that become the through-line every later pass writes against. Decided once, small, it does not drift.

2. **COLD-OPEN pass — the opening, alone.** Write only the opening stretch that has to hook. It is the highest-stakes writing in the film and holds most of the animation budget, so it gets its own dedicated, unhurried pass. Then **probe it** (below) and carousel the stills as a viewer. The opening earns the rest of the film; treat it that way.

3. **ACT passes — one act at a time.** Write the body one act per pass, against the outline — roughly **thirty to fifty beats per pass**. Keep passes this size on purpose: it is the volume at which full compliance holds. At the top of each act pass, restate the live targets — words per animation beat, the prosody rule, and the hold length for where you are in the film (longer early, tighter late).

4. **COMPLIANCE check after every pass — cheap, before moving on.** Scan the pass: are the animate beats within the word target? Is the narration flowing on dashes and commas, not pumping on full stops? Are the holds tapering? Any token with no locked reference? Catching drift *per pass* stops it compounding — a slip that enters in act two and is caught in act two never reaches act five.

### The probe mechanic (how "render and carousel" actually works)
Rendering stills is driven by a **beats file** — never by pasting anything into a terminal. Two modes, both one command:

- **10-beat probe (optional).** A quick, representative/adversarial ten beats — a few tokened character beats, a two-shot, a couple of character-less landscapes/objects — to sanity-check faces, two-shots, routing, and register on a throwaway before committing to the film. ~$0.30.
- **First-40 (compulsory).** The real film's opening 40, rendered and carouselled as the batch-eligibility gate.

Both run the same way: a **dry pass first** (zero spend) prints the per-beat routing table — which beats attached a character reference and which fell through to plain render — so you confirm the tokens resolved before spending a cent. Then the same command without the dry flag renders the stills; pull them and click through in a folder view. The only per-session act is authoring the beats; everything mechanical around it is one command.

### The human rhythm, and the rule of thumb
Between passes, the human reviews and re-anchors; the writer does not barrel from outline to final beat unattended. **Short passes, a check between each, the contract restated at the top of every one.** That rhythm is how a long film gets written at full quality instead of decaying by the back half — the same anti-lethargy principle the hold-taper and tight-beat rules enforce inside the film, now applied to the act of writing it.

**Rule of thumb: if one pass is producing more than ~50 beats, it is too big — split it.** Volume is the enemy of compliance; passes are how you beat it.

---

## 2. THE BEAT TEMPLATE — THE FORMAT CONTRACT

**The grammar is `[A]`.** Every cinematic beat — still or animated — is a beat tagged `[A]`, with narration on its own line(s) plus a `VISUAL:` line and, for animate beats, a `MOTION:` line. There is **no per-beat "KLING"/"KB"/numbered tag** — the parser understands `[A]`, and anything else mis-parses. Whether a beat animates or holds is decided two ways, below, not by a tag.

**How a beat becomes animated vs a still:**
1. **Positional (the default).** The first N beats (N=40) animate; the rest are free Ken-Burns stills. This is the existing routing — nothing to add.
2. **Per-beat signal.** A beat that carries a **`MOTION:` line** is authored as an animate beat; a beat with **no `MOTION:` line** is a still. (A later option routes animation by "has a MOTION line" instead of position — deferred; the positional default is what ships now.)

**An ANIMATE beat** — within the first N, authored to ~15 words, **with** a MOTION line:
```
[A]
Narration on its own line — ~15 words, authored to fill ~5 seconds.
VISUAL: shot size, angle, light, subject; put {token} in natural position to mark a registered character.
MOTION: one primary camera or subject move — see §6 CAMERA MOVES.
```

**A STILL beat** — no MOTION line:
```
[A]
Narration — written for the image and the sentence, sized to its hold.
VISUAL: a SELF-CARRYING frame (see below); shot size, angle, light, subject; {token} to mark a character.
```
- No `MOTION:` line → a slow programmatic push (Ken-Burns) is applied automatically.
- **Hold taper: 6–10 s early → 2–6 s by the end.** Open with longer holds on the awe/reflection beats you want the viewer to sit inside; tighten steadily as the film runs, down to 2–6 s through the back half. A long film stays alive on a *quickening cut-rate* — the back end is carried by stills changing faster, never by longer holds and never by motion.
- **Never stretch a clip or add slow-motion to fill time.** If a stretch of narration runs long, break it into more beats (more stills) — do not hold one still longer or slow an animation to cover the words. Stretched clips and slow-motion read as lethargy and kill pace. The cure for a long, sludgy passage is always *more beats*, never *slower ones*.
- **A still beat's narration fits its hold — never a wall of text on one image.** At a normal speaking pace a 2–10 s hold is roughly **6–28 words**; that is the working band. Past ~28 words, split into two beats. A high word-count on a single beat is the classic way a script goes lethargic.
- **THE SELF-CARRYING STILL.** A still cannot lean on motion, so composition does 100% of the work. Prompt every still as a **single frame that must stop the scroll on its own**: one clear subject · strong silhouette · decisive light on the story point · real foreground/midground/background depth · negative space that frames the subject. **The test, per still: could this frame be the thumbnail?** If it couldn't survive as a poster, it is under-composed. (The §6 hero-shot rule is this pushed hardest on the peaks; but *every* still gets poster-grade intent.)

**Fast cutting = one flowing narration, broken into beats at the punctuation.** This is the single most important authoring mechanic in the contract, and it does three jobs at once. Write a passage as **one continuous thought — clauses joined by dashes and commas** (this is also the prosody rule, §5) — then **break it into beats at those connectors.** Each beat carries one clause and gets its own still or clip; the dashes hold the voice in one unbroken contour across all of them, so the *visuals* cut rapidly while the *narration* flows as a single breath. **One beat = one still; the beats are Lego blocks of a larger narration block.** Montage-speed cutting with no special mechanism — the renderer makes one still per beat, and the writing does the rest.
- **Break only at a real connector — a dash, a comma, a clause end. Never mid-phrase.** The connector is both the join (for the voice) and the legal cut point (for the visual). Splitting mid-phrase makes audio and picture fight.
- **Example.** One block — *"The sky over the field turned black — twelve thousand men rose from the treeline — and stepped into the open, straight into the guns"* — becomes three beats: [black sky] / [the line rising] / [the advance into fire]. Three stills, three cuts, one unbroken spoken breath.

**Field discipline:**
- Every `[A]` beat has a `VISUAL:`. A beat with narration and no visual is a hard error — the engine refuses it.
- `{token}` tokens appear **in `VISUAL:` only.** Write character names as **plain prose in narration** ("Elijah sat down…") — no tokens in narration, so nothing brace-shaped ever reaches the voice. See §4.

---

## 3. THE ALLOCATION RULE — ANIMATE vs STILL vs DURATION

**The allocation is decided by one number you author per beat: word count. It is arithmetic, not judgment.**

**The clip length:** one animation clip = **~5 seconds**. At a normal speaking pace (~170 wpm, ~2.8 words/second), five seconds ≈ **14 words**. Author animate beats slightly over the line (~15 words / ~5.2 s) so they reliably fill one clip and play *as-is* — no stretch, no slow-motion distortion. The clip's own final-frame hold absorbs any sub-second tail. That held frame is the **only** clip micro-mechanism retained; clip-stretching, mid-beat freezes, and wordless-beat surgery are all **deleted** — authoring-to-the-clip makes them unnecessary.

**The default rule (the version you can debug tired):**
- **Beats 1–40 → animate**, each ≤5 s / ~15 words, each with a `VISUAL:` + `MOTION:`.
- **Beats 41–end → stills**, each holding 2–10 s on its own narration, written however the story reads.

**Placement — the 40 are fixed in *count*, not *position*.** Tag animation on the **cold open + each structural peak + the finale** (≈5–7 places, marked at *outline* level — seven decisions, not 355), not merely the first 40 slots. Same budget, same cost, aimed where the story actually needs motion. "First 40 by position" is a legitimate blunt start; the day a late climax feels flat, move three or four animate beats to it — no new machinery.

**The dial (as revenue grows):** 40 animate beats → 80 → 200 → full animation. Same "write fat + add MOTION" discipline, larger N. Raise it as monetisation justifies; the number is the only thing that changes.

**⚠ THE EXTEND-CHAIN — LATER, not now. Do not build or use for the first films.** When a scene needs >5 s of *continuous* motion (one sustained moment, not a cut), clips are chained — each clip's last frame seeds the next with a continuing motion prompt. When it lands:
- Use **only** for a sustained continuous moment (one crane over a battlefield, a slow walk to camera). A new composition is a new beat, not a link.
- **2–4 links max (~10–20 s).** Drift compounds per link; beyond ~4 the face will not survive.
- **Flagship emotional peaks only** — the opening crane, the finale that must breathe. The most expensive and most drift-prone tool in the kit. The first films do not touch it.

---

## 4. THE CHARACTER SYSTEM — `{token}`
*Proven on a real render: recurring characters held their faces and wardrobe across every beat, a two-character shot kept both distinct, and character-less beats rendered clean with no reference. This is how it works — use it as documented.*

**Per-channel dial:** Scripture On Screen = **heavy** (recurring named cast, continuity across episodes). Sacred Dawn = **light/off** (anonymous cosmic drama). Synthetic Press = **light** (one-off named figures). Same mechanism, different depth.

**Register a character ONLY if they recur.** One appearance = describe them inline in that beat's `VISUAL:` (a character who appears once cannot drift from himself). Multiple appearances — same film or across episodes — = a registry entry, the only case where cross-instance drift is possible.

### The mechanism (already built in the engine — do not re-invent it)
A registered character is three linked things, all keyed by the same lowercase name:
- a **short description** in the channel's `base_canon`,
- a **reference image path** in the channel's `reference_map`,
- a **locked reference PNG** in the channel's `refs/` folder.

```
<channel>/
  channel.json     -> base_canon (short descriptions) + reference_map (ref paths)
  refs/            -> the locked reference PNGs
    elijah.png
    elisha.png
    widow.png
```
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

**Convention — one lowercase name, everywhere identical:** the `{token}`, the `base_canon` key, the `reference_map` key, and the ref basename are all the same lowercase word (`{elijah}` ↔ `base_canon.elijah` ↔ `reference_map.elijah` ↔ `refs/elijah.png`). Lead each description with the character's own name so it reads naturally when the engine expands it inline into a prompt.

### How a `{token}` resolves (VISUAL only)
When a VISUAL line contains `{elijah}`, the engine does two things automatically: it **expands** `{elijah}` into that character's description, in place, and it **attaches** that character's reference image so the render preserves the exact face and wardrobe. A beat with **no** token renders normally, with the channel's look. This per-beat conditional behaviour is what makes mixed-cast films work — character beats and character-less beats (the sea, a city, a dead riverbed) both come out right, off the presence or absence of a token.

**Two hard requirements, or it fails:**
- **Lowercase, exact match.** `{elijah}`, never `{Elijah}` — a capitalised or misspelled token matches nothing, attaches no reference, and errors on expansion.
- **The description lives in `base_canon`.** That is the key the engine reads. A description filed anywhere else is invisible and the token will error.

### The three authoring rules that keep character renders clean
- **⚠ The description is a SHORT identity TAG (~20 words max), not a portrait.** A long character description *swamps the render* — the model paints a static portrait and never renders the action. Keep only what must stay constant for glance recognition: build, hair, wardrobe, signature expression. **Strip beauty/photoreal words** ("smooth skin," "soft delicate features," "warm oval face") — they drag the render toward a frozen portrait. The reference image carries the face; the description carries the wardrobe and silhouette, briefly.
- **⚠ Framing first, token in natural position.** Lead the VISUAL with the shot (size, angle, light), then let the token sit where it naturally falls in the scene ("Wide low shot of {elijah} on the ridge…"). Never lead a VISUAL with the character. Leading with the character starves the action — which is the other reason the description stays short. Never write the channel's look/style into a VISUAL line; the engine adds that itself.
- **⚠ Register-match — every beat in ONE grade, and the enemy is MURK, not saturation.** *(Banked across renders: character beats [reference path] and character-less beats [text-to-image] can drift apart in grade and break the "one film" feel — but the real failure mode is soft, dark, painterly murk, NOT rich colour. Killing the murk by neutralising the colour was an over-correction; the fix is to lift the light, not drain the palette.)* The target is one shared grade on both paths: **bright, chromatic, crisp, high-contrast, high dynamic range — desert gold and deep lapis, clean vivid light — Bay/Woo blockbuster energy, but the camera worships the phenomenon, never a glamorised hero.** Saturation is not the problem; softness, muddy shadows, and washed-out haze are. The channel-config lever (done once per channel) is to match the plain-render look (`style_suffix`) to the character-render look (the reference lock) so both sit in that same bright-chromatic-crisp grade. The authoring lever: **specify light BRIGHT and CLEAN** — the model defaults dark and murky when light is left unspecified — and never soft-painterly-hazy. Judge on the carousel: if a beat looks murky, muddy, or washed-out, *lift its light*; don't cool its colour.

### Casting, and the drift watchlist
**The casting pass** (once per film, before scripting is "done"): generate candidates for each recurring character, pick the one that *is* them, lock it as `<name>.png`, eyeball once. The highest-value probe you will do — get the face right here and every beat inherits it.

**Where consistency can break (the only places):**
- **Two-character frames** — two references in one shot drift harder than one. Prefer single-character framing and cut between them; reserve the shared frame for beats where the two-shot *is* the point, and eyeball those on the carousel. *(On the validation render the two-shot held — but it is the beat to watch.)*
- **Token order in a two-shot** — keep the visual order matching the composition ("left figure {elijah}, right figure {elisha}").
- **Long extend-chains** — drift compounds per link (see §3; not in the first films).
- Everything anonymous is safe by default. Density is not the enemy of coherence — a *missing* reference is. With references locked, hundreds of stills stay consistent.

**Status by channel:** **Scripture On Screen** is fully live and proven — cast locked, registry wired, per-beat routing confirmed on a render. **Synthetic and Sacred Dawn** are anonymous-cinematic and use no character tokens — they author and batch against this contract with no character work at all.

---

## 4A. SETTING CONTINUITY — PIN THE PLACE ACROSS EVERY BEAT IN A SCENE
*The character system locks WHO is in the shot. This locks WHERE. Place drifts exactly like an unlocked character — and it is just as visible.*

A scene rendered as several independent stills will invent several different locations — a canyon in one beat, a bare plateau in the next, a city that should not exist in a third — unless the setting is pinned. Each still is internally fine; they simply do not agree on where we are. That inter-shot drift breaks the illusion of one continuous place as badly as a face that changes between shots. It is the single most common way a multi-shot scene falls apart, and it is pure authoring — the fix costs nothing but discipline.

**The rule: every beat that shares a setting carries the same setting, specified in detail and repeated verbatim.**

- **Write the setting once, as a locked phrase** — the invariant identity of the place: terrain, material, defining features, and explicit negatives. Example: *"the bare rocky summit of Mount Carmel — pale weathered stone, dry scrub, scattered grey boulders, open wilderness, no buildings, no city, no structures."*
- **Paste that exact phrase into the VISUAL line of every beat in the scene.** Identical wording pulls the independent renders toward the same place. Do not paraphrase it beat to beat — **verbatim repetition is the mechanism**, the same way an identical `{token}` re-attaches an identical face.
- **Add explicit negatives for what the model wrongly adds.** "Biblical" pulls toward "ancient city," so a wilderness scene must say "no buildings, no city." Deserts sprout structures, throne rooms sprout windows — the model omits nothing unless told.
- **Let framing detail vary; keep the identity fixed.** A looking-up shot shows sky, a wide shot shows the valley below — that visible detail changes per beat, but the locked identity phrase stays word-for-word the same in all of them.
- **A new setting = a new locked phrase.** When the scene moves — mountaintop → throne room → wilderness — write a fresh locked phrase for the new place and repeat *that* one verbatim across its beats. One phrase per location, held for the length of the scene.

The robust version, later, is a locked setting **image** — a `reference_style_anchor` plate attached to every beat in a scene, so place is reference-anchored the way a character's face is. *(Render-learned this session: the verbatim phrase pulls the beats much closer to one place but does NOT fully eliminate drift — a canyon still crept into one shot of a locked-summit scene. So the phrase is a real reduction, not a cure. The `reference_style_anchor` plate is the true fix and is now a priority build, not a "someday" — it's the same $0.08 edit-path mechanism the character refs already use, currently read-but-unwired in the engine.)*

---

## 5. NARRATIVE PRINCIPLES — GOVERN `NARRATION`
*Prescriptive. There is no interpretation.*

### THE OPENING LAW (the highest-leverage rule in the whole contract)
- The title makes a promise. The thumbnail amplifies it. **The opening fulfils it in the first frame.** Never delay, never explain first.
- **Open on impact, never on history.** "The Day Jerusalem Fell" → open on Jerusalem burning. "The Angels Who Fell" → open on the rebellion. A disaster film → open on the sky already on fire, the hand already on the lever — **not** two men writing a letter.
- **Maximum intensity from frame one.** No warm-up, no "today we're going to," no thanks, no throat-clearing. Drop the viewer into Act III of an epic already in motion.
- Structure is free to flash back *after* the peak — open on the collision, then earn the right to explain how it came.

### THE CURIOSITY ENGINE (the golden rule)
- **Never answer a question without opening a larger one.** Every reveal raises the stakes; every payoff earns a new gap. Curiosity never reaches zero.
- Run the loop: create question → hint → partial answer → unexpected twist → larger question → higher stakes → reward → repeat. Never fully close the loop.
- **Keep an open-loop stack** — several unanswered questions live at once (What happened? Why? Who caused it? Who survived? Could it have been prevented? How bad does this get? Why has nobody told this? Can it happen again?). As one closes, another opens.
- **Reveal less, imply more.** Information reduces curiosity; discovery increases it. Reveal a fact only when it creates *more* questions. Never dump facts — weave them into drama.
- **End every section on a lean-forward:** "But then…" / "Nobody expected…" / "Everything was about to change."
- **Every 30 seconds is its own trailer.** Treat each ~30-second stretch as a self-contained hook whose only job is to make the next one impossible to skip. Nothing exists purely to explain — every line pulls forward.

### ESCALATION & EMOTION (every 20–40 seconds)
- **The audience must FEEL something every 20–40 seconds.** Rotate states — wonder, fear, hope, shock, awe, dread, relief, disbelief, tension, triumph, reflection. Never hold one emotion long; the change refreshes attention.
- **Every section increases at least one:** scale, danger, mystery, consequence, emotion, urgency, spiritual/historical significance, human cost. If none increase — rewrite.
- **Reward constantly** — a shocking fact, a revelation, a cinematic line, a beautiful image — then immediately raise the next question. Never ask the viewer to wait.
- **Rhythm and contrast:** large moment → small intimate moment → reflection → escalation → silence → explosion. Never hold one *tempo* either — fast, then pause, then reveal, then fast, then silence, then escalate; the audience follows rhythm subconsciously. Constant loudness goes invisible. Pair opposites — big/small, hope/despair, silence/chaos, faith/fear, order/collapse. The greater the contrast, the greater the impact.
- **Dread over surprise:** let the audience know something terrible is coming before the characters do. **Inevitability:** build the sense of history moving toward a collision the viewer must witness.

### THE HUMAN LENS
- **People move people, not statistics.** Anchor every epic event through one individual — one mother, soldier, priest, child, witness, survivor, prophet, disciple, angel, family.
- **Scale-shift** constantly: individual → family → city → nation → civilisation → humanity. The viewer keeps realising "this is bigger than I thought."
- **Disaster is never a number.** Show consequence — families, empty streets, ash, silence afterward. The emotional arc matters more than the destruction.

### THE SENTENCE & THE IMAGE
- **Visual narration only.** Not "many people died" but "a city where even the birds had stopped singing." Concrete imagery creates memory.
- **One unforgettable sentence every few paragraphs** — a trailer line: "The sky turned into fire." "The mountain answered." "An empire collapsed before breakfast."
- **Immersion is sensory:** sight, sound, smell, temperature, light, dust, smoke, wind, silence. Don't describe history — make them experience it.
- **Narrate like a witness, not an encyclopedia.** Conviction, not hedging. Avoid uncertainty unless uncertainty is the point.

### NARRATION FOR THE EAR — PROSODY (VO-QUALITY, NON-NEGOTIABLE)
*The narration is not read — it is spoken. Punctuation is prosody control. These rules are as binding as the story rules; they decide whether the voice sounds broadcast or robotic.*
- **Kill the see-saw. Dampen full stops.** Too many periods in a row make the voice fall to a terminal (sentence-final) pitch again and again — the read pumps up-and-down, the "see-saw." **Replace most periods with em-dashes and commas** so the voice holds a continuation contour and flows. One long flowing sentence with dashes reads far better than four short stops. Reserve the full stop for a deliberate, weighted landing — then it *means* something.
  - *See-saw:* "The sky went black. The men advanced. Nobody moved. It was too late." → four terminal falls.
  - *Flowing:* "The sky went black as the men advanced — and nobody moved, because it was already too late." → one contour, one landing.
- **Spell every number out.** "Twelve thousand," not "12,000"; "the ninth century," not "the 9th." Digits get mangled by the voice. (Numbers may appear as digits in a VISUAL line — that's for the image, not the voice.)
- **Write for the breath.** Read each line aloud in your head. If you run out of breath or stumble, the voice will too — break it or re-dash it. Punctuation is where the voice breathes; place it on purpose.

### TRUTH & AUTHORITY
- **Prove extraordinary claims immediately** — historical evidence, eyewitness accounts, ancient texts, archaeology, scripture, contemporary records. Show it is grounded.
- **Never exaggerate.** Reality is already extraordinary; truth told cinematically beats fiction exaggerated.
- **Alternate story and fact** — story → fact → story → reveal → emotion. Never long explanatory blocks.

### GENRE OVERLAYS
- **Biblical — spiritual awe:** never reduce a miracle to spectacle. Reverence, mystery, grandeur, weight. The viewer should feel small before the event.
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
> Every paragraph must increase at least one of: curiosity, emotion, danger, mystery, consequence, beauty, awe, dread, scale, urgency. **If it does none — cut it.** The mantra: Promise · Prove · Escalate · Reveal · Complicate · Reward · Escalate again. Never coast. Never plateau.

---

## 6. VISUAL PRINCIPLES — GOVERN `VISUAL` + `MOTION`
*Prescriptive.*

### THE VARIETY LAW (the top rule — everything below serves it)
- **No two consecutive beats may share framing, angle, scale, or pace.** Every beat differs from the one before it on **at least one axis**: high/low, close/far, wide/tight, fast/slow, warm/cold, loud/still, subject/environment. Repetition is invisibility — the eye stops seeing what stops changing.
- **Rotate every axis across the film:** extreme-wide → wide → medium → close → extreme-close and back; eye-level → low → high; hold → cut → motion; warm → cold. Never settle into a groove.
- **The one guardrail — variety is motivated, never mechanical.** Cut wide because the narration *widened*, low because the moment gained *power*, fast because the story *accelerated* — not on a timer. Variety serves the sentence; timer-driven variety is the metronome problem in a different costume.

### MOTION DISCIPLINE
- **Motion has purpose or it does not happen.** Every camera move answers one question: *what emotion should the audience feel?* No purpose → no move (write it as a still).
- **The camera is invisible.** Move with intention, as a real weighted camera on a dolly would — never because the tool *can*. Natural beats spectacular.
- **Physically possible by default.** Reserve impossible movement for the supernatural — miracles, angelic appearances, visions, apocalypse.
- **Slow is fast.** Slow movement reads as expensive, gives the eye time to absorb, *and* reduces AI hallucination. The camera breathes — eases in, accelerates gently, settles. Never start or stop abruptly.
- **Avoid the fatigue movers.** No constant handheld, no spinning, no perpetual drone drift, no rapid random motion. Unstable images create fatigue and motion sickness; stable images build trust. Prefer locked shots, slow dolly, slow crane, gentle orbit, measured tracking.

### CAMERA MOVES (the `MOTION:` vocabulary — pick ONE primary per beat)
- **Push-in** — the single most powerful move. Revelations, prophecies, dread, divine encounters, emotional speeches. Quietly increases pressure.
- **Pull-back** — reveal scale/consequence: armies, cities, destruction, heaven, apocalypse. "This is bigger than I imagined."
- **Crane** — vertical = emotional scale. Ascending = epic; descending = intimate. Reserve big cranes for major peaks.
- **Orbit** — slow arcs only, ~20–30° max. Fast circles read synthetic.
- **Track / dolly / gentle parallax** — measured, weighted, purposeful.

### COMPOSITION
- **Depth always.** Foreground, midground, background — columns, smoke, people, dust, clouds. Never one flat plane.
- **Hero shot every 20–30 s** — one composition that could be a movie poster. The viewer should remember individual frames.
- **Strong silhouettes** for prophets, kings, angels, cities, crosses, mountains, ships, temples. Simple shapes are remembered.
- **Faces retain.** Eyes create emotion. When emotion matters, move closer — faces outperform landscapes emotionally.
- **Alternate scale and framing** constantly. Never repeat the same framing back-to-back.
- **⭐ Scale needs a human face at the bottom of the frame (the signature blockbuster move — all three movie channels).** Spectacle reads as *majestic*, not merely big, when one small human witnesses it: the vast event filling the frame above and behind, and one weathered face or lone silhouette dwarfed beneath it. This is the marriage of **blockbuster scale and reverent smallness** — Bay/Woo grade and energy on the surface, Attenborough's humility underneath: the camera worships the *phenomenon*, never glamorises the hero. Never render the fireball, the flood, the collapsing city *alone* — render the small human beneath it. The awe lives in the size difference. (This is the visual form of the Human Lens, §5 — and the one move the spray-and-pray incumbents skip.)
- **Angle with intent:** eye-level = honesty (use most). Low angle = power (kings, giants, angels, tsunamis, walls of fire). High angle = vulnerability (victims, survivors, ruins, isolation). POV sparingly, for immersion.

### LIGHT, COLOUR, ATMOSPHERE
- **Light guides the eye.** Brightest point = story point. Faces usually carry the strongest readable light unless another object is the intentional focal point. Never compete with your own subject.
- **Colour evolves with the narrative** — warm hope, cold uncertainty, fiery climax, quiet ash-grey aftermath.
- **Air is never empty** — dust, mist, snow, rain, smoke, ash, embers, fog, light rays. Atmosphere creates depth and scale.
- **Keep the register consistent — one grade across the whole film** *(see §4 register-match)*. The enemy is *murk* (soft, dark, painterly, muddy), not saturation. The look is bright, chromatic, crisp, high-contrast — reach for rich desert-gold/lapis freely; just keep the light **clean**, never hazy or washed-out.
- **Specify light BRIGHT — the model defaults dark and murky when light is left unspecified.** Every beat names its scene light (clear gold dawn, blazing clean afterglow, vivid twilight). An unlit prompt renders muddy.
- **Negations grow from evidence, never speculation.** Add a negative ("no murk," "no modern objects," "no muddy shadows") only for a failure class you have actually seen render wrong. Speculative negation vetoes the model's best output — do not pre-emptively ban things that haven't gone wrong.
- **Cloth and environment move** — robes, capes, flags, hair, smoke, ash, drifting light. Small ambient motion makes a still feel alive (and is drift-safe).

### RHYTHM & IMPACT
- **⭐ A spectacle is a SEQUENCE of hero shots, never one composite frame (render-proven this session).** The instinct is to cram the whole miracle — the fire, the altar, the prophet, the crowd — into a single image. It always fails: the phenomenon shrinks to a prop (fire on an altar reads as a campfire) and nothing is a hero shot. Instead, *stage the moment across several beats, each a distinct hero frame*: the phenomenon gets its **own** beat with nothing else in it (the column of fire tearing down from a hole in black cloud — no altar, no man), then the strike, then the human reaction, then the aftermath. This is the fast-cutting rule (§2) applied to the peak, and it is the single move that separates "the film that shocked the world" from a barbecue. Proven on the Mount Carmel cold open: the composite read as a campfire; the six-beat sequence read as a scene.
- **Stillness is a weapon.** Before every major event, slow down — almost stop. Silence increases impact; the motion after feels larger.
- **Don't animate explosions continuously.** Sequence it: stillness → impact → shockwave → aftermath → recovery. Contrast creates power.
- **Match-cut on visual similarity** — a torch becomes a burning city; a tear becomes rain; a feather becomes falling ash.
- **Sync major camera moves to audio** — music builds, percussion hits, revelations, silence.

### DRIFT CONTROL (the AI-stability rules — non-negotiable)
- **One primary motion per beat**, plus subtle secondary ambient motion. Never everything moving equally — simultaneous complex motion is the #1 hallucination cause.
- **Lock the subject, move the camera.** A stable anchored subject reads as intentional; a subject drifting through frame reads as error.
- **The subject moves *less*.** Large exaggerated body movement increases errors — let the environment (cloth, smoke, dust) carry the motion.
- **Consistency:** same clothing, age, facial structure, hair, direction of travel across a character's beats.
- **Cut before failure.** Clips are strongest in their opening moments. End early — the audience remembers quality. (This is why the clip plays as-is and the tail holds on the final frame.)
- **Simple beats complex.** One elegant move almost always looks more expensive than five competing ones.

### SHOT LENGTH (per beat texture)
- **3–6 s** emotionally rich scenes · **2–4 s** escalation · **6–10 s** awe / reflection. Avoid long static shots unless pristine.

### GENRE OVERLAYS
- **Divine (biblical):** God is not frantic motion — immense scale, light, silence, slow movement, weight, majesty. Reverence over spectacle.
- **Apocryphal:** half-seen figures, ancient ruins, dust-filled libraries, moonlit mountains, soft movement. Let imagination do part of the work.
- **Disaster:** show normality → recognition → fear → impact → silence → aftermath, not only the destruction.

### THE CINEMATIC TEST
> Pause on any frame. Could it be mistaken for a still from a $200M feature? If not — fix composition, light, depth, colour, silhouette, subject placement, negative space. **Final doctrine: the audience should think "I feel like I'm there," never "look at the animation." The camera is not the hero. The story is.**

---

## 7. THE GOLD-STANDARD REFERENCE SCENE
*A worked cold open. Every element correct: open-on-the-peak, flash-back structure, `{token}` resolution, animate-beat word-counting, still beats, purpose-driven motion, human anchor, cinematic sentence, open loops. Copy this shape.*

**Channel:** Scripture On Screen · **Film:** *The Prophet Who Declared War on the Sky* · **Register:** liturgical-cinematic; grounded photoreal biblical grade; reverence over spectacle.

> **WRONG opening** (chronological, low-stakes): "In the ninth century BC, the kingdom of Israel was ruled by a king named Ahab…" — history first. Delete.
> **RIGHT opening** (open on the peak): fire falling from heaven on the mountain — the film's climax, teased cold — *then* flash back.

```
[A]
Fire fell from a cloudless sky and swallowed the altar whole — stone, water, and the dust beneath it.
VISUAL: Extreme low angle, night. A column of white fire descending onto a stone altar on a mountaintop; awestruck crowd in silhouette below; embers in the air.
MOTION: Slow push-in on the falling fire; embers drifting upward; subtle heat shimmer.
  # animate beat (has MOTION); 18 words -> ~6.4 s -> fills the clip, plays as-is

[A]
A thousand people fell on their faces in the same instant.
VISUAL: High angle, wide. A vast crowd prostrate on scorched rock, faces to the ground, one figure still standing among them. Firelight raking across them, deep shadows.
  # still beat (no MOTION line)

[A]
Elijah did not flinch as the flames roared past him, close enough to feel their breath.
VISUAL: Medium, eye-level. {elijah} standing motionless before the wall of white fire, camel-hair cloak whipping, face lit gold, unafraid.
MOTION: Locked subject; the fire and cloak move, he does not. Slow, almost imperceptible push.
  # animate beat; 15 words -> ~5.3 s. Narration = plain "Elijah"; VISUAL {elijah} expands his description + attaches his ref

[A]
But three years before this mountain, before the fire, there was only silence — and a sky that had forgotten how to rain.
VISUAL: Extreme wide, high angle, muted grey-ochre. A cracked, dead riverbed winding through a starving kingdom; a lone figure walking its length. Dust haze, no green.
  # still beat. Landscape kept grounded/muted (register-match) so it reads as the same film as the character beats

[A]
The land was dying — the people were dying — and no one knew why.
VISUAL: Close, eye-level. A child's cracked lips and hollow eyes, a dry clay water jar tipped empty beside her. Harsh flat light, dust on skin.
  # still beat; note the dashes carrying one continuous spoken contour across the clause

[A]
Elijah walked into the throne room and told the most powerful king in Israel it would not rain.
VISUAL: Wide two-shot, low angle favouring the throne. Left figure {elijah}, ragged and calm; right figure a heavy-bearded king enthroned in gold, half-risen in fury. Hard shafts of light, deep parallax of columns behind.
MOTION: Slow track from Elijah toward the throne across the hall — one continuous move, camera weighted.
  # animate beat; 18 words -> ~6.4 s. {elijah} is registered; the king is plain prose (no ref) — register him only if he recurs, then cast an ahab.png. Two-shot: eyeball on the carousel.

[A]
The king's face changed — he had heard threats before, but never one delivered like a sentence already carried out.
VISUAL: Extreme close, low angle. The king's eyes — fury curdling into fear. Gold and shadow, a single catchlight.
  # still beat; king still inline prose

[A]
Elijah turned, walked out of the palace, and vanished into the wilderness for three burning years.
VISUAL: Wide, eye-level, silhouette. {elijah} walking out through a blazing palace doorway into white desert light, back to camera, robe trailing dust.
MOTION: Slow pull-back as he recedes into the light — revealing the scale of the emptiness he walks into.
  # animate beat; 16 words -> ~5.6 s
```

**Why this passes the contract:** opens on the peak, not the chronology; every animate beat carries a MOTION line and clears the clip by word count; still beats hold on image and sentence; `{token}` appears in VISUAL only while narration keeps plain names; the registered character is tokened, the un-cast king is inline prose; the landscapes are kept grounded to match the character grade; the two-shot is flagged for a carousel check; one cinematic sentence per stretch; open loops stacked (why the drought? who is this man? what happens on that mountain?); reverence over spectacle; one primary motion per animate beat, subject locked, environment carrying the movement; and the prosody runs on dashes, not a string of full stops.

---

*Loaded at the start of every scripting session; the sole gate on batch-eligibility. Governs authorship only. When a session banks a genuinely new authoring rule, graduate it into this file — and keep it ruthlessly scoped, or it becomes the sprawl it replaced.*

*Reconciliation law: this contract is **additive and forward-only**. When a render or session proves something newer than an older doctrine says (e.g. a doctrine that predates a proven capability), forward progress wins and the doctrine is updated to match — never the reverse. Never roll back a proven gain to satisfy a stale document.*
