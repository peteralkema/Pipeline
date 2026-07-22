# _LEGO-FLAGS.md — banked findings for merge into `_LEGO.md`

*Opened 22 Jul 2026 during the Methuselah build (Sacred Dawn, 12 blocks / 480 beats).
Each flag names the section of `_LEGO.md` it belongs in. Merge and delete — this file is a
staging area, not a permanent document.*

**Status key:** `OPEN` needs a doc edit · `RESOLVED` examined and no change needed ·
`BANKED` real solution, deliberately not built yet.

---

## Process gaps — THE PROCESS 0 to 9

### 01 — Step 0 must write `package.md` · OPEN
Step 0's stated output is "a decision to build," which lives in chat and is gone next session.
**Fix:** Step 0 writes `<project>/package.md` — title, thumbnail concept, both winnability verdicts
*with the evidence*, render-safety flags, truth ledger, metadata. See the Methuselah file for shape.

### 02 — Step 1 must write `architecture.md` · OPEN
Step 1's gate is "block plan exists." Exists *where*? **Fix:** Step 1 writes
`<project>/architecture.md` — block roles, gaps, handoffs, token sets, spine object, loop stack,
per-block wet budget, and the dated chronology (see flag 16).

The doc already diagnoses this failure — *"feels like from-scratch every session is the signature of
a rule that lives only in conversation"* — and then commits it in its own first two steps.

### 03 — block CSVs to disk · OPEN
Step 2 keeps per-block CSVs in chat by design. Eight to twelve blocks × 40 rows is too much state to
hold in a conversation, and it makes authoring non-resumable. **Fix:** write `blocks/bNN.csv`, merge
from disk at Step 3. The stated reason (folder clutter) is much cheaper than the cost it buys.

### 04 — the cold open is a step, not a parenthetical · OPEN — highest value
Currently one clause inside the Filmora line at Step 9: *"cold-open cut LAST from the best clip of
each block."* **That instruction is the trailer error and it is measurably costing retention.**

Sacred Dawn evidence, two films, both curves:
- *Forbidden Books* (76:10): 93.5% at 46s → **60.7% at 91s**
- *200 Taught Us* (37:30): 97.8% at 22s → **54.8% at 45s → 35.9% at 67s**
- Relative retention in that window: **0.22–0.36** (bottom decile) against **0.58–0.75** mid-film

The collapse lands where the cold open *ends*. Viewers survive the trailer and bail at the handoff
into block 1. **Fix:** a numbered step with its own narration file, its own render, its own gate and
a seam check. Full spec in `architecture.md` — the drop / the name / the question / the handoff, plus
the seam mechanics (VO ends before the cut, music carries unresolved, no fade, match on movement).

### 05 — nothing produces the thumbnail · OPEN
Step 0 commits a *concept*. No step makes the file. On a channel whose declared moat is packaging,
thumbnail production is absent from the pipeline.

### 11 — Step 9 measures nothing · OPEN
*"Read CTR+AVD @48h, day-14/21; bank every failure as portable law"* — no file, no format, no script.
The FILM RECORD table has nothing writing into it, which is why WITW's row is all *(pending)*.
**Fix:** an observation artifact plus the retention-join script. Because the container is arithmetic,
beat *i* of block *N* spans `((N−1)×200)+((i−1)×5)` seconds — a retention curve joins onto the beat
rows with no estimation. STORY ARC calls this "the unlock" and lists it under FUTURE. Build it.

---

## Craft law — AUTHORING CRAFT

### 07 — the spine object · OPEN
The single recurring **physical** thing that carries a film and pays off at the climax. The
competitor's entire 698K-view film is one (a watch-fire, extinguished by one raindrop at 68:00);
Methuselah's is the marked stones. Nothing in the craft law names the device.

**Selection rule discovered:** prefer a spine object that **escalates visually**. A fire looks
identical at year 100 and year 900; a stone field does not, and becomes the film's escalation meter.

### 08 — the refrain · OPEN
A repeated line whose meaning changes because circumstances moved underneath it. Competitor recurs
theirs at ~2:00 / 11:00 / 28:00 / 64:00. Cheap, powerful, absent from the doc. Applies to numbers as
well as lines — *two hundred* recurs three times in Methuselah block 4.

### 09 — the named antagonist · OPEN
The competitor has none; the world is the villain, which is diffuse, and their film sags for twelve
minutes. A named opponent recurring across the film is the fix, and it should be a gate question at
Step 1: *who opposes the protagonist by name, and in which blocks does he appear?*

### 10 — the dialogue gap, quantified · OPEN
SCOPE already flags single-narrator VO as a constraint. The winning film in our lane uses two-hander
dialogue heavily throughout. That is no longer a scope note, it is a **measured competitive cost**.
Add a line on how narration compensates — reported speech, the witness voice — until it is solved.

### 06 — narration WPM · RESOLVED, no change
The competitor runs 7,285 words over 4,281s = **102 WPM** against Elliot's measured ~160. I argued
for slowing the body and was wrong: Sacred Dawn's own curves show dense narration costs nothing after
the open (*Forbidden Books* holds 35%→13% across 90% of runtime at 161 WPM, relative retention
0.70–0.75 mid-film). Inferring a pacing conclusion from a competitor's production figure with no
retention curve attached fails the two-independent-signals rule.

**Standing position:** author at measured WPM under container-fill. Breath in the first 90 seconds is
hand-placed in the cold open, which is a separately assembled artifact anyway — no contamination of
the repeatable path. Revisit only if a curve shows mid-film decay correlating with word density.

