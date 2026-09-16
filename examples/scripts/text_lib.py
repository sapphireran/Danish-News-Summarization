"""Shared helpers for the CPU-only examples.

The 2023 root scripts talk to Hugging Face tokenizers and NLTK. This
module reconstructs the same *control flow* with a tiny regex tokenizer
so the examples run without those packages.

Approximate token counts will not match OPUS-MT or mT5. They are good
enough to exercise packing, length reports, and overlap scores.
"""

from __future__ import annotations

import csv
import json
import random
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"
DATA_DIR = EXAMPLES_DIR / "data"
CONFIG_DIR = EXAMPLES_DIR / "configs"
EXPECTED_COLUMNS_PATH = DATA_DIR / "expected_columns.json"

TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")
WORD_RE = re.compile(r"\w+", re.UNICODE)
PUNCT_BREAKS = {",", ";", ":"}


def load_expected_columns(path: Path | None = None) -> dict:
    target = path or EXPECTED_COLUMNS_PATH
    with target.open(encoding="utf-8") as handle:
        return json.load(handle)


def read_csv(path: Path | str) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path | str, rows: Sequence[dict[str, str]], fieldnames: Sequence[str]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def approximate_tokens(text: str) -> list[str]:
    """Whitespace-and-punctuation tokens. Not SentencePiece, not OPUS-MT."""
    return TOKEN_RE.findall(text or "")


def approximate_token_len(text: str, add_special_tokens: bool = True) -> int:
    # The 2023 packer counts tokenizer.encode(..., add_special_tokens=True)
    # per sentence. Mirror that with a fake BOS/EOS pair.
    extra = 2 if add_special_tokens else 0
    return len(approximate_tokens(text)) + extra


def word_tokens(text: str, lowercase: bool = True) -> list[str]:
    tokens = WORD_RE.findall(text or "")
    if lowercase:
        return [token.lower() for token in tokens]
    return tokens


def split_sentences(text: str) -> list[str]:
    """Light sentence splitter. Abbreviations will fool it; NLTK is smarter."""
    cleaned = normalize_space(text)
    if not cleaned:
        return []
    parts = SENTENCE_SPLIT_RE.split(cleaned)
    return [part.strip() for part in parts if part.strip()]


