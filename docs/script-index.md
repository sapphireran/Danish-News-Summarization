# Script-by-script notes

Personal reread of the seven Python files in the repo root. Line references are approximate; the files are short.

## `Ctranslate_converter.py`

A list of `TransformersConverter` constructions. Only `Helsinki-NLP/opus-mt-en-da` → `models/opus-mt-en-da_ct2` is live.

Commented blocks:

- NLLB 3.3B and 600M distilled (earlier pivot idea)
- `opus-mt-da-en` (required by `translate.py`)

There is no CLI, no quantization flag, no existence check. Re-running overwrites the output directory if CTranslate2 allows it; some versions refuse a non-empty dest.

**First edit on a rerun:** uncomment the `da-en` pair.

## `translate.py`

The heaviest labeling script.

| Lines (approx) | What |
| --- | --- |
| 14–18 | Hardcoded `10000_articles_without_linebreaks.csv` → `translated_articles.csv` |
| 20–22 | Reads `article text` and `id` |
| 28–29 | CTranslate2 translator + HF tokenizer for `opus-mt-da-en` |
| 32–38 | `translate()` with NLLB-style `target_prefix` and `hypotheses[0][1:]` |
| 41–64 | `split_long_sentence` (character accumulator) |
| 67–100 | `split_into_sentences` (token-accurate packing) |
| 103–112 | `translate_article` joins packs with spaces |
| 116–127 | Full-file loop, writes `id, body, translated` |

`src_lang='dan_Latn'` is passed to `from_pretrained` and to `translate()`, but Marian tokenizers ignore it. Leftover from NLLB.

`nltk.download('punkt')` runs on every invocation. Fine on a workstation; noisy in a tight loop of experiments.

## `summary.py`

Same packing idea, T5 instead of CTranslate2.

| Detail | Value |
| --- | --- |
| Input | `translated_articles.csv` |
| Slice | `[:10]` |
| Model | `mrm8488/t5-base-finetuned-summarize-news` |
| Decode | beams 2, max 80, repetition 5.0 |
| Output | `summarized_file_ml80_rp5.0.csv` |

`split_into_sentences` and `split_long_sentence` are copies, not imports. `split_article` / `sentences_to_text` are thin wrappers so each 512-token English pack can be summarized independently.

The T5 checkpoint may expect a `summarize:` prefix. The script does not add one. If a rerun looks like it is copying the article, try the prefix.

## `translate_back.py`

Slimmer than `translate.py`:

- No `split_long_sentence` (summaries are short)
- Packs with `max_length` 512, not `text_max_length` 460
- Drops the English `translated` column
- Still has NLLB prefixes and `[1:]`

Output `labeled_dataset_ml80_rp5.0.csv` is the silver-label file.

## `finetune.py`

Hugging Face `Seq2SeqTrainer` on `google/mt5-large`.

Loads three CSVs, tokenizes to 1024 / 128, trains 20 epochs, Adafactor, fp16, ROUGE-1 mid F for `load_best_model_at_end`, writes `./large_model`.

Oddities worth remembering:

- `test` split is loaded and ignored
- tokenizer is not saved next to the weights
- `datasets.load_metric("rouge")` is the old API
- no seed
- `save_steps=100` is inert under `save_strategy="epoch"`

## `use_model.py`

Qualitative decoder for `./small_model` on `ScandEval/nordjylland-news-summarization-mini`.

Prints five batches of size 2. The displayed `input_text` uses dataset index `i`, not `i * batch_size`. Batch 0 is aligned; later batches are not.

`no_repeat_ngram_size=1` is much stricter than the training config (`3`).

Gold labels are tokenized to 180 tokens here, 128 in `eval.py`.

## `eval.py`

`Seq2SeqTrainer.evaluate()` on `alexandrainst/nordjylland-news-summarization` test, batch 64, `dataloader_drop_last=True`.

ROUGE keys become `rouge_rouge1_mid_fmeasure` because of an extra prefix. BERTScore uses `xlm-roberta-large`.

`evaluate` is imported and unused; `datasets.load_metric` is what actually runs.

## What is *not* a script

There is no `split_dataset.py`, no `requirements` pin from 2023, no argparse, and no shared `text_chunking` module. The examples folder adds the last of those for documentation only; the course files still contain their own copies.
