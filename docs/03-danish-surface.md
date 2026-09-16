# Danish surface form

The 2023 scripts treated Danish as “whatever Punkt and OPUS-MT accept”.
That is workable for news prose and sloppy at the edges this workbook
cares about.

## Abbreviations versus sentence boundaries

`nltk.sent_tokenize` is English-tuned. Danish news is full of `kr.`,
`bl.a.`, `f.eks.`, `kl.`, `mio.`, `pct.`. The workbook splitter keeps
those from ending a sentence when the next word is lowercase
(`40 kr. for voksne`) and *does* split when a new sentence starts with
a capital (`15 kr. Pressen kræver…`). `kl. 23:40` stays one sentence.

That choice is documented so the lead-2 control is deterministic. It is
not a claim that the 2023 Punkt splits matched it.

## Decimal comma and clock time

`3,5 km` is a number, not two sentences. `23:40` is a time token, not
`23` and `40`. The entity layer canonicalises times to `HH:MM` so
`23:40` and `23:30` are different values. Years in `1800–2099` are
their own kind, which is how `1904` → `1914` shows up as a lost year
rather than a lost integer.

## æ, ø, å

`Lærke Holm` is a different surface from `Larke Holm`. The pivot on
`kz-07` drops the æ and the silver label never puts it back. The
gazetteer lists `Larke Holm` as an alias so the *person* can still be
counted as present — and the planted `NAME-STUCK` scar still records
that the Danish spelling died. Those are two different questions:
“is the person mentioned?” versus “did the Danish name survive?”

## Compounds

Danish news loves long closed compounds. The English pivot usually
splits them (`messingorkester` → `brass band`, `håndpresse` →
`letterpress`). The silver hop then has to choose a Danish word. It
does not always choose the source word. `letterpress` comes home as
`trykpresse`. `bladderwrack` comes home as `tang`.

The compound list in `kystlinje/world.py` is short and intentional. It
is not a morphological analyser. It exists so the ledger can say
“this specific word left” instead of only “token overlap fell”.

## Definite suffixes

`toldkammeret` is the definite form of `toldkammer`. The gazetteer
stores the definite form because that is what the briefs use. A real
system would lemmatise. This workbook does not pretend to.
