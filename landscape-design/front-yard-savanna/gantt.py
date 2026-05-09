"""
Bloom-overlap Gantt chart — Drawing 4 of 5.

Every species in the design plotted along the year (April–November) as a
horizontal bar across its bloom window. Reveals continuous-bloom coverage and
any thin spots at a glance.

Output: bloom-gantt.pdf and bloom-gantt.png in annotated/.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "annotated"
OUT.mkdir(exist_ok=True)


# (common_name, sci, kind, start_half_month, end_half_month, color, qty,
#  zone)
# half-months: Apr=1, mid-Apr=2, May=3, mid-May=4, Jun=5, mid-Jun=6,
#              Jul=7, mid-Jul=8, Aug=9, mid-Aug=10, Sep=11, mid-Sep=12,
#              Oct=13, mid-Oct=14, Nov=15
SPECIES = [
    # name,                                 kind,  start, end, color,   qty
    ("Serviceberry",         "Amelanchier laevis",        "tree",  1, 3,
     "#f6e8e2", 1),
    ("Wild Lupine",          "Lupinus perennis",          "forb",  3, 5,
     "#7a6abf", 7),
    ("Prairie Smoke",        "Geum triflorum",            "grnd",  3, 5,
     "#9b7390", 9),
    ("False Blue Indigo",    "Baptisia australis",        "forb",  4, 6,
     "#5d6d9c", 3),
    ("Pussytoes",            "Antennaria neglecta",       "grnd",  4, 5,
     "#d8d2b8", 7),
    ("Wild Strawberry",      "Fragaria virginiana",       "grnd",  4, 6,
     "#e8e0d0", 5),
    ("Ninebark",             "Physocarpus opulifolius",   "shrub", 5, 6,
     "#f0e8e0", 2),
    ("Gray Dogwood",         "Cornus racemosa",           "shrub", 5, 7,
     "#f0e8e0", 1),
    ("Butterfly Milkweed",   "Asclepias tuberosa",        "forb",  6, 9,
     "#e0892a", 5),
    ("Wild Bergamot",        "Monarda fistulosa",         "forb",  7, 10,
     "#c66da8", 7),
    ("Purple Coneflower",    "Echinacea purpurea",        "forb",  7, 13,
     "#a04688", 10),
    ("Swamp Milkweed",       "Asclepias incarnata",       "swale", 7, 9,
     "#d8639a", 3),
    ("Blue Flag Iris",       "Iris versicolor",           "swale", 5, 7,
     "#3a6a9c", 3),
    ("Cardinal Flower",      "Lobelia cardinalis",        "swale", 9, 12,
     "#c92a40", 3),
    ("Great Blue Lobelia",   "Lobelia siphilitica",       "swale", 9, 12,
     "#5d6d9c", 3),
    ("Smooth Blue Aster",    "Symphyotrichum laeve",      "forb",  11, 14,
     "#7596c2", 5),
    ("Little Bluestem",      "Schizachyrium scoparium",   "grass", 11, 15,
     "#c08552", 9),
    ("Prairie Dropseed",     "Sporobolus heterolepis",    "grass", 10, 12,
     "#a89060", 7),
]

KIND_LABEL = {
    "tree":  "TREE",
    "shrub": "SHRUB",
    "forb":  "FORB",
    "grass": "GRASS",
    "grnd":  "GROUND",
    "swale": "SWALE",
}
KIND_COLOR = {
    "tree":  "#5a3a1a",
    "shrub": "#7a4a2a",
    "forb":  "#9a5a3a",
    "grass": "#a8852a",
    "grnd":  "#7a6a4a",
    "swale": "#3a6a8a",
}

# Half-month grid
HALF_MONTH_LABELS = [
    "Apr", "·", "May", "·", "Jun", "·", "Jul", "·", "Aug", "·",
    "Sep", "·", "Oct", "·", "Nov",
]
N = len(HALF_MONTH_LABELS)  # 15

# ----------------------------------------------------------------
# Figure
# ----------------------------------------------------------------

fig, ax = plt.subplots(figsize=(15, 11), dpi=160)

# Sort by bloom start, then duration
species_sorted = sorted(SPECIES, key=lambda s: (s[3], s[4] - s[3]))

# Background month bands
for i in range(0, N, 2):
    ax.add_patch(patches.Rectangle((i + 0.5, -1), 2, len(species_sorted) + 2,
                                     facecolor="#f6f2e8", edgecolor="none",
                                     zorder=0))

# Species bars
for row, (name, sci, kind, start, end, color, qty) in enumerate(
        species_sorted):
    y = len(species_sorted) - row
    # bar
    ax.add_patch(patches.FancyBboxPatch((start + 0.5, y - 0.35),
                                          end - start, 0.7,
                                          boxstyle="round,pad=0.02",
                                          facecolor=color,
                                          edgecolor="#1a1a1a",
                                          linewidth=0.6, zorder=2,
                                          alpha=0.85))
    # label on left
    ax.text(0.3, y, name, fontsize=9, weight="bold", va="center", ha="right",
            color="#1a1a1a")
    ax.text(0.3, y - 0.35, sci, fontsize=7, va="center", ha="right",
            style="italic", color="#5a5a5a")
    # kind badge
    ax.add_patch(patches.FancyBboxPatch((-3.4, y - 0.3), 1.6, 0.6,
                                          boxstyle="round,pad=0.05",
                                          facecolor=KIND_COLOR[kind],
                                          edgecolor="none",
                                          zorder=2.5))
    ax.text(-2.6, y, KIND_LABEL[kind], fontsize=7, weight="bold",
            color="white", ha="center", va="center")
    # quantity on right
    ax.text(N + 1.3, y, f"×{qty}", fontsize=9, va="center", ha="left",
            color="#3a3a3a", weight="bold")

# Month axis (tick marks at month boundaries)
for i in range(N + 1):
    ax.plot([i + 0.5, i + 0.5], [0.5, len(species_sorted) + 0.5],
            color="#d0c8b8", linewidth=0.4, zorder=1)

# Month labels at top
for i, label in enumerate(HALF_MONTH_LABELS):
    if label != "·":
        ax.text(i + 1, len(species_sorted) + 0.9,
                label, fontsize=10, ha="center", weight="bold",
                color="#3a5a2a")

# Headers
ax.text(0.3, len(species_sorted) + 1.3, "SPECIES",
        fontsize=10, weight="bold", color="#3a5a2a", ha="right")
ax.text(-2.6, len(species_sorted) + 1.3, "KIND",
        fontsize=10, weight="bold", color="#3a5a2a", ha="center")
ax.text(N + 1.3, len(species_sorted) + 1.3, "QTY",
        fontsize=10, weight="bold", color="#3a5a2a", ha="left")

# Pollinator-key seasons strip at bottom
season_y = -0.5
seasons = [
    ("Spring",  1, 5, "#9b7cb8"),
    ("Summer",  5, 11, "#c66da8"),
    ("Fall",    11, 14, "#5a7fb8"),
    ("Winter\nstructure", 14, 16, "#a85a3a"),
]
for label, start, end, color in seasons:
    ax.add_patch(patches.Rectangle((start + 0.5, season_y - 0.4),
                                     end - start, 0.5,
                                     facecolor=color, edgecolor="none",
                                     alpha=0.55, zorder=1))
    ax.text((start + end) / 2 + 0.5, season_y - 0.15,
            label, fontsize=9, weight="bold", ha="center", va="center",
            color="white")

ax.text(0.3, season_y - 0.15, "SEASON", fontsize=10, weight="bold",
        ha="right", color="#3a5a2a")

ax.set_xlim(-3.6, N + 3)
ax.set_ylim(season_y - 1, len(species_sorted) + 2)
ax.set_xticks([])
ax.set_yticks([])
for sp in ax.spines.values():
    sp.set_visible(False)

# Title and footer
ax.set_title("FRONT-YARD OAK SAVANNA EDGE — Bloom-Overlap Calendar  "
             "(Drawing 4 of 5)",
             fontsize=14, weight="bold", color="#3a5a2a", loc="center",
             pad=20)

fig.text(0.5, 0.02,
         "Continuous bloom April → October  ·  18 species  ·  "
         "no gap month  ·  satisfies Ch.10 pollinator-design "
         "principle (lines 415-445)",
         ha="center", va="bottom", fontsize=9, color="#5a4a3a",
         style="italic")

# Note
ax.text(N + 0.5, -1.0,
        "Note: bar position approximates each species' MN bloom window. "
        "Duration depends on weather, microsite, and individual genetics.",
        ha="right", va="top", fontsize=7, style="italic", color="#7a7a7a")

plt.tight_layout(rect=[0, 0.02, 1, 0.98])
plt.savefig(OUT / "bloom-gantt.pdf", bbox_inches="tight", facecolor="white")
plt.savefig(OUT / "bloom-gantt.png", bbox_inches="tight", facecolor="white",
            dpi=180)
print(f"gantt: {OUT / 'bloom-gantt.pdf'}")
print(f"gantt: {OUT / 'bloom-gantt.png'}")
