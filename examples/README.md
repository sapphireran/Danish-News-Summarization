# Examples

CPU-only walkthrough of the **data contracts** behind the 2023 Danish news
summarization project. Nothing in this folder downloads OPUS-MT, T5, or mT5.

If you want the real GPU pipeline, go back to the root [README](../README.md)
and [docs/pipeline.md](../docs/pipeline.md). This tree exists so you can see
the filenames, columns, and sentence packer without a course machine.

## What is in here

```
examples/
  data/
    raw_danish_articles.csv         # mirrors 10000_articles_without_linebreaks.csv
    translated_articles.csv         # mirrors translate.py
    summarized_articles.csv         # mirrors summary.py (summary is English)
    labeled_danish.csv              # mirrors translate_back.py (summary is Danish)
    nordjylland_like_eval.csv       # mirrors eval.py column names
    finetune/                       # mirrors datasets/*.csv
    generate_sample_csvs.py         # rebuilds the CSVs from sample_corpus.py
  lib/
    schema.py                       # column contracts
    text_chunking.py                # packer ported from the course scripts
    extractive_summary.py           # first-N sentence baseline
    sample_corpus.py                # the 12 fictional articles
  validate_example_data.py
  sentence_chunking_demo.py
  toy_labeling_pipeline.py
  length_stats.py
  inspect_splits.py
  test_text_chunking.py
  output/                           # gitignored products of a local run
```

The 12 articles are **fictional**. They use real Danish place names and
institutions the way a classroom handout would. They are not a news dump.

## Run the walkthrough

From the repository root:

```bash
pip install -r requirements-examples.txt
python -c "import nltk; nltk.download('punkt')"   # optional but closer to the course scripts
python examples/test_text_chunking.py
python examples/validate_example_data.py
python examples/sentence_chunking_demo.py
python examples/sentence_chunking_demo.py --id da-006 --max-length 40
python examples/length_stats.py
python examples/inspect_splits.py
python examples/toy_labeling_pipeline.py
```

All of those commands should exit 0. `toy_labeling_pipeline.py` writes into
`examples/output/` and will not overwrite the committed CSVs.

## How the sample files map onto the course scripts

| Example file | Course file the scripts actually open | Columns |
| --- | --- | --- |
| `data/raw_danish_articles.csv` | `10000_articles_without_linebreaks.csv` | `id`, `article text` |
| `data/translated_articles.csv` | `translated_articles.csv` | `id`, `body`, `translated` |
| `data/summarized_articles.csv` | `summarized_file_ml80_rp5.0.csv` | `id`, `body`, `translated`, `summary` (EN) |
| `data/labeled_danish.csv` | `labeled_dataset_ml80_rp5.0.csv` | `id`, `body`, `summary` (DA) |
| `data/finetune/train_dataset.csv` | `datasets/train_dataset.csv` | `id`, `body`, `summary` |
| `data/finetune/validation_dataset.csv` | `datasets/validation_dataset.csv` | `id`, `body`, `summary` |
| `data/finetune/test_dataset.csv` | `datasets/test_dataset.csv` | `id`, `body`, `summary` |
| `data/nordjylland_like_eval.csv` | hub Nordjylland test | `input_text`, `target_text`, `text_len`, `summary_len` |

`validate_example_data.py` enforces that list, plus:

- ids are unique and identical (and in the same order) across the four pipeline stages,
- `body` never drifts from the raw `article text`,
- Danish columns contain `æ/ø/å`,
- English columns are not stuffed with those letters,
- train / validation / test partition the twelve ids without leakage.

If you rename a column in a course script, change `examples/lib/schema.py` in
the same commit.

## Two kinds of Danish summary

Each article in `sample_corpus.py` carries **two** Danish abstracts:

| Field | Style | Where it is written |
| --- | --- | --- |
| `summary_da_pivot` | Short, a bit like English news after OPUS-MT | `labeled_danish.csv` and the finetune splits |
| `summary_da_editorial` | Tighter local-news lede | `nordjylland_like_eval.csv` |

That split is the whole point of the 2023 eval design. Silver labels and
editorial labels are not the same genre. `toy_labeling_pipeline.py` adds a
third style — first two sentences of the body — and prints the mean unigram
Jaccard against the pivot labels. Expect a low number. High overlap would
mean the hand-written pivot labels were just the lede copied twice.

## Sentence packing

`translate.py` and `summary.py` cannot send a 2,000-token feature through a
512-token encoder. They:

1. sentence-split,
2. cut over-long sentences on `,` / `;` / `:`,
3. greedy-pack sentences until the budget is full,
4. run the model on each pack,
5. join the outputs with spaces.

`sentence_chunking_demo.py` prints those packs. Use `--max-length 80` to see
many packs on the long energy and economy pieces (`da-006`, `da-012`). Use
`460` to see the budget the course translator actually used (`int(512 * 0.9)`).

`translate_back.py` skips step 2. The helper exposes that as
`split_overlong=False`.

The course cutter mixed a running `len(word)+1` budget with a token cap.
`split_long_sentence_legacy` keeps that behaviour; the default helper measures
both cuts with the same length function so a demo is readable. Details are in
[docs/pipeline.md](../docs/pipeline.md).

## Rebuilding the CSVs

Edit `examples/lib/sample_corpus.py`, then:

```bash
python examples/data/generate_sample_csvs.py
python examples/validate_example_data.py
```

Commit both the corpus module and the regenerated CSVs. The validator will
fail if the finetune id lists in `sample_corpus.py` drift.

## What this will not do

- It will not fine-tune mT5. Twelve rows are a schema fixture, not a train set.
- It will not call CTranslate2. The `translated` column is hand-written English.
- It will not prove the 2023 ROUGE numbers. There are no weights in git.

Use it as a regression gate when you touch docs, schemas, or the packer.
