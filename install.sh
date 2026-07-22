#!/bin/bash
# One-time setup for the crypto research brief pipeline. Run this after
# cloning the repo:
#   git clone <repo-url> ~/crypto_research_assistant
#   cd ~/crypto_research_assistant
#   ./install.sh
#
# Safe to run more than once — re-running just re-applies the same setup
# (this property is called "idempotent").

set -e  # stop immediately if any command fails, instead of continuing
        # on to steps that assume the failed one worked

# Figure out where this script lives, so setup works no matter whose
# computer or username it's running under.
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=== Crypto Research Brief — Setup ==="
echo "Installing into: $PROJECT_DIR"
echo ""

# --- 1. Check Python is installed ---
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found. Install it from https://www.python.org/downloads/ and re-run this script."
    exit 1
fi
echo "[1/6] Python found: $(python3 --version)"

# --- 2. Create a virtual environment ---
# A "virtual environment" (venv) is a private, self-contained copy of
# Python just for this project, so its packages can't clash with anything
# else installed on this Mac.
if [ ! -d ".venv" ]; then
    echo "[2/6] Creating virtual environment..."
    python3 -m venv .venv
else
    echo "[2/6] Virtual environment already exists, skipping."
fi

# --- 3. Install dependencies ---
echo "[3/6] Installing required packages..."
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt

# --- 4. Collect API keys ---
# A ".env" file holds secret values (API keys) that the code reads at
# runtime. It's kept out of git on purpose, so keys never get shared or
# uploaded — each person's .env stays only on their own machine.
if [ -f ".env" ]; then
    echo "[4/6] .env already exists, skipping key setup."
else
    echo "[4/6] Setting up API keys."
    echo "You'll need two free API keys:"
    echo "  - Anthropic: https://console.anthropic.com/settings/keys"
    echo "  - NewsAPI:   https://newsapi.org/register"
    echo ""
    read -rp "Paste your Anthropic API key: " ANTHROPIC_KEY
    read -rp "Paste your NewsAPI key: " NEWSAPI_KEY

    cat > .env <<EOF
ANTHROPIC_API_KEY=$ANTHROPIC_KEY
NEWSAPI_API_KEY=$NEWSAPI_KEY
EOF
    echo "Saved to .env"
fi

# --- 5. Schedule the daily 8am run ---
# "cron" is macOS's built-in daily-alarm-clock system for running a
# command automatically at a set time, even with no one logged in to
# watch it happen.
echo "[5/6] Scheduling the daily 8am run (cron)..."
CRON_CMD="cd $PROJECT_DIR && $PROJECT_DIR/.venv/bin/python3 main.py >> $PROJECT_DIR/cron.log 2>&1"
CRON_LINE="0 8 * * * $CRON_CMD"
# Remove any previous entry for this exact project folder first, so
# re-running this script doesn't create duplicate cron jobs.
( crontab -l 2>/dev/null | grep -vF "$PROJECT_DIR" ; echo "$CRON_LINE" ) | crontab -

# --- 6. Catch-up agent (launchd) ---
# cron only fires at exactly 8:00am — if the Mac is asleep then, it's
# simply skipped. "launchd" is macOS's more flexible scheduler; here it
# runs a quick check every 30 minutes ("did today's brief get made yet?")
# so a missed 8am run still catches up shortly after the Mac wakes up.
echo "[6/6] Setting up the catch-up check (launchd)..."
chmod +x run_if_missing.sh
PLIST_LABEL="com.cryptoresearch.catchup"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"

launchctl unload "$PLIST_PATH" 2>/dev/null || true  # ignore error if not loaded yet

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/run_if_missing.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/cron.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/cron.log</string>
</dict>
</plist>
EOF

launchctl load "$PLIST_PATH"

echo ""
echo "=== Setup complete ==="
echo "Your first brief will generate automatically at 8am (or within ~30"
echo "minutes of your Mac being awake after that), and will appear in:"
echo "  iCloud Drive > CryptoBriefs"
echo ""
echo "Want to generate one right now instead of waiting? Run:"
echo "  cd $PROJECT_DIR && .venv/bin/python3 main.py"
