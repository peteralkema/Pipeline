# _CANONICAL.md — YOUTUBE MEDIA FLYWHEEL · THE ONE DOC
**v3 · 26 Jul 2026.** This document REPLACES `_STRATEGY.md`, `_BRIDGE.md`, `_MOTION-DOCTRINE.md`, and the doctrine portions of `_LEGO.md` — all folded here. The briefcase is now exactly: **this file + the two channel doctrine docs (slates baked in) + the code files listed in §1.** `__MASTER-WORKLOG.md` stays separate as history, loaded on demand. If any other doc contradicts this one, this one wins.

---

## 0. THESIS
One channel-agnostic Python pipeline turns a beat CSV into a finished narrated, scored, packaged video. The production system is the moat; the discipline of banking failures as tool-agnostic laws is the deeper moat. **A video design is PURELY DATA** — one row per beat, every decision a column; the code stays dumb and reads columns. Proven twice on 26 Jul with two fresh-session authored videos through the full gate chain.

Portfolio thesis (banked 26 Jul): the flywheel is **universal-question-answering-from-lore** — one engine, N single-lore channels, one question ledger reused across all. Never multi-lore in one channel: congregation coherence is the asset. Nouns deplete; felt questions refill (`lane lifespan = S-tier subject ledger ÷ upload rate`). Slot #1 = Scripture On Screen teaching pivot; it validates the template for every future slot.

---

## 1. TOOLS MANIFEST (live, load-bearing — `--help` these; NEVER write a reconstruction)
A fresh session MUST list the briefcase for `.py` files before writing any code. **Writing your own version of any tool below is a defect, not initiative.** Real CLI signatures as read from source:

| file | role | signature (verified) |
|---|---|---|
| `audit_script.py` | **Gate 1 — the CSV gate.** Mechanical audit of `master.csv` before compile | `python audit_script.py <master.csv>` (defaults: `--max-words 55`, `--kling-words 18`) |
| `csv2script.py` | **Compiler.** CSV + canon.json + sections/desc/thumbsubject → `<slug>.md` + `.thumb.json` | run `--help`; consumes the `-src/` folder inputs |
| `parse_script.py` | **Gate 2 — gate of record.** Parses the compiled `.md` | `python parse_script.py <script.md> [--json X] [--json-full X]` |
| `run_batch.py` | **Step 8 runner** (box: `shared/run_batch.py`) | `--inbox <dir of pairs> --channel <dir> --kling-count N [--plan] [--limit] [--publish-start ISO+tz] [--publish-interval-hours H]` |
| `build_lego.py` | authoring verbs (box) | `--help` on box |
| `recreation_pipeline` legs | re-render EXISTING projects (`stills`, `finish`) | box only; `run_batch` is for NEW projects only (exists-guard refuses existing) |
| `draft_moves.py` | fills the `move` column by the motion doctrine (§6) | box; CSV-side |
| `kenburns --move` | permanent per-move geometry test rig | box |
| `intake.py` | **the authoring gate** — runs IN the authoring session (pure text; no box). Completeness + tokens + audit_script + strips strays; `--admit` adds ledger/judgment flags | `python3 intake.py <dir-or-zip> --channel <underscore_form> [--admit --ledger <doctrine.md>]` |

`orchestrate.py` is engine-side; sessions never touch it. **Settled 26 Jul:** `run_batch` writes `render_policy.json` with `kling_count` = **contiguous front-N, which is the mechanism that decides animation**. Scattered per-beat `MOTION:` lines outside the front-N are inert (harmless, wasted authoring). Do not relitigate Law 8.

---

