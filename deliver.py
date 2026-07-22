"""Deliver a finished brief to iCloud Drive so it syncs to the user's phone,
and fire a native macOS notification. No credentials required — relies on
iCloud Drive already being signed in on the Mac running the pipeline."""

import subprocess
from pathlib import Path

import markdown

ICLOUD_DIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/CryptoBriefs"

CSS = """
<style>
  body { max-width: 700px; margin: 40px auto; padding: 0 20px;
         font-family: -apple-system, sans-serif; line-height: 1.6; color: #222; }
  h1, h2 { border-bottom: 1px solid #ddd; padding-bottom: 6px; }
  code { background: #f4f4f4; padding: 2px 5px; border-radius: 4px; }
  hr { margin: 30px 0; border: none; border-top: 1px solid #ddd; }
</style>
"""


def deliver_to_icloud(brief_md: str, filename_stem: str) -> Path:
    """Render the brief as styled HTML and save it into the iCloud Drive
    folder, which syncs to any of the user's other Apple devices."""
    ICLOUD_DIR.mkdir(parents=True, exist_ok=True)
    html_body = markdown.markdown(brief_md)
    html_path = ICLOUD_DIR / f"{filename_stem}.html"
    html_path.write_text(f"<html><head>{CSS}</head><body>{html_body}</body></html>")
    return html_path


def notify_done(message: str) -> None:
    """Show a native macOS notification. Fails silently if there's no GUI session."""
    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{message}" with title "Crypto Research Brief Ready"',
        ],
        check=False,
        capture_output=True,
    )
