# _BRIEFCASE-INSTRUCTIONS.md — HOW TO OPERATE (v2 era)
### The contract in one line: **the process is entirely Claude's; Peter runs the laptop and the box, and reviews the finished video in Studio — his taste feedback feeds the NEXT video at scripting stage.**
### Load order every fresh session: _CANONICAL.md → __MASTER-WORKLOG.md → v2-PLUMBING.md → this file → per-channel doctrine doc when the task needs it.

---

## 0. ROLES (Law 15, restated for the v2 era)

**Claude owns end-to-end:** topic development within the slate → RIVER → CHOP →
gates → src set → handoff commands → (Peter executes) → next-video incorporation of
Studio feedback. Claude reads real code before proposing changes, runs every gate
for real, and never asks Peter an infrastructure question the briefcase answers.

**Peter owns:** the topic slate + creative/quality judgment calls flagged inline;
physically executing LAPTOP/BOX command blocks (sessions have no SSH — the handoff
IS the interface); watching finished videos in Studio and giving taste verdicts;
publish scheduling. Peter does NOT review anything between launch and Studio.

**Handoff packaging (Law 15's correction, permanent):** once gates are green, the
session's turn ends with ONE message containing the complete remaining command
sequence — LAPTOP scp, BOX ingest, BOX run — launch riding in the SAME message,
with "stop and paste back only if X looks wrong" phrasing. Never dribble commands
across turns.

## 1. THE PROCESS, STEP BY STEP (v2 project, feature-length)

**STEP 0 — PACKAGE (inline, sign-off gated).** Read the slate entry. State the
package: title, angle, spectacle inventory FROM THE SOURCE (hard rule — inventory
before beats), cold-open concept checked against the Opening Signature Ledger,
BOM estimate (beats × $0.08 + kling × $0.42 + ~$1; $25 default / $30 flagged
override), runtime target (words ÷ 165 = minutes; 70 min ≈ 11,500 words; note
Elliot measured ≈150 wpm on the teaser register — plan margin).

**STEP 1 — ARCHITECT (inline).** Acts (≤12; teaching content clusters into ≤6),
token list WITH archetype tags (Law 22: spanning rule ≥3 composition classes per
token; names `[a-z_]+` only, Law 20), the three dials (novelty ≥2/block — currently
under-hit, address deliberately; span ≤0.35; escalation rising — currently
unenforced, design it in), kling plan (front-N Law 8, OR — once the authored `kling` column lands — placement-by-value per Law 28e: first-10-min saturation, act-opener pairs, hero miracles, probe reserve), **the REGISTER MAP (Law 28d: which sequences carry dream/vision transformation license; everything else is witness grammar)**, scale plan (cold open =
its own zone, Law 17), thumbnail-payoff plan (Law 18: beat 1 IS the thumbnail
image). If creative license wanted: invoke the DREAM LICENSE (Law 24) explicitly.

**STEP 2 — RIVER (Pass 1).** Pure continuous prose, no CSV thinking, permission-
slip length. Act headers as `## `-headings (mandatory — chop derives blocks from
them, even for shorts, Law 27). Craft voices per §3 of CANONICAL. Colon discipline:
never `move:`/`visual:`/`motion:` mid-prose (Law 25). ASCII-safe names (no macrons).
Pauses per the PAUSE DOCTRINE. READ pass (2.5) before chopping: opener variety,
crutch phrases, rhythm.

**STEP 3 — CHOP + GATE LOOP (mechanical, run everything for real).**
`chop_river.py <river> <config> --out master.csv` — the config carries routes,
variants (spanning rule), archetypes + cap, kling_count + motion prompts,
scale/scale5 rules, force_reassign. Then in order, fixing at SOURCE each time:
(a) negation grep on the config (`\b(no|not|never|without|cannot) `— variants/canon
only; route regexes may match river negations); (b) chop's own archetype report;
(c) Law-21 bare-split scan (any beat >55 by `len(narration.split())`); (d) empty-
narration + tag-word scan (Law 25) until the tools carry it;  (g) **motion-prompt grammar scan (Law 28)**: every kling motion prompt checked — continuous phenomena only, no contact verbs (jumps/cracks/explodes/slides/bursts/shatters/strikes), witness prompts carry the physics anchor, contact events authored as cut-pairs; (e) `audit_script.py
--csv master.csv --canon canon.json` to ALL HARD GATES PASS; (f) `intake.py . 
--channel <ch> --bom-ceiling <n>` to GREEN. Boundary discipline: block N's last
route token ≠ block N+1's first, on all three axes (tableau/shot-dist/human) —
the counters reset per block.

**STEP 4 — SRC SET.** `<slug>-src/`: master.csv, canon.json, chop-config.json,
sections.json (block "0" EXACTLY "COLD OPEN"), desc.txt, thumbsubject.txt,
river-draft.md (for the record). **v2: NO csv2script, NO parse_script — the set
goes straight through the door.** (v1 legacy projects only: compile + parse per
the old contract.)

**STEP 5 — HANDOFF (one message).** LAPTOP: scp the src dir to `Pipeline/`.
BOX (one block): pull, venv, `.env` (`set -a; source .env; set +a`), music copy
into `<project>/music/`, then:
```
cd shared/v2
python ingest.py --src ~/Pipeline/<slug>-src --db ~/Pipeline/<channel>/projects/<slug>/<slug>.db --slug <slug> --channel <channel> --title "..." --tags "..."
python render.py --project ~/Pipeline/<channel>/projects/<slug> --stage audio
python render.py --project ~/Pipeline/<channel>/projects/<slug> --stage measure
python render.py --project ~/Pipeline/<channel>/projects/<slug> --status
```
Checkpoint line: "expect N beats / measure N/N / coverage ≥90; optionally play
voiceover.mp3; then:" —
```
tmux new-session -d -s <slug>1 "cd ~/Pipeline/shared/v2 && source ~/venvs/pipeline/bin/activate && set -a && source ~/Pipeline/.env && set +a && python render.py --project ~/Pipeline/<channel>/projects/<slug> > ~/Pipeline/<slug>1.log 2>&1"
```
Upload lands PRIVATE. Scheduling: `python upload.py --project ... --publish-at
<RFC3339 UTC>` (or Studio by hand). Long jobs ALWAYS in tmux; only one ffmpeg-heavy
render at a time; API-bound stages coexist fine.

**STEP 6 — STUDIO (Peter).** Watch. Verdict in plain language. Claude converts the
verdict SAME SESSION into: a named law with a receipt (CANONICAL §2), a tool change
where mechanical (rules are checked mechanically or not checked, Law 9), and the
next spoke's Step-1 constraints. That conversion is the flywheel; an unbanked
verdict is a verdict paid for twice.

## 2. THE MEASURES (compute per film, report in handoff or on request)
BOM ($); runtime (words÷165, note real-pace calibration); archetype entropy +
top-share vs 25% cap; token top-share vs 15%; longest runs (token ≤6 / archetype /
dist <3 / move ≤3); move mix (25×4); novelty/block + escalation (the two open
dials); phenomenon uniqueness; post-render from the DB: coverage, floors, fit-label
histogram (`generations`), cost by stage (SUM(cost)).

## 3. STANDING DISCIPLINE (unchanged, load-bearing)
Read real code before proposing changes — grep signatures; never guess CLI flags
(the session's one violation this era was assuming a stale constant; the fix was
grepping the live file). Patches = idempotent patch_*.py (anchor-verify, .pre_
backup, py_compile, ASCII). Named-path git only; pull --no-edit before push;
verify on box after pull. Config changes via python one-liners. BOX/LAPTOP labels
in prose before every block; no comments inside blocks. One step at a time on
multi-step work; full paste-blocks, never snippets. Fix at SOURCE, then regenerate —
never hand-edit downstream artifacts (.md, .db). Never restart Mission Control
mid-render (v1 only; v2 has no daemon). The .db is gitignored; media travels rsync.

## 4. WHAT A SESSION MUST NEVER DO
Invent tools/sidecars; hand-author machine formats; hand-edit a .db; relitigate
settled laws (front-N, never-stretch, river-first); silently exceed the BOM
ceiling; end a gate-green session without the complete handoff block; leave a
Studio verdict or a box failure unbanked.
