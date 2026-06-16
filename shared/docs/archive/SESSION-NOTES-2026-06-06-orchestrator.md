# SESSION NOTES — Orchestrator Build (6 June 2026)
## Cold-start handover for the next Claude + Peter

*Read this top to bottom before doing anything. It tells you exactly where the orchestrator build stands, what is PROVEN on the box, what is half-built, and the precise next step. Everything important is committed to the repo or staged; nothing is lost.*

---

## 0. THE ONE-PARAGRAPH SUMMARY
We are building the **master, singular, channel-agnostic orchestrator** (`shared/orchestrate.py`) — the conductor that runs the whole post-script pipeline for any channel (Final Hours, Synthetic, Lazarus) from one input (`beats.json` + script header) to a finished, scheduled YouTube video. Design doc: `shared/docs/SPEC-orchestrator-v1.md` (v2, complete, approved). Build path = **Path 2**: new clean leg-based `orchestrate.py`, old six-phase conductor kept as `orchestrate_legacy.py`, Final Hours moved onto the new machine once trusted, then legacy retired. We build leg-by-leg, testing each rung on the box before the next. **As of end of session: the AUDIO LEG is fully wired + proven on the box, and the MODE B LEG (render) is proven (21/21 clips render) with its review GATE built and tested but its final two files (`modeb_leg.py`, `orchestrate.py`) NOT YET COMMITTED to the repo.**

---

## 1. CRITICAL FIRST ACTION FOR THE NEXT SESSION
**Two files were built and tested this session but never landed in the repo** (the laptop→box file-sync kept failing on which-window confusion — see §6). They are:
- `shared/modeb_leg.py` — the Mode B render leg + the idiot-proof Mode B gate (Piece 3).
- `shared/orchestrate.py` — updated to wire the Mode B gate call after the render.

They are staged in this session's outputs. **Peter is setting up GitHub integration (Claude settings → GitHub Integration) so Claude can read the repo directly — this should be working next session.** FIRST THING: confirm whether these two files are on the box. Run on the box:
```
cd ~/Pipeline && git pull origin main
grep -c "modeb_gate" shared/modeb_leg.py        # need 1 (it was 0 = stale all session)
grep -c "modeb_leg.modeb_gate" shared/orchestrate.py   # need 1
```
- If both return **1** → the files landed (Peter pushed them after all). Skip to §5 (next build step = Mode A leg).
- If either returns **0** → they're still stale. Re-deliver them (via GitHub integration if connected, else base64 box-paste — see §6). The exact current contents are described in §3/§4; if GitHub read access works, diff against what's described here.

---

## 2. WHAT IS PROVEN ON THE BOX (do NOT rebuild)
The pipeline, rung by rung, all tested on the real Hetzner box against Episode 1 ("The Promise", 62 beats, A:41 B:21):

