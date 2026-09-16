"""Offline HTML atlas of packing panes for the Toftevig fixtures."""

from __future__ import annotations

import html
from pathlib import Path

from pakhus.concat import rouge_l
from pakhus.hops import Cascade, run_corpus
from pakhus.paths import REPORT_DIR
from pakhus.packing import ascii_atlas

_CSS = """
:root { --ink: #1b1b18; --paper: #f6f1e4; --rule: #cbbf9a; --pane: #2f5d50; --warn: #8b3a2a; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Iowan Old Style", Palatino, Georgia, serif; background: var(--paper); color: var(--ink); }
header { padding: 2rem 8vw 1rem; border-bottom: 1px solid var(--rule); }
header h1 { margin: 0 0 .3rem; font-size: 1.8rem; letter-spacing: .02em; }
header p { margin: 0; max-width: 46rem; line-height: 1.45; }
main { padding: 1.5rem 8vw 4rem; }
article { margin: 2rem 0 3rem; }
article h2 { margin: 0 0 .4rem; font-size: 1.25rem; }
.meta { color: #4a463a; font-size: .92rem; margin-bottom: 1rem; }
.panes { display: grid; gap: .45rem; margin: .6rem 0 1rem; }
.row { display: grid; grid-template-columns: 4.5rem 1fr 11rem; gap: .6rem; align-items: center; font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .82rem; }
.bar { height: 1.05rem; background: #e4dcc6; border-radius: 2px; overflow: hidden; }
.bar > span { display: block; height: 100%; background: var(--pane); }
.bar.over > span { background: var(--warn); width: 100% !important; }
.bar.empty { outline: 1px dashed var(--warn); }
pre { background: #efe8d4; padding: .8rem 1rem; overflow: auto; font-size: .78rem; line-height: 1.4; }
.silver { border-left: 3px solid var(--pane); padding: .2rem 0 .2rem 1rem; max-width: 46rem; }
table { border-collapse: collapse; font-size: .9rem; margin: 1rem 0 2rem; }
th, td { border-bottom: 1px solid var(--rule); text-align: left; padding: .35rem .7rem .35rem 0; }
.flag { color: var(--warn); font-weight: 600; }
"""


def _bar(ratio: float, over: bool, empty: bool) -> str:
    pct = 0 if empty else min(100, max(0, round(ratio * 100)))
    classes = "bar"
    if over:
        classes += " over"
    if empty:
        classes += " empty"
    return f'<div class="{classes}"><span style="width:{pct}%"></span></div>'


def _article_html(row) -> str:
    article = row.article
    concat = row.concat
    flags = []
    if concat.would_truncate_at_128:
        flags.append("would truncate @128")
    if concat.echo_names:
        flags.append("echo " + ", ".join(concat.echo_names))
    flag_html = f'<span class="flag">{" · ".join(flags)}</span>' if flags else ""
    hop1_rows = []
    for pane in row.hop1.panes:
        hop1_rows.append(
            "<div class='row'>"
            f"<div>p{pane.pane_id:02d}</div>"
            f"{_bar(pane.fill_ratio, pane.over_budget, pane.empty)}"
            f"<div>{pane.unit_sum}/{pane.budget} · {pane.n_sentences} sents"
            f"{' · EMPTY' if pane.empty else ''}{' · OVER' if pane.over_budget else ''}{' · leftover' if pane.fill_ratio < 0.4 else ''}"
            "</div></div>"
        )
    rouge = rouge_l(row.danish_silver, article.oracle_summary_da)
    return f"""
<article id="{html.escape(article.id)}">
  <h2>{html.escape(article.id)} — {html.escape(article.title_da)}</h2>
  <p class="meta">split={html.escape(article.split)} · planted={html.escape(", ".join(article.planted))}
  · hop1 panes={row.hop1.n_panes} · hop2 panes={row.hop2.n_panes}
  · silver units={concat.silver_units} · pane0 share={concat.pane0_share:.2f}
  · figure survival={concat.figure_survival:.2f} · oracle ROUGE-L={rouge:.2f}
  {flag_html}</p>
  <h3>Hop 1 panes (Danish packing)</h3>
  <div class="panes">{''.join(hop1_rows)}</div>
  <h3>ASCII atlas</h3>
  <pre>{html.escape(ascii_atlas(row.hop1, article.id) + "\n\n" + ascii_atlas(row.hop2, article.id))}</pre>
  <h3>Silver-sim (concatenated pane briefs, back to Danish)</h3>
  <p class="silver">{html.escape(row.danish_silver)}</p>
  <h3>Oracle brief</h3>
  <p class="silver">{html.escape(article.oracle_summary_da)}</p>
</article>
"""


def render_html(cascade: Cascade | None = None) -> str:
    cascade = cascade or run_corpus()
    body = "\n".join(_article_html(row) for row in cascade.rows)
    rows = "".join(
        "<tr>"
        f"<td><a href='#{html.escape(r.article.id)}'>{html.escape(r.article.id)}</a></td>"
        f"<td>{r.hop1.n_panes}</td><td>{r.hop2.n_panes}</td>"
        f"<td>{r.concat.silver_units}</td>"
        f"<td>{'yes' if r.concat.would_truncate_at_128 else 'no'}</td>"
        f"<td>{r.concat.pane0_share:.2f}</td>"
        f"<td>{r.concat.figure_survival:.2f}</td>"
        "</tr>"
        for r in cascade.rows
    )
    return f"""<!DOCTYPE html>
<html lang="da">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Pakhuset — Toftevig window atlas</title>
  <style>{_CSS}</style>
</head>
<body>
<header>
  <h1>Pakhuset</h1>
  <p>CPU atlas of the 2023 Danish news silver-label packing house.
  Each bar is one window. The original course scripts are not run here;
  Toftevig copy is fictional and sentence-aligned so hop-2 repacking is
  visible without OPUS-MT or T5.</p>
</header>
<main>
  <table>
    <thead><tr><th>id</th><th>hop1 panes</th><th>hop2 panes</th><th>silver units</th><th>trunc @128</th><th>pane0 share</th><th>figure survival</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  {body}
</main>
</body>
</html>
"""


def write_report(directory: Path | None = None, cascade: Cascade | None = None) -> Path:
    directory = directory or REPORT_DIR
    directory.mkdir(parents=True, exist_ok=True)
    cascade = cascade or run_corpus()
    path = directory / "index.html"
    path.write_text(render_html(cascade), encoding="utf-8")
    text_path = directory / "atlas.txt"
    text_path.write_text(
        "\n\n".join(
            ascii_atlas(r.hop1, r.article.id) + "\n" + ascii_atlas(r.hop2, r.article.id)
            for r in cascade.rows
        )
        + "\n",
        encoding="utf-8",
    )
    return path
