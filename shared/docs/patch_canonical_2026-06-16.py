#!/usr/bin/env python3
"""
patch_canonical_2026-06-16.py - bring the canonical reference current after the
16 June session (motion root-fix + upload live across five channels + the
v1.2-v1.9 Mission Control arc the doc never absorbed).

Anchored, all-or-nothing: every anchor is verified to occur exactly once on the
ORIGINAL text before a single byte is written; any miss aborts with the offending
label and writes nothing. Backs up to .pre_canon0616; sentinel-gated idempotency.

Run from the repo root on the LAPTOP, then commit/push, then git pull --no-edit on
the box. (Doc-only change - no service restart, no node-check needed.)
"""
import sys
import shutil
from pathlib import Path

DOC = Path("shared/docs/_YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md")
SENTINEL = "Last updated: 16 June 2026"

EDITS = []  # (label, old, new)

# ── A. Header dateline ───────────────────────────────────────────────────────
EDITS.append(("header dateline",
"""*Maintained by Peter + Claude. Last updated: 15 June 2026 (Mission Control at v1.1: audio\u2192stills seam fix + decided-gate stale guard, and a Re-assemble button. Doc set consolidated to two: this reference = the system; `ante-machinam.md` = the craft.).*""",
"""*Maintained by Peter + Claude. Last updated: 16 June 2026 (Mission Control at v1.9. This session: the `default_motion` dead-default fixed at its true source (`modea_beats.py`), and **upload wired end-to-end across five channels** \u2014 `upload_episode.py` proven on a real private upload, the 7-day token expiry killed by publishing the OAuth app to Production, and the Mission Control Upload button live (private-only). Doc set is two: this reference = the system; `ante-machinam.md` = the craft.).*"""))

# ── B/C. Roster rows ─────────────────────────────────────────────────────────
EDITS.append(("roster Sacred Dawn",
"""| **Sacred Dawn** (@sacredawn) | The Bible's cosmic & primeval drama \u2014 the Watchers, the Nephilim, the Flood, Creation, the war in heaven \u2014 as cinematic recreation. "The Bible's origin story, brought to life through cinematic recreation." Reverent, never sensational | Mode A only | **Elliot** (British, deep, liturgical) | **Live, newest.** Launched 10\u201311 June with "Before the Flood: The True Story of the Nephilim and the Watchers." Upload manual (Entertainment / private). The highest-fit use of the machine found to date \u2014 see \u00a79.3. Full doctrine: `sacred-dawn-creed.md`. |""",
"""| **Sacred Dawn** (@sacredawn) | The Bible's cosmic & primeval drama \u2014 the Watchers, the Nephilim, the Flood, Creation, the war in heaven \u2014 as cinematic recreation. "The Bible's origin story, brought to life through cinematic recreation." Reverent, never sensational | Mode A only | **Elliot** (British, deep, liturgical) | **Live, newest.** Launched 10\u201311 June with "Before the Flood: The True Story of the Nephilim and the Watchers." Upload now via the Mission Control button (private; Production token bound to the Sacred Dawn channel, \u00a75.5/\u00a75.7). The highest-fit use of the machine found to date \u2014 see \u00a79.3. Full doctrine: `sacred-dawn-creed.md`. |"""))

EDITS.append(("roster Scripture",
"""| **Scripture on Screen** (@scripture_on_screen) | Scripture rendered as cinematic recreation \u2014 narrative books of the Bible brought to life beat by beat (Esther in production); a sibling lane to Sacred Dawn with its own register | Mode A only | (dramatic `default_motion` set) | **In production.** First project: Esther (119 beats, ~26 min). Channel has a good dramatic `default_motion`; per-project motion still hot-fixed until the dead-default root fix lands (\u00a75.3). |""",
"""| **Scripture on Screen** (@scripture_on_screen) | Scripture rendered as cinematic recreation \u2014 narrative books of the Bible brought to life beat by beat (Esther in production); a sibling lane to Sacred Dawn with its own register | Mode A only | dramatic `default_motion` (now channel-resolved) | **In production.** First project: Esther (119 beats, ~26 min). Dramatic `default_motion` now fires automatically (the dead-default root fix landed, \u00a75.3 \u2014 no more per-project motion hot-fix). Upload token authed (Production, bound to the Scripture On Screen channel). |"""))

