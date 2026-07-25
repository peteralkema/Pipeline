# FLAGS — 17 Jul 2026 session
**Banked mid-flight, to be folded into `_LEGO.md` / `_CHANNELS.md` on the next doc pass.**
Ordered by value, not by discovery. ✅ = already done. 🔧 = build. 📄 = doc only.

---

## THE LAWS — these are the ones worth keeping

### ⭐ 1. The human-scale rule has a CEILING (amends `_LEGO.md §3A.2`) 📄
> **"Scale needs a human face at the bottom of the frame"** is Sacred Dawn's signature move and it is
> right from **mountain up to city**. At **planetary** scale it INVERTS: the model sizes the object to
> the person and you get a diorama.
>
> **Measured 17 Jul:** 4 of 5 wide lunar shots WITH a man came back door-sized. The one WITHOUT was
> instantly planetary and the best frame of the day.
>
> **The refinement:** the human establishes scale only when a **known-size world** is in frame with him —
> mountain, city, cliff, ridge. Absent that, he becomes the ruler and the object shrinks to fit.
> On the moon, **the limb is the only scale reference that survives.**
> **Exempt:** tight faces. A close-up has no scale reference to corrupt.

### ⭐ 2. Every fix opens the next gravity well — the probe loop IS the pipeline 📄
> Wells found, in order, one per round: **painterly → murk → steampunk → archaeological ruin →
> egyptian → colonnade → star destroyer.**
> This is not failure, it is the process. It means the probe is not a phase you pass — it is the loop
> you live in. **§0's law generalises: every blanket you remove reveals the next one underneath.**

### ⭐ 3. The probe is a SAMPLER, not a scan 📄🔧
> The probe rendered 16 of 80 beats and found steampunk in 8. **The sweep found it in 24.**
> **Probe to DISCOVER the failure class. Sweep the whole film to FIX it.**
> Without the sweep, six unprobed blocks ship the disease.

### ⭐ 4. The word target is a MEASUREMENT, not a gate (corrects `_LEGO.md §4`) 📄
> A 5.000s beat holds **11.9 words** at 143 WPM. That is the hard ceiling.
> - comps: 11.7/beat = **2% air** — wall-to-wall, zero punch
> - `_LEGO.md` says 380 = 9.5/beat = 20% air — **still nearly flat**
> - block 1 came in at **239 = 6.0/beat = 50% air** — "The voice changes." "The story stops."
>
> **430 was never achievable with variance. Neither is 380.** Punchy 3-word beats cost budget.
> **The count is not a target — it is a measurement of the register you wrote.**
> **The real gate is one-directional and always satisfiable: `words <= span * 11.9` per SENTENCE.**
> Under-run is safe; the tail is a pad. Then the count *tells* you what you made.
> *(The doc currently carries BOTH a per-sentence gate and a per-beat target. They contradict.)*

### 5. The register gate is a beat-table SWEEP, not a doc 📄🔧
> The doctrine was clean and the output wasn't. I scrubbed "dust-filled libraries" from the contract
> and wrote it into the film an hour later. **Scrubbing a document does not scrub the authoring.**
> Two commands, ten seconds, would have caught it:
> - **setting mix** per block (block 1 draft 1: chapel **20/40** — half the block was a book on a stand)
> - **banned words** in the `phenomenon` column
>
> ### 5a. Spectacle-vs-object ratio (the sharper version)
> Block 2 draft 1: **27/40 object-led** — hands, fragments, tablets, vellum. Set dressing changed,
> disease identical. **Sacred Dawn's authority is not "look at the evidence" — it is "look at what
> they were looking at."** Every claim about the text must cut to the sky it describes.
> After the fix: **11/40 object-led, `heavens` 3→20.** Same narration. Purely visual.

### 6. Literal-metaphor violations are the #1 gravity-well source 📄
> `_LEGO.md §3A.2` already says *"no literal-metaphor beats — models render metaphors as corny props."*
> **"Machine" is this film's central metaphor and I wrote `mechanism` into eleven image prompts.**
> The model rendered Victorian clockwork.
> **THE RESOLUTION: the narration says machine. The image NEVER renders one.**
> Enoch describes gates, portions, storehouses — architecture. Render cut stone, nothing moving.
> **The viewer supplies the word, and that is stronger than showing a cog.**

---

## NEW WELLS FOUND TONIGHT (block 1, 40 stills) 📄

