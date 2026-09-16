# Extractive baselines

The 2023 project never printed a lead-k number. That is the first thing I
would run now. If lead-2 already hugs a gold extractive sentence, the silver
pipeline is not "adding abstraction"; it is risking facts for style.

## What is implemented

All five live in `silverlab.baselines` and run from
`python3 -m silverlab baselines`.

| Name | Rule | Default k |
| --- | --- | --- |
| `lead1` | First sentence | 1 |
| `lead2` | First two sentences, original order | 2 |
| `longest` | Most tokens, ties broken by earlier index | 1 |
| `keyword` | Title content-word overlap | 2 |
| `textrank` | PageRank on a sentence graph | 2 |

TextRank edge weight between sentences *i* and *j* is content-word overlap
divided by `log(|i|+1) + log(|j|+1)`, then 40 iterations of PageRank with
damping 0.85. Selected sentences are **always emitted in document order**,
so a high-scoring last sentence does not appear before the lede.

Keyword falls back to lead-1 when the title has no content words. That is
deliberate: an empty title should not look like a sophisticated graph.

## How to read the scores

```bash
python3 -m silverlab metrics --against extractive
python3 -m silverlab metrics --against abstractive
```

- Against **extractive** gold: you are asking whether the baseline can find
  the sentence I copied out of the article. Lead-1 should be strong on this
  corpus because I wrote inverted-pyramid briefs on purpose.
- Against **abstractive** gold: you are asking how much lexical overlap a
  rewrite still shares. Low ROUGE-2 is expected. That is not a student-model
  failure.

Do not compare these F-measures to a remembered mT5 run. Different gold,
different tokenizer, different documents.

## Why fiction, not Nordjylland

Nordjylland summaries are real newsroom text. Pulling them into git as a
"sample" would either violate the point of a tiny lab or quietly freeze a
slice I do not have a license sheet for in this folder. The fiction briefs
are mine. They are long enough that the five baselines can disagree — see
`lab-01`, where Saturn lives in the first sentence and the rain backup lives
in the fifth.

## Implementation notes

- Tokenization is `silverlab.tokenize.tokenize`, not Hugging Face.
- Sentence boundaries are `silverlab.sentences.split_sentences`, not `punkt`.
- There is no stemming. Danish definite suffixes (`teleskopet`, `kuplen`)
  therefore cost recall against a rewrite that uses the bare noun. That is a
  feature of the metric, documented in [danish-language.md](danish-language.md).
