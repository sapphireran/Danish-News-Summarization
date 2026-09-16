"""Four-hop silver labels, with an oracle bound and a gloss bound.

The 2023 pipeline was:

    Danish article
      --opus-mt-da-en--> English article
      --t5-news-summarizer--> English summary  (per packed window)
      --opus-mt-en-da--> Danish summary

This module replays that *shape* on the Vesterklit gazette:

* **oracle hops** use the gold parallel sentences (upper bound if
  translation were perfect and the summarizer only dropped sentences)
* **gloss hops** use the closed-world word list (lower bound / degraded)

The extractive hop is lead-k on the English side, optionally one lead
sentence from each packed window — the closest laptop analogue of
``summary.py``, which summarised each window and concatenated the
results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .lexicon import GlossResult, gloss_danish_to_english, gloss_english_to_danish
from .packing import PackedWindow, pack_article, window_texts
from .sentences import first_sentences, split_sentences


@dataclass
class HopRecord:
    article_id: str
    danish_source: str
    english_oracle: str
    english_gloss: str
    gloss_unknown_da: List[str]
    gloss_coverage_da: float
    windows: List[PackedWindow]
    english_summary_oracle: str
    english_summary_gloss: str
    danish_back_oracle: str
    danish_back_gloss: str
    gloss_unknown_en: List[str]
    gloss_coverage_en: float
    gold_da_summary: str
    gold_en_summary: str

    def hop_pairs(self) -> List[tuple[str, str]]:
        return [
            ("da_source", self.danish_source),
            ("en_oracle", self.english_oracle),
            ("en_gloss", self.english_gloss),
            ("en_summary_oracle", self.english_summary_oracle),
            ("en_summary_gloss", self.english_summary_gloss),
            ("da_back_oracle", self.danish_back_oracle),
            ("da_back_gloss", self.danish_back_gloss),
            ("gold_da_summary", self.gold_da_summary),
        ]


def _join_aligned(sentences: Sequence[str]) -> str:
    return " ".join(s.strip() for s in sentences if s and s.strip())


def extractive_from_windows(
    windows: Sequence[PackedWindow],
    per_window: int = 1,
) -> str:
    """Take the first ``per_window`` sentences of each packed window."""
    if per_window <= 0:
        return ""
    pieces: List[str] = []
    for window in windows:
        pieces.extend(window.sentences[:per_window])
    return " ".join(pieces)


def extractive_lead(text: str, k: int = 2) -> str:
    return first_sentences(text, k)


def run_hops(
    article_id: str,
    danish_sentences: Sequence[str],
    english_sentences: Sequence[str],
    gold_da_summary: str,
    gold_en_summary: str,
    lead_k: int = 2,
    per_window: int = 1,
    pack_budget: int = 40,
) -> HopRecord:
    """Run oracle + gloss hops for one aligned article.

    ``pack_budget`` is in *word* tokens. The gazette articles are short,
    so a small budget (default 40) is what actually produces multiple
    windows. The 2023 scripts used 460 subword pieces; that would pack
    each sample story into a single window and hide the algorithm.
    """
    if len(danish_sentences) != len(english_sentences):
        raise ValueError(
            f"{article_id}: danish/english sentence counts differ "
            f"({len(danish_sentences)} vs {len(english_sentences)})"
        )

    danish_source = _join_aligned(danish_sentences)
    english_oracle = _join_aligned(english_sentences)

    gloss_fwd: GlossResult = gloss_danish_to_english(danish_source)
    windows = pack_article(english_oracle, text_max_length=pack_budget)

    # Oracle extractive: lead-k of the gold English, plus one sentence
    # per packed window (union, order-preserving).
    lead = extractive_lead(english_oracle, lead_k)
    from_windows = extractive_from_windows(windows, per_window=per_window)
    english_summary_oracle = _unique_sentence_union(lead, from_windows)

    # Gloss extractive: same algorithm on the glossed English.
    gloss_windows = pack_article(gloss_fwd.text, text_max_length=pack_budget)
    gloss_lead = extractive_lead(gloss_fwd.text, lead_k)
    gloss_from_windows = extractive_from_windows(gloss_windows, per_window=per_window)
    english_summary_gloss = _unique_sentence_union(gloss_lead, gloss_from_windows)

    # Back-translation: oracle uses the reverse gold alignment for those
    # English sentences that still exist; gloss uses the word list.
    danish_back_oracle = _oracle_backtranslate(
        english_summary_oracle, english_sentences, danish_sentences
    )
    back_gloss = gloss_english_to_danish(english_summary_gloss)

    return HopRecord(
        article_id=article_id,
        danish_source=danish_source,
        english_oracle=english_oracle,
        english_gloss=gloss_fwd.text,
        gloss_unknown_da=sorted(set(gloss_fwd.unknown)),
        gloss_coverage_da=gloss_fwd.coverage,
        windows=windows,
        english_summary_oracle=english_summary_oracle,
        english_summary_gloss=english_summary_gloss,
        danish_back_oracle=danish_back_oracle,
        danish_back_gloss=back_gloss.text,
        gloss_unknown_en=sorted(set(back_gloss.unknown)),
        gloss_coverage_en=back_gloss.coverage,
        gold_da_summary=gold_da_summary,
        gold_en_summary=gold_en_summary,
    )


def _unique_sentence_union(*blobs: str) -> str:
    seen = set()
    out: List[str] = []
    for blob in blobs:
        for sent in split_sentences(blob):
            key = sent.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(sent)
    return " ".join(out)


def _oracle_backtranslate(
    english_summary: str,
    english_sentences: Sequence[str],
    danish_sentences: Sequence[str],
) -> str:
    """Map selected English sentences back via the gold alignment.

    Matching is exact after strip+casefold. Sentences the extractive hop
    invented (should not happen on oracle) are left in English so the
    ledger can show them as attrition, not silently drop them.
    """
    table = {en.strip().casefold(): da for en, da in zip(english_sentences, danish_sentences)}
    out: List[str] = []
    for sent in split_sentences(english_summary):
        hit = table.get(sent.strip().casefold())
        out.append(hit if hit is not None else sent)
    return " ".join(out)


def pack_danish_source(danish_source: str, pack_budget: int = 40) -> List[PackedWindow]:
    return pack_article(danish_source, text_max_length=pack_budget)
