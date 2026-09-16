"""CSV contracts used by the December 2023 course scripts.

Column names are taken from the scripts themselves, not from the private
10k dump (which was never committed).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CsvSchema:
    name: str
    script: str
    columns: tuple[str, ...]
    notes: str


COURSE_SCHEMAS: tuple[CsvSchema, ...] = (
    CsvSchema(
        name="source-articles",
        script="translate.py",
        columns=("id", "article text"),
        notes=(
            "Hardcoded input filename: 10000_articles_without_linebreaks.csv. "
            "The space in 'article text' is required."
        ),
    ),
    CsvSchema(
        name="translated",
        script="translate.py",
        columns=("id", "body", "translated"),
        notes="Writes translated_articles.csv. 'body' is the original Danish.",
    ),
    CsvSchema(
        name="summarized",
        script="summary.py",
        columns=("id", "body", "translated", "summary"),
        notes=(
            "Reads translated_articles.csv but slices [:10] before the loop. "
            "Default output: summarized_file_ml80_rp5.0.csv."
        ),
    ),
    CsvSchema(
        name="labeled",
        script="translate_back.py",
        columns=("id", "body", "summary"),
        notes=(
            "English summary column is dropped. Danish silver labels land in "
            "'summary'. Default output: labeled_dataset_ml80_rp5.0.csv."
        ),
    ),
    CsvSchema(
        name="finetune-split",
        script="finetune.py",
        columns=("id", "body", "summary"),
        notes=(
            "Expects datasets/train_dataset.csv, validation_dataset.csv, "
            "test_dataset.csv. Same three columns as the labeled file."
        ),
    ),
    CsvSchema(
        name="public-eval",
        script="eval.py / use_model.py",
        columns=("input_text", "target_text", "text_len", "summary_len"),
        notes=(
            "Nordjylland news summarization on the Hub. eval.py loads "
            "alexandrainst/nordjylland-news-summarization; use_model.py "
            "loads ScandEval/nordjylland-news-summarization-mini."
        ),
    ),
)


def schema_by_name(name: str) -> CsvSchema:
    for schema in COURSE_SCHEMAS:
        if schema.name == name:
            return schema
    raise KeyError(name)
