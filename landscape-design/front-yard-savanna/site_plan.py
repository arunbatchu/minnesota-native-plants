"""
Top-down site plan — Front-Yard Oak Savanna Edge.

Scale: 1 in. = 4 ft.  North up.  Coordinates are in feet, origin SW corner of
view, +x east, +y north.

Output: site-plan.pdf and site-plan.png in annotated/.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path as MPath
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "annotated"
OUT.mkdir(exist_ok=True)

# ---- view extent (ft) ----
XMIN, XMAX = 0, 62
YMIN, YMAX = 0, 38

# ---- house & hardscape ----
HOUSE_FOOTPRINT = [
    (4, 28), (50, 28), (50, 38), (4, 38), (4, 28),
]
# Bay window bumps south
BAY_WINDOW = [(18, 28), (32, 28), (32, 26.5), (18, 26.5), (18, 28)]
# Front porch
PORCH = [(50, 28), (58, 28), (58, 35), (50, 35), (50, 28)]
PORCH_STEPS = [(54, 25), (58, 25), (58, 28), (54, 28), (54, 25)]
# Driveway (extends off bottom of view)
DRIVEWAY = [(50, 0), (62, 0), (62, 22), (50, 22), (50, 0)]
# Concrete walkway from driveway curving up to porch and over swale
WALKWAY_POINTS = [
    (50, 22), (49, 24), (48, 25.5), (49, 27), (54, 27.5),
]
# Side service walkway (west wall)
SIDE_WALK = [(0, 28), (4, 28), (4, 32), (0, 32), (0, 28)]

# ---- existing vegetation (kept) ----
# Two mature arborvitae east end of bed
ARBORVITAE = [(46.5, 27), (49, 27.5)]
ARB_R = 2.5
# Mature crabapple at front entry
CRABAPPLE = (54, 20)
CRAB_R = 5

# ---- new bed footprint ----
# Curves outward. Deepest at west, tapers to east at arborvitae.
BED_OUTLINE = [
    (10, 26.5),    # NW corner against house
    (10, 26.5),
    (10, 21),      # SW depth (deepest)
    (12, 17),      # bench pocket
    (16, 16.5),
    (24, 18.5),
    (32, 19.5),
    (40, 20.5),
    (44, 21.5),
    (46, 24),      # meets arborvitae
    (46, 26.5),    # NE corner up to wall
]

# ---- vegetated swale (sedge meadow) ----
# Crescent between arborvitae and walkway, replacing the river-rock channel
SWALE_OUTLINE = [
    (47, 27.5), (50, 25), (52, 22), (54, 19),
    (55, 21), (53, 24), (51, 26.5), (48, 27.8),
]

# ---- path (limestone steppers, dashed line) ----
PATH = [(48, 22.5), (44, 22), (38, 21.5),
        (30, 20.5), (22, 19), (16, 17.8), (13, 17.5)]

# ---- bench ----
BENCH = (12, 17.5)
BENCH_W, BENCH_L = 1.5, 5  # 18" deep × 5 ft long (in plan, runs east-west)

# ---- plant placements (id, x, y, mature_radius_ft, color, abbrev) ----
# (label, x, y, planting_radius_ft, mature_radius_ft, color, abbrev)
# Trees and shrubs draw at PLANTING size as a solid disc, with a dotted
# outline showing mature canopy footprint so the plan reads as installable.
WOODY = [
    ("Serviceberry",       14, 23.5, 1.5, 6.0, "#7a4a2a", "SVB"),
    ("Gray Dogwood",       11, 24.5, 1.0, 4.0, "#a8723e", "GDW"),
    ("Ninebark (W)",       19, 26,   0.8, 2.5, "#9a5a3a", "NIN"),
    ("Ninebark (E)",       33, 26,   0.8, 2.5, "#9a5a3a", "NIN"),
]

# Forb drifts as elliptical patches with quantity labels
DRIFTS = [
    # (label, cx, cy, w, h, color, count)
    ("False Blue Indigo (Baptisia)",  17, 22.5, 4, 2,   "#5d6d9c", 3),
    ("Wild Bergamot (Monarda)",        25, 22,   6, 2.5, "#c66da8", 7),
    ("Smooth Blue Aster",              39, 22,   4, 2,   "#7596c2", 5),
    ("Wild Lupine",                    15, 19.5, 4, 2,   "#7a6abf", 7),
    ("Purple Coneflower drift A",      24, 20,   4, 2,   "#a04688", 5),
    ("Purple Coneflower drift B",      36, 20.5, 3.5, 1.8, "#a04688", 5),
    ("Butterfly Milkweed",             40, 19.5, 3, 1.8, "#e0892a", 5),
    ("Little Bluestem",                28, 18,   8, 1.5, "#c08552", 9),
    ("Prairie Smoke (groundcover)",    20, 17.5, 6, 1.2, "#9b7390", 9),
    ("Prairie Dropseed (front ribbon)", 12, 18.5, 3, 1, "#a89060", 7),
]

# Swale plantings (within the SWALE_OUTLINE)
SWALE_PLANTS = [
    ("Tussock Sedge (channel)",       51, 23.5, 2.5, 1.5, "#4a7d6c", 9),
    ("Fox Sedge",                     53, 22,   2,   1,   "#5b8a72", 7),
    ("Soft Rush",                     49.5, 25, 1.5, 1,   "#6a9580", 5),
    ("Blue Flag Iris",                52, 23.5, 1.2, 0.8, "#3a6a9c", 3),
    ("Swamp Milkweed",                54.5, 21, 1.5, 0.8, "#d8639a", 3),
    ("Cardinal Flower",               54, 23,   1.2, 0.7, "#c92a40", 3),
]

# Service-area groundcover (HVAC + gas meter buffer on west wall)
SERVICE_AREA = [(0, 28), (4, 28), (4, 32), (0, 32)]


# ============================================================
# Drawing
# ============================================================

fig, ax = plt.subplots(figsize=(17, 11), dpi=160)
ax.set_xlim(XMIN, XMAX)
ax.set_ylim(YMIN, YMAX)
ax.set_aspect("equal")

# --- background lawn (light green wash) ---
ax.add_patch(patches.Rectangle((XMIN, YMIN), XMAX - XMIN, YMAX - YMIN,
                                facecolor="#e8efd8", edgecolor="none",
                                zorder=0))

# --- driveway (stamped concrete) ---
ax.add_patch(patches.Polygon(DRIVEWAY, closed=True,
                              facecolor="#d8d2c5", edgecolor="#9a9080",
                              linewidth=1.0, zorder=1))
ax.text(56, 8, "driveway\n(stamped concrete)", ha="center", va="center",
        fontsize=8, color="#666", style="italic")

# --- concrete walkway (with subtle curve via filled polygon) ---
walkway_w = 4
wpts = []
for i, (x, y) in enumerate(WALKWAY_POINTS):
    # offset perpendicular for width
    if i == 0:
        nx, ny = 1, 0
    elif i == len(WALKWAY_POINTS) - 1:
        nx, ny = 0, 1
    else:
        x_prev, y_prev = WALKWAY_POINTS[i - 1]
        x_next, y_next = WALKWAY_POINTS[i + 1]
        dx, dy = x_next - x_prev, y_next - y_prev
        L = (dx ** 2 + dy ** 2) ** 0.5 or 1
        nx, ny = -dy / L, dx / L
    wpts.append((x + nx * walkway_w / 2, y + ny * walkway_w / 2))
for x, y in reversed(WALKWAY_POINTS):
    idx = WALKWAY_POINTS.index((x, y))
    if idx == 0:
        nx, ny = 1, 0
    elif idx == len(WALKWAY_POINTS) - 1:
        nx, ny = 0, 1
    else:
        x_prev, y_prev = WALKWAY_POINTS[idx - 1]
        x_next, y_next = WALKWAY_POINTS[idx + 1]
        dx, dy = x_next - x_prev, y_next - y_prev
        L = (dx ** 2 + dy ** 2) ** 0.5 or 1
        nx, ny = -dy / L, dx / L
    wpts.append((x - nx * walkway_w / 2, y - ny * walkway_w / 2))
ax.add_patch(patches.Polygon(wpts, closed=True,
                              facecolor="#d8d2c5", edgecolor="#9a9080",
                              linewidth=0.8, zorder=1))

# --- house footprint ---
ax.add_patch(patches.Polygon(HOUSE_FOOTPRINT, closed=True,
                              facecolor="#f5ecd8", edgecolor="#5a4a3a",
                              linewidth=2.5, zorder=2))
# bay window bump
ax.add_patch(patches.Polygon(BAY_WINDOW, closed=True,
                              facecolor="#f5ecd8", edgecolor="#5a4a3a",
                              linewidth=2.0, zorder=2))
# porch
ax.add_patch(patches.Polygon(PORCH, closed=True,
                              facecolor="#ede0c8", edgecolor="#5a4a3a",
                              linewidth=2.0, zorder=2))
ax.add_patch(patches.Polygon(PORCH_STEPS, closed=True,
                              facecolor="#ede0c8", edgecolor="#7a6a5a",
                              linewidth=1.2, zorder=2))
ax.text(27, 33, "Stucco home (1997)\n5,500 sq ft · 2 stories",
        ha="center", va="center", fontsize=9, color="#5a4a3a", style="italic")
ax.text(54, 31.5, "front\nporch", ha="center", va="center",
        fontsize=8, color="#5a4a3a", style="italic")
ax.text(25, 27.4, "bay window", ha="center", va="center",
        fontsize=7, color="#5a4a3a", style="italic")

# Side service area (HVAC, gas meter)
ax.add_patch(patches.Polygon(SERVICE_AREA, closed=True,
                              facecolor="#cfd1c2", edgecolor="#8a8a7a",
                              linewidth=1, linestyle="--", zorder=1.5))
ax.text(2, 30, "service\n(HVAC,\ngas meter)\n3 ft\nclearance",
        ha="center", va="center", fontsize=6.5, color="#666",
        style="italic")

# --- new bed footprint ---
bed_path = MPath(BED_OUTLINE + [BED_OUTLINE[0]])
ax.add_patch(patches.PathPatch(bed_path, facecolor="#dfe8d2",
                                edgecolor="#5a7a3a", linewidth=2.0,
                                zorder=2.5, alpha=0.7))
ax.text(28, 24.5, "NEW PLANTING BED — Oak Savanna Edge",
        ha="center", va="center", fontsize=10, color="#3a5a2a",
        style="italic", weight="bold", alpha=0.6)

# --- vegetated swale ---
swale_path = MPath(SWALE_OUTLINE + [SWALE_OUTLINE[0]])
ax.add_patch(patches.PathPatch(swale_path, facecolor="#cce0e8",
                                edgecolor="#3a6a8a", linewidth=2.0,
                                zorder=2.5, alpha=0.85))
ax.text(52.5, 22.8, "VEGETATED\nSWALE", ha="center", va="center",
        fontsize=8, color="#1a4a6a", style="italic", weight="bold",
        alpha=0.85)

# --- existing trees to preserve ---
for cx, cy in ARBORVITAE:
    ax.add_patch(patches.Circle((cx, cy), ARB_R,
                                  facecolor="#5d8a5a", edgecolor="#2a4a2a",
                                  linewidth=1, zorder=4, alpha=0.85))
ax.text(47.5, 28, "(2) existing\narborvitae",
        ha="center", va="bottom", fontsize=7, color="#1a3a1a",
        style="italic")

# Crabapple
ax.add_patch(patches.Circle(CRABAPPLE, CRAB_R,
                              facecolor="#f4cce0", edgecolor="#a04088",
                              linewidth=1, linestyle="--", zorder=3.5,
                              alpha=0.7))
ax.text(CRABAPPLE[0], CRABAPPLE[1], "EXISTING\ncrabapple\n(spring pink)",
        ha="center", va="center", fontsize=7, color="#5a2055",
        style="italic")

# --- path (stepping stones along the path line) ---
for i in range(len(PATH) - 1):
    x1, y1 = PATH[i]
    x2, y2 = PATH[i + 1]
    n_steps = max(int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / 1.5), 1)
    for k in range(n_steps):
        t = (k + 0.5) / n_steps
        sx = x1 + (x2 - x1) * t
        sy = y1 + (y2 - y1) * t
        ax.add_patch(patches.Ellipse((sx, sy), 1.0, 0.7,
                                       facecolor="#c8b896",
                                       edgecolor="#7a6850",
                                       linewidth=0.8, zorder=5))

# --- bench ---
bx, by = BENCH
ax.add_patch(patches.Rectangle((bx - BENCH_L / 2, by - BENCH_W / 2),
                                 BENCH_L, BENCH_W,
                                 facecolor="#6a4828", edgecolor="#3a2818",
                                 linewidth=1.2, zorder=6))
ax.text(bx, by - 1.2, "BENCH\n(east-facing)", ha="center", va="top",
        fontsize=8, color="#3a2818", weight="bold")

# --- woody plants ---
# Solid disc = planting size (what the installer sees on day 1)
# Dotted ring = mature canopy footprint (what to allow space for)
for label, x, y, planting_r, mature_r, color, abbrev in WOODY:
    # Mature canopy outline (dotted)
    ax.add_patch(patches.Circle((x, y), mature_r,
                                  facecolor="none", edgecolor=color,
                                  linewidth=1.0, linestyle=(0, (2, 2)),
                                  zorder=3.8, alpha=0.5))
    # Planting size (solid)
    ax.add_patch(patches.Circle((x, y), planting_r,
                                  facecolor=color, edgecolor="#1a1a1a",
                                  linewidth=1.0, zorder=4, alpha=0.85))
    # Trunk dot
    ax.add_patch(patches.Circle((x, y), 0.15,
                                  facecolor="#1a1a1a", zorder=4.5))
    ax.text(x, y - mature_r - 0.3, abbrev, ha="center", va="top",
            fontsize=7.5, weight="bold", color="#1a1a1a")

# --- forb drifts ---
for label, cx, cy, w, h, color, count in DRIFTS:
    ax.add_patch(patches.Ellipse((cx, cy), w, h,
                                   facecolor=color, edgecolor="#3a3a3a",
                                   linewidth=0.8, zorder=4, alpha=0.55,
                                   linestyle=":"))
    ax.text(cx, cy, f"{count}", ha="center", va="center",
            fontsize=8, weight="bold", color="#1a1a1a")

# --- swale plants ---
for label, cx, cy, w, h, color, count in SWALE_PLANTS:
    ax.add_patch(patches.Ellipse((cx, cy), w, h,
                                   facecolor=color, edgecolor="#1a3a4a",
                                   linewidth=0.6, zorder=4, alpha=0.7,
                                   linestyle=":"))
    ax.text(cx, cy, f"{count}", ha="center", va="center",
            fontsize=7, weight="bold", color="#1a1a1a")

# --- north arrow ---
n_x, n_y = 58, 35
ax.annotate("", xy=(n_x, n_y + 1.5), xytext=(n_x, n_y - 1.5),
            arrowprops=dict(arrowstyle="-|>", lw=2, color="#1a1a1a"))
ax.text(n_x, n_y + 2.2, "N", ha="center", va="center",
        fontsize=14, weight="bold", color="#1a1a1a")
ax.add_patch(patches.Circle((n_x, n_y), 2.5, facecolor="none",
                              edgecolor="#1a1a1a", linewidth=0.8))

# --- scale bar ---
sb_x, sb_y = 2, 1.5
sb_len = 8  # 8 ft scale bar
ax.add_patch(patches.Rectangle((sb_x, sb_y), sb_len / 2, 0.4,
                                 facecolor="#1a1a1a", edgecolor="#1a1a1a"))
ax.add_patch(patches.Rectangle((sb_x + sb_len / 2, sb_y), sb_len / 2, 0.4,
                                 facecolor="white", edgecolor="#1a1a1a"))
ax.text(sb_x, sb_y - 0.6, "0", ha="center", va="top", fontsize=8)
ax.text(sb_x + sb_len / 2, sb_y - 0.6, "4", ha="center", va="top",
        fontsize=8)
ax.text(sb_x + sb_len, sb_y - 0.6, "8 ft", ha="center", va="top",
        fontsize=8)
ax.text(sb_x, sb_y + 1.0, "Scale: 1 in. = 4 ft", ha="left", va="bottom",
        fontsize=9, weight="bold")

# --- title block (right side, bottom) ---
tb_x, tb_y = 38, 1
tb_w, tb_h = 23, 7
ax.add_patch(patches.Rectangle((tb_x, tb_y), tb_w, tb_h,
                                 facecolor="#fbf7ee", edgecolor="#5a4a3a",
                                 linewidth=1.5))
ax.text(tb_x + 0.6, tb_y + tb_h - 0.8,
        "FRONT-YARD OAK SAVANNA EDGE",
        ha="left", va="top", fontsize=14, weight="bold",
        color="#3a5a2a", family="serif")
ax.text(tb_x + 0.6, tb_y + tb_h - 1.8,
        "Site Plan — Top View",
        ha="left", va="top", fontsize=10, color="#5a4a3a")
ax.text(tb_x + 0.6, tb_y + tb_h - 3.0,
        "8547 Crane Dance Trail · Eden Prairie MN 55344",
        ha="left", va="top", fontsize=9, color="#3a3a3a")
ax.text(tb_x + 0.6, tb_y + tb_h - 3.8,
        "Lot 0.36 ac · Parcel 1311622340067",
        ha="left", va="top", fontsize=8, color="#5a5a5a")
ax.text(tb_x + 0.6, tb_y + tb_h - 4.6,
        "Pre-settlement: bur oak savanna (Marschner)",
        ha="left", va="top", fontsize=8, color="#5a5a5a", style="italic")
ax.text(tb_x + 0.6, tb_y + tb_h - 5.3,
        "Soil: Hayden/Lester loam (TBC via Web Soil Survey)",
        ha="left", va="top", fontsize=8, color="#5a5a5a", style="italic")
ax.text(tb_x + 0.6, tb_y + 0.4,
        "Designer: Claude (Anthropic) acting as MN native-plants specialist  ·  Drawing 1 of 5",
        ha="left", va="bottom", fontsize=7, color="#7a7a7a", style="italic")

# --- legend (bottom-left) ---
lg_x, lg_y = 2, 4
ax.text(lg_x, lg_y + 4, "LEGEND", fontsize=10, weight="bold",
        color="#3a5a2a")
legend_items = [
    ("●", "#7a4a2a", "Serviceberry (SVB) — west anchor, 15-20 ft mature"),
    ("●", "#a8723e", "Gray Dogwood (GDW)"),
    ("●", "#9a5a3a", "Ninebark (NIN) — flanking bay window, kept low"),
    ("◌", "#7a4a2a", "Dotted ring = mature canopy at year ~10"),
    ("⬭", "#c66da8", "Forb drift — number = quantity"),
    ("⬭", "#5b8a72", "Swale plug planting"),
    ("○", "#5d8a5a", "Existing tree to preserve"),
    ("---", "#7a6850", "Stepping-stone path (limestone)"),
]
for i, (sym, col, txt) in enumerate(legend_items):
    y = lg_y + 3 - i * 0.55
    ax.text(lg_x, y, sym, fontsize=11, color=col, weight="bold")
    ax.text(lg_x + 0.8, y, txt, fontsize=7.5, color="#3a3a3a", va="center")

# clean axes
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_color("#5a4a3a")
    spine.set_linewidth(1.5)

# Outer border with margin
ax.set_xlim(XMIN - 1, XMAX + 1)
ax.set_ylim(YMIN - 0.5, YMAX + 0.5)

plt.tight_layout()
plt.savefig(OUT / "site-plan.pdf", bbox_inches="tight", facecolor="white")
plt.savefig(OUT / "site-plan.png", bbox_inches="tight", facecolor="white",
            dpi=180)
print(f"site plan: {OUT / 'site-plan.pdf'}")
print(f"site plan: {OUT / 'site-plan.png'}")