| well | trigger | fix |
|---|---|---|
| **star destroyer** | `plated`, `seamed` | ban them — industrial words in an image prompt |
| **the door** | a **single opening framed alone** | **never frame one opening in `{heavens}`.** Close = door (no limb to anchor). Wide + ranked + curve = planetary. **This is the same law as #1: no scale reference → model falls back to human scale.** |
| **uninvited galaxies** | none — arrives unprompted | word-removal insufficient; needs a **negative prompt** |
| **letterboxing** | unknown | shots 002/005/017 came back with black bars, not filling 16:9. **Check the render config.** |

**Also banked:** `gateway` carries human scale — a thing you walk through. The one prompt that said
*"openings cut into the lunar rock"* was the only one that read planetary. **13 beats de-doored.**

---

## THE CANON TOKEN LAW 📄

### 7. A canon token must name what a place IS, not what it isn't ✅
> `{heavens}` was *"the sky seen from outside the world — vast open air, no ground, no horizon line,
> no architecture."* Defined by negation. **"Open air" invited clouds**, and **"no architecture"
> contradicted every prompt written into it.**
> Rewritten to *"the airless surface of the moon... hard black horizon, black star-scattered space,
> raw unfiltered sunlight, no clouds, no blue sky, no ground, no earth."*
> **One token fixed all 37 `heavens` beats at once, for $0.40.** Earth-drift 5/5 dead.

### 8. Setting continuity IS a canon token ✅
> The locked place-phrase (`_LEGO.md §3A.2`) needs no new mechanism. `{token}` → `canon` block →
> `_expand_canon`. **Verbatim repetition by construction, one string, cannot drift.**
> **Verified:** `stills --beats` accepts *"a dict with optional 'canon' block + 'beats' list"* and
> expands both `image_prompt` and `motion_prompt`, writing the result into `storyboard.json`.
> *(`_LEGO.md §13` said an `entities` column. Wrong — corrected.)*

### 9. NEVER read-modify-write a config file 🔧
> **`canon.json` lost six of eight tokens TWICE today** — a patch script read the file from a sandbox
> that was not the source of truth and rewrote from it. Silent. The gate caught it only because
> `{chapel}` then failed to resolve.
> **Write the full object explicitly. Always.**

---

## ENGINE FACTS — for `_LEGO.md §9`, "do not re-learn the hard way" 📄

### 10. TWO different artifacts are called `beats.json`
> - **parse leg output:** `visual`, `mode`, `component`, `found_line`, `face_hold`, `warnings`
> - **what `stills --beats` reads:** `narration`, **`image_prompt`** (REQUIRED, no `.get()`), `motion_prompt`
>
> **I reconstructed the schema from a neighbour (`01-semjaza/beats.json`) instead of reading the
> consumer. `--help` had told me the right format ten minutes earlier.** Cost: a KeyError and 20 min.

### 11. The flux banner is a LYING INSTRUMENT
> `recreation_pipeline.py:1565` prints `{IMAGE_MODEL}` — the **module constant**, always `flux`.
> The render decides at **line 688**: `config.get("image_model", IMAGE_MODEL)` → `nano_banana_2` wins.
> **The one line telling you which model you are about to spend on reports the exact wrong thing the
> entire de-fork existed to escape.** Two-line fix. A print statement that cries wolf about your worst
> failure mode will eventually mask the real one.

### 12. `beats.json` is gitignored — and that is CORRECT
> `.gitignore:24 **/projects/**/beats.json`. Pre-existing. **The CSV + the converter is the tracked
> truth; the artifact is built where it is used.** Same principle as never committing clips.
> **Cost 20 min and three wrong guesses to rediscover.**

### 13. `style_suffix` is prepended at RENDER, not at ingest
> Line 632: `f"{style_suffix}. {image_prompt}"`, resolved by `resolve_look()`.
> **It is never in `storyboard.json`** — so grepping the storyboard for a killed clause proves nothing.

### 14. `load_channel_config(strict=True, anchor=Path(args.project))`
> The channel resolves from the **project path**. Run from the channel dir. There is no `--channel` flag.

### 15. `--project` must be ONE path part
> `recreation_pipeline.py:1386`: `if not project.is_absolute() and len(project.parts) == 1`.
> **Nest it and the `projects/` prefix is silently skipped.** Hence `moon-bNN-finish` flat.

---

## BUILD — open work 🔧

### 16. `--variants` IS NOT WIRED — blocks the whole pick workflow
> The `variants` column exists, `build_moon.py` prices it, **nothing consumes it.**
> Block 1 rendered **40 stills, not 112** — one per beat, not pick-from-4.
> **This is the single biggest open item.** The 160→40 pick is gospel and there is currently no
> mechanism to generate the candidates.

