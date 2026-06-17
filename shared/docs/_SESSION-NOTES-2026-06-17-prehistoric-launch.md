# SESSION NOTES — 17 June 2026 — Prehistoric Disasters channel launch (end to end)

*A dated session note kept as the deliberate exception (per the worklog's own discipline): a whole-channel launch is worth a deeper trace than a compressed RECORD block. The durable lessons have already graduated to the living docs (links below); this file is the index to the session's artifacts and the "how" of the day. Full operational/strategic detail lives in the docs — this is the map, not the territory.*

---

## What shipped (one line each)

- **A whole new channel, Prehistoric Disasters, stood up and proven end to end** — Ken-Burns-only (~$3/video), Victor voice, locked thumbnail look, 8-track curated music library, banner art, OAuth'd. First video (Toba, 88 beats, 20.7 min) rendered → packaged → uploaded private via the batch runner. Blocked from publishing only by YouTube's 15-min unverified-account cap.
- **Automated thumbnail pipeline** — Flux N=2 candidates → Sonnet-4-6 vision selects the best substrate on CTR rules → deterministic Pillow overlay (locked house look) → wired into convergence before upload. Built, tuned, LOCKED.
- **Unattended batch runner** — `auto` gate-mode + `--unattended` flag + `run_batch.py` (drives the real `ingest.create_project`). Proven `--plan` then `--limit 1`.
- **Music into convergence** — curated per-channel `--music-dir` (random-N + crossfade + loop), driven by a `channel.json` `music` block. Resolves the long-open generated-vs-curated decision in favour of curated.

## Where the durable lessons graduated (don't duplicate them here)

- **Canonical reference** (`__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md`): roster (+Prehistoric Disasters); §5.8 the unattended batch path; §6 the automated thumbnail pipeline + the curated-music decision; §9 the packaging principles (Ken-Burns-lanes-win-on-packaging corollary, thumbnail doctrine); §10 current state; §12/§13 the 15-min cap, the env-source rule, the script-format spec, the runtime calibration, the batch/thumbnail/music command references.
- **Ante-machinam** (`__ante-machinam.md`): §IV.6 runtime calibration (beat-floored, ~14s/beat); Part VI script-format-from-exemplar.
- **Worklog** (`__MASTER-WORKLOG.md`): 17 June RECORD block + reshuffled backlog (account-verification Tier-1, Mission Control thumbnail integration Tier-3 #11, faster-encode Tier-4 #18, per-project scheduling).
- **Channel doctrine** (`_Prehistoric-Disasters.md`): the full channel brief + the 19-topic launch backlog (§8).

## Key artifacts (the "how" of the day)

Scripts / slate (in Peter's outputs, deploy to the channel as authored):
- `prehistoric-slate-19.md` — the ranked 19-topic launch backlog (also lives as §8 of the channel doctrine). Ship-next: Chicxulub (ep2), Permian "96% DEAD", Lost Human Species.
- `toba.md` — the 88-beat shipped script (~20.7 min). Correct format (the second, working version).
- `toba-full.md` — the expanded ~28-min-words-estimate version (climax trio weighted deepest, likely ~40 min real). HELD for the real publish pending the 88-vs-expanded decision.

Code (committed to the repo; full source there, sentinel-guarded idempotent patches):
- `shared/patch_gate_auto.py` — adds the `auto` gate-mode to `await_gate`.
- `shared/patch_orchestrate_unattended.py` — adds `--unattended` + `auto` to `--gate-mode` choices.
- `shared/run_batch.py` — the batch runner (inbox of `<name>.md` + `<name>.thumb.json` pairs).
- `shared/patch_music_dir.py` — adds `--music-dir` (random-N + crossfade + loop) to `assemble_episode.py`.
- `shared/patch_convergence_musicdir.py` — drives the music-dir from the `channel.json` `music` block.
- `shared/make_thumbnail.py`, `shared/select_thumbnail_still.py`, `shared/patch_convergence_thumbnail.py` — the thumbnail pipeline (built earlier, locked this session).

Config:
- `prehistoric-disasters/channel.json` — the locked channel identity (voice, style_suffix, `kling_count:0`, full thumbnail + music + upload blocks).
- `prehistoric-disasters/music/` — 8 ominous beds, normalized `track_NN.mp3`.
- `prehistoric-disasters/token.json` + `client_secret.json` — OAuth, bound to @PrehistoricDisasters.

## The blocker and the next move

Toba uploaded private but YouTube rejected it: **"Processing abandoned — video too long"** (unverified account = 15-min cap). NEXT: verify the account (youtube.com/verify, phone) → delete the abandoned upload → re-assemble Toba WITH music (the render predated the music wiring) → re-run `upload_episode.py --project prehistoric-disasters/projects/toba` → publish. Then ship Chicxulub as ep2, read ep1+ep2 first-48h CTR+AVD before authoring the other 18.

## The single richest "how" source

The full conversation transcript of this session (the build order, every command, the tuning loops, the diagnoses). If a detail isn't in the docs above, it's in the transcript.

---

*Full detail in the four living docs + the patch sidecars (`.pre_*` backups on the box). This note is the index; the docs are the reference.*
