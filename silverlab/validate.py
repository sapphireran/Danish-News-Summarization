"""Integrity checks for the fiction corpus and the hop-error catalog."""

from __future__ import annotations

from dataclasses import dataclass

from .catalog import ERROR_CODES, ErrorItem, load_catalog
from .fiction import Brief, load_briefs
from .sentences import split_sentences


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def _brief_checks(briefs: list[Brief]) -> list[Check]:
    checks: list[Check] = []
    ids = [brief.id for brief in briefs]
    checks.append(
        Check("unique-brief-ids", len(ids) == len(set(ids)), f"{len(ids)} briefs")
    )
    checks.append(Check("non-empty-corpus", bool(briefs), f"{len(briefs)} briefs"))
    for brief in briefs:
        sentences = split_sentences(brief.article_text)
        checks.append(
            Check(
                f"{brief.id}-sentence-count",
                len(sentences) >= 4,
                f"{len(sentences)} sentences",
            )
        )
        checks.append(
            Check(
                f"{brief.id}-extractive-in-article",
                brief.gold_extractive in brief.article_text,
                "gold extractive must be a substring of the article",
            )
        )
        checks.append(
            Check(
                f"{brief.id}-abstractive-differs",
                brief.gold_abstractive not in brief.article_text,
                "gold abstractive should be a rewrite, not a copy",
            )
        )
        checks.append(
            Check(
                f"{brief.id}-has-danish-vowels",
                any(ch in brief.article_text for ch in "æøåÆØÅ"),
                "article should look like Danish",
            )
        )
    return checks


def _catalog_checks(items: list[ErrorItem], briefs: list[Brief]) -> list[Check]:
    checks: list[Check] = []
    brief_ids = {brief.id for brief in briefs}
    item_ids = [item.id for item in items]
    checks.append(
        Check("unique-error-ids", len(item_ids) == len(set(item_ids)), f"{len(item_ids)} items")
    )
    for item in items:
        checks.append(
            Check(
                f"{item.id}-known-article",
                item.article_id in brief_ids,
                item.article_id,
            )
        )
        checks.append(
            Check(
                f"{item.id}-severity-range",
                1 <= item.severity <= 5,
                str(item.severity),
            )
        )
        unknown = [code for code in item.codes if code not in ERROR_CODES]
        checks.append(
            Check(f"{item.id}-known-codes", not unknown, ",".join(unknown) or "ok")
        )
        if item.article_id in brief_ids:
            article = next(brief.article_text for brief in briefs if brief.id == item.article_id)
            checks.append(
                Check(
                    f"{item.id}-source-span-found",
                    item.source_span in article,
                    item.source_span[:48],
                )
            )
    return checks


def run_checks() -> list[Check]:
    briefs = load_briefs()
    items = load_catalog()
    return _brief_checks(briefs) + _catalog_checks(items, briefs)


def failed_checks(checks: list[Check] | None = None) -> list[Check]:
    material = checks if checks is not None else run_checks()
    return [check for check in material if not check.ok]
