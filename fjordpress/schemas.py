"""CSV column contracts copied off the 2023 scripts.

The original files never declared a schema. These tuples are read out of
the ``pandas.DataFrame({...})`` constructors and the ``load_dataset``
calls so an example can fail loudly when a column is renamed.

``eval.py`` / ``use_model.py`` talk to public Hugging Face sets whose
columns are ``input_text`` / ``target_text``. Fine-tuning talks to local
CSVs with ``id`` / ``body`` / ``summary``. The mismatch is real.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence, Tuple

# translate.py reads this column name from the raw dump.
RAW_INPUT_COLUMNS: Tuple[str, ...] = ("id", "article text")

# translate.py writes:
TRANSLATED_COLUMNS: Tuple[str, ...] = ("id", "body", "translated")

# summary.py writes (and also keeps the English source):
SUMMARISED_COLUMNS: Tuple[str, ...] = ("id", "body", "translated", "summary")

# translate_back.py writes the fine-tune table:
LABELED_COLUMNS: Tuple[str, ...] = ("id", "body", "summary")

# finetune.py local splits:
SPLIT_COLUMNS: Tuple[str, ...] = ("id", "body", "summary")

# eval.py public set (alexandrainst/nordjylland-news-summarization):
PUBLIC_EVAL_COLUMNS: Tuple[str, ...] = (
    "input_text",
    "target_text",
    "text_len",
    "summary_len",
)

SCHEMA_CATALOG = {
    "raw_input": RAW_INPUT_COLUMNS,
    "translated": TRANSLATED_COLUMNS,
    "summarised": SUMMARISED_COLUMNS,
    "labeled": LABELED_COLUMNS,
    "split": SPLIT_COLUMNS,
    "public_eval": PUBLIC_EVAL_COLUMNS,
}


@dataclass(frozen=True)
class SchemaError(ValueError):
    schema_name: str
    missing: Tuple[str, ...]
    extra: Tuple[str, ...]

    def __str__(self) -> str:  # pragma: no cover - message formatting
        bits = [f"schema {self.schema_name!r} mismatch"]
        if self.missing:
            bits.append(f"missing {list(self.missing)}")
        if self.extra:
            bits.append(f"unexpected {list(self.extra)}")
        return "; ".join(bits)


def validate_columns(
    columns: Sequence[str],
    schema_name: str,
    allow_extra: bool = False,
) -> None:
    expected = SCHEMA_CATALOG[schema_name]
    have = list(columns)
    missing = tuple(col for col in expected if col not in have)
    extra = tuple(col for col in have if col not in expected)
    if missing or (extra and not allow_extra):
        raise SchemaError(schema_name, missing, extra if not allow_extra else ())


def validate_row(row: Mapping[str, object], schema_name: str) -> None:
    validate_columns(list(row.keys()), schema_name, allow_extra=True)
    for col in SCHEMA_CATALOG[schema_name]:
        value = row.get(col)
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"schema {schema_name!r}: empty column {col!r}")


def script_io_notes() -> Tuple[str, ...]:
    """Short archaeology notes shown by ``fjordpress schemas``."""
    return (
        "translate.py reads 'article text' but writes the same field as 'body'.",
        "summary.py keeps English in 'summary' and also keeps 'translated'.",
        "translate_back.py drops 'translated' and overwrites 'summary' with Danish.",
        "finetune.py expects datasets/{train,validation,test}_dataset.csv with id/body/summary.",
        "eval.py ignores the local CSVs and loads a public HF dataset with input_text/target_text.",
        "use_model.py loads ScandEval/nordjylland-news-summarization-mini, not the local test split.",
        "summary.py slices the frame with [:10], so only the first ten rows are summarised.",
        "Ctranslate_converter.py only converts opus-mt-en-da; da-en is commented out.",
        "translate.py still looks for models/opus-mt-da-en_ct2.",
        "OPUS-MT is called with NLLB-style prefixes dan_Latn / eng_Latn.",
    )
