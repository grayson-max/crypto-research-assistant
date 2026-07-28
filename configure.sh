#!/bin/bash
# Change preferences (schedule time, delivery folder name) after install,
# without redoing venv/dependency/API-key setup. Run any time from the
# project folder:
#   ./configure.sh
#
# To change which coins are tracked, edit the "coins" section of
# config.json directly (see config.example.json for the shape each coin
# entry needs), then re-run this script so the cron schedule stays in sync.

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -f "config.json" ]; then
    echo "No config.json found — run ./install.sh first."
    exit 1
fi

echo "=== Crypto Research Brief — Configure ==="
echo ""
if [ -d "$HOME/Library/Mobile Documents/com~apple~CloudDocs" ]; then
    DELIVERY_LABEL="iCloud Drive"
else
    DELIVERY_LABEL="local — iCloud Drive isn't set up on this Mac"
fi
.venv/bin/python3 - "$DELIVERY_LABEL" <<'PYEOF'
import sys
from config import load_config

delivery_label = sys.argv[1]
c = load_config()
print("Current settings:")
print(f"  Coins tracked: {', '.join(c['coins'].keys())}")
print(f"  Schedule time: {c['schedule_time']}")
print(f"  Delivery folder ({delivery_label}): {c['delivery']['folder_name']}")
PYEOF
echo ""

CURRENT_TIME=$(.venv/bin/python3 -c "from config import load_config; print(load_config()['schedule_time'])")
CURRENT_FOLDER=$(.venv/bin/python3 -c "from config import load_config; print(load_config()['delivery']['folder_name'])")

read -rp "New schedule time [$CURRENT_TIME]: " NEW_TIME
NEW_TIME="${NEW_TIME:-$CURRENT_TIME}"

read -rp "New iCloud Drive folder name [$CURRENT_FOLDER]: " NEW_FOLDER
NEW_FOLDER="${NEW_FOLDER:-$CURRENT_FOLDER}"

.venv/bin/python3 - "$NEW_TIME" "$NEW_FOLDER" <<'PYEOF'
import sys
from config import load_config, save_config

schedule_time, folder_name = sys.argv[1], sys.argv[2]
config = load_config()
config["schedule_time"] = schedule_time
config["delivery"]["folder_name"] = folder_name
save_config(config)
PYEOF

echo "Updated config.json"

scripts/schedule.sh "$NEW_TIME"
chmod +x scripts/copy_guide.sh
scripts/copy_guide.sh "$NEW_FOLDER"

echo ""
if [ -d "$HOME/Library/Mobile Documents/com~apple~CloudDocs" ]; then
    echo "Done. Briefs will now be delivered to iCloud Drive > $NEW_FOLDER at $NEW_TIME daily."
else
    echo "Done. iCloud Drive doesn't look set up on this Mac, so briefs will be"
    echo "saved locally instead, in: $PROJECT_DIR/$NEW_FOLDER (at $NEW_TIME daily)."
fi
echo "(A copy of the setup/removal guide is saved there too.)"
