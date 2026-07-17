"""
Mission Control — ingest: the Create front door + rich project listing.

create_project(): the whole "agreed script.md -> launchable project" flow,
server-side, zero keystrokes for the operator:
   1. resolve channel folder from the script's `channel:` header
   2. mkdir <channel>/projects/<slug>/   (slug validated; refuse if exists)
   3. write script.md
   4. run parse_script.py -> beats.json + beats_full.json
   5. VERIFY (wordless beats / missing VISUAL) -> REFUSE on hard errors
   6. scoped git add/commit/push (pull first; WARN-not-block if push fails)
   7. return {ok, slug, channel, verify, git} so the page can select + show

rich_list_projects(): newest-first, each with channel/date/stage for the
dropdown labels. Sequence is a VIEW property (sort), never identity (folder name).

The paste-text box in the UI is the seam a future Claude MCP connector fills:
same endpoint, different producer of the script text.
"""

from __future__ import annotations
import json
import os
import re
import subprocess
import time
from pathlib import Path

_MC = Path(__file__).resolve().parent
_SHARED = _MC.parent
_REPO = _SHARED.parent


# --------------------------------------------------------------------------
# Channel folder resolution (hyphen/underscore tolerant, like the orchestrator)
# --------------------------------------------------------------------------

def _resolve_channel_folder(header_channel: str) -> str | None:
    for c in (header_channel, header_channel.replace("_", "-"),
              header_channel.replace("-", "_")):
        if (_REPO / c / "channel.json").is_file():
            return c
    return None


def _parse_header_channel(script_text: str) -> str | None:
    """Read the `channel:` value from the script header (first lines before
    the first '## ' section)."""
    for line in script_text.splitlines():
        s = line.strip()
        if s.startswith("## "):
            break
        if s.lower().startswith("channel:"):
            return s.split(":", 1)[1].strip()
    return None


SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")


def validate_slug(slug: str) -> str | None:
    """Return an error string if invalid, else None."""
    if not slug:
        return "slug is empty"
    if not SLUG_RE.match(slug):
        return ("slug must be lowercase letters/numbers/hyphens, "
                "start alphanumeric, <=61 chars (e.g. watchers-daughters)")
    return None


# --------------------------------------------------------------------------
# Verify — the same checks the ante-machinam threshold one-liner runs
# --------------------------------------------------------------------------

def _wordless_is_legal(channel_dir) -> bool:
    """# [wordless] silence is legal when the channel declares timing_source=beatsheet

    A wordless-spine channel (picture + score carry the story; VO is a sparse, removable
    layer) has silent beats BY DESIGN. Its timing is declared in the beat-sheet, not
    measured from narration, so it never enters build_audio_script's continuous-narration
    doctrine. Absent that declaration, a wordless beat remains an authoring error.
    """
    if not channel_dir:
        return False
    try:
        cfg_path = Path(channel_dir) / "channel.json"
        if not cfg_path.is_file():
            return False
        return json.loads(cfg_path.read_text(encoding="utf-8")).get("timing_source") == "beatsheet"
    except Exception:
        return False   # unreadable config -> strict. Never relax a gate on an error.


def verify_beats(beats_path: Path, channel_dir=None) -> dict:
    """Return {ok, beats, modes, wordless, no_visual, wordless_ok}. ok=False on hard errors.

    wordless beats are a hard error EXCEPT on a timing_source=beatsheet channel, where
    they are legal and merely reported (the silent-beat inventory is craft information).
    A Mode A beat with no VISUAL is a hard error on every channel.
    """
    b = json.loads(beats_path.read_text())
    wordless = [x["index"] for x in b if not (x.get("narration") or "").strip()]
    no_visual = [x["index"] for x in b
                 if x.get("mode") == "A" and not (x.get("visual") or "").strip()]
    modes = {}
    for x in b:
        modes[x.get("mode")] = modes.get(x.get("mode"), 0) + 1
    wordless_ok = _wordless_is_legal(channel_dir)
    return {
        "ok": (wordless_ok or not wordless) and not no_visual,
        "beats": len(b),
        "modes": modes,
        "wordless": wordless,
        "wordless_ok": wordless_ok,
        "no_visual": no_visual,
    }


# --------------------------------------------------------------------------
# Git — scoped, pull-first, warn-not-block
# --------------------------------------------------------------------------

