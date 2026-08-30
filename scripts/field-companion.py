#!/usr/bin/env python3
"""Build the Minnesota Native Plants Field Companion — a printable booklet.

The book is a website. This is the part you can put in a back pocket and take
into the yard: a site-assessment checklist with room to write, a month-by-month
maintenance calendar, and the three bloom-succession charts.

Built with the booklet-pdf skill's helpers. Run bloom-charts.py and
bloom-charts-png.py first so the charts exist.

Usage:
    python3 scripts/field-companion.py
"""
from __future__ import annotations

import sys
from pathlib import Path

SKILL_SCRIPTS = Path.home() / ".claude/skills/booklet-pdf/scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

from reportlab.lib.units import inch                      # noqa: E402
from reportlab.pdfgen import canvas as rl_canvas          # noqa: E402

import lib                                                # noqa: E402
from lib import (                                         # noqa: E402
    C_ACCENT, C_INK, C_MUTED, C_NOTE_LINE, C_PAPER, C_RULE,
    C_SECTION_BG, C_TITLE,
    F_SANS, F_SANS_B, F_SERIF, F_SERIF_B, F_SERIF_I,
    content_box, draw_image_fit, draw_paragraph, draw_section_title,
    fill_paper, page_chrome, page_notes,
    page_section_intro,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/downloads/mn-native-plants-field-companion.pdf"
IMG = ROOT / "docs/downloads/img"
BOOK = "MN Native Plants — Field Companion"
SITE = "arunbatchu.github.io/minnesota-native-plants"


# ------------------------------------------------------------------
# Small drawing helpers specific to this booklet
# ------------------------------------------------------------------

def write_lines(c, x, y, w, n, gap=0.34 * inch):
    """n ruled lines to write on. Returns the y below the last one."""
    c.setStrokeColor(C_NOTE_LINE)
    c.setLineWidth(0.6)
    for _ in range(n):
        c.line(x, y, x + w, y)
        y -= gap
    return y


def checkbox_row(c, x, y, w, label, hint=""):
    """A square checkbox, a label, and an optional italic hint after it."""
    s = 9
    c.setStrokeColor(C_RULE)
    c.setLineWidth(0.9)
    c.rect(x, y - 1, s, s, fill=0, stroke=1)
    c.setFillColor(C_INK)
    c.setFont(F_SANS, 10)
    c.drawString(x + s + 7, y, label)
    if hint:
        wid = c.stringWidth(label, F_SANS, 10)
        c.setFillColor(C_MUTED)
        c.setFont(F_SERIF_I, 9.5)
        c.drawString(x + s + 12 + wid, y, hint)
    return y - 0.235 * inch


def field_row(c, x, y, w, label, rule_frac=0.62):
    """A label with a fill-in rule running to the right of it."""
    c.setFillColor(C_INK)
    c.setFont(F_SANS_B, 9.5)
    c.drawString(x, y, label)
    lx = x + w * (1 - rule_frac)
    c.setStrokeColor(C_NOTE_LINE)
    c.setLineWidth(0.6)
    c.line(lx, y - 2, x + w, y - 2)
    return y - 0.30 * inch


def subhead(c, x, y, w, text):
    c.setFillColor(C_ACCENT)
    c.setFont(F_SANS_B, 8.5)
    c.drawString(x, y, text.upper())
    y -= 0.09 * inch
    c.setStrokeColor(C_RULE)
    c.setLineWidth(0.8)
    c.line(x, y, x + w, y)
    return y - 0.21 * inch


# ------------------------------------------------------------------
# Pages
# ------------------------------------------------------------------

def page_cover(c):
    fill_paper(c)
    c.setFillColor(C_TITLE)
    c.rect(0, lib.PAGE_H - 3.9 * inch, lib.PAGE_W, 3.9 * inch, fill=1, stroke=0)

    c.setFillColor(C_PAPER)
    c.setFont(F_SANS_B, 10)
    c.drawCentredString(lib.PAGE_W / 2, lib.PAGE_H - 1.15 * inch,
                        "MINNESOTA NATIVE PLANTS")
    c.setFont(F_SERIF_B, 44)
    c.drawCentredString(lib.PAGE_W / 2, lib.PAGE_H - 2.0 * inch,
                        "Field Companion")
    c.setFont(F_SERIF_I, 13)
    c.drawCentredString(lib.PAGE_W / 2, lib.PAGE_H - 2.55 * inch,
                        "Take this outside. Write on it.")

    bree = ROOT / "docs/img/mascot/neutral.png"
    if bree.exists():
        draw_image_fit(c, bree, lib.PAGE_W / 2 - 0.9 * inch,
                       lib.PAGE_H * 0.34, 1.8 * inch, 1.8 * inch)

    c.setFillColor(C_INK)
    c.setFont(F_SERIF, 12)
    for i, line in enumerate([
            "A site-assessment checklist, a month-by-month",
            "maintenance calendar, and bloom charts for prairie,",
            "woodland and wetland — the parts of the book that",
            "work better on paper than on a screen."]):
        c.drawCentredString(lib.PAGE_W / 2, lib.PAGE_H * 0.29 - i * 17, line)

    c.setFillColor(C_MUTED)
    c.setFont(F_SANS, 8.5)
    c.drawCentredString(lib.PAGE_W / 2, 1.05 * inch, SITE)
    c.drawCentredString(lib.PAGE_W / 2, 0.85 * inch,
                        "CC BY-NC-SA 4.0 — print and share freely")


def page_site_assessment(c, n):
    fill_paper(c)
    page_chrome(c, n, section="Site Assessment", book_title=BOOK)
    x, y, w, h = content_box(n)
    y = y + h - 0.35 * inch
    y = draw_section_title(c, x, y, w, "01 — Before you buy anything",
                           "Assess the site")
    y -= 0.22 * inch
    y = draw_paragraph(
        c, "Fill this in before you choose a single plant. Almost every "
           "failed native planting is a plant put somewhere it was never "
           "adapted to.",
        x, y, w, font=F_SERIF, size=10.5, leading=14.5)
    y -= 0.24 * inch

    y = subhead(c, x, y, w, "The basics")
    for label in ["Date", "Location / address", "Bed name or area"]:
        y = field_row(c, x, y, w, label)
    y -= 0.10 * inch

    y = subhead(c, x, y, w, "Sun — count it, don't guess")
    y = draw_paragraph(
        c, "Check the spot every two hours from 8am to 6pm on a clear "
           "midsummer day. March readings mislead: the canopy is not out yet.",
        x, y, w, font=F_SERIF_I, size=9.5, leading=13)
    y -= 0.06 * inch
    for label, hint in [("Full sun", "6+ hours direct"),
                        ("Part sun / part shade", "3–6 hours, or dappled"),
                        ("Full shade", "under 3 hours")]:
        y = checkbox_row(c, x, y, w, label, hint)
    y = field_row(c, x, y - 0.02 * inch, w, "Hours counted")
    y -= 0.08 * inch

    y = subhead(c, x, y, w, "Moisture — the percolation test")
    y = draw_paragraph(
        c, "Dig a hole 12 inches deep and across. Fill it, let it drain, "
           "fill again, and time the second drain.",
        x, y, w, font=F_SERIF_I, size=9.5, leading=13)
    y -= 0.06 * inch
    for label, hint in [("Under 1 hour", "dry site"),
                        ("1–4 hours", "mesic — most Minnesota yards"),
                        ("Over 4 hours", "wet site")]:
        y = checkbox_row(c, x, y, w, label, hint)
    y = field_row(c, x, y - 0.02 * inch, w, "Drain time")
    y -= 0.08 * inch

    y = subhead(c, x, y, w, "Soil — the jar test")
    y = draw_paragraph(
        c, "A cup of soil in a quart jar of water with a teaspoon of dish "
           "soap. Shake, wait 48 hours. Sand settles first, then silt, then "
           "clay on top.",
        x, y, w, font=F_SERIF_I, size=9.5, leading=13)
    y -= 0.06 * inch
    for label, hint in [("Mostly sand", "fast drainage, low fertility"),
                        ("Mostly clay", "slow, holds nutrients"),
                        ("Roughly even — loam", "widest plant choice")]:
        y = checkbox_row(c, x, y, w, label, hint)


def page_site_assessment_2(c, n):
    fill_paper(c)
    page_chrome(c, n, section="Site Assessment", book_title=BOOK)
    x, y, w, h = content_box(n)
    y = y + h - 0.35 * inch

    y = subhead(c, x, y, w, "Look it up — five minutes, free")
    y = draw_paragraph(
        c, "Two lookups tell you more than any plant tag. The soil survey "
           "names the actual soil under your feet; the Marschner map shows "
           "what grew on your parcel before 1850.",
        x, y, w, font=F_SERIF, size=10.5, leading=14.5)
    y -= 0.12 * inch
    y = field_row(c, x, y, w, "USDA Web Soil Survey — map unit name")
    c.setFillColor(C_MUTED)
    c.setFont(F_SANS, 8)
    c.drawString(x, y + 0.10 * inch, "websoilsurvey.nrcs.usda.gov/app")
    y -= 0.16 * inch
    y = field_row(c, x, y, w, "Marschner pre-settlement community")
    c.setFillColor(C_MUTED)
    c.setFont(F_SANS, 8)
    c.drawString(x, y + 0.10 * inch,
                 "mnatlas.org/resources/vegetation-presettlement")
    y -= 0.22 * inch
    y = field_row(c, x, y, w, "USDA hardiness zone")
    y -= 0.10 * inch

    y = subhead(c, x, y, w, "Before you plant — the local rules")
    for label, hint in [
            ("Checked city vegetation-height ordinance", ""),
            ("Checked whether a managed-landscape permit is offered", ""),
            ("Checked HOA covenants", "a city permit does not override these"),
            ("Checked SWCD or Lawns to Legumes cost-share", "")]:
        y = checkbox_row(c, x, y, w, label, hint)
    y -= 0.12 * inch

    y = subhead(c, x, y, w, "Sketch the bed")
    c.setFillColor(C_MUTED)
    c.setFont(F_SERIF_I, 9.5)
    c.drawString(x, y, "North arrow, existing trees, downspouts, the wet spot.")
    y -= 0.18 * inch

    box_h = y - (content_box(n)[1] + 0.15 * inch)
    if box_h > 1.2 * inch:
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.9)
        c.rect(x, y - box_h, w, box_h, fill=0, stroke=1)
        # faint grid to sketch against
        c.setStrokeColor(C_NOTE_LINE)
        c.setLineWidth(0.3)
        step = 0.25 * inch
        gx = x + step
        while gx < x + w:
            c.line(gx, y - box_h, gx, y)
            gx += step
        gy = y - box_h + step
        while gy < y:
            c.line(x, gy, x + w, gy)
            gy += step


