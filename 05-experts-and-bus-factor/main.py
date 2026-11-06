"""Module 05: blame share + recent activity, and the bus factor."""

import os
import sys
import tempfile
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from demo_repo import AS_OF, build_demo  # noqa: E402

from minirisk.ownership import bus_factor, experts  # noqa: E402

NOW = datetime.fromisoformat(AS_OF).replace(tzinfo=timezone.utc).timestamp()


def main() -> None:
    # The bus factor is the fewest people holding MORE than half.
    assert bus_factor([6, 4]) == 1
    assert bus_factor([5, 5]) == 2          # exactly half is not more than half
    assert bus_factor([1, 1, 1]) == 2
    assert bus_factor([3, 3, 2, 2]) == 2
    assert bus_factor([1, 1, 1, 1]) == 3

    with tempfile.TemporaryDirectory() as tmp:
        repo = build_demo(os.path.join(tmp, "demo"))

        # Surviving lines of app/core.py: Alice 13, Bob 7, Carol 1 (of 21).
        # In the last 30 days (since 2026-01-30) Bob changed 2 lines and Carol 1.
        res = experts(repo, "app/core.py", NOW, recent_days=30)
        rows = {r["name"]: r for r in res["rows"]}
        for r in res["rows"]:
            print(r)
        assert rows["Alice"]["blame_share"] == 13 / 21
        assert rows["Bob"]["recent_share"] == 2 / 3 and rows["Alice"]["recent_share"] == 0
        assert abs(rows["Alice"]["score"] - 0.6 * 13 / 21) < 1e-12
        assert abs(rows["Bob"]["score"] - (0.6 * 7 / 21 + 0.4 * 2 / 3)) < 1e-12
        # Recent work moved the ranking: Alice owns the most lines but Bob is the one to ask.
        assert [r["name"] for r in res["rows"]] == ["Bob", "Alice", "Carol"]
        assert res["bus_factor"] == 1            # Alice alone holds 61.9%

        # A directory is just every file under it.
        res = experts(repo, "app", NOW, recent_days=30)
        assert sum(r["lines"] for r in res["rows"]) == 21 + 7   # core.py + util.py
    print("module 05 ok")


if __name__ == "__main__":
    main()
