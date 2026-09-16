"""Pretty-print the structured copy of finetune.py / summary.py settings.

    python examples/report_hyperparameters.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONFIG_PATH = ROOT / "examples" / "data" / "hyperparameters.json"


def _section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    print(f"Source: {CONFIG_PATH.relative_to(ROOT)}")
    print(f"Copied from: {config['source_script']}")
    print(f"Base model:  {config['base_model']}")
    print(f"Export dir:  {config['final_export']}")

    _section("Data map")
    data = config["data"]
    for key in ("train", "validation", "test"):
        print(f"  {key:12s} {data[key]}")
    print(f"  text         {data['text_column']}  (max {data['encoder_max_length']})")
    print(f"  summary      {data['summary_column']}  (max {data['decoder_max_length']})")

    _section("Trainer")
    args = config["training_arguments"]
    interesting = [
        "num_train_epochs",
        "learning_rate",
        "lr_scheduler_type",
        "warmup_steps",
        "optim",
        "per_device_train_batch_size",
        "gradient_accumulation_steps",
        "fp16",
        "metric_for_best_model",
        "save_total_limit",
    ]
    for key in interesting:
        print(f"  {key:28s} {args[key]}")

    _section("mT5 generation config")
    for key, value in config["generation_config"].items():
        print(f"  {key:28s} {value}")

    _section("English labeler (summary.py)")
    labeler = config["english_labeler"]
    for key in ("model", "text_max_length", "max_length", "repetition_penalty", "num_beams"):
        print(f"  {key:28s} {labeler[key]}")

    _section("Notes")
    for note in config["notes"]:
        print(f"  - {note}")


if __name__ == "__main__":
    main()
