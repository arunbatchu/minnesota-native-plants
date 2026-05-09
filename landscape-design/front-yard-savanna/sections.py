"""
Cross-section drawings.

Section A — through the WEST third of the bed (with serviceberry, bench).
Section B — through the CENTER of the bed (in front of bay window — sightline
            preservation matters here).
Section C — through the VEGETATED SWALE (three moisture bands).

Each section is a side view: x = horizontal distance from foundation,
y = height above ground. Scale is honest — plants drawn at mature heights.

Output: sections.pdf and sections.png in annotated/.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "annotated"
OUT.mkdir(exist_ok=True)


# ---------------------------------------------------------------
# Plant silhouettes
# ---------------------------------------------------------------

def draw_tree(ax, x, base_y, trunk_h, canopy_h, canopy_w,
              trunk_color="#5a3a1a", canopy_color="#5a8a4a", alpha=0.85,
              label=None):
    # Trunk
    ax.add_patch(patches.Rectangle((x - 0.15, base_y), 0.3, trunk_h,
                                     facecolor=trunk_color,
                                     edgecolor=trunk_color, zorder=3))
    # Canopy
    ax.add_patch(patches.Ellipse((x, base_y + trunk_h + canopy_h / 2),
                                   canopy_w, canopy_h,
                                   facecolor=canopy_color,
                                   edgecolor="#3a5a3a",
                                   linewidth=0.8, zorder=3, alpha=alpha))
    if label:
        ax.text(x, base_y + trunk_h + canopy_h + 0.4, label,
                ha="center", va="bottom", fontsize=8, weight="bold",
                color="#1a3a1a")


def draw_shrub(ax, x, base_y, h, w, color="#7a9a5a", alpha=0.8, label=None):
    ax.add_patch(patches.Ellipse((x, base_y + h / 2), w, h,
                                   facecolor=color,
                                   edgecolor="#3a5a3a",
                                   linewidth=0.8, zorder=3, alpha=alpha))
    if label:
        ax.text(x, base_y + h + 0.2, label, ha="center", va="bottom",
                fontsize=7.5, color="#1a3a1a")


def draw_forb(ax, x, base_y, h, w=0.9, color="#a76aab", flower_color=None,
              alpha=0.85, label=None):
    # Stem cluster
    for dx in (-w * 0.3, 0, w * 0.3):
        ax.plot([x + dx, x + dx], [base_y, base_y + h * 0.85],
                color="#5a6a3a", linewidth=1.4, zorder=2)
    # Flower head/foliage
    ax.add_patch(patches.Ellipse((x, base_y + h * 0.9), w, h * 0.32,
                                   facecolor=flower_color or color,
                                   edgecolor="#3a3a3a", linewidth=0.5,
                                   zorder=3, alpha=alpha))
    if label:
        ax.text(x, base_y + h + 0.15, label, ha="center", va="bottom",
                fontsize=7, color="#3a3a3a")


def draw_grass(ax, x, base_y, h, w=0.7, color="#c0a060", alpha=0.85,
               label=None):
    # Tufted base + curving plumes
    for dx in (-w * 0.3, 0, w * 0.3):
        ax.plot([x + dx, x + dx + 0.1],
                [base_y, base_y + h],
                color=color, linewidth=2.0, zorder=2, alpha=alpha)
    # Plume tip
    ax.add_patch(patches.Ellipse((x, base_y + h - 0.05), w, 0.25,
                                   facecolor=color, edgecolor="#7a6038",
                                   linewidth=0.5, zorder=3, alpha=alpha))
    if label:
        ax.text(x, base_y + h + 0.15, label, ha="center", va="bottom",
                fontsize=7, color="#5a4a2a")


def draw_groundcover(ax, x_start, x_end, base_y, h=0.6, color="#9b9050",
                     alpha=0.7, label=None):
    ax.add_patch(patches.Rectangle((x_start, base_y),
                                     x_end - x_start, h,
                                     facecolor=color, edgecolor=color,
                                     linewidth=0.5, zorder=2, alpha=alpha))
    if label:
        ax.text((x_start + x_end) / 2, base_y + h + 0.15, label,
                ha="center", va="bottom", fontsize=6.5,
                color="#3a3a3a", style="italic")


# ---------------------------------------------------------------
# Common section frame
# ---------------------------------------------------------------

def setup_section(ax, title, x_max, y_max, soil_h=0.5):
    # Sky gradient (subtle)
    ax.add_patch(patches.Rectangle((-0.5, 0), x_max + 1, y_max,
                                     facecolor="#eef5fa", edgecolor="none",
                                     zorder=0))
    # Soil
    ax.add_patch(patches.Rectangle((-0.5, -soil_h), x_max + 1, soil_h,
                                     facecolor="#6b4a2a",
                                     edgecolor="#3a2a1a",
                                     linewidth=1, zorder=1))
    # Mulch line on top of soil
    ax.add_patch(patches.Rectangle((-0.5, 0), x_max + 1, 0.12,
                                     facecolor="#9a6a3a",
                                     edgecolor="none", zorder=1.5))
    # Grass at the end (lawn)
    ax.add_patch(patches.Rectangle((x_max - 1.5, 0), 2, 0.18,
                                     facecolor="#7da155",
                                     edgecolor="none", zorder=2))

    ax.set_xlim(-0.7, x_max + 1.0)
    ax.set_ylim(-soil_h - 0.3, y_max)

    # Height ruler on right
    for h in range(0, int(y_max) + 1, 2):
        ax.plot([x_max + 0.3, x_max + 0.5], [h, h], color="#5a4a3a",
                linewidth=1)
        ax.text(x_max + 0.6, h, f"{h} ft", fontsize=7, va="center",
                color="#5a4a3a")
    ax.plot([x_max + 0.4, x_max + 0.4], [0, y_max], color="#5a4a3a",
            linewidth=0.8)

    # Distance ruler on bottom
    for x in range(0, int(x_max) + 1, 2):
        ax.plot([x, x], [-soil_h - 0.05, -soil_h - 0.15],
                color="#5a4a3a", linewidth=1)
        ax.text(x, -soil_h - 0.22, f"{x}", fontsize=7, ha="center",
                va="top", color="#5a4a3a")
    ax.text(x_max / 2, -soil_h - 0.45, "distance from foundation (ft)",
            ha="center", va="top", fontsize=8, color="#5a4a3a")

    ax.set_title(title, fontsize=12, weight="bold", color="#3a5a2a",
                 loc="left", pad=10)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


def draw_foundation(ax, y_max):
    ax.add_patch(patches.Rectangle((-0.7, 0), 0.7, y_max,
                                     facecolor="#cbb892",
                                     edgecolor="#5a4a3a",
                                     linewidth=1.5, zorder=4))
    ax.text(-0.35, y_max / 2, "STUCCO\nFOUNDATION\nWALL\n(south face)",
            ha="center", va="center", fontsize=7, weight="bold",
            color="#3a3a3a", rotation=90)


# ---------------------------------------------------------------
# Section A — west third (with serviceberry & bench)
# ---------------------------------------------------------------

def section_a(ax):
    setup_section(ax, "SECTION A — through the WEST third  "
                  "(serviceberry anchor + bench pocket)",
                  x_max=12, y_max=20)
    draw_foundation(ax, 20)

    # Plants (close-to-foundation → outward)
    draw_shrub(ax, 1.5, 0, h=4, w=3, color="#8a4a3a",
               label="Gray Dogwood\n(6-10 ft mature)")
    draw_tree(ax, 3.0, 0, trunk_h=4, canopy_h=10, canopy_w=10,
              trunk_color="#5a3a1a", canopy_color="#6a8a4a",
              label="Serviceberry — 15-20 ft mature")

    draw_forb(ax, 5.0, 0, h=3.0, w=1.0, color="#5d6d9c",
              flower_color="#6a7ab0",
              label="False\nBlue Indigo")
    draw_forb(ax, 6.0, 0, h=2.5, w=0.9, color="#7a6abf",
              flower_color="#8a7ad0", label="Wild Lupine")

    # Bench
    bx = 7.5
    ax.add_patch(patches.Rectangle((bx - 1.5, 1.4), 3, 0.3,
                                     facecolor="#6a4828",
                                     edgecolor="#3a2818",
                                     linewidth=1, zorder=4))
    ax.add_patch(patches.Rectangle((bx - 1.4, 0), 0.18, 1.4,
                                     facecolor="#6a4828", zorder=4))
    ax.add_patch(patches.Rectangle((bx + 1.22, 0), 0.18, 1.4,
                                     facecolor="#6a4828", zorder=4))
    ax.text(bx, 1.85, "BENCH", ha="center", va="bottom",
            fontsize=8, weight="bold", color="#3a2818")

    draw_grass(ax, 9.0, 0, h=2.8, w=0.8, color="#c08552",
               label="Little Bluestem")
    draw_grass(ax, 10.0, 0, h=2.0, w=0.7, color="#a89060",
               label="Prairie\nDropseed")
    draw_groundcover(ax, 10.7, 11.7, 0, h=0.4, color="#9b7390",
                     label="Prairie Smoke")

    # Bed-edge marker
    ax.plot([12, 12], [0, 0.3], color="#3a3a3a", linewidth=2)
    ax.text(12.0, -0.15, "bed edge", ha="center", va="top",
            fontsize=7, style="italic", color="#3a3a3a")


# ---------------------------------------------------------------
# Section B — center bed (bay-window sightline)
# ---------------------------------------------------------------

def section_b(ax):
    setup_section(ax, "SECTION B — through the CENTER bed  "
                  "(directly in front of bay window — sightline preserved)",
                  x_max=12, y_max=8)
    draw_foundation(ax, 8)

    # Bay window dashed line
    ax.plot([0, 12], [4.5, 4.5], color="#3a6a8a",
            linewidth=1.2, linestyle=":", zorder=1.5)
    ax.text(11, 4.65, "bay-window sightline (~4.5 ft AGL)",
            ha="right", va="bottom", fontsize=7,
            color="#3a6a8a", style="italic")

    # Ninebark — kept LOW to preserve sightline (pruned at sill)
    draw_shrub(ax, 1.5, 0, h=3.0, w=2.5, color="#7a9a5a",
               label="Ninebark\n(pruned to <30\")")

    draw_forb(ax, 4.0, 0, h=3.0, w=1.0, color="#c66da8",
              flower_color="#d878b5", label="Wild Bergamot")
    draw_forb(ax, 5.5, 0, h=2.8, w=0.9, color="#a04688",
              flower_color="#b85a9a", label="Purple Coneflower")
    draw_forb(ax, 7.0, 0, h=1.6, w=0.7, color="#e0892a",
              flower_color="#f5a050", label="Butterfly\nMilkweed")
    draw_grass(ax, 8.5, 0, h=2.5, w=0.8, color="#c08552",
               label="Little Bluestem")
    draw_groundcover(ax, 9.3, 11.5, 0, h=0.5, color="#9b7390",
                     label="Prairie Smoke (groundcover)")

    # Bed edge
    ax.plot([12, 12], [0, 0.3], color="#3a3a3a", linewidth=2)


# ---------------------------------------------------------------
# Section C — vegetated swale
# ---------------------------------------------------------------

def section_c(ax):
    """A — vegetated swale cross-section.

    Three moisture bands; channel center has a slight depression with
    erosion-control blanket year 1.
    """
    setup_section(ax, "SECTION C — VEGETATED SWALE  "
                  "(3 moisture bands, no rock)",
                  x_max=12, y_max=4)
    draw_foundation(ax, 4)

    # Slight depression in soil (the channel)
    # Override soil with a curved channel
    ax.add_patch(patches.Rectangle((-0.5, -0.5), 13, 0.5,
                                     facecolor="#6b4a2a",
                                     edgecolor="#3a2a1a", zorder=1))
    # Carve channel (depression centered around x=6-9)
    chx = [3, 5, 6.5, 8, 10, 12]
    chy = [0, -0.3, -0.5, -0.4, -0.1, 0]
    ax.fill_between(chx, chy, [-0.5] * len(chx),
                    color="#6b4a2a", zorder=1.1)
    # Mulch + channel surface (no mulch in channel, mulch on rim only)
    ax.add_patch(patches.Rectangle((0, 0), 3, 0.12,
                                     facecolor="#9a6a3a", zorder=1.5))
    ax.add_patch(patches.Rectangle((10, 0), 2.5, 0.12,
                                     facecolor="#9a6a3a", zorder=1.5))

    # Erosion-control blanket on channel (year 1, biodegradable)
    ax.add_patch(patches.Rectangle((3, -0.45), 7, 0.05,
                                     facecolor="#a08858", edgecolor="none",
                                     hatch="...", zorder=1.6, alpha=0.7))

    # Plants — three bands
    # Dry rim (inland)
    draw_grass(ax, 1.0, 0, h=2.5, w=0.7, color="#c08552",
               label="Little Bluestem")
    draw_grass(ax, 2.0, 0, h=2.0, w=0.7, color="#a89060",
               label="Prairie Dropseed")

    # Moist slope
    draw_forb(ax, 3.5, 0, h=2.5, w=0.8, color="#d8639a",
              flower_color="#e87cb0",
              label="Swamp Milkweed")
    draw_forb(ax, 4.5, -0.1, h=2.2, w=0.8, color="#c92a40",
              flower_color="#e83a55", label="Cardinal\nFlower")

    # Wet channel center — sedges and rushes
    draw_grass(ax, 5.7, -0.4, h=2.0, w=0.7, color="#4a7d6c",
               label="Tussock\nSedge")
    draw_grass(ax, 6.6, -0.5, h=1.6, w=0.6, color="#5b8a72",
               label="Fox\nSedge")
    draw_forb(ax, 7.4, -0.45, h=2.0, w=0.7, color="#3a6a9c",
              flower_color="#4a7ab0", label="Blue\nFlag Iris")
    draw_grass(ax, 8.2, -0.4, h=1.5, w=0.6, color="#6a9580",
               label="Soft\nRush")

    # Moist slope on outer side
    draw_forb(ax, 9.5, -0.1, h=2.0, w=0.7, color="#5d6d9c",
              flower_color="#7a8acc",
              label="Great Blue\nLobelia")

    # Dry rim (outer/lawn side)
    draw_grass(ax, 10.5, 0, h=2.0, w=0.7, color="#a89060",
               label="Prairie Dropseed")

    # Annotation labels on channel
    ax.annotate("CHANNEL CENTER\n(wettest)\n9-12\" plug spacing",
                xy=(7, -0.5), xytext=(7, 3.4),
                fontsize=7.5, ha="center", color="#1a4a6a", weight="bold",
                arrowprops=dict(arrowstyle="-", color="#3a6a8a", lw=0.8))
    ax.annotate("MOIST SLOPE", xy=(4, -0.05), xytext=(4, 2.85),
                fontsize=7.5, ha="center", color="#1a4a6a",
                arrowprops=dict(arrowstyle="-", color="#3a6a8a", lw=0.6))
    ax.annotate("DRY RIM", xy=(1.5, 0.05), xytext=(1.5, 3.0),
                fontsize=7.5, ha="center", color="#5a4a2a",
                arrowprops=dict(arrowstyle="-", color="#7a6a4a", lw=0.6))

    # Erosion blanket label
    ax.text(6.5, -0.85, "biodegradable erosion-control blanket "
                       "(year 1 only — sedges break through)",
            ha="center", va="top", fontsize=6.5, style="italic",
            color="#5a4a2a")


# ---------------------------------------------------------------
# Master figure
# ---------------------------------------------------------------

fig = plt.figure(figsize=(17, 14), dpi=160)

ax_a = fig.add_subplot(3, 1, 1)
section_a(ax_a)

ax_b = fig.add_subplot(3, 1, 2)
section_b(ax_b)

ax_c = fig.add_subplot(3, 1, 3)
section_c(ax_c)

# Master title
fig.suptitle(
    "FRONT-YARD OAK SAVANNA EDGE — Cross-Sections (Drawing 2 of 5)",
    fontsize=15, weight="bold", color="#3a5a2a", y=0.995)

# Footer
fig.text(0.5, 0.005,
         "8547 Crane Dance Trail · Eden Prairie MN · "
         "south-facing, full sun, Hennepin moraine loam · "
         "all heights at mature size",
         ha="center", va="bottom", fontsize=9, color="#5a4a3a",
         style="italic")

plt.tight_layout(rect=[0, 0.02, 1, 0.985])
plt.savefig(OUT / "sections.pdf", bbox_inches="tight", facecolor="white")
plt.savefig(OUT / "sections.png", bbox_inches="tight", facecolor="white",
            dpi=180)
print(f"sections: {OUT / 'sections.pdf'}")
print(f"sections: {OUT / 'sections.png'}")
