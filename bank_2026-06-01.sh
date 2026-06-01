#!/usr/bin/env bash
# bank_2026-06-01.sh — Consolidated banking of today's strategic and operational findings.
#
# Run from the Pipeline directory root (the one that contains final-hours/, success-coach/, shared/).
# Verify location first:
#   pwd should end with "03. Pipeline"
#   ls -d final-hours success-coach shared should show all three
#
# What this writes:
#   APPENDS to shared/docs/PIPELINE_PLAYBOOK.md  — operational updates dated 1 June 2026
#   APPENDS to shared/docs/script-craft-principles.md  — Principles 8, 9, 10 from Arthur Revives analysis
#   APPENDS to shared/docs/competitive-analysis.md  — 1 June 2026 update section
#   CREATES shared/docs/arthur-revives-script-craft-analysis.md  — comparative case study
#   CREATES shared/docs/channel-4-hypothesis.md  — strategic frame
#   CREATES shared/docs/lazarus-films-curriculum.md  — apprenticeship + brutal filter + taglines

set -e

if [ ! -d "shared/docs" ]; then
    echo "ERROR: shared/docs/ not found from this directory. Run from Pipeline root." >&2
    exit 1
fi

echo "Banking 1 June 2026 findings into shared/docs/..."

# ===========================================================================
# 1. APPEND to PIPELINE_PLAYBOOK.md
# ===========================================================================

cat >> shared/docs/PIPELINE_PLAYBOOK.md << 'PLAYBOOK_EOF'

---

## PART 7 — UPDATES (1 June 2026)

Operational lessons banked after shipping Mary Celeste (Final Hours video 6, 15:54 runtime, 168 shots).

### Whisper-based frame-accurate sync — built and baked in

Built `shared/align_with_whisper.py` to measure per-shot audio duration from Whisper word-level timestamps. Patched `assemble()` in `shared/recreation_pipeline.py` to read `audio_duration` per-shot from storyboard.json when present, with three-tier priority: Whisper-measured → word-count proxy → uniform fallback.

Auto-Whisper hook injected into `assemble()` — runs Whisper + alignment automatically when storyboard lacks `audio_duration` on every shot. Idempotent. Graceful fallback if whisper not installed. Adds 3-5 min to first render, then cached.

**True-up principle — every render ends with Whisper true-up before publish.** Not optional, not debug-only — standard. The three commands:

```
whisper projects/NAME/voiceover.mp3 --model small --output_format json --output_dir projects/NAME/ --word_timestamps True
python ../shared/align_with_whisper.py --project NAME --verbose
python -u ../shared/recreation_pipeline.py finish --project NAME --no-music --assemble-only
```

When to run:
- After every finish that regenerated voiceover.mp3
- After any correction round that touched clips or stills
- As final QA before publishing — even if nothing seems wrong
- ALWAYS for Lazarus dramatic content (dialogue scenes require frame-accurate sync)
- Optionally for Final Hours documentary content (0.5s drift tolerable but not preferred)

What's normal: the assembler trades small per-shot pacing for zero global drift. Narration micro-stretches or micro-compresses within individual shots. Correct behaviour — do not "fix" it.

**Spell-breaker register principle.** Documentary tolerates near-accurate sync because viewers attribute small gaps to documentary pacing. Drama collapses on any sync gap because audiences decode emotion from voice+visual simultaneously. Lazarus protocol: full true-up + end-to-end script-in-hand listen + zero drift accepted.

### Storyboard discipline auditor — built

Built `shared/audit_storyboard_discipline.py` as Step 7.5 in the pipeline. Detects face-resolution violations via keyword+regex (face/faces/expression keywords/eyes), uses Claude Sonnet 4.6 to rewrite while preserving framing/location/period/atmosphere. Outputs `storyboard_audited.json`. Supports `--dry-run`, `--verbose`. Costs ~$0.39 per video. Mary Celeste audit: 77/168 shots rewritten. False positives occur on "stern" of ship, body posture "lean", "face turned away" — needs cleanup pass.

### proj_paths convention — patched

`recreation_pipeline.py` (line 765) and `upload.py` (line 323) both now auto-prepend `projects/` when given a bare project name. Backward compatible. Future pipeline scripts must inherit the same convention.

### Clip filename convention — `shot_NNN.mp4` not `clip_NNN.mp4`

Animation outputs land as `shot_NNN.mp4`. Corrections scripts must reference this filename pattern. Was the source of Mary Celeste round-3/4/5 corrections silently deleting nothing because they referenced `clip_NNN.mp4` which never existed.

### Voiceover regeneration discovery

The `finish` step regenerates voiceover.mp3 every run unless explicitly told not to. This stales any prior Whisper alignment. Phase 2 fix: detect existing voiceover.mp3 and skip Inworld call (saves cost AND preserves alignment). Until then, always re-run Whisper true-up after any finish.

### SRT generator timing

upload.py generates subtitles.srt from storyboard's even-spacing timing, not the Whisper-measured audio_duration. SRT timestamps are wrong even when video sync is correct. Workaround until Phase 2 fix: skip SRT upload, let YouTube auto-caption.

### Animation step skip-existing bug

`cmd_finish` reports "[NNN/168] already done, skipping" even when the clip file doesn't exist. Source of wasted Mary Celeste round-4 finish run. Phase 2 fix: verify file actually exists on disk before skipping.

### Foreign-language pronunciation hints

Inworld respects phonetic spellings in brackets. For Latin, French, Cornish place names, or any foreign proper noun, write `"Dei Gratia [DAY-ee GRAH-tsee-ah]"` to lock pronunciation deterministically. Avoids TTS lottery on terms that signal dignified-documentary register correctness.

### Named-narrator companion register

Five registers now distinguished in the AI-recreation lane:
1. Third-person reverent, no host (Final Hours current state)
2. Second-person coaching, you ARE the host (Success Coach)
3. Second-person documentary, "you are there" (History Vault Retold)
4. First-person on-camera protagonist (Chloe, Emma, Mira)
5. Named-narrator companion, voice IS the host (Arthur Revives the Past — 48.8K subs, 4.36M views in 4 months)

For Final Hours: name the narrator. Open every video around 0:15-0:20 (AFTER the cold open, never before) with: "I'm [name]. This is Final Hours. Walk with me through what happened next." Preserves the spell-breaker discipline. Adds the parasocial warmth layer the current third-person-reverent register lacks.

Name shortlist: Edmund or Walter (period-British scholarly), Daniel or James (period-neutral dignified). Final selection deferred until first script using the pattern (likely Eyam — see channel-4-hypothesis.md and arthur-revives-script-craft-analysis.md for context).

### Phase 2 pipeline backlog (additions from today)

