"""Module 04: which files change together? support and confidence."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .history import stream_commits
from .hotspots import RenameMap, files_at


def coupling(repo: str, target: str, max_files_per_commit: int = 50,
             min_support: int = 2) -> dict[str, Any]:
    live = files_at(repo)
    rn = RenameMap()
    totals: Counter[str] = Counter()    # commits touching each file
    together: Counter[str] = Counter()  # commits touching each file AND the target
    n_target = 0
    for c in stream_commits(repo):
        rn.learn(c.files)
        if len(c.files) > max_files_per_commit:
            continue
        files = {rn.resolve(f.path) for f in c.files}
        totals.update(files)
        if target in files:
            n_target += 1
            together.update(files - {target})
    rows = [{"path": p, "support": s, "confidence": s / n_target, "reverse": s / totals[p]}
            for p, s in together.items() if p in live and s >= min_support]
    rows.sort(key=lambda r: (-r["confidence"], -r["support"], r["path"]))
    return {"target": target, "commits": n_target, "rows": rows}
