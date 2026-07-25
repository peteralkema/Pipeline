# SESSION LOG — the full process, 13 Jul 2026
### From "we're doing barbecues" to two complete shippable videos in one session
**Companion docs:** `_SCRIPT-CONTRACT.md` · `_MOTION-DOCTRINE.md` · `_SESSION-NOTES-2026-07-13.md`

This is the *narrative* record — what we did, in order, why, and what each step taught — so the process itself is repeatable, not just the outputs. The terse reference facts live in `_SESSION-NOTES`; this is the story and the method.

---

## THE ARC OF THE SESSION
We started trying to render a single Mount Carmel cold-open frame and it looked like "a barbecue." We ended with two complete, packaged, scroll-stopping videos across two channels (Scripture's *Revelation in 3 Minutes*, Synthetic's *40 Greatest Catastrophes in 3 Minutes*) — each 40 image-to-video clips, a cinematic thumbnail with clean titling, description, chapters, and engagement comment. In between we fixed three engine-level problems, resolved the grade, cracked spectacle staging, defined a distinctive register, and built a repeatable production workflow. The through-line: **every fix came from reading the actual source (code or doc), not assuming — and every craft rule came from reacting to a real render.**

---

## PHASE 1 — THE ENGINE FIXES (read the code, don't assume)

**1. The character system was already built — and had one config bug.** Reading `recreation_pipeline.py` proved the `{token}` mechanism (expand description + attach reference image + route to `/edit`) already existed and worked. The only bug: Scripture's character descriptions sat under a `canon` key the engine doesn't read; the engine reads `base_canon`. Fix = rename the key. Lesson: **the capability existed; the assumption that it didn't was the error.**

**2. The golden-hour "slop" was a MODEL FORK.** Character beats rendered on nano-banana-2 (`/edit`); character-less beats fell to the module default `flux` — a painterly styliser that renders "cinematic/golden-hour" prompts muddy. Two models = two looks. Fix = register `nano_banana_2` as a text-to-image endpoint and set the channel `image_model` to it, so both paths share one model family. Lesson: **when two things look different, suspect two different code paths before you blame the prompt.**

**3. `reference_style_anchor` is read-but-unwired.** The engine reads a setting-anchor key and does nothing with it. It's the proper fix for both residual register-match AND setting-continuity. Flagged as the priority next engine build (still pending).

---

## PHASE 2 — THE GRADE SAGA (the most transferable lesson)
The de-forked landscapes came out *flat and neutral* — we'd over-corrected. The unlock: **the enemy was never saturation, it was MURK** (soft, dark, painterly, muddy). Michael Bay is heavily saturated and reads premium because it is *bright, crisp, high-contrast, clean*. So the fix is to **lift the other direction** — keep the grounded photoreal crispness, add back chroma/contrast/light-energy — never revert toward the slop. And because the model is now nano-banana-2 (not flux), chromatic words render crisp, not muddy, so they're safe again. Result: the "Bay-bright-biblical" grade (and a teal-orange equivalent for Synthetic). Two authoring rules banked: **specify light BRIGHT** (the model defaults dark when unspecified), and **negations grow from evidence, never speculation.**

---

## PHASE 3 — SPECTACLE STAGING (barbecue → scene)
The Carmel frame failed because we crammed the whole miracle into one image, shrinking the fire to a campfire. The competitor teardown (Unraveling the Scriptures, 576K, whose Elijah did 2.8M) showed the fix: **a spectacle is a SEQUENCE of hero shots, never one composite.** They give the fire its *own* hero shot (a vortex descending from parting cloud, no altar, no man). We rebuilt Carmel as a 6-shot sequence — clouds / vortex / strike / prophet / crowd falls / aftermath — and it became a scene. This is the fast-cutting rule applied to the peak. Banked to the contract.

---

## PHASE 4 — THE DISTINCTIVE REGISTER ("Bay's surface, Attenborough's soul")
The differentiation nobody in the lane hits: **blockbuster scale + reverent smallness.** Bay's grade, energy and scale on the surface; Attenborough's humility underneath — the small living thing dwarfed by a vast force. Concretely: **scale needs a human face at the bottom of the frame** (the signature composition rule, all three movie channels), and the camera worships the *phenomenon*, never glamorises the hero. Consistency (grounded look + locked cast) is the premium signal the spray-and-pray incumbents lack.

---

