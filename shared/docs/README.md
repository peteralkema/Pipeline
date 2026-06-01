# README — The Final Hours Production Documentation Set
*Start here. This is the map to the territory.*
*Last updated: 31 May 2026 — after shipping Pudding Lane (Final Hours video 5).*

---

## What this document is for

Read this when you start a new chat about production work. Read this when your brain feels fuzzy and you've forgotten which document covers what. Read this when you're orienting after a few days away.

This README is the entry point. The actual work happens in the other documents. Their job is depth; this document's job is to point you to the right depth at the right moment.

---

## The documents at a glance

There are nine working documents across `shared/docs/` and the channel `docs/` folders. They split into three tiers based on how often you need them.

**Tier 1 — read at the start of every production cycle (5 documents):**

1. `production-system-as-moat.md` — the strategic spine. Why all the discipline matters.
2. `PIPELINE_PLAYBOOK.md` — the operational reference. What commands to run.
3. `script-craft-principles.md` — the craft layer. What makes a good script.
4. `production-patterns-that-work.md` — the production patterns. Canon and storyboard discipline.
5. `final-hours/docs/backlog.md` — the forward queue. What's next.

**Tier 2 — read when the situation calls for it:**

6. `competitive-analysis.md` — read before topic selection. What's already in the lane.
7. `calibration-reference.md` — read when the flat period feels like failure. Permission to keep going.

**Tier 3 — read for specific planning moments:**

8. `hetzner-pre-read.md` — read when planning the migration.
9. `scaling-architecture.md` — read when planning multi-channel growth.
10. `multi-genre-script-architecture.md` — read when starting Channel 3 R&D.

---

## What each document actually covers

### Tier 1 — the five-document production stack

**`production-system-as-moat.md`** — the strategic anchor. Sam Altman's "design for continuous and exponential improvement in the models" applied to AI video production. Defines the three layers — fast (tools that change every 3-12 months), orchestration (pipeline that lasts years), discipline (habits that compound over a career). The actual moat is the discipline layer. Read this when you've forgotten *why* the rulebook, the canon discipline, the encapsulation principle, and the bank-failures-as-principles habits matter. The other documents are operational consequences of this one.

**`PIPELINE_PLAYBOOK.md`** — the operational reference. The 12-step lifecycle from topic to published video. Every command, every flag, every file path, every troubleshooting recipe. Schema clarifications. The streaming patch story. The metadata.json upload behavior. The thumbnail design pattern. The A/B testing pattern. Read this when you need to know exactly what command to run next, or when something breaks and you need the troubleshooting recipe.

**`script-craft-principles.md`** — eleven script-craft principles banked across Pompeii, Anne Boleyn, Hartley, Hindenburg, and Pudding Lane production cycles. Cold-open structure, sensory writing, clock-anchored dread, silent beats, image-not-explanation closing, the cold-open contract refinement from Hindenburg retention data, low-friction protagonist anonymity from Pudding Lane, narrative seeds planted early from The Fool study, pace-aware sensory density from Pudding Lane voiceover analysis. Includes a pre-lock audit table. Read at step 3 of the playbook (script writing). Audit every script against the principles before going to canon.

**`production-patterns-that-work.md`** — eleven architectural patterns that minimize stills drift, restill cycles, and time-to-ship. Face-never-resolved canon strategy, ensemble anonymization via framing, object-substitution for groups, empty-room shots, scene canons over character canons, fire-as-environment, parallel thumbnail design, period-accuracy guards, beats.json schema, per-location shot cap, voiceover duration audit. Read at step 5 (canon writing) and step 8 (canon-aware editing of the storyboard). These are the decisions that make Pudding Lane ship clean on first pass.

**`final-hours/docs/backlog.md`** — the live forward queue. Current state of all published and scheduled videos with their metrics. Decisions waiting on data (the Hindenburg vs Pudding Lane retention comparison, the A/B thumbnail test). Video 6 direction principles. Candidate topics reordered by protagonist-register (anonymous vs named). Cross-promotion discipline. Channel velocity check. Read at the very start of any production cycle to know what's next.

### Tier 2 — situational reading

**`competitive-analysis.md`** — ten Final Hours-adjacent channels analyzed with their actual NexLev data. Majestic Studios' breakthrough pattern. The Fool's long-haul artisan model. Arthur and Matt's fast-positive trajectories. Lessons stolen from each. Useful before topic selection (step 1) — check which competitors are already in your candidate topic's lane before committing.

**`calibration-reference.md`** — four channels with very different breakthrough timelines. Majestic Studios broke out at month 9 after six flat months. The Redline Report broke out at month 35 after years of plateau. Matt Reconstructs broke out in 6 months. Arthur Revives in 4 months. Read when the flat period feels like failure. The shape is real. Keep shipping.

### Tier 3 — planning-specific reading

**`hetzner-pre-read.md`** — what Hetzner is, what to buy, what migration involves, the trigger conditions for migrating now vs deferring. Read when planning the Hetzner weekend (currently scheduled for 7 June).

**`scaling-architecture.md`** — what's already future-proofed for multi-channel growth. What needs work at scale but isn't blocking now. The fal cost curve as channels multiply. The build-for-two, design-for-ten, refactor-at-four principle. Read when planning Channel 3 launch or thinking about portfolio-level decisions.

