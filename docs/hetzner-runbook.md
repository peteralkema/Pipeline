# Hetzner Runbook & As-Is Status
*The single source of truth for the production box. Process AND current state.*
*Destination in repo: `shared/docs/hetzner-runbook.md`*
*v1.0 — 4 June 2026. Supersedes the pre-migration draft.*

This document has two halves:
- **Part A — As-Is Status (v1.0):** a snapshot of what exists right now. Read this to know what you're rebuilding *to*.
- **Part B — Rebuild Runbook:** the proven, step-by-step procedure to recreate the box from zero.

The test this document must pass: *if all institutional memory vanished, could Peter (or a freelancer) rebuild this box from nothing using only this file.* Every surprise we hit on 4 June is written down here so the next rebuild doesn't rediscover it the hard way.

The governing rule: **NO HETZNER = NO VIDEOS.** Every video is generated and uploaded from this box. The laptop is a thin client for code edits, script writing, thumbnail design (Clickly), and final QC — not a production runtime.

---

# PART A — As-Is Status (v1.0, 4 June 2026)

## The box

| Field | Value |
|---|---|
| Provider | Hetzner Cloud |
| Project | Pipeline |
| Name | pipeline-prod |
| Server ID | #136326963 |
| Type | **CPX32** (4 vCPU AMD, 8GB RAM, 160GB SSD) — x86, *not* Arm |
| Location | Falkenstein, Germany (eu-central, DC Park 1) |
| OS | Ubuntu 24.04.4 LTS |
| Kernel | 6.8.0-124-generic (post-reboot) |
| IPv4 | 116.202.18.68 |
| IPv6 | 2a01:4f8:c014:a48d::/64 |
| Cost | ~€17.50/mo incl. IPv4 + VAT |

## Access

- **SSH is on port 443, not 22.** The production network (Zscaler/corporate) blocks/breaks outbound 22 — the connection establishes then dies at key exchange. 443 looks like HTTPS and passes. SSH listens on **both** 22 and 443; you connect on 443.
- Connect: `ssh -p 443 peter@116.202.18.68`
- Login user: **peter** (sudo-enabled). Root login disabled.
- Auth: **SSH key only**, no passwords. Key: laptop's `~/.ssh/id_ed25519` (comment `peter-hetzner`).
- **Emergency door:** Hetzner web console (console.hetzner.cloud → pipeline-prod → `>_` icon). Goes through Hetzner's own 443 infrastructure — works even if SSH, ufw, or the network all fail. Needs a root password (set via the **Rescue** tab when needed). This is the Zscaler-proof fallback that can never be locked out.

## Security posture

- SSH: `PermitRootLogin no`, `PasswordAuthentication no`, key-only.
- Socket-activation (`ssh.socket`) **disabled**; classic always-on `ssh.service` enabled. (Required on Ubuntu 24.04 — the socket ignores `Port` lines in `sshd_config`.)
- ufw: active, default **deny incoming**, allow outgoing. Open ports: **22/tcp, 443/tcp** (v4 + v6).
- fail2ban: active, watching sshd on ports 22,443. `ignoreip` whitelists `127.0.0.1/8 ::1 147.161.230.109` — the last is the **Zscaler egress IP**, whitelisted so we can't self-ban (all our traffic appears to come from it). *If the egress IP changes, update `/etc/fail2ban/jail.local` or risk a lockout — but the web console always recovers.*

## Runtime

- venv: `~/venvs/pipeline`, Python **3.12.3** (matches laptop, matches frozen requirements).
- System deps: python3.12, python3.12-venv, python3-pip, ffmpeg (6.1.1), git (2.43), tmux (3.4), rsync, build-essential.
- Repo: `~/Pipeline`, cloned from `github.com/peteralkema/Pipeline`, at commit **9b7e483** ("Pin dependencies moviepy<2").
- Python deps: installed from pinned `requirements.txt`. **moviepy==1.0.3** (critical — `moviepy.editor` namespace breaks on 2.x). Confirmed `from moviepy.editor import ...` works on the box.
- TLS: clean. No `verify=False` anywhere in executable code (purged 3 June). `ssl_compat.py` gates the Zscaler cert workaround on `~/combined_cacert.pem` existing — absent on the box, so normal/correct TLS verification is used. certifi provides the CA baseline.

## Secrets on the box

