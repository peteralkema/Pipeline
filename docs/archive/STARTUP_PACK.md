# STARTUP_PACK
*Load-once context for any production chat. The map plus the non-negotiable craft.*
*v1.0 — 5 June 2026. Consolidates the README map, the moat spine, and the craft non-negotiables (script-craft, production-patterns, hook gate) into one file so a fresh chat needs only two attachments.*

---

## How to use this

At the start of a new production chat, attach exactly two files:

1. **`PIPELINE_PLAYBOOK.md`** — the operational layer (the orchestrator, the box, every command).
2. **`STARTUP_PACK.md`** (this file) — the map plus the craft you apply before touching the pipeline.

Plus, when the video is in flight, attach **the current `backlog.md`** — it's live state that changes every video, so it stays a separate file rather than baked in here (baking it in would make this pack stale immediately).

Then say one sentence about where you are: *"Starting video N from topic selection,"* or *"Script locked, moving to canon,"* or *"Stills generated, going to review."* That collapses the surface area to the relevant section.

The deeper documents (competitive analysis, calibration, hetzner-runbook, scaling, multi-genre, the Synthetic Press design docs) are **not** in this pack — pull them in only when the situation calls for them. The index in Part 5 says which and when.

The discipline this pack encodes: **drive the production yourself.** These are the system; the flow is yours. Use Claude for the parts where a second mind genuinely helps — sensory writing, canon design, storyboard judgement, analytics reading — not as an autopilot that pretends to follow the playbook step by step.

---

# PART 1 — THE MAP

The working documents split into three tiers by how often you need them.

**Tier 1 — every production cycle.** The moat spine (Part 2 below), the playbook (separate file), script-craft (Part 3), production-patterns (Part 4), the hook gate (Part 5), and the live backlog (separate file). Everything Tier 1 except the playbook and backlog is now inlined in this pack.

