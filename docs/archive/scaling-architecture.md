# Scaling Architecture — From Two Channels to Ten
*Last updated: 30 May 2026*

For both Final Hours and Success Coach. A working brief on what's already future-proofed in the multi-channel architecture, what becomes load-bearing at scale, and the honest economic and operational tradeoffs as the portfolio grows.

---

## What's already future-proofed

The architecture as it stands genuinely supports ten channels with no rewrites.

The pipeline lives in `shared/`, channel-agnostic, doing all the heavy lifting — script ingestion, canon substitution, image generation, animation, TTS, music, assembly, thumbnail generation, upload. Channels are defined by `channel.json` markers — voice, style, music, base canon. Rulebooks are layered: universal in shared, channel-specific overlaid on top. Beat-scripts carry video-specific canon merged with channel base canon at load time.

To add a tenth channel: create one folder, drop one `channel.json`, write the first beat-script, `cd` in, run pipeline. No code changes. No architectural decisions. Just a new folder.

The work done across the multi-channel migration of late May 2026 wasn't "make Success Coach work alongside Final Hours." It was "make N channels work indistinguishably from one channel." Future-you launching channel seven in 2027 follows literally the same recipe as Success Coach in 2026.

The Hetzner box (once provisioned) is the same. Whatever single VPS handles two channels in parallel handles ten. Render jobs aren't channel-aware at the orchestration layer — they're just "render this project folder." Disk usage scales linearly with active projects, not with channel count. A single VPS at the CPX31 tier (8GB RAM, ~€14/month) can comfortably handle five to ten channels in serial, with no upgrades needed until render frequency exceeds the CPU's ability to keep up.

---

## What needs work at scale — but isn't blocking now

Six honest concerns ordered by when they bite, not by severity.

### Reviewer interface needs channel awareness

When ten channels' worth of stills land on the VPS, the freelancer doing reviews needs to know which channel's review they're in. The `review_manifest.json` will need a `channel` field; the URL structure becomes `/review/<channel>/<project>/<batch>`. The review UI shows the channel's canon as a reference panel because canonical Sarah from Success Coach looks nothing like canonical Hartley from Final Hours. Small addition, not architectural — earned at channel three or four.

### Render orchestration becomes load-bearing

Two channels rendering serially is fine. Ten channels with shifting priorities and overlapping schedules needs a real queue. The right move is the "boring solution" — Python `subprocess` calling pipeline commands from a simple priority queue file (JSON list of jobs, picked off oldest-first or by explicit priority). Ships in a day. Scales to dozens of jobs per day without rewriting. The pipeline itself stays unaware of the queue; the queue is a wrapper.

A more sophisticated option later — Redis-backed RQ, or even Celery — earns its keep only if you're running multiple parallel workers, which only matters if a single VPS isn't keeping up. Not until ~20+ renders per week.

### Strategy docs need refactoring

At two channels, per-channel `strategy.md` files are coherent. At ten, you don't want ten strategy docs with overlapping principles. The clean shape is `shared/docs/principles.md` for what's universal (rulebook discipline, canon discipline, retention curve interpretation, the three-attempts rule, canonise-at-three) and channel docs that are *only* channel-specific (the wedge, the audience, the topic principles). Worth the refactor when launching channel four — premature now.

### Cross-channel state document

A `shared/docs/portfolio.md` listing all live channels with one-paragraph summaries each. New chats read it first to understand the full landscape. Small lift now (~30 minutes), scales naturally as channels are added. Worth doing in the next session — the architecture supports it cleanly and the document gets more valuable as it ages.

### YouTube API quotas

Default quota is 10,000 units/day per Google Cloud project. Uploads are 1,600 units each. That's ~6 uploads/day per GCP project. Two channels sharing one GCP project is fine; ten channels would hit quota limits trivially. The current `auth.py` + `upload.py` per-channel structure already supports separating Google Cloud projects per channel — each channel folder holds its own `client_secret.json` and `token.json`, so a dedicated GCP project per channel is just a credential swap, no code change. Bank this discipline now: when creating channel three's OAuth credentials, use a fresh Google Cloud project rather than reusing Final Hours'. The pattern compounds cleanly.

