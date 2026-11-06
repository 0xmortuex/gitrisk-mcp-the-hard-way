"""Module 07: wrap everything as an MCP server with a directory sandbox.

Run:  python -m minirisk.server --dir /path/to/repos
"""

from __future__ import annotations

import argparse
import functools
import os
import time
from collections.abc import Callable
from typing import Any, TypeVar

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from . import coupling as coupling_mod
from . import notes, ownership
from . import hotspots as hotspots_mod
from .gitio import GitError, git

mcp = MCPServer("minirisk", instructions="Read-only git history analytics: hotspots, "
                "file_experts, change_coupling, release_notes. Pass repo= (path).")

ROOTS: list[str] = []
F = TypeVar("F", bound=Callable[..., Any])


def norm(p: str) -> str:
    return os.path.normcase(os.path.realpath(p))


def open_repo(path: str | None) -> str:
    """Return the repo toplevel, but only if it lives under an allowed root."""
    roots = ROOTS or [norm(os.getcwd())]
    path = path or roots[0]
    if not os.path.isdir(path):
        raise GitError(f"{path!r} is not a directory")
    top = git(path, "rev-parse", "--show-toplevel").decode().strip()
    # Check the REPOSITORY, not just the folder the caller named: a sub-folder of an
    # allowed root could belong to a repository that lives outside it.
    if not any(os.path.commonpath([norm(top), r]) == r for r in roots) or not any(
            os.path.commonpath([norm(path), r]) == r for r in roots):
        raise GitError(f"{path!r} is outside the allowed directories {roots}; start the server "
                       "with --dir <path>")
    return top


def tool(fn: F) -> F:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except GitError as e:
            raise ToolError(str(e)) from e   # the ONLY exception type clients get to read

    mcp.tool()(wrapper)
    return fn


def fmt(rows: list[dict[str, Any]], cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        lines.append("| " + " | ".join(f"{r[c]:.2f}" if isinstance(r[c], float) else str(r[c])
                                       for c in cols) + " |")
    return "\n".join(lines)


@tool
def hotspots(repo: str | None = None, half_life_days: float = 90.0, limit: int = 10,
             max_files_per_commit: int = 100) -> str:
    """Rank files by recency-weighted churn x (1 + log2 authors). Skips mass commits."""
    top = open_repo(repo)
    rows = hotspots_mod.hotspots(top, time.time(), half_life_days, max_files_per_commit)[:limit]
    return fmt(rows, ["path", "score", "commits", "lines", "authors"])


@tool
def file_experts(path: str, repo: str | None = None) -> str:
    """Who knows this file or directory (blame + recent commits), and the bus factor."""
    top = open_repo(repo)
    res = ownership.experts(top, path, time.time())
    if not res["rows"]:
        raise GitError(f"no history for {path!r}; paths are relative to the repository root")
    return f"bus factor {res['bus_factor']}\n" + fmt(
        res["rows"], ["name", "lines", "blame_share", "recent_share", "score"])


@tool
def change_coupling(path: str, repo: str | None = None) -> str:
    """Files that change in the same commits as `path`: support and confidence."""
    top = open_repo(repo)
    res = coupling_mod.coupling(top, path)
    if res["commits"] == 0:
        raise GitError(f"no commits touch {path!r}")
    return fmt(res["rows"], ["path", "support", "confidence", "reverse"])


@tool
def release_notes(from_ref: str | None = None, to_ref: str = "HEAD",
                  repo: str | None = None) -> str:
    """Markdown release notes grouped by conventional-commit type."""
    top = open_repo(repo)
    return notes.release_notes(top, from_ref or notes.latest_tag(top), to_ref)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", action="append", default=[])
    ns = ap.parse_args()
    ROOTS[:] = [norm(d) for d in ns.dir]
    mcp.run()


if __name__ == "__main__":
    main()
