#!/bin/bash
# Runs the crypto research pipeline only if today's report doesn't exist yet.
# Used as a catch-up check by the launchd agent, in case the 8am cron job
# was missed because the laptop was asleep.

# $0 is "the path this script was run with" — cd-ing into its folder and
# printing the full path (pwd) gives us the project location no matter
# whose computer or username this runs under.
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
TODAY=$(date +%Y-%m-%d)
REPORT_FILE="$PROJECT_DIR/reports/brief_${TODAY}.md"

if [ ! -f "$REPORT_FILE" ]; then
    "$PROJECT_DIR/.venv/bin/python3" "$PROJECT_DIR/main.py" >> "$PROJECT_DIR/cron.log" 2>&1
fi
