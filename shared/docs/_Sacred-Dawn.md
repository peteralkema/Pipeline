# Sacred Dawn — Channel Doctrine
*The single consolidated channel reference for Sacred Dawn (@sacredawn). Load this — with the four `_` system docs — on any Sacred Dawn session. Captures positioning, the creation logic, competitive analysis, the moat, content model, craft spine, packaging doctrine, the episode backlog, config facts, and roadmap.*

*Consolidated 11 June 2026 from the launch-night creed (10 June).*
*Updated 19 June 2026 — second pass. Folds in: the ten-video cosmic/primeval **batch** (§8); the switch to **curated Artlist** music (§5, §9); the **thumbnail pipeline** + `.thumb.json` schema (§7, §9); the **two-lever retention model** and **script-authoring rules** (§6); the cleared **pipeline-prep gate** (§9, §10).*
*Updated 20 June 2026 — third pass, THE SATAN FLAGSHIP SESSION. The most important production session to date. Folds in: the **flagship method** — taking the channel's single worst-retaining video (War in Heaven) and rebuilding it into the strongest film the channel has produced (§2b, new §6b); the **data-driven rebuild workflow** (pull the loser's retention curve → diagnose WHY it bled → rebuild as open-loop story → multi-pass authoring with human review → calibration to real markup; §6b); the **audio professionalisation lessons** (MUSIC_LEVEL 0.07→0.040 channel-wide; LUFS measurement as the instrument, not the ear; §5b); the **chapters/description doctrine** (§7b); and the **bottom-left thumbnail authority lesson** — the single biggest packaging insight of the session (§7, rewritten). Satan is rendered + scheduled but NOT yet judged by audience — the NexLev retention read is diarised for ~mid-July (§10).*

*The `_` prefix floats it to the top of `shared/docs/`; it is **channel-scoped, load-on-demand**, not a system doc.*

*[Phrasing note, carried from 11 June: lead with "cinematic recreation," the word that carries the un-referenced-sublime thesis. Treat "cinematic recreation" as canonical throughout.]*

---

## 0. What this is, in one paragraph

**Sacred Dawn** is a faceless, fully-AI cinematic channel that renders the Bible's cosmic and primeval drama — Creation, the Fall, the Watchers and the Nephilim, the Flood, Babel, Sodom, Leviathan, the plagues, the long day, the fire on Carmel — as ~16–25 minute documentary-films. The pitch in one line: *the Bible's origin story, told as a film series.* Reverent, majestic, never shock-bait. It runs on the same channel-agnostic pipeline as Final Hours and You Had To Be There — one config file (`sacred-dawn/channel.json`) and content, no new code. It is the highest-fit use of the machine found to date, for a reason this document exists to make explicit: it is the lane where AI's weakness becomes the genre's requirement. As of 19 June the channel has its launch film live ("The Watchers / Before the Flood"), the Book of Giants film rendered, and a **ten-video cosmic/primeval batch authored, gate-clean, and pipeline-prepped** (§8) — held for an unattended batch-of-batches run.

---

## 1. Positioning

