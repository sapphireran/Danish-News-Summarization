# Metric notes (personal)

I used two automatic metrics in 2023: ROUGE (selection + report) and BERTScore (report). This note is how I think about them for **Danish news summaries**, not a generic IR lecture.

## ROUGE

ROUGE counts n-gram overlap between a prediction and a reference. I logged mid F for 1-grams, 2-grams, and longest common subsequence (L).

### Why I used it

It was the course default and the DanSum tables I had in a tab. Hugging Face `Seq2SeqTrainer` plus `datasets.load_metric("rouge")` is a well-worn path. I wanted comparability with student lore, not a new metric career.

### Why it is a bad fit for this project specifically

1. **Label shift.** Silver references and Nordjylland references are different dialects of “a summary.” ROUGE assumes the reference is the desired text. Here the desired text at *train* time is silver, and at *test* time is gold. One metric, two tasks.
2. **Danish morphology.** `politiet` vs `politi` vs `politiets` is a cheap miss. English ROUGE papers quietly rely on Porter stemming; I did not configure a Danish stemmer.
3. **Compounds.** `nordjyllands` `politi` vs `NordjyllandsPoliti`-style tokenization depends on SentencePiece. ROUGE-2 becomes a tokenization lottery.
4. **Length.** A verbose student that covers the facts can lose to a short student that copies the gold’s first eight words. Nordjylland golds are short. My silver labels are often stitched and long. ROUGE-L will punish that even when a human prefers the long one — or the reverse.

### What the mid F actually is

The old `rouge` metric returns a bootstrap aggregation with `low` / `mid` / `high`. `mid` is the center of that aggregation, not a mystical “median summary.” I threw away `low`/`high`, which is how you hide instability on a 4k test set that is probably stable anyway — and hide instability on a 20-row smoke test that is not.

### ROUGE-L vs Lsum

I joined `sent_tokenize` sentences with newlines. That is the Lsum convention. If a future rerun uses `evaluate.load("rouge")` with `use_stemmer=True` and no newlines, the number is a different statistic. I will name it explicitly.

## BERTScore

BERTScore is cosine similarity of contextual embeddings, matched greedily, then P/R/F1.

### Why I added it

I wanted something that would not zero-out a good paraphrase. The pivot almost *guarantees* paraphrase relative to TV2 Nord editors: different hop, different style. ROUGE-2 would call that failure. BERTScore is closer to “same space of meaning.”

### Why XLM-R large + `lang='da'`

- Multilingual backbone that actually saw Danish.
- `lang` selects baseline stats and, more importantly, stops me from loading `roberta-large` English by accident.

I would not switch to a Danish-only encoder without a side-by-side on a 100-row sample. Changing the encoder changes the number more than changing beam size from 4 to 2.

### What BERTScore will not tell me

- Factual consistency (entity swap)
- Discourse (two events in the wrong order)
- Register (tabloid vs TV2 Nord)
- Whether the output is Danish

A high mean F1 plus a few English predictions can coexist if the English happens to be semantically close in XLM-R space. That is why I want a language-ID count in any new table.

## chrF / chrF++ (not implemented)

Character n-grams. Better behaved on rich morphology. EuroEval’s later summarization write-ups emphasize chrF-style scores (with extra word-order and recall weighting, plus a language penalty).

If I add one metric in a rerun, it is chrF++ on Nordjylland test, SacreBLEU implementation, documented `word_order` and `beta`. I would still keep ROUGE-1 for continuity with `metric_for_best_model`.

I would not replace BERTScore with chrF; they answer different questions (surface form vs embedding overlap).

## Human ranking

DanSum used human ranks and still found factual errors the numbers missed. My §8 rubric in [docs/evaluation-notes.md](../docs/evaluation-notes.md) is a cheaper personal version: language, on-topic, entities, coverage, hallucination.

I did not run it in 2023. I should have run it on 20 rows instead of a 20th epoch.

## Baseline discipline

A metric without a baseline is a mood. Baselines I owe a rerun:

1. **Unfinetuned mT5-large** generate on Nordjylland (likely garbage or English; still a floor).
2. **Lead-N** (first sentence, first 80 tokens) — strong for news.
3. **Silver model as implemented** — the system under test.
4. Optional: **mT5-large trained on Nordjylland train** — the “you could have just used gold” ceiling. This is a different project; I would label it as such.

Lead-N often looks brutally good on ROUGE for news. If I cannot beat first-sentence ROUGE-1, I will write that down in public in this personal repo. That is more useful than a lonely 22.something.

## How I want a row to look

```text
run_id:           2026-xx-xx-a
git:              <sha>
data_rev:         <hf revision>
n_test:           4178
decode:           beams=4 max_len=128 no_rep=3 lp=0.8
rouge1_mid_f:     .
rouge2_mid_f:     .
rougel_mid_f:     .
bertscore_f1:     .
chrfpp:           .
pred_chars_mean:  .
ref_chars_mean:   .
empty_pred:       .
not_danish:       .
lead_rouge1:      .
unft_rouge1:      .
```

Until those dots fill from a script, I will not put a number in the README.