## PHASE 5 — COMPETITIVE + ECONOMIC READ
- **Format validated at scale:** the incumbent runs the exact "[X] – The Movie (2026) … Complete Full 4K" strategy to 2.8M-repeatable. The vein is proven; multi-winner tolerant (two Elijahs both >2.7M).
- **Cost edge is decisive:** our feature ≈ $75–90 all-in vs their ~$400–1,500. Break-even is a rounding error → take ten cheap swings for the price of their one. *"1/10th the cost, happy with 1/100th their views."*
- **Decline lip-sync** (a liability, and doctrine bans it). **Close the animation gap on the monetization dial** (40 → 80 → 200 → full), never day-one.

---

## PHASE 6 — THE MONTAGE PRODUCTION WORKFLOW (the repeatable factory)
The completeness montage ("X in 3 minutes", pure musical score, no narration, 100% hero shots) is a cheaper/faster feeder product. The workflow, proven twice:

1. **Curate 40 distinct scenes** as an *emotional-rotation-with-rising-floor* sequence (open on peak, rotate register beat-to-beat so it never numbs, resolve on recovery). Every beat a different world → variety is structural, cross-beat drift impossible.
2. **Generate 4 composition variants per beat** on the fixed scale-vs-humanity grammar: a=WIDE (phenomenon dominant), b=MID (human larger), c=TIGHT (reaction), d=WILDCARD. 160 stills, ~$13.
3. **Pick from the carousel** — the human eye picks the strongest frame per beat (40 numbers). Rename copies `01_ 02_…` grouped by beat for fast carouseling; keep originals for the shot-number handoff. *The picks are the taste signal, and they only persist in a saved reference folder — the session forgets them.*
4. **Assemble a finish-project** — copy the 40 winners into a fresh project renamed `shot_001..040` in beat order, write a 40-entry storyboard with **per-beat motion assigned by the Motion Doctrine**, set `kling_count: 40`.
5. **Kling image-to-video** off the exact picked frames (composition can't drift — Kling only adds the assigned motion). 40 clips, ~$14. Run unattended in tmux, both montages chained with `;`.
6. **Filmora** — import the 40 clips (they land named in beat order), score the music by hand (music carries the majesty; done manually so it hits the beats).
7. **Package** — thumbnail (find it in the render pile OR generate: one dominating phenomenon + tiny human + title lockup in reserved negative space), description + grouped chapters, one pinned reflexive-opinion comment.

Total per montage ≈ $27 render + your edit time. Two videos, two channels, one session.

---

## PHASE 7 — PACKAGING (proven on both)
- **Thumbnail = image sells awe, title sells the deal — never echo each other.** Vast phenomenon dominant, one tiny human for scale, a single eye-anchor (chromatic accent OR a clean pool of light), title lockup in reserved dark negative space.
- **Title text: render clean + add as a layer** (AI garbles text) — though ChatGPT's UI rendered clean titles this time. Keep the lockup **identical across videos** — matching type = series branding.
- **Shorter title wins at grid size** ("REVELATION" beat "THE BOOK OF REVELATION"). Judge every thumbnail at 1cm tile size (the squint test), not full screen.
- **Pinned comment:** one specific, low-effort, reflexive-opinion question ("Which horseman is most terrifying?"). Reply to the first 10–20. Never stack asks.

---

## THE META-LESSONS (how we worked)
1. **Read the source, don't reconstruct from memory** — the three engine fixes all came from reading code; the errors all came from assuming. Applies to docs as much as code.
2. **Doctrine transfer = checklist, not summary** — enumerate every rule, place-verbatim or flag-the-drop for veto. Summarizing silently drops rules.
3. **Additive, forward-only** — a proven render beats a stale doctrine; update the doctrine to match progress, never roll back a gain.
4. **The human picks, the machine generates wide** — taste is selection, not specification; the winner is *found* in a wide batch, not art-directed up front. Cheap stills ($0.08) make fishing for outliers nearly free.
5. **Motion is derived, not chosen** — the crux of the two stunning videos: one deterministic rule read off each shot, applied 40 times (see `_MOTION-DOCTRINE.md`).
6. **The friction is the manual glue, not the work** — machine discipline (laptop→git→box), the prompt tells you which machine, timestamped folders, tmux for unattended. Bank the glue too.

---

## STILL OPEN (the build queue)
- Wire `reference_style_anchor` (priority engine task — fixes setting-continuity + register-match).
- The full Synthetic2 §5/§13 enumerate-and-veto audit into the contract.
- Change the module default `IMAGE_MODEL` from `flux` to `nano_banana_2` so no channel ever silently forks again.
- Commit the five box-only engine files; fix the leaky `.gitignore`.
- Update `_Synthetic2.md` §13 to the three-character lock + resolved grade; archive dead `_Synthetic.md`.
- The batch-of-batches runbook (`_BATCH-RUNBOOK.md`).
- Publish both videos; read the 48h signal (CTR + retention); reinvest where retention proves the animation gap.
