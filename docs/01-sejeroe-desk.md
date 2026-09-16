# Sejerø Tidende

Sejerø is a small island in the Kattegat. The eight briefs in this workbook
are fiction written for the desk: a cancelled ferry, a threatened school,
a harbour dredge, a turbine hearing, winter shop hours, a new fire tanker,
a church roof, and a seal haul-out. None of them is scraped news.

The 2023 course project built a Danish summarizer by *silver-labelling*:

1. Translate Danish news to English.
2. Summarize the English with a news-tuned T5.
3. Translate the English summary back to Danish.
4. Fine-tune mT5 on those pairs.
5. Evaluate on Nordjylland news with ROUGE and BERTScore.

That pipeline is honest about its shortcut. It is also easy to misread.
A high ROUGE-1 against a silver label can hide a missing WHEN, a swapped
WHO, or a WHY that flipped polarity. The desk keeps a gold 5W1H card and
a human oracle manchet next to each silver label so those failures have
somewhere to land.

The closed world is deliberately tiny. Eight briefs, one quote each, a
handful of connectives, and a 5 / 2 / 1 CSV split that only exists to
mirror `finetune.py`. The point is not another toy trainer. The point is
to see, without a GPU, what the 2023 hops keep from a Danish lede.

## What the desk is not

- It is not a replacement for `finetune.py`.
- It is not a dump of the 10 000-article CSV.
- It is not company code and it does not call social APIs.
- It does not download NLTK `punkt` or Hugging Face weights.

## Entry points

```bash
PYTHONPATH=. python3 -m sejeroe --help
PYTHONPATH=. python3 -m sejeroe walk --id SEJ-001
PYTHONPATH=. python3 -m sejeroe manchet
PYTHONPATH=. python3 -m sejeroe score
PYTHONPATH=. python3 examples/run_desk.py
```
