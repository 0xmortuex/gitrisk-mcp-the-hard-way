# Module 06: release notes

## The concept

Release notes are the one output a human reads directly, so the output is markdown rather
than numbers. The input is a range of commits. The work is classifying them.

### Conventional commits

A convention that makes machines' lives easy:

```
type(scope)!: description (#PR)
feat(api)!: add x (#12)     ->  type=feat  scope=api  breaking=True  PR=12
```

`parse_subject()` is one regular expression. Details that matter:

- `type` is matched case-insensitively and must be a *known* type (`feat`, `fix`, `docs`...).
  `wip: thing` has the right shape but is not a type we know, so it falls to
  **Other changes** instead of inventing a heading called "Wip".
- The `!` marks a breaking change. (The full server also reads a `BREAKING CHANGE:` line
  in the body.)
- A PR number counts only as a **trailing** `(#n)`, the form GitHub's squash merge writes.
  `fix: handle (#3) in the middle` is prose, not a reference.
- Subjects that match nothing are kept whole. Real repositories are mostly messages like
  `update the readme a bit`, and dropping them would hide work.

### Order and grouping

The headings follow the `TITLES` dict, not the order commits happen to appear, so
Features always precede Bug fixes. Empty groups are omitted.

### Merge commits

A merge has two parents and no diff of its own; the commits it merged are *also* in the
range. Listing the merge among the changes would count that work twice. So merges go in
a separate section, and GitHub's `Merge pull request #7 from carol/feat-x` yields the PR
number and branch. `main.py` makes a real feature branch and a real `--no-ff` merge to
check this.

### Choosing the range

`from..to` means "reachable from `to` but not from `from`". `latest_tag()` uses
`git describe --tags --abbrev=0`, the nearest tag behind `HEAD`. In the demo that is
`v0.1`, the third commit, so exactly the last three commits are in range.

## Run it

```
python 06-release-notes/main.py
```

Expect (shas differ):

```
## v0.1..HEAD

3 commits

### Refactoring
- tidy (3c0e2fb)

### Documentation
- explain routes (f95807c)

### Style
- reformat everything (26e67f3)
```

Then the branch is merged and the run asserts a Features entry with scope `api`, and a
`Merged pull requests` entry `#7 (carol/feat-x)`.
