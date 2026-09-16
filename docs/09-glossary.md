# Glossary

Short definitions as used in this repository. Words in _italics_ have their own entry.

**Adafactor** — Memory-efficient optimizer used in `finetune.py`. Standard for T5-family fine-tunes.

**Abstractive summary** — A summary that may use words not present in the article. Opposite of _extractive_. mT5 and the English T5 are abstractive.

**BERTScore** — Metric that compares embeddings of prediction and reference tokens. Here: XLM-R large, `lang='da'`.

**CTranslate2** — Fast inference runtime. OPUS-MT is converted into this format for the label factory.

**Chunk / pack** — A list of sentences whose token count fits a model window. See [02-chunking-and-length.md](02-chunking-and-length.md).

**Extractive summary** — Sentences copied from the article. Not what this project trains, though high ROUGE-1 can look extractive.

**Factory** — Informal name for Stages 1–4: translate, summarize, translate back.

**Lead** — The opening summary sentence(s) of a news story. The English T5 is biased toward this shape.

**mT5** — Multilingual T5 (`google/mt5-*`). The model being fine-tuned for Danish→Danish summarization.

**Nordjylland News summarization** — External Danish eval set used by `eval.py` / `use_model.py`. Not part of the silver-label dump.

**OPUS-MT** — Helsinki-NLP Marian models trained on OPUS bitext. Used for da↔en.

**Pack-wise summarization** — Summarizing each _chunk_ independently and concatenating. Causes collage-shaped silver labels.

**punkt** — NLTK sentence tokenizer models.

**ROUGE** — Overlap metrics (unigram, bigram, LCS). Mid-F is what the scripts log.

**Silver label** — A training target produced automatically (here: translated English summaries), not written by a journalist.

**SYN- id** — Prefix for synthetic example articles in `examples/data/`. Never a real CMS id.

**Translationese** — Fluent but unidiomatic text that has passed through machine translation.

**Truncation vs. packing** — Fine-tuning truncates to 1024 tokens. The factory packs and stitches instead.

**Window** — The model's maximum input length (512 for OPUS-MT/T5, 1024 for mT5 bodies).
