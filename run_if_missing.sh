#!/bin/bash
# Runs the crypto research pipeline only if today's report doesn't exist yet.
# Used as a catch-up check by the launchd agent, in case the 8am cron job
# was missed because the laptop was asleep.

PROJECT_DIR="/Users/ghoe25/crypto_research_assistant"
TODAY=$(date +%Y-%m-%d)
REPORT_FILE="$PROJECT_DIR/reports/brief_${TODAY}.md"

if [ ! -f "$REPORT_FILE" ]; then
    "$PROJECT_DIR/.venv/bin/python3" "$PROJECT_DIR/main.py" >> "$PROJECT_DIR/cron.log" 2>&1
fi
