#!/usr/bin/env python3
"""
patch_canonical_2026-06-17-eve.py — APPEND-ONLY additions to the canonical for the
17 June evening session (audio-chain fixes, Prehistoric live, Wild Horizons benchmark,
scheduler design, YouTube quota). Targeted find/replace; verifies every anchor hits
exactly once and refuses if not. Does NOT rewrite — only inserts. Idempotent (sentinel).

Run on LAPTOP:  python3 shared/docs/patch_canonical_2026-06-17-eve.py
"""
import sys
from pathlib import Path

def _find():
    here = Path(__file__).resolve().parent
    for c in [here/"__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md",
              Path.cwd()/"shared/docs/__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md"]:
        if c.exists(): return c
    return None

SENTINEL = "17 June eve"

EDITS = [
 # (label, old, new)
 ("date header",
  "Doc set is two: this reference = the system; `ante-machinam.md` = the craft.).*",
  "The evening session (17 June eve): three audio-chain bugs fixed (music never reached the batch path; music ducked under the voice; per-channel voice speed added), Prehistoric verified + 2 videos PUBLISHED, the Wild Horizons lane benchmark found, the upload scheduler designed. Doc set is two: this reference = the system; `ante-machinam.md` = the craft.).*"),

 ("music fixes",
  "Random-N gives variance across renders (two videos won't share a bed). The standalone `make_music.py`",
  "Random-N gives variance across renders (two videos won't share a bed). **Two mux bugs fixed 17 June eve (both silently shipping):** (1) the convergence music block referenced an undefined `channel_dir` -> NameError swallowed by a bare try/except -> silently `--no-music` on the batch path; fixed to derive `_channel_dir = proj.parent.parent` and drop the swallow (`patch_convergence_channeldir_fix.py`). (2) the `amix` had no `normalize` option -> ffmpeg's `normalize=1` default ducked music under loud narration and pumped it in pauses (intermittent music + too quiet); fixed with `amix=inputs=2:normalize=0:...` (`patch_amix_normalize.py`). **Validate audio END TO END for level, never a one-listen presence check.** The standalone `make_music.py`"),

 ("speakingRate",
  "Voices: Victor (Final Hours/Synthetic/hooks/**Prehistoric Disasters**), Elliot (Sacred Dawn), Ashley (Success Coach), Vinny (You Had To Be There). `voice_id` snake_case.",
  "Voices: Victor (Final Hours/Synthetic/hooks/**Prehistoric Disasters**), Elliot (Sacred Dawn), Ashley (Success Coach), Vinny (You Had To Be There). `voice_id` snake_case. **Per-channel voice speed (17 June eve, `patch_inworld_speaking_rate.py`):** the payload passes `speakingRate` inside `audioConfig`, read from `channel.json` `speaking_rate` (0.5-1.5, default 1.0 when absent -> other channels unchanged). Prehistoric = 0.9. Baked into `voiceover.mp3` (affects future renders only). The 'we slowed Victor for Final Hours' memory was FALSE — no speed key existed before this; all channels ran at 1.0."),

 ("quota",
  "Verify the account (youtube.com/verify, phone) before the first long upload — see §12.**",
  "Verify the account (youtube.com/verify, phone) before the first long upload — see §12.** **Quota (confirmed 17 June eve): the old 'six uploads/day' wall is GONE** — Google cut `videos.insert` from ~1,600 to ~100 units on 4 Dec 2025; 10,000/day now covers ~100 uploads/day. Batch uploads are a non-issue; stagger for AUDIENCE, not quota. **Scheduling (designed, not built):** upload private + `status.publishAt` and YouTube auto-publishes — NEVER public+publishAt (rejected); front-48h clock starts at `publishAt`. Design: `run_batch.py --publish-start <ISO+tz> --publish-interval-hours 12`, video N -> start + N*interval, `--plan` prints the calendar; Studio stays the review surface."),

 ("principle 13",
  "darken only the text zone with a directional gradient scrim, never the whole frame.**",
  "darken only the text zone with a directional gradient scrim, never the whole frame.**\n13. **Lane benchmark — flat high-floor beats the jackpot** (17 June eve). The Prehistoric lane benchmark is **Wild Horizons** (`UC0g0WbvanQND4dC1JDaW1_w`) — faceless AI-cinematic deep-time catastrophe, ~$4,300/mo, ~218K avg views/video in under a year, and **no outliers even at 1.3x**: a FLAT high floor (every video clears six figures), not a power-law jackpot. For a factory model a high floor beats a fat tail. Their ~32-min average (72-min biggest hit) says the lane rewards **long-form**. Chicxulub was algorithmically SUGGESTED next to it in Studio -> YouTube has classified the channel into the neighbourhood, positioned to draw its recommendation traffic."),

 ("current state",
  "**Specs written, not built:** decade-look Phase 2 (grade layer); Mission Control thumbnail integration (panel create-flow capture + review-time preview); per-project `publishAt` scheduling.",
  "**Shipped 17 June eve:** three audio-chain bugs fixed (channel_dir music, amix normalize=0, per-channel speakingRate — §6); Prehistoric LIVE (account verified, chicxulub re-run through the full process with music + 0.9 Victor + front-2 Kling, both Toba + Chicxulub PUBLIC); decisions banked (front-2 Kling = per-batch `--kling-count 2` flag not a baked default; the tiny-human silhouette STAYS, let comments rule it); Wild Horizons benchmark (§9 #13); upload scheduler designed.\n\n**Open (top of next):** read ep1 (Toba) + ep2 (Chicxulub) first-48h CTR + AVD vs the Wild Horizons ~218K floor (front-2-Kling hook lift, tight-vs-long-form decision); build the upload scheduler; then batch validated topics. Let the data drive.\n\n**Specs written, not built:** the upload scheduler (no-state, timestamp-in — designed this session); decade-look Phase 2; Mission Control thumbnail integration; faster final encode.\n\n**A fresh session starts here:** load the five `_`/`__` docs (this canonical, the worklog, ante-machinam, `_Prehistoric-Disasters.md`, machina). Everything is committed + pushed; the only open external action is reading the first-48h data, then building the scheduler, then a batch."),

 ("channel.json keys",
  "keys are `name`/`voice_id`/`style_suffix`/`default_motion`/`default_music_prompt`/`base_canon`/`upload`/**`thumbnail`**/**`music`**. Diff a new one",
  "keys are `name`/`voice_id`/`style_suffix`/`default_motion`/`default_music_prompt`/`base_canon`/`upload`/**`thumbnail`**/**`music`**/**`speaking_rate`** (optional float 0.5-1.5, default 1.0; Prehistoric=0.9). Diff a new one"),

 ("gotchas",
  "- **Two assemblers:** only `assemble_episode.py` is alignment-safe; `finish --assemble-only` drifts.",
  "- **Music mux (17 June eve):** the `amix` must carry `normalize=0` (else ffmpeg's `normalize=1` ducks music under the voice). Convergence derives the channel dir from `proj.parent.parent`, NOT a `channel_dir` var (never existed — old code silently ran `--no-music`). Validate audio end to end for level.\n- **Voice speed:** `channel.json` `speaking_rate` -> `speakingRate` in the Inworld `audioConfig`; baked into `voiceover.mp3` (audio-leg re-run to change).\n- **YouTube quota:** `videos.insert` ~100 units since 4 Dec 2025; ~100 uploads/day. Schedule via private + `status.publishAt` (NEVER public+publishAt).\n- **Re-run a project with new settings:** `ingest.create_project` refuses an existing project; `rm -rf` the project + re-ingest via `run_batch.py` (full re-render, ~$4 Ken-Burns — how chicxulub got music+0.9+Kling). For a free re-mux on an existing render use standalone `assemble_episode.py --music-dir …`.\n- **Two assemblers:** only `assemble_episode.py` is alignment-safe; `finish --assemble-only` drifts."),

 ("roster status",
  "**Launched, fully automated.** Stood up end to end 17 June: locked thumbnail look (`low_silhouette`), curated music library, batch-runner-produced. First video (Toba, 88 beats, 20.7 min) rendered + packaged + uploaded private — pending account verification (15-min cap) to publish. Slate of 19 topics queued (`prehistoric-slate-19.md`); ship Chicxulub as ep2, read data, then batch.",
  "**LIVE, fully automated.** Stood up + published 17 June: locked `low_silhouette` thumbnail, curated music, batch-runner-produced, Victor at 0.9. **Two videos public** (Toba ep1, Chicxulub ep2). 19-topic slate queued; read ep1+ep2 first-48h data before authoring the rest. Lane benchmark: Wild Horizons (§9 #13). Full doctrine: `_Prehistoric-Disasters.md`."),
]

def main():
    t = _find()
    if not t: sys.exit("FAIL: canonical not found next to script or in ./shared/docs/.")
    text = t.read_text()
    original = text
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present)."); return
    # verify all anchors first
    for label, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            sys.exit(f"FAIL: anchor '{label}' found {n} times (expected 1) — refusing. "
                     f"Paste the surrounding lines and I'll re-cut.")
    for label, old, new in EDITS:
        text = text.replace(old, new, 1)
    if SENTINEL not in text:
        sys.exit("FAIL: sentinel missing after edits — aborting.")
    bak = t.with_suffix(t.suffix + ".pre_0617eve")
    if not bak.exists(): bak.write_text(original)
    t.write_text(text)
    print(f"OK: patched {t.name} ({len(EDITS)} additions).")
    print("    Verify:  grep -n 'normalize=0\\|Wild Horizons\\|speaking_rate' shared/docs/__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md")

if __name__ == "__main__":
    main()
