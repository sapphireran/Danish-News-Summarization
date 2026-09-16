# Examples

These examples belong to the personal ITU course project. They use
fictional Danish news written for this repository. They do not include
company data, the private 10k-article dump, or trained weights.

Run every command from the repository root so the `danish_summarization`
package imports cleanly.

## What is here

| Path | Role |
| --- | --- |
| `data/sample_articles.csv` | six-row stand-in for the private dump |
| `data/sample_translated.csv` | Danish body plus English pivot |
| `data/sample_summarized.csv` | English T5-style summaries |
| `data/sample_labeled.csv` | Danish silver labels |
| `data/sample_train.csv` | two-row toy fine-tune split |
| `inspect_csv_schema.py` | column-contract check |
| `chunk_sample_articles.py` | sentence packing demo |
| `simulate_labeling_pipeline.py` | stage-by-stage walkthrough |
| `print_training_recipe.py` | recorded mT5 hyperparameters |

The English and Danish summaries in the sample files are hand-written so
the walkthrough stays readable. They imitate the lead style of the course
pipeline; they are not model output.

## Commands

```
python3 examples/inspect_csv_schema.py
python3 examples/chunk_sample_articles.py
python3 examples/chunk_sample_articles.py --max-length 40
python3 examples/simulate_labeling_pipeline.py
python3 examples/print_training_recipe.py
```

`chunk_sample_articles.py` uses a small whitespace-token budget on purpose.
With the default `--max-length 80` several sample articles spill into a
second window, which is the behaviour `summary.py` has to handle on real
news features.

## How this maps to the root scripts

```
sample_articles.csv      ->  translate.py
sample_translated.csv    ->  summary.py
sample_summarized.csv    ->  translate_back.py
sample_labeled.csv       ->  hand split, then finetune.py
sample_train.csv         ->  one split only, for schema checks
```

The sample English columns are already filled in. You do not need
CTranslate2 or T5 to see the join. If you later point the root scripts at
these files, rename them to the constants those scripts hard-code, or edit
the constants.

## Adding another sample row

1. Write an original Danish article. Do not paste copyrighted news.
2. Keep the body as one CSV field. Quote it if it contains commas.
3. Add the same `id` to every stage file.
4. Write a short English pivot, an English lead, and a Danish lead.
5. Run `inspect_csv_schema.py` and `simulate_labeling_pipeline.py`.

Ids in this folder use the `sample-00N` prefix so they cannot collide with
a numeric dump from the course data.

## Tests

`tests/test_examples.py` re-reads the sample CSVs and runs the same schema
checks as the inspect script. It also requires every raw id to appear in
the labeled file.