EDITS.append(("roster Synthetic",
"""| **Synthetic Press** | AI-era human drama \u2014 AI-*drama* not AI-doom; real boardrooms, founding dinners, 2am calls, dramatised as cinema; mouths closed (no lip-sync) | **Dual-mode (A + B)** \u2014 cinematic recreation + Remotion motion-graphics for evidence/quotes/numbers | Peter's own broadcast read (marquee) + Victor (scratch) | **Flagship, launching.** Render side proven end-to-end; upload/OAuth not set up. `channel: synthetic` (alias trap). |""",
"""| **Synthetic Press** | AI-era human drama \u2014 AI-*drama* not AI-doom; real boardrooms, founding dinners, 2am calls, dramatised as cinema; mouths closed (no lip-sync) | **Dual-mode (A + B)** \u2014 cinematic recreation + Remotion motion-graphics for evidence/quotes/numbers | Peter's own broadcast read (marquee) + Victor (scratch) | **Flagship, launching.** Render side proven end-to-end; upload token authed (Production, bound to the Synthetic Press channel). `channel: synthetic` (alias trap). |"""))

# ── §5 convergence_leg ───────────────────────────────────────────────────────
EDITS.append(("convergence_leg publish-half",
"""- **convergence_leg**: pool clips \u2192 `assemble_episode.py` (interleave in true beat order via index map, hold each to audio-measured duration, mux ducked music bed) \u2192 `final_video.mp4`. (Publish half \u2014 thumbnail gate, schedule gate, upload \u2014 built for some channels, not all.)""",
"""- **convergence_leg**: pool clips \u2192 `assemble_episode.py` (interleave in true beat order via index map, hold each to audio-measured duration, mux ducked music bed) \u2192 `final_video.mp4`. (Publish half: **upload is built and live across five channels** via the Mission Control button \u2192 `upload_episode.py` (\u00a75.5/\u00a75.7); thumbnail gate + schedule control remain manual/optional.)"""))

# ── §5.1 version + Re-assemble parenthetical ─────────────────────────────────
EDITS.append(("§5.1 version sentence",
"""`APP_VERSION` is hand-bumped on every shipped page change and pairs with the auto SHA; **Mission Control is v1.1.**""",
"""`APP_VERSION` is hand-bumped on every shipped page change and pairs with the auto SHA; **Mission Control is v1.9** (the v1.2\u2013v1.9 arc \u2014 the aligned-Re-assemble drift fix, the A/B/C reliability hardening, and the live Upload button \u2014 is in \u00a75.7)."""))

EDITS.append(("§5.1 Re-assemble parenthetical",
"""**FINAL VIDEO panel** (shipped, see \u00a75.5) with a **Re-assemble button** (re-stitch the final video from the current clips via `finish --assemble-only`, no render cost \u2014 so re-rendering a clip and rebuilding the video is a two-click loop; the future home for music options).""",
"""**FINAL VIDEO panel** (shipped, see \u00a75.5) with a **Re-assemble button** (re-stitch the final video from the current clips, no render cost; as of v1.2 it routes through the ALIGNED assembler `assemble_episode.py` + `_index.json`, NOT `finish --assemble-only` which drifts \u2014 see the two-assemblers principle in \u00a75.7) and a live **Upload button** (v1.9, private-only)."""))

