"""Self-contained HTML lab report for the fictional corpus."""

from __future__ import annotations

import html
from pathlib import Path

from .baselines import run_all_baselines
from .catalog import items_for_article, load_catalog
from .fiction import load_briefs
from .rouge import mean_scores, score_pair
from .rubric import score_rubric
from .sentences import split_sentences

CSS = """
:root {
  --ink: #1c1917;
  --paper: #f6f1e7;
  --card: #fffaf1;
  --rule: #d6c7b2;
  --accent: #9a3412;
  --muted: #57534e;
  --good: #166534;
  --mid: #a16207;
  --bad: #9f1239;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  background: var(--paper);
  color: var(--ink);
  line-height: 1.5;
}
header {
  padding: 2.4rem 8vw 1.4rem;
  border-bottom: 1px solid var(--rule);
}
header p { max-width: 46rem; color: var(--muted); }
h1, h2, h3 { font-weight: 650; letter-spacing: -0.02em; }
main { padding: 1.5rem 8vw 4rem; }
section { margin: 2.4rem 0; }
table { border-collapse: collapse; width: 100%; font-size: 0.92rem; }
th, td { border-bottom: 1px solid var(--rule); padding: 0.45rem 0.55rem; text-align: left; vertical-align: top; }
th { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }
.card {
  background: var(--card);
  border: 1px solid var(--rule);
  border-radius: 10px;
  padding: 1rem 1.1rem 1.15rem;
  margin: 0.9rem 0;
}
.muted { color: var(--muted); }
.kicker { font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent); }
.score-hi { color: var(--good); font-variant-numeric: tabular-nums; }
.score-mid { color: var(--mid); font-variant-numeric: tabular-nums; }
.score-lo { color: var(--bad); font-variant-numeric: tabular-nums; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: 0.8rem; }
nav a { color: var(--accent); margin-right: 1rem; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.88em; }
"""


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _score_class(value: float) -> str:
    if value >= 0.55:
        return "score-hi"
    if value >= 0.30:
        return "score-mid"
    return "score-lo"


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def build_report_html() -> str:
    briefs = load_briefs()
    catalog = load_catalog()
    per_baseline: dict[str, list[dict[str, float]]] = {}
    article_blocks: list[str] = []

    for brief in briefs:
        results = run_all_baselines(brief.article_text, brief.title)
        rows = []
        for name, result in results.items():
            metrics = score_pair(result.summary, brief.gold_abstractive)
            per_baseline.setdefault(name, []).append(metrics)
            r1 = metrics["rouge1_fmeasure"]
            rows.append(
                "<tr>"
                f"<td><code>{_esc(name)}</code></td>"
                f"<td class='{_score_class(r1)}'>{_fmt(r1)}</td>"
                f"<td class='{_score_class(metrics['rouge2_fmeasure'])}'>{_fmt(metrics['rouge2_fmeasure'])}</td>"
                f"<td class='{_score_class(metrics['rougeL_fmeasure'])}'>{_fmt(metrics['rougeL_fmeasure'])}</td>"
                f"<td>{_esc(result.summary)}</td>"
                "</tr>"
            )
        rubric = score_rubric(brief.article_text, results["lead2"].summary, brief.gold_abstractive)
        errors = items_for_article(brief.id, catalog)
        error_html = (
            "<ul>"
            + "".join(
                f"<li><code>{_esc(item.id)}</code> "
                f"[{_esc(','.join(item.codes))}] sev={item.severity}: "
                f"{_esc(item.explanation)}</li>"
                for item in errors
            )
            + "</ul>"
            if errors
            else "<p class='muted'>No catalogued hop errors on this brief.</p>"
        )
        article_blocks.append(
            f"<article class='card' id='{_esc(brief.id)}'>"
            f"<div class='kicker'>{_esc(brief.id)} · {_esc(brief.topic)}</div>"
            f"<h3>{_esc(brief.title)}</h3>"
            f"<p>{_esc(brief.article_text)}</p>"
            f"<p><strong>Gold extractive.</strong> {_esc(brief.gold_extractive)}</p>"
            f"<p><strong>Gold abstractive.</strong> {_esc(brief.gold_abstractive)}</p>"
            f"<p class='muted'>Lead-2 rubric mean {rubric.mean:.2f} "
            f"(faith {rubric.faithfulness}, cov {rubric.coverage}, "
            f"flu {rubric.fluency}, conc {rubric.conciseness}, da {rubric.danish_naturalness})</p>"
            "<table><thead><tr><th>Baseline</th><th>R1 F</th><th>R2 F</th><th>RL F</th><th>Summary</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>"
            f"{error_html}"
            "</article>"
        )

    mean_rows = []
    for name, rows in per_baseline.items():
        means = mean_scores(rows)
        mean_rows.append(
            "<tr>"
            f"<td><code>{_esc(name)}</code></td>"
            f"<td class='{_score_class(means['rouge1_fmeasure'])}'>{_fmt(means['rouge1_fmeasure'])}</td>"
            f"<td class='{_score_class(means['rouge2_fmeasure'])}'>{_fmt(means['rouge2_fmeasure'])}</td>"
            f"<td class='{_score_class(means['rougeL_fmeasure'])}'>{_fmt(means['rougeL_fmeasure'])}</td>"
            "</tr>"
        )

    catalog_rows = []
    for item in catalog:
        catalog_rows.append(
            "<tr>"
            f"<td><code>{_esc(item.id)}</code></td>"
            f"<td><a href='#{_esc(item.article_id)}'>{_esc(item.article_id)}</a></td>"
            f"<td>{_esc(', '.join(item.codes))}</td>"
            f"<td>{item.severity}</td>"
            f"<td>{_esc(item.source_span)}</td>"
            f"<td>{_esc(item.silver_span)}</td>"
            f"<td>{_esc(item.explanation)}</td>"
            "</tr>"
        )

    sentence_total = sum(len(split_sentences(brief.article_text)) for brief in briefs)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Silver-label methods lab</title>
  <style>{CSS}</style>
