"""Five-axis annotation rubric plus a deterministic heuristic scorer.

The heuristic is a lab instrument, not a substitute for a second human. Docs
in `docs/annotation-rubric.md` explain the 1–5 anchors. The 2023 course never
committed a human eval sheet; this is the sheet I wish I had kept.
"""

from __future__ import annotations

from dataclasses import dataclass

from .tokenize import content_tokens, tokenize

AXES = (
    "faithfulness",
    "coverage",
    "fluency",
    "conciseness",
    "danish_naturalness",
)

# Leftover English that should not appear in a Danish silver label.
ENGLISH_LEFTOVERS = (
    "the",
    "and",
    "from",
    "with",
    "premiere",
    "open",
    "night",
    "tent",
    "square",
    "graduation",
    "films",
    "nasa",
)


@dataclass(frozen=True)
class RubricScores:
    faithfulness: int
    coverage: int
    fluency: int
    conciseness: int
    danish_naturalness: int
    notes: str = ""

    def as_dict(self) -> dict[str, int | str]:
        return {
            "faithfulness": self.faithfulness,
            "coverage": self.coverage,
            "fluency": self.fluency,
            "conciseness": self.conciseness,
            "danish_naturalness": self.danish_naturalness,
            "notes": self.notes,
        }

    @property
    def mean(self) -> float:
        return (
            self.faithfulness
            + self.coverage
            + self.fluency
            + self.conciseness
            + self.danish_naturalness
        ) / 5.0


def _clamp_star(value: float) -> int:
    return max(1, min(5, int(round(value))))


def score_rubric(article: str, summary: str, reference: str | None = None) -> RubricScores:
    """Heuristic 1–5 scores. `reference` is an optional gold abstractive."""
    pred = content_tokens(summary)
    src = set(content_tokens(article))
    ref = set(content_tokens(reference)) if reference else src
    pred_set = set(pred)

    if not pred:
        return RubricScores(1, 1, 1, 1, 1, notes="empty summary")

    supported = pred_set & src
    faithfulness_ratio = len(supported) / max(len(pred_set), 1)
    coverage_ratio = len(pred_set & ref) / max(len(ref), 1)

    tokens = tokenize(summary)
    unique_ratio = len(set(tokens)) / max(len(tokens), 1)
    starts_capital = bool(summary) and summary[0].isupper()
    ends_punct = bool(summary) and summary.rstrip()[-1] in ".!?"
    fluency = 3.0
    fluency += 0.7 if starts_capital else -0.8
    fluency += 0.5 if ends_punct else -0.4
    fluency += 0.6 if unique_ratio > 0.72 else -0.6

    length = len(tokens)
    if 8 <= length <= 42:
        conciseness = 5.0
    elif 5 <= length < 8 or 42 < length <= 60:
        conciseness = 3.0
    else:
        conciseness = 2.0

    leftover_hits = sum(1 for tok in tokens if tok in ENGLISH_LEFTOVERS)
    has_danish_vowel = any(ch in summary.casefold() for ch in "æøå")
    naturalness = 4.0
    naturalness -= 1.2 * leftover_hits
    if has_danish_vowel:
        naturalness += 0.6
    else:
        naturalness -= 0.8

    notes_bits = []
    if leftover_hits:
        notes_bits.append(f"{leftover_hits} English leftover(s)")
    if faithfulness_ratio < 0.5:
        notes_bits.append("many unsupported content words")
    if coverage_ratio < 0.15:
        notes_bits.append("thin coverage of the reference")

    return RubricScores(
        faithfulness=_clamp_star(1 + 4 * faithfulness_ratio),
        coverage=_clamp_star(1 + 4 * coverage_ratio),
        fluency=_clamp_star(fluency),
        conciseness=_clamp_star(conciseness),
        danish_naturalness=_clamp_star(naturalness),
        notes="; ".join(notes_bits),
    )
