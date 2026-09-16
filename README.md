# Danish-News-Summarization

Personal ITU *Advanced Natural Language Processing and Deep Learning* (2023) final project: a Danish news summarizer trained on **silver labels** produced by pivoting through English.

Danish articles are translated to English (OPUS-MT), summarized with an English news T5, then translated back. The resulting `(Danish article, Danish summary)` pairs fine-tune mT5 so inference can stay in Danish.

This repository is course code plus later personal notes. It is not a packaged library. Intermediate CSVs and model weights were never committed.

## Start here

| If you want… | Open |
| --- | --- |
| The original six-step command list | [Workflow](#workflow) below |
| How each script names its files and columns | [`docs/pipeline.md`](docs/pipeline.md), [`docs/datasets-and-schemas.md`](docs/datasets-and-schemas.md) |
| Models, CTranslate2, mT5 size mismatch | [`docs/models-and-conversion.md`](docs/models-and-conversion.md) |
| Trainer settings and eval caveats | [`docs/fine-tuning.md`](docs/fine-tuning.md), [`docs/evaluation.md`](docs/evaluation.md) |
| Known leftover bugs (NLLB prefixes, `[:10]`, `small_model`) | [`docs/design-notes.md`](docs/design-notes.md) |
| A laptop run with **no** Hub downloads | [`examples/README.md`](examples/README.md) |

```bash
python examples/run_all.py
```

That command uses only the standard library and the fictional fixtures in `examples/data/`. It does not train or call OPUS-MT.

## Workflow

These are the 2023 GPU scripts. They read and write **hardcoded filenames** in the current working directory. Uncomment the `da→en` conversion before step 2; the checked-in converter only writes `opus-mt-en-da`. Remove the `[:10]` slice in `summary.py` before a full labeling run. Details: [`docs/reproduction.md`](docs/reproduction.md).

### Step 1: Model conversion

Run `Ctranslate_converter.py` to convert Helsinki-NLP OPUS-MT checkpoints with CTranslate2.

```
python Ctranslate_converter.py
```

### Step 2: Translate dataset

Use `translate.py` to translate the Danish news dump into English.

```
python translate.py
```

### Step 3: Extract summary

Run `summary.py` to summarize the translated English articles.

```
python summary.py
```

### Step 4: Translate back to Danish

Use `translate_back.py` to translate those summaries back into Danish. The result is a tagged Danish news file (`id`, `body`, `summary`).

```
python translate_back.py
```

### Fine-tuning the model

Split the labeled CSV into `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, and `datasets/test_dataset.csv` (no split script is in git). Then:

```
python finetune.py
```

### Model evaluation

`use_model.py` prints a few predictions on a public Nordjylland mini split. `eval.py` scores ROUGE and BERTScore on the full public test set. Both load `./small_model` as written, while `finetune.py` saves `./large_model`.

```
python use_model.py
python eval.py
```

## Repository map

```
Ctranslate_converter.py   OPUS-MT → CTranslate2
translate.py              Danish articles → English
summary.py                English T5 news summaries
translate_back.py         English summaries → Danish silver labels
finetune.py               mT5-large on datasets/*.csv
use_model.py              qualitative prints
eval.py                   ROUGE + BERTScore
docs/                     personal notes written after the course
examples/                 stdlib walkthroughs + synthetic CSVs
```

## License

MIT. See [`LICENSE`](LICENSE). Do not commit real news dumps or generated summaries of copyrighted articles; the only sample articles in git are the fictional rows under `examples/data/`.
