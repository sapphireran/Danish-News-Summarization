# Script I/O reference

All paths are relative to the repository root. None of these scripts take CLI flags.

## `Ctranslate_converter.py`

| | |
| --- | --- |
| Purpose | Convert a Transformers OPUS-MT checkpoint to CTranslate2 |
| Reads | Hub id `Helsinki-NLP/opus-mt-en-da` (network / cache) |
| Writes | `models/opus-mt-en-da_ct2/` |
| Commented | da→en OPUS-MT and two NLLB sizes |
| Extra deps | `ctranslate2` |

## `translate.py`

| | |
| --- | --- |
| Purpose | Danish articles → English |
| Reads | `10000_articles_without_linebreaks.csv` (`id`, `article text`) |
| Reads | `models/opus-mt-da-en_ct2/`, tokenizer `Helsinki-NLP/opus-mt-da-en` |
| Writes | `translated_articles.csv` (`id`, `body`, `translated`) |
| Device | CTranslate2 `cuda` or `cpu` |
| Chunk budget | `int(512 * 0.9)` OPUS-MT tokens |

## `summary.py`

| | |
| --- | --- |
| Purpose | English articles → English summaries |
| Reads | `translated_articles.csv` |
| Reads | `mrm8488/t5-base-finetuned-summarize-news` |
| Writes | `summarized_file_ml80_rp5.0.csv` (`id`, `body`, `translated`, `summary`) |
| Row filter | **first 10 rows only** |
| Generate | beams 2, max length 80, repetition penalty 5.0 |

## `translate_back.py`

| | |
| --- | --- |
| Purpose | English summaries → Danish summaries |
| Reads | `summarized_file_ml80_rp5.0.csv` |
| Reads | `models/opus-mt-en-da_ct2/`, tokenizer `Helsinki-NLP/opus-mt-en-da` |
| Writes | `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`) |
| Note | Packs with `max_length=512`; `text_max_length` is unused |

## `finetune.py`

| | |
| --- | --- |
| Purpose | Fine-tune `google/mt5-large` on silver pairs |
| Reads | `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, `datasets/test_dataset.csv` |
| Columns | `id`, `body`, `summary` (test split is loaded, not evaluated) |
| Writes | trainer dir `mt5-summarize-large/`, final `./large_model/` |
| Token limits | body 1024, summary 128 |
| Select best | `rouge_1_mid_fmeasure` |

## `use_model.py`

| | |
| --- | --- |
| Purpose | Print a few generations |
| Reads | `ScandEval/nordjylland-news-summarization-mini` test split |
| Reads | tokenizer `google/mt5-small`, weights `small_model/` |
| Writes | stdout |
| Batch size | 2, first 5 batches |

## `eval.py`

| | |
| --- | --- |
| Purpose | Corpus ROUGE + BERTScore |
| Reads | `alexandrainst/nordjylland-news-summarization` test split |
| Reads | tokenizer `google/mt5-small`, weights `small_model/` |
| Writes | stdout metrics dict |
| Eval batch | 64, `dataloader_drop_last=True` |
| BERTScore | `lang='da'`, `xlm-roberta-large` |

## Example scripts (new, stdlib)

| Script | Reads | Writes |
| --- | --- | --- |
| `examples/export_sample_csvs.py` | `examples/corpus.py` | `examples/data/*.csv` |
| `examples/toy_pipeline.py` | `examples/data/*.csv` | stdout report (optional `--json` path) |
| `examples/metrics_demo.py` | labeled + toy predictions | stdout table |
| `examples/inspect_samples.py` | corpus + CSVs | stdout |
| `examples/tests/*` | the above | unittest |

See [examples/README.md](../examples/README.md) for commands.
