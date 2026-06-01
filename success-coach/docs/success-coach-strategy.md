# Success Coach — Strategy
*Last updated: 30 May 2026*

---

## Who and where

**Peter Alkema** — same operator as Final Hours, see `final-hours/docs/strategy.md` for full context. Success Coach pre-dates Final Hours by six years; it was Peter's original creator presence (Student Success Coach, then broader professional development) built on Udemy courses + slides-and-stock-footage YouTube videos. The new Final Hours pipeline is being applied to relaunch Success Coach as a second channel running cinematic narrative recreation instead of the old slide-deck format.

---

## The channel

**Name:** Success Coach
**Handle:** @successcoach100 (separate Brand Account)
**Subscribers:** ~6,000 (built over 6 years of student-success content)
**State as of 30 May 2026:** Dormant on the old format. Pipeline ready for the new format. First video scripted (`six_minutes_beats.json` — *The Six Minutes That Doubled Her Salary*). No new videos published yet under the new format.

The 6k subscriber base is a real asset — far more than Final Hours has — but it's a *student-success and career advice* audience accustomed to talking-head/slides/screen-recording content. The format change is genuine; viewers who recognise Peter will see a completely different production register from what they subscribed to.

---

## The pivot

The previous Success Coach format (slide decks, recorded narration, stock footage) had hit a creative and economic ceiling. Generic career advice content is a saturated category; the production-cost-per-video was reasonable but the *differentiation* was zero. With six years of identical-shaped content the channel had trained YouTube to expect a particular performance profile, and the algorithm settled the channel into a low-distribution equilibrium.

The decision: take the Final Hours pipeline — which produces cinematic photoreal narrative recreations for ~$25 per video — and point it at professional development topics. The wedge: **nobody in the career-advice space is doing cinematic narrative recreation.** Career content on YouTube is overwhelmingly talking-head essay (Ali Abdaal register), animated slide deck (LinkedIn-influencer register), or screen-recording walkthrough. Cinematic recreation of *one human in one career moment* is a genuinely empty lane.

---

## The fusion thesis

Final Hours works because it takes one human inside a catastrophe and stays with their decision-making in slow time. Applied to professional development, the analog is **one human inside a career moment** — the email she rewrote three times, the six minutes in the meeting that decided her bonus, the year he built something at 5am before work.

Career advice is universally abstracted on YouTube ("how to negotiate salary"). The format-novelty is to make it *specific* — name a person (real or composite), put them in a real room, let the camera stay with them through the decision. The lesson is delivered through what they did, not as bullet points. That's the wedge.

The same three-layer moat applies (rulebook + canon + beat-grid). The first Success Coach video, *The Six Minutes That Doubled Her Salary*, will pressure-test the architecture against modern visual settings — modern offices, business attire, glass meeting rooms, laptop screens. Expect to bank a new wave of channel-specific rules from the first video. That's not a setback; it's the moat widening into a second visual era.

---

## Format decisions (locked)

### Pure-narrative first, wrap-around later

