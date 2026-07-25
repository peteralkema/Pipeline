# SESSION NOTES — 04 July 2026 (evening) — THE CRAFT-VS-CASH SURFACE
## Mission Control v1.9 → v3.6 in one sitting: per-beat cost controls, the mode invariant, the packaging box

_Companion to the worklog RECORD entry of the same date. This is the deep narrative; the worklog carries the compressed version and the backlog deltas. Doctrine graduations are marked → throughout._

---

## 0. What this session was

The banked plan was four MC review-page controls: Ken-Burns override, clip-merge, scroll-to-top, thumbnail upload. What shipped was those four **plus** everything the building surfaced: a portfolio-wide engine bug fixed at its root, motion presets that grew into a full per-beat mode system, a letterbox repair tool, and the FINAL VIDEO panel restructured into equal CONTENT | PACKAGING boxes. **Twelve MC versions (v1.9 → v3.6), three engine patches, ~15 patch scripts, two hotfixes, one ~$3 test project, ~17 doctrine entries.** The review page is now the surface where craft-judgment and cash meet per beat — the thing §7 scoped, built and proven.

## 1. Housekeeping (the session's first surprise)

`git status` on the box showed the **ffmpeg assemble fix was already committed** — priority #1 self-resolved. Rescued from untracked: `shared/reassemble_static.py` (QQrew static-reassemble, real pipeline code) and `make_thumb_bottomleft.py`; recorded the deliberate deletion of `gettysburg-trailer-2/script.md`. A laptop-side untracked copy of `reassemble_static.py` blocked the pull — parked, pulled, diffed, deleted (identical).

## 2. The assembler read — sync is structurally safe (the shared prerequisite)

Read `shared/assemble_episode.py` (417 lines) + the Gettysburg film's `_index.json` + `durations.json` in full before writing anything. **The make-or-break question resolved favorably and unambiguously:** `durations.json` is the sole timing source — every beat's segment is built to exactly its Whisper-measured duration; the clip's file length only decides HOW the slot fills (trim / slow-fill / kb-tail / freeze). Voiceover muxed whole, untouched; output pinned to voice length (VOICE WINS). Nothing ever timestamps from clip file-length, so **both toggles change only the pixel source and the beat timeline cannot drift by construction.** The index is a complete 1-based-shot → 0-based-beat map (every beat owns a shot number whether rendered or not); `durations.json` carries per-beat `audio_start`.

