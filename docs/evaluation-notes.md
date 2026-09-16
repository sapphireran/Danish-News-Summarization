# Personal evaluation notes

These are evaluator notes for **my** ITU 2023 final project, written in September 2026 while rereading the committed scripts. They are not a published result and they are not a company eval harness.

I still do not have the 2023 metric printout. Anything that looks like a score in this file is a **definition**, a **worked example of how I would compute it**, or a **comparison to other people’s published work**. It is not a number I am claiming for `./large_model`.

## 1. What I was trying to measure

Three different questions got collapsed into two scripts:

| Question | Intended instrument | Script that almost does it |
| --- | --- | --- |
| Did the student learn the silver style? | ROUGE on `datasets/test_dataset.csv` | *Missing.* `finetune.py` never evaluates the silver test split after `train()`. |
| Is the student usable on real Danish news blurbs? | ROUGE + BERTScore on Nordjylland test | `eval.py` |
| Does a generation look like a summary to a human? | Printed triples (article, gold, pred) | `use_model.py` |

A complete personal eval would have reported all three, plus a tiny human rubric (see §8). I only automated the second and third, and I pointed them at **different** Hugging Face datasets, tokenizers, and generate settings.

## 2. Distributions I actually pointed at

### 2.1 Silver splits (training world)

- **Source:** `labeled_dataset_ml80_rp5.0.csv` after my undocumented fold cut.
- **Language:** Danish article, Danish silver summary.
- **Style:** English-news T5, Marian-backtranslated, often multi-span because of map-reduce.
- **Leakage risk vs Nordjylland:** unknown. The 10k CSV is not in git and is not hashed.

`finetune.py` uses this world for train and validation. Validation ROUGE-1 mid F is the **model selection** metric (`metric_for_best_model`). That means the checkpoint I would have kept is the one that best copies silver labels, not the one that best matches TV2 Nord.

### 2.2 Nordjylland full test (`eval.py`)

From the public dataset card (Alexandra Institute, Oliver Kinch, CC0-1.0):

- Train 75,219 / val 4,178 / test 4,178
- Fields on the card: `text`, `summary`, `text_len`, `summary_len`
- Article length 21–35,164 characters; summary length 12–499 characters
- 181 pairs where the summary is longer than the article
- Source: TV2 Nord API

`eval.py` instead tokenizes `input_text` and `target_text` and drops those names. That matches a **ScandEval-shaped** schema, not the card I just quoted. If the Hub dataset still ships `text`/`summary`, `tokenize_data` throws or yields empty features. I cannot tell from git which schema the 2023 `datasets` loader returned; ScandEval wrappers have used `input_text`/`target_text` for other tasks. This is the first thing I would print in a rerun:

```python
print(load_dataset("alexandrainst/nordjylland-news-summarization", split="test").column_names)
print(load_dataset("ScandEval/nordjylland-news-summarization-mini", split="test").column_names)
```

Until that print exists, `eval.py` is a protocol document, not a one-click score.

### 2.3 Nordjylland mini (`use_model.py`)

`ScandEval/nordjylland-news-summarization-mini` is a convenience slice for spotting. It is the right place for qualitative notes and the wrong place to quote a headline number. Mini vs full can differ in length mix and in how “news-like” the leftover rows are.

## 3. Automatic metrics, as implemented

### 3.1 ROUGE (selection + reporting)

Both `finetune.py` and `eval.py` follow the Hugging Face summarization recipe from that year:

1. Decode predictions with `skip_special_tokens=True`.
2. Replace label `-100` with `pad_token_id` before decode.
3. `sent_tokenize` each string and join sentences with `\n`.
4. `datasets.load_metric("rouge").compute(..., use_aggregator=True)`.
5. Read `.mid.fmeasure` for rouge1 / rouge2 / rougeL.

The newline join is important: the default Google ROUGE implementation used by `datasets` treats newlines as sentence boundaries for ROUGE-Lsum. Without it, a multi-sentence summary is one blob and Lsum collapses toward L. I did this on purpose.

