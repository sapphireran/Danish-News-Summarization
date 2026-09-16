# Stylebook gates

ROUGE asks "how many n-grams survived?". A night editor asks something
else. The Sejerø stylebook is seven gates run on a candidate text:

| Gate | Passes when |
| --- | --- |
| `who_in_lede` | WHO surface form in the **first sentence** |
| `what_in_lede` | WHAT surface form in the first sentence |
| `when_in_opening` | WHEN in the first **two** sentences |
| `where_in_opening` | WHERE in the first two sentences |
| `quote_or_speaker` | Quote span kept, or the speaker still named |
| `figures_majority` | At least half of the gold clocks/counts/kroner |
| `contrast_men` | If the brief used *men*, the text still has *men* |

Silver labels in this workbook usually fail `quote_or_speaker` and
`figures_majority`. That is the T5 hop: keep the event, drop the spoken
sentence and the awkward number. Lead-1 often passes the manchet gates
because the journalist already wrote them.

Planted errors are the adversarial case:

- `SEJ-005` polarity-flip fails WHAT/WHY on purpose and still looks
  fluent.
- `SEJ-008` why-flip keeps "100 meters" and "14" so figure recall stays
  high while the quote's negation dies.

```bash
PYTHONPATH=. python3 examples/inspect_gates.py
PYTHONPATH=. python3 examples/inspect_gates.py --id SEJ-001 --role silver_da
PYTHONPATH=. python3 -m sejeroe gates --role lead1_da
```

Gold figures live in `examples/data/08_figures.csv`. They are written on
the fixture, not regex-guessed, so "22 procent" does not match a planted
"steg 22 procent" as a *why* slot — the why aliases require *faldt*.
The figure gate is looser on purpose: it asks whether the *number*
survived, not whether the verb did.
