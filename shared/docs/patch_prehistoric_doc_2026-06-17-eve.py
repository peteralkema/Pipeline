#!/usr/bin/env python3
"""
patch_prehistoric_doc_2026-06-17-eve.py — update _Prehistoric-Disasters.md for the
evening session: channel is LIVE (2 videos published), audio-chain fixes + 0.9 Victor
noted, Wild Horizons benchmark added to §7, slate statuses advanced (Chicxulub live).
Targeted find/replace, anchor-verified, refuses on miss, idempotent (sentinel).

Run on LAPTOP:  python3 shared/docs/patch_prehistoric_doc_2026-06-17-eve.py
"""
import sys
from pathlib import Path

def _find():
    here = Path(__file__).resolve().parent
    for c in [here/"_Prehistoric-Disasters.md",
              Path.cwd()/"shared/docs/_Prehistoric-Disasters.md"]:
        if c.exists(): return c
    return None

SENTINEL = "LIVE — published 17 June eve"

EDITS = [
 ("status line (header)",
  "- **Created:** 17 June 2026. **Status:** launched, fully automated; first video (Toba) rendered + packaged + uploaded private, **pending account verification** (15-min cap) to publish.",
  "- **Created:** 17 June 2026. **Status:** LIVE — published 17 June eve. Account verified (15-min cap lifted); **two videos public** — Toba (ep1) and Chicxulub (ep2). Fully automated via the batch runner."),

 ("format line — add 0.9",
  "faceless; Inworld **Victor** narration; photoreal-cinematic deep-time stills (fal Flux-pro) on the **Ken-Burns-only floor** (`kling_count:0`, ~$3/video); curated crossfaded ominous music bed (random-3 from the channel's library at MUSIC_LEVEL 0.07).",
  "faceless; Inworld **Victor** narration at **`speaking_rate` 0.9** (slower, deliberate, for the deep-time register); photoreal-cinematic deep-time stills (fal Flux-pro) on the **Ken-Burns-only floor** (`kling_count:0`, ~$3/video) with an optional per-batch front-2-Kling hook (`--kling-count 2`, ~$0.84); curated crossfaded ominous music bed (random-3 at MUSIC_LEVEL 0.07, `amix normalize=0` so it holds a steady level under the voice)."),

 ("op principle — silhouette stays",
  "**Silhouette / scale-anchor note:** the \"tiny human for scale\" thumbnail motif works only for **human-era** topics (Toba, the Lost Human Species, the Last Mammoths). For **pre-human deep-time** (Chicxulub, the Permian, Snowball Earth) a human is an anachronism — swap the scale anchor to a lone tree, creature, or boat in the `thumbnail.json` subject. Flag every slate topic human-era ✅ vs pre-human ⚠️.",
  "**Silhouette / scale-anchor note (decided 17 June eve — the silhouette STAYS in-video):** the channel-wide `style_suffix` puts a tiny lone human silhouette in every still. Decided to KEEP it even on pre-human topics: it reads SYMBOLICALLY (a witness / scale-anchor, the dignified-minimum version of the Chloe-vs-History time-traveller), gives a focal point vs a flat National Geographic spread, is distinctive (nobody in the lane does it), and delivers the channel's core job (felt scale). Let the audience rule it — watch comments on pre-human videos for literal-reading complaints; reconsider only if they appear, not on theory. (The THUMBNAIL scale-anchor is a separate, per-`thumbnail.json` choice — still swap to a lone tree/creature/boat for pre-human thumbnails where a human would jar at a glance. Flag slate topics human-era ✅ vs pre-human ⚠️.)"),

 ("op principle — add audio-chain note",
  "- **Music tracks must have no spaces in filenames**",
  "- **Audio chain (three fixes banked 17 June eve, see canonical §6):** music reaches the batch path only because convergence now derives the channel dir from `proj.parent.parent` (the old `channel_dir` var was undefined → silent `--no-music`); music holds a steady level because the `amix` carries `normalize=0` (the `normalize=1` default ducked it under the voice); Victor's pace is set per-channel via `speaking_rate` in `channel.json`. Validate audio END TO END for level, not a one-listen presence check.\n- **Music tracks must have no spaces in filenames**"),
]

LIVE_STATE_OLD = """## 7. Live state (as of 17 June 2026 — launch session)

| Video | Status | Signal |
|---|---|---|
| **Toba** ("10 Prehistoric Disasters That Almost Ended Humanity", 88 beats, ~20.7 min) | Rendered + thumbnailed + uploaded **private**; **REJECTED at processing — "video too long"** (15-min unverified-account cap). | No retention data yet. **ACTION: verify the account, delete the abandoned upload, re-assemble WITH music (the render predated the music wiring), re-run `upload_episode.py --project prehistoric-disasters/projects/toba`, publish.** Decide 88-beat vs the expanded ~28-min `toba-full.md` for the real publish. |

**This is a pre-launch channel with one video in the pipe and zero published retention data.** Every distribution principle above is inherited from the umbrella doctrine and the sibling channels, not yet validated on this channel's own curves. The first real diagnostic comes after Toba (or whichever video publishes first) clears 48 hours.

**The first open experiment — 88-beat vs expanded:** the `toba.md` (88 beats, ~20.7 min) and `toba-full.md` (expanded, climax trio weighted deepest, ~28-min words-estimate → likely ~40 min real) are two cuts of the same topic. Publishing one and reading its AVD curve tells us whether this lane wants tight ~20-min episodes or long-form ~40-min deep dives — a length-strategy data point that shapes the whole slate. (Length is source-driven and retention-earned, never padded to a competitor benchmark.)"""

