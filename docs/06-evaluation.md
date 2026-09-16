# Evaluation

Two scripts look at a trained checkpoint. They are not interchangeable.

| | `use_model.py` | `eval.py` |
| --- | --- | --- |
| Purpose | Print a few articles and generations | Aggregate ROUGE + BERTScore |
| Weights | `small_model` | `small_model` |
| Tokenizer name | `google/mt5-small` | `google/mt5-small` |
| Hub set | `ScandEval/nordjylland-news-summarization-mini` `test` | `alexandrainst/nordjylland-news-summarization` `test` |
| Text columns | `input_text`, `target_text` | `input_text`, `target_text` |
| Target tok cap | 180 (labels only) | 128 |
| Generate | beams=2, `no_repeat_ngram_size=1`, max 128 | Trainer generate via `predict_with_generate` (model defaults) |
| Batch | DataLoader `batch_size=2`, first 5 batches | `per_device_eval_batch_size=64` |

Neither script scores `datasets/test_dataset.csv` (the silver split).

## Qualitative: `use_model.py`

For each of five batches it prints:

1. `***** Input's Text *****` — `split_dataset["test"]["input_text"][i]`
2. `***** Summary Text (True Value) *****` — decoded gold from that **batch**
3. `***** Summary Text (Generated Text) *****` — decoded generate()

There is a real footgun: the input text is indexed with the batch **index** `i` (0..4), while the gold/pred strings come from `batch` which contains **two** examples (`batch_size=2`). So the printed article is example `i` of the dataset, but the printed gold/pred are example `0` of batch `i` (dataset indices 0, 2, 4, 6, 8). Example `i` and "first row of batch `i`" only coincide when `i == 0`. Read the first block as aligned; treat later blocks as loosely paired.

`no_repeat_ngram_size=1` forbids repeating any token. Danish function words (`i`, `og`, `at`) get blocked on the second use. Outputs can look like keyword soup. For demos closer to `finetune.py`, use `no_repeat_ngram_size=3` and `num_beams=4`.

## Quantitative: `eval.py`

`Seq2SeqTrainer.evaluate()` runs generate over the tokenized Nordjylland test set (`dataloader_drop_last=True`, so a leftover partial batch is discarded).

### ROUGE

Legacy `datasets.load_metric("rouge")`, `use_aggregator=True`. Predictions and references are sentence-split and joined with newlines before scoring (ROUGE-Lsum style).

Logged keys:

- `rouge_rouge1_mid_fmeasure` (dict comprehension uses `f'rouge_{key}_mid_fmeasure'` where `key` is already `rouge1`, so the prefix doubles)
- `rouge_rouge2_mid_fmeasure`
- `rouge_rougeL_mid_fmeasure`
- `rouge_rougeLsum_mid_fmeasure` if the metric returns it

The `mid` field is the bootstrap midpoint from the `rouge-score` aggregator, not a custom statistic.

Training logs in `finetune.py` use cleaner names (`rouge_1_mid_fmeasure`). Do not paste the two dicts into one table without renaming.

### BERTScore

```python
bert_metric.compute(
    predictions=decoded_preds,
    references=decoded_labels,
    lang="da",
    model_type="xlm-roberta-large",
)
```

`lang='da'` selects the BERTScore baseline for Danish. `xlm-roberta-large` is a multilingual encoder, which is the right family for Danish news. This download is large and runs on GPU if available.

Means of precision, recall, and F1 are logged.

BERTScore is much closer to "does this mean the same thing?" than ROUGE on morphologically rich Danish, but it still rewards lexical/semantic overlap with the *Nordjylland* reference style, which is not the silver-teacher style.

## What a number means

| You computed | Against | It measures |
| --- | --- | --- |
| ROUGE in `finetune.py` | silver val CSV | Fidelity to the translate-summarize-translate teacher |
| ROUGE / BERTScore in `eval.py` | Nordjylland gold | Transfer to a human Danish news abstract set |
| Eyeballing `use_model.py` | Nordjylland mini | Fluency and obvious hallucinations |

A model can score well on silver val (it cloned T5-translationese) and poorly on Nordjylland (humans write different abstracts). Report both if you claim anything.

## Nordjylland column mapping

| Nordjylland | Silver CSV |
| --- | --- |
| `input_text` | `body` |
| `target_text` | `summary` |
| `text_len`, `summary_len` | (not used; dropped in `map`) |
| (no id used) | `id` |

You cannot point `eval.py` at `datasets/test_dataset.csv` without renaming columns or changing `tokenize_data`.

## Practical eval checklist

1. Confirm `small_model` (or the path you changed) contains the weights you intend — `config.json` + `model.safetensors` / `pytorch_model.bin`.
2. Confirm the tokenizer SentencePiece model matches the trained checkpoint size (`mt5-small` vs `mt5-large`).
3. Download NLTK `punkt` before metrics (`use_model.py` does; `eval.py` does not — add `nltk.download("punkt")` if the worker is clean).
4. First run of BERTScore will pull `xlm-roberta-large`.
5. Write `metrics` to a JSON file. `eval.py` only `print`s the dict.

`examples/configs/eval.yaml` restates the Hub ids and metric names. `examples/inspection/print_pipeline_io.py` does **not** call the Hub; it only pretty-prints the local sample CSVs.
