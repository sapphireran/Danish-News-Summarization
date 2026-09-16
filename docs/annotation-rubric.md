# Annotation rubric

I did not keep a 2023 human eval sheet. This is the sheet I would use on a
50-article sample before believing any automatic table.

Five axes, each 1–5. Score the **summary against the article**. The optional
gold rewrite is only for the coverage axis when you have one.

## Axes

### Faithfulness

Does every content word in the summary have a home in the article?

| Score | Anchor |
| --- | --- |
| 1 | Contradicts a load-bearing fact |
| 2 | Invents a beneficiary, number, or place |
| 3 | One unsupported modifier |
| 4 | All facts traceable; mild paraphrase |
| 5 | Nothing I would mark with `ADD`, `ENT`, or `NUM` |

### Coverage

Are the article's load-bearing facts present?

| Score | Anchor |
| --- | --- |
| 1 | Wrong event |
| 2 | Missing who or when |
| 3 | Lede only; backup plan / price / condition gone |
| 4 | Lede plus one constraint |
| 5 | Lede, constraint, and the detail I would put in a standfirst |

### Fluency

Would I read this aloud on local radio?

| Score | Anchor |
| --- | --- |
| 1 | Broken syntax |
| 2 | Repeated phrases or missing sentence boundary |
| 3 | Readable but clumsy |
| 4 | Fine news Danish |
| 5 | Something a desk would ship without a copy pass |

### Conciseness

Is the summary a summary?

| Score | Anchor |
| --- | --- |
| 1 | Almost the article, or two tokens |
| 2 | One clause, or a ramble past 60 tokens |
| 3 | Slightly thin or slightly long |
| 4 | Tight |
| 5 | 8–42 tokens and no throat-clearing |

### Danish naturalness

Does it sound like it was born in Danish?

| Score | Anchor |
| --- | --- |
| 1 | Mostly English |
| 2 | Mixed calque (`from a tent on the square i Thisted`) |
| 3 | Grammatical but translated (`får premiere`) |
| 4 | Native, maybe one anglicism |
| 5 | Compounds and definite suffixes sitting where a Dane would put them |

## Heuristic scorer

`silverlab.rubric.score_rubric` is a **lab instrument**. It rewards content-word
support, punishes leftover English, and likes 8–42 token summaries. It cannot
see that Saturn became Saturday. That is why the [error catalog](error-catalog.md)
exists.

```bash
python3 -m silverlab rubric
python3 -m silverlab rubric --id lab-01
```

The CLI scores **lead-2** against the gold abstractive rewrite. That is a
baseline sanity check, not a model eval.

## Protocol if I annotate again

1. Sample 50 articles stratified by length.
2. Two annotators, independent, then a 30-minute adjudication.
3. Write codes from the catalog onto every score below 4 on faithfulness.
4. Store a JSON line per article next to the checkpoint hash.
5. Never average the five axes into a single "quality" without showing the
   faithfulness column first.
