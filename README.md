# Danish News Summarization

Personal ITU course project (December 2023). This repository is **not** work code and does not contain employer, client, or proprietary material.

**Course:** Advanced Natural Language Processing and Deep Learning, IT University of Copenhagen, 2023  
**Author:** Sapphire Ran (`pang990801`)  
**License:** MIT  
**Original commit window:** 16–18 December 2023

The project builds a Danish news summarizer by first manufacturing silver labels: Danish articles are translated to English, summarized by an English news T5, then translated back to Danish. Those pairs are used to fine-tune multilingual T5 (`mT5`). Held-out evaluation is intended against the public Nordjylland News summarization set.

The 2023 tree is a lab notebook that got the pipeline running, not a packaged research release. Numeric scores, raw articles, converted CTranslate2 models, and fine-tuned weights were never committed. This documentation pass (September 2026) records what the scripts actually do, how I meant to evaluate them, and what I would not trust without a rerun.

## Why this approach

In late 2023, Danish abstractive summarization data existed (DaNewsroom, Nordjylland News) but I wanted a course-sized experiment that did **not** start from human Danish summaries. The question was:

> If I only have unlabeled Danish news text, can I borrow a strong English summarizer through translation and still get a usable Danish `mT5`?

That is classic *translate–summarize–translate* silver labeling (sometimes called cross-lingual pivot summarization). It is cheap, it is leaky, and it is a good teaching problem: every hop can inject error, and automatic metrics on a *different* human-written test set will punish style mismatch even when the model is fluent.

I chose OPUS-MT for the two Danish↔English hops because Marian models were small enough to convert with CTranslate2 and run over thousands of articles. I chose `mrm8488/t5-base-finetuned-summarize-news` as the English pivot summarizer because it was already specialized for news, not generic T5. I chose `google/mt5-large` for the final Danish model because mT5 had seen Danish in pretraining and Seq2SeqTrainer plus ROUGE was the course-default evaluation loop.

## Repository map

| Path | Role |
| --- | --- |
| [`Ctranslate_converter.py`](Ctranslate_converter.py) | Convert a Hugging Face Marian/OPUS checkpoint to CTranslate2. |
| [`translate.py`](translate.py) | Danish article → English (`opus-mt-da-en`). |
| [`summary.py`](summary.py) | English article → English summary (`t5-base` news model). |
| [`translate_back.py`](translate_back.py) | English summary → Danish (`opus-mt-en-da`). |
| [`finetune.py`](finetune.py) | Fine-tune `google/mt5-large` on the silver CSV splits. |
| [`use_model.py`](use_model.py) | Qualitative generation on a small ScandEval split. |
| [`eval.py`](eval.py) | Quantitative ROUGE + BERTScore via `Seq2SeqTrainer.evaluate()`. |
| [`docs/`](docs/README.md) | Pipeline, evaluation protocol, reproduction, known issues. |
| [`notes/`](notes/README.md) | Personal retrospective and metric notes. |
| [`requirements.txt`](requirements.txt) | Unpinned 2023-era Python dependencies. |

## End-to-end workflow

Run the steps in order on a machine with a GPU if you can. The original scripts assume CUDA when available and fall back to CPU.

```text
Danish articles CSV
        │
        ▼
Ctranslate_converter.py     →  models/opus-mt-*-ct2
        │
        ▼
translate.py                →  translated_articles.csv
        │
        ▼
summary.py                  →  summarized_file_ml80_rp5.0.csv
        │
        ▼
translate_back.py           →  labeled_dataset_ml80_rp5.0.csv
        │
        ▼
(manual train/val/test split under datasets/)
        │
        ▼
finetune.py                 →  ./large_model
        │
        ├── use_model.py    →  printed examples
        └── eval.py         →  ROUGE + BERTScore dict
```

### Step 1 — Convert translation models

```bash
python Ctranslate_converter.py
```

The file as committed only converts `Helsinki-NLP/opus-mt-en-da` into `models/opus-mt-en-da_ct2`. The Danish→English converter, plus the NLLB-200 experiments, are left commented. Uncomment the `opus-mt-da-en` block before running `translate.py`, or convert that model by hand with the same `TransformersConverter` API.

### Step 2 — Translate Danish articles to English

```bash
python translate.py
```

Reads `10000_articles_without_linebreaks.csv` (`id`, `article text`) and writes `translated_articles.csv` (`id`, `body`, `translated`). Long articles are sentence-split with NLTK, then packed into chunks under ~90% of the 512-token Marian limit.

### Step 3 — Summarize the English side

```bash
python summary.py
```

Reads `translated_articles.csv` and writes `summarized_file_ml80_rp5.0.csv`. Generation uses beam size 2, `max_length=80`, and `repetition_penalty=5.0` (the `ml80_rp5.0` suffix). **As committed, the script slices the frame to the first 10 rows.** That is a leftover smoke-test guard; remove `[:10]` for a full run.

### Step 4 — Translate summaries back to Danish

```bash
python translate_back.py
```

