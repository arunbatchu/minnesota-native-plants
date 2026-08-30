#!/usr/bin/env python3
"""Render the chapters' inline bloom-chart SVGs to PNG for the print booklet.

The charts live inline in the chapter markdown so the website needs no image
files. ReportLab cannot embed SVG, so the print path re-renders the same markup
through Chrome. One source, two outputs — the printed chart cannot drift from
the web one.

Usage:
    python3 scripts/bloom-charts-png.py
"""
import re
import sys
import tempfile
from pathlib import Path

CHAPTERS = {
    "03-prairie-plants-grasslands": "bloom-prairie",
    "04-woodland-forest-plants": "bloom-woodland",
    "05-wetland-shoreline-plants": "bloom-wetland",
}
OUT = Path("docs/downloads/img")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def main():
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp())
    jobs = []

    for chapter, name in CHAPTERS.items():
        md = Path("docs/chapters") / chapter / "index.md"
        m = re.search(r"<svg.*?</svg>", md.read_text(), re.S)
        if not m:
            print(f"  no chart found in {chapter} — run bloom-charts.py first",
                  file=sys.stderr)
            continue
        # White ground and dark ink: this is going onto paper, so the
        # currentColor the web version inherits has to be pinned here.
        html = work / f"{name}.html"
        html.write_text(
            "<!doctype html><meta charset=utf-8>"
            "<body style='margin:0;padding:20px;background:#fff;color:#1f2a1a'>"
            + m.group(0) + "</body>")
        jobs.append((html, OUT / f"{name}.png"))

    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for html, png in jobs:
            pg = b.new_page(viewport={"width": 1100, "height": 900},
                            device_scale_factor=2)
            pg.goto(html.resolve().as_uri())
            pg.wait_for_timeout(400)
            pg.locator("svg").screenshot(path=str(png))
            pg.close()
            print(f"  {png}  {png.stat().st_size // 1024}KB")
        b.close()

    print(f"\n{len(jobs)} chart(s) rendered for print")
    return 0


if __name__ == "__main__":
    sys.exit(main())
