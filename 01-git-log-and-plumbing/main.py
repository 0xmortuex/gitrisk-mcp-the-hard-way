"""Module 01: read a repository's history through git's plumbing, safely."""

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from demo_repo import build_demo  # noqa: E402

from minirisk.gitio import GitError, commits, git, is_shallow  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo = build_demo(os.path.join(tmp, "demo"))

        log = commits(repo)
        for c in log:
            print(c.sha[:7], c.author, c.subject)
        assert len(log) == 6
        assert [c.author for c in log] == ["Carol", "Bob", "Carol", "Alice", "Bob", "Alice"]
        assert log[-1].subject == "feat: initial core" and log[-1].parents == ()  # the root commit
        assert not any(c.is_merge for c in log)

        # Plumbing answers a question directly instead of parsing prose:
        assert git(repo, "rev-list", "--count", "HEAD").decode().strip() == "6"
        assert git(repo, "rev-parse", "--is-bare-repository").decode().strip() == "false"
        assert not is_shallow(repo)

        # A subject that contains our separators' look-alikes still parses, because the
        # separators are control characters nobody types into a commit message.
        assert all("\x1f" not in c.subject for c in log)

        # Refs are user input. A ref that starts with "-" would become a git OPTION.
        try:
            commits(repo, "--output=/tmp/pwned")
        except GitError as e:
            print("refused:", e)
        else:
            raise AssertionError("an option-looking ref must be rejected")

        # A failing git command raises with git's own message, never returns silently.
        try:
            commits(repo, "no-such-branch")
        except GitError as e:
            assert "no-such-branch" in str(e) or "unknown revision" in str(e)
        else:
            raise AssertionError("an unknown ref must raise")
    print("module 01 ok")


if __name__ == "__main__":
    main()
