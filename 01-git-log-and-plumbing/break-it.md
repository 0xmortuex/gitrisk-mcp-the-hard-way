# Break It: Module 01

## Challenge 1: A hostile ref

Remove the `startswith("-")` check in `commits()` and call `commits(repo, "--output=pwned.txt")`.
Look for `pwned.txt` in the repository. Put the check back.

**Hint:** `git log --output=FILE` writes the log to a file. The list form of `subprocess`
stopped a shell injection, but git is a second interpreter with its own option syntax.

## Challenge 2: Let git refresh the index

In `clean_env()`, delete `GIT_OPTIONAL_LOCKS`. Hash `.git/` before and after a few `git log`
calls (module 07 has a `snapshot()` helper). On a real working tree whose files have been
touched, does anything change?

**Hint:** it depends on the git version and the repository, which is exactly why the guard
is unconditional.

## Challenge 3: The wrong name field

Change `%aN` to `%an` and add a `.mailmap` containing `Bob <bob@example.com> Bobby <bobby@old.example>`
plus a commit made as Bobby. How many authors does `commits()` report?
