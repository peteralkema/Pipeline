# NOTE: Where the canonical docs encode Final-Hours DNA as if it were universal law

*Banked during the crew-channel build. The insight: Final Hours was the first channel, so its
craft got written into `_PIPELINE-CANONICAL.md` and `ante-machinam.md`
as "channel-agnostic" truth. It isn't. Much of it is **cinematic-slow-faceless-dread** craft
wearing a universal label. Every non-Final-Hours channel has to actively fight this gravity.
This catalogues the specific rules that work AGAINST a bright / fast-cut / character-driven /
flat-illustrated channel, so the next bright channel doesn't re-fight them from scratch.*

*The pipeline MECHANICS are genuinely universal (header format, numbers-spelled-out,
no-legible-text-in-stills, the leg system, parse-verify-before-spend). The CRAFT rules are the
ones infected by Final Hours. The list below is craft, not mechanics.*

---

## The rules this channel deliberately BREAKS (and why)

**1. Beat granularity (Constitution §6: ~15-35 words, 5-12s per beat).**
This is the single biggest one. It assumes Kling-animated slow-cinematic pacing where a still is
slow-filled across a long spoken beat. This channel is FAST-CUT — 4-10 words, 1-3s per beat,
Ink/Mack rhythm. The pacing is authored in beat LENGTH, and short is correct. The §6 table is
Final Hours DNA. **Break it: write short beats.**

**2. Animatable foreground (Constitution §7: every beat needs a kinetic subject to move).**
This exists because Final Hours ANIMATES every still with Kling. This channel uses NO animation —
static stills cut fast, held for their beat duration (`_still_to_held_clip`, not Ken-Burns, not
Kling). With no motion, "what moves in this frame?" is moot. Stills are composed pictures, not
"frames to be moved." **Break it: compose strong static shots; ignore the foreground-motion rule.**

**3. Faceless by default (Part III: never resolve a face; build canon around places not people).**
This is the deepest infection. The whole pipeline was built FACELESS because Flux drifts on faces
and Final Hours' dignity register wanted faces turned away. This channel is the OPPOSITE — a
recurring, visible, named CHARACTER (the Driver, later the crew) in nearly every frame. This is the
hardest thing for this pipeline and the reason the probes fought us on consistency. We accept the
difficulty knowingly. **Break it: resolve the character's face every frame; carry consistency via
`base_canon` + a tool-agnostic character bible (the durable IP), not place-canon.**

**4. The slow-cinematic register itself (Part IV: dread, weight, "let it land in silence,"
present-tense doom, clock-anchored tension).**
Final Hours / Sacred Dawn craft. This channel is BRIGHT, WRY, PROPULSIVE, playful-on-top. The
emotional register is curiosity and delight, not dread and dignity. Keep the universal retention
truths (recognition is the mechanic; CTR won by package, distribution by retention; front-load the
payload) — DROP the funereal register. **Break it: write wry and fast, not weighty and slow.**

**5. Realism / cinematic-photoreal style.**
Final Hours, Sacred Dawn, Scripture, Prehistoric are all painterly-photoreal cinematic. The style
suffixes across the portfolio pull toward realism. This channel is FLAT-CEL ANIMATED ILLUSTRATION,
explicitly NOT photoreal (the photoreal drift was the failure mode in the style probes — it read
"Final Hours" and we rejected it). **Break it: flat cel-shaded; negative the realism.**

**6. Ken-Burns as the cheap floor.**
The doc frames the cost-floor lane as "Ken-Burns-only, ~$3, kling_count:0." This channel goes one
notch leaner: NO Ken-Burns either — pure static holds. Ken-Burns pan/zoom is invisible/janky at a
1-3s cut rate. **Break it: static holds, the cheapest lane in the portfolio.**

---

## What's GENUINELY universal (keep — not infected)

- Header format (`channel/title/description/tags`, bare key:value, no fences)
- `channel` must match the folder
- Numbers spelled out in narration; numerals in metadata
- One VISUAL per Mode A beat; it's the image prompt
- Script is king — lock it first, everything binds to it (THE core principle)
- Image models can't render legible text → no in-still text (or Mode B card)
- Parse-verify zero-spend before any render
- `safety_tolerance:"5"` for flux black-frame rejects
- `base_canon` auto-merges into every beat
- `people_directive` (positive prompt) is the real lever; negatives are weak on flux-pro
- CTR won by package; distribution by retention; recognition is the retention mechanic
- Nothing publishes that a human didn't review

---

## The meta-lesson (the actual gift)

**Build order encodes bias.** The first channel's craft becomes the "default" and silently infects
every doc claiming to be channel-agnostic. The mechanics generalised cleanly; the CRAFT did not.
The fix is not to rewrite the canonical docs but to recognise that **`ante-machinam.md` Part IV is
the Final-Hours/Sacred-Dawn craft brief, not universal craft** — and every genuinely different
channel needs its OWN craft brief that explicitly states which universal-seeming rules it breaks.
This note IS the crew channel's "here's what we break" brief. Future bright/fast channels should
start by reading this list, not by re-deriving it the hard way.

*The learning was the gift: we found the bias by hitting it, named it, and now it's cheap to avoid.*
