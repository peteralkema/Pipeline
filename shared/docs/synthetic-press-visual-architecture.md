# Synthetic Press — Visual Architecture

*Cross-channel reference document for Synthetic Press.*
*Banked 3 June 2026 from the Mode A / Mode B strategic conversation.*
*Lives at: `shared/docs/synthetic-press-visual-architecture.md`*

---

## 0. Why this document exists

Synthetic Press has to compete with Drew Spartz's Species (362K subs), Coldfusion (4M subs), and the upcoming Hollywood AI films. The competitors set a visual ceiling, and Final Hours' cinematic-recreation-only pipeline cannot reach it.

A Netflix documentary on the OpenAI saga would not be 15 minutes of cinematic recreation. It would interleave recreation with motion-graphics evidence — the leaked email, the SEC filing, the $300B valuation chart, the timeline of the November 2023 weekend. The interleaving is the documentary feel.

This document banks the architecture for that interleaved system: two production modes, a component library to build, the principles for choosing between them, and a 5-day build plan that gets Episode 1 ready for production with Mode B graphics in place.

---

## 1. Two-mode architecture

Synthetic Press videos are composed of two distinct visual modes, interleaved in the final cut.

### Mode A — Dramatic recreation

Cinematic AI-generated stills + Kling motion. Same pipeline as Final Hours. Used for:

- Human moments — what happened in a room between people
- Emotional beats — realization, betrayal, decision, regret
- Atmosphere/period — what 2015 OpenAI HQ felt like, what the November 2023 board call looked like
- Moments where we have testimony but no footage
- Time-collapsing montages

This is the channel's narrative spine. The audience returns here.

### Mode B — Explainer graphics

Code-rendered motion graphics in Remotion. Vox/Dhruv Rathee/Johnny Harris register. Used for:

- Evidence presentation — court filings, leaked emails, SEC documents, group chat screenshots
- Data and numbers — valuations, headcounts, investment amounts, dates
- Geographic/temporal context — maps, timelines, organizational charts
- Document/text reveal — "the letter said this," highlighted at the exact moment
- Tweet/social media artifacts — inherently text-based, screenshot-as-evidence
- Process explanation — how RLHF works, what an org chart looks like before vs after a conversion

This is the channel's texture and credibility. The "we did the homework" layer.

### How the two cut together

Documentary effect comes from MOVEMENT between the modes, not from either mode in isolation. A typical 90-second sequence on the November 2023 board call:

- 0-15s — Mode A: recreated boardroom, dim conference room, phone on the table
- 15-25s — Mode B: timeline animation showing 72 hours of November 17-19
- 25-50s — Mode A: recreated phone calls, Satya Nadella's face in shadow
- 50-65s — Mode B: the board's official statement, highlighted line by line
- 65-90s — Mode A: Mira Murati reading the email on her phone, expression flat

The cuts BETWEEN modes carry the documentary register. Stay too long in either mode and the form collapses — pure Mode A becomes a drama, pure Mode B becomes a Vox explainer. The interleaving IS Synthetic Press.

---

## 2. Decision framework — when to use which mode

For any given beat in a Synthetic Press script, ask:

**Does this moment require a human face, room, or scene to land?** → Mode A.
*Example: "Sam Altman sat at the head of the table" — human, room, atmosphere. Mode A.*

**Is the evidence ITSELF the point?** → Mode B.
*Example: "The board's statement said he had not been 'consistently candid'" — the quote is the artifact. Show the actual statement with the phrase highlighted. Mode B.*

**Is there a number or data point the audience must absorb?** → Mode B.
*Example: "Microsoft had invested $13 billion." Show a count-up from $1B to $13B with the year axis. Mode B.*

**Is this a tweet, email, leaked Slack, or any born-digital artifact?** → Always Mode B.
*Example: "Musk posted on X" — show the tweet card. Never recreate a person typing.*

**Is this geographic, temporal, or organizational context?** → Mode B.
*Example: "OpenAI had 770 employees. By Sunday night, 738 had signed the letter." — bar chart or count-up. Mode B.*

