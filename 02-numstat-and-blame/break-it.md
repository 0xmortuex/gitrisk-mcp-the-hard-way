# Break It: Module 02

## Challenge 1: Forget `-z`

Remove `-z` from the `git log` arguments in `stream_commits` and run `main.py`. Which
assertion fails first, and why? Then create a file whose name contains a space and a
double quote and see what plain numstat prints for it.

## Challenge 2: Parse the file content

In `blame_counts`, remove the `if line[:1] == b"\t": continue` guard. Commit a file that
contains a line starting with 40 hex digits, a space and two numbers. What happens to the
counts?

**Hint:** blame prefixes real file content with a TAB precisely so you can tell it apart.

## Challenge 3: Whitespace ownership

Reformat a file (re-indent every line) in a new commit, then compare `blame_counts` with
and without `-w`. Who "owns" the file in each case? Which answer would you want from a tool
that tells you whom to ask about the logic?

## Challenge 4: Orphaned git

Call `next(iter(stream_commits(repo)))` in a loop 200 times and watch the process list.
Now delete the `finally` block and repeat.