- Skip-existing logic in stills command (3 lines, line ~926 in recreation_pipeline.py)
- fal retry-on-error with exponential backoff (line ~409)
- `--start-shot N` argument for stills command
- Centralise Claude model IDs in shared/models.json
- Inworld speed parameter for Attenborough-pace pivot (currently 155 wpm vs 120-130 wpm target)
- Discipline auditor false-positive cleanup (stern of ship, body posture lean, face-turned-away)
- Pipeline writes log file by default
- SRT generator rewrite using Whisper word-level timestamps
- Pipeline files reorganisation: move auth.py + upload.py to `shared/`
- Voiceover regeneration skip-existing logic in finish step
- Animation step skip-existing bug: verify file exists on disk before skipping

PLAYBOOK_EOF

echo "  ✓ Appended Part 7 (1 June 2026 updates) to PIPELINE_PLAYBOOK.md"

# ===========================================================================
# 2. APPEND to script-craft-principles.md
# ===========================================================================

cat >> shared/docs/script-craft-principles.md << 'CRAFT_EOF'

---

## Three additional principles from Arthur Revives the Past (1 June 2026)

Studied today: Arthur Revives the Past (48.8K subs, 4 months old, 4.36M total views, 218K average per video). Closer direct analogue to Final Hours than Chloe vs History was — same lane, same tools, same dignified faceless register, single narrator, 18-28 minute runtimes.

The critical isolation: same channel, same operator, same tools, same format, same author voice produces 632K views as tour-guide ("Pompeii: Before the Disaster") and 1.1M views with dramatic-arc craft ("London 1300: The Apocalypse Happened in 1348"). ~470K view delta. Cleaner isolation of script craft than the Chloe Plummer Titanic A/B (which had thumbnail and runtime confounds).

The three principles below are what separates the 1.1M-view London 1300 from the 632K-view Pompeii. They are also what separates the Chloe-tier 2.1M Titanic from the 1.1K flop. They are not optional. They are the moat.

---

## Principle 8 — Announce the dramatic arc in the first minute

The lesson. Arthur's 1.1M London 1300 opens not with "today we visit London" but with: "London. The year is 1300, and the city stands at its medieval peak. With 100,000 souls packed within its walls, London is three times larger than any other English city. Old St. Paul's Cathedral towers almost 500 ft into the sky, taller than anything Britain would build for another 400 years. Merchant ships from Venice, Florence, and the Hanseatic League crowd the Thames. This is England's crown jewel, the beating heart of a kingdom. **But in the next 50 years, two catastrophes would bring this mighty city to its knees. First, the Great Famine of 1315, 3 years of relentless rain that turned fields into swamps and grain into rot. Then, in 1348, something far worse...**"

The script-craft moves visible here:
1. Date locked first (1300 anchors the time before anything else)
2. Scale established with concrete numbers (100K souls, 3× larger, 500ft, 400 years, Venice/Florence/Hanseatic ships)
3. Dramatic promise announced explicitly ("two catastrophes would bring this mighty city to its knees")
4. Second catastrophe teased without naming it ("something far worse...") — curiosity gap inside the hook

The 632K Pompeii version does none of these. It opens as tour guide. "Welcome back. I'm Arthur. Today we step into ancient Pompei. Walk with me through the past. By the autumn of 79 AD, Pompei had become one of the most prosperous cities in the Roman Empire..." Tour-guide register. No dramatic arc promised. The eruption sits in the background as historical fact rather than dramatic destination.

Application to Final Hours. The current cold-open principle (Principle 1) hits the date-person-money beats but does not always announce the dramatic arc. Mary Celeste does — "There is one person the story almost always leaves out" promises the Arthur Stanley Briggs reveal. Pudding Lane does it weakly. Hindenburg does it via the title rather than the opening line.

Going forward, every Final Hours script announces its dramatic arc in the first minute. Format: [date/place locked first] + [scale set with concrete numbers] + [stakes promise explicit] + [optional teaser of the worst still to come]. For Eyam (the recommended next video): "Derbyshire. October 1665. A travelling cloth merchant arrives in the village of Eyam carrying flea-infested fabric from London. Within fourteen months, two-thirds of the village will be dead. They will choose this. This is why."

---

## Principle 9 — Act transitions with narrator-to-viewer irony

The lesson. Arthur's 1.1M London 1300 uses a specific structural move at the boundary between Act 2 (Great Famine) and Act 3 (Black Death). After describing the famine's resolution: "London had survived, weakened, traumatized, but alive. **It had no idea what was coming next.**"

That last sentence breaks the diegesis. The narrator briefly steps outside the historical frame to acknowledge what the viewer knows that the historical characters do not. Dramatic irony as transition device.

Why it works. The audience has been told (in the opening) that two catastrophes are coming. Act 2 closes with the first one resolved. The narrator's direct address ("it had no idea") activates the viewer's anticipation of the second catastrophe — the famine wasn't the worst; the worst is about to come. The viewer pays attention through the act break because they're now waiting for the shoe to drop. Without this transition, the famine's resolution would feel like the video's natural endpoint and retention would crater.

Application to Final Hours. The current craft principles do not name this move. Mary Celeste partially deploys it ("She handed him her last letter. She thought she was being practical") but the irony stays inside the diegesis rather than addressing the viewer directly. Hindenburg has no equivalent transition.

Going forward, every Final Hours script uses at least one narrator-to-viewer direct address at an act break. The narrator briefly steps outside the diegesis to acknowledge what the viewer knows that the historical characters do not. For Eyam: after the village seals itself off in act 2, the narrator transition: "They thought the worst was behind them. The worst was just beginning."

---

## Principle 10 — Moralised closer that reflects back at the present-day viewer

The lesson. Arthur's 1.1M London 1300 ends with: "We've learned from their mistakes. We don't dump sewage in our drinking water. We understand disease transmission. We have grain reserves and insurance systems. But the fundamental challenge, concentrating millions of people in one place and keeping them fed, healthy, safe, that's still London's legacy. They built the first truly urban society in English history, then watched it nearly die, then rebuilt it stronger. We're still living in the world they created, a world where cities dominate, where commerce trumps status, where catastrophe leads to reinvention instead of collapse. London proved it first through famine, plague, and death. **Cities survive.**"

The 632K Pompeii version ends with: "Thanks so much for watching. Let me know in the comments what city or scene you'd like to see next, and feel free to share any constructive feedback. Until next time."

The difference is structural, not stylistic. The 1.1M ending reflects the historical event back at the present-day viewer. The viewer leaves the video holding something they didn't have at the start — a moral question about their own world. The 632K ending lets the viewer leave with nothing. They came, they saw Pompeii, they bounce out.

