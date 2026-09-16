"""Plain-text and single-file HTML lab reports for the gazette hops."""

from __future__ import annotations

import html
from typing import Iterable, List, Sequence

from .corpus import GazetteArticle
from .hops import HopRecord
from .ledger import LedgerRow, summarise_ledger
from .metrics import rouge_scores


def _bar(value: float, width: int = 20) -> str:
    value = max(0.0, min(1.0, value))
    filled = int(round(value * width))
    return "█" * filled + "░" * (width - filled)


def render_text(
    records: Sequence[HopRecord],
    articles: Sequence[GazetteArticle],
    ledger_rows: Sequence[LedgerRow],
) -> str:
    by_id = {art.article_id: art for art in articles}
    summary = summarise_ledger(ledger_rows)
    lines: List[str] = []
    lines.append("Fjordpressen lab notes — Vesterklit gazette")
    lines.append("=" * 52)
    lines.append("")
    lines.append("Closed-world bounds on the 2023 four-hop silver label.")
    lines.append("Oracle = gold parallel sentences + extractive keep.")
    lines.append("Gloss  = word-list DA↔EN + extractive keep.")
    lines.append("")
    lines.append("Corpus means")
    lines.append("-" * 52)
    for key, label in (
        ("oracle_entity_retention", "oracle entity retention"),
        ("gloss_entity_retention", "gloss entity retention"),
        ("oracle_rouge1", "oracle ROUGE-1 vs gold DA"),
        ("gloss_rouge1", "gloss ROUGE-1 vs gold DA"),
        ("oracle_rougeL", "oracle ROUGE-L vs gold DA"),
        ("gloss_rougeL", "gloss ROUGE-L vs gold DA"),
        ("oracle_compression", "oracle compression"),
        ("gloss_compression", "gloss compression"),
    ):
        val = summary[key]
        lines.append(f"  {_bar(val)} {val:5.3f}  {label}")
    lines.append("")

    for record in records:
        art = by_id[record.article_id]
        lines.append(f"## {record.article_id} — {art.title_da}")
        lines.append(f"section: {art.section}")
        lines.append(f"windows: {len(record.windows)}  "
                     f"gloss DA coverage: {record.gloss_coverage_da:.3f}")
        if record.gloss_unknown_da:
            preview = ", ".join(record.gloss_unknown_da[:8])
            more = "" if len(record.gloss_unknown_da) <= 8 else "…"
            lines.append(f"OOV DA→EN: {preview}{more}")
        gold_vs_oracle = rouge_scores(record.danish_back_oracle, record.gold_da_summary)
        gold_vs_gloss = rouge_scores(record.danish_back_gloss, record.gold_da_summary)
        lines.append(
            f"back-oracle vs gold  R1={gold_vs_oracle.rouge1:.3f}  RL={gold_vs_oracle.rougeL:.3f}"
        )
        lines.append(
            f"back-gloss  vs gold  R1={gold_vs_gloss.rouge1:.3f}  RL={gold_vs_gloss.rougeL:.3f}"
        )
        lines.append("facts:")
        for fact in art.facts:
            lines.append(f"  - {fact}")
        lines.append("gold DA summary:")
        lines.append(f"  {art.gold_da_summary}")
        lines.append("oracle DA back-translation:")
        lines.append(f"  {record.danish_back_oracle}")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_html(
    records: Sequence[HopRecord],
    articles: Sequence[GazetteArticle],
    ledger_rows: Sequence[LedgerRow],
) -> str:
    by_id = {art.article_id: art for art in articles}
    summary = summarise_ledger(ledger_rows)
    cards = []
    for record in records:
        art = by_id[record.article_id]
        oracle = rouge_scores(record.danish_back_oracle, record.gold_da_summary)
        gloss = rouge_scores(record.danish_back_gloss, record.gold_da_summary)
        oov = ", ".join(html.escape(t) for t in record.gloss_unknown_da[:12])
        facts = "".join(f"<li>{html.escape(f)}</li>" for f in art.facts)
        windows = "".join(
            f"<li><code>w{i}</code> ({w.n_sentences} sents, budget {w.token_budget}) "
            f"{html.escape(w.text[:180])}{'…' if len(w.text) > 180 else ''}</li>"
            for i, w in enumerate(record.windows)
        )
        cards.append(
            f"""
<section class="card">
  <h2>{html.escape(record.article_id)} <span>{html.escape(art.title_da)}</span></h2>
  <p class="meta">{html.escape(art.section)} · {len(record.windows)} windows ·
     gloss coverage {record.gloss_coverage_da:.3f}</p>
  <table>
    <tr><th></th><th>ROUGE-1</th><th>ROUGE-L</th></tr>
    <tr><td>oracle back vs gold</td><td>{oracle.rouge1:.3f}</td><td>{oracle.rougeL:.3f}</td></tr>
    <tr><td>gloss back vs gold</td><td>{gloss.rouge1:.3f}</td><td>{gloss.rougeL:.3f}</td></tr>
  </table>
  <h3>Facts the silver label should keep</h3>
  <ul>{facts}</ul>
  <h3>Packed English windows (oracle)</h3>
  <ol>{windows}</ol>
  <h3>Gold Danish summary</h3>
  <blockquote>{html.escape(art.gold_da_summary)}</blockquote>
  <h3>Oracle Danish back-translation</h3>
  <blockquote>{html.escape(record.danish_back_oracle)}</blockquote>
  <h3>Gloss Danish back-translation</h3>
  <blockquote>{html.escape(record.danish_back_gloss)}</blockquote>
  <p class="oov"><strong>DA→EN OOV</strong> {oov or '— none —'}</p>
</section>
"""
        )

    def metric_row(key: str, label: str) -> str:
        val = summary[key]
        return (
            f"<tr><td>{html.escape(label)}</td>"
            f"<td class='num'>{val:.3f}</td>"
            f"<td class='bar'><span style='width:{val*100:.1f}%'></span></td></tr>"
        )

    metrics = "".join(
        metric_row(k, lab)
        for k, lab in (
            ("oracle_entity_retention", "Oracle entity retention"),
            ("gloss_entity_retention", "Gloss entity retention"),
            ("oracle_rouge1", "Oracle ROUGE-1"),
            ("gloss_rouge1", "Gloss ROUGE-1"),
            ("oracle_rougeL", "Oracle ROUGE-L"),
            ("gloss_rougeL", "Gloss ROUGE-L"),
        )
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Fjordpressen lab notes — Vesterklit gazette</title>
<style>
  :root {{
    --ink: #1b1a17;
    --paper: #f6f1e7;
    --card: #fffdf8;
    --rule: #c8bba4;
    --accent: #6b4f2a;
    --bar: #8a6a3b;
  }}
  html {{ background: var(--paper); color: var(--ink); }}
  body {{
    font-family: "Iowan Old Style", "Palatino Linotype", Palatino, serif;
    max-width: 880px; margin: 2rem auto; padding: 0 1.25rem 4rem;
    line-height: 1.5;
  }}
  h1 {{ font-weight: 600; letter-spacing: -0.02em; }}
  h2 span {{ font-weight: 400; color: var(--accent); }}
  .lede {{ font-size: 1.05rem; }}
  .card {{
    background: var(--card); border: 1px solid var(--rule);
    padding: 1rem 1.2rem; margin: 1.4rem 0; border-radius: 2px;
  }}
  table {{ border-collapse: collapse; width: 100%; margin: 0.6rem 0 1rem; }}
  th, td {{ text-align: left; padding: 0.25rem 0.4rem; border-bottom: 1px solid var(--rule); }}
  td.num {{ font-variant-numeric: tabular-nums; width: 4.5rem; }}
  td.bar span {{
    display: inline-block; height: 0.65rem; background: var(--bar);
    min-width: 2px;
  }}
  blockquote {{
    margin: 0.4rem 0 1rem; padding-left: 0.8rem;
    border-left: 3px solid var(--accent); color: #333;
  }}
  .meta, .oov {{ color: #555; font-size: 0.95rem; }}
  code {{ font-family: "Source Code Pro", "IBM Plex Mono", monospace; font-size: 0.9em; }}
  footer {{ margin-top: 2rem; color: #666; font-size: 0.9rem; }}
</style>
</head>
<body>
<h1>Fjordpressen lab notes</h1>
<p class="lede">A closed-world replay of the 2023 ITU four-hop silver label
on the invented Vesterklit gazette. No model weights are loaded.
<strong>Oracle</strong> hops use the gold parallel.
<strong>Gloss</strong> hops use the word list. The gap between them is the
study-kit stand-in for hop error.</p>
<table>
  <caption>Means across the gazette</caption>
  {metrics}
</table>
{''.join(cards)}
<footer>
  Personal study kit for sapphireran/Danish-News-Summarization.
  All Vesterklit copy is fiction.
</footer>
</body>
</html>
"""


def write_text(path, records, articles, ledger_rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_text(records, articles, ledger_rows), encoding="utf-8")


def write_html(path, records, articles, ledger_rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html(records, articles, ledger_rows), encoding="utf-8")


def iter_unknown_types(records: Iterable[HopRecord]) -> List[str]:
    seen = set()
    out: List[str] = []
    for record in records:
        for tok in record.gloss_unknown_da:
            key = tok.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(tok)
    return out
