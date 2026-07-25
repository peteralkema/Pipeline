# _PACKAGING-AUDIT.md

The fixed instrument for measuring the packaging layer across the portfolio. Runs on a
cadence, produces the same numbers every time, and writes one dated row per channel into
`audit_history.csv`. **The value is the time series, not any single pull.** A one-off
competitive read is a vibe; a fortnightly identical read is an instrument.

Supersedes ad-hoc competitor lookups. Doctrine moves still require the
two-independent-signals rule.

---

## 1. Cohort definition (lock once, never re-pick)

For each live channel, at launch, build an **age-matched control cohort**:

- `get_similar_channels(channelId, async=true, level=3)` -> poll status
- Keep channels whose `joinedDate` is within +/- 45 days of yours
- Keep similarity score >= 55%
- Drop channels with `daysSinceStart` > 400 (legacy channels are not your competition
  set; they won on a different YouTube)
- Target 6-12 channels. Freeze the list in `<channel>/cohort.json`.

**Do not re-pick the cohort each cycle.** Re-picking selects for whoever happens to be
winning today, which is survivorship bias and makes the time series meaningless. If a
cohort member dies, record the death — that is data. **And the cohort MUST contain
channels that failed with the same tactics** — the original winners-only version of this
table produced a false 100× packaging thesis that survived four sessions until Covenant
Lens falsified it.

Sacred Dawn frozen cohort as corrected 2026-07-25 (the rung ladder):

| rung | channel | joined | role |
|---|---|---|---|
| peer | Covenant Lens | ~2026-06-12 | age-matched control — did the hygiene, sits at our level |
| rung 1 | FeelAngels | 2026-04-18 | accumulation proof, zero hygiene |
| rung 1 | Bible Secrets: Hidden History | 2026-04-02 | volume-without-topic control |
| rung 2 | Sealed Word | ~2026-04-28 | grind route (143 vids, 8 subs/vid) |
| rung 2 | Bible Academia | ~2026-05-13 | breakout route (24 vids, 304 subs/vid) — primary model |
| ceiling | Discernment Made Clear | 2026-06-09 | 6-hits-in-40 lottery reference, never the target |
| ceiling | Forgotten Bible Stories | 2026-06-16 | decaying launch-spike cautionary |
| ceiling | The Enoch Codex | 2026-06-04 | one-breakout channel; universal-question-inside-lore proof |

Discernment Made Clear is the **primary control**: launched one day before Sacred Dawn,
identical video count. Age, cadence, volume and category all held constant, which
isolates the variable to packaging and topic selection. Treat its numbers as the
counterfactual for what your machine could have produced.

---

## 2. Metrics — always pulled via MCP, never pasted

Pasted tables get scrambled. This has already caused one wrong recommendation.

**Per cohort channel** (`get_channel_analytics`, `youtube_channel_outliers`):
`joinedDate`, `daysSinceStart`, `videoCount`, `subscriberCount`, `viewCount`,
`avgViews`, `keywords[]` populated y/n, per-video `lengthSeconds` and `title`.

**Per own video** (`get_my_top_videos`, `get_my_video_analytics`):
`views`, `averageViewDuration`, `lengthSeconds`, `subscribersGained`, `shares`.

Never trust `publishDate` from the suggested-video endpoint — it is imputed. Use
`joinedDate` from channel analytics.

---

## 3. The five indicators

### 3.1 Packaging Gap (the KPI)
`cohort_median_avgViews / your_avgViews`

Sacred Dawn, 2026-07-24: **112x** (15,339 / 137, vs primary control).
This is the single headline number. Track it fortnightly. Everything else explains it.

### 3.2 Retention-Views Correlation (the diagnostic)
Spearman rank correlation between per-video `views` and per-video
`retention = averageViewDuration / lengthSeconds`.

- **Positive** -> packaging is selecting correctly; your best content gets your most views.
  Problems here are content or distribution problems.
- **Negative** -> the title layer is actively promoting your weakest content and burying
  your strongest. This is a packaging emergency and it is invisible if you only look at views.