## 2. THE LAWS (each with its receipt)
1. **Runtime law:** `words ÷ 165 wpm = minutes`. (Chambers ratio was ~3× wrong; 70 min needs ~11,500 words.)
2. **Beat-length band:** target **15–25 words/beat** (verified: 19.1 avg passed everything, Sacred 26 Jul). Kling beats **≤18 words** (freeze-tail; enforced by `audit_script --kling-words`). The golden pair's ~45 w/beat is a valid *alternate register*, not the default.
3. **Cost ceiling law:** **$25 max per Line B video.** Bill of materials: `beats × $0.08 + kling_beats × $0.42 + ~$1 flat (TTS/whisper)`. Compute it at Step 1 and again after any beat-count change. Both 26 Jul videos: ~$24.1 and ~$24.6.
4. **ROMAN ceiling:** csv2script crashes above 12 acts. Teaching videos cluster lessons into ≤6 thematic acts, never one-act-per-lesson.
5. **Law 8 — Kling is contiguous front-N** via `--kling-count` at render; pipeline extends clips to narration length (no freeze-tail). The `move` column is universal (both lines — mechanism-agnostic directorial intent). Settled; see §1.
6. **Canon fixes require RECOMPILE**, not re-render — tokens expand into VISUALs at compile time.
7. **Directed Ken Burns floor is LIVE:** `move` column (push/pull/crane/settle/static) travels CSV → `MOVE:` line → `Beat.move` → floor call-sites. Every beat gets a MOVE. `draft_moves.py` fills it; the doctrine is §6.
8. **Sidechain ducking is LIVE** (assemble): voice ducks music ~8–10 dB; music baseline 0.11.
9. **Subject ledger / scale budget / three dials** (novelty ≥2 per block, span ≤0.35, escalation rising) are Step 1/3 forcing functions. Stating a rule in prose does not prevent violating it — **rules are checked mechanically or they are not checked** (receipt: 15 scale-5 violations authored by the same session that wrote the rule correctly in prose, 26 Jul).
10. **Ledger law (26 Jul):** lane lifespan = S-tier subject ledger ÷ upload rate. Nouns deplete, questions refill. Slates spread across DISTINCT S-tier pains; check every new title against the channel's shipped ledger for pool-overlap before authoring (receipt: slate #1 vs chambers overlap caught only because the worklog was loaded).
11. **Tank law:** a new/relaunched channel dark-builds **≥25 videos** and drips daily; never trickle a slate out as it renders.
12. **Probe before spend** (~$1.60 buys rulebook negatives) — Line B at $25/video may skip the probe by explicit operator instruction only; skipping is Peter's call, never the session's.
13. **Attribution moat:** the text SAYS — we never assert. The frame flirts; the narration never claims.
14. **Distribution physics:** CTR + AVD in the first 48h drive everything; browse hits are front-loaded. Impression allocation is the real constraint below ~1K impressions.

---

## 3. THE AUTHORING CONTRACT (what a fresh session DELIVERS — the anti-variance spec)
Two independent sessions given the same briefcase produced divergent outputs on 26 Jul (one invented an audit tool; one invented a `kling.json` sidecar and skipped MOVE). Cause: doctrine without a deliverable contract. This section IS the contract; deviations are defects.

