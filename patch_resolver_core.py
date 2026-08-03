#!/usr/bin/env python3
"""patch_resolver_core.py -- splice the @-resolver into shared/v2/visuals.py.

Idempotent, anchor-verified, .pre_* backup, py_compile-before-write, ASCII-only.
Scope: resolver core (_load_assets/_detect_ats/_resolve_refs/_gen_still_edit) plus
the Pass-A branch that routes @-carrying beats to the seedream edit path BEFORE the
legacy {curly}+reference_paths guard. No canon rows, no admin GET, no intake gate:
those are the S3 registry-lock artifact. Run from the repo root.
"""
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

TARGET = Path("shared/v2/visuals.py")
SENTINEL = "def _gen_still_edit("

FUNCS = '''def _load_assets(project_dir: Path) -> dict:
    """Per-channel <channel>/assets.json: the frozen fal snapshot (S3 lock).
    Absent for films with no cast -- returns empty, the @-branch never fires."""
    p = project_dir.parent.parent / "assets.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _detect_ats(phenomenon: str) -> list:
    """All @identifiers in the authored phenomenon (Law-20 grammar, no digits)."""
    return re.findall(r"@([a-z][a-z_]*)", phenomenon or "")


def _resolve_refs(phenomenon: str, ats: list, assets: dict, beat_id: int):
    """@ids -> (image_urls from the frozen snapshot, prompt with @id -> name).
    Unknown or url-less @ is a HARD stop -- an unbound face never renders."""
    urls, disp = [], phenomenon
    for a in ats:
        rec = assets.get("@" + a) or assets.get(a)
        if not rec:
            raise SystemExit(
                "beat %d: unknown @%s -- not in <channel>/assets.json. "
                "Lock it (S3) or fix the mention." % (beat_id, a))
        rurls = rec.get("reference_urls") or []
        if not rurls:
            raise SystemExit(
                "beat %d: @%s has no reference_urls in assets.json -- "
                "run the registry --refresh to freeze the fal snapshot." % (beat_id, a))
        for u in rurls:
            if u not in urls:
                urls.append(u)
        disp = re.sub(r"@" + re.escape(a) + r"\\b", rec.get("name", a), disp)
    return urls, disp


def _gen_still_edit(prompt: str, image_urls: list, out_path: Path) -> Path | None:
    """P3 shape, verbatim: seedream v5 pro edit, explicit refs, FAL_KEY, sync."""
    import os
    key = os.environ.get("FAL_KEY")
    if not key:
        raise SystemExit("resolver: FAL_KEY not in environment")
    body = {"prompt": prompt, "image_urls": image_urls,
            "image_size": "landscape_16_9"}
    try:
        r = requests.post("https://fal.run/bytedance/seedream/v5/pro/edit",
                          headers={"Authorization": "Key " + key,
                                   "Content-Type": "application/json"},
                          json=body, timeout=300)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("      SKIP (edit refused): %s -- %s." % (out_path.name, type(e).__name__))
        return None
    imgs = data.get("images") or []
    if not imgs or "url" not in imgs[0]:
        print("      SKIP (edit no media): %s -- keys=%s" % (out_path.name, list(data)))
        return None
    return _download(imgs[0]["url"], out_path)


'''

FUNC_ANCHOR = "def _channel_fx_speckles(project_dir: Path) -> float:\n"

ASSETS_ANCHOR = '    style = proj["style_contract"] or ""\n'
ASSETS_ADD = '    assets = _load_assets(project_dir)\n'

BRANCH_ANCHOR = (
    '        m = re.match(r"^\\{([a-z0-9_]+)\\}", b["phenomenon"].strip())\n'
)
BRANCH_ADD = '''        _ats = _detect_ats(b["phenomenon"])
        if _ats:
            urls, disp = _resolve_refs(b["phenomenon"], _ats, assets, b["id"])
            eprompt = "%s. %s" % (style.strip(), disp) if style else disp
            out = stills_dir / ("shot_%03d.png" % b["id"])
            got = _gen_still_edit(eprompt, urls, out)
            v2db.log_generation(con, stage="stills", model="seedream_edit",
                                prompt=eprompt, beat_id=b["id"],
                                cost=STILL_COST if got else 0.0,
                                result_path=str(out) if got else None,
                                status="done" if got else "refused",
                                kept=1 if got else 0)
            if got:
                v2db.mark(con, b["id"], still_path=str(out))
            con.commit()
            continue
'''


def die(msg):
    print("ABORT: " + msg)
    sys.exit(1)


def main():
    if not TARGET.exists():
        die("%s not found -- run from the repo root." % TARGET)
    src = TARGET.read_text()

    if SENTINEL in src:
        print("already patched (%s present) -- no-op." % SENTINEL)
        return

    for name, anchor in (("funcs", FUNC_ANCHOR),
                         ("assets", ASSETS_ANCHOR),
                         ("branch", BRANCH_ANCHOR)):
        n = src.count(anchor)
        if n != 1:
            die("%s anchor found %d times (need exactly 1)." % (name, n))

    out = src.replace(FUNC_ANCHOR, FUNCS + FUNC_ANCHOR, 1)
    out = out.replace(ASSETS_ANCHOR, ASSETS_ANCHOR + ASSETS_ADD, 1)
    out = out.replace(BRANCH_ANCHOR, BRANCH_ADD + BRANCH_ANCHOR, 1)

    if not out.isascii():
        die("payload produced non-ASCII output.")

    tmp = Path(tempfile.gettempdir()) / "visuals_resolver_candidate.py"
    tmp.write_text(out)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        die("candidate failed py_compile: %s" % e)

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_resolver_core")
    shutil.copy2(str(TARGET), str(backup))
    TARGET.write_text(out)
    py_compile.compile(str(TARGET), doraise=True)
    print("patched %s (+%d lines); backup at %s"
          % (TARGET, out.count("\n") - src.count("\n"), backup.name))


if __name__ == "__main__":
    main()
