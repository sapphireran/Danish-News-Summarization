# Hyperparameter reference

Numbers below are the defaults **as written in the repo root scripts**, not suggested sweeps. YAML twins live in `examples/configs/` so you can diff a future experiment against this page.

## Translation (`translate.py`, `translate_back.py`)

| Name | translate.py | translate_back.py |
| --- | --- | --- |
| `max_length` | 512 | 512 |
| `text_max_length` | 460 (`int(512 * 0.9)`) | 460 (computed; packer uses 512) |
| CTranslate2 device | CUDA if available else CPU | same |
| Tokenizer | `Helsinki-NLP/opus-mt-da-en` | `Helsinki-NLP/opus-mt-en-da` |
| `src_lang` passed to `from_pretrained` | `dan_Latn` | `eng_Latn` |
| `target_prefix` per sentence | `eng_Latn` | `dan_Latn` |
| Long-sentence splitter | yes (character heuristic) | no |
| Corpus-level batch size | 1 article | 1 summary |

## English summarization (`summary.py`)

| Name | Value |
| --- | --- |
| Model | `mrm8488/t5-base-finetuned-summarize-news` |
| Encoder / pack limit | 512 |
| `num_beams` | 2 |
| `max_length` (decoder, per chunk) | 80 |
| `repetition_penalty` | 5.0 |
| `length_penalty` | 1.0 |
| `early_stopping` | True |
| DataFrame slice | first 10 rows |
| Output name | `summarized_file_ml80_rp5.0.csv` |

## Fine-tune (`finetune.py`)

| Name | Value |
| --- | --- |
| `model_name` | `google/mt5-large` |
| Source `max_length` | 1024 |
| Target `max_length` | 128 |
| Map `batch_size` | 128 |
| `min_length` (config) | 9 |
| `max_length` (config generate) | 128 |
| `length_penalty` | 0.8 |
| `no_repeat_ngram_size` | 3 |
| `num_beams` | 4 |
| `dropout_rate` | 0.1 |
| `output_dir` | `mt5-summarize-large` |
| `num_train_epochs` | 20 |
| `learning_rate` | 0.0003 |
| `lr_scheduler_type` | `polynomial` |
| `warmup_steps` | 1000 |
| `optim` | `adafactor` |
| `weight_decay` | 0.01 |
| `per_device_train_batch_size` | 8 |
| `per_device_eval_batch_size` | 8 |
| `gradient_accumulation_steps` | 1 |
| `evaluation_strategy` | `epoch` |
| `save_strategy` | `epoch` |
| `predict_with_generate` | True |
| `generation_max_length` | 128 |
| `save_steps` | 100 (ignored with epoch save) |
| `logging_steps` | 250 |
| `push_to_hub` | False |
| `fp16` | True |
| `load_best_model_at_end` | True |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` |
| `save_total_limit` | 1 |
| Final `save_pretrained` | `./large_model` |

## Qualitative generate (`use_model.py`)

| Name | Value |
| --- | --- |
| Local weights | `small_model` |
| Hub tokenizer / config name | `google/mt5-small` |
| Dataset | `ScandEval/nordjylland-news-summarization-mini` `test` |
| Source tok cap | 1024 |
| Label tok cap | 180 |
| DataLoader `batch_size` | 2 |
| Printed batches | 5 |
| `num_beams` | 2 |
| `num_return_sequences` | 1 |
| `no_repeat_ngram_size` | 1 |
| `remove_invalid_values` | True |
| `max_length` | 128 |

## Quantitative eval (`eval.py`)

| Name | Value |
| --- | --- |
| Local weights | `small_model` |
| Hub tokenizer name | `google/mt5-small` |
| Dataset | `alexandrainst/nordjylland-news-summarization` `test` |
| Source tok cap | 1024 |
| Label tok cap | 128 |
| `per_device_eval_batch_size` | 64 |
| `dataloader_drop_last` | True |
| `predict_with_generate` | True |
| ROUGE | `datasets.load_metric("rouge")`, aggregator on |
| BERTScore model | `xlm-roberta-large` |
| BERTScore `lang` | `da` |

## Knobs that are worth sweeping (if you continue the project)

Not implemented — notes only:

1. **Teacher `max_length`** 80 vs 128 vs 160. Directly changes silver verbosity and how often mT5 truncation bites.
2. **Teacher `repetition_penalty`** 5.0 is extreme. 1.5–2.5 is the usual news-T5 range.
3. **Chunk vs. truncate.** Truncating the English article to 512 and summarizing once gives a more "lede-like" teacher; chunk-and-join gives broader coverage.
4. **mT5 size.** `mt5-small` for iteration, `mt5-large` for the 2023 final run.
5. **`no_repeat_ngram_size` at demo time.** Use 3, not 1, unless you are debugging loops.
6. **Eval batch 64** on mT5-large + generate will OOM. Drop to 4–8 if you point `eval.py` at `./large_model`.
