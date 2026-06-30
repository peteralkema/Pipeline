# patch_per_channel_image_model.py
# Makes IMAGE_MODEL per-channel instead of a global constant, so QQrew can render
# on nano_banana while Final Hours / Sacred Dawn / etc. stay on flux.
#
# WHAT IT DOES (idempotent, anchor-verified, .pre_* backup, py_compile-gated):
#   In shared/recreation_pipeline.py, generate_still() currently hardcodes:
#       endpoint = IMAGE_ENDPOINTS[IMAGE_MODEL]
#   This patch replaces that line so the model is read from the resolved channel
#   config (channel.json "image_model"), falling back to the module IMAGE_MODEL
#   default ("flux") when the channel doesn't specify one. The flux-only
#   safety_tolerance branch already keys off the resolved model, so it stays correct.
#
# Run on LAPTOP (edit machine). Commit + push + pull on box as usual.
import sys, shutil, datetime, pathlib, subprocess

SRC = pathlib.Path("shared/recreation_pipeline.py")

# The exact anchor we expect inside generate_still (verified live this session).
ANCHOR = '    endpoint = IMAGE_ENDPOINTS[IMAGE_MODEL]'

# Replacement: resolve model from channel config, default to module IMAGE_MODEL.
# generate_still already computes `config = load_channel_config(strict=True, anchor=out_path)`
# a few lines above, so `config` is in scope here.
REPLACEMENT = (
    '    # Per-channel image model: channel.json may set "image_model"\n'
    '    # (e.g. "nano_banana" for flat-cel channels). Falls back to the module\n'
    '    # IMAGE_MODEL default ("flux") for cinematic channels that omit it.\n'
    '    model = config.get("image_model", IMAGE_MODEL)\n'
    '    endpoint = IMAGE_ENDPOINTS[model]'
)

# The safety_tolerance branch must also key off `model`, not the global.
ST_ANCHOR = '    if IMAGE_MODEL == "flux":'
ST_REPLACEMENT = '    if model == "flux":'

SENTINEL = 'model = config.get("image_model", IMAGE_MODEL)'

def main():
    if not SRC.exists():
        print("ERR not found:", SRC, "(run from repo root on LAPTOP)"); sys.exit(1)
    text = SRC.read_text()

    if SENTINEL in text:
        print("Already patched (per-channel image_model present). Nothing to do.")
        return

    # Verify both anchors exist exactly once before touching anything.
    if text.count(ANCHOR) != 1:
        print(f"ERR endpoint anchor found {text.count(ANCHOR)}x (expected 1). Aborting, no write.")
        sys.exit(1)
    if text.count(ST_ANCHOR) != 1:
        print(f"ERR safety_tolerance anchor found {text.count(ST_ANCHOR)}x (expected 1). Aborting, no write.")
        sys.exit(1)

    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = SRC.with_suffix(f".py.pre_imagemodel_{ts}")
    shutil.copy(SRC, bak)

    new = text.replace(ANCHOR, REPLACEMENT).replace(ST_ANCHOR, ST_REPLACEMENT)
    SRC.write_text(new)

    # Gate on py_compile; restore backup if it fails.
    r = subprocess.run([sys.executable, "-m", "py_compile", str(SRC)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        shutil.copy(bak, SRC)
        print("ERR py_compile failed; restored backup. Error:\n", r.stderr)
        sys.exit(1)

    print("OK per-channel image_model wired into generate_still()")
    print("  - endpoint now: IMAGE_ENDPOINTS[config.get('image_model', IMAGE_MODEL)]")
    print("  - safety_tolerance branch keyed off resolved model")
    print("  - py_compile: clean")
    print("backup:", bak.name)
    print('\nNEXT: add  "image_model": "nano_banana"  to qqrew/channel.json,')
    print("then re-render Ep3. Other channels (no image_model key) stay on flux.")

if __name__ == "__main__":
    main()
