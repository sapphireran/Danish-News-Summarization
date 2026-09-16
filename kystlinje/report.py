"""Self-contained HTML workbook: entity telescope + per-brief cards."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .align import html_source_spans, lost_entities, surviving_entities
from .corpus import all_briefs
from .ledger import (
    HOPS,
    HopLedger,
    build_all_ledgers,
    hop_loss_table,
    kind_survival,
    mean_survival,
    worst_end_to_end,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = REPO_ROOT / "examples" / "report" / "index.html"

_KINDS = ("person", "place", "org", "number", "year", "time", "money", "measure", "compound")


def render_report(ledgers: list[HopLedger] | None = None) -> str:
    ledgers = ledgers or build_all_ledgers()
    means = {hop: mean_survival(ledgers, hop) for hop in HOPS}
    worst = worst_end_to_end(ledgers)
    loss = hop_loss_table(ledgers)
    kind_rows = []
    for kind in _KINDS:
        kind_rows.append(
            (kind, *(kind_survival(ledgers, kind, hop) for hop in ("pivot", "summary", "silver", "lead2")))
        )

    cards = "\n".join(_brief_card(led) for led in ledgers)
    return _PAGE.format(
        n=len(ledgers),
        mean_pivot=_pct(means["pivot"]),
        mean_summary=_pct(means["summary"]),
        mean_silver=_pct(means["silver"]),
        mean_lead=_pct(means["lead2"]),
        bars=_telescope_bars(means),
        loss_rows="".join(
            f"<tr><td>{escape(a)} → {escape(b)}</td><td>{value:.2f}</td></tr>" for a, b, value in loss
        ),
        kind_rows="".join(_kind_row(row) for row in kind_rows),
        worst_id=escape(worst.brief.id),
        worst_title=escape(worst.brief.title_da),
        worst_rate=_pct(worst.survival_rate("silver")),
        toc="".join(
            f'<li><a href="#{led.brief.id}">{escape(led.brief.id)} — {escape(led.brief.title_da)}</a></li>'
            for led in ledgers
        ),
        cards=cards,
    )


def write_report(path: Path | None = None) -> Path:
    dest = Path(path) if path else DEFAULT_REPORT
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_report(), encoding="utf-8")
    return dest


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def _telescope_bars(means: dict[str, float]) -> str:
    labels = [
        ("source", "Danish source"),
        ("pivot", "English pivot"),
        ("summary", "English summary"),
        ("silver", "Danish silver"),
        ("lead2", "Lead-2 control"),
    ]
    chunks = []
    for key, label in labels:
        width = max(4, int(round(100 * means[key])))
        chunks.append(
            "<div class='tel-row'>"
            f"<span class='tel-lab'>{escape(label)}</span>"
            f"<span class='tel-track'><span class='tel-bar hop-{key}' style='width:{width}%'></span></span>"
            f"<span class='tel-n'>{_pct(means[key])}</span>"
            "</div>"
        )
    return "\n".join(chunks)


def _kind_row(row: tuple) -> str:
    kind, *vals = row
    cells = "".join(f"<td>{_pct(v)}</td>" for v in vals)
    return f"<tr><td>{escape(str(kind))}</td>{cells}</tr>"


def _brief_card(ledger: HopLedger) -> str:
    brief = ledger.brief
    lost_silver = lost_entities(ledger, "silver")
    kept_silver = surviving_entities(ledger, "silver")
    planted = "".join(
        "<li>"
        f"<code>{escape(err.code)}</code> on <em>{escape(err.hop)}</em>: "
        f"{escape(err.source_span) or '∅'} → {escape(err.drifted_span) or '∅'} "
        f"<span class='note'>{escape(err.note)}</span>"
        "</li>"
        for err in brief.planted
    )
    lost_list = ", ".join(escape(e.surface) for e in lost_silver) or "—"
    kept_list = ", ".join(escape(e.surface) for e in kept_silver) or "—"
    return f"""
<article class="card" id="{escape(brief.id)}">
  <header>
    <p class="kicker">{escape(brief.id)} · {escape(', '.join(brief.themes))}</p>
    <h3>{escape(brief.title_da)}</h3>
    <p class="sub">{escape(brief.title_en)}</p>
  </header>
  <p class="rates">
    pivot {_pct(ledger.survival_rate('pivot'))} ·
    summary {_pct(ledger.survival_rate('summary'))} ·
    silver {_pct(ledger.survival_rate('silver'))} ·
    lead-2 {_pct(ledger.survival_rate('lead2'))}
  </p>
  <h4>Source with silver survival</h4>
  <p class="body">{html_source_spans(brief, 'silver')}</p>
  <div class="two">
    <section>
      <h4>English summary</h4>
      <p>{escape(brief.summary_en)}</p>
    </section>
    <section>
      <h4>Danish silver label</h4>
      <p>{escape(brief.silver_da)}</p>
    </section>
  </div>
  <p><strong>Kept in silver:</strong> {kept_list}</p>
  <p><strong>Lost by silver:</strong> {lost_list}</p>
  <h4>Planted scars</h4>
  <ul class="planted">{planted}</ul>
