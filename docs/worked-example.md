# Worked example: article `dn-001`

This page follows one sample article through every CSV the course scripts
write. The text is the fictional Aalborg harbour piece in
`examples/sample_data/`. It is not from the 2023 news dump.

The same walk can be reproduced without models:

```bash
python3 examples/demo_chunking.py --id dn-001 --text-max-length 180
python3 examples/inspect_dataset.py --path examples/sample_data/03_labeled_sample.csv
```

## Stage 0 — raw Danish

File: `examples/sample_data/00_articles_sample.csv`

| Column | Value |
| --- | --- |
| `id` | `dn-001` |
| `article text` | Danish body (750 characters, six sentences) |

`translate.py` is the only script that reads the spaced column name
`article text`. After this stage the Danish text is always called `body`.

## Chunking before translation

OPUS-MT cannot take the whole article if the encoder budget is tight. With
the example packer and a demo budget of 180 (much smaller than the course
`int(512 * 0.9) = 460`), `dn-001` becomes six windows:

| Window | What it holds |
| --- | --- |
| 1 | Council approval of the three-year promenade plan |
| 2 | Benches, lighting, market / skating surface, start of the mayor quote |
| 3 | Rest of the mayor quote (linger after work, not just cycle through) |
| 4 | Spring construction if permits arrive |
| 5 | Shopkeepers asking for temporary parking |
| 6 | Commuter car park on Vesterbro before the first excavator |

At the real 460-character-budget stand-in the article fits in two windows.
The course scripts measure *tokens* for the “is this sentence too long?”
check and *characters* inside `split_long_sentence`, so a GPU rerun will
not match these counts exactly. The split *shape* is the same: sentence
pack, then a hard cut on long sentences.

## Stage 1 — English article

File: `01_translated_sample.csv`

| Column | Role |
| --- | --- |
| `id` | `dn-001` |
| `body` | Same Danish text as stage 0 |
| `translated` | English article |

The English gold in the sample is a human bilingual pair written for this
archive. `translate.py` would instead run CTranslate2 over the windows and
join them with spaces. `summary.py` later reads `translated` and ignores
`body` except to copy it forward.

## Stage 2 — English summary

File: `02_summarized_sample.csv`

English gold summary:

> Aalborg will extend its harbour promenade over three years, adding
> seating, lighting and a seasonal market space, with construction planned
> for spring if permits arrive.

The course T5 run would summarize each English window (`max_length=80`,
`repetition_penalty=5.0`) and concatenate the pieces. That can grow past
the 128-token label cap used in `finetune.py`. The sample summary is a
single short paragraph on purpose, so it survives that cap.

## Stage 3 — Danish silver label

File: `03_labeled_sample.csv`

| Column | Role |
| --- | --- |
| `id` | `dn-001` |
| `body` | Original Danish article |
| `summary` | Danish summary |

Danish gold summary:

> Aalborg udvider havnepromenaden over tre år med bænke, lys og
> sæsonplads til marked, og anlægget kan starte til foråret, hvis
> tilladelserne kommer.

`translate_back.py` drops the English `translated` column here. This pair
is what mT5 would see as one training example.

## Stage 4 — split membership

With seed `2023` and an 8/2/2 split of the twelve samples, `dn-001` lands
in **train** (`04_train_split_sample.csv`). The validation ids are
`dn-007` and `dn-012`; the test ids are `dn-006` and `dn-008`.

`finetune.py` tokenizes `body` to 1024 tokens and `summary` to 128, then
throws the `id` away. After that point the example is only tensors.

## What a reader should notice

1. The Danish `body` never changes after stage 0. `examples/validate_csvs.py`
   treats a drifted body as an error (`body_drift`).
2. The English columns exist only to manufacture the label. Inference on
   the fine-tuned mT5 is Danish in, Danish out.
3. A silver summary is a compressed *and* twice-translated version of the
   source. Named entities (Limfjordsbroen, Kvægtorvet, Vesterbro) are the
   easy ROUGE hits; the “linger after work” clause is the kind of detail
   that often disappears.
4. The public Nordjylland News evaluation set does **not** use these
   columns. It uses `input_text` / `target_text`. Do not point `eval.py`
   at `03_labeled_sample.csv`.

## Commands that touch this id

```bash
python3 examples/demo_chunking.py --id dn-001 --text-max-length 180
python3 examples/validate_csvs.py \
  --path examples/sample_data/03_labeled_sample.csv \
  --stage labeled
python3 examples/toy_pipeline.py \
  --sample-dir examples/sample_data \
  --output-dir /tmp/dns-gold \
  --replay-gold
```

The replay-gold toy run should write a labeled file whose `dn-001` summary
matches the Danish gold sentence above.