History Vault Retold uses the same move at the end of their 320K Pompeii: "They had hours to escape. They had warning signs for days, and thousands stayed anyway. Some prioritized property over survival. Everyone assumed it would pass. They thought this couldn't happen to them. Well, they were wrong." Mirror held up to the viewer.

Chloe vs History's 2.1M Titanic uses it implicitly: "I don't have the words to describe what I saw today. It's one thing reading about it, but it's another thing actually living it." The viewer is invited to feel the gap between knowing and experiencing.

Application to Final Hours. This is the principle Final Hours most commonly misses. Mary Celeste's closer ("...and the ocean took him too") is dramatic but stays inside the diegesis. Pudding Lane's closer is restrained but doesn't reflect. Hindenburg ends with Matilde on the grass — image, not reflection. Principle 7 (end with the image, not the explanation) is right for some videos but does not preclude the moralised closer that *follows* the image moment.

Going forward, every Final Hours script ends with the historical event reflected back at the present-day viewer. Not "until next time." Not "thanks for watching." The disaster gets moral weight in the modern world. The viewer is left holding something they didn't have at the start.

For Eyam, the closer almost writes itself: "They could have run. Most people in 1665 did. Eyam stayed. Two hundred and sixty of them died so that the surrounding villages would live. We do not know if any of them, in their last hours, thought it had been worth it. We do know what they chose. The choice is the inheritance."

---

## The ten principles, distilled (1 June 2026)

The original seven from Chloe vs History:

1. Cold-open with three concrete facts in ten seconds. Date, person, money. No build-up.
2. Acknowledge the AI-recreation craft once, early, in a single line.
3. Give sensation, not description. The narration earns its keep by being the senses the image lacks.
4. Clock-anchor the dread. Specific times before specific events. The clock becomes a character.
5. Name the surrounding humans. The protagonist is one person among many specific people, all of whom matter.
6. Let emotional beats land in silence. At least two beats per video with no narration.
7. End with the image, not the explanation.

The three from Arthur Revives the Past:

8. Announce the dramatic arc in the first minute.
9. Use narrator-to-viewer irony at act transitions.
10. Close with moralised reflection back at the present-day viewer.

Principles 7 and 10 are not contradictory. The image lands first; the reflection follows.

CRAFT_EOF

echo "  ✓ Appended Principles 8-10 to script-craft-principles.md"

# ===========================================================================
# 3. APPEND to competitive-analysis.md
# ===========================================================================

cat >> shared/docs/competitive-analysis.md << 'COMPETE_EOF'

---

## PART 6 — UPDATES (1 June 2026)

After Mary Celeste ship-prep, deep-dive on the AI-cinematic-recreation lane uncovered seven new operator observations and two metric corrections to the 30 May analysis.

### Metric corrections

**Chloe vs History is 71% Shorts, 29% long-form** (12.1M Shorts views vs 4.97M long-form views, total 17M). The original 30 May framing of her as a pure long-form viral operator was incomplete. Her 491K average-per-video number rolls Shorts and long-form together. Her 2.1M Titanic (i4O5KNnKvBE) IS a real long-form hit but it's an outlier even within her own channel. Channel-level distribution architecture relies heavily on Shorts traffic.

**CHRONVEIL is 95.17% Shorts, 4.83% long-form.** NexLev's similar-channels widget rolled it up as "278K avg views per video" — that metric pooled Shorts and long-form into a single average and produced a misleading headline. CHRONVEIL is not a long-form competitor at all. Competing for For You Page algorithm, not suggested-video algorithm. The Shorts virality skills do not transfer to long-form retention.

**Strategic implication of both corrections:** Long-form viral-tier competition in this lane is THINNER than the rolled-up data suggested. The capability moat for high-craft long-form (Final Hours, Channel 4 when launched, Lazarus when launched) is wider than the May 30 analysis indicated.

### New operator data — high-relevance

**Original Emma (secular Pompeii channel)** — referenced in transcript: rWZradNzivE Pompeii video at 9.5K views. Confirmed fully AI synthetic character via Gemini visual analysis (skin smoothness, hand-clipping artifacts, lip-sync failures at emotional peaks). Production stack inferred: SDXL or Flux backend, InstantID/PuLID face cloning, HeyGen-class lip-sync, Topaz upscaling. Operates closest to "literary short film" register — scripted character (Alaria, Lucia, Marcus), explicit promise, tragic-or-rescue dramatic structure. Confirms first-person on-camera protagonist register is accessible to solo or small-team operators with 18-24 months of pipeline R&D.

**Esme Time Travels (UCnpfQoMoNfMWUiXsu3le0ow)** — 20.4K subs, joined March 27 2026 (~65 days old at time of analysis), 101 videos in 60 days (1.5+ videos/day). 799K total views, 7,917 average per video. Distribution: 25.59% Shorts, 74.41% long-form (Esme IS a long-form operator). Three videos at 100K+ (Blitz 126K @ 15.9x outlier, Black Death 123K @ 15.5x, Salem 87K @ 11x). 15x outlier score means individual hits run 15x above her own channel baseline.

The Esme business model matters. Custom domain (esmetimetravels.com), Buy Me A Coffee, sells a "How To Ebook," Channel Memberships enabled. She isn't competing for ad revenue alone — she's monetising the operation across three revenue streams (ad revenue + memberships + ebook). The 1.5 videos/day cadence is a *lottery model*: most videos plateau, occasional ones go viral, the ebook captures viewers who want to do what she does. This is the operator type Leo coaches toward in his "copy-paste viral scripts" framework. It works for Esme specifically because she pairs format-throughput with playbook-as-product monetisation. It does NOT work as a craft-tier strategy.

**Mira Was There** — 1.62K subs, 4 videos in 3 weeks. Sequence: Pompeii 15K (1.2x outlier) → Black Death 22K (1.8x) → Titanic 9K (0.7x) → Troy 2.5K (0.2x). Declining VPH and declining outlier multipliers indicate audience burnout. Voice register: Gen-Z TikTok crossing into long-form, vocal-fry filler, slang-heavy. Script structure: tutorial-vlog with disaster appendix, no character arc, no failure-to-warn discipline. **The failure mode of format-without-craft.** Mira copied Emma's surface format (selfie thumbnail, time-travel-vlog framing, disaster topics, ~8 minute runtime) but missed the dramatic architecture. Two weeks of viewer trust burned in four videos.

