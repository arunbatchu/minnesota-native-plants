"""
Front-yard Oak Savanna Edge — design overlay renderer.
Site: 8547 Crane Dance Trail, Eden Prairie MN.

Loads site photos, draws translucent planting zones, numbered species markers,
a path, a bench, sun arrows, and a legend block with bloom calendar.
Output goes to annotated/.

Coordinates are tunable via the constants near the top — re-render is one line.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
PHOTOS = ROOT / "photos"
OUT = ROOT / "annotated"
OUT.mkdir(exist_ok=True)

# --------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------
PHOTO_W, PHOTO_H = 2400, 1800
LEGEND_H = 1200
CANVAS_W, CANVAS_H = PHOTO_W, PHOTO_H + LEGEND_H

# --------------------------------------------------------------------------
# Color palette  (RGBA)
# --------------------------------------------------------------------------
C = {
    "z1_woody":     (139,  69,  19, 100),   # saddle brown — backbone
    "z2_tall":      (218, 165,  32, 100),   # goldenrod — tall forbs
    "z3_mid":       (186,  85, 211, 100),   # orchid — mid drifts
    "z4_low":       ( 60, 179, 113, 100),   # sea green — low edge
    "z5_swale":     ( 70, 130, 180, 110),   # steel blue — swale
    "path":         (245, 222, 179, 230),   # wheat — stepper path
    "path_stroke":  (130, 100,  60, 255),
    "bench":        (101,  67,  33, 255),   # walnut — bench
    "marker_fill":  (255, 255, 255, 245),
    "marker_stroke":( 30,  30,  30, 255),
    "marker_text":  ( 30,  30,  30, 255),
    "sun":          (255, 200,   0, 230),
    "sightline":    ( 80, 130, 200, 220),
    "legend_bg":    (252, 248, 240, 255),
    "title":        ( 40,  70,  35, 255),
    "subtitle":     ( 90, 100,  70, 255),
    "body":         ( 40,  40,  40, 255),
    "rule":         (180, 170, 150, 255),
    "accent":       (139,  69,  19, 255),
}

# --------------------------------------------------------------------------
# Geometry — coordinates in the resized 2400x1800 photo
# Photo 02 (corner-three-quarter): looking at house from front-left lawn.
# Right side of photo = east (front porch + arborvitae).
# Left side of photo  = west (where bed wraps to side; serviceberry goes here).
# --------------------------------------------------------------------------

# --- Coordinates for the head-on view (01-front-existing.jpg) ---
# Photo shows the bed straight-on. West (where serviceberry goes) = LEFT.
# East (porch / dry-creek swale) = RIGHT. Bay window is centered.

ZONES = [
    {
        "id": 1,
        "name": "Backbone — small tree & shrubs",
        "color": "z1_woody",
        "polygon": [(280, 880), (2050, 880), (2050, 1080), (280, 1080)],
    },
    {
        "id": 2,
        "name": "Tall forbs & grasses (3–5 ft)",
        "color": "z2_tall",
        "polygon": [(280, 1080), (2050, 1080), (2030, 1220), (260, 1220)],
    },
    {
        "id": 3,
        "name": "Mid drifts (2–3 ft)",
        "color": "z3_mid",
        "polygon": [(260, 1220), (2030, 1220), (1990, 1360), (220, 1360)],
    },
    {
        "id": 4,
        "name": "Low edge (under 2 ft)",
        "color": "z4_low",
        "polygon": [(220, 1360), (1990, 1360), (1900, 1530), (180, 1530)],
    },
    {
        "id": 5,
        "name": "Vegetated swale — sedge meadow",
        "color": "z5_swale",
        "polygon": [(2050, 1280), (2380, 1300), (2390, 1640),
                    (2080, 1660), (2000, 1480)],
    },
]

# Stepping-stone path: enters from concrete walkway right edge,
# winds across front of bed, terminates at bench pocket west third.
PATH = [(2280, 1640), (1950, 1560), (1500, 1490),
        (1000, 1450), (650, 1430), (450, 1410)]

# Bench in the west-third pocket
BENCH = (420, 1380)
BENCH_SIZE = (110, 30)

# Sun arc (south-facing) — sun is behind the camera; place icon top-left
# with a "south sun" label
SUN_POS = (180, 180)
SUN_R = 55

# Indoor sightline (from bay window through the bed to cul-de-sac)
# Bay window is in the upper center of the head-on view; sightline
# extends down through the bed to the foreground lawn (toward photographer)
SIGHTLINE_FROM = (1380, 700)
SIGHTLINE_TO = (1380, 1700)

# Numbered markers (id, x, y, abbrev) — abbreviations match SPECIES dict
MARKERS = [
    (1,  450,  950, "SVB"),   # Serviceberry — west anchor
    (2, 1000, 1000, "NIN"),   # Ninebark left of bay window (kept low for view)
    (3, 1900, 1000, "NIN"),   # Ninebark right of bay window
    (4,  300, 1000, "GDW"),   # Gray Dogwood — behind serviceberry
    (5,  750, 1140, "BAP"),   # Baptisia
    (6, 1400, 1150, "BBM"),   # Wild Bergamot
    (7, 1850, 1150, "ASR"),   # Smooth Blue Aster
    (8,  600, 1290, "LUP"),   # Wild Lupine
    (9, 1100, 1300, "PCF"),   # Purple Coneflower
    (10, 1700, 1300, "BMW"),  # Butterfly Milkweed
    (11, 900, 1430, "LBS"),   # Little Bluestem
    (12, 1500, 1450, "PSM"),  # Prairie Smoke
    (13, 250, 1450, "PDS"),   # Prairie Dropseed (front-edge ribbon)
    (14, 2150, 1430, "BFI"),  # Blue Flag Iris (swale wet pocket)
    (15, 2240, 1560, "TSC"),  # Tussock Sedge (swale channel)
]

SPECIES = {
    "SVB": ("Serviceberry",         "Amelanchier laevis",       "small tree"),
    "NIN": ("Ninebark",             "Physocarpus opulifolius",  "shrub"),
    "GDW": ("Gray Dogwood",         "Cornus racemosa",          "shrub"),
    "BAP": ("False Blue Indigo",    "Baptisia australis",       "tall forb"),
    "BBM": ("Wild Bergamot",        "Monarda fistulosa",        "mid forb"),
    "ASR": ("Smooth Blue Aster",    "Symphyotrichum laeve",     "mid forb"),
    "LUP": ("Wild Lupine",          "Lupinus perennis",         "mid forb"),
    "PCF": ("Purple Coneflower",    "Echinacea purpurea",       "mid forb"),
    "BMW": ("Butterfly Milkweed",   "Asclepias tuberosa",       "low forb"),
    "LBS": ("Little Bluestem",      "Schizachyrium scoparium",  "grass"),
    "PSM": ("Prairie Smoke",        "Geum triflorum",           "groundcover"),
    "PDS": ("Prairie Dropseed",     "Sporobolus heterolepis",   "grass"),
    "BFI": ("Blue Flag Iris",       "Iris versicolor",          "swale wet"),
    "TSC": ("Tussock Sedge",        "Carex stricta",            "swale center"),
}

# Bloom calendar — month abbrev + color reflecting peak palette
BLOOM = [
    ("Apr", (232, 224, 210)),   # serviceberry white
    ("May", (155, 124, 184)),   # lupine/baptisia/prairie smoke purple
    ("Jun", (240, 240, 240)),   # ninebark/dogwood white
    ("Jul", (198, 109, 168)),   # bergamot/coneflower pink
    ("Aug", (212,  72, 138)),   # coneflower/swamp milkweed
    ("Sep", ( 90, 127, 184)),   # asters blue
    ("Oct", (168,  90,  58)),   # bluestem copper
    ("Nov", (138, 106,  74)),   # winter structure
    ("Dec", (122,  90,  74)),
    ("Jan", (122,  90,  74)),
    ("Feb", (122,  90,  74)),
    ("Mar", (154, 138, 122)),
]

# --------------------------------------------------------------------------
# Fonts
# --------------------------------------------------------------------------

def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        ("/System/Library/Fonts/Helvetica.ttc", 1 if bold else 0),
        ("/System/Library/Fonts/Avenir.ttc",    7 if bold else 0),
        ("/System/Library/Fonts/Geneva.ttf",    0),
        ("/Library/Fonts/Arial Unicode.ttf",    0),
    ]
    for path, idx in candidates:
        try:
            return ImageFont.truetype(path, size, index=idx)
        except (OSError, ValueError):
            continue
    return ImageFont.load_default()


# --------------------------------------------------------------------------
# Drawing helpers
# --------------------------------------------------------------------------

def draw_zone(overlay: ImageDraw.ImageDraw, zone: dict) -> None:
    overlay.polygon(zone["polygon"], fill=C[zone["color"]])
    # subtle stroke
    pts = zone["polygon"] + [zone["polygon"][0]]
    overlay.line(pts, fill=(*C[zone["color"]][:3], 200), width=3)


def draw_path(overlay: ImageDraw.ImageDraw, points: list[tuple[int, int]]) -> None:
    # Wide tan band first
    overlay.line(points, fill=C["path"], width=42, joint="curve")
    # Dashed darker stroke down the middle
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        # crude dash by drawing short segments along the line
        steps = 12
        for s in range(0, steps, 2):
            t1 = s / steps
            t2 = (s + 1) / steps
            overlay.line(
                [(x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1),
                 (x1 + (x2 - x1) * t2, y1 + (y2 - y1) * t2)],
                fill=C["path_stroke"], width=4,
            )


def draw_bench(overlay: ImageDraw.ImageDraw, pos: tuple[int, int],
               size: tuple[int, int]) -> None:
    cx, cy = pos
    w, h = size
    # bench seat
    overlay.rectangle(
        [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
        fill=C["bench"], outline=(40, 25, 15, 255), width=2,
    )
    # legs hint
    overlay.rectangle([cx - w // 2 + 6, cy + h // 2,
                       cx - w // 2 + 14, cy + h // 2 + 16], fill=C["bench"])
    overlay.rectangle([cx + w // 2 - 14, cy + h // 2,
                       cx + w // 2 - 6, cy + h // 2 + 16], fill=C["bench"])
    # label
    f = load_font(22, bold=True)
    overlay.text((cx - 60, cy + h // 2 + 22), "BENCH", font=f,
                 fill=(40, 25, 15, 255))


def draw_marker(overlay: ImageDraw.ImageDraw, x: int, y: int,
                num: int, abbrev: str) -> None:
    r = 26
    overlay.ellipse(
        [x - r, y - r, x + r, y + r],
        fill=C["marker_fill"], outline=C["marker_stroke"], width=3,
    )
    f = load_font(24, bold=True)
    text = str(num)
    bbox = overlay.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    overlay.text(
        (x - tw // 2, y - th // 2 - 3),
        text, font=f, fill=C["marker_text"],
    )
    # abbreviation tag below circle
    f2 = load_font(18, bold=True)
    bbox2 = overlay.textbbox((0, 0), abbrev, font=f2)
    aw = bbox2[2] - bbox2[0]
    pad = 4
    overlay.rectangle(
        [x - aw // 2 - pad, y + r + 2,
         x + aw // 2 + pad, y + r + 2 + 22],
        fill=(255, 255, 255, 230), outline=C["marker_stroke"], width=1,
    )
    overlay.text((x - aw // 2, y + r + 4), abbrev, font=f2,
                 fill=C["marker_text"])


def draw_sun(overlay: ImageDraw.ImageDraw, pos: tuple[int, int], r: int) -> None:
    cx, cy = pos
    overlay.ellipse([cx - r, cy - r, cx + r, cy + r], fill=C["sun"],
                    outline=(200, 150, 0, 255), width=3)
    # rays
    import math
    for i in range(8):
        a = i * math.pi / 4
        x1 = cx + (r + 10) * math.cos(a)
        y1 = cy + (r + 10) * math.sin(a)
        x2 = cx + (r + 30) * math.cos(a)
        y2 = cy + (r + 30) * math.sin(a)
        overlay.line([(x1, y1), (x2, y2)], fill=C["sun"], width=5)
    f = load_font(22, bold=True)
    overlay.text((cx - 70, cy + r + 32), "SOUTH SUN", font=f,
                 fill=(160, 110, 0, 255))


def draw_arrow(overlay: ImageDraw.ImageDraw,
               start: tuple[int, int], end: tuple[int, int],
               color: tuple[int, int, int, int], width: int = 6,
               label: str | None = None) -> None:
    overlay.line([start, end], fill=color, width=width)
    # arrowhead
    import math
    x1, y1 = start
    x2, y2 = end
    angle = math.atan2(y2 - y1, x2 - x1)
    head = 22
    spread = math.pi / 7
    p1 = (x2 - head * math.cos(angle - spread),
          y2 - head * math.sin(angle - spread))
    p2 = (x2 - head * math.cos(angle + spread),
          y2 - head * math.sin(angle + spread))
    overlay.polygon([(x2, y2), p1, p2], fill=color)
    if label:
        f = load_font(20, bold=True)
        mx = (x1 + x2) // 2 + 12
        my = (y1 + y2) // 2
        overlay.text((mx, my), label, font=f, fill=color[:3] + (255,))


# --------------------------------------------------------------------------
# Legend
# --------------------------------------------------------------------------

def draw_legend(canvas: Image.Image, top: int) -> None:
    """Render the legend block below the photo."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    legend_top = top
    legend_left = 0

    # Background
    draw.rectangle(
        [0, legend_top, CANVAS_W, CANVAS_H],
        fill=C["legend_bg"],
    )
    # top rule
    draw.line([(0, legend_top), (CANVAS_W, legend_top)],
              fill=C["accent"], width=4)

    # Title block
    pad = 40
    f_title = load_font(48, bold=True)
    f_subtitle = load_font(26, bold=False)
    f_meta = load_font(20, bold=False)

    draw.text(
        (pad, legend_top + 30),
        "Front-Yard Oak Savanna Edge",
        font=f_title, fill=C["title"],
    )
    draw.text(
        (pad, legend_top + 90),
        "8547 Crane Dance Trail · Eden Prairie MN · USDA 4b/5a",
        font=f_subtitle, fill=C["subtitle"],
    )
    draw.text(
        (pad, legend_top + 124),
        "Restoring the pre-settlement Big Woods savanna of Hennepin County  ·  "
        "design grounded in Minnesota Native Plants textbook (Ch. 02, 06, 10)",
        font=f_meta, fill=C["body"],
    )

    rule_y = legend_top + 175
    draw.line([(pad, rule_y), (CANVAS_W - pad, rule_y)],
              fill=C["rule"], width=2)

    # === LEFT COLUMN: Zone color key ===
    col_left_x = pad
    col_y = rule_y + 25
    f_h = load_font(28, bold=True)
    f_b = load_font(22, bold=False)
    f_sm = load_font(20, bold=False)

    draw.text((col_left_x, col_y), "PLANTING ZONES", font=f_h,
              fill=C["accent"])
    col_y += 45

    for z in ZONES:
        sw_x, sw_y, sw_w, sw_h = col_left_x, col_y, 36, 28
        draw.rectangle(
            [sw_x, sw_y, sw_x + sw_w, sw_y + sw_h],
            fill=C[z["color"]][:3] + (255,),
            outline=(60, 60, 60, 255), width=1,
        )
        draw.text(
            (sw_x + sw_w + 14, sw_y + 1),
            f"{z['id']}.  {z['name']}",
            font=f_b, fill=C["body"],
        )
        col_y += 42

    # Path + bench legend
    col_y += 8
    draw.line([(col_left_x, col_y), (col_left_x + 36, col_y)],
              fill=C["path_stroke"], width=8)
    draw.text((col_left_x + 50, col_y - 14), "Stepping-stone path",
              font=f_b, fill=C["body"])
    col_y += 36

    draw.rectangle([col_left_x, col_y, col_left_x + 36, col_y + 18],
                   fill=C["bench"])
    draw.text((col_left_x + 50, col_y - 4),
              "Bench pocket (west third, east-facing)",
              font=f_b, fill=C["body"])
    col_y += 38

    # === MIDDLE COLUMN: Numbered species list ===
    mid_x = pad + 720
    mid_y = rule_y + 25
    draw.text((mid_x, mid_y), "SPECIES KEY", font=f_h, fill=C["accent"])
    mid_y += 45

    row_h = 56  # taller rows so common name + sci name don't overlap
    half = (len(MARKERS) + 1) // 2
    for i, (num, _x, _y, abbrev) in enumerate(MARKERS):
        col = i // half
        row = i % half
        sx = mid_x + col * 400
        sy = mid_y + row * row_h
        # circle
        cr = 14
        draw.ellipse(
            [sx, sy, sx + cr * 2, sy + cr * 2],
            fill=C["marker_fill"], outline=C["marker_stroke"], width=2,
        )
        f_num = load_font(18, bold=True)
        nstr = str(num)
        nb = draw.textbbox((0, 0), nstr, font=f_num)
        nw = nb[2] - nb[0]
        nh = nb[3] - nb[1]
        draw.text(
            (sx + cr - nw // 2, sy + cr - nh // 2 - 2),
            nstr, font=f_num, fill=C["marker_text"],
        )
        # name
        common, sci, _kind = SPECIES[abbrev]
        draw.text((sx + 38, sy - 2), common, font=f_b, fill=C["body"])
        f_it = load_font(18, bold=False)
        draw.text((sx + 38, sy + 24), sci, font=f_it,
                  fill=(100, 80, 60, 255))

    # === RIGHT COLUMN: Bloom calendar strip ===
    right_x = pad + 720 + 760 + 20
    right_y = rule_y + 25
    if right_x + 280 > CANVAS_W - pad:
        # If too wide, stack below middle column instead
        right_x = pad
        right_y = mid_y + half * 36 + 30

    draw.text((right_x, right_y), "BLOOM CALENDAR", font=f_h,
              fill=C["accent"])
    right_y += 45

    # 12 bars stacked horizontally
    bar_w = 64
    bar_h = 90
    gap = 4
    for i, (m, color) in enumerate(BLOOM):
        bx = right_x + i * (bar_w + gap)
        draw.rectangle(
            [bx, right_y, bx + bar_w, right_y + bar_h],
            fill=color + (255,),
            outline=(120, 110, 90, 255), width=1,
        )
        f_m = load_font(18, bold=True)
        mb = draw.textbbox((0, 0), m, font=f_m)
        mw = mb[2] - mb[0]
        # month label below
        draw.text(
            (bx + (bar_w - mw) // 2, right_y + bar_h + 6),
            m, font=f_m,
            fill=(60, 60, 60, 255),
        )

    right_y += bar_h + 36
    f_caption = load_font(18, bold=False)
    f_caption_b = load_font(18, bold=True)
    rows = [
        ("Spring", "Serviceberry → Lupine, Baptisia, Prairie Smoke"),
        ("Summer", "Bergamot, Coneflower, Butterfly Milkweed"),
        ("Fall",   "Smooth Blue Aster, Cardinal Flower, copper Bluestem"),
        ("Winter", "exfoliating Ninebark bark, Bluestem plumes, dogwood berries"),
    ]
    for label, text in rows:
        draw.text((right_x, right_y), label, font=f_caption_b,
                  fill=C["accent"])
        draw.text((right_x + 80, right_y), text, font=f_caption,
                  fill=C["body"])
        right_y += 28

    # Footer
    foot_y = CANVAS_H - 60
    draw.line([(pad, foot_y - 12), (CANVAS_W - pad, foot_y - 12)],
              fill=C["rule"], width=1)
    f_foot = load_font(18, bold=False)
    draw.text(
        (pad, foot_y),
        "Lot 0.36 ac · Parcel 1311622340067 · pre-settlement: bur oak savanna · "
        "soil: Hayden/Lester loam (Hennepin moraine) · full sun, south face",
        font=f_foot, fill=C["subtitle"],
    )


# --------------------------------------------------------------------------
# Top-level render
# --------------------------------------------------------------------------

def render_primary() -> Path:
    src = PHOTOS / "01-front-existing.jpg"
    photo = Image.open(src).convert("RGBA")
    photo = photo.resize((PHOTO_W, PHOTO_H), Image.LANCZOS)

    # Canvas with extra space for legend below
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255, 255, 255, 255))
    canvas.paste(photo, (0, 0))

    # Translucent overlay for zones, path, etc.
    overlay = Image.new("RGBA", (PHOTO_W, PHOTO_H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay, "RGBA")

    for zone in ZONES:
        draw_zone(od, zone)

    draw_path(od, PATH)

    # Sightline first, behind markers
    draw_arrow(
        od, SIGHTLINE_FROM, SIGHTLINE_TO,
        color=C["sightline"], width=5,
        label="indoor sightline preserved",
    )

    draw_sun(od, SUN_POS, SUN_R)

    # Bench
    draw_bench(od, BENCH, BENCH_SIZE)

    # Markers last (on top)
    for num, x, y, abbrev in MARKERS:
        draw_marker(od, x, y, num, abbrev)

    # Composite
    canvas.alpha_composite(overlay, (0, 0))

    # Legend
    draw_legend(canvas, PHOTO_H)

    out = OUT / "01-front-design-overlay.jpg"
    canvas.convert("RGB").save(out, quality=92)
    return out


def render_sightline() -> Path:
    """Annotate the bay-window interior view to show the preserved sightline."""
    src = PHOTOS / "08-bay-window-interior.jpg"
    photo = Image.open(src).convert("RGBA")
    photo = photo.resize((PHOTO_W, PHOTO_H), Image.LANCZOS)

    canvas = Image.new("RGBA", (PHOTO_W, PHOTO_H + 280), (255, 255, 255, 255))
    canvas.paste(photo, (0, 0))

    overlay = Image.new("RGBA", (PHOTO_W, PHOTO_H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay, "RGBA")

    # Translucent green band where the new low-height central planting goes
    od.polygon(
        [(200, 1450), (2200, 1400), (2200, 1750), (200, 1750)],
        fill=(60, 179, 113, 90),
    )
    od.text(
        (700, 1500),
        "low planting (under 30\") preserves view",
        font=load_font(34, bold=True),
        fill=(30, 80, 30, 255),
    )

    # Arrow showing the sightline through the window
    draw_arrow(
        od, (1200, 200), (1200, 1380),
        color=(60, 110, 200, 220),
        width=7,
        label="primary indoor view",
    )

    canvas.alpha_composite(overlay, (0, 0))

    # Caption strip below
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle([0, PHOTO_H, PHOTO_W, PHOTO_H + 280],
                   fill=C["legend_bg"])
    draw.line([(0, PHOTO_H), (CANVAS_W, PHOTO_H)],
              fill=C["accent"], width=3)
    f_t = load_font(36, bold=True)
    f_b = load_font(22, bold=False)
    pad = 40
    draw.text((pad, PHOTO_H + 30),
              "Bay-window sightline — preserved",
              font=f_t, fill=C["title"])
    draw.text(
        (pad, PHOTO_H + 90),
        "The central section of the new bed (in front of this window) is "
        "kept under 30\" mature height —",
        font=f_b, fill=C["body"],
    )
    draw.text(
        (pad, PHOTO_H + 122),
        "low forbs, prairie smoke groundcover, and short grasses — so the "
        "borrowed view of the flowering tree across",
        font=f_b, fill=C["body"],
    )
    draw.text(
        (pad, PHOTO_H + 154),
        "the cul-de-sac stays open. The serviceberry and ninebarks live to "
        "the west and at the corners, not center.",
        font=f_b, fill=C["body"],
    )
    draw.text(
        (pad, PHOTO_H + 200),
        "Bench is offset to the west third — visible at the edge of this "
        "view but not blocking it.",
        font=f_b, fill=C["body"],
    )

    out = OUT / "08-bay-window-sightline.jpg"
    canvas.convert("RGB").save(out, quality=92)
    return out


def render_swale() -> Path:
    """Annotate the dry-creek photo to show the vegetated-swale plan."""
    src = PHOTOS / "03-dry-creek.jpg"
    photo = Image.open(src).convert("RGBA")
    # this photo is portrait 3072x4080 — resize to fit within 1800x2400
    photo = photo.resize((1800, 2400), Image.LANCZOS)

    pad_bottom = 380
    canvas = Image.new("RGBA", (1800, 2400 + pad_bottom),
                       (255, 255, 255, 255))
    canvas.paste(photo, (0, 0))

    overlay = Image.new("RGBA", (1800, 2400), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay, "RGBA")

    # Three moisture bands
    # Channel center (sedge meadow) — middle of rock area
    od.polygon(
        [(450, 800), (1150, 750), (1300, 1500), (1100, 2200),
         (700, 2350), (350, 2000)],
        fill=(70, 130, 180, 100),
    )
    # Moist slope
    od.polygon(
        [(200, 600), (1500, 550), (1700, 1500), (1500, 2380),
         (300, 2380), (100, 1800)],
        fill=(60, 140, 100, 70),
    )
    # Label markers
    f_l = load_font(36, bold=True)
    f_s = load_font(26, bold=False)
    od.text((900, 1300), "CHANNEL", font=f_l, fill=(30, 60, 100, 255))
    od.text((900, 1340), "Tussock Sedge · Fox Sedge · Soft Rush",
            font=f_s, fill=(30, 60, 100, 255))
    od.text((900, 1370), "Blue Flag Iris", font=f_s, fill=(30, 60, 100, 255))

    od.text((150, 800), "MOIST SLOPE", font=f_l, fill=(30, 100, 60, 255))
    od.text((150, 840),
            "Swamp Milkweed · Cardinal Flower · Great Blue Lobelia",
            font=f_s, fill=(30, 100, 60, 255))

    # arrow indicating water flow
    draw_arrow(od, (1000, 700), (900, 2200),
               color=(40, 80, 140, 180), width=6, label="water flow")

    canvas.alpha_composite(overlay, (0, 0))

    # caption
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle([0, 2400, 1800, 2400 + pad_bottom],
                   fill=C["legend_bg"])
    draw.line([(0, 2400), (1800, 2400)], fill=C["accent"], width=3)
    f_t = load_font(36, bold=True)
    f_b = load_font(22, bold=False)
    pad = 40
    draw.text((pad, 2430),
              "Vegetated swale — replaces the river-rock channel",
              font=f_t, fill=C["title"])
    draw.text(
        (pad, 2484),
        "Per Rima's preference: no rock. Native sedges and rushes "
        "form a fibrous root mat that armors the flow path —",
        font=f_b, fill=C["body"],
    )
    draw.text(
        (pad, 2516),
        "same drainage function, no rock, fully alive. Standard "
        "MN DNR / Met Council green-stormwater approach.",
        font=f_b, fill=C["body"],
    )
    draw.text(
        (pad, 2562),
        "Year-1 protection: biodegradable jute or coir blanket "
        "over the planted channel while sedges establish.",
        font=f_b, fill=C["body"],
    )
    draw.text(
        (pad, 2610),
        "If installer finds existing drain tile under the rock, "
        "preserve it. Test pit before full removal.",
        font=f_b, fill=C["body"],
    )
    draw.text(
        (pad, 2660),
        "Hand-pull creeping charlie before any soil disturbance "
        "or it spreads aggressively.",
        font=f_b, fill=C["body"],
    )

    out = OUT / "03-dry-creek-design.jpg"
    canvas.convert("RGB").save(out, quality=92)
    return out


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

if __name__ == "__main__":
    p1 = render_primary()
    print(f"primary: {p1}")
    p2 = render_sightline()
    print(f"sightline: {p2}")
    p3 = render_swale()
    print(f"swale: {p3}")
