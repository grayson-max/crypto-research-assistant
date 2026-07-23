# Crypto Research Brief — project context for Claude

This project generates a daily research brief on a configured set of
crypto assets (default: BTC, ETH, SOL) for internal use at a Registered
Investment Advisory (RIA) firm. It is research support only, not
investment advice, and is never shown directly to clients.

## Where the data lives

- `reports/brief_YYYY-MM-DD.md` — one file per day the pipeline has run,
  named by the date it was generated. To answer any question about a
  specific date or a date range, read the matching file(s) directly —
  `ls reports/` to see what's available.
- `config.json` — which coins are currently tracked, delivery schedule,
  and delivery destination. Check this before assuming BTC/ETH/SOL if a
  question is about "which coins does this track."
- Briefs are also delivered as styled HTML to iCloud Drive (folder name
  set in `config.json` under `delivery.folder_name`), but the Markdown
  files in `reports/` are the canonical, plain-text source for reading or
  summarizing brief content.

## Answering questions about brief content

When asked something like "how did BTC do this week" or "summarize the
sentiment trend this month," read the relevant dated files in `reports/`
(not just today's) and answer from what they contain — don't guess or
use outside knowledge of current prices, since this pipeline's only
source of truth is whatever was fetched and written into those files on
each date.

Follow the same compliance framing the generated briefs themselves use:
- Do not use the words "buy," "sell," or "should."
- Do not give price targets or predictions.
- Do not tell the reader what action to take.
- Describe only what the data and headlines in the brief files show.

This matters even in ad hoc conversation, not just in the automated
generation step (see `generate_brief.py`'s `SYSTEM_PROMPT` for the same
rules applied there) — a question asked in chat should get an answer
held to the same standard as the written brief.

## Changing what's in the brief

The user may ask in plain English for a change to the brief's content
or appearance — e.g. "add a new data point," "show a chart of BTC's
price this month," "make the headlines section shorter." These are code
changes, not config options — go to the file that owns that concern
rather than guessing:

- **`deliver.py`** — the styled HTML report: KPI stat tiles, the
  Fear & Greed gauge, colors/layout/spacing, and anything about how the
  brief *looks* (including adding a new chart — see `_sparkline_svg` for
  the existing pattern of a small inline SVG chart with no external
  library).
- **`generate_brief.py`** — what the brief *says*: the `SYSTEM_PROMPT`
  controls tone/structure/compliance rules, and `build_prompt` controls
  what data gets handed to Claude to write about. A request to track a
  new data point (e.g. trading volume trend, a new coin) usually starts
  in `fetch_market_data.py` (fetch it) and flows through here (mention
  it in the prompt) and `deliver.py` (display it).
- **`fetch_market_data.py` / `fetch_dominance.py` / `fetch_headlines.py`
  / `fetch_fear_greed.py`** — where to add a genuinely new upstream data
  source, if the request needs something none of these already fetch.

After making a change, regenerate a brief to verify it end-to-end rather
than just reading the diff:
```
.venv/bin/python3 main.py
```
then check both `reports/brief_<today>.md` and the delivered HTML in
iCloud Drive (path from `config.json`'s `delivery.folder_name`) — the
HTML is the styled version and often the one place layout/chart changes
are actually visible.

## Automation and troubleshooting

- `cron.log` — check here first if a day's brief seems to be missing.
- `.claude/skills/checkbrief/` — checks today's brief exists and isn't
  stale, and opens it in the browser.
- `.claude/skills/askbrief/` — answers historical questions across
  multiple days of briefs.
- `install.sh` / `configure.sh` / `uninstall.sh` — set up, change, or
  remove the automation (cron + launchd). Not typically what a Q&A
  question is about, but relevant if asked "how do I change the
  schedule" or similar.
