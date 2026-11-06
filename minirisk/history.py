"""Module 02: per-file changes (git log --numstat -z) and surviving lines (git blame)."""

from __future__ import annotations

import re
import subprocess
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field

from .gitio import FORMAT, Commit, GitError, clean_env, git, parse_record


@dataclass
class FileChange:
    path: str
    added: int
    deleted: int
    binary: bool = False
    old_path: str | None = None  # set when git detected a rename


@dataclass
class DetailedCommit(Commit):
    files: list[FileChange] = field(default_factory=list)


def parse_numstat(rest: bytes) -> list[FileChange]:
    r"""-z output: 'A\tD\tpath\0'. A rename is 'A\tD\t\0old\0new\0'. A binary file is '-\t-\t...'."""
    toks = rest.lstrip(b"\n").split(b"\x00")
    out: list[FileChange] = []
    i = 0
    while i < len(toks):
        if not toks[i]:
            i += 1
            continue
        a, d, p = toks[i].split(b"\t", 2)
        binary = a == b"-"
        added, deleted = (0, 0) if binary else (int(a), int(d))
        if p == b"":
            out.append(FileChange(toks[i + 2].decode("utf-8", "backslashreplace"), added, deleted,
                                  binary, toks[i + 1].decode("utf-8", "backslashreplace")))
            i += 3
        else:
            out.append(FileChange(p.decode("utf-8", "backslashreplace"), added, deleted, binary))
            i += 1
    return out


def stream_commits(repo: str, rev: str = "HEAD", merges: bool = False,
                   since: str | None = None, max_count: int | None = None) -> Iterator[DetailedCommit]:
    """Yield commits newest-first WHILE git is still producing them (constant memory)."""
    if rev.startswith("-"):
        raise GitError(f"invalid ref {rev!r}")
    args = ["git", "-C", repo, "log", "-z", "-M", "--numstat", "--date-order", "--format=" + FORMAT]
    if not merges:
        args.append("--no-merges")
    if since:
        args.append(f"--since={since}")
    if max_count:
        args.append(f"--max-count={max_count}")
    args.append(rev)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, env=clean_env())
    assert proc.stdout is not None
    try:
        buf = b""
        while chunk := proc.stdout.read1(1 << 16):  # type: ignore[attr-defined]
            buf += chunk
            *done, buf = buf.split(b"\x1e")
            for rec in done:
                if rec:
                    yield _decode(rec)
        if buf:
            yield _decode(buf)
    finally:
        if proc.poll() is None:
            proc.kill()      # the caller stopped early: do not leave git running
        proc.wait()
        proc.stdout.close()


def _decode(rec: bytes) -> DetailedCommit:
    head, _, rest = rec.partition(b"\x00")
    c = parse_record(head.decode("utf-8", "replace"))
    return DetailedCommit(c.sha, c.ts, c.author, c.email, c.parents, c.subject, parse_numstat(rest))


_HDR = re.compile(rb"^([0-9a-f]{40}|[0-9a-f]{64}) \d+ \d+")


def blame_counts(repo: str, sha: str, path: str) -> Counter[str]:
    """Surviving lines per commit: every line of --line-porcelain starts with its commit sha."""
    out = git(repo, "blame", "--line-porcelain", "-w", "-M", sha, "--", path)
    counts: Counter[str] = Counter()
    for line in out.split(b"\n"):
        if line[:1] == b"\t":      # the file's own content: never parse it
            continue
        m = _HDR.match(line)
        if m:
            counts[m.group(1).decode()] += 1
    return counts


def identities(repo: str, shas: list[str]) -> dict[str, tuple[str, str, int]]:
    """sha -> (name, email, time) with .mailmap applied, for many shas in one git call."""
    out = git(repo, "log", "--no-walk=unsorted", "--stdin", "--format=%H%x1f%aN%x1f%aE%x1f%at",
              input_=("\n".join(shas) + "\n").encode())
    res = {}
    for line in out.decode("utf-8", "replace").splitlines():
        h, n, e, t = line.split("\x1f")
        res[h] = (n, e.lower(), int(t))
    return res