</article>
"""


_PAGE = """<!DOCTYPE html>
<html lang="da">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kystlinje workbook — entity telescope</title>
<style>
  :root {{
    --ink: #1c2430;
    --paper: #f4efe4;
    --rule: #c9bba3;
    --teal: #2c6f7a;
    --clay: #b5523a;
    --moss: #4d6b3c;
    --kept: #d7ead4;
    --lost: #f3d0c8;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font: 17px/1.5 "Iowan Old Style", "Palatino Linotype", Palatino, serif;
    color: var(--ink);
    background: var(--paper);
  }}
  header.hero, main {{ max-width: 920px; margin: 0 auto; padding: 2.2rem 1.4rem; }}
  header.hero h1 {{
    font-size: 2.2rem;
    letter-spacing: -0.02em;
    margin: 0 0 0.4rem;
  }}
  .kicker {{
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-size: 0.74rem;
    color: var(--teal);
    margin: 0 0 0.6rem;
  }}
  .lede {{ font-size: 1.08rem; }}
  .tel-row {{ display: grid; grid-template-columns: 9.5rem 1fr 4.2rem; gap: 0.6rem; align-items: center; margin: 0.35rem 0; }}
  .tel-lab {{ font-size: 0.88rem; }}
  .tel-track {{ background: #e5dccb; height: 0.85rem; border-radius: 99px; overflow: hidden; }}
  .tel-bar {{ display: block; height: 100%; border-radius: 99px; background: var(--teal); }}
  .tel-bar.hop-source {{ background: var(--ink); }}
  .tel-bar.hop-silver {{ background: var(--clay); }}
  .tel-bar.hop-lead2 {{ background: var(--moss); }}
  .tel-n {{ font-variant-numeric: tabular-nums; font-size: 0.88rem; text-align: right; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; margin: 1rem 0 1.6rem; }}
  th, td {{ border-bottom: 1px solid var(--rule); text-align: left; padding: 0.35rem 0.4rem; }}
  th {{ font-size: 0.76rem; letter-spacing: 0.06em; text-transform: uppercase; }}
  .card {{
    background: #fffaf1;
    border: 1px solid var(--rule);
    padding: 1.2rem 1.3rem 1.4rem;
    margin: 1.4rem 0;
  }}
  .card h3 {{ margin: 0.15rem 0; }}
  .sub {{ margin: 0 0 0.6rem; color: #5c564b; font-style: italic; }}
  .rates {{ font-variant-numeric: tabular-nums; color: var(--teal); }}
  .two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
  @media (max-width: 720px) {{ .two {{ grid-template-columns: 1fr; }} .tel-row {{ grid-template-columns: 1fr; }} }}
  mark.kept {{ background: var(--kept); padding: 0 0.12em; }}
  mark.lost {{ background: var(--lost); padding: 0 0.12em; text-decoration: underline wavy var(--clay); }}
  .body {{ font-size: 1.02rem; }}
  .planted {{ padding-left: 1.1rem; }}
  .note {{ color: #5c564b; }}
  a {{ color: var(--teal); }}
  footer {{ max-width: 920px; margin: 0 auto; padding: 0 1.4rem 3rem; color: #5c564b; font-size: 0.88rem; }}
</style>
</head>
<body>
<header class="hero">
  <p class="kicker">Personal coursebook · ITU ANLP/DL 2023</p>
  <h1>Kystlinje entity telescope</h1>
  <p class="lede">
    Eighteen original magazine briefs about a fictional island chain.
    Each row is a handwritten stand-in for Danish → English → English summary → Danish
    silver label. Bars show what fraction of <em>source</em> entities still appear
    after each hop. Nothing here is a 2023 mT5 score.
  </p>
  <p>Corpus size: {n} briefs. Worst end-to-end survival:
     <a href="#{worst_id}">{worst_id}</a> ({worst_title}) at {worst_rate}.</p>
  {bars}
  <h2>Average entities lost per hop</h2>
  <table>
    <thead><tr><th>Hop</th><th>Mean entities lost</th></tr></thead>
    <tbody>{loss_rows}</tbody>
  </table>
  <h2>Survival by entity kind (source → hop)</h2>
  <table>
    <thead><tr><th>Kind</th><th>Pivot</th><th>Summary</th><th>Silver</th><th>Lead-2</th></tr></thead>
    <tbody>{kind_rows}</tbody>
  </table>
  <h2>Briefs</h2>
  <ol>{toc}</ol>
</header>
<main>
{cards}
</main>
<footer>
  Fiction only. Not the private 10k dump, not Nordjylland-News copy, not employer code.
  Rebuild with <code>python3 -m kystlinje report</code>.
</footer>
</body>
</html>
"""