def split_long_sentence(sentence: str, max_length: int) -> list[str]:
    """Port of translate.py / summary.py long-sentence splitting."""
    words = approximate_tokens(sentence)
    current_chunk: list[str] = []
    chunks: list[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in PUNCT_BREAKS and current_length < max_length:
            chunks.append(_join_tokens(current_chunk))
            current_chunk = []
            current_length = 0
        elif current_length >= max_length:
            last_word = current_chunk.pop()
            if current_chunk:
                chunks.append(_join_tokens(current_chunk))
            current_chunk = [last_word]
            current_length = len(last_word) + 1

    if current_chunk:
        chunks.append(_join_tokens(current_chunk))
    return [chunk for chunk in chunks if chunk]


def _join_tokens(tokens: Sequence[str]) -> str:
    """Join so punctuation does not pick up a leading space."""
    pieces: list[str] = []
    for token in tokens:
        if not pieces:
            pieces.append(token)
            continue
        if re.fullmatch(r"[^\w\s]+", token) and token not in {"(", "[", "{"}:
            pieces[-1] = pieces[-1] + token
        else:
            pieces.append(token)
    return " ".join(pieces)


@dataclass
class PackedWindow:
    sentences: list[str]
    token_lengths: list[int]

    @property
    def token_count(self) -> int:
        return sum(self.token_lengths)

    def as_text(self) -> str:
        return " ".join(self.sentences)


def pack_sentences(
    article: str,
    text_max_length: int,
    *,
    split_overlong: bool = True,
) -> list[PackedWindow]:
    """Reconstruct the 2023 window packer.

    1. Sentence-split the article.
    2. Optionally carve up sentences whose approximate token length is
       above ``text_max_length``.
    3. Pack consecutive sentences until the next one would overflow.
    """
    raw_sentences = split_sentences(article)
    sentence_tokens_lengths: list[tuple[str, int]] = []

    for sentence in raw_sentences:
        sentence_length = approximate_token_len(sentence, add_special_tokens=True)
        if split_overlong and sentence_length > text_max_length:
            for chunk in split_long_sentence(sentence, text_max_length):
                chunk_length = approximate_token_len(chunk, add_special_tokens=True)
                if chunk.strip():
                    sentence_tokens_lengths.append((chunk, chunk_length))
        elif sentence.strip():
            sentence_tokens_lengths.append((sentence, sentence_length))

    windows: list[PackedWindow] = []
    current_sentences: list[str] = []
    current_lengths: list[int] = []
    current_length = 0

    for sentence, length in sentence_tokens_lengths:
        if current_sentences and current_length + length > text_max_length:
            windows.append(PackedWindow(current_sentences, current_lengths))
            current_sentences = [sentence]
            current_lengths = [length]
            current_length = length
        else:
            current_sentences.append(sentence)
            current_lengths.append(length)
            current_length += length

    if current_sentences:
        windows.append(PackedWindow(current_sentences, current_lengths))
    return windows


def lead_n_sentences(text: str, n: int) -> str:
    sentences = split_sentences(text)
    if not sentences or n <= 0:
        return ""
    return " ".join(sentences[:n])


def ngrams(tokens: Sequence[str], n: int) -> list[tuple[str, ...]]:
    if n <= 0 or len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def overlap_f1(pred_tokens: Sequence[str], gold_tokens: Sequence[str], n: int) -> float:
    pred_grams = ngrams(pred_tokens, n)
    gold_grams = ngrams(gold_tokens, n)
    if not pred_grams and not gold_grams:
        return 1.0
    if not pred_grams or not gold_grams:
        return 0.0
    pred_counts = Counter(pred_grams)
    gold_counts = Counter(gold_grams)
    overlap = sum((pred_counts & gold_counts).values())
    precision = overlap / len(pred_grams)
    recall = overlap / len(gold_grams)
    return _f1(precision, recall)


def lcs_length(left: Sequence[str], right: Sequence[str]) -> int:
    if not left or not right:
        return 0
    # Hunt–Szymanski-style DP over the shorter axis.
    if len(right) < len(left):
        left, right = right, left
    previous = [0] * (len(right) + 1)
    for left_token in left:
        current = [0]
        for j, right_token in enumerate(right, start=1):
            if left_token == right_token:
                current.append(previous[j - 1] + 1)
            else:
                current.append(max(previous[j], current[-1]))
        previous = current
    return previous[-1]


def rouge_l_f1(pred_tokens: Sequence[str], gold_tokens: Sequence[str]) -> float:
    if not pred_tokens and not gold_tokens:
        return 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0
    lcs = lcs_length(pred_tokens, gold_tokens)
    precision = lcs / len(pred_tokens)
    recall = lcs / len(gold_tokens)
    return _f1(precision, recall)


@dataclass
class OverlapScores:
    rouge1: float
    rouge2: float
    rougeL: float
    pred_tokens: int
    gold_tokens: int

    def as_dict(self) -> dict[str, float | int]:
        return {
            "rouge1": self.rouge1,
            "rouge2": self.rouge2,
            "rougeL": self.rougeL,
            "pred_tokens": self.pred_tokens,
            "gold_tokens": self.gold_tokens,
        }


def score_overlap(pred: str, gold: str) -> OverlapScores:
    pred_tokens = word_tokens(pred)
    gold_tokens = word_tokens(gold)
    return OverlapScores(
        rouge1=overlap_f1(pred_tokens, gold_tokens, 1),
        rouge2=overlap_f1(pred_tokens, gold_tokens, 2),
        rougeL=rouge_l_f1(pred_tokens, gold_tokens),
        pred_tokens=len(pred_tokens),
        gold_tokens=len(gold_tokens),
    )


def mean(values: Iterable[float]) -> float:
    sequence = list(values)
    if not sequence:
        return 0.0
    return sum(sequence) / len(sequence)


@dataclass
class ColumnReport:
    stage: str
    path: str
    rows: int
    required: list[str]
    missing_columns: list[str]
    extra_columns: list[str]
    empty_cells: dict[str, int]
    duplicate_ids: list[str]
    id_column: str | None
    char_lengths: dict[str, dict[str, float]] = field(default_factory=dict)
    ok: bool = True
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "stage": self.stage,
            "path": self.path,
            "rows": self.rows,
            "required": self.required,
            "missing_columns": self.missing_columns,
            "extra_columns": self.extra_columns,
            "empty_cells": self.empty_cells,
            "duplicate_ids": self.duplicate_ids,
            "id_column": self.id_column,
            "char_lengths": self.char_lengths,
            "ok": self.ok,
            "notes": self.notes,
        }


