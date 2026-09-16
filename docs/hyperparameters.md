# Hyperparameter log

Values copied from the December 2023 scripts. Nothing here is the output of a proper sweep. Comments in `finetune.py` show I knew the scheduler could be `linear` / `cosine` / `polynomial` and left `polynomial` selected.

I did not record GPU model, CUDA version, random seeds, or wall-clock time.

## Translation (both hops)

| Name | `translate.py` | `translate_back.py` |
| --- | --- | --- |
| Marian max length | 512 | 512 |
| Pack budget | `int(512 * 0.9)` = 460 | function is passed **512**, not 460 |
| Long-sentence breaker | yes (`split_long_sentence`) | no |
| CTranslate2 `beam_size` | library default (2) | library default (2) |
| CTranslate2 `compute_type` | unset | unset |
| Target prefix | `eng_Latn` | `dan_Latn` |
| Prefix stripped | first hypothesis token | first hypothesis token |
| Batching | one packed sentence-list at a time | one summary at a time |

I never set CTranslate2 `inter_threads` / `intra_threads`. Throughput was “let the GPU cook overnight,” not a tuned serving stack.

## English summarizer (`summary.py`)

| Name | Value | Why I remember setting it |
| --- | --- | --- |
| Checkpoint | `mrm8488/t5-base-finetuned-summarize-news` | news-domain, base-sized |
| Encoder cap | 512 | T5 position length |
| `num_beams` | 2 | faster than 4 on 10k packs |
| `max_length` | 80 | encoded in the output filename |
| `repetition_penalty` | 5.0 | encoded in the output filename; high on purpose |
| `length_penalty` | 1.0 | default-ish |
| `early_stopping` | True | stop when all beams hit EOS |
| Map-reduce | summarize each pack, join with space | no second pass |
| Frame slice | `[:10]` | smoke test; dangerous if forgotten |

The filename `summarized_file_ml80_rp5.0.csv` is the only surviving sweep label. I do not have `ml60`, `ml100`, `rp2.0`, or `rp3.0` artifacts in this repo. If those CSVs existed, they lived on a course machine.

## Student model (`finetune.py`)

### Architecture / generate config (`AutoConfig.from_pretrained`)

| Name | Value |
| --- | --- |
| Base | `google/mt5-large` |
| `min_length` | 9 |
| `max_length` | 128 |
| `length_penalty` | 0.8 |
| `no_repeat_ngram_size` | 3 |
| `num_beams` | 4 |
| `dropout_rate` | 0.1 |

`min_length=9` was a hedge against empty or three-word dumps. `length_penalty=0.8` nudges shorter than raw beam search. `no_repeat_ngram_size=3` is the conventional “block repeated trigrams” setting from CNN/DM recipes.

### Tokenization

| Name | Value |
| --- | --- |
| Source max | 1024 |
| Target max | 128 |
| Batch map size | 128 rows |
| Columns dropped | `id`, `body`, `summary` |

1024 source tokens is generous for mT5-large on a single 16–24 GB card at batch 8. I accepted slow steps rather than losing the tail of long news pieces. The label cap 128 is tighter than `use_model.py`’s 180-token label tokenizer cap.

### `Seq2SeqTrainingArguments`

| Name | Value |
| --- | --- |
| `output_dir` | `mt5-summarize-large` |
| `log_level` | `error` |
| `num_train_epochs` | 20 |
| `learning_rate` | `3e-4` |
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
| `save_steps` | 100 (redundant with epoch saves) |
| `logging_steps` | 250 |
| `push_to_hub` | False |
| `fp16` | True |
| `load_best_model_at_end` | True |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` |
| `save_total_limit` | 1 |

Effective batch size is 8. There is no `seed` argument, so dropout and data shuffling are not recoverable.

Adafactor + `3e-4` + polynomial + 1000 warmup is a T5-family starting point, not something I grid-searched. 20 epochs with `save_total_limit=1` means I only kept the best-so-far by ROUGE-1. If ROUGE-1 preferred an early overfit-on-lead checkpoint, that is what `./large_model` is.

`log_level=error` hid step loss. I would not do that again; I want the loss curve even for a course project.

### Optimizer notes

Adafactor is the T5 paper’s friend: less memory than AdamW on a 1.2B model. `weight_decay=0.01` with Adafactor in Transformers is easy to misconfigure across versions (some versions ignore it or apply it differently). I did not verify the 2023 Transformers behavior.

## Qualitative decoder (`use_model.py`)

| Name | Value |
| --- | --- |
| `num_beams` | 2 |
| `num_return_sequences` | 1 |
| `no_repeat_ngram_size` | 1 |
| `remove_invalid_values` | True |
| `max_length` | 128 |
| dataloader batch | 2 |
| printed batches | 5 |

`no_repeat_ngram_size=1` is not a training hyperparameter. It is a demo-time knob and it changes the system.

## Quantitative decoder (`eval.py`)

| Name | Value |
| --- | --- |
| `per_device_eval_batch_size` | 64 |
| `evaluation_strategy` | `epoch` (unused, no train) |
| `predict_with_generate` | True |
| `dataloader_drop_last` | True |
| BERTScore model | `xlm-roberta-large` |
| BERTScore lang | `da` |
| Source / label truncate | 1024 / 128 |

Eval batch 64 is “cluster GPU” thinking. BERTScore with XLM-R large over 4k pairs is the slow tail of `compute_metrics`, not the generate pass.

## What I would sweep if I reran (personal, bounded)

I would not sweep everything. I would sweep these four, one at a time, silver-val ROUGE-1 plus 20-row human ENT/HAL:

1. T5 `max_length` ∈ {40, 80, 128} — does a shorter silver label match Nordjylland better?
2. T5 `repetition_penalty` ∈ {1.5, 2.5, 5.0} — 5.0 always felt like a panic setting.
3. Student `num_train_epochs` ∈ {3, 5, 10} — 20 is a lot if the silver set is small.
4. Student `learning_rate` ∈ {1e-4, 3e-4} with a fixed seed.

I would freeze Marian and CTranslate2 during that sweep so I am not retuning three hops at once.
