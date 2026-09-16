# English summarization stage

**Script:** `summary.py`  
**Teacher model:** `mrm8488/t5-base-finetuned-summarize-news`  
**Input column:** `translated` (English)  
**Output column:** `summary` (still English at this stage)

This is the only stage that *creates* new semantic content. Translation hops are meant to preserve meaning. The T5 hop is allowed to drop, merge, and rephrase.

## Why this checkpoint

`t5-base-finetuned-summarize-news` is a T5-base model further trained on English news abstracts. It matches the pivot language and the news domain. It does not know Danish. That is why the article has to be English before this script runs.

T5-base is 220M parameters — small enough to run with beam 2 on a single consumer GPU at 512 input tokens.

## Chunk-then-summarize

News bodies are often longer than 512 T5 tokens. The script reuses the same sentence-pack idea as translation:

1. `sent_tokenize` the English article.
2. Split over-long sentences with the character / punctuation heuristic.
3. Pack into sub-articles of ≤ 512 T5 tokens.
4. `summarize()` each sub-article independently (`max_length=80`).
5. `" ".join(sub_summaries)`.

Implications:

- A 3×512 article yields up to ~240 T5 tokens of summary (3 × 80), which is longer than the 128-token cap used later in mT5 training. The back-translation hop does not truncate. `finetune.py` **will** truncate those long silver labels at 128 tokens.
- Every chunk is represented in the joined summary. The teacher rarely writes a single lede-style abstract for a long piece; it writes a concatenation of local abstracts. mT5 will imitate that multi-lede style.
- Chunk boundaries can cut anaphora. The summarizer then invents or drops entities.

`examples/chunking/demo_chunking.py` prints how a long sample article is packed, using a whitespace stand-in tokenizer so you can see the groups without downloading T5.

## `generate()` settings

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

| Knob | Value | Effect |
| --- | --- | --- |
| `num_beams` | 2 | Mild search; cheap |
| `max_length` | 80 | Hard cap per chunk, including decoder start |
| `repetition_penalty` | 5.0 | Very strong. Suppresses loops; can also block legitimate repeated names |
| `length_penalty` | 1.0 | Neutral (beam scores not biased short/long) |
| `early_stopping` | True | Stop when `num_beams` complete hypotheses exist |

There is no `min_length` here. Empty-ish decodes are possible on garbage input.

The output filename `summarized_file_ml80_rp5.0.csv` is a reminder of `max_length` and `repetition_penalty`. If you sweep those two, keep the filenames distinct.

## Debug slice

```python
df = pd.read_csv(input_file_path)[:10]
```

This is easy to miss. Ten rows is enough to test the hop, not enough to train. Remove `[:10]` for a corpus run.

## Device

The T5 model is `.to(device)` with CUDA if available. Unlike CTranslate2, this is a full Transformers generate loop. Batch size is 1 sub-article. The script does not use `generate` padding / encoder batching across sub-articles of the same document, even though that would be straightforward.

## What the silver summaries look like

Expect:

- Short, journalistic English
- Occasional hallucination of numbers and titles (T5 news models do this)
- Repeated entity names when chunks overlap thematically
- A flatter discourse structure than a human abstract (no "the story overall is X")

After `translate_back.py` those traits become **Danish translationese** of English news-T5. That is the distribution `finetune.py` fits.

## Not done in this script

- No prefix like `summarize:` is added. This particular checkpoint is already news-specialized; the code encodes the raw English chunk.
- No trigram blocking (`no_repeat_ngram_size`). Repetition is handled only by `repetition_penalty=5.0`.
- No ROUGE filter against the English source (would require a reference you do not have).

## Related example files

- `examples/data/summarized_articles.sample.csv` — four-column shape after this hop
- `examples/configs/summarize.yaml` — the numeric defaults in one place
- `docs/07-hyperparameters.md` — same numbers next to training / eval
