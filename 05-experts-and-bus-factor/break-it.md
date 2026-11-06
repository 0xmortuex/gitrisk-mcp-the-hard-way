# Break It: Module 05

## Challenge 1: Rank by commit count

Replace `blame_share` with each author's commit count share. Who is the "expert" on
`app/core.py` now, and what did the reformat commit have to do with it?

## Challenge 2: Use `>=`

Change `cum * 2 > total` to `cum * 2 >= total` and run `bus_factor([5, 5])`.
Explain in one sentence why the new answer is dangerous.

## Challenge 3: Whitespace

Re-indent `app/core.py` in a new commit by Carol, then run `experts` with the blame
flags `-w` removed. Who owns the file? Put `-w` back.

## Challenge 4: The departed

Using only the data in `experts()`, add a field that marks an author as inactive when their
latest surviving commit is older than a year. What share of the code would then be owned by
inactive people? (The real server reports exactly this.)
