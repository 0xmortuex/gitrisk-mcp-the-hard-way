"""Module 07: serve it over MCP, then test the server the way an agent would use it."""

import asyncio
import hashlib
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from demo_repo import build_demo  # noqa: E402
from mcp import ClientSession  # noqa: E402
from mcp.client.stdio import StdioServerParameters, stdio_client  # noqa: E402


def snapshot(path: str) -> str:
    """Hash every byte under the repo, .git included: proves the tools never wrote anything."""
    h = hashlib.sha256()
    for root, dirs, names in os.walk(path):
        dirs.sort()
        for n in sorted(names):
            full = os.path.join(root, n)
            h.update(os.path.relpath(full, path).encode())
            with open(full, "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()


async def run(repo: str, allowed: str, outside: str) -> None:
    params = StdioServerParameters(command=sys.executable, args=["-m", "minirisk.server",
                                                                 "--dir", allowed], cwd=ROOT)
    async with stdio_client(params) as (rd, wr), ClientSession(rd, wr) as s:
        await s.initialize()
        names = {t.name for t in (await s.list_tools()).tools}
        assert names == {"hotspots", "file_experts", "change_coupling", "release_notes"}, names

        before = snapshot(repo)
        res = await s.call_tool("hotspots", {"repo": repo, "limit": 3})
        text = res.content[0].text
        print(text)
        assert not res.is_error and text.splitlines()[2].startswith("| app/core.py |")

        res = await s.call_tool("file_experts", {"repo": repo, "path": "app/core.py"})
        assert "bus factor 1" in res.content[0].text and "Alice" in res.content[0].text
        res = await s.call_tool("change_coupling", {"repo": repo, "path": "app/core.py"})
        assert "app/util.py" in res.content[0].text
        res = await s.call_tool("release_notes", {"repo": repo})
        assert "## v0.1..HEAD" in res.content[0].text
        assert snapshot(repo) == before, "a tool modified the repository"

        # Errors must reach the agent as readable text, with something it can act on.
        res = await s.call_tool("file_experts", {"repo": repo, "path": "no/such/file.py"})
        assert res.is_error and "no history for 'no/such/file.py'" in res.content[0].text
        res = await s.call_tool("hotspots", {"repo": outside})
        assert res.is_error and "outside the allowed directories" in res.content[0].text
        print(res.content[0].text)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        allowed = os.path.join(tmp, "allowed")
        repo = build_demo(os.path.join(allowed, "demo"))
        outside = build_demo(os.path.join(tmp, "elsewhere", "other"))
        asyncio.run(run(repo, allowed, outside))
    print("module 07 ok")


if __name__ == "__main__":
    main()