# ── §5.3 motion: open-bug paragraph -> FIXED ─────────────────────────────────
EDITS.append(("§5.3 motion fixed",
""" **Proven on Sacred Dawn:** a dramatic default ("dramatic motion, maximise elements of movement and interplay on scene, dramatic lighting effects. pan and zoom in") read markedly better than the global slow default \u2014 fast/dramatic motion is the right register for the channel; yellow/slow is not. *Known bug to fix (banked): the per-channel `default_motion` is currently **inert** because the storyboard-authoring step always populates per-beat `motion_prompt` (slow) and the build prefers the beat's own value over the channel default \u2014 the `or` never reaches it. Principle: **a per-channel default is dead if an upstream step always fills the field it defaults.** Fix = make the authoring guidance channel-aware. (`pan` only acts on Kling clips, not Ken-Burns floor clips.)*""",
""" **Proven on Sacred Dawn:** a dramatic default ("dramatic motion, maximise elements of movement and interplay on scene, dramatic lighting effects. pan and zoom in") read markedly better than the global slow default \u2014 fast/dramatic motion is the right register for the channel; yellow/slow is not. **FIXED 16 June (`patch_modea_beats_motion_omit.py`, sentinel `motion omitted when not face-hold`).** The dead-default lived in the PRODUCER, not the consumer: `modea_beats.py translate()` stamped every non-face-hold beat with the slow `DEFAULT_MOTION`, so `cmd_stills`'s correct `b.get("motion_prompt") or _default_motion` fall-through never fired. (Three layers \u2014 producer / consumer / Mission Control typed-box; a prior `patch_default_motion.py` had fixed the latter two, and the unfixed producer was first in the chain, so it always won.) Fix: `translate()` now OMITS `motion_prompt` on normal beats and writes it only for face-hold beats (`FACEHOLD_MOTION`); the channel's `default_motion` then resolves automatically. Proven end-to-end on Sacred Dawn (`all dramatic: True` across 52 beats, run from inside the channel folder). **Durable principle (banked): a per-channel default is dead if any upstream step unconditionally fills the field it defaults \u2014 make "nothing authored" representable as ABSENT, not a placeholder, so the default's fall-through can fire.** Scope: only the front N=40 Kling beats visibly change (Ken-Burns floor ignores motion); forward-only (storyboards already on disk are untouched). (`pan` only acts on Kling clips, not Ken-Burns floor clips.)"""))

# ── §5.5 panel: Upload disabled -> wired ─────────────────────────────────────
EDITS.append(("§5.5 panel",
"""### 5.5 FINAL VIDEO panel \u2014 the first piece of the upload surface

When a run reaches `done` (or a finished project is opened), a **FINAL VIDEO \u2014 UPLOAD TO STUDIO** panel fills the page's top-right (the wireframe's third corner of the U). The top region is a two-column flex row (`#topgrid`, capped at 1500px): controls (create + launch) left, the panel slot (`#toppanel`) right; storyboard stays full-width below. The panel shows the **assembled video autoplaying** in-page (served by the existing `/video/` route, base corrected to the project root where `final_video.mp4` lives), **title / description / tags** pulled live from the `beats_full.json` header via a new `/api/meta` route, and a **working Download button** (no auth needed). The **Upload button is present but disabled** \u2014 it needs `auth.py` fixed + `/api/upload`, which is the next session's build. When no finished video exists the slot shows a faint placeholder so the space never reads as broken.""",
"""### 5.5 FINAL VIDEO panel \u2014 the upload surface (now live)

When a run reaches `done` (or a finished project is opened), a **FINAL VIDEO \u2014 UPLOAD TO STUDIO** panel fills the page's top-right (the wireframe's third corner of the U). The top region is a two-column flex row (`#topgrid`, capped at 1500px): controls (create + launch) left, the panel slot (`#toppanel`) right; storyboard stays full-width below. The panel shows the **assembled video autoplaying** in-page (served by the `/video/` route, base at the project root where `final_video.mp4` lives), **title / description / tags** pulled live from the `beats_full.json` header via `/api/meta`, a **Download button**, the aligned **Re-assemble button**, and \u2014 as of v1.9 \u2014 a **live Upload button** (`patch_upload_button.py`). The Upload button is **private-only** by design (it shells `upload_episode.py --privacy private`; it can never publish \u2014 review + Altered-content=Yes happen in Studio). `/api/upload` + `/api/upload_status` mirror the Re-assemble fire-and-poll pattern (`_run_upload_bg` thread); on success the panel surfaces the video ID + Studio link, and a batched job (`header.parts > 1`) is refused by the script and reported as a non-error skip. When no finished video exists the slot shows a faint placeholder."""))

