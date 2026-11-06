# Module 07: the MCP server and how to test it

## The concept

Modules 01-06 are a library. This module turns it into a server an agent can call, and
spends most of its effort on three things a library does not need: **tool design**,
**error design**, and **proof that it is read-only**.

### MCP in one paragraph

A local MCP server is a program that speaks JSON-RPC over stdin/stdout. The client (Claude
Code, Claude Desktop) starts it as a subprocess, asks which tools exist, and calls them.
The SDK does the protocol; you write functions. Two consequences: **never `print()` to
stdout** (it is the protocol channel), and a tool's docstring *is* its manual, since the
model reads it to decide when to call the tool.

### Tool design

`server.py` exposes four tools: `hotspots`, `file_experts`, `change_coupling`,
`release_notes`. Each takes one optional `repo=` and returns a compact markdown table. Few tools
with clear names beat many tiny ones, and a table is cheaper for a model to read than raw
JSON. Defaults are chosen so a bare call works.

### Errors the agent can read

With mcp 2.x, a client only sees an exception's text if it is a `ToolError`; anything else
becomes a bare "Error executing tool". The wrapper converts *expected* failures:

```python
try:
    return fn(*args, **kwargs)
except GitError as e:
    raise ToolError(str(e)) from e
```

and deliberately leaves genuine bugs alone, so they are not disguised as user mistakes. A
good message says what to do next: `no history for 'x'; paths are relative to the repository root`.

### The sandbox

An agent that can read any repository on your disk can read your private ones. The server
takes `--dir` (repeatable). `open_repo()` asks git for the repository's real top level
and checks **that** against the allowed roots, not only the folder the caller named.
Why? A folder inside an allowed root may belong to a repository that lives *outside* it,
and its entire history would leak. Paths go through `realpath` and `normcase` first so
symlinks and Windows letter-case cannot sidestep the check.

### Proving it is read-only

The test hashes every byte under the repository, `.git` included, calls all four tools,
and hashes again:

```python
before = snapshot(repo)
... call every tool ...
assert snapshot(repo) == before, "a tool modified the repository"
```

A test like this is only as strong as the commands it exercises. `GIT_OPTIONAL_LOCKS=0` from
Module 01 is the safety net for the git commands that like to refresh `.git/index` behind
your back; the snapshot is what would notice if one ever slipped through.

### Testing like an agent

`main.py` launches the real server in a subprocess and talks to it through the MCP client:
it lists tools, calls them, reads the failure messages, and checks that an outside
repository is refused. That finds problems unit tests cannot (a stray `print`, a tool that
isn't registered, a message that never reaches the client).

## Run it

```
python 07-the-mcp-server/main.py
```

To use the server by hand with Claude Code:

```
claude mcp add minirisk -- python -m minirisk.server --dir /path/to/your/repos
```

(run from this tutorial's directory, or use absolute paths).

## Where to go next

The full [gitrisk-mcp](https://github.com/0xmortuex/gitrisk-mcp) adds: a streaming reader
with timeouts and `max_commits` limits, shallow-clone detection, bare repositories,
non-UTF-8 path names, weekly/monthly churn timelines, commit search, rename-following file
history, and a test suite that builds repositories with scripted histories and also runs a
generated 20,000-commit repository.
