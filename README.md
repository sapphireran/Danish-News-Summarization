# Danish news summarization

Personal final project for **Advanced Natural Language Processing and Deep
Learning**, IT University of Copenhagen, 2023.

The goal was a Danish news summarizer. The training articles did not come
with gold headlines, and there was no strong Danish news-domain abstractive
model to start from. The submitted pipeline therefore **pivots through
English**:

1. OPUS-MT Danish → English (CTranslate2)
2. English news T5 summaries
3. OPUS-MT English → Danish silver labels
4. Fine-tune mT5 on those labels
5. Evaluate on Nordjylland news (human summaries)

The original GPU scripts still live in the repository root. This tree also
has a CPU-only `danish_news/` package, `docs/`, and `examples/` so the same
pipeline can be inspected without downloading checkpoints or the 10k-article
scrape.

## Two ways in

### 1. CPU examples (no GPU, no 10k CSV)

```bash
python -m pip install -e ".[dev]"
python examples/04_inspect_csv_schema.py
python examples/01_chunk_danish_article.py --article-id harbour-plan --max-units 40
python examples/05_window_budget.py --article-id harbour-plan
python examples/02_pipeline_dry_run.py
python examples/03_evaluate_toy_summaries.py
python -m pytest
```

Fixtures are eight fictional Danish articles in `examples/data/`. The
dry-run translator is a glossary, not OPUS-MT. See
[examples/README.md](examples/README.md).

### 2. Original GPU course workflow

Requires CUDA, CTranslate2 conversions, and `10000_articles_without_linebreaks.csv`
(not in git).

#### Step 1: Model conversion

Convert OPUS-MT to CTranslate2. Uncomment the `opus-mt-da-en` block in
`Ctranslate_converter.py` as well — `translate.py` needs that directory.

```bash
python Ctranslate_converter.py
```

#### Step 2: Translate the Danish articles to English

```bash
python translate.py
```

#### Step 3: Summarize the English text

`summary.py` currently slices `[:10]` rows. Remove that slice for a full
run.

```bash
python summary.py
```

#### Step 4: Translate summaries back to Danish

```bash
python translate_back.py
```

#### Fine-tune mT5

`finetune.py` expects `datasets/train_dataset.csv`,
`datasets/validation_dataset.csv`, and `datasets/test_dataset.csv`
(`id`, `body`, `summary`).

```bash
python finetune.py
```

#### Inspect and evaluate

`use_model.py` and `eval.py` load `small_model` with `google/mt5-small`.
Point them at `./large_model` if that is what you trained.

```bash
python use_model.py
python eval.py
```

## Repository layout

```text
.
├── Ctranslate_converter.py   # OPUS-MT → CTranslate2
├── translate.py              # DA → EN
├── summary.py                # English T5 news summaries
├── translate_back.py        # EN → DA silver labels
├── finetune.py               # mT5-large
├── use_model.py              # print a few Nordjylland generations
├── eval.py                   # ROUGE + BERTScore
├── danish_news/              # CPU helpers (chunking, schemas, scoring)
├── docs/                     # pipeline, data, models, eval notes
├── examples/                 # runnable walkthroughs + fixture CSVs
└── tests/                    # pytest for the CPU layer
```

## Documentation

| Document | Topic |
| --- | --- |
| [docs/pipeline.md](docs/pipeline.md) | Stage-by-stage GPU pipeline |
| [docs/dataset.md](docs/dataset.md) | CSV columns and Nordjylland |
| [docs/models.md](docs/models.md) | OPUS-MT, CT2, T5, mT5 |
| [docs/evaluation.md](docs/evaluation.md) | ROUGE / BERTScore vs the toy scorer |
| [docs/design-notes.md](docs/design-notes.md) | Pivot rationale and script quirks |
| [docs/reproduction.md](docs/reproduction.md) | GPU vs CPU reproduction |

## License

MIT. See [LICENSE](LICENSE).
