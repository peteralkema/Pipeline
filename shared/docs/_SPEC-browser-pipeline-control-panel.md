# SPEC — Browser-Driven Pipeline Control Panel ("Mission Control") — v2
*Build spec + architecture guidance. Load this fresh next session, on the LAPTOP, with `shared/orchestrate.py`, `shared/serve_review.py`, `shared/review.py`, `shared/make_review_page.py`, and `shared/recreation_pipeline.py` open. This is a real architecture piece — turning the CLI orchestrator into a browser-driven service that visualises the ENTIRE video as a storyboard — not a UI tweak. Build it in the phased order in §8; do not try to do it all at once.*

*v1 written 12 June 2026 after the the-daughters run. **v2 written 12 June 2026 (same day, later)** after a long design session that reframed the goal from "stills review page with a launch button" to "a full end-to-end storyboard document of any video, every asset shown in beat order, editable, with a publish panel at the bottom." v2 also banks the real `proj_paths` resolver bug (it bit twice in one session), the Mode B overlay model, and the no-sessions rule. **Where v1 and v2 disagree, v2 wins.***

---

## 0. The one-paragraph goal (v2 — REFRAMED)

One browser tab is the whole operator surface AND the whole storyboard. Open a bookmarked URL → pick a **channel** from a dropdown → pick a **project** from a dropdown → set **live/dry-run** and **log level** → click **Launch**. The orchestrator runs server-side as a background job. The page is a **timeline document of the video**: a scroll, top to bottom, through every beat in the sequence it appears, each beat a row showing whatever assets exist for it so far — the Mode A still, then (once animated) the actual Kling clip playing inline, the measured duration, the narration, and any Mode B card floating on it. Long legs spin silently and surface each **gate as page state**. At the bottom: the assembled `final_video.mp4` playing inline, the YouTube metadata as editable fields, a schedule slot, and an Upload button. Zero terminal. Zero `cd`. Zero paths typed. Zero tmux. **No sessions, no expiry, ever.** The human does only human tasks: choose, listen, look, judge, edit, click.

**The reframe in one line (v2):** this is not a review gate that grew features — it is **the assembly, visualised, before you spend on the expensive stage.** You see the whole film as cheap assets (stills + audio durations + cards) laid end-to-end and can catch the problem *before* Kling animation, the exact class of problem that previously cost hours of manual Filmora editing.

**Design decision (v1, still holds):** when a long leg runs, the page **spins silently and shows the gate when ready** — no live log streaming in v1. Streaming is a later enhancement.

---

## 1. Why this is the right next build (and what it subsumes)

The the-daughters run proved the core pipeline is solid. **Every point of pain was operator-surface plumbing.** This panel fixes that class of problem at the root.

It **subsumes** these previously-separate backlog items (do them *inside* this build):

1. **Mode A gate auto-serve.** The panel owns the server lifecycle by construction — no separate manual `review.py` step. One always-on server, project selected via the UI, re-resolved per request.
2. **`proj_paths` / launcher path-resolution unification.** The dropdowns *build* the path; the human never types `--project`. (Underlying resolver bug still fixed in code — see §6 — but the UI removes human exposure.)
3. **No-arg interactive launcher `(no path)` halt.** Replaced by the Launch button.
4. **Stale-server / wrong-project review page.** One server, project chosen in UI, re-read per request, no symlink-cache race.

**The bugs this session that PROVE the rules (banked as motivation):**
- **The `proj_paths` double-bite (12 June).** `--animate-only` resolved correctly against `…/the-daughters/modea` (clips live there); `--assemble-only` then FAILED on the same path because `proj_paths` builds `voice = project/voiceover.mp3` and the voiceover lives at the *project root* (`…/the-daughters/voiceover.mp3`), one level up. Same resolver, two opposite expectations, unblocked only by a manual symlink. This is the canonical example of why §6's single resolver must exist.
- **The stale review server (the-daughters).** `serve_review.py` resolved `.review_current` once at boot and cached it; 184 PNGs on disk, page said "still not generated." Fixed that session only by `lsof -ti :8001 | xargs kill -9`. §3.4 (read per request) dissolves this.
- **The lost tmux prompt (the-daughters).** Orchestrator's blocking `input()` gate orphaned by a dropped pipe. §3.2 (gate protocol, gate state lives in the job record) dissolves this.

