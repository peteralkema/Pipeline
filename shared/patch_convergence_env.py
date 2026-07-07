#!/usr/bin/env python3
"""patch_convergence_env.py - propagate env (FAL_KEY) into convergence_leg._run's Popen."""
import py_compile, shutil, sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "convergence_leg.py"
ANCHOR = ("    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,\n"
          "                            stderr=subprocess.STDOUT, text=True, bufsize=1)")
REPLACEMENT = ("    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,\n"
               "                            stderr=subprocess.STDOUT, text=True, bufsize=1,\n"
               "                            env=os.environ.copy())")

def main():
    if not TARGET.is_file():
        sys.exit(f"ABORT: {TARGET} not found.")
    src = TARGET.read_text()
    if REPLACEMENT in src:
        print("OK (already patched)"); return
    if ANCHOR not in src:
        sys.exit("ABORT: anchor not found verbatim — inspect convergence_leg.py; do NOT force.")
    needs_os = not any(l.strip() == "import os" for l in src.splitlines()[:40])
    shutil.copy2(TARGET, TARGET.with_suffix(".py.pre_env"))
    new = src.replace(ANCHOR, REPLACEMENT, 1)
    if needs_os:
        lines = new.splitlines(keepends=True)
        ins = next((i for i,l in enumerate(lines[:40]) if l.startswith(("import ","from "))), 0)
        lines.insert(ins, "import os\n"); new = "".join(lines)
    TARGET.write_text(new)
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(TARGET.with_suffix(".py.pre_env"), TARGET)
        sys.exit(f"ABORT: py_compile failed, reverted: {e}")
    print("PATCHED: convergence_leg._run now passes env=os.environ.copy()"
          + ("  (added import os)" if needs_os else ""))

if __name__ == "__main__":
    main()
