# Script-Craft Principles
*The craft lessons that make a Final Hours script work.*
*Last updated: 31 May 2026 — after shipping Pudding Lane through one clean stills generation pass.*

This document captures *what makes a good Final Hours script*. It is read at script lock-in (step 3 of the Pipeline Playbook). Every script should be audited against these principles before going into production.

This is the craft layer. The production layer is `shared/docs/production-patterns-that-work.md`. The pipeline layer is `shared/docs/PIPELINE_PLAYBOOK.md`. Each governs a different question. Read all three.

These are not aspirational principles. Every one of them has been pressure-tested in production. They earned their place by surviving a real video cycle and showing up in the result.

---

## Principle 1 — Open cold with three concrete facts in ten seconds

The lesson. The first ten seconds of the cold open should contain at least three concrete, specific, falsifiable facts that anchor the story in a real moment in time. Date. Location. Person. Money. Object. Time of day. Specific number.

Why it works. The Final Hours audience opted in for documented historical recreation. Vague openings ("in a small town in the seventeenth century, a young woman...") signal generic AI content. Specific openings ("just before midnight on Saturday the first of September, 1666, in a bakery on Pudding Lane...") signal that this script knows what it is talking about.

The Chloe-school comparable is "April 10th 1912, $500 ticket, third class cabin G-Deck." Concrete enough that the viewer trusts they are not about to be lied to.

How to apply. Before writing anything else in the cold open, list the specific anchors. Date. Place. Person. Some object or amount or time. Front-load them in the first three sentences.

Pudding Lane's cold open does this: "just before midnight on Saturday the first of September, 1666" + "narrow timber-framed house on Pudding Lane" + "young woman in her late teens or early twenties" + "bakery kitchen." Four anchors. Inside the first ten seconds.

When you cannot find three concrete anchors, the topic is probably not a Final Hours topic. Final Hours stories are documented; vague ones are something else.

---

## Principle 2 — Acknowledge AI-recreation craft once, early, single line

The lesson. Acknowledge the AI-recreation discipline of the channel through a single sentence somewhere between 0:20 and 0:35. Brief. Specific. References the actual sources used. Never apologetic, never showy.

Why it works. Final Hours' brand promise is recreation from documented sources. The trust line confirms to the viewer that what they are about to see has historical grounding, AND it pre-empts the "this is just AI slop" objection from sceptical commenters.

The Pudding Lane formulation: *"Everything you are about to see has been recreated from the household accounts, the British Library letter of October 1666, and the parliamentary investigation that followed."*

Twenty-three words. Three specific source references. No defensiveness.

The Hindenburg formulation used "period photographs, the Doehner family's surviving accounts, and the official Lakehurst investigation records." Same structure, different sources.

How to apply. After the cold open, before the main narrative begins, drop the trust line as its own beat. One sentence. Move on.

What to avoid. Long explanations of AI-recreation methodology. References to specific software. Apologetic phrasing. The line works because it sounds like a museum placard, not a tech disclaimer.

---

## Principle 3 — Give sensation, not description

The lesson. The Final Hours register is sensory, not descriptive. Smells. Textures. Sounds. Specific tactile details. Not "she was tired" but "the warm flagstones from a day of baking." Not "the room was old" but "the timber settling into the night."

Why it works. Sensory writing puts the viewer IN the scene. Descriptive writing keeps them ABOUT the scene. The Final Hours audience watches for atmospheric immersion; the moment the writing turns gestural ("she would have felt scared") the spell breaks.

The Chloe-school comparable: *"It smells brand new. The paint, the floors, the fittings... Clean sheets, actual clean sheets"* — that single beat does what a paragraph of "she was overwhelmed by luxury" cannot.

Pudding Lane's Beat 1 (the kitchen at midnight) was specifically rewritten in v2 to apply this principle. The first draft was descriptive ("she would have helped clean the bakehouse"). The second draft was sensory: cooling oak ash, yeast left rising, the river three streets south, flagstones warm from a day of baking, copper pot ticking softly, watchmen calling midnight, timber settling, rats in the walls, the oven breathing heat fifteen feet across the kitchen.

