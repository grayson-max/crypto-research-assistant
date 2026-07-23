"""Deliver a finished brief to iCloud Drive so it syncs to the user's phone,
and fire a native macOS notification. No credentials required — relies on
iCloud Drive already being signed in on the Mac running the pipeline.

Builds a styled HTML report: a KPI row of per-coin stat tiles (price,
24h/7d/30d change, market cap + dominance, volume, supply, distance from
ATH, 7-day sparkline), a Fear & Greed gauge, and the AI-written narrative
— instead of just rendering the raw Markdown. Colors follow the project's
validated palette (see the dataviz design skill): status tokens for the
Fear & Greed gauge, a fixed up/down pair for every delta field, muted gray
for de-emphasized chart ink."""

import re
import subprocess
from pathlib import Path

import markdown

ICLOUD_DIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/CryptoBriefs"

COIN_NAMES = {"BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana"}

STYLE = """
<style>
  :root {
    --surface-1: #fcfcfb; --page: #f9f9f7; --text-primary: #0b0b0b;
    --text-secondary: #52514e; --muted: #898781; --gridline: #e1e0d9;
    --border: rgba(11,11,11,0.10);
    --delta-up: #006300; --delta-down: #d03b3b;
    --accent: #2a78d6;
    --status-critical: #d03b3b; --status-serious: #ec835a;
    --status-warning: #fab219; --status-good: #0ca30c;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --surface-1: #1a1a19; --page: #0d0d0d; --text-primary: #ffffff;
      --text-secondary: #c3c2b7; --muted: #898781; --gridline: #2c2c2a;
      --border: rgba(255,255,255,0.10);
      --delta-up: #0ca30c; --delta-down: #e66767;
      --accent: #3987e5;
    }
  }
  * { box-sizing: border-box; }
  body {
    max-width: 720px; margin: 40px auto; padding: 0 20px;
    font-family: -apple-system, "Segoe UI", sans-serif; line-height: 1.6;
    color: var(--text-primary); background: var(--page);
  }
  h1 { font-size: 1.5rem; margin-bottom: 2px; }
  .subtitle { color: var(--text-secondary); margin-top: 0; margin-bottom: 24px; }
  h2 {
    font-size: 1.05rem; color: var(--text-secondary); text-transform: uppercase;
    letter-spacing: 0.03em; border-bottom: 1px solid var(--gridline);
    padding-bottom: 6px; margin-top: 18px;
  }
  .kpi-row { display: flex; gap: 12px; flex-wrap: wrap; }
  .tile {
    flex: 1 1 200px; background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 16px;
  }
  .tile .label { font-weight: 600; font-size: 0.95rem; }
  .tile .name { color: var(--muted); font-size: 0.8rem; margin-left: 4px; }
  .tile .value { font-size: 1.4rem; font-weight: 600; margin: 4px 0 2px; }
  .tile .delta { font-weight: 600; font-size: 0.9rem; }
  .tile .facts { margin-top: 8px; border-top: 1px solid var(--gridline); padding-top: 6px; }
  .fact { display: flex; justify-content: space-between; gap: 8px; font-size: 0.74rem; padding: 1.5px 0; }
  .fact-label { color: var(--muted); white-space: nowrap; }
  .fact-value { color: var(--text-secondary); font-weight: 500; text-align: right; }
  .tile .spark { margin-top: 8px; display: block; }

  .gauge-card {
    background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 16px; margin-top: 12px;
  }
  .gauge-label { font-weight: 600; }
  .gauge-value { color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 8px; }
  .gauge-track {
    position: relative; height: 10px; border-radius: 5px;
    background: linear-gradient(to right,
      var(--status-critical) 0%, var(--status-serious) 25%,
      var(--status-warning) 50%, var(--status-good) 75%, var(--status-good) 100%);
  }
  .gauge-marker {
    position: absolute; top: -3px; width: 3px; height: 16px;
    background: var(--text-primary); border-radius: 2px;
    box-shadow: 0 0 0 2px var(--surface-1);
  }
  .gauge-scale { display: flex; justify-content: space-between; color: var(--muted); font-size: 0.7rem; margin-top: 4px; }

  .prose { margin-top: 28px; }
  .prose p { margin: 10px 0; }
  .prose ul { margin: 0 0 10px; padding-left: 20px; }
  .prose strong { color: var(--text-primary); }
  hr { border: none; margin: 0; }

  .disclaimer { color: var(--muted); font-size: 0.7rem; font-style: italic; margin-top: 24px; }
</style>
"""


def _compact_usd(n: float) -> str:
    """1,340,000,000,000 -> $1.34T. Keeps large stat-tile numbers readable."""
    for suffix, divisor in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(n) >= divisor:
            return f"${n / divisor:,.2f}{suffix}"
    return f"${n:,.2f}"


def _compact_num(n: float) -> str:
    """Same compacting as _compact_usd but without the $ — for supply counts."""
    for suffix, divisor in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(n) >= divisor:
            return f"{n / divisor:,.2f}{suffix}"
    return f"{n:,.0f}"


def _pct_span(value: float) -> str:
    """Signed percentage, colored green/red by sign — used for every delta
    field (24h/7d/30d/ATH distance) so direction reads at a glance."""
    color = "var(--delta-up)" if value >= 0 else "var(--delta-down)"
    return f'<span style="color:{color}">{value:+.2f}%</span>'


def _fact_row(label: str, value_html: str) -> str:
    return f'<div class="fact"><span class="fact-label">{label}</span><span class="fact-value">{value_html}</span></div>'