---

## 2. The hard architectural truth (read before building)

Today there are **two worlds**: the orchestrator (`orchestrate.py`, a long-running CLI whose gates are blocking `input()` calls) and the review server (`serve_review.py`, stateless HTTP serving stills + per-shot POSTs).

This panel **fuses** them: the browser must *launch and drive* the orchestrator, and the orchestrator's gates must become *web state* instead of terminal prompts.

**The core architectural move: invert control at the gates.** The orchestrator must be able to **pause and yield control back to a coordinator**, expose "I am waiting at gate X with this payload," and **resume when the browser sends a decision**. It stops being a script you watch and becomes a **state machine you observe and nudge.**

---

## 3. Recommended architecture (the load-bearing decisions)

### 3.1 One long-lived **coordinator/job service**, not "the browser runs orchestrate.py"

A single always-on **coordinator service** (`pipeline_server.py`, the evolution of `serve_review.py`) that:
- Serves the control-panel/storyboard page and the assets (stills, clips, final video).
- Owns a **job registry** (in memory + a small on-disk JSON per run, so a restart recovers state).
- **Spawns render work as a detached background job** and tracks status.
- Exposes a small **JSON API** the page polls: `GET /api/state?job=…` → `{phase, status, gate, beats:[…]}`.
- Receives **gate decisions** as POSTs: `/api/gate/audio`, `/api/gate/stills`, plus per-beat edits.

The render job and the web server are **separate processes/threads.** The browser is a *thin observer.* If the browser closes, the job keeps running; reopen and it reattaches by reading job state. **This is the single most important decision in the whole spec.**

The dropdowns replace the `.review_current` symlink + `review.py` repoint. Channel dropdown reads channel folders (anything with `channel.json`); project dropdown populates from the chosen channel's `projects/`. The selection becomes **job state held server-side.** No symlink, no repoint command, no boot cache.

### 3.2 Gates become a **gate protocol**, not `input()` calls

```
reach a gate ->
  write gate state to the job record:  {gate:"audio", status:"waiting", payload:{...}}
  block the JOB (not a terminal) until the job record's gate decision is set
  read decision, clear gate, continue
```

The decision arrives via the web API writing into the job record. **The orchestrator never calls `input()` again.** Build the gate protocol once; every gate (audio, stills, Mode B, motion, thumbnail, convergence, upload) uses it.

> Migration tip: keep a `--headless`/CLI fallback that drives the same gate states via `input()`, so you're never locked out if the web layer breaks mid-render. The gate's *state* is the source of truth; terminal and browser are two clients of it.

### 3.3 The page is **state-driven**, rendered from job state

Page = function of job state. But v2 makes the *body* richer than v1's single-panel-per-phase model — see §4. Page-level phase still governs the top controls (Launch / gates); the body is a continuous beat-timeline.

### 3.4 Server-side **truth**, client-side **render**, **read per request**

All real state lives server-side in the job record. The browser polls and renders, holds no authoritative state. **Every request re-reads the active project from the job record — nothing cached at boot.** This is the dissolution of the stale-server bug. Refresh anytime, open on phone mid-render, two tabs stay consistent.

Cost: a sub-ms read of a few-hundred-byte JSON per request. Free at one-operator volume. Caching is the whole bug, so we deliberately don't.

### 3.5 **No sessions. No expiry. Ever.** (HARD CONSTRAINT — v2)

Auth is the `X-Review-Key` header/query check already shipped — a static key, checked per request, **no server-side session state, no expiry timer.** The "session expired due to inactivity" pattern comes from servers that hold login state and age it out; we hold none. The bookmark works today, tomorrow, after a reboot, after a week away. **No future feature may introduce a session or an expiry.** Keep every new POST behind the same `_key_ok` header-or-query check; don't invent a second auth path.

