"""Render a saved brief (Markdown) as styled HTML and open it in the browser.

Usage: python3 view_brief.py [path-to-brief.md]
Defaults to today's brief if no path is given.
"""

import sys
import webbrowser
from datetime import date
from pathlib import Path

import markdown

REPORTS_DIR = Path(__file__).parent / "reports"

CSS = """
<style>
  body { max-width: 700px; margin: 40px auto; padding: 0 20px;
         font-family: -apple-system, sans-serif; line-height: 1.6; color: #222; }
  h1, h2 { border-bottom: 1px solid #ddd; padding-bottom: 6px; }
  code { background: #f4f4f4; padding: 2px 5px; border-radius: 4px; }
  hr { margin: 30px 0; border: none; border-top: 1px solid #ddd; }
</style>
"""


def render(md_path: Path) -> Path:
    html_body = markdown.markdown(md_path.read_text())
    html_path = md_path.with_suffix(".html")
    html_path.write_text(f"<html><head>{CSS}</head><body>{html_body}</body></html>")
    return html_path


def main() -> None:
    if len(sys.argv) > 1:
        md_path = Path(sys.argv[1])
    else:
        md_path = REPORTS_DIR / f"brief_{date.today().isoformat()}.md"

    if not md_path.exists():
        print(f"No brief found at {md_path}")
        sys.exit(1)

    html_path = render(md_path)
    webbrowser.open(f"file://{html_path.resolve()}")


if __name__ == "__main__":
    main()
