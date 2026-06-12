# SPEC — Browser-Driven Pipeline Control Panel ("Mission Control")
*Build spec + architecture guidance. Load this fresh next session, on the LAPTOP, with `shared/orchestrate.py`, `shared/serve_review.py`, `shared/review.py`, and `shared/make_review_page.py` open. This is a real architecture piece — turning the CLI orchestrator into a browser-driven service — not a UI tweak. Build it in the phased order in §6; do not try to do it all at once.*

*Written 12 June 2026, after the the-daughters (Sacred Dawn ep2) run, where the human friction was entirely in the command line — wrong directory, lost tmux prompt, manual server restarts, path-resolution mismatches. The pipeline core ran flawlessly; the **operator surface** is what hurt. This spec fixes the surface.*

---

## 0. The one-paragraph goal

One browser tab is the whole operator surface. Open a bookmarked URL → pick a **channel** from a dropdown → pick a **project** from a dropdown → set **live/dry-run** and **log level** → click **Launch**. The orchestrator runs server-side as a background job. The page spins through the long legs (audio, Whisper, stills) and surfaces each **gate as page state**: the audio gate appears as Accept/Swap buttons; the stills appear below for review with the existing per-shot controls; a **Generate Clips** button replaces today's terminal `go`. Zero terminal. Zero `cd`. Zero paths typed by a human. Zero tmux. The human does only human tasks: choose, listen, look, judge, click.

**Design decision already made (12 June):** when a long leg is running, the page **spins silently and shows the gate when ready** — no live log streaming in v1. Streaming is a later enhancement, not a launch requirement. This keeps the first build tractable.

---

## 1. Why this is the right next build (and what it subsumes)

The the-daughters run proved the core pipeline is solid — parse, audio, Whisper, 184 stills all rendered clean and the orchestrator marched to the stills gate without a hitch. **Every point of pain was operator-surface plumbing**, and this panel fixes that class of problem at the root rather than patching each bug:

This panel **subsumes** these previously-separate backlog items (do them *inside* this build, not before it):

1. **Mode A gate auto-serve** (the "click a bookmark, see stills, no commands" spec). The panel owns the server lifecycle by construction — there is no separate manual `review.py` step anymore. Root cause already diagnosed: `serve_review.py` resolves the `.review_current` symlink once at boot and caches it; the gate prints a command instead of running it. The panel makes that irrelevant — one always-on server, project selected via the UI, re-resolved per request.
2. **`proj_paths` / launcher path-resolution unification.** The dropdowns *build* the path; the human never types `--project`, so the `the-daughters` vs `sacred-dawn/projects/the-daughters` vs `.../modea` mismatch (which bit `recreation_pipeline.py finish` and the no-arg launcher today) stops existing at the operator level. (The underlying resolver bug should still be fixed in code — see §5 — but the UI removes the human exposure to it.)
3. **No-arg interactive launcher `(no path)` halt.** Replaced entirely by the Launch button.
4. **Stale-server / wrong-project review page.** One server, project chosen in UI, no symlink-cache race.

So this is not a new project competing with the backlog — it is the thing that **absorbs four backlog bugs** and turns them into non-issues.

---

## 2. The hard architectural truth (read before building)

Today there are **two worlds**:
- **The orchestrator** (`orchestrate.py`) — a long-running CLI process whose gates are blocking `input()` calls in a terminal.
- **The review server** (`serve_review.py`) — a stateless HTTP server that shows stills and handles per-shot POST actions.

This panel **fuses** them: the browser must *launch and drive* the orchestrator, and the orchestrator's gates must become *web state* instead of terminal prompts. That is the whole difficulty, and it dictates the architecture. Get the seam right and everything else is easy. Get it wrong (e.g. trying to keep `input()` and bolt a browser on) and it will fight you forever.

**The core architectural move: invert control at the gates.** Today the orchestrator *drives* and *blocks* at gates. In the new model, the orchestrator must be able to **pause and yield control back to a coordinator**, expose "I am waiting at gate X with this payload," and **resume when the browser sends a decision**. The orchestrator stops being a script you watch and becomes a **state machine you observe and nudge**.

