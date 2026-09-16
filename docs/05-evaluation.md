# Evaluation protocol

How the 2023 project measured the Danish summarizer, what the numbers mean, and how the GPU-free toy metric script relates to the real scores.

## Two evaluation surfaces

| Surface | Script | Data | Purpose |
| --- | --- | --- | --- |
| Qualitative | `use_model.py` | Nordjylland *mini* test split | Read 5 generations, catch obvious failure modes |
| Quantitative | `eval.py` | `alexandrainst/nordjylland-news-summarization` test | ROUGE + BERTScore to report |

Neither script scores silver labels. If you want a factory diagnostic ("did back-translation preserve entities?"), that is a different measurement and belongs in a notebook, not in `eval.py`.

## Qualitative loop (`use_model.py`)

For each of the first few batches (`batch_size=2`, `num_samples=5`):

1. Generate with `num_beams=2`, `no_repeat_ngram_size=1`, `max_length=128`.
2. Decode the reference labels, mapping `-100` back to `pad_token_id`.
3. Print input, reference, and generation.

Things to look for by hand:

- **Language:** Is the output Danish, English, or mixed? Under-trained mT5 often slips into English tokens.
- **Named entities:** Are cities, ministries, and people preserved or swapped?
- **Numbers:** Dates, percents, and kroner amounts are the first thing translationese corrupts.
- **Lead vs. tail:** Does the model only rewrite the first sentence?
- **Repetition:** `no_repeat_ngram_size=1` is extremely strict (no repeated unigrams). It can produce awkward paraphrases ("borgmesteren" then "kommunens leder"). The eval script does not use that setting.

The printed input uses `split_dataset["test"]["input_text"][i]` with the **batch index**, not the global example index. With `batch_size=2` that means the article you see is not always the article the batch was generated from. Treat the qualitative script as a smoke test, not a carefully aligned viewer.

## Quantitative loop (`eval.py`)

`Seq2SeqTrainer.evaluate()` generates predictions for the test set and calls `compute_metrics`.

### ROUGE

Loaded via `datasets.load_metric("rouge")` (deprecated; `evaluate.load("rouge")` is the modern equivalent). Predictions and references are sentence-tokenized and joined with newlines, the standard summarization setup so ROUGE-Lsum can see sentence boundaries.

Reported keys:

```
rouge_rouge1_mid_fmeasure
rouge_rouge2_mid_fmeasure
rouge_rougeL_mid_fmeasure
rouge_rougeLsum_mid_fmeasure
```

The dict comprehension is:

```python
{f'rouge_{key}_mid_fmeasure': value.mid.fmeasure for key, value in rouge.items()}
```

so the names are slightly redundant (`rouge_rouge1_...`). Fine-tune looks for `rouge_1_mid_fmeasure`, which is a **different key** produced in `finetune.py`. Do not compare those dictionaries without renaming.

ROUGE mid-F is the median of bootstrap-style aggregator stats from `rouge-score`. It is overlap, not meaning:

- High ROUGE-1 can mean "copied many content words."
- Low ROUGE-2 is normal for abstractive Danish because compounds and word order move.
- ROUGE-L rewards longest common subsequence; a reordered but faithful lead may score worse than a extractive copy.

### BERTScore

```python
bert_metric.compute(
    predictions=decoded_preds,
    references=decoded_labels,
    lang='da',
    model_type="xlm-roberta-large",
)
```

Aggregated as the mean of precision, recall, and F1 over the test set.

BERTScore is closer to semantic similarity than ROUGE, but:

- It is still embedding cosine, not a fact checker.
- XLM-R can be overly kind to fluent nonsense that lives in the same region of space as the reference.
- It is expensive. Running it on every train epoch would dominate wall time; that is why only `eval.py` uses it.

## What *not* to claim from these numbers

- **Factual correctness.** Neither metric knows that "3 million" and "300 million" are different.
- **Usefulness to a reader.** A high-scoring summary can bury the news.
- **Fairness across topics.** Sports and municipal politics tokenize differently; a micro-average hides that.
- **Comparability to English papers.** Danish morphology and compounds depress ROUGE relative to English numbers on CNN/DM.

Quote ROUGE and BERTScore as **automatic overlap / similarity**, then include two or three qualitative examples.

## Toy metrics in `examples/metrics_toy_eval.py`

The example script does **not** download `rouge-score` or XLM-R. It implements:

1. **Token F1** on whitespace tokens (a ROUGE-1-shaped overlap).
2. **Longest common subsequence ratio** (a ROUGE-L-shaped score).
3. A handful of hand-written prediction/reference pairs in Danish, including a fact-swap that overlap metrics *fail* to punish enough.

The point is pedagogical: you can see a fluent-but-wrong summary score well. Tests lock the arithmetic, not any scientific claim.

Run:

```bash
python examples/metrics_toy_eval.py
```

## Recommended reporting template

When you write up a revival run, include:

```
Model:        mT5-?  (checkpoint hash or date)
Train pairs:  N silver labels from <factory config>
Eval set:     alexandrainst/nordjylland-news-summarization  test
ROUGE-1 mid F:
ROUGE-2 mid F:
ROUGE-L mid F:
BERTScore F1 (XLM-R large, lang=da):
Notes:        (fp16, beam size, max length)
```

Plus at least one example where the model is factually wrong so readers do not over-trust the table.

## Statistical hygiene

The 2023 `eval.py` reports a single point estimate. Improvements on a revival should use:

- A frozen eval script and decoding settings.
- The same test split.
- Preferably a bootstrap interval over documents, not just a point.

Do not tune on the official test set. Use the silver validation split or a slice of Nordjylland *validation* if you need to pick `repetition_penalty`.
