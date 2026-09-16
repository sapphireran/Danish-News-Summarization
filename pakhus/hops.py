"""Four-hop silver cascade on Toftevig fixtures, no model weights.

Hop 1 uses canned parallel English (standing in for OPUS).
Hop 2 re-packs that English with the course summary packer and writes
extractive pane briefs (standing in for T5).
Hop 3 maps briefs back to Danish with a sentence glossary plus a small
word list, standing in for OPUS en-da.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pakhus.concat import score_concat, silver_from_panes
from pakhus.corpus import ARTICLES, Article, get_article
from pakhus.packing import PackResult, ascii_atlas, pack_course_summary, pack_course_translate
from pakhus.schemas import (
    HOP0_RAW,
    HOP1_TRANSLATED,
    HOP2_SUMMARIZED,
    HOP3_LABELED,
    HOP4_FINETUNE,
    PANE_TRACE,
    PUBLIC_EVAL,
    LAB_FILENAMES,
)
from pakhus.sentences import split_naive
from pakhus.tokenize import approx_encode_len


@dataclass
class HopTrace:
    article_id: str
    hop: str
    packer: str
    result: PackResult

    def rows(self) -> list[dict[str, object]]:
        out: list[dict[str, object]] = []
        for pane in self.result.panes:
            row = pane.as_dict()
            row["id"] = self.article_id
            row["hop"] = self.hop
            row["packer"] = self.packer
            out.append(row)
        return out


@dataclass
class CascadeRow:
    article: Article
    english: str
    english_silver: str
    danish_silver: str
    hop1: PackResult
    hop2: PackResult
    pane_briefs_en: list[str]
    concat: object


@dataclass
class Cascade:
    rows: list[CascadeRow] = field(default_factory=list)
    traces: list[HopTrace] = field(default_factory=list)

    def article_ids(self) -> list[str]:
        return [r.article.id for r in self.rows]


# Small closed glossary for words that appear in pane briefs but not as
# full canned sentences (truncation fragments, detokenized commas).
_WORD_GLOSSARY = {
    "harbour": "havn",
    "committee": "udvalg",
    "hearing": "høring",
    "quay": "kaj",
    "dredging": "uddybning",
    "warehouse": "pakhus",
    "ferry": "færge",
    "school": "skole",
    "dike": "dige",
    "municipality": "kommune",
    "million": "mio.",
    "wednesday": "onsdag",
    "thursday": "torsdag",
    "monday": "mandag",
    "november": "november",
    "october": "oktober",
    "december": "december",
    "march": "marts",
    "april": "april",
}


def _glossary(article: Article) -> dict[str, str]:
    table = {en.strip(): da.strip() for da, en in article.pairs}
    table[article.oracle_summary_en] = article.oracle_summary_da
    return table


def back_translate(english: str, article: Article) -> str:
    """Map English back to Danish using aligned sentences, then words."""
    if not english.strip():
        return ""
    table = _glossary(article)
    if english.strip() in table:
        return table[english.strip()]
    sentences = split_naive(english)
    out: list[str] = []
    for sent in sentences:
        key = sent.strip()
        if key in table:
            out.append(table[key])
            continue
        # Fuzzy: a pane brief may be a prefix of a canned sentence.
        matched = False
        for en, da in table.items():
            if key == en[: len(key)] and len(key) > 40:
                out.append(da)
                matched = True
                break
            if en.startswith(key) and len(key) > 40:
                out.append(da)
                matched = True
                break
        if matched:
            continue
        words = []
        for token in key.split():
            lower = token.lower().strip(".,;:\"«»")
            if lower in _WORD_GLOSSARY:
                words.append(_WORD_GLOSSARY[lower])
            else:
                words.append(token)
        out.append(" ".join(words))
    return " ".join(out).strip()


def run_article(article: Article) -> CascadeRow:
    hop1 = pack_course_translate(article.danish)
    english = article.english
    hop2 = pack_course_summary(english)
    english_silver, briefs = silver_from_panes(hop2)
    danish_silver = back_translate(english_silver, article)
    concat = score_concat(article.id, english, pack_result=hop2)
    return CascadeRow(
        article=article,
        english=english,
        english_silver=english_silver,
        danish_silver=danish_silver,
        hop1=hop1,
        hop2=hop2,
        pane_briefs_en=briefs,
        concat=concat,
    )


def run_corpus(articles: tuple[Article, ...] | None = None) -> Cascade:
    cascade = Cascade()
    for article in articles or ARTICLES:
        row = run_article(article)
        cascade.rows.append(row)
        cascade.traces.append(HopTrace(article.id, "hop1_translate", row.hop1.packer, row.hop1))
        cascade.traces.append(HopTrace(article.id, "hop2_summary", row.hop2.packer, row.hop2))
    return cascade


def hop0_rows(cascade: Cascade) -> list[dict[str, object]]:
    return [
        {"id": r.article.id, "article text": r.article.danish}
        for r in cascade.rows
    ]


def hop1_rows(cascade: Cascade) -> list[dict[str, object]]:
    return [
        {"id": r.article.id, "body": r.article.danish, "translated": r.english}
        for r in cascade.rows
    ]


def hop2_rows(cascade: Cascade) -> list[dict[str, object]]:
    return [
        {
            "id": r.article.id,
            "body": r.article.danish,
            "translated": r.english,
            "summary": r.english_silver,
        }
        for r in cascade.rows
    ]


def hop3_rows(cascade: Cascade) -> list[dict[str, object]]:
    return [
        {"id": r.article.id, "body": r.article.danish, "summary": r.danish_silver}
        for r in cascade.rows
    ]


def oracle_rows(cascade: Cascade) -> list[dict[str, object]]:
    return [
        {"id": r.article.id, "body": r.article.danish, "summary": r.article.oracle_summary_da}
        for r in cascade.rows
    ]


def finetune_rows(cascade: Cascade, split: str) -> list[dict[str, object]]:
    return [
        {"id": r.article.id, "body": r.article.danish, "summary": r.danish_silver}
        for r in cascade.rows
        if r.article.split == split
    ]


def public_eval_rows(cascade: Cascade) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for r in cascade.rows:
        if r.article.split != "test":
            continue
        rows.append(
            {
                "input_text": r.article.danish,
                "target_text": r.article.oracle_summary_da,
                "text_len": approx_encode_len(r.article.danish),
                "summary_len": approx_encode_len(r.article.oracle_summary_da),
            }
        )
    return rows


def pane_trace_rows(cascade: Cascade) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for trace in cascade.traces:
        rows.extend(trace.rows())
    return rows


def concat_rows(cascade: Cascade) -> list[dict[str, object]]:
    return [r.concat.as_dict() for r in cascade.rows]


def atlas_for(article_id: str) -> str:
    article = get_article(article_id)
    row = run_article(article)
    parts = [
        f"# {article.id}  {article.title_da}",
        f"planted: {', '.join(article.planted)}",
        f"figures: {', '.join(article.figures()) or '(none)'}",
        f"names: {', '.join(article.names()) or '(none)'}",
        "",
        "## hop 1  Danish → (canned) English  packer=course_translate",
        ascii_atlas(row.hop1, article.id),
        "",
        "## hop 2  English → extractive pane briefs  packer=course_summary",
        ascii_atlas(row.hop2, article.id),
        "",
        f"## concat  units={row.concat.silver_units}  "
        f"truncate@128={row.concat.would_truncate_at_128}  "
        f"pane0_share={row.concat.pane0_share:.2f}  "
        f"echo={','.join(row.concat.echo_names) or '(none)'}",
        row.english_silver,
    ]
    return "\n".join(parts) + "\n"


# Re-export contract names so writers can map files without circular imports.
CONTRACTS_FOR_HOPS = {
    "hop0": HOP0_RAW,
    "hop1": HOP1_TRANSLATED,
    "hop2": HOP2_SUMMARIZED,
    "hop3": HOP3_LABELED,
    "hop4": HOP4_FINETUNE,
    "public": PUBLIC_EVAL,
    "panes": PANE_TRACE,
    "files": LAB_FILENAMES,
}
