#!/usr/bin/env python3
"""
patch_worklog_2026-06-19.py — APPEND the full 19 June day (morning build + afternoon
multi-channel run) to __MASTER-WORKLOG.md: a RECORD block + backlog updates (slug rule,
thumbnail-upload retry gap, re-ingest, --plan slug-check gap, music box-local).
Anchor-verified, idempotent (sentinel), refuses on miss. Append-only.

Run on LAPTOP:  python3 shared/docs/patch_worklog_2026-06-19.py
"""
import sys
from pathlib import Path

def _find():
    here = Path(__file__).resolve().parent
    for c in [here/"__MASTER-WORKLOG.md", Path.cwd()/"shared/docs/__MASTER-WORKLOG.md"]:
        if c.exists(): return c
    return None

SENTINEL = "19 June 2026 — the batch-of-batches"

RECORD_ANCHOR = "# THE RECORD (compressed, newest first)"

RECORD_BLOCK = '''# THE RECORD (compressed, newest first)

_Each block: date \u00b7 what shipped \u00b7 what it left open (now tracked in THE BACKLOG above). Durable lessons have graduated to the canonical (\u00a7-refs) / ante-machinam; this is the index, not the detail._

### 19 June 2026 \u2014 the batch-of-batches, music across four channels, thumbnail word-fit, first multi-channel run
The day the factory ran many channels in one launch. Built the driver, rolled music onto four channels, fixed a thumbnail bug, and ran a real multi-channel scheduled batch end to end \u2014 catching several production-grade gaps live.

**The batch-of-batches (`run_all_batches.py`, built + proven).** A thin sequential driver over `run_batch.py`: reads `batch_plan.json` (one entry per channel \u2014 channel, inbox, kling_count, publish_start, interval, skip), runs each channel's batch in turn, isolates per-channel failures, passes `--plan` through for a zero-spend dry-run of every channel's calendar, writes a combined manifest, exits non-zero if any failed. Sequential by design. The inbox convention is now uniform: every channel owns `<channel>/batch_inbox/`. \u2192 canonical \u00a75.9.

**Music rolled onto four channels.** Curated per-channel `music/` libraries (8 tracks each, normalized `track_NN.mp3`) + the `channel.json` `music` block, now live on Prehistoric Disasters, You Had To Be There, Scripture On Screen, Final Hours \u2014 all on the identical proven config (`{dir:music,tracks:3,crossfade_seconds:2,level:0.07}`). **Banked: music is BOX-LOCAL, not git** \u2014 `.gitignore:78` is `*.mp3`, so libraries are scp'd to the box, never committed (repo tracks only the `channel.json` block). Caused an empty-commit + fast-forward-reject confusion mid-session; the rule is "music = scp, config = git." **The `level` key in the music block is currently INERT** \u2014 the mux reads a hardcoded `MUSIC_LEVEL = 0.07` constant in `assemble_episode.py:61`, not the block; per-channel level would need wiring (deliberately not built \u2014 0.07 is the proven global). 0.07 is still unverified by ear on the three new channels.

**Thumbnail word-break fixed (`patch_thumbnail_nobreak.py`).** A Scripture thumbnail rendered "HE LOST E / VERYTHING" \u2014 `_fit_text` wrapped via `textwrap.wrap()` with no break flags, chopping a long word at the char limit. Fix: `break_long_words=False, break_on_hyphens=False` on both wrap calls; the existing shrink-to-fit loop then shrinks the font until the unbroken word fits. Structural fix in the shared `make_thumbnail.py` \u2014 EVERY channel inherits it. \u2192 canonical \u00a76.

**First multi-channel scheduled run \u2014 launched, corrected, relaunched.** A 20-video run across Final Hours / YHTBT / Scripture / Cathedral. First attempt was killed mid-flight and corrected for a timezone error (below); franklin-expedition + herculaneum shipped from an earlier proof and were pulled to `_shipped/`. After correction, FH (5) + YHTBT (3) + Scripture (3) shipped; **Cathedral's 9 all prep-failed on the slug rule** (below) \u2014 caught at zero spend. Renamed + relaunched with Sacred Dawn (10) added: a 20-video run (lady-be-good 1 + Cathedral 9 + Sacred Dawn 10). **LIVE-STATE: confirm the run's manifest (X/20) + spot-check Studio (private + correct schedule + thumbnail attached) when it completes.**

**Banked this session (durable, \u2192 canonical):**
- **Slug rule: filenames must be `^[a-z0-9][a-z0-9-]{0,60}$`** \u2014 lowercase letters/numbers/hyphens, start alphanumeric, no underscores, no `NN_` prefixes. `create_project` (`mission_control/ingest.py:validate_slug`) refuses otherwise, at the slug stage, BEFORE any spend. Cathedral's `02_ton-618`\u2026 and three Sacred Dawn scripts (`elijah_carmel`, `sun_stood_still`, `ten_plagues`) failed this; fix is `_`\u2192`-` rename of both pair members. **Bake into the authoring checklist.** \u2192 canonical \u00a712 + ante-machinam.
- **`--plan` does NOT catch slug errors** \u2014 it skips the real `create_project`, so a bad filename sails through the dry-run as "planned" then fails at real-run time. The dry-run validates inboxes + schedules but not slugs. Pre-run slug scan: `for f in <inbox>/*.md; do basename "${f%.md}" | grep -qE '^[a-z0-9][a-z0-9-]*$' || echo BAD; done`. (Backlog: `--plan` should run `validate_slug` on each stem.) \u2192 canonical \u00a75.9 + Tier 2.
- **Channel-header vs folder slug** \u2014 `cathedral_of_stars` uses an underscore slug (folder + script headers agree); `sacred_dawn` headers auto-resolve to the `sacred-dawn/` folder; the rest are hyphenated. The plan's `channel` must match the FOLDER; the script `channel:` header must match what the orchestrator resolves. An empty hyphen-`cathedral-of-stars` stub created by mistake had to be deleted. Resolve identity explicitly \u2014 check the folder AND the header.
- **The timezone +02:00 summer trap** \u2014 a scheduled `publish_start` written `+01:00` (winter CET) in June schedules an hour later than intended (01:00 typed as `+01:00` displays as 02:00 in Studio; the actual summer offset is CEST/`+02:00`). Caught after a video showed 02:00; fixed the whole plan to `+02:00`. \u2192 canonical \u00a75.9.
- **The render-vs-publish race** \u2014 a scheduled video only honors `publishAt` if it finishes uploading before that instant; a start too close to "now" means a late-in-queue video uploads past its slot and YouTube publishes it immediately. Date the earliest start far enough ahead for the queue to clear. \u2192 canonical \u00a75.9.

**Two open gaps surfaced (Tier 2):**
- **Re-ingest:** `run_batch.py` writes a manifest but does NOT move shipped pairs out of the inbox \u2014 a re-run re-renders + re-uploads (duplicates) everything still in `batch_inbox`. Until closed, move shipped pairs to `<inbox>/_shipped/` by hand before re-running. Durable fix (decided to live at the channel-batch level, `run_batch.py`): auto-archive to `_shipped/` on `ok=True` only. Patch drafted (`patch_batch_archive_shipped.py`), NOT applied (don't change the machine mid-run).
- **Thumbnail-set is fire-once, no retry, failure not surfaced.** `upload_episode.py` uploads the video (line 257) then sets the thumbnail in a SEPARATE call (line 262); if that call fails/skips, the video ships with the auto-grab and nothing errors. Hit noahs-flood (thumbnail.png was perfect on disk, 1MB, just never attached). Also: the **video ID is never persisted to the project**, so there's no on-disk link from project \u2192 uploaded video to fix it after the fact. Fix path: a standalone `set_thumbnail.py` (video ID + png \u2192 `thumbnails().set()`, no re-upload) + persist the video ID + retry the set call. For now, re-set by hand in Studio.

\u2192 canonical roster + \u00a75.8/\u00a75.9 (batch + batch-of-batches), \u00a76 (music box-local, thumbnail word-fit), \u00a712 (slug/timezone/re-ingest/thumbnail-upload gotchas).'''

