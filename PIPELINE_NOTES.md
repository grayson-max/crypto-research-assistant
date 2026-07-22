# Pipeline Notes (plain-language reference)

This project is a **modular pipeline**: an assembly line where each file is
one station that does one job and hands its output to the next station.
`main.py` is the foreman that calls each station in order.

## Files

### `fetch_market_data.py` — DONE
Calls CoinGecko's API (a REST API — a web address you send a request to and
get structured data back from, instead of a webpage).

- `requests.get(...)` sends the request. `params` are the query options
  (which coins, which currency) tacked onto the URL, e.g.
  `?ids=bitcoin,ethereum&vs_currencies=usd`.
- `response.raise_for_status()` — if CoinGecko errors out, this makes Python
  throw an error immediately instead of silently continuing with garbage
  data. Fail loudly, not silently.
- `.json()` converts the raw text response into a Python `dict`
  (key/value pairs, like a lookup table).
- The loop over `COINS.items()` translates CoinGecko's naming ("bitcoin")
  back to our naming ("BTC"), and reshapes their nested response into the
  clean `{price, change_24h, market_cap}` shape the rest of the pipeline
  expects. This reshaping is called **normalizing** — different APIs return
  data in different shapes, so you convert them all to one consistent shape
  your own code can rely on.

### `fetch_headlines.py` — DONE
Same idea as market data, but calls NewsAPI instead of CoinGecko, and
returns text headlines instead of numbers.

**Switched from CryptoPanic to NewsAPI**: CryptoPanic discontinued its free
API plan in April 2026, so we use NewsAPI's `/v2/everything` search
endpoint instead, querying "Bitcoin"/"Ethereum"/"Solana" separately (no
built-in coin tagging like CryptoPanic had, so we tag by which query
returned the result).

**Known limitation**: NewsAPI searches full article text, not just the
headline, so a coin can get matched from a passing mention even if the
headline isn't really about that coin (e.g. an unrelated tech article that
happens to reference Ethereum once). Worth noting in the final write-up —
this is a tradeoff of the free/simple search API versus a purpose-built
crypto news aggregator.

