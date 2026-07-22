---
name: checkbrief
description: Confirm today's crypto research brief was generated correctly by the automation (cron + launchd), check it isn't stale, check cron.log for errors, and open it in the browser for reading. Use when the user runs /checkbrief or asks to check today's brief.
---

# Check today's brief

Run these steps in order against the project at `~/crypto_research_assistant`.

## 1. Confirm the file exists and is today's

```bash
TODAY=$(date +%Y-%m-%d)
ls -la ~/crypto_research_assistant/reports/brief_${TODAY}.md
```

- If the file is **missing**: say so plainly, then check `cron.log` (step 2)
  for why — most likely the 8am cron job hasn't fired yet, or both cron and
  the launchd catch-up failed. Also check whether the file exists for a
  *previous* date (`ls ~/crypto_research_assistant/reports/`) — if so, that
  confirms the pipeline works in general and today's run specifically
  didn't happen or hasn't happened yet.
- If the file **exists**, check its modification timestamp with `ls -la`
  (or `stat`) and confirm it's from *today*, not a stale copy sitting from
  a manual test run days ago. Flag it if the timestamp looks off relative
  to expected run times (8am cron, or within ~30 min of first wake if
  caught up by launchd).

## 2. Check cron.log for errors

```bash
tail -30 ~/crypto_research_assistant/cron.log
```

- Empty or no output for today = good sign (the `run_if_missing.sh` catch-up
  script only writes to the log when it actually runs the pipeline).
- If there's a traceback or error near today's date, read it and explain
  in plain language what broke (e.g. expired API key, network error, rate
  limit) — don't just dump the raw error at the user.

## 3. Open it in the browser

```bash
cd ~/crypto_research_assistant && source .venv/bin/activate && python3 view_brief.py
```

This renders today's brief as styled HTML and opens it in the default
browser (see `view_brief.py` for how — no `.md` file path argument needed,
it defaults to today's date).

## 4. Summarize for the user

In plain language, confirm:
- Whether today's brief exists and is fresh (not stale)
- Whether cron.log showed any errors
- That it's now open in the browser for them to read

If anything failed, explain the likely cause and what to check next
(e.g. "API key expired", "no internet at 8am", "laptop was asleep past the
30-min catch-up window too") rather than just reporting failure.
