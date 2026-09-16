# Training and evaluation

Fine-tuning and scoring are the last third of the course project. The
scripts assume the silver labels already exist and that a local model
directory will be written by hand.

## Fine-tuning

`finetune.py` loads `google/mt5-large` and three local CSVs:

```
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

Each file must have `id`, `body`, and `summary`. Tokenization truncates
bodies at 1024 tokens and summaries at 128 tokens. The test split is loaded
into the `DatasetDict` but is not passed to `Seq2SeqTrainer`. It is there
so you can score the silver test rows later with the same tokenizer.

### Generation config baked into the model

`AutoConfig.from_pretrained` is called with decode settings that then ride
along with the saved model:

| Setting | Value |
| --- | --- |
| `min_length` | 9 |
| `max_length` | 128 |
| `length_penalty` | 0.8 |
| `no_repeat_ngram_size` | 3 |
| `num_beams` | 4 |
| `dropout_rate` | 0.1 |

`length_penalty=0.8` slightly prefers shorter outputs. That matches the
lead-style silver labels.

### Trainer settings

| Setting | Value | Why it is there |
| --- | --- | --- |
| `num_train_epochs` | 20 | small silver set, lots of passes |
| `learning_rate` | 3e-4 | Adafactor default-ish for T5 |
| `lr_scheduler_type` | `polynomial` | decay after 1000 warmup steps |
| `warmup_steps` | 1000 | avoids early spike on a fresh mT5 |
| `optim` | `adafactor` | the usual T5 optimizer |
| `weight_decay` | 0.01 | light regularization |
| `per_device_train_batch_size` | 8 | 1024-token mT5-large is large |
| `fp16` | `True` | memory; can be unstable on mT5 |
| `predict_with_generate` | `True` | needed for ROUGE during eval |
| `generation_max_length` | 128 | matches the config |
| `load_best_model_at_end` | `True` | restore best ROUGE-1 checkpoint |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` | mid F1, not high |
| `save_total_limit` | 1 | disks fill up fast |
| `push_to_hub` | `False` | keep weights local |

The trainer writes checkpoints under `mt5-summarize-large/` and then saves
the best model to `./large_model`. `use_model.py` and `eval.py` load
`./small_model` instead. That mismatch is historical: the inspection
scripts were pointed at the smaller run because it was cheaper to reload.
If you only train the large model, change `local_model_path` or copy the
directory.

### Metrics during training

`compute_metrics` uses `datasets.load_metric("rouge")`. That API is the
older `datasets` metric loader. It returns the full ROUGE object, and the
script stores:

- `rouge_1_mid_fmeasure`
- `rouge_2_mid_fmeasure`
- `rouge_l_mid_fmeasure`

Predictions and labels are sentence-split with NLTK before scoring so
ROUGE-Lsum-style newlines exist. Labels that were padded with `-100` are
mapped back to the pad token before decode.

There is no BERTScore in the training loop. That metric is reserved for
`eval.py` because it pulls `xlm-roberta-large`.

## Inspection

`use_model.py` is the qualitative loop:

1. Load the Nordjylland mini test split.
2. Tokenize `input_text` / `target_text`.
3. Run `model.generate` with 2 beams and `no_repeat_ngram_size=1`.
4. Print the article, the gold summary, and the generation.

`no_repeat_ngram_size=1` is stronger than the training config's trigram
block. Inspection outputs will therefore look less repetitive than the
checkpoint's default decode. That is useful for a demo and misleading if
you compare those strings to `eval.py`.

The printout uses `split_dataset["test"]["input_text"][i]` together with
batch `i`. The DataLoader batch size is 2, so only the first row of each
batch lines up with `i`. Read the loop as "show me a few batches", not as
"show me items 0..4 aligned to the dataset order".

## Held-out scoring

`eval.py` loads the full Nordjylland news test split and runs
`trainer.evaluate()`. It reports ROUGE mid F-measures plus BERTScore
precision, recall, and F1. BERTScore is requested with `lang='da'` and
`model_type="xlm-roberta-large"`.

This is an extrinsic check. Nordjylland summaries are not the silver
labels. A model that copies the back-translation style can still lose
ROUGE against journalistic gold leads. That gap is part of the course
write-up, not a bug in the scorer.

`dataloader_drop_last=True` means a leftover partial batch is ignored.
On a small split that can hide a few rows. The mini set used by
`use_model.py` is safer for a laptop demo.

## Suggested local recipe

For a machine that cannot host mT5-large:

1. Keep `finetune.py` as the recorded large-model recipe.
2. Change `model_name` to `google/mt5-small` only in a working copy.
3. Write that run to `./small_model` so `use_model.py` and `eval.py` work
   unchanged.
4. Lower `per_device_train_batch_size` before touching `fp16`.

The example script `examples/print_training_recipe.py` prints the recorded
hyperparameters and the stage notes. It does not start a trainer.
