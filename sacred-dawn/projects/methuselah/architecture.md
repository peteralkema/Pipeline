# architecture.md — Sacred Dawn · project `methuselah`

*Step 1 artifact (LEGO flags 02 and 16). Written 22 Jul 2026. Blocks 1–12 authored against this
document; any change here after authoring requires re-gating the affected blocks.*

---

## SHAPE

**12 blocks × 40 beats × 5.000s = 2,400.000s (40:00)** plus a **55s cold open** = **40:55**.

Block N starts at `(N−1) × 200.000s` inside the body. Add 55.000s for absolute film time once the
cold open is laid in front. A retention timestamp therefore maps onto a beat row with no
estimation — beat *i* of block *N* spans `((N−1)×200) + ((i−1)×5)` to `+5` seconds.

**Runtime rationale.** Not 71 minutes. Longer runtime buys watch-hours, which is already the easier
YPP gate (291 days at current pace vs 570 for subs). Subs is binding and comes from views, which
come from packaging, not runtime. Twenty-one blocks would mean ~2,100 stills to hand-pick and the
pick is the one thing that cannot be automated. Fallback: 8 blocks. Stretch: 16, only if block 8
proves out.

---

## THE SPINE OBJECT — the marked stones

**One flat stone laid on the summit for every year he lives.** By the end there are nine hundred and
sixty-nine of them and the mountain has run out of room.

This is the film's single load-bearing invention and it was chosen deliberately over the
competitor's watch-fire. **A fire looks identical at year one hundred and year nine hundred; a stone
field escalates visually and countably.** It gives the film a built-in escalation meter the audience
can see rather than be told, and the final image writes itself: water closing over the field.

Escalation checkpoints: **10** (b1) → **300** (b8) → **360** (b8) → **849** (b11) → **969** (b12).

Two tokens carry it because the place changes materially over time: `{highstone}` is the bare summit;
`{stonefield}` is the same summit once it is covered. Minting a second token rather than relaxing the
first is the doctrine response to a canon contradiction, here applied to *time* rather than content.

## THE ANTAGONIST — Lamech of Cain's line

Genesis 4:23–24. The first recorded boast of murder, preserved in verse. His sons are Jubal (who
invented stringed instruments) and Tubal-Cain (instructor in bronze and iron). **One household
supplies both the weapons and the song.**

The structural payoff is the **two Lamechs**: Methuselah names his own son Lamech (Gen 5:25) long
before he ever hears the other Lamech speak, so the horror is retroactive. And the numbers rhyme in
the text — Cain's Lamech demands seventy-sevenfold; Seth's Lamech is given seven hundred and
seventy-seven years (Gen 5:31). This lands in block 7–8, exactly where the competitor's film goes
flat for twelve minutes.

Pre-loaded by the **two Enochs** in block 3: Cain's city is named Enoch (Gen 4:17) while Methuselah's
father is a different Enoch entirely. By the time the second name doubles, the audience has been
taught to notice.

---

## THE COLD OPEN — 55s, 11 clips, ~145 words

Its own narration file, its own Inworld render at the identical `voiceId`/`modelId` and speed, laid
in front in Filmora. **Not a trailer.** A trailer has its own arc, completes, and forces block 1 to
restart — that restart is the 45–90s seam where Sacred Dawn currently loses 30–40 points of
retention on every video (relative retention 0.22–0.36, bottom decile).

| window | move |
|---|---|
| 0:00–0:08 | **THE DROP** — open inside the moment. Hard cut in on the stone field and the number. |
| 0:08–0:20 | **THE NAME** — coordinates. Deliver the title's noun. Attribution lands here. |
| 0:20–0:40 | **THE QUESTION** — widen. Ask the thing the film exists to answer. |
| 0:40–0:55 | **THE HANDOFF** — one sentence that grammatically requires block 1 beat 1. |

**Seam mechanics (this is the actual repair):** VO ends 1.5–2s *before* the visual cut; block 1's
first line starts on or under the last cold-open frame. **One continuous music bed from 0:00 through
at least 2:00, unresolved under the handoff** — no crossfade, no new track at the cut. No fade to
black. Match on movement across the cut. Printed side by side, the last cold-open line and block 1
beat 1 must read as one paragraph.

