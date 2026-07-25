# _LEGO-FEATURE-FILM.md
### The repeatable pathway for a 100%-Kling narrated feature film
**Status:** proven end-to-end on Sacred Dawn / *The Book of Enoch* (30 min, 10 blocks), 15 Jul 2026.
**Companion docs:** `_SCRIPT-CONTRACT.md` (authoring) · `_MOTION-DOCTRINE.md` (motion) · `_Sacred-Dawn.md` (register) · `_SESSION-NOTES-2026-07-15.md` (the run that proved it)

---

## 0. WHAT THIS IS

A **feature film assembled from identical Lego blocks.** One block = one 3-minute unit = 40 Kling clips +
one contained VO. Ten blocks laid end-to-end in Filmora = a 30-minute film. Twenty blocks = an hour.
The block never changes; only the count does.

**It reuses the existing pipeline unmodified.** No new engine code. Every step below is an existing
subcommand of `recreation_pipeline.py` plus two thin scripts (`build_enoch_all.py`-shaped generator,
`build_finish.py` assembler). That is the point: **the pathway is a way of USING the machine, not a new machine.**

**What distinguishes it from the montage pathway** (`_SESSION-LOG-2026-07-13.md`):
| | Montage (feeder) | Feature (this doc) |
|---|---|---|
| length | 3 min | 30–60 min |
| audio | music only, no narration | **contained VO per block** + music bed |
| blocks | 1 | N |
| cost | ~$27 | ~$300 for 30 min |
| motion | derived, silence is structural | derived, **silence re-triggered as grief** |
| assembly | one Filmora timeline | N blocks + **hand-seamed** |

---

## 1. THE BLOCK — THE LEGO UNIT

**One block = 3 minutes of finished film.**

| property | value | why |
|---|---|---|
| **beats** | **40** | 40 × 5s Kling = **3:20 container** |
| **stills generated** | **160** (40 beats × 4 variants) | the carousel needs a wide net |
| **stills picked** | **40** (one per beat) | the taste signal |
| **clips** | **40**, 100% Kling | no Ken-Burns floor in a feature |
| **VO** | **~390–440 words** | 143 WPM (Elliot) → 2:44–3:04 speech, fits 3:20 with 15–30s air |
| **still cost** | 160 × $0.08 = **$12.80** | nano-banana-2 |
| **clip cost** | 40 × $0.42 = **~$17** | Kling 2.5 Turbo Pro, 5s |
| **block cost** | **~$30** | |

**The block is self-contained.** Its VO does not run across the seam. Its 40 clips do not depend on the
previous block's frames. This is what makes it a Lego brick: **blocks fail independently and re-render
independently.** A bad block is $30, not a film.

**Scaling:**
| film | blocks | beats | stills | clips | speech | cost |
|---|---|---|---|---|---|---|
| 15 min | 5 | 200 | 800 | 200 | ~14:20 | ~$150 |
| **30 min** | **10** | **400** | **1600** | **400** | **~28:40** | **~$300** |
| 45 min | 15 | 600 | 2400 | 600 | ~43:00 | ~$450 |
| 60 min | 20 | 800 | 3200 | 800 | ~57:20 | ~$600 |

*Incumbent comparison: $400–1,500 per feature. At ~$300 for 30 min you take ten swings for their one.*

---

## 2. THE FILM SPINE (before any block exists)

**A feature is N blocks on a narrative spine — NOT N montages in a pile.**

```
[ TRAILER COLD-OPEN ]  45–90s · cut LAST · $0 · re-uses the best clip of each block
[ BLOCK 1 ] … [ BLOCK N ]  the escalating spine
[ CLOSING SEED ]  pays off the cold open's loop + hooks the sequel
```

**Spine rules:**
- **Each block answers one question and opens two** (`_SCRIPT-CONTRACT.md` §5, the Curiosity Engine).
- **Each block has its own emotional identity.** Never hold one register across blocks — that's viewer
  fatigue. Enoch's: curiosity → suspense → fascination → horror → urgency → catastrophe → awe → wonder →
  reflection → resolution.
- **Thumbnail material lives in blocks 2–4** (the proven-demand spectacle: Watchers, giants).
- **Retention holds in the last three blocks** — they must be the strangest content, because that's where
  viewers leave.
- **The reflective block is the danger zone.** Enoch's block 9 (the dead) sits between two peaks and is the
  softest beat in the film. It needs your *strangest frames* and *most motion*, precisely because the VO goes
  quiet there. (This is where the settle-lull bug did its damage — see §7.)
- **The cold open is written and cut LAST**, once you've seen the whole thing come together.

---

## 3. AUTHORING — TWO INDEPENDENT HALVES

