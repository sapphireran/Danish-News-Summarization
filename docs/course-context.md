# Course context (ITU ANLP / DL, 2023)

The repository is the final project for ITU's *Advanced Natural Language
Processing and Deep Learning* course, autumn 2023. The brief, as
remembered from the committed scripts rather than from a lost report:

Danish abstractive summarisation data was scarce. The public
Nordjylland news set existed, but the project wanted a *larger* training
signal built from raw Danish articles. The chosen workaround was
**silver labels**: translate the article to English, summarise with an
English news T5, translate the summary back to Danish, then fine-tune
mT5 on `(Danish body, Danish silver summary)`.

That is a method, not a product. The root scripts are a lab trail:

* `Ctranslate_converter.py` — export Helsinki-NLP OPUS-MT to CTranslate2
* `translate.py` — Danish article → English article
* `summary.py` — English article → English summary (first ten rows only)
* `translate_back.py` — English summary → Danish summary
* `finetune.py` — mT5-large on local CSVs
* `use_model.py` / `eval.py` — qualitative + ROUGE/BERTScore on a
  *public* test set, not necessarily the local split

The study kit does not claim the 2023 numbers. It claims a readable
reconstruction of the *shape*, plus a gazette you can run on a laptop.
