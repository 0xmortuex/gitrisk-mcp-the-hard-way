"""Build the small, fully scripted repository every module analyses.

Real git, real commits, explicit identities and dates, so every number the modules
print can be checked by hand. History (author, date, files and lines appended):

  c1 alice 2026-01-05  feat: initial core            app/core.py +10  app/util.py +4  README.md +2
  c2 bob   2026-01-12  fix: edge case (#1)           app/core.py +5   app/util.py +2
  c3 alice 2026-01-19  feat(api): routes (#2)        app/core.py +3   api/routes.py +6      <- tag v0.1
  c4 carol 2026-02-02  docs: explain routes          api/routes.py +4
  c5 bob   2026-02-09  refactor: tidy                app/core.py +2   app/util.py +1
  c6 carol 2026-02-16  style: reformat everything    vendor/f00..f11.txt +1 each, app/core.py +1
"""

from __future__ import annotations

import os
import subprocess

ALICE = ("Alice", "alice@example.com")
BOB = ("Bob", "bob@example.com")
CAROL = ("Carol", "carol@example.com")

AS_OF = "2026-03-01T00:00:00"  # the "now" used by the modules, so scores are reproducible


def git(path: str, *args: str, env: dict[str, str] | None = None) -> str:
    full = os.environ.copy() if env is None else env
    proc = subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "-c", "core.autocrlf=false", *args],
        cwd=path, capture_output=True, env=full, check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode(errors="replace"))
    return proc.stdout.decode("utf-8", "replace")


class Repo:
    def __init__(self, path: str) -> None:
        self.path = path
        os.makedirs(path, exist_ok=True)
        git(path, "init", "-q")
        git(path, "config", "user.name", "setup")
        git(path, "config", "user.email", "setup@example.com")
        git(path, "config", "commit.gpgsign", "false")
        self.counter = 0

    @classmethod
    def existing(cls, path: str) -> "Repo":
        """Wrap a repository that already exists (no git init)."""
        r = cls.__new__(cls)
        r.path, r.counter = path, 1000
        return r

    def commit(self, who: tuple[str, str], date: str, message: str, appends: dict[str, int]) -> None:
        for rel, n in appends.items():
            full = os.path.join(self.path, *rel.split("/"))
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "ab") as fh:  # explicit "\n": identical on every OS
                for _ in range(n):
                    self.counter += 1
                    fh.write(f"{rel}:{who[0]}:{self.counter}\n".encode())
        env = os.environ.copy()
        env.update(GIT_AUTHOR_NAME=who[0], GIT_AUTHOR_EMAIL=who[1], GIT_AUTHOR_DATE=date,
                   GIT_COMMITTER_NAME=who[0], GIT_COMMITTER_EMAIL=who[1], GIT_COMMITTER_DATE=date)
        git(self.path, "add", "-A", env=env)
        git(self.path, "commit", "-q", "-m", message, env=env)


def build_demo(path: str) -> str:
    r = Repo(path)
    r.commit(ALICE, "2026-01-05T10:00:00+0000", "feat: initial core",
             {"app/core.py": 10, "app/util.py": 4, "README.md": 2})
    r.commit(BOB, "2026-01-12T10:00:00+0000", "fix: edge case (#1)",
             {"app/core.py": 5, "app/util.py": 2})
    r.commit(ALICE, "2026-01-19T10:00:00+0000", "feat(api): routes (#2)",
             {"app/core.py": 3, "api/routes.py": 6})
    git(path, "tag", "v0.1")
    r.commit(CAROL, "2026-02-02T10:00:00+0000", "docs: explain routes", {"api/routes.py": 4})
    r.commit(BOB, "2026-02-09T10:00:00+0000", "refactor: tidy",
             {"app/core.py": 2, "app/util.py": 1})
    mass = {f"vendor/f{i:02d}.txt": 1 for i in range(12)}
    mass["app/core.py"] = 1
    r.commit(CAROL, "2026-02-16T10:00:00+0000", "style: reformat everything", mass)
    return path