Cut LAST, from picked clips, sourced from **one moment** in the late middle — not a survey of every
block, and never the film's final payoff shot.

---

## THE BLOCKS

Chronology column is Methuselah's age (flag 16). All ages from Genesis 5; see `package.md` for the
full ledger.

| # | title | M age | role | curiosity gap | handoff | tokens | wet |
|---|---|---|---|---|---|---|---|
| 1 | THE NAME | 0–10 | open on the object | if his death is the trigger, what is he *for*? | he is handed the count, untold what it counts | youngearth · village · highstone · hut | ~35% |
| 2 | THE FIRST MAN | ~40–243 | the relay begins | what is worth remembering for nine centuries? | smoke on the horizon that is not cooking smoke | firsthome · firstman · eden · youngearth · village · highstone | 18% |
| 3 | THE CITY OF CAIN | ~250 | the antagonist world | where did they *learn* this? | his father is awake, and has been dreaming | city · forge · youngearth · village · highstone | 45% |
| 4 | THE ONES WHO CAME DOWN | ~250 | the Watchers; spectacle 1 | what came of the mingling? | something enormous on the horizon | hermon · watchers · forge · youngearth · village · city · highstone | 28% |
| 5 | THE ONES THEY MADE | ~250–290 | the giants; spectacle 2 | does anyone up there see this? | the fire bends sideways with no wind | nephilim · youngearth · village · city · highstone | 30% |
| 6 | THE MAN WHO DID NOT DIE | 300 | the translation; spectacle 3, act-one peak | he inherits the vigil alone | footprints that stop where nothing stops | city · cave · lightcolumn · highstone · youngearth · village | 18% |
| 7 | LAMECH WHO BOASTED | 187 → later | **the antagonist block** | is there anyone left who will not? | he stops counting years, starts counting generations | city · forge · highstone · hut · youngearth · village | 10% |
| 8 | THE YEARS ALONE | 300–369 | the long time (retrospective) | is it worth witnessing for a world not watching? | a light in a house at night | stonefield · highstone · village · youngearth · city | 10% |
| 9 | THE CHILD WHO SHONE | 369 | the turn; hope enters | who *can* answer this? | only one man could, and he left | luminouschild · hut · village · stonefield · highstone · hermon · nephilim · cave · lightcolumn | 10% |
| 10 | THE FATHER RETURNS | 369 | spectacle 4; the answer | what is the boy *for*? | the command comes | lightcolumn · stonefield · luminouschild · highstone · hut · village · youngearth · city | 20% |
| 11 | THE HUNDRED AND TWENTY YEARS | 849–969 | the build; the world's answer | when does the clock run out? | the animals appear on the trails | ark · stonefield · youngearth · city · forge · village · cave · highstone | 8% |
| 12 | THE LAST STONE | 969 | payoff | — | out of the film | ark · flood · stonefield · highstone · youngearth · village · city · lightcolumn · firsthome | 30% |

**Block 7 sits in flashback deliberately.** Genesis 5:25 puts Lamech's birth at Methuselah 187 —
before block 6's translation at 300. Rather than reorder, the block steps back, which means the name
was innocent when given and became terrible afterwards. The Opening Law permits flashing back after
a peak, and block 6 is the peak.

**Block 8 is the film's structural risk** — the competitor lost twelve minutes here. Mitigations,
all executed: the stone field as visible escalation; exactly one full scene (the night he sits down
at the bottom of the path, beats 31–36); a human held in frame every three beats or fewer even in
pure sweep.

**Escalation ladder:** b3 → b4 → b5 rising on scale and danger; b6 drops deliberately to emotional
peak; b7 rises on human cost; b8 is the trough by design and is anchored on one scene; b9–b10 rise
on mystery and consequence; b11 on urgency; b12 pays off.

---

## OPEN-LOOP STACK

Never fewer than two live at once.

