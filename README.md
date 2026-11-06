# MCP Server: Git Risk Analytics, The Hard Way

Build an MCP server that answers the questions a new teammate asks about a codebase:
*which files are the riskiest, who actually knows them, which files secretly change
together, and what would we lose if one person left?* Start from `git log` bytes and end
with an agent calling your tools over MCP.

At the end you will have built a small version of
[gitrisk-mcp](https://github.com/0xmortuex/gitrisk-mcp) yourself, and you will understand
the parts that tutorials about "wrap an API in a tool" skip: **parsing a tool's output
without being fooled by it, scoring with defensible maths, and proving that a read-only
server really is read-only.**

## Why this exists

Generic git MCP servers expose `status`, `diff` and `commit`. Those answer "what is
happening now". Almost every hard question about an old codebase is about **history**:

- *Where do bugs live?* Files that change a lot, recently, by many hands.
- *Who should review this?* Not the person with the most commits (they may have run a
  formatter) but whoever's lines **survive** in the file today.
- *What breaks when I touch this?* Files that always change in the same commit.
- *What if Dana leaves?* Directories where one person holds most of the knowledge.

None of that is hard maths. The hard part is the data: renames, merge commits, reformat
commits that touch 4,000 files, binary files, `.mailmap`, shallow clones. Each module
adds one piece and a `main.py` that **builds a real git repository with scripted commits
and asserts exact numbers**.

## Modules

| # | Module | You build | Key idea |
|---|---|---|---|
| 01 | [git log formats and plumbing](01-git-log-and-plumbing) | `gitio.py` | Argument lists, control-character separators, refs are untrusted input |
| 02 | [numstat and blame parsing](02-numstat-and-blame) | `history.py` | `-z` output, streaming, renames, binary files, `--line-porcelain` |
| 03 | [hotspot scoring](03-hotspot-scoring) | `hotspots.py` | Churn x exponential recency decay x author breadth; mass commits |
| 04 | [change coupling](04-change-coupling) | `coupling.py` | Support, confidence, reverse confidence |
| 05 | [experts and bus factor](05-experts-and-bus-factor) | `ownership.py` | Surviving lines vs recent work; "more than half" |
| 06 | [release notes](06-release-notes) | `notes.py` | Conventional commits, PR numbers, merge commits |
| 07 | [the MCP server](07-the-mcp-server) | `server.py` | Tool design, errors, `--dir` sandbox, proving read-only |

## Run it

You need Python 3.10+ and `git` on your PATH. Nothing else is installed globally.

```
python -m venv .venv
.venv/Scripts/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python verify.py              # builds a real repo per module and checks every number
python verify.py 03 05        # just some modules
```

Or run one module on its own: `python 03-hotspot-scoring/main.py`.

## The demo repository

Every module analyses the same six-commit history built by [`demo_repo.py`](demo_repo.py)
with explicit authors and dates, so all numbers can be checked with a pencil:

```
c1 alice 2026-01-05  feat: initial core           app/core.py +10  app/util.py +4  README.md +2
c2 bob   2026-01-12  fix: edge case (#1)          app/core.py +5   app/util.py +2
c3 alice 2026-01-19  feat(api): routes (#2)       app/core.py +3   api/routes.py +6    <- tag v0.1
c4 carol 2026-02-02  docs: explain routes         api/routes.py +4
c5 bob   2026-02-09  refactor: tidy               app/core.py +2   app/util.py +1
c6 carol 2026-02-16  style: reformat everything   vendor/f00..f11.txt +1 each, app/core.py +1
```

`c6` is the villain: a mass "reformat" commit that touches 13 files and would wreck every
statistic if we let it.

## How each module works

1. **The concept**, with the reason behind each design choice.
2. **The code**: small enough to read in one sitting, all of it in `minirisk/`.
3. **`main.py`**: runs the code against a real repository and checks the results with `assert`.
4. **`break-it.md`**: experiments that make the code fail on purpose, so you see why each guard exists.

## License

MIT.