**Is this an interior moment — a thought, a realization, a decision?** → Mode A.
*Example: "Mira Murati read the message. She had been CEO for eleven hours." — emotional interior. Mode A.*

**When in doubt:** Mode A is the default. Synthetic Press is a documentary about HUMANS, not a presentation about evidence. Mode B is the surgical tool used to deliver specific pieces of proof or data. If a beat could go either way, pick Mode A unless there's a specific artifact (document, tweet, chart) that NEEDS to be on screen.

---

## 3. Per-video ratio guidance

Target ratio for a 12-15 minute Synthetic Press video:

- **Mode A: 60-70%** of runtime
- **Mode B: 30-40%** of runtime

This is the inverse of Vox (where graphics dominate and host-face is the texture). Synthetic Press is documentary-first, graphics-second. The Netflix anchor, not the Vox anchor.

Practical numbers for a 12-minute Episode 1:

- ~8 minutes of Mode A across 4-6 recreation scenes
- ~4 minutes of Mode B across 8-12 distinct moments (each 20-40 seconds)

Mode B moments should be MORE FREQUENT but SHORTER than Mode A scenes. A 12-minute video might have 5 long Mode A scenes (~90 seconds each) and 10 short Mode B moments (~25 seconds each). The Mode B sprinkles texture between the recreated drama.

**Anti-pattern: Mode B chunks longer than 60 seconds.** If your script has 90 seconds straight of "and the document says... and then the chart shows... and the tweet from..." — you've written a Vox script, not a Synthetic Press script. Break it up with Mode A return cuts.

**Anti-pattern: Mode A scenes longer than 2 minutes without Mode B return.** Past 2 minutes of pure recreation, the audience forgets they're watching a documentary and starts judging it as a film. The Mode B cuts remind them this is REAL and DOCUMENTED.

---

## 4. Vox / Johnny Harris / Dhruv Rathee craft principles

These are the distilled best practices from watching the explainer-journalism category. They apply to all Mode B work and are non-negotiable for Synthetic Press to compete visually.

### Principle 1 — Highlighter is a verb, synced to narrator

The yellow pen stroke that draws across "world's richest person" must happen at the EXACT moment the narrator says those words. Audio-visual sync is the entire effect. A highlighter that appears before the words are spoken telegraphs the punchline; after, it feels like a missed beat.

Implementation: every `<HighlightedHeadline>` component takes a `narrationSyncMs` prop. The pen-stroke animation starts at that timestamp relative to the clip's narration audio. Test in playback against the actual voiceover.

### Principle 2 — Documents have texture

Vox never shows flat white documents. Real documents have paper grain, slight off-axis rotation (5-7 degrees from vertical), subtle drop shadow underneath, sometimes a coffee stain or fold mark for older docs. Vintage cream paper for pre-2010 documents, white bond paper for modern.

Implementation: maintain a small library of base paper textures in `synthetic-press/assets/paper-textures/`. Components apply them as background layers.

### Principle 3 — Ken Burns is precise, not decorative

When Vox pans across a document, the pan goes FROM a wide shot of the document TO the specific highlighted phrase. The movement is narrative — "look here, then look HERE." Not generic "let me add some motion."

Implementation: `<DocumentReveal>` component takes `startFrame` (bounding box of wide view) and `endFrame` (bounding box of focal phrase). The component eases between them over the narration duration. Pan duration matches the audio.

### Principle 4 — Numbers count up

A $300B valuation chart doesn't appear at $300B. It counts from $0 to $300B in 1.5-2 seconds. Bars grow in. Lines draw. The audience watches the value accumulate, which creates tension and absorption time. Static charts feel cheap.

Implementation: every numeric component animates from 0 (or a previous reference value) to the target. Default duration 1.5s with ease-out curve.

### Principle 5 — One thing at a time

Vox never shows five graphics simultaneously. The screen strips away everything except ONE highlight, ONE document, ONE chart, ONE tweet. White space matters. Crowded frames signal "data dump," not "argument."