| loop | opened | closed |
|---|---|---|
| L1 — when he dies, the water comes | cold open / b1 | b12 |
| L2 — the promise of the one who crushes the serpent | b2 | b12 (deliberately unresolved — sequel) |
| L3 — where did the city learn metallurgy? | b3 | b4 b30 |
| L4 — what came of the mingling? | b4 | b5 |
| L5 — the two Lamechs | b3 (Enochs) → b7 | b8 b30 |
| L6 — what is the shining child? | b9 | b10 |
| L7 — a hundred and twenty years | b11 | b12 |

---

## AIR / WET BUDGET (flag 15)

`air` is **authored at Step 2 and confirmed at Step 7**, not discovered. A beat carrying visible
suspended matter — dust in a beam, smoke, embers, mist, sparks, spray, drifting cloth — is dead as a
still and commits to Kling; a beat naming the surface its light lands on runs free on the Ken Burns
floor.

Budget above, weighted about two-thirds into the first half on the retention argument. **Block 12 is
the honest exception** — water *is* visible air, and it pays off a forty-minute loop.

Measured across the authored film: **~108 Kling beats of 480 (22%)**. The other 372 run at $0.
Note `air` drives **clip** spend only; still spend is fixed by `weight` at 100 real stills per block.

---

## BILL OF MATERIALS

| | |
|---|---|
| beats | 480 (12 × 40) |
| narration | **6,626 words · 13.80 words/beat** (WITW shipped 13.5) |
| per-block words | 569 / 563 / 549 / 557 / 546 / 548 / 566 / 541 / 544 / 547 / 545 / 551 |
| weight | 120 hero + 360 connective |
| grid | 1,200 real stills × $0.08 = **$96.00** |
| clips | ~108 Kling + ~372 Ken Burns floor |
| canon | 18 tokens (16 place-locks + 2 identity locks) |
| voice | Elliot, `inworld-tts-1.5-max`, measured ~156–161 WPM |

---

## BEFORE STEP 3 MERGE — required

1. **Apply the block 8 corrections.** 8/16 → `"Three hundred and sixty. On a summit nobody in the
   valley had ever climbed."` · 8/34 → `"He was three hundred years into a job that had never been
   explained to him."` The six-hundred-year stretch sits *after* Noah's birth and is handled at
   block 11 beat 1.
2. **Apply the block 11 corrections.** 11/5 → `"His grandson was four hundred and eighty years old
   and still young for that world."` · 11/38 → `"Take these inside with you. Your great-grandfather
   wrote them for somebody unborn."` (Enoch → Methuselah → Lamech → Noah.)
3. **Re-gate the merged master.** Twelve per-block passes are not a film-level pass.
4. **Read the token × block heatmap.** `{city}` at 60% in block 7 and `{firsthome}` at 52% in block 2
   are both far past the framing-repeat threshold. Both are motivated (each block is one continuous
   scene in one place) and both vary subject rather than place, which is the correct response — but
   they are the two cells to look at with the master open.
5. **Verify `len(cfg["canon"]) == 18`** before any spend. A silent canon miss renders every `{token}`
   literally or aborts the gate.
6. **Confirm `image_model: nano_banana_2`** and `safety_tolerance:"5"` in `sacred-dawn/channel.json`.
   Gate the first grid frames >7KB.

## PROBE PRIORITIES (Step 6)

Highest drift risk first, all fixable at the token:

- **`{eden}`** — carries the WITW `newearth` failure mode exactly. Brightness adjectives alone render
  as a bright desert. Written as glory-as-substance; if the probe returns a sunny meadow, fix at the
  token, not the beats.
- **`{lightcolumn}`** — must read as a solid weighted pillar, never a haze or a lens flare. Balrog
  principle. Used on 9 beats total.
- **`{luminouschild}`** — horror-coding risk. Must read healthy, warm, calm, entirely human.
- **`{watchers}` / `{nephilim}`** — mass and hard shadow, never glow and float.
- **`{stonefield}`** — must read as ordered rows of laid stones, not a natural scree field or a
  graveyard.
