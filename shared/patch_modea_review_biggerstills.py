#!/usr/bin/env python3
"""
patch_modea_review_biggerstills.py — make the Mode A stills-review page show the STILL
large (like the Mode B clip), so detail is visible for review.

ROOT CAUSE: Mode A's grid was `360px 1fr 380px` — the IMAGE column was fixed at 360px
while the TEXT column got the flexible `1fr`. So the still stayed small while text grew.
Mode B looks big because its media column is `minmax(360px,1fr)` — it grows to fill.

FIX (Option A, CSS only, all 3 columns kept): give the IMAGE column the flexible large
share. Image grows with the window; narration flexes; controls keep a fixed width.
Also updates the 1200px breakpoint to match. Idempotent.
"""
import io, sys
from pathlib import Path

PATH = Path("shared/make_review_page.py")

OLD_MAIN = "  .shot {{ display: grid; grid-template-columns: 360px 1fr 380px; gap: 20px;"
NEW_MAIN = "  .shot {{ display: grid; grid-template-columns: minmax(480px, 1.6fr) minmax(0, 1fr) 340px; gap: 20px;"

OLD_BP = "  @media (max-width: 1200px) {{ .shot {{ grid-template-columns: 280px 1fr 320px; }} }}"
NEW_BP = "  @media (max-width: 1200px) {{ .shot {{ grid-template-columns: minmax(360px, 1.4fr) minmax(0, 1fr) 300px; }} }}"


def main():
    if not PATH.exists():
        sys.exit(f"!! {PATH} not found (run from repo root).")
    src = io.open(PATH, encoding="utf-8").read()
    if "minmax(480px, 1.6fr)" in src:
        print("already patched (bigger stills layout present) — no change.")
        return
    if OLD_MAIN not in src:
        sys.exit("!! main .shot grid anchor not found verbatim — NOT patching. Inspect make_review_page.py line ~90.")
    src = src.replace(OLD_MAIN, NEW_MAIN, 1)
    if OLD_BP in src:
        src = src.replace(OLD_BP, NEW_BP, 1)
    else:
        print("   (note: 1200px breakpoint anchor not found — left as-is; main grid still patched.)")
    io.open(PATH, "w", encoding="utf-8").write(src)
    print(f"patched {PATH}: Mode A still column now flexes large (image gets the 1.6fr share).")


if __name__ == "__main__":
    main()
