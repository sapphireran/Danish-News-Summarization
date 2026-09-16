"""CSV schemas for each stage of the personal course-project pipeline.

The original scripts hard-code filenames and column names. Keeping the
contracts in one place makes the sample files and ``schema_check.py``
agree with ``translate.py``, ``summary.py``, ``translate_back.py`` and
``finetune.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    required: bool = True
    description: str = ""


@dataclass(frozen=True)
class StageSchema:
    stage: str
    filename_glob: str
    columns: tuple[ColumnSpec, ...]
    produced_by: str
    notes: str = ""

    @property
    def required_names(self) -> list[str]:
        return [column.name for column in self.columns if column.required]


RAW_ARTICLES = StageSchema(
    stage="raw_articles",
    filename_glob="10000_articles_without_linebreaks.csv",
    columns=(
        ColumnSpec("id", description="Stable article identifier from the source dump."),
        ColumnSpec("article text", description="Danish body text, typically without hard line breaks."),
    ),
    produced_by="external Danish news dump used as course input",
    notes="``translate.py`` reads these two columns and no others.",
)

TRANSLATED = StageSchema(
    stage="translated_articles",
    filename_glob="translated_articles.csv",
    columns=(
        ColumnSpec("id", description="Copied from the raw file."),
        ColumnSpec("body", description="Original Danish article (renamed from 'article text')."),
        ColumnSpec("translated", description="English article after opus-mt-da-en."),
    ),
    produced_by="translate.py",
)

SUMMARIZED = StageSchema(
    stage="summarized_english",
    filename_glob="summarized_file_ml80_rp5.0.csv",
    columns=(
        ColumnSpec("id"),
        ColumnSpec("body", description="Original Danish article."),
        ColumnSpec("translated", description="English article."),
        ColumnSpec("summary", description="English abstractive summary (max_length=80, repetition_penalty=5.0)."),
    ),
    produced_by="summary.py",
    notes="The committed ``summary.py`` currently slices ``df[:10]`` — a debug leftover.",
)

LABELED = StageSchema(
    stage="labeled_danish",
    filename_glob="labeled_dataset_ml80_rp5.0.csv",
    columns=(
        ColumnSpec("id"),
        ColumnSpec("body", description="Original Danish article."),
        ColumnSpec("summary", description="Danish summary after opus-mt-en-da."),
    ),
    produced_by="translate_back.py",
    notes="The English 'translated' column is dropped at this stage.",
)

FINETUNE_SPLIT = StageSchema(
    stage="finetune_split",
    filename_glob="datasets/{train,validation,test}_dataset.csv",
    columns=(
        ColumnSpec("id"),
        ColumnSpec("body"),
        ColumnSpec("summary"),
    ),
    produced_by="manual split of the labeled Danish file",
    notes="``finetune.py`` expects exactly these three columns.",
)

EVAL_NORDJYLLAND_2023 = StageSchema(
    stage="eval_nordjylland_2023_names",
    filename_glob="Hugging Face: ScandEval/nordjylland-news-summarization-mini",
    columns=(
        ColumnSpec("input_text", description="Danish article."),
        ColumnSpec("target_text", description="Danish reference summary."),
        ColumnSpec("text_len", description="Character length of the article."),
        ColumnSpec("summary_len", description="Character length of the summary."),
    ),
    produced_by="ScandEval mini split, as used by use_model.py",
    notes=(
        "``eval.py`` also requests these four names from "
        "``alexandrainst/nordjylland-news-summarization``. The public card for "
        "that dataset now documents ``text`` / ``summary`` instead. See docs/evaluation.md."
    ),
)

PIPELINE_SCHEMAS: dict[str, StageSchema] = {
    spec.stage: spec
    for spec in (
        RAW_ARTICLES,
        TRANSLATED,
        SUMMARIZED,
        LABELED,
        FINETUNE_SPLIT,
        EVAL_NORDJYLLAND_2023,
    )
}


class SchemaError(ValueError):
    """One or more rows failed a stage contract."""


def validate_records(
    records: Sequence[Mapping[str, object]],
    stage: str,
    require_non_empty: Sequence[str] | None = None,
) -> list[str]:
    """Return a list of human-readable problems. Empty list means OK.

    Missing columns are errors. Extra columns are allowed so later notes
    can be attached without breaking older files.
    """
    if stage not in PIPELINE_SCHEMAS:
        raise KeyError(f"unknown stage {stage!r}; known: {sorted(PIPELINE_SCHEMAS)}")

    schema = PIPELINE_SCHEMAS[stage]
    problems: list[str] = []
    required = schema.required_names
    nonempty = list(require_non_empty) if require_non_empty is not None else required

    if not records:
        problems.append(f"{stage}: file has no data rows")
        return problems

    sample_keys = set(records[0].keys())
    missing = [name for name in required if name not in sample_keys]
    if missing:
        problems.append(f"{stage}: missing columns {missing}; have {sorted(sample_keys)}")
        return problems

    for index, row in enumerate(records):
        for name in nonempty:
            value = row.get(name)
            if value is None or (isinstance(value, str) and not value.strip()):
                problems.append(f"{stage}: row {index} column {name!r} is empty")
    return problems


def format_schema_table(stage: str) -> str:
    schema = PIPELINE_SCHEMAS[stage]
    lines = [
        f"# {schema.stage}",
        f"file: {schema.filename_glob}",
        f"produced by: {schema.produced_by}",
        "",
        "columns:",
    ]
    for column in schema.columns:
        extra = f" — {column.description}" if column.description else ""
        lines.append(f"- `{column.name}`{extra}")
    if schema.notes:
        lines.extend(["", f"notes: {schema.notes}"])
    return "\n".join(lines)
