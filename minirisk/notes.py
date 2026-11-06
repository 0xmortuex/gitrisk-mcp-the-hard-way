"""Module 06: release notes from conventional commits, PR numbers and merges."""

from __future__ import annotations

import re
from collections import defaultdict

from .gitio import Commit, commits, git

TITLES = {"feat": "Features", "fix": "Bug fixes", "perf": "Performance", "refactor": "Refactoring",
          "docs": "Documentation", "test": "Tests", "build": "Build", "ci": "CI",
          "chore": "Chores", "style": "Style"}
CC = re.compile(r"^(?P<type>[A-Za-z]+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?:\s*(?P<desc>.+)$")
PR_TAIL = re.compile(r"\(#(\d+)\)\s*$")
PR_MERGE = re.compile(r"^Merge pull request #(\d+) from (\S+)")


def parse_subject(subject: str) -> dict[str, object]:
    """feat(api)!: add x (#12)  ->  type, scope, breaking, description, PR number."""
    cc = CC.match(subject)
    tail = PR_TAIL.search(subject)
    return {
        "type": cc.group("type").lower() if cc and cc.group("type").lower() in TITLES else None,
        "scope": cc.group("scope") if cc else None,
        "breaking": bool(cc and cc.group("bang")),
        "desc": cc.group("desc") if cc else subject,
        "pr": int(tail.group(1)) if tail else None,
    }


def release_notes(repo: str, from_ref: str, to_ref: str = "HEAD") -> str:
    rng: list[Commit] = commits(repo, f"{from_ref}..{to_ref}")
    groups: dict[str, list[str]] = defaultdict(list)
    merges = []
    for c in rng:
        if c.is_merge:
            m = PR_MERGE.match(c.subject)
            merges.append(f"- #{m.group(1)} ({m.group(2)})" if m else f"- {c.subject}")
            continue
        p = parse_subject(c.subject)
        title = TITLES.get(str(p["type"]), "Other changes")
        scope = f"**{p['scope']}:** " if p["scope"] else ""
        groups[title].append(f"- {scope}{p['desc']} ({c.sha[:7]})")
    order = list(TITLES.values()) + ["Other changes"]
    out = [f"## {from_ref}..{to_ref}", "", f"{len(rng)} commits", ""]
    for title in order:
        if title in groups:
            out += [f"### {title}", *groups[title], ""]
    if merges:
        out += ["### Merged pull requests", *merges, ""]
    return "\n".join(out)


def latest_tag(repo: str) -> str:
    return git(repo, "describe", "--tags", "--abbrev=0").decode().strip()
