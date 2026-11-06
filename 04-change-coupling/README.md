# Module 04: change coupling

## The concept

Some files are bound together by nothing in the code. A schema and the migration that
creates it. A route table and its documentation. A config key and the three services that
read it. No import links them, yet every change to one is followed by a change to the
other. History reveals those hidden dependencies, and they predict "I changed A and
forgot B" bugs.

### Support and confidence

Treat each commit as a basket of files, like a shopping basket. For a target file `T` and
another file `X`:

```
support(X)    = number of commits that touch both T and X
confidence(X) = support / commits touching T          P(X changes | T changes)
reverse(X)    = support / commits touching X          P(T changes | X changes)
```

In the demo, `app/util.py` changed alongside `app/core.py` in commits 1, 2 and 5, and
`core.py` changed in 4 usable commits:

- support = 3, confidence = 3/4: three quarters of the time you edit core, util moves too.
- reverse = 3/3 = 1.0: util never changes without core. That asymmetry is informative:
  util looks like a helper that serves core.

Two numbers because they mean different things. A file that appears in *every* commit (a
changelog) has high reverse confidence with everything and says nothing.
`confidence` tells you what to check after editing `T`; `reverse` tells you whether `X`
really belongs to `T`.

### Why `min_support`

A single shared commit proves nothing: `api/routes.py` shares commit 3 with core
(confidence 1/4). With `min_support=2` it disappears. Raise it on bigger repositories.

### Mass commits poison coupling

The reformat commit touches `app/core.py` and 12 vendor files. If counted, core would be
"coupled" to every vendor file (confidence 1/5 each) and the real signal would sink under
noise. So commits with more than `max_files_per_commit` files are skipped, *and the
denominator excludes them*: `n_target` counts only usable commits, which is why
the result for core says 4 commits when it was touched 5 times.

### Renames, again

`RenameMap` from Module 03 is reused: a pair that changed together under old names still
counts for the new names. Counting `totals` after `resolve()` is what makes the reverse
number correct.

## Run it

```
python 04-change-coupling/main.py
```

It asserts support 3, confidence 0.75 and reverse 1.0 for `app/util.py`, that `min_support=2`
leaves only that one file, and that without the mass-commit filter 12 vendor files show up
at confidence 1/5.