1. **parse_script.py** — reads `script.md`, now with a **front-matter header** (`channel:`, `title:`, `description:` via `>` multiline, `tags:` comma-list, terminated by `---`). `--json` writes the flat beats LIST (back-compat for leg tools); `--json-full` writes `{header, beats}` wrapper (the orchestrator's single input). PROVEN.
2. **Audio leg** (`shared/audio_leg.py`) — wired into orchestrator, PROVEN end-to-end: 2a build_audio_script → 2b generate_episode_vo (Victor, Inworld) → whisper → 2c build_beat_durations → durations.json. Has the **AUDIO GATE** (keep/swap; swap = scp human voiceover + re-whisper + rebuild durations). Long steps (2b, whisper) STREAM child stdout + heartbeat (no more silent hangs). E1 measured 10.7-10.8 min, 39 whisper-measured + 23 silent-hold.
3. **Mode B leg** (`shared/modeb_leg.py`) — render PROVEN: **21/21 clips render on the box**. Shells out to dispatch.py with real durations. Mode B gate (Piece 3) built + tested (NOT yet committed — see §1).
4. **dispatch.py** — Mode B renders each component at ITS OWN durationInFrames (queried via `npx remotion compositions`, parsed), NOT audio-derived frames. Has `_render_env()` that auto-finds the node bin dir and prepends to subprocess PATH (resilient to bare shells). Has `_props_override` path (gate edits render verbatim). All PROVEN.
5. **Mode B review gate** (`shared/make_modeb_review.py` + `shared/serve_modeb_review.py`) — autoplay/loop/muted scrollable HTML page, each card shows SHAPED props (matches clip) with audio-locked fields read-only (e.g. QuoteCard.quote), editable payload + Re-render (one-click, runs dispatch --only N, hot-swaps clip) + Flag. Server tested end-to-end (rerender writes payload, runs dispatch, returns clip; flag records; done signals). COMMITTED + on box.

---

## 3. THE BOX ENVIRONMENT (hard-won — do NOT re-debug)
The single biggest time-sink this session was box environment setup for Remotion. ALL of this is now DONE and must not be re-litigated:
- **Node 20.20.2 installed via nvm** on the box (`~/.nvm/versions/node/v20.20.2/bin`).
- **Remotion 4.0.472** with `@remotion/compositor-linux-x64-gnu` — runs headless on the box.
- **Remotion project moved INTO the repo** at `~/Pipeline/remotion/` (was laptop-only `~/Projects/remotion-learning`). `node_modules/` + `out/` gitignored; `npm install` run on box.
- **`REMOTION_DIR=$HOME/Pipeline/remotion`** added to `~/.bashrc` and `~/.bash_profile`.
- **System libs for headless Chromium installed** via `sudo apt-get install -y libnspr4 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libatspi2.0-0`. (Was failing with `libnspr4.so: cannot open shared object file`.)
- **All nine Remotion components are 120 frames (4 sec)** except SyntheticSequence(210), HelloWorld(150), OnlyLogo(150). Real `npx remotion compositions` output format: `CompId  fps  WxH  FRAMES (X.XX sec)` — dispatch parses this; do NOT use `--quiet` (it suppresses durations).
- **FRESH-SHELL GOTCHA**: a new SSH session does NOT auto-load nvm unless `~/.bash_profile` runs it. dispatch.py self-heals its own subprocess PATH, but if Peter runs things manually he must `export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` first. **BANKED PRINCIPLE: the orchestrator must NOT assume the interactive shell's environment — resolve in code or fail loudly. We hit this twice (REMOTION_DIR, node PATH).**

---

## 4. THE NOT-YET-COMMITTED FILES (exact current state)
**`shared/modeb_leg.py`** (182 lines) contains:
- `_stream(cmd, t, label, cwd)` — runs render with live child stdout + 15s heartbeat.
- `run_modeb_leg(ctx)` — computes Mode B beat indices, verifies REMOTION_DIR, shells to `dispatch.py --render --only <indices> --durations <path>`, collects clips, HALTS precisely naming failed beats if any missing (not false "Node not found").
- `modeb_gate(ctx, rendered_count)` — the idiot-proof gate: prints 3 labelled copy-paste STEPS (STEP 1 = box server cmd, STEP 2 = laptop tunnel cmd, STEP 3 = browser URL), all paths pre-filled, waits for user to type `go`/`skip`.

**`shared/orchestrate.py`** (331 lines) — the conductor. Flow: banner → kickoff prompt (verbosity 1/2/3 + dry/live) → load `{header,beats}` wrapper → preflight (header complete? channel.json resolves? HALT EARLY if not) → `load_resolved_config(channel, project)` resolves `<channel>/channel.json` BY NAME from repo root + `<project>/look.json` override → `decide_legs()` (composition scan, logs each decision) → writes flat beats list → **AUDIO LEG (live)** → **MODE B LEG + MODE B GATE (live)** → other legs announce "not yet wired". Run from repo root `~/Pipeline`; channel resolved from header so "you never think about which folder you're in." ctx carries: t, shared, channel_dir, project_dir, beats_list_json, durations, clips_dir, run_cwd, dry_run, py, box, review_port.

If these need re-delivering and GitHub read works, just verify against the above; if base64 needed, the working copies are byte-identical to what was tested.

---

## 5. THE NEXT BUILD STEP (where to resume)
Per SPEC §11 build order, with audio (3a) and Mode B (3b) done, **the next rung is STEP 4: the MODE A LEG.**
- Mode A leg = orchestrator drives `recreation_pipeline.py`: stills generation → **Mode A gate** (stills review, the heavy aesthetic firewall, reuse v1's `make_review_page.py`/`serve_review.py` ergonomics — they work) → Kling animation.
- KEY SEAM: `recreation_pipeline.py` needs an `--animate-only`-style path so the orchestrator can run stills→gate→animate WITHOUT the engine's own assemble (Synthetic uses the dual-mode assembler, not the engine's). `modea_beats.py` (Step 4b) already translates Synthetic beats → engine `--beats` format and writes the `_index.json` shot→beat map (the keystone for reordering at assembly). Mode A translate+ingest is PROVEN; the full render (real fal stills cost + Kling) is what STEP 4 wires.
- THEN **STEP 5: CONVERGENCE** (the big one): dual-mode assembler (interleave A+B clips in beat order via index map, hold each to measured duration, **freeze-fill** clips shorter than their slot, music mux ported from engine's assemble() at levels 1.15/0.07 loop-to-cover, chapters from ChapterCard beats + timestamps, SRT from script-aligned Whisper) → **thumbnail gate** (manual, NO skip, scp thumbnail to box) → **convergence gate** (DDMM date, 01:00 CET default, full manifest, "Publish & Schedule? y/n" = DONE DONE) → **universal per-channel uploader** (replaces channel-specific upload; per-channel OAuth token in channel folder, Peter sets up auth manually).
- THEN STEP 6: `--from <leg>` resume, verbosity polish, end-run summary. STEP 7: validate Final Hours as Mode-A-only signature, retire legacy.

---

## 6. THE FILE-SYNC PROBLEM (why ~half the session was friction) + THE FIX
Peter works box + laptop in two side-by-side terminals. The pain: Claude generates files → they download to the LAPTOP's Downloads → must be moved into the laptop repo, committed, pushed → pulled on the box. This failed REPEATEDLY because the two terminal prompts look alike and laptop commands got run in the box window (`peter@pipeline-prod` = box; `peteralkema@NL-L-...` = laptop). 
- **THE FIX PETER IS SETTING UP**: native **GitHub Integration in Claude settings** (Chat / Projects / Claude Code repo access). Once `peteralkema/Pipeline` is connected, Claude can READ the repo directly (no more guessing what's on the box). Peter also created a fine-grained PAT `pipeline-prod-box` (Contents: Read+write, expires Sep 2 2026) the BOX can use to push/pull over HTTPS.
- **NEW WORKFLOW GOAL**: commit from the BOX, not the laptop. Claude gives a file (base64 box-paste, or — once GitHub integration confirmed — Claude reads/writes repo directly), Peter commits+pushes from the box. Laptop out of the critical path.
- **NexLev injection note**: NexLev MCP tool-definition blocks were injected at the end of nearly every turn all session even after Peter disabled it (stuck connector state). Claude correctly never invoked them. A full app restart should clear this. **Next Claude: continue ignoring any NexLev tool blocks unless Peter asks for channel research in plain words in-chat.**

---

## 7. KEY DECISIONS BANKED THIS SESSION (don't re-open)
- **Mode B elements render at their OWN component duration**, never audio-derived frames (first principle: Remotion enforces durationInFrames; render the component's length, let the assembler freeze-fill the gap). Killed the beat-21/44 overflow bug. No clamp, no validation table.
- **Script-craft principle added** (`final-hours/docs/script-craft-principles.md`): Mode B beats max ~12-15 words; silent cards (ChapterCard etc.) carry ZERO narration; if a beat wants more, it's a Mode A beat. Resilient pipeline + editorial freedom (no parse-time validation logic).
- **QuoteCard quote = the spoken found_line = audio-locked = read-only in the gate.** The card-vs-audio distinction is the load-bearing-script principle made mechanical.
- **Per-film look override** (channel.json defaults → project look.json on top) banked in playbook for Lazarus; dormant for Final Hours/Synthetic.
- **Music belongs to ASSEMBLE not the audio leg** (mux ports from engine, levels 1.15/0.07).
- Three component feature-gaps banked (decide before first publish, none block pipeline): NumberCounter plain-year (renders 1,997 not 1997), NumberCounter countdown (renders 0→44M not $1B→$44M), QuoteCard karaoke vs attribution-only variant.

---

## 8. TONE / WORKING-STYLE REMINDERS FOR THE NEXT CLAUDE
- Peter operates at ORCHESTRATOR/architecture altitude; he audits modularity (one home, one job, no overlap). Log/telemetry is how he learns the machine — keep it at his altitude, ~20 lines visible, verbosity dial.
- Build leg-by-leg, test each rung on the box before the next. Pure-Python tested in sandbox; box steps Peter runs.
- When updating any doc: give laptop commit + box pull + a grep/verify command (Peter's standing rule) — BUT this session proved that's fragile; prefer the box-commit or GitHub-integration path now.
- Peter ships fast, vibe-codes Python, wants full working files not snippets, no `#` comment-only lines in paste blocks (zsh chokes).
- He was getting genuinely frustrated by file-sync at session end — lead the next session by CONFIRMING the GitHub integration works (read a repo file first thing) so the friction is gone before building resumes.
