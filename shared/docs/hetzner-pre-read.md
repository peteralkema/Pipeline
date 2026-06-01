# Hetzner — Pre-Read
*For Peter, before deciding on cloud migration*

A working brief covering what Hetzner is, what to buy, what migration involves, and the honest tradeoffs against the laptop setup that already works. Read this before committing real money.

---

## What Hetzner is, exactly

Hetzner is a German hosting company. Two relevant product lines:

**Hetzner Cloud** — virtual machines (VPS) starting at ~€4-6/month for a basic instance, ~€10-20/month for something with enough RAM and CPU to run the pipeline comfortably. Spins up in 60 seconds, billed by the hour. This is what we want.

**Hetzner Dedicated** — physical servers starting at ~€40-80/month, used by people who need 64GB+ RAM or specific hardware. Overkill for what the pipeline needs.

We want Hetzner Cloud. The right starting tier is roughly **CPX21** (3 vCPU, 4GB RAM, 80GB disk, ~€8/month) or **CPX31** (4 vCPU, 8GB RAM, 160GB disk, ~€14/month). The 8GB tier is the safer call — moviepy is mildly RAM-hungry, and headroom prevents OOM crashes mid-render.

No GPU needed. The expensive AI work (Flux image generation, Kling animation) runs on fal.ai's infrastructure, not yours. The VPS just orchestrates: makes API calls, downloads results, stitches with ffmpeg/moviepy. A modest CPU and decent network connection are all it needs.

Region matters slightly. Hetzner has datacentres in Falkenstein/Nuremberg (Germany), Helsinki (Finland), Hillsboro (Oregon US), Ashburn (Virginia US), and Singapore. **Pick Germany or Finland** — closest to Kraków, low latency on file uploads back to your laptop and to fal.ai's EU endpoints.

---

## Why migrate at all

The honest reasons, in order of weight:

**The laptop is your ABB work machine.** Every overnight render is a render that can't happen when you need the laptop for actual work. Anne Boleyn rendered overnight at Salta — that's hours where the laptop was tied up. As you ship more videos, this constraint scales badly.

**Persistent reviewable URLs.** This is the new reason that's emerging from the freelancer-review architecture conversation. To share stills with a freelancer via a web interface, the stills need to live somewhere with a public (or auth-gated) HTTPS URL. A laptop on Google Drive can't do that natively. A VPS can host a tiny review page over HTTPS in a way that's stable, shareable, and revocable.

**Unattended cron-scheduled renders.** Once you trust the pipeline to run without human eyeballs, you can schedule a render to start at 2am, finish by 4am, and have stills waiting for review when you wake up. On the laptop this works *if you remember to leave it open and plugged in*. On the VPS it works because nobody closed the lid.

**Geographic untethering.** Travel, holiday, week off. The VPS doesn't care.

**Pipeline survives laptop disasters.** Spilled coffee, stolen bag, OS reinstall — the VPS is unaffected. The laptop becomes just a thin client into the real production environment.

The reasons *not* to migrate yet:

**The laptop setup currently works.** Three videos shipped. Don't migrate to fix a problem that doesn't exist *yet*.

**Hetzner adds a real cost line** (~€100-170/year). Modest, but real, and ongoing.

**It's another thing to maintain.** SSH, security updates, monitoring disk usage, debugging at a distance. Not hard but real overhead.

**The migration itself takes a day.** Not catastrophic but it's a day of infrastructure work instead of video work.

---

## The trigger moments

Migrate when *any* of the following becomes true:

The laptop is genuinely blocking a render you want to run. Not "I had to plan around it" but "I needed it for work and the render didn't happen."

You're hiring the freelancer for stills review. The web interface needs persistent hosting. (This is your stated near-term direction.)

You're shipping more than two videos per week. The unattended-overnight pattern becomes load-bearing.

You start an extended trip or absence. The laptop dependency becomes real.

None of those are true today. Two of them are visibly approaching. The next 4-8 weeks is the window where the trigger likely fires.

---

## What lives on the VPS, what stays on the laptop

This is the architectural question worth deciding now even before the migration.

**On the VPS — the production runtime:**

The pipeline code (`shared/`, both channel folders).
The `.env` file (with secrets — Hetzner instances should be locked down).
The fal/Inworld/Claude/YouTube credentials.
The active project folders during render (stills, clips, voiceovers, final videos).
The rulebook and channel.json configs.
A small HTTPS server (nginx + a static review page generator) for freelancer review.

**On the laptop — your control surface:**