**Deliverable = the `-src/` authoring set, nothing else:**
```
<slug>-src/
  master.csv        # the heart — one row per beat, 15–25 w/beat
  canon.json        # every {token} used in the CSV MUST have an entry
  sections.json     # act structure for csv2script
  desc.txt          # video description
  thumbsubject.txt  # thumbnail subject prompt
out/<slug>.md + out/<slug>.thumb.json   # produced ONLY by the real csv2script.py
```
`package.md` and `architecture.md` content stays **inline in chat** (gated on Peter's sign-off), never filed.

**Definition of done:** `audit_script.py` ALL HARD GATES PASS on the CSV, then `csv2script.py` compiles clean, then `parse_script.py` exit 0 with beat counts matching and moves present = beats. The session's self-assessment is not a gate.

**Prohibitions (each one happened on 26 Jul):**
- NO new tools, no reconstructed auditors, no invented sidecar formats (`kling.json`, top-level `description.txt` — no consumer exists).
- NO touching `packaging/*`, no commits, no pushes — code transport is Peter's job.
- NO hand-authoring the compiled `.md` — it is the machine's output format.
- NO relitigating Law 8 / front-N; no guessing CLI signatures (read `--help` or the source).
- NO infrastructure questions to Peter that the briefcase answers; an unanswerable question is a defect report against this doc, filed in session notes.

**The two gate vocabularies are DIFFERENT INSTRUMENTS — never conflate:**
- *Step 1 architecture gates* (human-judged, inline): arch self-score, spectacle share, ten-frames test, subject ledger, scale budget, visual budget. These are judgment, applied before beats exist.
- *Step 3 `audit_script.py` gates* (mechanical, on the CSV): words ≤55 (band 15–25 by law), kling-words ≤18, unresolved tokens, novelty ≥2/block, topic-mix ≥70%, human-absent-run ≤5, verb top-3 ≤30%, render-safety word scan (e.g. "dying"/"blood" can silently trip the image safety classifier — reword when flagged), CSV integrity/quoting.
- *Visual-monotony gate* (intake, on the CSV — the "no 16 wheat fields" enforcement): flags any BARE token (a `{token}` that is the entire visual with no per-beat framing after it) and any run of ≥4 beats whose token-stripped visual text is identical/near-identical. Bare tokens and identical-visual runs are the die-video failure signature; caught here before spend, not after.

The write → machine-check → fix → present loop per authored chunk is the proven working pattern; run it every chunk. Craft laws that the checks serve: contents-not-containers; positive-statement-only visuals (no "no X" phenomenon language); one subject per beat; the spine object with the ten-frames test; cold open is the highest-leverage sixty seconds.

**VISUAL NOVELTY — the "no more 16 wheat fields" law (27 Jul).** Tokens and canon are valuable and lead to more sophisticated film production — a recurring named figure who holds identity across a slate, a location that recurs and should feel like the same place. Keep them. But we have a documented tendency: when we introduce a tool we over-correct and over-use it, and the failure mode is visual monotony. This law rebalances — moderation and fit-for-purpose, not prohibition.

THE FAILURE (real receipt, "What Happens When You Die", shipped 26 Jul): beats 10-25 — sixteen consecutive beats — each carried the bare token `{sower_field}` as the ENTIRE visual, so all sixteen compiled to the byte-identical prompt "a teacher standing among bending grain stalks at golden hour, small birds rising." The stills engine got one prompt sixteen times and produced a minute-plus of near-identical wheat fields. Worse, the token didn't even deliver the consistency it promised — backgrounds, tunic colour and light drifted anyway. A bare place-token repeated is monotony WITHOUT consistency. Same failure as Methuselah's "endless rocks on mountains."

THE RULE — **never a bare token; every beat carries its own distinct framing.** A `{token}` locks a place or a face; it does NOT author the shot. Each beat must add its own framing after the token — angle, distance, foreground, light. Compare:
- WRONG (what shipped): sixteen beats each = `{sower_field}` and nothing else.
- RIGHT (how our best authors already work — the "Forgive" prayer scene ran 20+ beats in one location and reads as a real scene because every beat differs): `{sower_field} wide, the teacher small against the grain` / `{sower_field} close on hands scattering seed onto the path` / `{sower_field} low angle, sparrows lifting off the furrow` / `{sower_field} the teacher's face turning toward the birds`. Same place, sixteen different frames.

This restores the original script-king craft: when a human writes a fresh framing per beat, visual variety comes for free — no writer describes the same field the same way sixteen times. Lean LESS on tokens than we have been; reach for a fresh full-written visual by default, and use a token when a place or face genuinely recurs and should stay consistent. The `move` column varies the camera, but a varied move over an identical still is still one shot — novelty must live in the still, beat by beat. Not outlawed, not orthodoxy: fit for purpose. No more 16 wheat fields.

This is a PREVENTION rule (author it right the first time), enforced mechanically by intake's bare-token / identical-visual-run gate (§3 gate list) so it is caught before spend, not fixed after.

**PAUSE DOCTRINE (breath — required authoring judgment, per video).** Elliot's pace is right, but the narration must be given space to breathe or it runs airless. Sprinkle Inworld SSML break tags throughout the script — `<break time="700ms" />` inside the narration column, at the natural resting points. This is a per-video judgment call on *placement*, but it is NOT optional to do: every script gets deliberate pausing. Range and placement heuristics (observed working, 26 Jul — ~60 breaks across ~158 beats is a healthy density): a beat of ~0.9–1.5s (900–1500ms) AFTER the title question or a hero line lands, to let it register; ~0.6–0.7s (600–700ms) at the turn between thoughts or before a reveal; ~0.4–0.5s (450–500ms) on quick connective beats. Longer holds pair naturally with `settle`/`static` moves and hush/awe registers; short breaths with `push`/`pull` momentum beats. Do not front-load all pauses into the cold open — distribute across the whole runtime so the teaching body breathes too. Breaks live in the narration text and are stripped before the word-count, so they cost nothing against the word band.

---

## 4. THE LINE B RUN OF SHOW (Bridge steps, with owners)
0. **PACKAGE** (session, inline): title from the channel slate, universal test, thumbnail subject/lockup, hook, tags. Gate: Peter's sign-off.
1. **ARCHITECT** (session, inline): container math from the runtime law + $25 BOM; blocks ≤12 acts (~6 for teaching); subject ledger + scale budget + visual budget; spine object + ten-frames test; check the slate title against the shipped ledger for pool overlap. Gate: Peter's sign-off.
2. **AUTHOR** the CSV chunk-by-chunk (a generator script for quoting safety is good practice), canon tokens defined AS USED, `move` on every beat, MOTION only on the front-N kling beats. Machine-check every chunk before presenting.
3. **AUDIT**: real `audit_script.py`, iterate to ALL HARD GATES PASS. (Its row reporting has a 0-index vs "row N" mismatch — verify fixes by re-running, never by eyeballing.)
4. **COMPILE**: real `csv2script.py` → pair.
5. **MACHINE GATE**: real `parse_script.py` exit 0, beats in = beats out, moves = beats.
6. **PROBE** (box, optional per law 12).
7. **INBOX**: pair → `<channel>/batch_inbox_<slug>/` on the box (scp from laptop; remote paths are relative to `~`, include `Pipeline/`; brace-globs don't expand over scp).
8. **BATCH** (box): `run_batch.py --plan` first, then real run in tmux, serial by priority, logs to repo root. Never restart Mission Control mid-render. After shipping, the pair moves to the inbox's `_shipped/`.
9. **OBSERVE**: per-channel observe loop (in the channel doctrine): 48h CTR+AVD read; `APV = watch-hours × 3600 ÷ views ÷ duration-seconds`; YouTube Studio CSV is authoritative (NexLev lags 2–3 days and is a floor, not a ceiling); bank the read in the worklog and the channel's shipped ledger.

---

## 5. ECONOMICS (reference shapes)
- Line B teaching/essay, ~17–18 min: 150–200 beats × $0.08 + 19–26 kling × $0.42 + $1 ≈ **$23–25**. Ceiling $25 (law 3).
- Golden-pair register (~45 w/beat) ≈ $32/hour of runtime; LEGO 13.5 w ≈ $104/hour — words-per-beat, not minutes, decides cost.
- VO convergence: Whisper calibration forces ~5s clips; tolerate extended clips as needed and KB the rest. Container-fill to zero drift.

---

## 6. MOTION DOCTRINE (folded whole — drives the `move` column and kling MOTION prompts)
**Motion is a function of the shot, not a choice.** Per beat, in order: force is vertical/rising → **crane**. One overwhelming subject → **push**. Meaning is scale/number/spread → **pull**. Quiet beat (grief, aftermath, held breath) → **settle** (slow exhale down) or **static/near-locked** (ambient only) — the quiet override BEATS the axis rule. Else → **push** (safe default).
Hard rules: one primary motion per beat; slow is fast; lock the subject, move the camera; **never push on silence**; motivated, never timer-driven; the still is locked first (composition can't drift — only the move is variable). Healthy full-film distribution: push ~25–30%, pull ~20%, crane ~20%, static ~15–20%, settle ~10–15%; max same-move run ≤2–3. Rotation comes free from the shots' own variety.

---

## 7. INFRASTRUCTURE & DISCIPLINE
- BOX `peter@pipeline-prod` 116.202.18.68, SSH port 443, `~/Pipeline`, venv `~/venvs/pipeline` (`python`). LAPTOP `~/Projects/Pipeline`, macOS (`python3`). GitHub `peteralkema/Pipeline` = sole code transport; media by rsync/scp, gitignored.
- Never hand-edit the box. Patches = idempotent `patch_*.py` (anchor-verify, `.pre_` backup, `py_compile`, ASCII). Config via `python3 -c` one-liners. Named-path git only; `git pull --no-edit` before push. Long jobs in tmux. Command blocks labeled BOX/LAPTOP in prose, no comments inside blocks.
- Mission Control :8002 (`mission-control.service`, user systemd) — never restart mid-render (cgroup teardown kills in-flight legs). Orphan port: stop + `pkill -f pipeline_server.py` + start, confirm Main PID changed.
- Plumbing gotchas: `parse_script --json-full` emits `visual`/`motion`, engine `cmd_stills` wants `image_prompt`/`motion_prompt` (run_batch converts; direct legs do NOT). Direct `stills` writes `<project>/stills/` (finish reads it correctly). `select_thumbnail_still` errors every run — ignore; thumbnails are hand-made. `git add -A` is forbidden (sweeps render outputs). fal stills REQUIRE `safety_tolerance:"5"` or silent black PNG.

---

## 8. FRESH-SESSION PROTOCOL
1. Load: `_CANONICAL.md` (this) + the ONE channel doctrine for the session's channel (slate + observe loop live inside it). Worklog on demand for state questions.
2. List the briefcase for code files FIRST; `--help` before use; never reconstruct.
3. Confirm with Peter: channel, slate number(s), skip-probe yes/no, publish schedule. Then execute §3/§4 with the chunk-check loop. One step at a time; full paste-blocks; terse.
4. **BEFORE HANDOVER — run the gate until GREEN.** `python3 intake.py <your -src dir> --channel <underscore_form>` in this session's own container. Fix every listed defect and re-run until it prints GREEN. The §3 prohibitions (complete set, resolving tokens, no stray sidecars, move column, front-N kling, BOM ceiling) are enforced by this gate, not by memory — a fresh session skimming prose on a phone will miss them, so the gate is the enforcement. GREEN is sufficient quality control; the handover zip does NOT get re-gated at the batch boundary. Only then produce the handover zip (the -src set + the compiled pair).
5. End of session: session notes in the defect-report format (what shipped, chronology warts included, fixes caught, briefcase defects found, open items).
6. Target state: **multiple CSVs per session** — one Claude per channel, several slate titles per sitting, each delivered as a complete `-src/` set in outputs.
7. Next horizon (not yet built): a "batch operator" Claude whose whole job is §4 steps 7–9 — take finished pairs, seat inboxes, drive `run_batch` through to Studio.

## 9. CHANGE BUDGET
Max three engine changes per campaign, ranked, spent only on what strengthens the production system + packaging layer. Everything else is authoring-side (free) or rejected. Current queue: fx uniform grain (inert default, channel-config strength, no mapping), channel-agnostic upload step with batch exit-gate, make_shorts.py.