### `sentiment.py` — DONE
No API call at all — pure logic. Scans each headline's text (lowercased)
for words from `POSITIVE_WORDS` / `NEGATIVE_WORDS`, counts hits on each
side, and labels the headline whichever way has more hits — a tie (usually
0-0, no keyword matches at all) is `neutral`. Deterministic and auditable
(unlike an LLM's judgment) — important for a compliance-sensitive use case,
since you can always point to exactly which word triggered a tag.

**Observed behavior**: most real headlines come back `neutral`, since
day-to-day crypto reporting is often matter-of-fact rather than using
clearly loaded words like "crash" or "rally." This is expected and
arguably correct — better to under-call sentiment than force a false
positive/negative read. Worth mentioning as a known characteristic (not a
bug) in the final write-up.

### `generate_brief.py` — DONE
Takes market data + tagged headlines, builds a **prompt** (the instructions
sent to Claude), calls the Anthropic API, and appends the compliance
disclaimer in code — not left to the model to remember. Uses `claude-opus-4-8`
via the Anthropic Python SDK. The `SYSTEM_PROMPT` carries the compliance
rules (no "buy/sell/should", no price targets, research-only framing) —
tested live and it reliably avoided all three banned words.

### `main.py` — DONE (wiring)
Imports functions from the other files and calls them in sequence.
It doesn't know or care *how* each step works internally — it just calls
each function and trusts it returns the right shape of data. Saves the
final brief to `reports/brief_YYYY-MM-DD.md` (Markdown — the archive copy)
and calls `deliver.py` to send a styled copy to iCloud Drive.

**`check_env_vars()`** runs first and fails immediately with a clear message
if `.env` is missing a required key — added specifically for the portable/
second-user version, so a misconfigured setup gives a readable error
instead of a confusing stack trace several steps into the pipeline.

**Failure handling:** `run()` (the real pipeline) is wrapped in a
try/except in `main()`. Any failure — bad API key, network issue, rate
limit — prints the full traceback (visible in `cron.log`), fires a
"FAILED: ..." desktop notification, and exits with code 1. This matters
because the pipeline runs unattended via cron; a silent crash with no
signal would mean a missed day going unnoticed.

### `deliver.py` — DONE
Delivery mechanism, chosen over email after weighing options: renders a
full styled HTML report and saves it into
`~/Library/Mobile Documents/com~apple~CloudDocs/CryptoBriefs/` — the local
folder that iCloud Drive automatically syncs to all of the user's Apple
devices. Chosen over email because it requires **zero account setup** for
a new user (no app passwords, no SMTP config) as long as they're signed
into iCloud on their Mac, which is the default for virtually all Mac users.
Also fires the native macOS notification (best-effort — some environments,
like screen-sharing/Focus modes, suppress it; this is a known non-fatal
platform quirk, not a pipeline bug).

The report is a proper stat-sheet, not just rendered Markdown: a KPI row
of one stat tile per coin (price, 24h/7d/30d change, market cap + rank +
dominance %, 24h volume, circulating/max supply, distance from all-time
high, a 7-day sparkline), a Fear & Greed Index gauge, then the AI-written
narrative underneath. Colors follow the project's validated data-viz
palette (see the `dataviz` skill) — a fixed green/red pair for every delta
field, status-scale colors for the Fear & Greed gauge. An earlier version
included a jargon glossary; dropped after feedback that the recipient is
an industry professional, not a beginner.

### `fetch_fear_greed.py` / `fetch_dominance.py` — DONE
Two small free, no-key-required data sources layered on top of the
original CoinGecko/NewsAPI pair: `alternative.me`'s Fear & Greed Index
(market-wide sentiment, 0-100) and CoinGecko's `/global` endpoint (each
coin's % share of total crypto market cap). Both feed the stat tiles;
Fear & Greed is also passed into `generate_brief.py`'s prompt so the
written narrative can reference it.

**`fetch_market_data.py` was consolidated** to use CoinGecko's
`/coins/markets` endpoint instead of `/simple/price` — one call now
returns price, 24h/7d/30d change, market cap, rank, volume, supply, ATH,
and a 7-day hourly sparkline, replacing what used to be two separate
endpoints (a since-removed `fetch_price_history.py`).

## Supporting files

- **`requirements.txt`** — list of external packages (libraries other
  people wrote) the project depends on. `pip install -r requirements.txt`
  installs everything in this list, so anyone running the project gets the
  same setup.
- **`.env.example`** — template showing which secret keys the project
  needs, without real values. Copy to a real `.env` and fill in your keys.
- **`.gitignore`** — tells git (version control) which files to never
  track/upload — most importantly `.env`, so API keys never end up in a
  public repo.
- **`.venv/`** — a virtual environment: an isolated, self-contained copy of
  Python and its installed packages, scoped to just this project. Without
  it, `pip install` installs packages globally, where they can clash with
  other projects needing different versions. Activate it with
  `source .venv/bin/activate` before running code so Python looks there
  first for packages.

## Automation (scheduling)

Two mechanisms work together so the brief generates reliably even if the
laptop is asleep at the scheduled time:

- **cron job** (`crontab -l` to view) — runs `main.py` directly every day at
  8:00 AM. Simple, but silently skipped if the Mac is asleep/off at 8am.
- **launchd agent** (`~/Library/LaunchAgents/com.grayson.cryptoresearch.plist`)
  — runs `run_if_missing.sh` every 30 minutes, plus once whenever the agent
  loads (login/wake). The script checks whether today's report file already
  exists; if not, it runs the pipeline. This is the catch-up mechanism —
  since the check is near-instant when nothing's needed, it does not spam
  API calls, but catches missed days within ~30 minutes of the laptop waking.
- **Notification** — `main.py` calls `notify_done()` at the end of a run,
  which shows a native macOS notification via `osascript`. Works when
  triggered by the launchd agent (runs in the logged-in GUI session); may
  silently fail to display if triggered by plain cron, which lacks GUI
  session access on macOS — this is a known platform quirk, not a bug.
- **Logs**: `~/crypto_research_assistant/cron.log` — check here first if a
  day's brief doesn't appear.
- **To remove**: `crontab -e` (delete the line) and
  `launchctl unload ~/Library/LaunchAgents/com.grayson.cryptoresearch.plist`
  followed by deleting that plist file.

## Build order status

1. Scaffold — done
2. `fetch_market_data.py` (CoinGecko) — done, tested against live data
3. `fetch_headlines.py` (NewsAPI) — done, tested against live data
4. `sentiment.py` — done, tested against live headlines
5. `generate_brief.py` (Anthropic API) — done, tested against live data
6. Run `main.py` end to end — done, first real brief saved to reports/brief_2026-07-17.md
7. Generate 3 sample briefs — in progress. Day 1 done (2026-07-17). Pipeline only
   pulls live/current data (no historical backfill), so Days 2 and 3 need to be
   run on two separate future days: `cd ~/crypto_research_assistant && source
   .venv/bin/activate && python3 main.py`. Each run auto-names by date, so
   files won't overwrite each other.
8. Write summary doc — done (SUMMARY.md). Sample-briefs section references
   Day 1 only for now; update the list there once Days 2 and 3 land.
