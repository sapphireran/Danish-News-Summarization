# English summarization stage

`summary.py` is the only stage that is allowed to be English-only. It
reads `translated_articles.csv` and writes
`summarized_file_ml80_rp5.0.csv`.

## Model

```text
mrm8488/t5-base-finetuned-summarize-news
```

That checkpoint is a T5-base model fine-tuned on English news
summarization. It is **not** multilingual. Feeding it Danish `body`
text produces garbage. Always summarize the `translated` column.

The script currently processes only the first 10 rows:

```python
df = pd.read_csv(input_file_path)[:10]
```

Treat that as a debug leftover. A full silver-label run must drop the
slice or replace it with an explicit `--limit` you choose on purpose.

## Generation settings

```python
model.generate(
    input_ids=input_ids,
    num_beams=2,
    max_length=80,
    repetition_penalty=5.0,
    length_penalty=1.0,
    early_stopping=True,
)
```

| Knob | 2023 value | Effect |
| --- | --- | --- |
| `num_beams` | 2 | Light beam search. Cheap, slightly stabler than greedy. |
| `max_length` | 80 | Hard cap per **chunk**, not per article. |
| `repetition_penalty` | 5.0 | Very high. Suppresses loops; can also drop repeated entities. |
| `length_penalty` | 1.0 | Neutral. No extra pressure toward short or long beams. |
| `early_stopping` | True | Stop when `num_beams` complete hypotheses exist. |

The output filename records two of these (`ml80`, `rp5.0`) so later
experiments can sit next to each other without overwriting. If you
change the knobs, change the filename too.

## Chunk-then-concatenate

The English T5 is used with `text_max_length = 512`. The same
sentence-packing helper as `translate.py` splits a long English article
into windows. Each window is summarized independently. The silver label
is:

```python
summary = " ".join(sub_summaries)
```

Consequences:

- A 2,000-token feature can become three 80-token summaries glued
  together, i.e. a ~240-token target. `finetune.py` later truncates
  labels at 128 tokens, so the tail of those concatenated labels is
  thrown away at train time.
- Cross-window coreference is invisible to the summarizer. "The mayor"
  in window 2 may be a different person from window 1 as far as T5
  knows.
- Lead bias stacks: each window tends to emphasize its own first
  sentences, so the joined summary can read like several ledes.

A later personal rerun should either:

- summarize only the first window (lossy, but length-honest), or
- summarize each window and then run a second-pass "summary of
  summaries" with a lower `max_length`, or
- switch to a long-context English summarizer and drop chunking.

## Tokenization details

`summarize()` encodes the whole window in one `tokenizer.encode` call
without truncation arguments. If packing failed and a window still
exceeds the model max length, Transformers will warn or error depending
on version. Fix packing first; do not silently `truncation=True` here
or you will summarize a chopped sentence and never notice.

`clean_up_tokenization_spaces=True` is passed to `decode`. That is
appropriate for English news text.

## Why this model and not the mT5 being trained

Using the student model to label its own training data would collapse
the factory. The English T5 is an external teacher. mT5 only sees the
final Danish pairs. That is the whole point of the pivot.

## Personal smoke test

Before a long run:

1. Take 5 synthetic or held-out articles.
2. Translate them (or use the fixtures in `examples/data/`).
3. Run `summary.py` with the `[:10]` slice left on.
4. Read the English summaries. If they miss the news lede or invent
   facts, the silver labels will teach those mistakes.
5. Only then remove the slice.

`examples/scripts/extractive_summarize.py` is a no-GPU stand-in: it
picks the first N sentences of the English (or Danish) text. That is
not the course model, but it lets the CSV contract and the later
translate-back stage be exercised.
