# Hyperparameters as committed

Copied from the 2023 files. Not re-tuned. Not recommended. Written
down so a later reader does not have to grep.

## Translation (`translate.py`, `translate_back.py`)

| knob | value |
| --- | --- |
| model (forward) | `models/opus-mt-da-en_ct2` |
| model (back) | `models/opus-mt-en-da_ct2` |
| HF tokenizer names | `Helsinki-NLP/opus-mt-da-en`, `…-en-da` |
| `max_length` | 512 |
| `text_max_length` | `int(512 * 0.9)` = 460  (forward / summary) |
| back-translation pack budget | 512 (see packing note) |
| target prefixes | `eng_Latn` / `dan_Latn` (NLLB style on OPUS) |
| input file (forward) | `10000_articles_without_linebreaks.csv` |
| column read | `article text` |
| output (forward) | `translated_articles.csv` |
| input (back) | `summarized_file_ml80_rp5.0.csv` |
| output (back) | `labeled_dataset_ml80_rp5.0.csv` |

## English summariser (`summary.py`)

| knob | value |
| --- | --- |
| model | `mrm8488/t5-base-finetuned-summarize-news` |
| `max_length` (generate) | 80 |
| `repetition_penalty` | 5.0 |
| `length_penalty` | 1.0 |
| `num_beams` | 2 |
| `early_stopping` | True |
| rows actually scored | `df[:10]` |

The output filename encodes the generate knobs: `ml80_rp5.0`.

## Fine-tune (`finetune.py`)

| knob | value |
| --- | --- |
| model | `google/mt5-large` |
| input max | 1024 |
| label max | 128 |
| generate `min_length` | 9 |
| generate `max_length` | 128 |
| `length_penalty` | 0.8 |
| `no_repeat_ngram_size` | 3 |
| `num_beams` | 4 |
| `dropout_rate` | 0.1 |
| epochs | 20 |
| learning rate | 3e-4 |
| scheduler | polynomial |
| warmup | 1000 |
| optim | adafactor |
| weight decay | 0.01 |
| train / eval batch | 8 |
| fp16 | True |
| best-model metric | `rouge_1_mid_fmeasure` |
| `save_total_limit` | 1 |
| output | `mt5-summarize-large` then `./large_model` |

## Evaluation (`eval.py`, `use_model.py`)

| knob | eval.py | use_model.py |
| --- | --- | --- |
| base tokenizer name | `google/mt5-small` | `google/mt5-small` |
| local weights | `small_model` | `small_model` |
| dataset | `alexandrainst/nordjylland-news-summarization` test | `ScandEval/nordjylland-news-summarization-mini` test |
| eval batch | 64 | 2 (display) |
| generate beams | trainer default | 2 |
| `no_repeat_ngram_size` | (none set) | 1 |
| label max at tokenize | 128 | 180 |
| extra metrics | ROUGE + BERTScore `da` / `xlm-roberta-large` | printed strings only |

`finetune.py` trains **large** and writes `./large_model`.
`eval.py` loads **`small_model`**. That mismatch is in
[script-archaeology.md](script-archaeology.md).
