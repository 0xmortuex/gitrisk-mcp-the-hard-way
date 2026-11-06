"""Run every module's main.py against real git, the way CI does.

Each main.py builds its own scripted repository in a temp directory and checks its
results with assert, so a chapter whose code drifts from what its README claims fails here.

Usage: python verify.py            # all modules
       python verify.py 03 05      # just these
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    if not shutil.which("git"):
        sys.exit("git not found on PATH - install git first")
    wanted = sys.argv[1:]
    modules = sorted(
        d for d in os.listdir(ROOT)
        if os.path.isfile(os.path.join(ROOT, d, "main.py"))
        and (not wanted or any(d.startswith(w) for w in wanted))
    )
    if not modules:
        print("no modules matched")
        return 1
    failed = []
    for m in modules:
        start = time.monotonic()
        proc = subprocess.run([sys.executable, os.path.join(ROOT, m, "main.py")],
                              capture_output=True, text=True, timeout=300, cwd=ROOT)
        ok = proc.returncode == 0
        print(f"{'PASS' if ok else 'FAIL'}  {m}  ({time.monotonic() - start:.1f}s)")
        if not ok:
            failed.append(m)
            print("    " + (proc.stdout + proc.stderr).strip().replace("\n", "\n    "))
    print(f"\n{len(modules) - len(failed)}/{len(modules)} modules verified against real git")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
