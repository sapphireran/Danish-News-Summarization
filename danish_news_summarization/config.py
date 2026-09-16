"""Named stage configs that mirror the hardcoded paths in the root scripts.

Keeping the original filenames here (``summarized_file_ml80_rp5.0.csv`` and
friends) makes the documentation and the GPU scripts point at the same
artifacts. Examples write into ``examples/output/`` instead, so a dry run
never overwrites a real experiment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class StageConfig:
    """One step of the translate → summarize → translate-back → train loop."""

    name: str
    script: str
    description: str
    input_path: str
    output_path: str
    input_stage: str | None
    output_stage: str
    model: str
    notes: Tuple[str, ...] = field(default_factory=tuple)

    @property
    def input_columns(self) -> List[str]:
        from .schema import STAGE_COLUMNS

        if self.input_stage is None:
            return []
        return list(STAGE_COLUMNS[self.input_stage])

    @property
    def output_columns(self) -> List[str]:
        from .schema import STAGE_COLUMNS

        return list(STAGE_COLUMNS[self.output_stage])


PIPELINE_STAGES: Tuple[StageConfig, ...] = (
    StageConfig(
        name="convert_models",
        script="Ctranslate_converter.py",
        description="Convert Helsinki-NLP OPUS-MT checkpoints to CTranslate2.",
        input_path="Helsinki-NLP/opus-mt-en-da (and opus-mt-da-en)",
        output_path="models/opus-mt-en-da_ct2",
        input_stage=None,
        output_stage="raw_articles",
        model="Helsinki-NLP/opus-mt-en-da",
        notes=(
            "The checked-in converter currently enables only the en→da model.",
            "Uncomment the da→en block before running translate.py.",
        ),
    ),
    StageConfig(
        name="translate_da_en",
        script="translate.py",
        description="Translate Danish article bodies to English with OPUS-MT da→en.",
        input_path="10000_articles_without_linebreaks.csv",
        output_path="translated_articles.csv",
        input_stage="raw_articles",
        output_stage="translated",
        model="models/opus-mt-da-en_ct2",
        notes=(
            "Input column is 'article text'; output renames it to 'body'.",
            "Articles are sentence-packed to ~90% of the 512-token window.",
        ),
    ),
    StageConfig(
        name="summarize_en",
        script="summary.py",
        description="Summarize the English translations with a news-tuned T5.",
        input_path="translated_articles.csv",
        output_path="summarized_file_ml80_rp5.0.csv",
        input_stage="translated",
        output_stage="summarized",
        model="mrm8488/t5-base-finetuned-summarize-news",
        notes=(
            "Default generate() settings: max_length=80, repetition_penalty=5.0, num_beams=2.",
            "The checked-in script slices to the first 10 rows ([:10]) — remove that for a full run.",
        ),
    ),
    StageConfig(
        name="translate_en_da",
        script="translate_back.py",
        description="Translate English summaries back to Danish to form silver labels.",
        input_path="summarized_file_ml80_rp5.0.csv",
        output_path="labeled_dataset_ml80_rp5.0.csv",
        input_stage="summarized",
        output_stage="labeled",
        model="models/opus-mt-en-da_ct2",
        notes=(
            "Output drops the English translation and keeps Danish body + Danish summary.",
            "These pairs are later split into datasets/train|validation|test_dataset.csv.",
        ),
    ),
    StageConfig(
        name="finetune_mt5",
        script="finetune.py",
        description="Fine-tune google/mt5-large on the silver Danish pairs.",
        input_path="datasets/train_dataset.csv",
        output_path="./large_model",
        input_stage="finetune",
        output_stage="finetune",
        model="google/mt5-large",
        notes=(
            "20 epochs, Adafactor, lr=3e-4, polynomial decay, warmup 1000, fp16.",
            "Best checkpoint selected by rouge_1_mid_fmeasure on the validation split.",
        ),
    ),
    StageConfig(
        name="inspect_predictions",
        script="use_model.py",
        description="Print a handful of generated vs. reference summaries.",
        input_path="ScandEval/nordjylland-news-summarization-mini",
        output_path="(stdout)",
        input_stage=None,
        output_stage="labeled",
        model="small_model",
        notes=(
            "Qualitative check. Uses a different public dataset than the silver labels.",
            "Column names on that dataset are input_text / target_text, not body / summary.",
        ),
    ),
    StageConfig(
        name="evaluate",
        script="eval.py",
        description="ROUGE + BERTScore on alexandrainst/nordjylland-news-summarization.",
        input_path="alexandrainst/nordjylland-news-summarization",
        output_path="(stdout metrics dict)",
        input_stage=None,
        output_stage="labeled",
        model="small_model",
        notes=(
            "BERTScore is computed with xlm-roberta-large and lang='da'.",
            "eval.py currently loads google/mt5-small's tokenizer with weights from small_model/.",
        ),
    ),
)

STAGE_BY_NAME: Dict[str, StageConfig] = {stage.name: stage for stage in PIPELINE_STAGES}


def gpu_output_dir() -> str:
    """Directory used by the original scripts (repository root)."""
    return "."


def example_output_dir() -> str:
    """Directory used by the dry-run examples."""
    return "examples/output"
