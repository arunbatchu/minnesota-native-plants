"""
Construction details — Drawing 3 of 5.

Four 2D detail drawings (1:10ish), the kind of cross-section a contractor
needs to bid and build:

  Detail 1: Stepping-stone path — bed prep cross-section
  Detail 2: Bench pad — pea gravel on compacted base
  Detail 3: Trench-cut bed edge — between bed and lawn
  Detail 4: Soft mowing strip — fieldstone alternative

Output: details.pdf and details.png in annotated/.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "annotated"
OUT.mkdir(exist_ok=True)


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def hatch_layer(ax, x, y, w, h, hatch, fc="#ffffff", ec="#3a3a3a", **kw):
    ax.add_patch(patches.Rectangle((x, y), w, h, facecolor=fc,
                                     edgecolor=ec, hatch=hatch,
                                     linewidth=1.0, **kw))


def label_arrow(ax, txt, xy, xytext, color="#3a3a3a", fontsize=8):
    ax.annotate(txt, xy=xy, xytext=xytext,
                fontsize=fontsize, color=color,
                arrowprops=dict(arrowstyle="-", lw=0.7, color=color))


def setup_detail(ax, title, x_max, y_min, y_max):
    ax.set_xlim(-0.5, x_max + 0.5)
    ax.set_ylim(y_min - 0.2, y_max + 0.3)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=11, weight="bold", color="#3a5a2a",
                 loc="left", pad=8)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


# --------------------------------------------------------------------
# Detail 1: Stepping-stone path
# --------------------------------------------------------------------

def detail_path(ax):
    setup_detail(ax, "DETAIL 1 — Stepping-Stone Path  (scale ~1:8)",
                 x_max=24, y_min=-12, y_max=4)

    # Original undisturbed soil (subgrade)
    ax.add_patch(patches.Rectangle((-1, -12), 26, 12,
                                     facecolor="#7a5a3a",
                                     edgecolor="#3a2a1a", linewidth=1,
                                     hatch="//"))

    # Excavation: 4" base + 2" screenings + 2" stone = 8" deep
    ex_top = 0
    ex_bot = -8
    ax.add_patch(patches.Rectangle((4, ex_bot), 16, 8,
                                     facecolor="#a6804a",
                                     edgecolor="#5a4a3a", linewidth=1.2,
                                     hatch=""))

    # Compacted aggregate base (4")
    hatch_layer(ax, 4, -8, 16, 4, hatch="...",
                fc="#9a8870", ec="#3a3a3a")
    label_arrow(ax, "compacted aggregate base — 4\" Class 5",
                xy=(12, -6), xytext=(13, -10.5))

    # Screenings (decomposed granite or limestone fines, 2")
    hatch_layer(ax, 4, -4, 16, 2, hatch="..",
                fc="#c8b896", ec="#3a3a3a")
    label_arrow(ax, "limestone screenings — 2\" leveling course",
                xy=(12, -3), xytext=(2, -2.5))

    # The stepper itself
    ax.add_patch(patches.FancyBboxPatch((6, -2), 12, 3,
                                          boxstyle="round,pad=0.05",
                                          facecolor="#9a8a72",
                                          edgecolor="#3a3a3a",
                                          linewidth=1.5))
    ax.text(12, -0.5, "Chilton or local limestone stepper\n"
                      "18-24\" wide × ~2\" thick",
            ha="center", va="center", fontsize=7.5, color="#1a1a1a")

    # Surrounding mulch / soil
    hatch_layer(ax, -1, 1, 5, 1, hatch="--",
                fc="#9a6a3a", ec="#5a4a3a")
    hatch_layer(ax, 20, 1, 5, 1, hatch="--",
                fc="#9a6a3a", ec="#5a4a3a")
    ax.text(2, 1.5, "shredded\nhardwood mulch", fontsize=7,
            color="#3a3a3a", ha="center")
    ax.text(22, 1.5, "shredded\nhardwood mulch", fontsize=7,
            color="#3a3a3a", ha="center")

    # Plants flanking
    ax.add_patch(patches.Ellipse((1, 4), 2, 3, facecolor="#a04688",
                                   edgecolor="#3a3a3a", alpha=0.6))
    ax.add_patch(patches.Ellipse((23, 4), 2, 3, facecolor="#c08552",
                                   edgecolor="#3a3a3a", alpha=0.6))

    # Dimension lines
    ax.annotate("", xy=(4, -9), xytext=(20, -9),
                arrowprops=dict(arrowstyle="<->", color="#3a3a3a"))
    ax.text(12, -9.3, "16\" excavated bed", ha="center", va="top",
            fontsize=7, color="#3a3a3a")

    ax.annotate("", xy=(21, -8), xytext=(21, 1),
                arrowprops=dict(arrowstyle="<->", color="#3a3a3a"))
    ax.text(21.3, -3.5, "8\"\ntotal\ndepth", fontsize=7, color="#3a3a3a")

    # Notes
    ax.text(-0.3, -11, "NOTES:\n"
            "• Set steppers in screenings so top sits flush with mulch\n"
            "• 18-24\" stride spacing along path\n"
            "• Pitch slightly outward for drainage\n"
            "• Lawn-side: trim grass to crisp edge against stepper",
            fontsize=7, va="top", ha="left", color="#3a3a3a",
            family="monospace")


# --------------------------------------------------------------------
# Detail 2: Bench pad
# --------------------------------------------------------------------

def detail_bench(ax):
    setup_detail(ax, "DETAIL 2 — Bench Pad  (scale ~1:8)",
                 x_max=24, y_min=-10, y_max=8)

    # Subgrade
    ax.add_patch(patches.Rectangle((-1, -10), 26, 10,
                                     facecolor="#7a5a3a",
                                     edgecolor="#3a2a1a", hatch="//"))

    # Excavation 6" deep × 60" wide
    ax.add_patch(patches.Rectangle((4, -6), 16, 6,
                                     facecolor="#a6804a",
                                     edgecolor="#3a2a1a", linewidth=1.2))
    # Compacted base 4"
    hatch_layer(ax, 4, -6, 16, 4, hatch="...", fc="#9a8870", ec="#3a3a3a")
    # Pea gravel 2"
    hatch_layer(ax, 4, -2, 16, 2, hatch="oo", fc="#c8b896", ec="#3a3a3a")
    label_arrow(ax, "pea gravel — 2\"  (drains well, easy to top up)",
                xy=(12, -1), xytext=(11, 6.2))
    label_arrow(ax, "compacted aggregate base — 4\" Class 5",
                xy=(12, -4), xytext=(0.5, -6.7))

    # Edging (steel or reclaimed brick)
    ax.add_patch(patches.Rectangle((3.5, -2.2), 0.4, 3.0,
                                     facecolor="#3a2a1a",
                                     edgecolor="#1a1a1a", linewidth=1.2))
    ax.add_patch(patches.Rectangle((20.1, -2.2), 0.4, 3.0,
                                     facecolor="#3a2a1a",
                                     edgecolor="#1a1a1a", linewidth=1.2))
    ax.text(2.5, 0.5, "steel\nedge\n(or brick)", fontsize=7, ha="center",
            color="#3a3a3a")

    # Bench legs and seat
    leg_h = 5
    ax.add_patch(patches.Rectangle((6, 0), 0.6, leg_h,
                                     facecolor="#5a3a1a",
                                     edgecolor="#1a1a1a", linewidth=1))
    ax.add_patch(patches.Rectangle((17.4, 0), 0.6, leg_h,
                                     facecolor="#5a3a1a",
                                     edgecolor="#1a1a1a", linewidth=1))
    # Seat slab
    ax.add_patch(patches.Rectangle((5, 5), 14, 1,
                                     facecolor="#6a4828",
                                     edgecolor="#1a1a1a", linewidth=1.2))
    ax.text(12, 5.5, "weathered cedar bench seat — 5 ft × 18\"",
            ha="center", va="center", fontsize=8, color="#fff",
            weight="bold")

    # Dim line
    ax.annotate("", xy=(4, -7), xytext=(20, -7),
                arrowprops=dict(arrowstyle="<->", color="#3a3a3a"))
    ax.text(12, -7.4, "60\" pad width (5 ft)", ha="center", va="top",
            fontsize=7, color="#3a3a3a")

    ax.text(-0.3, -9.0, "NOTES:\n"
            "• Compacted base prevents settling\n"
            "• Pea gravel on top — comfortable underfoot, drains fast\n"
            "• Steel or brick edge keeps pea gravel contained\n"
            "• Bench can be set on flagstone or anchored with 12\" stakes",
            fontsize=7, va="top", ha="left", color="#3a3a3a",
            family="monospace")


# --------------------------------------------------------------------
# Detail 3: Trench-cut bed edge
# --------------------------------------------------------------------

def detail_edge(ax):
    setup_detail(ax, "DETAIL 3 — Trench-Cut Bed Edge  (scale ~1:4)",
                 x_max=14, y_min=-6, y_max=4)

    # Base soil
    ax.add_patch(patches.Rectangle((-1, -6), 16, 6,
                                     facecolor="#7a5a3a",
                                     edgecolor="#3a2a1a", hatch="//"))

    # Lawn side (left)
    ax.add_patch(patches.Rectangle((-1, 0), 7, 0.4,
                                     facecolor="#7da155",
                                     edgecolor="#3a5a2a", linewidth=1))
    # Lawn grass tufts
    for x in range(0, 6):
        ax.plot([x + 0.3, x + 0.3], [0.4, 1.0],
                color="#3a5a2a", linewidth=1.2)
        ax.plot([x + 0.5, x + 0.6], [0.4, 0.9],
                color="#3a5a2a", linewidth=1.2)
        ax.plot([x + 0.7, x + 0.7], [0.4, 1.0],
                color="#3a5a2a", linewidth=1.2)
    ax.text(2.5, 1.5, "LAWN", fontsize=10, weight="bold",
            color="#3a5a2a", ha="center")

    # Trench cut (V-shape, 4" deep × 4" wide)
    trench = [(6, 0), (6.8, -1.2), (7.6, 0)]
    ax.add_patch(patches.Polygon(trench, closed=True,
                                   facecolor="#3a2a1a",
                                   edgecolor="#1a1a1a", linewidth=1.5))
    ax.text(6.8, -2.3, "trench\n4\" × 4\"\nre-cut\nspring",
            ha="center", va="top", fontsize=6.5,
            color="#3a3a3a", style="italic")

    # Bed side (right)
    ax.add_patch(patches.Rectangle((7.6, 0), 7, 0.5,
                                     facecolor="#9a6a3a", hatch="--",
                                     edgecolor="#5a4a3a", linewidth=1))
    ax.text(11, 0.7, "shredded hardwood mulch — 2-3\" deep",
            fontsize=7, ha="center", color="#3a3a3a")

    # Plants on bed side
    ax.add_patch(patches.Ellipse((9, 2.8), 1.5, 2.5,
                                   facecolor="#c66da8",
                                   edgecolor="#3a3a3a", alpha=0.6))
    ax.add_patch(patches.Ellipse((11.5, 2.5), 1.4, 2.0,
                                   facecolor="#c08552",
                                   edgecolor="#3a3a3a", alpha=0.6))
    ax.add_patch(patches.Ellipse((13.5, 2.0), 1.0, 1.4,
                                   facecolor="#9b7390",
                                   edgecolor="#3a3a3a", alpha=0.6))
    ax.text(11, 4.2, "PRAIRIE  /  SAVANNA  BED",
            fontsize=10, weight="bold", color="#3a5a2a", ha="center")

    ax.text(-0.3, -5.0, "NOTES:\n"
            "• No steel edging — softer, more naturalistic\n"
            "• Re-cut trench in early spring with a half-moon edger\n"
            "• Trench catches mulch creep and gives a crisp visual line",
            fontsize=7, va="top", ha="left", color="#3a3a3a",
            family="monospace")


# --------------------------------------------------------------------
# Detail 4: Fieldstone mowing strip alternative
# --------------------------------------------------------------------

def detail_mowing_strip(ax):
    setup_detail(ax, "DETAIL 4 — Fieldstone Mowing Strip  "
                 "(alternative to trench edge — scale ~1:4)",
                 x_max=14, y_min=-6, y_max=4)

    ax.add_patch(patches.Rectangle((-1, -6), 16, 6,
                                     facecolor="#7a5a3a",
                                     edgecolor="#3a2a1a", hatch="//"))

    # Lawn side
    ax.add_patch(patches.Rectangle((-1, 0), 6, 0.4,
                                     facecolor="#7da155",
                                     edgecolor="#3a5a2a", linewidth=1))
    for x in range(0, 5):
        ax.plot([x + 0.3, x + 0.3], [0.4, 1.0],
                color="#3a5a2a", linewidth=1.2)
        ax.plot([x + 0.7, x + 0.7], [0.4, 0.9],
                color="#3a5a2a", linewidth=1.2)
    ax.text(2, 1.5, "LAWN", fontsize=10, weight="bold",
            color="#3a5a2a", ha="center")

    # Fieldstone strip — flush with lawn so mower wheel can ride on it
    # 12" wide × 2" thick stones set in screenings
    ax.add_patch(patches.Rectangle((5, -1.5), 4, 1.5,
                                     facecolor="#9a8a72",
                                     edgecolor="#3a3a3a", linewidth=1))
    # Multiple stones
    for x in range(0, 4):
        ax.add_patch(patches.Rectangle((5 + x, 0), 0.95, 0.4,
                                         facecolor="#a89a82",
                                         edgecolor="#3a3a3a", linewidth=1))
    ax.text(7, -1.9, "fieldstone or flagstone — 12\" wide, 2\" thick",
            fontsize=7, ha="center", color="#3a3a3a")
    ax.text(7, -2.4, "set in 1\" screenings on compacted base",
            fontsize=6.5, ha="center", color="#3a3a3a", style="italic")

    # Bed side
    ax.add_patch(patches.Rectangle((9, 0), 5, 0.5,
                                     facecolor="#9a6a3a", hatch="--",
                                     edgecolor="#5a4a3a", linewidth=1))
    ax.text(11.5, 0.7, "mulch + plants",
            fontsize=7, ha="center", color="#3a3a3a")

    ax.add_patch(patches.Ellipse((10.5, 2.5), 1.5, 2.0,
                                   facecolor="#a04688",
                                   edgecolor="#3a3a3a", alpha=0.6))
    ax.add_patch(patches.Ellipse((13, 2.0), 1.2, 1.5,
                                   facecolor="#c08552",
                                   edgecolor="#3a3a3a", alpha=0.6))

    ax.text(-0.3, -4.2, "NOTES:\n"
            "• Stones set flush with lawn so mower wheel rides ON them\n"
            "• Eliminates string-trimming the bed edge\n"
            "• Pickable look matches savanna palette better than steel\n"
            "• Use 4-6 fieldstones for the bench-pad approach side only,\n"
            "  trench-cut elsewhere",
            fontsize=7, va="top", ha="left", color="#3a3a3a",
            family="monospace")


# --------------------------------------------------------------------
# Master figure (2×2 grid)
# --------------------------------------------------------------------

fig = plt.figure(figsize=(17, 12), dpi=160)

ax1 = fig.add_subplot(2, 2, 1); detail_path(ax1)
ax2 = fig.add_subplot(2, 2, 2); detail_bench(ax2)
ax3 = fig.add_subplot(2, 2, 3); detail_edge(ax3)
ax4 = fig.add_subplot(2, 2, 4); detail_mowing_strip(ax4)

fig.suptitle(
    "FRONT-YARD OAK SAVANNA EDGE — Construction Details (Drawing 3 of 5)",
    fontsize=15, weight="bold", color="#3a5a2a", y=0.997)
fig.text(0.5, 0.005,
         "8547 Crane Dance Trail · Eden Prairie MN  ·  for installer use  ·  "
         "all dims approximate, verify on-site",
         ha="center", va="bottom", fontsize=9, color="#5a4a3a",
         style="italic")

plt.tight_layout(rect=[0, 0.02, 1, 0.985])
plt.savefig(OUT / "construction-details.pdf", bbox_inches="tight",
            facecolor="white")
plt.savefig(OUT / "construction-details.png", bbox_inches="tight",
            facecolor="white", dpi=180)
print(f"details: {OUT / 'construction-details.pdf'}")
print(f"details: {OUT / 'construction-details.png'}")
