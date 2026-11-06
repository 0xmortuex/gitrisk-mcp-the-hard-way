"""Module 06: conventional commits, PR numbers and merge commits."""

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from demo_repo import CAROL, Repo, build_demo, git  # noqa: E402

from minirisk.notes import latest_tag, parse_subject, release_notes  # noqa: E402


def main() -> None:
    p = parse_subject("feat(api)!: add x (#12)")
    assert p == {"type": "feat", "scope": "api", "breaking": True, "desc": "add x (#12)", "pr": 12}
    p = parse_subject("update the readme a bit")
    assert p["type"] is None and p["pr"] is None and p["desc"] == "update the readme a bit"
    assert parse_subject("wip: thing")["type"] is None   # not a known type: 'Other changes'
    assert parse_subject("fix: handle (#3) in the middle")["pr"] is None  # only a trailing (#n)

    with tempfile.TemporaryDirectory() as tmp:
        repo = build_demo(os.path.join(tmp, "demo"))
        assert latest_tag(repo) == "v0.1"
        text = release_notes(repo, "v0.1")
        print(text)
        # v0.1 is the third commit; three commits follow it.
        assert text.startswith("## v0.1..HEAD\n\n3 commits\n")
        assert text.index("### Refactoring") < text.index("### Documentation") < text.index("### Style")
        assert "- explain routes (" in text and "- tidy (" in text
        assert "### Features" not in text   # both features are in v0.1 already

        # Merge commits: a real branch, merged with GitHub's message format.
        git(repo, "checkout", "-q", "-b", "feat-x")
        r = Repo.existing(repo)
        r.commit(CAROL, "2026-02-20T10:00:00+0000", "feat(api): add x endpoint", {"api/x.py": 3})
        git(repo, "checkout", "-q", "main")
        env = os.environ.copy()
        env.update(GIT_COMMITTER_NAME="Carol", GIT_COMMITTER_EMAIL="carol@example.com",
                   GIT_AUTHOR_NAME="Carol", GIT_AUTHOR_EMAIL="carol@example.com",
                   GIT_AUTHOR_DATE="2026-02-21T10:00:00+0000",
                   GIT_COMMITTER_DATE="2026-02-21T10:00:00+0000")
        git(repo, "merge", "--no-ff", "-q", "feat-x", "-m", "Merge pull request #7 from carol/feat-x",
            env=env)
        text = release_notes(repo, "v0.1")
        assert "### Features\n- **api:** add x endpoint (" in text
        assert "### Merged pull requests\n- #7 (carol/feat-x)" in text
        assert "5 commits" in text  # 3 + the feature commit + the merge
    print("module 06 ok")


if __name__ == "__main__":
    main()