The single most important structural fact of this pathway:

> **The VO and the visual beats are authored SEPARATELY and are only loosely coupled.**
> The VO rides *above* the visuals. It is never locked shot-for-shot. Neither half references the other's
> line numbers. This is deliberate — it is what makes 40 free-standing picks possible.

**Half A — the narration** (one file, N sections):
- ~390–440 words per block. Word count is the lever; **never the speed dial.**
- All `_SCRIPT-CONTRACT.md` §5 rules bind: Opening Law, Curiosity Engine, escalation every 20–40s, human
  lens, visual narration, **prosody** (em-dashes over full stops — kill the see-saw; spell every number out;
  write for the breath).
- **Attribution moat (apocryphal/biblical lanes):** every supernatural claim stays *the text says / Enoch
  describes / the book claims*. Never assert in our own voice. This protects YPP and it is non-negotiable —
  reject any retention advice that asks for a bald assertion ("The Flood was Heaven's military response").
- Each block ends on an **open loop pulling forward** — and **vary the phrasing.** Four blocks closing on the
  same construction is a pattern the viewer *feels*.

**Half B — the visual beats** (a `build_<film>_all.py` generator):
- 40 beats per block, each a tuple: `(title, phenomenon, anchor, wildcard)`.
- **Prompts carry ZERO grade words.** The look lives in `channel.json`'s `style_suffix`. Per-beat light
  ("in a dim chamber", "under bright parting cloud") is *content* and belongs in the beat.
- **No literal-metaphor beats.** No keys, globes, hearts, scales. Models render metaphors as corny props and
  anachronisms. Render the consequence, not the metaphor.
- Beat text drives the **emotion classifier** and later the **motion derivation** — so write phenomena with
  real verbs (descends, towers, spreads, waits).

---

## 4. THE FOUR-VARIANT GRAMMAR (per beat)

Every beat generates four stills. This is the safety net that guarantees each beat has a usable frame.

| variant | shot | face | typical motion |
|---|---|---|---|
| **a** | **WIDE** — phenomenon dominant, human tiny and dwarfed | none (anonymous *by distance*) | PULL-BACK |
| **b** | **MID** — human larger in lower frame, phenomenon looming behind | partial (¾ / profile) | PUSH-IN |
| **c** | **TIGHT** — the reaction shot | **full anonymous face + register-matched emotion** | PUSH-IN |
| **d** | **WILDCARD** — authored hero composition, unique to this beat | varies | derived from text |

**Anonymous, never faceless.**
> Faceless hides every face. Anonymous just never locks one. The drift risk lives in repeating *one*
> unlocked protagonist face — so the recurring figure stays turned or distant, and every other face shows
> freely. A different anonymous face each time reads as *humanity reacting*, not continuity breaking.

**The tight's emotion is rotated by register, never blanket.** Classify each beat awe / fear / grief from its
own text; the tight takes the matching phrase. A blanket "deeply moved" collapses to tears on 100% of frames
and destroys the emotional-variation lever.

**PROVEN FINDING — weight toward the wildcard.** Real pick distribution on Enoch:
```
a(wide)=100   b(mid)=81   c(face)=75   d(WILDCARD)=144  ← 36%, the clear winner
```
The authored hero shot beat every formula variant. Block 8: a=2, d=20.
→ **Next film: 2 wildcards per beat (a, c, d1, d2) instead of a/b/c/d.** Same $12.80, better picks.

---

## 5. THE MOTION LAW FOR NARRATED FEATURES

`_MOTION-DOCTRINE.md` was written for a **music-driven montage**. Two rules must be re-triggered for a
narrated feature. **Name the departure — never silently reinterpret.**

| doctrine (montage) | feature (VO) |
|---|---|
| "Never push-in on **silence**" | **"Never push on the grief/aftermath beats."** There is no silence — the VO never stops. Same rule, new trigger. |
| NEAR-LOCKED for held-breath beats | **Retired.** Under continuous VO a locked frame reads as a stalled slideshow, not a held breath. SETTLE carries the quiet work. |

Everything else transfers intact: one primary move per beat, slow and eased, subject locked and camera
carries it, motivated by meaning never a timer, four moves and nothing else.

**Motion derives from `beat × variant × register` — never beat alone.**
The same beat picked as an `a` wide is a scale-reveal (PULL-BACK); picked as a `c` face it's one overwhelming
subject (PUSH-IN). **The picks record is what makes correct derivation possible.**

**The precedence ladder (first match wins):**
```
1. grief/aftermath  → SETTLE      (never push)
2. vertical force   → CRANE-UP    (overrides framing)
3. c tight face     → PUSH-IN
4. a wide           → PULL-BACK
5. b mid            → PUSH-IN
6. d wildcard       → scale→PULL-BACK · vertical→CRANE-UP · else PUSH-IN
```

