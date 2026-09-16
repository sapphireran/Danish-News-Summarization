# Workbook key

`python3 -m kystlinje quiz` prints ten questions. Answers are derived
from the live ledger, so they stay correct if a planted scar moves.
`python3 -m kystlinje quiz --answers` prints the key. `--grade N TEXT`
checks one attempt.

The questions are:

1. Which directed hop loses the most source entities on average?
2. Which brief has the worst source→silver survival?
3. Which brief plants the 1904→1914 year shift?
4. Which brief plants the 23:40→23:30 time shift?
5. Which brief flattens `Lærke` to `Larke`?
6. How many briefs are in the corpus?
7. How many character-budget windows does the longest brief produce at 80?
8. On this fiction set, does lead-2 or silver keep more source entities?
9. What is the source CSV column for the Danish body?
10. `finetune.py` saves `./large_model`. What does `eval.py` load?

Question 8 is the methodological sting. Lead-2 cannot mutate a year. It
also cannot see sentence five. Silver can do both. On a magazine brief
that front-loads names, lead-2 often *looks* stronger on entity recall.
That is not an argument against abstractive models. It is an argument
for measuring them on facts, not only on n-grams.

## Suggested reading order

```
python3 -m kystlinje show kz-07
python3 -m kystlinje ledger --id kz-07
python3 -m kystlinje show kz-08
python3 -m kystlinje align kz-08
python3 -m kystlinje show kz-05
python3 -m kystlinje ledger --id kz-05
python3 -m kystlinje quiz
```

Then open `examples/report/index.html` and jump to those three ids.
