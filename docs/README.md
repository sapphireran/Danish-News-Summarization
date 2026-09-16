# Documentation index

These notes describe the personal 2023 ITU final project in this repository: a Danish news summarizer trained on silver labels from an English pivot.

Read this page first, then follow the numbered guides. The `examples/` tree is the hands-on companion: same CSV schemas, no GPU weights.

## What this project is

A research-style pipeline, not a packaged product.

- **Input:** Danish news article text.
- **Training target:** a Danish summary produced automatically (translate → English summarize → translate back).
- **Model:** multilingual T5 fine-tuned as a seq2seq summarizer.
- **Evaluation:** official Nordjylland news summarization pairs, scored with ROUGE and BERTScore.

The interesting claim is not “we invented a new architecture.” It is “can noisy cross-lingual silver labels teach a multilingual encoder-decoder to summarize Danish news well enough to score on a human-labeled test set?”

## Suggested reading order

| Order | Doc | What you get |
| --- | --- | --- |
| 1 | [pipeline.md](pipeline.md) | Stage-by-stage data flow, file names, and why articles are chunked |
| 2 | [datasets.md](datasets.md) | CSV columns, public eval sets, and the example corpus |
| 3 | [models.md](models.md) | OPUS-MT, English T5, mT5, CTranslate2, generation settings |
| 4 | [evaluation.md](evaluation.md) | ROUGE vs BERTScore, Danish tokenization caveats |
| 5 | [script-reference.md](script-reference.md) | Every root script: inputs, outputs, hardcoded paths |
| 6 | [reproduction.md](reproduction.md) | Environment, disk, and a safe dry-run path |
| 7 | [known-issues.md](known-issues.md) | Script/README mismatches worth fixing before a full rerun |
| 8 | [design-notes.md](design-notes.md) | Why the pivot exists and where label noise comes from |

## Mental model

```
Danish article
    │
    ▼
OPUS-MT da→en  (CTranslate2)
    │
    ▼
English T5 news summarizer
    │
    ▼
OPUS-MT en→da  (CTranslate2)
    │
    ▼
silver pair (da body, da summary)
    │
    ▼
fine-tune mT5
    │
    ▼
Nordjylland test set → ROUGE + BERTScore
```

Chunking sits under both translation steps and the English summarizer. Those models have a 512-token comfort zone. Long Jutland news stories do not. The algorithm is documented in [pipeline.md](pipeline.md) and reimplemented without NLTK in `examples/text_chunking.py`.

## What is intentionally not here

- Trained weights (`small_model`, `large_model`, `models/*_ct2`)
- The original 10k-article dump
- Course report PDFs or slides

Those artifacts stay local. The docs plus `examples/data/` are enough to understand the shapes and try the plumbing.

## Related personal files

- Root scripts are the 2023 course code, left in place.
- `examples/` is new documentation-as-code: schemas, a sample corpus, chunking, and toy metrics.
- `requirements.txt` lists the heavy stack for the root scripts only.
