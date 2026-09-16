"""Show a simple silver-label filter on the fictional corpus.

The 2023 pipeline writes every back-translated pair to disk. A later
cleanup would drop pairs that are too long, too short, or barely
compressed. This demo prints keep/drop decisions; it does not rewrite
the sample CSVs.

    python examples/length_filter.py
    python examples/length_filter.py --min-ratio 0.05 --max-ratio 0.35
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.data.corpus import ARTICLES
from examples.danish_sentences import word_tokenize


@dataclass(frozen=True)
class FilterThresholds:
    min_body_words: int = 50
    max_body_words: int = 400
    min_summary_words: int = 8
    max_summary_words: int = 60
    min_ratio: float = 0.04
    max_ratio: float = 0.45


@dataclass(frozen=True)
class FilterDecision:
    article_id: str
    body_words: int
    summary_words: int
    ratio: float
    keep: bool
    reasons: tuple[str, ...]


def decide(article_id: str, body: str, summary: str, thresholds: FilterThresholds) -> FilterDecision:
    body_words = len(word_tokenize(body))
    summary_words = len(word_tokenize(summary))
    ratio = summary_words / max(1, body_words)
    reasons: list[str] = []
    if body_words < thresholds.min_body_words:
        reasons.append(f"body too short ({body_words} < {thresholds.min_body_words})")
    if body_words > thresholds.max_body_words:
        reasons.append(f"body too long ({body_words} > {thresholds.max_body_words})")
    if summary_words < thresholds.min_summary_words:
        reasons.append(f"summary too short ({summary_words} < {thresholds.min_summary_words})")
    if summary_words > thresholds.max_summary_words:
        reasons.append(f"summary too long ({summary_words} > {thresholds.max_summary_words})")
    if ratio < thresholds.min_ratio:
        reasons.append(f"ratio {ratio:.3f} < {thresholds.min_ratio}")
    if ratio > thresholds.max_ratio:
        reasons.append(f"ratio {ratio:.3f} > {thresholds.max_ratio}")
    return FilterDecision(
        article_id=article_id,
        body_words=body_words,
        summary_words=summary_words,
        ratio=ratio,
        keep=not reasons,
        reasons=tuple(reasons),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-body-words", type=int, default=50)
    parser.add_argument("--max-body-words", type=int, default=400)
    parser.add_argument("--min-summary-words", type=int, default=8)
    parser.add_argument("--max-summary-words", type=int, default=60)
    parser.add_argument("--min-ratio", type=float, default=0.04)
    parser.add_argument("--max-ratio", type=float, default=0.45)
    args = parser.parse_args()
    thresholds = FilterThresholds(
        min_body_words=args.min_body_words,
        max_body_words=args.max_body_words,
        min_summary_words=args.min_summary_words,
        max_summary_words=args.max_summary_words,
        min_ratio=args.min_ratio,
        max_ratio=args.max_ratio,
    )

    print("Silver-label length/ratio filter on the fictional corpus")
    print(
        f"body words [{thresholds.min_body_words}, {thresholds.max_body_words}]  "
        f"summary words [{thresholds.min_summary_words}, {thresholds.max_summary_words}]  "
        f"ratio [{thresholds.min_ratio}, {thresholds.max_ratio}]"
    )
    print("These thresholds are teaching defaults, not the 2023 scripts.\n")
    print(f"{'id':<8}{'body':>6}{'sum':>6}{'ratio':>8}  decision")
    print("-" * 52)

    kept = 0
    for article in ARTICLES:
        decision = decide(
            article["id"],
            article["danish_body"],
            article["danish_summary"],
            thresholds,
        )
        kept += int(decision.keep)
        label = "keep" if decision.keep else "DROP"
        print(
            f"{decision.article_id:<8}{decision.body_words:>6}"
            f"{decision.summary_words:>6}{decision.ratio:>8.3f}  {label}"
        )
        for reason in decision.reasons:
            print(f"        {reason}")

    dropped = len(ARTICLES) - kept
    print("-" * 52)
    print(f"kept {kept}/{len(ARTICLES)}  dropped {dropped}")
    if dropped:
        print("da-005 is the short museum note; it is meant to fail a min-body rule.")


if __name__ == "__main__":
    main()
