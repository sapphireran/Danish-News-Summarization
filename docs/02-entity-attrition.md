# Entity attrition

Other personal branches already reconstruct CSV contracts and run mock
DA→EN→summary→DA hops. This one asks a narrower question:

> Of the names, places, organisations, numbers, and Danish compounds
> that sit in the source article, how many still occur after each hop?

That is not ROUGE. ROUGE rewards n-gram overlap with a reference
summary. Entity survival asks whether *the facts you would circle with a
pen* are still there. A silver label can be fluent, short, and wrong.

## How the ledger is built

For each Kystlinje brief:

1. Extract entities from the Danish source with a gazetteer of the
   fictional island chain, plus numbers, times, money, and a short
   compound list (`blæretang`, `håndpresse`, `messingorkester`, …).
2. Mark an entity as present in a later hop if any of its aliases fire.
   `Klintø Skakklub` may appear as `Klintø Chess Club`. `Lærke Holm` may
   appear as `Larke Holm` — that alias is listed on purpose, because the
   pivot planted it.
3. Report survival at four hops after the source: English pivot,
   English summary, Danish silver, and a lead-2 extractive control.

The control matters. Lead-2 cannot invent a year, but it also cannot
keep a fact that lived in sentence five. Silver can keep a late fact
and still mutate it (`1904` → `1914`).

## Where the losses live

On this fiction set the English summary hop is the slaughterhouse.
A live run of `python3 -m kystlinje ledger` on the eighteen briefs
gives mean source-entity survival of **0.88** after the pivot, **0.52**
after the English summary, **0.54** after the Danish silver label, and
**0.70** for lead-2. Average entities lost: 0.94 (source→pivot), 2.89
(pivot→summary), 0.22 (summary→silver). Worst end-to-end is `kz-04`
(Otto Kvist / Sandvig window) at 25 percent: the silver label keeps the
glazier and drops the workshop, the magazine name, and the 214 pieces
of glass.

The pivot is a careful translation, so most gazetteer aliases survive
it. The summary is written like a 2023 news T5: two sentences, a
handful of names, almost no secondary numbers. Ticket prices, volunteer
counts, glass-piece counts, and the chair of the chess club die here.

The silver hop is smaller but nastier. It is where *digits flip*:

| brief | source | silver |
| --- | --- | --- |
| `kz-05` | 11 of 14 hives | 12 of 14 |
| `kz-08` | lock built in 1904 | 1914 |
| `kz-13` | 63 weather vanes | 60 |
| `kz-17` | last boat 23:40 | 23:30 |
| `kz-18` | 7 performances | otte |

Those are not hypothetical. They are planted so the ledger has
something to catch, and so a person rereading the project can see the
failure mode without a GPU.

A second silver failure is *term drift*. `håndpresse` comes back as
`trykpresse`. `blæretang` comes back as `tang`. The sentence is still
about printing or seaweed. The specific object is gone. ROUGE-L may
barely notice.

## Reading the telescope

`python3 -m kystlinje ledger` prints the mean survival rates and a
per-entity yes/no table. `python3 -m kystlinje report` draws the same
numbers as a horizontal telescope in
[`examples/report/index.html`](../examples/report/index.html).

Green marks in the HTML are source spans that still occur in the silver
label. Wavy red marks are source spans that do not. Open `kz-07`
(dialect tapes) and `kz-08` (the 1904 lock) first.

## What the numbers are allowed to mean

They describe eighteen fictional magazine briefs with handwritten hops.
They do not describe OPUS-MT, T5, or mT5. They do not replace a 2023
eval run. They are a study tool for the method: if you train on silver
labels, you train on whatever the hops kept.