Also read on the way through: the `--index`/`--durations` defaults still hardcode `ep1-the-promise` (worklog #9 alive in the text — every invocation must pass explicit flags), and the assembler's kb-tail block carries the banked zoompan craft (`upscale, z='min(zoom+0.0008,1.10)'`) that later got reused.

Side-read from the Gettysburg `--plan` data: beats run 1.5–3s against the 5s Kling atom — **half to two-thirds of every paid clip is discarded**. Clip-merge is the bigger money lever; KB shipped first because it banks the per-beat-control pattern at near-zero risk.

## 3. KB override (engine + MC) — and the bug it flushed out

**Engine (`patch_kenburns_toggle.py`):** `render_policy.json` gains `kb_override: [beat,...]`; routing becomes kling only if `bi < N AND bi not in overrides`. **The freed slot is SAVED, not slid.** Banner reports applied overrides; `--plan` marks them. Proven zero-cost on the real Gettysburg film: beats 3 and 7 flipped, marked, priced, neighbors untouched, policy file restored.

**MC v2.0:** `/api/kb_toggle` (merge-discipline — siblings never clobbered, copied from the static-button patch), KB button in the motion cell, state painted from the policy file on every render (truth on disk, not in-memory — the `__MOTION_EDITS` lesson applied), motion box + Render-this-clip disabled while ON (that button fires Kling directly).

**The 10-beat test flushed the engine bug:** KB-ON beats rendered as static stills. Root cause was the **01 Jul QQrew hardcode** — the per-channel `ken_burns` flag "did not take at render time" (CWD-walk-up + cached config), so `_z = "1"` was hardcoded into the SHARED `ken_burns_still()` and every KB floor clip portfolio-wide became a held frame. QQrew's channel doctrine had silently become engine law — **build-order bias, new head.**

**The fix (`patch_kenburns_flag_fix.py`):** resolve the flag from the STILL's own path (walk `still_path.parents` to the first `channel.json` — deterministic regardless of CWD, per-call, uncached; one tiny JSON read per clip vs a full encode). QQrew `ken_burns:false` keeps its true-static floor (functionally tested on mock channel trees); synthetic/no-key defaults to the real capped zoom-in. → **DOCTRINE: a channel-specific fix lands in the channel's config, never in the shared function; if the flag doesn't take, fix the flag resolution, not the constant.**

**Second discovery from the mixed test results:** some KB clips zoomed (CLI-rendered) and some didn't (MC-rendered) — because **`pipeline_server.py` imports the engine functions at startup and runs them in-process.** → **DOCTRINE (restart law): MC runs imported engine code — every engine pull requires a service restart before MC-driven renders pick it up; CLI is always fresh. The restart window: after every engine pull, never mid-render** (cgroup teardown, standing rule).

## 4. Motion presets → the mode system (the session's emergent design)

Started as "add a second motion direction box": shipped as **two preset buttons with the exact Gettysburg-proven wording** — Dynamic (`dynamic cinematic camera movement, powerful momentum, natural realistic motion, dramatic atmosphere`) and Slow crane-up (`slow cinematic camera movement, crane-up to wide angle powerful momentum, natural realistic motion, dramatic atmosphere`) — stamping into the existing motion box and riding the existing persist seam (blur → `/api/motion` → `storyboard.json` → batch animate) with zero engine change. Peter's field result driving it: the slow-crane wording "significantly reduced hallucinogenic animation."

Then the design grew, correctly, in three steps:

- **v2.6 — the mode invariant:** every beat is in exactly ONE visibly active mode: **Kling** (green motion-box border + exactly-matching preset green; typing custom text un-greens the preset live), **KB** (green button), or **Inherit** (green button). Status line per mode: Kling = "renders its own 5s Kling atom - source for inherit chains"; KB = "free Ken-Burns push on its own still - no atom"; inherit = the chain line (below).
- **v2.7 — presets are mode buttons:** clickable in ANY state; clicking one while KB/inherit is ON releases that toggle **through the real endpoints** (policy file stays the single truth), stamps the wording, takes the green. One click from any mode to Kling. → **DOCTRINE: presets are modes, not macros; the policy file is the only truth — the page just paints it.**
- → **DOCTRINE (three-tier motion rule, for `_Synthetic2.md §7`): Kling-dynamic for meaning-in-the-move, Kling-slow-crane for gravity-with-motion, free KB push for meaning-in-stillness.** Peter's one-line version: **"animate the galloping horse, never the wheat field."**

Also removed in this arc (v2.1): the **dead Accept/Reject judge buttons** — written only to in-memory `window.__JUDGED`, no save endpoint, no consumer, state evaporating on reload. Grep-verified dead, cleanly excised. Banked deliberate-later: a reject-list driving a one-click "re-render all rejected" batch action (build it WITH a backend or not at all).

## 5. Clip-merge / inherit (the money lever) — the derived-clip design

Peter's worry ("real surgery… ages debugging") reframed the design and improved it: **merge as derived clip, not index surgery.** Beat B keeps its own shot number; after all atoms exist, an **inherit pass** manufactures `shot_<B>.mp4 = ffmpeg -ss <offset>` on the source clip. The assembler sees an ordinary clip and does what it already does. Zero changes to `assemble_episode.py`, zero to `_index.json`, timing untouched by construction.

**Engine (`patch_clip_inherit.py`):** `inherit_prev: [beat,...]`; routing precedence inherit > kb_override > front-N; main loop defers inherit beats (no fal call); second pass **walks chains** back to the nearest non-inherited ancestor summing consumed durations from frozen `durations.json` (B inherits A, C inherits B → C reads A's atom at `A_dur + B_dur`); **every failure is benign** — no predecessor / source missing / <0.3s left in the atom (ffprobe-guarded) → free `ken_burns_still` fallback on B's OWN still with a printed warning. The cut always assembles. Chain math functionally verified.

**MC v2.2–v2.7 (the idiot-proofing arc, "max craft min cash"):**
- Inherit button in the motion cell; `/api/inherit_toggle` merge-style; **mutual exclusion both ways server-enforced** (turning one on removes the beat from the other list); beat 0 disabled (no predecessor).
- **The decision line** under the button, evolved across three versions into: **"Inheriting beat J - chain of N beats on one atom = X.XXs"** — chain-aware totals (true consumption of the single source atom, not pairwise), GREEN fits the 5s atom / AMBER exceeds (tail falls back free) / **RED when the walk-back lands on a KB source** ("no atom to inherit — you can only inherit from a horse, never from a wheat field") or falls off the front. **Live repaint on every toggle click** — the UI computes exactly what the render pass will do, before any spend. Proven on-page: kb-toggle4 with beats 4–9 all inherit showed "Inheriting beat 3 - chain of 2…7 on one atom", correctly amber past the atom.
- v2.4's first sum implementation ran BEFORE the state fetch resolved — fixed in v2.5 (paint inside the `.then`).

**Peter's KB-source scenario probe** (what if the previous beat is KB-ON?) was answered from the code, not guessed: mechanically safe (fallback), economically pointless (a KB source has no tail), and the UI now says so in red BEFORE spend. A KB beat poisons the whole inherit run behind it — visible, not silent.

**STILL OPEN: the inherit render proof at the artifact** — `rm` one inherited beat's clip → `--animate-only` (expect `[inherit] shot NNN <- beat J's atom @ X.XXs (free)`) → Re-assemble → eyeball one continuous camera move across the boundary. The chain lines prove routing; the assembled cut proves the footage. **First task next session after the 48h read.**

## 6. The two page-killing hotfixes (patch-craft family, all → doctrine)

- **v2.3 — the apostrophe.** The inherit tooltip contained `beat\'s`; the escape survives the PATCH layer but the page's JS lives inside a **Python string** in the server source — the server's own parser collapses `\'` to a bare `'`, terminating the JS string. One syntax error killed the entire page script ("loading…" forever, header static). `py_compile` passed — legal Python, broken JavaScript. → **DOCTRINE: no apostrophes in JS string literals that travel through a Python string layer — two escape decoders, one character, dead page.** Every subsequent patch self-checks for `\'`.
- **v3.3 — the NameError.** `_handle_fix_letterbox` called `shutil.copy2`; `shutil` was imported in the patch script, not the server. Uncaught NameError → connection died → browser "TypeError: Failed to fetch". Journal traced it to the exact line (and confirmed the handler died AT the backup — detection had already succeeded on the real letterboxed frames). → **DOCTRINE: a handler's imports live IN the handler (the local-import pattern the file itself teaches); `py_compile` validates syntax only — never names, never carried JS. MC patch verify = compile + load the page + click the button.** (The empty first journal grep also re-taught verify-at-the-artifact applies to my own diagnoses.)

## 7. Letterbox analyse + fix (v3.1–v3.3)

The screenshots showed the fal silent-substitute family's newest member: **baked-in letterbox bars inside a correctly-sized canvas** — `enforce_16x9.py` cannot see them because the canvas lies. New `/api/fix_letterbox` + "Analyse + fix stills" button (stills-gate bar AND, v3.2, the always-visible project panel for retro fixes on done projects): detection deliberately strict to protect dark cinematography (**a bar row/column must be near-uniform pure black — max luminance <24, mean <10 — and run ≥2% of the dimension**; flux letterbox is dead black, real night scenes carry highlights); plausibility guard refuses to crop away >50% of frame; fix = crop live region, LANCZOS cover-resize back; one-time backups in `stills/_pre_letterbox_fix/` (**a SUBDIR, so nothing globbing `stills/shot_*.png` ever matches a backup**); response flags fixed shots that already have clips (fixing the still doesn't fix the clip — the message says "re-render these clips, then Re-assemble"). Detection functionally proven on synthetic frames: 60px bars found exactly, fixed, re-scan clean; dark-scene-with-highlights untouched. → **fal silent-substitute family += baked-in letterbox.**

## 8. Thumbnail: upload → source-mode redesign (v2.9 → v3.0)

v2.9 shipped a plain upload writing `thumbnail.png`; Peter's next message reframed it correctly: **the uploaded image is a SOURCE to composite text onto, not the thumbnail.** v3.0: upload writes persistent `<root>/thumbnail_source.png`; panel gains source-mode pair (**Still # / Uploaded image**, green-mode pattern); still# greys and stops validating in upload mode; Generate branches `--shot N` vs `--still <source>` — **`make_thumbnail.py` already had `--still`, so ZERO engine change**; a successful upload auto-switches mode and previews the source. Iterate source × text freely; `thumbnail.png` stays the one derived artifact `upload_episode.py` reads. → **DOCTRINE: sources persist, artifacts derive.** Proven live in the closing screenshot: still-8 GENERAL / ROBERT E. LEE poster composited in the PACKAGING box.

## 9. The CONTENT | PACKAGING layout (v3.4–v3.6) — and the cap archaeology

The FINAL VIDEO panel restructured: **CONTENT** (video, Download, Re-assemble, Analyse+fix, Title/Description/Tags — metadata rides with the video so a rendered thumbnail never pushes it) | **PACKAGING** (pure thumbnail: preview promoted to mirror the video, generate/source/upload), Upload full-width beneath both. **The layout is the thesis drawn: content and packaging as equals, because CTR lives entirely in the right box.**

Two incidents en route, both banked:
- **The stale-Downloads incident:** v3.4 was amended pre-apply, but `mv -f ~/Downloads/…` shipped the pre-amendment download. Fixed forward with a fresh-named v3.5. → **DOCTRINE: after a patch is amended, the Downloads copy is stale — re-download, or the mv ships the old one; fresh filenames for amended patches.** (The anchor-verify discipline held throughout: nothing writes unless the file matches.)
- **The four-cap chain:** width was pinned by `.panel` class (720px) → inline cssText (720) → `#toppanel` slot (760) → `#topgrid` wrapper (1500), peeled one screenshot at a time until a single `grep -n "max-width"` exposed the lot. Final fix: inline `max-width:none` on the done-panel (inline beats class; the class stays intact for panels that legitimately use it). → **DOCTRINE: when a width won't move, grep the whole cascade first — peeling caps by screenshot costs a round-trip per layer, one grep costs none.**

Also v2.8: the fixed **⇧ Top** scroll button (worklog #33 closed).

## 10. The test project + authoring lesson

`kb-toggle4` (synthetic, 10 beats, aftermath-of-Pickett's-Charge micro-scene, ~$3): 7 motion-carrying beats + 3 deliberately static (fallen-field wide, canteen, twilight wide) as toggle targets. First paste **halted at parse: the section-marker whitelist** — only `## COLD OPEN` / `## PART …` / `## ACT …` are recognized; `## THE SILENCE AFTER` would have been read aloud by TTS. Good failure message, missing law. → **`_Synthetic2.md §5f` addition: the recognized-marker whitelist belongs in the markup law.** The project then served every proof in the session: KB routing, the flag-fix A/B, the chain lines, the thumbnail loop.

## 11. The version-stamp discipline

v1.9's stamp was lagging (the presets patch had silently never traveled — stamp+sha caught it). From v2.0 on, **every MC patch carries its own APP_VERSION bump** — the stamp can never lag the code, and it paid rent immediately (caught the stale-Downloads apply, confirmed every restart). Twelve bumps this session, each one a shipped page change.

## 12. Doctrine ledger (graduate next session)

**→ `_Synthetic2.md`:** §5f parser marker whitelist; §7 cost-controls SHIPPED + the three-tier motion rule (dynamic / slow-crane / free-KB; "animate the galloping horse, never the wheat field"; "you can only inherit from a horse") + the inherit chain mechanics and its UI truth-mirror.
**→ canonical reference (reliability/§ code-leaks):** channel-fixes-live-in-channel-config (the 01 Jul hardcode autopsy); MC-imports-engine-code restart law (after every engine pull, never mid-render); the patch-craft family (JS-apostrophe double-decode; handler imports live in the handler; py_compile proves syntax never names/JS; MC verify = compile+load+click); fal silent-substitute family += baked-in letterbox; sources persist, artifacts derive; the policy file is the only truth, the page paints it; stale-Downloads re-download rule; grep-the-cascade for CSS caps; the v-stamp-bump-in-every-patch rule.

## 13. Outstanding (carried, in order)

1. **48h READ evening 5 Jul** — unchanged top task (Gettysburg film CTR/AVD/Browse% + retention curve + Shorts distribution shape).
2. **Inherit artifact proof** (§5 above) — the one shipped control unproven at the artifact.
3. **Letterbox retro-fix follow-through** — run Analyse+fix on the project with the two flagged stills, `rm` + re-render the flagged clips, Re-assemble, eyeball.
4. **Doctrine graduation pass** (§12) into `_Synthetic2.md` + canonical.
5. Then the biblical pivot prerequisites as previously banked (per-channel reference-lock, parallel-fal semaphore).

Daemonize-runs (restart survives in-flight renders) remains open and matters MORE now — twelve restarts this session all had to wait for idle.
