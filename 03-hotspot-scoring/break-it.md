# Break It: Module 03

## Challenge 1: Let the reformat in

Run `hotspots(repo, NOW, half_life_days=0, max_files_per_commit=1000)` and print the top 15.
Which files appear that should not? Which author now looks like a co-owner of everything?

## Challenge 2: Learn renames too late

In `hotspots()` move `rn.learn(c.files)` below the `continue` for mass commits, then
test with a repository where a directory is moved in a 200-file commit. What happens to the
history of the moved files?

## Challenge 3: Pick your own weights

Replace `1 + log2(n)` with plain `n`. Make a file with 10 authors and 1 line each, and
another with 1 author and 12 lines. Which ranks higher under each formula? Which one
matches your intuition about risk?

## Challenge 4: Time is a parameter

Run the same call with `half_life_days` of 7, 90 and 3650. Describe, in a sentence each,
what question each setting answers ("what is on fire this week", "what is
risky this quarter", "what is big historically").
