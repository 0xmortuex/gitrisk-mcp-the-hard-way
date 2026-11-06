# Break It: Module 07

## Challenge 1: Print to stdout

Add `print("opening", repo)` at the top of `open_repo` and run `main.py`. What does the
client do? Change it to `print(..., file=sys.stderr)`.

## Challenge 2: Check the folder, not the repository

In `open_repo`, delete the check on `top` and keep only the check on `path`. Then create
`outer/` as a git repository, run the server with `--dir outer/sub`, and call `hotspots`
with `repo=outer/sub`. What did the sandbox just allow?

## Challenge 3: Let a bug through as a ToolError

Change the wrapper to `except Exception as e: raise ToolError(str(e))`. Introduce a typo in
`fmt()`. What does the agent see now, and why is that worse than a generic failure?

## Challenge 4: Prove the proof

Temporarily add `git(repo, "update-index", "--refresh")` to `hotspots` and run
`main.py`. Does the read-only assertion catch it? (If your working tree is clean it may
not. Touch a file's mtime first, and think about what that says about how strong the test is.)