# ── §5.7 NEW: fold in the v1.2-v1.9 arc (insert before ## 6) ─────────────────
EDITS.append(("§5.7 insert",
"""When a path bug appears, check this distinction first.

---

## 6. The tech stack (the fast layer \u2014 swappable)""",
"""When a path bug appears, check this distinction first.

### 5.7 The v1.2\u2013v1.9 arc \u2014 aligned re-assemble, reliability hardening, and live upload

The canonical jumped from v1.1 to v1.9; the arc between (detail in the 15-June and 16-June SESSION-NOTES) banked several load-bearing facts:

**Two assemblers, only one aligned (the drift fix, v1.2).** `assemble_episode.py` (iterates BEATS, places each via `_index.json` `rev_map`, holds each to the FROZEN `durations.json`) is alignment-correct and is what the launched convergence run uses. `recreation_pipeline.assemble()` (positional `zip`, ignores `_index.json`, re-derives durations live via a Whisper re-align) **drifts** when shot-order \u2260 beat-order. The v1.1 Re-assemble button shelled `finish --assemble-only` \u2192 the wrong assembler \u2192 drift after a motion re-render. **Anything that assembles MUST use `assemble_episode.py`.** `finish --assemble-only` (calls the unsafe one) is a CLI footgun, still un-retired (backlog). The Re-assemble button now re-pools `modea/clips/` \u2192 `<project>/clips/` then shells `assemble_episode.py` with the exact convergence flagset.

**Run-record liveness is three signals, not one (A/B/C hardening, v1.6\u2013v1.8).** Phase (what the run says it's doing), heartbeat (gate-phase liveness), and pid-alive (process liveness). **A:** `active_job_id` prefers the freshest LIVE run by `started_at` (record content, not file mtime \u2014 a touched terminal record must not re-float). **B:** launch refuses if a run is already live (one live run total, global; dry-run exempt) \u2014 returns 409, prevents the duplicate-spawn that once stranded an orphan + dup records. **C:** `build_state` reaps a non-terminal record whose pid is dead (`os.kill(pid, 0)` \u2192 `ProcessLookupError` \u2192 flip to `dead`), covering hard-killed work legs the gate-only heartbeat can't see. Net: close/refresh/restart always rejoins the correct run; duplicates can't spawn; dead processes self-heal. `_TERMINAL_PHASES = ("done","stopped","error","stale","dead")`.

**Multiple writers must share one source of truth.** The FINAL VIDEO panel flickered when select + poll + done-event disagreed; all writers now key off "does a final video exist" (artifact-aware), not a transient `done` phase.

**Upload (v1.9).** `/api/upload` + `/api/upload_status` + `_run_upload_bg` shell the channel-agnostic `upload_episode.py` (private-only) \u2014 see \u00a75.5 and \u00a76 (Publish). The fire-and-poll shape mirrors Re-assemble exactly; it's the template for any new long-running console action.

---

## 6. The tech stack (the fast layer \u2014 swappable)"""))

# ── §6 Inworld model contradiction flag ──────────────────────────────────────
EDITS.append(("§6 Inworld model flag",
"""- **TTS:** Inworld (`inworld-tts-1.5-max`). Voices: Victor (Final Hours/Synthetic/hooks), Elliot (Sacred Dawn), Ashley (Success Coach lessons), Vinny (You Had To Be There). `voice_id` is snake_case in channel.json \u2014 `voiceId` silently falls back to Victor. Markup performs per-voice \u2014 prove it before relying on it.""",
"""- **TTS:** Inworld. *(Model-string contradiction to resolve: this doc said `inworld-tts-1.5-max` but the live `recreation_pipeline.py` sets `INWORLD_MODEL = "inworld-tts-2"` \u2014 the code is what runs; verify against the box and reconcile.)* Voices: Victor (Final Hours/Synthetic/hooks), Elliot (Sacred Dawn), Ashley (Success Coach lessons), Vinny (You Had To Be There). `voice_id` is snake_case in channel.json \u2014 `voiceId` silently falls back to Victor. Markup performs per-voice \u2014 prove it before relying on it.""",
))