- `~/Pipeline/.env` (chmod 600), built fresh — **not** copied from laptop. Five real keys filled: `ANTHROPIC_API_KEY`, `FAL_KEY`, `INWORLD_API_KEY`, `JAMENDO_CLIENT_ID`, `PEXELS_API_KEY`. Four `YOUTUBE_*` lines present but **empty** (vestigial — YouTube auth is file-based). No Mac paths (the old `*_ROOT` and `PIPELINE_CA_BUNDLE` vars were dead and dropped).
- YouTube OAuth, per channel (chmod 600), scp'd over 443:
  - `~/Pipeline/final-hours/token.json` + `client_secret.json`
  - `~/Pipeline/success-coach/token.json` + `client_secret.json`
  - Tokens refresh headless (`creds.refresh(Request())`, no browser fallback). A *full* re-auth would need a browser the box lacks — **never delete these tokens.**

## What is PROVEN on the box (as of 4 June)

- Provisioning, hardening, reboot-survival (box comes back on 443 unattended).
- Repo clone, dependency install, all core imports (`moviepy.editor`, `fal_client`, `anthropic`, `certifi`).
- **YouTube upload, end-to-end, headless** — `upload.py` authenticated via copied token, uploaded an unlisted test video, confirmed in Studio, deleted. The auth + upload path works on Linux.

## What is NOT yet proven (do not assume)

- **The generation half:** fal image calls, Inworld TTS, Jamendo music — none exercised on the box yet. These go through the rebuilt SSL/certifi path with the new `.env` keys; expected to work, unverified as of v1.0. First validation = a disposable end-to-end render.
- No full video has been rendered on the box.

## Known loose ends (banked, not yet done)

1. **`final-hours/upload.py` was edited ON THE BOX, not in git.** The 4 June change — dropped SRT generation + caption upload (auto-captions drift and were being deleted in Studio anyway), made `script.txt` conditional on a missing `metadata.json` — exists only on the box. **Reconcile to the laptop + repo from the laptop side, then `git pull` on the box.** Until then, a fresh clone would NOT have this change.
2. **`upload.py` is duplicated per channel and has drifted.** `final-hours/upload.py` has `metadata.json` support + bare-project-name resolve that `success-coach/upload.py` lacks, and now also the SRT/script change. Unify into a single `shared/upload.py` (final-hours version canonical) — **revisit at channel 3**, per build-for-two-design-for-ten.
3. **`generate_srt` import + `upload_captions` function** in `final-hours/upload.py` are now orphaned (calls removed, definitions remain). Harmless; clean up during the channel-3 unification.
4. **Per-channel Google Cloud projects** for YouTube quota: at scale (10k units/day, ~6 uploads/day per GCP project), give channel 3+ its own GCP project. Credential swap, no code change.
5. **Thumbnails are laptop-in-the-loop.** Clickly is a browser GUI; thumbnails are made on the laptop and scp'd into the project folder. `upload.py` attaches `thumbnail.jpg`/`.png` if present, else lets YouTube auto-generate (graceful).

---

# PART B — Rebuild Runbook (proven procedure)

*Rebuilds the box from zero. Every step here was executed on 4 June 2026. Sections marked **[UNVERIFIED]** are expected behaviour not yet confirmed — validate, don't trust.*

## Phase 0 — Laptop pre-flight (before provisioning)

In the active laptop venv, at the repo root:

```bash
pip freeze > requirements.txt
grep -i '^moviepy' requirements.txt          # MUST read moviepy==1.0.3 (or <2). If 2.x, hard-pin it.
grep -o '^[A-Z_]*=' .env | sort              # confirm key names (required set in Phase 3)
```

Pre-push TLS guard — no disabled cert verification may reach the box:

```bash
grep -rn "verify=False\|verify = False\|_create_unverified_context" --include="*.py" .
```

Any hit in executable code (not a comment/docstring) gets fixed before committing. Then commit the pinned requirements and push.

## Phase 1 — Provision and harden

**1a. SSH key on the laptop:**
```bash
ls ~/.ssh/id_ed25519.pub 2>/dev/null || ssh-keygen -t ed25519 -C "peter-hetzner"
cat ~/.ssh/id_ed25519.pub
```

**1b. Provision** at console.hetzner.cloud: New Project "Pipeline" → Add Server → Location **Falkenstein** → Image **Ubuntu 24.04** → Type **CPX32** (Regular Performance tab → x86/AMD; the 4 vCPU / 8GB / 160GB row — *not* Arm CAX, torch/whisper wheels are painful on Arm) → paste the SSH key → name `pipeline-prod` → Create. Note the IPv4.