### Process knowledge updates

Memory updates and custom instructions become channel-N-aware. The current "Peter is building Final Hours and Success Coach" framing breaks down at four channels. The right shape is to keep a portfolio document as the master context, and have memory + custom instructions point to that file rather than enumerate channels inline.

---

## Why fal costs grow non-linearly with scale

This is the one place the architecture math gets genuinely interesting. The naive assumption is "ten channels × $25/video × four videos/month = $1,000/month" which scales linearly. The honest picture is more nuanced — and goes both directions.

### Two forces pushing costs *up* faster than linear

**Cluster discipline implies more videos per channel, not the same.** The strategy banked from Final Hours — topic clusters beat topic variety, ship 5-10 videos in the same niche before pivoting — means a successful channel actually produces *more* videos per month over time, not the same number. At channel one you might ship two per week to build out the cluster. At channel ten with five mature clusters per channel, you might be shipping seven per week from that channel alone. Cumulative volume grows as channels mature.

**Reshoot rates increase with channel novelty.** New visual eras (modern office, Tudor stone, Edwardian deck, ancient Roman) each require their own rulebook accumulation. Channel one's first three videos had high reshoot rates; the rulebook stabilises and reshoot rates drop. But each *new* channel resets that learning curve — channel six in a setting we've never produced (1970s Cold War interiors, Victorian London streets, Mughal architecture) starts with the universal rulebook but no channel-specific rules, and burns through 20-30 reshoots per video for the first three before stabilising. Each new channel has a $50-100 "tax" in extra reshoots before the rulebook moats up.

**Premium quality per video also raises costs.** Anne Boleyn used Flux Pro (more expensive than Seedream) because the modern-face-prior was unfightable on Seedream. As you produce more videos, you'll find new categories where the cheaper model fails and you need the premium model. Per-still cost creeps from $0.03 to $0.05 over time, applied across more videos = compound increase.

### Three forces pushing costs *down* faster than linear

**Failed-render auto-fallback prevents catastrophic spend.** The Kling content-policy-refusal auto-fallback we built means a single broken still doesn't burn $25 of subsequent animation. At ten-channel scale, with hundreds of videos rendering monthly, the savings from a robust fallback (rather than an exception that crashes the whole render and wastes the upstream work) is meaningful. Bank this: every layer of robustness in the pipeline pays for itself ten times more at scale than it does at one channel.

**Bulk pricing and committed-spend negotiation.** fal.ai's published pricing applies up to a soft threshold (~$500-1000/month). At ten-channel scale you're spending ~$1500-3000/month and you become someone fal's account team negotiates rates with. Historically these contracts get 15-30% off published rates for committed-spend agreements. Worth a calendar reminder to *negotiate fal pricing* once you're consistently spending >$500/month for three months.

**The rulebook compounds across channels at the universal level.** A modern-text-rendering rule banked from Success Coach prevents the same failure in every other channel that touches modern content. An anatomy rule banked from Final Hours prevents the same failure across all historical channels. The universal layer of the rulebook (currently ~21 rules) prevents specific spell-breaker categories *across every render that ever runs*. At ten channels with maybe 50 universal rules, each one of those is preventing maybe ten reshoots per video × maybe 50 videos per month × maybe ten months. The compound prevention is hard to count precisely but it's real and big.

**Re-render-only assembly is free.** The `--assemble-only` mode lets you re-stitch any past video from existing clips with zero new fal spend. At scale this matters: changing assembly logic, swapping music beds, redoing captions, all without re-paying for the expensive part. Once a video is rendered, its asset library is permanently available for $0/iteration.

### The honest economic shape

At one channel: ~$100/month in fal credits (4 videos × $25).
At two channels (current state): ~$200/month, scaling linearly.
At four channels: probably ~$500/month — slightly super-linear because of the new-visual-era tax and increased cluster cadence.
At ten channels: probably ~$1500-2500/month — bracket because the variance depends on whether you've negotiated committed-spend with fal, whether the universal rulebook has matured enough to drop reshoot rates, whether new channels are in already-mastered or fresh visual eras.

