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
    "- Write 2-3 short paragraphs followed by a few bullet points highlighting "
    "the most notable items per asset."
)


def build_prompt(market_data: dict, headlines: list[dict]) -> str:
    """Construct the LLM prompt from structured market data and tagged headlines."""
    lines = ["Market data (BTC/ETH/SOL):"]
    for symbol, data in market_data.items():
        if data is None:
            lines.append(f"- {symbol}: no data available")
            continue
        lines.append(
            f"- {symbol}: ${data['price']:,.2f}, "
            f"24h change {data['change_24h']:+.2f}%, "
            f"market cap ${data['market_cap']:,.0f}"
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


def generate_brief(market_data: dict, headlines: list[dict]) -> str:
    """Call the Anthropic API and return brief text with the disclaimer appended."""
    client = anthropic.Anthropic()
    prompt = build_prompt(market_data, headlines)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    brief_text = next(
        (block.text for block in response.content if block.type == "text"), ""
    )
    return brief_text + DISCLAIMER
