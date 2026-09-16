# Nordjylland versus the private dump

Two Danish news resources show up in this project. They are not
interchangeable, and only one of them is public.

## Public: Nordjylland News Summarization

- Hub: [`alexandrainst/nordjylland-news-summarization`](https://huggingface.co/datasets/alexandrainst/nordjylland-news-summarization)
- Curator: Oliver Kinch, Alexandra Institute
- Source: TV2 Nord API
- License: CC0
- Language: Danish
- Official card fields: `text`, `summary`, `text_len`, `summary_len`
- Splits on the card: train 75 219, val 4 178, test 4 178
- Known wart on the card: 181 rows where the summary is longer than the text

`eval.py` loads that dataset's `test` split, then tokenizes `input_text` /
`target_text` and drops `['input_text', 'target_text', 'text_len', 'summary_len']`.
The official card does **not** list `input_text` or `target_text`. A clean
`load_dataset` of the Alexandra set will not match those column names unless
something remaps them first. That is a [script scar](script-scars.md).

## Public mini: ScandEval

`use_model.py` loads `ScandEval/nordjylland-news-summarization-mini` and also
expects `input_text` / `target_text`. ScandEval's wrappers exist to make
Nordic tasks look the same inside their harness. Do not assume the mini split
is a random 1% of the Alexandra test set, and do not assume the columns match
the official card.

## Private: the 10k course dump

`translate.py` reads `10000_articles_without_linebreaks.csv` with columns
`id` and `article text`. That file is not in git. I am not going to replace
it with a scraped Nordjylland slice and call it the same experiment:

- Nordjylland pairs already have summaries. The course dump was unlabeled
  body text that the hop was supposed to label.
- Mixing a public eval set into the silver trainer is leakage if you later
  score on the same stories.
- I do not have a provenance note for the 10k file beyond "Danish news
  articles used in the ITU project".

The fiction CSV at `examples/data/fiction_articles.csv` reuses the
`article text` header so schema experiments have something to open. It is
sixteen rows of original fiction.

## What I use each set for

| Resource | Role in 2023 | Role in this lab |
| --- | --- | --- |
| 10k dump | Silver-label source | Missing; documented only |
| Nordjylland full | `eval.py` test | Documented, not vendored |
| ScandEval mini | `use_model.py` smoke | Documented, not vendored |
| `lab-*` fiction | — | Baselines, rubric, catalog |

If I retrain, the student still should be scored on Nordjylland **and** on a
held-out slice of whatever dump I silver-label. Those two numbers answer
different questions.
