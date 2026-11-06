# Break It: Module 06

## Challenge 1: Count merges as changes

Remove the `if c.is_merge:` branch in `release_notes`. What does the merge commit's subject
end up doing in the output?

## Challenge 2: Hostile subjects

Make a commit whose subject is `feat: ` followed by 5,000 `(`. Does `parse_subject`
return quickly? Why is a short, anchored regex safer here than a clever one?

## Challenge 3: Squash vs merge

A repository that always squash-merges has no merge commits at all. Where do its PR
numbers come from, and which regex handles them?

## Challenge 4: Ranges that lie

Run `release_notes(repo, "main", "feat-x")` on a branch that has diverged. Explain
why `a..b` and `b..a` give different answers, and what `a...b` would give.
