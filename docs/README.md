# Personal notes for the 2023 ITU summarisation project

This folder is a reconstruction of decisions that lived only in the
root scripts. Nothing here is company work. The executable companion is
the `fjordpress` package: a closed-world gazette that replays the four
silver-label hops without downloading weights.

| note | question it answers |
| --- | --- |
| [course-context.md](course-context.md) | What the 2023 course project was trying to do |
| [silver-label-hops.md](silver-label-hops.md) | Why DA→EN→summary→DA exists at all |
| [packing-windows.md](packing-windows.md) | How 512 / 0.9 / char+1 / subword interact |
| [closed-world-lexicon.md](closed-world-lexicon.md) | What the study kit uses instead of OPUS-MT |
| [entity-ledger.md](entity-ledger.md) | How to see hop attrition without BERTScore |
| [hyperparameters-as-committed.md](hyperparameters-as-committed.md) | Numbers copied out of `finetune.py` / `eval.py` |
| [script-archaeology.md](script-archaeology.md) | Scars left in the 2023 files |
| [vesterklit-gazette.md](vesterklit-gazette.md) | The invented municipal corpus |
| [evaluation-without-weights.md](evaluation-without-weights.md) | Laptop metrics vs the original stack |
| [rebuilt-checklist.md](rebuilt-checklist.md) | What I would change if the course ran again |

Generated lab notes (text + HTML) live in [generated/](generated/) after
`python -m fjordpress report --snapshot`.
