# Data formats

Every stage of the 2023 pipeline is a UTF-8 CSV with a header. The column
names change, and those names are hard-coded in the root scripts.

## Raw Danish dump

**File (original run):** `10000_articles_without_linebreaks.csv`  
**Fixture:** `examples/data/sample_danish_articles.csv`

| Column | Meaning |
| --- | --- |
| `id` | Stable article id. Used to join later stages. |
| `article text` | Full Danish body, line breaks already stripped. |

`translate.py` does `df['article text']` and `df['id']`. A rename here will
crash the script rather than fail later.

The original filename is a hint: newline-stripped bodies keep
`nltk.sent_tokenize` from treating each line as a paragraph boundary. If you
bring in a new dump, flatten newlines before this stage.

## After Danish → English

**File:** `translated_articles.csv`  
**Fixture:** `examples/data/sample_translated_articles.csv`

| Column | Meaning |
| --- | --- |
| `id` | Copied from the raw dump. |
| `body` | Original Danish, renamed from `article text`. |
| `translated` | English body, windows joined with spaces. |

From this point on the Danish source is always called `body`.

## After English summarisation

**File:** `summarized_file_ml80_rp5.0.csv`  
**Fixture:** `examples/data/sample_english_summaries.csv`

| Column | Meaning |
| --- | --- |
| `id` | Copied. |
| `body` | Original Danish. |
| `translated` | English body (still present for debugging). |
| `summary` | English summary, still not the training target. |

`ml80` and `rp5.0` are `max_length` and `repetition_penalty` from
`summary.py`. If you change those knobs, change the filename or you will
overwrite a previous labelling pass.

## After English → Danish

**File:** `labeled_dataset_ml80_rp5.0.csv`  
**Fixture:** `examples/data/sample_labeled_danish.csv`

| Column | Meaning |
| --- | --- |
| `id` | Copied. |
| `body` | Original Danish. |
| `summary` | Back-translated Danish silver label. |

This is the schema `finetune.py` tokenizes (`data["body"]`, `data["summary"]`).

## Fine-tune splits

**Files:** `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`,
`datasets/test_dataset.csv`

Same three columns as the labelled file. The 2023 project created these
outside git. Suggested personal split for a 10k-article dump:

- train 80%
- validation 10%
- test 10%

Shuffle on `id`, not on row order, in case the dump was grouped by outlet
or date. The silver *test* split is only useful for sanity checks. Reported
numbers should come from Nordjylland News, not from this CSV.

## Nordjylland News (evaluation)

`eval.py` loads `alexandrainst/nordjylland-news-summarization` (`split="test"`).
`use_model.py` loads `ScandEval/nordjylland-news-summarization-mini`.

| Column | Meaning |
| --- | --- |
| `input_text` | Danish article. |
| `target_text` | Human Danish summary. |
| `text_len` | Precomputed article length. Dropped at tokenize time. |
| `summary_len` | Precomputed summary length. Dropped at tokenize time. |

The tokenize functions in `eval.py` / `use_model.py` already `remove_columns`
those last two fields.

## Example evaluation pairs

**Fixture:** `examples/data/sample_eval_pairs.csv`

| Column | Meaning |
| --- | --- |
| `id` | Story id from the invented fixtures. |
| `input_text` | Short Danish snippet. |
| `target_text` | Hand-written reference. |
| `prediction` | Hand-written stand-in for a model output. |

`examples/score_sample_summaries.py` reads this file. It is not produced by
any root script.

## Validation helpers

`danish_news_sum.dataset.validate_columns` and `summarize_dataset` are the
checks the example scripts run. Minimum bar before a training job:

- no empty `body` or `summary`
- every `id` unique
- mean compression roughly between 3× and 20× (outside that, packing or
  the English T5 probably collapsed)
- no summary that is longer than its body
