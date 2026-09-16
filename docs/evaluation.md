# Evaluation

There are two evaluation scripts, and they answer different questions.

| Script | Question | Dataset | Weights |
| --- | --- | --- | --- |
| `use_model.py` | "Does this look like a summary?" | Nordjylland mini test | `small_model` |
| `eval.py` | "What are the ROUGE / BERTScore numbers?" | Alexandrainst Nordjylland test | `small_model` |

Neither script reads the silver-label CSVs. That is deliberate. Training
fuel and the reported test set are different corpora.

## Qualitative loop (`use_model.py`)

The script:

1. Downloads `ScandEval/nordjylland-news-summarization-mini` `test`.
2. Tokenizes `input_text` to 1024 and `target_text` to 180.
3. Builds a `DataLoader` with batch size 2.
4. Generates 5 batches with:

```python
model.generate(
    ...,
    num_beams=2,
    num_return_sequences=1,
    no_repeat_ngram_size=1,
    remove_invalid_values=True,
    max_length=128,
)
```

5. Prints the raw article, the decoded gold summary, and the generation.

`no_repeat_ngram_size=1` forbids repeating any unigram. That is extremely
aggressive: a model cannot say "Aalborg" twice. Useful for spotting
loops, bad for fluent Danish. For a fair qualitative read, set it to 3
to match `finetune.py`.

The printout uses `split_dataset["test"]["input_text"][i]` with `i` as
the **batch index**, while `text_labels[0]` / `text_preds[0]` are the
**first row of that batch**. With `batch_size=2` the article and the
summary on screen can belong to different examples. When you care about
alignment, set `batch_size=1` or index with `i * batch_size`.

## Quantitative loop (`eval.py`)

`eval.py` builds a `Seq2SeqTrainer` with no training set and calls
`trainer.evaluate()`.

### Metrics

**ROUGE** via `datasets.load_metric("rouge")`, aggregated:

```text
rouge_1_mid_fmeasure
rouge_2_mid_fmeasure
rouge_l_mid_fmeasure
```

(The code iterates `rouge.items()`, so the keys are `rouge_{rouge1,rouge2,rougeL,...}_mid_fmeasure`.)

**BERTScore** via `datasets.load_metric("bertscore")`:

```python
lang="da"
model_type="xlm-roberta-large"
```

Reported as mean precision, recall, and F1.

BERTScore with `xlm-roberta-large` is the expensive part. It is also
the metric that is more forgiving of paraphrase, which matters because
a pivot-trained model often says the right thing with different wording
than the Nordjylland editors.

### Trainer settings

```python
output_dir="mt5-summarize-large"
per_device_eval_batch_size=64
evaluation_strategy="epoch"
predict_with_generate=True
dataloader_drop_last=True
```

`dataloader_drop_last=True` silently drops an incomplete last batch.
On a small test set that can hide several examples. Turn it off unless
you are chasing a batch-size bug.

`per_device_eval_batch_size=64` plus generation plus BERTScore is a
lot of memory. If evaluate OOMs, drop this to 8 or 16.

The tokenizer is loaded from `google/mt5-small` even if the checkpoint
is a large model. That is correct only if `small_model` was actually
trained from mT5-small. If you copy `large_model` → `small_model`,
change `model_name` to `google/mt5-large` or load the tokenizer from
the checkpoint directory.

## How to read the numbers

Personal rule of thumb from the course write-up process:

- **ROUGE-1** moving is cheap. Lead-3 already scores something.
- **ROUGE-2** is the first number that usually shows whether the model
  copies useful phrases from the article.
- **ROUGE-L** tracks longer consistent phrasing.
- **BERTScore-F1** is the one to look at when the summaries "sound
  right" but ROUGE is stuck, which is common with pivot labels.

Do not compare `eval.py` numbers to silver-label ROUGE on
`datasets/test_dataset.csv`. Those test targets were produced by the
same factory. A model can overfit pivotese and look strong there while
losing on Nordjylland News.

## Baseline you can run without a checkpoint

`examples/scripts/compute_overlap_metrics.py` implements a tiny
ROUGE-1/2/L-style overlap scorer (no `rouge-score` package required).
Use it to:

- score lead-N against the synthetic fixtures
- score two CSV columns against each other after a dry-run
- sanity-check that ids still align

It will not match Hugging Face ROUGE bit-for-bit (no stemming, no
bootstrap intervals), and that is fine. It exists so the examples stay
runnable on a CPU-only agent.

## Reproducing a fair eval later

1. Freeze the checkpoint directory name in one config.
2. Freeze the dataset id and split.
3. Set `dataloader_drop_last=False`.
4. Set generation knobs equal to the ones in `finetune.py`
   (`num_beams=4`, `no_repeat_ngram_size=3`, `max_length=128`).
5. Record the `transformers`, `evaluate`, and `bert-score` versions.
6. Print the number of scored examples, not only the means.

Until those are true, treat printed metrics as directional, not as a
leaderboard score.
