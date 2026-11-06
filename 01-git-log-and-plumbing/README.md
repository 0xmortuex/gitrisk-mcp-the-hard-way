# Module 01: git log formats and plumbing

## The concept

Everything in this project rests on one move: run `git`, read its output, and turn it into
numbers. Two decisions here save you from nearly every bug later.

### Decision 1: argument lists, never shell strings

```python
cmd = ["git", "-c", "core.quotepath=off", "-C", repo, *args]
subprocess.run(cmd, capture_output=True, env=clean_env(), check=False)
```

A list goes straight to the operating system with no shell in between, so a branch called
`main; rm -rf ~` is just a strange name. Your server will receive refs and paths from an
AI agent that got them from a user that got them from a web page. Treat them as hostile.

Lists do not fully solve it: git itself parses `--output=/tmp/x` as an option. So refs get
one extra check (`commits()` rejects anything starting with `-`), and the real server
resolves a ref to a commit id before using it.

### Decision 2: a read-only environment

`clean_env()` drops inherited `GIT_*` variables (a stray `GIT_DIR` would silently point
your analysis at a different repository) and sets:

- `GIT_OPTIONAL_LOCKS=0`: many git commands opportunistically refresh `.git/index`. An
  analytics tool must not write, even a cache. This turns that off.
- `GIT_LITERAL_PATHSPECS=1`: a path like `src/*.py` means that exact name, not a glob.

### Parsing the log: pick separators that cannot occur

Commit subjects contain commas, tabs, pipes, quotes. They cannot contain ASCII 0x1f (unit
separator) or 0x1e (record separator) in practice, so:

```
--format=%x1e%H%x1f%at%x1f%aN%x1f%aE%x1f%P%x1f%s
```

`%x1e` starts each record, `%x1f` separates fields. Splitting is then two `split()` calls
with no escaping rules. Three field choices matter:

- `%aN` / `%aE` (capital N and E) apply `.mailmap`. If Bob committed as `Bobby` once, the
  mailmap folds him back into one person. `%an` / `%ae` would not.
- `%at` is the author timestamp as unix seconds: no time zone parsing, ever.
- `%P` gives parent shas. More than one parent means a merge commit, which we will need to
  treat differently (it has no diff of its own).

## Run it

```
python 01-git-log-and-plumbing/main.py
```

It builds the demo repository, prints the six commits, and asserts the author order, the
root commit, `rev-list --count`, that an option-looking ref is refused, and that an unknown
ref raises.

## What to notice

- `git rev-list --count HEAD` and `rev-parse --is-shallow-repository` are *plumbing*:
  commands designed to be parsed. Prefer them to scraping `git status`-style prose.
- A failing command raises `GitError` with git's own message. Never return an empty result
  on failure: "no hotspots" and "git crashed" must look different to the agent.
