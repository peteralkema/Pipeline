# _BRIDGE.md — LEGO-grade authoring, PIPELINE-grade production
*Written 25 Jul 2026. The best-of-both-worlds contract: author with every instrument LEGO
built, produce through the batch-of-batches machine — without touching the machine.
Governs Line B. Line F (LEGO 0–10 + Filmora, one at a time) continues unchanged.*

---

## 0. THE THESIS IN ONE PARAGRAPH

LEGO's value was never its render path — the render path is the part PIPELINE already does
better (assembles, thumbnails, uploads, schedules, unattended). **LEGO's value is the
authoring instrument**: package-first, the subject ledger, the scale budget, the three
dials, the variety audit, the token craft, the cold-open spec. Every one of those lives
in TEXT AND DATA, before a cent is spent — which means every one of them can ride into
the batch inbox with **zero changes to the engine**. The mechanism is a one-way compile:

> **Author in the LEGO CSV. Audit the CSV. Compile the CSV into the `<n>.md` +
> `<n>.thumb.json` pair. The pair enters the inbox like any other script.
> PIPELINE never knows LEGO existed.**

The CSV is the *instrument layer* (what the operator and the audits read). The .md pair
is the *machine layer* (what parse_script reads). One-way, deterministic, gated by
`check_script.py` exactly like a hand-written script — so the machine's own gate of
record still stands between authoring and spend.

**Engine changes required today: ZERO.** Two new standalone files only (`audit_script.py`,
`csv2script.py`), both of which read/write files and never import the engine.

---

## 1. WHY ZERO ENGINE CHANGES IS ACTUALLY AVAILABLE

Three things the pipeline already shipped make the bridge free — each one would otherwise
have been a required change:

1. **Floor-first + `kling_override` (MC v3.9.2).** Per-beat additive Kling routing already
   exists. LEGO's `draft_air` spend dial (sliding quota × motion-want × score floor) is
   just a smarter way to CHOOSE the override list — it can run at authoring time and emit
   the plan into the pair. The mechanism it feeds is already live.
2. **Per-beat MOTION → Kling prompt** shipped. LEGO's `motion` column compiles 1:1 to
   `MOTION:` lines.
3. **Project canon merge (project-wins) fixed 30 June** — though the bridge doesn't even
   need it: `{tokens}` are expanded at COMPILE TIME, so the .md that enters the inbox is
   fully resolved text. The parser sees plain VISUAL lines; token drift is impossible
   downstream because tokens no longer exist downstream.

---

## 2b. THE GOLDEN PAIR — build-order bias, made explicit

`bible-they-burned-v2.md` + `.thumb.json` — the channel's most successful batch-produced
video — is the named FORMAT AUTHORITY for every compiled pair, verified directly against
`parse_script.py`. The meta-principle (build order encodes bias) is handled by writing the
inheritance down and splitting it in two:

**LAW (inherited by every compiled script):** header = `channel / title / description /
tags`, single-line values, underscore channel form (`sacred_dawn`), NO slug key (slug is
the filename); body opens `## COLD OPEN` (the parser HALTS without a recognized section
heading); blocks emit `## ACT <ROMAN> — <NAME>`; beat = `[A] <narration on the tag line>`
+ `VISUAL:` + optional `MOTION:` in the same block; blank line between beats only.
thumb.json keys = `subject` (the full image prompt) / `title` / `subtitle` (the lockup).

