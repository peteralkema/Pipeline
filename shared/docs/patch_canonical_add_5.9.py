#!/usr/bin/env python3
"""
patch_canonical_add_5.9.py — INSERT section 5.9 (the batch-of-batches) before section 6,
AND add 19 June gotchas to section 12 (slug rule, music box-local, thumbnail-set fire-once).
Anchor-verified, idempotent (sentinel), refuses on miss. Append-only.

Run on LAPTOP:  python3 shared/docs/patch_canonical_add_5.9.py
"""
import sys
from pathlib import Path

def _find():
    here = Path(__file__).resolve().parent
    for c in [here/"__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md",
              Path.cwd()/"shared/docs/__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md"]:
        if c.exists(): return c
    return None

SENTINEL = "### 5.9 The batch-of-batches"

ANCHOR_6 = "## 6. The tech stack (the fast layer \u2014 swappable)"

SECTION = '''### 5.9 The batch-of-batches \u2014 many channels, one launch (shipped 19 June)

`run_batch.py` (\u00a75.8) ships one channel's inbox. **`run_all_batches.py`** ships *every* channel's inbox in one launch \u2014 a thin sequential driver over `run_batch.py` so a multi-channel release doesn't have to be kicked off by hand. All the real work still happens inside `run_batch.py`; the batch-of-batches just loops it.

**The two-level model:** a **batch** = one channel's `batch_inbox` \u2192 N videos; a **batch-of-batches** = a list of channels each run as its own batch, **one after another in sequence** (`run_all_batches.py --plan-file <plan>`). Sequential, never parallel \u2014 no human watching, and N concurrent channels would mean N concurrent fal/Inworld/encode bursts on a 16GB box. A 4-channel / 20-video run is one long sequential job \u2014 run it in `tmux`.

**The inbox convention (the contract):** every channel owns its inbox at **`<channel>/batch_inbox/`** \u2014 the channel-local folder of `<name>.md` + `<name>.thumb.json` pairs, so a channel runs identically standalone or inside the batch-of-batches. Create the folder for every channel even if it sits out a run.

**The plan file (`batch_plan.json`):** the driver reads a JSON config so the *script never changes*; you edit the plan (via a `python3 -c` one-liner). Each entry: `channel` (required \u2014 must match the channel FOLDER and the `channel:` header inside that channel's scripts), `inbox` (`<channel>/batch_inbox`), `kling_count` (default 0), `publish_start` (ISO-8601 **with tz offset**; omit for private-immediate \u2014 each channel carries its OWN start), `publish_interval_hours` (default 12), `limit`, `skip`.

**Invocation \u2014 always `--plan` first:**
```
python shared/run_all_batches.py --plan-file shared/batch_plan.json --plan   # dry: every channel, zero spend, prints each calendar
python shared/run_all_batches.py --plan-file shared/batch_plan.json          # real, all active channels in sequence (tmux)
python shared/run_all_batches.py --plan-file shared/batch_plan.json --only <channel>   # one channel
```
`--plan` passes through to each `run_batch.py` (prep preview, no spend) and doubles as a readiness check: a missing/empty inbox or bad plan shows up as a per-channel \u2717 with zero spend. **But `--plan` does NOT validate slugs** \u2014 it skips the real `create_project`, so a bad filename (see below) sails through as "planned" then prep-fails at real-run time. Run a slug scan before spending: `for f in <inbox>/*.md; do basename "${f%.md}" | grep -qE '^[a-z0-9][a-z0-9-]*$' || echo BAD; done`. (Backlog: fold `validate_slug` into `--plan`.)

**Failure isolation + manifest:** each channel runs in its own try/except; one channel failing is logged \u2717 and the driver moves on. Combined `all_batches_manifest_<ts>.json` + \u2713/\u2717 summary; exits non-zero if any failed. (Note: an empty inbox reports \u2717 "no .md scripts" \u2014 that's "nothing pending," not a breakage.)

**Banked operational lessons (19 June, from the first real multi-channel run):**
- **Slug rule \u2014 `^[a-z0-9][a-z0-9-]{0,60}$`.** Project slugs (filenames) must be lowercase letters/numbers/hyphens, start alphanumeric, no underscores, no `NN_` prefixes \u2014 `create_project` (`mission_control/ingest.py:validate_slug`) refuses otherwise, at the slug stage BEFORE any spend. Cathedral's `02_ton-618`\u2026 and three Sacred Dawn scripts failed this; fix is a `_`\u2192`-` rename of both pair members. (Bake into the authoring checklist.)
- **Slug must match folder AND header.** `cathedral_of_stars` uses an underscore slug because its folder + script `channel:` headers agree; `sacred_dawn` headers auto-resolve to the `sacred-dawn/` folder; the rest are hyphenated. The plan's `channel` matches the FOLDER; the header must match what the orchestrator resolves. Resolve identity explicitly \u2014 an empty hyphen-stub created by mistake had to be deleted.
- **The timezone +02:00 summer trap.** A scheduled video is uploaded `privacyStatus: private` WITH `status.publishAt`; YouTube auto-flips it public. `publish_start` is an absolute instant, so **the offset must be the channel's actual wall-clock offset on the publish date** \u2014 in summer that is **`+02:00`** (CEST), not winter `+01:00`. `+01:00` in June schedules an hour later than intended (01:00 displays as 02:00). Verify the `--plan` local time is what you want; the UTC line sits the right hours behind.
- **The render-vs-publish race.** A scheduled video only honors `publishAt` if it finishes uploading before that instant. With many videos rendering sequentially, a start too close to "now" means a late video uploads past its slot and YouTube publishes it immediately. Date the earliest start far enough ahead for the queue to clear.

**Open gap \u2014 re-ingest (Tier 2):** `run_batch.py` writes a manifest but **does not move shipped pairs out of the inbox**, so a re-run re-renders + re-uploads (duplicates) everything still in `batch_inbox`. Until closed, move a shipped pair to `<inbox>/_shipped/` by hand before re-running. Durable fix: auto-archive on `ok=True` only, built into `run_batch.py` (so it fires for direct single-channel runs too) \u2014 belongs at the channel-batch level, not the wrapper.

**Open gap \u2014 thumbnail-set fire-once (Tier 2):** `upload_episode.py` uploads the video then sets the thumbnail in a SEPARATE call; if that call fails/skips, the video ships with the auto-grab and nothing errors (hit noahs-flood \u2014 thumbnail.png perfect on disk, just never attached). The video ID is also never persisted to the project. Fix: persist the video ID, retry the set call, and a standalone `set_thumbnail.py` (video ID + png \u2192 `thumbnails().set()`, no re-upload). For now, re-set by hand in Studio.

**Re-running after a partial/aborted run:** videos already shipped are private+scheduled in Studio AND still in the inbox. Either (A) delete the shipped Studio uploads, leave the pairs for a fresh re-render; or (B) keep the uploads, move their pairs to `_shipped/`, and set the re-run's `publish_start` past the kept slots so the calendar doesn't collide. `ingest.create_project` refuses an existing project, so a true re-render needs `rm -rf <channel>/projects/<slug>` first.

---

'''

