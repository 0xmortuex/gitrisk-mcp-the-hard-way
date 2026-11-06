"""Module 01: talk to git safely and parse the simplest useful log.

Two rules carry the whole project:
  1. Always pass an argument LIST to subprocess, never a shell string.
  2. Pick separators that cannot appear in the data (ASCII 0x1f and 0x1e).
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass


class GitError(Exception):
    pass


def clean_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_OPTIONAL_LOCKS"] = "0"      # even `git log` may refresh the index: forbid it
    env["GIT_LITERAL_PATHSPECS"] = "1"   # a path is a path, not a glob
    return env


def git(repo: str, *args: str, input_: bytes | None = None) -> bytes:
    cmd = ["git", "-c", "core.quotepath=off", "-c", "log.showSignature=false", "-C", repo, *args]
    proc = subprocess.run(cmd, input=input_, capture_output=True, env=clean_env(), check=False)
    if proc.returncode != 0:
        raise GitError(f"git {args[0]} failed: {proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout


@dataclass
class Commit:
    sha: str
    ts: int
    author: str
    email: str
    parents: tuple[str, ...]
    subject: str

    @property
    def is_merge(self) -> bool:
        return len(self.parents) > 1


# %H sha, %at author time (unix), %aN/%aE author name/email WITH .mailmap applied,
# %P parent shas, %s subject.  \x1f separates fields, \x1e starts a record.
FORMAT = "%x1e%H%x1f%at%x1f%aN%x1f%aE%x1f%P%x1f%s"


def parse_record(text: str) -> Commit:
    sha, ts, name, email, parents, subject = text.split("\x1f")
    return Commit(sha, int(ts), name, email.lower(), tuple(parents.split()), subject.strip())


def commits(repo: str, rev: str = "HEAD") -> list[Commit]:
    if rev.startswith("-"):
        raise GitError(f"invalid ref {rev!r}")  # never let a ref turn into an option
    out = git(repo, "log", "--format=" + FORMAT, rev).decode("utf-8", "replace")
    return [parse_record(r) for r in out.split("\x1e") if r.strip()]


def is_shallow(repo: str) -> bool:
    return git(repo, "rev-parse", "--is-shallow-repository").decode().strip() == "true"