### 3.6 Dropdown safety — idiot-proof (v2)

While a job is active (`phase !== "idle"`), the dropdowns **lock** (greyed, unclickable) and show the running channel/project. Launch is **hidden**, replaced by a status line ("▶ figures-test running — animating 184 clips"). You cannot switch project mid-render and yank the grid out from under a live job. When the job reaches `done` (or is explicitly cleared), `phase` flips to `idle`, dropdowns unlock, Launch returns. Every irreversible/spend action (Launch, Generate Clips, Upload) is a deliberate button press that only exists in the right phase — never a side effect of a dropdown.

---

## 4. The timeline-document model (v2 — THE CORE REFRAME)

The page body is **not** "the panel for the current phase." It is **a scrollable list of beat-rows, each rendering its own assets independently, based on that beat's type and state.** Beat 7 can show a finished clip while beat 8 shows a bare still while beat 9 is a Mode B card — all visible at once, in beat order.

### 4.1 The unit is the **beat-row**; a row is a **cell registry**

Given a beat's `{mode, stage, assets, overlays}`, the row renders the right cells:
- **still cell** — the Mode A Flux still.
- **clip cell** — once animated, the Kling clip inline (looping, muted).
- **narration cell** — the spoken words (the timing source).
- **duration cell** — measured seconds from durations.json (now); a per-beat audio scrubber later (schema ready, not built).
- **prompt/provenance cell** — the image prompt that rendered + which file each value came from (the glass-box; cures operator blindness).
- **motion cell** — per-shot motion input (later; backend seam `animate_still(still, motion_prompt, out)` already exists).
- **overlay cell(s)** — Mode B cards floating on this beat (see §5).

New asset type later = **new cell renderer in the row**, not a new page. Growth stays additive at the *row* level — finer-grained and more future-proof than v1's phase-level panels.

### 4.2 UI is a pure function of `beats[]`

`page = f(beats[])`, `row = f(beat)`, `cell = f(beat, asset_type)`. Recursive, state-driven. Add a field, render a cell. Never store "is this gate open?" as a hand-flipped JS boolean — derive everything from server state.

### 4.3 The five growth rules (from v1, still binding)

1. **UI is a pure function of job/beat state.** (Non-negotiable.)
2. **Cells/panels are independent modules keyed by type/phase.** No cell reaches into another's internals.
3. **Generate the page; never hand-edit generated HTML.** Serve the page dynamically (generated in-process or static assets read fresh) so feature changes appear on a **service restart**, not a per-project regenerate. Split templates per cell/panel early (a `templates/` dir) before there are six — the doubled-brace f-string footgun gets worse with every addition.
4. **A stable JSON API contract** between page and server. Every feature that needs server work gets a named endpoint.
5. **Know the framework escape hatch and its trigger.** Vanilla JS generated from Python is right now. Migrate to React/Svelte + FastAPI when: >~3 interdependent panels, real-time streaming/WebSockets wanted, hand-managing DOM-diffing, or the doubled-brace generator becomes a regular bug source. The §3–§4 architecture ports cleanly when the day comes. Don't pre-migrate; don't ignore the trigger.

### 4.4 Content-stale vs feature-stale (operator rule)

- Page stale on **content** (new stills/clips/data) → **refresh**.
- Page stale on **features** (new button/cell/panel) → **restart the coordinator** (`systemctl --user restart mission-control.service`), then refresh. (Because the page is served dynamically, there is no per-project HTML to regenerate.)

---

## 5. Mode B = OVERLAY ANNOTATION, never a timeline slice (v2 — banked design)

This is the model that fixes the complexity that previously forced hours of manual Filmora compositing.

### 5.1 The principle

