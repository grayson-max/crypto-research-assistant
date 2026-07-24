"""Best-effort verification pass over a generated brief: cross-checks every
number mentioned in the AI-written text against the source data it was built
from, and flags words that don't look like real English or known crypto/
finance terms. Catches LLM hallucinations (wrong price, wrong %) and typos
before delivery. Never blocks delivery — issues are surfaced as a warning
section appended to the brief instead (see main.py)."""

import re

from spellchecker import SpellChecker

SUFFIX_MULTIPLIERS = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000, "T": 1_000_000_000_000}

DOLLAR_RE = re.compile(r"\$([\d,]+(?:\.\d+)?)\s*([KMBT])?", re.IGNORECASE)
PERCENT_RE = re.compile(r"[+-]?\d+(?:\.\d+)?%")

# Words a general English dictionary won't know. Extend as new jargon shows
# up in verify_spelling's output — false positives here are just noise, not
# bugs, since this check never blocks delivery.
KNOWN_TERMS = {
    "btc", "eth", "sol", "bitcoin", "ethereum", "solana", "coingecko",
    "ria", "defi", "altcoin", "altcoins", "staking", "staked", "unstaked",
    "onchain", "stablecoin", "stablecoins", "etf", "etfs", "dominance",
    "sentiment", "crypto", "fomc", "sec", "cpi", "rebound", "selloff",
    "outflows", "inflows", "whale", "whales", "hodl", "hodler", "hodlers",
    "airdrop", "airdrops", "tokenomics", "rollup", "rollups", "custodial",
    "noncustodial", "liquidity", "orderbook", "spot", "perp", "perps",
    "L1", "L2", "layer1", "layer2", "ath", "atl", "bullish", "bearish",
    "api", "tokenized", "tokenization", "memecoin", "memecoins", "intraday",
    "timeframes", "timeframe", "drawdown", "drawdowns",
}


def _expected_numbers(market_data: dict, dominance: dict, fear_greed: dict) -> list[float]:
    """Flatten every numeric field the brief was generated from into one list
    to check mentioned numbers against."""
    values = []
    for data in market_data.values():
        if data is None:
            continue
        for key in (
            "price", "change_24h", "change_7d", "change_30d",
            "market_cap", "volume_24h", "ath_change_percentage",
        ):
            if data.get(key) is not None:
                values.append(float(data[key]))
    values.extend(float(v) for v in dominance.values() if v is not None)
    values.append(float(fear_greed["value"]))
    return values


def _parse_dollar(raw: str, suffix: str | None) -> float:
    value = float(raw.replace(",", ""))
    if suffix:
        value *= SUFFIX_MULTIPLIERS[suffix.upper()]
    return value


def _has_match(value: float, expected: list[float]) -> bool:
    """True if `value` is close to something in `expected` — a fixed
    absolute tolerance handles rounding on small percentages, a relative
    tolerance handles rounding on large dollar figures."""
    return any(abs(value - exp) <= max(0.05, abs(exp) * 0.01) for exp in expected)


def _figure_candidates(match: re.Match, is_percent: bool) -> list[float]:
    """The numeric value(s) a regex match could represent — a bare percentage
    with no explicit sign could be either, since prose often states a change
    as an unsigned magnitude with direction implied by a nearby word
    ("down 1.0%", "off 1.3%")."""
    if is_percent:
        value = float(match.group(0).rstrip("%"))
        return [value] if match.group(0)[0] in "+-" else [value, -value]
    return [_parse_dollar(match.group(1), match.group(2))]


def _headline_source(candidates: list[float], headlines: list[dict]) -> str | None:
    """Return the source name of the first headline whose own text quotes a
    number matching one of `candidates` — i.e. this figure was pulled from
    that article, not invented, even though it isn't in our fetched market
    data. Matching is tight (0.5%) since a quoted figure should reproduce
    exactly, unlike rounded price/percent data."""
    for item in headlines:
        headline_text = item.get("headline") or ""
        found = [
            _parse_dollar(m.group(1), m.group(2)) for m in DOLLAR_RE.finditer(headline_text)
        ] + [
            float(m.group(0).rstrip("%")) for m in PERCENT_RE.finditer(headline_text)
        ]
        if any(abs(v - f) <= max(0.01, abs(f) * 0.005) for v in candidates for f in found):
            return item.get("source")
    return None


