"""Fetch recent BTC/ETH/SOL headlines from NewsAPI."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://newsapi.org/v2/everything"

# NewsAPI has no built-in coin tagging, so we search per-coin with terms
# specific enough to avoid unrelated noise (plain "SOL" or "ETH" match too
# many unrelated words/tickers).
COIN_QUERIES = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "SOL": "Solana",
}

HEADLINES_PER_COIN = 5


def fetch_headlines() -> list[dict]:
    """Return a list of {coin, headline, source, published_at} dicts."""
    api_key = os.getenv("NEWSAPI_API_KEY")
    headlines = []

    for coin, query in COIN_QUERIES.items():
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": HEADLINES_PER_COIN,
            "apiKey": api_key,
        }

        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        articles = response.json().get("articles", [])

        for article in articles:
            headlines.append(
                {
                    "coin": coin,
                    "headline": article.get("title"),
                    "source": (article.get("source") or {}).get("name"),
                    "published_at": article.get("publishedAt"),
                }
            )

    return headlines


if __name__ == "__main__":
    for item in fetch_headlines():
        print(item)
