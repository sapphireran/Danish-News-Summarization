# Datasets

The course project uses three kinds of tables:

1. A private Danish news dump used only to create silver labels.
2. The silver-labeled splits written under `datasets/`.
3. Public Nordjylland news sets used for inspection and scoring.

This page lists the columns the scripts actually read. The same contracts
are encoded in `danish_summarization.schema`.

## Private Danish news dump

`translate.py` reads `10000_articles_without_linebreaks.csv`. The file is
not in git. The name is the whole specification:

- about 10,000 rows
- article bodies already flattened to single lines
- two columns: `id` and `article text`

The space in `article text` is easy to miss. Later stages rename that column
to `body`. If you rebuild the dump, keep the original name or change
`translate.py`.

Suggested checks before a long translation run:

- no empty bodies
- ids are unique
- line breaks inside quotes will not explode `pandas.read_csv`
- a few rows are actually Danish news, not navigation chrome or paywall stubs

The examples ship a six-article stand-in at
`examples/data/sample_articles.csv`. Those rows are original fiction written
for this repository. They are not from the course dump.

## Silver-label tables

### After Danish to English

`translated_articles.csv`

| Column | Source |
| --- | --- |
| `id` | copied from the dump |
| `body` | original Danish `article text` |
| `translated` | English article from OPUS-MT |

### After English summarization

`summarized_file_ml80_rp5.0.csv`

| Column | Source |
| --- | --- |
| `id` | copied |
| `body` | original Danish |
| `translated` | English article |
| `summary` | English T5 summary, possibly concatenated from several windows |

`summary.py` currently slices the frame to `[:10]`. That is a leftover from
debugging. A full run must remove the slice.

### After English to Danish

`labeled_dataset_ml80_rp5.0.csv`

| Column | Source |
| --- | --- |
| `id` | copied |
| `body` | original Danish |
| `summary` | Danish back-translation of the English summary |

The English columns are dropped here on purpose. Fine-tuning should not see
the pivot language.

### Fine-tune splits

`finetune.py` expects three files that already have the labeled schema:

- `datasets/train_dataset.csv`
- `datasets/validation_dataset.csv`
- `datasets/test_dataset.csv`

The original course work split the silver labels by article id. There is no
script in the repo that performs the split. When you recreate it, keep all
rows for one `id` in a single split and avoid leaking near-duplicate wires
across train and validation.

Token limits used in `finetune.py`:

- body: 1024 tokens
- summary: 128 tokens

Those are mT5 tokenizer tokens, not whitespace words. Long Danish features
will be truncated on the right.

## Public evaluation sets

`use_model.py` loads `ScandEval/nordjylland-news-summarization-mini` and
prints a few generations. `eval.py` loads
`alexandrainst/nordjylland-news-summarization` and scores the full test
split.

Both public tables use different column names:

| Course silver labels | Nordjylland |
| --- | --- |
| `body` | `input_text` |
| `summary` | `target_text` |
| _(none)_ | `text_len`, `summary_len` |

The evaluation scripts tokenize `input_text` / `target_text` and then drop
the extra length columns. Do not point `finetune.py` at Nordjylland without
renaming columns first. That would also change the experiment: the silver
labels are machine-written, while Nordjylland summaries are the external
reference.

## Example tables

The `examples/data/` directory mirrors every stage with six fictional
articles:

| File | Stage |
| --- | --- |
| `sample_articles.csv` | raw dump |
| `sample_translated.csv` | after Danish to English |
| `sample_summarized.csv` | after English summarization |
| `sample_labeled.csv` | after back-translation |
| `sample_train.csv` | two-row toy train split |

These files are small enough to read in a pager and stable enough for
schema tests. They are not a substitute for the 10k-article run.

## Quality notes on silver labels

Back-translation creates a specific kind of target:

- Named entities often survive, but titles and agency names can flip.
- English T5 likes lead-style summaries. The Danish targets therefore look
  more like news leads than like multi-sentence abstracts.
- A high repetition penalty on the English side reduces loops, but it can
  also drop a second fact that should have stayed in the lead.
- If the forward translation already drifted, the Danish target will encode
  that drift. Fine-tuning then rewards the drifted phrasing.

When you inspect a bad generation from `use_model.py`, check the silver
label for that domain first. Some errors are inherited from the labeling
pipeline, not from mT5.
