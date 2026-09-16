# Evaluation

There are two evaluation surfaces, and they do not share a dataset or a decode config.

## Qualitative: `use_model.py`

**Dataset:** `ScandEval/nordjylland-news-summarization-mini` (test)

**Weights:** `./small_model`

**What it does:** pulls a `DataLoader` of batch size 2, generates 5 batches, prints:

- the raw `input_text` from the untokenized dataset at index `i`
- the decoded gold label from the **current batch** (`text_labels[0]`)
- the decoded prediction (`text_preds[0]`)

Because the print uses `split_dataset["test"]["input_text"][i]` (the *i*-th dataset row) but decodes `batch[0]` (the first item of the *i*-th batch of size 2), the article and the gold/pred pair are **misaligned** as soon as `i > 0`. Batch 0 happens to line up. Treat later prints as suspect unless you fix the index (`i * batch_size`).

Decode settings:

```
num_beams=2
num_return_sequences=1
no_repeat_ngram_size=1
remove_invalid_values=True
max_length=128
```

`no_repeat_ngram_size=1` forbids repeating any unigram. That is extremely aggressive for Danish (articles, prepositions, auxiliary verbs) and will distort wording. The training config used `no_repeat_ngram_size=3`.

## Quantitative: `eval.py`

**Dataset:** `alexandrainst/nordjylland-news-summarization` (test)

**Weights:** `./small_model`

**What it does:** `Seq2SeqTrainer.evaluate()` with `predict_with_generate=True` and `per_device_eval_batch_size=64`.

Metrics:

### ROUGE

Loaded with `datasets.load_metric("rouge")`, `use_aggregator=True`.

Reported keys:

- `rouge_rouge1_mid_fmeasure` (the dict comprehension prefixes `rouge_` onto the already-named `rouge1` key)
- `rouge_rouge2_mid_fmeasure`
- `rouge_rougeL_mid_fmeasure`
- and any other ROUGE variants the metric object returns (for example `rougeLsum`)

The mid F-measure is the median of bootstrap samples, not the mean. That matches `finetune.py`’s `rouge_1_mid_fmeasure` selection, but the **key names differ** (`rouge_1_mid_fmeasure` vs `rouge_rouge1_mid_fmeasure`). You cannot paste eval.py output into the trainer’s `metric_for_best_model` without renaming.

ROUGE is computed after NLTK sentence tokenization with sentences joined by `\n`. That is the conventional setup for `rougeLsum`. It is still a lexical overlap metric. A correct Danish paraphrase with different function words scores badly.

### BERTScore

```python
bert_metric.compute(..., lang='da', model_type="xlm-roberta-large")
```

Reported: mean precision, recall, F1 over the test set.

BERTScore is kinder to paraphrases than ROUGE but expensive (XLM-R large, every pred/ref pair). First run downloads the encoder. `lang='da'` only selects the default model when `model_type` is omitted; here `model_type` is explicit, so `lang` is unused except for logging.

## What these numbers are allowed to claim

The public Nordjylland sets are **not** drawn from the same silver-label distribution as `labeled_dataset_ml80_rp5.0.csv`.

A model can:

- score well on Nordjylland and still parrot translationese on in-domain silver text, or
- overfit silver labels and look worse than a smaller model on Nordjylland.

Report both, or be explicit that the published number is out-of-domain relative to the training pairs.

Silver-label ROUGE against the held-out `datasets/test_dataset.csv` (unused by `finetune.py`) would measure “does the model copy the pivot pipeline,” not “is the summary good.” That number is still useful as a sanity check: if it is near zero, training did not run.

## Offline stand-in

`examples/demo_offline_metrics.py` computes:

- unigram / bigram overlap precision, recall, F1 (a ROUGE-1/2-shaped toy)
- longest common subsequence F1 (a ROUGE-L-shaped toy)

on the synthetic public-eval JSONL. It does not download `rouge` or `bert-score`. Use it to check that fixtures and tokenization helpers stay wired. Do not quote those toy scores as model quality.

## Practical eval checklist

1. Confirm `./small_model` (or whatever path you set) is the checkpoint you intend, not an empty directory.
2. Align tokenizer source with that checkpoint.
3. Fix the `use_model.py` print index if you will paste qualitative examples into a report.
4. Record decode settings next to the number (`num_beams`, `max_length`, `no_repeat_ngram_size`).
5. Record which Nordjylland repo + split you used. Mini and full are not interchangeable.
6. Keep a copy of `metrics = trainer.evaluate()` stdout; the scripts do not write a JSON file.
