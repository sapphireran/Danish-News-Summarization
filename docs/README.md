# Documentation index

These notes describe the **2023 ITU course implementation** in this repository: a Danish news summarizer trained on silver labels produced by a Danish → English → summarize → Danish loop.

They are personal project notes, not a paper or a product spec. Script names, CSV columns, and hyperparameters below are taken from the Python files in the repo root.

## Start here

| Doc | What it covers |
| --- | --- |
| [01-pipeline.md](01-pipeline.md) | Stage diagram, artifacts, and which script owns each hop |
| [02-datasets.md](02-datasets.md) | Column schemas, expected filenames, and how to split for `finetune.py` |
| [03-translation.md](03-translation.md) | CTranslate2 conversion, OPUS-MT models, sentence packing |
| [04-summarization.md](04-summarization.md) | English T5 summarizer, chunking, generate() settings |
| [05-training.md](05-training.md) | mT5 tokenization, trainer args, checkpoint layout |
| [06-evaluation.md](06-evaluation.md) | `use_model.py` vs `eval.py`, ROUGE, BERTScore, external test sets |
| [07-hyperparameters.md](07-hyperparameters.md) | One table of every numeric default in the scripts |
| [08-limitations-and-ethics.md](08-limitations-and-ethics.md) | Silver-label risk, translationese, news-domain bias |
| [09-reproduction.md](09-reproduction.md) | Hardware assumptions, caches, and a checklist |

Companion runnable material lives in [`../examples/`](../examples/README.md).

## Design in one paragraph

Danish abstractive summarization data was thin for a single-semester project. English news summarizers were already strong. The compromise: machine-translate Danish articles, summarize in English, translate the summary back, then teach a multilingual encoder-decoder to map Danish articles to those Danish silver summaries. At test time the fine-tuned mT5 reads Danish and writes Danish — no pivot.

## Script map

```
Ctranslate_converter.py
        │  writes models/opus-mt-en-da_ct2
        │  (da-en conversion is commented out — enable it)
        ▼
10000_articles_without_linebreaks.csv
        │  translate.py
        ▼
translated_articles.csv          (id, body, translated)
        │  summary.py
        ▼
summarized_file_ml80_rp5.0.csv   (id, body, translated, summary)
        │  translate_back.py
        ▼
labeled_dataset_ml80_rp5.0.csv   (id, body, summary)
        │  manual train/val/test split
        ▼
datasets/{train,validation,test}_dataset.csv
        │  finetune.py
        ▼
./large_model   +   mt5-summarize-large/
        │
        ├── use_model.py   (qualitative, small_model + ScandEval mini)
        └── eval.py        (quantitative, small_model + Nordjylland test)
```

`use_model.py` and `eval.py` load `small_model`, while `finetune.py` saves `./large_model`. If you only ran the large trainer, either point those scripts at `./large_model` or fine-tune `google/mt5-small` into `small_model`.

## Conventions used in these docs

- **Body** means the original Danish article text.
- **Translated** means the English pivot of that article.
- **Summary** means a short abstract. After `summary.py` it is English; after `translate_back.py` it is Danish.
- **Silver labels** means automatically generated targets, not journalist-written gold.
- Length limits are **tokenizer tokens**, not whitespace words, unless a function is clearly counting characters (the long-sentence splitter in `translate.py` / `summary.py` mixes both — see [03-translation.md](03-translation.md)).
