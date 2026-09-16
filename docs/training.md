# Training

`finetune.py` is a straightforward `Seq2SeqTrainer` loop on silver
Danish pairs. This page documents the hyperparameters **as they appear
in the file**, plus the knobs that are easy to get wrong when you
revisit the script years later.

## Data

```python
train_dataset      = load_dataset('csv', data_files='datasets/train_dataset.csv')['train']
validation_dataset = load_dataset('csv', data_files='datasets/validation_dataset.csv')['train']
test_dataset       = load_dataset('csv', data_files='datasets/test_dataset.csv')['train']
```

Required columns: `id`, `body`, `summary` (see [dataset.md](dataset.md)).
`id` is dropped after tokenization; it never enters the loss.

Tokenization:

| field | max_length | note |
| --- | --- | --- |
| `body` | 1024 | mT5 can go longer than the 512-token translators |
| `summary` | 128 | matches `generation_max_length` |

A body longer than 1024 tokens is truncated from the **end**. For
inverted-pyramid news that is usually acceptable (lede survives). For
a feature that buries the news, it is not — chunk-and-stitch at
fine-tune time if you see many `text_len > 1024` rows.

## Optimiser and schedule

| argument | value in `finetune.py` |
| --- | --- |
| `num_train_epochs` | 20 |
| `learning_rate` | `3e-4` |
| `lr_scheduler_type` | `polynomial` |
| `warmup_steps` | 1000 |
| `optim` | `adafactor` |
| `weight_decay` | 0.01 |
| `per_device_train_batch_size` | 8 |
| `per_device_eval_batch_size` | 8 |
| `gradient_accumulation_steps` | 1 |
| `fp16` | True |
| `predict_with_generate` | True |
| `generation_max_length` | 128 |
| `evaluation_strategy` / `save_strategy` | `epoch` |
| `load_best_model_at_end` | True |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` |
| `save_total_limit` | 1 |
| `push_to_hub` | False |

Adafactor + a relatively high `3e-4` is the classic T5 / mT5 recipe.
If you switch to AdamW, drop the learning rate by about 10×.

20 epochs on a 10k-pair silver set is a lot. Watch the validation
ROUGE-1; if it peaks around epoch 4–8 and then the model starts
copying training calques, cut `num_train_epochs` or raise dropout.

## Metrics inside the trainer

`compute_metrics` decodes predictions, replaces `-100` labels with the
pad id, sentence-tokenizes both sides with NLTK, and calls
`datasets.load_metric("rouge")`.

It reports only the **mid F-measure** for ROUGE-1/2/L. That is the
value `Seq2SeqTrainer` uses to pick the best checkpoint. See
[evaluation.md](evaluation.md) for the fuller BERTScore suite in
`eval.py`, which does **not** run during training.

`datasets.load_metric` is deprecated. Current Hugging Face code uses
`evaluate.load("rouge")`. The behaviour is the same; the import is not.
`eval.py` already imports `evaluate` but still calls `load_metric`.

NLTK `punkt` must be present on the training box or `compute_metrics`
will raise in the first evaluation pass — i.e. after a full epoch.

## Saving

After `trainer.train()` the script writes `./large_model` via
`save_pretrained`, unwrapping `model.module` if a `DataParallel` wrap
is present. The *best* checkpoint according to ROUGE-1 also lives
under `mt5-summarize-large/` because `load_best_model_at_end=True`.
Copy the one you actually want to `large_model/` or `small_model/`
explicitly; do not assume the last epoch is the best.

## Practical run notes

- **CPU:** do not bother. The examples exist so you can learn the
  pipeline without this script.
- **Single 16 GB GPU:** drop to `google/mt5-base` or `mt5-small`,
  `per_device_train_batch_size=2`, `gradient_accumulation_steps=4`,
  and consider `max_length=768` on the encoder.
- **Tokenizer / model mismatch:** keep `model_name` and the folder you
  later load in `use_model.py` / `eval.py` in lockstep.
- **Hub datasets vs silver CSV:** `finetune.py` cannot read
  Nordjylland's `input_text` / `target_text` without a rename.

## What this fine-tune cannot fix

mT5 will imitate the silver labels, including their systematic errors.
If OPUS-MT consistently mistranslates a municipal name, the fine-tuned
model will treat that mistranslation as the Danish target style. Clean
or filter the CSV before you spend the 20 epochs.
