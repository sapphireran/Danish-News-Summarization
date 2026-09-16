# Entity ledger

`eval.py` reported ROUGE mid-F and BERTScore F1 against a public
Danish test set. Those numbers do not say *which fact died on which
hop*.

The ledger does. Each gazette article ships a gold mention list
(people, places, numbers). For every hop the kit records:

* kept / lost mentions (case- and hyphen-folded)
* retention ratio
* compression vs the Danish source
* ROUGE-1 / ROUGE-L vs the gold Danish summary (on Danish hops)

```bash
python -m fjordpress ledger --article vk-001
python examples/score_ledger.py vk-004
```

How to read a row:

* `da_source` should be near 1.0 retention. If it is not, the gold
  entity list is wrong — fix the list, not the hop.
* `en_oracle` can drop Danish-only morphology but should keep names
  and numbers.
* `en_summary_*` is where most attrition *should* happen: the
  extractive hop is allowed to drop sentences.
* `da_back_oracle` should restore any gold sentence the extractive hop
  kept. Lost entities here are extractive, not translational.
* `da_back_gloss` also pays the word-list tax. Compare it to oracle
  to see translation damage.

The HTML report in `docs/generated/vesterklit-lab-notes.html` is the
same ledger in a form you can scroll.
