# Evaluation without weights

`eval.py` needs `google/mt5-small` as a tokenizer name, a local
`small_model` directory, `datasets.load_metric("rouge")`, and
BERTScore with `xlm-roberta-large` in Danish. That is a long first
run even when you already believe the method.

The study kit keeps three laptop numbers:

| number | what it is | what it is not |
| --- | --- | --- |
| ROUGE-1 / 2 / L | word n-gram and LCS F1 | the official ROUGE perl script |
| entity retention | gold mention survival | NER |
| compression | summary words / source words | a quality score |

BERTScore is omitted on purpose. A laptop that can fetch
`xlm-roberta-large` can also run the original `eval.py`.

## How the committed gazette scored

On the ten stories, extractive oracle back-translation lands around
the mid-0.4s ROUGE-1 against the hand-written gold Danish summaries.
That is expected: the gold summaries are abstractive and short; the
oracle hop is extractive and long. Gloss hops sit a little lower.

Do not compare those figures to a 2023 `eval.py` log. Different
references, different languages-in-the-middle, different summarisers.

## When to trust a number

* Trust **retention** to answer "did this hop drop Lisbeth Holm?".
* Trust **oracle vs gloss** to answer "is the damage from translation
  or from dropping sentences?".
* Distrust **absolute ROUGE** as a claim about mT5-large.