**Healthy spread** (Enoch's verified 400): `PUSH 178 · PULL 123 · CRANE 72 · SETTLE 27`.
Push dominant is expected — it's the doctrine's powerful default. **A flatline is the failure signal**;
so is any single block carrying >~15% settles.

---

## 6. THE PIPELINE MAPPING (existing code, no new engine)

| step | command | cost |
|---|---|---|
| ingest beats → storyboard | `stills --beats … --project … --storyboard-only` | **$0** |
| render stills | `stills --beats … --project …` | $0.08 ea |
| re-render one still | `restill` | $0.08 |
| routing/cost preview | `finish --project … --kling-count 40 --plan` | **$0** |
| animate only | `finish --project … --animate-only --kling-count 40 --no-music` | $0.42/clip |
| re-stitch existing | `finish --assemble-only` | $0 |

**Facts about the engine you must not re-learn the hard way:**
- **There is no `animate` subcommand.** It's `finish` ("animate + narrate + assemble"). `--animate-only`
  stops after clips — correct when cutting in Filmora.
- **The animate leg reads `storyboard.json`, NOT `beats.json`.** A finish project with no storyboard animates
  everything with `_default_motion` and silently discards your derived motion. **The `--storyboard-only`
  ingest on the finish project is MANDATORY.**
- **`_tiered_kling_count` reads `render_policy.json`, not `channel.json`.** Pass `--kling-count 40` explicitly.
- **`--plan` is the definitive pre-spend answer** to "will every clip get Kling?" Free. Use it every time.
- The stills cache is **filename-based**. Never re-render into a folder with output — use fresh `-vN` folders.
- Module default `IMAGE_MODEL` is `flux` (the murk styliser). `image_model: nano_banana_2` must be explicit
  in `channel.json` or character-less beats fork to a second look.

---

## 7. THE PATHWAY — STEP BY STEP

### PHASE 0 — GATE THE GRADE (before one cent)
1. **Reconcile the `style_suffix`:** palette only (colour, materials, mass, brightness, anti-murk negatives).
   **No light source, no shafts, no blanket shadow** — those are content and belong in beats.
2. Confirm `image_model: nano_banana_2`. Set both **on the laptop → commit → push → pull on box.**
3. **Verify on the box with a check that distinguishes EVERY known-bad grade**, not just the one you're
   thinking about. (A storm-only check passes a warm-daylight suffix with flying colours.)
4. If the box pull aborts: `git diff` **first**, read it, then `git checkout --` only what you understand.

### PHASE 1 — PROBE THE REGISTER ($1.60)
20 stills, **2 per block, register-spread** (per block: most-cosmic beat + most-earthly beat). Never uniform-
random — it can hand you 20 cosmic beats and never test the daylight half, which is the half a bad suffix wrecks.
**Verdict:** do the earthly canaries read bright-real without a stamped storm? Do the cosmic beats hold mass
without glowing vapor? If yes → register locked.

### PHASE 2 — PROBE WHAT CHANGED ($1.60 each time)
Any material change to what renders (faces, emotion, grammar) earns its own probe, **re-weighted toward the
change**. Enoch's face probe: 10 tight, 5 mid, 3 wide, 2 wildcard.
**Verdict:** does the new thing land, *and* do the c-row faces differ from each other (no latent protagonist drift)?

### PHASE 3 — RENDER ALL STILLS, ONE RUN ($12.80/block)
Fresh `-v2` folders. Free `--storyboard-only` sweep across all N blocks first (catches parse issues the probe
never sampled). Then one unattended tmux loop.
> **Batch the machine work. Chunk the human work.** The block boundary buys nothing at render time — it exists
> to protect your *eye*.
Watch for `falling back to flux` → note the shot, `restill` it later for $0.08.

### PHASE 4 — CAROUSEL, ONE BLOCK PER SITTING
160 stills → 40 winners into a `Winners/` folder per block. **Ten sittings, not one marathon** — by frame 600
you're rubber-stamping, and a tired pick is a weak clip you pay $0.42 to animate.
**Ask per group of four: which of these earns $0.42 of Kling?** — not "which is prettiest."
**Integrity gate (all blocks):** 40 picks · **no duplicate beats** · **no missing beats**.
> 40 picks does not mean one-per-beat. Two winners on beat 7 + none on beat 23 still counts 40, and it
> silently corrupts beat order — discovered only after the full Kling spend.
**Back up the picks record.** It's the only artifact of the taste signal and the session forgets it.

### PHASE 5 — ASSEMBLE + DERIVE MOTION ($0)
`build_finish.py emit` → reads `Winners/`, derives `beat × variant × register` → writes per-block
`beats.json` + `picks.json` + a **400-row veto table** showing every move *and its reasoning*.
**Read the veto table.** Check the portfolio spread and each block's settle count. Flip anything wrong.
Fix misclassifications by **correcting the register and re-deriving** — never by hand-picking a move.
`build_finish.py place` (on box) copies picked frames into `<block>-finish/stills/` renamed `shot_001..040`
**in beat order**. Copies, never moves — originals stay intact.

### PHASE 6 — INGEST + VERIFY ($0) ← the step that saves the whole spend
```
for each block: stills --beats <block>-finish/beats.json --project <block>-finish --storyboard-only
```
Then **read `storyboard.json`** and confirm: N×40 shots · **zero OTHER/DEFAULT** · the block you patched shows
the patched spread. Zero defaults = every clip carries your derived prompt.

### PHASE 7 — PLAN, THEN FIRE ($0, then $17/block)
`finish … --kling-count 40 --plan` on every block. Want **N=40 → 40 Kling**, no Ken-Burns fallbacks.
Then in tmux: `finish … --animate-only --kling-count 40 --no-music`.
**Never restart `mission-control.service` mid-animate** — the cgroup teardown kills the leg.

### PHASE 8 — VO
One MP3 per block from the narration master. Paste one block at a time — a chunk failure costs one block,
not the whole film. Elliot @ 1.0.

### PHASE 9 — FILMORA (the human leg)
Clips land named `shot_001..040` in beat order → import a block, they lay themselves out. Drop the block's
MP3 over them; loose thematic sync carries it. **Seam the blocks by hand.** Music bed under everything.

### PHASE 10 — COLD OPEN, CUT LAST ($0)
Now that the film exists, cut the trailer from **the best clip of each block**. No new renders. It flashes
every block, plants the film's biggest loop, and the final block pays it off. See §8.

### PHASE 11 — PACKAGE
Thumbnail: **render a clean plate with NO text instruction at all** (mentioning text summons text — and
hallucinated "4K ULTRA HD" badges), then lay your own lockup in. **Identical type across every video IS the
series branding** — a generative model cannot give you identical twice. Judge at 1cm, not full screen.
Title short. Description + grouped chapters. One pinned reflexive-opinion question.

---

## 8. THE COLD-OPEN BLOCK (its own Lego shape)

| property | value |
|---|---|
| **length** | 45–90s |
| **clips** | **re-used**, ~2 from each block — the strongest frame of each |
| **new render cost** | **$0** |
| **VO** | ~110–215 words (143 WPM) |
| **cut** | **LAST**, after the film is assembled |
| **job** | flash every block · plant the film's biggest open loop · the final block pays it off |

**Why last:** you can only pick "the best shot of each block" once every block exists. Writing it first means
promising something the film may not deliver — and the Opening Law says the opening must *fulfil* the promise
in the first frame, not set one you'll hope to meet.

---

## 9. THE PRE-SPEND CHECKLIST (print this)

**Before stills ($12.80/block):**
- [ ] `style_suffix` = palette only, no welded light/shafts/shadow
- [ ] `image_model: nano_banana_2` verified **on the box**
- [ ] verify screens **every** known-bad grade, not just one
- [ ] register probe passed (spread across the axis)
- [ ] any material change since last probe → **new probe**
- [ ] fresh `-vN` folders (never re-render into existing output)
- [ ] free `--storyboard-only` sweep clean on all N blocks
- [ ] prompts: 0 empty · 0 grade-leak · 100% ASCII · N×160 count

**Before Kling ($17/block):**
- [ ] carousel integrity: 40 picks · no dupes · no missing — **every block**
- [ ] picks record backed up
- [ ] veto table read; portfolio spread rotates (not flat); no block >~15% settles
- [ ] `build_finish.py place` → N folders × 40 files, `shot_001..040`
- [ ] **`--storyboard-only` ingest run on every finish project**
- [ ] `storyboard.json` verified: N×40 shots, **0 OTHER/DEFAULT**
- [ ] `--plan` clean on every block: N=40 → 40 Kling, no KB fallbacks
- [ ] tmux; nothing will restart `mission-control.service`

---

## 10. THE LAW THAT GENERATED THIS DOCUMENT

> **Any rule that applies to 100% of beats is a bug until proven otherwise.**

Four instances in one session, four different layers — grade, faces, emotion, motion. Each was a blanket
stamped where content should have earned it. Each cost a probe or a patch to find.
**Drama is earned by content, not stamped by grade.** The same sentence is true of faces, of emotion, and of
the camera. When you find yourself writing a rule that fires on every beat: that's the bug.
