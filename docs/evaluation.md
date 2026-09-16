# Evaluation protocol

Two different “look at the model” paths exist. Only one computes corpus metrics.

## Qualitative: `use_model.py`

- Dataset: `ScandEval/nordjylland-news-summarization-mini`, test split.
- Weights: `small_model`.
- Tokenizer: `google/mt5-small`.
- Prints five batches (DataLoader `batch_size=2`, loop cap `num_samples=5`).
- Each block shows the Danish article, the decoded gold summary, and the generation.

Use this when you want to read mistakes, not when you want a number for a report.

Caveats:

- `no_repeat_ngram_size=1` forbids repeating any unigram. Danish definite forms and function words suffer; outputs can look unnaturally wide-vocab.
- The printed “input text” uses `split_dataset["test"]["input_text"][i]` (dataset index `i`), while predictions come from dataloader batch `i`. With `batch_size=2` those indices are not the same article after the first batch.

## Quantitative: `eval.py`

- Dataset: `alexandrainst/nordjylland-news-summarization`, test split.
- Weights: `small_model`.
- Tokenizer: `google/mt5-small`.
- `Seq2SeqTrainer.evaluate()` with `predict_with_generate=True`.
- `per_device_eval_batch_size=64`, `dataloader_drop_last=True` (the last incomplete batch is discarded).

### ROUGE

The script still calls `datasets.load_metric("rouge")` (deprecated; `evaluate.load("rouge")` is the replacement).

Predictions and labels are decoded, then each string is passed through `nltk.sent_tokenize` and rejoined with newlines. That is the canonical “ROUGE sees sentence boundaries” trick from the Hugging Face summarization examples.

Reported keys:

- `rouge_1_mid_fmeasure`
- `rouge_2_mid_fmeasure`
- `rouge_l_mid_fmeasure` (from the mid bootstrap interval of `rouge-score`)

Training uses the same ROUGE-1 mid F-measure as `metric_for_best_model`.

Danish ROUGE is a lexical overlap metric. It punishes valid paraphrases (`kommunen` vs `byrådet`, `i dag` vs `torsdag`) and rewards n-gram copying. Silver-label models often look stronger on ROUGE than they read, because they echo pivot phrasing that also overlaps the lede.

### BERTScore

```python
bert_metric.compute(
    predictions=decoded_preds,
    references=decoded_labels,
    lang='da',
    model_type="xlm-roberta-large",
)
```

The script averages `precision`, `recall`, and `f1` across the test set.

BERTScore is the better semantic sanity check for Danish: it can give credit when the model names the same event in different words. It is also slower and pulls `xlm-roberta-large`. First eval run will download that encoder.

`lang='da'` and an explicit `model_type` together pin the encoder so a later bert-score default change does not silently move the number.

## What the course metrics are for

| Question | Metric to trust first |
| --- | --- |
| Did training move at all? | Validation ROUGE-1 from `finetune.py` |
| Are we copying vs paraphrasing? | ROUGE-2 vs BERTScore gap |
| Does it read like a Danish lede? | Manual read of `use_model.py` (after fixing the index bug) |
| Can we compare to ScandEval / papers? | `eval.py` on Nordjylland, same generate settings as the paper |

This repo does not ship a results table. If you rerun, record:

- Checkpoint name (`small_model` vs `large_model`)
- Generate hyperparameters
- Dataset revision / split
- ROUGE-1/2/L mid F and BERTScore P/R/F1

## Toy metrics in `examples/`

`examples/metrics_demo.py` does **not** call Hugging Face. It implements:

- Token-level unigram precision / recall / F1 (a ROUGE-1 sketch)
- Longest common subsequence F1 (a ROUGE-L sketch)
- Character-level compression ratio (`len(summary) / len(body)`)

These run on `examples/data/labeled_dataset.csv` vs `examples/data/toy_predictions.csv` so the examples tree stays stdlib-only. Numbers are for teaching the schema, not for reporting.

### Tokenization used by the toy metric

Lowercase, keep Danish letters, split on non-letters. Good enough to show that a missing number or a dropped place name hurts unigram recall.

## Recommended generate settings for a fair rerun

If you want inspect and eval to match training:

- Load the same checkpoint both scripts use.
- Copy `num_beams=4`, `no_repeat_ngram_size=3`, `min_length=9`, `max_length=128`, `length_penalty=0.8` into `use_model.py` and `eval.py`.
- Do not drop the last eval batch (`dataloader_drop_last=False`) unless you are matching an old number that did.
