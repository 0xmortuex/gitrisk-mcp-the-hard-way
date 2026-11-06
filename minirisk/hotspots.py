"""Module 03: which files are risky? churn x recency x number of authors."""

from __future__ import annotations

import math
from typing import Any

from .gitio import git
from .history import stream_commits

DAY = 86400.0


def decay(age_days: float, half_life_days: float) -> float:
    """Weight of a change that is `age_days` old: halves every `half_life_days`."""
    return 1.0 if half_life_days <= 0 else 0.5 ** (max(age_days, 0.0) / half_life_days)


class RenameMap:
    """git log is newest-first, so a rename is seen BEFORE the older commits that use the old name."""

    def __init__(self) -> None:
        self.alias: dict[str, str] = {}

    def resolve(self, p: str) -> str:
        while p in self.alias:
            p = self.alias[p]
        return p

    def learn(self, files: list[Any]) -> None:
        for f in files:
            if f.old_path:
                self.alias[f.old_path] = self.resolve(f.path)


def files_at(repo: str, rev: str = "HEAD") -> set[str]:
    out = git(repo, "ls-tree", "-r", "-z", "--name-only", rev)
    return {p.decode("utf-8", "backslashreplace") for p in out.split(b"\x00") if p}


def hotspots(repo: str, now: float, half_life_days: float = 90.0, max_files_per_commit: int = 100,
             since: str | None = None) -> list[dict[str, Any]]:
    live = files_at(repo)
    rn = RenameMap()
    stats: dict[str, dict[str, Any]] = {}
    for c in stream_commits(repo, since=since):
        rn.learn(c.files)                         # learn renames even from commits we skip
        if len(c.files) > max_files_per_commit:   # a reformat says nothing about risk
            continue
        weight = decay((now - c.ts) / DAY, half_life_days)
        for f in c.files:
            p = rn.resolve(f.path)
            if p not in live:                     # deleted files are not hotspots
                continue
            s = stats.setdefault(p, {"commits": 0, "lines": 0, "w": 0.0, "authors": set()})
            lines = 1 if f.binary else f.added + f.deleted
            s["commits"] += 1
            s["lines"] += lines
            s["w"] += lines * weight
            s["authors"].add(c.email)
    rows = [{"path": p, "score": s["w"] * (1 + math.log2(len(s["authors"]))), "commits": s["commits"],
             "lines": s["lines"], "authors": len(s["authors"])} for p, s in stats.items()]
    rows.sort(key=lambda r: (-r["score"], r["path"]))
    return rows
