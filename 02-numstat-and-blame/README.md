# Module 02: numstat and blame parsing

## The concept

Module 01 told us who committed and when. Risk analysis needs to know *which files* and
*how many lines*. Git has two commands for that, and they answer different questions.

| Command | Question | Cost |
|---|---|---|
| `git log --numstat` | How many lines did each commit add and delete, per file? | One pass over history |
| `git blame` | Which commit does each line that exists **today** come from? | One pass per file |

### numstat, parsed safely with `-z`

Plain `--numstat` prints `3	1	src/a.py`, and shows renames as `src/{old => new}/a.py`, a
format that is miserable to parse and quotes unusual file names. With `-z`, git switches to
NUL separators and prints exact bytes:

```
3\t1\tsrc/a.py\0
-\t-\tlogo.png\0                      <- binary file: dashes instead of numbers
2\t0\t\0old/b.py\0new/b.py\0          <- rename: empty path, then old, then new
```

`parse_numstat()` walks the NUL-separated tokens with an index, because a rename consumes
three tokens and a normal change consumes one. `main.py` tests it on those exact bytes.

Two details that bite later:

- **Binary files** have no line counts. We store `0/0` and set `binary=True`, so the
  scoring module can decide what to do (the real server counts a binary change as one line).
- **Paths are bytes.** A file may be named in Latin-1. We decode with `backslashreplace`,
  so it shows as `caf\xe9.txt`: visible, unique, never a crash.

### Streaming

`stream_commits()` does not call `git log` and wait. It starts git with a pipe and yields
each commit as soon as its bytes arrive:

```python
while chunk := proc.stdout.read1(1 << 16):
    buf += chunk
    *done, buf = buf.split(b"\x1e")      # complete records, plus an unfinished tail
```

On a repository with 200,000 commits this runs in constant memory and lets the caller
stop after the first 5,000. The `finally` block kills git if the caller walked away
early; otherwise the abandoned process would keep running.

### blame: surviving lines

`git blame --line-porcelain` repeats full commit information for every line. We only want
the sha at the start of each header line, and the file's own text (prefixed by a TAB) must
never be parsed, because a source line can contain anything, including something that
looks like a sha:

```python
if line[:1] == b"\t":        # the file's own content
    continue
```

Flags: `-w` ignores whitespace changes, so re-indenting a file does not hand it to whoever
did that, and `-M` follows lines moved inside the file.

`identities()` then maps the (few) distinct shas to names, with the mailmap applied, in a
**single** `git log --no-walk --stdin` call, rather than one process per line.

## Run it

```
python 02-numstat-and-blame/main.py
```

It checks the parser on literal bytes, streams the demo history (the reformat commit has
13 files), proves that stopping early works, and blames `app/core.py`:
`{'Alice': 13, 'Bob': 7, 'Carol': 1}`. A second repository tests a real rename and a
real binary file.
