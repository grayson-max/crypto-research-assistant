"""Keyword-based positive/neutral/negative tagging for headlines."""

POSITIVE_WORDS = [
    "rally", "surge", "adoption", "gain", "gains", "bullish", "record high",
    "soar", "soars", "jump", "jumps", "rebound", "breakout", "outperform",
    "inflow", "inflows", "upgrade", "partnership", "launch", "launches",
]

NEGATIVE_WORDS = [
    "crash", "hack", "hacked", "lawsuit", "sell-off", "selloff", "bearish",
    "plunge", "plunges", "drop", "drops", "decline", "outflow", "outflows",
    "ban", "banned", "investigation", "fraud", "exploit", "exploited",
    "delist", "delisted", "downgrade", "warning",
]


def tag_sentiment(headline: str) -> str:
    """Return 'positive', 'negative', or 'neutral' based on keyword matches."""
    text = (headline or "").lower()

    positive_hits = sum(1 for word in POSITIVE_WORDS if word in text)
    negative_hits = sum(1 for word in NEGATIVE_WORDS if word in text)

    if positive_hits > negative_hits:
        return "positive"
    if negative_hits > positive_hits:
        return "negative"
    return "neutral"


def tag_headlines(headlines: list[dict]) -> list[dict]:
    """Add a 'sentiment' key to each headline dict."""
    for item in headlines:
        item["sentiment"] = tag_sentiment(item.get("headline", ""))
    return headlines


if __name__ == "__main__":
    from fetch_headlines import fetch_headlines

    for item in tag_headlines(fetch_headlines()):
        print(f"[{item['sentiment']:>8}] {item['coin']}: {item['headline']}")
