# Metrics from scratch

`finetune.py` and `eval.py` call `datasets.load_metric("rouge")`. That helper
is deprecated, pulls a third-party scorer, and needs the 2023 stack. The lab
reimplements the three numbers the trainer actually logged: ROUGE-1, ROUGE-2,
and ROUGE-L, each as precision / recall / F-measure.

## Tokenization

1. Case-fold with `str.casefold` (keeps æ/ø/å).
2. Keep runs of letters and digits, including Danish vowels and a single
   internal apostrophe.
3. No Porter stemmer, no Danish lemmatizer, no sentence-break inside ROUGE.

Two strings that differ only by a definite suffix (`klit` vs `klitter`) will
not match. That is honest for a pedagogical scorer and harsh for Danish.

## ROUGE-N

Let *P* and *R* be the n-gram bags of the prediction and the reference.
Overlap is the sum of clipped counts (Lin 2004): `sum((Counter(P) & Counter(R)).values())`.

```
precision = overlap / |P|
recall    = overlap / |R|
F         = 2PR / (P+R)   (0 if P=R=0)
```

Unigrams use `n=1`, bigrams `n=2`. Empty prediction or reference scores 0.

## ROUGE-L

ROUGE-L here is the **sentence-level** LCS F-measure, not the summary-level
union of sentence LCSes that some official scripts use.

```
L = LCS_length(tokens(pred), tokens(ref))
precision = L / |pred|
recall    = L / |ref|
F         = 2PR / (P+R)
```

LCS is computed with a two-row DP table. The fiction summaries are short;
quadratic time is fine.

## What I refuse to compute

- A mid/low/high bootstrap. One brief is one brief.
- BERTScore. `eval.py` already documents the intended call
  (`lang='da'`, `xlm-roberta-large`). The lab will not download that model.
- A fake 2023 leaderboard. If I find the old printout I will add a dated
  note. Until then the only published numbers in this branch are the
  fiction-corpus tables from `python3 -m silverlab metrics`.

## Worked numeric example

Prediction: `katten sidder`  
Reference: `katten sover`

ROUGE-1 overlap is the unigram `katten`. Precision = recall = F = 0.5.

ROUGE-2 has no overlapping bigram, so F = 0.

ROUGE-L LCS is `katten` (length 1). Precision = recall = F = 0.5.

`tests/test_rouge.py` locks that example down.