LIVE_STATE_NEW = """## 7. Live state (as of 17 June 2026 — evening, LIVE)

| Video | Status | Signal |
|---|---|---|
| **Toba** (ep1, "10 Prehistoric Disasters That Almost Ended Humanity", 88 beats, ~20.7 min) | **PUBLISHED public.** Account verified (15-min cap lifted). | First-48h CTR + AVD pending — read next session. |
| **Chicxulub** (ep2, "The Last Day of the Dinosaurs: The Asteroid They Never Saw Coming", 81 beats, ~8:55) | **PUBLISHED public.** Re-run through the FULL process (delete project → re-ingest → `run_batch.py --kling-count 2 --limit 1`) to bake in music + 0.9 Victor + front-2 Kling. | First-48h CTR + AVD pending. Watch the first 10-15s for the front-2-Kling hook lift specifically. |

**The channel is LIVE with two public videos and zero first-48h data yet.** The distribution principles in §6 are inherited from the umbrella doctrine; the first real diagnostic comes when ep1/ep2 clear 48 hours. **Read both next session via NexLev `get_my_video_analytics` + `get_my_audience_retention`.**

**The lane benchmark — Wild Horizons** (`UC0g0WbvanQND4dC1JDaW1_w`, @WildHorizons6688). This IS the lane: faceless AI-cinematic deep-time catastrophe, Google-Trends keyword `dinosaurs`, even a Toba video ("The 74,000-Year-Old Monster That Killed 99% of Our Ancestors", 326K). Numbers: outlier 6.33, 48.7K subs, ~$4,300/mo, 13.7M total views, **avg ~218K views/video**, and **NO outliers even at 1.3× → a FLAT high-floor curve** (every video clears six figures; the lane delivers reliably, not via jackpots — for a factory model a high floor beats a fat tail). Avg length **~32 min**, biggest hit a 72-min full doc → the lane rewards **long-form**. **It appeared as a SUGGESTED video next to Chicxulub in Studio** → YouTube has classified this channel into the neighbourhood and it's positioned to draw Wild Horizons' recommendation traffic. Compare ep1/ep2 CTR + AVD against the ~218K floor.

**The first open experiment — tight vs long-form:** `toba.md` (88 beats, ~20.7 min) vs `toba-full.md` (~40 min real). The Wild Horizons ~32-min average + 72-min mega-hit leans toward long-form; confirm against ep1/ep2's OWN AVD curves before committing the slate. (Length is source-driven and retention-earned, never padded to a competitor benchmark — but the benchmark is a strong prior.)"""

SLATE_HEADER_OLD = "| — | **Toba** | \"10 Prehistoric Disasters That Almost Ended Humanity\" | LISTICLE | ✅ | **ep1 — rendered, pending account-verify + publish** |\n| 1 | **Chicxulub** | \"The Last Day of the Dinosaurs\" — the asteroid already in the sky, the animals unaware | DEEP-DIVE | ⚠️ | **ep2 — ship next** |"
SLATE_HEADER_NEW = "| — | **Toba** | \"10 Prehistoric Disasters That Almost Ended Humanity\" | LISTICLE | ✅ | **ep1 — LIVE (published)** |\n| 1 | **Chicxulub** | \"The Last Day of the Dinosaurs: The Asteroid They Never Saw Coming\" | DEEP-DIVE | ⚠️ | **ep2 — LIVE (published, front-2 Kling)** |"

def main():
    t = _find()
    if not t: sys.exit("FAIL: _Prehistoric-Disasters.md not found next to script or in ./shared/docs/.")
    text = t.read_text()
    original = text
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present)."); return
    all_edits = EDITS + [("live state §7", LIVE_STATE_OLD, LIVE_STATE_NEW),
                         ("slate ep1/ep2 rows", SLATE_HEADER_OLD, SLATE_HEADER_NEW)]
    for label, old, new in all_edits:
        n = text.count(old)
        if n != 1:
            sys.exit(f"FAIL: anchor '{label}' found {n} times (expected 1) — refusing. "
                     f"Paste the surrounding lines and I'll re-cut.")
    for label, old, new in all_edits:
        text = text.replace(old, new, 1)
    if SENTINEL not in text:
        sys.exit("FAIL: sentinel missing after edits — aborting.")
    bak = t.with_suffix(t.suffix + ".pre_0617eve")
    if not bak.exists(): bak.write_text(original)
    t.write_text(text)
    print(f"OK: patched {t.name} ({len(all_edits)} additions).")
    print("    Verify:  grep -n 'LIVE — published\\|Wild Horizons\\|amix normalize' shared/docs/_Prehistoric-Disasters.md")

if __name__ == "__main__":
    main()
