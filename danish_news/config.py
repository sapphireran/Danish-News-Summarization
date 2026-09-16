"""JSON configuration for the example scripts.

The course scripts bake paths and hyperparameters into module-level
constants. The example CLIs instead read a small JSON file so a reader can
change the window budget or fixture paths without editing Python.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from danish_news.chunking import Unit
from danish_news.pipeline import PipelineConfig

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
DATA_DIR = EXAMPLES_DIR / "data"


@dataclass(frozen=True)
class ExampleConfig:
    raw_csv: str = "sample_articles.csv"
    translated_csv: str = "sample_translated.csv"
    summarized_csv: str = "sample_summaries_en.csv"
    labeled_csv: str = "sample_labeled.csv"
    references_csv: str = "sample_references.csv"
    max_units: int = 80
    unit: Unit = "words"
    summary_max_sentences: int = 2
    data_dir: str = str(DATA_DIR)

    @property
    def data_path(self) -> Path:
        return Path(self.data_dir)

    def resolve(self, name: str) -> Path:
        path = Path(getattr(self, name) if hasattr(self, name) else name)
        if path.is_absolute():
            return path
        return self.data_path / path

    def pipeline(self) -> PipelineConfig:
        return PipelineConfig(
            max_units=self.max_units,
            unit=self.unit,
            summary_max_sentences=self.summary_max_sentences,
        )

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


def load_config(path: str | Path | None = None) -> ExampleConfig:
    """Load `examples/example_config.json` unless a path is supplied."""
    config_path = Path(path) if path else EXAMPLES_DIR / "example_config.json"
    if not config_path.is_file():
        return ExampleConfig()
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    known = {key: value for key, value in payload.items() if key in ExampleConfig.__dataclass_fields__}
    if "data_dir" not in known:
        known["data_dir"] = str(config_path.parent / "data")
    return ExampleConfig(**known)


def dump_default_config(path: str | Path) -> Path:
    target = Path(path)
    target.write_text(
        json.dumps(ExampleConfig().to_json(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return target