What I did **not** log:

- precision and recall (only F)
- `low` / `high` bootstrap intervals (DanSum papers report those)
- ROUGE-Lsum as a separate named key (`eval.py` iterates `rouge.items()`, so whatever the metric object contains becomes `rouge_{key}_mid_fmeasure`)
- stemming / language-specific ROUGE. Danish stemming in the classic `rouge-score` package is not on the same footing as English Porter. Overlap metrics will under-credit morphological variants (`politi` / `politiets`).

mT5 SentencePiece also splits Danish compounds differently than a word tokenizer. ROUGE-2 is therefore an even harsher, noisier number than it is in English news papers.

### 3.2 BERTScore (reporting only)

`eval.py` only:

```python
bert_metric.compute(
    predictions=decoded_preds,
    references=decoded_labels,
    lang='da',
    model_type="xlm-roberta-large",
)
```

Then mean pooling over the test predictions (after `drop_last`). I did not keep per-example BERTScore, so I cannot draw “long articles fail” plots from the 2023 run.

Why this pair:

- `lang='da'` stops an accidental English RoBERTa.
- XLM-R large was the default multilingual BERTScore backbone people used in 2023 for Danish.
- BERTScore is more forgiving of paraphrase than ROUGE-2, which matters when the student was trained on silver style and tested on gold style.

Why I do not treat BERTScore as a factuality metric: it will happily give a high F1 to a fluent summary that swaps two municipalities. DanSum’s own write-up makes the same warning. I agreed with them then and I still do.

### 3.3 Metrics I did not implement and now wish I had

| Metric | Why it would have helped |
| --- | --- |
| chrF / chrF++ | Character n-grams tolerate Danish morphology better than word ROUGE. EuroEval later leaned this way for summarization. |
| Language ID on outputs | Catches “the model is emitting English.” |
| Entity F1 (PER/LOC/ORG) | Would have shown pivot named-entity damage. |
| Compression ratio | `len(pred)/len(src)` vs gold. I suspect the student is too long. |
| Coverage / density (Grusky et al.) | Distinguishes extractive vs abstractive silver labels. |
| Duplicate-n-gram rate | Checks whether `repetition_penalty=5.0` and `no_repeat_ngram_size` actually behaved. |
| Silver-vs-gold ROUGE on overlapping docs | Direct measure of label shift. |

I would **not** add BLEU as a headline number. BLEU is a translation metric; it punishes legitimate summary paraphrase even more than ROUGE-2.

## 4. Decode settings are part of the metric

This is easy to forget and it is wrong in this repo.

| Knob | `finetune.py` config | `eval.py` | `use_model.py` |
| --- | --- | --- | --- |
| Weights dir | saves `large_model` | loads `small_model` | loads `small_model` |
| Tokenizer name | `google/mt5-large` | `google/mt5-small` | `google/mt5-small` |
| Beams | 4 (config) | Trainer default generate | 2 |
| `no_repeat_ngram_size` | 3 | (config on model if loaded) | **1** |
| Max new tokens | 128 | 128 (training_args) | 128 |
| Min length | 9 | depends on loaded config | unset in generate() |
| Length penalty | 0.8 | depends on loaded config | unset |

`Seq2SeqTrainer.evaluate()` with `predict_with_generate=True` uses the model’s generation config plus `generation_max_length`. If I load a checkpoint whose `config.json` still has the `AutoConfig` block from `finetune.py`, eval is closer to training. If I load a stripped `save_pretrained` directory that lost those keys, eval silently uses mT5 defaults.

`use_model.py` is a different decoder. Comparing a printed example from that script to an `eval.py` ROUGE is comparing two systems.

The `small_model` vs `large_model` mismatch is worse than a decode-knob mismatch. Either I locally copied large weights into `small_model/` and never committed the rename, or the eval scripts point at a different experiment (mT5-small fine-tune) that is not in this tree. I do not remember which. A rerun must pick one name and use it everywhere.