Implementation: each Mode B clip features exactly one primary element. Multiple data points become a sequence of clips, not a busy composite.

### Principle 6 — Color discipline (3-4 colors max)

Vox uses red + yellow + white + grey, almost nothing else. Johnny Harris uses red + cream + black. Dhruv Rathee uses yellow + red + white. Each channel commits to a tight palette and the consistency IS the brand.

**Synthetic Press palette (proposal):**
- Primary: deep navy `#0a1628` (background, anchor)
- Accent: amber `#d4a017` (highlights, key data) — echoes the "press" identity, gold-leaf old-news quality
- Neutral: bone white `#f4f1ea` (paper, text)
- Warning: rust red `#8b3a1e` (used sparingly — for the moment of risk, the failure, the verdict)

Lock this palette. Every component uses it. No exceptions.

### Principle 7 — Cuts back to the human anchor

Vox cuts back to the host face every 20-30 seconds. The host is the human anchor — the audience returns to that face. Synthetic Press is faceless, so the equivalent return is Mode A recreation. Every Mode B sequence should cut back to Mode A within 30-45 seconds.

The recreation footage IS the human anchor of this channel.

### Principle 8 — Animations under 2 seconds

Highlight strokes: 0.6-1.0s. Bar reveals: 1.0-1.5s. Document zooms: 1.5-2.5s. Tweet cards entering: 0.4-0.6s. Number count-ups: 1.0-2.0s.

If a Mode B animation runs longer than 2 seconds, it's either too complex or the narration is moving too slowly. Information delivery is the goal; motion is the wrapper.

### Principle 9 — Iconic, not literal

When Vox shows "$13 billion invested by Microsoft," they don't render 13 billion dollar bills. They show the Microsoft logo + a count-up number + an arrow. Symbol over realism. The audience parses symbols faster than literal depictions.

For Synthetic Press: company logos, simple icons (a gavel for the verdict, a phone for the board call, a building for the org), and typography do more work than illustrated scenes.

### Principle 10 — The pause matters

After a key reveal — the highlighted phrase, the final chart value, the tweet that drops — Vox holds 1-2 seconds of stillness. The audience absorbs. Don't cut immediately to the next graphic; that signals "I'm rushing you."

Implementation: every Mode B clip has a `holdMs` prop that adds a post-animation pause before the cut. Default 1500ms.

---

## 5. Component library spec

The 9 components Synthetic Press needs. Phased so Episode 1 ships with the first 6, then Episodes 2-3 add the rest.

### Phase 1 — Build for Episode 1 (5 days)

#### `<HighlightedHeadline>`

**When to use:** Headlines from real newspapers/sites, quoted passages from documents, key sentences in emails. Anywhere the AUDIENCE needs to see the words AND have specific words emphasized.

**When NOT to use:** Long body text (use `<DocumentReveal>` instead). Numbers (use `<DataCounter>`). Generic narration support (just narrate over Mode A footage).

**Props:**
- `headline` — full text of the headline/quote
- `highlight_words` — substring(s) to apply highlighter to
- `date` — optional date stamp
- `source` — optional source attribution (e.g., "The New York Times")
- `narrationSyncMs` — ms offset when highlighter draws (synced to narrator)
- `holdMs` — pause after animation completes
- `paperTexture` — "vintage" | "modern" | "newsprint"

**Vox best practice:** highlighter sweep is 0.6-0.9s, easing out, with a slightly imperfect edge (not pixel-perfect rectangle — looks human-drawn). Sound design: subtle "wet marker" SFX timed to the stroke.

**Common pitfall:** highlighting too many words. If you highlight the whole headline, nothing is emphasized. Pick 2-5 words maximum.

**Typical duration:** 4-6 seconds total (1s read-in + 0.8s highlighter + 1.5s hold + 1-2s outro).

#### `<NewspaperArticle>`

**When to use:** When you need to show the full article context — headline + dateline + body text + optional photo cutout of the subject. The "press evidence" moments. The Elon Musk image you uploaded is the canonical example.

**When NOT to use:** When only the headline matters (use `<HighlightedHeadline>`). When showing a digital-era article (use a stylized webpage screenshot instead).