How to apply. For every beat, ask: what does the scene smell like, sound like, feel like to touch? Pick the two or three most specific sensory details that put the viewer there.

When you cannot generate sensory detail, the writing is too far from the source material. Go back to research and find one more specific texture, sound, or smell from the period.

---

## Principle 4 — Clock-anchor the dread

The lesson. Use specific times to anchor the dread. "Ten o'clock that Saturday night." "A quarter past midnight." "One o'clock in the morning." The clock becomes the suspense engine.

Why it works. Time-stamped beats make the inevitability of what is coming feel material rather than abstract. The viewer knows what is about to happen; the clock advances toward it; the dread builds.

Hindenburg used "at seven twenty-one PM" and "at seven twenty-five PM" as the anchor points. Pudding Lane uses "ten o'clock... a quarter past midnight... half past midnight... one o'clock." The closer the anchors get to the catastrophe, the tighter the time intervals become.

How to apply. Identify the catastrophic moment in the story. Work backwards. Place time anchors at intervals leading up to it — wider intervals early, tighter intervals as the moment approaches. The narration should regularly remind the viewer where they are in the clock.

For the silent gap. Sometimes the most powerful clock-anchored beat is the one where time passes without anything happening. Pudding Lane's Beat 4: *"For an hour, nothing happens. For another hour, still nothing."* Two hours of silence between Farriner going to bed and Dagger waking. The clock doing the work alone.

---

## Principle 5 — Name the surrounding humans

The lesson. Even when the protagonist is the focus, name the other people in the story. Family. Colleagues. Witnesses. Their names ground the scene in specific human reality.

Why it works. Anonymous "his daughter," "his journeyman," "a maid" reads as generic. Named "Hanna," "Thomas Dagger," "Matilde" reads as documented. Naming is the single cheapest way to signal that the script has done its research.

Hindenburg names Hermann, Matilde, Irene, Walter, Werner. Pompeii names the family found at the gate. Pudding Lane names Thomas Farriner, his daughter Hanna, his journeyman Thomas Dagger. The unnamed maid is the only one without a name in Pudding Lane — and *her* anonymity is itself the story.

How to apply. Before writing any beat involving people, name them. Use their real historical names where known. Acknowledge explicitly when a name was never recorded.

The Final Hours dignity comes partly from this naming discipline. Names matter because the people mattered.

---

## Principle 6 — Let emotional beats land in silence

The lesson. The most powerful beats in a Final Hours script are the ones where the narrator stops talking. The viewer sees the image, the image carries the weight, the narrator does not narrate over it.

Mark silent beats explicitly in the script: `[silent beat — the burning bakery seen from a distance, the upstairs window glowing orange]`. The pipeline respects these markings; the assembled video holds the silence.

Why it works. Over-narration is the most common AI-video failure mode. Telling the viewer what to feel is the opposite of letting them feel. The silent beat is the channel's signature craft choice.

Pompeii (51% retention) used three silent beats. Hartley used at least two. Pudding Lane uses three: the dark bakehouse with the unseen ember, the burning bakery seen from a distance, and the Monument at dawn as the closing image.

The structural rule that works. Three silent beats per script — one in the second act (the dread sits), one in the third act (the catastrophe lands), one in the closing image (the meaning settles). Vary the placement, but three is the right count for a 7-minute Final Hours.

How to apply. Identify the moments where the narrator's voice would diminish rather than amplify. Mark them as silent beats. Trust the image.

---

## Principle 7 — End with the image, not the explanation

The lesson. Do not close the video with a documentary-narrator wrap-up ("and so we remember her" / "her story reminds us that..."). Close on a single image that lets the meaning settle without naming it.

