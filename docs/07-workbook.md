# Workbook

All of these run without weights. From the repository root:

1. **Walk one brief through the hops.**

   ```bash
   PYTHONPATH=. python3 examples/walk_ferry.py
   ```

   Mark, on paper, which 5W1H slots die between `summarized_en` and
   `labeled_da`.

2. **Score the manchet, not the paragraph.**

   ```bash
   PYTHONPATH=. python3 examples/inspect_manchet.py
   ```

   For each id, write down whether the *first sentence* of the silver
   label would pass a news editor.

3. **Compare silver, oracle, and a planted error.**

   ```bash
   PYTHONPATH=. python3 examples/score_slots.py --id SEJ-005
   PYTHONPATH=. python3 examples/score_slots.py --planted
   ```

   `SEJ-005`'s polarity flip turns a winter cut into an expansion.
   Note how ROUGE-1 against the silver label stays friendly.

4. **Pack the ferry brief on a 16-word budget.**

   ```bash
   PYTHONPATH=. python3 examples/pack_lede.py --id SEJ-001 --policy manchet-tight
   ```

   Window 0 should still be a usable manchet. Later windows are colour
   and the quote. That is the inverted pyramid in packing form.

5. **Length inflation.**

   ```bash
   PYTHONPATH=. python3 -m sejeroe length
   ```

   Find a brief where the *word* ratio and the *subword* ratio disagree
   the most. That disagreement is the compound.

6. **Extractive lead vs silver.**

   ```bash
   PYTHONPATH=. python3 examples/compare_baselines.py
   ```

   For how many ids does **lead-2** beat silver on slot recall? Manchet
   coverage of lead-1 and silver is usually tied; the interesting gap is
   quotes, figures, and the second sentence.

7. **Night-editor gates.**

   ```bash
   PYTHONPATH=. python3 examples/inspect_gates.py --role silver_da
   PYTHONPATH=. python3 examples/inspect_gates.py --id SEJ-001 --role lead1_da
   ```

   List the gates silver fails and lead-1 passes.

8. **Align one brief.**

   ```bash
   PYTHONPATH=. python3 examples/align_parallel.py --id SEJ-004
   ```

   Find the quote sentence. Check whether its English gloss is longer in
   *words* than in *subwords* relative to the Danish compound.

9. **Refresh the clipboard and the cards.**

   ```bash
   PYTHONPATH=. python3 examples/run_desk.py
   PYTHONPATH=. python3 examples/write_cards.py
   ```

   Open `examples/report/index.html` and `docs/generated/cards/`.

10. **If you later rerun the 2023 GPU scripts**, do not feed the Sejerø
    CSVs to `finetune.py` and expect a real model. Eight rows are a
    schema check. Use them to verify column names before touching the
    10 000-article dump.
