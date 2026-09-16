# Dataset

Two different Danish news resources show up in this repository. They are
easy to mix up because both look like "Danish article → Danish summary".

## 1. Silver labels (what the project *creates*)

The ITU 2023 workflow starts from a dump of Danish news bodies,
historically named:

```
10000_articles_without_linebreaks.csv
```

Required columns (stage `raw_articles`):

| column | meaning |
| --- | --- |
| `id` | Stable identifier, copied through every later file |
| `article text` | Danish body, line-breaks already flattened |

That file is **not** in git — it is large, and the original dump may
still be under a news-licensing terms of use. The examples replace it
with ten original fictional stories in `examples/data/`.

After the three generation scripts you should have:

```
labeled_dataset_ml80_rp5.0.csv
```

with columns `id`, `body`, `summary` (stage `labeled`). Split that by
hand or with your usual sklearn/pandas split into:

```
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

`finetune.py` reads those three paths and nothing else. It tokenizes
`body` to 1024 tokens and `summary` to 128.

### What a silver label is, and is not

A row in `labeled_dataset_*.csv` is:

- **Danish** source text (the original body, not the English translation).
- A **Danish** target that has passed through English T5.

It is **not** a journalist's own dek or a human abstract. Typical failure
modes that survive into training:

- Named entities that OPUS-MT quietly dropped (`Dokk1` → "the library").
- Numbers that T5 rounded or invented (`2,4 millioner` → "three million").
- English syntax calques after the back-translation
  (`Det er et sted, hvor vi kan fejle i mindre skala` is fine;
  `Det er en sted til at fejle på en mindre skala` is a calque).
- Summaries that only cover the first packed window, because later
  windows were concatenated with no reranking.

If you extend this project, a cheap filter is: drop pairs whose
summary/body word ratio is below 0.05 or above 0.50, and drop pairs
where a digit in the summary does not appear in the body.

## 2. Nordjylland news summarization (what the project *evaluates on*)

`eval.py` loads:

```
alexandrainst/nordjylland-news-summarization
```

`use_model.py` loads the smaller sibling:

```
ScandEval/nordjylland-news-summarization-mini
```

Those Hub datasets use **different column names**:

| Hub column | Role | Silver-label equivalent |
| --- | --- | --- |
| `input_text` | Danish article | `body` |
| `target_text` | Danish summary | `summary` |
| `text_len` / `summary_len` | cached lengths | — |

They are human-oriented regional news pairs, not the silver labels.
That is why a model can look strong on its own validation ROUGE and
still look average here — the style and compression differ.

## Sample fixtures in this repo

`danish_news_summarization/sample_data.py` holds ten original stories
(Aarhus libraries, Hirtshals floating wind, Nørrebro cycle street, and
so on). They are teaching fixtures, not scraped journalism.

| file | stage | columns |
| --- | --- | --- |
| `examples/data/sample_danish_articles.csv` | raw_articles | `id`, `article text` |
| `examples/data/sample_translated_articles.csv` | translated | `id`, `body`, `translated` |
| `examples/data/sample_summarized_articles.csv` | summarized | `id`, `body`, `translated`, `summary` |
| `examples/data/sample_labeled_dataset.csv` | labeled | `id`, `body`, `summary` |
| `examples/data/sample_article_index.csv` | (index) | `id`, `title`, `city`, `topic`, word counts |

Regenerate them after editing `sample_data.py`:

```bash
PYTHONPATH=. python -m danish_news_summarization.cli export-data --out examples/data
```

## Suggested split discipline

When you *do* have a real silver-label CSV:

1. Split **by article id**, never by sentence. The chunker already
   fragments long bodies; a sentence-level split leaks.
2. Keep a city / outlet column if you have one, and stratify. Otherwise
   the validation set can become "just the last 500 rows from one paper".
3. Write the split ids to a text file next to the CSVs. Re-running
   `train_test_split` without a seed is how eval numbers become folklore.
4. Do not evaluate `finetune.py`'s `test_dataset.csv` and the Nordjylland
   Hub set in the same table without labelling which is which.

## Encoding

All example writers use UTF-8 without a BOM. Danish æ/ø/å will corrupt
silently if Excel re-saves the CSV as `windows-1252`. If a later script
prints `Ã¥` instead of `å`, re-export; do not "fix" it in the model.
