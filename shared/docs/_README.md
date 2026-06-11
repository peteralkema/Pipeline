# README — The Production Documentation Set
*Start here. This is the map to the territory.*
*Last updated: 11 June 2026 — after the Sacred Dawn launch and the ante-machinam v2.0 consolidation. (Supersedes the 31 May 2026 Final-Hours-only edition.)*

---

## What this document is for

Read this when you start a new chat about production work, when your brain feels fuzzy and you've forgotten which document covers what, or when you're orienting after a few days away.

This README is the entry point. The actual work happens in the other documents. Their job is depth; this document's job is to point you to the right depth at the right moment.

**What changed since the 31 May edition:** the operation is now a multi-channel **YouTube Media Flywheel**, not a single channel. `YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md` is the umbrella doc that sits above everything. And the craft layer has consolidated: the former `script-craft-principles.md` is **retired into `ante-machinam.md`**, which is now the single pre-machine bible (constitution + craft canon + the threshold into the machine). Read ante-machinam where you used to read script-craft-principles.

---

## The umbrella

**`YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md`** — the strategic umbrella for the whole operation: one channel-agnostic pipeline serving multiple channels (Final Hours, Sacred Dawn, You Had To Be There live; Synthetic Press launching; Lazarus Films designed). The thesis: the production system is the moat; packaging beats production. **Read this first, every conversation.** Everything below sits beneath it.

---

## The documents at a glance

They split into tiers by how often you need them.

**Tier 1 — read at the start of a production cycle:**

1. `YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md` — the umbrella (above).
2. `production-system-as-moat.md` — the strategic spine. Why the discipline compounds.
3. `ante-machinam.md` — **the pre-machine bible.** Constitution (what the machine enforces), the full craft canon (what makes a script land — formerly script-craft-principles), Part III (how to write a VISUAL that renders + animates), the channel briefs, and the threshold into the orchestrator. Read this before brainstorming a topic and before locking any script.
4. `PIPELINE_PLAYBOOK.md` — the operational reference. What commands to run, the orchestrator, troubleshooting.
5. The relevant channel's strategy/backlog/creed — e.g. `sacred-dawn-creed.md`, `final-hours-backlog.md`. What's next for the channel you're working on.

**Tier 2 — read when the situation calls for it:**

6. `competitive-analysis.md` — read before topic selection. What's already in the lane.
7. `calibration-reference.md` — read when the flat period feels like failure. Permission to keep going.
8. `production-patterns-that-work.md` — canon and storyboard production discipline (the production-side companion to ante-machinam Part III).

**Tier 3 — read for specific planning moments:**

9. `hetzner-pre-read.md` — infrastructure (the box is live; read when changing infra).
10. `multi-genre-script-architecture.md` — Lazarus / multi-genre R&D.
11. Session notes (`SESSION-NOTES-YYYY-MM-DD-*.md`) — the running log of what was banked when.

---

## What the load-bearing documents cover

**`ante-machinam.md`** (the consolidation — the one most people get wrong about). It is now FOUR things in one, because keeping them together is what stops them drifting apart:
- **Part I — the Constitution:** the seven mechanical truths the machine enforces (continuous voice / every beat has words; header matches folder; spell out numbers; one VISUAL per Mode A beat; lock the script first; beat granularity ≤~55 words; every beat has an animatable foreground subject). Author against these from the first line or the build halts.
- **Part III — writing the VISUAL line:** faceless-by-default, scene-canons, object-substitution, fire-as-environment, and "Author for motion" (the drift-safe motion vocabulary that makes clips actually move).
- **Part IV — the craft canon:** the full treatment that *was* script-craft-principles, reconciled and de-duplicated, plus the 70s-nostalgia retention lessons and the packaging doctrine. The gate (first 60–90s), the body (recognition, recurring spine, clock-dread, naming, irony, seeds), the close (image + moralised closer), packaging (title/thumbnail complement-not-echo, comment-bait), and the 20-row pre-lock audit table (IV.7). **Audit every script against IV.7 before lock.**
- **Part V/VI — channel briefs + the threshold:** the per-channel register, then the exact parse → verify → dry-run → live → gates path into the orchestrator.

**`PIPELINE_PLAYBOOK.md`** — the operational reference. The lifecycle from topic to published video, the orchestrator (the channel-agnostic machine, its legs and two gates), every command and file path, and the troubleshooting recipes. Read this when you need to know exactly what to run next, or when something breaks.

**`production-system-as-moat.md`** — the strategic anchor. The three layers (fast tools / orchestration / discipline); the real moat is the discipline layer. The other documents are operational consequences of this one.

**`script-craft-principles.md`** — **RETIRED.** Now a one-line stub pointing to ante-machinam Part IV. Do not add craft principles there; add them to Part IV. (Kept as a stub so old links and upload habits resolve to the right place.)

---

## How to start a new production chat

**One — open with the umbrella + the bible.** Upload `YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md`, `ante-machinam.md`, `PIPELINE_PLAYBOOK.md`, and the working channel's creed/backlog. Those cover topic → script → production → publish for any channel.

**Two — tell Claude where you are.** One sentence: *"Sacred Dawn, episode two, from topic selection."* / *"Final Hours, script locked, going to canon."* / *"Stills generated, going into review."* That collapses Claude's surface area to the relevant section.

**Three — drive the production yourself.** The documents are the system; the flow is yours. Use Claude for the parts where a second mind genuinely helps — topic validation, sensory writing, the craft audit, storyboard/motion decisions, analytics interpretation. The mechanical operational work stays yours.

**Add tier 2 when needed** (competitive-analysis before an uncertain topic; calibration-reference when morale is a factor). Leave tier 3 out of production chats.

---

## Non-production chats

- **Infrastructure:** `production-system-as-moat.md` + `hetzner-pre-read.md`.
- **New-channel R&D:** the canonical reference + `ante-machinam.md` (Part III/IV transfer) + `multi-genre-script-architecture.md` + the channel's strategy doc.
- **Strategic / multi-channel planning:** the canonical reference + `production-system-as-moat.md` + `competitive-analysis.md` + the relevant backlog.

---

## When this README itself becomes outdated

Update it when a new working document is added, a document's scope changes, the tier split changes, a new channel launches, or the lifecycle evolves. The discipline: when you find yourself uploading docs in a different combination than this recommends, ask why — sometimes it's one-off, sometimes it's a signal the README needs updating.

The honest failure mode is that the next-chat-you doesn't know which subset matters — upload all of them and the chat becomes a documentation audit; upload one and miss the patterns. This README is the map that prevents that. Always uploaded first.

---

## The starting stack — for copy-paste

> Here are the reference documents. I'm working on [channel], [current stage]. Attached: YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md, ante-machinam.md, PIPELINE_PLAYBOOK.md, [channel creed/backlog], README.md.

That single message gets a new Claude to full operating context in one upload.
