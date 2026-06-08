# Ante Machinam — v1.00
*Before the Machine. The a priori knowledge for authoring a script and its beats, so that what enters the channel-agnostic pipeline orchestrator is already shaped to run clean and land well.*

*Destination in repo: `shared/docs/ante-machinam.md`. Read this BEFORE brainstorming a topic — not after a script exists.*

---

## 0. What this document is, and why it exists

The pipeline is **channel-agnostic**: one orchestrator runs `audio → (Mode B) → Mode A → convergence` for any channel, from one input (`beats_full.json` + its header) to a finished video. The process never changes. What changes every time is the **content** — and content is entirely channel-specific. A script for Final Hours and a script for Synthetic Press run through the identical machine and must come out as completely different films.

This document is the layer *before* the machine. It holds the knowledge you need in your head **before you pick a topic or write a line**, because that knowledge changes how you brainstorm, how you write, and what the beats file looks like. Get this layer right and the script is better, the stills come out clean on the first pass, the beats parse without surprises, and the orchestrator runs to `final_video.mp4` without a wasted spend.

It exists because of a real lesson. When we built the Troy episode, the *format* of `script.md` came from the authoring guide, but the **granularity economics** came from a buried end-to-end-validation note, the **`--project` flag** came from the orchestrator spec, and the **every-beat-has-narration rule** had to be reconciled across a guide and older session notes that appeared to contradict each other. The conversion succeeded, but only by triangulating five documents. This is that triangulation, done once, so it never has to be done again.

