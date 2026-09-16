# Examples

GPU-free companions to the 2023 pipeline. Nothing in this folder downloads OPUS-MT, T5, or mT5. The articles are original fiction set in made-up towns (Havneby, Klitsogn, Øholm, Skovby). They are not news, and they are not from the course corpus.

## What to run first

From the repository root:

```bash
python -m pip install -r requirements-examples.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

python examples/run_chunking_demo.py
python examples/inspect_sample_dataset.py
python examples/metrics_toy_eval.py
python -m pytest tests/
```

`inspect_sample_dataset.py` is the schema linter for the CSV hop. If you edit a sample file and break a column name or reuse an id, it should exit non-zero.

## Files

| Path | Purpose |
| --- | --- |
| `text_chunking.py` | Packing algorithm from `translate.py` / `summary.py` |
| `run_chunking_demo.py` | Prints pack traces for the sample articles |
| `inspect_sample_dataset.py` | Checks columns, `SYN-*` ids, split partition |
| `metrics_toy_eval.py` | Unigram F1 + LCS on hand-written pairs |
| `silver_label_walkthrough.md` | One article followed through every hop |
| `data/sample_articles.csv` | Raw Danish bodies (`id`, `article text`) |
| `data/sample_translated.csv` | After a *hand-simulated* da→en hop |
| `data/sample_summaries_en.csv` | After a *hand-simulated* English summary hop |
| `data/sample_labeled_da.csv` | After a *hand-simulated* en→da hop |
| `data/sample_finetune_split/` | 5 / 2 / 1 partition of the labeled set |
| `expected_outputs/` | Frozen stdout snippets for the demos |

"Hand-simulated" means a person wrote the English and the back-translation to show the intended *shape* of factory output. They are not CTranslate2 hypotheses. That keeps the repo small and copyright-clean.

## Sample world

All eight articles share a fictional coastal municipality so entity checks are easy:

- **Havneby** — larger town, station, library, football club
- **Klitsogn** — municipality name, council, school, emergency services
- **Øholm** — island served by a ferry
- **Skovby** — neighbouring club / bypass village (**Sønderby** is the bypass site)

If a silver summary turns Klitsogn into Copenhagen, the factory failed in a way you can see without ROUGE.

## Tiny token budget

`run_chunking_demo.py` defaults to `--budget 16` (whitespace words + 1 special token). Production packing uses 460–512 real SentencePiece tokens, which would leave every sample article in a single pack. The tiny budget is a microscope.

```bash
python examples/run_chunking_demo.py --id SYN-004 --budget 20
```

## Adding a ninth article

1. Invent a new `SYN-009` story in the same towns. Do not paste a real outlet.
2. Add the row to all four factory CSVs and to exactly one split file.
3. Run `python examples/inspect_sample_dataset.py` and `pytest`.
4. Mention the new id in `silver_label_walkthrough.md` only if you fully write the hop-by-hop notes.

## What these examples deliberately omit

- Beam search, repetition penalty, fp16
- Hub dataset cards
- Any claim that the hand-written summaries are model output

For those, read `docs/` and the root scripts.
