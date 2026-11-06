"""Module 04: support, confidence and why mass commits must be ignored."""

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from demo_repo import build_demo  # noqa: E402

from minirisk.coupling import coupling  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo = build_demo(os.path.join(tmp, "demo"))

        # Mass commit ignored (13 files > 10): app/core.py was touched by 4 other commits.
        res = coupling(repo, "app/core.py", max_files_per_commit=10, min_support=1)
        by = {r["path"]: r for r in res["rows"]}
        print(res["commits"], by["app/util.py"])
        assert res["commits"] == 4
        # util.py changed with core.py in commits 1, 2 and 5 -> support 3, confidence 3/4,
        # and util.py never changed without core.py (3 of its 3 commits) -> reverse 1.0
        assert by["app/util.py"]["support"] == 3
        assert by["app/util.py"]["confidence"] == 3 / 4
        assert by["app/util.py"]["reverse"] == 1.0
        # routes.py shares only commit 3 with core.py
        assert by["api/routes.py"]["support"] == 1
        assert by["api/routes.py"]["confidence"] == 1 / 4
        assert by["api/routes.py"]["reverse"] == 1 / 2  # routes.py has 2 commits, 1 with core.py

        # min_support removes accidental pairs:
        strict = coupling(repo, "app/core.py", max_files_per_commit=10, min_support=2)
        assert [r["path"] for r in strict["rows"]] == ["app/util.py"]

        # Without the filter the reformat commit makes core.py look coupled to 12 vendor files.
        noisy = coupling(repo, "app/core.py", max_files_per_commit=100, min_support=1)
        vendor = [r for r in noisy["rows"] if r["path"].startswith("vendor/")]
        assert noisy["commits"] == 5 and len(vendor) == 12
        assert all(r["confidence"] == 1 / 5 for r in vendor)
    print("module 04 ok")


if __name__ == "__main__":
    main()