> **Mode A owns time. Mode B is an annotation that points at a span of words inside a Mode A beat.** A Mode B beat is never a slice of the timeline — it is a *highlight on the spine*, with a start/end derived from Whisper finding its words inside the parent Mode A beat's narration.

The card does not consume time. It overlays a window. The voiceover is never cut. There is **no "timeline exceeds voiceover" problem** because the visual timeline is exactly the voiceover length, always — Mode A clips tile it completely, cards float above. A card may **outlive its phrase** (a $13B counter that needs 3s though the words took 0.8s just keeps floating over the still-playing Mode A clip underneath). That is the feature, not a bug.

### 5.2 Authoring (the script stage)

The human writes the full sentence as Mode A, then immediately marks the phrase to card:

```
[A] the cat chased the dog around the house and then the dog sat on the mat and then the dog chased the cat around the house
VISUAL: ...
[B:QuoteCard] the dog sat on the mat
```

Adjacency here is **authoring convenience** — natural to write the sentence then the carded phrase right after it.

### 5.3 Parse-time inference → stored fact

`parse_script.py` resolves the adjacency into a **stored link**: it writes `parent_index` (and `phrase`) onto the Mode B beat. **Inference rule:** a Mode B beat's parent is the **immediately preceding Mode A beat**, and its `phrase` **must be a substring of that beat's narration**. If the phrase isn't found in the preceding Mode A beat, the parser **warns** (safety net against a typo producing a detached card). Substring-in-preceding-beat is unambiguous; bare repeated-phrase matching could mis-target a phrase that appears twice.

From this moment the link is a **fact in the data**, not a fact about position. In `beats.json` onward, the Mode B beat carries `parent_index: N` and **need not be adjacent** — it can be reordered anywhere; the tie holds because it's stored. This is also what makes on-page card editing safe (see §5.5): edit the card's words and the link survives because it lives in the field, not in matching script text.

### 5.4 Resolution & rendering on the page

`build_beats_view()` walks beats in order. A Mode B beat **with** `parent_index` does **not** become a top-level row — it folds into its parent's `overlays[]`, with `overlay_start/overlay_end` computed by scoping its `phrase` to the parent's `[audio_start, audio_start+duration]` window in the Whisper timestamps. That scoping is the "match the *right* 'mat'" guarantee — only possible because we know the parent.

- **Mode B with `parent_index` → OVERLAY:** nested in the parent row, card thumbnail positioned along the parent's duration bar at `overlay_start..overlay_end`, highlighted phrase shown under the narration exactly where it occurs. Owns no time. **This is the assembly, visualised, for free.**
- **Mode B without `parent_index` → CUTAWAY:** its own row, owns its time (true chapter break / standalone card — the old sequence model, still valid).
- **Pure Mode A video → ZERO Mode B chrome.** Page reads `any(b.mode=="B")` — false → no overlay UI at all. Sacred Dawn / Final Hours pages look exactly like a stills storyboard. You never see a concept you aren't using.

### 5.5 Editing a card on the page (scope locked v2)

A card thumbnail in its parent row exposes:
- the rendered Remotion card (looping, muted),
- the **payload as editable fields** + a **raw props JSON** box,
- (later) anchor phrase, duration, component-type controls,
- a **Re-render this card** button → server renders *this beat only* (`dispatch.py --only N`), swaps the nested preview.

**Schema decision: payload per beat (editable, safe); component by REFERENCE (`"QuoteCard"`, a pointer to shared `.tsx`).** Editing the payload is scoped to this card. Editing the component *code* would change every card of that type in every episode — a global change; deferred and, when built, must be a separately-labeled "edit template (affects all)" action. We do NOT store full tsx per beat (that would fork every card and make "fix the QuoteCard font everywhere" a 200-edit job).

**Three edit types, different costs (page does only the work each demands):**
1. **Content** (spelling, the number, attribution) → payload change → re-render this card. No Whisper. **— ENABLED NOW.**
2. **Anchor phrase** (which words trigger it) → needs Whisper to recompute `overlay_start` in the parent window. **— DEFERRED.**
3. **Duration** (drag longer/shorter) → `overlay_end = overlay_start + d`. No render, no Whisper, instant. **— DEFERRED.**
4. **Element-type swap** (QuoteCard ↔ ChapterCard etc.) → re-render as the new component. **— DEFERRED.**

