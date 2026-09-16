# Documentation

Personal notes for the 2023 ITU course project that lives in this repository.
The code at the repository root is unchanged in behaviour: convert OPUS-MT,
translate Danish news to English, summarise, translate the summaries back, then
fine-tune mT5.

| Page | What it covers |
| --- | --- |
| [overview.md](overview.md) | Why the project exists and how the pieces fit |
| [silver-label-pipeline.md](silver-label-pipeline.md) | DA→EN→summary→DA labelling in detail |
| [models-and-conversion.md](models-and-conversion.md) | OPUS-MT, CTranslate2, English T5, mT5 |
| [data-format.md](data-format.md) | CSV columns at each stage |
| [fine-tuning.md](fine-tuning.md) | `finetune.py` hyperparameters and loss setup |
| [evaluation.md](evaluation.md) | `eval.py`, `use_model.py`, and the offline example metrics |
| [reproduction.md](reproduction.md) | How to replay the original GPU run |
| [limitations.md](limitations.md) | Silver-label caveats and known script quirks |

Runnable fixtures live in [examples/](../examples/README.md).
