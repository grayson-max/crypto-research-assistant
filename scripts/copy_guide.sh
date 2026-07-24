#!/bin/bash
# Copies READ_ME_instructions.html into the iCloud Drive delivery folder,
# using the folder name passed as $1, so the setup/removal guide sits
# right alongside the delivered briefs — easy to find later even if the
# project folder itself is forgotten.
#
# Shared by install.sh (first-time setup) and configure.sh (in case the
# delivery folder is renamed later) so this only lives in one place.
#
# Usage: scripts/copy_guide.sh CryptoBriefs

set -e

FOLDER_NAME="$1"
if [ -z "$FOLDER_NAME" ]; then
    echo "Usage: scripts/copy_guide.sh <delivery-folder-name>" >&2
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/$FOLDER_NAME"

mkdir -p "$ICLOUD_DIR"
cp "$PROJECT_DIR/READ_ME_instructions.html" "$ICLOUD_DIR/READ_ME_instructions.html"
