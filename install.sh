#!/bin/bash
# One-time setup for the crypto research brief pipeline. Run this after
# cloning the repo:
#   git clone <repo-url> ~/crypto_research_assistant
#   cd ~/crypto_research_assistant
#   ./install.sh
#
# Safe to run more than once — re-running just re-applies the same setup
# (this property is called "idempotent").
#
# Later, to change coins/schedule/delivery without redoing all of this,
# run ./configure.sh instead. To remove everything this script sets up,
# run ./uninstall.sh.

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
echo "[1/7] Python found: $(python3 --version)"

# --- 2. Create a virtual environment ---
# A "virtual environment" (venv) is a private, self-contained copy of
# Python just for this project, so its packages can't clash with anything
# else installed on this Mac.
if [ ! -d ".venv" ]; then
    echo "[2/7] Creating virtual environment..."
    python3 -m venv .venv
else
    echo "[2/7] Virtual environment already exists, skipping."
fi

# --- 3. Install dependencies ---
echo "[3/7] Installing required packages..."
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt

# --- 4. Preferences (which coins, what time, where briefs are delivered) ---
# config.json holds everything that's safe to tweak later — it's separate
# from .env (which only holds secret API keys). Both are git-ignored, so
# every independent install gets its own copy of each.
if [ -f "config.json" ]; then
    echo "[4/7] config.json already exists, skipping preferences setup."
    echo "      (Run ./configure.sh any time to change coins/schedule/delivery.)"
else
    echo "[4/7] Setting preferences."
    read -rp "Track the default coins — Bitcoin, Ethereum, Solana? [Y/n]: " USE_DEFAULT_COINS
    if [[ "$USE_DEFAULT_COINS" =~ ^[Nn] ]]; then
        echo "config.json's \"coins\" section supports any coin CoinGecko tracks."
        echo "Using the defaults for now — edit config.json (or run ./configure.sh"
        echo "once it's built out further) to change which coins are tracked."
    fi
    read -rp "What time should the daily brief run? [08:00]: " SCHEDULE_TIME
    SCHEDULE_TIME="${SCHEDULE_TIME:-08:00}"
    read -rp "iCloud Drive folder name for delivered briefs? [CryptoBriefs]: " FOLDER_NAME
    FOLDER_NAME="${FOLDER_NAME:-CryptoBriefs}"

    .venv/bin/python3 - "$SCHEDULE_TIME" "$FOLDER_NAME" <<'PYEOF'
import json
import sys
from pathlib import Path

schedule_time, folder_name = sys.argv[1], sys.argv[2]
config = json.loads(Path("config.example.json").read_text())
config["schedule_time"] = schedule_time
config["delivery"]["folder_name"] = folder_name
Path("config.json").write_text(json.dumps(config, indent=2) + "\n")
PYEOF
    echo "Saved to config.json"
fi

# --- 5. Collect and validate API keys ---
# A ".env" file holds secret values (API keys) that the code reads at
# runtime. It's kept out of git on purpose, so keys never get shared or
# uploaded — each person's .env stays only on their own machine.
if [ -f ".env" ]; then
    echo "[5/7] .env already exists, skipping key setup."
else
    echo "[5/7] Setting up API keys."
    echo "You'll need two API keys:"
    echo "  - Anthropic (paid, billed per use): https://console.anthropic.com/settings/keys"
    echo "  - NewsAPI   (free tier):            https://newsapi.org/register"
    echo ""
    echo "Note: the Anthropic key here is a developer API key that this script"
    echo "calls in code to draft each day's brief. It's separate from a"
    echo "Claude.ai or Claude Code login/subscription — having one doesn't"
    echo "give you the other."
    echo ""
    read -rp "Paste your Anthropic API key: " ANTHROPIC_KEY
    read -rp "Paste your NewsAPI key: " NEWSAPI_KEY

    cat > .env <<EOF
ANTHROPIC_API_KEY=$ANTHROPIC_KEY
NEWSAPI_API_KEY=$NEWSAPI_KEY
EOF

    echo "Checking keys work..."
    if ANTHROPIC_API_KEY="$ANTHROPIC_KEY" .venv/bin/python3 - <<'PYEOF'
import os
import sys
import anthropic

try:
    anthropic.Anthropic().messages.create(
        model="claude-opus-4-8",
        max_tokens=1,
        messages=[{"role": "user", "content": "hi"}],
    )
except Exception as exc:
    print(f"Anthropic key check failed: {exc}", file=sys.stderr)
    sys.exit(1)
PYEOF
    then
        echo "  Anthropic key: OK"
    else
        echo "  Anthropic key check failed — fix the key in .env and re-run ./install.sh"
        exit 1
    fi

    if NEWSAPI_KEY_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "https://newsapi.org/v2/top-headlines?country=us&pageSize=1&apiKey=$NEWSAPI_KEY"); [ "$NEWSAPI_KEY_CHECK" = "200" ]; then
        echo "  NewsAPI key: OK"
    else
        echo "  NewsAPI key check failed (HTTP $NEWSAPI_KEY_CHECK) — fix the key in .env and re-run ./install.sh"
        exit 1
    fi

    echo "Saved to .env"
fi

# --- 6. Schedule the daily run ---
# "cron" is macOS's built-in daily-alarm-clock system for running a
# command automatically at a set time, even with no one logged in to
# watch it happen.
SCHEDULE_TIME=$(.venv/bin/python3 -c "from config import load_config; print(load_config()['schedule_time'])")
echo "[6/7] Scheduling the daily $SCHEDULE_TIME run (cron)..."
chmod +x scripts/schedule.sh
scripts/schedule.sh "$SCHEDULE_TIME"

# --- 7. Catch-up agent (launchd) ---
# cron only fires at the exact scheduled minute — if the Mac is asleep
# then, it's simply skipped. "launchd" is macOS's more flexible scheduler;
# here it runs a quick check every 30 minutes ("did today's brief get made
# yet?") so a missed run still catches up shortly after the Mac wakes up.
echo "[7/7] Setting up the catch-up check (launchd)..."
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

FOLDER_NAME=$(.venv/bin/python3 -c "from config import load_config; print(load_config()['delivery']['folder_name'])")

echo ""
echo "=== Setup complete ==="
echo "Your first brief will generate automatically at $SCHEDULE_TIME (or within"
echo "~30 minutes of your Mac being awake after that), and will appear in:"
echo "  iCloud Drive > $FOLDER_NAME"
echo ""
echo "Want to generate one right now instead of waiting? Run:"
echo "  cd $PROJECT_DIR && .venv/bin/python3 main.py"
echo ""
echo "To change coins/schedule/delivery later, run: ./configure.sh"
echo "To remove everything this installed, run:      ./uninstall.sh"