Two ways to apply the Final Hours format to career content were considered: pure narrative (no on-camera Peter, all cinematic), and wrap-around (Peter's avatar opens and closes, recreation in the middle). The wrap-around was the original preference because it leverages the existing 6k subscribers' recognition of Peter as the trusted coach.

The avatar generation attempt on 29-30 May produced unusable results — multiple attempts (Seedream re-anchored, anti-arrogance prompting, Flux Pro swap) all returned the same "polished catalogue-male" register that didn't match Peter's actual likeness or convey the warmth needed. The conclusion: **AI avatar generation in May 2026 is a six-month problem, not a tonight problem.** Three known paths forward exist for when this gets revisited (Flux+IP-Adapter with Peter's photo as conditioning, external reference image as anchor, Midjourney-anchored reference), but none are blocking for shipping Success Coach.

Decision: **ship pure-narrative.** Peter's face appears on the *thumbnail only* — using a real cropped photo of himself, segmented via rembg the same way Final Hours uses cinematic stills on thumbnails. Existing subscribers see his face on the thumbnail and click; the video itself is narrative-only with Inworld narration. This unblocks Success Coach immediately; the wrap-around can be added later when the avatar question is genuinely solved.

### Inherited from Final Hours, unchanged

- Beat-grid script architecture (84 beats × ~13 words × ~5s clip = ~7-minute video)
- Canon mechanism (`{tag}` substitution for recurring characters and settings)
- Even-spacing assembly (`z = narration / clip_count`)
- Auto-fallback on Kling content-policy refusals
- Programmatic thumbnail generation via rembg + Pillow
- Scheduled publishing via `--schedule-cet-1am`

### Channel-specific (`success-coach/channel.json`)

- **Voice:** placeholder set to Victor (Final Hours's voice) for now. Worth auditioning Inworld voices for a warmer, more conversational coach register before shipping. "Ashley" used previously for lesson content is a candidate. Defer voice selection until after first stills review.
- **Style suffix:** "cinematic photoreal modern documentary look, contemporary 2026 setting, soft natural directional light, shallow depth of field, gentle film grain, slightly desaturated muted palette, 35mm cinematic feel, calm and observational" — distinct from Final Hours's painterly golden-hour register.
- **Music prompt:** "Calm reflective acoustic underscore... soft warm piano, subtle string pads, restrained and hopeful but not saccharine" — distinct from Final Hours's mournful drone bed.
- **Base canon:** `coach_avatar` and `coach_office` defined for future wrap-around use, but currently unreferenced in `six_minutes_beats.json` because that video is pure-narrative.

---

## Inherited audience mechanics

Three owned audiences predate this relaunch and matter for distribution:

**The 6k Success Coach YouTube subscribers themselves.** Notification-eligible, will appear in their subscription feeds. First-batch seed pool for every Success Coach video. Bigger than Final Hours's entire subscriber count; this is the real algorithmic asset.

**The 5k Facebook "Student Success Coach" community.** Adjacent-but-distinct audience; came for student/career advice, would respond well to dignity-and-decisiveness framing. The Hartley video might actually be the right cross-post for this community even though it's a Final Hours video — the dignity-under-pressure theme is exactly what the community engages with.

**The X "professional insights" following.** Higher-quality signal seed pool; followers came for Peter's taste and judgment, so retention on a Success Coach video should be above average.

The cross-promotion discipline from Final Hours applies: let YouTube cold-test for 48 hours first, then amplify videos the algorithm has already chosen to expand. Don't push every Success Coach video to the same audience or fatigue sets in.

---

## Topic principle

The 100-video backlog (see `backlog.md`) is organised into 10 clusters of 10 videos, each cluster being a coherent topical neighbourhood. The first three videos to ship should come from **one cluster** to give the algorithm a clear signal of what the channel is about. Cluster discipline > topic variety, same lesson banked from Final Hours.

The strongest opening cluster, given the cinematic-recreation novelty and existing audience: **money, salary, negotiation**. Salary-curiosity is universal high-CTR. The "specific number that doubled" emotional hook is the strongest narrative pull in the backlog. The hidden-architecture-of-hiring frame is the highest retention anchor for follow-up videos.

Topics avoided deliberately, at least at first: anything that requires showing readable text on screen (resume contents, email bodies, document text — image models can't render legible text reliably). Anything that needs many different specific named brands or logos (renders as gibberish corporate-looking logos). Anything that requires intimate physical action involving hands manipulating objects (typing, writing, signing — hands warp in motion).

Topics that are easy production wins: conversations between two people in a meeting room, individual reflection moments, walking-through-office establishing shots, atmospheric "evening at home" framings.

---

## Honest unknowns

The Final Hours moat — rulebook + canon + beat-grid — is proven on three videos in the historical setting. None of it has been pressure-tested on modern content. **Expect the first Success Coach video to surface a new class of failure modes.** Specific things likely to break or need new rules: modern clothing renders inconsistently (buttons in wrong places, asymmetric lapels), laptop screens showing readable text (the engraving problem all over again), faces in close modern detail (Edwardian faces had more visual variety than AI-default model-attractive), glass meeting rooms reflecting confusingly.

The avatar question is genuinely unsolved. The thumbnail-uses-Peter's-real-photo workaround works for video one but doesn't scale to actual on-camera Peter in the videos themselves. Some future videos in the 100-video backlog (the "advice-heavy" ones we'd originally planned as wrap-around format) won't work as well in pure-narrative mode and may need to be deferred until the avatar problem is solved.

**Audience reception is also unproven.** The 6k existing subscribers subscribed for slide-deck student-success content. Whether they engage with cinematic narrative recreation of corporate scenes is a real open question. Some will love it (the format-novelty hits); some will be confused (this isn't what they signed up for); some will unsubscribe. That's expected and probably healthy.

The 6-month thesis: ship 10-20 videos in the new format, observe which clusters resonate with which audiences, double down on what works, accept that some videos will earn nothing. Same dud-tolerance philosophy as Final Hours.

---

## Key files

```
success-coach/
├── channel.json                    — channel config (voice, style, music, base canon)
├── rulebook.json                   — channel-specific rules (currently empty; will accrue)
├── auth.py / upload.py             — separate from Final Hours, separate YouTube credentials
├── client_secret.json / token.json
├── projects/
│   ├── coach_alex_reference/       — abandoned avatar generation attempt
│   └── six_minutes/                — first Success Coach video, scripted
├── beat-scripts/
│   ├── coach_alex_reference.json   — reference-generation file (avatar parked)
│   └── six_minutes_beats.json      — first video, 84-beat script
├── assets/                         — (empty, will accumulate)
└── docs/
    ├── strategy.md                 — this file
    └── backlog.md                  — what's next + 100-video backlog
```

Multi-channel architecture details (channel.json marker, walked-up resolution, two-layer rulebook, base-canon merge) are documented in `final-hours/docs/strategy.md` — same architecture, same conventions. To work on Success Coach: `cd success-coach/`, the pipeline picks up the channel context automatically from the marker file.
