#!/bin/bash
# One-line installer for the Crypto Research Brief pipeline.
#
# Paste this whole line into Terminal:
#   curl -fsSL https://raw.githubusercontent.com/grayson-max/crypto-research-assistant/main/bootstrap.sh | bash
#
# What this does, in order:
#   1. Asks for your two API keys and checks each one works, before
#      touching anything else — so a bad key is caught immediately,
#      not after everything else is already set up.
#   2. Downloads the project to ~/crypto_research_assistant.
#   3. Hands off to install.sh for the rest (Python environment,
#      dependencies, daily schedule). install.sh is safe to run again
#      later on its own — see ./configure.sh to change coins/schedule/
#      delivery, or ./uninstall.sh to remove everything.

set -e

REPO_URL="https://github.com/grayson-max/crypto-research-assistant.git"
INSTALL_DIR="$HOME/crypto_research_assistant"

echo "=== Crypto Research Brief — Setup ==="
echo ""

if ! command -v git >/dev/null 2>&1; then
    echo "Git isn't installed yet. macOS should now be prompting you to install"
    echo "it (a small \"Install Command Line Developer Tools\" popup) — click"
    echo "Install, wait for it to finish, then paste this same command again."
    git --version >/dev/null 2>&1 || true
    exit 1
fi

if [ -f "$INSTALL_DIR/.env" ]; then
    echo "Found an existing install with saved API keys at $INSTALL_DIR —"
    echo "keeping those, no need to re-enter them."
    echo ""
    SKIP_KEYS=1
else
    echo "First, two API keys. Nothing is downloaded or installed until both are"
    echo "confirmed working, so you'll find out right away if something's wrong"
    echo "instead of after everything else is already set up."
    echo ""
    echo "Key 1 — Anthropic (writes the brief; paid, billed per use, typically a"
    echo "  few cents a month for one brief a day):"
    echo "  https://console.anthropic.com/settings/keys"
    echo "Key 2 — NewsAPI (finds headlines; free):"
    echo "  https://newsapi.org/register"
    echo ""

    while true; do
        read -rp "Paste your Anthropic API key: " ANTHROPIC_KEY
        echo "  Checking..."
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://api.anthropic.com/v1/messages \
            -H "x-api-key: $ANTHROPIC_KEY" \
            -H "anthropic-version: 2023-06-01" \
            -H "content-type: application/json" \
            -d '{"model":"claude-opus-4-8","max_tokens":1,"messages":[{"role":"user","content":"hi"}]}')
        if [ "$HTTP_CODE" = "200" ]; then
            echo "  Anthropic key: OK"
            break
        else
            echo "  That key didn't work (HTTP $HTTP_CODE). Double-check it and try again."
        fi
    done

    while true; do
        read -rp "Paste your NewsAPI key: " NEWSAPI_KEY
        echo "  Checking..."
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://newsapi.org/v2/top-headlines?country=us&pageSize=1&apiKey=$NEWSAPI_KEY")
        if [ "$HTTP_CODE" = "200" ]; then
            echo "  NewsAPI key: OK"
            break
        else
            echo "  That key didn't work (HTTP $HTTP_CODE). Double-check it and try again."
        fi
    done

    echo ""
    echo "Both keys confirmed."
    echo ""
fi

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Found an existing install at $INSTALL_DIR — updating it."
    git -C "$INSTALL_DIR" pull --quiet
elif [ -e "$INSTALL_DIR" ]; then
    echo "$INSTALL_DIR already exists and isn't a copy of this project."
    echo "Move or rename it, then paste this command again."
    exit 1
else
    echo "Downloading the project to $INSTALL_DIR ..."
    git clone --quiet "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

if [ -z "$SKIP_KEYS" ]; then
    cat > .env <<EOF
ANTHROPIC_API_KEY=$ANTHROPIC_KEY
NEWSAPI_API_KEY=$NEWSAPI_KEY
EOF
fi

if [ ! -f config.json ]; then
    cp config.example.json config.json
    echo "Using default settings: BTC/ETH/SOL, 8:00 AM daily, delivered to"
    echo "iCloud Drive > CryptoBriefs. Change any of this later with:"
    echo "  cd ~/crypto_research_assistant && ./configure.sh"
fi

chmod +x install.sh configure.sh uninstall.sh
echo ""
./install.sh
