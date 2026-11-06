# Break It: Module 04

## Challenge 1: Everything couples to the changelog

Add a `CHANGELOG.md` that every commit appends to. Run `coupling()` for `app/core.py`.
What are its confidence and reverse values? Which one tells you the file is not really
coupled?

## Challenge 2: Count the denominator wrongly

Make `n_target` count mass commits too (move the `+= 1` above the size check).
How does the confidence of `app/util.py` change, and is the new number still the probability
you meant?

## Challenge 3: Symmetry

Run `coupling(repo, "app/util.py")` and compare with `coupling(repo, "app/core.py")`.
The support for the pair is the same. Explain why the confidences differ.
