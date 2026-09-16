# Why measures die on the silver-label hops

The 2023 method is four models in a row:

```
Danish article
  → OPUS-MT da→en
  → English news T5 (max 80 tokens, repetition_penalty 5.0)
  → OPUS-MT en→da
  → mT5 fine-tune on (body, silver summary)
```

A later eval against Nordjylland-News then asks mT5 for Danish prose and
scores ROUGE / BERTScore. That protocol is almost silent on whether `2,4 ha`
is still `2,4 ha`.

## What a hop is allowed to rewrite

Translation is allowed to change *surface*. `47,2 mm` becomes `47.2 mm`.
`3.200 kr.` becomes `3,200 kr.` or `3200 DKK`. `kl. 8.15` becomes `8:15 AM`.
`3. søndag i advent` becomes `the third Sunday of Advent`. None of those
rewrites are errors by themselves.

Summarization is allowed to *drop*. The English T5 was trained on English
news leads. It keeps the first fact and the last colour sentence. A yield
in `t/ha`, a signed night temperature, and a bus line number sit in the
middle and look like decoration.

Back-translation is allowed to *guess the surface back*. If the summary
says `8:15 AM`, the Danish side may emit `kl. 8.15` or `kl. 20.15`. If it
says `2.4 ha`, the comma may come back as `2,4` or vanish (`24 ha`). If it
says `3,200 kr.`, a model that has seen more dollars than kroner will
write `dollar`.

## What this lab counts

`maalestok` does not rerun OPUS-MT. It stores a hand-written pivot, an
English summary with the scars the 2023 stack invites, a silver Danish
line, and an oracle Danish line that keeps the source measures.

The ledger then asks, for each source measure:

* did a counterpart appear?
* is the normalized value the same?
* if not, which named failure is it (`comma_shift`, `sign_drop`,
  `clock_12h`, `currency_swap`, `unit_swap`, `feast_swap`, `scale_shift`,
  `dimension_shift`, `line_swap`, `precision_loss`)?

Lead-2 (the first two Danish sentences) is the extractive control. On
front-loaded almanac prose it keeps more numbers than the silver line,
which is the whole point of writing the lab down: the 2023 hops are not
a free label.

## What this is not

It is not a 2023 scoreboard. The original `eval.py` printout was never
committed. Inventing an mT5 ROUGE table would be a different kind of
lie than planting a `24 ha` scar on a story that already contains `2,4 ha`.
