# Evaluation

Two root scripts look at a trained checkpoint. One is qualitative, one is
numeric. Neither uses the silver CSVs.

## Qualitative preview — `use_model.py`

- Tokenizer: `google/mt5-small`
- Weights: `small_model`
- Data: `ScandEval/nordjylland-news-summarization-mini`, test split
- Batch size 2, first five batches
- Generation: 2 beams, `no_repeat_ngram_size=1`, `max_length=128`

The script prints the raw `input_text`, the decoded human `target_text`,
and the decoded generation. `no_repeat_ngram_size=1` is harsher than the
training config (which uses 3). Preview outputs will therefore avoid
repeated *words*, not just repeated trigrams, and can look more clipped
than `eval.py`.

## Numeric eval — `eval.py`

- Tokenizer: `google/mt5-small`
- Weights: `small_model`
- Data: `alexandrainst/nordjylland-news-summarization`, test split
- `per_device_eval_batch_size=64`
- `predict_with_generate=True`
- `dataloader_drop_last=True` — the last incomplete batch is dropped

Metrics, computed in `compute_metrics`:

| Key | Source |
| --- | --- |
| `rouge_{1,2,L,Lsum}_mid_fmeasure` | Hugging Face `rouge`, mid F-measure |
| `bertscore_precision` | mean over the batch |
| `bertscore_recall` | mean over the batch |
| `bertscore_f1` | mean over the batch |

BERTScore is requested with `lang='da'` and
`model_type="xlm-roberta-large"`. That download is large. The first eval
on a clean machine will spend most of its time pulling XLM-R, not running
mT5.

ROUGE uses `nltk.sent_tokenize` after decode so ROUGE-Lsum can see
sentence boundaries. `eval.py` does not call `nltk.download("punkt")`.
Do that once before the run.

## Offline stand-in — `examples/score_sample_summaries.py`

The example script scores
`examples/data/sample_eval_pairs.csv` with the lexical helpers in
`danish_news_sum.metrics`:

- ROUGE-1 / ROUGE-2 style n-gram overlap F1
- ROUGE-L style LCS F1
- compression ratio against `input_text`

These are not Hugging Face `rouge` and not BERTScore. They exist so the
documentation can show the *shape* of a score table without model
downloads. Typical numbers on the hand-written fixtures sit well above a
real mT5 run, because the "predictions" were written by a person who
could see the references.

## How to read a real score table

On Nordjylland News, treat the numbers as a *transfer* score:

- **ROUGE-1** moving while ROUGE-2 stays flat usually means the model
  learned topical words (place names, "kommune", "metro") but not the
  reference phrasing.
- **ROUGE-L** much lower than ROUGE-1 means word choice is fine and
  order is not.
- **BERTScore** can stay high when ROUGE is low. XLM-R will reward
  paraphrases that a news desk would still accept. That is useful, but
  it will also reward fluent translationese that misses a specific
  number.
- A silver-trained model that beats a raw `google/mt5-small` baseline on
  Nordjylland News is the actual claim of the project. Compare against
  that baseline before celebrating an absolute ROUGE number.

## What the 2023 scripts do not compute

- Bootstrap confidence intervals
- Per-outlet or per-length buckets
- Human preference / factuality
- A lead-3 extractive baseline (worth adding if you extend the project)

`examples/inspect_silver_labels.py` is the place to look at *training*
length statistics. It is not an evaluation of the fine-tuned model.