A clone of the git repository for code edits (you'd write Python locally, push to VPS).
Final video downloads for visual quality control before publish.
The "human in the loop" — script writing, beat-script authoring, final review.

The Google Drive folder you're using now becomes optional. You can keep it as a backup mirror, or drop it once the VPS is the source of truth. My steer is **keep Drive as a backup for a few months** while the VPS workflow proves itself, then drop it once you trust the cloud setup.

---

## File transfer model

Three workable options:

**One — git for code, scp/rsync for files.** Code lives in a git repo (GitHub private repo, free). You push code changes from laptop, pull on VPS. Project assets (stills, videos) move via `scp` or `rsync` over SSH. Lowest friction, most flexible, lots of documentation. My recommendation for the start.

**Two — Hetzner Volume Storage attached to the VPS, mounted as a shared filesystem.** Slightly more complex but cleaner separation between code and data. Worth it if you ever scale to multiple VPS instances or want to detach and re-attach storage.

**Three — Syncthing or rclone for two-way sync** with the existing Google Drive folder. Keeps the Drive workflow alive on top of the VPS. Possibly over-engineered for the gain.

Start with option one. Move to option two if storage becomes meaningful.

---

## What the migration day actually looks like

Roughly 6-8 hours of focused work, doable in one Saturday:

**Step 1 — provision and harden the VPS** (45 min). Sign up at hetzner.com/cloud, create a CPX31 instance in Falkenstein with Ubuntu 24.04. SSH in. Update packages. Create a non-root user. Set up SSH key auth, disable password login. Install ufw and configure a basic firewall (SSH + HTTPS only). Install fail2ban. This is standard Linux server hygiene and there are well-trodden tutorials.

**Step 2 — install runtime** (30 min). Python 3.12, ffmpeg, build essentials. Create a venv mirroring your current `~/venvs/success-coach/`. Install the pipeline's pip dependencies from `requirements.txt`. Install `rembg[cpu]` so thumbnails work.

**Step 3 — move the code** (30 min). Create a private GitHub repo with the contents of `03. Pipeline/`. Clone it on the VPS. Copy the `.env` file across via scp (it shouldn't be in git). Verify the rulebook --view command works in both channels.

**Step 4 — first render test** (1-2 hours). Run a known-working project (Hartley, with all its existing files) through `finish --assemble-only` to verify everything stitches correctly. Then try a fresh 4-shot test render end-to-end to confirm fal API access, Inworld TTS, the works. Solve any issues that surface.

**Step 5 — review interface** (2-3 hours). Install nginx, configure it for HTTPS via Let's Encrypt (free, auto-renewing). Write a small Python script that generates a static review HTML page from a project's storyboard.json + stills folder. Mount it at a subdomain or path. Add HTTP basic auth so it's not publicly browseable. Test that you can open the URL from your phone and see Hartley's stills.

**Step 6 — first real render on the VPS** (overnight). Pick a video you're about to ship anyway. Run it overnight. Verify it produces the same output the laptop would have.

By Sunday evening: VPS is live, first cloud render complete, review URL working. The remaining work after that is operational refinement, not infrastructure.

---

## Security — minimum bar

The VPS will hold your fal key, Inworld key, Anthropic key, and YouTube OAuth tokens. Treat it accordingly:

SSH key-only auth. No password login.
Non-root user for daily work.
ufw firewall: only SSH (port 22) and HTTPS (443) open to the world.
fail2ban to block brute-force attempts.
HTTP basic auth on the review subdomain (or IP allowlist if the freelancer is at a fixed address).
Backup the `.env` file separately (encrypted, e.g. in 1Password). If the VPS dies, you want the keys recoverable.
Regular `apt update && apt upgrade` — set a calendar reminder for monthly.

This is the minimum bar for a personal VPS with credentials. Not paranoid, not lax.

---

## Honest cost-benefit at a year

**Annual cost of the laptop status quo:** ~€0 in direct hosting. Real cost is in lost render slots when the laptop's needed for work, plus the inability to host the review interface for the freelancer.

**Annual cost with Hetzner CPX31:** ~€170 in hosting. Plus the migration day (one Saturday) and ongoing maintenance (~30 min/month). Net new cost: ~€200/year and ~12 hours/year of ops time.

**Annual savings/benefits with Hetzner:** Unblocks freelancer review (which the math earlier showed is genuinely valuable). Decouples render scheduling from laptop availability. Removes risk of laptop loss / OS issues taking down production. Enables travel without breaking the pipeline.

The trade is favourable when *any* of the trigger moments fires. Right now, none has, so the trade is mildly negative. In 4-8 weeks, when the freelancer onboarding starts, the trade becomes clearly positive.

---

## Decision check before signing up

Five honest questions to answer yes-or-no before clicking "create account" at hetzner.com:

Am I shipping at least one video per week and seeing the laptop become a constraint? *Currently: no, but getting there.*

Am I within 30 days of hiring the stills reviewer? *Currently: pending review-rubric work and 2-3 more shipped videos.*

Do I have a free Saturday for the migration in the next 2 weeks? *You answer this.*

Am I comfortable with basic Linux server admin (SSH, package management, debugging at a distance)? *Yes — based on the vibe-coding fluency seen across this whole project, this is well within your range.*

Is the €170/year line item something I'm happy committing to indefinitely? *You answer this.*

If you can say "yes" to three or more of those, the migration earns its keep. If two or fewer, defer.

---

## What I'd actually do, sequenced

The honest plan I'd run if I were you, in order:

1. **Finish six_minutes and ship it.** Don't context-switch into infrastructure until video four is live.
2. **Bank the stills-review rubric** across videos five and six. Catch failure categories, refine the taxonomy.
3. **Then book a Saturday for the migration.** Probably 4-6 weeks from now. By then the trigger conditions are clearer, the rubric is mature enough for a reviewer, and the infrastructure investment is paying off immediately.
4. **Hire the freelancer two weeks after migration** so the review interface is stable before another human depends on it.

Don't migrate this week. Don't migrate next week. The right move right now is to keep shipping on the laptop and build up the cognitive surplus to do the migration properly when it matters. Premature infrastructure is one of the easiest ways to lose a month of momentum.

But know what you'll buy when the moment comes, which is what this document is for.
