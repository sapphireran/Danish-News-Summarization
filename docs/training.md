# Training

`finetune.py` is the only training entry point. It is a single-GPU
Hugging Face `Seq2SeqTrainer` loop over local CSVs.

## Data map

```python
body      → tokenizer(..., max_length=1024, truncation=True)  # encoder
summary   → tokenizer(..., max_length=128,  truncation=True)  # labels
```

Dropped columns: `id`, `body`, `summary`. The collator is
`DataCollatorForSeq2Seq`, which pads labels to `-100` so pad tokens do
not enter the loss.

mT5 uses a SentencePiece vocabulary shared across languages. You do not
need a Danish-specific tokenizer. You do need `sentencepiece` installed.

## Hyperparameters (as checked in)

Taken verbatim from `Seq2SeqTrainingArguments` and `AutoConfig` in
`finetune.py`.

| Argument | Value |
| --- | --- |
| Base checkpoint | `google/mt5-large` |
| Epochs | 20 |
| Learning rate | `3e-4` |
| Scheduler | `polynomial` |
| Warmup steps | 1000 |
| Optimizer | `adafactor` |
| Weight decay | 0.01 |
| Train batch | 8 |
| Eval batch | 8 |
| Grad accumulation | 1 |
| Eval / save | every epoch |
| Predict with generate | yes |
| Generation max length | 128 |
| Logging steps | 250 |
| `save_steps` | 100 (overridden by `save_strategy="epoch"`) |
| fp16 | True |
| Load best at end | True |
| Best metric | `rouge_1_mid_fmeasure` |
| `save_total_limit` | 1 |
| Push to Hub | False |
| Output dir | `mt5-summarize-large` |

Generation config on the model (not the Trainer):

| Argument | Value |
| --- | --- |
| `min_length` | 9 |
| `max_length` | 128 |
| `length_penalty` | 0.8 |
| `no_repeat_ngram_size` | 3 |
| `num_beams` | 4 |
| `dropout_rate` | 0.1 |

## Loss and selection

The training loss is standard seq2seq cross-entropy on the decoder
tokens. Model selection is **not** by loss: `compute_metrics` decodes
the validation set, sentence-tokenizes with NLTK, and reports ROUGE-1/2/L
mid F-measure. The checkpoint with the highest ROUGE-1 mid F is copied
to `./large_model` after `trainer.train()`.

If the process is wrapped in `DataParallel` (`trainer.model.module`),
the script unwraps before `save_pretrained`.

## Hardware notes

mT5-large with 1024-token inputs and fp16 typically needs around 16–24
GB of VRAM at batch 8. If you OOM:

1. Drop `per_device_train_batch_size` to 2 or 4 and raise
   `gradient_accumulation_steps` so the effective batch stays 8.
2. Fine-tune `google/mt5-small` instead and point `eval.py` /
   `use_model.py` at the same directory (they already assume small).
3. Turn off `predict_with_generate` during training-time eval and only
   run ROUGE at the end — generation is the expensive part of each
   epoch.

CPU training is possible for mT5-small on the fictional
`examples/data/sample_*_split.csv` tables (a few dozen rows) but is not
useful for the 10k silver-label run.

## Reproducibility gaps

The script does not set `seed`, `data_seed`, or `full_determinism`.
Adafactor + fp16 on GPU will not replay bit-identically. Record at
least:

- git commit of the scripts
- Hugging Face revision of `google/mt5-large`
- CSV hashes of the three splits
- GPU model and `torch.cuda.get_device_name()`
- `transformers`, `datasets`, `torch` versions

## What is not trained

- The OPUS-MT and English T5 checkpoints are frozen feature/label
  generators.
- `eval.py` constructs a `Seq2SeqTrainer` but only calls `evaluate()`.
- The `test` split loaded in `finetune.py` is never scored there;
  `eval.py` uses Nordjylland-News instead.
