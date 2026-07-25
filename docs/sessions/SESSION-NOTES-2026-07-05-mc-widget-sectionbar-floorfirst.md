# SESSION NOTES — 05 July 2026 — MC v3.7–v3.8, FLOOR-FIRST scoped, docs reconciled
## Spend widget · section bar · the floor-first inversion · frame-chaining · full doc pass

_Continuation of the 04 Jul craft-vs-cash arc (`SESSION-NOTES-2026-07-04-mc-craft-cash-surface.md`). Shorter build session, one large design idea (floor-first), and a full documentation reconcile. Doctrine graduations marked → ._

---

## 1. Where the session opened

MC at v3.6, both §7 cost-controls shipped, the ship panel already CONTENT | PACKAGING. The tech-stack question from Peter produced a clean one-paragraph inventory of the whole machine (markdown → fal Flux-pro/NB2 → fal Kling / ffmpeg-zoompan / inherit → Inworld/ElevenLabs → Whisper → ffmpeg/Remotion → PIL packaging → YouTube API, orchestrated by Mission Control, researched via NexLev MCP, on Hetzner with GitHub as the only transport). Worth keeping as the elevator description of the pipeline.

## 2. v3.7 — the persistent ESTIMATED SPEND widget

Peter's ask: a fixed little window, always visible while scrolling, showing total estimated spend of the currently-specified animation (KB = zero, Kling counted). Cheap to build **because of** everything already there — the page paints each beat's mode from the policy file (`dataset.kbon`/`inhon`), the GET already returns `kling_count`, and the chain lines already repaint on every toggle. So the widget just counts modes exactly as the tiered render routes them (**Kling only if `beat < N AND not kb AND not inherit`**) and rides the existing repaint hook.

Bonus it computes free: how many Kling-mode beats already have clips on disk → shows **remaining** spend, not just total (the number that matters mid-review). Fixed bottom-left, gold-bordered, opposite the ⇧ Top button. Functionally verified against kb-toggle4's real state (3 Kling $1.05 / 1 KB / 6 inherit, all rendered → remaining $0.00) and the front-N free floor (beats beyond N count as free even untoggled — routing-exact, not a naive count).

→ **The whole craft-vs-cash loop is now closed: every per-beat decision prices itself in real time, in view, wherever you are in the scroll.** On an Elijah-scale project this is what keeps a review session honest.

## 3. The scale question → v3.8 the section bar

Peter's scale question: a 60-min project = how many beats? The answer is register-dependent and an order of magnitude apart — **classic feature format ~11–12s/beat → ~300 beats for 60 min; all-trim (Synthetic) ~2.3s/beat → ~1,550 beats.** Elijah bridge (25–35 min all-trim) ≈ 650–920.

Which surfaced the real problem: **the storyboard doesn't survive 1,000+ rows** — every clip cell is an autoplaying looping video; a few hundred kills the browser. The fix is Peter's own instinct (horizontal part-buttons to navigate) built as **pagination disguised as navigation**: a sticky section bar, one button per `stage` (the field already on every beat header — `## COLD OPEN`/`## PART` markers), clicking renders ONLY that section, so only the visible section's videos mount.

**v3.8 shipped:** sticky per-stage buttons + ALL; ALL default ≤200 beats (small projects unchanged), first-section default above (never mount 1,500 videos); empty-stage beats fold into a "—" button so nothing is ever hidden; active button in the green mode-language; re-render preserves the chosen section. Cost widget grew a "(section) / project total" split so both numbers stay visible under filtering. Functionally verified: grouping order, default logic, fold, filter counts.

→ **This is the Elijah-scale prerequisite** — banked alongside per-channel reference-lock and the fal semaphore. It ships BEFORE floor-first because floor-first's section-by-section workflow needs it underneath.

## 4. FLOOR-FIRST — the session's best design idea (scoped, not built)

Peter's framing, verbatim in spirit: when stills come back, immediately auto-KB every beat on the right → all KB buttons green, cost zero → **assemble straight away without clicking a single button**. Then go through the parts button-by-button applying craft; if tired half-way, the rest is already KB. Seeing KB already done is *encouraging* — the minimum work is done, any time/cash added just boosts from that floor.

Its proper name is **floor-first**, and it's the strongest idea of the whole arc because it inverts the review psychology and unifies the economics: the $3-KB video and the $17-cinematic video become **the same project at different craft depths**, and a beat that always has a clip can never black-frame or block assemble (an entire failure class gone). Everything you do is an *upgrade from a shipped floor*, not a prerequisite for shipping.

**Two design decisions with teeth (settled before any patch):**
- **The skip-existing trap.** `cmd_finish` skips beats whose clip exists — so once the floor fills every slot, batch animate skips everything including upgraded beats. Fix: upgrading a beat's mode must **delete its floor clip** (free, regenerable in seconds). Direction matters — **KB→Kling deletes** (discards a free artifact); **Kling→KB never deletes** (never silently discard paid clips). The per-beat Render/preset path already overwrites (works today, confirmed from the `_handle_animate` read — it does NOT check clip-exists); only the batch `finish` path needs delete-on-upgrade.
- **Kling goes additive.** With an all-KB floor, front-N `kling_count` is meaningless → invert the model: default mode = KB, `render_policy.json` grows `kling_override:[beats]` alongside `inherit_prev`. **The presets become the writers** — clicking Dynamic/Slow-crane ADDS the beat to the Kling list (and deletes the floor clip). The cost widget then opens at **$0** and every preset click ticks it up — spend becomes something you visibly ADD, per beat, per section. Routing stays backward-compatible (`kling if in kling_override OR (bi < N and not overridden)`); floor-first projects run N=0.