**INCIDENTAL (the pair's content choices — NOT law):** its ~45-word beats, MOTION on
every beat, its title grammar, its act names, its topic. These are per-film decisions;
inheriting them silently would be the Final Hours contamination pattern repeating.

Conformance is mechanical, not aspirational: every compiled `.md` runs through
`parse_script.py` and must yield beats == CSV rows, a visual on every beat, narration on
every beat, zero warnings. The parser is the gate of record; when parser and compiler
disagree, the compiler is fixed.



| LEGO column | compiles to | verdict | notes |
|---|---|---|---|
| `block_id` | nothing structural (optional chapter comment for the description's chapter block) | **SURVIVES as authoring/audit unit** | Blocks remain the drafting pass size (§SCRIPT-CONTRACT 1A) and the unit the dials read. The machine doesn't need them; the author does. |
| `clip_index` | beat order in the .md | **SURVIVES (implicit)** | Row order IS the film. Same law as LEGO's flat index. |
| `sentence_id` | — | **DROPPED** | Exists only for `calibrate`'s TTS grouping. PIPELINE's model (VO rides above visuals, whisper-aligned, loosely coupled) never needs it. |
| `weight` (hero/connective) | nothing today | **SURVIVES in-CSV (audit + future)** | No variant grid on this path (see §4). Retained because (a) the audit checks hero density per block, (b) heroes rank first in the Kling plan, (c) it is the ready-made driver if hero-variant ever ships (§6). |
| `register` | wording of MOTION lines + authoring tone | **SURVIVES (indirect)** | Drives how motion is written, not a machine field. |
| `narration` | the beat's narration line | **1:1** | All laws intact: no tokens, numbers spelled out, prosody on dashes, ≤55w ceiling, ~15w on Kling beats so the clip plays as-is. |
| `phenomenon` | `VISUAL:` line, **tokens expanded at compile** | **1:1** | Every LEGO visual law rides along: names its own light, positive-statement only (never "no X"), contents-not-containers, depth, the cinematic test. |
| `subject` | — | **SURVIVES (audit-only)** | The single most important column, and it never needed the machine — it feeds the three dials at Step 3. This is the column that kills the sixty-fifth fire. |
| `scale` | — | **SURVIVES (audit-only)** | The escalation dial. Budgeted at Step 1, audited at Step 3, invisible to the parser. |
| `topic_class` (NEW: lore/universal) | — | **SURVIVES (ledger)** | Tonight's experiment column. Audit prints batch composition (≥70% universal). |
| `setting` (derived) | — | survives (audit) | Derived from the leading token pre-expansion; setting-aware sweep runs before compile. |
| `words` (derived) | — | survives (audit) | Pre-checks the 55w gate with the parser's own counting rules (em-dash/alnum filter) so `check_script` never surprises. |
| `variants` (derived) | — | **DROPPED** | No grid: one still per beat is the Line B economics. See §4 for what replaces the pick. |
| `still_cost`/`clip_cost`/`beat_cost` (derived) | — | survives (audit) | Reformulated for pipeline economics: `beats × still_price + kling_count × $0.42`. Bill of materials visible while still text. |
| `air` (kling/kb) | the **kling_override plan** emitted with the pair | **SURVIVES → existing mechanism** | draft_air's ranking logic runs at authoring; output is the per-beat additive list floor-first already consumes. Filled on every row; kb = floor. |
| `move` (push/pull/crane…) | — | **DOES NOT TRANSFER** | Pipeline's Ken Burns applies its own variation; there is no per-beat KB direction input. Accepted loss (§4). Column stays in the CSV, inert, for Line F reuse and the day the fx layer wants it. |
| `motion` (Kling prompt) | `MOTION:` line on kling beats | **1:1** | Only on `air=kling` rows; compiler hard-fails a kling row with blank motion (same invariant as LEGO). |
| `fx` (NEW, from 24 Jul) | — (inert until the fx build) | **FORWARD-COMPATIBLE** | dust/embers/mist/grain per beat. Authored now, consumed later by the one sanctioned engine change (§6). §0 law applies: fx on every beat is a bug. |

**Net:** eleven columns survive with full force, two compile 1:1, one feeds an existing
mechanism, two drop because the machine solved their problem a different way, one is an
accepted loss.

---

## 3. WHAT SURVIVES WHOLE (the zero-cost list — this is most of LEGO)

- **Step 0, PACKAGE FIRST — now with the topic gate.** Title + thumbnail + winnability +
  *"could someone who has never heard of the Book of Enoch want this?"* before a beat
  exists. Un-packageable → killed at $0. `package.md` directly populates `thumb.json`
  (including the `subject` key `--plan` won't catch if missing — §5.9) and the metadata.
- **Step 1, ARCHITECT.** Subject ledger (subjects allocated to one block, spent =
  forbidden), scale budget (no 5s early), visual budget (spectacle share on the token
  list), ten-frames test, spine object, named antagonist, refrain. Scored ≥70 before
  authoring — the Methuselah lesson, applied to every Line B script.
- **Step 2 craft, entire.** Variety law, light-per-beat, positive statements, canon
  tokens (defined once in the project `canon.json`, expanded at compile), token
  craft (Balrog principle, glory-as-substance, location-scout read), tight-first word
  counts, prosody, THE OPENING LAW.
- **Step 3, INTERROGATE AS DATA.** The three dials, verb histogram, noun-palette,
  human-absent runs, near-duplicate Jaccard scan — all pure-stdlib reads of the CSV,
  all before any spend. This is `audit_script.py` and it is the instrument that did not
  exist when 40 lore videos shipped.
- **The cold open — folded INTO the script.** No separate `coldopen.mp3` on this path:
  the first ~10 beats ARE the cold open, authored under the full spec (the drop, the
  name, the question, the handoff; one moment, never a trailer; the last cold-open line
  grammatically requires the next beat). The seam's music rule is already how
  `assemble_episode.py` behaves — one continuous crossfaded bed. This attacks the
  channel's ONE measured retention weakness (0.22–0.36 relative first minute) on every
  batch video, not just features.
- **The Kling plan as craft.** Heroes and motion-want beats first, run-breaking over
  next-highest-score, front-load the gate the viewer must survive.
- **Probe — as a throwaway mini-project.** Compile a 10-beat probe pair, run it through
  the machine itself (`run_batch --plan` → `--limit 1`, stop at the stills gate), eyeball,
  delete. Same engine, same model, same suffix as the real render — which makes it a
  BETTER probe than LEGO's own (no flux-vs-nano-banana register mismatch). Zero code.

## 3b. WHAT BREAKS — and why each loss is acceptable

| lost | why it doesn't hurt Line B |
|---|---|
| **The 4-variant grid + human pick** | The pick is LEGO's creative act and its cost driver (2–4× stills). Line B's economics are one still per beat; the existing **stills-review gate** (eyeball before animation spend, never skip) catches spell-breakers, and a re-roll is $0.08. The pick stays gospel on Line F where the film earns it. |
| **Container-fill / calibrate / the 200s grid** | Solves Filmora hand-alignment. PIPELINE aligns by whisper with VO deliberately loosely coupled — the problem doesn't exist here. Word discipline survives; the convergence loop doesn't need to. |
| **Per-beat KB `move` direction** | Pipeline KB varies itself. Marginal craft loss on free-floor beats; the fx layer (§6) is the better upgrade for the same beats anyway. |
| **`verify_clips` / 5.000s trim** | Engine-internal to LEGO's path; pipeline has its own assembly and gates. |
| **Filmora** | That's the point. |

---

## 4. THE LINE B RUN OF SHOW (steps, renumbered)

```
0  PACKAGE   package.md + thumb.json + title      gate: universal test + winnability + tile at 120px
1  ARCHITECT architecture.md: ledger/scale/visual gate: arch ≥ 70, spectacle ≥ 30%, ten-frames
2  AUTHOR    master.csv, block by block, in chat  gate: per-block drafting checks (contract 1A passes)
3  AUDIT     audit_script.py on the CSV           gate: three dials + variety + duplicates + 55w + topic mix
4  COMPILE   csv2script.py → <n>.md + <n>.thumb.json + kling plan
5  MACHINE-GATE  check_script.py on the COMPILED .md   (the gate of record — parser's own block model)
6  PROBE     10-beat throwaway pair → run_batch --limit 1 → stills gate → delete
7  INBOX     pair → batch_inbox; slug rules; three-gate pre-flight + create_project verify (§5.9)
8  BATCH     run_all_batches / run_batch — UNTOUCHED, UNATTENDED
9  OBSERVE   ledger row at ship (topic_class, line, length, title shape);
             weekly Studio CTR read; fortnightly cohort read; observations fed to Step 0
```

Steps 0–4 are laptop text work. Step 5 is the existing gate. Steps 7–8 are the existing
machine, byte-for-byte. Nothing in the working batch-of-batches path is edited, patched,
or debugged.

---

## 5. THE TWO NEW TOOLS (standalone; never import the engine)

**`audit_script.py`** — read-only. Input: `master.csv` (+ `canon.json`, `architecture.md`).
Prints: three dials (novelty per block, span per subject, escalation curve) · spectacle
share vs the ≥30% gate · verb histogram (top-3 <30%) · noun-palette coverage ·
longest human-absent run (≤5) · near-duplicate pairs (Jaccard ≥0.42, judged not
mass-fixed) · word histogram + 55w violations using the parser's counting rules ·
hero density per block · topic_class composition vs the 70% floor · pre-spend bill of
materials. Exit non-zero on any hard gate so it can sit in a shell chain.

**`csv2script.py`** — deterministic compiler. Reads `master.csv` + `canon.json` +
`package.md`. Writes the `<n>.md` (header from channel + package; beats in parser block
form — narration, blank-line-free `VISUAL:`, `MOTION:` on kling rows; tokens expanded;
ASCII normalised), the `<n>.thumb.json` (subject key populated — the `--plan` blind spot),
and the kling plan for the floor-first override. Hard-fails on: kling row with blank
motion · unresolved token · 55w breach · slug violation (`^[a-z0-9][a-z0-9-]{0,60}$`) ·
non-ASCII. Idempotent: same CSV in, byte-identical pair out.

Both live in `shared/`, both are `patch_*.py`-delivered like everything else, neither
touches a line of existing code.

---

## 6. THE CHANGE BUDGET — max three, ranked, and when to spend them

1. **NOW: nothing.** The bridge ships on the two standalone tools alone. This is the
   proposal's core claim and it should be defended against scope creep.
2. **NEXT (the one sanctioned engine touch): the ambient fx layer.** Additive inside the
   KB clip step; reads the `fx` column via the compiled pair (or sidecar); inert when the
   column is absent, so every existing script behaves identically. Grain + Artlist
   overlays first. This upgrades the ~80%+ of every Line B video that is free floor —
   the highest quality-per-dollar item on the visual backlog — and it is guarded by
   column-presence, which is the same off-by-default pattern floor-first used.
3. **DELIBERATE-LATER (only if stills-gate data demands): hero 2-variant.** Render 2
   stills on `weight=hero` beats, pick on the existing stills-review page. +$0.08 ×
   hero count (~$2–3 on a 125-beat video) for the pick where it matters. Build it when
   the stills gate shows hero beats failing at a rate that costs re-renders — not for
   taste.

---

## 7. COST MODEL (Line B, the proven-ticket shape: 35 min question-essay)

~5,600 words at measured ~160 WPM ≈ **~125 beats** at tight-first ~45w/beat.

| leg | count | unit | cost |
|---|---|---|---|
| stills | 125 | ~$0.08 | ~$10 |
| Kling (override plan) | 10–15 beats | $0.42 | $4–6 |
| TTS + whisper | — | — | ~$1 |
| fx layer (when built) | any | $0 | $0 |
| **total** | | | **~$15–17** |

Against ~$100–160 + multiple sessions for a Line F feature. Ten Line B draws per feature-
equivalent spend, each carrying the full authoring instrument, each attacking the proven
ticket shape, each uploaded and scheduled by the machine.

---

## 8. RISKS AND GUARDS

- **The compiler must never outrank the gate of record.** `check_script.py` runs on the
  COMPILED .md; if compiler and parser ever disagree, the parser wins and the compiler is
  fixed. Same principle as laptop/box gate agreement.
- **Blind spots stay blind:** `--plan` misses thumb.json schema errors, `no_visual`
  beats and slug traps — the compiler hard-fails all three earlier, but the §5.9
  three-gate + verify pre-flight still runs. Belt and braces.
- **Token expansion is compile-time**, so a canon edit requires re-compile (one command).
  Acceptable: Line B scripts are one-shot.
- **Manual Studio boundary unchanged:** AI-content flag, per-video review before slots —
  nothing publishes that a human didn't see.
- **Reconciliation law applies:** this doc is additive and forward-only. Line F keeps the
  full LEGO 0–10 including the pick and Filmora; nothing here rolls that back.

---

*The one-line summary: LEGO taught the operation how to DECIDE what a film shows before
paying for it. PIPELINE knows how to BUILD and SHIP it unattended. The bridge is a
compiler between two file formats — the instrument keeps its full authority, the machine
keeps its perfect record of not being touched.*
