"""Documented hyperparameters copied from the 2023 root scripts.

These dataclasses do not launch training. They exist so ``docs/`` and
``examples/`` can print the same numbers ``finetune.py`` / ``summary.py`` used,
and so a later personal experiment can load a JSON file instead of editing
scripts in place.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class TranslationConfig:
    source_model: str
    converted_dir: str
    max_length: int = 512
    length_margin: float = 0.9
    src_lang: str = "dan_Latn"
    tgt_lang: str = "eng_Latn"

    @property
    def text_max_length(self) -> int:
        return int(self.max_length * self.length_margin)


@dataclass(frozen=True)
class SummarizationConfig:
    model_name: str = "mrm8488/t5-base-finetuned-summarize-news"
    text_max_length: int = 512
    summary_max_length: int = 80
    num_beams: int = 2
    repetition_penalty: float = 5.0
    length_penalty: float = 1.0
    early_stopping: bool = True


@dataclass(frozen=True)
class FineTuneConfig:
    model_name: str = "google/mt5-large"
    output_dir: str = "mt5-summarize-large"
    save_dir: str = "./large_model"
    input_max_length: int = 1024
    label_max_length: int = 128
    min_length: int = 9
    length_penalty: float = 0.8
    no_repeat_ngram_size: int = 3
    num_beams: int = 4
    dropout_rate: float = 0.1
    num_train_epochs: int = 20
    learning_rate: float = 3e-4
    lr_scheduler_type: str = "polynomial"
    warmup_steps: int = 1000
    optim: str = "adafactor"
    weight_decay: float = 0.01
    per_device_train_batch_size: int = 8
    per_device_eval_batch_size: int = 8
    gradient_accumulation_steps: int = 1
    generation_max_length: int = 128
    logging_steps: int = 250
    fp16: bool = True
    metric_for_best_model: str = "rouge_1_mid_fmeasure"


@dataclass(frozen=True)
class EvalConfig:
    base_tokenizer: str = "google/mt5-small"
    local_model_path: str = "small_model"
    eval_dataset: str = "alexandrainst/nordjylland-news-summarization"
    preview_dataset: str = "ScandEval/nordjylland-news-summarization-mini"
    input_max_length: int = 1024
    label_max_length: int = 128
    eval_batch_size: int = 64
    bertscore_lang: str = "da"
    bertscore_model: str = "xlm-roberta-large"


DA_EN = TranslationConfig(
    source_model="Helsinki-NLP/opus-mt-da-en",
    converted_dir="models/opus-mt-da-en_ct2",
    src_lang="dan_Latn",
    tgt_lang="eng_Latn",
)

EN_DA = TranslationConfig(
    source_model="Helsinki-NLP/opus-mt-en-da",
    converted_dir="models/opus-mt-en-da_ct2",
    src_lang="eng_Latn",
    tgt_lang="dan_Latn",
)

ENGLISH_NEWS_T5 = SummarizationConfig()
MT5_LARGE = FineTuneConfig()
MT5_SMALL = FineTuneConfig(
    model_name="google/mt5-small",
    output_dir="mt5-summarize-small",
    save_dir="./small_model",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=8,
)
DEFAULT_EVAL = EvalConfig()


def dump_json(config: object, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(config), indent=2) + "\n", encoding="utf-8")


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
