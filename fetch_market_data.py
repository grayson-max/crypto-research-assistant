"""Fetch price, 24h change, and market cap for BTC/ETH/SOL from CoinGecko."""

import requests

COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
}

API_URL = "https://api.coingecko.com/api/v3/simple/price"


def fetch_market_data() -> dict:
    """Return {symbol: {price, change_24h, market_cap}} for BTC/ETH/SOL."""
    params = {
        "ids": ",".join(COINS.values()),
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_market_cap": "true",
    }

    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    raw = response.json()

    market_data = {}
    for symbol, coingecko_id in COINS.items():
        coin_data = raw.get(coingecko_id)
        if coin_data is None:
            market_data[symbol] = None
            continue

        market_data[symbol] = {
            "price": coin_data.get("usd"),
            "change_24h": coin_data.get("usd_24h_change"),
            "market_cap": coin_data.get("usd_market_cap"),
        }

    return market_data


if __name__ == "__main__":
    print(fetch_market_data())
