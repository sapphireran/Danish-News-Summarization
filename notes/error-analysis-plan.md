# Error-analysis plan (personal, not yet run)

I do not have generations on disk. This is the sheet I would fill before I allow myself to talk about “quality.”

## Sample construction

Draw **32** Nordjylland test rows, not 5:

| Stratum | N | How |
| --- | --- | --- |
| Random | 12 | `seed=2023` |
| Longest articles | 5 | by `text_len` |
| Shortest articles | 5 | by `text_len` (skip empty / 21-char stubs if they are junk) |
| Longest gold summaries | 5 | by `summary_len` |
| Gold longer than article | up to 5 | the known 181-card anomaly, if any fall in test and I still have budget |

32 is a weekend of reading, not a thesis. Stratifying stops me from only remembering average-length crime briefs.

Decode **once** with the training generate config. Save `notes/runs/<id>/samples.jsonl` with `id`, source, gold, pred, lengths, ROUGE-1, BERTScore F1. Then rate in a spreadsheet without the automatic columns visible.

## Codes I would put on each row

Short codes, stackable:

| Code | Meaning | Usually blamed on |
| --- | --- | --- |
| `EN` | Output not Danish | mT5 / pivot residue |
| `COPY` | Near-extractive first sentences | student shortcut |
| `LEAD` | Ignores the rest of the article | map-reduce + 128-token labels |
| `ENT` | Wrong person / place / org | OPUS hops |
| `NUM` | Wrong number, date, age | T5 + MT |
| `POL` | Wrong party / office / charge | high severity ENT |
| `GEN` | Generic news sentence | over-compression |
| `REP` | Loops or synonym churn | decode knobs |
| `LONG` | Much longer than gold without adding facts | silver style |
| `SHORT` | Drops the actual news | length_penalty / min_length |
| `HALL` | Invented event | English T5 |
| `OK` | I would ship this to a classmate as a demo | — |

A row can be `OK+LONG`. `HALL` and `POL` never sit next to `OK`.

## Questions I would answer in prose after the 32

1. Are `ENT` errors already visible in the English hop if I still have `translated_articles.csv` for the same `id`? If yes, stop blaming mT5.
2. Do `LEAD` errors correlate with `text_len` > 2,000? If yes, the packer-as-summarizer design is the story.
3. Is `LONG` the dominant non-fatal code? If yes, silver labels are too chatty for Nordjylland and I should shorten T5 before I train another large model.
4. Do high BERTScore rows still carry `HALL`? If yes, I write that sentence in the README and I stop treating BERTScore as comfort.
5. Is `COPY` secretly winning ROUGE? If lead-N beats me and humans prefer gold, ROUGE is not on my side and I should say so.

## What I will not do

- I will not rate my own 5 cherry-picked fluent outputs and call it a user study.
- I will not post-edit predictions and then score them.
- I will not drop `HALL` rows from the automatic average.

## If I cannot recover the 10k dump

Error analysis still works on Nordjylland alone. I lose the “blame the hop” question (1) unless I re-translate those 32 articles with the same OPUS setup. That mini-pivot on 32 rows is cheap and I would do it even without the original dump.
