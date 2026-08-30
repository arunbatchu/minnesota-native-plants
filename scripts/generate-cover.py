#!/usr/bin/env python3
"""Regenerate docs/img/cover.png.

The cover art is the book's own learning graph: 289 concepts coloured by
taxonomy, sized by how many other concepts connect to them, laid out by
vis-network's physics engine. Utilitarian and beautiful — it carries the real
structure of the book rather than decorating it.

Requires: playwright (pip install playwright), Pillow, and Google Chrome.
Run from the repo root:  python3 scripts/generate-cover.py
"""
import functools
import http.server
import os
import shutil
import socketserver
import tempfile
import threading

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT = "/System/Library/Fonts/Avenir Next.ttc"
W, H = 1731, 909
BG = (250, 250, 246)
INK = (26, 38, 28)
GREEN = (46, 125, 50)        # the book's primary, #2e7d32
GOLD = (198, 156, 42)        # Bree's stripe
MUTED = (104, 116, 106)
FAINT = (146, 156, 146)

work = tempfile.mkdtemp()
shutil.copy(f"{ROOT}/scripts/cover-graph-render.html", f"{work}/graphcover.html")
shutil.copy(f"{ROOT}/docs/learning-graph/learning-graph.json", f"{work}/graph.json")

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=work)
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
srv.RequestHandlerClass.log_message = lambda *a, **k: None
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": W, "height": H},
                        device_scale_factor=2, color_scheme="light")
        pg.goto(f"http://127.0.0.1:{port}/graphcover.html")
        pg.wait_for_function("window.__ready===true", timeout=120000)
        pg.wait_for_timeout(1200)
        pg.screenshot(path=f"{work}/art.png", omit_background=True,
                      clip={"x": 0, "y": 0, "width": W, "height": H})
        b.close()
finally:
    srv.shutdown()


def font(size, index):
    return ImageFont.truetype(FONT, size, index=index)   # 0=Bold 5=Medium 7=Regular


art = Image.open(f"{work}/art.png").convert("RGBA").resize((W, H), Image.LANCZOS)
big = art.resize((int(W * 1.05), int(H * 1.05)), Image.LANCZOS)
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
layer.paste(big, (int(W * .28) - (big.width - W) // 2, -(big.height - H) // 2), big)

# Fade the art out under the title block so the type stays legible.
px = layer.load()
for x in range(int(W * .46)):
    a = max(0.0, min(1.0, (x - W * .12) / (W * .34)))
    a = a * a * (3 - 2 * a)                      # smoothstep
    for y in range(H):
        r, g, bl, al = px[x, y]
        if al:
            px[x, y] = (r, g, bl, int(al * a))

cover = Image.alpha_composite(Image.new("RGBA", (W, H), BG + (255,)), layer).convert("RGB")
d = ImageDraw.Draw(cover)

x0 = 112
d.text((x0, 286), "Minnesota", font=font(96, 0), fill=INK)
d.text((x0, 390), "Native Plants", font=font(96, 0), fill=GREEN)
d.line([(x0, 534), (x0 + 118, 534)], fill=GOLD, width=5)

y = 574
for line in ["Prairie, woodland, wetland — the plants",
             "that belong here, and why it matters."]:
    d.text((x0, y), line, font=font(38, 5), fill=MUTED)
    y += 52

d.text((x0, H - 96),
       "17 chapters  ·  289 concepts  ·  22 interactive simulations  ·  211 species",
       font=font(24, 7), fill=FAINT)

# Bree, bottom right, small — she is the guide, not the subject.
bree_path = f"{ROOT}/docs/img/mascot/neutral.png"
if os.path.exists(bree_path):
    bree = Image.open(bree_path).convert("RGBA")
    bree.thumbnail((190, 190), Image.LANCZOS)
    cover.paste(bree, (W - bree.width - 84, H - bree.height - 70), bree)

out = f"{ROOT}/docs/img/cover.png"
cover.save(out, optimize=True)
print(f"wrote {out}  {cover.size}  {os.path.getsize(out)//1024}KB")
