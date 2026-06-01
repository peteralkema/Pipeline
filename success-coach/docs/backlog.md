# Success Coach — Backlog
*Last updated: 30 May 2026*

The forward queue. First three videos to ship, the 100-video backlog organised by topical cluster, deferred items specific to Success Coach, and working principles for when to revisit them.

Read alongside `strategy.md` for the why.

---

## Live state

| Item | Status | Notes |
|---|---|---|
| `six_minutes_beats.json` | Scripted, 84 beats, 1036 narration words | Pure-narrative format. Avatar beats replaced with cinematic imagery. Ready to run stills. |
| Coach Alex avatar | Parked indefinitely | Four attempts produced unusable catalogue-model faces. See "Avatar problem" below. |
| Success Coach channel auth | Needs setup | `auth.py` and `upload.py` exist as copies from Final Hours; OAuth handshake against the @successcoach100 channel still needs to run. One-time setup. |
| Success Coach rulebook | Empty | Will accrue organically from first video's reshoot lessons. |
| Voice selection | Placeholder Victor | Inworld voice selection deferred until after first stills are reviewed. |

---

## First three videos to ship (priority order)

These three share a "how corporate decisions actually get made" neighbourhood. The intent is to give the algorithm a clear signal of what the channel is about before publishing a fourth. Same cluster discipline banked from Final Hours.

### Video 1 — *The Six Minutes That Doubled Her Salary*

The salary negotiation that worked. Sarah, 32, walks into a meeting earning £58k and walks out earning £120k. The three moves she made — naming her specific number, holding the silence, refusing to respond immediately. 84-beat script complete. Pure narrative (no avatar). The first pressure-test of the architecture on modern content.

Expected new failures to bank: modern clothing rendering (buttons, lapels), readable text on screens or notebooks, glass meeting rooms reflecting confusingly, faces in close modern detail.

### Video 2 — *The Email That Got Him Fired*

The reply-all that ended a career. A senior manager writes a private complaint, hits reply-all by accident, and the rest of his organisation reads what he really thinks of the leadership. Cinematic recreation of the exact 30 seconds: the typing, the click, the silence, the calls that follow.