DATE_OLD = "_Last updated: 17 June 2026 (evening \u2014 audio-chain fixes, Prehistoric live, scheduler designed)._"
DATE_NEW = "_Last updated: 19 June 2026 (batch-of-batches built + launched; music on four channels; thumbnail word-fit; first multi-channel run)._"

SCHED_OLD = """2. **Build the upload scheduler** (Tier-4 #18 below, promoted to do-next) \u2014 no-state, `--publish-start <ISO+tz>` + `--publish-interval-hours` in `run_batch.py`, each video uploaded private with a computed `publishAt`, YouTube auto-publishes. Then a batch is hands-off. Design banked below."""
SCHED_NEW = """2. **Read the live multi-channel run + close the gaps it surfaced.** The 20-video run (lady-be-good + Cathedral 9 + Sacred Dawn 10) launched 19 June. When it completes: check the manifest for \u2717, spot-check Studio (private + correct 01:00 `+02:00` schedule + **thumbnail attached** \u2014 the thumbnail-set call can silently fail), and before ANY next run move shipped pairs out of the inboxes (re-ingest gap). The scheduler + batch-of-batches SHIPPED 19 June. **Three real gaps to close (Tier 2):** (a) re-ingest auto-archive in `run_batch.py`; (b) thumbnail-set retry + persist video ID + a standalone `set_thumbnail.py`; (c) `--plan` should run `validate_slug` so bad filenames fail cheap."""

def main():
    t = _find()
    if not t: sys.exit("FAIL: __MASTER-WORKLOG.md not found next to script or in ./shared/docs/.")
    text = t.read_text()
    original = text
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present)."); return
    edits = [("record block", RECORD_ANCHOR, RECORD_BLOCK),
             ("date", DATE_OLD, DATE_NEW),
             ("scheduler tick", SCHED_OLD, SCHED_NEW)]
    for label, old, new in edits:
        n = text.count(old)
        if n != 1:
            sys.exit(f"FAIL: anchor '{label}' found {n} times (expected 1) \u2014 refusing. "
                     f"Paste the surrounding lines and I'll re-cut.")
    for label, old, new in edits:
        text = text.replace(old, new, 1)
    if SENTINEL not in text:
        sys.exit("FAIL: sentinel missing after edits \u2014 aborting.")
    bak = t.with_suffix(t.suffix + ".pre_0619")
    if not bak.exists(): bak.write_text(original)
    t.write_text(text)
    print(f"OK: patched {t.name} (3 edits: record block + date + scheduler tick).")
    print("    Verify:  grep -n 'batch-of-batches\\|slug rule\\|thumbnail-set is fire-once\\|box-local' shared/docs/__MASTER-WORKLOG.md")

if __name__ == "__main__":
    main()
