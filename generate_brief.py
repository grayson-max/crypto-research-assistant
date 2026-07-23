"""Build a prompt from market data + headlines/sentiment and call the Anthropic API
to generate a short research brief, with a hard-enforced compliance disclaimer."""

import anthropic

MODEL = "claude-opus-4-8"

DISCLAIMER = (
    "\n\n---\n"
    "**This document is for internal research purposes only and does not "
    "constitute investment advice or a recommendation to buy, sell, or hold "
    "any asset. Advisor review required before any client-facing use.**"
)

SYSTEM_PROMPT = (
    "You are a research assistant writing an internal daily crypto market brief "
    "for a financial advisor at a Registered Investment Advisory (RIA) firm. "
    "This brief is for internal research support only — it is never shown "
    "directly to clients and does not constitute investment advice.\n\n"
    "Rules:\n"
    "- Do not use the words 'buy', 'sell', or 'should'.\n"
    "- Do not give price targets or predictions.\n"
    "- Do not tell the reader what action to take.\n"
    "- Stick to describing what the data and headlines show, and note any "
    "notable sentiment shifts.\n"
    "- Do not include any disclaimer or compliance language — one is "
    "appended automatically after your response.\n"
    "- Write the Market Overview as short bullet points (not paragraphs) "
    "covering price action, sentiment, and any notable regulatory/"
    "infrastructure themes — a few bullets per topic, not dense prose.\n"
    "- For each asset's Notable Items, lead with a single bold headline "
    "figure line (price, 24h/30d change) followed by short bullet points "
    "for each notable item.\n"
    "- One fact or idea per bullet. Never join multiple facts in a single "
    "bullet with semicolons or 'and' — split them into separate bullets "
    "instead, so the reader can scan line by line without parsing dense "
    "clauses.\n"
    "- Use terse data-label format for stats, not full sentences — e.g. "
    "'Market cap: $1.30T (#1 rank)' and 'Volume (24h): $24.5B', not "
    "'Market cap of $1.30T holds the #1 rank.'\n"
)


def build_prompt(market_data: dict, headlines: list[dict], fear_greed: dict) -> str:
    """Construct the LLM prompt from structured market data, tagged headlines,
    and the current Fear & Greed reading."""
    lines = ["Market data (BTC/ETH/SOL):"]
    for symbol, data in market_data.items():
        if data is None:
            lines.append(f"- {symbol}: no data available")
            continue
        lines.append(
            f"- {symbol}: ${data['price']:,.2f}, "
            f"24h change {data['change_24h']:+.2f}%, "
            f"7d change {data['change_7d']:+.2f}%, "
            f"30d change {data['change_30d']:+.2f}%, "
            f"market cap ${data['market_cap']:,.0f} (rank #{data['market_cap_rank']}), "
            f"24h volume ${data['volume_24h']:,.0f}, "
            f"{data['ath_change_percentage']:+.1f}% from all-time high"
        )

    lines.append(
        f"\nCrypto Fear & Greed Index: {fear_greed['value']}/100 "
        f"({fear_greed['classification']}) — a market-wide sentiment gauge, "
        "not specific to BTC/ETH/SOL. Reference it briefly in the Market "
        "Overview if it adds context, but don't over-index on it."
    )

    lines.append("\nRecent headlines with sentiment tags:")
    for item in headlines:
        lines.append(
            f"- [{item['coin']}] ({item['sentiment']}) {item['headline']} "
            f"— {item['source']}"
        )

    lines.append(
        "\nWrite today's research brief from this data, following the system rules."
    )
    return "\n".join(lines)


def generate_brief(market_data: dict, headlines: list[dict], fear_greed: dict) -> str:
    """Call the Anthropic API and return brief text with the disclaimer appended."""
    client = anthropic.Anthropic()
    prompt = build_prompt(market_data, headlines, fear_greed)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1536,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    brief_text = next(
        (block.text for block in response.content if block.type == "text"), ""
    )
    return brief_text + DISCLAIMER