**Build shape (next session):** engine `--kb-floor` pass (duration-exact KB for every clipless beat — `durations.json` exists pre-stills, so free and fast, ~minutes of small ffmpeg encodes) + `kling_override` routing; MC "Floor all (free)" button first (explicit, at the stills gate and project panel), automation after it's proven; preset→kling_override wiring with clip deletion; paint/widget updates. The section bar (v3.8) is already its prerequisite.

→ **canonical §5.12 carries the floor-first scope.**

## 5. Frame-chaining (discussed, not built — the minutes-long-scene question)

Peter noticed competitors running people walking/talking for minutes at a time. **The technique is frame-chaining:** the model still only makes 5–10s atoms — nobody generates minutes in one call — but you feed clip A's last frame as clip B's start image with a continuing motion prompt (Kling supports this natively — image-to-video first-frame conditioning, an explicit extend feature, first+last-frame control; Runway/Luma/Veo have equivalents). 5–6 links = 30–60s continuous. **The tell is drift** — faces and costumes slowly mutate across the chain, often masked with slight slow-motion. Two other disguises: same-environment atoms cut under continuous narration (a budget version of which inherit already produces), and native-speech tools (Veo 3) or lip-sync passes (Kling lip-sync, Runway Act-One, Hedra) for sustained dialogue. Cost is unremarkable — a 60s chained scene ≈ 12 atoms ≈ $4.

**The pipeline read:** it would be a **fourth per-beat mode** — "Extend previous ($0.35)" — beside Inherit, sharing the chain machinery but making a paid call from A's last frame instead of a free seek into A's tail. But it's a **doctrine question, not a capability one:** Synthetic's all-trim register is deliberately the opposite bet (2.3s cuts, high tempo), and Gettysburg's early AVD says that bet is live. Candidate only for Elijah emotional-peak flagship spend (the fire falling, the stillness after) — and evidence-first: run a competitor's long-scene through the NexLev watch-tool for a seam teardown before designing anything.

## 6. The documentation reconcile

Confirmed **STARTUP_PACK.md is dead** — dated Jun 5, unused, never in the actual load ritual, and the source of the weeks-stale auto-profile that keeps pasting in (5 channels, "Synthetic launching," pre-v2.0 priorities). De-referenced everywhere; the real load set is **canonical + worklog + `_Synthetic2.md`.**

**Canonical (`.pre_0702`, a month stale) fully updated to v3.8 reality:**
- §5.1 MC bumped to v3.8 + the RESTART LAW (MC imports engine code in-process → restart after every engine pull, never mid-render).
- New **§5.12** — the whole v1.9→v3.8 craft-vs-cash arc (every shipped control + the KB engine root-cause fix + the floor-first scope).
- Roster rebuilt: 11+ channels, correct statuses (Synthetic SHIPPED, Q-Qrew Ep1–5, Cathedral/Woodworking added, Lazarus rendered-pending, Scripture as the Elijah target, ElevenLabs Brian for Synthetic).
- Four new doctrine blocks in §7: **patch-craft discipline** (py_compile proves syntax never names/JS → verify = compile+load+click; handler-imports-in-the-handler; no-apostrophes-across-the-Python→JS-boundary; version-stamp = deploy check; re-download-after-amend; policy-file-is-truth); **channel-fixes-live-in-channel-config** (the QQrew hardcode autopsy, §2B second head); **the fal silent-substitute family** (+= baked-in letterbox, verify-at-the-artifact); **sources-persist-artifacts-derive**.
- §5.2 tiered-render + §5.6 artifact paths updated; §10 current state rewritten for 05 Jul.

**Worklog:** header bumped to v3.8, STARTUP_PACK marked dead, new RECORD entry for v3.7/v3.8 + floor-first scope + frame-chaining, Last-updated line refreshed.

## 7. Outstanding (carried, in order)

1. **48h READ (evening 5 Jul)** — Gettysburg film CTR/AVD/Browse% + retention curve + Shorts distribution. Unchanged #1.
2. **Inherit ARTIFACT proof** — still the one shipped control unproven at the assembled cut (`rm` an inherited clip → `--animate-only` → Re-assemble → eyeball the continuous move). Plus the letterbox retro-fix loop.
3. **FLOOR-FIRST build** (§4) — the section bar is in place; this is the next major MC+engine build.
4. **Doctrine graduation into `_Synthetic2.md`** — §5f parser marker whitelist, §7 shipped-toggles + the three-tier motion rule ("animate the galloping horse, never the wheat field"; "you can only inherit from a horse"). (The canonical half is now done.)
5. **Biblical pivot prerequisites** — per-channel reference-lock + parallel-fal semaphore → Elijah blockbuster.

Daemonize-runs (restart survives in-flight renders) remains open and matters more with every MC iteration.
