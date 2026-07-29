#!/bin/bash
# Writes (or replaces) this project's crontab entry using the schedule time
# passed as $1, in HH:MM 24-hour format (e.g. "08:00" or "17:30").
#
# Shared by install.sh (first-time setup) and configure.sh (changing the
# time later) so the cron-writing logic only lives in one place.
#
# Usage: scripts/schedule.sh 08:00

set -e

TIME="$1"
if [ -z "$TIME" ]; then
    echo "Usage: scripts/schedule.sh HH:MM" >&2
    exit 1
fi

# Reject anything that isn't 24-hour HH:MM before it reaches cron — without
# this, a typo like "830" (missing the colon) silently sets both HOUR and
# MINUTE to 830, producing a cron line that runs at the wrong time (or not
# at all) with no error anywhere a user would think to look.
if ! [[ "$TIME" =~ ^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$ ]]; then
    echo "\"$TIME\" isn't a valid 24-hour HH:MM time (e.g. \"08:00\" or \"17:30\")." >&2
    exit 1
fi

HOUR="${TIME%%:*}"
MINUTE="${TIME##*:}"

# Strip any leading zero (cron/bash can misread "08" as an invalid octal
# number) — 10#$HOUR forces base-10 interpretation either way, belt and
# suspenders.
HOUR=$((10#$HOUR))
MINUTE=$((10#$MINUTE))

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# Quoted, not just "$PROJECT_DIR" interpolated bare into the string — this
# whole line becomes crontab text that cron later hands to /bin/sh -c, so
# without quotes here a project path containing a space (e.g. a Mac
# username like "John Smith") makes `cd` receive only the first word,
# fail, and silently skip the rest of the command — no brief, no error
# anywhere a user would think to look.
CRON_CMD="cd \"$PROJECT_DIR\" && \"$PROJECT_DIR/.venv/bin/python3\" main.py >> \"$PROJECT_DIR/cron.log\" 2>&1"
CRON_LINE="$MINUTE $HOUR * * * $CRON_CMD"

# Remove any previous entry for this exact project folder first, so
# re-running this doesn't create duplicate cron jobs. Matched against
# `cd "$PROJECT_DIR"` (with the closing quote), not the bare path — a bare
# substring match would also strip a *different* project whose path
# happens to start with this one (e.g. "crypto_research_assistant" vs
# "crypto_research_assistant_v2"), since the shorter path is a prefix of
# the longer one. `grep -v` exits with status 1 (not an error here) when
# it filters out every line — e.g. when this project already had exactly
# one entry and nothing else is in the crontab — so it's guarded with
# `|| true`. Without that, `set -e` would abort this subshell before the
# echo below runs, and `crontab -` would silently install an EMPTY
# crontab, wiping out everything (not just this project's line).
( crontab -l 2>/dev/null | grep -vF "cd \"$PROJECT_DIR\"" || true ; echo "$CRON_LINE" ) | crontab -

echo "Scheduled daily run at $TIME ($PROJECT_DIR)"