**How to use it.** Open this with a topic in mind. Read Part I and II to know what the machine will and will not accept (so you never author something it can't run). Read Part III–IV for the craft that applies to every channel. Then read the one channel brief in Part V that you're writing for — that brief positions the script. Part VI is the threshold: the exact steps that carry the finished `script.md` into the machine.

A note on precedence: where this document and an older session note disagree, **this document wins**, because it already resolves the contradictions in favour of the latest first-principles model (the continuous-voice reset of 7 June and everything downstream of it). The old silent-beat / hold machinery, the 7-minute 84-beat fixed grid, and the separate `metadata.json` are all superseded — see below.

---

# PART I — The Constitution

*Six mechanical truths the machine enforces. They are not style advice; they are the physics of the pipeline. Knowing them before you write is what separates a script that runs from a script that halts.*

### 1. There is one continuous voice track, and every beat must carry spoken words.

The spoken narration is a single, unbroken audio track, and it is the **sole source of truth for timing**. The track is never cut, never padded, never stopped to let a graphic play. Every beat — Mode A or Mode B — carries narration, and every beat's on-screen duration equals the measured duration of its spoken words (the "Lego rule": beat-1 words + beat-2 words + … in order, no gaps, no special cases).

A beat with **no words is an authoring error.** `build_audio_script.py` halts on it with exit 1. There is no "silent beat," no "hold," no inserted gap — that machinery was removed in the first-principles reset and does not exist anymore.

**The silence reconciliation (the most-overridden point in all the docs, get this right).** The craft tradition calls for "letting emotional beats land in silence" and "ending on the image." Under the *current* machine this does **not** mean authoring a wordless beat, and it does not even mean a long near-silent hold — because a beat plays for exactly as long as its words are spoken, you cannot hold an image in silence beyond the words underneath it. Authored silent holds are a **deferred capability**, not a thing you can write today. So: the restraint is achieved by writing a *short, slow, weighty line* over the key image and trusting the register to make it breathe — never by writing zero words, and never by expecting an image to linger past its narration. If you find yourself wanting a wordless beat, give it one short spoken sentence instead.

### 2. The header is the single source of metadata, and `channel` must match the folder.

The first lines of `script.md`, before the first `## COLD OPEN`, are the header. Four keys are **required** — `channel`, `title`, `description`, `tags` (comma-separated) — and the orchestrator's preflight **halts before any spend** if any is missing. There is no separate `metadata.json`; the header *is* the YouTube title/description/tags.

`channel` must resolve to a channel folder. The resolver tries the name as given, then swaps hyphens and underscores, and uses whichever folder has a `channel.json`. So `final_hours` → `final-hours/` works. But a genuine **alias does not resolve**: `synthetic_press` will not find `synthetic/`. When in doubt, **set `channel` to the exact folder name.** (This bit us twice — it is a class of bug, not a one-off.)

### 3. Spell out numbers and symbols in narration.

The narration is read aloud by TTS. Write "eleven eighty-four BC," not "1184 BC"; "ten thousand," not "10,000"; "thirteen billion dollars," not "$13B." This applies only to the spoken narration. The **title and description are metadata, displayed not spoken** — keep numerals there (they are searchable and read better on a thumbnail/description).

### 4. One `VISUAL:` line per Mode A beat — it is the image prompt.

A Mode A beat is `[A]` + its spoken narration, with a single `VISUAL: …` line beneath it. That line is exactly what the still generator draws. Extra VISUAL lines after the first are ignored. Everything that is not a VISUAL line becomes narration. (How to write a good VISUAL line is Part III.)

### 5. The script is load-bearing and is locked first.

Because audio is measured from the script and every visual timing hangs off that audio, the script is the foundation everything else is bound to. A misspelled on-screen card can be fixed in seconds at a review gate; a wrong *spoken* line cannot be fixed without re-running the audio leg and re-rendering. This is not bureaucracy — it is why great films start from a locked script. Lock the words before you think about pictures.

### 6. Beat granularity is governed by the clip-to-duration ratio. This is the rule that most affects how good the video looks.

One beat becomes one still and one animated clip of roughly **five seconds**. At assembly, a Mode A clip is **slow-filled** to stretch across its beat's measured spoken duration. Stretch up to about 2–3× is invisible; past that it reads as dead, stretched video (the end-to-end test threw a heavy-stretch warning at 4.8×). The fix is never in the assembler — **it is authored, by writing shorter beats.**

So author each beat so its spoken words run roughly **5–12 seconds**, with a **hard ceiling around 15 seconds (~55 words)**. Punchy single-sentence lines earn their own short beat (they cut crisply and carry weight). The table below is the working map; the pipeline measures the true duration with Whisper at the audio gate, so these numbers are for *planning the grain*, not for sync.

| Spoken words | ≈ seconds @150 wpm | Stretch over a ~5 s clip | Verdict |
|---|---|---|---|
| 8–18 | ~3–7 s | ~1–1.5× | Ideal motion (the old Final Hours tight-grid instinct — sound) |
| 18–35 | ~7–14 s | ~1.5–3× | Good; the workable default |
| 35–55 | ~14–22 s | ~3–4× | Acceptable only for a deliberately still, weighty beat |
| 55+ | 22 s+ | >4× | **Split it.** Two beats, two visuals. |

A 28–31 minute episode at this grain is roughly 120–160 beats. That is a real spend (one still + one clip per beat), which is exactly why high-volume episodes are the ones that justify the banked parallel-animation and batch-mode work — but it is the correct grain for clean motion.

---

# PART II — The two modes, and which channel uses which

There are two ways a beat can render. Knowing the model before you write prevents authoring a structure the machine can't run.

**Mode A — cinematic recreation.** A still (fal Flux) animated into a ~5 s clip (fal Kling). Carries the narrative spine — human moments, rooms, atmosphere, emotional beats. One `VISUAL:` line. This is the Final Hours signature and the bulk of every channel.

**Mode B — Remotion motion-graphic.** A coded card: a headline, a quote, a counter, a chapter title, a document reveal. Used only where the *evidence or data is itself the point* — a figure to absorb, a quote to show, a tweet, a filing.

The rule that governs Mode B authoring, and the one the old docs got wrong: **Mode B is a transformation of the narration, never an addition to it.** You write the complete script as continuous Mode A narration first. Then you *promote* selected phrases to Mode B — the words stay spoken, exactly as written; only what is on screen changes from a recreation to a graphic. Promoting a phrase in the middle of a Mode A beat **splits that beat into two**, which you author explicitly as `[A] (first half) → [B:Component] (the promoted phrase) → [A] (second half)`. The parser does not split for you.

Constraints that follow:
- A Mode B beat still carries spoken words (the promoted phrase). Keep it **short — about 12–15 words, ≤ ~4 seconds.** A full sentence or a paragraph is a Mode A beat.
- The six components are `HighlightedHeadline`, `LowerThird`, `NumberCounter`, `ChapterCard`, `QuoteCard`, `DocumentReveal`. A tag outside this set parses but warns.
- Some components' *on-screen* text has no script-side source (e.g. `HighlightedHeadline`'s headline). Pass it explicitly in the tag (`text="…"`) or finalise it on the **Mode B review page**, which is a design surface, not just an inspection step.
- **Silent / chapter cards as wordless beats no longer exist.** A `ChapterCard` with zero narration would halt the audio build (Constitution §1). If a channel wants chapters, they are authored as `ChapterCard` beats that still carry a short spoken line — or deferred. Do not author wordless cards.

