# Backlog addendum — Music

*Append to `shared/docs/` backlog (e.g. success-coach-backlog / final-hours-backlog or a shared backlog).*

## Music generation gap (added 7 June 2026)

**Status:** the assembler's music MUX is ready; music GENERATION is not wired to the new model.

- `assemble_episode.py` already accepts a music bed: `--music <file>` or auto-finds `<project>/music.mp3`,
  loops it to cover the voice length, mixes at VOICE_LEVEL 1.15 / MUSIC_LEVEL 0.07, output pinned to
  voice length. Mux is DONE and validated. Default run used `--no-music`.
- What's missing: `music_score.py` (Jamendo; crossfades; needs `music_category` + `JAMENDO_CLIENT_ID`)
  reads the OLD 41-shot storyboard shape, not the new per-beat / per-episode timing. It must be adapted
  to the 62-beat episode (drive cue length + crossfades from `durations.json` / total voice length, not
  from a storyboard).

**Next-session task when picked up:**
1. Read `music_score.py` fully (it predates the cleanup).
2. Re-point it at the episode timing: total = voice length (`durations.json` sum); it just needs to
   produce one bed (or a few crossfaded tracks) that covers that length — the assembler handles looping.
3. Produce `<project>/music.mp3`, then assemble WITHOUT `--no-music` to hear it under the narration.
4. Calibration already banked: VOICE_LEVEL 1.0–1.15, MUSIC_LEVEL ~0.07 (bed sits low under voice).

Priority: lower than (a) the channel-resolution fix + full live orchestrator run, and (b) Mode B
within-card word-sync. Music is polish on an already-working assembled video.