The honest break-even per video remains favourable. At ~$30/video all-in cost (fal + Inworld + Claude + everything), break-even is ~3,000-5,000 monetised views at history-RPM rates (~$5-8 CPM). Across ten channels that's the same break-even per video — the *channel selection* discipline matters more than infrastructure cost at scale.

**The thing that actually fails first at scale isn't fal cost — it's review bandwidth.** Stills review is currently bottlenecked by your time at one or two videos per week. At four channels with cluster discipline you're producing six to eight videos per week. Even with a freelancer doing $3/hour pattern-matching, review becomes the limiting factor before fal cost does. This is why the freelancer architecture work (and the Hetzner migration that enables it) is the highest-leverage next infrastructure investment.

---

## The build-for-two, design-for-ten, refactor-at-four principle

Worth banking as a permanent principle because it's been quietly proving itself across this whole project.

**Two channels forces real multi-tenancy thinking.** None of the "if/else final_hours" hacks that look fine at one channel and break at three. The work to make Success Coach a true peer of Final Hours (not a fork, not a special case) is what made the architecture genuinely N-channel-capable.

**Ten is the realistic 18-month horizon you want to be ready for.** Designing for ten means asking "what breaks when I 5x this" at every architectural decision. Most things that break at ten also break at five; designing for ten catches them earlier.

**Four is the magic refactoring number.** By channel four you've shipped enough videos that genuine patterns are visible — what's universal, what's channel-specific, what's per-video. Refactoring at one or two is premature (you don't know what's permanent yet). Refactoring at six or seven is late (you've accumulated technical debt across all of them). Four is the sweet spot.

**Translating this into a sequencing principle:** when you hit a "this would be better as N-channel-capable" thought, write it down rather than implement immediately. Implement when you're standing up channel three or four — when the second use case forces the abstraction to be real rather than guessed.

---

## What I'd build next, sequenced

The honest sequence I'd run if I were Peter, in priority order. This is a 6-month roadmap.

1. **Finish six_minutes and ship it.** No infrastructure work until video four is live across both channels.
2. **Bank the stills-review rubric** across Success Coach videos 2 and 3. Catch failure categories. Stabilise the taxonomy.
3. **Add `review_manifest.json` generation to the pipeline** (~30 lines in `cmd_stills`). Costs nothing if unused. Makes the pipeline reviewer-ready from now on.
4. **Migrate to Hetzner** (one Saturday, weeks 4-8 from now). Build the basic web review UI. See `hetzner-pre-read.md` for the migration brief.
5. **Hire the stills reviewer** (two weeks after migration so the interface is stable).
6. **Launch Final Hours channel three** — true crime or vanished places, whichever NexLev signal supports — and verify the architecture genuinely supports a third channel with zero refactoring required. This is the hidden test of all the work above.
7. **Refactor strategy docs and rulebook organisation at channel four**, per the principle above.

None of this is blocked by anything in this document. The architecture is ready; the work is operational and sequential.

---

## The moat as it stands

Worth stating plainly because it's been growing quietly across this whole project. The defensible assets are now:

The pipeline architecture itself — channel-agnostic, configurable, extensible. Most solo creators in this space couldn't add a second channel without doubling their codebase. Adding a tenth channel here is a half-hour task. That is genuinely rare.

The two-layer rulebook — 21 universal rules and growing, layered with channel-specific moats. Each rule is one category of failure permanently prevented. The accumulation rate is faster than competitors can catch up to from a standing start.

The canon mechanism — per-character, per-video, per-channel-base. Solves the consistency problem that breaks most AI-recreation channels by shot three. Bank-tested across three Final Hours videos and one Success Coach video.

The beat-grid architecture — script-as-shot-list-from-inception. Eliminates an entire class of narration/footage sync bugs that other AI-recreation channels are still solving manually.

The cost discipline — ~$25/video all-in vs competitors' $2,000-5,000. The 100x cost asymmetry means dud-tolerance is the strategy. Most channels can't survive five flops in a row; this one can survive forty.

The operating principles, written down — three attempts is the line, canonise at three, retention curves over view counts, cross-promote known fires, build-for-two-design-for-ten. Each one is a banked decision that compounds across every future render.

Channel one publishes. Channel two pre-launches. Channel ten is genuinely visible from here. That's the moat.
