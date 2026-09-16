# Evaluation

Two scripts look at a trained checkpoint. They answer different questions.

| Script | Question | Output |
| --- | --- | --- |
| `use_model.py` | Does a generation look like Danish news? | Printed triples |
| `eval.py` | How close are generations to a Danish reference set? | ROUGE + BERTScore dict |

Neither script evaluates the silver-label test CSV (`datasets/test_dataset.csv`). That file is loaded in `finetune.py` but never passed to the trainer. In-training validation ROUGE is computed on `datasets/validation_dataset.csv` only.

## Qualitative inspection

`use_model.py` loads `ScandEval/nordjylland-news-summarization-mini` test, tokenizes `input_text` / `target_text`, and runs `model.generate` on the first five batches of size 2.

Each printed block has three sections:

1. **Input's Text** — `split_dataset["test"]["input_text"][i]`
2. **Summary Text (True Value)** — decoded labels from the batch
3. **Summary Text (Generated Text)** — decoded hypotheses

There is a small indexing hazard: the input text is taken with the batch index `i` (0..4), while each batch contains two rows. The printed "input" is therefore the i-th dataset row, not necessarily the row that produced `text_preds[0]` in that batch. Read the printed input as a nearby example, not a perfectly aligned triple, unless you change the script to index with `i * batch_size`.

Things worth watching in the printout:

- Language: is the hypothesis Danish, English, or mixed? mT5 can slip into English if silver targets were noisy.
- Lead bias: does the model copy the first sentence and stop?
- Named entities: are towns, agencies, and numbers preserved?
- Length: training `min_length=9` vs inspection `no_repeat_ngram_size=1` can yield short, jumpy strings.

## Automatic metrics in `eval.py`

`compute_metrics` receives generated token ids and label ids from `Seq2SeqTrainer.evaluate()`.

Preprocessing before both metrics:

1. `batch_decode` predictions with `skip_special_tokens=True`.
2. Replace label `-100` with `pad_token_id`, then decode.
3. `strip` and NLTK `sent_tokenize` each string.
4. Re-join sentences with `\n`.

The newline join is the ROUGE-Lsum convention used by the Hugging Face summarization examples: ROUGE-L can then score at sentence level.

### ROUGE

```python
rouge_metric = datasets.load_metric("rouge")
rouge = rouge_metric.compute(..., use_aggregator=True)
```

Reported keys:

| Key | Source |
| --- | --- |
| `rouge_rouge1_mid_fmeasure` | `rouge['rouge1'].mid.fmeasure` |
| `rouge_rouge2_mid_fmeasure` | `rouge['rouge2'].mid.fmeasure` |
| `rouge_rougeL_mid_fmeasure` | `rouge['rougeL'].mid.fmeasure` |
| `rouge_rougeLsum_mid_fmeasure` | if the aggregator provides `rougeLsum` |

The dict comprehension is `{f'rouge_{key}_mid_fmeasure': value.mid.fmeasure for key, value in rouge.items()}`, so the key names include a doubled `rouge` prefix. Training's `compute_metrics` uses cleaner names (`rouge_1_mid_fmeasure`). Do not compare those strings blindly.

`datasets.load_metric` is deprecated. The modern call is `evaluate.load("rouge")`. Scores should stay comparable if the underlying `rouge-score` package is the same.

ROUGE-1/2 are surface overlap. They punish valid paraphrases and reward extractive copies. On silver-label models this often over-states quality when the system copies the lede, and under-states quality when it rephrases a correct fact.

### BERTScore

```python
bert_metric = datasets.load_metric("bertscore")
bert_metric.compute(..., lang='da', model_type="xlm-roberta-large")
```

Reported keys (means over the eval set):

- `bertscore_precision`
- `bertscore_recall`
- `bertscore_f1`

BERTScore uses contextual embeddings, so a Danish paraphrase can still score well. `xlm-roberta-large` is heavy; the first eval download is slow. `lang='da'` selects the recommended model for Danish when `model_type` is omitted; here `model_type` is set explicitly, so `lang` is mostly documentation.

## What the numbers can and cannot say

The eval set is Nordjylland News summarization. Training targets are machine-translated T5 blurbs. A high ROUGE on Nordjylland would mean the silver-label model transferred to that reference style. A low ROUGE can mean any of:

- Silver labels taught a different summary length or tone.
- Translationese leaked into the decoder.
- Decode settings at eval time do not match training (`eval.py` does not pass the `AutoConfig` generation knobs from `finetune.py`).
- The checkpoint on disk is `small_model` (maybe under-trained) rather than `large_model`.

In-training ROUGE on `validation_dataset.csv` measures consistency with **silver** labels, not with Nordjylland. You can overfit silver style and still look weak on `eval.py`.

## Toy overlap without GPU

`examples/rouge_toy.py` implements a tiny ROUGE-N F1 on token sets so the idea of unigram/bigram overlap is visible on the sample summaries. It is not the official `rouge-score` package and should not be quoted as a project result.

```bash
python -m examples.rouge_toy
```

## Suggested extra checks (not in the 2023 scripts)

If you extend evaluation later, useful personal additions are:

- Language ID on hypotheses (flag English leaks).
- Mean generated length vs reference length.
- Entity overlap (numbers, dates, place names) on a hand-checked slice.
- A 20-example error sheet: hallucination, omission, wrong polarity.

Those are notes, not implemented jobs.