**1c. First access — EXPECT PORT 22 TO FAIL on the Zscaler network.** Try `ssh root@<IP>` from the laptop. If it times out (connection establishes then dies — the network breaking SSH on 22), **do not fight it.** Use the web console:
- console.hetzner.cloud → pipeline-prod → **`>_`** icon (top right).
- If it shows `login:` and you have no password: server page → **Rescue** tab → **Reset root password** → copy the one-time password → log into the `>_` console as `root` with it.
- You're now on the box via the browser, bypassing the network entirely.

**1d. Update:**
```bash
apt update && apt upgrade -y
```

**1e. Create the non-root user (in the web console as root):**
```bash
adduser peter                       # set a password (for sudo)
usermod -aG sudo peter
getent group sudo                   # MUST show 'peter' at the end — verify it took
mkdir -p /home/peter/.ssh
chmod 700 /home/peter/.ssh
echo '<PASTE-YOUR-id_ed25519.pub-LINE-HERE>' > /home/peter/.ssh/authorized_keys
chmod 600 /home/peter/.ssh/authorized_keys
chown -R peter:peter /home/peter/.ssh
cat /home/peter/.ssh/authorized_keys    # verify: exactly one line, ends 'peter-hetzner'
wc -l /home/peter/.ssh/authorized_keys  # verify: 1
```
*(Web-console paste mangles heredocs — use single-line `echo`, not `cat <<EOF`.)*

**1f. Put SSH on 443 (the step that makes the box reachable on this network):**
```bash
echo 'Port 443' >> /etc/ssh/sshd_config
echo 'Port 22'  >> /etc/ssh/sshd_config        # keep 22 too (free, works on permissive networks)
grep -n '^Port' /etc/ssh/sshd_config            # verify both present
systemctl disable --now ssh.socket              # Ubuntu 24.04: socket ignores Port lines
systemctl enable ssh.service
systemctl restart ssh.service
ss -tlnp | grep -E ':(22|443)'                  # MUST show sshd on 0.0.0.0:443 AND :22 (v4+v6 = 4 lines)
```

**1g. Test 443 from the laptop BEFORE hardening** (new terminal, keep the console open):
```bash
ssh -p 443 peter@<IP>
sudo whoami                                      # asks peter's password, must print 'root'
```
If `sudo whoami` says "not in sudoers," the group add didn't apply to the session — reconnect (group changes need a fresh login). If still failing, re-run `usermod -aG sudo peter` in the root console.

**1h. Harden SSH (only after 443 login + sudo both proven):**
```bash
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```
Then open a *second* laptop terminal and confirm a fresh `ssh -p 443 peter@<IP>` still logs in (no password prompt). Prove the door still opens before trusting it.

**1i. Firewall (allow 443 BEFORE enabling, or you lock yourself out):**
```bash
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable                                  # y at the warning
sudo ufw status verbose                          # confirm 443 + 22 ALLOW, default deny in
```

