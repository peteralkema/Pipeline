# Final Hours — Backlog
*Last updated: 30 May 2026*

The forward queue. Live state of in-flight work, decisions waiting on data, deferred pipeline improvements, and candidate videos. Read alongside `strategy.md` for the why.

---

## Live state

| Video | Published | Status | Notes |
|---|---|---|---|
| Pompeii v2 | 28 May | ~26 views in first 12h | Curve showed flat hours 0-6, climb hours 7-10, plateau — characteristic small-channel "early signal check then expand or settle" pattern |
| Anne Boleyn | 29 May | ~11 views, mid-window | Pushed early to X (~20 views) and SSC Facebook group (~4 reach) — cross-promotion was undisciplined, contaminates clean algorithmic read |
| Hartley (Titanic) | scheduled next 01:00 Europe/Warsaw | rendered, thumbnail done, captions attached | First video to use `--schedule-cet-1am` for optimal US-evening landing |

---

## Decisions waiting on data

These are the things you cannot decide right now; they depend on what the algorithm does over the next 1-3 weeks.

### After Hartley publishes — observe before acting

Don't push Hartley to social audiences in the first 48 hours. Let the algorithm cold-test. Specifically:

- Check Pompeii's retention curve at 72-hour mark (Studio Analytics → per-video → Audience retention). Curve shape diagnostic; view count is not.
- Check Anne's retention curve at 48-hour mark with the same lens.
- Check Hartley's first-hour signals when you wake up — was it actually published, is the impression-expansion happening, is anyone watching past 30 seconds.

### Cross-post Hartley to SSC group?

The dignity-under-pressure framing is a natural fit for a Success Coach community. Worth doing only *if* Hartley shows real algorithmic life at 48 hours. The framing for the post if/when it happens: open with one of the script's lines about the choice he made, position as a slow cinematic meditation on dignity under pressure, link the video. Should be the last cross-post in the Final Hours cycle for a while — three pushes to the same audience in a week is fatigue.

### Video four direction

Three principles for choosing:

1. **Build a topical cluster around whichever first-three video shows life.** If Hartley's Titanic frame gets distribution, the next video is also a maritime disaster — Lusitania, the Wilhelm Gustloff, the Andrea Doria. Topical clusters compound algorithmically much more than topic variety. If Pompeii shows life, next is another ancient-world catastrophe. If Anne shows life, next is another Tudor execution. If none of them move, choose freely.

2. **Use the canon mechanism from inception.** No retrofitting like Hartley. Write the canon block first, then the beat-script. Test the architecture now that it's been built.

3. **Avoid the Titanic-adjacent algorithmic neighbourhood for ~3 months** if Hartley doesn't break out. Chloe vs History's Titanic content is currently dominating that neighbourhood; piling in adds nothing useful while she's surging. Pick a different historical setting unless your Hartley shows it has its own pull.

Candidate topics worth scripting when ready (not ordered):

- The last hours of the people inside Pompeii's House of Menander (lavish interior we know who lived there)
- The Wilhelm Gustloff — 9,000+ deaths in the freezing Baltic, January 1945
- The Hindenburg landing at Lakehurst — the families on the ground waiting
- The Pompeii children at the Stabian baths (poignant skeletal posture preserved)
- The Lusitania bandmaster (literal Hartley parallel, gives canon mechanism a real test on an inherited character archetype)
- The Donner Party — winter in the Sierra Nevada, the day they made the decision
- The Mary Celeste — the empty ship found drifting, what happened to the ten people aboard
- The night Vesuvius woke — the family of Pliny the Elder watching from across the bay

These are scaffolding ideas, not commitments. Pick one based on algorithm signal after Hartley.

---

## Deferred build items (pipeline improvements)

Ordered by impact, not urgency. None of these are blocking. All are improvements that get easier the more videos you've shipped on the current architecture.

### Whisper-based SRT

Replace even-spacing caption timing (current implementation: `z = narration / clip_count`) with real speech-aligned timing via Whisper transcription. Current captions display drift against spoken words — words are still correctly indexed for SEO, only on-screen timing is off. Worth building when you start caring about captioned-watching audiences. Once built, retrofit caption tracks on already-published videos in Studio (no re-upload needed).

### Pre-render cost estimate

Print expected fal spend before `finish` runs, given the current fal credit balance. With auto-top-up enabled, a loop bug could silently burn meaningful credit. Soft guardrail. Roughly 30 lines of code: count beats, multiply by per-clip cost, print before starting render.

### Beat-multiples for rhythmic variation

Allow individual beats to be integer multiples of the base unit (most beats 1×, peak beats 2×) for rhythmic variation. Currently all beats are equal-length on the assembled video. Adding rhythm would let emotional peaks linger. Probably 50-100 lines of pipeline changes; not urgent.

### Cloud migration to Hetzner

Hetzner VPS ~€5/month for unattended overnight rendering. Auto-fallback is already proven (Anne Boleyn rendered unattended overnight on the laptop). Cloud migration just decouples render time from laptop availability. Requires: tmux/screen for persistent sessions, file transfer setup (rsync or SFTP), git for syncing the pipeline. Day-off task when ready. Worth doing before video count gets large enough that overnight laptop renders become annoying.

### Whisper retrofitting

Once Whisper-SRT is built, swap caption tracks on already-published videos in Studio (no re-upload required). Cosmetic improvement, low priority.

### Pipeline self-tests

`rulebook --count` flag to print rule counts instead of full dump (currently we pipe through Python for this). Possibly a `--validate` mode that checks env vars, channel.json structure, token file existence, fal connectivity. Small ergonomic wins, none blocking.

---

## Working principles for "when to revisit deferred items"

- Whisper-SRT becomes urgent when a viewer leaves a comment about caption drift, or when you start running paid ads to videos (where caption quality affects conversion).
- Pre-render cost estimate becomes urgent the first time a render unexpectedly costs significantly more than ~$30.
- Beat-multiples becomes useful when you've shipped 10+ videos and start feeling the even-spacing rhythm as a creative ceiling.
- Cloud migration becomes urgent when you're shipping >2 videos per week and laptop overnight renders block your morning workflow.
- Pipeline self-tests become useful when onboarding a second person (developer or VA) onto the workflow.

None of these are urgent today. The pipeline shipping 3 videos in 5 days with the current architecture is the proof point.

---

## Operating reminders

A few small things easy to forget across sessions:

- **The venv name is `success-coach`** for historical reasons (created when that was the active project). Serves both channels. Don't rename it; the path is hardcoded in muscle memory and shell aliases.
- **Channel detection is by `channel.json` marker**, found by walking up from CWD. `cd final-hours/` before running pipeline commands, or `cd success-coach/`. Both work; pipeline reads the channel context from wherever it is.
- **The thumbnail script writes `<project>/thumbnail.png`** which is exactly what `upload.py` looks for. No separate `--thumbnail` flag needed.
- **First run of `make_thumbnail.py` after an environment reset downloads the rembg U2Net model** (~170MB) into `~/.u2net/`. Takes 30-90 seconds the first time, 1-3 seconds thereafter.
- **`grep -c '_expand_canon\|_load_beats_with_canon'` on the pipeline** is a quick sanity check that the canon mechanism is in place; should return ~6 matches.
- **`shared/rulebook.json.pre_migration_backup` exists** from the 30 May rulebook split — pre-multi-channel snapshot, available if needed.
