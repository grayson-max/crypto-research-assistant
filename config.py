"""Load per-install preferences (which coins to track, delivery schedule,
delivery destination) from config.json, falling back to config.example.json's
defaults if a user hasn't run install.sh / configure.sh yet.

config.json is git-ignored (like .env) — every independent install gets its
own copy, same pattern as API keys."""

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
CONFIG_PATH = PROJECT_DIR / "config.json"
EXAMPLE_PATH = PROJECT_DIR / "config.example.json"


def load_config() -> dict:
    path = CONFIG_PATH if CONFIG_PATH.exists() else EXAMPLE_PATH
    return json.loads(path.read_text())


def save_config(config: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n")
