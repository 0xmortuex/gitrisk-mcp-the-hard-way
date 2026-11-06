"""Module 02: per-file changes with numstat, surviving lines with blame."""

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from demo_repo import ALICE, BOB, Repo, build_demo, git  # noqa: E402

from minirisk.history import (  # noqa: E402
    blame_counts,
    identities,
    parse_numstat,
    stream_commits,
)


def main() -> None:
    # 1. The parser, on hand-written bytes: ordinary, binary and renamed files.
    raw = b"\n3\t1\tsrc/a.py\x00-\t-\tlogo.png\x002\t0\t\x00old/b.py\x00new/b.py\x00"
    files = parse_numstat(raw)
    assert [(f.path, f.added, f.deleted, f.binary, f.old_path) for f in files] == [
        ("src/a.py", 3, 1, False, None),
        ("logo.png", 0, 0, True, None),
        ("new/b.py", 2, 0, False, "old/b.py"),
    ]

    with tempfile.TemporaryDirectory() as tmp:
        repo = build_demo(os.path.join(tmp, "demo"))

        # 2. Streaming numstat over the demo history.
        log = list(stream_commits(repo))
        assert len(log) == 6
        newest = log[0]
        assert newest.subject == "style: reformat everything" and len(newest.files) == 13
        core = sum(f.added for c in log for f in c.files if f.path == "app/core.py")
        assert core == 21  # 10 + 5 + 3 + 2 + 1
        # Stopping early must not leave git running or raise:
        first = next(iter(stream_commits(repo)))
        assert first.sha == newest.sha

        # 3. Blame: who owns the surviving lines of app/core.py?
        counts = blame_counts(repo, "HEAD", "app/core.py")
        ident = identities(repo, list(counts))
        by_author: dict[str, int] = {}
        for sha, n in counts.items():
            name = ident[sha][0]
            by_author[name] = by_author.get(name, 0) + n
        print(by_author)
        assert by_author == {"Alice": 13, "Bob": 7, "Carol": 1}

        # 4. Renames and binary files in a real repository.
        r = Repo(os.path.join(tmp, "ren"))
        r.commit(ALICE, "2026-01-01T10:00:00+0000", "add", {"old/name.py": 20})
        os.makedirs(os.path.join(r.path, "new"))
        git(r.path, "mv", "old/name.py", "new/name.py")
        with open(os.path.join(r.path, "logo.png"), "wb") as fh:
            fh.write(b"\x89PNG\x00\x01\x02" * 40)
        r.commit(BOB, "2026-01-02T10:00:00+0000", "move + add logo", {"new/name.py": 1})
        move = next(iter(stream_commits(r.path)))
        by_path = {f.path: f for f in move.files}
        assert by_path["new/name.py"].old_path == "old/name.py" and by_path["new/name.py"].added == 1
        assert by_path["logo.png"].binary and by_path["logo.png"].added == 0
    print("module 02 ok")


if __name__ == "__main__":
    main()