MONTHS = [
    ("January", ["Order seed and plugs — good stock sells out by March",
                 "Read; plan next season's bed"]),
    ("February", ["Start 90-day stratification for lupine, shooting star",
                  "Prune shrubs while dormant"]),
    ("March", ["Start 60-day stratification for the bluestems, leadplant",
               "Frost-seed onto snow or frozen ground",
               "Cut last year's stems — late, so overwintering insects emerge"]),
    ("April", ["Prescribed burn window, with training and permits",
               "First spring ephemerals — Bloodroot, Hepatica, Pasque Flower",
               "Queen bumble bees emerge and need flowers NOW"]),
    ("May", ["Plant plugs and containers once frost risk passes",
             "Pull garlic mustard before seed pods mature",
             "Peak woodland bloom — visit a remnant to see it"]),
    ("June", ["Water new plantings deeply: 1 inch a week, not daily sprinkles",
              "Cut wild parsnip roots below the crown — wear long sleeves",
              "Showy Lady's Slipper blooms in fens"]),
    ("July", ["Spot-weed; do not let anything set seed",
              "Peak prairie bloom",
              "Leave the hose off unless it is a first-year planting"]),
    ("August", ["Collect ripe seed — if you have to tug, it is not ready",
                "Take the 10% rule seriously; never from public land "
                "without a permit",
                "Cut-stump herbicide season opens for woody invasives"]),
    ("September", ["Best month for cut-stump buckthorn treatment",
                   "New bumble bee queens fattening — late bloom matters",
                   "Divide and move perennials"]),
    ("October", ["Leave the leaves; leave the stems standing",
                 "Plant trees and shrubs",
                 "Note the gaps — what had nothing blooming this year?"]),
    ("November", ["Fall dormant seeding — let winter do the stratification",
                  "Last call for cut-stump treatment"]),
    ("December", ["Nothing. That is the correct answer.",
                  "Winter tree ID: bark, buds, silhouette"]),
]


