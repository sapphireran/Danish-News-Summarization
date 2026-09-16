# Danish-News-Summarization

Personal final project for ITU *Advanced Natural Language Processing and Deep
Learning* (2023): a Danish news summariser trained on **silver labels**.
Danish articles are translated to English, summarised with an English news
T5, translated back to Danish, and used to fine-tune mT5. Held-out scores
come from Nordjylland News, not from the automatic labels.

This repository is personal course work. It is not affiliated with a newsroom
or a company model dump.

## Quick start (offline examples)

The original GPU scripts are unchanged. The `docs/` and `examples/` trees
add a path you can run on a laptop:

```bash
pip install -r requirements-examples.txt
python examples/dry_run_pipeline.py
python examples/chunk_sample_articles.py
python examples/inspect_silver_labels.py
python examples/score_sample_summaries.py
python -m pytest tests
```

That walk uses invented fixtures in `examples/data/` and the helpers in
`danish_news_sum/`. No OPUS-MT, T5, or mT5 weights are downloaded.

## GPU workflow (original 2023 scripts)

### 1. Model conversion

Convert Helsinki-NLP OPUS-MT to CTranslate2. The committed converter only
runs `opus-mt-en-da`; uncomment the da→en block before translating.

```bash
python Ctranslate_converter.py
```

### 2. Translate the Danish dump

Input: `10000_articles_without_linebreaks.csv` (`id`, `article text`).

```bash
python translate.py
```

### 3. Summarise the English bodies

`summary.py` is hard-coded to the first ten rows. Remove `[:10]` for a
full pass.

```bash
python summary.py
```

### 4. Translate summaries back to Danish

```bash
python translate_back.py
```

### 5. Fine-tune mT5

Split the labelled CSV into `datasets/{train,validation,test}_dataset.csv`
(`id`, `body`, `summary`), then:

```bash
python finetune.py
```

### 6. Inspect and evaluate

`use_model.py` prints generations from `small_model` on the ScandEval mini
split. `eval.py` reports ROUGE and Danish BERTScore on Nordjylland News.

```bash
python use_model.py
python eval.py
```

## Documentation

- [docs/README.md](docs/README.md) — index
- [docs/overview.md](docs/overview.md) — design of the silver-label bet
- [docs/silver-label-pipeline.md](docs/silver-label-pipeline.md) — DA→EN→summary→DA
- [docs/reproduction.md](docs/reproduction.md) — full GPU replay
- [examples/README.md](examples/README.md) — fixtures and walkthrough scripts

## Layout

| Path | Purpose |
| --- | --- |
| `Ctranslate_converter.py` | OPUS-MT → CTranslate2 |
| `translate.py` / `translate_back.py` | DA↔EN hops |
| `summary.py` | English T5 news summaries |
| `finetune.py` | mT5 training |
| `eval.py` / `use_model.py` | Nordjylland News eval |
| `danish_news_sum/` | Offline chunking, CSV checks, lexical metrics |
| `examples/` | Invented articles and runnable walkthroughs |
| `docs/` | Extended notes for a later personal rerun |

## Licence

MIT. See [LICENSE](LICENSE). The invented example stories in
`examples/data/` are part of this repository. The original 10k-article dump
used in 2023 is not included and is not covered by the MIT licence.
