---
name: askbrief
description: Answer questions about crypto research brief history across multiple days (e.g. "how did BTC do this week", "summarize sentiment trend this month"), by reading the relevant dated files in reports/. Use when the user asks about brief content spanning more than just today.
---

# Answer questions about brief history

Run these steps against the project at `~/crypto_research_assistant`
(or wherever this repo is cloned).

## 1. Figure out which dates are actually relevant

```bash
ls reports/*.md
```

Match the user's question to a date range (e.g. "this week" = the last
7 calendar days that have a file; "this month" = every file from the
current month present in `reports/`). If a requested date has no file,
say so plainly rather than guessing — the pipeline only has data for
days it actually ran.

## 2. Read the relevant files

Read each matching `reports/brief_YYYY-MM-DD.md` in full. These are
plain Markdown — no special parsing needed.

## 3. Answer using only what's in those files

Follow the same compliance framing as the brief generator itself (see
`CLAUDE.md` in the project root, and `generate_brief.py`'s
`SYSTEM_PROMPT`):
- No "buy," "sell," or "should"
- No price targets or predictions
- No telling the reader what action to take
- Describe only what the data/headlines in the brief files show —
  don't supplement with outside knowledge of current prices or news,
  since the brief files are the only source of truth for this project

When summarizing a trend across multiple days, point to the specific
dates/figures that support the summary (e.g. "BTC's 24h change moved
from +1.83% on 07-21 to -2.30% on 07-23") rather than a vague
generalization — this keeps the answer auditable, the same way the
automated briefs are.
