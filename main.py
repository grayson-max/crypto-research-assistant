"""Orchestrate the pipeline: fetch market data + headlines, tag sentiment,
generate a brief, save it to reports/brief_YYYY-MM-DD.md, and deliver a
styled copy to iCloud Drive if available (syncs to phone), or a local
fallback folder otherwise, with a desktop notification."""

import os
import subprocess
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
from generate_brief import generate_brief, DISCLAIMER
from deliver import deliver_to_icloud, notify_done
from verify_brief import verify_brief

load_dotenv()

REPORTS_DIR = Path(__file__).parent / "reports"

REQUIRED_ENV_VARS = ["ANTHROPIC_API_KEY", "NEWSAPI_API_KEY"]

SOURCES_NOTE = (
    "Data sources: CoinGecko (price, market cap, dominance), "
    "Alternative.me (Fear & Greed Index), NewsAPI (headlines)."
)


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

    brief, issues = verify_brief(brief, market_data, dominance, fear_greed, headlines)
    if issues:
        warning_section = (
            "\n\n## ⚠️ Verification Notes\n"
            "_Automated checks flagged the following — review before relying on this brief:_\n\n"
            + "\n".join(f"- {issue}" for issue in issues)
            + "\n"
        )
        brief = brief.replace(DISCLAIMER, warning_section + DISCLAIMER)
        print(f"Verification flagged {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")

    today = date.today()
    stem = f"brief_{today.isoformat()}"

    REPORTS_DIR.mkdir(exist_ok=True)
    out_path = REPORTS_DIR / f"{stem}.md"
    out_path.write_text(f"{brief}\n\n_{SOURCES_NOTE}_\n")
    print(f"Saved brief to {out_path}")

    html_path, synced_to_icloud = deliver_to_icloud(
        brief, stem, market_data, dominance, fear_greed,
        today.strftime("%A, %B %-d, %Y"), SOURCES_NOTE,
    )

    if synced_to_icloud:
        print(f"Delivered to iCloud Drive: {html_path}")
    else:
        print(
            f"iCloud Drive isn't set up on this Mac, so the brief was saved "
            f"locally instead (still findable, just won't sync to your "
            f"phone/other devices):\n  {html_path}\n"
            f"Turn on iCloud Drive in System Settings to have future "
            f"briefs sync automatically."
        )

    # When run by hand in Terminal (stdout is a real tty), pop the folder
    # open in Finder — this is the "correctly directs the user to where the
    # HTML version is" fix: don't just print a path and hope it's read
    # correctly, actually show it. Skip this for cron/launchd's unattended
    # runs, which redirect stdout to cron.log and would otherwise pop a
    # Finder window open on its own every single morning.
    if sys.stdout.isatty():
        subprocess.run(["open", str(html_path.parent)], check=False)

    suffix = f" ({len(issues)} verification issue(s) flagged)" if issues else ""
    location = "iCloud Drive" if synced_to_icloud else "local folder (see Terminal)"
    notify_done(f"Saved to {location}: {html_path.name}{suffix}")


def main() -> None:
    try:
        run()
    except Exception as exc:
        traceback.print_exc()
        notify_done(f"FAILED: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
