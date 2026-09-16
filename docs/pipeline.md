# Pipeline

The repository is a linear batch pipeline, not a library. Each stage reads a
CSV, writes another CSV, and the next script hard-codes that filename.

```text
Danish articles CSV
        |
        v
Ctranslate_converter.py -----> models/opus-mt-en-da_ct2
                               models/opus-mt-da-en_ct2   (commented out)
        |
        v
translate.py -------------> translated_articles.csv
        |
        v
summary.py ---------------> summarized_file_ml80_rp5.0.csv
        |
        v
translate_back.py --------> labeled_dataset_ml80_rp5.0.csv
        |
        v
manual split -------------> datasets/{train,validation,test}_dataset.csv
        |
        v
finetune.py --------------> large_model/   (or mt5-summarize-large/)
        |
        +--> use_model.py  (qualitative generations)
        +--> eval.py       (ROUGE + BERTScore on Nordjylland News)
```

## Stage contracts

### 0. Convert translation models

`Ctranslate_converter.py` wraps Hugging Face OPUS-MT checkpoints with
CTranslate2 so later stages can batch-translate on GPU or CPU without
keeping the full Transformers encoder-decoder graph in memory.

**As committed in 2023, only `Helsinki-NLP/opus-mt-en-da` is converted.**
The Danish-to-English converter lines are commented out, but `translate.py`
loads `models/opus-mt-da-en_ct2`. Uncomment those lines before running
the Danish-to-English stage, or the first translation step will fail.

### 1. Danish to English

`translate.py` expects:

| Field | Source |
| --- | --- |
| Input file | `10000_articles_without_linebreaks.csv` |
| Input columns | `id`, `article text` |
| Model directory | `models/opus-mt-da-en_ct2` |
| Tokenizer | `Helsinki-NLP/opus-mt-da-en` |
| Output file | `translated_articles.csv` |
| Output columns | `id`, `body`, `translated` |

`body` is a copy of the original Danish article. `translated` is English.

Long articles are sentence-split with NLTK, then packed into windows that
stay under 90% of the 512-token OPUS-MT limit. See
[translation.md](translation.md).

### 2. English summarization

`summary.py` expects `translated_articles.csv` and writes
`summarized_file_ml80_rp5.0.csv`.

The filename encodes the generation settings used in 2023:

- `ml80` — `max_length=80` tokens for each chunk summary
- `rp5.0` — `repetition_penalty=5.0`

The committed script also slices `df[:10]`. That was a smoke-test leftover.
Remove the slice before labeling a full corpus.

Output columns: `id`, `body`, `translated`, `summary` (English).

### 3. English summaries back to Danish

`translate_back.py` reads the summarizer CSV and writes
`labeled_dataset_ml80_rp5.0.csv` with:

| Column | Language | Meaning |
| --- | --- | --- |
| `id` | — | Stable article id from the source dump |
| `body` | Danish | Original article |
| `summary` | Danish | Pivot-translated silver label |

This is the file that later becomes the fine-tuning corpus after a train /
validation / test split.

### 4. Fine-tune mT5

`finetune.py` does **not** read `labeled_dataset_ml80_rp5.0.csv` directly.
It expects already-split files:

```text
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

Each split must have `id`, `body`, and `summary`. How those splits were cut
in 2023 is not recorded in the repo. A reasonable personal default is an
article-level 90 / 5 / 5 split with no leaked ids across files.

### 5. Inspect and score

`use_model.py` and `eval.py` load a local checkpoint (`small_model` by
default) and a public Danish news test set. They are independent of the
silver-label CSVs. That is intentional: the silver labels train the model,
but the reported numbers should come from human-written Nordjylland News
summaries.

## What is not automated

The 2023 scripts leave several gaps that a later personal rerun has to fill
by hand:

1. Downloading the original 10k Danish article dump.
2. Converting **both** OPUS-MT directions.
3. Removing the `[:10]` debug slice in `summary.py`.
4. Splitting `labeled_dataset_ml80_rp5.0.csv` into `datasets/*.csv`.
5. Deciding whether evaluation should load `small_model` or `large_model`.
   Training writes `./large_model`, but both eval scripts load `small_model`.
6. Installing NLTK `punkt` (and, on newer NLTK, `punkt_tab`).

The toy pipeline in `examples/scripts/dry_run_pipeline.py` walks the same
file contracts with tiny synthetic articles so the CSV shapes can be
checked without GPUs.

## Suggested working directory layout

```text
Danish-News-Summarization/
  Ctranslate_converter.py
  translate.py
  summary.py
  translate_back.py
  finetune.py
  eval.py
  use_model.py
  models/
    opus-mt-da-en_ct2/
    opus-mt-en-da_ct2/
  datasets/
    train_dataset.csv
    validation_dataset.csv
    test_dataset.csv
  large_model/          # written by finetune.py
  small_model/          # expected by eval.py / use_model.py
  10000_articles_without_linebreaks.csv
  translated_articles.csv
  summarized_file_ml80_rp5.0.csv
  labeled_dataset_ml80_rp5.0.csv
```

Keep `models/`, raw dumps, and generated CSVs out of git. They are large,
regenerable, and (for the news dump) not this repository's to republish.