Schema **carries** `phrase`, `overlay_start`, `overlay_end`, `component` from day one (so previews resolve correctly); only the *edit controls* for the deferred three come later. No retrofit.

### 5.6 Honest caveat: the page leads the assembler

The storyboard can **preview/edit/re-render** overlays correctly well before the pipeline can **assemble** them. Dual-mode A+B interleave (the 4c compositing of card-over-clip at `overlay_start..overlay_end`) is **not built** — convergence currently does the Mode-A path only. This is the right order (see the bug for free, fix it cheap, then build the assembler that honours the preview). For pure-Mode-A channels none of this matters — it's all invisible.

---

## 6. The data spine — `_index.json` is the SOLE join authority (v2 — confirmed against real data)

Confirmed by recon against `the-daughters` (184 beats, all assets on disk):

**Beat object (the real ten fields):** `index` (0-based), `mode`, `component`, `payload`, `narration`, `found_line`, `visual`, `face_hold`, `silence_after`, `warnings`.

**The artifacts and their join keys:**
- `beats_full.json` = `{header, beats}`. Header IS the YouTube metadata (title/description/tags). 184 beats.
- `beats.json` = same beats, flat.
- `storyboard.json` = a **flat list** of 184 shot objects (image prompts post-Claude-slice). *(Shot-object keys to confirm in Phase 0 — the one unconfirmed field-set.)*
- `durations.json` = **dict keyed by beat index as a STRING.** `durations["6"]` = `{duration:6.86, audio_start:56.98, source:"whisper", frames:206, mode:"A", component:null}`. Joins **directly by beat index** — no remap.
- `_index.json` = **dict `engine_shot_number(str, 1-based) → beat_index(int, 0-based)`.** `{"1":0, "2":1, … "7":6, …}`. So `shot_007.png` ↔ beat index 6 (the 7th beat).
- `voiceover.mp3` / `voiceover.json` (Whisper word timestamps). **Note: voiceover lives at the PROJECT ROOT**, not under `modea/` — the source of the assemble path bug.
- `modea/stills/shot_NNN.png`, `modea/clips/shot_NNN.mp4`.

**THE HARD RULE (proven, not assumed):**
> To find the still/clip for a beat, **never compute `shot_{index+1}`.** Invert `_index.json` to build `beat_index → engine_shot`, then load `shot_{engine_shot:03d}`. Durations join by `str(beat_index)`. Assets join through the inverted index map. The map is currently identity-with-offset (all-Mode-A, no drops) — that is LUCK, not safety. A Mode B beat or a dropped TTS beat makes the engine's contiguous `001,002,…` numbering map to NON-contiguous beat indices, and position-join silently lies. The storyboard reads assets through the same `_index.json` the assembler uses, so what you see is what ends up in the cut at that timestamp — by construction.

**The 185-vs-184 stray-file lesson:** inverting the map (not listing the directory) means a stray/duplicate still simply never maps to a beat — ignored, not misaligned. Map-not-directory protects alignment.

---

## 7. The publish panel (v2 — the bottom of the scroll)

The same scroll ends in a **publish panel** at `phase: done`:
- the assembled `final_video.mp4` playing inline,
- the YouTube metadata as **editable fields, read straight from the header** (`title/description/tags` — the header IS the metadata, no separate metadata.json), writable back so you fix the title without touching the file,
- a **schedule** field (Final Hours doctrine: 01:00 CET ≈ US prime),
- an **Upload** button.

