# If I redid this

A 2026 note. Not a rewrite of the course scripts.

## Keep the question, drop the silent hops

The course question is still good: can you build a Danish summarizer
when you do not have a large Danish supervision set? Pivot silver
labels are one answer. They are a better answer if every hop is logged.

If I rebuilt the pipeline I would write three extra columns on every
row, not just `body` and `summary`:

- `pivot_en` — the English article, kept
- `summary_en` — the English teacher output, kept
- `entity_delta` — source entities missing from the silver label

The 2023 labeled CSV throws the English hops away. That makes the
compounded error invisible at train time.

## Do not evaluate only with ROUGE

ROUGE on Nordjylland-News is a start. It will not see `1904` become
`1914`. I would add:

- entity / number / time F1 against the Danish source (not against the
  silver label — that would reward the teacher’s mistakes)
- a short human rubric: faithfulness, quantity, Danish naturalness
- an extractive lead-2 / lead-3 baseline on the same test set, so the
  neural model has to beat “first two sentences”

The Kystlinje ledger is a toy version of the first bullet.

## Fix the script scars before spending GPU hours

Uncomment da→en conversion. Remove NLLB prefixes unless the model is
actually NLLB. Delete `[:10]`. Save and load the same directory. Pin
`evaluate` instead of `datasets.load_metric`. None of those changes are
on this branch, because the point of the archive is to remember what
was actually committed in December 2023.

## Do not republish the news dump

The 10k file stays off git. Fiction is enough to document the method.
If a future rerun needs real articles, they should be pulled under
whatever licence the source newsroom offers, not copied from a course
USB stick into a public repository.