# ── §6 Publish (NEW bullet appended to the stack, after Research/analytics) ───
EDITS.append(("§6 add Publish bullet",
"""- **Research/analytics:** NexLev MCP""",
"""- **Publish/upload:** `shared/upload_episode.py` \u2014 the ONE channel-agnostic uploader (header=metadata, channel folder=identity). One Google account (`peteralkema2@gmail.com`); one shared OAuth client, **published to Production** so refresh tokens don't expire (Testing mode = 7-day expiry, the old weekly-re-auth pain). Each channel has its own `token.json` (binds to the channel picked in the OAuth chooser). Five channels authed + bindings verified: Final Hours, Sacred Dawn, You Had To Be There, Synthetic Press, Scripture On Screen. (Success Coach is on a separate account, `\u20266`, out of scope.) The per-channel `auth.py` files are now redundant \u2014 `upload_episode.py --auth-only` does auth too.
- **Research/analytics:** NexLev MCP"""))

# ── §10 header + live-channels ───────────────────────────────────────────────
EDITS.append(("§10 header",
"""## 10. Current state (15 June 2026)

**Live channels:** Final Hours (primary), Sacred Dawn, You Had To Be There, Success Coach (packaging fixes in progress).""",
"""## 10. Current state (16 June 2026)

**Live channels:** Final Hours (primary), Sacred Dawn, You Had To Be There, Success Coach (packaging fixes in progress). **All five recreation channels (Final Hours, Sacred Dawn, You Had To Be There, Synthetic Press, Scripture On Screen) now upload from the Mission Control button on non-expiring Production tokens.**"""))

# ── §10 Specs-written -> built (the upload line) ─────────────────────────────
EDITS.append(("§10 specs-written",
"""**Specs written, not built:** the **upload wiring** behind the FINAL VIDEO panel's disabled button \u2014 `auth.py` fix + `/api/upload` (next session). Also still: decade-look Phase 2 (grade layer); multi-project / daemonized review server.""",
"""**Shipped 16 June (motion root-fix + upload-live arc):**
- **Motion dead-default ROOT-FIXED** (\u00a75.3) \u2014 the producer (`modea_beats.py`) was stamping the slow placeholder; now omits motion on normal beats so the channel `default_motion` fires. Sacred Dawn proven `all dramatic: True`. The per-project motion hot-fix is retired.
- **Upload: spec \u2192 working.** `upload_episode.py` proven on a real private upload (gustloff \u2192 video ID `wiykuEhTY1k`). The 7-day token expiry killed by publishing the OAuth app to **Production**. **Five channels authed** with Production tokens, each binding verified against the right YouTube channel. Mission Control **Upload button wired** (v1.9, private-only).
- **Stale-doc corrections banked** (this update): the phantom `auth.py` CLIENT_SECRET/TOKEN_FILE swap bug does not exist and was removed; the motion fix was re-located from the consumer to the producer; the Mission Control version was reconciled v1.1 \u2192 v1.9 with the missing v1.2\u2013v1.9 arc folded into \u00a75.7.

**Specs written, not built:** decade-look Phase 2 (grade layer); multi-project / daemonized review server; music wired into convergence."""))

# ── §10 closing paragraph ────────────────────────────────────────────────────
EDITS.append(("§10 open-from-session",
"""**Open from this session (top of next):** **finish the upload** \u2014 `auth.py` fix + `/api/upload` to light up the FINAL VIDEO panel's disabled Upload button (backlog item 1); then the `default_motion` root fix (item 2) to stop the per-project motion hot-fix. The standing read holds: ship real videos on the proven tiered economics (Esther is rendered; Enoch packaging/publish still pending) and let first-48h CTR + AVD drive what to fix next \u2014 not grind the backlog.""",
"""**Open from this session (top of next):** prove dramatic motion end-to-end on a real render (`cain-abel` \u2014 new, no storyboard \u2014 is the clean test); set **Altered content = Yes** in Studio for the uploaded gustloff (`wiykuEhTY1k`, currently private) before publishing. The standing read holds: ship real videos on the proven tiered economics and let first-48h CTR + AVD drive what to fix next \u2014 not grind the backlog."""))

