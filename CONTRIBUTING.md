# Contributing (personal project)

This is a personal academic repository, not a company codebase. The notes below are for future-me and for anyone who wants to keep the documentation honest.

## Ground rules

1. **Do not add employer or client code.** If a change only makes sense inside a workplace repo, it does not belong here.
2. **Do not commit scraped Danish news.** Example articles stay fictional (`SYN-*` ids). Real corpora stay on the machine that is allowed to hold them.
3. **Do not rewrite the 2023 root scripts "for cleanliness"** unless you are deliberately starting a dated fork. Historical quirks are documented in `docs/` on purpose.
4. **Do not add social-media integrations** or publish generations as news.

## Where to change things

| Kind of change | Put it here |
| --- | --- |
| Explain the 2023 method | `docs/*.md` |
| GPU-free demo / sample CSV | `examples/` + `tests/` |
| Dependency for demos | `requirements-examples.txt` |
| Dependency for the old GPU pipeline | `requirements.txt` |
| Behaviour of the course scripts | root `*.py` (call it out in the PR) |

## Checks before you push documentation work

```bash
python -m pip install -r requirements-examples.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
python examples/inspect_sample_dataset.py
python examples/run_chunking_demo.py --id SYN-001
python examples/compare_budgets.py --id SYN-004
python examples/metrics_toy_eval.py
python -m pytest tests/
```

If you edit a sample CSV, the inspector and `tests/test_sample_data.py` must stay green. If you change toy metric examples, update `tests/test_metrics_toy_eval.py` and the prose in `docs/05-evaluation.md` together.

## Commit style

Prefer a few substantial commits over "fix typo" noise:

- scaffolding / README
- docs by theme (pipeline vs eval vs ethics)
- examples + tests

Each commit should leave the example suite importable.

## Language

Prose in `docs/` and `examples/*.md` is English so the course write-up stays accessible. Sample *data* is Danish. Do not translate the sample bodies into English in place; the whole point is a Danish `body` column.
