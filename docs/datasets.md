# Datasets

This project touches three different kinds of data. Mixing them up is the
most common way to get a confusing training run.

1. **Source dump** — unlabeled Danish news used to *create* silver labels.
2. **Silver-label CSVs** — files written by the pivot pipeline.
3. **Evaluation sets** — public Danish summarization benchmarks with
   human-written targets.

## 1. Source dump (not in git)

`translate.py` hard-codes:

```text
10000_articles_without_linebreaks.csv
```

Expected columns:

| Column | Type | Notes |
| --- | --- | --- |
| `id` | string or int | Must stay unique. Later joins key on this. |
| `article text` | string | Danish body. Line breaks were already stripped in the 2023 dump. |

The dump itself is not committed. That is correct: it is a 10k-article news
corpus, not a toy fixture. For local experiments use the synthetic rows in
[`examples/data/sample_articles.csv`](../examples/data/sample_articles.csv).
Those rows are original fiction written for this repository. They are not
scraped news.

### Practical checks before translation

- No empty `article text` values. Empty strings still go through the
  translator and produce empty or garbage labels.
- Ids are unique. `translate.py` does not deduplicate.
- Encoding is UTF-8. Danish æ/ø/å will mojibake if Excel saved the file as
  a Windows code page.
- Line breaks inside a cell are fine for pandas, but the 2023 filename
  (`without_linebreaks`) suggests the dump was already flattened to one
  paragraph per article. Sentence splitting still works either way.

Approximate size: 10,000 rows. At 512-token windows, a long feature piece
can become several translation batches, so wall-clock time is closer to
"number of windows" than "number of rows".

## 2. Intermediate pipeline CSVs

All generated CSVs are UTF-8 with `index=False`.

### `translated_articles.csv`

| Column | Language | Source |
| --- | --- | --- |
| `id` | — | Copied from the dump |
| `body` | Danish | `article text` renamed |
| `translated` | English | OPUS-MT da→en |

`summary.py` reads `translated` and keeps `body` so the original Danish
survives the English-only summarizer.

### `summarized_file_ml80_rp5.0.csv`

| Column | Language | Source |
| --- | --- | --- |
| `id` | — | Copied |
| `body` | Danish | Copied |
| `translated` | English | Copied |
| `summary` | English | T5 news summarizer |

If an article was split into several 512-token windows, `summary` is the
space-joined concatenation of per-window summaries. That can make silver
labels longer and more extractive than a single-document summary.

### `labeled_dataset_ml80_rp5.0.csv`

| Column | Language | Source |
| --- | --- | --- |
| `id` | — | Copied |
| `body` | Danish | Original article |
| `summary` | Danish | OPUS-MT en→da of the English T5 summary |

This is the silver-label corpus. `translated` is dropped here on purpose:
fine-tuning should see Danish in and Danish out.

## 3. Fine-tuning splits

`finetune.py` loads:

```text
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

Hugging Face `load_dataset('csv', ...)` then `['train']` is used even for
the validation and test files. That is a datasets-library quirk, not a
claim that those files are training data. The `DatasetDict` keys are what
matter:

```python
split_dataset = DatasetDict({
    'train': train_dataset,
    'validation': validation_dataset,
    'test': test_dataset,
})
```

Required columns: `id`, `body`, `summary`. Extra columns are not removed
until `tokenize_data`, which only drops `id`, `body`, and `summary`. If you
add helper columns (`source`, `n_tokens`, …), extend that `remove_columns`
list or tokenization will fail.

### Split advice (personal, not from the 2023 hand-in)

- Split **by article id**, never by sentence.
- Do not put the same `id` in two files.
- Keep a held-out slice of silver labels if you want an in-domain
  diagnostic, but do **not** treat silver-label ROUGE as the project
  result. The model can learn to imitate pivot artifacts.
- A 90 / 5 / 5 split is enough when the labeled file has on the order of
  10k rows. With fewer than ~500 rows, prefer 80 / 10 / 10.

`finetune.py` tokenizes `body` to 1024 tokens and `summary` to 128 tokens.
Summaries much longer than 128 tokens are silently truncated.

## 4. Public evaluation sets

Two different Nordjylland News datasets appear in the eval scripts. They
are related but not interchangeable.

| Script | Dataset id | Split | Notes |
| --- | --- | --- | --- |
| `eval.py` | `alexandrainst/nordjylland-news-summarization` | `test` | Full test split |
| `use_model.py` | `ScandEval/nordjylland-news-summarization-mini` | `test` | Smaller qualitative set |

`eval.py` has a commented line that also used the mini set. The committed
path uses the Alexandrainst dump.

Expected columns after load (as used by the tokenizers):

| Column | Role |
| --- | --- |
| `input_text` | Danish article |
| `target_text` | Human Danish summary |
| `text_len` | Dropped after tokenization |
| `summary_len` | Dropped after tokenization |

These names do **not** match the silver-label CSVs (`body` / `summary`).
That is why `finetune.py` and `eval.py` cannot share one tokenize function
without a column adapter.

## 5. Column-name cheat sheet

| Stage | Article column | Summary / translation column |
| --- | --- | --- |
| Source dump | `article text` | — |
| After da→en | `body` | `translated` (en) |
| After English summary | `body` | `summary` (en) |
| After en→da | `body` | `summary` (da) |
| Fine-tune splits | `body` | `summary` (da) |
| Nordjylland News | `input_text` | `target_text` |

`examples/data/expected_columns.json` encodes the same table so
`examples/scripts/inspect_dataset.py` can validate a file against a named
stage.

## 6. What not to commit

Do not add to git:

- The 10k news dump
- Generated translation / summary CSVs from real news
- `models/*_ct2` directories
- `large_model/`, `small_model/`, or `mt5-summarize-large/`
- Hugging Face or datasets cache directories

The `examples/data/` fixtures are synthetic and small. Those *are* meant
to be committed so the pipeline contracts stay reviewable.