</head>
<body>
  <header>
    <div class="kicker">Personal lab · ITU ANLP 2023 archive</div>
    <h1>Silver-label methods lab</h1>
    <p>
      Sixteen original fictional Danish briefs, five extractive baselines, a from-scratch
      ROUGE, and a hop-error catalog. No GPU, no 10k dump, no invented 2023 scoreboard.
      Gold abstractive sentences are hand-written rewrites; gold extractive sentences are
      copied from the article so a lead baseline has something honest to chase.
    </p>
    <nav>
      <a href="#means">Mean table</a>
      <a href="#articles">Articles</a>
      <a href="#catalog">Error catalog</a>
    </nav>
  </header>
  <main>
    <section>
      <div class="grid">
        <div class="card"><div class="kicker">Briefs</div><h2>{len(briefs)}</h2><p class="muted">fictional, lab-* ids</p></div>
        <div class="card"><div class="kicker">Sentences</div><h2>{sentence_total}</h2><p class="muted">Danish-aware splitter</p></div>
        <div class="card"><div class="kicker">Catalog items</div><h2>{len(catalog)}</h2><p class="muted">typed hop errors</p></div>
      </div>
    </section>
    <section id="means">
      <h2>Mean ROUGE against gold abstractive</h2>
      <p class="muted">These numbers describe the fiction corpus only. They are not the missing 2023 mT5 scores.</p>
      <table>
        <thead><tr><th>Baseline</th><th>ROUGE-1 F</th><th>ROUGE-2 F</th><th>ROUGE-L F</th></tr></thead>
        <tbody>{''.join(mean_rows)}</tbody>
      </table>
    </section>
    <section id="articles">
      <h2>Articles and per-brief scores</h2>
      {''.join(article_blocks)}
    </section>
    <section id="catalog">
      <h2>Hop-error catalog</h2>
      <p class="muted">Invented teacher mistakes, anchored on spans that actually occur in the briefs.</p>
      <table>
        <thead><tr><th>Id</th><th>Article</th><th>Codes</th><th>Sev</th><th>Source</th><th>Silver</th><th>Why</th></tr></thead>
        <tbody>{''.join(catalog_rows)}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def write_report(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_report_html(), encoding="utf-8")
    return path
