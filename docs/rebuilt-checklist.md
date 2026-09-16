# If the course ran again

A personal list, not a rewrite of the 2023 scripts.

1. **One config object.** Paths, 512, 0.9, `ml80`, `rp5.0`, model
   names, and the `[:10]` guard belong in one file. The output
   filename can still encode the generate knobs.
2. **Convert both OPUS directions** or stop mentioning da-en in the
   README.
3. **Do not send NLLB language prefixes to OPUS-MT** unless a note
   says why `hypotheses[0][1:]` is required.
4. **Train and eval the same size**, or write `large_model` and
   `small_model` as two documented experiments.
5. **Eval on the local test split first**, then on Nordjylland as a
   transfer check. Today those are different column schemas.
6. **Log hop attrition.** Keep a 20-article probe with planted names
   and numbers. The Vesterklit ledger is a sketch of that probe.
7. **Drop `datasets.load_metric`.** `evaluate` is already imported.
8. **Do not slice `[:10]` in the file that writes the training CSV**
   unless the slice is named `probe`.
9. **SentencePiece length everywhere**, or character length
   everywhere. Mixing them in one pipeline made the long-sentence
   splitter incommensurable with the packer.
10. **A model-free dry run** in CI so the CSV contracts cannot drift.
    That is what `python -m fjordpress fixtures` is for.

The 2023 scripts stay as they are. The checklist is the thing I
wanted in the lab book and did not write at the time.
