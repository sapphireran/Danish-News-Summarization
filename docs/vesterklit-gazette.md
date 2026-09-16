# Vesterklit Gazette

Ten invented municipal stories, six aligned sentences each. The town,
the ferry, the museum, and the people are fiction. The point of a
closed world is that every name is known and every number is planted.

## Cast

| name | role |
| --- | --- |
| Lisbeth Holm | ferry director |
| Karsten Vang | engineer on the Klitsand mast |
| Amina Sørensen | teacher at Nordmark School |
| Ellen Buhl | mayor |
| Poul Nissen | Amberhus chair |
| Yasmin El-Khatib | bilingual exhibition texts |
| Henrik Straarup | technical lead, night bus |
| Sofie Tranberg | heat-pump subsidy desk |
| Mikkel Ravn | technical department / fishery chair (two stories) |
| Troels Kjær | volunteer lead on the parish scans |

Places: Havnepladsen, Mågeø, Sølvdyp, Nordmark, Klitsand, Rylevej,
Stenmole, Amberhus, Tangløb, Brohuset.

## Split

| split | ids | stories |
| --- | --- | --- |
| train | vk-001 … vk-006 | storm ferry, mast, school roof, Stenmole vote, Amberhus, night bus |
| validation | vk-007, vk-008 | heat pumps, bike path |
| test | vk-009, vk-010 | parish archive, cod quota |

The split is for the *shape* of `datasets/train_dataset.csv` etc.
It is not large enough to train mT5.

## House rules

* Six sentences, not five or seven, so packing demos stay comparable.
* Each story plants at least one number and two proper names.
* Gold summaries are written by hand, not extracted, so ROUGE against
  the oracle back-translation stays honest (extractive ≠ abstractive).
* No living real journalist, outlet, or council is named.

If you add a story: keep the 1:1 alignment, add it to exactly one
split, extend the lexicon until `python -m fjordpress lexicon` is
clean, and mention every gold entity in the Danish source.