**Biblical Emma (Noah's Ark channel)** — 306 subs, 6 videos in 13 days. Noah's Ark video: 3.9K views, 3.8x outlier in 13 days. Different audience than secular Emma (evangelical/apologetic verticals). Script: Genesis 7:16 quoted 3 times, Korean naval engineering paper cited, Titanic-tonnage comparison. **Confirms format is a delivery vehicle that adapts to verticals, not a single market.** Faith audiences. Disaster audiences. Military audiences. Maritime audiences. Each is a distinct vertical with distinct competitive density.

**History Vault Retold** — 1.16K subs, 5 videos in ~2 months. Pompeii at 320K views, 219 VPH, 5x outlier. Register: faceless, second-person ("You're buying fish at the market. Yet, you have just 3 hours to live"). Dignified-documentary cinematography, classical music, restrained narrator. Moralised closer: "They had hours to escape. They had warning signs for days, and thousands stayed anyway. Some prioritized property over survival. Everyone assumed it would pass. They thought this couldn't happen to them. Well, they were wrong." This is a third viable register in the lane — between first-person protagonist (Chloe/Emma) and Final Hours' current third-person reverent.

**Woodstock channel** — 45 views in 3 weeks. Format-perfect thumbnail (close-up, crying, hippie costume, yellow text, "I cried"). 57-second runtime. Topic-format mismatch: Woodstock is a positive event with no threat-promise to resolve. Performance-of-emotion (full open-mouth tears) rather than embodied threat-detection (Chloe's wide-eyed alarm). **What happens when Leo's "copy-paste viral scripts" framework is applied without craft-taste filtering.** Surface-perfect thumbnail + wrong topic + no script craft = 0x outlier. Bring this to Thursday's noon call as a concrete example.

### Five registers now distinguished in the lane

The 30 May analysis identified Final Hours as third-person reverent and Chloe vs History as first-person protagonist. Today's deeper read identified three more:

1. **Third-person reverent, no host** — Final Hours current state. Dignified distance. Reverent of the dead. No parasocial warmth mechanism.
2. **Second-person coaching, you ARE the host** — Success Coach. The viewer is being taught. The relationship is the product.
3. **Second-person documentary, "you are there"** — History Vault Retold. The viewer IS the protagonist. Parasocial implication.
4. **First-person on-camera protagonist** — Chloe, Emma, Mira. Named character with face/body presence.
5. **Named-narrator companion, voice IS the host** — Arthur Revives the Past. Faceless first-person. The narrator is named (Arthur), has a recognisable voice and personality, addresses the viewer as companion. The channel handle IS the narrator's name. Solves the parasocial-warmth problem without an on-camera face.

Arthur's register is the most underused in the lane and the most directly accessible to Final Hours' current capability stack. Final Hours could adopt it without changing anything about its production pipeline. Just name the narrator. See PIPELINE_PLAYBOOK Part 7 for implementation pattern.

### The honest hypothesis update

The 30 May analysis closed with "you are not betting on a hypothetical" — the lane is hot, the path is being walked, the cost of admission is the flat period. That holds. The 1 June refinement adds two layers:

**Format-chasing is the wrong strategic move.** Six months of operator data now shows format-replicators outnumber format-succeeders by roughly 10:1. The channels that succeed do so on dramatic script craft — character introduction, stakes establishment, failure-to-warn structure, restrained closer — that is orthogonal to surface format. See arthur-revives-script-craft-analysis.md for the Pompeii-vs-London-1300 isolation that empirically validates this.

**The durable position is adjacent to the format with capability advantages competitors cannot match within the format's window.** This is the framing for Channel 4 specifically (see channel-4-hypothesis.md) but the principle applies across Final Hours' positioning decisions too. Don't compete on what everyone can copy. Compete on what the Lazarus apprenticeship (see lazarus-films-curriculum.md) is building over the next 18 months.

COMPETE_EOF

echo "  ✓ Appended Part 6 (1 June 2026 updates) to competitive-analysis.md"

# ===========================================================================
# 4. CREATE arthur-revives-script-craft-analysis.md
# ===========================================================================

cat > shared/docs/arthur-revives-script-craft-analysis.md << 'ARTHUR_EOF'
# Script-Craft Analysis — Arthur Revives the Past
*The closest direct analogue to Final Hours found in any NexLev research.*
*Drafted 1 June 2026 from comparative analysis of two of his videos.*

## The Find

**Arthur Revives the Past** (@ArthurRevivesthePast, UCJC35B558iY_ljm6RwRlkcg)

- 48.8K subscribers
- 20 videos
- Joined January 19, 2026 (~4 months active)
- **4.36M total views, 218K average per video**
- Newsletter + Instagram + Website (full operator stack)

Channel mission, quoted: *"History isn't dead, it's just waiting to be told... combining deep historical research with cutting-edge Artificial Intelligence, I recreate faces, landscapes, and legendary moments with stunning realism."*

Same lane, same tools, same dignified faceless register, similar runtime, same single-narrator format as Final Hours. Started four months before Final Hours and now at 48.8K subscribers, 4.36M total views. The operator profile maps almost exactly onto what Final Hours is trying to become.

## The Title Formula

**[Place + optional year]: [evocative subordinate clause about destruction/loss] (AI Reconstruction)**

Top performers across his 18 published videos:

| Title | Views |
|---|---|
| London 1300: The Apocalypse Happened in 1348 | 1.1M |
| What IRAN Looked Like 2,500 Years Ago Before It Burned | 713K |
| Pompeii: Before the Disaster | 632K |
| What Rome Looked Like at the Height of the Roman Empire | 500K |
| What Ancient Alexandria ACTUALLY Looked Like | 356K |
| Knossos 1700 BC: Europe's First Civilization | 228K |
| What Jerusalem Actually Looked Like Before Rome Destroyed It | 180K |
| What Carthage ACTUALLY Looked Like Before Rome Burned It | 154K |
| What Constantinople ACTUALLY Looked Like Before the Sun Went Dark | 112K |
| Walking through Athens 2,500 years ago | 67K |

The semantic engine in every title: **show what was lost, before it was lost**. The viewer already knows the destruction is coming — that knowledge is the dramatic engine that holds them through the recreation. Pompeii is going to be buried. London is going to be plagued. Carthage is going to be burned. The viewer signs up to watch the doomed past.

Same structural move Final Hours makes ("December 1872. A merchant ship is found drifting") but applied at city scale rather than at single-vessel scale.

## The Critical Cross-Check — Pompeii (632K) vs London 1300 (1.1M)

Same channel. Same operator. Same production tools. Same format. Same author voice. Both 18-24 minutes long. Both opened by "I'm Arthur, join me..."

**~470K view delta between them.** This is the cleanest possible isolation of script craft as the variable. Cleaner than the Chloe vs History Titanic A/B (which had thumbnail and runtime confounds). Here, both videos use the same thumbnail format and similar runtimes. Only the script structure varies.

### What the 632K Pompeii video does

**Opening — tour-guide register:**
> "Welcome back. I'm Arthur. Today we step into ancient Pompei. Walk with me through the past. By the autumn of 79 AD, Pompei had become one of the most prosperous cities in the Roman Empire, a thriving commercial hub with a population approaching 15,000 people... In this video, I use modern AI tools to bring historic paintings and archaeological reconstructions to life."

Friendly host setup. Transparency about AI tools (defensive register — explaining the method). No explicit promise of dramatic arc. The viewer is being invited on a walking tour, not put on watch for a coming catastrophe.

**Middle — architectural inventory.** The Pompeii script proceeds as a sequenced walking tour of buildings — basilica, temples, baths, forum, theater. The disaster is referenced but not built toward. The eruption sits in the background as historical fact rather than dramatic destination.

**Closer — polite signoff:**
> "Pompei is a city shaped by preservation rather than reconstruction. The volcanic ash that destroyed it also protected it... That's why the past never feels far away here. Thanks so much for watching. Let me know in the comments what city or scene you'd like to see next."

Tour-guide signoff. No moralised reflection. The video ends as it began — polite, informative, friendly. No structural arc completed because none was promised at the start.

### What the 1.1M London 1300 video does

**Opening — dramatic stakes announced:**
> "Today, we visit London, but not the modern one. We're going to the year 1300. I'm Arthur. Join me on this journey through the past. London. The year is 1300, and the city stands at its medieval peak. With 100,000 souls packed within its walls, London is three times larger than any other English city. Old St. Paul's Cathedral towers almost 500 ft into the sky, taller than anything Britain would build for another 400 years. Merchant ships from Venice, Florence, and the Hanseatic League crowd the Thames. This is England's crown jewel, the beating heart of a kingdom. **But in the next 50 years, two catastrophes would bring this mighty city to its knees. First, the Great Famine of 1315, 3 years of relentless rain that turned fields into swamps and grain into rot. Then, in 1348, something far worse...**"

Four critical script-craft moves missing from the Pompeii video:

1. **Date locked first.** "1300" is the anchor before anything else. Tells the viewer when they are.
2. **Scale established with concrete numbers.** 100K souls. 3× larger than any other English city. 500ft cathedral. 400 years before anything taller. The viewer can *see* the size.
3. **The dramatic promise is announced explicitly in the first minute.** "Two catastrophes would bring this mighty city to its knees." This is the dramatic engine that runs the entire video.
4. **The second catastrophe is teased without naming it.** "Then, in 1348, something far worse..." Curiosity gap inside the hook. The viewer has to keep watching to find out what.

The Pompeii video has none of these. The London 1300 video has all of them.

**Middle — sensory peak with restraint:**
> "Bodies piled up faster than they could be buried... Parents abandoned children they couldn't feed. Children became orphans when their parents starved... Between 10 and 25% of England's urban population was dead."

Specific numbers. Concrete consequences. No melodrama. Then the structural transition that signals Act 3:
> "London had survived, weakened, traumatized, but alive. **It had no idea what was coming next.**"

Perfect Chloe-tier dramatic move. The narrator briefly steps outside the story to address the viewer's knowledge of what's coming. The viewer knows the Black Death is next. The London characters don't. The dramatic irony is the engine.

The Pompeii video has nothing equivalent. It walks from building to building.

**Closer — moralised reflection:**
> "We've learned from their mistakes. We don't dump sewage in our drinking water. We understand disease transmission. We have grain reserves and insurance systems. But the fundamental challenge, concentrating millions of people in one place and keeping them fed, healthy, safe, that's still London's legacy. They built the first truly urban society in English history, then watched it nearly die, then rebuilt it stronger. We're still living in the world they created, a world where cities dominate, where commerce trumps status, where catastrophe leads to reinvention instead of collapse. London proved it first through famine, plague, and death. **Cities survive.**"

The structural move that History Vault Retold's Pompeii ("They thought this couldn't happen to them. Well, they were wrong") and Chloe Plummer's Titanic ("I don't have the words to describe what I saw today") both use. **The disaster gets reflected back at the present-day viewer.** The video ends with the historical event having moral weight in the modern world. The viewer is left holding something.

The Pompeii video ends with "Until next time." Nothing reflected back. Nothing held.

### The Diagnosis

Same operator, same format, same tools, same runtime, same thumbnail format produces a 632K-view video when written as tour-guide, and a 1.1M-view video when written with dramatic-arc craft. **The ~470K-view delta is entirely script-craft attributable.**

This empirically validates the morning's hypothesis. Format alone is not the moat. Script craft is.

## What Final Hours Already Does Right

Cross-checking against the script-craft moves identified in the London 1300 winner:

1. Date locked first ✅ — "December 1872. A merchant ship is found drifting on the Atlantic..."
2. Scale established with concrete numbers ✅ — "Eight adults and a two-year-old child aboard. None of them were ever found."
3. Dramatic promise announced in hook ✅ — "But there is one person the story almost always leaves out. A seven-year-old boy named Arthur Stanley Briggs."
4. Sensory peak with restraint ✅ — Mary Celeste's "breakfast cooling on the table... Sarah Briggs's sewing basket... toys... a little girl's clothes"
5. **Moralised closer — PARTIAL.** Mary Celeste ends with "...and the ocean took him too" but lacks the present-day reflection move that London 1300 deploys.

Final Hours is operating at Arthur's craft tier already on most beats. The single biggest weakness is the closing reflection move — Mary Celeste and Pudding Lane both close on the historical event itself rather than reflecting the moral weight back at the present-day viewer. This is the smallest fixable variable that would move Final Hours closer to Arthur's 1.1M tier. See script-craft-principles.md Principle 10.

## Demand-Signal Cross-Check Against Final Hours Backlog

| Backlog topic | Recent viral signal | Verdict |
|---|---|---|
| Mary Celeste | Just shipped | n/a |
| Wilhelm Gustloff | 105K best result @ 39.8x outlier from tiny channel | Moderate signal |
| Lusitania | 330K on wreck-focused angle | Moderate signal (different angle) |
| Donner Party | 8.5K single result | Weak signal |
| Hindenburg | No real results | Weak signal |
| Pompeii House of Menander | No specific results | Weak signal |
| Pompeii Stabian Baths children | No specific results | Weak signal |
| Pliny the Elder family | No specific results | Weak signal |
| Pompeii (general) | Arthur 632K, History Vault Retold 320K | Saturated but proven |

**The strongest demand signal is for content NOT on the current backlog:** the Black Death / Great Famine / plague-era catastrophe topic. Arthur's London 1300 (Black Death framing) hit 1.1M. Mira's Black Death hit 22K (her 1.5x outlier). There's no plague video on the Final Hours backlog. This is a genuine backlog gap worth filling.

## Concrete Recommendation for Next Final Hours Video

**Eyam, Derbyshire 1665.** The village that voluntarily self-quarantined during the Great Plague to stop spread to neighbouring villages. 260 died of 350 inhabitants. Catherine Mompesson (the rector's wife) and William Mompesson (the rector) are named, documented, and have surviving letters.

Why Eyam fits Final Hours specifically:

- **Single isolated community making a choice with permanent consequences** — same emotional architecture as Mary Celeste's empty ship
- **Named protagonists with documented last words** — Catherine Mompesson's death August 25 1666, William's surviving letters to family
- **Failure-to-warn structure inverted** — they chose to *not* warn outsiders, sealing themselves in to save others
- **Moralised closer almost writes itself** — "They chose to die so others would live"
- **Black Death lane is hot** — Arthur's 1.1M proof, Mira's 22K proof
- **No English-language viral video on the Eyam framing yet** — open positioning
- **Differentiates Final Hours from Arthur** — he covers cities; Final Hours covers individual final hours within those events

The Eyam adaptation lets Final Hours hit Arthur's craft tier (10 principles applied), in a topic vertical with proven demand, in a positioning that's currently empty. Strongest single-video recommendation across the entire backlog audit.

## What Final Hours Should Borrow From Arthur

Beyond the three script-craft principles (8, 9, 10 — banked in script-craft-principles.md), one further observation:

**Arthur uses a named-narrator companion register.** "I'm Arthur. Today we step into ancient Pompei. Walk with me through the past." Every video. The channel handle IS the narrator's name. Solves the parasocial-warmth problem without putting a face on camera.

Final Hours could adopt this without changing anything about the production pipeline. Just name the narrator. Open every video around 0:15-0:20 (after the cold open, never before) with: "I'm [name]. This is Final Hours. Walk with me through what happened next." See PIPELINE_PLAYBOOK Part 7 for the full implementation pattern. Name shortlist: Edmund or Walter (period-British scholarly), Daniel or James (period-neutral dignified).

## Banking Status

The three new script-craft principles from this analysis are banked as Principles 8, 9, 10 in script-craft-principles.md. The named-narrator pattern is banked in PIPELINE_PLAYBOOK.md Part 7. The Eyam recommendation lives here and waits for the final-hours-backlog.md update.

This document itself is the comparative case study — referenceable when future videos are being written and the question "does this script announce its arc / use act-transition irony / close with reflection?" needs an empirical answer.

ARTHUR_EOF

echo "  ✓ Created arthur-revives-script-craft-analysis.md"

# ===========================================================================
# 5. CREATE channel-4-hypothesis.md
# ===========================================================================

cat > shared/docs/channel-4-hypothesis.md << 'CH4_EOF'
# Channel 4 — Strategic Hypothesis
*Pre-launch strategic frame.*
*Drafted 1 June 2026. Launch target: mid-2027.*

## The Core Hypothesis

Chasing the current AI-cinematic-recreation format directly is the wrong move. The format is saturated with format-copycats (Mira, Woodstock channel, dozens of small failures in NexLev's similar-channels data), and the channels that succeed at scale (Chloe vs History at 2.1M-view tier, Arthur Revives the Past at 1.1M-view tier) do so on craft-tier capabilities — dramatic script architecture, character introduction discipline, stakes establishment, restrained closer — that are NOT widely distributed among YouTube creators.

The durable position is **adjacent** to the format with capability advantages competitors cannot match within the format's window.

## Channel 4's Differentiation Axes

1. **Male AI avatar protagonist** — currently uncontested at scale in this lane. Chloe, Emma (secular and biblical), Mira are all female on-camera. No major operator is running male-protagonist first-person time-travel cinema at viral scale.
2. **First-person protagonist register with optional second-person address** — hybrid between Chloe (pure vlog) and History Vault Retold (pure documentary). The male AI avatar narrates events as the protagonist while occasionally turning to address the viewer directly.
3. **Underserved verticals** — military history embedded witness, maritime exploration, classical world from male POV, survival/wilderness. NOT Pompeii/Titanic/Black Death (saturated).
4. **Lazarus-apprenticeship script craft** — see lazarus-films-curriculum.md. Six months of master-writer adaptation discipline before launch, building dramatic instinct that copycats cannot shortcut.
5. **Shared capability stack with Lazarus and Final Hours** — Hetzner-deployed avatar, frame-accurate Whisper sync, multi-speaker dialogue, character consistency, dramatic-arc craft.

## Why Not Launch Sooner

Launching before the Lazarus apprenticeship produces Mira-tier output — surface-format right, dramatic architecture missing. The data from competitor analysis shows this failure mode reliably produces declining VPH curves and audience burnout within 4-6 videos.

The Lazarus apprenticeship through Sredni Vashtar (Saki — perfect endings), Maltese Falcon (Hammett — compression and dialogue), and The Loving Spirit (du Maurier — interior register, opens 1 Jan 2027 in US PD) builds the dramatic taste that Channel 4 will need to operate at Chloe's or Arthur's tier rather than Mira's.

## Why The Lane Will Still Exist In Mid-2027

Format-chasers burn through audience trust in weeks. Esme's high-volume operator model survives because she monetises the playbook itself (ebook + memberships) — but most operators chasing format collapse within months. Mira's 4-video decline is the typical trajectory.

Long-form viral-tier competition in this lane is **thinner than aggregate metrics suggest**. CHRONVEIL is 95% Shorts. Chloe vs History is 71% Shorts. Pure long-form craft-tier operators are rare and irreplaceable on a competitor timeline shorter than the Lazarus apprenticeship window.

By mid-2027:
- Format-replicator competition will have churned through 2-3 cohorts of operators
- Esme's playbook-as-product model will be widely copied, diluting it
- Saturation pressure will push craft-tier operators (Arthur, Chloe) to differentiate further or plateau
- A craft-tier male-protagonist entrant with shared-stack production economics enters into a thinner field than today

## Compounding Logic

Every capability built for Channel 4 also serves Lazarus and Final Hours:

| Capability | Built when | Serves |
|---|---|---|
| Whisper frame-accurate sync | 1 June 2026 (Mary Celeste) | All three |
| Storyboard discipline auditor | 31 May 2026 | All three |
| proj_paths convention | 31 May 2026 | All three |
| Hetzner deployment | 4 June 2026 | All three |
| Lip-sync character consistency | Mid-June 2026 R&D | Lazarus dramatic dialogue + Channel 4 protagonist |
| Multi-genre script architecture | Phase 2 backlog | Lazarus dialogue + Channel 4 character beats |
| Dramatic-arc script craft | Lazarus apprenticeship June-Dec 2026 | Channel 4 viral-tier writing |

The investment IS the script-craft. The channels are how it deploys.

## Sequence Lock

- **June 2026** — Hetzner migration (Thursday 4 June). Avatar capability R&D begins.
- **June-August 2026** — Sredni Vashtar (Saki) proof of concept. Avatar capability proven on dramatic dialogue.
- **15 August 2026** — Astana AI Film Festival submission deadline. Maltese Falcon (Hammett, US PD since Jan 2026) target.
- **Aug-Dec 2026** — Additional Lazarus adaptations as apprenticeship continues. Multi-author dramatic-craft library expands.
- **1 January 2027** — The Loving Spirit (du Maurier, opens US PD this date). Lazarus marquee launch with literary-event framing.
- **Q1-Q2 2027** — Channel 4 pilot script written using Lazarus-trained dramatic instincts. Avatar character finalised. Vertical selected.
- **Mid-2027** — Channel 4 launches.

## What Tomorrow's Data Will Inform

Mary Celeste's first 48 hours of retention data will indicate whether protagonist-anchoring framing meaningfully outperforms artifact-anchoring framing. If yes, the Channel 4 thesis strengthens — protagonist storytelling generalises across registers. If no, the framing for Channel 4 needs revision but the architecture above still holds.

Either way, the strategic architecture is durable. The Lazarus apprenticeship runs regardless of any single video's performance. The Hetzner capability stack runs regardless. The dramatic-craft moat compounds regardless.

## What Channel 4 Will NOT Be

- **Not a Mira-style format-copy** — surface format right, dramatic architecture missing
- **Not an Esme-style throughput operation** — 1.5 videos per day at medium craft monetised through ebook
- **Not a Pompeii/Titanic/Black Death entry** — those verticals are saturated; the algorithm will pair new entries against Chloe and Arthur
- **Not launched before the apprenticeship is complete** — premature launch produces Mira's curve, not Chloe's

## What Channel 4 WILL Be

- A craft-tier long-form historical recreation channel
- With a male AI avatar protagonist
- Operating in an underserved vertical (military, maritime, classical, or survival — selected via Q1 2027 NexLev research)
- Deploying scripts written with Lazarus-apprenticeship-trained dramatic instinct
- Running on Hetzner-deployed avatar capability proven on Lazarus first
- Sharing the production pipeline (Whisper sync, discipline auditor, multi-speaker dialogue) with Final Hours and Lazarus

The unique strategic combination — male-protagonist + craft tier + underserved vertical + shared-stack economics — is not currently occupied by any operator in the NexLev competitive data. The window for this entry exists now and through mid-2027. Beyond that, the position becomes harder to claim as the lane matures.

CH4_EOF

echo "  ✓ Created channel-4-hypothesis.md"

# ===========================================================================
# 6. CREATE lazarus-films-curriculum.md
# ===========================================================================

cat > shared/docs/lazarus-films-curriculum.md << 'LAZ_EOF'
# Lazarus Films — Apprenticeship Curriculum + Selection Filter + Taglines
*The strategic frame for Lazarus as the script-craft training ground for the wider operation.*
*Drafted 1 June 2026.*

## The Core Insight

Lazarus Films is not primarily a content channel. It is a **five-year creative writing curriculum disguised as a content business**, which simultaneously produces channel content AND develops the script-craft capability that powers Channel 4's eventual viral tier and Final Hours' continuing improvement.

## Why This Matters

The genuine moat in AI cinematic recreation is not the pipeline (now commodity), the visual style (now commodity), or the format (now widely copied). The moat is **screenplay-craft applied to YouTube format**.

Chloe vs History's Titanic video at 2.1M views and Arthur Revives the Past's London 1300 at 1.1M views work because the scripts understand character introduction with backstory, stakes establishment with explicit promise, failure-to-warn dramatic structure, sensory disaster scenes, and restrained emotional reflection in closing.

Mira's Pompeii at 15K views and her diminishing-returns curve (1.2x → 1.8x → 0.7x → 0.2x) demonstrate what happens when the format is copied without the script craft underneath.

The Woodstock channel at 45 views in 3 weeks demonstrates what happens when format + wrong-topic-match is applied without any craft filter at all.

## Why Public Domain Master Writers Become The Best Script Teachers

Every public domain author you adapt teaches a different dramatic technique:

| Author | Technique taught |
|---|---|
| Saki | Perfect cruel endings, last-line discipline |
| Hammett | Compression, dialogue rhythm, refusal to over-explain |
| du Maurier | Interior dread, landscape as character, Cornish register |
| Christie | Misdirection, reveal pacing, withheld information |
| Faulkner | Temporal manipulation, voice as structure |
| Conrad | Moral ambiguity, witness perspective, colonial weight |
| Wharton | Class observation, social cruelty in drawing rooms |
| Chandler (when PD) | Voice, metaphor, world-weariness |
| Highsmith (when PD) | Sustained dread, sympathy with the wrong character |
| O'Connor | Religious unease, sudden violence |
| Greene | Moral compromise, faith under pressure |

Five years of Lazarus adaptations = absorbed dramatic instincts of fifteen master writers.

## The Compounding Logic

Every Lazarus adaptation simultaneously:
1. Produces content for the Lazarus channel
2. Develops your dramatic-writing capability
3. Builds capability transferable to Channel 4 viral tier
4. Builds capability transferable to Final Hours' continuing improvement (Principles 8-10 came directly from Arthur Revives analysis, which is the same dramatic-craft-extraction skill applied to a contemporary operator instead of a PD author)
5. Creates a permanent craft moat no YouTube competitor can shortcut

By 2030: 50+ adaptations done, fifteen master writers internalised, capability moat impossible to replicate by anyone working only in YouTube.

## Why The Sequence Matters

Launching Channel 4 BEFORE the Lazarus apprenticeship would produce Mira-tier work — format right, dramatic architecture missing.

Launching Lazarus first means:
- Six months of dramatic craft development before Channel 4 launches
- Sredni Vashtar (Saki) = proof of concept + perfect ending discipline
- Maltese Falcon (Hammett, US PD since 1 Jan 2026) = feature length + dialogue craft + multi-character
- The Loving Spirit (du Maurier, opens US PD 1 Jan 2027) = interior register + landscape work + first-day-of-PD launch event
- Channel 4 launches mid-2027 with eighteen months of dramatic apprenticeship behind it

---

## The Brutal YouTube Test — Selection Filter

Reading PD authors as pleasure and reading them for Lazarus adaptation are not the same activity. Most romantic literary impulses fail the YouTube test. The filter below is applied BEFORE the romantic-literary instinct gets a vote.

### Five filter questions

**1. 30-second promise.** Does the opening promise an event the viewer wants to see resolved within the first 30 seconds? Tone is not enough. Promise.

Sredni Vashtar opens with a sick boy being told he will not live to grow up — 30-second promise.
Maltese Falcon opens with a beautiful woman walking into a detective's office with a lie — 30-second promise.
Wharton's Ethan Frome opens with a frame narrator looking at a man in a small town and wondering what happened to him twenty years ago — slower promise, viable for written fiction, dead on YouTube.

**2. One-sentence plot compression.** Can the story be described in a single sentence that makes a stranger want to watch?

Sredni Vashtar — abused boy's pet ferret kills his abuser.
Maltese Falcon — detective hunts the killers of his partner while a femme fatale lies to him.
Don't Look Now — couple grieving their daughter's death see her ghost in Venice.
Most Henry James doesn't compress.

**3. Peak inside the runtime window.** YouTube viewing optimum is 10-20 minutes. Some stories peak too early (Shirley Jackson's Lottery — 15 minutes is fine). Some peak too late (any 800-page novel with the climax in the final 100 pages). Adaptations have to compress AROUND the peak, which means the source has to have one.

A Saki story is a single beat. A 1930s Hammett novel is multiple beats but tightly engineered toward a 90-minute film equivalent. Joyce's Dubliners stories peak in fragments — some adaptable, some not.

**4. Visualisable specifics.** AI cinematography needs concrete images. Saki gives you the shed, the ferret, the boy's specific face. Hammett gives you Sam Spade's office, the falcon statue, San Francisco fog. Du Maurier gives you Manderley, the Cornish cliffs, Rebecca's monogrammed handkerchief. Henry James gives you interiority. The Ambassadors is harder to AI-cinema than Sredni Vashtar by an order of magnitude.

**5. Articulable protagonist stake.** What does this person want, and what will they lose if they fail.

Sam Spade — find his partner's killer, survive.
The boy in Sredni Vashtar — survive his abuser.
Maxim de Winter — possess Manderley without his first wife's ghost.
Boccaccio's frame characters in Decameron — escape plague-Florence.

Most modernist literature deliberately undermines stake-articulation, which is why it loses on YouTube.

### The discipline

The five filters narrow a romantic-literary shelf of fifty beloved works to maybe twelve. Of those twelve, only six or seven pass the additional channel-fit and visual-pipeline tests. That's the actual Lazarus shortlist for two years of production.

**Critical:** apply the five filters BEFORE the romantic-literary instinct gets a vote. The works you love most are not always the works that will work for Lazarus.

The works that fail the YouTube test still earn their reading time because they teach craft that transfers to the works that pass. Henry James fails the filter but his consciousness compression sharpens your instinct when you adapt Hammett. Joyce fails the filter but his epiphany endings sharpen your instinct when you adapt Saki.

## The Reading-as-Work Principle

Reading PD authors during the build phase is operational work, not leisure-time-with-strategic-bonus. Three filters run simultaneously during every PD read:

1. **Technique catalogue** — what craft pattern does this writer teach? Builds dramatic vocabulary without formal study.
2. **Adaptation scoring** — which specific work is the next Lazarus video? Length, dialogue density, character count, AI-cinematic feasibility, period accessibility.
3. **Capability spec** — which pipeline capability would this work unlock or demand? Each work read becomes a Hetzner R&D priority signal.

The three filters cannot be parallelised by hiring. They require synthesis between source material + current pipeline capability + channel register + current YouTube demand, which is operator-specific knowledge that doesn't transfer.

Output of running the three filters consistently over 6-12 months: a curated PD shortlist that no other operator can reproduce, because it's the intersection of public availability + craft pattern + pipeline feasibility + channel register + demand timing. The shortlist is closer to the actual moat than the public PD catalogue.

**Operational implication:** protected reading time IS pipeline-building time. Don't trade it for tactical execution time. The list compounds.

---

## Public Domain Legal Positioning

The audiobook YouTube ecosystem splits into three operator types:

1. **Pure PD operators** — focus on works whose authors died before 1955 (M.R. James, Le Fanu, Blackwood, Saki). Globally PD under life+70 rules. Legally clean everywhere.
2. **Copyright gray-zone operators** — read works still under copyright in their jurisdiction (Tony Walker reading du Maurier from the UK before 2059). Operating on practical reality that small-channel readings don't get enforcement. Legal exposure that scales with growth.
3. **Librivox re-uploaders** — take volunteer Librivox recordings (which are themselves PD) and republish with stock images. Legal but heavily commoditised.

Lazarus operates as Type 1. The targeted works are clean:

- **Sredni Vashtar (Saki, died 1916)** — globally PD everywhere on Earth. Zero risk.
- **Maltese Falcon (Hammett, published 1930)** — entered US PD on 1 Jan 2026. YouTube hosts in US territory; US law governs.
- **The Loving Spirit (du Maurier, 1931)** — enters US PD on 1 Jan 2027. First-day-of-PD launch with literary-event framing.

**This is a meaningful differentiator.** Lazarus can credibly claim "every adaptation we ship is verifiably in the public domain." That's a trust signal in a content category where competitors are operating in legal gray zones. It also positions for January 1st launch announcements that get press attention — "the first cinematic adaptation of [work] on the day it became publicly available" is genuine news to PD enthusiasts, literary journalists, and the kind of viewer who cares about provenance.

---

## Taglines

### Banner candidate (current frontrunner)

**LAZARUS: public domAIn revival**

Why it works:
- Single-pass legibility (no clause parsing required)
- "Revival" is the right verb — biblical resonance with Lazarus, semantic match to the channel mission, register-flexible (solemn or celebratory both work)
- Single capitalised AI is the only joke, quiet rather than smirking
- Internally coherent across channel name, mission, and tagline: Lazarus revives + public domain is what gets revived + AI is how
- Survives both dignified-literary register and accessible-YouTube register

### Deprecated draft

"Putting the AI in Public DomAIn" — clever but requires clause parsing. Works as social bio or end-card text where viewers have more time. Demoted from banner candidacy.

### Status

Banner candidate frozen at "LAZARUS: public domAIn revival" pending R&D phase. May still get displaced by something better that emerges during Sredni Vashtar production. Test by mocking up against the actual visual banner design before locking.

---

## The Source Material Is The Moat

Public domain dramatic writing from masters 1900-1960 is:

- **Free** (no licensing, no royalties)
- **Vast** (thousands of works across multiple writers per year)
- **Self-renewing** (1 January cohort enters every year)
- **Underused by YouTube creators** (who lack literary training to find it)
- **Permanent** (works don't expire, only enter PD)
- **Compounding** (each adaptation teaches techniques applicable to all future work)

This is the rarest combination of leverage available to a solo operator: free input material, permanent supply, training data for capability development, transferable across multiple revenue streams.

The PD catalogue is public. The taste curve through it is not. The taste curve is what becomes uncopyable.

LAZ_EOF

echo "  ✓ Created lazarus-films-curriculum.md"

echo ""
echo "Banking complete. Verification:"
echo ""
ls -la shared/docs/

