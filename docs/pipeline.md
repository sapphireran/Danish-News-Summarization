# Pipeline

This repository is a personal ITU course project from 2023. The goal was to
fine-tune a multilingual T5 model for Danish news summarization when there
was no large public corpus of Danish article/summary pairs that matched the
news domain we wanted.

The workaround is silver labeling:

1. Translate Danish news to English.
2. Summarize the English text with an existing English news model.
3. Translate the summaries back to Danish.
4. Fine-tune mT5 on the original Danish body plus the back-translated summary.

The root scripts are the original course code. They are left in place. This
page describes what they do, which files they expect, and where they are
brittle.

## Stage map

```
Danish news CSV
        |
        |  translate.py
        |  Helsinki-NLP/opus-mt-da-en  (CTranslate2)
        v
translated_articles.csv
        |
        |  summary.py
        |  mrm8488/t5-base-finetuned-summarize-news
        v
summarized_file_ml80_rp5.0.csv
        |
        |  translate_back.py
        |  Helsinki-NLP/opus-mt-en-da  (CTranslate2)
        v
labeled_dataset_ml80_rp5.0.csv
        |
        |  manual split into datasets/{train,validation,test}_dataset.csv
        |  finetune.py
        |  google/mt5-large
        v
./large_model
        |
        |  use_model.py / eval.py
        |  Nordjylland news test sets
        v
printed generations and ROUGE / BERTScore
```

`Ctranslate_converter.py` is a prerequisite, not a data stage. It writes
CTranslate2 model directories under `models/`.

## Why English as a pivot

In 2023 the strongest widely available news summarizers were English. Danish
abstractive models existed, but they were smaller or trained on mixed
domains. The course bet was:

- OPUS-MT is good enough for Danish news prose.
- An English news T5 will produce tighter leads than a zero-shot multilingual
  model.
- Back-translation will leak some English phrasing, but mT5 can still learn
  a usable Danish lead-generation style.

That bet is documented here because it explains several design choices that
look odd if you only read the scripts: the 80-token English summary cap, the
high repetition penalty, and the later evaluation on Nordjylland news rather
than on the silver labels themselves.

## Length handling

OPUS-MT and the English T5 checkpoint both sit near a 512-token window.
Danish newspaper articles are often longer. Every translation and summary
script therefore:

1. Splits the text into sentences.
2. Splits any remaining oversized sentence on commas or hard word boundaries.
3. Packs sentences into batches that stay under `int(512 * 0.9) = 460`.
4. Runs the model once per batch and concatenates the outputs.

The reusable version of that logic lives in
`danish_summarization.chunking`. The examples call it directly so you can see
the batches without downloading models.

`translate_back.py` is slightly different. It packs with `max_length=512`
instead of the 0.9 safety budget, and it does not split oversized sentences
before packing. That is usually fine because the English summaries are short.

## Device selection

The scripts pick CUDA when `torch.cuda.is_available()` is true and CPU
otherwise. CTranslate2 gets the same string: `"cuda"` or `"cpu"`. There is no
Apple MPS path and no multi-GPU data-parallel wrapper.

Fine-tuning mT5-large with `per_device_train_batch_size=8` and `fp16=True`
assumes a single GPU with enough memory for 1024-token inputs. If you only
have a smaller card, lower the batch size or use gradient accumulation. The
course run used the large checkpoint; `use_model.py` and `eval.py` later load
a `small_model` directory, which is the mT5-small experiment that was easier
to inspect.

## File names are part of the interface

The original scripts do not take CLI flags. Paths are constants at the top of
each file:

| Script | Input | Output |
| --- | --- | --- |
| `translate.py` | `10000_articles_without_linebreaks.csv` | `translated_articles.csv` |
| `summary.py` | `translated_articles.csv` | `summarized_file_ml80_rp5.0.csv` |
| `translate_back.py` | `summarized_file_ml80_rp5.0.csv` | `labeled_dataset_ml80_rp5.0.csv` |
| `finetune.py` | `datasets/{train,validation,test}_dataset.csv` | `./large_model` |

The `ml80_rp5.0` suffix records the English summary settings: `max_length=80`
and `repetition_penalty=5.0`. If you change those numbers, rename the files
to match or you will lose track of which silver labels belong to which
generation settings.

## What this pipeline is not

- It is not a production newsroom tool. There is no serving layer, no
  streaming input, and no human review queue.
- It is not a faithful translation-quality study. Translation is a means to
  create labels, not the object of evaluation.
- It does not train on Nordjylland news. That corpus is used afterwards as
  an external check.

See [datasets.md](datasets.md) for column contracts, [translation.md](translation.md)
for the OPUS-MT / CTranslate2 details, and [training-and-eval.md](training-and-eval.md)
for the mT5 recipe.
