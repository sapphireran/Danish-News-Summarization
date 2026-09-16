# Datasets

Three different dataset shapes appear in this repository. They are easy
to mix up because several columns are named `summary` or `text` at
different stages.

## 1. Unlabeled Danish articles (pipeline input)

`translate.py` default path: `10000_articles_without_linebreaks.csv`

| column | type | notes |
| --- | --- | --- |
| `id` | identifier | passed through every later CSV |
| `article text` | Danish string | the space in the name is intentional |

The filename is the only hint at scale. The file itself is not in git
(and should stay out of git; see the root `.gitignore`).

After `translate.py` the working table is `translated_articles.csv`:

| column | type |
| --- | --- |
| `id` | identifier |
| `body` | original Danish (`article text` renamed) |
| `translated` | English pivot |

## 2. Silver-label tables (pipeline output → fine-tune)

`summary.py` writes `summarized_file_ml80_rp5.0.csv`:

| column | type |
| --- | --- |
| `id` | identifier |
| `body` | Danish source |
| `translated` | English pivot |
| `summary` | **English** summary |

`translate_back.py` writes `labeled_dataset_ml80_rp5.0.csv`:

| column | type |
| --- | --- |
| `id` | identifier |
| `body` | Danish source |
| `summary` | **Danish** silver summary |

`finetune.py` then reads three splits that must already exist:

```
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

Required columns: `id`, `body`, `summary`. Extra columns are dropped by
the tokenizer `remove_columns` list, so do not add fields without
updating `finetune.py`.

A fictional mini-corpus with this exact schema lives in
[`examples/data/`](../examples/data/README.md).

## 3. Public evaluation sets (not used for training)

### `alexandrainst/nordjylland-news-summarization`

Used by `eval.py` (`split="test"`).

Public card (Hugging Face):

| field | meaning |
| --- | --- |
| `text` | Danish article from TV2 Nord |
| `summary` | editor / site summary |
| `text_len` | character length of `text` |
| `summary_len` | character length of `summary` |

Published split sizes: train 75,219 / validation 4,178 / test 4,178.
License on the card: CC0. Language: `da`.

`eval.py` tokenizes `input_text` / `target_text` and drops
`text_len` / `summary_len`. That field pair is the **ScandEval** naming,
not the Alexandra Institute card. If a raw `load_dataset` call returns
`text` / `summary` instead, the tokenize function will KeyError. In that
case rename columns before mapping:

```python
test_dataset = test_dataset.rename_columns(
    {"text": "input_text", "summary": "target_text"}
)
```

### `ScandEval/nordjylland-news-summarization-mini`

Used by `use_model.py`. This is the compact ScandEval packaging of the
same Nordjylland-News task, with `input_text`, `target_text`,
`text_len`, and `summary_len`. It is the right set for a quick
qualitative loop; it is not large enough to replace `eval.py`.

`eval.py` has a commented line that also loaded this mini split.

## Length conventions

| Stage | Encoder cap | Decoder / generation cap |
| --- | --- | --- |
| OPUS-MT translate | 512 (`text_max_length ≈ 460`) | translation length follows source |
| English T5 | 512 | 80 |
| mT5 fine-tune | 1024 | 128 |
| `use_model.py` label tokenize | 1024 | 180 |
| `eval.py` label tokenize | 1024 | 128 |

The 180 vs 128 mismatch means `use_model.py` can display a longer
reference than `eval.py` scored. Prefer 128 everywhere if you want the
printed references to match the metric.

## Recommended local layout

```
datasets/
  train_dataset.csv
  validation_dataset.csv
  test_dataset.csv
examples/data/                 # fictional samples, safe to commit
  sample_danish_articles.csv
  sample_translated_articles.csv
  ...
```

Do not commit the 10k-article dump or any TV2 Nord text. The example
tables are original fiction written for this documentation.
