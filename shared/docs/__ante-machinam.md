# ⚰️ RETIRED — `ante-machinam.md` (30 June 2026)

> **THIS DOCUMENT IS NO LONGER LIVE. DO NOT AUTHOR FROM IT. DO NOT ADD TO IT.**
>
> `ante-machinam.md` was the single biggest structural flaw in the doc set: it was **Final-Hours / Sacred-Dawn craft wearing a `__` "channel-agnostic" label**, and it pulled every other channel's prompting toward the wrong register (dread-slow-faceless-photoreal). The @Q-Qrew build made the bias undeniable — a deliberately-opposite channel (bright, fast-cut, character-driven, flat-cel, **static**) had to fight this document at every turn.
>
> **Where its content went (30 June de-bias):**
> - **CRAFT** (the retention canon Part IV, the VISUAL-line patterns Part III, beat-granularity, animatable-foreground, the channel briefs Part V) → **`_Final-Hours.md §11`** (Final Hours' own craft canon — it was always FH craft). Each channel's craft lives in its own **`_ChannelName.md`**.
> - **MECHANICS** (the real Constitution: every-beat-has-words / silence-reconciliation, header-is-metadata, numbers-spelled-out, one-VISUAL-per-beat, lock-the-script; the two-mode promotion rule; the script-format contract; the author pre-flight; the runtime/wpm calibration) → **canonical reference §8** (`__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md`).
>
> **Two items were relabelled on the way out:** beat granularity and animatable-foreground were filed here under "the Constitution / the physics of the pipeline." They are **not** physics — they are FH craft. QQrew runs static at ~5-word beats with no foreground motion and the pipeline does not care. They are now `[CRAFT: FH-derived]` in `_Final-Hours.md §11.1–11.2`.
>
> **Status:** the file is left in place as a historical record and as the source for the deferred footer-scrub (≈13 live docs still carry stale "craft in ante-machinam" pointers — tracked as a follow-up; see the worklog). It is NOT to be loaded in a session, edited, or cited as authority. The body below (v3.0) is preserved verbatim **for reference only.**
>
> **The meta-lesson (enshrined in canonical §2B):** *BUILD ORDER ENCODES BIAS.* The first instance of anything silently becomes the "neutral" default. When building the first of a kind, ask "is this universal, or just this one's flavour?" — and tag at creation.

---
---

# Ante Machinam — v3.0
*Before the Machine. The single a priori reference for authoring a script and its beats, so that what enters the channel-agnostic pipeline orchestrator is already shaped to run clean and land well.*

*Destination in repo: `shared/docs/ante-machinam.md`. Read this BEFORE brainstorming a topic — not after a script exists.*

*v3.0 slims the document to **pure craft**. The control plane (Mission Control) now runs the machine, so the old Part VI command mechanics — parse / verify / dry-run / launch / babysit-the-gates over SSH — are replaced by a two-paragraph bridge (you paste a `script.md` and press Launch; the console is documented in the canonical reference §5). Everything that makes a script *land* is untouched: the Constitution (Part I), the VISUAL-writing craft (Part III), the full retention canon (Part IV), the channel briefs (Part V). This is the half the machine cannot do for you — the moat. v2.0's consolidation of `script-craft-principles.md` into Part IV stands; that file remains a stub pointing here. There is one craft source of truth.*

---

## 0. What this document is, and why it exists

The pipeline is **channel-agnostic**: one orchestrator runs `audio → (Mode B) → Mode A → convergence` for any channel, from one input (`beats_full.json` + its header) to a finished video. The process never changes. What changes every time is the **content** — and content is entirely channel-specific. A script for Final Hours and a script for Sacred Dawn run through the identical machine and must come out as completely different films.

This document is the layer *before* the machine. It holds the knowledge you need in your head **before you pick a topic or write a line**, because that knowledge changes how you brainstorm, how you write, and what the beats file looks like. Get this layer right and the script is better, the stills come out clean on the first pass, the beats parse without surprises, and the orchestrator runs to `final_video.mp4` without a wasted spend.

**How to use it.** Open this with a topic in mind. Read Part I and II to know what the machine will and will not accept (so you never author something it can't run). Read Part III for how to write a VISUAL line that renders clean and animates well. Read Part IV — the craft canon — for what makes the writing *land*. Then read the one channel brief in Part V that you're writing for. Part VI is the threshold: the exact steps that carry the finished `script.md` into the machine.

A note on precedence: where this document and an older session note or doc disagree, **this document wins**, because it already resolves the contradictions in favour of the latest first-principles model (the continuous-voice reset of 7 June and everything downstream of it). The old silent-beat/hold machinery, the 7-minute 84-beat fixed grid, the separate `metadata.json`, and the verbatim `[silent beat]` syntax are all **superseded** — Part IV reconciles the craft principles that used to assume them.

---

# PART I — The Constitution

*Seven mechanical truths the machine enforces. They are not style advice; they are the physics of the pipeline. Knowing them before you write is what separates a script that runs from a script that halts.*

### 1. There is one continuous voice track, and every beat must carry spoken words.

The spoken narration is a single, unbroken audio track, and it is the **sole source of truth for timing**. The track is never cut, never padded, never stopped to let a graphic play. Every beat — Mode A or Mode B — carries narration, and every beat's on-screen duration equals the measured duration of its spoken words (the "Lego rule": beat-1 words + beat-2 words + … in order, no gaps, no special cases).

A beat with **no words is an authoring error.** `build_audio_script.py` halts on it with exit 1. There is no "silent beat," no "hold," no inserted gap — that machinery was removed in the first-principles reset and does not exist anymore.

**The silence reconciliation (the most-overridden point in all the docs, get this right).** The craft tradition (Part IV) calls for "letting emotional beats land in silence" and "ending on the image." Under the *current* machine this does **not** mean authoring a wordless beat, and it does not even mean a long near-silent hold — because a beat plays for exactly as long as its words are spoken, you cannot hold an image in silence beyond the words underneath it. Authored silent holds are a **deferred capability**, not a thing you can write today. So: the restraint is achieved by writing a *short, slow, weighty line* over the key image and trusting the register to make it breathe — never by writing zero words, and never by expecting an image to linger past its narration. If you find yourself wanting a wordless beat, give it one short spoken sentence instead. (This supersedes the old Principle 6 and its `[silent beat]` syntax — see Part IV.)

### 2. The header is the single source of metadata, and `channel` must match the folder.

The first lines of `script.md`, before the first `## COLD OPEN`, are the header. Four keys are **required** — `channel`, `title`, `description`, `tags` (comma-separated) — and the orchestrator's preflight **halts before any spend** if any is missing. There is no separate `metadata.json`; the header *is* the YouTube title/description/tags.

`channel` must resolve to a channel folder. The resolver tries the name as given, then swaps hyphens and underscores, and uses whichever folder has a `channel.json`. So `final_hours` → `final-hours/` works, and `sacred_dawn` → `sacred-dawn/` works. But a genuine **alias does not resolve**: `synthetic_press` will not find `synthetic/`. When in doubt, **set `channel` to the exact folder name.** (This bit us twice — it is a class of bug, not a one-off.)

### 3. Spell out numbers and symbols in narration.

The narration is read aloud by TTS. Write "eleven eighty-four BC," not "1184 BC"; "ten thousand," not "10,000"; "a hundred and twenty years," not "120 years." This applies only to the spoken narration. The **title and description are metadata, displayed not spoken** — keep numerals there (they are searchable and read better on a thumbnail/description).

### 4. One `VISUAL:` line per Mode A beat — it is the image prompt.

A Mode A beat is `[A]` + its spoken narration, with a single `VISUAL: …` line beneath it. That line is exactly what the still generator draws. Extra VISUAL lines after the first are ignored. Everything that is not a VISUAL line becomes narration. (How to write a good VISUAL line is Part III.)

### 5. The script is load-bearing and is locked first.

Because audio is measured from the script and every visual timing hangs off that audio, the script is the foundation everything else is bound to. A misspelled on-screen card can be fixed in seconds at a review gate; a wrong *spoken* line cannot be fixed without re-running the audio leg and re-rendering. This is not bureaucracy — it is why great films start from a locked script. Lock the words before you think about pictures.

### 6. Beat granularity is governed by the clip-to-duration ratio. This is the rule that most affects how good the video looks.

One beat becomes one still and one animated clip of roughly **five seconds**. At assembly, a Mode A clip is **slow-filled** to stretch across its beat's measured spoken duration. Stretch up to about 2–3× is invisible; past that it reads as dead, stretched video (the end-to-end test threw a heavy-stretch warning at 4.8×; the Sacred Dawn launch confirmed it — a 52-beat / 17.7-min cut averaged ~4× and read as slow motion). The fix is never in the assembler — **it is authored, by writing shorter beats.**

So author each beat so its spoken words run roughly **5–12 seconds**, with a **hard ceiling around 15 seconds (~55 words)**. Punchy single-sentence lines earn their own short beat (they cut crisply and carry weight). The table below is the working map; the pipeline measures the true duration with Whisper at the audio gate, so these numbers are for *planning the grain*, not for sync.

| Spoken words | ≈ seconds @150 wpm | Stretch over a ~5 s clip | Verdict |
|---|---|---|---|
| 8–18 | ~3–7 s | ~1–1.5× | Ideal motion |
| 18–35 | ~7–14 s | ~1.5–3× | Good; the workable default |
| 35–55 | ~14–22 s | ~3–4× | Acceptable only for a deliberately still, weighty beat |
| 55+ | 22 s+ | >4× | **Split it.** Two beats, two visuals. |

A 25–31 minute episode at this grain is roughly 110–160 beats. That is a real spend (one still + one clip per beat), which is exactly why high-volume episodes are the ones that justify the banked parallel-animation and batch-mode work — but it is the correct grain for clean motion.

### 7. Every beat needs an animatable foreground subject. The still is a *frame to be moved*, not a picture to be admired.

The animator (Kling) can only move what is in the frame. A wide hills-and-valley or open-sea shot has no foreground subject, so it animates as a slow zoom across a postcard — technically motion, emotionally dead. A beat whose still carries a **foreground subject in mid-action** gives the animator an anchor and converts into real movement: the blade turns and catches the light, the hand drives the hammer, the wave crests and breaks, the giant's foot comes down and the dust bursts.

This is a **physics constraint, not a style preference**, which is why it lives in the Constitution. You cannot fix an inert clip at the animation gate — there is nothing in the frame to move. The fix is authored, upstream, in the VISUAL line, *before the still renders.* (How to write the animatable foreground without reopening Flux's drift problems is Part III — "Author for motion".)

The one-line test for every beat, applied before lock: **"What in this frame moves, and is it close enough to see it move?"** If the honest answer is "a slow drift across scenery," the shot is wrong — rewrite it to bring a kinetic subject into the foreground. Wide establishing shots are still allowed, but they become the **minority**, and they are kept **short** (a five-second wide stretched ~2× is a fine breath between kinetic beats; stretched ~4× it is the dead postcard).

*(This truth pairs with §6: a more kinetic shot is usually also a shorter beat. Author both at once — close, active, ~5–12 seconds of narration each.)*

---

# PART II — The two modes, and which channel uses which

There are two ways a beat can render. Knowing the model before you write prevents authoring a structure the machine can't run.

**Mode A — cinematic recreation.** A still (fal Flux) animated into a ~5 s clip (fal Kling). Carries the narrative spine — human moments, rooms, atmosphere, emotional beats. One `VISUAL:` line. This is the Final Hours / Sacred Dawn signature and the bulk of every channel.

**Mode B — Remotion motion-graphic.** A coded card: a headline, a quote, a counter, a chapter title, a document reveal. Used only where the *evidence or data is itself the point* — a figure to absorb, a quote to show, a tweet, a filing.

The rule that governs Mode B authoring: **Mode B is a transformation of the narration, never an addition to it.** You write the complete script as continuous Mode A narration first. Then you *promote* selected phrases to Mode B — the words stay spoken, exactly as written; only what is on screen changes from a recreation to a graphic. Promoting a phrase in the middle of a Mode A beat **splits that beat into two**, which you author explicitly as `[A] (first half) → [B:Component] (the promoted phrase) → [A] (second half)`. The parser does not split for you.

Constraints that follow:
- A Mode B beat still carries spoken words (the promoted phrase). Keep it **short — about 12–15 words, ≤ ~4 seconds.** A full sentence or a paragraph is a Mode A beat.
- The six components are `HighlightedHeadline`, `LowerThird`, `NumberCounter`, `ChapterCard`, `QuoteCard`, `DocumentReveal`. A tag outside this set parses but warns.
- Some components' *on-screen* text has no script-side source. Pass it explicitly in the tag (`text="…"`) or finalise it on the **Mode B review page**.
- **Silent / chapter cards as wordless beats no longer exist.** A `ChapterCard` with zero narration would halt the audio build (Constitution §1). Author chapter cards with a short spoken line, or defer.

The orchestrator decides legs by composition automatically: **no Mode B beats → the Mode B leg is skipped** and the plan is `audio → modeA → convergence`. This is the proven Final Hours / Sacred Dawn path. The absence of `[B:…]` beats is the signal.

---

# PART III — Writing the `VISUAL:` line (so stills come out clean on the first pass)

These are the production patterns that make Flux render reliably. A script written with them in mind generates clean stills; a script written without them generates restill rounds and wasted spend.

**Faceless by default; resolve a face only when you must.** When a person's identity is unknown, marginal, or anonymous, *never resolve the face* — frame from behind, in profile, silhouetted against light, in deep shadow, in soft focus, turned away. This mirrors the dignity register **and** eliminates Flux's single hardest drift problem. Only foreground a face when the audience must bond with one specific, named, documented person.

**Build canon around places, not people.** A scene canon ("the bakehouse," "the citadel at golden hour") renders consistently across twenty shots; a character canon drifts. Get variety from **angle and detail within a locked location** — the wide, the desk, the doorway, a single object.

**Substitute objects for groups.** Flux fails on three-plus figures in a frame. A family becomes an empty table with four settings and one chair pushed back; a crowd becomes a single abandoned object.

**Empty rooms carry meaning, and render perfectly.** The empty landing after the people ran; the wall after the death.

**Fire (and any catastrophe) is environment, not subject.** Write what the fire *does* — "orange glow pulsing on the wall," "smoke rolling across the ceiling" — not a close-up of flames consuming a person. Same for serpents, eruptions, drownings, floods: handle at distance.

**Period accuracy is the watermark.** Write the explicit guard into the VISUAL where a landmark or era is involved ("the medieval pre-Wren cathedral, NOT the modern dome").

**Image models cannot render legible text.** Frame engravings, signs, document text obliquely, in shadow, or out of focus. If specific text must be legible on screen, that is a Mode B card's job, not a still's.

**Distribute sensory detail across locations.** Six sensory details stacked in one room produce twenty near-identical shots and breathless pacing. Spread the richness across the kitchen, the lane, the river three streets south, the rooftops. (This is the production face of Part IV's pace-aware-density principle.)

**Aspect.** A shippable episode wants `landscape_16_9` stills (the model defaults narrower; ask for 16:9 explicitly); flag it if output comes back 4:3.

Write VISUAL lines as concrete, atmospheric scene descriptions — what the camera sees, who is in it and how they're framed (faceless), the light and palette — not literal instructions for impossible shots. One per beat.

## Author for motion — the animatable foreground (and how to do it without drift)

Part III so far keeps stills *clean*. This makes them *move*. The two goals appear to fight — clean stills came from wides and faceless framing; motion wants a foreground subject doing something — but they only fight if you reach for the wrong kind of subject. A clear-faced figure walking toward camera is full of motion *and* full of drift. The craft is to choose foreground subjects that are **inherently animatable *and* inherently drift-safe.**

Three classes of drift-safe motion. Author the bulk of every episode from these.

**1. The body, without the face.** A figure framed from **behind, low-angle at the legs, or as a silhouette** is faceless (no drift) yet a huge moving subject: the giant's foot drives into wet clay, mud flung outward; a massive hand closes; a robed back turns. This is the "giant walking, earth shaking" shot — kinetic and safe — because the camera never resolves the face.

**2. Objects and hands.** Highest motion-conversion, lowest drift. Flux renders a single object or a pair of hands cleanly; Kling animates them vividly. Land beats on these: the hammer striking sparks, the blade quenched and hissing steam, fingers tracing stars, a cup trembling as footsteps approach, the loom's shuttle, the sandals turning on the rising water.

**3. The environment as an active force.** Catastrophe-as-environment authored as *motion in progress*: not "a flooded valley" but "the water surges across the threshold and climbs the loom's legs." A wave cresting toward camera, fire climbing a wall, dust rolling down the lane ahead of the footsteps.

**The shot-ratio rule.** The body of the film is close/medium kinetic beats; the wide establishing shot is the exception, kept short (stretch ≤ ~2×). Three wides in a row means two are hiding a beat that should have come down to a foreground subject.

**Embed the motion in the VISUAL line** — describe what moves, as a verb the animator can perform in ~5s. It shapes the still toward something animatable and becomes the default cue when the stills-review motion-direction feature (backlog) ships.

**The drift caution — a dial, not a switch.** Foreground-action dial up, face-resolution dial down — both at once: faces resolved-away, one figure not three, objects and partial bodies over full clear figures.

---

# PART IV — The craft canon (channel-agnostic)

*The full craft treatment — what makes the writing land, as opposed to Part III's what-makes-it-render. It absorbs the former `script-craft-principles.md` (the eleven Final Hours principles + the three Arthur principles), folds in the 70s-nostalgia retention lessons and the Sacred Dawn packaging doctrine, reconciles everything to the current machine, and de-duplicates the numbering that had rotted in the old doc. Every principle here was pressure-tested in a shipped video; the examples are channel-specific (Pudding Lane, Hindenburg, Pompeii, Mary Celeste, the 70s-parents hit, the Watchers) but the principles are universal. The register changes by channel (Part V bends it); the mechanics of retention do not.*

*Spine in one sentence: **win the click with the package, hook the first sixty seconds, hold the body with recognition and a recurring beat, and land a close that converts a viewer into a subscriber.***

## IV.0 — The two retention truths everything else serves

- **CTR is won by the package; distribution is won by retention.** The title and thumbnail win the click; AVD and the first-48-hour curve decide whether the algorithm pushes the video cold (the 70s-parents hit went 94% from recommendations on the strength of early retention spikes). Everything below serves one of these two.
- **Recognition is the retention mechanic.** The Studio-flagged lean-in spikes landed at moments of *personal recognition* — a named, specific, physically-precise thing the viewer holds in their body. Vague beats get no spike; named, vivid specifics do. This is the most transferable lesson, and it reappears everywhere below.

## IV.1 — The first sixty-to-ninety seconds (the gate)

Run every cold open through this before lock.

**Drop the viewer inside a scene, present-tense and sensory — never brief them about the video.** "Picture it. It's a summer afternoon, nineteen seventy-six." / "Feel it before you see it. The water trembling in the cup." Never "in this video we'll look at…"

**Three concrete anchors in the first ten seconds** — date, place, person, amount, object, time of day, number; falsifiable, front-loaded ("just before midnight on Saturday the first of September, 1666, in a bakery on Pudding Lane" — four anchors). Year-only/temporal anchor acceptable for deep antiquity. If you can't find three, the topic may be wrong for the channel.

**A named anchor within fifteen seconds** — the specific human or named place the viewer commits to following.

**Announce the dramatic arc in the first minute** — **[date/place locked] + [scale in concrete numbers] + [stakes promise explicit] + [tease of the worst still to come].** The single biggest separator between a 1.1M and a 600K video on the same channel (Arthur's "London 1300": "two catastrophes would bring this mighty city to its knees… then, in 1348, something far worse…"). The tour-guide open is the failure mode.

**Deliver the title's contract by ~20 seconds — then keep delivering tension through two minutes.** A context block over ~45–90s without renewing tension causes drop-off (Hindenburg → 11.3%; Pompeii interleaved → 51%). Audit 0:20–2:00: mark every tension-renewal beat; gaps over ~45s get a tension beat woven in or cut.

**Front-load the payload — compress the runway.** (70s first-30s dip, 104%→79%.) Reach a visceral, concrete payload fast; don't throat-clear with meta. The Watchers rebuild: open inside the scene with body-sensation, land the killer recognition image by ~0:15, then widen to thesis.

**Plant the recurring spine and the emotional thesis in the open** — name the recurring payoff beat (70s "ends with somebody knocking on your door"; Watchers "all of it ends in water"), and seed the thesis you'll harvest at the close (70s "they figured a little danger was good for ya"; Watchers "knowledge poured into a world too young to hold it").

**Foreshadow pivot at ~40–55s; cliffhanger at ~60s, cut mid-thought.**

## IV.2 — Through the body

**Sensation, not description** — supply the senses the image can't: smell, texture, sound, weight, temperature. "Vinyl seats that'd brand the backs of your legs in July." "The heat pressing on your face, the ring of the hammer off the stone." Never "she felt afraid." This makes AI visuals feel lived rather than illustrated.

**Pace-aware sensory density — distribute across locations.** Six details in one room → twenty near-identical shots and breathless pacing (Pudding Lane's bakehouse, compressed to ~4s/shot). Spread the same richness across kitchen, lane, river, rooftops. Test: if more than three details land in one location, redistribute. (Confined-location stories where the confinement *is* the weight are the deliberate exception.)

**Recognition as the retention mechanic** — land beats on one universal, physically-precise, vivid specific: the named memory (70s) or the famous-thing-made-vivid (the giant; Azazel's first sword = "this is where war was born"; Noah built it for a hundred and twenty years while the world laughed). Engineer those moments; don't let the recognisable thing pass as a flat mention.

**A recurring payoff beat as spine** — a repeated resolution the viewer learns to anticipate turns disconnected beats into one running bit (the 70s "court date," the Watchers' tightening rain-clock). Anticipation is retention.

**Clock-anchor the dread** — specific times before specific events; tighten intervals as the catastrophe nears. The clock becomes a character. (Time passing with nothing happening is achieved now with a short weighty line, not a wordless hold — Constitution §1.)

**Name the surrounding humans — and name the absence when the record lost it.** Named reads as documented; anonymous reads as generic. And when the record never kept a name, never invent one — name the absence as a refrain, three times (Pudding Lane's unnamed maid; the Watchers' nameless family). This is the dignity register and it unlocks the face-never-resolved production win.

**Narrator-to-viewer irony at act transitions** — once, the narrator steps outside the frame to name what the viewer knows that the characters don't ("It had no idea what was coming next"). Activates anticipation across the act break where retention craters. A scalpel, not a tic.

**Plant seeds early, harvest late** — specific facts dropped as if incidental early, returned to with weight at the close (The Fool's bank-fraud detail; the Watchers' "and also after the waters"). Plant only facts that gain weight when revisited — not gags, unless the register is comedic.

## IV.3 — The close (where a view becomes a subscriber)

**End on the image, then reflect — sequential, not contradictory.** The final beat is one image held by a weighty line (a ring, a clock, ash, the ark alone on grey water). Then the move most often missed — a **moralised closer that reflects the event back at the present-day viewer.** Not "thanks for watching" (the 632K Pompeii); the disaster reflected at the modern viewer (the 1.1M London 1300: "we're still living in the world they created… cities survive"). The viewer should leave holding something they didn't have at the start — that converts a watcher into a commenter, sharer, subscriber.

**The over-deliver must accelerate, not decelerate** (70s Leak 2: a three-item bonus dragged AVD 41.6%→38.4%). Exceed the promise only with your *strongest* material — one killer bonus, or fold the best into the body, then stop. For a film, the close accelerates into the sequel hook rather than trailing.

## IV.4 — Packaging is craft (title + thumbnail + comment)

**Lead the package with tension, not just warmth — the then-vs-now / transgression hook.** "10 Things '70s Parents Did That Would Be Illegal Today" beats "Nostalgic Things From the 70s." "London 1300: The Apocalypse Happened in 1348" beats "Pompeii: Before the Disaster." Lead with the tension, the stakes, or the question.

**Title and thumbnail complement, not echo.** Image carries the *what*; title carries the *why-click*; never the same nouns. Sacred Dawn launch: title "Before the Flood: The True Story of the Nephilim and the Watchers" (recognition/search) + thumbnail "ANGELS OR GIANTS?" (a question the title doesn't ask).

**Comment-bait built into the subject, not bolted on.** A recognition-rich topic writes its own pinned comment ("what did your parents let you do?"; "who do you believe they were — angels, the line of Seth, or men who reached too high?"). Build the question into the video (plant it, ask it at the close), seed it in the description, pin it. Thumbnail-asks → video-stages → comment-harvests is one coherent loop.

**The list/act structure is a retention scaffold** — a numbered list is micro-promises with a visible finish line; for narrative channels the equivalent is clear acts with forward-pulling act-turn hooks. The viewer always knows where they are and that there's a destination.

## IV.5 — The narrator is a retention device

A characterful, intimate narrator is itself a reason to stay, and a major differentiator in a niche full of flat AI TTS. The register is channel-specific — Vinny's wry Brooklyn, Elliot's grand liturgical authority, Victor's mournful dread — but the principle is constant: the personality holds the viewer across the slow parts. Write *to* the voice. Direct address ("you know them, even if no one ever told you this part"; "tell me what you believe") creates presence and pulls retention; deploy it at the open, the act seams, and the close.

## IV.6 — Production realities that shape the writing

**Acknowledge the recreation once, early, single line** — a museum-placard sentence naming real sources ("recreated from the household accounts, the British Library letter, and the parliamentary investigation"; "drawn from Genesis, the Book of Enoch, and the Book of the Watchers"). Specific, never apologetic, never a tech disclaimer. For attribution-sensitive material it doubles as the fidelity guard that protects credibility and monetization.

**Inworld renders faster than you plan — write long.** Measured ~150–190 wpm against a 135 wpm plan; the rendered cut is ~85–90% of the word-count estimate. Doesn't affect sync (Whisper measures the real audio) but does affect runtime. Write 10–15% more than the target. (The Watchers: 2,716 words → 17.7 min, ~195 wpm.) **But runtime is beat-floored, not words-only (banked 17 June).** The Ken-Burns minimum hold stretches short beats up to the clip floor, so a words-only estimate UNDERSHOOTS real runtime. Real runtime is roughly **beat count times ~14s**. Prehistoric Disasters' Toba: 88 beats -> 20.7 min measured (a words-only estimate predicted ~13). A ~28-min words-estimate script lands closer to ~40 min. Sanity-check runtime from beat count, not wpm alone.

## IV.7 — The pre-lock audit table (channel-agnostic)

Before any script is locked, fill this in. Any "weak" or "missing" → revise before production.

| # | Principle | Status |
|---|---|---|
| 1 | Dropped inside a scene, present-tense + sensory open (not "in this video") | |
| 2 | Three concrete anchors in 10s; named anchor by 15s | |
| 3 | Dramatic arc announced in the first minute (scale + stakes + tease) | |
| 4 | Title contract delivered by ~20s AND tension sustained through 2:00 | |
| 5 | Payload front-loaded; recurring spine + thesis planted in the open | |
| 6 | Foreshadow pivot ~40–55s; cliffhanger ~60s cut mid-thought | |
| 7 | Sensation not description, distributed across locations | |
| 8 | Recognition beats — one vivid universal/famous specific per key moment | |
| 9 | A recurring payoff beat as spine | |
| 10 | Clock-anchored dread, tightening intervals | |
| 11 | Surrounding humans named; absence named as refrain when applicable | |
| 12 | Narrator-to-viewer irony at ≥1 act transition | |
| 13 | Seeds planted early, harvested late | |
| 14 | End on the image, then moralised closer reflecting at the present-day viewer | |
| 15 | Over-deliver accelerates (or ends clean) — no trailing leftovers | |
| 16 | Package: tension/transgression hook; title & thumbnail complement not echo | |
| 17 | Comment-bait built into the subject (planted → asked → pinnable) | |
| 18 | Recreation acknowledged once, early, single line | |
| 19 | Written ~10–15% long for Inworld's faster read | |
| 20 | Constitution check: no wordless beats; numbers spelled out; ≤~55 words/beat; animatable foreground per beat | |

---

# PART V — Channel positioning briefs

*The pipeline is one machine; these channels are different films. Read the one you are writing for.*

### Quick reference

| | Final Hours | Sacred Dawn | Synthetic Press | Lazarus Films | You Had To Be There |
|---|---|---|---|---|---|
| Premise | Last hours of people/places | Bible's cosmic-primeval origin story | AI-era human drama | PD literary adaptation | Un-filmable lived nostalgia |
| Mode | A only | A only | Dual (A+B) | A, narrated | A only |
| Register | Dread-and-dignity | Reverent, majestic, liturgical | Documentary witness | Dignified-literary | Wry, warm, conspiratorial |
| Voice | Victor | Elliot | Peter / Victor | TBD | Vinny |
| Runtime | 12–32 min | 17–25 min | 15–20 min | 12–15 min | 10–15 min |
| `channel:` | `final_hours` | `sacred_dawn` | `synthetic` | confirm folder | `you_had_to_be_there` |
| Status | Live, primary | Live | Launching | Designed | Live |

## V.1 — Final Hours

**Premise.** The last hours of one human story inside a larger catastrophe; the camera stays with one named person (or place) while history happens around them. **Mode A only.** **Register:** dread-and-dignity, mournful, present-tense third-person witness; never action/mystery/conspiracy. **Runtime:** long-form (12–16; city pieces 20–32; the 7-min grid is superseded). **Specifics:** recreation acknowledgment woven as "what's in the ground" for city pieces; anonymity-as-refrain; the moralised closer is the most-missed beat. **City sub-series:** title grammar `[Place] [Year]: [doom hook] (AI Reconstruction)`; the six-beat hook; callback frame (open on the catastrophe image = thumbnail, return near the end). **Gotcha:** `final_hours` → `final-hours/`.

## V.2 — Sacred Dawn

**Premise.** The Bible's cosmic and primeval drama as cinematic recreation — the origin story brought to life. Reverent, never sensational. **Mode A only.** **Register:** reverent, grand, liturgical, mournful-and-awed; present-tense witness. **Voice:** Elliot. **Runtime:** 17–25 min. **Specifics:** attribution discipline is the moat (tag *Genesis says / the Book of Enoch says*; canon vs apocrypha plainly; reverent-curiosity, never shock-bait); the un-referenced sublime is the engine's home (no footage to be wrong against — Flux's unreality reads as awe); lean foreground-action + faceless hard (Part III); palette glory→ember→storm→dawn. **Gotchas:** `sacred_dawn` → `sacred-dawn/`; `voice_id` snake_case (NOT `voiceId` — silent Victor fallback); no resolution key; upload manual (Entertainment / `category_id "24"` / private). Full doctrine: `sacred-dawn-creed.md`.

## V.3 — Synthetic Press

**Premise.** AI-native cinematic documentary on the human drama of the AI era — AI-drama, not AI-doom. **Dual-mode** (A 60–70% / B 30–40%); author continuous Mode A first, then promote phrases. **Register:** documentary witness; present tense for hot moments, past for context; never invent dialogue. **No lip-sync** — figures seen not heard; "the spoken line and its receipt" (voice says it; a Mode B card carries name/source/date; a highlight sweeps the phrase). **Runtime:** 15–20. **Voice:** Peter (marquee) / Victor (scratch). **Gotchas:** `channel: synthetic` (NOT `synthetic_press`); upload/OAuth not set up; 1080p master.

## V.4 — Lazarus Films

**Premise.** Dignified cinematic adaptation of public-domain dramatic writing. **Designed, not built.** **Mode A, narrated, no lip-sync yet** — do not script spoken dialogue. **Register:** dignified-literary, reverent, never camp; start in atmospheric-horror/supernatural-dread. **Specifics:** cold open from the source then pull back to the narrator; honour the text. **Look-override** (unique to Lazarus): `channel.json` defaults + per-film `look.json` (channel owns the frame, film owns the interior). **Gotcha:** confirm folder + `channel.json` before first run.

## V.5 — You Had To Be There

**Premise.** Cinematic recreation of un-filmable lived nostalgia — memories no camera caught. **Mode A only.** **Register:** wry, warm, conspiratorial, intimate. **Voice:** Vinny. **Runtime:** 10–15. **Specifics:** the list/transgression format is the proven shape (the launch hit); per-job decade looks; Vinny markup law (cap `[pause]` at two, attach to real words, no `[sigh]`). **Gotcha:** `you_had_to_be_there`.

---

# PART VI — Crossing the threshold (into the machine)

*This used to be a page of terminal commands — parse, verify, dry-run, launch, babysit the gates over SSH. **Mission Control replaced all of it.** The craft above is what still matters; the mechanics below are now two paragraphs.*

**What you hand the machine.** A `script.md` with the right shape: the four-key header (`channel`, `title`, `description`, `tags`) before the first `## COLD OPEN`; then each beat as `[A]` + narration on one line, `VISUAL: …` on the next, a blank line between. Mode B beats put the spoken line *above* the `[B:Component] …` tag. Numbers spelled out in narration; numerals fine in the header. That is the entire contract — get the script right and the machine does the rest.

**Author the format by copying a known-good script, never from this description (banked 17 June).** The shape above is a *description*; the parser reads *exact markup*. Authoring from the prose -- YAML `---` fences, single-`#` headers, `NARRATION:`/`VISUAL:` labels -- parsed to ZERO beats and crashed the build (ZeroDivisionError on the first Toba draft). The reliable method: open a working `script.md` (a shipped Sacred Dawn or Final Hours project), copy its exact structure -- bare `key: value` header lines with NO fences, `## COLD OPEN` / `## PART ...` double-hash section headers, then `[A] <narration on one line>` followed by `VISUAL: <prompt>` on the next line with a blank line between beats -- and swap in your content. For bulk-prepping a script in the wrong shape, a mechanical reformatter (strip fences, `#`->`##`, reorder any `NARRATION:`/`VISUAL:` pair into `[A]`+`VISUAL:`) is the converter pattern. **Verify before spending:** `parse_script.py <md> --json /tmp/b.json --json-full /tmp/f.json` prints the beat count for free -- a zero or a crash means the format is wrong, not the content.

**How you run it.** Paste the script into Mission Control (`:8002`), pick the channel, hit **Launch**. The page is the operator surface now: the parse, the preflight halt-on-bad-header, the leg planning, the spend all happen behind the **Launch** button. The two firewalls you authored *for* are now page state — the **audio gate** (keep the synthetic read, or swap in a human VO) and the **stills gate** (review every still, then Generate Clips, or Stop and keep the stills). After the stills gate: tiered render (Kling front-N / Ken-Burns floor), assemble, and the finished video appears in the panel with Download. *(The canonical reference §5 is the full operator's manual for the console; this doc's job ends where the script enters the page.)*

**The one pre-lock discipline that survives unchanged:** fill the Part IV audit table (IV.7) and run the Constitution check (Part I) *before* you paste. The machine will faithfully render a bad script into a bad video — the gates catch a drifted still, not a slow open or a dead wide. The audit is upstream of the machine because the machine can't do it for you.

### Pre-flight checklist (author against these before you paste)

| Check | Pass condition |
|---|---|
| Header complete | `channel`, `title`, `description`, `tags` all present |
| Channel name | the exact folder name (hyphen/underscore auto-resolves; a true alias does not — Synthetic is `synthetic`, not `synthetic_press`) |
| Every beat has words | no wordless beats (they halt the audio build) |
| Every Mode A beat has a VISUAL | one `VISUAL:` line each |
| Numbers spelled out | no bare digits in narration |
| Granularity | no beat over ~55 words; long passages split |
| Animatable foreground | every beat has a kinetic foreground subject (or a deliberately short wide); no run of dead wides |
| Craft audit | the Part IV pre-lock table is filled, no "weak/missing" |
| Mode mix | Mode-A channels → all `A`; Synthetic → A + B |
| Mode B beats short | each promoted phrase ≤ ~12–15 words, ≤ ~4 s |

---

## Appendix — one-screen card

**The constitution (author to these from the first line):**
1. Every beat has spoken words — wordless beats halt the build; silence is unavailable, not authored.
2. Header carries channel/title/description/tags; `channel` matches the folder.
3. Spell out numbers in narration; numerals fine in metadata.
4. One VISUAL per Mode A beat; it is the image prompt.
5. Lock the script first — everything downstream is bound to it.
6. ~5–12 s per beat (~15–35 words), hard ceiling ~55; split long passages.
7. Every beat carries an animatable foreground subject in mid-action — the still is a frame to be moved. Wides are the short minority. Ask: *what moves, and is it close enough to see?*

**The craft canon (Part IV) in one breath:** win the click with a tension package (title & thumbnail complement, not echo) → drop inside a scene with three anchors and announce the arc in the first minute → front-load the payload, plant the spine and thesis → hold the body with recognition beats, a recurring payoff, clock-dread, named humans, narrator irony, and seeds → close on the image then a moralised reflection that converts the viewer → comment-bait built into the subject → write long for Inworld.

**The channels in one line each:**
- **Final Hours** — last hours of a person/place; Mode A; present-tense dread; `final_hours`.
- **Sacred Dawn** — biblical cosmic-primeval recreation; Mode A; reverent/Elliot; `sacred_dawn`.
- **Synthetic Press** — AI-era human drama; dual-mode; documentary witness; `synthetic`.
- **Lazarus Films** — dignified PD adaptation; Mode A narrated; per-film look override; confirm folder.
- **You Had To Be There** — un-filmable nostalgia; Mode A; wry/Vinny; list format; `you_had_to_be_there`.

**The threshold:** paste `script.md` into Mission Control → Launch → `keep` at the audio gate (listen first), review then Generate Clips at the stills gate → tiered render → assemble → the finished video in the panel.

---

*v3.0 — craft-only slim. Strips the Part VI terminal mechanics (obsoleted by Mission Control; the canonical reference §5 is the console manual) down to a paste-and-Launch bridge, and reconciles the appendix threshold line to the control plane. No craft was removed: Parts I, III, IV, V are carried forward intact, including the animatable-foreground principle (Constitution §7 + Part III "Author for motion") and the full IV.7 pre-lock audit. Maintenance: bump the version when a run banks a lesson that changes how a script is authored before it enters the machine — operational/console lessons go in the canonical reference, craft lessons stay here.*
