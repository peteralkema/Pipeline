# Final Hours — Backlog
*Last updated: 31 May 2026 — after shipping Pudding Lane.*

The forward queue. Live state of in-flight work, decisions waiting on data, and candidate videos. Read alongside `strategy.md` for the why, `shared/docs/PIPELINE_PLAYBOOK.md` for the operations, and `shared/docs/script-craft-principles.md` for craft.

---

## Live state

| Video | Published | Status | Notes |
|---|---|---|---|
| Pompeii v2 | 28 May | Baseline data point | 51% retention — channel high water mark. Ash closer banked as template. |
| Anne Boleyn | 29 May | Live | Cross-promo to X (~20 views) and SSC FB group contaminated the algorithmic read. Limited diagnostic value as comparable. |
| Hartley (Titanic) | 30 May | Live | First scheduled-publish video. ~17% retention. CTR ~2.15% — the previous channel high before Hindenburg. |
| Hindenburg | 30 May | Live | https://youtu.be/J1w2JkpG5xU — CTR 2.12% (74% above 1.22% baseline). AVD ~34s = 11.3% retention. Lowest retention of any Final Hours video. A/B thumbnail test running 13 days (MrBeast-face vs Matilde on-brand). |
| Pudding Lane | scheduled 01:00 Europe/Warsaw 1 June | Uploaded private | https://youtu.be/f1LT9g1un_Y — First face-never-resolved anonymous-protagonist video. One canon character + four scene canons. Shipped through clean stills generation pass. Title: "She Wouldn't Jump." |

---

## Decisions waiting on data

These are the things you cannot decide right now; they depend on what the algorithm does over the next 1-3 weeks.

### Hindenburg vs Pudding Lane retention comparison

The two videos test fundamentally different structural choices:

- **Hindenburg** — named ensemble protagonist (Matilde Doehner), high biographical setup density in the first 2 minutes, period photographs as reference, dignified register, multi-character canon. The data so far: clicks well, drops off fast.
- **Pudding Lane** — anonymous single protagonist (face never resolved), specific historical event (Great Fire 1666), distributed sensory writing across locations, one-character canon. We don't yet know how it performs.

If Pudding Lane retains noticeably better than Hindenburg, the architecture lesson is: **anonymity + single protagonist + face-never-resolved is the higher-retention register for Final Hours.** That has cascading implications for which candidate topics to script next.

If Pudding Lane retains roughly the same as Hindenburg, the retention problem is something other than character anonymity — most likely cold-open pacing, biographical-density vs tension-density balance, or shot rhythm.

If Pudding Lane retains worse than Hindenburg, the anonymity register may actually hurt — viewers may need a named human to bond with. (Worth knowing if true.)

### A/B thumbnail test on Hindenburg

13-day test running between MrBeast-face "HINDENBURG: A DEADLY MISTAKE" thumbnail and dignified Matilde-with-period-wardrobe "HER IMPOSSIBLE CHOICE" thumbnail. YouTube measures watch-time share, not just CTR.

Decision rule banked: **stick with the on-brand option even if MrBeast wins by 5-10%.** Brand is the moat that compounds across all future videos; an individual video's marginal advantage from off-brand packaging is not.

### Pinned comments outstanding

- Hindenburg: *"Matilde survived another 35 years and was buried in Mexico City beside her husband and her daughter. What do you think you would have done in those 34 seconds?"* (Not yet pinned. Add in the morning.)
- Pudding Lane: *"The Monument to the Great Fire of London stands 202 feet tall, exactly 202 feet from where Thomas Farriner's bakery once stood. It bears the names of the kings, the architects, and the city officials who built it. It does not bear the name of the woman who died first. Hers was never written down."* (Add immediately after Pudding Lane publishes at 01:00.)

---

## Video 6 direction

Three principles for choosing:

1. **Decide after Pudding Lane retention data lands (48-72 hours post-publish).** The Hindenburg vs Pudding Lane comparison determines the architectural register for the next 3-5 videos. Don't lock the next topic before the data lands.

2. **Build a topical cluster around whichever video shows strongest retention.** If Pudding Lane retains well, the next video should also be an anonymized-protagonist historical disaster — the Lusitania bandmaster (literal Hartley parallel), the Pompeii children at the Stabian baths, the Wilhelm Gustloff. If Hindenburg retains better than expected on closer analysis, named-protagonist disaster tragedy stays the register — possibly the Donner Party with a named focal character. Topical clusters compound algorithmically far more than topic variety.