**Props:**
- `headline` — main headline
- `subhead` — optional sub-headline
- `body_text` — first 1-2 paragraphs of body
- `date_stamp` — formatted date label
- `cutout_subject_url` — optional path to a cutout image (person, with red rough-edge stroke per Vox style)
- `highlight_phrases` — array of phrases to highlight as the narrator says them
- `paperTexture` — defaults to "newsprint"
- `entrance_animation` — "fade" | "slide" | "ken-burns-in"

**Vox best practice:** the cutout subject (e.g., Elon Musk) gets a hand-drawn red outline 4-6px wide, slightly imperfect. The subject sits ON TOP of the newspaper, breaking the rectangle. This is the Johnny Harris signature move.

**Common pitfall:** unreadable body text. Body text exists for VISUAL TEXTURE — it doesn't need to be readable. Use lorem-ipsum-style filler in real newspaper typography unless the body specifically contains a quote you'll highlight.

**Typical duration:** 8-15 seconds depending on how many phrases highlight in sequence.

#### `<DocumentReveal>`

**When to use:** Court filings, SEC documents, contracts, official letters. Long-form documents where the audience needs to feel the DOCUMENT-NESS, then zoom to the specific clause.

**When NOT to use:** Headlines (use `<HighlightedHeadline>`). Tweets (use `<TweetCard>`). Charts (use chart components).

**Props:**
- `document_image_url` — full document image (real or recreated)
- `start_frame` — initial bounding box (usually wide shot of full doc)
- `end_frame` — final bounding box (close on the focal clause)
- `highlight_text_at_endframe` — text inside end_frame to highlight after zoom completes
- `narration_duration` — total duration for the Ken Burns motion
- `paperTexture` — "official-letterhead" | "court-filing" | "memo" | "contract"

**Vox best practice:** the document has a 5-7 degree off-axis rotation. Drop shadow with soft edges. Ken Burns easing curve is "ease-in-out" not linear. Sound design: subtle paper-shuffle SFX at start, faint pen-write SFX when highlight appears.

**Common pitfall:** zooming too fast. The audience needs time to register the document as a document before you take them to the detail. Minimum 2.5s from wide to focused.

**Typical duration:** 6-12 seconds. Long compared to other components because the reveal IS the value.

#### `<DataCounter>`

**When to use:** Any single number that matters. Valuation, employee count, investment amount, casualty count, time elapsed, dollar amount.

**When NOT to use:** Multiple values (use `<AnimatedBarChart>` or `<TimelineEvents>`). Percentages where the comparison matters (use bar chart).

**Props:**
- `start_value` — initial value (often 0 or a reference point like previous year)
- `end_value` — target value
- `unit` — "$" | "%" | "B" (billion) | "M" (million) | "" 
- `label` — descriptor below the number ("OpenAI valuation, March 2026")
- `duration_ms` — count-up duration (default 1500)
- `easing` — "ease-out" (default — fast start, slow finish, lets audience read final value)

**Vox best practice:** the number sits centered, large (60-100pt), in the channel's accent color. Label small (16-20pt) below in neutral color. The count-up uses a monospace or tabular-nums variant so digits don't jiggle. After the count completes, there's a 1-2s hold on the final value.

**Common pitfall:** counting too fast. A $300B count-up in 0.5 seconds doesn't let the audience register the journey. 1.5-2 seconds is the sweet spot.

**Typical duration:** 3-4 seconds total (1.5-2s count + 1.5-2s hold).

#### `<TweetCard>`

**When to use:** Any tweet/X post that's part of the evidence. Musk's tweets, Altman's tweets, public statements made on social media.

**When NOT to use:** Generic narration about what someone said (just narrate over Mode A). LinkedIn posts (build a separate `<LinkedInCard>` if needed).

**Props:**
- `handle` — "@elonmusk"
- `display_name` — "Elon Musk"
- `verified` — boolean (the blue checkmark)
- `avatar_url` — profile pic
- `tweet_text` — full text
- `highlight_phrases` — optional phrases to highlight inside the tweet
- `timestamp` — "Aug 29, 2024 · 11:42 PM"
- `likes` — optional engagement number
- `entrance` — "slide-up" (default) | "fade"

