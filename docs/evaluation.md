# Evaluation

Two scripts look at a trained checkpoint. They answer different questions and they do not share a CLI.

| Script | Question | Dataset | Metrics |
| --- | --- | --- | --- |
| `use_model.py` | “Does this look like a summary?” | ScandEval Nordjylland **mini** test | none (prints text) |
| `eval.py` | “What is the number?” | Alexandra Institute Nordjylland test | ROUGE-1/2/L + BERTScore P/R/F1 |

Both load `small_model` and a `google/mt5-small` tokenizer. Read [models.md](models.md) before you trust a number from a `large_model` run.

## `use_model.py` — qualitative

Flow:

1. Download `ScandEval/nordjylland-news-summarization-mini` `test`.
2. Tokenize `input_text` (1024) and `target_text` (180).
3. `DataLoader` batch size 2, collate with `DataCollatorForSeq2Seq`.
4. For the first 5 batches, `model.generate` with:
   - `num_beams=2`
   - `num_return_sequences=1`
   - `no_repeat_ngram_size=1`
   - `remove_invalid_values=True`
   - `max_length=128`
5. Print the raw `input_text` from the *untokenized* dataset at index `i`, the decoded label, and the decoded prediction.

### Indexing trap

The loop uses batch index `i` to look up `split_dataset["test"]["input_text"][i]`. The DataLoader batch size is 2, so printed “input” is article `i` while the decoded tensors are a *batch of two*. The first printed input can disagree with the first decoded label. When you inspect, trust `text_labels` / `text_preds` more than the `input_text[i]` line, or change the script to zip over the batch.

### `no_repeat_ngram_size=1`

This blocks any repeated token. Danish function words (`i`, `og`, `på`, `det`) become hard to use twice. Inspection output may look more clipped than `eval.py` output, which uses trainer generate + the model config (trigram blocking, not unigram).

## `eval.py` — quantitative

Flow:

1. Download `alexandrainst/nordjylland-news-summarization` `test`.
2. Tokenize `input_text` (1024) and `target_text` (128).
3. Build a `Seq2SeqTrainer` with `predict_with_generate=True`, `per_device_eval_batch_size=64`, `dataloader_drop_last=True`.
4. `trainer.evaluate()` → `print(metrics)`.

`evaluation_strategy="epoch"` on an eval-only trainer is unused noise; it does not change `evaluate()`.

`dataloader_drop_last=True` **drops** the last incomplete batch. With batch 64 that can hide up to 63 test rows. For a reported number, set it to `False`.

### ROUGE

Decoded text is sentence-split with NLTK and rejoined on `\n` so the legacy metric can compute ROUGE-Lsum-style scores. Reported keys:

- `rouge_rouge1_mid_fmeasure` (note the extra `rouge_` prefix plus the metric name)
- `rouge_rouge2_mid_fmeasure`
- `rouge_rougeL_mid_fmeasure`

The dict comprehension is:

```python
{f'rouge_{key}_mid_fmeasure': value.mid.fmeasure for key, value in rouge.items()}
```

`key` is already `rouge1` / `rouge2` / `rougeL`, so the printed names are `rouge_rouge1_...`. `finetune.py` uses cleaner names (`rouge_1_mid_fmeasure`). Do not compare those keys as strings; compare the values.

ROUGE on Danish:

- It is lexical overlap. A good paraphrase scores low.
- Compound words (`energiforsyningen` vs `forsyning af energi`) hurt ROUGE-2.
- Mid F-measure is a bootstrap summary from the old `rouge` scorer, not a simple corpus mean.

### BERTScore

```python
bert_metric.compute(
    predictions=decoded_preds,
    references=decoded_labels,
    lang='da',
    model_type="xlm-roberta-large",
)
```

Then mean precision / recall / F1.

BERTScore is the better “does this *mean* the same thing?” number for a pivot-language system, because silver-label models often choose different function words than Nordjylland editors. It is also slower and depends on XLM-R’s Danish quality.

`lang='da'` and `model_type="xlm-roberta-large"` together: the explicit model type wins. `lang` is used to pick idf / baseline settings inside bert-score.

### What a “good” score meant in the course

There is no committed `metrics.json`. When you rerun, write the printed dict into `docs/` or a gist and record:

- checkpoint path and size (small vs large),
- dataset revision,
- whether `[:10]` was still in `summary.py` when labels were built,
- generate settings.

Without those, a single ROUGE-1 is not comparable to the 2023 run.

## Why not evaluate on silver labels?

You *can* point `eval.py` at a CSV with `input_text`/`target_text` columns copied from `body`/`summary`. That measures reconstruction of the teacher pipeline, which is useful as a sanity check (scores should be clearly higher than Nordjylland). It is not a claim about Danish summarization quality.

`examples/data/nordjylland_like_eval.csv` uses the eval column names on fictional text so `examples/validate_example_data.py` can check that schema too.

## Human inspection checklist

For each printed pair, mark:

1. **Faithfulness:** any fact that is not in the article? (pivot pipelines invent entities at the translation hops.)
2. **Coverage:** is the actual news event present, or only color?
3. **Language:** Danish a native reader would publish, vs word-for-word English?
4. **Length:** one lede vs a stitched list of chunk summaries?
5. **Names:** municipalities, ministries, clubs spelled as in the article?

Five articles from `use_model.py` are enough to catch a broken tokenizer. They are not enough to pick a winner between two checkpoints — use `eval.py` plus a 20-article manual sheet if you compare runs.

## Modern replacements (optional)

If you rewrite eval later, the 2023 APIs map like this:

| Committed | Current HF |
| --- | --- |
| `datasets.load_metric("rouge")` | `evaluate.load("rouge")` |
| `datasets.load_metric("bertscore")` | `evaluate.load("bertscore")` |
| `evaluation_strategy=` | `eval_strategy=` (transformers ≥4.41) |
| `tokenizer=` on `Trainer` | `processing_class=` (newer transformers) |

The example validation script does not import `transformers`, so docs CI can stay offline.
