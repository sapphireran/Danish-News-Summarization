# Danish-News-Summarization

ITU Advanced Natural Language Processing and Deep Learning (2023) final
project: a Danish summarizer trained on **silver labels**. Danish articles
were translated to English, summarized with a news-tuned T5, and translated
back to Danish. Those pairs fine-tuned mT5.

The original course scripts still live at the repository root. They need
GPU weights and a corpus that is not in git.

This checkout also has a personal, download-free workbook — **Sejerø
Tidende** — that replays the same hops on eight fictional island briefs
and scores what a news manchet keeps: 5W1H slots, quotes, and connectives.

## Course workflow (GPU, original scripts)

### 1. Model conversion

`Ctranslate_converter.py` writes CTranslate2 folders for OPUS. The
committed file only converts `opus-mt-en-da`; uncomment the `da-en` lines
before `translate.py`.

```
python Ctranslate_converter.py
```

### 2. Translate the Danish dump to English

```
python translate.py
```

### 3. Summarize the English

```
python summary.py
```

`summary.py` currently scores only `df[:10]`. Remove that slice for a
full run. Output name: `summarized_file_ml80_rp5.0.csv`.

### 4. Translate summaries back to Danish

```
python translate_back.py
```

### 5. Fine-tune mT5

```
python finetune.py
```

Expects `datasets/train_dataset.csv`, `validation_dataset.csv`, and
`test_dataset.csv` with columns `id`, `body`, `summary`.

### 6. Inspect and evaluate

```
python use_model.py
python eval.py
```

`eval.py` uses `alexandrainst/nordjylland-news-summarization`.
`use_model.py` prints the ScandEval mini split. See
[docs/06-course-scripts.md](docs/06-course-scripts.md) for the scars
(NLLB prefixes on OPUS, `no_repeat_ngram_size=1` in the printer, and the
deprecated `load_metric` call).

## Personal workbook (CPU, no weights)

```bash
python3 -m pip install -r requirements-examples.txt
PYTHONPATH=. python3 examples/run_desk.py
PYTHONPATH=. python3 examples/walk_ferry.py
PYTHONPATH=. python3 examples/inspect_manchet.py
PYTHONPATH=. python3 examples/pack_lede.py --id SEJ-001 --policy manchet-tight
PYTHONPATH=. python3 examples/score_slots.py --planted
PYTHONPATH=. python3 -m pytest tests/
```

| Path | Role |
| --- | --- |
| [`docs/`](docs/README.md) | Pipeline notes, manchet / slot / quote write-ups, workbook |
| [`examples/`](examples/README.md) | CLI wrappers and course-shaped CSVs |
| [`sejeroe/`](sejeroe/__init__.py) | Stdlib desk library |
| [`tests/`](tests) | Sentence split, packing, slots, planted-error checks |

The eight briefs (`SEJ-001`–`SEJ-008`) are fiction set on Sejerø. They
are not a slice of the 10 000-article dump.

## License

MIT. See [LICENSE](LICENSE).