Pompeii closes on ash. Hindenburg closes on a destroyed camera. Hartley closes on silence. Pudding Lane closes on the Monument at dawn, the gilded urn catching first light, the inscription that does not name her.

Why it works. The closing image is the moment the viewer carries out of the video. Explanations diminish. Images compound. The image becomes the post-roll thought, the comment-section reference, the thumbnail association for future videos.

How to apply. Write the final beat as image only. The narration above it may name the historical detail that closes the loop ("It does not name the woman who died first. Hers was never written down.") but the closing visual is held in silence and pulls the viewer's attention there.

The pattern across Final Hours videos. The closing image is always a single object or scene at a still moment: a ring, a clock, a camera, a column, an open door, ash, the morning after.

---

## Principle 8 — Cold open delivers the title's emotional contract within 20 seconds AND sustains tension through the first 2 minutes

The lesson. The cold open must pay off the title's promise within the first 20 seconds. Title says "She Wouldn't Jump"? Within 20 seconds the cold open must have established that she is at a window, that there is a reason to jump, and that she does not. Title says "34 Seconds to Save Her Children"? Within 20 seconds the cold open must have established that there were 34 seconds, that there are children to save, and that not all can be saved.

But — and this is the refinement we banked from Hindenburg retention data — *delivering the contract within 20 seconds is necessary but not sufficient.* The script must continue delivering tension throughout the first 2 minutes. Biographical or contextual setup that exceeds 90 seconds without renewing tension causes early drop-off.

Why this refinement matters. Hindenburg's cold open delivered the title's contract beautifully in the first 20 seconds. But beats 1-2 then spent 90 seconds on Frankfurt, Mexico City, $700 tickets, family biography. Viewers who clicked on "34 Seconds to Save Her Children" got the hook and then waited through a slow biographical detour before any tension returned. Result: 11.3% retention vs Pompeii's 51%.

The principle is two-part: deliver the contract early AND keep delivering tension throughout the first 2 minutes. Biographical setup is fine, but it must be interleaved with tension renewal, not stacked as a pure block.

How to apply. After writing the script, audit minutes 0:20 to 2:00 specifically. Mark every place where tension renews. If there is a gap longer than 45 seconds without a tension-renewal beat, restructure: cut some of the biographical material, or weave a tension beat into the biography itself.

The Pompeii test. Pompeii's cold open establishes "they waited" and then sustains low-grade dread throughout the first two minutes by intercutting Vesuvius-as-context with the family at the gate. The biography (their relationship, their home, their belongings) is delivered IN tension, not BEFORE tension. That is why it retained 51%.

What "tension renewal" looks like. A new fact about the impending catastrophe. A new sensory detail of dread (the smell of smoke, the unnatural stillness, the rumble underground). A clock-anchored beat that advances the clock toward the catastrophe. A narration return to the protagonist's awareness of something wrong.

---

## Principle 9 — Low-friction protagonist anonymity as a script structural choice

The lesson. When the historical protagonist's identity is unrecorded, marginal, or anonymous — lean into the anonymity at the script level. Do not invent a name. Do not invent a personality. Do not invent a backstory. Let the anonymity be the story.

Why it works at the script level. The viewer comes to Final Hours expecting documented recreation. When the historical record has not preserved a name, the dignified response is to acknowledge that absence explicitly. Pretending we know more than we do violates the brand. Acknowledging the gap honestly *is* the brand.

The Pudding Lane script does this in three deliberate moves:
- Cold open: *"We do not know her name. No record of it has ever been found."*
- Beat 1: *"We do not know where she was born. We do not know how long she had worked for Farriner. We do not know whether she had family in the city."*
- Closing: *"It does not name the woman who died first. Hers was never written down."*

The unnamed-ness is named at three points across the script. It becomes a refrain. It becomes the emotional spine.

The downstream production benefit. Principle 9 at the script level enables the face-never-resolved production choice at the canon level (see production-patterns-that-work.md, Principle 1). Script writing that establishes anonymity gives canon writing permission to never resolve the face. Together they eliminate the hardest Flux drift problem AND deepen the craft register.

