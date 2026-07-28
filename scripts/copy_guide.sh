#!/bin/bash
# Copies READ_ME_instructions.html into the same folder deliver.py writes
# briefs to, using the folder name passed as $1, so the setup/removal
# guide sits right alongside them — easy to find later even if the
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
ICLOUD_ROOT="$HOME/Library/Mobile Documents/com~apple~CloudDocs"

# Mirror deliver.py's own check exactly: this container only exists once
# iCloud Drive has actually been turned on for this Mac. mkdir -p would
# happily create it anyway as an ordinary local folder, which is real on
# disk but invisible in Finder's iCloud Drive sidebar — so check first
# rather than assume, and use the same local fallback deliver.py uses if
# it's not there, so the guide always lands next to the brief, not split
# across two different folders.
if [ -d "$ICLOUD_ROOT" ]; then
    DEST_DIR="$ICLOUD_ROOT/$FOLDER_NAME"
else
    DEST_DIR="$PROJECT_DIR/$FOLDER_NAME"
fi

mkdir -p "$DEST_DIR"
cp "$PROJECT_DIR/READ_ME_instructions.html" "$DEST_DIR/READ_ME_instructions.html"
