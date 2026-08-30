#!/usr/bin/env python3
"""Generate static bloom-succession charts from the species trait data.

Chapter 6 and Chapter 10 both argue that continuous bloom matters more than
peak bloom — a garden with a spectacular July and nothing in April starves the
queen bumble bees that emerge in April. The book had no way to *see* that. The
Bloom Calendar MicroSim is interactive and unprintable; this produces a static
chart you can take outside.

Charts are inline SVG so they need no image files, scale to any width, and
follow the reader's light/dark theme through `currentColor` and a palette that
reads on both grounds.

Source of truth is .plant-gallery/traits.json (bloom month ranges) plus
.plant-gallery/species.json (which chapter each species is mentioned in).

Usage:
    python3 scripts/bloom-charts.py            # write into chapters 3, 4, 5
    python3 scripts/bloom-charts.py --check    # report only, write nothing
"""
import json
import re
import sys
from pathlib import Path

TRAITS = Path(".plant-gallery/traits.json")
SPECIES = Path(".plant-gallery/species.json")
CHAPTERS = Path("docs/chapters")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_N = {m: i for i, m in enumerate(MONTHS)}

# Season colours. Chosen to stay legible on both the light and dark Material
# grounds, and to make the spring and autumn shoulders visually distinct from
# the midsummer mass — the shoulders are the point of the chart.
SEASON = [
    (2, "#7e57c2", "Early spring"),    # Mar-Apr
    (4, "#43a047", "Late spring"),     # May-Jun
    (6, "#f9a825", "Summer"),          # Jul-Aug
    (8, "#e65100", "Fall"),            # Sep onward
]

# Which chapter's species list drives which chart.
CHARTS = [
    ("03-prairie-plants-grasslands", "Prairie Bloom Succession",
     "Every prairie species in this book that flowers, by month."),
    ("04-woodland-forest-plants", "Woodland Bloom Succession",
     "Woodland species by month. Note how much of it happens before June — "
     "that is the canopy closing."),
    ("05-wetland-shoreline-plants", "Wetland and Shoreline Bloom Succession",
     "Wetland and shoreline species by month."),
]

MARK_START = "<!-- BLOOM-CHART:START -->"
MARK_END = "<!-- BLOOM-CHART:END -->"

# A bloom-succession chart is read as a planting recommendation, so anything
# not native to Minnesota is excluded rather than drawn in a warning colour.
# Smooth Brome and Kentucky Bluegrass both flower in the prairie chapter's
# window and both belong nowhere near a "plant these" chart.
NOT_NATIVE = ("invasive", "non-native", "not a minnesota native",
              "not part of the minnesota native flora")


def is_native(trait):
    w = trait.get("wildlife", "").lower()
    return not any(marker in w for marker in NOT_NATIVE)


def parse_bloom(s):
    """'May-Jun' -> (4, 5). 'May' -> (4, 4). Non-flowering -> None."""
    months = re.findall(r"\b(" + "|".join(MONTHS) + r")\b", s)
    if not months:
        return None
    a = MONTH_N[months[0]]
    b = MONTH_N[months[-1]]
    return (a, b) if b >= a else (a, 11)


def season_color(start):
    color = SEASON[0][1]
    for lo, c, _ in SEASON:
        if start >= lo:
            color = c
    return color