When to apply. Any Final Hours topic where the historical record has lost a name or identity. Servants whose names were never recorded. Victims known only by their occupation or location. Witnesses referenced by relationship rather than name. These topics are *better* Final Hours material than topics where the protagonist's identity is well-documented but unremarkable.

When NOT to apply. Named protagonists where the audience needs to bond with one specific person. Matilde Doehner. Wallace Hartley. These need their identity foregrounded.

The honest test. Ask: *does the historical record name this person?* If no, this principle applies. If yes, write the character canon and let the audience know them.

---

## Principle 10 — Plant narrative seeds early, harvest them late

The lesson banked from The Fool's "Amy's Baking Company" study. Plant specific narrative details early in the script (preferably in the first 90 seconds) that the viewer will not understand the significance of yet. Harvest them in the closing beats, where they pay off the entire arc.

Why it works. The Fool's video plants "Amy spent a year in jail for bank fraud, Sammy was banned from France and Germany" at 1:42, then returns to deport them and explain at 17:10. The reward of recognition at the closing is what makes the closing land. The viewer feels clever for remembering; the script feels deliberate rather than meandering.

Final Hours has not historically planted seeds explicitly. This is a craft principle we are adding to the discipline going forward.

How to apply. Identify one or two specific historical details that pay off at the closing. Mention them early in a way that *seems* incidental. Return to them at the end with weight.

The Pudding Lane application that should have been there. The Monument's location at 202 feet from the bakery, its height of 202 feet, and the fact that it bears the names of everyone *except* the maid — this is the closing payoff. The seed could have been planted earlier ("the bakery sat at the corner of Pudding Lane and Fish Street Hill, just north of the river") so that the closing's "two hundred and two feet from where the bakery stood" lands as a return to a known place rather than a fresh location.

When NOT to over-apply. Final Hours is not a comedy show. Do not plant gags. Do not plant ironies. Plant only specific factual details that gain weight when revisited.

---

## How these principles compound

Principles 1-7 are the foundational craft layer. Apply them to every Final Hours script.

Principle 8 is the retention principle. Apply specifically when auditing the first two minutes of the script before lock.

Principle 9 is the anonymity principle. Apply when the topic warrants it; it dramatically simplifies production.

Principle 10 is the structural payoff principle. Apply when the closing has a strong specific detail that benefits from setup.

Together they produce scripts that:
- Open with documented authority (1, 2)
- Immerse via sensation rather than description (3)
- Build dread through specific temporal anchoring (4)
- Ground in named human reality (5)
- Let images do emotional work (6, 7)
- Retain viewers across the critical first 2 minutes (8)
- Embrace historical anonymity as craft choice (9)
- Reward attention with structural payoff (10)

---

## The pre-lock audit table

Before any script is locked, fill in this table. If any cell reads "weak" or "missing," revise before going to production.

| Principle | Status (met / partial / weak / missing / N/A) |
|---|---|
| 1 — Three concrete facts in 10 seconds | |
| 2 — AI-recreation acknowledgement | |
| 3 — Sensation not description | |
| 4 — Clock-anchored dread | |
| 5 — Named surrounding humans | |
| 6 — Silent beats (target: 3) | |
| 7 — End on image not explanation | |
| 8 — Cold open contract + 2-minute tension | |
| 9 — Anonymity as craft (when applicable) | |
| 10 — Seeds planted early, harvested late | |

Pudding Lane's pre-lock audit had all principles met or partial. It shipped clean. Future scripts should target the same audit pass before going to canon and stills generation.

---

## Maintenance

Add to this document when a new craft lesson is banked through a complete video cycle. Cleanly-shipped videos earn the right to add a principle. Failed videos that revealed a new craft failure mode also earn a principle (cautionary).

Resist adding aspirational principles that have not been earned through actual shipping. The discipline of this document is that every principle here has been pressure-tested in production.