### 12 — silence is assembled, never spoken · BANKED, not built
No TTS platform gives a reliable pause instruction. **Stop asking for one.** Make `sentence_id` the
TTS render unit — one call per group, N files back — then concatenate with ffmpeg-generated silence
at exact durations.

Because the container is arithmetic, the gap is *subtracted, not estimated*: a group spanning beats
12–14 owns 15.000s; render it at 12.4s and the gap is 2.6s. **Cumulative drift is zero on the first
pass, always** — which collapses Steps 4–5 entirely and turns `calibrate` into a verifier that should
print zeros. Two columns: `pause_after` (authored override) and `pause_mode` (`grid` | `tight`).

Free consequences: hash-cache each group so an enrichment pass re-renders thirty utterances, not the
film; and emit `timing.json` (utterance boundaries, gap positions, block seams in absolute seconds)
as a music cue sheet and a direct feed to flag 11.

Two hazards: separate calls break prosodic continuity across a split, so group 2–4 sentences where
the voice must run on; and uniform auto-fill is the §0 blanket, so expect roughly half of groups to
run `tight`. **Build when there is a measured reason, not an aesthetic one.**

---

## Visual and packaging

### 13 — contrast, not brightness · OPEN (edit `_Sacred-Dawn.md` §1)
The bright-crisp-real law is right about sharpness and murk and **wrong about global luminance.**
Restate as: *one brilliantly lit subject against maximum tonal contrast.* A dark ground is permitted
and at 120px is usually better — a bright subject on a bright ground means nothing dominates.

Two signals agree: the competitor's near-black Methuselah tile (698K in 11 days) and Sacred Dawn's own
bright-busy thumbnails sitting in the 5-to-40-view tail.

**Sub-findings from the Methuselah render run:**
- **Palette is a re-roll lottery, not a dial.** On cracked-stone-face-on-black the model ignored
  temperature clauses in *both* directions. Re-roll and pick; do not rewrite the clause.
- **Listing forbidden injuries trips the safety classifier at the prompt door.** Naming
  wounds/blood/burns/rot/skull-like in a FIGURE RULE caused a content-policy refusal. Same
  state-the-positive law as the phenomenon cells, one layer earlier.
- **"Cracked plates" pulls toward scales.** Write *strata* and *slabs*.

### 15 — air is authored at Step 2, confirmed at Step 7 · OPEN
The doc has `air` one-way: read off the picked frame, never chosen. Correct at pick time — but it
makes the film's entire Kling bill an emergent property of writing nobody was told to control.

**Fix:** declare a per-block wet budget at Step 1; author phenomena to it; `air` at Step 7 confirms
rather than decides. The tell is in the light clause — *"hard sunlight across the stone"* is dry,
*"shafts of light through dust"* is wet. Same light, but the dust commits the beat to Kling.

**Note the cost model:** `air` drives **clip** spend only. Still spend is fixed by `weight`
(hero 4 variants / connective 2) and is unchanged by air — every beat needs a picked still whether it
animates or not.

Methuselah result: ~108 Kling of 480 (22%), two-thirds weighted into the first half.

### 14 — the "grave" collision · OPEN
`grave` is on Sacred Dawn's banned list as a *register adjective* and is also the ordinary English
noun for a burial place. `gate_canon` greps raw text and cannot disambiguate, so any burial beat
aborts. Either scope the ban to adjectival use or note the workaround (*a mound of turned earth*).
Hit in Methuselah blocks 2, 8 and 11.

---

## Canon technique

### 17 — a non-leading token is an identity lock · OPEN (additive)
`setting` derives from the **leading** `{token}` of `phenomenon`, so a token placed mid-cell rides
along without corrupting the derivation. `{firsthome}` leads (place); `{firstman}` sits inline
(identity). This is the cheap alternative to reference mode for a character appearing in one block —
a reference plate is overkill for nine beats.

### 18 — re-mint a token when the same place changes over time · OPEN (additive)
The summit in block 1 (`{highstone}`, bare rock) and the summit in block 8 (`{stonefield}`, covered
in hundreds of laid stones) are materially different locations. The doc's rule for canon
contradictions — mint a new token and retag rather than relax the shared one — applies to **time** as
well as content. On a film spanning centuries this is the normal case, not the exception.

---

## Step 1 discipline

### 16 — Step 1 must carry the chronology · OPEN
A block plan that assumes a time-shape the source contradicts is invisible until you are authoring
beat one. **Fix:** `architecture.md` carries a dated spine column alongside role/gap/handoff.

**Cost on this film: three separate catches.** The block-8 architecture assumed centuries between the
translation and Noah's birth when Genesis 5 gives sixty-nine years; a correction pass then introduced
a second error inside block 8; and block 11 twice mis-stated a family relation (Noah is Methuselah's
grandson, not great-grandson; Enoch is Noah's great-grandfather, not great-great). On a film whose
hook *is* the dates, a missed one is a permanent liability under the attribution moat.

---

## Merge order

1. **04** — the live retention bleed, and it is measurable.
2. **11** — the measurement artifact and retention-join; makes every later film cheaper to diagnose.
3. **01 / 02 / 16** — the Step 0–1 artifacts, chronology included.
4. **07 / 08 / 09** — the three craft-law additions.
5. **13 / 14 / 15 / 17 / 18** — visual, gate and canon corrections.
6. **05 / 03 / 10** — thumbnail step, block CSVs to disk, dialogue note.
7. **06** — record as resolved so it is not re-litigated. **12** — record as banked with its spec.

None of these touch `build_lego`. All are doc edits plus one small pure-stdlib script (flag 11).
