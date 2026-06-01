# Final Hours — Strategy
*Last updated: 30 May 2026*

---

## Who and where

**Peter Alkema** — based in Kraków (corporate Mac, ABB day job). Solo operator. Former Udemy course creator with deep instructional design background. Vibe-codes in Python. No developers.

Previously ran the "Success Coach" Udemy-course-derived faceless channel for student-success content over six years. That playbook is now archival. Final Hours is the live primary channel; Success Coach (@successcoach100, ~6k subs) is being relaunched on the same pipeline as a second channel using cinematic narrative recreation applied to professional development.

---

## The channel

**Name:** Final Hours
**Handle:** @FinalHours_history (Brand Account under peteralkema2@gmail.com)
**Created:** May 2026
**Format:** Faceless. Inworld Victor narration. Photoreal painterly cinematic stills animated by fal/Kling. 7-minute runtime. 84-beat fixed-grid scripts. Mournful drone-and-strings music bed.
**Niche:** AI-recreated long-form history — "the last hours of people and places history remembers."

**State as of 30 May:**
- Pompeii — published 28 May (Video ID: CkbWHjkQa1Q). Title: *Pompeii Had One Day to Escape. Most of Them Chose to Stay.*
- Anne Boleyn — published 29 May (Video ID: 4A6bLIWMYXc). Title: *They Gave Anne Boleyn One Day To Die. She Made It Last Five Hundred Years.*
- Wallace Hartley (Titanic) — rendered, scheduled to publish at next 01:00 Europe/Warsaw via the upload script's `--schedule-cet-1am` flag. Title: *He Kept Playing.*

---

## Thesis

The channel is not a "history channel." It is a **dread-and-recognition recreation pipeline** — a system for taking one human story inside a catastrophe and rendering it in slow cinematic photoreal form for ~$25 per video. The frame is consistent: the camera stays with one named human while history happens around them. Anne in her chamber, Hartley on the deck, the families at the Pompeii boathouses. The catastrophe is the setting; the dignity-or-cowardice-or-bewilderment of one person is the subject.

Three things make this defensible against competitors who could trivially copy the format:

