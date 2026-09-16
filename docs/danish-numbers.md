# Danish number surfaces the 2023 scripts never normalize

`translate.py` and `summary.py` split on NLTK tokens and characters. They
never parse a number. The packer will happily cut `3.200 kr.` in the
middle, and the T5 will happily emit `3200` without a currency.

## Decimal comma vs thousand dot

| Surface | Meaning | English pivot often writes |
| --- | --- | --- |
| `47,2` | 47 + 2/10 | `47.2` |
| `3.200` | three thousand two hundred | `3,200` or `3200` |
| `1.234,56` | 1234 + 56/100 | `1,234.56` |
| `1,2 mio.` | 1.2 million | `1.2 million` |

The dangerous pair is `2,4` / `2.4` / `24`. Once the English summary
loses the point, the Danish back-translation has no comma to restore.
`maalestok.measures.parse_da_number` treats a lone dotted group of three
as thousands (`3.200` → 3200) and a lone comma as a decimal
(`47,2` → 47.2). That is the parish convention, not a claim about every
Danish CSV.

## Clocks

Almanac Danish writes `kl. 8.15`, `kl. 08.15`, `06.00–09.30`,
`man.–tors. 13.00–17.00`. English news T5 writes `8:15 AM`, `6–9:30 a.m.`,
`1–5 p.m.`. Two failures show up in the fixtures:

* **12-hour wrap** — `kl. 8.15` → `8:15 AM` → `kl. 20.15` (`bh-03`)
* **range drift** — `13.00–17.00` → `13:00–19:00` (`bh-08`),
  `09.00–14.00` → `09.00–16.00` (`bh-15`)

Punkt-on-English also likes to split on `kl.` and on the clock dots.
The lab splitter protects those on purpose; the 2023 scripts do not.

## Money

`kr.` is an abbreviation *and* a unit. `1,2 mio. kr.` is a scaled unit.
`3.200 kr.` is a thousand-grouped unit. A tokenizer that peels `kr.` as
its own token makes the packer's comma-flush path irrelevant and the
NLLB `hypotheses[0][1:]` path dangerous when a summary starts on the
amount.

`dollar` in `bh-02` is the planted currency swap. The 2023 English T5
was trained on US/UK news. It does not owe Blåhøj a kroner.

## Dates and feasts

`12. juni` is an ordinal day plus a month, not the end of a sentence.
`3. søndag i advent` is an ordinal feast. After a pivot that says
`third Sunday`, Advent and Lent are interchangeable for a model that
has no church calendar. That is `bh-04`.

## Signed weather

Unicode minus `−8,3 °C`, ASCII `-8.3 C`, and `8.3 degrees below` are
three surfaces. Drop the sign and the night is a mild January morning
(`bh-06`). The extractor keeps the sign on the `Measure` so the ledger
can name `sign_drop` instead of `value_shift`.