3. **Apply all three principles banked today.** Pace-aware sensory density (distribute sensory detail across 3+ locations not 1). Per-location shot cap (no more than 10 shots per scene canon). Voiceover duration audit (ffprobe before finish, regenerate if >10% off estimate). Video 6 should ship without the Pudding Lane pacing issue recurring.

---

## Candidate topics

Reordered after Pudding Lane's anonymity experiment. Each topic flagged with its protagonist-register (Anonymous / Named).

**Strong anonymized-protagonist candidates** (if Pudding Lane retention validates the register):

- **The Lusitania bandmaster** *(Anonymous variant)* — the lesser-known bandmaster of the Lusitania who played as she went down. Direct Hartley parallel but unnamed in most records. One-character canon, scene canon for the ship.
- **The Pompeii children at the Stabian baths** *(Anonymous)* — the poignant skeletal posture preserved. The children's names are lost. Single confined location plus volcanic eruption as environment.
- **The Mary Celeste** *(Anonymous)* — empty ship found drifting, ten people aboard, all gone. Inverse of Pudding Lane — the protagonists are present only by their absence. Could be the most genuinely Final Hours topic in the backlog.

**Strong named-protagonist candidates** (if Hindenburg's named-character work needs another data point):

- **The Donner Party** *(Named)* — winter in the Sierra Nevada, the day they made the decision. James Reed and family as focal point. Multi-character but with clear documentary source material.
- **Pliny the Younger watching Vesuvius** *(Named)* — the night Vesuvius woke, the family of Pliny the Elder watching from across the bay. Pliny's letters survive. Strong "named witness to disaster" register.
- **House of Menander, Pompeii** *(Named)* — lavish interior whose residents we partially know. Single-location plus volcanic eruption. Tests canon mechanism on named historical figures with archaeological grounding.

**Wild cards** (genuinely different but worth holding):

- **The Wilhelm Gustloff** — 9,000+ deaths in the freezing Baltic, January 1945. Scale-of-tragedy challenge; would push retention with the sheer numbers. Anonymous or single-protagonist focal options both viable.
- **The Tay Bridge disaster, 1879** — Sunday evening train, bridge collapse, no survivors. Anonymous variant possible.

These are scaffolding ideas, not commitments. Pick one based on algorithm signal after Pudding Lane.

---

## Cross-promotion discipline

The 30 May lesson: don't push videos to social audiences in the first 48 hours. Let the algorithm cold-test. Specifically:

- Check retention curves at the 48-72h mark in Studio Analytics → per-video → Audience retention. Curve shape is diagnostic; view count is not.
- Cross-post only videos the algorithm has already shown signal on.
- Three cross-posts to the same audience in a week is fatigue.

Outstanding cross-post question: Hartley to SSC group is still pending. The dignity-under-pressure framing is a natural fit. Worth doing this week if Hartley's 48-72h retention curve looks healthy.

---

## Channel velocity check

Five videos shipped or scheduled in 7 days (28 May - 1 June). Cadence is real but unsustainable as a baseline. The 30 May Hetzner pre-read identified overnight render time as the bottleneck; that constraint will fire repeatedly if cadence holds at this rate.

Hetzner migration is planned for weekend 7 June. Until then, treat 1-2 videos per week as the realistic sustainable rate. Video 6 doesn't need to ship before the migration; the migration enables higher cadence after it.

---

## What this document is NOT

Pipeline operational guidance lives in `shared/docs/PIPELINE_PLAYBOOK.md`. Deferred build items (Whisper-SRT, pre-render cost estimate, beat-multiples, Hetzner migration, pipeline self-tests) live there. Operating reminders (venv name, channel detection, thumbnail script behaviour) live there. This backlog is the forward queue only.

Strategic framing (channel positioning, topic principles, audience mechanics) lives in `final-hours/docs/strategy.md`.

Production patterns (face-never-resolved, scene canons over character canons, object-substitution for groups, etc.) live in `shared/docs/production-patterns-that-work.md`.

Script craft principles live in `shared/docs/script-craft-principles.md`.

Together those documents cover the full operating context. This backlog focuses ruthlessly on *what's next*.
