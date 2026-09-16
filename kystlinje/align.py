"""ASCII / HTML alignment of tokens that survive from source to silver."""

from __future__ import annotations

from .corpus import Brief
from .danish import content_tokens, normalize
from .entities import Entity, entity_survives
from .ledger import HopLedger, build_ledger


def _token_hits(token: str, other_text: str) -> bool:
    if not token:
        return False
    folded = normalize(other_text)
    needle = normalize(token)
    if len(needle) <= 2:
        return False
    return needle in folded


def render_alignment(brief: Brief, *, hop: str = "silver") -> str:
    """Mark source tokens that still occur in *hop* with [brackets]."""
    ledger = build_ledger(brief)
    hop_text = ledger.texts()[hop]
    pieces: list[str] = []
    for token in content_tokens(brief.body_da):
        if _token_hits(token, hop_text):
            pieces.append(f"[{token}]")
        else:
            pieces.append(token)
    return " ".join(pieces)


def surviving_entities(ledger: HopLedger, hop: str) -> list[Entity]:
    return [row.entity for row in ledger.rows if row.survived(hop)]


def lost_entities(ledger: HopLedger, hop: str) -> list[Entity]:
    return [row.entity for row in ledger.rows if not row.survived(hop)]


def html_source_spans(brief: Brief, hop: str = "silver") -> str:
    """Wrap surviving source entities in <mark> for the HTML report."""
    ledger = build_ledger(brief)
    text = brief.body_da
    spans: list[tuple[int, int, bool]] = []
    for row in ledger.rows:
        span = row.entity.span
        if not span:
            continue
        spans.append((span[0], span[1], row.survived(hop)))
    spans.sort(key=lambda item: (item[0], -item[1]))
    # Greedy non-overlapping, longest first at a position.
    kept: list[tuple[int, int, bool]] = []
    cursor = 0
    for start, end, ok in spans:
        if start < cursor:
            continue
        kept.append((start, end, ok))
        cursor = end
    out: list[str] = []
    last = 0
    for start, end, ok in kept:
        out.append(_esc(text[last:start]))
        css = "kept" if ok else "lost"
        out.append(f'<mark class="{css}">{_esc(text[start:end])}</mark>')
        last = end
    out.append(_esc(text[last:]))
    return "".join(out)


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