**Hard safety rules:**
- Upload uploads as **PRIVATE/scheduled to Studio**, never straight-to-public; shows title/visibility/schedule for a final confirm. This preserves the existing "review auto-metadata in Studio before public" habit and is the safe default for a power-law channel.
- **Lights up per channel as OAuth is wired** (Final Hours has working auth; Sacred Dawn/Synthetic/others not yet). Built ready, dark until wired. (This is backlog item: channel-agnostic uploader + batch exit-gate.)
- **Hidden for batch jobs.** A batched multi-part job (header `parts: N`) must **stop at `final_video.mp4`** and show "this is a batch — cut in Filmora, no auto-upload" (one job → many videos breaks single-metadata). You cannot accidentally upload a 4-in-1 reel as one video.

**Music (future field, not now):** music added in Filmora for now; an **Artlist.io** subscription exists. When wired, music resolves channel-then-project like `look.json` via a `music.json` (`{"source":"artlist","category":"sacred-epic","track":"…"}`) — music-BY-CATEGORY is a known future field. Publish panel will show "music: sacred-epic (Artlist)" as a provenance line. Leave room; build nothing now.

---

## 8. The job-record schema (v2 — built against confirmed data)

One JSON file per run. The `beats[]` carries full provenance so the page shows the data AND the alignment is trustworthy.

```jsonc
{
  "job_id": "the-daughters-1718200000",
  "channel": "sacred_dawn",
  "project": "the-daughters",
  "phase": "gate_stills",              // idle|rendering_audio|gate_audio|rendering_stills|
                                       //   gate_stills|animating|assembling|done
  "paths": { /* from the single resolver — §6 / §9 */ },
  "header": { "title": "...", "description": "...", "tags": [...] },
  "beats": [
    {
      "index": 6,                      // 0-based, the SPINE / join key
      "mode": "A",
      "stage": "animated",             // authored|still|reviewed|animated|assembled
      "narration": "Before the rain. Before the ark...",
      "visual": "a single clay oil-lamp burning on a wooden sill...",
      "duration_s": 6.86,
      "audio_start": 56.98,
      "face_hold": false,
      "look_resolved": "channel default (biblical epic)",
      "overlays": [                    // Mode B cards floating on THIS beat (empty for most)
        // {
        //   "child_index": 42, "component": "QuoteCard",
        //   "phrase": "the dog sat on the mat",
        //   "overlay_start": 314.9, "overlay_end": 316.3,  // ABSOLUTE seconds
        //   "payload": {...}, "highlight": "mat"
        // }
      ],
      "assets": {
        "still": { "path": "modea/stills/shot_007.png", "engine_shot": 7, "via": "_index.json" },
        "clip":  { "path": "modea/clips/shot_007.mp4",  "engine_shot": 7, "via": "_index.json" },
        "audio": { "slice": null, "duration_s": 6.86 }   // per-beat slice path lands later
      },
      "source_files": {                // the glass-box — what file each value came from
        "narration": "beats_full.json",
        "visual": "storyboard.json",
        "duration": "durations.json",
        "index_map": "_index.json"
      }
    }
  ]
}
```

Invariants: `index` is the 0-based spine and the join key for everything; durations join by `str(index)`; still/clip join `index → engine_shot` **through `_index.json`**, never by position; a Mode B beat with `parent_index` is **folded into its parent's `overlays[]`**, not emitted as a top-level row.

---

## 9. Code-level fixes to fold in (inside the build, not separate patches)

- **Unify project-path resolution (§6 / the double-bite bug).** `proj_paths()` (recreation_pipeline.py ~1083) builds ALL six paths off the one `project` arg AND auto-prefixes a bare name with `projects/` only if a top-level `projects/` exists in cwd — which fails under the channel-folder architecture and resolves differently from `orchestrate.py`. The split between `--animate-only` (wants the `modea` path) and `--assemble-only` (wants voiceover at the project root) is THIS bug. **One resolver, used by orchestrate, finish, and the coordinator** — given channel + project slug, returns the canonical paths (and knows voiceover lives at the project root, clips/stills under `modea/`). The dropdowns produce channel+slug; the resolver does the rest. Kill the cwd-dependent auto-prefix.
- **Server re-reads the active project per request, not at boot.** In the coordinator model "active project" is just job state, so the symlink-cache bug dissolves.
- **Audio-gate label is cosmetic-hardcoded "Victor."** Synthesis correctly uses `voice_id` from channel.json; only the gate banner says "Victor." Render the voice from job state (`payload.voice_id`) in the audio-gate panel — shows "Elliot" correctly. Free fix while rebuilding that gate.

