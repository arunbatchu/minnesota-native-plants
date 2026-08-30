#!/usr/bin/env python3
"""Screenshot every MicroSim for the visual catalog.

Drives the *installed* Google Chrome through Playwright, so nothing has to be
downloaded. Each sim's main.html is loaded at the iframe height declared in its
own index.md, given a moment to finish drawing, and clipped to that box.

Sims are served over a throwaway HTTP server rooted at docs/, NOT opened as
file:// URLs. That matters: graph-viewer fetches
../../learning-graph/learning-graph.json, and browsers block fetch() on
file:// for CORS reasons. Shot from disk it photographs its own error message.

Usage:
    python3 scripts/capture-sims.py                 # all sims, skip existing
    python3 scripts/capture-sims.py --force         # re-shoot everything
    python3 scripts/capture-sims.py bloom-calendar  # just one
"""
import contextlib
import functools
import http.server
import re
import socketserver
import sys
import threading
from pathlib import Path

SIMS = Path("docs/sims")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WIDTH = 900
DEFAULT_HEIGHT = 600
SETTLE_MS = 2500


def iframe_height(sim_dir):
    """Read the height the sim's own page asks for."""
    index = sim_dir / "index.md"
    if not index.exists():
        return DEFAULT_HEIGHT
    m = re.search(r'height="(\d+)px"', index.read_text())
    return int(m.group(1)) if m else DEFAULT_HEIGHT


@contextlib.contextmanager
def serve(root):
    """Serve `root` on an ephemeral port for the life of the block."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(root))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        httpd.RequestHandlerClass.log_message = lambda *a, **k: None
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            yield f"http://127.0.0.1:{httpd.server_address[1]}"
        finally:
            httpd.shutdown()


def main(argv):
    from playwright.sync_api import sync_playwright

    force = "--force" in argv
    wanted = [a for a in argv if not a.startswith("-")]

    dirs = sorted(d for d in SIMS.iterdir()
                  if d.is_dir() and (d / "main.html").exists())
    if wanted:
        dirs = [d for d in dirs if d.name in wanted]

    shot = skipped = failed = 0
    with serve(SIMS.parent) as base, sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME)
        for d in dirs:
            out = d / f"{d.name}.png"
            if out.exists() and not force:
                print(f"  cached  {d.name}")
                skipped += 1
                continue
            h = iframe_height(d)
            try:
                page = browser.new_page(viewport={"width": WIDTH, "height": h})
                page.goto(f"{base}/sims/{d.name}/main.html",
                          wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(SETTLE_MS)
                page.screenshot(path=str(out),
                                clip={"x": 0, "y": 0, "width": WIDTH, "height": h})
                page.close()
                kb = out.stat().st_size // 1024
                print(f"  shot    {d.name}  {WIDTH}x{h}  {kb}KB")
                shot += 1
            except Exception as e:                   # noqa: BLE001
                print(f"  FAILED  {d.name}: {type(e).__name__}: {str(e)[:120]}",
                      file=sys.stderr)
                failed += 1
        browser.close()

    print(f"\n{shot} shot, {skipped} cached, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
