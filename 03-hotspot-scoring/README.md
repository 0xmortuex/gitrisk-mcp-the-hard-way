# Module 03: hotspot scoring

## The concept

A *hotspot* is a file where trouble is likely: it changes a lot, it changed recently, and
many people change it. Each factor is a known predictor of defects, and each can be
fooled, so the score handles the fooling.

```
score(file) = sum over its commits of  lines(commit) * 0.5 ** (age_days / half_life)
              * (1 + log2(distinct authors))
```

### Churn: lines changed

`lines = added + deleted`. A one-line edit counts 2 (one line out, one in), a new
10-line file counts 10. A binary change counts as 1, since we cannot count its lines but
the change happened.

### Recency: exponential decay

A change 90 days old should matter half as much as one today, one 180 days old a quarter.
That is `0.5 ** (age / half_life)`. Compared with a hard "last 6 months" cutoff, decay has
no cliff: a commit does not suddenly stop counting at midnight. `half_life=0` switches
it off, which makes tests easy to reason about.

`main.py` uses a fixed `now` (`AS_OF` in `demo_repo.py`) instead of the real clock. If the
test used `time.time()`, the expected numbers would change every day.

### Authors: `1 + log2(n)`

One author gives x1, two give x2, four give x3, eight give x4. A file touched by many
people lacks a single owner, and coordination bugs live there. A logarithm stops a file
edited by 40 people from outscoring everything else by sheer headcount.

### Defences against noisy history

- **Mass commits.** `style: reformat everything` touched 13 files and 12 of them nothing
  else ever touched. Counting it would rank `vendor/f00.txt` as a hotspot. Commits with
  more than `max_files_per_commit` files are skipped.
- **Deleted files.** Churn on a file that no longer exists is not a risk to anyone. We rank
  only paths present at `HEAD` (`files_at()`).
- **Renames.** If `old/name.py` became `new/name.py`, its past belongs to the new name.
  git log walks newest-first, so we see the rename *before* the older commits that use
  the old name. `RenameMap` records `old -> new` as it goes, and `resolve()` translates.
  Note that `learn()` is called *before* the mass-commit `continue`, because a directory
  move is often itself a mass commit.

## Run it

```
python 03-hotspot-scoring/main.py
```

With decay off and the mass commit skipped (`max_files_per_commit=10`), `app/core.py` has
4 commits, 20 lines and 2 authors: `20 * (1 + log2 2) = 40`. Let the mass commit in and
Carol becomes a third author with 21 lines: `21 * (1 + log2 3)`. A second repository
checks that a renamed file keeps all 3 commits and 23 lines.
