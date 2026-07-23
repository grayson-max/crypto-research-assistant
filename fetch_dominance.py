"""Fetch each coin's share of total crypto market cap ("dominance") from
CoinGecko's global market stats — shows whether capital is concentrated in
majors or rotating into smaller coins."""

import requests

from config import load_config

API_URL = "https://api.coingecko.com/api/v3/global"


def fetch_dominance() -> dict:
    """Return {symbol: pct} e.g. {"BTC": 56.85, "ETH": 9.94, "SOL": 1.94}."""
    coins = {
        symbol: data["dominance_symbol"] for symbol, data in load_config()["coins"].items()
    }
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    percentages = response.json()["data"]["market_cap_percentage"]

    return {symbol: percentages.get(cg_symbol) for symbol, cg_symbol in coins.items()}


if __name__ == "__main__":
    print(fetch_dominance())
