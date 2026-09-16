# Personal project notes

This folder documents the 2023 ITU *Advanced Natural Language Processing and Deep Learning* final project that lives in this repository: a Danish news summarizer trained on **automatically generated** article–summary pairs.

The original scripts (`translate.py`, `summary.py`, `translate_back.py`, `finetune.py`, `eval.py`, `use_model.py`, `Ctranslate_converter.py`) are course artifacts. They were written to run on a GPU workstation with local CSV dumps and converted CTranslate2 models. They are **not** a packaged library.

These notes exist so the pipeline can be reread later without reconstructing every hardcoded path from memory.

## Contents

| Document | What it covers |
| --- | --- |
| [pipeline.md](pipeline.md) | End-to-end label-generation and training flow, including file names each script expects |
| [datasets-and-schemas.md](datasets-and-schemas.md) | CSV columns, Hugging Face eval sets, and train/validation/test splits |
| [models-and-conversion.md](models-and-conversion.md) | OPUS-MT, CTranslate2, the English T5 news summarizer, and mT5 |
| [fine-tuning.md](fine-tuning.md) | Tokenization, `Seq2SeqTrainer` settings, and checkpoint layout |
| [evaluation.md](evaluation.md) | ROUGE, BERTScore, qualitative inspection, and metric caveats |
| [hyperparameters.md](hyperparameters.md) | Generation and training knobs copied out of the scripts |
| [reproduction.md](reproduction.md) | Environment, disk, and GPU notes for actually rerunning the 2023 flow |
| [design-notes.md](design-notes.md) | Intentional shortcuts, mismatches between scripts, and things to fix before a rerun |

Runnable, **offline** walkthroughs that do not download models live in [`../examples`](../examples).

## One-paragraph summary of the idea

Danish news articles are long. In 2023 there was no cheap, high-quality Danish abstractive summarizer with gold labels at the scale we wanted. The project therefore:

1. Translates Danish articles to English with Helsinki-NLP OPUS-MT (`da→en`).
2. Summarizes the English text with a T5 model already fine-tuned on English news.
3. Translates those English summaries back to Danish (`en→da`).
4. Treats `(original Danish article, back-translated Danish summary)` as silver training pairs.
5. Fine-tunes multilingual T5 (`google/mt5-large` in the training script) so inference happens entirely in Danish.
6. Scores the result on the public Nordjylland news summarization sets.

The silver labels are noisy. Round-trip translation drops named entities, hedging, and Danish syntax. The point of the project was to measure whether that noise was still useful enough to train a monolingual Danish summarizer.

## Script map

```
Ctranslate_converter.py  →  models/opus-mt-*-ct2
translate.py             →  translated_articles.csv
summary.py               →  summarized_file_ml80_rp5.0.csv
translate_back.py        →  labeled_dataset_ml80_rp5.0.csv
                         ↘  (manual split) datasets/{train,validation,test}_dataset.csv
finetune.py              →  ./large_model
use_model.py             →  printed predictions on a public test split
eval.py                  →  ROUGE + BERTScore on a public test split
```

Column names are not consistent across stages. Read [datasets-and-schemas.md](datasets-and-schemas.md) before writing any new glue code.
