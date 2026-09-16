# Examples

CPU-only companions to the 2023 root scripts. Nothing in this folder downloads weights or talks to Hugging Face.

## What is here

| Path | Purpose |
| --- | --- |
| `text_chunking.py` | Sentence split + greedy pack used before OPUS-MT / T5 |
| `schemas.py` | Column contracts for every CSV stage |
| `demo_pipeline.py` | Validate samples, pack bodies, hash-split ids |
| `inspect_sample.py` | Print one id through raw → labeled |
| `rouge_toy.py` | Dependency-free ROUGE-N on the fixtures |
| `sample_data/` | Five fictional articles and their stage tables |

## Run

From the repository root:

```bash
python -m examples.demo_pipeline
python -m examples.inspect_sample --list-ids
python -m examples.inspect_sample --article-id aalborg-library-hours
python -m examples.inspect_sample --validate-dir examples/sample_data
python -m examples.rouge_toy
python -m unittest discover -s tests -v
```

`--refresh-splits` on the demo rewrites `sample_data/04_*.csv` from `03_labeled_dataset.csv` using the same hash function the tests expect.

## Why fixtures instead of model output

A full labeling pass needs CTranslate2 graphs and T5-base. That is the opposite of a portable example. The English and Danish strings in `sample_data/` are written by hand to look like the *shape* of the pipeline (Danish body stays put; English appears; a short summary comes back in Danish). They are not measurements of OPUS-MT or T5 quality.

If you later drop real model output into a private folder, you can still call `examples.schemas.validate_csv` with the matching column tuple.

## Packing budgets

| Runtime | Budget used in the 2023 scripts | Demo default |
| --- | --- | --- |
| OPUS-MT | `int(512 * 0.9)` = 460 | `demo_pipeline.MARIAN_BUDGET` |
| T5 news | 512 | `demo_pipeline.T5_BUDGET` |

The demo estimates length with whitespace tokens, not SentencePiece. Chunk counts will not match a real tokenizer. Use `pack_article(text, budget, length_fn=tokenizer.encode_len)` if you wire a real tokenizer later.

## Tests

`tests/` covers:

- packing overflow and comma flush
- schema errors (missing column, empty field, duplicate id)
- sample-directory id flow
- hash split membership for the five known ids
- toy ROUGE identity / unrelated pairs
