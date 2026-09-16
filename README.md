# Danish-News-Summarization

Personal 2023 ITU *Advanced Natural Language Processing and Deep Learning*
final project: a Danish news summarizer trained on **silver labels** from a
DA→EN→English-news-T5→EN→DA cascade, then fine-tuned as mT5.

The Python files in the repository root are the frozen exam snapshot. They
are not a library. This branch adds **Pakhuset**, a CPU packing-house lab
that reconstructs the 512-token windows those scripts actually use, without
downloading OPUS-MT, T5, or mT5.

## Why packing?

Every hop re-splits the text and packs sentences into crates that fit a
512-token model. Windows are not written to CSV, so they are forgotten
between hops. Pane summaries are concatenated and later truncated to 128
tokens at train time. That control flow is documented in [`docs/`](docs/README.md)
and measured on fictional Toftevig articles in [`examples/`](examples/README.md).

## CPU lab (no weights)

```bash
python -m pip install -e ".[dev]"
python -m pakhus scars
python -m pakhus atlas --article tof-001
python -m pakhus hops
python -m pakhus report
python -m pytest
```

Workbook: [`docs/09-workbook.md`](docs/09-workbook.md). HTML atlas:
`examples/report/index.html`.

Toftevig copy is original fiction (a made-up harbour municipality). It is
not scraped news and not the 2023 10k-article dump.

## Course GPU workflow (historical)

Needs CUDA, the original CSV (not in git), and both OPUS directions.
`Ctranslate_converter.py` as committed exports **only** `opus-mt-en-da`;
`translate.py` loads `models/opus-mt-da-en_ct2`. See
[`docs/05-script-scars.md`](docs/05-script-scars.md) and
[`docs/08-reproduction.md`](docs/08-reproduction.md).

### Step 1: Model conversion

```bash
python Ctranslate_converter.py
```

### Step 2: Translate dataset

```bash
python translate.py
```

Reads `10000_articles_without_linebreaks.csv` (`id`, `article text`).

### Step 3: Extract summary

```bash
python summary.py
```

As committed, this file slices `[:10]` rows. `max_length=80` is **per
English pane**, not per article.

### Step 4: Translate back to Danish

```bash
python translate_back.py
```

### Fine-tuning

```bash
python finetune.py
```

Expects `datasets/train_dataset.csv`, `validation_dataset.csv`, and
`test_dataset.csv` with columns `id`, `body`, `summary`. Writes
`./large_model`. Labels are truncated at 128 tokens.

### Model evaluation

```bash
python use_model.py
python eval.py
```

These load `small_model` and a Nordjylland Hugging Face split, not the
checkpoint `finetune.py` writes. That mismatch is intentional archaeology,
not a hidden extra step.

## Layout

| Path | Role |
| --- | --- |
| `Ctranslate_converter.py`, `translate.py`, `summary.py`, `translate_back.py`, `finetune.py`, `use_model.py`, `eval.py` | Frozen 2023 scripts |
| `pakhus/` | CPU packing lab |
| `docs/` | Notes on windows, concatenation, scars, CSV contracts |
| `examples/` | Toftevig fixtures, CLIs, HTML atlas |
| `tests/` | pytest for the lab (not GPU) |

## License

MIT. See `LICENSE`.
