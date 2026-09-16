# Danish News Summarization

Personal ITU project for **Advanced Natural Language Processing and Deep Learning (2023)**.

The goal is a Danish news summarizer trained on **automatically generated labels**. High-quality Danish summary pairs were scarce, so this repo builds silver labels with a translate → summarize → translate-back loop, then fine-tunes multilingual T5 (`mT5`) on the resulting Danish `(article, summary)` pairs.

This is a personal academic archive. The original training scripts are kept as they were submitted. The `docs/` and `examples/` trees explain the pipeline, schemas, and design choices so the project can be reread or reproduced without guessing file names.

## Why this approach

Danish abstractive summarization had much less labeled news data than English in 2023. The silver-label recipe used here is:

1. Translate Danish articles to English with Helsinki-NLP OPUS-MT (`da→en`), converted to [CTranslate2](https://github.com/OpenNMT/CTranslate2) for faster batch decoding.
2. Summarize the English text with a T5 news summarizer (`mrm8488/t5-base-finetuned-summarize-news`).
3. Translate the English summaries back to Danish (`en→da`).
4. Fine-tune `google/mt5-large` (or `mt5-small` for lighter experiments) on the Danish pairs.
5. Evaluate on a held-out Danish news set (Nordjylland News summarization) with ROUGE and BERTScore.

The labeling path is lossy. Translation error, English-centric summarizer style, and back-translation all land in the training targets. That is intentional: the project studies whether those silver labels are still useful enough to train a Danish-only decoder. See [docs/design-notes.md](docs/design-notes.md).

## Repository layout

```text
.
├── Ctranslate_converter.py   # Convert OPUS-MT checkpoints to CTranslate2
├── translate.py              # Danish articles → English
├── summary.py                # English articles → English summaries
├── translate_back.py         # English summaries → Danish summaries
├── finetune.py               # Fine-tune mT5 on labeled Danish CSVs
├── use_model.py              # Print a few model predictions
├── eval.py                   # ROUGE + BERTScore on a test split
├── docs/                     # Pipeline, models, data, evaluation
├── examples/                 # Sample CSVs + CPU-only utilities
└── tests/                    # Unit tests for the example utilities
```

The original scripts stay at the repo root. New documentation and runnable examples live under `docs/` and `examples/` so the 2023 training code remains easy to compare with the write-up.

## Workflow

The diagram is the same path the root scripts implement.

```text
Danish article CSV
        │
        ▼
  CTranslate2 da→en          translate.py
        │
        ▼
  English article + id
        │
        ▼
  T5 news summarizer         summary.py
        │
        ▼
  English summary
        │
        ▼
  CTranslate2 en→da          translate_back.py
        │
        ▼
  Danish (body, summary)
        │
        ▼
  train / validation / test  datasets/*.csv
        │
        ▼
  mT5 fine-tune              finetune.py
        │
        ▼
  inspect / evaluate         use_model.py, eval.py
```

### Step 1: Model conversion

`Ctranslate_converter.py` converts a Transformers OPUS-MT checkpoint with CTranslate2.

```bash
python Ctranslate_converter.py
```

The checked-in converter currently converts **`Helsinki-NLP/opus-mt-en-da` only**. `translate.py` loads `models/opus-mt-da-en_ct2`. Uncomment the `opus-mt-da-en` block (or convert that model the same way) before running Danish→English translation. Details are in [docs/models.md](docs/models.md).

### Step 2: Translate the dataset

`translate.py` reads Danish articles and writes English text.

```bash
python translate.py
```

Default paths:

| Role | Path | Columns |
| --- | --- | --- |
| Input | `10000_articles_without_linebreaks.csv` | `id`, `article text` |
| Output | `translated_articles.csv` | `id`, `body`, `translated` |
| Model | `models/opus-mt-da-en_ct2` | — |

Long articles are split on sentences (and over-long sentences on punctuation) so each OPUS-MT batch stays near a 512-token window. The same packing rules are reimplemented in `examples/text_chunking.py` so you can inspect them without downloading weights.

### Step 3: Extract English summaries

```bash
python summary.py
```

Default paths:

| Role | Path | Notes |
| --- | --- | --- |
| Input | `translated_articles.csv` | Uses the `translated` column |
| Output | `summarized_file_ml80_rp5.0.csv` | Adds `summary` |
| Model | `mrm8488/t5-base-finetuned-summarize-news` | `max_length=80`, `repetition_penalty=5.0` |

The script currently slices `df[:10]` before summarizing. That is a leftover debug cap. Remove it for a full run. See [docs/troubleshooting.md](docs/troubleshooting.md).

### Step 4: Translate summaries back to Danish

```bash
python translate_back.py
```

| Role | Path | Columns |
| --- | --- | --- |
| Input | `summarized_file_ml80_rp5.0.csv` | `id`, `body`, `summary` (English) |
| Output | `labeled_dataset_ml80_rp5.0.csv` | `id`, `body`, `summary` (Danish) |
| Model | `models/opus-mt-en-da_ct2` | — |

The Danish `body` is the original article, not a round-tripped translation. Only the summary crosses English and back.

### Fine-tuning

```bash
python finetune.py
```

Expected files (not produced automatically — split the labeled CSV yourself):

- `datasets/train_dataset.csv`
- `datasets/validation_dataset.csv`
- `datasets/test_dataset.csv`

Each file needs `id`, `body`, `summary`. The trainer starts from `google/mt5-large`, trains for 20 epochs with Adafactor, and writes the best checkpoint to `./large_model`. Hyperparameters are listed in [docs/hyperparameters.md](docs/hyperparameters.md).

### Inspection and evaluation

```bash
python use_model.py
python eval.py
```

`use_model.py` prints a few generations from a local `small_model` directory against `ScandEval/nordjylland-news-summarization-mini`.

`eval.py` runs ROUGE and Danish BERTScore on `alexandrainst/nordjylland-news-summarization` (test split) using the same local `small_model` path. Metric definitions are in [docs/evaluation.md](docs/evaluation.md).

## Documentation

| Document | Contents |
| --- | --- |
| [docs/README.md](docs/README.md) | Index of the write-up |
| [docs/pipeline.md](docs/pipeline.md) | Stage-by-stage I/O and script behavior |
| [docs/datasets.md](docs/datasets.md) | CSV and Hugging Face schemas |
| [docs/models.md](docs/models.md) | OPUS-MT, CTranslate2, T5, mT5 |
| [docs/evaluation.md](docs/evaluation.md) | ROUGE, BERTScore, generation settings |
| [docs/hyperparameters.md](docs/hyperparameters.md) | Training and decode knobs copied from the scripts |
| [docs/design-notes.md](docs/design-notes.md) | Why silver labels, and where error accumulates |
| [docs/reproducing.md](docs/reproducing.md) | Hardware, downloads, and a full-run checklist |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Known gaps in the 2023 scripts |

## Examples (CPU, no model weights)

The `examples/` package is meant to be run on a laptop. It does **not** call Transformers or CTranslate2.

```bash
python -m examples.demo_pipeline
python -m examples.inspect_sample --article-id aalborg-library-hours
python -m examples.rouge_toy
python -m unittest discover -s tests -v
```

Sample tables live in `examples/sample_data/` and follow the same column names as the root scripts. They are short, fictional North Jutland-style notices written for this repo. They are not scraped news.

## Dependencies

Root training scripts (GPU recommended):

```bash
pip install -r requirements.txt
```

Example utilities and tests use the standard library only. Optional extras for playing with the sample CSVs in a notebook:

```bash
pip install -r examples/requirements.txt
```

NLTK `punkt` is required by the original translation and summary scripts:

```bash
python -c "import nltk; nltk.download('punkt')"
```

## Status of the 2023 scripts

These behaviors are documented rather than silently rewritten:

- `Ctranslate_converter.py` does not emit the `da-en` model `translate.py` expects.
- `summary.py` processes only the first 10 rows.
- `datasets.load_metric` is deprecated; `evaluate.load` is the current API.
- `use_auth_token=False` on `AutoTokenizer.from_pretrained` is deprecated.
- `finetune.py` and `eval.py` / `use_model.py` use different default model sizes and local folders (`large_model` vs `small_model`).
- `summary.py` hard-codes `[:10]` and a specific output filename encoding `ml80` and `rp5.0`.

See [docs/troubleshooting.md](docs/troubleshooting.md) before a full reproduction.

## License

MIT. See [LICENSE](LICENSE).
