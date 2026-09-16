# Config mirrors

Each YAML file restates numbers and paths that are **hardcoded** in a root
script. The Python files do not read YAML. Keep the two in sync by hand
when you change a default.

| File | Mirrors |
| --- | --- |
| [`convert_models.yaml`](convert_models.yaml) | `Ctranslate_converter.py` |
| [`translate.yaml`](translate.yaml) | `translate.py` |
| [`summarize.yaml`](summarize.yaml) | `summary.py` |
| [`translate_back.yaml`](translate_back.yaml) | `translate_back.py` |
| [`finetune_mt5_large.yaml`](finetune_mt5_large.yaml) | `finetune.py` as checked in |
| [`finetune_mt5_small.yaml`](finetune_mt5_small.yaml) | suggested `small_model` recipe |
| [`eval.yaml`](eval.yaml) | `use_model.py` + `eval.py` |

See also [../../docs/07-hyperparameters.md](../../docs/07-hyperparameters.md).