The orchestrator decides legs by composition automatically: **no Mode B beats → the Mode B leg is skipped** and the plan is `audio → modeA → convergence`. This is the proven Final Hours path. You do not flag it; the absence of `[B:…]` beats is the signal.

---

# PART III — Writing the `VISUAL:` line (so stills come out clean on the first pass)

These are the production patterns that make Flux render reliably. They are worth knowing before you write, because a script written with them in mind generates clean stills, and a script written without them generates restill rounds and wasted spend.

**Faceless by default; resolve a face only when you must.** When a person's identity is unknown, marginal, or anonymous, *never resolve the face* — frame from behind, in profile, silhouetted against light, in deep shadow, in soft focus, turned away. This mirrors the dignity register **and** eliminates Flux's single hardest drift problem. Variations: a named-but-unseen figure (Helen "always at the edge of frame, turned, veiled"), and death-by-absence (a child's death rendered as an empty wall, never the child). Only foreground a face when the audience must bond with one specific, named, documented person.

**Build canon around places, not people.** A scene canon ("the bakehouse," "the citadel at golden hour") renders consistently across twenty shots; a character canon drifts. Get visual variety from **angle and detail within a locked location** — the wide, the desk, the doorway, a single object — not from constantly inventing new locations. Ask of two shots: could a viewer say "those are the same shot"? If they'd say "both the captain's cabin, but one's the desk and one's a child's shoe," that's right.

**Substitute objects for groups.** Flux fails on three-plus figures in a frame. A family becomes an empty table with four settings and one chair pushed back; a crowd becomes a single abandoned object. The viewer's imagination populates it more powerfully than the render could.

**Empty rooms carry meaning, and render perfectly.** The empty landing after the people ran; the wall after the death. Reliable to render, and a recognised cinematic device.

**Fire (and any catastrophe) is environment, not subject.** Write what the fire *does* — "orange glow pulsing on the wall," "smoke rolling across the ceiling," "a skyline engulfed against a black sky" — not a close-up of flames consuming a person. Same for serpents, eruptions, drownings: handle at distance.

**Period accuracy is the watermark.** The thing literate viewers spot first is wrong-period architecture or anachronism. Write the explicit guard into the VISUAL where a landmark or era is involved ("the medieval pre-Wren cathedral, NOT the modern dome").

**Image models cannot render legible text.** Engravings, signs, document text, numbers on screens — frame them obliquely, in shadow, or out of focus. Never rely on the model to produce specific words. (If specific text must be legible and on screen, that is a Mode B card's job, not a still's.)

**Distribute sensory detail across locations.** Six sensory details stacked in one room produce twenty near-identical shots and breathless pacing. Spread the same richness across the kitchen, the lane outside, the river three streets south, the rooftops — same immersion, naturally varied shot rhythm.

**Aspect.** The current still model needs to be asked for 16:9 explicitly (it otherwise defaults narrower). This is an engine setting, not something you write into the VISUAL — but know that a shippable episode wants `landscape_16_9` stills, and flag it if output comes back 4:3.

Write VISUAL lines as concrete, atmospheric scene descriptions — what the camera sees, who is in it and how they're framed (faceless), the light and palette — not as literal instructions for impossible shots. One per beat.

---

# PART IV — The universal script-craft spine (channel-agnostic)

This is the craft that applies to every channel. The channel briefs in Part V then bend it to a register. All of it has been pressure-tested against real outlier videos (Chloe vs History, Arthur Revives the Past) and against our own retention data.

### The first sixty seconds — the stress-test gate

Run every cold open through this before lock. Most of these are non-negotiable for any of the three channels:

1. **Date anchor within ten seconds.** A specific date, ideally the first sentence. Year-only is acceptable for deep antiquity.
2. **Named anchor within fifteen seconds.** A specific human (or, for the city-catastrophe format, a specific named place) the viewer commits to following.
3. **A concrete number within thirty seconds**, ideally with a comparative anchor ("three times larger than," "taller than anything for four hundred years").
4. **Announce the dramatic arc in the first minute.** Not "today we visit X" but "[date/place locked] + [scale in numbers] + [the stakes promise made explicit] + [a tease of the worst still to come]." This is the single biggest separator between a 1.1M-view video and a 600K-view video on the same channel with the same tools.
5. **A foreshadow pivot at forty to fifty-five seconds** — the turn from "here is the world" to "here is what is about to destroy it."
6. **A cliffhanger at the sixty-second mark** — cut mid-thought, not on a clean sentence.

### Through the body

- **Sensation, not description.** The narration earns its keep by supplying the senses the image cannot — smell, texture, sound, weight — never "she felt afraid."
- **Clock-anchor the dread.** Specific times before specific events; tighten the intervals as the catastrophe approaches. The clock becomes a character.
- **Name the surrounding humans.** Naming signals research; anonymity (when the record lost the name) is itself a deliberate, named refrain — not vagueness.
- **Narrator-to-viewer irony at act transitions.** At least once, the narrator steps briefly outside the frame to name what the viewer knows and the characters do not ("It had no idea what was coming next"). This is what pulls retention across an act break.
- **Plant seeds early, harvest them late.** One or two specific factual details mentioned as if incidental early, returned to with weight at the close.

### The close

- **End on the image, then reflect.** The final beat is an image held by a single weighty line. Then — and this is the move most often missed — a **moralised closer that reflects the event back at the present-day viewer.** Not "thanks for watching." The viewer should leave holding something they did not have at the start. (Image first; reflection second; the two are not in tension.)

### One pacing reality to plan around

Inworld renders narration **faster** than the nominal estimate — measured around 150–190 wpm against a 135 wpm plan, i.e. the rendered cut is shorter than the word count predicts. Plan length with that in mind (write a little long if you want a specific runtime). It does not affect sync — the pipeline measures the real audio with Whisper at the audio gate — but it does affect whether you hit a target length.

---

# PART V — Channel positioning briefs

*The pipeline is one machine; these three channels are three different films. Read the one you are writing for. Each brief is only what you need to position and write a script — not the strategy, not the backlog.*

### Quick reference

| | Final Hours | Synthetic Press | Lazarus Films |
|---|---|---|---|
| Premise | The last hours of people and places history remembers | The human drama of the AI era — AI-drama, not AI-doom | Dignified cinematic adaptation of public-domain dramatic writing |
| Mode | **Mode A only** | **Dual-mode (A + B)** | **Mode A, narrated** (no lip-sync yet) |
| Register | Dread-and-dignity, present tense, mournful | Documentary witness — calm, not panicked, not gleeful | Dignified-literary, period-aware, reverent, never camp |
| Runtime | Long-form: 12–16 min, up to ~28–32 for city pieces | 15–20 min | 12–15 min |
| Voice | Victor (Inworld) | Peter (human) for marquee; Victor as scratch | Single literary narrator (to be set) |
| `channel:` header | `final_hours` → `final-hours/` | **`synthetic`** (not `synthetic_press`) | confirm folder before first run |
| Status | Live, primary | Flagship, launching | Designed, not yet built |

---

## V.1 — Final Hours

**Premise.** Faceless AI-recreated history: the last hours of one human story inside a larger catastrophe. The camera stays with one named person (or, in the city-catastrophe sub-series, one named place) while history happens around them. The catastrophe is the setting; the dignity, cowardice, or bewilderment of the subject is the subject.

**Mode.** **Mode A only.** No Mode B cards. This is the signature, and it is also why the current pipeline runs Final Hours cleanest — the composition scan skips the Mode B leg, and there are no silent-card problems to manage.

**Register.** Dread-and-dignity. Mournful, considered, slow. **Present tense, third-person omniscient witness** ("He is thirty-three years old. He plays the violin."). Never action, mystery, conspiracy, or breezy explanation. If a topic doesn't fit that mood, it is wrong for Final Hours regardless of how interesting it is.

**Runtime.** Long-form is now the correct format — minimum 12–16 minutes, and the city-catastrophe pieces run inside the proven 20–32 minute band. (The old 7-minute, 84-beat fixed grid is **superseded**; long-form delivers roughly three times the absolute watch time and is what the velocity data favours.)

**The craft spine, applied.** All of Part IV applies, plus three Final Hours specifics:
- **Acknowledge the recreation once, early** — a single museum-placard line of real sources ("recreated from the household accounts, the British Library letter, and the parliamentary investigation"). For the city sub-series this is better *woven into* a "rebuild the city as it actually stood / here is what's in the ground" framing than stated as a disclaimer.
- **Anonymity as craft.** When the record lost the name, never invent one — name the absence, as a refrain, three times across the script. This unlocks the face-never-resolved production win.
- **The moralised closer is the most commonly missed beat.** End on the image, then reflect it at the present-day viewer.

**The city-catastrophe sub-series** (the Troy/Arthur lane — a famous place, a catastrophe, an open visual lane, and ideally a timing catalyst):
- **Title grammar:** `[Place] [Year]: [doom hook] (AI Reconstruction)` — e.g. *Troy 1184 BC: The Night the Trojan Horse Ended the War (AI Reconstruction)*.
- **The six-beat hook:** (1) dateline; (2) in-medias-res catastrophe, present tense, with numbers; (3) the toll; (4) the pivot — "but before this [doom], [the city] was…"; (5) three curiosity-gap wonders; (6) handoff to the narrator/the rebuild.
- **Callback frame:** open on the catastrophe image (which is also the thumbnail), then earn it across the episode and return to the identical frame near the end ("you've seen this before — except now you know whose city it is").

**Visual signature.** Warm, painterly, cinematic; faceless; scene canons with angle-variation; palette shifts by act (glory/daylight → doom/ember-and-night → present/cool documentary for an archaeology coda). 16:9.

**Gotchas.** `channel: final_hours` resolves to `final-hours/` (confirmed live). Nothing else channel-specific blocks a run.

---

## V.2 — Synthetic Press

**Premise.** AI-native cinematic documentary on the human drama of the AI era — **AI-drama, not AI-doom.** Real people, real rooms, real moments (boardrooms, founding dinners, the 2am phone calls). It sits at the confluence of the doom audience and the exposé audience; the differentiator is that nobody else *dramatises* these events as cinema.

**Mode.** **Dual-mode.** Roughly Mode A 60–70%, Mode B 30–40%. Mode A carries the human moments and emotional interiors; Mode B carries the evidence — a figure to absorb, a quote, a tweet, a filing, an org change. **Author the full continuous Mode A narration first, then promote phrases to Mode B** (Part II). Every promoted phrase stays spoken and short (≤ ~12–15 words). Do not author wordless cards.

**Register.** Documentary witness — curious, not panicked, not gleeful. Third-person omniscient with occasional companion phrasing ("we step into the boardroom"). **Present tense for the specific hot moments** (the verdict, the firing, the founding dinner); **past tense for context** (structures, valuations, equity). Controlled tension closer to *The Social Network* than to horror. Stylised recreation, never photographic deepfake; reference documented events; **never invent dialogue.**

**No lip-sync — and this shapes the writing.** The recreated figures are *seen, not heard* — mouths stay closed. Real lines land as the narrator's voice over a wordless visual world, which makes the **"spoken line and its receipt"** pattern the signature move: the **voice** says the line; a **Mode B card** carries the words plus name/source/date (the citation the voice omits); a **highlight** sweeps the stressed phrase as it's spoken. No karaoke — the card never duplicates a full sentence the narrator is also reading.

**Runtime.** 15–20 minutes. **Voice:** Peter's own broadcast-trained read for marquee episodes (a costly, uncopyable trust signal); Victor/Inworld as scratch.

**Packaging.** Doom/exposé-curiosity title grammar, documentary-restraint delivery — win the click from the neighbourhood, deliver the calmer register that earns the subscribe. The SYNTHETIC wordmark and cold near-black/indigo palette are constant; cinematic-recreation imagery (never stock, never webcam) is the one signal that separates it from both neighbourhoods.

**Gotchas.**
- **`channel: synthetic`**, not `synthetic_press` — the alias does not resolve to the `synthetic/` folder. This is the exact mismatch that halted an early dry-run.
- **Upload leg / YouTube OAuth is not set up** for Synthetic — render-side runs fine, but publishing is a future manual setup step.
- 1080p master.

---

## V.3 — Lazarus Films

**Premise.** Dignified cinematic adaptation of **public-domain dramatic writing** — novels, plays, short stories — done with respect, not spectacle. The third panel of a worldview (Final Hours = the end; Success Coach = the journey; Lazarus = the return/resurrection). The counter-position to public-domain slop reboots.

**Status.** **Designed, not yet built.** The first three are sequenced as *Sredni Vashtar* (Saki — the technical proof), *The Maltese Falcon* (Hammett — the brand statement, targeted at the Astana AI Film Festival, deadline 15 August 2026), and *The Loving Spirit* (du Maurier — opens on the 1 January 2027 public-domain drop).

**Mode.** **Mode A, narrated, no lip-sync — for now.** The near-term Lazarus film is narrated literary adaptation in the same wordless-visual-world contract as Final Hours and Synthetic, only literary in register. **Dialogue-driven works that need characters to actually speak (the Maltese Falcon ambition) require multi-speaker / lip-sync capability that is not built — do not script for spoken dialogue yet.** The first films must work as *narrated* adaptations.

**Register.** Dignified-literary, period-aware, restrained, reverent, never camp; sentence rhythm matched to the source author's. The algorithmically warm starting cluster is **atmospheric horror / supernatural dread** (Saki, Bierce, Stevenson, M.R. James, Jacobs, Blackwood) — start there for the first several films, broaden deliberately later. Title language: *[Work] — A [Author] Adaptation (AI Cinematic Recreation)*.

**Craft specifics on top of Part IV.**
- **Cold open from the source, not exposition.** Open on two lines of dramatic dialogue or atmospheric mood drawn from the work itself, then pull back to the narrator (the Tony Walker pattern) — e.g. the boy's prayer to Sredni Vashtar under music, then "I'm [narrator]. Welcome to Lazarus Films."
- **Honour the text.** The adaptation serves the source; it does not out-angle or modernise it.

**The look-override mechanism (unique to Lazarus).** Lazarus is the channel built on **per-film look overrides**: `channel.json` carries the house defaults, and each film drops a `look.json` on top — *the channel owns the frame, the film owns the interior*. Final Hours and Synthetic don't use this; Lazarus does.

**Gotchas.**
- **Confirm the channel folder and `channel.json` before the first run.** Lazarus has been referenced historically under `channel-3/`; a real `channel.json` (voice, resolution, default look) must exist and the header `channel:` must match that folder name, or preflight halts.
- The festival-cut workflow (slate + credits) is a future pipeline build, not a script concern.

---

# PART VI — Crossing the threshold (the bridge into the machine)

The script is locked. Here is the exact path from `script.md` to a running orchestrator. This is the part that, missing one flag, halted us on the Troy live run — so it lives here, in full.

**1. The `script.md` shape.** Header (four keys) → blank line → `## COLD OPEN` → `## PART ONE`, `## PART TWO`, … Each beat is `[A]` + narration on one line, then `VISUAL: …` on the next, then a blank line. (Mode B beats only for dual-mode channels: the spoken line ABOVE the `[B:Component] …` tag.) Numbers spelled out in narration; numerals fine in the header.

**2. Parse — always write both files.**
```
python shared/parse_script.py <channel>/projects/<slug>/script.md \
  --json      <channel>/projects/<slug>/beats.json \
  --json-full <channel>/projects/<slug>/beats_full.json
```
`beats.json` is the flat list the leg tools read; `beats_full.json` is the `{header, beats}` wrapper the orchestrator reads.

**3. Verify before spending (the cheap check that catches everything).**
```
python3 -c "
import json
b=json.load(open('<channel>/projects/<slug>/beats.json'))
bad=[x['index'] for x in b if not (x.get('narration') or '').strip()]
novis=[x['index'] for x in b if x['mode']=='A' and not (x.get('visual') or '').strip()]
print('beats:', len(b), '| modes:', {m: sum(1 for x in b if x['mode']==m) for m in {x['mode'] for x in b}})
print('wordless beats:', bad if bad else 'none')
print('Mode A beats with no VISUAL:', novis if novis else 'none')
"
```
Confirm: every beat has narration, every Mode A beat has a VISUAL, the mode mix matches intent. A wordless beat or a missing VISUAL caught here costs nothing; caught after TTS and renders costs money and time.

**4. Dry-run — and pass `--project`.** The orchestrator reads the *channel* from the header but still needs the *project* to know where to write artifacts. `--beats` alone halts with "channel/project unresolved." The correct command:
```
python3 shared/orchestrate.py --project <slug> \
  --beats <channel>/projects/<slug>/beats_full.json --log normal --dry-run
```
Read the output: the banner should name the project (not "(unnamed)"); preflight should confirm the header is complete and the channel folder resolved; and the decided legs should be what you expect (Mode-A-only channels: `audio → modeA → convergence`, with the Mode B leg explicitly skipped).

**5. Live, and the gates.** Drop `--dry-run`. Then:
- **Audio leg** runs unattended (TTS over every beat, then Whisper). At the **audio gate**, type `keep` to use the rendered read (or `swap` to substitute a human recording, which re-measures timing from it).
- **Mode A stills** render. At the **Mode A stills gate**, the orchestrator prints the box-server / laptop-tunnel / browser block and waits for `go`. **The gate is honour-system — it does not check that you opened the review page**, so actually review the stills before typing `go`. This gate holds indefinitely and spends nothing further until you proceed, so it is the safe place to leave a long run parked.
- After `go`: animation (Kling), then convergence assembles `final_video.mp4`.

**6. Know what isn't there yet.** There is no `--from` resume, so a re-run re-spends every leg from the top — review carefully at the stills gate rather than restarting. The publish half of convergence (thumbnail gate, schedule gate, upload) is built for some channels and not others; treat upload as a separate, channel-specific step.

### Pre-flight checklist

| Check | Pass condition |
|---|---|
| Header complete | `channel`, `title`, `description`, `tags` all present |
| Channel resolves | `channel` matches a folder with `channel.json` (or its hyphen/underscore swap) |
| Every beat has words | verify one-liner reports `wordless beats: none` |
| Every Mode A beat has a VISUAL | verify one-liner reports `Mode A beats with no VISUAL: none` |
| Numbers spelled out | scan narration — no bare digits the TTS would mangle |
| Granularity | no beat over ~55 words; long passages split |
| Mode mix matches the channel | Final Hours / early Lazarus → all `A`; Synthetic → A + B |
| Mode B beats short | each promoted phrase ≤ ~12–15 words, ≤ ~4 s |
| Dry-run clean | plan is the expected legs; no preflight halt |

---

## Appendix — one-screen card

**The constitution (author to these from the first line):**
1. Every beat has spoken words — wordless beats halt the build; silence is unavailable, not authored.
2. Header carries channel/title/description/tags; `channel` matches the folder.
3. Spell out numbers in narration; numerals fine in metadata.
4. One VISUAL per Mode A beat; it is the image prompt.
5. Lock the script first — everything downstream is bound to it.
6. ~5–12 s per beat (~15–35 words), hard ceiling ~55; split long passages.

**The channels in one line each:**
- **Final Hours** — last hours of a person/place; Mode A only; present-tense dread; long-form; `final_hours`.
- **Synthetic Press** — AI-era human drama; dual-mode (promote phrases to Mode B); documentary witness, mouths closed; `synthetic`.
- **Lazarus Films** — dignified PD adaptation; Mode A narrated, no lip-sync yet; literary register; confirm the folder first.

**The threshold:** parse (both files) → verify one-liner → dry-run **with `--project`** → live → `keep` at audio, review then `go` at stills → `final_video.mp4`.

---

*v1.00 — first edition, written immediately after the Troy episode end-to-end run. Precedence rule: this document supersedes the silent-beat/hold model, the separate metadata.json, and the 7-minute fixed-grid Final Hours format wherever older notes still describe them. Maintenance: bump the version and note the change when a new run banks a lesson that changes how a script should be authored before it enters the machine.*