Sacred Dawn, 2026-07-24: **negative.** Best-retaining video (Cain's Wife, 36.5%) has the
second-lowest view count. Worst-retaining videos sit mid-table. This finding alone
justifies freezing production for a re-title wave.

### 3.3 Format Variance
`stdev(lengthSeconds) / mean(lengthSeconds)` across the last 20 uploads.

Winners run < 0.15 — Forgotten Bible Stories is effectively 0.00 (every video 1:10-1:16),
Enoch Codex ~0.08, Discernment ~0.04. Sacred Dawn is ~0.75 (9:21 to 1:16:10).

YouTube cannot learn what a channel is when each upload presents as a different product.
Enforce as a duration band in `channel.json`; gate at script-validation time, not render time.

### 3.4 Second-Person Rate
`% of last 20 titles containing you / your / a direct interrogative`

Winners: 60-80%. Sacred Dawn before this wave: 5%. Target after: >= 70%.

### 3.5 Tag Coverage
`keywords[]` populated y/n + term count. Sacred Dawn: **empty**. All three winners loaded,
with search-intent long-tails ("why was book of enoch removed from bible") plus adjacency
bait ("joe rogan bible", "graham hancock"). Free, unclaimed, and wired straight into the
channel-agnostic upload step.

---

## 4. Decision rules (so it is not vibes)

| Condition | Action |
|---|---|
| Packaging Gap > 10x | Freeze new production. Run a re-title wave before spending another cent on fal. |
| Retention-views correlation negative | The problem is the title layer, not the script. Do not rewrite scripts. |
| Format variance > 0.25 | Lock the duration band in `channel.json` before the next batch stages. |
| Second-person rate < 30% | Re-title wave, ranked by retention descending. |
| Video retention < 20% | **Do not re-title it.** Re-cut the cold open or retire it. A better title on weak retention just burns impressions faster and teaches the algorithm you do not hold. |
| Tag coverage empty | Blocking defect on the upload step. |

Read windows: **48h** for CTR and early retention, **day 14 and day 21** for traffic-source
shift. Never call a re-title at 48h on traffic source — impressions have to accumulate first.

---

## 5. Cadence

- **Fortnightly**, per live channel — the five indicators, appended to `audit_history.csv`.
- **Monthly**, portfolio roll-up — Packaging Gap across all channels, ranked. The worst
  gap gets the next wave of attention.
- **At launch**, per new channel — lock the cohort.

---

## 6. Build note

`packaging_audit.py` — reads `cohort.json`, hits NexLev MCP + YouTube Analytics, computes
the five indicators, appends a dated row to `audit_history.csv`, prints any triggered
decision rules. Read-only, no spend, safe to run any time. Should sit alongside
`dump_channel.py` and follow the same read-only mirror pattern.

Until it exists, run the pulls by hand on the same fortnightly cadence and record the same
five numbers. The consistency matters more than the automation.

---

## 7. Banked principles from the 2026-07-24 audit

- **Views and retention can be anti-correlated.** When they are, the title layer is
  broken. This is undetectable from a views-only view of the channel and is the most
  valuable thing the instrument produces.
- **Throughput is not scarce in a served lane.** Every winner in the Sacred Dawn cohort is
  batch-dropping AI video on the same dates. Nineteen channels are literally named
  "Forgotten Bible Stories." The machine is table stakes; the packaging layer is the moat.
  Correct the flywheel thesis accordingly: the machine's real edge is that it can run
  packaging experiments at a volume a hand-editor cannot, and that edge is unused until
  packaging is measured.
- **NexLev's similar-channels table lags roughly a week on fast movers** and its
  "Avg Monthly Uploads" is a batch-drop artifact, not a cadence. Never read cadence off it.
- **A channel description can encode an anti-positioning.** Sacred Dawn's "No clickbait,
  no conspiracy" is an aesthetic refusal of the exact mechanism the lane rewards. Audit
  the description as part of packaging, not branding.
- **Tags reveal strategy that titles hide.** Forgotten Bible Stories reads as a generic
  biblical-cinematic channel from its titles; its tags ("ethiopian bible", "black
  israelites") show it is serving a specific underserved identity audience. Always pull
  `youtube_channel_about` on a cohort member before concluding what lane it is in.
- **Do not promise no answer.** Sacred Dawn's highest-retaining video was titled "The
  Question Genesis Won't Answer." The title told the viewer there was no payoff.
