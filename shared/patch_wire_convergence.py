#!/usr/bin/env python3
"""
patch_wire_convergence.py — wire the convergence leg into orchestrate.py.

Adds `import convergence_leg` and, after the Mode A block, calls
run_convergence_leg(ctx, ma) when "convergence" is in the planned legs — so the
orchestrator runs the FULL arc (audio → modeB → modeA → convergence → final_video)
in one command instead of stopping at "legs not yet wired".

Idempotent + self-verifying (ast-parse). Backs up to orchestrate.py.pre_convergence.
"""
import io, sys, ast, shutil
from pathlib import Path

PATH = Path("shared/orchestrate.py")

IMPORT_OLD = "import modea_leg\n"
IMPORT_NEW = "import modea_leg\nimport convergence_leg\n"

# Anchor: the END of the Mode A block. We saw it as:
#     ma = modea_leg.run_modea_leg(ctx)
#     if ma is None:
#         t.halt("Mode A leg halted. Fix the reported issue and re-run.")
#         sys.exit(1)
# We append the convergence call immediately after that block, capturing `ma`.
MODEA_OLD = '''        ma = modea_leg.run_modea_leg(ctx)
        if ma is None:
            t.halt("Mode A leg halted. Fix the reported issue and re-run.")
            sys.exit(1)
'''

MODEA_NEW = '''        ma = modea_leg.run_modea_leg(ctx)
        if ma is None:
            t.halt("Mode A leg halted. Fix the reported issue and re-run.")
            sys.exit(1)
    else:
        ma = None

    # ── 3d: CONVERGENCE LEG (pool clips → assemble → final_video) — convergence_leg.py ──
    if "convergence" in legs:
        cv = convergence_leg.run_convergence_leg(ctx, ma)
        if cv is None:
            t.halt("convergence leg halted. Fix the reported issue and re-run.")
            sys.exit(1)
'''


def main():
    if not PATH.exists():
        sys.exit(f"!! {PATH} not found (run from repo root).")
    src = io.open(PATH, encoding="utf-8").read()

    if "import convergence_leg" in src and 'if "convergence" in legs:' in src:
        print("already wired (convergence import + call present) — no change.")
        return

    if IMPORT_OLD not in src:
        sys.exit("!! import anchor 'import modea_leg' not found — NOT patching.")
    if MODEA_OLD not in src:
        sys.exit("!! Mode A block anchor not found verbatim — NOT patching. Inspect orchestrate.py.")

    src = src.replace(IMPORT_OLD, IMPORT_NEW, 1)
    src = src.replace(MODEA_OLD, MODEA_NEW, 1)

    # Remove "convergence" from the pending/not-yet-wired message so it doesn't double-report.
    # (Harmless if the exact string differs; we only attempt a safe, specific swap.)
    pending_old = 'pending = [l for l in legs if l not in ("audio", "modeB", "modeA")]'
    pending_new = 'pending = [l for l in legs if l not in ("audio", "modeB", "modeA", "convergence")]'
    if pending_old in src:
        src = src.replace(pending_old, pending_new, 1)

    try:
        ast.parse(src)
    except SyntaxError as e:
        sys.exit(f"!! patched source does not parse ({e}) — NOTHING written.")

    shutil.copy2(PATH, str(PATH) + ".pre_convergence")
    io.open(PATH, "w", encoding="utf-8").write(src)
    print(f"patched {PATH}: convergence leg wired (import + call after Mode A; removed from pending).")
    print(f"backup → {PATH}.pre_convergence")


if __name__ == "__main__":
    main()