def inspect_rows(
    rows: Sequence[dict[str, str]],
    stage: str,
    path: Path | str,
    spec: dict,
) -> ColumnReport:
    required = list(spec.get("required") or [])
    optional = set(spec.get("optional") or [])
    present = list(rows[0].keys()) if rows else []
    missing = [column for column in required if column not in present]
    extra = [column for column in present if column not in required and column not in optional]
    empty_cells = {column: 0 for column in required if column in (present or required)}
    for row in rows:
        for column in empty_cells:
            if not normalize_space(row.get(column, "")):
                empty_cells[column] += 1

    id_column = "id" if "id" in present or "id" in required else None
    duplicate_ids: list[str] = []
    if id_column:
        seen: dict[str, int] = {}
        for row in rows:
            key = row.get(id_column, "")
            seen[key] = seen.get(key, 0) + 1
        duplicate_ids = sorted(key for key, count in seen.items() if key and count > 1)

    char_lengths: dict[str, dict[str, float]] = {}
    for column in required:
        if column == "id" or column not in present:
            continue
        lengths = [len(row.get(column, "") or "") for row in rows]
        if not lengths:
            continue
        char_lengths[column] = {
            "min": float(min(lengths)),
            "max": float(max(lengths)),
            "mean": round(mean(float(value) for value in lengths), 1),
        }

    report = ColumnReport(
        stage=stage,
        path=str(path),
        rows=len(rows),
        required=required,
        missing_columns=missing,
        extra_columns=extra,
        empty_cells=empty_cells,
        duplicate_ids=duplicate_ids,
        id_column=id_column,
        char_lengths=char_lengths,
    )
    report.ok = not missing and not duplicate_ids and all(count == 0 for count in empty_cells.values())
    if spec.get("notes"):
        report.notes.append(str(spec["notes"]))
    if not rows:
        report.ok = False
        report.notes.append("File has a header but no data rows.")
    return report


def align_by_id(
    left_rows: Sequence[dict[str, str]],
    right_rows: Sequence[dict[str, str]],
    id_column: str = "id",
) -> Iterator[tuple[str, dict[str, str], dict[str, str]]]:
    right_index = {row[id_column]: row for row in right_rows if row.get(id_column)}
    for left in left_rows:
        key = left.get(id_column, "")
        if key in right_index:
            yield key, left, right_index[key]


def split_rows(
    rows: Sequence[dict[str, str]],
    *,
    train: float,
    validation: float,
    test: float,
    seed: int,
    id_column: str = "id",
) -> dict[str, list[dict[str, str]]]:
    if abs((train + validation + test) - 1.0) > 1e-6:
        raise ValueError(f"Split ratios must sum to 1, got {train}+{validation}+{test}")
    if any(value < 0 for value in (train, validation, test)):
        raise ValueError("Split ratios must be non-negative")

    ids = []
    seen = set()
    for row in rows:
        key = row.get(id_column, "")
        if key not in seen:
            seen.add(key)
            ids.append(key)
    rng = random.Random(seed)
    rng.shuffle(ids)

    n = len(ids)
    n_train = int(n * train)
    n_validation = int(n * validation)
    # Put the remainder in test so nothing is dropped.
    n_test = n - n_train - n_validation
    if test == 0:
        n_test = 0
        n_validation = n - n_train
    assignments = {
        "train": set(ids[:n_train]),
        "validation": set(ids[n_train : n_train + n_validation]),
        "test": set(ids[n_train + n_validation : n_train + n_validation + n_test]),
    }
    buckets = {"train": [], "validation": [], "test": []}
    for row in rows:
        key = row.get(id_column, "")
        for name, group in assignments.items():
            if key in group:
                buckets[name].append(dict(row))
                break
    return buckets


def unicode_letter_ratio(text: str) -> float:
    letters = 0
    total = 0
    for char in text or "":
        if char.isspace():
            continue
        total += 1
        if unicodedata.category(char).startswith("L"):
            letters += 1
    return 0.0 if total == 0 else letters / total


def looks_like_danish(text: str) -> bool:
    """Very rough heuristic for fixture checks, not a language id model."""
    lowered = (text or "").lower()
    markers = (" og ", " det ", " en ", " på ", " til ", " æ", " ø", " å")
    return any(marker in lowered for marker in markers)