- **Premise:** the cosmic/primeval drama of scripture, rendered cinematically — the Bible's origin story as a film series.
- **Register:** reverent, grand, liturgical, mournful-and-awed. Dread-and-dignity transposed from Final Hours to the sacred-primeval. Present-tense witness. Never sensational, never "BANNED / TERRIFYING / what they're hiding."
- **Handle:** `@sacredawn` · **Display name:** Sacred Dawn · **Tagline (banner):** "The Bible's origin story, retold" (NOT "awaken the divine within" — that's new-age and off-genre).
- **Audience:** the faith + biblical-mystery audience — large, high-RPM, and crucially **AI-indifferent** (embraces rendered imagery; does not forensically fact-check it). It is **not** reverence- or quality-indifferent — see §4.

---

## 2. The thesis — why this channel exists

### The strategic chain that led here

We started from the operation's banked filter: **un-filmable vs. re-watchable.** The machine's edge is un-filmable lived/visionary experience; it's a poor fit for re-watchable media that exists in crisp HD, where an AI impression reads as wrong to an AI-sensitive audience.

We tested **military** first. It failed — not for lack of demand (it's one of the most saturated, monetized faceless lanes on YouTube), but because it's the worst quadrant *twice over*: most of it (WW2, Vietnam, modern war) exists in archival footage the engine can't produce and shouldn't fake, **and** the war-buff audience is the single most AI-hostile audience on the platform. Channels literally sell "(No AI)" as a feature (Commanders and Tactics) and "a fully human team" as a virtue (Historia Militum). Wrong fight.

We then scanned for the inverse: un-filmable, AI-*indifferent*, monetized, beginner-open, clear of the existing channels. **Biblical cosmic-primeval recreation** passed every filter harder than anything else — and the cosmic-origins sub-lane (Watchers / Nephilim / Flood / forbidden knowledge) is both the highest-pull and the worst-served-visually slice of it.

### The principle this channel is built on: the un-referenced sublime

*(Banked 10 June 2026, confirmed in the first stills review; reconfirmed across the 19 June batch — every one of the ten scenes is un-photographable.)*

The reason biblical-primeval is the **highest-fit use of the machine** is that it closes both failure modes at once:

- **No audience-side reference.** No one has footage of the Watchers descending, a giant over a mud-brick house, the sea splitting, the destroyer passing over a marked door, or the sun frozen above a battlefield. The AI image isn't competing with a real photograph the viewer can catch it failing against — it is the *only* image that could ever exist for these scenes. Flux's painterly, slightly-unreal, impossibly-lit quality — the thing that reads as *fake* in military or modern history — here reads as **awe, the sacred, the visionary.** The model's weakness is the genre's requirement.
- **No model-side failure.** The reverent register *wants* the faceless figure, the turned-away silhouette, the colossal shadow, light-as-presence, object-substitution — exactly the craft (ante-machinam Part III) that dodges Flux's one remaining weakness (faces, hands, 3+ figures). Reverence and the production win are the same move. (This also makes the hardest content — Sodom's mob, the tenth plague, Carmel's self-cutting — handleable *by implication*, which is both reverent and advertiser-safe. See §6.)

**The generalizable filter for every future channel:** *Is there a reference the audience can catch us failing against?* If yes (military, modern history in HD, recognizable places/people) → knife fight. If no (scripture's cosmic-primeval scenes, mythology, the deep past, the imagined future) → open water, and the engine is doing what only it can. Sacred Dawn is the cleanest example of open water found so far. The lane the machine was actually built for.

### Why it's durable (the anti-graveyard asset)

The Bible is a fixed, finite, public-domain canon with permanent, non-seasonal, non-trend demand and billions of adherents who re-engage with the *same* stories their whole lives. You cannot saturate the Flood. There is no spike to chase and therefore no crest to fall off. The only saturation risk is in **packaging** (the shock-bait treadmill), which we opt out of by anchoring on the canon — see §4.


---

## 2b. The flagship method — turn the worst video into the best (banked 20 June, the Satan session)

**The single most valuable strategic discovery of the channel so far: the worst-performing video on a channel is the best raw material for its flagship.** Counter-intuitive, and proven in one session on *War in Heaven*.

### The chain of reasoning
*War in Heaven* (Lucifer's fall) was the channel's **worst retainer** — 13:31 runtime, AVD 127s, **15.7%**, a continuous-bleed curve with no plateau (see §6). The instinct is to bury a loser. The correct read, from pulling the actual NexLev data, was the opposite:

- **It out-clicked everything on the channel.** Most lifetime views, most subscribers gained, of any Sacred Dawn video. The title/thumbnail ("How the Morning Star Became Satan") was the channel's strongest magnet. **The demand and the packaging were already proven.** The topic was never the problem.
- **The failure was 100% retention shape, not topic.** Pulled the curve: 95% present at 8s, **49% by 57s**, then a continuous slide to single digits with no plateau ever. That is the signature of a **closed concept** — "here is how X became Y," answer delivered up front, nothing left to stay for.
- **The contrast that proved length isn't the enemy.** *The Watchers' Daughters* is the channel's **longest** video (33 min) AND its **best** holder (AVD 409s, ~20.6%) — same brutal early cliff, but then it establishes a plateau and holds it across the entire back two-thirds, with YouTube's relative-retention score climbing into the top third late. **Length is survivable; an unplateaued curve is fatal.** Your best asset is your longest.

### The flagship verdict
So the move was not to bury *War in Heaven* but to **rebuild it as the flagship** — same proven demand, fixed retention shape — at deliberate, exceptional production investment (40+ Kling, a full ~26-min film, hand-finished packaging). The bet: take the topic the audience already wants, and for the first time actually *hold* them on it.

**The generalizable law (bank for every channel):** before authoring anything new, look at the channel's *worst-retaining but well-clicked* video. High CTR + low AVD = proven demand, broken execution = **the highest-leverage flagship candidate on the channel.** You already know people want it; you just have to make it hold. This is the inverse of chasing a new topic — it's mining the demand you've already paid to discover.

*(Status as of 20 June: Satan is rendered, packaged, and scheduled to publish 21 June 20:00 CEST. The audience has NOT yet judged it. Peter's instinct — and the data-model prediction — is that this rebuild will dramatically outperform the original. The NexLev retention read is diarised for ~mid-July; see §10. Until then this is a well-reasoned bet, not a proven win.)*

---

## 3. Competitive analysis

*All figures from NexLev pulls, June 2026 session. Revenue/RPM are NexLev estimates; treat as directional. The lane is live and beginner-open NOW — multiple channels under six months old already at $3–5k/mo — but entrants are pouring in, which is why speed of execution matters.*

### The biblical cosmic-mystery cohort (the direct competitive set)

| Channel | Created | Subs | Est. $/mo | Signature content | Note |
|---|---|---|---|---|---|
| **Scripture Origins** | May 2025 | ~42.7K | ~$4,108 | Nephilim / Enoch / "biblical mysteries" documentary | "Giants Ruled for 1,636 Years" **1.5M**; "Watchers' daughters" **900k**. The lane leader to study. |
| **Scripture Legacy** | Apr 2025 | ~17.0K | ~$4,133 | Enoch / Nephilim / soul-after-death | "Archangel sent to destroy the Nephilim" 279k; "Before the Flood: Nephilim and Sons of God" 214k. |
| **Biblical Facts** | Aug 2023 | ~66.5K | ~$2,508 | Angels / archangels / Lucifer history | "Complete History of the Angels…Watchers, Lucifer" **712k**; "Metatron" **631k**. |
| **Bible Hidden** | Dec 2025 | ~83.2K | ~$5,276 | Bible mysteries, 3 uploads/wk | Fast climber; explicitly AI-assisted, family-friendly framing. |
| **Immersive Bible Stories** | Apr 2026 | ~28.3K | (climbing) | 70-min "Full Bible Movie 4K" | **2 months old**, 8.05 outlier, ~91k avg views. Proof of how fast a fresh channel breaks here. |
| **Eden \| Bible Animation** | Mar 2026 | ~13.1K | ~$3,775 | Animated full Bible stories | **3 months old → $3.7k/mo.** "Adam and Eve" **1.3M**. The beginner-breakout proof. Animation format (not our lane). |
| **Christian Bible Animation** | Oct 2025 | ~32.9K | ~$1,983 | Animated figures (Leah, Moses…) | Animation format. |
| **Untold Scripture** | (reboot) | ~9.2K | — | "What really happened to…" figures | Solomon 320k, Absalom 229k, Bathsheba 194k — the figure/scandal angle. |
| **Biblical Footsteps** | 2022 | ~49.5K | — | Lived reconstruction ("what Jesus ate") | "Bread Jesus ate" 450k. The un-filmable daily-life angle — adjacent, instructive. |

### Keep watching (the tracking shortlist)

Track these monthly for what's breaking and what's saturating — **Scripture Origins, Scripture Legacy, Biblical Facts, Bible Hidden, Immersive Bible Stories, Eden.** Watch their *outlier* videos (per-video, not channel averages) and the *shape* of new title framings. Mine them for **packaging discipline**, never for content to copy (Phase-2 idea in the flywheel doc: extract structural pattern only, never output — and not before the first batch's own retention is in).

### Lanes considered and rejected (so the reasoning is on record)

- **Military / war history** — rejected. Demand-rich but archival-dependent and the most AI-hostile audience on YouTube. (Battle Probe, WW2 Dossier ~$9.3k/mo, History of Battlefields ~$7.8k/mo, Commanders and Tactics "(No AI)", Historia Militum "fully human team".)
- **Speculative-future / evolution-timelapse** — Timelapse Studio (~$8,200/mo on 3 videos, Paris 2.1M) is hot but a *morph/timelapse* format — **wrong engine** (not still→Kling→narrate), and cloning fast. Skip.
- **Ancient-mystery / archaeology** — First Humans (~$10,969/mo) is strong and AI-indifferent, but it's a packaging/thumbnail game built on short "Scientists Finally Solved…" reveals more than cinematic recreation. Held as a **runner-up lane**, not the pick. (Note: Prehistoric Disasters now occupies an adjacent deep-time lane on the same machine — different channel, different register.)

---

## 4. The moat — durable vs. shock-bait packaging

The money-leaders print on a **packaging treadmill**: "BANNED," "TERRIFYING truth," "what the Church won't teach," "Noah Was NOT Human." That demand is durable; those *framings* are not — you burn shock-hooks faster than you can write them and you swim in the clone swarm on every one. There is also real **YPP / demonetization risk** in that register ("AI slop / reused content"); several cohort channels show monetization not-yet-enabled despite real views.

Sacred Dawn keeps the **curiosity** and drops the **fabrication**:

- Anchor on real questions the canon genuinely raises (who were the sons of God? what was the sin of Sodom? did the giants survive the Flood? was Pharaoh's hardened heart his own or God's?) — mysteries asked for three thousand years, not ones manufactured last Tuesday. *Each batch script ends on exactly such a question as comment-bait — see §6/§8.*
- **Attribution discipline is the moat made literal.** Every supernatural claim is tagged *the Book of Genesis says / the old texts say (Book of Enoch)*; the distinction between canon and apocrypha is stated plainly, in the body, never as cold-open throat-clearing. This is what separates reverent execution from the slop crowd, and it doubles as the theological-fidelity guard that protects monetization. (The Enoch-derived Watchers script keeps this scrupulously — "the old texts say," never occult or conspiracy.)
- **The name is a tonal filter.** Read the shock titles under "Sacred Dawn" and they jar; read the reverent-curiosity titles and they sing. The channel identity quietly disciplines packaging — anything that clashes with the name is probably a title we shouldn't run.

The audience is **AI-indifferent but not quality- or reverence-indifferent.** It won't punish the AI look; it *will* punish cheap recreation and sloppy theology. Both cut toward us — they're exactly the bar best-execution clears and the slideshow factories don't.

---

## 5. The content model

- **Format:** long-form cinematic recreation. The launch film ran ~17.7 min; the 19 June batch deliberately lands tighter, **~16–17.5 min** (measured per script in §8), where retention is easier to hold on a still-cold channel. Long-form maximizes watch-time-dollars (runtime × RPM × mid-rolls) and stacks watch-hours toward the YPP gate fastest.
- **Mode:** **Mode A only** (cinematic recreation; no Mode B graphics). Cleanest pipeline path: composition scan skips the Mode B leg → `audio → modeA → convergence`.
- **Motion:** **front-two-Kling** is the Sacred Dawn signature — `kling_count: 2` (Kling on beats 1–2 to land motion on the cold-open kill zone; everything else Ken Burns). This is set in `channel.json` *and* must be passed to the batch runner as `--kling-count 2` — the runner defaults to 0 (all Ken Burns) without the flag.
- **Voice:** **Elliot** (Inworld; `voice_id: "Elliot"`, model `inworld-tts-1.5-max`). British, deep, majestic, liturgical — "high priest reading scripture." For US viewers this is an *asset*: the authoritative British voice is the conditioned documentary-gravitas cue (Attenborough/BBC/prestige-doc). The risk isn't the accent; it's over-formality tipping cold — controlled at the script level by sensory and direct-address lines. Validate against retention, not speculation. **Register target banked 20 June (Satan): the Charlton-Heston-epic voice — the gravitas of the DeMille/`Ten Commandments`/`Ben-Hur` biblical-epic narrator, the voice the faith audience was raised on (see the film-lineage note, §10b). Elliot at the corrected speaking rate hits exactly this: authority without strain, mournful-and-awed, never breathless. This is the *sound* of the un-referenced sublime — the audience's conditioned cue for "this story is sacred and serious." When a future flagship script is calibrated, read it aloud against that bar: would it sit under a Heston-grade voice, or does a beat force the voice to rush or shout? If it forces either, trim the beat.* *(Note: a hardcoded "Victor" label may still print in the gate log — cosmetic; the read is Elliot. Killing that label is a banked system-doc task.)*
- **Render rate (calibration constant):** **153 words/min.** Target ~16 min ≈ ~2,450 words. Every batch script was verified against this.
- **Look (`style_suffix` / thumbnail suffix):** cinematic biblical epic, painterly oil-painting light, dramatic chiaroscuro, volumetric god-rays, warm gold/amber deepening to storm-grey and ash, weathered antiquity, faceless figures, no text, no modern elements, 16:9. **Palette shifts by act:** glory/daylight → ember/forge-night → storm-grey/water → still grey dawn.
- **Music — curated Artlist library (19 June), level corrected to 0.040 (20 June).** Eight tracks in `sacred-dawn/music/` (`track_01.mp3`…`track_08.mp3`); `channel.json` carries a `music` block `{dir: "music", tracks: 3, crossfade_seconds: 2, level: 0.07}` — but **note the `level` key is INERT** (the mux reads a hardcoded `MUSIC_LEVEL` constant in `assemble_episode.py`, not the block). The assembler picks **3 of 8 at random**, crossfades the joins, loops to fill. VOICE_LEVEL 1.15. *Track-weighting trick: the best bed (Empires Fall) is duplicated (track_07 = track_08), doubling its draw in the random 3-of-8. Music files are gitignored; scp to the box, commit only the `channel.json` block.* **THE BED IS A FEATURE, NOT A BUG: the random 3-of-8 draw produced, on Satan, a score that felt scored to the narrative — quiet under the intimate beats, swelling at the climax — twice, on two different random draws. The well-curated library makes the odds break right. The future leap is score-AWARE placement (use Whisper timestamps + beat energy to place calm tracks under low beats and intense under the climax) — that turns lucky atmosphere into intentional scoring. Banked as an engine horizon item.* See **§5b** for the audio-level lesson — the most important audio learning of the session.
- **Cost:** **under $20 in fal spend per finished video**, regardless of beat count — Ken Burns is free, Kling is the only paid motion leg, and the front-two-Kling policy keeps Kling calls to two per film. Beat count does **not** drive cost; stop framing higher-beat scripts as a spend concern.
- **Upload:** manual for now (channel-agnostic OAuth upload step not yet wired). Category = **Entertainment** (`category_id: "24"`), `privacy_status: private` until the upload step + batch exit-gate land. The 19 June batch is staged for the **batch-of-batches** process (one batch at a time on the box).


---

## 5b. Audio professionalisation — measure with LUFS, not the ear (banked 20 June)

A viewer commented that the music was too loud; Peter heard the same across channels. Rather than nudge by ear, we **measured it** — and turned a judgment call into a number with a threshold. This is the professionalisation pattern for the whole engine: *measure, don't guess.*

### The measurement
`ffmpeg -i <file> -af loudnorm=print_format=json -f null -` reports **integrated loudness in LUFS** (EBU R128, the broadcast standard). On Satan:
- Voice (`voiceover.mp3`): **−20.77 LUFS**
- Music bed at the old 0.07 (linear gain ≈ −23 dB): landed ~**−34.5 LUFS** → voice-to-music gap of only **~13.8 LU**
- Music bed at 0.040 (≈ −28 dB): lands **−39.4 LUFS** → gap **~18.7 LU**

**The broadcast target for narration-over-bed is the music sitting 18–22 LU below the voice.** 0.07 was ~4–6 LU too hot — measurably, not imaginarily. The viewer's ear was right, and now we have the number.

### The fix (shipped, channel-wide)
`MUSIC_LEVEL` **0.07 → 0.040** in `assemble_episode.py` — an idempotent anchor-verified patch, laptop → GitHub → box. Affects every channel on the next render (the constant is shared). Satan was re-muxed at 0.040 (free — cached clips + voiceover, no Kling, no re-spend) and that 0.040 version is the one being published.

### The critical measurement lesson (don't repeat the wrong test)
**Measuring the integrated loudness of the FINAL MIX does NOT show the change** — the voice dominates the integrated number, so dropping a quiet bed barely moves it (0.07 mix −19.54, 0.040 mix −19.57 — near-identical, looked like the fix did nothing). **The right instrument is the bed STEM at its applied gain, compared to the voice.** Measure the track with the gain applied (`-af "volume=0.04,loudnorm=print_format=json"`) and subtract from the voice LUFS — *that* gap is what moved (13.8 → 18.7 LU). Bank this: **judge music level by the voice-to-bed LU gap on the stems, never by the integrated loudness of the mix.**

### Conversion reference
`MUSIC_LEVEL = N` is linear gain; **dB = 20·log₁₀(N)**. 0.07 = −23 dB, 0.040 = −28 dB, 0.030 = −30.5 dB. To push the gap ~2 LU lower, roughly halve the linear value.

### The two engine fixes this exposed (banked, not yet built — see worklog)
1. **Wire the inert `level` key through** so channels can override the 0.040 default per-channel.
2. **Replace the fixed multiplier with a measured-LUFS target** — at assemble time, measure the voice's integrated loudness and normalise the bed via `loudnorm` to land a fixed ~20 LU below, *regardless of source track loudness*. The raw tracks measured −11.49 LUFS with a 15.1 LRA (very dynamic) — fixed-gain scaling can't handle that variance; a LUFS target self-corrects. **This is the real professionalisation of the audio leg.** 0.040 flat is the interim; LUFS-target is the endpoint.

---

## 6. The craft spine (retention)

*The "You Had To Be There" launch gave us Studio-validated retention mechanics; the cosmic-origins genre inherits them in a reverent key. Sharpened 19 June against real NexLev retention curves pulled for this channel into a **two-lever** model plus a fixed authoring checklist.*

### The two-lever model (what actually moves retention)

Retention has **two separate levers**, and they fail for different reasons:

1. **The cold open (universal, topic-independent).** The channel bleeds ~half its audience in the first ~75 seconds *regardless of topic*. The fix is structural, applied to **every** script:
   - Open **inside a concrete moment**, not a thesis. Body-sensation first.
   - **No meta / no throat-clearing** in the open — no "told in a handful of lines," no "drawn from," no sourcing. Attribution moves to Part One and later.
   - **No hollow teases** — deliver the famous line/image immediately, don't promise it.
   - **Every one of the first ~5 beats escalates**; front-load the real payload, including the curiosity hook the title is selling.
   - **Plant the spine image** in the open.
   - Standard cold-open shape: **~8 beats of escalating wrongness**, with the date/place braided in around beats 4–5 (never as an opening brief). **Kling on beats 1–2** so motion lands on the kill zone.
2. **The body (the topic/execution filter).** Past the open, retention is decided by whether the piece is an **escalating STORY, not a concept-explainer.** Promise early, deliver late; one recurring, escalating spine image; reverent attribution lives here (never in the open). Two universal cliffs to engineer against: the early **2–3% cliff** (first 30–40s context-dump) and the mid-video **~50–60% cliff** (the human thread getting abandoned for explanation). **Length is not the lever — topic, execution, and the cold open are.** Best prior performer: *Before the Flood* (AVD 25.3%, plateaus mid-runtime). Worst: *War in Heaven* (15.7%, continuous bleed, no plateau). **Confirmed 20 June against the live NexLev curves: the channel's BEST holder is its LONGEST video — *The Watchers' Daughters*, 33 min, AVD 409s/~20.6%, which establishes a plateau and holds it across the back two-thirds. Length is survivable; an unplateaued curve is fatal. A plateau is built by open loops (promise early, pay late) and act-break re-hooks; continuous bleed is what a closed concept-explainer produces. See §6b for the full rebuild method.**

### The fixed script-authoring rules (every batch script verified against these)

- Beats paired **1:1 with VISUAL** lines; one VISUAL per beat; every beat has narration.
- **Zero digits in narration** — all numbers spelled out (and the em-dash written literally).
- **No beat over 55 words** (the awk/grep gate counts the em-dash as a token, so a flagged 56 is usually 55 real words + dash — trim anyway to clear the gate).
- **Faceless, drift-safe:** silhouettes / from-behind / hands / distant forms; **no resolved faces; God is never depicted** (light, voice, presence only); violence and death **by implication.**
- **Recurring spine object** planted early, harvested at the climax (Flood: the family's loom and the two small sandals; the rain as the countdown drumbeat).
- **Human throughline** present through the entire runtime, including the explanation section (defuses the mid-video cliff).
- **Sensation over description** — supply the senses the still can't (cold on the mountain, heat at the forge, water across bare feet).
- **Plant the thesis early, pay it off late**, turned at the present-day viewer.
- **Close accelerates:** end on the image → moralised closer → **answerable comment-bait question** (this-or-that / yes-no, never rhetorical — the channel had zero comments early; the question writes the pinned comment) → **sequel hook.**
- **Script locked before any pipeline spend.** Scripts are human-reviewed and edited before the machine runs.

### The calibration workflow (banked production lesson)

First drafts consistently land **short on beat-count and runtime with many over-55 beats** (the model writes ~33–42 rich ~52-word beats when aiming for ~58–64). The reliable fix: (1) write and verify; (2) **trim all over-55 beats**; (3) **insert new beats pre-trimmed to ≤52 words** at anchor points; (4) final over-55 sweep. The pre-trimming in step 3 is the key — scripts built this way land at a handful of over-55 flags instead of dozens. Always re-verify after each pass; em-dash inflation means a "trimmed" beat often still reads 56 and needs a second cut.


---

## 6b. The rebuild method — how Satan was built (the repeatable workflow, banked 20 June)

This is the exact, repeatable sequence that turned the channel's worst video into its strongest film. **It is now the standard method for any flagship rebuild.**

### Step 0 — Get the analysis, don't guess
Start from the underperformer's **real retention data**, pulled via NexLev (`get_my_audience_retention` + `get_my_video_analytics`), not from memory or a pasted table. Read the curve *shape*: where does it cliff, does it ever plateau, where does it bleed. For *War in Heaven*: catastrophic 0–60s cliff (95%→49%), then continuous bleed, no plateau, relative-retention bottom-quartile throughout. Diagnose the *category* of failure: this was a **closed concept-explainer**, not a story.

### Step 1 — Reframe topic into story (the open loop)
The fix for "closed concept" is to make it an **escalating story with a question that stays open**. For Satan: reframe *pride* (a flaw) into *betrayal* (a relationship) — "he was loved most, and broke faith with the love that made him." The central question ("how does the most beloved creature become the enemy?") is posed in the first minute and not resolved until the last. Plant a **spine object that pays off an hour later** — here, the *Morning Star name itself*: planted in the cold open, curdled at the turn, and *given back to its rightful owner* (Revelation's "I am the bright and morning star") in the final beat. The whole film became the story of a stolen name.

### Step 2 — Architect for the plateau
Build the body as **acts (~10 min each), every act ending on a cliff that re-hooks** — that is what manufactures plateaus instead of bleed. Satan ran six acts: The Light-Bearer → The Turning → The War → The Fall → The War Comes to Earth → The Promised End. **Cold open in medias res** at the fall itself (the famous image delivered immediately, "Satan" landed by the sixth beat, zero throat-clearing), then rewind. The Act-V pivot — "this is happening to *you*, now" — is the back-half plateau-builder (it's where *Watchers' Daughters* holds its back third).

### Step 3 — Multi-pass authoring WITH human review (do not one-shot a flagship)
A flagship script is built in passes, reviewed by Peter between each, NOT dumped whole:
1. Diagnose + propose the architecture (spine, cold-open fix, act structure) — Peter approves the *approach* before any beats.
2. Write **act by act**, Peter reviewing voice/register/pathos on Act I before proceeding (catches a broken throughline at beat 30, not beat 180).
3. Steer packaging mid-build (Peter's "lead from SATAN, the betrayal, the fall-from-glory" reshaped title + thumbnail + spine).
4. **The calibration pass** (the make-or-break, see §6 calibration workflow): conform the human-review draft to the **real `parse_script.py` markup** (copy a known-good script's shape — NEVER author markup from the doc, it zero-beats), split every over-55 beat, thicken thin acts, strip redundant look-tokens from VISUALs (the `style_suffix` already appends them — double-printing is off-house), re-spec soft-motion beats so Kling has a real animatable foreground.
5. **Parse-proof on the box BEFORE any spend** (`parse_script.py … --json-full`, expect the exact beat count, no ZeroDivisionError). This is non-negotiable for a doc-conformed script.

### Step 4 — Front-load the motion budget on the kill zone
Flagship exception to the `kling_count: 2` signature: Satan ran **`--kling-count 45`** (~$19, a deliberate flagship spend), armoring the cold open + the Turning + the entire war set-piece — the exact stretch where the original hemorrhaged. The cold open *opens at the fall*, so the highest-impact lightning-fall motion lands in the first minute. Everything past the paid zone runs the free Ken-Burns floor — and the back half was authored *for* it (every back-half VISUAL has a single focal point that punches in cleanly).

### The result and the honest caveat
Satan is the strongest film the channel has produced — Peter's verdict: visuals, drama, narrative, the arc, the fidelity of figures and landscapes, the voice, all holding together; moved to tears on both the 0.07 and 0.040 cuts. **But the audience has not judged it yet.** The craft verdict and the retention-model prediction both say this rebuild should dramatically beat the original's 15.7%. The NexLev read in ~mid-July is the actual proof. **The lesson that's already banked regardless of the number: the craft and the retention engineering turned out to be the SAME act — the betrayal arc that moved Peter is the same escalating structure the data predicts will hold viewers. Emotion and metrics are not a tradeoff; they are the same lever pulled well.**

### Authoring footnote — the long-beat stretch warning
The assemble log flags beats stretched 3–4× (a 5s clip held 16–20s) on long-narration beats — a single still held ~18s can feel static even with Ken-Burns motion. For the next flagship, split long-narration beats so no single visual holds that long. (Mitigated on Satan because those beats fell inside the Kling-armored zone.)

---

## 6c. The visual signature — what the Satan frames prove (banked 20 June)

The Satan stills are the strongest visual language the channel has produced. The lessons are reproducible, not lucky — name them so future batches aim at them:

**The visual spine, not just the narrative spine.** §6b banks the Morning-Star *name* as the narrative spine. The frames prove a second, parallel spine: a **recurring visual motif carried across the runtime** — here the **burning wing / falling feather**, glory-becoming-ash rendered in close-up fire dissolving into smoke (the wing-on-fire sequence). It returns through the film as the visual echo of the name's corruption: gold light → ember → ash. **Bank: a flagship should plant a recurring VISUAL motif (an object, a light-state, a body-in-space) alongside the narrative spine, and pay it off in the same beats.** The wing-fire close-ups are the template — abstract enough to be warp-safe (no faces, no hands), specific enough to *mean* something. This is the single most repeatable visual lever from Satan.

**Scale through the lone witness.** The strongest wide frames seat a colossal radiant figure above a low crowd of small, faceless, robed silhouettes, or a single tiny figure under an immense light-vortex. The drama is in the *size ratio*, not in any face. This is the channel's silhouette-witness device (carried from the §5 style) doing the felt-scale job that a National-Geographic-flat composition can't. Keep the subject high-and-huge or the witness low-and-small; never resolve the divine face (§6) — light, wing, vortex, and shadow carry it.

**Fidelity of intent over fidelity of detail, at the frame level.** Every one of these frames works *because* it doesn't ask Flux to resolve the hard thing — the angel is light and silhouette, the fall is a body flat on scorched ground seen at distance, the host is rows of dark cloaked forms. The painterly, slightly-unreal Flux quality reads here as *visionary*, not *fake* (the §2 un-referenced-sublime thesis, confirmed at the still level). **Authoring consequence: a VISUAL prompt that needs a clean face, clean hands, or three resolved figures is the wrong prompt for this channel — recompose to silhouette, scale, or light before spending.**

**Motion earns its place on the spine.** The fire-wing beats are where the flagship Kling spend landed (§6b), and they're the frames people replay. Bank: on a flagship, spend the motion budget on the *visual-spine* beats — the motif that means something in motion (the wing burning, the feather falling) — not on generic establishing shots. Motion on the meaning-bearing image is what reads as cinematic; motion on a wide is wallpaper.

---

## 7. Title & thumbnail doctrine

**Complement, never echo.** The image carries the *what*; the title carries the *why-click*. They must not repeat the same nouns. The recognition noun lives in the thumbnail **subtitle**, the dread/curiosity hook in the **title**, the video title carries recognition + a curiosity clause.

### THE BOTTOM-LEFT AUTHORITY PATTERN — the flagship thumbnail signature (banked 20 June, the most important packaging insight of the session)

**A single hammer-word headline anchored BOTTOM-LEFT carries more weight, gravity, and authority than the same text top-left.** Discovered building Satan's thumbnail, and confirmed by eye: `SATAN / FALL FROM GLORY` seated in the lower-left of a colossal falling-angel image reads like a *film poster* — the title grounds the image, the subject owns the sky above it. Top-left, the same words read like a *label* on the picture.

**Reserve this pattern for FLAGSHIPS.** The standard ten-batch thumbnails keep the locked top-left house anchor (consistency is the brand). The bottom-left treatment is a deliberate, rationed signal that says *this one is an event* — used precisely *because* it breaks the house grid. Overuse it and it stops meaning "flagship." So: **top-left = standard episode; bottom-left = flagship.** That is now a packaging tier, not a one-off.

**Why it also solved a real problem.** The standard top-left anchor *collides* with this channel's grand subjects: a colossal wings-spread angel fills the upper frame, and the headline clips the wing/head. The six working batch thumbnails all share a hidden discipline — the **subject is low and small, the drama is up and to the side**, so the headline owns the empty upper-left by construction. A flagship that *wants* a huge high subject can't use the top-left anchor without a collision. Bottom-left resolves it: subject up, text down, no fight. The aesthetic win (authority) and the compositional fix (no collision) are the same move.

**The flagship single-word title.** Satan also inverted the usual title/subtitle roles: the big slot carried the **recognition noun** (`SATAN`) and the small slot the **emotional hook** (`FALL FROM GLORY`), where the batch does hook-big / noun-small. This works *only* when the recognition noun is also the click-magnet — Satan is the rare word that is both. Don't generalize the inversion; do generalize "lead a flagship from its single most magnetic word."

### How the bottom-left flagship thumbnail was produced (until the engine supports it)
`make_thumbnail.py` has **no text-anchor flag** (the anchor is locked in the `channel.json` thumbnail block, top-left). So a one-off standalone (`make_thumb_bottomleft.py`) was used: it reads `channel.json` for the *exact* house look (Anton, near-white title / amber subtitle, 12px stroke, drop shadow, left scrim) and only overrides the anchor to bottom-left, with a soft bottom gradient to seat the text (darken only where the text lands, never the whole frame). Touches nothing shared. **The proper engine fix is a `--text-anchor` flag** (see worklog) — and the *cheap, deterministic* version is to have the existing substrate-selection Sonnet call also return which corner is clear (`text_corner`) based on where the subject's mass sits, and pass that to the flag. One call, no re-render, text still lands in one of two locked corners so the brand stays consistent. Do NOT build a post-composition re-inspection+re-render loop — that adds a second vision call to every thumbnail to fix a case that's rare.

### The standard doctrine (unchanged, for the ten-batch and routine episodes)

### The two-beat video title

Recognition anchor **+ em-dash curiosity clause.** Pattern, drawn from the batch:
*"Sodom and Gomorrah: The Day Fire Fell from the Sky — and the Woman Who Looked Back."*
The recognition half secures the search/suggest floor; the em-dash clause sells the click.

### The thumbnail pipeline (now wired in `channel.json`)

- Each script ships with a **paired `<slug>.thumb.json`** — exactly three keys: **`subject`** (rich Flux-style scene prose with a deliberate text-clear zone — "the left third kept dark and near-empty for the headline"), **`title`** (UPPERCASE curiosity/dread hook), **`subtitle`** (lowercase recognition noun). No mode/composition field in the JSON — composition lives in the `subject` prose plus the `channel.json` thumbnail block.
- The generator makes **2 candidates**, **Sonnet selects** the best, text is composited as a layer (models can't render legible type).
- `channel.json thumbnail` block (live, 19 June): `composition: "centered_subject"` (confirmed a valid mode in `make_thumbnail.py`), `candidates: 2`, a faceless-biblical `candidate_prompt_suffix` (right-two-thirds subject, left-third negative space, no faces, no text), Anton font (DejaVu fallback), left scrim, `segment_foreground: false`. **`segment_foreground: false` is deliberate** — it composites title-over-scrim and skips segmentation, so **rembg is not required** (and rembg tends to cut silhouettes badly against dark skies anyway).
- **Pairing discipline (bit us this session):** the batch runner pairs by slug — `md.with_suffix(".thumb.json")` — so `<slug>.md` and `<slug>.thumb.json` must share the **exact** base name, dot-named. Mismatched names (e.g. `cain_and_abel_script_draft.md` ↔ `cain.thumb.json`) are **silently skipped**. The inbox must contain only the current batch's matched pairs.
- **Avoid:** stock reaction-faces / pointing fingers (the faceless-channel slop tell), sepia "biblical-mystery" wash, all-caps shock words. **Brand:** the gold "Sacred Dawn" wordmark carries across banner and thumbnails. Squint-test at ~120px.


---

## 7b. Description & chapters doctrine — the professional video page (banked 20 June)

Manual uploads (which flagships are, until the upload step lands) are the chance to ship a **professional description with hyperlinked chapters** — and it's worth doing, because the description is read semantically by the algorithm and the chapters lift watch-time navigation.

### Chapters (YouTube auto-hyperlinks them — no manual linking)
A `mm:ss Title` list in the description becomes clickable chapters automatically **if**: the first is exactly `0:00`, there are **at least three**, and each is **≥10s apart**. 

**Compute the timestamps from `durations.json`, never estimate** — each beat carries `audio_start` (the Whisper-aligned real start in seconds). Map each script section to its first beat's `audio_start`, format `mm:ss`. Estimating from word counts lands chapters 20–40s off — amateur. Satan's seven, computed from the real alignment:
`0:00 The Falling Star · 2:02 The Light-Bearer · 5:17 The Turning · 11:23 War in Heaven · 16:17 The Fall · 19:51 The War Comes to Earth · 23:37 The Promised End`.
**Chapter titles get drama, not section labels** — never expose production language ("Cold Open" → "The Falling Star"); use the searchable phrase where one exists ("War in Heaven").

### The description structure (the template)
1. **Hook paragraph** that sells the betrayal/arc and poses the open question (mirrors the video's own hook).
2. **Source-credibility line** — "Drawn faithfully from Isaiah, Ezekiel, Luke, Jude, and the Book of Revelation, with the older traditions named plainly where they speak." This is the **attribution-discipline moat made public** *and* monetization insurance against the AI-slop/misinformation flag.
3. **The chapter block** (auto-hyperlinking).
4. **The comment-bait question** echoed from the close (writes the pinned comment).
5. **The sequel tease** (Satan → Michael).
6. **A standing disclaimer line** — "All imagery is artistic interpretation; supernatural events are presented as the ancient texts describe them, with canon and tradition distinguished throughout." Keep on every Sacred Dawn description; it's the public face of the §4 moat and protects YPP.

Do **not** keyword-stuff — tags carry SEO; the description reads like a human wrote it. **Engine path:** the durations file already has everything; a future `patch` builds section-name → first-beat `audio_start` → `mm:ss` + a per-channel chapter-title map + the description template. Banked.

---

## 8. The episode slate

### The 19 June batch — authored, gate-clean, pipeline-prepped (the canonical cosmic/primeval ten)

Each script is paired with a verified `.thumb.json`, lands faceless and reverent, and passed every gate (beats = VISUALs, 0 over-55, 0 digits, 0 pairing gaps, `channel: sacred_dawn` header, 3-key thumb). Staged in `sacred-dawn/batch_inbox/` for the batch-of-batches run.

| # | Slug | Video title | Beats | Min | Thumb title / subtitle |
|---|---|---|---|---|---|
| 1 | `cain` | Cain and Abel: The First Murder — and the Mark God Gave the Man Who Did It | 63 | 16.2 | THE FIRST MURDER / cain and abel |
| 2 | `eden` | The Fall: How Paradise Was Lost — and the Promise Hidden in the Curse | 54 | 16.3 | THE FIRST LIE / the garden of eden |
| 3 | `flood` | Noah's Flood: The Day the World Drowned — and the Door God Shut Himself | 55 | 16.8 | THE WORLD DROWNED / noah's flood |
| 4 | `babel` | The Tower of Babel: The Day Humanity Climbed Toward Heaven — and Heaven Came Down | 51 | 16.5 | THEY REACHED TOO HIGH / the tower of babel |
| 5 | `sodom` | Sodom and Gomorrah: The Day Fire Fell from the Sky — and the Woman Who Looked Back | 51 | 17.0 | DON'T LOOK BACK / sodom and gomorrah |
| 6 | `leviathan` | Leviathan: The Sea Monster Hidden in the Bible — and the Dragon God Has Promised to Slay | 46 | 15.8 | IT LIVES IN THE DEEP / leviathan |
| 7 | `watchers` | The Watchers: The Night Two Hundred Angels Fell — and the Forbidden Oath That Doomed the Ancient World | 53 | 16.8 | TWO HUNDRED FELL / the watchers |
| 8 | `ten_plagues` | The Ten Plagues of Egypt: How God Humbled an Empire — and the Night the Angel of Death Came | 50 | 17.0 | DEATH PASSED OVER / the ten plagues |
| 9 | `sun_stood_still` | The Day the Sun Stood Still: The Battle Where God Stopped the Sky — and the Hail That Fell from Heaven | 52 | 16.9 | HE COMMANDED THE SKY / the day the sun stood still |
| 10 | `elijah_carmel` | Elijah and the Fire from Heaven: The Prophet Who Challenged a Kingdom — and the Fire That Answered | 53 | 17.4 | FIRE FELL FROM HEAVEN / elijah on carmel |

**Lane logic for the batch.** Sacred Dawn owns the **cosmic / primeval / apocryphal / judgment** register; canonical human drama (Isaac, Jacob, Joseph, Samson) is Scripture On Screen's lane and was deliberately avoided. Each script is an **escalating story**, not a concept-explainer. Notable craft choices banked:
- **Non-cannibalization with existing films.** `watchers` is the *origin* (the oath on Hermon, the descent, Azazel's forbidden knowledge, the archangels' verdict, Enoch's denied petition) — built to **not** retread the launched Watchers film or the Book of Giants film; one callback line hands the giants' horror to Book of Giants ("told in another place"), and the close hooks the Flood and Enoch.
- **Hard content handled by implication** (reverent + advertiser-safe): Sodom's mob and Lot's offer, the tenth plague's deaths, Carmel's self-cutting — all veiled by the text's own restraint and rendered as marked doors, rising cries, shadow.
- **Sequel architecture.** Flood ↔ Babel bookend; Ten Plagues hooks the Red Sea; Sodom carries the mercy-before-judgment spine (Abraham's bargain → "remember Lot's wife"); Leviathan escalates deep-as-chaos → Jonah → Job → chaos-dragon → "the sea was no more."

**Sequencing discipline.** Ship the batch, then **hold further scripts until the first retention reads land** (power-law discipline — don't bank new content directions before cold-start data supports them). Best-first ordering; do **not** let channel averages drive sequencing (best-first drags averages by construction). Judge per-video on outlier score + retention **shape**.

### The Satan flagship (20 June — rendered, packaged, scheduled; audience verdict pending)

| Slug | Video title | Beats | Min | Kling | Thumb |
|---|---|---|---|---|---|
| `satan-morning-star` | Satan: How Heaven's Most Beloved Angel Became God's Enemy — The Fall of the Morning Star | 89 | ~26.4 | **45** | SATAN / FALL FROM GLORY (**bottom-left flagship anchor**) |

The channel's first **flagship rebuild** (§2b, §6b): *War in Heaven* — worst retainer (15.7%) but best-clicked topic — rebuilt as an 89-beat open-loop betrayal epic. Six acts, in-medias-res cold open at the fall, the Morning-Star-name spine paid off across the full runtime, `--kling-count 45` armoring the kill zone. Music at the corrected 0.040 (§5b). Professional description + seven auto-hyperlinked chapters (§7b). Scheduled 21 June 20:00 CEST, private until publish. **The audience verdict (NexLev retention vs the original's 15.7%) is the open question — diarised ~mid-July (§10).** Drawn from Isaiah, Ezekiel, Luke, Jude, Revelation, with the apocryphal refusal-to-bow (Life of Adam and Eve) named as tradition.

### Prior films (already live / rendered)
- **The Watchers / "Before the Flood: The True Story of the Nephilim and the Watchers"** — *launched 10 June.* 52 beats, ~17.7 min, Elliot. Thumbnail "ANGELS OR GIANTS?". The headwater.
- **The Book of Giants: "The Lost Story of the Nephilim — and the Demons They Became"** — rendered (`sacred-dawn/projects/book-of-giants1/final_video.mp4`).

### Deeper backlog (held; mine per-video outliers before sequencing)
**The War in Heaven / Lucifer's fall — REBUILT 20 June as the `satan-morning-star` flagship (§2b/§6b/§8); the original is retired.** The Book of Enoch (the scribe who walked with God — strong sequel to `watchers`), The Bloodline That Survived the Flood (Anakim → Rephaim → Goliath), The Garden's Other Tree (Tree of Life / flaming sword), The Watchers' Teachers One by One (Azazel deep-dive — only if the forbidden-knowledge beats spike), the Red Sea (hooked by `ten_plagues`), the still small voice (hooked by `elijah_carmel`).

---

## 9. Channel config & facts

- **Handle:** `@sacredawn`. **Display name:** Sacred Dawn (set deliberately in create-flow; don't auto-derive from handle).
- **`channel:` header value:** `sacred_dawn` → resolves to `sacred-dawn/` via the underscore→hyphen swap. **Channel ID:** `UCs-VNV8IY6eiklcKprDWqIA` (connected to NexLev).
- **`channel.json` schema** (matched to `final-hours/channel.json`): `name`, **`voice_id`** (snake_case — `voiceId` silently falls back to Victor), `style_suffix`, `base_canon`, `upload: {category_id, privacy_status}`, plus the blocks added 19 June below. **No resolution key** (the `?x?` in the preflight banner is an unset slot with a working default — ignore).
- **Blocks added 19 June (via `shared/patch_sacred_dawn_blocks.py`, laptop → GitHub → box):**
  - `thumbnail` — `composition: "centered_subject"`, `candidates: 2`, faceless-biblical `candidate_prompt_suffix`, Anton font (+ DejaVu/Impact fallbacks), left scrim (`width 0.42, opacity 0.55, feather 0.7`), top-left text anchor, `segment_foreground: false`. (Ported from the proven prehistoric block, then overridden for biblical faceless.)
  - `music` — `{dir: "music", tracks: 3, crossfade_seconds: 2, level: 0.07}`. Eight Artlist tracks placed in `sacred-dawn/music/` on the box and ffprobe-verified as real audio.
  - `kling_count: 2`.
  - The patch is idempotent (refuses unless name resolves to `sacred_dawn`, backs up to `channel.json.pre_blocks`, no-ops if already applied).
- **Voice:** `voice_id: "Elliot"`, model `inworld-tts-1.5-max`.
- **Project / batch paths:** films at `sacred-dawn/projects/<slug>/`; batch inbox at `sacred-dawn/batch_inbox/` (matched `<slug>.md` + `<slug>.thumb.json` pairs only). Music at `sacred-dawn/music/`.
- **Category:** Entertainment (`24`), not People & Blogs. Tags from the header.

---

## 10. Launch state & roadmap

**Launched 10 June 2026 — "The Watchers."** Continuity QC clean, audio gate cleared, genre validated the engine ("this genre is perfect for AI images").

**20 June 2026 — the Satan flagship session (the channel's most important to date).** The flagship-rebuild method proven end to end (§2b, §6b): worst video → strongest film. Audio corrected channel-wide to 0.040 with LUFS measurement (§5b); the bottom-left flagship thumbnail pattern banked (§7); chapters/description doctrine banked (§7b). Satan rendered, packaged, scheduled — audience verdict diarised mid-July.

**19 June 2026 — ten-video batch authored + pipeline-prep gate cleared.** All ten scripts + thumbs gate-clean (§8). Channel brought up to the post-launch pipeline standard:
- `channel.json` patched with thumbnail + music + `kling_count: 2` blocks (idempotent patch, shipped laptop → GitHub → box, confirmed applied).
- Both pipeline mode-strings confirmed in source: `centered_subject` valid in `make_thumbnail.py`; music loader globs `*.mp3` and picks N at random.
- Eight Artlist tracks placed in `sacred-dawn/music/` and verified as real audio (durations 0:41–2:44; Empires Fall intentionally duplicated to 2× weight). `segment_foreground: false` confirms rembg not needed.
- 20-file inbox (10 matched, slug-corrected pairs) packaged and ready to extract into `sacred-dawn/batch_inbox/`.

**Pending (the next actions, in order):**
1. **Fire the batch-of-batches run** for these ten — `--kling-count 2`, one batch at a time on the box (Whisper/ffmpeg are CPU-bound and contend under parallel batches). Manual upload per video (Entertainment, private) until the upload step lands.
2. **First retention reads.** These are the data gate. The new batch is **not yet live**, so there is no fresh per-video retention to pull yet — that is exactly what gates episode sequencing and any new content direction.
3. **★ MEASURE THE SATAN BET (~mid-July 2026).** Pull the `satan-morning-star` retention curve + AVD/CTR via NexLev and compare against the original *War in Heaven* (13:31, AVD 127s, **15.7%**, continuous-bleed). The flagship-rebuild thesis (§2b/§6b) predicts a dramatically better hold — a real plateau instead of a bleed. **This is the proof of the whole flagship method.** Read: cold-open hold (first ~75s), whether a mid-runtime plateau formed (the open-loop/act-break payoff), CTR on the bottom-left flagship thumbnail, and which acts spike. **★ Pin this video-specific watch-point: the ~8-minute mark, where the angelic drama pivots to the human creature (man made, the command to bow). YouTube's own analysis tool independently flagged it as the likely retention seam — it maps onto the §6 mid-video-cliff risk (camera leaving one thread for another). If the curve dips there, the next-flagship lesson is to smooth or re-hook across the angelic→human pivot.** Early qualitative signal (publish day): a returning channel viewer (@Solarpunk97) commented “I've watched every single one of these! More please!” sixteen minutes in — the demand thesis (§2b) showing up before the numbers can. One comment isn't data, but it's the right kind of early sign. Peter's instinct says this one is special — confirm or correct it with the data, don't assume.
4. Banked system-doc tasks (do between batches, never while a run is parked): auto-launch the review server before the stills gate; kill the hardcoded "Victor" gate label (read `voice_id` dynamically); regenerate the on-genre banner + fix the tagline.
5. **Add a Sacred Dawn brief to `ante-machinam.md` Part V** once the first batch's retention lands.
6. **Engine upgrades surfaced by the Satan session** (tracked in the worklog; channel benefits directly): the `--text-anchor` thumbnail flag (enables bottom-left flagship thumbnails natively + the cheap Sonnet `text_corner` selection); the music `level`-key wiring + the LUFS-target normalisation (§5b); a chapters/description auto-builder from `durations.json` (§7b); score-aware music placement (§5).

**Watch on the first batch:** cold-open retention (first ~75s — the universal lever), the mid-video ~50–60% cliff (did the human throughline hold it?), CTR per thumbnail hook, whether Elliot's register holds US viewers, and which beats spike. Let the data — not speculation — drive what ships next.

---

## 10b. The audience is a century old — the film lineage (banked 20 June)

A strategic grounding, not a craft rule: **this audience has been served by spectacle-plus-reverence for over a century**, which is the §2 anti-saturation thesis proven by film history. The lineage Sacred Dawn inherits: DeMille's silent and 1956 `Ten Commandments`, `Ben-Hur`, `The Robe`, the golden-age biblical epics; John Huston's `The Bible: In the Beginning` (1966) — which dramatizes Creation, Eden, Cain/Abel, the Flood, Babel, Sodom: *this channel's exact slate, sixty years ago*; DreamWorks' `The Prince of Egypt` (1998) — the craft model, which renders God as **light and layered voice, never a face** (the §6 rule, validated by the most acclaimed reverent biblical film of the modern era) and handles death by implication; `The Passion of the Christ` (2004) — the business proof that the faith audience shows up in enormous numbers for reverent intensity; and `The Chosen` (2017–) — the current phenomenon, which wins on **character interiority and serialization** (the lever the old tableaux lacked, and the lever Satan reached for by turning pride into betrayal).

**Three things to take from the lineage:** (1) the **voice** target is the Heston-grade biblical-epic narrator (§5 voice note) — the audience's conditioned cue for sacred-and-serious; (2) the **craft** model for the divine is `Prince of Egypt` — light and voice, never a resolved face; (3) the **retention** model is `The Chosen` — make them *care* (interiority), don't just make them *gaze* (spectacle). The strategic punchline: **the budget to render these images used to be a studio's; now it's under twenty dollars.** Sacred Dawn is the cheapest-ever entrant into a century-old, never-saturated market, in the one sub-lane (cosmic/primeval) live-action mostly skips because it can't do the Watchers descending or Leviathan in the deep without looking silly. That is the open water (§2).

---

## 11. Appendix — the packaging test (durable vs. shock-bait, as a feed)

The reframe titles read *coherent* under "Sacred Dawn"; the shock titles *jar*. Run the eye-test before publishing any title.

**Run these (durable — the live batch passes):** "Noah's Flood: The Day the World Drowned — and the Door God Shut Himself" · "Sodom and Gomorrah: The Day Fire Fell from the Sky — and the Woman Who Looked Back" · "The Day the Sun Stood Still: The Battle Where God Stopped the Sky" · "Elijah and the Fire from Heaven" · "The Watchers: The Night Two Hundred Angels Fell."

**Never run these (shock-bait — they print for others but burn out and risk monetization):** "The TERRIFYING Truth About the Nephilim" · "Noah Was NOT Human" · "The Bible's DARKEST Chapter the Church Won't Teach" · "What They're HIDING About the Giants."

*The line: keep the curiosity, drop the fabrication. The canon is the asset; reverent best-execution is the moat.*

---

*Maintained by Peter + Claude. Update this doc when the first-batch retention lands, when a new episode banks a craft lesson, or when the competitive cohort shifts. This is Sacred Dawn's creed: the un-referenced sublime, rendered with reverence, packaged with curiosity, anchored on a canon that cannot be saturated.*
