"""CSV column contracts taken from the frozen 2023 scripts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CsvContract:
    name: str
    filename: str
    columns: tuple[str, ...]
    required: tuple[str, ...]
    notes: str
    course_file: str


HOP0_RAW = CsvContract(
    name="hop0_raw",
    filename="10000_articles_without_linebreaks.csv",
    columns=("id", "article text"),
    required=("id", "article text"),
    notes="Space in `article text` is load-bearing for translate.py.",
    course_file="translate.py",
)

HOP1_TRANSLATED = CsvContract(
    name="hop1_translated",
    filename="translated_articles.csv",
    columns=("id", "body", "translated"),
    required=("id", "body", "translated"),
    notes="body is the original Danish; translated is English.",
    course_file="translate.py",
)

HOP2_SUMMARIZED = CsvContract(
    name="hop2_summarized",
    filename="summarized_file_ml80_rp5.0.csv",
    columns=("id", "body", "translated", "summary"),
    required=("id", "body", "translated", "summary"),
    notes="summary is English, concatenated across T5 panes.",
    course_file="summary.py",
)

HOP3_LABELED = CsvContract(
    name="hop3_labeled",
    filename="labeled_dataset_ml80_rp5.0.csv",
    columns=("id", "body", "summary"),
    required=("id", "body", "summary"),
    notes="English columns dropped. summary is the Danish silver label.",
    course_file="translate_back.py",
)

HOP4_FINETUNE = CsvContract(
    name="hop4_finetune",
    filename="datasets/train_dataset.csv",
    columns=("id", "body", "summary"),
    required=("id", "body", "summary"),
    notes="Same columns as hop 3; split is not committed.",
    course_file="finetune.py",
)

PUBLIC_EVAL = CsvContract(
    name="public_eval",
    filename="nordjylland-like.csv",
    columns=("input_text", "target_text", "text_len", "summary_len"),
    required=("input_text", "target_text"),
    notes="eval.py / use_model.py Hugging Face schema, not silver-label schema.",
    course_file="eval.py",
)

PANE_TRACE = CsvContract(
    name="pane_trace",
    filename="pane_trace.csv",
    columns=(
        "id",
        "hop",
        "packer",
        "pane_id",
        "n_sentences",
        "approx_units",
        "budget",
        "fill_ratio",
        "empty",
        "over_budget",
        "text",
    ),
    required=("id", "hop", "pane_id", "text"),
    notes="Lab sidecar. The 2023 CSVs do not keep pane ids.",
    course_file="(lab)",
)

CONTRACTS = {
    c.name: c
    for c in (
        HOP0_RAW,
        HOP1_TRANSLATED,
        HOP2_SUMMARIZED,
        HOP3_LABELED,
        HOP4_FINETUNE,
        PUBLIC_EVAL,
        PANE_TRACE,
    )
}

LAB_FILENAMES = {
    "hop0_raw": "00_raw_articles.csv",
    "hop1_translated": "01_translated_articles.csv",
    "hop2_summarized": "02_summarized_articles.csv",
    "hop3_labeled": "03_labeled_dataset.csv",
    "hop3_oracle": "03_labeled_oracle.csv",
    "hop4_train": "04_train_dataset.csv",
    "hop4_validation": "04_validation_dataset.csv",
    "hop4_test": "04_test_dataset.csv",
    "public_eval": "05_public_eval_shape.csv",
    "pane_trace": "pane_trace.csv",
    "concat_scores": "concat_scores.csv",
}


class SchemaError(ValueError):
    pass


def validate_row(contract: CsvContract, row: dict[str, object]) -> list[str]:
    problems: list[str] = []
    for col in contract.required:
        if col not in row:
            problems.append(f"{contract.name}: missing column {col!r}")
        elif row[col] is None or str(row[col]).strip() == "":
            problems.append(f"{contract.name}: empty value for {col!r}")
    extra = set(row) - set(contract.columns)
    # Extra columns are allowed on lab sidecars only if they do not
    # collide with a renamed hop-0 field.
    if "article_text" in row and contract.name == "hop0_raw":
        problems.append(
            "hop0_raw: found article_text; translate.py reads 'article text'"
        )
    if extra and contract.name == "hop0_raw":
        problems.append(
            f"hop0_raw: unexpected columns {sorted(extra)}; keep the space in 'article text'"
        )
    return problems


def validate_table(contract: CsvContract, rows: list[dict[str, object]]) -> list[str]:
    if not rows:
        return [f"{contract.name}: no rows"]
    problems: list[str] = []
    header = set(rows[0])
    for col in contract.required:
        if col not in header:
            problems.append(f"{contract.name}: header missing {col!r}")
    for i, row in enumerate(rows):
        for issue in validate_row(contract, row):
            problems.append(f"row {i}: {issue}")
    return problems


def assert_article_text_column(columns: list[str]) -> None:
    if "article text" not in columns:
        raise SchemaError(
            "hop 0 requires the literal column name 'article text' "
            f"(got {columns!r})"
        )
    if "article_text" in columns:
        raise SchemaError("do not rename 'article text' to article_text")
