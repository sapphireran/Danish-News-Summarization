# Silver labels versus extractive and editorial Danish

The 2023 project never pretends the automatically generated Danish summaries
are gold. This page is the vocabulary for the three Danish abstracts that
exist for every article in `examples/lib/sample_corpus.py`.

## Three summaries, one article

Take `da-001` (the fictional North Jutland storm).

**Extractive (toy pipeline).** The first two sentences of the body. Faithful,
often too long, and it keeps every number that happened to sit in the lede.
It will mention Energinet and 14,000 households because the journalist put
those facts first. It will not mention Friday’s last 60 kV line if that fact
lives in the tail.

**Pivot silver (`summary_da_pivot`).** A short Danish rendering of an English
news-T5 abstract. It compresses, it reorders, and it sometimes prefers a
calque (“tvang Aalborg til at åbne tre herberger”) over the idiom a local
desk would pick. This is what `finetune.py` sees as `summary`.

**Editorial (`summary_da_editorial`).** A tighter Danish lede written as if a
human editor had filed the abstract. Word choice is more local (`nødherberg`,
`fuld genetablering`). This is what `nordjylland_like_eval.csv` stores as
`target_text`, standing in for Nordjylland’s human references.

The toy pipeline’s Jaccard score against the pivot labels is *supposed* to be
modest. If it ever climbs toward 1.0, the hand-written pivot labels have
collapsed into the lede and you are no longer documenting the course method.

## Why the student model can look “English”

mT5 copies the pivot distribution. After a long train you should expect:

- sentence-initial `En` + noun + number, the T5-news template,
- fewer subordinate clauses than a Politiken abstract,
- entities that survived both OPUS hops, not the ones that died in chunk 3.

Scoring that model on editorial Nordjylland text is therefore a domain shift,
not just a language shift. [evaluation.md](evaluation.md) is written with
that shift in mind.

## How to read the example comparison file

After `python examples/toy_labeling_pipeline.py` open
`examples/output/extractive_vs_pivot.csv`.

| Column | Meaning |
| --- | --- |
| `id` | article id |
| `jaccard` | unigram Jaccard between extractive and pivot |
| `extractive` | first-N Danish sentences |
| `pivot_silver` | hand-written “T5-via-OPUS” Danish |

Sort by `jaccard`.

- **High Jaccard** (`da-011`, the short museum note) — the article *is* a
  lede. Pivot and extractive have nothing else to say.
- **Low Jaccard** (`da-006`, `da-012`) — the body has hearing procedure,
  finance, and local colour. The pivot abstract picked the energy/politics
  spine; the extractive baseline stopped after the first two sentences.

That is the same failure mode a real 10k run will have, except the English
teacher can also hallucinate a spine that was never in the body. The example
corpus does not hallucinate; the GPU pipeline can.

## Filters the course scripts never had

If you rebuild silver labels, consider dropping a row when:

1. the English summary is shorter than 40 characters,
2. the Danish back-translation still contains English function words
   (`the`, `and`, `of`) at high rate,
3. the joined chunk summaries exceed 128 tokens (they will be truncated),
4. a proper noun in the summary does not appear in the Danish body
   (after a simple case-fold check).

None of those filters are in `translate_back.py`. The example validator only
checks schema and `æ/ø/å`, not factual overlap. Adding a noun-overlap check
on the 12-row corpus is a good personal extension; it will not scale to
messy OCR dumps without a gazetteer.

## Genre mix

The twelve rows are balanced on purpose:

| Genre | ids | Why it is here |
| --- | --- | --- |
| weather | `da-001` | classic news T5 comfort zone |
| transport | `da-002`, `da-009` | plans vs breaking operations |
| research | `da-003` | abstract-heavy nouns |
| sport | `da-004` | names, minutes, table position |
| municipal | `da-005` | coalition math |
| energy | `da-006` | long hearing text, packer stress |
| labor | `da-007` | conditions and carve-outs |
| culture | `da-008`, `da-011` | event + short museum |
| housing | `da-010` | waiting lists, local plans |
| economy | `da-012` | long feature, packer stress |

A real dump will not be balanced. If you sample 10k outlet articles you will
over-represent crime and football. The example mix is a teaching set, not a
prior over Danish news.
