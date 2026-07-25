# Hetzner Portability Notes — 1 June 2026

Pre-migration audit of the pipeline before Thursday 4 June 2026 deployment to Hetzner Cloud.

## Audit results — all clean

**Hardcoded macOS paths:** zero. Pipeline uses `pathlib.Path` and relative paths throughout. Confirmed via `grep -rn "/Users/\|/Volumes/\|~/Library/" --include="*.py" .` returning nothing.

**Mac-only imports:** zero. The full import set in `shared/recreation_pipeline.py` is: `dotenv`, `moviepy.editor`, `pathlib.Path`, `anthropic`, `argparse`, `base64`, `fal_client`, `json`, `os`, `requests`. All pip-installable on Ubuntu 24.04.

**Zscaler/CERT_BUNDLE workaround:** lines 172-176 of recreation_pipeline.py check for `~/combined_cacert.pem` and only activate if the file exists. On Hetzner the file won't exist → workaround stays dormant → normal SSL verification used. No code change needed.

## What needs to transfer Thursday

**Code:** `git clone https://github.com/peteralkema/Pipeline.git` on the VPS. That brings everything except the gitignored files below.

**Credentials (via scp, NOT in git):**
- `.env` at Pipeline root — contains ANTHROPIC_API_KEY, INWORLD_API_KEY, FAL_KEY
- `final-hours/token.json` — YouTube OAuth for the Final Hours channel
- `success-coach/token.json` — YouTube OAuth for the Success Coach channel
- `final-hours/client_secret.json` — Google Cloud OAuth client
- `success-coach/client_secret.json` — same

**Python dependencies (via pip on VPS):** anthropic, fal-client, requests, python-dotenv, moviepy, openai-whisper, Pillow, google-auth, google-auth-oauthlib, google-api-python-client.

Generate exact versions Wednesday evening via `pip freeze > requirements.txt` in the active venv on the laptop.

**System dependencies (via apt on VPS):** python3.12, python3.12-venv, python3-pip, ffmpeg, git, tmux, rsync.

**Whisper model cache:** Whisper downloads the `small` model on first use (~470MB). Let it download on the VPS the first time `align_with_whisper.py` runs.

## What stays on the laptop

- The Zscaler `~/combined_cacert.pem` certificate bundle (ABB-specific, not needed on VPS)
- The local Python venv `success-coach` (recreate on VPS as a fresh venv with the same package set)
- Mary Celeste's final_video.mp4 and other gigabyte-scale outputs (regeneratable from VPS)
- Google Drive sync (becomes optional backup; VPS becomes source of truth after migration)

## Thursday morning sequence

1. **08:00-09:00:** Provision Hetzner CPX31 in Falkenstein, Ubuntu 24.04. SSH harden (key-only auth, ufw firewall, fail2ban).
2. **09:00-10:00:** Install system deps via apt. Install Python venv. Install pip dependencies.
3. **10:00-11:00:** `git clone` the Pipeline repo. scp credentials. Test that pipeline imports cleanly.
4. **11:00-12:00:** Run Mary Celeste `finish --assemble-only` on the VPS. Compare output to laptop's final_video.mp4.
5. **12:00-13:30:** Leo call hard interrupt.
6. **13:30-17:00:** Document runbook. Optional HTTPS review server stretch goal. Hetzner snapshot.

## Verification proof point

If `python ../shared/recreation_pipeline.py finish --project mary_celeste --no-music --assemble-only` produces a final_video.mp4 of identical duration (~15:54) and identical Whisper-aligned shot timings on the VPS, the migration is proven and the pipeline runs cloud-native.