Production note: the email itself is never shown legibly on screen (image models can't render legible text reliably — banked rule). Frame the screen at an angle, in shadow, or out of focus. The viewer infers the content from narration.

### Video 3 — *How Hiring Decisions Are Actually Made*

What happens in the 15 minutes after a candidate leaves the interview room. The conversation between the panel. The two factors that decide most hires that nobody mentions to candidates. Composite character study — three interviewers, one candidate, one conversation.

Highest retention-anchor concept of the three: hidden-architecture content (showing what's normally invisible) tends to land hard. If any of the three breaks out, this is the most likely.

---

## The 100-video backlog

Ten clusters of ten. Cluster names are stable; specific videos within each cluster accrue as Peter writes them. The list below is scaffolding to think with, not commitments.

### Cluster 1 — Crossing from university to career
The transition moment. First job applications, first interviews, the gap between what universities teach and what employers actually want. The graduate's identity rupture.

Example videos: *The Question She Couldn't Answer in Her First Interview*, *The First Day She Realised Her Degree Wasn't Enough*, *The Job She Didn't Apply For (And Got)*.

### Cluster 2 — First job survival
The first 90 days. The mistakes that don't show up in the formal probation but determine whether you survive year one. Workplace norms nobody explains.

Example videos: *The Meeting Where She Said Too Much*, *The First Time He Was Asked to Lie*, *The Two Habits That Saved Her Probation*.

### Cluster 3 — Workplace politics and hidden power
How decisions actually get made. Who holds influence vs who holds titles. The conversations that happen in the corridor that shape everything.

Example videos: *The Email That Got Him Fired* (video 2), *The Coffee That Cost Her the Promotion*, *Who Really Decided Your Salary*.

### Cluster 4 — Money, salary, negotiation
The conversations about pay. What gets negotiated. What gets quietly decided. The numbers behind the polite small talk.

Example videos: *The Six Minutes That Doubled Her Salary* (video 1), *The Bonus Conversation He Got Wrong*, *Why Two People With The Same Job Earn £40k Different*.

### Cluster 5 — Managers and managing up
The skill nobody teaches. Reading your manager. Anticipating what they need before they ask. The promotion that comes from solving your manager's problems.

Example videos: *The Update She Sent That Got Her Promoted*, *The Meeting He Should Have Cancelled*, *What His Manager Actually Wanted To Hear*.

### Cluster 6 — Career inflection points
The decisions that compound. The job change. The first time leading. The moment you realise you've outgrown the role. When to stay vs when to leave.

Example videos: *The Promotion She Turned Down*, *The Year He Stopped Applying To Jobs*, *The Day She Stopped Being An Individual Contributor*.

### Cluster 7 — The hidden architecture
How things actually work. The processes nobody documents. The decisions made before the meeting. The performance review behind the performance review.

Example videos: *How Hiring Decisions Are Actually Made* (video 3), *The Performance Review You Don't See*, *Who Decides Who Gets Made Redundant*.

### Cluster 8 — Burnout and mental performance
The slow cost. The signal you're missing because you're tired. The moment of recognising you can't keep going. The recovery that doesn't look like recovery.

Example videos: *The Friday Night She Couldn't Stop Working*, *The Burnout He Didn't See Coming*, *The Year She Said No To Everything*.

### Cluster 9 — Masterclass moments
The single decision that defines someone's career. The hard conversation. The bet. The boundary they finally drew. The "I quit" that didn't actually happen.

Example videos: *The Three Sentences That Saved His Job*, *The Boundary She Drew With Her CEO*, *The Letter He Never Sent*.

### Cluster 10 — AI era careers
The genuinely new category. What changes. What doesn't. The jobs being created and destroyed. The skills that hold value when the tooling commoditises. Peter's own positioning fits this cluster — *AI Era Careers* by an AI-recreation channel is structurally on-brand.

Example videos: *The Job She Trained AI To Do (And Then Lost)*, *The Skill That Got More Valuable When AI Arrived*, *The Manager Who Hired An AI Instead*.

---

## Deferred items

### The avatar problem

Pure narrative is the format for now. The wrap-around format remains available as a future upgrade once on-camera Coach Alex generation works. Three known fix paths exist, none of which are blocking shipping the first batch of videos:

**Path one — Flux + IP-Adapter with Peter's own photo as conditioning.** Use a real photo of Peter as the structural anchor passed through fal's IP-Adapter API. The generated avatar would be visually similar to but distinct from Peter himself, locked across every shot. Highest-promise path; requires extending `generate_still` to accept image conditioning.

**Path two — External reference image as IP-Adapter anchor.** Source a stock photo or public-domain image of an ordinary kind-faced middle-aged man (not Peter, not a model) and use that as the anchor. Sidesteps the model-prior fight by giving Flux a concrete structural reference instead of a 700-word description.

**Path three — Midjourney-anchored reference.** Generate one perfect Coach Alex still in Midjourney (which has better aesthetic control than Seedream/Flux for this kind of character work) and bring it back into the pipeline as the IP-Adapter anchor. Higher friction (separate tool, separate session) but produces the strongest anchor when text-anchored generation has fully failed.

Revisit when there are 5-10 published Success Coach videos and audience signal suggests the wrap-around format would meaningfully improve performance.

### Voice selection

Currently set to "Victor" (Final Hours's voice) in `channel.json`. Worth auditioning Inworld voices for a warmer, more conversational coach register. "Ashley" used previously for lesson content is one candidate. Other Inworld voices worth testing have shifted since the original Success Coach Udemy content; check the current voice catalogue at https://studio.inworld.ai/ before committing.

Defer the audition until after the first stills review for video 1 — there's no urgency before then, and once the first video's narration script is locked, the voice test becomes concrete instead of speculative.

### Modern-content rulebook

Currently `success-coach/rulebook.json` is empty. It will accrue organically from video 1's reshoot lessons. Expected categories of rule (predicted, to be confirmed):

- Modern clothing rendering inconsistencies (asymmetric buttons, weird lapels, ill-fitting collars)
- Laptop and phone screens (always frame so the screen content is not legible)
- Glass meeting rooms (the model renders ghost reflections of nonexistent people)
- Modern faces (the AI-default-attractive register that hits Final Hours's wide character shots will hit modern characters too)
- Specific corporate brands and logos (renders as gibberish corporate symbols)

Don't pre-populate the rulebook with predicted rules — wait for actual spell-breakers caught in stills review. Predicted rules tend to over-constrain.

### Success Coach upload and auth scripts

Currently `auth.py` and `upload.py` are copies of the Final Hours versions, with channel-suffix references stripped. They need:

1. **OAuth handshake against the @successcoach100 Google account.** Run `python3 auth.py` from `success-coach/` once, which opens a browser, logs into peteralkema2@gmail.com, selects the Success Coach brand account, and writes `token.json`. One-time setup.
2. **Verify `client_secret.json` is the right one.** The Google Cloud project that issued the OAuth credentials needs to have access to the Success Coach channel. Might require creating a second Google Cloud project if quota limits become an issue (Peter's instinct on per-channel projects is correct — keeps quotas independent).

This is a 15-minute one-time setup task before the first publish. Not urgent until video 1 is rendered and ready to upload.

---

## Working principles

A few things specific to Success Coach worth banking as decisions made:

**Don't push every new Success Coach video to the 6k existing subscribers.** The notification feed itself is the first algorithmic test — subscribers who watch and retain signal the algorithm to expand reach. If the video clears that bar, the cross-promotion to Facebook and X earns its keep. If it doesn't clear, those audiences are spared a video that wasn't ready.

**Expect higher early-window views than Final Hours.** 6k subscribers vs Final Hours's much smaller base means the cold-start view counts won't be directly comparable. Pompeii at ~26 views in 12 hours was normal for a new channel; a Success Coach video at ~26 views in 12 hours would be an underperformance signal because the subscriber notification feed alone should deliver more than that.

**Topic-cluster discipline is more important here than on Final Hours.** Final Hours's audience came expecting historical recreation; the format itself is the channel identity. Success Coach's 6k subscribers came expecting career advice; the format change is real and viewers need to learn what to expect. Three videos in the same cluster compound that learning; three videos in three different clusters look like a channel having an identity crisis.

**The Final Hours rulebook is not a starting point for Success Coach.** All Hartley-specific, period-specific, and Edwardian-specific rules have been correctly migrated out of universal scope (post 30 May rulebook split). Success Coach starts with only the genuinely universal rules — anatomy, gravity, text-rendering, eyeline. Modern content will need its own rule accumulation from scratch.

**Sarah, Mark, and other recurring characters across multiple videos should have channel-level base canon if they recur.** If the salary cluster ends up using "Sarah, 32, charcoal blazer, cream blouse" across three videos, that canon should move from beat-script local to channel base_canon. Below three videos, beat-script local is fine. Same canonise-at-three discipline as Final Hours.