def _sparkline_svg(prices: list[float], up: bool) -> str:
    """A 12-point-style inline trend line: muted gray body, colored endpoint
    dot for the current direction (green if the week is up, red if down)."""
    if len(prices) < 2:
        return ""

    width, height, pad = 64, 20, 3
    lo, hi = min(prices), max(prices)
    span = (hi - lo) or 1  # avoid divide-by-zero on a flat week

    points = []
    for i, price in enumerate(prices):
        x = pad + (i / (len(prices) - 1)) * (width - 2 * pad)
        y = height - pad - ((price - lo) / span) * (height - 2 * pad)
        points.append((x, y))

    color = "var(--delta-up)" if up else "var(--delta-down)"
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    last_x, last_y = points[-1]

    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<polyline points="{path}" fill="none" stroke="var(--muted)" '
        f'stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="2.5" fill="{color}"/>'
        f"</svg>"
    )


def _stat_tile(symbol: str, data: dict, dominance_pct: float | None) -> str:
    change = data["change_24h"]
    up = change >= 0
    delta_color = "var(--delta-up)" if up else "var(--delta-down)"
    arrow = "▲" if up else "▼"

    dominance_str = f" &middot; {dominance_pct:.1f}% dominance" if dominance_pct is not None else ""

    if data["max_supply"]:
        supply_str = f"{_compact_num(data['circulating_supply'])} / {_compact_num(data['max_supply'])}"
    else:
        supply_str = f"{_compact_num(data['circulating_supply'])} (no cap)"

    facts = "".join(
        [
            _fact_row("7d / 30d", f"{_pct_span(data['change_7d'])} / {_pct_span(data['change_30d'])}"),
            _fact_row("Mkt cap", f"{_compact_usd(data['market_cap'])} &middot; #{data['market_cap_rank']}{dominance_str}"),
            _fact_row("Volume (24h)", _compact_usd(data["volume_24h"])),
            _fact_row("Supply", supply_str),
            _fact_row("From ATH", _pct_span(data["ath_change_percentage"])),
        ]
    )

    return f"""
    <div class="tile">
      <span class="label">{symbol}</span><span class="name">{COIN_NAMES.get(symbol, "")}</span>
      <div class="value">${data['price']:,.2f}</div>
      <div class="delta" style="color: {delta_color}">{arrow} {change:+.2f}% (24h)</div>
      <div class="facts">{facts}</div>
      <div class="spark">{_sparkline_svg(data['sparkline_7d'], up)}</div>
    </div>
    """


def _fear_greed_gauge(fear_greed: dict) -> str:
    value = fear_greed["value"]
    classification = fear_greed["classification"]
    return f"""
    <div class="gauge-card">
      <div class="gauge-label">Fear &amp; Greed Index</div>
      <div class="gauge-value">{value}/100 — {classification}</div>
      <div class="gauge-track">
        <div class="gauge-marker" style="left: calc({value}% - 1.5px)"></div>
      </div>
      <div class="gauge-scale"><span>Extreme Fear</span><span>Neutral</span><span>Extreme Greed</span></div>
    </div>
    """


def render_html(
    brief_md: str,
    market_data: dict,
    dominance: dict,
    fear_greed: dict,
    report_date: str,
) -> str:
    """Assemble the full styled report: KPI row, gauge, and AI-written prose
    (as HTML) — the disclaimer paragraph already embedded in brief_md rides
    along inside the prose section."""
    tiles = "".join(
        _stat_tile(symbol, data, dominance.get(symbol))
        for symbol, data in market_data.items()
        if data is not None
    )

    # The page already has its own <h1> above; drop the brief's own
    # "# Daily Crypto Market Brief" heading so it doesn't repeat below.
    body_md = re.sub(r"^#\s+.*\n+", "", brief_md, count=1)

    # Pull the trailing compliance disclaimer out of the prose so it can be
    # rendered smaller/italic instead of as a bolded paragraph.
    disclaimer_match = re.search(r"\n+---\n\*\*(.+?)\*\*\s*$", body_md, re.DOTALL)
    disclaimer_html = ""
    if disclaimer_match:
        body_md = body_md[: disclaimer_match.start()]
        disclaimer_html = f'<p class="disclaimer">{disclaimer_match.group(1)}</p>'

    prose_html = markdown.markdown(body_md)

    return f"""<html><head><meta charset="utf-8">{STYLE}</head><body>
      <h1>Daily Crypto Research Brief</h1>
      <p class="subtitle">{report_date}</p>

      <div class="kpi-row">{tiles}</div>
      {_fear_greed_gauge(fear_greed)}

      <div class="prose">{prose_html}</div>
      {disclaimer_html}
    </body></html>"""


def deliver_to_icloud(
    brief_md: str,
    filename_stem: str,
    market_data: dict,
    dominance: dict,
    fear_greed: dict,
    report_date: str,
) -> Path:
    """Render the full styled report and save it into the iCloud Drive
    folder, which syncs to any of the user's other Apple devices."""
    ICLOUD_DIR.mkdir(parents=True, exist_ok=True)
    html = render_html(brief_md, market_data, dominance, fear_greed, report_date)
    html_path = ICLOUD_DIR / f"{filename_stem}.html"
    html_path.write_text(html)
    return html_path


def notify_done(message: str) -> None:
    """Show a native macOS notification. Fails silently if there's no GUI session."""
    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{message}" with title "Crypto Research Brief Ready"',
        ],
        check=False,
        capture_output=True,
    )
