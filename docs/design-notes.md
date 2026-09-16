# Design notes

This page records why the 2023 project is shaped the way it is. It is personal commentary on the submitted scripts, not a paper.

## The data problem

Abstractive summarization wants `(document, summary)` pairs. English had CNN/DailyMail, XSum, and newsroom-scale dumps. Danish did not have a comparably large public news pair set in the course window. Nordjylland News summarization existed as an evaluation-sized Danish set, which is exactly why this repo treats it as a **test** resource rather than a train set.

The course project therefore manufactures labels.

## Why pivot through English

The pivot is a bet on English tooling:

- OPUS-MT `da-en` / `en-da` were strong, small, and well worn-in.
- A T5 checkpoint already fine-tuned on English news was one `from_pretrained` away.
- mT5 could read Danish at fine-tune time without a Danish-only pretrained decoder.

The alternative — train a Danish summarizer from unsupervised objectives or from a tiny gold set — was heavier than a final-project calendar.

Cost of the bet: every training target is translationese of an English-centric news style. T5-base news models like CNN/DailyMail ledes (who-what-where in one or two sentences). Danish local news (municipal notices, regional politics, weather, sport) does not always want that shape. The silver summary can sound like a wire rewrite of a village meeting.

## Where error accumulates

```text
Danish fact  --da→en-->  English wording  --T5-->  English compression  --en→da-->  Danish target
```

Four places the target can drift from the article:

1. **da→en** drops or mistranslates a Danish-specific term (party nickname, place, compound noun).
2. **Chunking** splits a sentence so T5 never sees a negation and its clause together.
3. **T5** hallucinates a standard news frame ("officials said") that was not in the source.
4. **en→da** picks a grammatical Danish sentence that is not the wording a Danish editor would use, or flips a function word.

mT5 is then asked to map a clean Danish `body` onto that noisy `summary`. If the model is strong, it may learn to ignore the worst noise and extract from `body`. If it is weak, it may imitate translationese.

This is why qualitative prints on a **gold** Danish set matter more than silver-label ROUGE. Silver ROUGE can rise while the model learns to copy T5's English habits in Danish clothing.

## Why chunk instead of truncate

OPUS-MT and T5-base are 512-token models. Danish regional articles often run longer once tokenized, especially after SentencePiece-style subwords.

Truncating to 512 tokens would systematically drop the tail. Local news sometimes buries the decision (the actual summary-worthy event) after quotes and background.

The scripts instead:

1. Sentence-split.
2. Split over-long sentences on commas if needed.
3. Pack greedy chunks up to the token budget.
4. Translate or summarize each chunk.
5. Concatenate.

Coverage goes up. Coherence goes down. A silver summary of a long piece can list several local facts in source order, which is closer to extractive highlight concatenation than to a single edited abstract.

`examples/text_chunking.py` isolates that packing so you can feed it a long string and see the chunks.

## Why CTranslate2 instead of `model.generate`

Label generation is a one-time pass over thousands of articles, two translation directions plus T5. CTranslate2's translator is built for that batch shape. The fine-tune stays on Transformers because `Seq2SeqTrainer` already implements generate-during-eval, Adafactor, and checkpointing.

Keeping two runtimes is awkward (and the converter/script mismatch on `da-en` shows it) but it matches the 2023 split of labor: fast labeling, familiar training.

## Why mT5, and why large for train / small for eval

mT5 is the straightforward multilingual seq2seq in the Transformers examples from that year. `mt5-large` has enough capacity to memorize silver patterns and still generate fluent Danish. `mt5-small` is what you keep around to poke at outputs without filling the GPU.

The repo never documents a distillation step from large to small. The two folders are best read as two experiment tracks that shared script names.

## Metric choice

ROUGE was the course-default summarization metric. BERTScore with XLM-R large was the "but ROUGE is lexical" complement, and `lang='da'` made the intent explicit.

What the project did **not** optimize:

- Human pairwise preference
- Factual consistency models
- Danish-specific tokenizers for ROUGE (ROUGE is run on whatever `sent_tokenize` + the rouge library tokenize)

Danish compounds make ROUGE-2 brittle. BERTScore is the more forgiving number; it is also slower and harder to explain in a short report.

## Debug leftovers that changed the science

Two lines quietly shrink the experiment:

- `summary.py` keeps `[:10]` rows.
- `Ctranslate_converter.py` does not export the model `translate.py` needs.

If those were active during the original run, the author almost certainly had local edits that never landed in git. Treat the GitHub tree as the submitted snapshot, not necessarily the exact command history that produced a private checkpoint.

## What I would change in a personal rerun

These are notes, not patches to the root scripts:

1. Convert **both** OPUS-MT models in the converter.
2. Remove the `[:10]` cap or make it `--limit`.
3. Checkpoint translation every N rows.
4. Drop NLLB prefixes on bilingual OPUS-MT, or switch fully to NLLB.
5. Align `small_model` / `large_model` via one `--model-path`.
6. Evaluate the silver test split **and** Nordjylland, and say which is which.
7. Lower `repetition_penalty` from 5.0 unless a sweep says otherwise.
8. Seed the trainer.

The `examples/` tree implements the non-GPU parts of (3)-style schema checks and (1)-style documentation. It does not replace the training scripts.
