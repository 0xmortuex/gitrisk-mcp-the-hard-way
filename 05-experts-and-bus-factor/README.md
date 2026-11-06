# Module 05: experts and the bus factor

## The concept

"Who should review this?" and "what happens if she leaves?" are the same question seen from
two sides: how is knowledge of this code distributed?

### Why not just count commits?

Count commits and Carol wins `app/core.py` because she once ran a formatter. Count lines
added and whoever pasted a big generated file wins. What we want is **who wrote the code
that is still here**. `git blame` answers that exactly, and that is the first half of
the score:

```
blame_share(a)  = a's surviving lines / all surviving lines
```

For `app/core.py`: Alice 13, Bob 7, Carol 1 of 21.

### But people move on

Alice wrote the most, but the last three months of work were all Bob's. He remembers
the current shape of the code; she may not. So the second half is recent activity:

```
recent_share(a) = lines a changed in the last N days / all lines changed in that window
score(a)        = 0.6 * blame_share + 0.4 * recent_share
```

If nobody touched the path recently the recent term has no data, so the score falls back
to `blame_share` alone rather than dividing by zero.

The weights (0.6/0.4) are a judgement call; they are constants at the top of the formula
so you can argue with them. In the demo, with a 30-day window, the ranking is
**Bob (0.467), Alice (0.371), Carol (0.162)**: Alice owns most lines but Bob is the person
to ask.

### Bus factor: "more than half"

The bus factor is the smallest number of people who together hold more than 50% of the
knowledge, so losing them would lose most of it.

```python
def bus_factor(weights):
    total, cum = sum(weights), 0.0
    for k, w in enumerate(sorted(weights, reverse=True), 1):
        cum += w
        if cum * 2 > total:      # strictly more than half
            return k
```

The comparison is strict on purpose. `[5, 5]` is a 50/50 split: neither person alone
holds most of it, so the answer is 2. With `>=` it would claim 1 for a perfectly shared
file, the opposite of the truth. `[6, 4]` is 1; Alice's 13 of 21 (61.9%) is 1 too.

A directory is analysed by blaming every file under it and adding the counts, with
`ls-tree -r` to list the files at `HEAD` (never the working tree: uncommitted edits are not
"knowledge" yet).

## Run it

```
python 05-experts-and-bus-factor/main.py
```

It checks the `bus_factor` edge cases, then the exact shares, the recency-shifted ranking
and that the directory total is 28 lines.