**Tier 2 — situational.** `competitive-analysis.md` (read before topic selection — what's already in the lane). `calibration-reference.md` (read when the flat period feels like failure — permission to keep shipping).

**Tier 3 — planning-specific.** `hetzner-runbook.md` (box build/rebuild). `scaling-architecture.md` (multi-channel growth). `multi-genre-script-architecture.md` + the Synthetic Press design docs (channel-4 / Lazarus R&D).

The cognitive flow across a cycle: **selecting a topic** → backlog (+ competitive analysis if unsure). **Writing the script** → script-craft (Part 3) + the pre-lock audit table. **Building canon / editing the storyboard** → production-patterns (Part 4). **Running the pipeline** → the playbook + the orchestrator. **Publishing / reading retention** → backlog (update it, bank the analytics, decide the next video). The moat spine sits under all of it as the *why*.

---

# PART 2 — THE MOAT SPINE (why the discipline matters)

The system has three layers, and they age at different rates:

- **Fast layer** — the tools (flux, Kling, Inworld, the model IDs). These change every 3–12 months. Don't anchor identity here.
- **Orchestration layer** — the pipeline and the conductor. Lasts years. Worth engineering well.
- **Discipline layer** — the habits that compound: bank every failure as a rule, encapsulate hard-won fixes in code, write canon before shots, audit before paying. **This is the actual moat.** Competitors can copy the surface format in a weekend; they cannot copy two years of banked discipline.

Two corollaries that govern day-to-day decisions:

- **Packaging beats production.** Demand-validated topic, a title that promises a dramatic arc, a retention hook, a consistent on-brand thumbnail — these drive distribution more than raw render quality. CTR + AVD in the first 48 hours are the signals the algorithm watches.
- **A principle not in code only runs if a human remembers it.** Bank failures as rules; push rules from docs into the conductor/scripts wherever it's worth it. (The running ledger of which principles are enforced in code vs. left to attention is Part 8 of the playbook.)

The strategic frame for the current bet: this is a content factory, and the channel is a distribution vehicle. The power-law logic (one breakout pays for the duds) means **shipping and generating algorithm signal comes before perfect positioning** at the early stage — but judge on per-video NexLev outlier scores and retention-curve *shape*, never on channel averages (best-first topic ordering drags averages down by construction).

---

# PART 3 — SCRIPT-CRAFT (the 10 principles + the gate)

Applied at Step 3 (script writing). Full treatment in `shared/docs/script-craft-principles.md`; this is the working distillation.

1. **Open cold with three concrete facts in ten seconds.** Date, person, place, money, object, time. Specific openings signal documented recreation; vague ones signal AI slop.
2. **Acknowledge the AI-recreation craft once, early, in a single line.** Name the actual sources ("recreated from the household accounts, the British Library letter, the parliamentary investigation"). Museum-placard register, never a tech disclaimer.
3. **Give sensation, not description.** Smells, textures, sounds. Not "she was tired" but "the warm flagstones from a day of baking." The narration earns its keep by being the senses the image lacks.
4. **Clock-anchor the dread.** Specific times before specific events; intervals tighten as the catastrophe approaches. The clock is the suspense engine. Silence between beats ("for an hour, nothing happens") can be the strongest clock beat.
5. **Name the surrounding humans.** Family, colleagues, witnesses, by their real recorded names. Naming is the cheapest signal that the script did its research.
6. **Let emotional beats land in silence.** Mark silent beats explicitly; the image carries the weight. Target three per video — one in the second act (dread sits), one in the third (catastrophe lands), one as the closing image (meaning settles).
7. **End with the image, not the explanation.** No "and so we remember her." Close on a single still object/scene. Images compound; explanations diminish.
8. **Announce the dramatic arc in the first minute, and sustain tension through the first two.** Deliver the title's emotional contract within 20s, then keep renewing tension — no biographical block longer than ~45s without a tension beat. (The Hindenburg 11% vs Pompeii 51% retention lesson.)
9. **Use narrator-to-viewer irony at an act transition.** At least once, the narrator steps briefly outside the diegesis to name what the viewer knows that the characters don't ("They thought the worst was behind them. It was just beginning.").
10. **Close with moralised reflection back at the present-day viewer.** After the closing image, hand the viewer something they didn't have at the start — a moral question about their own world. Not "thanks for watching." (Principles 7 and 10 coexist: the image lands first, the reflection follows.)

**Anonymity as craft (when applicable):** if the historical record lost the name, lean into it — don't invent one. Name the absence as a refrain. This enables face-never-resolved at the canon level (Part 4, #1).

### The pre-lock audit table (fill before locking the script)

| Principle | Status (met / partial / weak / missing / N/A) |
|---|---|
| 1 — Three concrete facts in 10 seconds | |
| 2 — AI-recreation acknowledgement | |
| 3 — Sensation not description | |
| 4 — Clock-anchored dread | |
| 5 — Named surrounding humans | |
| 6 — Silent beats (target: 3) | |
| 7 — End on image not explanation | |
| 8 — Cold-open contract + 2-minute tension | |
| 9 — Narrator-to-viewer irony at an act break | |
| 10 — Moralised closer reflecting at the viewer | |
| (Anonymity as craft — when applicable) | |

Any "weak" or "missing" → revise before canon or storyboard.

---

# PART 4 — PRODUCTION PATTERNS (the 12, distilled)

Applied at Step 5 (canon) and Step 8 (canon-aware beats). Full treatment in `shared/docs/production-patterns-that-work.md`. These are the upstream architectural choices that make the gap between script and shipped video small.

1. **Face-never-resolved as canon strategy.** For undocumented protagonists: face always from behind / in silhouette / deep shadow / turned away. Mirrors historical reality, eliminates flux's hardest drift problem, cuts canon entries.
2. **Ensemble anonymisation via framing, not canon.** Characters in <6 shots → anonymise by framing ("photographed from behind"), not a canon entry (which drifts anyway).
3. **Object-substitution for group composition.** Flux fails on 3–4 figures. Replace with objects that imply the group (an abandoned spinning wheel, a child's shoe in the ash). The viewer's imagination does the work.
4. **Empty-room shots carry meaning.** Flux renders empty interiors reliably; the absence is the subject (the empty landing after they ran).
5. **Scene canons over character canons** (~3–5× more reliable). Build canon around places, not people. Specify period, materials, lighting source, time of day, atmospheric register.
6. **Fire/storm-as-environment, never as subject.** Write what the fire *does* (glow on the wall, smoke across the ceiling), not close-ups of flames.
7. **Thumbnail design starts at script lock, not after stills.** Run it in parallel; saves 30–60 min/video.
8. **Architectural period-accuracy is the watermark.** Explicit "NOT the modern X" guards for any famous landmark (medieval cathedral not Wren dome; iron lattice not modern bridge).
9. **Canon block before shots in beats.json.** Schema is `{"canon": {...}, "beats": [...]}` — top-level key is `beats`, not `shots`.
10. **Per-location shot cap during canon-aware editing** (~10 shots/scene in a 7-min video). Audit distribution; consolidate over-concentrated sequences before generating.
11. **Voiceover duration audit before finish.** Inworld renders ~85–90% of the 135-wpm estimate. Write 10–15% more script than the runtime target; ffprobe-check before assembly.
12. **Angle-variation-within-canon, not canon-variation-across-shots.** Variety comes from angles/details/focal points inside a locked scene canon (the captain's cabin: the desk, the charts, a child's shoe, the unmade bed), not from constantly inventing new locations. Keeps cost flat and builds the channel's recognisable visual vocabulary.

(In v2.1 the pipeline automates several of these — face/expression discipline, canon-by-subject assignment, silent-reject handling, shot-grammar variety, low-memory assembly. The rest are still human judgement at authoring time. The full in-code-vs-human ledger is Part 8 of the playbook.)

---

# PART 5 — THE HOOK GATE (run on every first 60 seconds before lock)

Applied at Step 4.5. Transcribe your own first 60 seconds verbatim, then run this 7-question gate. **Pass = all 7. Fail 2+ = revise the opening, not the video.** Full corpus in `shared/docs/hook-craft-library.md`.

1. **Date anchor** — a specific historical date within the first 10 seconds. ("Recently" fails.)
2. **Named protagonist** — a specific human, by name or named role, within 15 seconds. ("A young woman" fails.)
3. **Specific number** — at least one concrete scale figure in the first 30 seconds; bonus for a comparative anchor ("3× larger than", "1800 years before"). ("Many" fails.)
4. **Foreshadow at 40–55s** — a clear pivot from setup to threat/mystery/disaster. (A clean tourist-brochure paragraph at 0:50 fails.)
5. **Cliffhanger at the 60s mark** — land mid-thought, not at a clean sentence end.
6. **Tense check** — present tense for Final Hours / Lazarus ("she is awake", "bread is baking"). For Synthetic Press, present for the iconic moment, past for context.
7. **Dramatic irony or contrast** — at least one of: explicit dramatic irony ("no one knew…"), a contrast structure ("three years ago X; today Y"), a subversion of expectations, or an ordinary-to-catastrophic juxtaposition.

---

# PART 6 — WHERE TO GO DEEPER

Pull these in only when the situation calls for it; don't pre-load them.

- **Topic selection feels uncertain** → `shared/docs/competitive-analysis.md` (who's already in the lane; title-formula patterns; the empty-lane findings).
- **The flat period feels like failure** → `shared/docs/calibration-reference.md` (breakthrough timelines: 4 months to 4+ years; you're inside the distribution).
- **Working on the box / rebuilding it** → `shared/docs/hetzner-runbook.md` (provision, harden, the 443 story, the rebuild procedure).
- **Multi-channel / portfolio decisions** → `shared/docs/scaling-architecture.md`.
- **Channel-4 / Synthetic Press / Lazarus R&D** → `multi-genre-script-architecture.md` + the Synthetic Press design docs (two-mode visual architecture, the 10 Vox principles, the component build plan). Keep these *out* of Final Hours production chats — mixing pollutes both.
- **Current state, queue, pending decisions, per-video metrics** → the live **`backlog.md`** (attach the current copy alongside this pack).

---

*This pack is a living artefact. Update it when a craft principle is added or refined, when the tier split changes, or when a deeper doc earns promotion into the load-once set. Keep it neat — the whole point is that two attachments get a fresh Claude to full operating context.*
