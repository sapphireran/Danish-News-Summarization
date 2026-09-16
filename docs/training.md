# Fine-tuning notes

`finetune.py` fine-tunes `google/mt5-large` with Hugging Face
`Seq2SeqTrainer`. The numbers below are transcribed from the committed
script, not from a sweep.

## Data

```
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

Each file must have `id`, `body`, `summary`. Tokenization truncates the
article at 1024 tokens and the summary at 128. The test split is loaded
into the `DatasetDict` but never passed to `Seq2SeqTrainer`; only
`train` and `validation` are used. Held-out scoring after training is
`eval.py`'s job, and that script reads Nordjylland, not this test CSV.

## Generation config baked into `AutoConfig`

| Key | Value | Intent |
| --- | --- | --- |
| `min_length` | 9 | Avoid empty or two-word dumps |
| `max_length` | 128 | Match the label tokenizer ceiling |
| `length_penalty` | 0.8 | Mild preference for shorter beams |
| `no_repeat_ngram_size` | 3 | Limit repeated news stock phrases |
| `num_beams` | 4 | |
| `dropout_rate` | 0.1 | |

## Trainer

| Key | Value |
| --- | --- |
| `output_dir` | `mt5-summarize-large` |
| `num_train_epochs` | 20 |
| `learning_rate` | `3e-4` |
| `lr_scheduler_type` | `polynomial` |
| `warmup_steps` | 1000 |
| `optim` | `adafactor` |
| `weight_decay` | 0.01 |
| `per_device_train_batch_size` | 8 |
| `fp16` | `True` |
| `evaluation_strategy` / `save_strategy` | `epoch` |
| `load_best_model_at_end` | `True` |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` |
| `save_total_limit` | 1 |
| `push_to_hub` | `False` |

Adafactor plus a relatively high `3e-4` learning rate was a common mT5
recipe at the time (the official mT5 paper also uses Adafactor).
`fp16=True` assumes a CUDA GPU; a CPU or Apple MPS run needs that flag
turned off.

After `trainer.train()` the script writes `./large_model`. `use_model.py`
and `eval.py` load `small_model` instead. That mismatch is easy to miss:
a successful large-model train does not automatically become the
checkpoint the eval scripts look for. Either point those scripts at
`./large_model` or copy / export a distilled or separately trained
`small_model`.

## Metrics inside the trainer

`compute_metrics` decodes beams, splits both prediction and reference
with `nltk.sent_tokenize`, then calls `datasets.load_metric("rouge")`.
It stores the **mid** F-measure for ROUGE-1/2/L. The mid value is the
median bootstrap estimate from the official ROUGE aggregator, not the
mean. That choice is defensible on a noisy student dataset; just do not
compare those numbers to papers that report the mean.

`datasets.load_metric` is deprecated. Current Hugging Face guidance is
`evaluate.load("rouge")`, which is already how `eval.py` imports the
`evaluate` package — but `eval.py` still calls `datasets.load_metric`
in the metric function. Both scripts need the `rouge` extra /
`rouge-score` package at runtime.

## What this file does not decide

- How the labeled CSV is split (no committed sampler, no seed).
- Early stopping patience (best checkpoint is kept, but training always
  runs 20 epochs).
- A learning-rate sweep. `3e-4` is a single point.

`examples/configs/training.example.json` repeats these values in one
place so they can be diffed against a future rewrite without rereading
the script.