# ── §11 near-term backlog (whole list replace: drop done items, renumber) ─────
EDITS.append(("§11 backlog list",
"""**Near-term backlog (priority):**
1. **Upload wiring \u2014 finish the FINAL VIDEO panel** (the panel + Download shipped; the Upload button is disabled). The dependency chain: **fix `auth.py`** (CLIENT_SECRET/TOKEN_FILE variable-swap; headless OAuth \u2192 auth on laptop, `scp token.json` to box; correct Final Hours brand account `peteralkema2@gmail.com`; 7-day-testing token expiry) \u2192 add **`/api/upload`** (wire the existing `shared/upload_episode.py`) + GET/POST schedule/visibility fields (mirror `/api/meta` + `render_policy`) \u2192 enable the panel's Upload button. Single-video auto-upload; **batched jobs exit at `final_video.mp4`** (header flag, e.g. `parts: 4`). Until then, uploads manual via Studio (Entertainment, tags, Altered-content = Yes).
2. **`default_motion` dead-default fix** (\u00a75.3) \u2014 make the storyboard-authoring guidance channel-aware so the per-channel default fires instead of being overridden by the slow string baked into every beat. Read `recreation_pipeline.py` ~95\u2013115 / ~470\u2013485 / ~1245\u20131275 first. (Enoch was hot-fixed per-project this session; this is the root-cause fix.)
3. **Cheap correctness items:** strip animate label says "Kling" regardless of the tiered split \u2014 make it reflect Kling-\u2264N / Ken-Burns->N; confirm `cmd_stills` passes `safety_tolerance:"5"` on the first stills pass (stops black frames at the gate); fix `finish --plan` (mkdir-before-exit + CWD-relative path); build_state should prefer the freshest `.mc_jobs` record (double-job gotcha).
4. **v2 motion routing** (\u00a75.2) \u2014 route Kling-vs-Ken-Burns by which beats *earn* motion (duration/action), not the positional first-N split.
5. **Music** \u2014 decide generated (`make_music.py`) vs curated Jamendo; wire chosen path into convergence. (`finish` already has `--music`/`--no-music`; generates a bed unless `--no-music`.)
6. **Decade-look Phase 2** \u2014 write+commit `film_emulate.py` grade presets, wire a single grade pass into `assemble()`.
7. **Inworld-layer:** wire dead `speed` key; fix sentence-chunking voice-drift; **chunk-validation guard**; kill hardcoded voice/gate labels (leg prints "Victor" regardless of resolved voice).
8. **Beat-granularity discipline** \u2014 bake "~8\u201312s/beat, ~90\u2013110 beats for a ~20-min film" into authoring.
9. **Banked-for-later:** parallel fal animation (semaphore, ~5\u20138\u00d7 faster); formalised batch orchestration (split at the stills-review seam); `.gitignore` for `*.bak*/*.pre_*`; move the **Kling-count field into the always-visible controls strip** (currently only at the stills gate \u2014 breaks the always-visible-but-disabled rule).""",
"""**Near-term backlog (priority):**
1. **Upload polish (optional)** \u2014 the uploader + button are live (\u00a75.5/\u00a75.7). Remaining nice-to-haves: per-channel `channel.json` `upload` blocks (category/privacy) for the four channels lacking them (default is category 24 / private \u2014 fine); a schedule/visibility control on the panel (the script already has `--schedule-cet-1am` / `--publish-at`). Rename the OAuth consent-screen app to "Pipeline" (currently "Success Coach Upload Tool").
2. **Retire/guard `finish --assemble-only`** (\u00a75.7) \u2014 it calls the alignment-UNSAFE `recreation_pipeline.assemble()`; either route it through `assemble_episode.py` too, or have it refuse with a pointer. Still reachable from the CLI.
3. **Cheap correctness items:** strip animate label says "Kling" regardless of the tiered split \u2014 make it reflect Kling-\u2264N / Ken-Burns->N; confirm `cmd_stills` passes `safety_tolerance:"5"` on the first stills pass (stops black frames at the gate); fix `finish --plan` (mkdir-before-exit + CWD-relative path).
4. **v2 motion routing** (\u00a75.2) \u2014 route Kling-vs-Ken-Burns by which beats *earn* motion (duration/action), not the positional first-N split.
5. **Music** \u2014 decide generated (`make_music.py`) vs curated Jamendo; wire chosen path into convergence. (`finish` already has `--music`/`--no-music`; generates a bed unless `--no-music`.)
6. **Decade-look Phase 2** \u2014 write+commit `film_emulate.py` grade presets, wire a single grade pass into `assemble()`.
7. **Inworld-layer:** reconcile the model-string (\u00a76: doc `1.5-max` vs code `inworld-tts-2`); wire dead `speed` key; fix sentence-chunking voice-drift; **chunk-validation guard**; kill hardcoded voice/gate labels (leg prints "Victor" regardless of resolved voice).
8. **Beat-granularity discipline** \u2014 bake "~8\u201312s/beat, ~90\u2013110 beats for a ~20-min film" into authoring.
9. **Retire the redundant `auth.py` files** (`final-hours/auth.py`, `success-coach/auth.py`) \u2014 superseded by `upload_episode.py --auth-only`; harmless but drift-prone.
10. **Banked-for-later:** parallel fal animation (semaphore, ~5\u20138\u00d7 faster); formalised batch orchestration (split at the stills-review seam); `.gitignore` for `*.bak*/*.pre_*`; move the **Kling-count field into the always-visible controls strip** (currently only at the stills gate \u2014 breaks the always-visible-but-disabled rule)."""))