## 5. Protocol I would run now (still personal, still offline)

Order matters. I would not quote a number until step G.

**A. Schema probe.** Print column names and two raw rows for both Hub datasets.

**B. Map columns explicitly.**

```text
source = row["text"] or row["input_text"]
reference = row["summary"] or row["target_text"]
```

Never `remove_columns` a guessed list.

**C. Load one checkpoint + its tokenizer.** Prefer `./large_model` plus a tokenizer saved from the same `finetune.py` run. If the tokenizer was not saved, load `google/mt5-large`, not small.

**D. Silver closed test.** `trainer.evaluate(tokenized_dataset["test"])` on the silver test CSV. This is the “did training work” number.

**E. Nordjylland test.** Same generate kwargs as D. Report:

- ROUGE-1/2/L mid F
- BERTScore mean F1 (XLM-R large, `lang=da`)
- mean pred length and mean ref length in characters and in tokens
- count of empty predictions
- count of predictions whose `langid` is not `da`

**F. Unfinetuned baseline.** `google/mt5-large` with a `"summarize: "` prefix (mT5 is not T5; the prefix may do nothing useful) and without. The point is a lower bound, not a fair prompt sweep.

**G. Qualitative sheet.** 20 articles: 10 random from Nordjylland test, 5 longest, 5 shortest. Score with the rubric in §8. Do this *before* looking at the automatic table so I cannot fish.

**H. Optional diagnostic.** If the 10k dump can be recovered, exact-string overlap against Nordjylland test `text`. Any hit is leakage and must be listed.

I am not running A–H in this documentation pass. There are no weights and no 10k CSV in the workspace.

## 6. How I would present a number if I had one

A single line, not a leaderboard cosplay:

```text
model:        mT5-large fine-tuned on DA←EN T5 silver (ml80, rp5.0)
eval set:     alexandrainst/nordjylland-news-summarization test (N=4178, drop_last → 4160)
decode:       beams=4, max_length=128, no_repeat_ngram_size=3, length_penalty=0.8
ROUGE-1 midF: <not recorded>
ROUGE-2 midF: <not recorded>
ROUGE-L midF: <not recorded>
BERTScore F1: <not recorded>
notes:        student never trained on this reference style
```

For comparison *context only*, DanSum-mT5-large on their DaNewsroom slice (not Nordjylland) reported approximately ROUGE-1 23.76, ROUGE-2 7.46, ROUGE-L 18.25, BERTScore 88.97, with bootstrap intervals. Those figures are **not** a target I hit or missed. Different data, different decode, different cleaning.

Nordjylland gold is often closer to a short editorial blurb than DaNewsroom abstractive newsroom summaries. I would expect a silver-pivot model to land in a messy middle: fluent, sometimes extractive on the Danish source (because mT5 can copy), sometimes English-news-shaped.

## 7. Failure modes I would look for in `use_model.py` prints

I remember seeing some of these in the terminal in 2023. That is anecdotal.

1. **English leakage.** A Danish article in, an English noun phrase out. Pivot residue.
2. **Entity drift.** Correct story, wrong town or party. Typical MT hop damage.
3. **Lead bias.** First packed chunk dominates; later chunks’ sub-summaries were truncated at 128 tokens during training so the student learned “summarize the beginning.”
4. **Repetition or synonym soup.** Opposite failure modes from `no_repeat_ngram_size=1` vs an under-penalized T5.
5. **Over-compression to a cliché.** “Der er sket en ulykke.” True of too many articles.
6. **Index mismatch in the printer.** Article `i` shown, generation from batch `i`. After batch 0 the story on screen is the wrong story. Any qualitative memory that used those prints is tainted.

When I rerun qualitative eval I will decode one example at a time and print `input_ids` length next to the text.

## 8. Tiny human rubric (not used in 2023)

Five binary / 1–5 items, written so a classmate who does not know the method can apply them:

| Code | Prompt | Scale |
| --- | --- | --- |
| LANG | Is the output Danish? | Y/N |
| ON | Is it about this article, not a generic news sentence? | Y/N |
| ENT | Are the main people and places the same as in the article? | 1–5 |
| COV | Would a reader get the same takeaway as from the gold blurb? | 1–5 |
| HAL | Any invented fact? | Y/N (Y is bad) |

I would not average these into a fake MOS without more raters. For a course project, a 20-row table plus two paragraphs of commentary is enough honesty.

## 9. Trainer evaluation mechanics that change the number

Details I want future-me to remember because they silently change ROUGE:

- **`dataloader_drop_last=True`** in `eval.py` drops the last incomplete batch of 64. 4,178 → 4,160.
- **`per_device_eval_batch_size=64`** plus generate with beams can OOM on a 12 GB card once sequences are 1024+128. The 2023 box had enough VRAM; a laptop will not.
- **`fp16` is a training flag**, not set on the eval TrainingArguments. Eval is fp32 unless the loaded weights / Trainer defaults say otherwise.
- **`datasets.load_metric("rouge")`** downloads the old metric script from the Hub. Firewalled environments die here. The replacement is `evaluate.load("rouge")`, which is what I had before commit `d216a1a` reverted it.
- **NLTK `punkt`** must be present or `sent_tokenize` crashes inside `compute_metrics` after a long generate pass. That is the most demoralizing failure mode.
- **mT5 extra_id tokens.** If decode does not skip specials correctly, ROUGE eats `<extra_id_0>` and the score tanks. I check one raw `tokenizer.decode(..., skip_special_tokens=False)` sample every time.

## 10. Validity threats (personal audit)

| Threat | Severity | Status |
| --- | --- | --- |
| No committed scores | High | Cannot claim improvement |
| Checkpoint / tokenizer size mismatch | High | Eval scripts may not load the trained model |
| Column-name mismatch on Nordjylland | High | Eval may not run |
| Silver vs gold style shift | High | Expected; not measured |
| Possible document overlap 10k vs test | Medium | Unchecked |
| Mini dataset for eyeballing, full for numbers | Low | Acceptable if disclosed |
| `summary.py` `[:10]` | High for reproduction | Unknown whether the real labels used the slice |
| NLLB prefixes on OPUS-MT | Medium | May have degraded every silver label |
| Display index bug in `use_model.py` | Medium | Qualitative notes unreliable |
| Deprecated metric API | Low | Reproducibility on modern `datasets` |
| No seed recorded for fold split | Medium | Cannot rebuild the same train set |
| `drop_last` | Low | 18 examples ignored |

I would not submit this as an empirical paper in the current state. I would submit it as a systems / method course report: the pipeline is real, the measurement is incomplete.

## 11. Decision I would make with a clean rerun

- If Nordjylland BERTScore F1 is only marginally above unfinetuned mT5 and ENT/HAL look bad: **retire the pivot** and fine-tune on Nordjylland train like a normal person. The course question would then be answered: silver labels were not enough.
- If fluent and on-topic but ROUGE-2 is in the single digits: **keep the method as a data-augmentation story**, not as a replacement for gold. Mix a small gold subset with silver and measure again.
- If silver-test ROUGE is high and Nordjylland is low: **label shift confirmed.** Distill less aggressively (shorter T5, no map-reduce concat) or add a style transfer step.

Those branches are the actual evaluation, more than any one F-measure.

## 12. Changelog of my understanding

- **December 2023:** “Run `eval.py`, print the dict, put it in the report.” I treated Trainer.evaluate as truthy.
- **September 2026 (this note):** The eval entry points disagree with the training entry point and with the public dataset card. The missing score file is less embarrassing than the missing alignment between scripts. The method is still interesting; the measurement is not yet a measurement.

When I have a real score table I will put it in `notes/runs/` with the decode YAML, the git SHA, and the dataset revision hash — not in this file as folklore.
