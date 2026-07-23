"""Fetch price, 24h/7d/30d change, market cap, volume, supply, ATH, and a
7-day sparkline for the configured coins. One CoinGecko /coins/markets call
covers all of it."""

import requests

from config import load_config

API_URL = "https://api.coingecko.com/api/v3/coins/markets"


def fetch_market_data() -> dict:
    """Return {symbol: {...}} with everything a stat tile needs, or
    {symbol: None} if that coin wasn't in the response."""
    coins = {
        symbol: data["coingecko_id"] for symbol, data in load_config()["coins"].items()
    }
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coins.values()),
        "price_change_percentage": "24h,7d,30d",
        "sparkline": "true",
    }

    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    raw = {coin["id"]: coin for coin in response.json()}

    market_data = {}
    for symbol, coingecko_id in coins.items():
        coin = raw.get(coingecko_id)
        if coin is None:
            market_data[symbol] = None
            continue

        market_data[symbol] = {
            "price": coin.get("current_price"),
            "change_24h": coin.get("price_change_percentage_24h_in_currency"),
            "change_7d": coin.get("price_change_percentage_7d_in_currency"),
            "change_30d": coin.get("price_change_percentage_30d_in_currency"),
            "market_cap": coin.get("market_cap"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "volume_24h": coin.get("total_volume"),
            "circulating_supply": coin.get("circulating_supply"),
            "max_supply": coin.get("max_supply"),
            "ath": coin.get("ath"),
            "ath_change_percentage": coin.get("ath_change_percentage"),
            "sparkline_7d": (coin.get("sparkline_in_7d") or {}).get("price", []),
        }

    return market_data


if __name__ == "__main__":
    print(fetch_market_data())
