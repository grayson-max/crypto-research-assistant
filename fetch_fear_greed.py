"""Fetch the current Crypto Fear & Greed Index (alternative.me) — a widely
recognized single 0-100 gauge of overall market sentiment, independent of
BTC/ETH/SOL-specific headlines."""

import requests

API_URL = "https://api.alternative.me/fng/"


def fetch_fear_greed() -> dict:
    """Return {value: int, classification: str} e.g. {"value": 33, "classification": "Fear"}."""
    response = requests.get(API_URL, params={"limit": 1}, timeout=10)
    response.raise_for_status()
    entry = response.json()["data"][0]

    return {
        "value": int(entry["value"]),
        "classification": entry["value_classification"],
    }


if __name__ == "__main__":
    print(fetch_fear_greed())
