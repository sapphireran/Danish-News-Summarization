# Evaluation

Two evaluation stories live in this repository.

1. **Course GPU path** (`eval.py`): Hugging Face `rouge` + BERTScore on
   Nordjylland gold summaries.
2. **CPU examples** (`danish_news.scoring`, `examples/03_evaluate_toy_summaries.py`):
   overlap F1 implemented in a few dozen lines so the definitions are
   readable without `evaluate` or `xlm-roberta-large`.

They are not comparable numbers. Do not paste the toy F1 into a report
and call it Nordjylland ROUGE.

## What `eval.py` computes

After `Seq2SeqTrainer.evaluate()`:

* decode with `predict_with_generate=True`
* replace label `-100` with the pad id
* `nltk.sent_tokenize` each prediction and reference, join with newlines
  (the ROUGE package's sentence convention)
* `datasets.load_metric("rouge")` with `use_aggregator=True`
* `datasets.load_metric("bertscore")` with `lang='da'` and
  `model_type="xlm-roberta-large"`

Reported keys:

* `rouge_{rouge1,rouge2,rougeL,rougeLsum}_mid_fmeasure`
* `bertscore_precision`, `bertscore_recall`, `bertscore_f1`

`load_metric` is the old `datasets` API; current Transformers examples use
`evaluate.load`. The metric *definitions* are the same.

`use_model.py` does not compute metrics. It prints `num_samples=5`
generations (`num_beams=2`, `no_repeat_ngram_size=1`, `max_length=128`)
against the ScandEval mini split. `no_repeat_ngram_size=1` forbids any
repeated unigram, which is a harsh constraint for Danish news names.

## Fine-tune selection metric

`finetune.py` sets `metric_for_best_model="rouge_1_mid_fmeasure"` and
`load_best_model_at_end=True`. The `compute_metrics` there only returns
ROUGE-1/2/L mid F-measure, not BERTScore. Checkpointing therefore ignores
semantic overlap that BERTScore would have caught.

## CPU scorer

`danish_news.scoring` tokenizes with a Danish-letter regex, then:

| Name | Definition |
| --- | --- |
| ROUGE-N | Clipped n-gram overlap; precision / recall / F1 |
| ROUGE-L | F1 of LCS(pred, ref) against the two lengths |
| Compression | `len(summary tokens) / len(article tokens)` |
| Novelty | Share of summary n-grams that never occur in the article |

These match the usual textbook formulas, not necessarily every flag of
`google-research/rouge` (stemming, bootstrapped mid/low/high). The fixture
evaluator compares `sample_labeled.csv` with `sample_references.csv` and
prints a per-article table plus a corpus mean.

Compression on the fixtures should sit well below 1.0 (summaries are
shorter than bodies). Novelty is expected to be *higher* on the
headline-style references than on extractive silver labels, because the
references rewrite.

## Generation settings that change scores

| Knob | Where | Effect |
| --- | --- | --- |
| `max_length=80` on T5 | `summary.py` | Caps each *window* summary, not the concatenated label |
| `repetition_penalty=5.0` | `summary.py` | Strong anti-loop; can erase repeated entities |
| `generation_max_length=128` | `finetune.py` | mT5 decode cap |
| `num_beams=4` vs `2` | fine-tune vs `use_model.py` | Different search at train-eval vs demo |
| `dataloader_drop_last=True` | `eval.py` | Last incomplete batch is skipped |

When you compare two mT5 runs, keep these knobs fixed. Changing only the
checkpoint while leaving `use_model.py` on 2-beam unigram-block decoding
will not match `eval.py`.
