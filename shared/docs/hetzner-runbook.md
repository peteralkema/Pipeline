# Hetzner Migration Runbook
*Repeatable procedure for deploying the Pipeline to a Hetzner Cloud VPS.*
*Destination in repo: `shared/docs/hetzner-runbook.md`*
*First executed: June 2026 (Final Hours / Success Coach). Verified against `recreation_pipeline.py` + `upload.py` on `peteralkema/Pipeline@main`.*

---

## The rule this runbook exists to support

**NO HETZNER = NO VIDEOS.** After the first successful cutover, every Final Hours, Synthetic Press, and Lazarus Films video is generated and uploaded from the VPS. The laptop is a thin SSH client and a place to write Python and eyeball final cuts — it is not a production runtime.

---

## What you need before starting

- Hetzner Cloud account (no box provisioned yet)
- Accounts/keys: Anthropic (`ANTHROPIC_API_KEY`), fal.ai (`FAL_KEY`), Inworld TTS (`INWORLD_API_KEY`)
- Per-channel YouTube OAuth: `token.json` + `client_secret.json` in each channel folder
- GitHub repo: `peteralkema/Pipeline` (private)
- An SSH keypair on the laptop (created in Phase 1 if absent)
- One uninterrupted block — budget ~6 hours, most of it unattended waits

### A note on the credential set — read before you build `.env`

The code reads exactly **three** environment keys: `ANTHROPIC_API_KEY`, `INWORLD_API_KEY`, `FAL_KEY` — plus `JAMENDO_CLIENT_ID` for music scoring. Notes for anyone copying an old brief:

- It is `INWORLD_API_KEY`, **not** `INWORLD_TTS_API_KEY`. The latter name will silently leave TTS unauthenticated.
- `JAMENDO_CLIENT_ID` **is required**: `music_score.py` (the live Jamendo scoring path that replaced fal's single-track music) reads it and `SystemExit`s on startup if it's missing. `recreation_pipeline.py` itself doesn't read it, which is what the old note below got wrong. Music there is generated via `fal-ai/elevenlabs/music` on the same `FAL_KEY`. Jamendo is only needed if `music_score.py` is in your live run path. Confirm before deciding:
  ```bash
  grep -rn "JAMENDO\|jamendo" --include="*.py" .
  ```
  If that returns hits in a script you actually run, add `JAMENDO_CLIENT_ID` to `.env`. If not, leave it out.

---

## Phase 0 — Pre-flight on the laptop (do this BEFORE provisioning)

The goal of Phase 0 is that the box never has to guess versions or hunt for secrets.

**0a. Freeze dependencies from the working venv — with moviepy pinned.**
The code uses `from moviepy.editor import ...`, which moviepy 2.x deleted. A fresh `pip install moviepy` on the box installs 2.x and every import dies. Pin it:
```bash
# in the active laptop venv
pip freeze > requirements.txt
grep -i '^moviepy' requirements.txt   # confirm it reads moviepy==1.x.x
```
If the freeze didn't pin it (e.g. it was installed via a constraint), hard-pin it by hand: ensure `requirements.txt` contains a line like `moviepy<2` or the exact `moviepy==1.0.3` the laptop runs. **Always install on the box from this file, never by package name.**

**0b. Reconcile `.env` against what the code reads.**
```bash
cat .env
```
Confirm the three keys above are present and correctly named. Decide Jamendo per the grep in 0a's sibling note.

**0c. (Optional, recommended) Land the `safety_tolerance` hygiene fix before you push.**
Not a migration step, but the first VPS render is your proof-of-life, and `fal-ai/flux-pro/v1.1` (the default `IMAGE_MODEL`) silently returns ~50% black-frame stills without it. One line in `generate_still`'s args dict in `recreation_pipeline.py`:
```python
args = {"prompt": full_prompt, "image_size": ASPECT, "safety_tolerance": "5"}
```
Commit and push so the box clones the fixed version. Skip only if you're deliberately keeping it separate.

**0d. Commit and push.**
```bash
git add requirements.txt
git commit -m "Pin deps (moviepy<2) for Hetzner deploy"
git push origin main
```

**0e. Pre-push TLS guard — sweep for disabled cert verification.**
Hardcoded `verify=False` and global `_create_unverified_context` are Zscaler-era
hacks that must never reach the box. Sweep before every push:
```bash
grep -rn "verify=False\|verify = False\|_create_unverified_context" --include="*.py" .
```
Any hit in executable code (not a comment/docstring) gets fixed before committing.
On a clean machine `requests`/httpx use the system + certifi CA store automatically.

**Gate:** `requirements.txt` is committed with moviepy pinned, `.env` is reconciled, secrets are still gitignored. Do not provision until this is true.

---

## Phase 1 — Provision and harden the box (~45 min)

**1a. Ensure an SSH key exists on the laptop:**
```bash
ls ~/.ssh/id_ed25519.pub 2>/dev/null || ssh-keygen -t ed25519 -C "peter-hetzner"
cat ~/.ssh/id_ed25519.pub   # copy this whole line
```

**1b. Create the server** in the Hetzner Cloud console (console.hetzner.cloud):
New Project → "Pipeline" → Add Server.
- Location: **Falkenstein** (Germany; low latency to fal.ai EU endpoints)
- Image: **Ubuntu 24.04**
- Type: **CPX31** (4 vCPU, 8GB RAM, 160GB disk, x86/AMD). *Take x86, not the cheaper ARM CAX tier — torch/whisper prebuilt wheels are far less fiddly on x86.*
- SSH keys: paste the public key from 1a. (This makes the box key-only from birth — you never set a root password.)
- Create. Note the public IP.

**1c. SSH in as root** (no password prompt — the key is already installed):
```bash
ssh root@YOUR_SERVER_IP
```

**1d. Update the system:**
```bash
apt update && apt upgrade -y
```

**1e. Create the non-root user and give it your key:**
```bash
adduser peter            # set a password — used only for sudo
usermod -aG sudo peter
rsync --archive --chown=peter:peter ~/.ssh /home/peter
```

**1f. CRITICAL — prove the new login works BEFORE hardening.**
In a **second, separate** laptop terminal, keeping the root session open:
```bash
ssh peter@YOUR_SERVER_IP
sudo whoami     # must print: root
```
If this fails, fix it from the still-open root session. Locking yourself out of a fresh box by hardening before verifying is the classic first-day mistake.

**1g. Harden SSH** (as `peter`, once 1f is green):
```bash
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

**1h. Firewall — SSH only** (443 is opened later, on review-server day):
```bash
sudo ufw allow OpenSSH
sudo ufw enable          # type y at the disruption warning
sudo ufw status          # confirm OpenSSH is listed
```

**1i. fail2ban:**
```bash
sudo apt install -y fail2ban
sudo systemctl enable --now fail2ban
sudo fail2ban-client status
```

**Gate:** `peter` logs in with key only, root login refused, `ufw status` shows OpenSSH, fail2ban running.

---

## Phase 2 — Runtime (~30 min)

**2a. System dependencies:**
```bash
sudo apt install -y python3.12 python3.12-venv python3-pip ffmpeg git tmux rsync build-essential
```

**2b. Create the venv** (mirrors the laptop's):
```bash
python3.12 -m venv ~/venvs/pipeline
source ~/venvs/pipeline/bin/activate
```

**Gate:** `python --version` reports 3.12.x; `ffmpeg -version` and `git --version` succeed.

---

## Phase 3 — Code and credentials (~30 min)

**3a. Clone the repo** (over HTTPS with a GitHub token, or set up a deploy key):
```bash
cd ~
git clone https://github.com/peteralkema/Pipeline.git
cd Pipeline
```

**3b. Install pinned dependencies:**
```bash
pip install -r requirements.txt     # installs moviepy<2 from the pin
```

**3c. Copy the gitignored secrets across via scp** (run these FROM THE LAPTOP, not the box):
```bash
scp .env peter@YOUR_SERVER_IP:~/Pipeline/.env
scp final-hours/token.json        peter@YOUR_SERVER_IP:~/Pipeline/final-hours/token.json
scp final-hours/client_secret.json peter@YOUR_SERVER_IP:~/Pipeline/final-hours/client_secret.json
scp success-coach/token.json        peter@YOUR_SERVER_IP:~/Pipeline/success-coach/token.json
scp success-coach/client_secret.json peter@YOUR_SERVER_IP:~/Pipeline/success-coach/client_secret.json
```
**Never delete these tokens.** `upload.py` only does `creds.refresh(Request())` — it refreshes headless fine, but a *full* re-auth needs a browser the box doesn't have.

**3d. Import smoke test:**
```bash
cd ~/Pipeline/final-hours
python -c "import sys; sys.path.insert(0,'../shared'); import recreation_pipeline"
```
Clean exit = all imports resolve on Linux.

**Gate:** imports cleanly, `.env` and both channels' credentials in place.

---

## Phase 4 — Pipeline smoke test (the proof point) (~1–2 hr)

Run a known-good project through assembly-only. Mary Celeste is the reference:
```bash
cd ~/Pipeline/final-hours
python ../shared/recreation_pipeline.py finish --project mary_celeste --no-music --assemble-only
```

**Verification:** the output `final_video.mp4` matches the laptop's — **~15:54 duration and identical Whisper-aligned shot timings.** If duration and timings match, the migration is proven and the pipeline runs cloud-native. This is the bar; everything else is refinement.

---

## Phase 5 — First Hetzner-native render

Pick the video you're shipping next (the next Final Hours). Run the full pipeline inside **tmux** so it survives your SSH session closing:
```bash
tmux new -s render
source ~/venvs/pipeline/bin/activate
cd ~/Pipeline/final-hours
# ... run the full render command for the new project ...
# detach with Ctrl-b then d; reattach later with: tmux attach -t render
```
Whisper downloads its `small` model (~470MB) on first alignment — let it. After this, the box is the production environment.

---

## What's different on Linux vs Mac (verified against the code)

1. **SSL / Zscaler — no action needed, and no `verify=False` to carry.** `recreation_pipeline.py` and `upload.py` gate the cert workaround on `~/combined_cacert.pem` existing. On the VPS that file is absent, so `REQUESTS_VERIFY` falls through to `True` and all `requests` calls use full, correct TLS verification automatically. Do **not** copy any `verify=False` hack across. *(The aggressive `httpx.Client.__init__` monkey-patch from the 3 June session notes lives only in `restill_from_feedback.py` / `serve_review.py` — the review-server utilities. Gate those on a cert-file check or env flag if and when you run the review server on the box. They are not on the render/upload path.)*

2. **moviepy.editor namespace.** Handled by the Phase 0 pin. Never `pip install moviepy` fresh on the box.

3. **No `caffeinate`, no laptop-sleep hacks.** 24/7 uptime; long renders go in tmux, not behind a propped-open lid.

4. **Whisper model cache** downloads on first use on the box; one-time ~470MB.

5. **Credential names** as corrected above (`INWORLD_API_KEY`; Jamendo conditional).

---

## Cutover

Cutover is decided when Phase 4 passes. From that point:

- The next Final Hours render runs on the box (Phase 5), not the laptop.
- The laptop stops being a runtime. It keeps a git clone for editing code (push → pull on box) and downloads final cuts for QC before publish.
- **Keep Google Drive as a read-only backup mirror for a few months** while the VPS workflow proves itself, then drop it once the box is trusted as the source of truth.
- Back up `.env` separately (encrypted, e.g. 1Password). If the box dies, the keys must be recoverable. Take a Hetzner snapshot after Phase 4.

---

## Security — minimum bar

SSH key-only, no password login. Non-root user for daily work. `ufw`: only SSH open until review-server day (then add 443). fail2ban running. `.env` backed up encrypted off-box. Monthly `sudo apt update && sudo apt upgrade` (set a calendar reminder).

---

## Lockout / trouble recovery

- **Can't log in as `peter` after hardening:** use the still-open root session (Phase 1f is why you keep it open) or Hetzner's web console (console.hetzner.cloud → server → Console) to fix `/etc/ssh/sshd_config` and `~/.ssh/authorized_keys`.
- **Locked out entirely:** Hetzner web console always works regardless of SSH/ufw state — use it to reset config; if needed, `sudo ufw disable` from there.
- **Import errors after clone:** almost always the moviepy pin — `pip show moviepy` and confirm it's <2.
- **TTS/auth 401s:** check `.env` key *names* match what the code reads (`INWORLD_API_KEY`, not `INWORLD_TTS_API_KEY`).
- **~50% black-frame stills:** the `safety_tolerance: "5"` fix (Phase 0c) didn't land — patch and re-render.

---

## Maintenance cadence

Monthly `apt upgrade`. Snapshot before any risky change. Re-run the Phase 0a freeze on the laptop whenever you add a dependency, then `git pull` + `pip install -r requirements.txt` on the box.
