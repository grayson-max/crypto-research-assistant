"""Orchestrate the pipeline: fetch market data + headlines, tag sentiment,
generate a brief, save it to reports/brief_YYYY-MM-DD.md, and deliver a
styled copy to iCloud Drive (syncs to phone) with a desktop notification."""

import os
import sys
import traceback
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from fetch_market_data import fetch_market_data
from fetch_headlines import fetch_headlines
from fetch_fear_greed import fetch_fear_greed
from fetch_dominance import fetch_dominance
from sentiment import tag_headlines
from generate_brief import generate_brief
from deliver import deliver_to_icloud, notify_done

load_dotenv()

REPORTS_DIR = Path(__file__).parent / "reports"

REQUIRED_ENV_VARS = ["ANTHROPIC_API_KEY", "NEWSAPI_API_KEY"]


def check_env_vars() -> None:
    """Fail fast with a clear message if setup is incomplete, instead of a
    confusing 401/auth stack trace several steps into the pipeline."""
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"Missing required API key(s) in .env: {', '.join(missing)}. "
            "Copy .env.example to .env and fill these in before running."
        )


def run() -> None:
    check_env_vars()

    market_data = fetch_market_data()
    headlines = tag_headlines(fetch_headlines())
    fear_greed = fetch_fear_greed()
    dominance = fetch_dominance()
    brief = generate_brief(market_data, headlines, fear_greed)

    today = date.today()
    stem = f"brief_{today.isoformat()}"

    REPORTS_DIR.mkdir(exist_ok=True)
    out_path = REPORTS_DIR / f"{stem}.md"
    out_path.write_text(brief)
    print(f"Saved brief to {out_path}")

    icloud_path = deliver_to_icloud(
        brief, stem, market_data, dominance, fear_greed,
        today.strftime("%A, %B %-d, %Y"),
    )
    print(f"Delivered to {icloud_path}")

    notify_done(f"Synced to iCloud Drive: {icloud_path.name}")


def main() -> None:
    try:
        run()
    except Exception as exc:
        traceback.print_exc()
        notify_done(f"FAILED: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
