# Quotes, attribution, and connectives

`summary.py` generates with two beams, `max_length=80`, and
`repetition_penalty=5.0`. That recipe likes a compressed lede and often
drops the quoted clause. `translate_back.py` then sees English without
Danish quotation marks (`»…«`) and without `siger`.

The desk records one quote per brief: speaker, Danish span, English span,
and the cue (`siger` / `said`). A quote is marked *kept* if the span is
present or if the speaker is present and at least 45 percent of the quote
tokens still overlap.

On the silver Danish labels in this workbook the quote is almost always
gone. The oracle keeps it for `SEJ-001`, `SEJ-002`, and the later briefs
where the spoken sentence *is* the news.

## Connectives

The briefs lean on a small Danish set:

| Word | Job in the manchet |
| --- | --- |
| `ifølge` / `Ifølge` | Attribution without a full quote |
| `hvis` / `Hvis` | Weather, ice, majority, ferry cancellation |
| `men` | Contrast: extra sailing *but* no bikes; power *but* no industrial horizon |
| `fordi` | Enrolment, cable, November sales |

Losing `men` is worse than losing an adjective. `SEJ-004`'s quote is
exactly that contrast: *strøm, men ikke en industrihorisont*. The silver
label keeps "turistforeningen er imod" and drops the spoken contrast.

`SEJ-008` is the ethical case. The ranger says the seals are **not** ill.
A planted WHY flip that claims they are sick would be a harmful silver
label and still share most unigrams with the true summary.
