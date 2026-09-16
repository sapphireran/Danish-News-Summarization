# Evaluation

Two scripts look at a trained checkpoint. Neither of them scores the
silver-label test CSV produced by the pipeline.

| Script | Checkpoint | Dataset | Output |
| --- | --- | --- | --- |
| `use_model.py` | `small_model` | `ScandEval/nordjylland-news-summarization-mini` (`test`) | Prints a handful of generations |
| `eval.py` | `small_model` | `alexandrainst/nordjylland-news-summarization` (`test`) | ROUGE + BERTScore dict |

That is a stricter setup than scoring the pipeline's own test split:
Nordjylland summaries come from TV2 Nord (editor-style), while the
training labels are machine translations of English T5 output. A drop
between trainer ROUGE (on silver validation) and `eval.py` ROUGE (on
Nordjylland) is expected. It measures domain-and-style transfer, not
just overfitting.

## Field names

`use_model.py` and `eval.py` tokenize `input_text` / `target_text` and
drop `text_len` / `summary_len`.

`ScandEval/nordjylland-news-summarization-mini` used those names when
the course code was written.

The public dataset card for
[`alexandrainst/nordjylland-news-summarization`](https://huggingface.co/datasets/alexandrainst/nordjylland-news-summarization)
now describes:

| Current card | Course script |
| --- | --- |
| `text` | `input_text` |
| `summary` | `target_text` |
| `text_len` | `text_len` |
| `summary_len` | `summary_len` |

If a current download raises `KeyError: 'input_text'`, rename columns
before `map`, or point `eval.py` at a snapshot that still uses the 2023
names. Do not assume the Alexandra set and the ScandEval mini set are
column-identical.

Published sizes on the Alexandra card (for orientation, not a promise
that Hugging Face will keep them):

- train 75,219
- validation 4,178
- test 4,178
- license CC0
- language `da`

The card also notes 181 pairs where the summary is longer than the
article. `eval.py` does not filter those.

## ROUGE

`eval.py` uses `datasets.load_metric("rouge")` with `use_aggregator=True`
and stores `*.mid.fmeasure` for every ROUGE key the metric returns
(`rouge1`, `rouge2`, `rougeL`, and usually `rougeLsum`). Predictions and
references are passed through `nltk.sent_tokenize` and joined with
newlines so ROUGE-Lsum can see sentence boundaries.

Danish ROUGE is an imperfect lexical overlap metric: compounding,
definite suffixes (`havnen` vs `havn`) and the silver-label paraphrase
stack all suppress n-gram matches even when the meaning is fine. Treat
ROUGE-2 especially as a lower bound.

## BERTScore

```python
bert_metric.compute(..., lang="da", model_type="xlm-roberta-large")
```

`lang="da"` would normally pick a recommended model; the script then
overrides that with XLM-RoBERTa large. First run downloads a sizable
checkpoint. The reported numbers are the mean precision / recall / F1
over the eval batch, not a bootstrap interval.

BERTScore is closer to “does this sound like the reference” than ROUGE,
but it is still an embedding similarity. It will not flag a fluent
summary that drops a key number (the 62 million kroner, the 1.2 km
path). For personal error analysis, read `use_model.py` printouts
alongside the scores.

## Offline analogue

`examples/compare_summaries.py` reports unigram F1 on Danish content
words between extractive silver labels and the hand-written gold in
`examples/data/sample_labeled.csv`. It is a teaching tool for “overlap
is not understanding”, not a replacement for ROUGE or BERTScore.

## Trainer vs eval script

`finetune.py` already computes ROUGE-1/2/L mid-F on the **silver**
validation split every epoch and uses ROUGE-1 to pick the checkpoint.
`eval.py` recomputes ROUGE (and BERTScore) on **Nordjylland**. Publish
or compare those two tables separately; mixing them hides the domain
shift the project is actually about.