---

## 10. Phased build order (don't do it all at once)

**Phase 0 — Resolver + `build_beats_view()` + job-record foundation.** Build the single project-path resolver (§9). Build `build_beats_view()`: read beats_full/storyboard/durations/`_index.json`, invert the index map, resolve overlays, emit the §8 per-beat record with provenance. Define the job-record schema. **No UI yet — prove `build_beats_view()` emits a correct record against `the-daughters` real data on the box** (beat 6 → shot_007, 6.86s, narration + prompt + provenance correct) before any server/HTML exists. *(First task: confirm storyboard.json shot-object keys — the one unconfirmed field-set.)*

**Phase 1 — Gate protocol + headless parity.** Convert the audio & stills gates from `input()` to read/write the job record (§3.2), keeping a CLI fallback driving the same states. Prove a full run still works end-to-end from the terminal but driven by job-record state. No browser yet — de-risk the hard part in isolation.

**Phase 2 — Coordinator service + control panel (Launch + dropdowns).** Evolve `serve_review.py` into the coordinator: channel/project dropdowns (read folder structure), live/dry-run + log-level controls, Launch → spawns the job. Page polls `/api/state`, spins silently. Surface the **audio gate** (Accept/Swap, voice read from state). Dropdown-lock safety (§3.6).

**Phase 3 — Storyboard body + stills gate.** The beat-timeline body renders from `beats[]` (§4): each row shows still + narration + duration + provenance, reusing the proven per-shot controls (AI Fix/Regenerate/Restill) as the stills cell. **Generate Clips** button replaces terminal `go`. First full browser-only run. Then: clips render inline in their rows as they complete.

**Phase 4 — Motion direction.** Per-shot motion inputs on the stills cells; carry through job record into `animate_still`'s `motion_prompt` (backend seam exists). New cell, not a rewrite.

**Phase 5 — Template split + Mode B overlay cells.** Split the generator into per-cell/panel templates (Rule 3) BEFORE adding Mode B. Then add overlay cells (§5): nested card preview, payload edit, re-render-this-card. Pure-Mode-A pages remain Mode-B-free.

**Phase 6+ — Publish panel, upload gate, batch.** Final video inline + editable header metadata + schedule + private-upload-with-confirm (§7); per-channel OAuth wiring; batch exit-gate. Each is a new phase + cell/panel + endpoint.

Ship Phase 2–3 first and live on it; that alone removes ~90% of the pain. Everything after is additive by design.

---

## 11. The test for "am I building it right?"

At every step: **"Is this new feature a new cell/panel + (maybe) a new endpoint + a new field — and nothing else?"** If yes, the architecture holds. If a feature forces you to touch three existing cells or add show/hide flags, stop: push the new thing into its own cell/phase rather than smear it. Growth must stay additive. Both named future features pass this test: **motion direction** = a cell on the stills row + a `motion` field; **Mode B** = overlay cells + the §5 resolution. That they fit as pure additions is the signal the architecture is right.

---

*Maintained by Peter + Claude. v2 banks the timeline-document reframe, the Mode B overlay model, `_index.json` as sole join authority (confirmed against real data), no-sessions/no-expiry, the publish panel, music-by-category as a future field, and the real proj_paths double-bite as Phase-0 motivation. The render core is proven; this makes driving it a browser-only, human-tasks-only experience — and the page becomes the assembly visualised before the expensive stage, so the bug that once cost hours in Filmora is caught for free. Sibling docs: `_YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md` (umbrella), `_ante-machinam.md` (craft), `_machina.md` (operations).*