# ── §12 Paths bullet: append the modea-folder principle ──────────────────────
EDITS.append(("§12 modea-folder principle",
"""- **Paths:** box repo `~/Pipeline`; laptop `~/Projects/Pipeline`; venv `~/venvs/pipeline`; channels at `<channel>/`, projects at `<channel>/projects/<slug>/`.""",
"""- **Paths:** box repo `~/Pipeline`; laptop `~/Projects/Pipeline`; venv `~/venvs/pipeline`; channels at `<channel>/`, projects at `<channel>/projects/<slug>/`.
- **No `modea/` folder = an un-rendered project (or a pure-Mode-B one), NOT a broken one.** `modea/` (with `stills/`, `clips/`, `storyboard.json`) is CREATED by the Mode A leg; a parsed-but-never-launched project legitimately holds only `script.md` (e.g. `enoch` is bare, `enoch1` is the rendered one). Don't assume every project has `modea/`.""",
))

# ── §12 OAuth bullet rewrite ─────────────────────────────────────────────────
EDITS.append(("§12 OAuth bullet",
"""- **OAuth:** Final Hours has working auth (under peteralkema2@gmail.com / `youtube-upload-test-497220`); `auth.py` has a known CLIENT_SECRET/TOKEN_FILE variable-swap bug; OAuth app in 7-day testing mode \u2192 weekly token expiry. Sacred Dawn / Synthetic / others: upload not set up.""",
"""- **OAuth:** one Google account `peteralkema2@gmail.com`; one shared OAuth client, **published to Production** (was Testing \u2192 7-day token expiry, now non-expiring). **Five channels authed** with per-channel `token.json`, each binding verified against the right YouTube channel (Final Hours, Sacred Dawn, You Had To Be There, Synthetic Press, Scripture On Screen). A token binds to the channel picked in the OAuth chooser \u2014 mint per channel via `upload_episode.py --project <ch>/projects/<x> --auth-only` on the LAPTOP (browser), then `scp token.json` to the box. **Verify a binding** (run from `~/Pipeline`): `python -c "from pathlib import Path; from shared.upload_episode import get_credentials; cd=Path('<channel>'); c=get_credentials(cd/'token.json',cd/'client_secret.json'); from googleapiclient.discovery import build; print(build('youtube','v3',credentials=c).channels().list(part='snippet',mine=True).execute()['items'][0]['snippet']['title'])"`. (There is NO `auth.py` variable-swap bug \u2014 that doc note was a phantom; removed. Success Coach is on a separate account, out of scope.)""",
))

