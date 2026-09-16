# Design notes

Why this tree grew a package and a `docs/` folder around a handful of
2023 course scripts, and what was *not* changed on purpose.

## What stayed in the repository root

`Ctranslate_converter.py`, `translate.py`, `summary.py`,
`translate_back.py`, `finetune.py`, `use_model.py`, and `eval.py` are
the historical workflow. They still hard-code paths, still call NLTK
and Transformers, and still do the actual GPU work.

They were **not** rewritten in place. A course archive that still runs
the way the report described is more useful than a clever refactor that
silently changes `repetition_penalty` or column names.

## What the package extracted

Three things were duplicated almost line-for-line across the generation
scripts:

1. Long-sentence splitting on `,` / `;` / `:` plus a character budget.
2. Packing sentences into a token budget.
3. The implicit CSV schema (`article text` → `body` → `summary`).

Those now live in:

| module | role |
| --- | --- |
| `danish_news_summarization/text.py` | NLTK-free sentence / word tokens |
| `danish_news_summarization/chunking.py` | the packer the GPU scripts describe |
| `danish_news_summarization/schema.py` | column contracts |
| `danish_news_summarization/config.py` | named stages + original filenames |
| `danish_news_summarization/pipeline.py` | CPU dry-run of the four label stages |
| `danish_news_summarization/sample_data.py` | ten fictional news pairs |
| `danish_news_summarization/cli.py` | `stages`, `schema`, `chunk`, `dry-run`, `export-data` |

The GPU scripts do **not** import this package yet. Wiring them up is
a good follow-up; it is also a behaviour change and should be its own
diff with a before/after translation of the same three articles.

## Chunking: character budget vs. token budget

The original `split_long_sentence` increments `current_length` by
`len(word) + 1` (characters) and compares it to `text_max_length`
(tokens). That is a unit mismatch. It usually *under*-splits relative
to the tokenizer, because a 40-character fragment can still be 20
subword tokens in Danish.

`chunking.split_long_sentence` keeps the original loop (so examples
match the 2023 comments) and then, if you pass `length_fn`, re-splits
any chunk that still exceeds the token budget. The GPU scripts will
keep the old behaviour until they are switched over.

`WhitespaceTokenizer` is a teaching tool. It adds two dummy special
tokens to mimic `add_special_tokens=True`. It will always report fewer
tokens than OPUS-MT or T5 on Danish.

## Sample articles are fictional

The ten stories in `sample_data.py` are original. They are written to
look like regional Danish news so the chunker and the schemas have
something realistic to chew on (decimal commas, `kl. 21`, `t.eks.`,
municipality names, kroner amounts). They are not quotes from a news
dump and should not be used as a benchmark.

Lengths are uneven on purpose. `dn-003` is a short news brief;
`dn-009` is a long feature that overflows a 40-token window.

## Why there is no `requirements-gpu.txt` pin to the 2023 stack

The course environment mixed specific CUDA, `ctranslate2`,
`transformers`, and `datasets` builds. Pinning a modern laptop to those
wheels would fail more often than it would help. `requirements.txt`
lists the GPU extras as comments; `requirements-examples.txt` is the
empty-on-purpose file that means "stdlib is enough".

## Follow-ups that would be real code changes

- Import `split_article` from the package in the three generation
  scripts, and delete the copies.
- Make `Ctranslate_converter.py` convert **both** OPUS directions by
  default, with a CLI flag for NLLB.
- Drop `df[:10]` or gate it behind `--limit`.
- Align `use_model.py` / `eval.py` on one Hub dataset and one
  checkpoint directory.
- Replace `datasets.load_metric` and `use_auth_token`.
- Filter silver labels that invent digits.

None of that is required to read the docs or run the examples.