Reads the English summaries and writes `labeled_dataset_ml80_rp5.0.csv` with columns `id`, `body` (original Danish article), `summary` (Danish silver label).

### Step 5 — Fine-tune mT5

```bash
python finetune.py
```

Expects `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, and `datasets/test_dataset.csv` with columns `id`, `body`, `summary`. Trains `google/mt5-large` for 20 epochs with Adafactor, polynomial decay, and ROUGE-1 mid F as the checkpoint metric. Saves `./large_model`.

### Step 6 — Inspect and evaluate

```bash
python use_model.py
python eval.py
```

`use_model.py` prints a handful of generations against `ScandEval/nordjylland-news-summarization-mini`. `eval.py` runs trainer-side metrics against `alexandrainst/nordjylland-news-summarization` test. See [`docs/evaluation-notes.md`](docs/evaluation-notes.md) before treating those two scripts as the same experiment.

## Data that is not in git

| Artifact | Expected locally | Why it is absent |
| --- | --- | --- |
| `10000_articles_without_linebreaks.csv` | Source Danish news dump | Large, not licensed in this repo |
| `translated_articles.csv` | DA→EN output | Regenerable, large |
| `summarized_file_ml80_rp5.0.csv` | EN summaries | Regenerable |
| `labeled_dataset_ml80_rp5.0.csv` | Silver DA pairs | Regenerable |
| `datasets/*.csv` | Fine-tune splits | Never committed |
| `models/*_ct2` | CTranslate2 weights | Downloaded/converted |
| `small_model/`, `large_model/`, `mt5-summarize-large/` | Fine-tuned checkpoints | Too large for git |

The public evaluation set *is* downloadable:

- [alexandrainst/nordjylland-news-summarization](https://huggingface.co/datasets/alexandrainst/nordjylland-news-summarization) — TV2 Nord article/summary pairs, CC0-1.0, 75,219 / 4,178 / 4,178.
- `ScandEval/nordjylland-news-summarization-mini` — smaller split used only by `use_model.py`.

Those human summaries are the **evaluation** distribution. They are not the training labels this pipeline creates.

## Models referenced in code

| Stage | Checkpoint | Notes |
| --- | --- | --- |
| DA→EN | `Helsinki-NLP/opus-mt-da-en` | Marian; Tatoeba da-en BLEU ~63.6 in the model card |
| EN→DA | `Helsinki-NLP/opus-mt-en-da` | Marian bilingual, not NLLB |
| EN summarize | `mrm8488/t5-base-finetuned-summarize-news` | News-domain English T5 |
| Fine-tune | `google/mt5-large` | ~1.2B encoder–decoder |
| Eval tokenizer / qualitative script | `google/mt5-small` | **Does not match** the fine-tune checkpoint size |
| BERTScore (eval) | `xlm-roberta-large`, `lang='da'` | Multilingual semantic overlap |

Commented-out alternatives in the converter: `facebook/nllb-200-3.3B` and `facebook/nllb-200-distilled-600m`. The translate scripts still pass NLLB-style `dan_Latn` / `eng_Latn` target prefixes into OPUS-MT. That is documented as a live footgun in [`docs/known-issues.md`](docs/known-issues.md).

## Evaluation in one paragraph

Training-time selection uses ROUGE-1 mid F on the silver validation CSV. Final reporting in `eval.py` was meant to be ROUGE-1/2/L mid F plus BERTScore P/R/F1 on Nordjylland test, with NLTK sentence tokenization so ROUGE-Lsum-style newlines exist. I never committed a score table. Treat any number you see elsewhere as unreproducible until this tree is rerun with the field-name and checkpoint-size issues fixed. Full protocol: [`docs/evaluation-notes.md`](docs/evaluation-notes.md).

## Documentation index

- [Documentation home](docs/README.md)
- [Pipeline, file by file](docs/pipeline.md)
- [Silver-labeling method](docs/silver-labeling.md)
- [Evaluation notes](docs/evaluation-notes.md)
- [Hyperparameter log](docs/hyperparameters.md)
- [Reproduction](docs/reproduction.md)
- [Known issues](docs/known-issues.md)
- [Personal notes index](notes/README.md)
- [2023 retrospective](notes/personal-retrospective-2023.md)
- [Metric notes](notes/metric-notes.md)
- [Models and data catalog](notes/models-and-data.md)
- [Error-analysis plan](notes/error-analysis-plan.md)
- [Run log template](notes/run-log-template.md)

## Status of this tree

Honest snapshot, not a sales pitch:

- The idea is intact and still a reasonable course project.
- Several scripts disagree with each other (checkpoint name, tokenizer size, dataset column names, converter outputs).
- `summary.py` will not process the 10k dump until the `[:10]` slice is removed.
- There is no `requirements` pin from 2023, no config file, and no recorded GPU or CUDA version.
- I am expanding **documentation and personal notes only**. The Python remains the December 2023 lab code.

## License

MIT. See [LICENSE](LICENSE). Third-party models and datasets keep their own licenses (OPUS-MT, mT5, T5, Nordjylland CC0, etc.).
