#!/usr/bin/env python3
"""
patch_channel_resolver_hyphen.py — make the orchestrator's channel resolver tolerant
of the hyphen/underscore difference between a channel's declared NAME and its FOLDER.

WHY: channel.json names use underscores (final_hours, synthetic_press, success_coach)
but the folders on disk use hyphens (final-hours/, synthetic/, success-coach/). The
resolver did `channel_dir = channel` verbatim, so the header `final_hours` looked for
`final_hours/channel.json` and missed `final-hours/channel.json`. This bit two channels
in a row (synthetic, final-hours) — it is a class bug, not an instance.

FIX: try the name as-given, then the '-'→'_' and '_'→'-' variants, and use whichever
folder actually contains a channel.json. Still falls back to the ./channel.json
(run-from-inside) case and the same warning if nothing matches. Idempotent.
"""
import io, sys

PATH = "shared/orchestrate.py"

OLD = '''    channel_dir = channel  # <repo_root>/<channel>/
    cfg_path = os.path.join(channel_dir, "channel.json")
    if not os.path.exists(cfg_path):
        # tolerate being run from inside the channel folder too (./channel.json)
        if os.path.exists("channel.json"):
            cfg_path, channel_dir = "channel.json", "."
        else:
            t.warn(f"channel.json not found for '{channel}' "
                   f"(looked for {channel}/channel.json from repo root). "
                   f"Run from ~/Pipeline, or check the channel name in the script header.")
            return None, None'''

NEW = '''    # Channel NAME (header / channel.json) uses underscores; the FOLDER on disk uses
    # hyphens (final_hours -> final-hours/, synthetic_press -> synthetic/ via alias).
    # Try the name as-given, then the '-'/'_' swaps, and use whichever folder has a
    # channel.json. (channel-agnostic: you never think about which spelling you used.)
    candidates = []
    for cand in (channel, channel.replace("_", "-"), channel.replace("-", "_")):
        if cand not in candidates:
            candidates.append(cand)
    channel_dir = None
    cfg_path = None
    for cand in candidates:
        p = os.path.join(cand, "channel.json")
        if os.path.exists(p):
            channel_dir, cfg_path = cand, p
            break
    if cfg_path is None:
        # tolerate being run from inside the channel folder too (./channel.json)
        if os.path.exists("channel.json"):
            cfg_path, channel_dir = "channel.json", "."
        else:
            t.warn(f"channel.json not found for '{channel}' "
                   f"(tried {', '.join(c + '/channel.json' for c in candidates)} from repo root). "
                   f"Run from ~/Pipeline, or check the channel name in the script header.")
            return None, None'''


def main():
    src = io.open(PATH, encoding="utf-8").read()
    if NEW.split("\n")[1].strip() in src:
        print("already patched (hyphen/underscore tolerant resolver present) — no change.")
        return
    if OLD not in src:
        print("!! anchor block not found verbatim — NOT patching. Inspect the resolver manually.",
              file=sys.stderr)
        sys.exit(1)
    src = src.replace(OLD, NEW, 1)
    io.open(PATH, "w", encoding="utf-8").write(src)
    print(f"patched {PATH}: channel resolver now tolerates hyphen/underscore folder naming.")


if __name__ == "__main__":
    main()