### 17. `.SKIP` placeholders (blocked behind #16)
> The stills review programme shows a **fixed 4-up grid, keys 1–4, auto-advance**. Breaking the grid
> makes it redundant — and the pick is the scarce resource, so the grid wins.
> **Design:** `shot_007_d1.SKIP.png` — a white tile, deliberately not requested.
> - **invariant:** every beat has exactly 4 files (the programme's requirement)
> - **gate:** non-`.SKIP` count == `variants` (distinguishes "not requested" from "fal failed")
> - **guard:** a pick resolving to a `.SKIP` file is a HARD FAIL — muscle memory at frame 600 will
>   eventually press `3` on a blank, and that would sail through to a $0.42 Kling render of nothing.

### 18. `describe.py` — the master helpfile 🔧
> **Code archaeology was the single biggest time sink today.** Five wrong guesses, all first-order
> interface facts.
> **Docs cannot fix this** — and today proved why: `_Sacred-Dawn.md` described a suffix already killed;
> `_SCRIPT-CONTRACT.md` carried a register scrubbed 12 days earlier. **Interface facts written into a
> doc rot the same way, and then I am confidently wrong instead of ignorantly wrong.**
> **Generate it from the artifact:** one script that introspects and prints — every subcommand + flags,
> required keys of each artifact with a real sample, where config anchors from, where `style_suffix`
> attaches, live `image_model` per channel, what's gitignored. **Run at session start, paste the output.**
> **It cannot lag, because it reads the code.** That is whisper and ffprobe applied to the codebase.
> `_LEGO.md §9` then holds only what CAN'T be generated — the traps above. Those don't rot.

### 19. The probe card is off by one 🔧
> Prints array indices (0–15); the stills are `shot_001`–`shot_016`. Print shot numbers.

### 20. `PHASE 3` is a principle, not a procedure — make it one 📄
> "20 stills, 2 per block, register-spread" gives a ratio, not a method. Compare `§7` motion: three
> questions, in order, first that fires names the move. **That is why motion never causes friction.**
> **Selection procedure — per slot, first rule that fires claims it:**
> 1. **change-weighted** — what changed since the last probe? **Half the probe.**
> 2. **novel-composition** — never rendered before. *A failure costs a PAYLOAD, not a still.*
> 3. **axis canaries** — one cosmic + one earthly per block, **MANDATORY**, never uniform-random.
> 4. **known-failure** — any class that has rendered wrong before.
>
> **And the half that was missing entirely: each slot carries a WRITTEN BINARY VERDICT before it
> renders.** Not "does it look good." *Does the chapel read bright — yes/no. Does the machine have
> mass rather than glow — yes/no.* **Writing the verdict first is what stops you rationalising a bad
> render at frame 600.** Emit the verdict line into `LOG.md` — that's the record Enoch 200 has none of.

### 21. Verify the CONSUMED artifact, not the inputs 📄
> Round 2 of the probe cost **$0.64 and tested nothing**: `canon.json` and `build_moon.py` both reached
> the box correctly — **and `beats.json` was never regenerated**, so the render used round 1's embedded
> canon. nano_banana_2 is non-deterministic, so it *looked* like new results.
> **A generated artifact is STALE until you have read it.** Count the beats before you spend.

### 22. The word counter must strip standalone punctuation 🔧
> `split()` counts `—` as a word: 296 vs 285. **The prosody rule MANDATES em-dashes over full stops,
> so a naive counter penalises exactly the writing style the doctrine requires.** The gate would fight
> the craft.

---

## RESOLVED TODAY ✅
- **The register survives the palette-only suffix.** All three earthly canaries passed. The beats carry
  their own light; the god-ray clause was not load-bearing. **Blocks 3–8 unblocked.**
- **The cool anchor comes from the beats, not the suffix.** `_CHANNELS.md §1` open item #1 — my worry
  about a monochrome-warm palette was wrong. Deep blue skies and cold shadow arrived from beat text.
- **Kling ships 121 frames, non-deterministically.** `-frames:v 120 -c copy` → 400 × 5.000000s. Not a
  re-encode. **Chapters are arithmetic now.**
- **Sacred Dawn's `style_suffix` was already fixed** — the doc lagged the config, not the reverse.

---

## THE THROUGH-LINE

> **Every real finding today came from a command against a live thing. None came from reading.**
>
> Kling's extra frame. Synthetic's stranded grade. Sacred Dawn's suffix already fixed. `kling_count: 2`.
> The contract still carrying "half-seen" twelve days after the cleanse. The steampunk. The doors.
> The canon clobber. **Not one was discoverable by reading documentation.**
>
> `_CHANNELS.md §0.1`'s verification chain — **artifact beats config, config beats doc** — is the most
> load-bearing paragraph in the set, and I proved it repeatedly by ignoring it.
