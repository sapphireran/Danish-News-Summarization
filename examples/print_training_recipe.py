#!/usr/bin/env python3
"""Print the recorded mT5 recipe and the original script notes.

Useful when you want the course hyperparameters without opening
finetune.py and the six other root scripts at once.

Run from the repository root:

    python3 examples/print_training_recipe.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_summarization.pipeline_notes import format_all_stages

RECIPE = {
    "base_model": "google/mt5-large",
    "body_tokens": 1024,
    "summary_tokens": 128,
    "epochs": 20,
    "learning_rate": 3e-4,
    "optimizer": "adafactor",
    "scheduler": "polynomial",
    "warmup_steps": 1000,
    "train_batch_size": 8,
    "fp16": True,
    "num_beams": 4,
    "length_penalty": 0.8,
    "no_repeat_ngram_size": 3,
    "best_model_metric": "rouge_1_mid_fmeasure",
    "checkpoint_dir": "mt5-summarize-large",
    "export_dir": "./large_model",
    "inspection_dir": "./small_model",
}


def main() -> int:
    print("Recorded fine-tune recipe from finetune.py")
    width = max(len(key) for key in RECIPE)
    for key, value in RECIPE.items():
        print(f"  {key:<{width}}  {value}")

    print()
    print("Original root-script notes")
    print()
    print(format_all_stages())
    print()
    print(
        "Inspection and evaluation load ./small_model, not ./large_model. "
        "See docs/training-and-eval.md and docs/limitations.md."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
