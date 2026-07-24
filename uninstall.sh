#!/bin/bash
# Removes everything install.sh set up outside this project folder (the
# cron job and the launchd catch-up agent), then asks — one thing at a
# time — before removing anything from inside the project folder itself.
# Nothing is deleted without being asked first, and this script never
# deletes the project folder itself.
#
# Run from the project folder:
#   ./uninstall.sh

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=== Crypto Research Brief — Uninstall ==="
echo "Project folder: $PROJECT_DIR"
echo ""

# --- 1. Remove the cron job ---
if crontab -l 2>/dev/null | grep -qF "$PROJECT_DIR"; then
    ( crontab -l 2>/dev/null | grep -vF "$PROJECT_DIR" ) | crontab -
    echo "[1/2] Removed the daily cron job."
else
    echo "[1/2] No cron job found for this project, skipping."
fi

# --- 2. Remove the launchd catch-up agent ---
# Label is derived from PROJECT_DIR the same way install.sh sets it up
# (see its step 7 for why) — plus a check for the old shared-name agent
# in case this project was installed before that fix.
PLIST_LABEL="com.cryptoresearch.catchup.$(printf '%s' "$PROJECT_DIR" | shasum -a 256 | cut -c1-12)"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"
LEGACY_PLIST_PATH="$HOME/Library/LaunchAgents/com.cryptoresearch.catchup.plist"

REMOVED_AGENT=0
if [ -f "$PLIST_PATH" ]; then
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    rm "$PLIST_PATH"
    REMOVED_AGENT=1
fi
if [ -f "$LEGACY_PLIST_PATH" ]; then
    launchctl unload "$LEGACY_PLIST_PATH" 2>/dev/null || true
    rm "$LEGACY_PLIST_PATH"
    REMOVED_AGENT=1
fi

if [ "$REMOVED_AGENT" = "1" ]; then
    echo "[2/2] Removed the launchd catch-up agent."
else
    echo "[2/2] No launchd catch-up agent found, skipping."
fi

echo ""
echo "Automation is fully stopped — no more briefs will generate on a schedule."
echo ""
echo "The project folder itself (code, .venv, .env, config.json, reports/)"
echo "is still here at $PROJECT_DIR. Nothing below is required — answer 'n'"
echo "to anything you'd rather keep."
echo ""

read -rp "Delete the virtual environment (.venv)? [y/N]: " DELETE_VENV
if [[ "$DELETE_VENV" =~ ^[Yy] ]]; then
    rm -rf .venv
    echo "  Removed .venv"
fi

read -rp "Delete your API keys and preferences (.env, config.json)? [y/N]: " DELETE_SECRETS
if [[ "$DELETE_SECRETS" =~ ^[Yy] ]]; then
    rm -f .env config.json
    echo "  Removed .env and config.json"
fi

read -rp "Delete your archived briefs (reports/)? [y/N]: " DELETE_REPORTS
if [[ "$DELETE_REPORTS" =~ ^[Yy] ]]; then
    rm -rf reports
    echo "  Removed reports/"
fi

echo ""
echo "=== Uninstall complete ==="
echo "To remove the project folder entirely, delete it yourself:"
echo "  rm -rf $PROJECT_DIR"
echo "(left as a manual step on purpose, since it also holds anything you"
echo "chose to keep above)."