---

## Principle 11 — Pace-aware sensory density

The lesson banked from Pudding Lane production. Dense single-location sensory writing produces dense single-location shot sequences AND gets accelerated by TTS. The combination produces breathless visual pacing that hurts retention.

Pudding Lane's Beat 1 layered six sensory details all inside the bakery kitchen — smells, tactile flagstones, copper pot, watchman calling, timber settling, rats in the walls, the oven breathing heat. All in one room. Claude's auto-storyboard faithfully generated 18-20 bakehouse interior shots across the first half of the video. Inworld then rendered the narration ~13% faster than the 135 wpm estimate (6:24 actual vs 7:20 expected), which compressed those bakehouse shots to ~4 seconds each. The cumulative effect: the first third feels breathless, the visual variety feels low, the retention curve will likely drop accordingly.

Why it works against the script. Principle 3 (sensation not description) is right — sensory writing puts the viewer IN the scene. But sensory writing applied to one location concentrates production output in that location. The fix is distribution.

How to apply. When writing a sensory beat, distribute the sensory detail across multiple locations rather than stacking it in one. Beat 1 of Pudding Lane v2 should have been: "smells in the kitchen + sound of the watchman in the lane outside + texture of her hands at the trestle table + the river three streets south + the wind blowing across the rooftops + the city of London settling into the night." Same sensory richness, six locations, naturally varied shot rhythm.

The structural test. Before locking a sensory beat, count the distinct locations it implies. If more than three sensory details land in the same location, redistribute.

The pacing test. Compute the script's word count divided by 135 (target wpm). That is your script-estimated runtime. Inworld's actual rendered runtime will be ~85-90% of that. Plan accordingly — write 10-15% more script than the runtime target so the rendered narration lands at the intended pace.

When to break this principle. Genuinely confined-location stories (a person trapped, a single conversation, a death watch) where the location confinement IS the emotional weight. For those, accept the dense single-location sequence as deliberate and lean into long static framings rather than trying to fake variety.

---

## Principle 11 — Pace-aware sensory density

The lesson banked from Pudding Lane production. Dense single-location sensory writing produces dense single-location shot sequences AND gets accelerated by TTS. The combination produces breathless visual pacing that hurts retention.

Pudding Lane's Beat 1 layered six sensory details all inside the bakery kitchen — smells, tactile flagstones, copper pot, watchman calling, timber settling, rats in the walls, the oven breathing heat. All in one room. Claude's auto-storyboard faithfully generated about 18-20 bakehouse interior shots across the first half of the video. Inworld then rendered the narration about 13% faster than the 135 wpm estimate (6:24 actual vs 7:20 expected), which compressed those bakehouse shots to about 4 seconds each. The cumulative effect: the first third feels breathless, the visual variety feels low.

Why it works against the script. Principle 3 (sensation not description) is right — sensory writing puts the viewer IN the scene. But sensory writing applied to one location concentrates production output in that location. The fix is distribution.

How to apply. When writing a sensory beat, distribute the sensory detail across multiple locations rather than stacking it in one. Beat 1 of Pudding Lane v2 should have been: smells in the kitchen, sound of the watchman in the lane outside, texture of her hands at the trestle table, the river three streets south, the wind across the rooftops, the city of London settling into the night. Same sensory richness, six locations, naturally varied shot rhythm.

The structural test. Before locking a sensory beat, count the distinct locations it implies. If more than three sensory details land in the same location, redistribute.

The pacing test. Compute the script's word count divided by 135 (target wpm). That is your script-estimated runtime. Inworld's actual rendered runtime will be about 85-90% of that. Plan accordingly — write 10-15% more script than the runtime target so the rendered narration lands at the intended pace.

When to break this principle. Genuinely confined-location stories (a person trapped, a single conversation, a death watch) where the location confinement IS the emotional weight. For those, accept the dense single-location sequence as deliberate and lean into long static framings rather than trying to fake variety.

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