**`multi-genre-script-architecture.md`** — Channel 3 R&D groundwork. Dramatic literature adaptation architecture. Read when starting Channel 3 work (currently planned for after Hetzner migration).

---

## How to start a new production chat

When you're starting fresh — new video, new chat — the discipline is:

**One — upload exactly five documents.** The tier 1 stack. Production-system-as-moat, PIPELINE_PLAYBOOK, script-craft-principles, production-patterns-that-work, and the current backlog. These five together cover everything needed to take a video from "let's do this topic" through "video uploaded and scheduled."

**Two — tell Claude where you are in the production cycle.** Don't make Claude guess. One sentence is enough. *"Here are the references. We're starting video 6 from topic selection."* Or *"Here are the references. Script is locked, moving to canon design."* Or *"Here are the references. Stills are generated, going into review."* That single sentence collapses Claude's surface area from "all five documents" to "the relevant section of one or two of them."

**Three — drive the production yourself.** The documents are the system, but the flow is yours. Don't let Claude pretend to follow the playbook step-by-step on autopilot. Use Claude for the parts where pattern-matching, sensory writing, canon design, storyboard editing, and analytics interpretation genuinely benefit from a second mind. The mechanical operational work stays yours.

**Add tier 2 documents when the situation calls for them.** If topic selection feels uncertain, add `competitive-analysis.md` to the chat. If morale is a factor, add `calibration-reference.md`. Don't pre-load them — pull them in when needed.

**Leave tier 3 documents out of production chats.** They belong to different conversations — infrastructure work, multi-channel strategy work, Channel 3 R&D work. Mixing them in pollutes the production flow.

---

## How to start a non-production chat

Three other kinds of chat worth distinguishing:

**Infrastructure / Hetzner migration:**
Upload `production-system-as-moat.md` (for the layered architecture context) and `hetzner-pre-read.md`. That's enough. Don't pull in production documents — they're irrelevant to the migration work.

**Channel 3 R&D:**
Upload `production-system-as-moat.md`, `production-patterns-that-work.md` (the patterns mostly transfer), `multi-genre-script-architecture.md`, and the Channel 3 strategy doc if one exists. Leave Final Hours-specific documents out.

**Strategic planning / multi-channel growth:**
Upload `production-system-as-moat.md`, `scaling-architecture.md`, `competitive-analysis.md`, and the relevant backlog. Skip the operational documents — they're not what the conversation is about.

---

## The documents map to a process

The five tier 1 documents are not just five reference files. They map to a specific cognitive flow during a production cycle.

When you're **selecting a topic**, the backlog is the document you reach for. It tells you what's been done, what's queued, what comparison data is pending. The competitive analysis comes in if you're uncertain about the lane.

When you're **writing the script**, script-craft-principles is the document you reach for. The ten principles plus the pre-lock audit table guide the work. The other documents stay quiet.

When you're **building canon and editing the auto-storyboard**, production-patterns-that-work is the document you reach for. Face-never-resolved, scene canons over character canons, object-substitution, the per-location shot cap. The playbook tells you the commands; this document tells you the architectural decisions inside the commands.

When you're **running the pipeline**, the playbook is the document you reach for. Step by step. Troubleshooting when something breaks.

When you're **publishing and analyzing retention**, the backlog is the document you reach for again. Update it. Bank the analytics. Decide what the next video is.

Production-system-as-moat sits underneath all of this as the *why*. You don't reach for it during a specific step; it's the air the other documents breathe.

---

## What goes wrong without this README

The honest failure mode of having nine working documents is that the next-chat-you (or future-Claude) doesn't know which subset matters. You upload all nine and the chat becomes an audit of the documentation rather than production work. You upload only one and miss the patterns that prevent Pudding Lane's pacing issue from recurring. You upload the wrong combination and discover mid-script that the relevant lessons are in a document you didn't bring.

This README solves that by being the *map*. Always uploaded first. Always uploaded alongside the tier 1 stack. When in doubt, read this; it tells you what to read next.

---

## When this README itself becomes outdated

This document is current as of 31 May 2026. It will need updating when:

- A new working document is added (e.g. when `channel-3/docs/strategy.md` lands, or when a new principle document earns its place)
- An existing document's scope changes substantially
- The tier 1 / tier 2 / tier 3 split changes because a tier 2 document becomes load-bearing for production, or vice versa
- The production lifecycle itself evolves (e.g. post-Hetzner migration, the operational layer of the playbook will need new content)

The discipline: when you find yourself uploading documents in a different combination than this README recommends, ask why. Sometimes the situation is one-off. Sometimes it's a signal that the README needs updating to reflect a new pattern.

---

## What this README is NOT

Operational guidance. Read the playbook for that.
Craft guidance. Read script-craft-principles for that.
Production architecture. Read production-patterns-that-work for that.
Strategic framing. Read production-system-as-moat for that.

This README is a map. The map is not the territory. The territory is the work — and the work is in the other documents.

Get them in front of you in the right order at the right time and the work flows. That's all this document does.

---

## The five-document production stack — final summary

For copy-paste convenience when starting a new chat:

> Here are the reference documents. I'm starting video [N] from [current stage]. Documents attached: production-system-as-moat.md, PIPELINE_PLAYBOOK.md, script-craft-principles.md, production-patterns-that-work.md, final-hours-backlog.md, README.md.

That single message gets a new Claude up to full operating context in one upload.
