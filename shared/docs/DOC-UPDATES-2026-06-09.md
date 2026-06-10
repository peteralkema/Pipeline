# DOC UPDATES — 2026-06-09 session

*Drop-in additions/edits for the existing `shared/docs/` files. Each block names its target doc and where it goes. Applied so the canonical docs reflect: decade look-override (Phase 1 shipped), audio-continuity QC, tunnel-free review, Vinny markup rules, batched multi-video jobs, and the upload exit-gate requirement.*

---

## A. `ante-machinam.md`

### A1 — Constitution §1 (the silence point): append the Vinny markup law

After the silence-reconciliation paragraph in Constitution §1, add:

> **Per-voice markup allowlist (banked 2026-06-09, You Had To Be There / Vinny).** TTS markup performs per-voice; do not assume a markup works until proven on that voice. For Vinny: `[laughs]` is ALLOWED (performs as a real laugh, use sparingly); `[sigh]` is BANNED (does not perform — write the exhale into words and rhythm instead); `[pause]` is capped at TWO, must attach to a beat with real spoken words, never stands alone, and never sits at a chunk seam (write it mid-narration with words on both sides). The reason is mechanical: a beat that is markup-heavy and word-light is exactly what makes an Inworld chunk fail and concatenate as dead air — this caused a 44-second silent hole in the Xennials episode (Whisper showed speech ending at 134.5s and not resuming until 178.7s). Keep pauses wrapped in words so every chunk has speech to anchor.

### A2 — Constitution §6 (granularity): correct the wpm figure

The pacing reality is now measured repeatedly. Update the Part IV "one pacing reality" note (and the §6 planning table caveat) to:

> Inworld/Vinny renders at roughly **190–200 wpm measured** (You Had To Be There: 3,829 narration words → 1,161.6s = ~198 wpm). For a target runtime, write SPOKEN words = minutes × ~195. A true 10-minute episode needs ~1,900 spoken words; a 40-minute batch needs ~7,800 spoken words. (Counting words in `script.md` overcounts because VISUAL lines + header are included — only the narration is spoken.)

### A3 — Part II / new subsection: batched multi-video jobs

Add after the two-modes section:

> **Batched multi-video jobs (banked 2026-06-09).** Nothing in the machine requires one script = one video — the pipeline is beat-based and mode-agnostic about where an "episode" ends. A single `script.md` may contain several self-contained parts (each with its own cold open and close); run it as ONE job and cut the assembled `final_video.mp4` into N videos in post (Filmora). Authoring rules for a batch: (1) each part opens cold and closes cleanly so the cut points are obvious; (2) the WHOLE job shares ONE look — the look resolver resolves one `look.json` per project and caches it, so you cannot vary the decade look across parts in a single job; batch by shared look (e.g. four `hi8_90s` parts together; a `vhs_80s` part runs as its own job, or is re-set to the shared look); (3) the audio-continuity QC matters MORE on a long batched read (more Inworld chunks = more failure surface) — read its verdict at the audio gate before approving. The header's title/description/tags describe the BATCH; per-video metadata is supplied manually at upload (and see the upload exit-gate requirement in the playbook).

### A4 — Part V.x / new look key in the header

The header now accepts an optional `look:` key (and alias `era:`). Add to the header description (Constitution §2 / the §1 shape in Part VI):

> Optional header key **`look:`** selects a decade look profile for the job (e.g. `look: hi8_90s`, or an alias like `look: 1990s`). It is convenience metadata; the resolver actually reads a `look.json` in the project folder. Omit `look` and the channel's default `style_suffix` is used (today's behaviour). The look governs the STILLS aesthetic in Phase 1; the grade layer is Phase 2.

---

## B. `PIPELINE_PLAYBOOK.md`

### B1 — PART 2D status table: update rows

- **Mode A stills gate row:** note the gate is now reviewable TUNNEL-FREE. The review server can bind public with token auth (`serve_review.py --host 0.0.0.0 --key <secret>` → `http://<box-ip>:8001/?key=<secret>`); `/stills/` and `/api/health` are key-exempt so images load; the page and the spend endpoints (`/api/restill`, `/api/aifix`) require the key. Still one project per server start (multi-project refactor is backlogged). Honor-system gate unchanged.
- **Convergence row:** add that the UPLOAD step must support a **batch exit-gate** — a batched (multi-video) job must stop at `final_video.mp4` and NOT auto-upload, because one job → many videos breaks the single-metadata assumption. Single-video jobs may auto-upload with per-project metadata; batched jobs exit before upload.

### B2 — PART 2 / new audio-gate behaviour

In the finish/audio section, add:

> **Audio-continuity QC at the audio gate (built 2026-06-09).** The audio gate now auto-runs `audio_qc.audio_continuity_check()` on the Whisper output and prints a verdict BEFORE the keep/swap prompt: clean (`✓ no gaps over 3s`) or a loud warning naming the gap location. A detected gap almost always means a failed Inworld chunk shipped as dead air — the correct response is ABORT and re-run the audio leg, NOT swap (swap substitutes a human read). The check is read-only and fails soft. This is the DETECTION half; the PREVENTION half (chunk-validation + retry inside `generate_voiceover`) remains on the Inworld-layer backlog.

### B3 — PART 4 / decade look-override entry

Add to KNOWN DEFERRED / now-partially-built:

> **Decade look-override (Phase 1 BUILT 2026-06-09).** Per-job look selection via `shared/look_resolver.py` + a project `look.json`. Phase 1 changes the STILLS look (`recreation_pipeline.py:529` now resolves the look instead of reading `channel.json` style_suffix directly). Backward-compatible: no `look.json` → channel default. Phase 2 (NOT built): write+commit `shared/film_emulate.py` (it does not currently exist in the repo) with ffmpeg grade presets and wire a single grade pass into `assemble()` at line 801. Registry currently holds `kodachrome_50s`, `color_60s`, `super8_70s`, `vhs_80s`, `hi8_90s`, `digicam_2000s`. KNOWN GAP: the review server's own `generate_still` does not yet resolve the look — regenerated stills ignore the per-job look until patched.

### B4 — PART 5 operating reminders: add

> - **Review server port collisions:** only one server can hold port 8001. Before starting `serve_review.py`, kill any stale one: `lsof -ti :8001 | xargs kill -9`. Run it in a tmux WINDOW (`Ctrl-b c`) inside the existing `orch` session so it survives disconnect; closing the window still kills it (until daemonized).
> - **Per-job look:** drop `{"look":"<profile>"}` in the project folder as `look.json`. Profiles: `kodachrome_50s` / `color_60s` / `super8_70s` / `vhs_80s` / `hi8_90s` / `digicam_2000s` (decade aliases work, e.g. `"1990s"`).

---

## C. `ORCHESTRATOR-DEPENDENCY-MAP.md`

### C1 — §2 audio_leg: add the QC step

Under `audio_leg.py -> run_audio_leg(ctx)`, after step 4 (build_beat_durations), add:

> 5. `audio_qc.audio_continuity_check()` (NEW 2026-06-09) — runs inside `audio_gate()` before the keep/swap prompt; reads `artifacts["whisper"]`; prints clean/gap verdict. Read-only, fails soft. Detection-only (prevention = Inworld chunk-validation, still backlogged).

### C2 — §2 modea_leg / new look resolution dependency

Add to the Mode A leg notes:

> - Still generation now resolves the per-job look: `recreation_pipeline.generate_still()` calls `look_resolver.resolve_look(out_path, config)` (NEW 2026-06-09) instead of reading `config["style_suffix"]` directly. Resolver walks up from the still's out_path to a project `look.json`; falls back to channel style_suffix. `serve_review.py`'s separate `generate_still` does NOT yet do this (follow-up).

### C3 — §6 data spine: add look.json and the QC

| Artifact | Produced by | Read by |
|---|---|---|
| `look.json` (per project, optional) | hand-authored / orchestrator (future, from header `look:`) | `look_resolver.resolve_look()` → `generate_still` |
| (the QC reads `voiceover.json`) | whisper | `audio_qc` (NEW) at the audio gate |

### C4 — §8 honesty flags: add

> - **`film_emulate.py` does not exist** — the decade-look grade layer (Phase 2) is unbuilt; Phase 1 ships stills-look only. Grade preset names in `look_resolver` are forward references.
> - **Upload exit-gate not built** — convergence has no notion of a batched (multi-video) job; it would try a single upload. Batched jobs must exit at `final_video.mp4`. Build an exit-gate / batch flag before wiring auto-upload.
> - **Review server look gap** — `serve_review.py.generate_still` ignores the per-job look.

---

## D. `STARTUP_PACK.md`

### D1 — PART 4 (production patterns): add two banked patterns

> 13. **Title and thumbnail must COMPLEMENT, not echo** (banked 2026-06-09). When the thumbnail carries the "what" (artifact, era, emotion), the title carries the "why-click" (the emotional/identity hook). Two hooks, not one said twice. Decide thumbnails in parallel with titles (extends pattern 7).
> 14. **Un-filmable vs. re-watchable — the niche-fit filter** (banked 2026-06-09). The machine's moat is UN-FILMABLE lived memory (the room, the feeling), which AI recreation renders legitimately. It is a poor fit for re-watchable media that exists in crisp HD (games, TV, films), where an AI impression reads as wrong to an AI-sensitive audience. Before committing a topic, ask: is the subject un-filmable lived experience, or a re-watchable artifact that already exists in HD? Treat this as a sixth niche-selection criterion alongside Leo's five (monetized / <100k subs / 20k+ avg views / recent virality / reproducible-in-a-pure-AI-machine).

### D2 — PART 2 (moat spine): add the spike lesson

> **Spike-chasing does not suit this operation** (banked 2026-06-09). By the time a demand spike is visible in Trends/NexLev it has usually already crested, and the clone swarm follows a breakout within days — so "proven topic with no graveyard" is largely a unicorn (demand and the graveyard are the same signal weeks apart). The edge is best-execution in permanently-warm, SERVED (not searched) lanes, not topic-timing. Use Trends' served-vs-searched distinction (YouTube-Search = mature/satisfied demand; Web-Search = fresh demand) and the Rising-Queries panel as DETAIL-mining for authentic era artifacts — not as a topic-picker.

### D3 — PART 1 map: note the new channel

> You Had To Be There (cinematic AI nostalgia recreation; Vinny voice) is live as a fourth channel context. Its look is decade-variable via the look-override (`look.json` per project) rather than one fixed channel look — the first channel to use per-job looks in production (Lazarus was the designed-for case; You Had To Be There is the first to ship it).
