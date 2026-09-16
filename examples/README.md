# Examples

Small, download-free walkthroughs of the 2023 Danish news summarization
pipeline. They use a fictional 10-article North Jutland corpus so you
can see CSV shapes, sentence packing, and ROUGE without converting
OPUS-MT or fine-tuning mT5.

The original course scripts (`translate.py`, `summary.py`,
`finetune.py`, …) are unchanged. These files sit next to them.

## What you need

Python 3.10+ and the standard library. No `torch`, no Hub token, no
GPU. From the repository root:

```bash
python examples/run_all_demos.py
```

That regenerates the CSV tables, validates schemas, and runs every demo
plus a few assertions.

## Commands

| Command | What it shows |
| --- | --- |
| `python examples/data/write_tables.py` | Rebuild CSVs from `data/corpus.py` |
| `python examples/validate_schemas.py` | Column contracts for each pipeline stage |
| `python examples/inspect_dataset.py [csv]` | Length stats and a text preview |
| `python examples/run_chunking_demo.py` | How long bodies are packed into windows |
| `python examples/run_silver_label_walkthrough.py` | DA → EN → EN summary → DA summary |
| `python examples/run_rouge_demo.py` | ROUGE-1/2/L on fictional predictions |
| `python examples/compare_summaries.py` | Body / reference / prediction together |
| `python examples/length_filter.py` | Keep/drop silver pairs by length and ratio |
| `python examples/report_hyperparameters.py` | Pretty-print the `finetune.py` defaults |

Useful flags:

```bash
python examples/run_chunking_demo.py --max-length 40 --id da-008
python examples/run_silver_label_walkthrough.py --id da-006
python examples/run_rouge_demo.py --sort rougeL_f1
python examples/inspect_dataset.py examples/data/sample_english_summaries.csv
```

## Layout

```
examples/
  danish_sentences.py      abbreviation-aware splitter (NLTK stand-in)
  text_chunking.py         packing rules from translate.py / summary.py
  rouge_lite.py            ROUGE-1/2/L in the standard library
  schemas.py               CSV contracts
  data/
    corpus.py              source of the fictional articles
    hyperparameters.json   structured copy of finetune.py defaults
    sample_*.csv           generated tables
```

## What the sample corpus is for

The ten articles are original fiction in a local-news register
(ferries, cycleways, storms, schools, wind, football, hospitals,
walking routes, eelgrass). They exist to:

1. Pin the exact column names each script reads and writes, including
   the space in `article text`.
2. Give `finetune.py` a 6/2/2 split it can load if you only want to
   test imports.
3. Make sentence packing visible: `da-006` and `da-008` are long on
   purpose.
4. Show that a “pretty good” prediction can still be factually off
   (`da-003` turns broken moorings into destroyed cutters) while ROUGE
   stays non-zero.

Do not train a real model on these ten rows and do not mix them into
Nordjylland-News.

## Mapping onto the course scripts

```
sample_danish_articles.csv       →  translate.py
sample_translated_articles.csv   →  summary.py
sample_english_summaries.csv     →  translate_back.py
sample_labeled_dataset.csv       →  manual split
sample_{train,validation,test}_split.csv  →  finetune.py
sample_predictions.csv           →  examples only (eval.py uses the Hub)
```

Copy the three split files to `datasets/` only if you are smoke-testing
the trainer. A serious run needs the silver-label pipeline and a real
split, documented in [`docs/reproduction.md`](../docs/reproduction.md).