def page_calendar(c, n, months, part):
    fill_paper(c)
    page_chrome(c, n, section="Maintenance Calendar", book_title=BOOK)
    x, y, w, h = content_box(n)
    y = y + h - 0.35 * inch

    if part == 1:
        y = draw_section_title(c, x, y, w, "02 — The year",
                               "Maintenance calendar")
        y -= 0.20 * inch
        y = draw_paragraph(
            c, "A native planting asks for less work than a lawn, but the "
               "work it does ask for is time-sensitive. Timing is what "
               "decides whether an hour spent helps or hurts.",
            x, y, w, font=F_SERIF, size=10.5, leading=14.5)
        y -= 0.26 * inch

    for i, (month, items) in enumerate(months):
        block_h = 0.30 * inch + len(items) * 0.185 * inch
        if i % 2 == 0:
            c.setFillColor(C_SECTION_BG)
            c.rect(x - 6, y - block_h + 0.12 * inch, w + 12, block_h,
                   fill=1, stroke=0)
        c.setFillColor(C_TITLE)
        c.setFont(F_SERIF_B, 13)
        c.drawString(x, y, month)
        y -= 0.21 * inch
        c.setFont(F_SANS, 9.5)
        for item in items:
            c.setFillColor(C_ACCENT)
            c.drawString(x + 4, y, "•")
            c.setFillColor(C_INK)
            for j, line in enumerate(lib.wrap_text(c, item, F_SANS, 9.5,
                                                   w - 18)):
                c.drawString(x + 16, y - j * 11.5, line)
                if j:
                    y -= 11.5
            y -= 0.185 * inch
        y -= 0.10 * inch