# §12 gotcha additions — append after the existing 'Two assemblers' line (a stable late-§12 anchor)
G_ANCHOR = "- **Mac-only SSL:** monkey-patch `httpx.Client.__init__` to `verify=False` before fal imports; not needed on the box."
G_NEW = '''- **Slug rule:** project filenames must be `^[a-z0-9][a-z0-9-]{0,60}$` (lowercase/digits/hyphens, start alphanumeric, NO underscores, no `NN_` prefix). `create_project` refuses otherwise at zero spend. `--plan` does NOT catch this \u2014 slug-scan the inbox first.
- **Music is box-local:** `*.mp3` is gitignored (`.gitignore:78`), so per-channel `music/` libraries are scp'd to the box, never committed; the repo tracks only the `channel.json` `music` block. The block's `level` key is inert \u2014 the mux uses hardcoded `MUSIC_LEVEL = 0.07` in `assemble_episode.py:61`.
- **Thumbnail-set can silently fail:** `upload_episode.py` sets the thumbnail in a separate call after upload; a failed/skipped set ships the video with the auto-grab and does NOT error. Video ID isn't persisted to the project. Re-set by hand in Studio (pull `thumbnail.png` via scp) until the retry + `set_thumbnail.py` fix lands.
- **Mac-only SSL:** monkey-patch `httpx.Client.__init__` to `verify=False` before fal imports; not needed on the box.'''

def main():
    t = _find()
    if not t: sys.exit("FAIL: canonical not found next to script or in ./shared/docs/.")
    text = t.read_text()
    original = text
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present)."); return
    edits = [("5.9 insert (before \u00a76)", ANCHOR_6, SECTION + ANCHOR_6),
             ("\u00a712 gotchas", G_ANCHOR, G_NEW)]
    for label, old, new in edits:
        n = text.count(old)
        if n != 1:
            sys.exit(f"FAIL: anchor '{label}' found {n} times (expected 1) \u2014 refusing. "
                     f"Paste the surrounding lines and I'll re-cut.")
    for label, old, new in edits:
        text = text.replace(old, new, 1)
    if SENTINEL not in text:
        sys.exit("FAIL: sentinel missing after edits \u2014 aborting.")
    bak = t.with_suffix(t.suffix + ".pre_5p9")
    if not bak.exists(): bak.write_text(original)
    t.write_text(text)
    print(f"OK: patched {t.name} (\u00a75.9 inserted + \u00a712 gotchas added).")
    print("    Verify:  grep -n '5.9 The batch-of-batches\\|Slug rule\\|Music is box-local\\|Thumbnail-set can silently' shared/docs/__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md")

if __name__ == "__main__":
    main()