def _git(args: list[str]) -> tuple[int, str]:
    p = subprocess.run(["git"] + args, cwd=str(_REPO),
                       capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def _commit_project(rel_project_dir: str, slug: str) -> dict:
    """pull -> add ONLY this project -> commit -> push. Never -A. Warn, don't
    block, on any failure (the project is already usable locally for launch)."""
    steps = []
    rc, out = _git(["pull", "--no-edit"])
    steps.append(("pull", rc, out[-200:]))
    rc, out = _git(["add", rel_project_dir])
    steps.append(("add", rc, out[-200:]))
    rc, out = _git(["commit", "-m", f"add project {slug}"])
    steps.append(("commit", rc, out[-200:]))
    if rc != 0:
        # nothing to commit (e.g. files gitignored) — not fatal
        return {"pushed": False, "warn": "commit produced nothing / failed",
                "steps": steps}
    rc, out = _git(["push"])
    steps.append(("push", rc, out[-200:]))
    if rc != 0:
        return {"pushed": False,
                "warn": "could not push to GitHub — project is created locally; sync later",
                "steps": steps}
    return {"pushed": True, "steps": steps}


# --------------------------------------------------------------------------
# Create — the whole front door
# --------------------------------------------------------------------------

def create_project(script_text: str, slug: str, do_git: bool = True) -> dict:
    serr = validate_slug(slug)
    if serr:
        return {"ok": False, "stage": "slug", "error": serr}

    header_channel = _parse_header_channel(script_text)
    if not header_channel:
        return {"ok": False, "stage": "header",
                "error": "no `channel:` line found in the script header"}

    folder = _resolve_channel_folder(header_channel)
    if not folder:
        return {"ok": False, "stage": "channel",
                "error": f"channel '{header_channel}' has no matching folder "
                         f"with channel.json"}

    project_dir = _REPO / folder / "projects" / slug
    if project_dir.exists():
        return {"ok": False, "stage": "exists",
                "error": f"project already exists: {folder}/projects/{slug}"}

    # 1. mkdir + 2. write script.md
    project_dir.mkdir(parents=True, exist_ok=False)
    script_md = project_dir / "script.md"
    script_md.write_text(script_text, encoding="utf-8")

    # 3. parse
    beats = project_dir / "beats.json"
    beats_full = project_dir / "beats_full.json"
    parse = subprocess.run(
        [os.sys.executable, str(_SHARED / "parse_script.py"), str(script_md),
         "--json", str(beats), "--json-full", str(beats_full)],
        cwd=str(_REPO), capture_output=True, text=True)
    if parse.returncode != 0 or not beats.is_file():
        # parse failed -> tear down the half-made project so it doesn't
        # appear launchable in the dropdown
        _safe_rmtree(project_dir)
        return {"ok": False, "stage": "parse",
                "error": (parse.stdout + parse.stderr)[-600:] or "parse failed"}

    # 4. verify — REFUSE on hard errors (missing VISUAL always; wordless unless the
    #    channel declares timing_source=beatsheet, where silence is by design)
    v = verify_beats(beats, channel_dir=folder)
    if not v["ok"]:
        _safe_rmtree(project_dir)
        return {"ok": False, "stage": "verify",
                "error": "script has hard errors — fix and re-create",
                "verify": v}

    # 5. git (scoped, warn-not-block)
    git_result = None
    if do_git:
        git_result = _commit_project(f"{folder}/projects/{slug}", slug)

    return {
        "ok": True,
        "channel": header_channel,
        "folder": folder,
        "slug": slug,
        "verify": v,
        "git": git_result,
    }


def _safe_rmtree(p: Path):
    """Remove a freshly-created project dir on failure. Guarded to only ever
    delete inside a channel's projects/ tree."""
    rp = p.resolve()
    if "/projects/" in str(rp) and rp.is_dir() and str(rp).startswith(str(_REPO.resolve())):
        import shutil
        shutil.rmtree(rp, ignore_errors=True)


# --------------------------------------------------------------------------
# Rich project listing — newest-first, with channel/date/stage labels
# --------------------------------------------------------------------------

def _project_stage(project_dir: Path) -> str:
    """Roll the per-beat stages up to one project-level stage word."""
    modea = project_dir / "modea"
    final = modea / "final_video.mp4"
    if final.is_file():
        return "assembled"
    clips = modea / "clips"
    stills = modea / "stills"
    if clips.is_dir() and any(clips.glob("*.mp4")):
        return "animated"
    if stills.is_dir() and any(stills.glob("*.png")):
        return "stills"
    if (project_dir / "beats_full.json").is_file():
        return "parsed"
    return "authored"


def rich_list_projects(channel_folder: str) -> list[dict]:
    """Newest-first list of {slug, stage, created} for one channel folder."""
    pdir = _REPO / channel_folder / "projects"
    if not pdir.is_dir():
        return []
    out = []
    for d in pdir.iterdir():
        if not d.is_dir():
            continue
        bf = d / "beats_full.json"
        # creation time: beats_full mtime if present, else dir mtime
        ts = bf.stat().st_mtime if bf.is_file() else d.stat().st_mtime
        out.append({
            "slug": d.name,
            "stage": _project_stage(d),
            "created": ts,
            "created_label": time.strftime("%d %b", time.localtime(ts)),
        })
    out.sort(key=lambda x: x["created"], reverse=True)  # newest first
    return out
