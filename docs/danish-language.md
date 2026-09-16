# Danish notes for an English teacher

The hop assumes that English news style is a neutral interlingua. It is not.
These are the language facts that bite a silver-label pipeline.

## Compounds and definite suffixes

Danish glues where English splits: *spejlteleskopet*, *målestationen*,
*ungdomsskolen*. An English T5 will happily summarize "the mirror telescope"
and the back-translation may return *teleskopet* or *spejlteleskop*. ROUGE
then punishes a perfectly good student. The lab tokenizer does not stem, so
that cost stays visible.

Definite meaning often lives in a suffix (`-en`, `-et`, `-ene`) rather than
in a separate article. Dropping the suffix can look like a small lexical
change and still flip givenness.

## Abbreviations the splitter must not cut

The 2023 scripts download `punkt`. The lab keeps an explicit list:
`f.eks.`, `bl.a.`, `ca.`, `kl.`, `dr.`, `nr.`, `kr.`, `pct.`, `osv.`,
`hhv.`, `dvs.`, `pga.`, and a few more in `silverlab.sentences.ABBREVIATIONS`.
Decimals (`12.5`) are protected separately.

If a splitter cuts `kl. 21` into a new sentence, the rain-backup fact in
`lab-01` becomes an orphan and the English teacher never sees it.

## Named entities that rhyme

Danish place names share onsets: Skørping / Skærbæk / Skive, Hobro / Holbæk,
Odense / Odder. After a trip through English they are one edit away from
each other — or from a better-known foreign city (Odense / Odessa,
Tórshavn / Tromsø). The catalog tags those as `ENT`.

## Numerals and units

Danish news writes `80`, `kl. 21`, `12 kilometer`, `40 kilo`, `to meter`.
English teachers like to round and to prefer SI words they have seen more
often. A metres-to-kilometres promotion is fluent and wrong. BERTScore can
still look kind. Faithfulness on the rubric should not.

## Word order and the v2 habit

Danish main clauses are verb-second. Back-translation sometimes lands an
English SVO calque that is readable and slightly off (`får premiere` from
"get premiere"). That is `STYLE`, severity 2–3, unless it also drags an
English word along.

## Why lead-k is not an English-only trick

Danish local news still fronts the event. The fiction briefs are written
that way on purpose, so lead-1 against extractive gold is a ceiling, not a
curiosity. A student that loses to lead-2 on faithfulness is not "more
abstractive". It is less trustworthy.