**Vox best practice:** the tweet card is a CARD — has a subtle drop shadow, rounded corners (16px), white background even on dark scenes. It looks like a screenshot, not native UI. This is important: viewers must recognize it as an artifact, not as the channel's UI.

**Common pitfall:** including the like/reply/retweet button row. Vox usually strips it — focuses attention on the text. Only include engagement count if it's narratively relevant.

**Typical duration:** 4-7 seconds.

#### `<ChapterCard>`

**When to use:** Episode opens, act breaks, "chapter" reveals within longer videos. The "Episode One: The Verdict" moment.

**When NOT to use:** Generic transitions (just hard cut). End-card (build a separate `<EndCard>` if needed).

**Props:**
- `chapter_label` — "EPISODE ONE" or "PART TWO"
- `chapter_title` — "THE VERDICT"
- `subtitle` — optional ("Oakland, California — May 18, 2026")
- `background_treatment` — "fade-in" | "ken-burns-still" (uses a Mode A still as backdrop)
- `duration_ms` — default 3500

**Vox best practice:** chapter cards are RESTFUL. They should feel like a breath between sections. Slow fade-in (0.8s), 2s hold, slow fade-out (0.8s). Centered typography. Channel accent color for the label, neutral for the title.

**Common pitfall:** putting too much info on the card. Two lines maximum (label + title), optionally three (+ subtitle). More than that and it's a paragraph, not a chapter break.

**Typical duration:** 3.5-4 seconds.

### Phase 2 — Build during Episodes 2-3 (3 days)

#### `<AnimatedBarChart>`

**When to use:** Comparing 3-8 values across categories. Countries, companies, time periods, departments.

**When NOT to use:** Single value (use `<DataCounter>`). More than 10 values (use a different chart type or break into multiple charts). Time-series (use `<AnimatedLineChart>`).

**Props:**
- `data` — array of `{label, value, color?}`
- `unit` — "$" | "%" | "B" | "M"
- `title` — optional chart title
- `subtitle` — optional context line
- `sort` — "by-value" | "as-given"
- `reveal_sequence` — "all-at-once" | "one-at-a-time" (sequential reveals are more dramatic)
- `duration_per_bar` — default 400ms

**Vox best practice:** bars grow FROM the axis OUT, not appearing wholesale. Value labels at the end of each bar appear AFTER the bar completes. Sequential reveals (one bar at a time, ~400ms each) are dramatically stronger than simultaneous reveals.

**Common pitfall:** using rainbow palettes. Stick to the channel's 3-4 colors. Differentiate bars by VALUE not by color when possible.

**Typical duration:** 5-10 seconds depending on bar count and reveal sequence.

#### `<TimelineEvents>`

**When to use:** Sequences of events in time. The "72 hours of November 2023." The "8-year history of OpenAI." Compressed time across a video.

**When NOT to use:** A single date (use `<HighlightedHeadline>` with a date stamp). A complex tree of events (use a custom diagram).

**Props:**
- `events` — array of `{timestamp, label, description?, mode_a_thumbnail?}`
- `orientation` — "horizontal" | "vertical"
- `reveal_pacing` — "narrator-synced" (each event appears as narrator names it)
- `axis_format` — "hours" | "days" | "months" | "years"

**Vox best practice:** the timeline LINE draws in first (left to right, ~0.8s), then events POP in at their positions sequentially as the narrator mentions them. Each event has a small node circle, a date label, and optionally a brief caption or Mode A thumbnail.

**Common pitfall:** too many events. 4-7 is the sweet spot. More than 8 and the audience loses track. If you need to show 12 events, break it into two timelines.

**Typical duration:** 10-20 seconds.

#### `<EmailReveal>`

**When to use:** Leaked emails, formal correspondence, internal company messages. The artifact IS the email format.