---

## 3. Recommended architecture (the load-bearing decisions)

These are the decisions that matter for the next two years of growth. Make them now, deliberately.

### 3.1 One long-lived **coordinator/job service**, not "the browser runs orchestrate.py"

Do **not** have the web server shell out to `orchestrate.py` and try to pipe its stdin/stdout to the browser. That couples a UI process to a render process and dies the moment SSH blinks (exactly today's tmux pain, relocated).

Instead: a single always-on **coordinator service** (an evolution of `serve_review.py` into something like `pipeline_server.py`) that:
- Serves the control-panel page and the review page.
- Owns a **job registry** (in memory + a small on-disk JSON per run, so a server restart can recover state).
- **Spawns the render work as a detached background job** (subprocess or worker thread) and tracks its status.
- Exposes a small **JSON API** the page polls: `GET /api/state?job=…` returns `{phase, status, gate, payload}`.
- Receives **gate decisions** as POSTs: `POST /api/gate/audio {decision: keep|swap}`, `POST /api/gate/stills {decision: go|skip}`.

The render job and the web server are **separate processes/threads**. The browser is a *thin observer* that polls state and posts decisions. If the browser closes, the job keeps running; reopen the tab and it reattaches by reading job state. This is the single most important decision in the whole spec — it makes the system resilient by construction.

### 3.2 Gates become a **gate protocol**, not `input()` calls

Define one tiny internal contract the orchestrator uses at every gate, regardless of gate type:

```
reach a gate ->
  write gate state to the job record:  {gate: "audio", status: "waiting", payload: {voiceover_url, minutes, voice_id}}
  block the JOB (not a terminal) until the job record's gate decision is set
  read decision, clear gate, continue
```

The decision arrives via the web API writing into the job record. **The orchestrator never calls `input()` again.** It waits on a job-record field (poll a small file/DB, or an event). This one abstraction is what lets every current and future gate (audio, stills, and later Mode B, motion-direction, thumbnail, convergence, upload) work the same way through the browser. **Build the gate protocol once; every gate uses it.**

> Migration tip: keep a `--headless`/CLI fallback that still uses `input()` for the same gate states, so you are never locked out if the web layer breaks mid-render. The gate's *state* is the source of truth; terminal and browser are two clients of it.

### 3.3 The page is **state-driven**, rendered from job state — not a script of steps

The control panel should render itself from `GET /api/state`. The page is a **function of job phase**:
- `phase: idle` → show channel/project dropdowns + Launch.
- `phase: rendering_audio` → spinner ("rendering narration…").
- `phase: gate_audio` → audio player + Accept/Swap.
- `phase: rendering_stills` → spinner ("rendering 184 stills…").
- `phase: gate_stills` → the stills grid + per-shot controls + **Generate Clips**.
- `phase: animating` → spinner ("animating 184 clips…").
- `phase: done` → link to `final_video.mp4`.

This is the React-style "UI is a function of state" discipline, done in vanilla JS. It is what keeps the page sane as it grows: **you add a phase and a panel, never a tangle of show/hide flags.** (See §4.)

### 3.4 Server-side **truth**, client-side **render**

All real state lives server-side in the job record (phase, gate, decisions, per-shot status). The browser holds **no authoritative state** — it polls and renders. This means: refresh the page anytime and nothing is lost; open it on your phone mid-render and it shows the same thing; two tabs stay consistent. The single hardest bug class in growing web UIs is client/server state drift — this architecture refuses to allow it.

### 3.5 Reuse the auth + key model you just fixed

The `X-Review-Key` header fix (shipped 12 June) is the right pattern — keep every new POST (Launch, gate decisions) behind the same `_key_ok` header-or-query check. Don't invent a second auth path.

---

## 4. Architecture guidance for growth (the part you asked for)

This page **will** grow — motion direction, Mode B Remotion, thumbnail review, upload, batch. Here is how to keep it from becoming a 4,000-line `review.html` that nobody can touch. Five rules, in priority order.

### Rule 1 — **UI is a pure function of job state.** (The non-negotiable one.)
Every panel renders from the job record. Never store "is the audio gate open?" as a JS boolean you flip by hand — derive it from `state.phase === "gate_audio"`. When you add motion direction or Mode B, you add a **phase** and a **panel that renders for that phase**, and the rest of the UI is untouched. This single rule is what makes growth additive instead of entangling.

### Rule 2 — **Panels are independent modules keyed by phase.**
Structure the page as a registry: `phase -> render function`. Each panel (Launch, AudioGate, StillsGrid, MotionDirection, ModeBReview, ThumbnailGate, ConvergenceGate, UploadGate) is a self-contained function that takes job state and returns DOM. Adding a feature = writing one new panel function + one new phase. **No panel reaches into another panel's internals.** If you later move to a framework (see Rule 5), this structure ports cleanly because it already thinks in components.

### Rule 3 — **Generate the page; never hand-edit generated HTML.**
You already learned this today the hard way (the `review.html` is emitted by `make_review_page.py`). Keep that discipline absolutely: the panel HTML/JS is **generated from one source generator**, and per-project pages are regenerated, never patched in place. As panels multiply, consider splitting the generator's giant f-string into **separate template files per panel** (a `templates/` dir, one file per panel, concatenated at generate-time). The f-string-with-doubled-braces approach (`{{ }}`) that bit us today gets *worse* with every panel added — moving panels to real template files (Jinja2, or even plain `.js` files served as static assets) removes the doubled-brace footgun entirely. **Do this split early, before there are six panels, not after.**

### Rule 4 — **A stable JSON API contract between page and server, versioned in your head.**
The page and server talk only through a small, explicit JSON API (`/api/state`, `/api/launch`, `/api/gate/<name>`, plus the existing per-shot `/api/aifix`, `/api/restill`). Treat this contract as the real interface. When you add motion direction, it's a new field in the stills-gate payload + a new POST (`/api/motion {shot, prompt}`) — **not** a new ad-hoc fetch wired into random JS. Every feature that needs server work gets a named endpoint. This keeps the surface auditable: you can always answer "what can the page ask the server to do?" by listing the routes.

### Rule 5 — **Know your framework escape hatch, and the trigger to take it.**
Vanilla JS generated from Python is right *now* — no build step, no deps, serves from a stdlib HTTP server, matches your vibe-code-in-Python reality. But there is a ceiling. **The trigger to migrate to a real frontend (React/Svelte/Vue + a small FastAPI backend) is when any one of these is true:** (a) the page exceeds ~3 panels with interdependent state, (b) you want real-time log streaming / progress bars (WebSockets), (c) you're hand-managing more than a little DOM-diffing, or (d) the doubled-brace generator becomes a regular source of bugs. Until then, vanilla + generator is correct. **Don't pre-migrate** (you'll burn weeks building infra for features you don't have yet), but **don't ignore the trigger** either (past it, every feature costs 3× in vanilla). The architecture in §3 — state-driven, server-truth, panel registry — **ports cleanly to a framework when the day comes**, which is exactly why it's worth building that way now even in vanilla.

### A note on the two future features you named, so today's decisions fit them:

- **Motion direction (per-shot, pre-animation).** This is a **field on the stills-gate panel**: each shot card gets a motion-prompt input. On Generate Clips, those prompts flow to `animate_still(still, motion_prompt, out)` — which **already takes `motion_prompt` as its second arg** (confirmed in `recreation_pipeline.py:589`). So the backend seam already exists; this feature is almost entirely UI + carrying the field through the job record into the animate call. Architecturally it's "add inputs to the StillsGrid panel + a `motion` field per shot in job state." It fits the model perfectly — which is the test that the model is right.
- **Mode B (Remotion graphics).** This is a **new phase + new panel** (`gate_modeB`) that renders for projects whose composition scan found `[B:…]` beats. The orchestrator already decides legs by composition (Mode B leg skipped when absent). In the panel model, the Mode B review is just another phase the page renders when the job reaches it — Sacred Dawn (Mode-A-only) never enters that phase; Synthetic does. Again: additive, not entangling. The architecture's job is to make "Synthetic has an extra gate" a one-panel addition, not a rewrite.

The meta-point: **both features you're worried about fit the §3/§4 model as pure additions.** That's the signal the architecture is right. If a future feature *doesn't* fit "new phase + new panel + new endpoint," that's the signal to stop and rethink the seam before building it.

---

## 5. Code-level fixes to fold in (do these inside the build, not as separate patches)

- **Unify project-path resolution.** `proj_paths()` in `recreation_pipeline.py` (~line 1083) auto-prefixes a bare name with `projects/` only if a top-level `projects/` dir exists in cwd — which fails under the channel-folder architecture (`sacred-dawn/projects/…`), and resolves differently from `orchestrate.py`. Today's `finish` crash (`FileNotFoundError: the-daughters/clips`) is this bug. **One resolver, used by orchestrate, finish, and the coordinator** — given a channel + project slug, returns the canonical paths. The dropdowns produce channel+slug; the resolver does the rest. Kill the cwd-dependent auto-prefix.
- **Make the server re-read `.review_current` (or the active project) per request, not at boot.** This is the symlink-cache bug. In the coordinator model the "active project" is just job state, so this dissolves — but if any symlink remains, read it per request.
- **Audio gate label is cosmetic-hardcoded "Victor."** The synthesis correctly uses `voice_id` from channel.json (confirmed: `_synthesize_chunk` reads `config["voice_id"]`, prints the real voice). Only the gate *banner text* says "Victor." In the new audio-gate panel, render the voice from job state (`payload.voice_id`), so it shows "Elliot" correctly. Free fix while rebuilding that gate.

---

## 6. Phased build order (don't do it all at once)

**Phase 0 — Resolver + job-record foundation.** Build the single project-path resolver (§5). Define the job-record schema (a JSON file per run: `phase`, `gate`, `decisions`, per-shot status). No UI yet. This is the spine; everything hangs off it.

**Phase 1 — Gate protocol + headless parity.** Convert the orchestrator's audio and stills gates from `input()` to **read/write the job record** (§3.2), keeping a CLI fallback that drives the same states. Prove a full run still works end-to-end from the terminal but now driven by job-record state. *No browser yet — this de-risks the hard part in isolation.*

**Phase 2 — Coordinator service + control panel (Launch + dropdowns).** Evolve `serve_review.py` into the coordinator: channel/project dropdowns (read folder structure), live/dry-run + log-level controls, Launch button → spawns the job. Page polls `/api/state`, spins silently (the agreed v1 behavior). Surface the **audio gate** as Accept/Swap.

**Phase 3 — Stills gate in the panel.** The existing stills grid + per-shot controls (now that AI Fix/Regenerate work) render as the `gate_stills` phase. **Generate Clips** button replaces terminal `go`. This is the first full browser-only run.

**Phase 4 — Motion direction.** Add per-shot motion inputs to the stills panel; carry through job record into `animate_still`'s `motion_prompt`. (Backend seam already exists.)

**Phase 5 — Template split + Mode B panel.** Split the generator into per-panel templates (Rule 3) *before* adding Mode B. Then add the `gate_modeB` phase/panel for Synthetic.

**Phase 6+ — Thumbnail gate, upload gate, batch.** Each is a new phase + panel + endpoint. By now the pattern is muscle memory.

Ship Phase 2–3 first and live on it; that alone removes 90% of today's pain. Everything after is additive by design.

---

## 7. The test for "am I building it right?"

At every step, ask: **"Is this new feature a new phase + a new panel + (maybe) a new endpoint — and nothing else?"** If yes, the architecture is holding. If a feature forces you to touch three existing panels or add show/hide flags, stop: you've drifted from state-driven rendering, and the fix is to push the new thing into its own phase/panel rather than smear it across the page. The whole point of §3–§4 is that **growth stays additive.** Protect that property above all else; it's what turns "the page that grows and grows" from a warning into a feature.

---

*Maintained by Peter + Claude. This spec is the operator-surface upgrade: the render core is proven, this makes driving it a browser-only, human-tasks-only experience — and gives the page an architecture that grows by addition, not entanglement.*