**The rulebook.** An accumulating per-channel list of caught spell-breakers — anatomy errors, gravity violations, location drift, instrument drift, character-consistency failures. Every spell-breaker caught in stills review becomes a permanent negative rule. Currently ~31 rules in `final-hours/rulebook.json`, layered on top of ~21 universal rules in `shared/rulebook.json`. Universal rules prevent universal failures (anatomy, gravity, illegible text). Channel rules enforce period-specific or topic-specific discipline (Edwardian uniforms render unreliably so default to plain black; only one ship per frame because the documentary-prior keeps duplicating vessels; AI image models can't render legible engravings so frame text obliquely or out of focus).

**The canon mechanism.** A per-video block of named descriptors (`{hartley}`, `{band_deck}`, `{coach_avatar}`) substituted into prompts wherever the subject recurs, so a character or ensemble can't drift across shots. The rule of thumb is brutally simple: anything appearing in three or more shots needs a canon entry. Below three, drift is invisible; at three or more, the eye starts tracking. Canon entries can reference each other recursively — `{hartley_deck}` builds on `{hartley}`. Channel-level base canon (e.g. Coach Alex for Success Coach) is auto-merged into every beat-script.

**The beat-grid architecture.** Scripts are written as N equal-length beats (~13 narration words each, ~5s clip each) from inception. Script, storyboard, and clip sequence are one structure on a fixed grid. This kills narration/footage sync bugs at source. Three videos in, the architecture produces clips that auto-align within seconds of target runtime — Hartley landed at 4.11s/clip × 85 beats = 7:00 narration over 7:05 footage, no manual reconciliation needed.

Tools (fal.ai Seedream/Flux + Kling, Inworld TTS, Claude API, YouTube API, rembg) are commodity. The moat is the three layers above plus accumulated production judgment.

---

## Economics

**Cost per video:** ~$25 in fal credits (mostly Kling animation at ~$0.30/clip × 85 clips), plus negligible Inworld and Claude costs. Roughly 30-90 minutes of unattended render time on the laptop, plus 2-4 hours of stills review and reshoots that decrease per video as the rulebook and canon expand.

**Comparison point.** Chloe vs History (closest format peer, persona/POV vlog style on the same fal stack) costs an estimated $2,000-5,000 per video. Final Hours runs at ~1/100th her cost. The asymmetry means break-even per video is ~3,000-5,000 monetised views (history RPM ~$5-8), versus her ~400,000+. **Dud-tolerance is the whole strategy.** Most videos can do nothing, and one breakout pays for many.

**Channel-portfolio vision (12-24 months):** Final Hours is the first channel. The pipeline is format-agnostic — once a working channel exists, additional channels in different niches (true crime, vanished places, maritime disasters, professional development) launch on the same engine. Per-channel canon + rulebook compound independently. Success Coach is the first portfolio expansion.

---

## Topic principles

Topics are chosen against three filters:

**One human story inside a larger catastrophe.** Not "the Titanic," but "Wallace Hartley on the Titanic." The signature framing. Anne Boleyn's waiting, not the broader Tudor politics. The Pompeii families in the boathouses, not the eruption as geology.

**Dread-and-dignity emotional register.** The channel does not do action, mystery, conspiracy, or breezy explanation. The mood is mournful, considered, slow. If a topic doesn't fit that register, it's wrong for Final Hours regardless of how interesting it is.

**Render-friendly visual range.** Tudor stone is easy. Water at night is harder. Large crowds in panic are harder still. But each new visual era widens the rulebook in a way that compounds for future videos in that setting. Maritime disasters are now significantly easier to produce than they would have been before Hartley, because the rulebook now knows ships, water at night, period uniforms, and instrument continuity.

The "final hours" framing is the channel's signature emotional anchor; it should be visible from the title. Pompeii's title used "one day to escape"; Anne's used "one day to die"; Hartley's uses "he kept playing" — slight variation on the time-quantified-dread pattern but kept the framing of one human's choice.

---

## Operating principles (banked)

Banked decisions across three videos, phrased as principles a future chat or future Peter can act on directly.

### Three attempts is the line.

If a shot has been reshot twice and is still misbehaving, the model has a learned prior we're fighting and writing better prompts won't escape it. The right move on attempt three is to **reframe the concept**, not negate the prior harder. We learned this on Final Hours wide ship shots (model defaults to "Titanic seen from another deck" no matter how explicitly we negate viewing platforms — solution was to reframe as detail shots of the funnel or hull lettering, sidestepping the prior entirely). Same lesson hit on Coach Alex avatar (Seedream's "polished professional male" prior was unfightable; switched models to Flux Pro). When you've hit three attempts, *change the technique*.

### Canonise anything appearing in 3+ shots.

Per-video drift is invisible at 1-2 occurrences and glaring at 3+. The Hartley video taught this expensively — instrument drift, uniform drift, and character drift across many shots, all of which would have been impossible if `{hartley}` and `{band_deck}` had been canon entries from the first stills run. The canon mechanism is now built and mandatory for every future video.

### The rulebook prevents universal failures; the canon enforces per-video continuity.

Two complementary layers that compound. The rulebook says "no figures embedded in floors." The canon says "Hartley is always 33, dark hair, brown wooden violin under his chin." Don't mix the layers — universal rules go in `shared/rulebook.json`, channel-specific rules in `<channel>/rulebook.json`, per-video canon in the beat-script. The architecture currently enforces this split correctly after the multi-channel migration of 30 May.

### Beat-grid first, then images.

Write the script as 84 beats of ~13 words each *before* generating anything. The pipeline ingests beat-scripts directly via `stills --beats <file>.json` — no Claude slicing of prose, no surprise drift between intent and storyboard. Every video so far has hit its runtime target within seconds because the grid was right from inception.

### Auto-fallback is what makes unattended rendering possible.

Kling's content-policy refusals (on execution shots, casts, remains, the sinking) silently downgrade to held-still ffmpeg clips and continue. The pipeline doesn't halt mid-render. Proven on Anne Boleyn (overnight render at Salta steakhouse in Kraków, completed unattended). This is the precondition for cloud migration later.

### Even-spacing assembly absorbs narration-vs-footage slack.

`z = narration_duration / clip_count`; every clip trimmed to z. Means total video runtime exactly equals narration runtime, no frozen ends. Works because Final Hours content is atmospheric — viewers don't notice that clip 23 covers slightly different words than the script writer intended. For tight word-image sync (which we don't need), Whisper-aligned SRT would replace this, but the cost is real and the benefit is small for this register.

### Schedule for 01:00 Europe/Warsaw.

Equivalent to ~19:00 US Eastern. Puts publish at the start of US prime evening, which means YouTube's first impression-expansion test (~6-12 hours after publish) lands on the next US evening when the audience is most active. Built into `upload.py` via `--schedule-cet-1am`. Hartley is the first video using this; Pompeii and Anne went out at less optimal hours and we'll learn what difference scheduling makes by comparing their early curves.

---

## Distribution principles (banked)

### Retention curve shape over all other metrics.

Studio's AI summaries on small samples are noise. View count and CTR averages on 11-50 view windows are noise. The retention curve shape — where viewers drop, where they re-engage — is the real diagnostic. Check it at 100+ views minimum. At lower volumes, anything you'd conclude is over-fitting.

### Cross-promote known fires, not new ones.

The discipline: let the algorithm cold-test each video for 48 hours before pushing to any owned audience. Pushing all videos to the social network flattens the signal of which one is actually worth pushing. If a video shows real algorithmic life at 48 hours, *that's* when cross-posting earns its keep — amplifying a fire the algorithm has already chosen to expand. Pompeii's social push was undisciplined (pushed early); Anne's was better-timed; Hartley's discipline is still to be determined.

### Adjacent owned audiences are higher-signal than personal feeds.

Peter has three owned audiences pre-dating Final Hours: an X "professional insights" following, a 5k Facebook "Student Success Coach" community, and his existing network. Match the video framing to the audience that fits it. Hartley's dignity-under-pressure register is a natural fit for a success-coach community; Pompeii's pure-spectacle frame is less so. Think of the audiences as a portfolio of targeted seed pools, not one broadcast list.

### Format competition is mostly an illusion on a recommendation platform.

Chloe vs History's *Titanic 1912* at 2.16M views in the same algorithmic neighbourhood as Hartley isn't a competitor — it's proven-demand signal. Differentiation is by *register* (dread vs vlog) and *length* (7-minute long-form vs short), not by topic avoidance. Same lane = tailwind if packaging is clearly different.

---

## Production principles (banked)

### People are the emotional core.

The Pompeii v1 lesson: broad anatomy negatives in the rulebook ("deformed hands, malformed anatomy") cause image models to AVOID generating people at all — they satisfy the constraint by producing empty rooms and landscapes. The rulebook now uses *specific* spell-breakers ("visible ribs through skin") not categorical anatomy bans, and a positive `people_directive` ("include people where the narrative calls for them, with natural well-formed faces and hands") shapes anatomy quality positively. Most shots should include human figures; empty atmospheric shots are the exception.

### Wide ship and wide character establishing shots fight the model's documentary prior.

Both Pompeii's wide ship shots and Coach Alex's wide portrait shots hit the same wall: the model has absorbed thousands of "establishing shot of [famous thing]" training examples and defaults there. Solution is to *reframe* — close-detail of one funnel, hands on strings, the ticket on a desk, the violin alone in lantern light. Detail framings sidestep the prior. This is also a craft upgrade disguised as a workaround — close-detail framings keep the camera with the human experience instead of pulling out to documentary distance.

### Image models cannot render small legible text.

Engravings, signs, document text, specific numbers on screens. The Hartley violin plaque lesson, banked permanently. Solution: frame text obliquely, in shadow, or partially out of frame. Tell the model the engraving exists but is not legible. Never rely on the model to produce specific words.

### Hands in empty scenes are a category-specific failure.

If a scene is specified as empty, the model invents disembodied hands at the edges. Banked as the "phantom hands" rule. Solution: frame tightly on objects so there's no space a figure could occupy, and explicitly state "no body parts anywhere in the frame."

### The Flux Pro image model has a more diverse human-face prior than Seedream.

Seedream defaults to catalogue-male / catalogue-female faces. Flux Pro produces more ordinary-looking, less-polished humans by default. Switched the active model on 30 May. Per-still cost slightly higher (~$0.05 vs $0.03) but the quality-of-faces win is substantial enough to make it the new default across both channels. Flux also renders slightly more painterly-cinematic than Seedream, which matches the Final Hours aesthetic well.

---

## Current state

The pipeline works. The economics are favourable. The discipline of catching spell-breakers per video is functioning. The rulebook is genuinely accumulating into a moat — 31 Final Hours-specific rules banked across three videos, each of which prevents a category of failure permanently.

**What hasn't happened yet: a video that gets meaningful algorithmic distribution.** Pompeii at ~26 views and Anne at ~11 views (as of last check) are in normal cold-start range — neither failing nor breaking out. The thesis is unproven at the *outcome* level. The pipeline works; whether the format will earn audience is the question the next month answers.

The economics are favourable enough that a long quiet stretch is sustainable while learning what works. The cost of being wrong on any single video is ~$25 plus a few hours; the cost of being right is potentially years of distribution.

---

## Key files (live working layout)

```
03. Pipeline/
├── shared/
│   ├── recreation_pipeline.py     — the pipeline (multi-channel aware)
│   ├── make_thumbnail.py
│   ├── srt_generator.py
│   ├── still_to_clip.py
│   └── rulebook.json               — universal rules
├── final-hours/
│   ├── channel.json                — channel config (voice, style, music)
│   ├── rulebook.json               — Final Hours channel rules
│   ├── auth.py / upload.py         — channel-specific YouTube auth + upload
│   ├── client_secret.json / token.json
│   ├── projects/
│   │   ├── pompeii_v2/             — published
│   │   ├── anne_boleyn/            — published
│   │   └── hartley/                — scheduled
│   ├── beat-scripts/
│   │   ├── anne_boleyn_beats.json
│   │   └── hartley_beats.json
│   ├── assets/                     — channel art, banners, finished videos
│   └── docs/
│       ├── strategy.md             — this file
│       └── backlog.md              — what's next
└── success-coach/                  — second channel, see its docs
```

Channel detection is by `channel.json` marker — the pipeline walks upward from the current working directory looking for it. To switch channels, `cd` to the channel folder; no `--channel` flag needed.
