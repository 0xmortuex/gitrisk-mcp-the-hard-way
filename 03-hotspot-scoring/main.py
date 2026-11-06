"""Module 03: churn x recency x authors, with mass-commit filtering and rename following."""

import math
import os
import sys
import tempfile
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from demo_repo import ALICE, AS_OF, BOB, CAROL, Repo, build_demo, git  # noqa: E402

from minirisk.hotspots import decay, hotspots  # noqa: E402

NOW = datetime.fromisoformat(AS_OF).replace(tzinfo=timezone.utc).timestamp()


def main() -> None:
    assert decay(0, 90) == 1.0 and decay(90, 90) == 0.5 and decay(180, 90) == 0.25
    assert decay(10, 0) == 1.0  # half_life 0 switches decay off

    with tempfile.TemporaryDirectory() as tmp:
        repo = build_demo(os.path.join(tmp, "demo"))

        # No decay, mass commit (13 files) skipped by a threshold of 10:
        rows = hotspots(repo, NOW, half_life_days=0, max_files_per_commit=10)
        by = {r["path"]: r for r in rows}
        for r in rows[:4]:
            print(r)
        assert [r["path"] for r in rows[:3]] == ["app/core.py", "api/routes.py", "app/util.py"]
        core = by["app/core.py"]
        assert (core["commits"], core["lines"], core["authors"]) == (4, 20, 2)
        assert core["score"] == 20 * (1 + math.log2(2))          # 40
        assert by["api/routes.py"]["score"] == 10 * 2            # Alice and Carol
        assert by["app/util.py"]["score"] == 7 * 2               # Alice and Bob
        assert not any(p.startswith("vendor/") for p in by)      # only touched by the mass commit

        # Keep the mass commit and Carol becomes a third author of core.py:
        rows = hotspots(repo, NOW, half_life_days=0, max_files_per_commit=100)
        core = {r["path"]: r for r in rows}["app/core.py"]
        assert (core["commits"], core["lines"], core["authors"]) == (5, 21, 3)
        assert abs(core["score"] - 21 * (1 + math.log2(3))) < 1e-9

        # Recency: with a 30-day half-life the newest commit (Feb 16) outweighs the oldest.
        rows = hotspots(repo, NOW, half_life_days=30, max_files_per_commit=10)
        core = {r["path"]: r for r in rows}["app/core.py"]
        expected = sum(
            n * decay((NOW - datetime.fromisoformat(d).timestamp()) / 86400, 30)
            for d, n in [("2026-01-05T10:00:00+00:00", 10), ("2026-01-12T10:00:00+00:00", 5),
                         ("2026-01-19T10:00:00+00:00", 3), ("2026-02-09T10:00:00+00:00", 2)]
        ) * 2
        assert abs(core["score"] - expected) < 1e-9, (core["score"], expected)

        # Renames: history under the old name counts for the new one.
        r = Repo(os.path.join(tmp, "ren"))
        r.commit(ALICE, "2026-01-01T10:00:00+0000", "add", {"old/name.py": 20})
        os.makedirs(os.path.join(r.path, "new"))
        git(r.path, "mv", "old/name.py", "new/name.py")
        r.commit(CAROL, "2026-01-02T10:00:00+0000", "move", {"new/name.py": 1})
        r.commit(BOB, "2026-01-03T10:00:00+0000", "tweak", {"new/name.py": 2})
        rows = hotspots(r.path, NOW, half_life_days=0)
        assert [x["path"] for x in rows] == ["new/name.py"]
        assert (rows[0]["commits"], rows[0]["lines"], rows[0]["authors"]) == (3, 23, 3)
    print("module 03 ok")


if __name__ == "__main__":
    main()
