"""CSV column contracts copied from the 2023 root scripts.

The course pipeline never wrote a schema file. These tuples are read off
the ``DataFrame(...)`` constructors and the ``load_dataset`` column drops.
"""

from __future__ import annotations

from dataclasses import dataclass

# translate.py reads this name from the raw dump.
RAW_SOURCE_COLUMN = "article text"

RAW_COLUMNS = ("id", "article text")
TRANSLATED_COLUMNS = ("id", "body", "translated")
SUMMARIZED_COLUMNS = ("id", "body", "translated", "summary")
LABELED_COLUMNS = ("id", "body", "summary")
FINETUNE_COLUMNS = ("id", "body", "summary")
PUBLIC_EVAL_COLUMNS = ("input_text", "target_text", "text_len", "summary_len")
SLOT_COLUMNS = ("id", "who", "what", "when", "where", "why", "how")
PLANTED_COLUMNS = ("id", "kind", "summary", "dropped_slots", "note")
ORACLE_COLUMNS = ("id", "body", "summary", "oracle")


@dataclass(frozen=True)
class Schema:
    name: str
    columns: tuple[str, ...]
    course_script: str
    note: str


SCHEMAS: tuple[Schema, ...] = (
    Schema(
        "raw_articles",
        RAW_COLUMNS,
        "translate.py",
        "Course file was 10000_articles_without_linebreaks.csv.",
    ),
    Schema(
        "translated_articles",
        TRANSLATED_COLUMNS,
        "translate.py / summary.py",
        "body stays Danish; translated is English.",
    ),
    Schema(
        "summarized_articles",
        SUMMARIZED_COLUMNS,
        "summary.py / translate_back.py",
        "Course name was summarized_file_ml80_rp5.0.csv.",
    ),
    Schema(
        "labeled_dataset",
        LABELED_COLUMNS,
        "translate_back.py / finetune.py",
        "summary is now Danish silver. Course name labeled_dataset_ml80_rp5.0.csv.",
    ),
    Schema(
        "finetune_split",
        FINETUNE_COLUMNS,
        "finetune.py",
        "datasets/train_dataset.csv and friends.",
    ),
    Schema(
        "public_eval_shape",
        PUBLIC_EVAL_COLUMNS,
        "eval.py / use_model.py",
        "alexandrainst/nordjylland-news-summarization and the ScandEval mini.",
    ),
    Schema(
        "slot_cards",
        SLOT_COLUMNS,
        "(desk only)",
        "Gold 5W1H cards for the Sejerø briefs.",
    ),
    Schema(
        "planted_errors",
        PLANTED_COLUMNS,
        "(desk only)",
        "Broken Danish summaries used as metric counterexamples.",
    ),
    Schema(
        "oracle_labels",
        ORACLE_COLUMNS,
        "(desk only)",
        "Silver Danish next to a human oracle manchet.",
    ),
)


def schema_by_name(name: str) -> Schema:
    for schema in SCHEMAS:
        if schema.name == name:
            return schema
    raise KeyError(name)


def missing_columns(name: str, columns: list[str]) -> tuple[str, ...]:
    expected = schema_by_name(name).columns
    have = set(columns)
    return tuple(col for col in expected if col not in have)
