# Script contracts (December 2023)

I/O and side effects of the root Python files, read from the committed source. This is a contract sheet, not a rewrite guide. The examples do not import these modules.

SHA I read: `545fe87` on `main`.

## Shared habits

Every GPU script:

- calls `nltk.download('punkt')` on import (network the first time);
- picks `cuda` if `torch.cuda.is_available()` else `cpu`;
- hard-codes input and output filenames in the module body;
- has no `argparse`;
- writes UTF-8 CSVs without an index.

There is no shared library and no config file.

## `Ctranslate_converter.py`

| | |
| --- | --- |
| Reads | Hugging Face `Helsinki-NLP/opus-mt-en-da` (download) |
| Writes | `models/opus-mt-en-da_ct2/` |
| CLI | none |
| Side effects | Hub download, local conversion |

Commented blocks would convert NLLB-200 3.3B / 600M and `opus-mt-da-en`. **`translate.py` needs the DA→EN directory, which this file does not build as committed.**

## `translate.py`

| | |
| --- | --- |
| Reads | `10000_articles_without_linebreaks.csv` (`id`, `article text`) |
| Model | `models/opus-mt-da-en_ct2` + tokenizer `Helsinki-NLP/opus-mt-da-en` |
| Writes | `translated_articles.csv` (`id`, `body`, `translated`) |
| Budget | 512 tokens; pack at `int(512 * 0.9)` = 460 |
| Extra | NLLB-style `target_prefix=['eng_Latn']` on a Marian model; hypothesis `[1:]` drop |

Long articles are sentence-split, optionally comma-broken, packed, and translated per pack. Packs are joined with spaces.

## `summary.py`

| | |
| --- | --- |
| Reads | `translated_articles.csv` |
| Model | `mrm8488/t5-base-finetuned-summarize-news` |
| Writes | `summarized_file_ml80_rp5.0.csv` (`id`, `body`, `translated`, `summary`) |
| Generate | beams 2, `max_length=80`, `repetition_penalty=5.0`, `length_penalty=1.0` |
| Extra | **`df = pd.read_csv(...)[:10]`** — only ten rows as committed |

Each packed English span gets its own summary; spans are concatenated.

## `translate_back.py`

| | |
| --- | --- |
| Reads | `summarized_file_ml80_rp5.0.csv` |
| Model | `models/opus-mt-en-da_ct2` + tokenizer `Helsinki-NLP/opus-mt-en-da` |
| Writes | `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`) |
| Extra | Same NLLB prefix habit (`dan_Latn`); **no** `split_long_sentence` |

Only `summary` is translated. `body` stays the original Danish article.

## `finetune.py`

| | |
| --- | --- |
| Reads | `datasets/train_dataset.csv`, `validation_dataset.csv`, `test_dataset.csv` (`id`, `body`, `summary`) |
| Model | `google/mt5-large` |
| Writes | trainer dir `mt5-summarize-large/` and `./large_model/` |
| Train | 20 epochs, Adafactor, lr `3e-4`, polynomial decay, warmup 1000, batch 8, fp16, `predict_with_generate` |
| Select | `rouge_1_mid_fmeasure` via deprecated `datasets.load_metric("rouge")` |

Tokenize `body` at 1024 and `summary` at 128, then drop those columns. `test` is loaded and tokenized but never passed to the trainer.

## `use_model.py`

| | |
| --- | --- |
| Reads | `ScandEval/nordjylland-news-summarization-mini` (`input_text`, `target_text`, …) |
| Model | local `small_model/` + tokenizer `google/mt5-small` |
| Writes | stdout, five batches of size 2 |
| Generate | beams 2, `no_repeat_ngram_size=1`, `max_length=128` |

Prints the *dataset* input at index `i` and the *decoded batch* label/pred at position 0. With `batch_size=2` those are not the same row. Qualitative only.

## `eval.py`

| | |
| --- | --- |
| Reads | `alexandrainst/nordjylland-news-summarization` split `test` |
| Model | local `small_model/` + tokenizer `google/mt5-small` |
| Writes | a printed metrics dict |
| Metrics | ROUGE-1/2/L mid F (`datasets.load_metric`) and BERTScore P/R/F1 (`xlm-roberta-large`, `lang='da'`) |

Column names in the script (`input_text`, `target_text`) do not match the public card (`text`, `summary`). Checkpoint directory and tokenizer size do not match `finetune.py` (`large_model` / `mt5-large`). Treat a clean-clone run as blocked until those three lines are aligned.

## Side-effect table

| Script | Hub download | Local weights | Writes CSV | Writes checkpoint |
| --- | --- | --- | --- | --- |
| `Ctranslate_converter.py` | yes | writes ct2 | no | yes |
| `translate.py` | tokenizer | reads ct2 | yes | no |
| `summary.py` | T5 | — | yes | no |
| `translate_back.py` | tokenizer | reads ct2 | yes | no |
| `finetune.py` | mT5-large | writes | no | yes |
| `use_model.py` | mini dataset + tok | reads `small_model` | no | no |
| `eval.py` | full test + metrics | reads `small_model` | no | no |

## Toy equivalents

| 2023 script | Example stand-in |
| --- | --- |
| `translate.py` input CSV | `examples/data/sample_articles.csv` |
| `translate.py` itself | `examples/run_toy_pipeline.py` hop 1 |
| `summary.py` | hop 2 (fixture lookup or lead-N) |
| `translate_back.py` | hop 3 |
| `datasets/*.csv` | `examples/data/splits/` |
| packer | `examples/pack_report.py` |
| schema | `examples/validate_schema.py` |

There is no toy `finetune.py`. Fine-tuning mT5 is out of scope for a stdlib example.