def annotate_and_verify_numbers(
    brief_text: str, market_data: dict, dominance: dict, fear_greed: dict, headlines: list[dict]
) -> tuple[str, list[str]]:
    """Cross-check every number in the brief. A number that matches the
    fetched market data is left alone. A number that instead matches a
    quote in one of the day's headlines gets a "Source: ..." citation
    inserted on the line right below it, rather than being flagged — it
    wasn't fetched by us, but it wasn't invented either. Only numbers that
    match neither are returned as genuinely unverified.

    Returns (annotated_brief_text, unverified_issues)."""
    expected = _expected_numbers(market_data, dominance, fear_greed)
    issues = []
    lines = brief_text.split("\n")

    for i, line in enumerate(lines):
        matches = list(DOLLAR_RE.finditer(line)) + list(PERCENT_RE.finditer(line))
        sources = set()

        for match in matches:
            is_percent = match.group(0).endswith("%")
            candidates = _figure_candidates(match, is_percent)
            if any(_has_match(v, expected) for v in candidates):
                continue

            source = _headline_source(candidates, headlines)
            if source:
                sources.add(source)
            else:
                issues.append(f'Unverified figure "{match.group(0)}" — not found in source data')

        if sources:
            indent = re.match(r"\s*", line).group(0)
            lines[i] = f"{line}\n{indent}*Source: {', '.join(sorted(sources))}*"

    return "\n".join(lines), issues


def verify_spelling(brief_text: str) -> list[str]:
    """Return words that don't look like valid English or known crypto/
    finance terms. Best-effort — jargon not yet in KNOWN_TERMS may still
    false-positive, which is fine since this only produces a flag.

    A word that's always capitalized wherever it appears (RLUSD, Metaplanet,
    Hyperliquid) is almost certainly a ticker/product/company name pulled
    from that day's headlines rather than a typo — real typos show up as
    lowercase words in normal prose — so those are skipped rather than
    requiring every new proper noun to be added to KNOWN_TERMS by hand."""
    checker = SpellChecker()
    checker.word_frequency.load_words(KNOWN_TERMS)

    all_words = re.findall(r"[A-Za-z']+", brief_text)
    candidates = {w.lower() for w in all_words if w[0].islower() and len(w) > 2}
    misspelled = checker.unknown(candidates)

    return [f'Possible misspelling: "{word}"' for word in sorted(misspelled)]


def verify_brief(
    brief_text: str, market_data: dict, dominance: dict, fear_greed: dict, headlines: list[dict]
) -> tuple[str, list[str]]:
    """Run all verification checks. Returns (annotated_brief_text, issues) —
    the brief with "Source: ..." citations inserted under any headline-
    sourced figures, and the list of remaining issues (unverifiable numbers
    plus possible misspellings) to surface in a warning section."""
    annotated, unverified_numbers = annotate_and_verify_numbers(
        brief_text, market_data, dominance, fear_greed, headlines
    )
    return annotated, unverified_numbers + verify_spelling(brief_text)


if __name__ == "__main__":
    sample = (
        "BTC is up 2.35% today, trading at $67,432.10 with a market cap of $1.30T.\n"
        "Tesla booked a $112M paper loss on its holdings, per the article."
    )
    fake_market_data = {
        "BTC": {
            "price": 67432.10, "change_24h": 2.35, "change_7d": 1.0, "change_30d": 5.0,
            "market_cap": 1_300_000_000_000, "volume_24h": 24_500_000_000,
            "ath_change_percentage": -10.0,
        }
    }
    fake_headlines = [
        {"coin": "BTC", "headline": "Tesla reports $112M paper loss on Bitcoin", "source": "CoinDesk"},
    ]
    annotated, issues = verify_brief(sample, fake_market_data, {}, {"value": 50}, fake_headlines)
    print(annotated)
    print(issues)
