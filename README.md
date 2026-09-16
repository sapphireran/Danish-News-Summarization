# Danish-News-Summarization

Personal ITU Advanced Natural Language Processing and Deep Learning
(2023) final project: a Danish news summarizer trained on **silver
labels** produced by a pivot-language factory.

The idea is simple even if the scripts are not:

1. Translate Danish news to English (OPUS-MT + CTranslate2).
2. Summarize the English with an off-the-shelf news T5.
3. Translate the summaries back to Danish.
4. Fine-tune mT5 on the resulting `(article, summary)` pairs.
5. Score the checkpoint on human-written Nordjylland News summaries,
   not on the silver labels.

This README is the short path. The long path is in
[`docs/`](docs/README.md). CPU-only fixtures and tools that do **not**
need a GPU live in [`examples/`](examples/README.md).

## Repository map

| Path | Role |
| --- | --- |
| `Ctranslate_converter.py` | Hugging Face OPUS-MT → CTranslate2 |
| `translate.py` | Danish articles → English |
| `summary.py` | English T5 summaries (note the `[:10]` debug slice) |
| `translate_back.py` | English summaries → Danish silver labels |
| `finetune.py` | mT5-large on `datasets/*.csv` |
| `use_model.py` | Print a few Nordjylland generations |
| `eval.py` | ROUGE + BERTScore on Nordjylland News |
| `docs/` | Personal notes: contracts, knobs, bugs |
| `examples/` | Synthetic CSVs, example configs, CPU scripts |

Generated news CSVs, CTranslate2 directories, and checkpoints are not
in git. See `.gitignore`.

## GPU workflow (2023 scripts)

You need CUDA-friendly `torch`, `ctranslate2`, `transformers`,
`datasets`, `evaluate`, `nltk`, and `pandas`. A loose pin list is in
[`requirements.txt`](requirements.txt). The course run used whatever
the lab image had in late 2023; do not expect a bit-identical env.

### Step 1: Model conversion

```bash
python Ctranslate_converter.py
```

The committed file only converts `Helsinki-NLP/opus-mt-en-da`.
Uncomment the `opus-mt-da-en` block before step 2. Details:
[docs/translation.md](docs/translation.md).

### Step 2: Translate the Danish dump

```bash
python translate.py
```

Expects `10000_articles_without_linebreaks.csv` with columns `id` and
`article text`. Writes `translated_articles.csv`.

### Step 3: English summaries

```bash
python summary.py
```

Writes `summarized_file_ml80_rp5.0.csv`. **Remove `df[:10]`** before a
full run or you will label ten rows and think you finished.

### Step 4: Translate summaries back to Danish

```bash
python translate_back.py
```

Writes `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`).

### Step 5: Split, then fine-tune

The 2023 repo never committed a splitter. Use the example tool:

```bash
python examples/scripts/split_labeled_dataset.py \
  --input labeled_dataset_ml80_rp5.0.csv \
  --output-dir datasets \
  --train 0.9 --validation 0.05 --test 0.05 --seed 2023

python finetune.py
```

`finetune.py` writes `./large_model`. `eval.py` and `use_model.py` load
`small_model`. Copy or re-point before scoring.

### Step 6: Look and score

```bash
python use_model.py
python eval.py
```

These two scripts load **different** Nordjylland News dumps. Read
[docs/evaluation.md](docs/evaluation.md) before quoting a number.

## CPU workflow (examples, no models)

```bash
python -m unittest discover -s examples/tests -t examples

python examples/scripts/inspect_dataset.py --stage source \
  --path examples/data/sample_articles.csv

python examples/scripts/dry_run_pipeline.py \
  --input examples/data/sample_articles.csv \
  --output-dir /tmp/danish-news-dry-run \
  --split

python examples/scripts/compute_overlap_metrics.py \
  --pred examples/data/sample_labeled.csv \
  --gold examples/data/sample_labeled.csv \
  --pred-col summary --gold-col summary
```

The last command is a self-overlap check and should print 1.0 for
ROUGE-1/2/L. The dry-run writes the same CSV names as the 2023
scripts, using extractive stubs instead of OPUS-MT/T5.

## Known sharp edges

- `Ctranslate_converter.py` does not convert the da→en model that
  `translate.py` needs.
- `summary.py` keeps a `[:10]` smoke-test slice.
- `finetune.py` saves `large_model`; eval loads `small_model`.
- `use_model.py` indexes articles by batch, not by row.
- `datasets.load_metric` is deprecated.
- `use_auth_token=False` breaks on current `transformers`.

The full list is [docs/troubleshooting.md](docs/troubleshooting.md).

## License

MIT. See [LICENSE](LICENSE). The synthetic stories in `examples/data/`
were written for this repository and are original fiction, not scraped
news.