**1j. fail2ban + self-ban guard:**
```bash
sudo apt install -y fail2ban
```
Find your egress IP first (the SSH login banner shows it: `... from <IP>`), then:
```bash
sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
# Never ban our own egress (Zscaler exit IP) or localhost. Update if egress changes.
ignoreip = 127.0.0.1/8 ::1 147.161.230.109
[sshd]
enabled = true
port = 22,443
maxretry = 5
bantime = 1h
findtime = 10m
EOF
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd
```
*(In a real SSH session heredocs paste fine — only the web console mangles them. Expect to see random bot IPs already banned within minutes of going public; that's normal and not you.)*

**1k. Reboot — the real lockout test:**
```bash
sudo reboot
```
Wait ~60s, then `ssh -p 443 peter@<IP>` from the laptop. Landing at the prompt unattended = the box comes up correctly configured on its own. Phase 1 done.

## Phase 2 — Runtime

```bash
sudo apt install -y python3.12 python3.12-venv python3-pip ffmpeg git tmux rsync build-essential
python3.12 -m venv ~/venvs/pipeline
source ~/venvs/pipeline/bin/activate
which python && python --version            # must be ~/venvs/pipeline/.../python, 3.12.x
```

## Phase 3 — Code, secrets, deps

**Clone:**
```bash
cd ~
git clone https://github.com/peteralkema/Pipeline.git
cd ~/Pipeline
git log --oneline -3                         # confirm the expected HEAD commit
```

**Build `.env` fresh** (do NOT copy the laptop's — it carries Mac paths). Create with the nine keys, fill the five real ones by hand (values never leave the laptop→box path):
```bash
cat > ~/Pipeline/.env << 'EOF'
ANTHROPIC_API_KEY=
FAL_KEY=
INWORLD_API_KEY=
JAMENDO_CLIENT_ID=
PEXELS_API_KEY=
YOUTUBE_CLIENT_ID_A=
YOUTUBE_CLIENT_SECRET_A=
YOUTUBE_CLIENT_ID_B=
YOUTUBE_CLIENT_SECRET_B=
EOF
nano ~/Pipeline/.env                         # fill the 5 real keys; leave the 4 YOUTUBE_* empty
chmod 600 ~/Pipeline/.env
grep -c '=..*' ~/Pipeline/.env               # MUST be 5 (five filled)
```
Required keys and exact names: `ANTHROPIC_API_KEY`, `FAL_KEY`, `INWORLD_API_KEY` (NOT `INWORLD_TTS_API_KEY`), `JAMENDO_CLIENT_ID` (required — `music_score.py` SystemExits without it), `PEXELS_API_KEY`.

**Copy YouTube auth files from the laptop (over 443 — capital `-P` for scp):**
```bash
# FROM THE LAPTOP, at the repo root:
scp -P 443 final-hours/token.json final-hours/client_secret.json peter@<IP>:~/Pipeline/final-hours/
scp -P 443 success-coach/token.json success-coach/client_secret.json peter@<IP>:~/Pipeline/success-coach/
# THEN ON THE BOX:
chmod 600 ~/Pipeline/*/token.json ~/Pipeline/*/client_secret.json
```

**Install deps:**
```bash
pip install -r requirements.txt
pip show moviepy | grep Version              # MUST be 1.0.3
python -c "from moviepy.editor import VideoFileClip; import fal_client, anthropic, certifi; print('imports OK')"
```
*(If pip starts compiling torch from source rather than using a wheel, you're on the wrong arch — confirm x86, not Arm.)*

## Phase 4 — Upload smoke test (PROVEN)

Isolate the upload/auth path with a throwaway:
```bash
mkdir -p ~/Pipeline/final-hours/projects/_uploadtest
cd ~/Pipeline/final-hours
ffmpeg -f lavfi -i color=c=black:s=640x360:d=3 -c:v libx264 -pix_fmt yuv420p projects/_uploadtest/final_video.mp4
cat > projects/_uploadtest/metadata.json << 'EOF'
{"title":"UPLOAD PIPELINE TEST - DELETE ME","description":"Upload path test. Safe to delete.","tags":["test"]}
EOF
python upload.py --project _uploadtest --privacy unlisted
```
Success = `OK Video uploaded -> https://youtu.be/...`. Confirm in Studio, **delete it**, then `rm -rf projects/_uploadtest`.
*(Requires the `final-hours/upload.py` SRT-drop edit from loose-end #1. A fresh clone without that edit will demand `script.txt` and a storyboard for SRT generation. Reconcile that edit to git so future clones have it.)*

## Phase 5 — Generation + full render  **[UNVERIFIED as of v1.0]**

Not yet validated on the box. Expected: a disposable short render exercises fal (images) → Inworld (TTS) → Jamendo (music) → Whisper align → moviepy assemble → unlisted upload, all through the certifi/SSL path. Run long jobs in **tmux** (`tmux new -s render`, detach Ctrl-b d, reattach `tmux attach -t render`) so they survive disconnects. Whisper downloads its `small` model (~470MB) on first use. **Validate this section and change it from UNVERIFIED to PROVEN after the first successful render.**

---

## Maintenance

Monthly `sudo apt update && sudo apt upgrade` (calendar reminder). Snapshot before risky changes. Re-run the Phase 0 freeze on the laptop when adding a dependency, then `git pull` + `pip install -r requirements.txt` on the box. Back up `.env` encrypted off-box (e.g. 1Password) — if the box dies the keys must be recoverable.

---

## Changelog

- **v1.0 — 4 June 2026.** First real migration. Box provisioned (CPX32 Falkenstein), hardened (SSH on 443 due to network blocking 22, key-only, ufw, fail2ban with egress whitelist), repo cloned, deps installed and importing, `.env` built, YouTube upload proven end-to-end. Generation/render path not yet validated. Corrects the pre-migration draft: CPX31→CPX32, SSH 22→443, adds web-console bootstrap, adds fail2ban egress whitelist, marks `JAMENDO_CLIENT_ID` required, adds as-is status snapshot.
