# Danish-News-Summarization

Personal ITU course project (Advanced NLP and Deep Learning, 2023): a
Danish news summarizer whose **training labels are themselves generated**.

The idea is a language hop. Danish articles are translated to English,
summarized with an English news T5, then translated back to Danish.
Those silver pairs fine-tune `google/mt5-large` so inference can stay
in Danish.

This repository still contains the original hand-in scripts. The
`docs/` and `examples/` trees were added later as personal notes and
offline walk-throughs. They do not change how the 2023 `*.py` files
behave.

## Neural workflow (original scripts)

You need CTranslate2 models, Transformers, and usually a CUDA GPU.
See [docs/reproduction.md](docs/reproduction.md) before a full run —
`Ctranslate_converter.py` currently exports only the EN→DA model, and
`summary.py` still slices the first ten rows.

### Step 1: Model conversion

```
python Ctranslate_converter.py
```

### Step 2: Translate the Danish dump to English

```
python translate.py
```

Input: `10000_articles_without_linebreaks.csv` (`id`, `article text`).

### Step 3: Summarize the English articles

```
python summary.py
```

Uses `mrm8488/t5-base-finetuned-summarize-news`.

### Step 4: Translate summaries back to Danish

```
python translate_back.py
```

### Fine-tune

```
python finetune.py
```

Expects `datasets/{train,validation,test}_dataset.csv` with
`id,body,summary`. Writes `./large_model`.

### Look at predictions / score Nordjylland

```
python use_model.py
python eval.py
```

These load `small_model` and a public Nordjylland split, not the
silver-label test CSV. Column names on the Alexandra dataset have
moved since 2023; see [docs/evaluation.md](docs/evaluation.md).

## Offline examples (no model download)

```
python3 -m unittest discover -s tests -v
python3 examples/schema_check.py
python3 examples/chunking_demo.py --max-length 40
python3 examples/toy_pipeline.py
python3 examples/compare_summaries.py
```

Or `bash examples/run_all.sh`.

The sample articles in `examples/data/` are invented. They exist to
show CSV schemas, sentence packing, and an extractive baseline. Details:
[examples/README.md](examples/README.md).

## Documentation

- [docs/pipeline.md](docs/pipeline.md) — DA→EN→T5→DA labeling and chunking
- [docs/dataset-schema.md](docs/dataset-schema.md) — column contracts
- [docs/training.md](docs/training.md) — mT5 hyperparameters
- [docs/evaluation.md](docs/evaluation.md) — ROUGE, BERTScore, Nordjylland
- [docs/limitations.md](docs/limitations.md) — known traps in the 2023 code
- [docs/reproduction.md](docs/reproduction.md) — what git can and cannot replay
- [docs/course-notes.md](docs/course-notes.md) — why silver labels

`requirements.txt` lists the neural stack. The examples and tests use
the standard library only.

## License

MIT. See [LICENSE](LICENSE).