def svg_chart(rows, title):
    """rows: list of (common_name, start_month, end_month), pre-sorted."""
    LEFT, TOP, ROW, RIGHT_PAD = 186, 44, 17, 16
    COL = 46
    width = LEFT + COL * 12 + RIGHT_PAD
    height = TOP + ROW * len(rows) + 34

    out = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{title}" style="max-width:100%;height:auto;'
        f'font-family:system-ui,-apple-system,sans-serif">',
        '<style>'
        '.bl-m{font-size:11px;fill:currentColor;opacity:.72}'
        '.bl-s{font-size:11px;fill:currentColor;opacity:.92}'
        '.bl-g{stroke:currentColor;opacity:.13}'
        '.bl-q{stroke:currentColor;opacity:.30}'
        '</style>',
    ]

    # month grid + labels
    for i, m in enumerate(MONTHS):
        x = LEFT + i * COL
        cls = "bl-q" if i in (3, 8) else "bl-g"   # Apr and Sep: the shoulders
        out.append(f'<line class="{cls}" x1="{x}" y1="{TOP - 16}" '
                   f'x2="{x}" y2="{height - 26}" stroke-width="1"/>')
        out.append(f'<text class="bl-m" x="{x + COL / 2}" y="{TOP - 22}" '
                   f'text-anchor="middle">{m}</text>')
    out.append(f'<line class="bl-g" x1="{LEFT + COL * 12}" y1="{TOP - 16}" '
               f'x2="{LEFT + COL * 12}" y2="{height - 26}" stroke-width="1"/>')

    for i, (name, a, b) in enumerate(rows):
        y = TOP + i * ROW
        x = LEFT + a * COL
        w = (b - a + 1) * COL
        label = name if len(name) <= 27 else name[:26] + "…"
        out.append(f'<text class="bl-s" x="{LEFT - 10}" y="{y + 10}" '
                   f'text-anchor="end">{label}</text>')
        out.append(f'<rect x="{x + 2}" y="{y + 2}" width="{w - 4}" height="11" '
                   f'rx="3" fill="{season_color(a)}" opacity="0.85"/>')

    # legend
    ly = height - 9
    lx = LEFT
    for _, color, label in SEASON:
        out.append(f'<rect x="{lx}" y="{ly - 9}" width="11" height="11" '
                   f'rx="2" fill="{color}" opacity="0.85"/>')
        out.append(f'<text class="bl-m" x="{lx + 16}" y="{ly}">{label}</text>')
        lx += 26 + len(label) * 6.4
    out.append("</svg>")
    return "\n".join(out)


def main(argv):
    check = "--check" in argv
    traits = json.loads(TRAITS.read_text())
    species = json.loads(SPECIES.read_text())

    # common name -> chapters it is mentioned in
    by_slug = {v["slug"]: v for v in species.values()}

    wrote = 0
    for chapter, title, blurb in CHARTS:
        rows = []
        excluded = 0
        for slug, t in traits.items():
            if slug.startswith("_"):
                continue
            sp = by_slug.get(slug)
            if not sp or chapter not in sp.get("mentioned_in", []):
                continue
            span = parse_bloom(t["bloom"])
            if not span:
                continue           # ferns, conifers: nothing to plot
            if not is_native(t):
                excluded += 1
                continue
            rows.append((sp["common_name"], span[0], span[1]))

        rows.sort(key=lambda r: (r[1], r[2], r[0]))
        if not rows:
            print(f"  {chapter}: no flowering species found — skipped")
            continue

        gaps = [MONTHS[m] for m in range(2, 10)
                if not any(a <= m <= b for _, a, b in rows)]
        note = (f"\n\nNo species in this chapter blooms in "
                f"{', '.join(gaps)}." if gaps else "")

        excl_note = (f" Non-native and invasive species mentioned in this "
                     f"chapter are left out — {excluded} of them — because a "
                     f"succession chart reads as a list of things to plant."
                     if excluded else "")

        block = (
            f"{MARK_START}\n"
            f"### {title}\n\n"
            f"{blurb} Bars show the typical bloom window in the Twin Cities — "
            f"a week or two later up north. The heavier lines mark April and "
            f"September, the two months a pollinator garden is most often "
            f"missing.{excl_note}{note}\n\n"
            f"<figure markdown>\n{svg_chart(rows, title)}\n"
            f"<figcaption>{len(rows)} native flowering species from this "
            f"chapter, ordered by when they open.</figcaption>\n</figure>\n"
            f"{MARK_END}"
        )

        path = CHAPTERS / chapter / "index.md"
        text = path.read_text()
        if MARK_START in text:
            text = re.sub(re.escape(MARK_START) + r".*?" + re.escape(MARK_END),
                          block, text, flags=re.S)
        else:
            anchor = "\n## Chapter Summary"
            if anchor not in text:
                print(f"  {chapter}: no Chapter Summary anchor — skipped")
                continue
            text = text.replace(anchor, f"\n{block}\n{anchor}", 1)

        if not check:
            path.write_text(text)
        wrote += 1
        print(f"  {chapter}: {len(rows)} species"
              + (f", gaps in {', '.join(gaps)}" if gaps else ", no gaps"))

    verb = "would write" if check else "wrote"
    print(f"\n{verb} {wrote} bloom chart(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