def page_bloom(c, n, img, kicker, title, caption):
    fill_paper(c)
    page_chrome(c, n, section="Bloom Succession", book_title=BOOK)
    x, y, w, h = content_box(n)
    cy = y + h - 0.35 * inch
    cy = draw_section_title(c, x, cy, w, kicker, title)
    cy -= 0.18 * inch
    cy = draw_paragraph(c, caption, x, cy, w,
                        font=F_SERIF, size=10.5, leading=14.5)
    cy -= 0.14 * inch
    draw_image_fit(c, img, x, y + 0.05 * inch, w, cy - y - 0.05 * inch)


def page_back_cover(c):
    fill_paper(c)
    c.setFillColor(C_TITLE)
    c.rect(0, 0, lib.PAGE_W, 2.6 * inch, fill=1, stroke=0)

    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 20)
    c.drawCentredString(lib.PAGE_W / 2, lib.PAGE_H * 0.68,
                        "The rest of the book lives online")
    c.setFillColor(C_INK)
    c.setFont(F_SERIF, 11.5)
    for i, line in enumerate([
            "17 chapters · 289 concepts · 22 interactive simulations",
            "211 species cards · 340 quiz questions",
            "", SITE]):
        c.drawCentredString(lib.PAGE_W / 2, lib.PAGE_H * 0.60 - i * 19, line)

    bree = ROOT / "docs/img/mascot/welcome.png"
    if bree.exists():
        draw_image_fit(c, bree, lib.PAGE_W / 2 - 0.8 * inch,
                       lib.PAGE_H * 0.36, 1.6 * inch, 1.6 * inch)

    c.setFillColor(C_PAPER)
    c.setFont(F_SERIF_I, 12)
    c.drawCentredString(lib.PAGE_W / 2, 1.55 * inch,
                        "“Let's grow together.”")
    c.setFont(F_SANS, 8.5)
    c.drawCentredString(lib.PAGE_W / 2, 1.15 * inch,
                        "Bree — rusty-patched bumble bee (Bombus affinis),")
    c.drawCentredString(lib.PAGE_W / 2, 1.0 * inch,
                        "Minnesota's state bee, federally endangered")
    c.drawCentredString(lib.PAGE_W / 2, 0.62 * inch,
                        "CC BY-NC-SA 4.0 · Arun Batchu")


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = rl_canvas.Canvas(str(OUT), pagesize=(lib.PAGE_W, lib.PAGE_H))
    c.setTitle("Minnesota Native Plants — Field Companion")
    c.setAuthor("Arun Batchu")

    page_cover(c); c.showPage()
    page_site_assessment(c, 2); c.showPage()
    page_site_assessment_2(c, 3); c.showPage()
    page_calendar(c, 4, MONTHS[:6], part=1); c.showPage()
    page_calendar(c, 5, MONTHS[6:], part=2); c.showPage()

    charts = [
        (IMG / "bloom-prairie.png", "03 — Bloom succession", "Prairie",
         "Every native prairie species in this book that flowers, by month. "
         "The heavier lines mark April and September — the two months a "
         "pollinator garden is most often missing."),
        (IMG / "bloom-woodland.png", "03 — Bloom succession", "Woodland",
         "Most of the woodland year happens before June. That is the canopy "
         "closing, and it is why spring ephemerals move so fast."),
        (IMG / "bloom-wetland.png", "03 — Bloom succession",
         "Wetland and shoreline",
         "Wetland and shoreline species by month."),
    ]
    # Portrait, not landscape. The charts are square-to-tall (aspect 0.89 to
    # 1.45), so a portrait page gives them more of the dimension they actually
    # need. Landscape letterboxed them into half the page.
    n = 6
    for img, kicker, title, caption in charts:
        page_bloom(c, n, img, kicker, title, caption)
        c.showPage()
        n += 1

    page_notes(c, n, prompt="What is blooming today, and what is not?",
               book_title=BOOK); c.showPage()
    n += 1
    page_notes(c, n, prompt="Species to look up when you get home.",
               book_title=BOOK); c.showPage()

    page_back_cover(c); c.showPage()
    c.save()
    size = OUT.stat().st_size // 1024
    print(f"wrote {OUT.relative_to(ROOT)}  ({n + 1} pages, {size}KB)")


if __name__ == "__main__":
    build()
