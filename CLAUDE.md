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