# ── §12 "Currently v1.1." ────────────────────────────────────────────────────
EDITS.append(("§12 currently v1.1",
"""`/api/state` also returns `version`+`sha`. **Currently v1.1.**""",
"""`/api/state` also returns `version`+`sha`. **Currently v1.9.**"""))

# ── §13 delete the Motion hot-fix bullet ─────────────────────────────────────
EDITS.append(("§13 delete motion hot-fix",
"""- **Motion hot-fix (the `default_motion` dead-default, \u00a75.3 \u2014 needed per project until the root fix lands):** before Generate Clips, rewrite every beat's `motion_prompt` to the channel's dramatic default. From the box, a heredoc that reads `default_motion` from `<channel>/channel.json`, backs up `storyboard.json` to a `.pre_motion_*` sidecar, and rewrites all beats. (Three projects have needed this \u2014 Enoch, the test runs, Esther \u2014 which is why the root fix is backlog item 2.)
""",
""))

# ── §13 Free assemble bullet: correct the parenthetical ──────────────────────
EDITS.append(("§13 free-assemble bullet",
"""- **Free assemble sanity-check:** `cd ~/Pipeline/<channel-folder>/projects && python ~/Pipeline/shared/recreation_pipeline.py finish --project <slug>/modea --assemble-only` \u2014 re-stitches from existing clips, no cost (this is what the Re-assemble button shells out to).""",
"""- **Free assemble sanity-check:** the Mission Control Re-assemble button is the right tool now (it uses the ALIGNED `assemble_episode.py`). The CLI `finish --project <slug>/modea --assemble-only` re-stitches free BUT calls the alignment-UNSAFE `recreation_pipeline.assemble()` (drifts \u2014 \u00a75.7); avoid it for anything you'll ship, and see backlog item 2 (retire/guard).""",
))

# ── §13 Auth bullet rewrite ──────────────────────────────────────────────────
EDITS.append(("§13 auth bullet",
"""- **Auth (until the upload panel is wired):** all OAuth/token work is still terminal \u2014 the whole point of backlog item 1 is to move it behind the panel's Upload button.""",
"""- **Auth / token-minting (one-time per channel):** uploading is now a console button, but minting a channel's token still needs a browser, so it stays a LAPTOP step: `upload_episode.py --project <ch>/projects/<x> --auth-only` (pick the matching channel in the chooser) \u2192 `scp token.json` to the box \u2192 verify the binding (\u00a712 OAuth). Non-expiring now that the app is Production, so this is genuinely one-time per channel.""",
))


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not DOC.exists():
        die(f"{DOC} not found - run from the repo root on the laptop.")

    src = DOC.read_text()

    if SENTINEL in src:
        print("Already applied (sentinel present) - no changes made.")
        return

    # Verify every anchor exactly once on the ORIGINAL source before writing.
    for label, old, _ in EDITS:
        c = src.count(old)
        if c != 1:
            die(f"[{label}] anchor found {c}x (expected 1) - NOTHING written. "
                f"Paste me the current text around this section and I'll re-cut it.")

    new = src
    for _, old, repl in EDITS:
        new = new.replace(old, repl)

    if SENTINEL not in new:
        die("sentinel not present after edits - aborting.")

    bak = DOC.with_suffix(DOC.suffix + ".pre_canon0616")
    shutil.copy2(DOC, bak)
    DOC.write_text(new)

    print(f"OK patched ({len(EDITS)} edits):")
    print(f"   {DOC}   (backup: {bak.name})")
    print("Canonical is now 16 June / Mission Control v1.9.")
    print("Doc-only change: commit/push, then `git pull --no-edit` on the box. No restart.")


if __name__ == "__main__":
    main()