**When NOT to use:** A quote from an email (use `<HighlightedHeadline>` with the quote — simpler). Multiple emails in sequence (consider `<DocumentReveal>` with multi-page).

**Props:**
- `from_name` and `from_email`
- `to_name` and `to_email`
- `subject` — full subject line
- `date` — formatted
- `body_text` — email body
- `highlight_phrases` — phrases to highlight as narrator reads them
- `email_client_style` — "gmail" | "outlook" | "generic" (matches the client's UI)

**Vox best practice:** the email looks like a SCREENSHOT of a real client. Pixel-perfect Gmail or Outlook chrome. The artifact-ness matters — viewers need to register "this is real."

**Common pitfall:** showing fake-looking client UIs. If you're going to render an email, render it in a recognizable client style. Generic "email card" looks staged.

**Typical duration:** 8-15 seconds.

### Phase 3 — Build as needed

- `<AnimatedLineChart>` — for time-series data (stock prices, growth curves)
- `<MapAnnotation>` — for geographic context (where Anthropic spun off, where the lawsuit was filed)
- `<OrgChartAnimation>` — for organizational structure changes (OpenAI before/after for-profit conversion)
- `<StockTicker>` — Microsoft stock during the November 2023 weekend, for example
- `<LogoMorph>` — company logo transitions (OpenAI's logo evolution)
- `<EndCard>` — episode ending with next-episode preview

---

## 6. The 5-day build plan

This is the carve-out for getting the Phase 1 component library production-ready BEFORE Episode 1 ships.

**Prerequisite:** Decide on Remotion as the toolchain. Install Remotion locally, set up a `synthetic-press/motion-graphics/` directory in the Pipeline repo, configure TypeScript + React.

### Day 1 — Foundation + first component

- Remotion project scaffolding in `synthetic-press/motion-graphics/`
- Design system tokens: colors (palette from Section 4 Principle 6), typography (channel fonts), spacing scale, animation easing curves
- Asset folders: `assets/paper-textures/`, `assets/sounds/`, `assets/fonts/`
- Build `<HighlightedHeadline>` end-to-end including: paper texture rendering, headline typography, highlighter pen-stroke animation with imperfect edges, date stamp, source attribution, audio sync mechanism, hold-after-animation
- Render a test clip in isolation and review against the Elon Musk reference image
- Commit and document

**Deliverable end-of-day:** `<HighlightedHeadline>` ships polished. The hardest component is done first because it teaches the design system.

### Day 2 — Document family

- Build `<NewspaperArticle>` reusing the paper texture system from Day 1. Add cutout subject support with red rough-edge outline (Johnny Harris signature). Support multi-phrase highlights.
- Build `<DocumentReveal>` with Ken Burns easing. Shared Ken Burns utility function for use across components.
- Render test clips for both. Cross-check against Vox/Johnny Harris references.

**Deliverable end-of-day:** all document-family components ship. The paper texture system is robust enough to handle different document types.

### Day 3 — Numbers and tweets

- Build `<DataCounter>` with monospace digit support, count-up easing, label rendering, accent-color theming
- Build `<TweetCard>` with profile circle, verified badge, timestamp formatting, optional highlights inside tweet body, card drop shadow
- Render test clips

**Deliverable end-of-day:** the numerical and social-artifact components ship. Episode 1 has 5 of the 6 needed components.

### Day 4 — Chapter cards + integration glue

- Build `<ChapterCard>` with restful fade-in/hold/fade-out, optional Ken Burns background using Mode A stills
- Build the integration layer: a Remotion render command that takes a `beats.json` entry with `mode: "explainer"` and renders the named component with the provided props to an MP4 clip with embedded audio
- Test the pipeline: hand-crafted beats.json with 3 Mode B beats, render all 3 clips, manually composite with Mode A clips, validate the cut

**Deliverable end-of-day:** all Phase 1 components ship. The render command exists. Manual composition validates the architecture works.

### Day 5 — Pipeline integration + polish

- Extend `recreation_pipeline.py` to route beats with `mode: "explainer"` to the Remotion renderer instead of Flux+Kling. Route `mode: "recreation"` (default) to the existing pipeline. The `finish` step composites both clip types in beat order.
- Document the component library: how to use each component, when to use each, prop reference, examples. Ship as `synthetic-press/motion-graphics/README.md`.
- Build one "kitchen sink" demo composition that exercises all 6 components. Render it. Watch it. Iterate.

**Deliverable end-of-day:** the full Phase 1 library is production-ready. Episode 1 can begin script writing with FULL knowledge that the Mode B components exist and work.

---

## 7. Pipeline integration architecture

The existing pipeline (recreation_pipeline.py) produces Mode A clips: Flux still → Kling motion → MP4. The Remotion pipeline produces Mode B clips: component + props + audio → MP4. Both must integrate into the same finish step.

### Extended beats.json schema

The existing schema supports recreation only. Extend it to support both modes:

```json
{
  "canon": { ... },
  "beats": [
    {
      "index": 1,
      "mode": "recreation",
      "narration": "It is May 18, 2026...",
      "image_prompt": "..."
    },
    {
      "index": 2,
      "mode": "explainer",
      "narration": "The verdict came down at 11:47 in the morning.",
      "component": "HighlightedHeadline",
      "props": {
        "headline": "OpenAI Loses Landmark Case Over Nonprofit Conversion",
        "highlight_words": "Loses Landmark Case",
        "date": "May 18, 2026",
        "source": "The Wall Street Journal",
        "narrationSyncMs": 1200,
        "holdMs": 1500,
        "paperTexture": "newsprint"
      }
    },
    {
      "index": 3,
      "mode": "recreation",
      "narration": "In Oakland, in the federal courthouse...",
      "image_prompt": "..."
    }
  ]
}
```

The `mode` field defaults to `"recreation"` if absent (backwards compatibility with Final Hours beats.json).

### Routing logic in recreation_pipeline.py

The `stills` command should:

- For `mode: "recreation"`: run existing Flux + Kling pipeline
- For `mode: "explainer"`: skip image generation entirely — these clips render later in finish

The `finish` command should:

- For each beat in order:
  - If `mode: "recreation"`: load the existing clip from `clips/shot_NNN.mp4`
  - If `mode: "explainer"`: invoke Remotion to render `clips/shot_NNN.mp4` from the component spec + voiceover slice
- Concatenate all clips in beat order
- Mix with music + voiceover
- Output final_video.mp4

### Remotion render invocation

A small Python wrapper around Remotion's CLI:

```python
def render_explainer_clip(beat: dict, voiceover_path: Path, output_path: Path):
    spec = {
        "component": beat["component"],
        "props": beat["props"],
        "audio": str(voiceover_path),
        "duration_ms": beat.get("duration_ms")  # if known, else inferred from audio
    }
    subprocess.run([
        "npx", "remotion", "render",
        "src/index.tsx",
        "ExplainerClip",
        str(output_path),
        "--props", json.dumps(spec)
    ], check=True)
```

The Remotion side has a single `<ExplainerClip>` composition that switches on `props.component` to render the right component with `props.props`.

---

## 8. Episode 1 worked example — OpenAI Verdict mode allocation

To validate the architecture, here's a tentative beat breakdown for Episode 1 showing mode allocation:

| Beat | Mode | Description | Duration |
|---|---|---|---|
| Cold open: courtroom recreation, judge entering | A | recreated Oakland federal court | 25s |
| Verdict document reveal — the ruling | B | DocumentReveal with focal phrase | 12s |
| Recreation: Altman watching from California | A | recreated home office, phone | 20s |
| Tweet reaction: Musk's "told you so" post | B | TweetCard | 6s |
| Recreation: 2015 founding meeting at Rosewood | A | recreated dinner | 45s |
| Tegmark FLI letter — the founding seed | B | HighlightedHeadline of the letter | 8s |
| Recreation: OpenAI early offices | A | recreated 2016 founding office | 30s |
| Microsoft investment count-up | B | DataCounter: $1B → $13B | 4s |
| Recreation: 2019 for-profit conversion announcement | A | recreated press conference | 35s |
| Org chart before/after | B | OrgChartAnimation (Phase 3, fallback to two DocumentReveals) | 10s |
| Recreation: November 2023 board call | A | recreated dim boardroom | 60s |
| Timeline: 72 hours of Nov 17-19 | B | TimelineEvents | 18s |
| Recreation: Murati's appointment as interim CEO | A | recreated office moment | 25s |
| The board's statement | B | HighlightedHeadline of the "not consistently candid" line | 7s |
| Recreation: Microsoft offering Altman a job | A | recreated phone call | 30s |
| Recreation: 738 employees sign the letter | A | recreated open-floor offices | 35s |
| Employee count chart | B | AnimatedBarChart (Phase 2 — for Episode 1 fall back to DataCounter showing 738/770) | 8s |
| Recreation: Altman's return | A | recreated press moment | 30s |
| Recreation: 2024 conversion preparation | A | recreated legal meeting | 35s |
| Recreation: 2026 verdict moment, back to courtroom | A | callback to cold open | 30s |
| Final document reveal — the ruling's key clause | B | DocumentReveal | 12s |
| Chapter card — END OF PART ONE — next: Lieutenant | B | ChapterCard | 4s |

**Mode A totals:** ~7:25 (about 62%)
**Mode B totals:** ~1:29 (about 12%) — actually low, will likely add more graphics moments in script v2
**Total:** ~12:00 (acceptable for Episode 1)

The Mode B share is below the target 30-40% in this first pass. In script refinement, look for places to break long Mode A scenes with Mode B inserts (a timeline reminder, a data point, a tweet). The script should be written WITH the component library in mind, not against it.

---

## 9. What to outsource vs build

Given the 5-day investment, the build covers the COMPONENT INFRASTRUCTURE that compounds across every future Synthetic Press video. What's still potentially worth outsourcing per-video:

**Outsource per-video to a motion designer:**
- Custom illustrations (e.g., if Episode 3 needs a specific diagram of how RLHF works that doesn't fit any component)
- One-off animated sequences that are too unique to componentize (e.g., a stylized recreation of a specific Twitter feed scroll)
- High-detail document recreations where pixel-accuracy matters (e.g., a real court filing recreated faithfully)

**Build in-house using the component library:**
- Everything else (~85% of Mode B work)

The library is the LEVERAGE. Each component built once renders infinite times. The motion designer becomes a SPECIALIST you call for the 15% that the library doesn't cover.

---

## 10. Inclusion in Episode 1 — non-negotiable

Episode 1 of Synthetic Press ships WITH the Phase 1 component library used throughout. No "we'll add motion graphics later." The library exists by Day 5. Episode 1 script writing begins Day 6 with full knowledge of what Mode B can do.

Reasoning: Synthetic Press has no audience yet. Episode 1 is the channel's positioning statement. If Episode 1 ships without the Vox-quality Mode B layer, the channel reads as "another Final Hours but about AI" — which it isn't. Synthetic Press needs to read as "Netflix documentary, AI-drama, cinematic + journalistic" from the first frame. The Mode B layer is non-negotiable for that positioning.

---

## 11. What this document does NOT cover (yet)

- Detailed Remotion code patterns and component implementation
- The specific Synthetic Press fonts (still to be chosen — proposal: a serif for the wordmark + a clean sans for graphics + a tabular-nums monospace for numbers)
- Sound design library for Mode B (paper shuffle, marker stroke, button click, etc.)
- The thumbnail-as-Mode-B principle for channel branding consistency
- A/B testing whether Synthetic Press videos that use MORE Mode B outperform those with LESS

These are Phase 2 documentation items, banked for future expansion.

---

## 12. Decision log

- **3 June 2026** — Document banked. Mode A/B architecture established. Remotion chosen as Mode B toolchain. 5-day build plan locked. Episode 1 will ship with Phase 1 components in place.
- **TBD** — Day 1 of the 5-day build. Set a calendar date and protect it.
- **TBD** — Episode 1 production begin date. Should be Day 6 of the build calendar.
