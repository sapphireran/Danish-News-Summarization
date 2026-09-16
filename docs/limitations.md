# Limitations

This project’s labels are **manufactured**. Everything below is a consequence of that choice, plus a few sharp edges in the committed scripts.

## Translationese

Danish → English → T5 → English → Danish does not return the Danish a journalist would have written. Typical artifacts:

- English word order leaking into Danish (`en storm ramte X i går nat` is fine; `det var rapporteret at ...` starts to sound like a calque),
- lost idioms (`gå i fisk`, sports metaphors, local political shorthand),
- proper-noun drift (`Aalborg` surviving while a smaller parish name is Anglicized and then re-Danishized wrong),
- register flattening: T5 news-English likes “authorities said” / “residents were forced to…”, and OPUS-MT copies that register back.

mT5 will imitate whatever it sees. If 80% of silver summaries open the same way, so will the model.

## Error compounding

Each hop can fail independently:

| Hop | Failure mode | Downstream effect |
| --- | --- | --- |
| da→en | dropped negation, wrong tense | English summary of the wrong event polarity |
| chunk pack | sentence split in the wrong place | summary of a fragment, then glued to the next fragment |
| English T5 | hallucination, generic news filler | fluent English that is not in the article |
| chunk-join | N × 80-token notes | a list, not an abstract; later truncated at 128 |
| en→da | gender, definite suffixes (`-en`/`-et`), numerals | ungrammatical targets that mT5 still copies |

There is no filter that drops low-confidence rows. A 10k run will train on its own worst translations.

## Teacher-domain mismatch

`mrm8488/t5-base-finetuned-summarize-news` is English *news*. It is weaker on:

- sports live-blogs,
- municipal budget tables,
- science-desk pieces with dense noun phrases,
- quotes that should stay quoted.

The example corpus includes those genres on purpose so you can see where an extractive Danish baseline (first two sentences) is sometimes more honest than a pivot abstract.

## Evaluation mismatch

Train text: outlet dump → silver abstract.  
Eval text: Nordjylland news → editorial abstract.

Style, length, and entity density will not match. A model can be a faithful student of T5-via-OPUS and still score modestly on Nordjylland. That is not automatically “training failed.”

## Script-level limitations (still in the tree)

These are documented rather than silently “fixed,” because this task is to expand personal docs/examples, not to rewrite the 2023 training code.

1. **`Ctranslate_converter.py` converts only `en-da`.** `translate.py` needs `da-en`.
2. **`summary.py` uses `df[:10]`.** A naive full run labels ten articles.
3. **NLLB `target_prefix` / drop-first-token** remains in both translation scripts after the project settled on OPUS-MT.
4. **`finetune.py` trains `mT5-large`; eval loads `small_model` + `mT5-small` tokenizer.**
5. **`use_model.py` prints `input_text[i]` for batch size 2.**
6. **`eval.py` `dataloader_drop_last=True`** can drop up to 63 test rows.
7. **No seed, no CLI, no config file.**
8. **`test_dataset` in `finetune.py` is never evaluated.**
9. **Tokenizer is not saved** with `./large_model`.
10. **`datasets.load_metric` is deprecated.** It still works on older `datasets` and will warn or fail on newer ones.

## Ethical / legal

- Do not commit scraped news you do not have the right to redistribute. The example CSVs are fictional.
- Silver summaries can invent facts. Do not deploy this as a production news abstractor without a human loop.
- BERTScore and XLM-R are not a substitute for a Danish speaker reading the output.

## What the example tree does *not* claim

`examples/toy_labeling_pipeline.py` builds **extractive** Danish labels (first-N sentences) and optional pivot-shaped rows from the hand-written sample files. That is a teaching tool for schemas and chunking. It is not a replacement for OPUS-MT + T5, and it will not reproduce the 2023 model.
