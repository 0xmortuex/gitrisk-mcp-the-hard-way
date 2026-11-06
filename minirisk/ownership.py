"""Module 05: who knows this code, and how many people does it depend on?"""

from __future__ import annotations

from collections import Counter
from typing import Any

from .gitio import git
from .history import blame_counts, identities, stream_commits

DAY = 86400.0


def bus_factor(weights: list[float]) -> int:
    """Fewest people whose combined share is MORE than half. Two equal halves need both: 2."""
    total = sum(weights)
    cum = 0.0
    for k, w in enumerate(sorted(weights, reverse=True), 1):
        cum += w
        if cum * 2 > total:
            return k
    return len(weights)


def experts(repo: str, path: str, now: float, recent_days: int = 180) -> dict[str, Any]:
    sha = git(repo, "rev-parse", "HEAD").decode().strip()
    files = [p.decode() for p in git(repo, "ls-tree", "-r", "-z", "--name-only", sha, "--", path)
             .split(b"\x00") if p]
    surviving: Counter[str] = Counter()
    for f in files:
        surviving.update(blame_counts(repo, sha, f))
    ident = identities(repo, list(surviving))
    lines: Counter[str] = Counter()
    names: dict[str, str] = {}
    for h, n in surviving.items():
        name, email, _ = ident[h]
        lines[email] += n
        names[email] = name
    recent: Counter[str] = Counter()
    for c in stream_commits(repo):
        if now - c.ts > recent_days * DAY:
            continue
        for f in c.files:
            if f.path == path or f.path.startswith(path.rstrip("/") + "/"):
                recent[c.email] += f.added + f.deleted
                names.setdefault(c.email, c.author)
    total, rtotal = sum(lines.values()), sum(recent.values())
    rows = []
    for email in set(lines) | set(recent):
        b = lines[email] / total if total else 0.0
        r = recent[email] / rtotal if rtotal else 0.0
        rows.append({"name": names[email], "lines": lines[email], "blame_share": b,
                     "recent_share": r, "score": 0.6 * b + 0.4 * r if rtotal else b})
    rows.sort(key=lambda r: (-r["score"], r["name"]))
    return {"rows": rows, "bus_factor": bus_factor([float(v) for v in lines.values()])}
