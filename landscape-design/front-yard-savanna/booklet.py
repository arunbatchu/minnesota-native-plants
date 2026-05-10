"""
Print-ready booklet — Front-Yard Oak Savanna Edge.

Generates booklet.pdf, US Letter portrait, ~32 pages. Designed to be:
  - printed at home or a print shop, 2-sided
  - 3-hole punched or spiral bound
  - written in (lined notes pages between sections)
  - carried to installer meetings

Section order:
  1.  Cover
  2.  Title block & contents
  3.  Project vision (text)
  4.  Site facts
  5.  NOTES
  6.  Site plan (full page)
  7.  Cross-sections (full page)
  8.  Construction details (full page)
  9.  NOTES
  10. Planting plan (tables, multiple pages)
  11. Bloom calendar (full page)
  12. NOTES
  13. Year 1 / Year 3 / Year 5 / Bench vignette renderings (one each)
  14. NOTES
  15. Mood board (curated references)
  16. Cost & install
  17. Maintenance & risk
  18. NOTES (multi-page final section)
  19. Back cover
"""
from __future__ import annotations

from pathlib import Path
from contextlib import contextmanager
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

ROOT = Path(__file__).parent
ANNOTATED = ROOT / "annotated"
OUT_PDF = ROOT / "booklet.pdf"

# ---- design tokens ----
PAGE_W, PAGE_H = letter  # 8.5 x 11
MARGIN_OUTER = 0.6 * inch
MARGIN_INNER = 0.85 * inch
MARGIN_TOP = 0.7 * inch
MARGIN_BOTTOM = 0.8 * inch

C_INK = HexColor("#1f2a1a")
C_TITLE = HexColor("#2a4a25")
C_ACCENT = HexColor("#5d3a1f")
C_RULE = HexColor("#aea580")
C_NOTE_LINE = HexColor("#bdb39a")
C_PAPER = HexColor("#fcf9f0")
C_MUTED = HexColor("#5e5544")
C_SECTION_BG = HexColor("#e8e2cd")

# Try to register a serif & sans pair for visual quality. Fall back to
# built-ins if anything fails.
def _register_fonts() -> tuple[str, str, str, str]:
    serif = "Times-Roman"
    serif_b = "Times-Bold"
    sans = "Helvetica"
    sans_b = "Helvetica-Bold"
    try:
        pdfmetrics.registerFont(TTFont(
            "Avenir", "/System/Library/Fonts/Avenir.ttc"))
        sans = "Avenir"
    except Exception:
        pass
    try:
        pdfmetrics.registerFont(TTFont(
            "AvenirHeavy", "/System/Library/Fonts/Avenir.ttc",
            subfontIndex=7))
        sans_b = "AvenirHeavy"
    except Exception:
        pass
    # Baskerville.ttc has caused mid-word kerning glitches in body text;
    # stick with Times-Roman (PDF built-in) for consistent rendering.
    return serif, serif_b, sans, sans_b


F_SERIF, F_SERIF_B, F_SANS, F_SANS_B = _register_fonts()


# ============================================================
# Landscape orientation context — for image-heavy pages.
# Mutates module-level PAGE_W/PAGE_H so the existing helpers
# (_content_box, _page_chrome, _fill_paper) Just Work.
# ============================================================

@contextmanager
def landscape_orientation(c):
    """Switch the canvas (and module-level dimensions) to landscape
    letter for the duration of the with-block. Restores portrait on exit.
    """
    global PAGE_W, PAGE_H
    portrait_w, portrait_h = PAGE_W, PAGE_H
    landscape_w, landscape_h = landscape(letter)
    c.setPageSize((landscape_w, landscape_h))
    PAGE_W, PAGE_H = landscape_w, landscape_h
    try:
        yield
    finally:
        PAGE_W, PAGE_H = portrait_w, portrait_h
        c.setPageSize((portrait_w, portrait_h))


# ============================================================
# Low-level helpers
# ============================================================

def _fill_paper(c):
    c.setFillColor(C_PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)


def _is_left_page(page_num: int) -> bool:
    """For 2-sided printing: even page numbers are LEFT-side (verso),
    odd are RIGHT-side (recto). Page 1 (cover) is recto."""
    return page_num % 2 == 0


def _content_box(page_num: int) -> tuple[float, float, float, float]:
    """Return (x, y, w, h) of the content box for this page."""
    if _is_left_page(page_num):
        # Left page: bind on right
        x = MARGIN_OUTER
        right_margin = MARGIN_INNER
    else:
        # Right page: bind on left
        x = MARGIN_INNER
        right_margin = MARGIN_OUTER
    y = MARGIN_BOTTOM
    w = PAGE_W - x - right_margin
    h = PAGE_H - MARGIN_TOP - MARGIN_BOTTOM
    return x, y, w, h


def _page_chrome(c, page_num: int, section: str | None = None,
                 show_page_num: bool = True):
    """Header bar, footer, page number."""
    if section:
        c.setFillColor(C_MUTED)
        c.setFont(F_SANS, 8)
        if _is_left_page(page_num):
            c.drawString(MARGIN_OUTER, PAGE_H - MARGIN_TOP + 0.25 * inch,
                         section.upper())
        else:
            c.drawRightString(PAGE_W - MARGIN_OUTER,
                              PAGE_H - MARGIN_TOP + 0.25 * inch,
                              section.upper())
        # Top rule
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.5)
        x, _, w, _ = _content_box(page_num)
        c.line(x, PAGE_H - MARGIN_TOP + 0.18 * inch,
               x + w, PAGE_H - MARGIN_TOP + 0.18 * inch)

    # Footer
    c.setFillColor(C_MUTED)
    c.setFont(F_SANS, 7.5)
    if show_page_num:
        if _is_left_page(page_num):
            c.drawString(MARGIN_OUTER, MARGIN_BOTTOM - 0.35 * inch,
                         f"{page_num}   ·   Front-Yard Oak Savanna Edge")
        else:
            c.drawRightString(PAGE_W - MARGIN_OUTER,
                              MARGIN_BOTTOM - 0.35 * inch,
                              f"Front-Yard Oak Savanna Edge   ·   "
                              f"{page_num}")


def _wrap_text(c, text: str, font: str, size: float,
               width: float) -> list[str]:
    """Wrap text into lines that fit the given width."""
    c.setFont(font, size)
    words = text.split()
    lines = []
    current = ""
    for w in words:
        trial = (current + " " + w).strip()
        if c.stringWidth(trial, font, size) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def _draw_paragraph(c, text: str, x: float, y: float, w: float,
                    font: str = F_SERIF, size: float = 11,
                    leading: float = 15, color=C_INK,
                    align: str = "left") -> float:
    """Draw a wrapped paragraph. Returns the new y after the paragraph."""
    c.setFillColor(color)
    lines = _wrap_text(c, text, font, size, w)
    cur_y = y
    for line in lines:
        c.setFont(font, size)
        if align == "center":
            c.drawCentredString(x + w / 2, cur_y, line)
        elif align == "right":
            c.drawRightString(x + w, cur_y, line)
        else:
            c.drawString(x, cur_y, line)
        cur_y -= leading
    return cur_y


def _draw_image_fit(c, path: Path, x: float, y: float, w: float, h: float,
                    caption: str | None = None,
                    caption_height: float = 0.4 * inch,
                    rotate: int = 0):
    """Draw an image scaled to fit (preserving aspect) in the box,
    optionally with a caption below.

    rotate: degrees counter-clockwise. Use -90 or 270 for "lay sideways
    so the long axis runs top-to-bottom" (book turned 90° CW to read)."""
    if not path.exists():
        c.setFillColor(HexColor("#f4cccc"))
        c.rect(x, y, w, h, fill=1, stroke=1)
        c.setFillColor(C_INK)
        c.setFont(F_SANS, 9)
        c.drawCentredString(x + w / 2, y + h / 2,
                            f"missing: {path.name}")
        return

    img = PILImage.open(path)
    if rotate:
        img = img.rotate(rotate, expand=True, resample=PILImage.BICUBIC)
    iw, ih = img.size
    img_h_for_box = h - (caption_height if caption else 0)
    aspect = iw / ih
    if aspect > w / img_h_for_box:
        # Image wider — fit to width
        draw_w = w
        draw_h = w / aspect
    else:
        draw_h = img_h_for_box
        draw_w = img_h_for_box * aspect
    draw_x = x + (w - draw_w) / 2
    draw_y = y + (img_h_for_box - draw_h) + (caption_height if caption else 0)
    if rotate:
        # Use ImageReader so we can pass the rotated PIL.Image directly
        from reportlab.lib.utils import ImageReader
        c.drawImage(ImageReader(img), draw_x, draw_y,
                    width=draw_w, height=draw_h,
                    preserveAspectRatio=True, mask="auto")
    else:
        c.drawImage(str(path), draw_x, draw_y,
                    width=draw_w, height=draw_h,
                    preserveAspectRatio=True, mask="auto")
    if caption:
        c.setFillColor(C_MUTED)
        c.setFont(F_SANS, 8.5)
        # caption is wrapped if needed
        caption_lines = _wrap_text(c, caption, F_SANS, 8.5, w - 0.1 * inch)
        cy = y + caption_height - 0.18 * inch
        for line in caption_lines[:2]:
            c.drawCentredString(x + w / 2, cy, line)
            cy -= 0.16 * inch


def _draw_section_title(c, x: float, y: float, w: float,
                        kicker: str, title: str) -> float:
    """Section opening: small kicker + big title. Returns y after."""
    c.setFillColor(C_ACCENT)
    c.setFont(F_SANS_B, 9)
    c.drawString(x, y, kicker.upper())
    y -= 0.32 * inch
    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 28)
    # Wrap title if too long
    lines = _wrap_text(c, title, F_SERIF_B, 28, w)
    for line in lines:
        c.drawString(x, y, line)
        y -= 0.42 * inch
    # Rule
    c.setStrokeColor(C_RULE)
    c.setLineWidth(1.2)
    c.line(x, y + 0.1 * inch, x + 0.8 * inch, y + 0.1 * inch)
    y -= 0.1 * inch
    return y


# ============================================================
# Page builders
# ============================================================

def page_cover(c):
    """Page 1 — front cover. Hero image + title overlay."""
    _fill_paper(c)
    # Hero image full bleed of upper 60%
    hero = ANNOTATED / "render-year5.png"
    if hero.exists():
        img = PILImage.open(hero)
        iw, ih = img.size
        # Crop to fit upper portion proportionally
        target_w = PAGE_W
        target_h = PAGE_H * 0.66
        aspect = iw / ih
        if aspect > target_w / target_h:
            draw_w = target_h * aspect
            draw_h = target_h
            draw_x = -(draw_w - target_w) / 2
        else:
            draw_w = target_w
            draw_h = target_w / aspect
            draw_x = 0
        c.drawImage(str(hero), draw_x, PAGE_H - target_h,
                    width=draw_w, height=draw_h,
                    preserveAspectRatio=False, mask="auto")
        # subtle dark gradient overlay at top for title legibility
        c.setFillColorRGB(0, 0, 0, alpha=0.35)
        c.rect(0, PAGE_H - 2.0 * inch, PAGE_W, 2.0 * inch,
               fill=1, stroke=0)

    # Title block over the hero
    c.setFillColor(HexColor("#fdfaf0"))
    c.setFont(F_SERIF_B, 38)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.1 * inch,
                        "Front-Yard")
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.55 * inch,
                        "Oak Savanna Edge")
    c.setFont(F_SANS, 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.85 * inch,
                        "A Minnesota-native pollinator garden, "
                        "designed and to be built")

    # Bottom band
    c.setFillColor(C_PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H * 0.34, fill=1, stroke=0)
    c.setStrokeColor(C_RULE)
    c.setLineWidth(2)
    c.line(0.6 * inch, PAGE_H * 0.34, PAGE_W - 0.6 * inch, PAGE_H * 0.34)

    # Bottom info
    bx = 0.85 * inch
    by = PAGE_H * 0.30
    c.setFillColor(C_MUTED)
    c.setFont(F_SANS_B, 8)
    c.drawString(bx, by, "SITE")
    c.setFillColor(C_INK)
    c.setFont(F_SERIF, 13)
    c.drawString(bx, by - 0.22 * inch,
                 "8547 Crane Dance Trail   ·   Eden Prairie, MN 55344")
    c.setFont(F_SANS, 9)
    c.setFillColor(C_MUTED)
    c.drawString(bx, by - 0.42 * inch,
                 "Lot 0.36 ac  ·  Hennepin County  ·  USDA 4b/5a microclimate")

    by -= 0.95 * inch
    c.setFont(F_SANS_B, 8)
    c.setFillColor(C_MUTED)
    c.drawString(bx, by, "DESIGNED FOR")
    c.setFillColor(C_INK)
    c.setFont(F_SERIF, 13)
    c.drawString(bx, by - 0.22 * inch, "Arun & Rima Batchu")

    by -= 0.55 * inch
    c.setFont(F_SANS_B, 8)
    c.setFillColor(C_MUTED)
    c.drawString(bx, by, "DESIGNER  ·  PACKAGE")
    c.setFillColor(C_INK)
    c.setFont(F_SERIF, 11)
    c.drawString(bx, by - 0.22 * inch,
                 "Claude (acting as MN native-plants specialist)  "
                 "·  v1.0")

    # Mascot tag in lower right
    c.setFont(F_SANS, 7)
    c.setFillColor(C_MUTED)
    c.drawRightString(PAGE_W - 0.6 * inch, 0.5 * inch,
                      "with thanks to Bree the Bee 🐝")


def page_title_and_contents(c):
    """Page 2 — title page reprise + table of contents."""
    _fill_paper(c)
    page = 2
    _page_chrome(c, page, section="Contents")
    x, y, w, h = _content_box(page)

    # Brand mark
    c.setFillColor(C_ACCENT)
    c.setFont(F_SANS_B, 9)
    c.drawString(x, y + h - 0.2 * inch, "DESIGN PACKAGE")
    c.setFont(F_SERIF_B, 22)
    c.setFillColor(C_TITLE)
    c.drawString(x, y + h - 0.6 * inch, "Front-Yard Oak Savanna Edge")
    c.setFont(F_SERIF, 12)
    c.setFillColor(C_INK)
    c.drawString(x, y + h - 0.9 * inch,
                 "A Minnesota-native pollinator garden")
    c.setStrokeColor(C_RULE)
    c.setLineWidth(0.8)
    c.line(x, y + h - 1.05 * inch, x + 1.5 * inch, y + h - 1.05 * inch)

    cur_y = y + h - 1.5 * inch
    c.setFillColor(C_MUTED)
    c.setFont(F_SANS_B, 9)
    c.drawString(x, cur_y, "CONTENTS")
    cur_y -= 0.35 * inch

    contents = [
        ("01", "Vision",                          "Why this garden, why now"),
        ("02", "Site facts",                      "What the property tells us"),
        ("",   "Notes",                           ""),
        ("03", "Site Plan",                       "Top-down master drawing"),
        ("04", "Cross-Sections",                  "Side views — west third, "
                                                  "center, swale"),
        ("05", "Construction Details",            "Path, bench pad, edges"),
        ("",   "Notes",                           ""),
        ("06", "Planting Plan",                   "Every plant, with quantity "
                                                  "and source"),
        ("07", "Bloom Calendar",                  "Continuous bloom Apr–Nov"),
        ("",   "Notes",                           ""),
        ("08", "Year 1",                          "How it looks just installed"),
        ("09", "Year 3 — July peak",              "How it looks established"),
        ("10", "Year 5",                          "How it looks matured"),
        ("·",  "    Year 3 — May spring",         "Lupine, Baptisia, Prairie Smoke"),
        ("·",  "    Bench in place",              "Closer view of the seating pocket"),
        ("11", "Bench Vignette",                  "An afternoon at the seat"),
        ("",   "Notes",                           ""),
        ("12", "Mood Board",                      "Gardens to visit, "
                                                  "references"),
        ("13", "Cost & Install",                  "Phasing, quotes, "
                                                  "installers"),
        ("14", "Maintenance & Risk",              "Year-by-year care"),
        ("15", "Plant Profiles",                  "Curtis-style botanical pages — 16 species"),
        ("",   "Notes & sketches",                "Multiple lined pages"),
    ]

    for num, title, sub in contents:
        c.setFillColor(C_ACCENT if num else C_MUTED)
        c.setFont(F_SANS_B, 9)
        c.drawString(x, cur_y, num if num else "·")
        c.setFillColor(C_INK)
        c.setFont(F_SERIF_B if num else F_SERIF, 11)
        c.drawString(x + 0.5 * inch, cur_y, title)
        if sub:
            c.setFillColor(C_MUTED)
            c.setFont(F_SERIF, 9.5)
            c.drawString(x + 2.4 * inch, cur_y, sub)
        cur_y -= 0.27 * inch

    # Footnote
    c.setFillColor(C_MUTED)
    c.setFont(F_SANS, 7)
    c.drawString(x, y + 0.4 * inch,
                 "Print 2-sided.  Fold a corner to bookmark where you are.  "
                 "Write in the notes pages.")


def page_section_intro(c, page_num: int, kicker: str, title: str,
                       body_paragraphs: list[str], section: str):
    _fill_paper(c)
    _page_chrome(c, page_num, section=section)
    x, y, w, h = _content_box(page_num)
    cur_y = y + h - 0.4 * inch
    cur_y = _draw_section_title(c, x, cur_y, w, kicker, title)
    cur_y -= 0.35 * inch

    for para in body_paragraphs:
        cur_y = _draw_paragraph(c, para, x, cur_y, w,
                                font=F_SERIF, size=11.5, leading=16)
        cur_y -= 0.12 * inch


def page_notes(c, page_num: int, prompt: str = ""):
    """A lined notes page."""
    _fill_paper(c)
    _page_chrome(c, page_num, section="Notes")
    x, y, w, h = _content_box(page_num)

    # Title
    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 22)
    c.drawString(x, y + h - 0.4 * inch, "Notes")

    if prompt:
        c.setFillColor(C_ACCENT)
        c.setFont(F_SANS, 10)
        prompt_lines = _wrap_text(c, prompt, F_SANS, 10, w)
        py = y + h - 0.85 * inch
        for line in prompt_lines:
            c.drawString(x, py, line)
            py -= 0.18 * inch
        line_top = py - 0.3 * inch
    else:
        line_top = y + h - 0.95 * inch

    # Lined area
    c.setStrokeColor(C_NOTE_LINE)
    c.setLineWidth(0.4)
    line_spacing = 0.36 * inch
    cy = line_top
    while cy > y + 0.2 * inch:
        c.line(x, cy, x + w, cy)
        cy -= line_spacing


def page_full_image(c, page_num: int, image_path: Path,
                    section: str, kicker: str, title: str,
                    caption: str = "",
                    rotate_image: int = 0):
    _fill_paper(c)
    _page_chrome(c, page_num, section=section)
    x, y, w, h = _content_box(page_num)

    # Title
    c.setFillColor(C_ACCENT)
    c.setFont(F_SANS_B, 9)
    c.drawString(x, y + h - 0.05 * inch, kicker.upper())
    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 20)
    c.drawString(x, y + h - 0.4 * inch, title)
    # rule
    c.setStrokeColor(C_RULE)
    c.line(x, y + h - 0.55 * inch, x + 0.7 * inch, y + h - 0.55 * inch)

    img_top = y + h - 0.85 * inch
    img_bottom = y + (1.0 * inch if caption else 0.3 * inch)
    img_h = img_top - img_bottom
    _draw_image_fit(c, image_path, x, img_bottom, w, img_h,
                    caption=None, rotate=rotate_image)

    if caption:
        cy = y + 0.85 * inch
        c.setFillColor(C_MUTED)
        c.setFont(F_SANS, 9.5)
        cap_lines = _wrap_text(c, caption, F_SANS, 9.5, w)
        for line in cap_lines:
            c.drawString(x, cy, line)
            cy -= 0.16 * inch


def page_planting_plan(c, page_num: int):
    _fill_paper(c)
    _page_chrome(c, page_num, section="Planting Plan")
    x, y, w, h = _content_box(page_num)
    cur_y = y + h - 0.2 * inch
    cur_y = _draw_section_title(c, x, cur_y, w,
                                "06 — Planting Plan",
                                "Every plant, every quantity")
    cur_y -= 0.2 * inch

    # Backbone table
    cur_y = _draw_table_header(c, x, cur_y, w,
                               "BACKBONE — woody anchors",
                               ["#", "Common name", "Scientific",
                                "Qty", "Mature"])
    rows = [
        ("1",  "Serviceberry",   "Amelanchier laevis",      "1", "15-20 ft"),
        ("2-3", "Ninebark",      "Physocarpus opulifolius", "2", "5-8 ft *"),
        ("4",  "Gray Dogwood",   "Cornus racemosa",         "1", "6-10 ft"),
    ]
    cur_y = _draw_table_rows(c, x, cur_y, w, rows)
    c.setFillColor(C_MUTED)
    c.setFont(F_SANS, 8)
    c.drawString(x, cur_y, "* prune ninebarks below 30\" to preserve "
                            "bay-window sightline")
    cur_y -= 0.3 * inch

    # Forb drifts
    cur_y = _draw_table_header(c, x, cur_y, w,
                               "FORBS & GRASSES — main bed",
                               ["#", "Common name", "Scientific",
                                "Qty", "Bloom"])
    rows = [
        ("5",  "False Blue Indigo", "Baptisia australis",       "3",  "May-Jun"),
        ("6",  "Wild Bergamot",     "Monarda fistulosa",        "7",  "Jul"),
        ("7",  "Smooth Blue Aster", "Symphyotrichum laeve",     "5",  "Sep-Oct"),
        ("8",  "Wild Lupine",       "Lupinus perennis",         "7",  "May-Jun"),
        ("9",  "Purple Coneflower", "Echinacea purpurea",       "10", "Jul-Sep"),
        ("10", "Butterfly Milkweed", "Asclepias tuberosa",      "5",  "Jun-Aug"),
        ("11", "Little Bluestem",   "Schizachyrium scoparium",  "9",  "Sep+"),
        ("12", "Prairie Smoke",     "Geum triflorum",           "9",  "May"),
        ("13", "Prairie Dropseed",  "Sporobolus heterolepis",   "7",  "Aug"),
    ]
    cur_y = _draw_table_rows(c, x, cur_y, w, rows)


def page_planting_plan_2(c, page_num: int):
    _fill_paper(c)
    _page_chrome(c, page_num, section="Planting Plan")
    x, y, w, h = _content_box(page_num)
    cur_y = y + h - 0.4 * inch
    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 18)
    c.drawString(x, cur_y, "Planting Plan, continued")
    cur_y -= 0.3 * inch

    cur_y = _draw_table_header(c, x, cur_y, w,
                               "VEGETATED SWALE — three moisture bands",
                               ["", "Common name", "Scientific",
                                "Qty", "Band"])
    rows = [
        ("14", "Blue Flag Iris",      "Iris versicolor",       "3",  "wet"),
        ("15", "Tussock Sedge",       "Carex stricta",         "9",  "channel"),
        ("·",  "Fox Sedge",           "Carex vulpinoidea",     "7",  "channel"),
        ("·",  "Soft Rush",           "Juncus effusus",        "5",  "channel"),
        ("·",  "Swamp Milkweed",      "Asclepias incarnata",   "3",  "moist"),
        ("·",  "Cardinal Flower",     "Lobelia cardinalis",    "3",  "moist"),
        ("·",  "Great Blue Lobelia",  "Lobelia siphilitica",   "3",  "moist"),
    ]
    cur_y = _draw_table_rows(c, x, cur_y, w, rows)
    cur_y -= 0.2 * inch

    cur_y = _draw_table_header(c, x, cur_y, w,
                               "SERVICE-AREA GROUNDCOVER — west wall buffer",
                               ["", "Common name", "Scientific",
                                "Qty", "Use"])
    rows = [
        ("·", "Pussytoes",        "Antennaria neglecta",   "7", "stepable"),
        ("·", "Wild Strawberry",  "Fragaria virginiana",   "5", "stepable"),
    ]
    cur_y = _draw_table_rows(c, x, cur_y, w, rows)
    cur_y -= 0.4 * inch

    # Quantities summary
    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 14)
    c.drawString(x, cur_y, "Plant total: ~111 specimens")
    cur_y -= 0.28 * inch
    c.setFillColor(C_MUTED)
    c.setFont(F_SERIF, 11)
    c.drawString(x, cur_y, "Includes 4 woody backbone, 62 forbs & grasses, "
                           "33 swale plugs and 1-gal, 12 service-area "
                           "groundcover.")
    cur_y -= 0.4 * inch

    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 12)
    c.drawString(x, cur_y, "Recommended sources")
    cur_y -= 0.22 * inch
    c.setFillColor(C_INK)
    c.setFont(F_SERIF, 10.5)
    sources = [
        "Prairie Moon Nursery — Winona MN  (mail order plugs & seed)",
        "Outback Nursery — Hastings MN  (1-gal natives, shrubs, trees)",
        "Glacial Ridge Growers — Glenwood MN  (wholesale plugs)",
        "Landscape Alternatives — Shafer MN  (design + supply)",
    ]
    for s in sources:
        c.drawString(x, cur_y, "·  " + s)
        cur_y -= 0.18 * inch


def _draw_table_header(c, x, y, w, title, headers):
    c.setFillColor(C_ACCENT)
    c.setFont(F_SANS_B, 9.5)
    c.drawString(x, y, title)
    y -= 0.18 * inch
    c.setStrokeColor(C_RULE)
    c.setLineWidth(0.6)
    c.line(x, y, x + w, y)
    y -= 0.16 * inch

    col_widths = [0.45 * inch, 1.85 * inch, 2.05 * inch,
                  0.55 * inch, 1.0 * inch]
    cx = x
    c.setFillColor(C_MUTED)
    c.setFont(F_SANS_B, 7.5)
    for i, hd in enumerate(headers):
        c.drawString(cx, y, hd.upper())
        cx += col_widths[i]
    y -= 0.16 * inch
    return y


def _draw_table_rows(c, x, y, w, rows):
    col_widths = [0.45 * inch, 1.85 * inch, 2.05 * inch,
                  0.55 * inch, 1.0 * inch]
    for r, row in enumerate(rows):
        # alternating row tint
        if r % 2 == 0:
            c.setFillColor(C_SECTION_BG)
            c.rect(x - 0.05 * inch, y - 0.08 * inch,
                   w + 0.1 * inch, 0.24 * inch,
                   fill=1, stroke=0)
        cx = x
        c.setFillColor(C_INK)
        for i, cell in enumerate(row):
            font = F_SERIF
            if i == 0:
                font = F_SANS_B
            elif i == 2:
                font = F_SERIF
            size = 10
            if i == 2:
                # italics for sci name (no oblique font registered, use serif)
                size = 9.5
            c.setFont(font, size)
            c.drawString(cx, y, cell)
            cx += col_widths[i]
        y -= 0.24 * inch
    return y - 0.05 * inch


def page_costs(c, page_num: int):
    _fill_paper(c)
    _page_chrome(c, page_num, section="Cost & Install")
    x, y, w, h = _content_box(page_num)
    cur_y = y + h - 0.2 * inch
    cur_y = _draw_section_title(c, x, cur_y, w,
                                "13 — Cost & Install",
                                "What you're spending, on what")

    cur_y -= 0.15 * inch

    rows = [
        ("Removal & site prep",                 "$1,500 - 2,500"),
        ("Hardscape (path, bench pad, bench)",  "$2,000 - 3,500"),
        ("Plants — woody backbone (4)",         "$400 - 700"),
        ("Plants — main bed forbs/grasses (~62)", "$750 - 1,100"),
        ("Plants — swale plugs and 1-gal (~33)", "$300 - 450"),
        ("Plants — service-area groundcover (12)", "$80 - 120"),
        ("Pro install labor",                   "$3,000 - 5,000"),
    ]
    c.setStrokeColor(C_RULE)
    c.setLineWidth(0.5)
    c.line(x, cur_y, x + w, cur_y)
    cur_y -= 0.2 * inch

    for label, cost in rows:
        c.setFillColor(C_INK)
        c.setFont(F_SERIF, 11)
        c.drawString(x, cur_y, label)
        c.setFont(F_SANS_B, 11)
        c.drawRightString(x + w, cur_y, cost)
        cur_y -= 0.24 * inch

    c.setStrokeColor(C_TITLE)
    c.setLineWidth(1.2)
    c.line(x, cur_y, x + w, cur_y)
    cur_y -= 0.28 * inch

    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 13)
    c.drawString(x, cur_y, "Project range")
    c.drawRightString(x + w, cur_y, "$8,030 — $13,370")
    cur_y -= 0.4 * inch

    c.setFillColor(C_MUTED)
    c.setFont(F_SERIF, 10)
    p = ("Get 2-3 quotes. Each installer's overhead and warranty terms "
         "vary widely. Ask: do you have direct experience with oak-savanna "
         "palettes (not just generic 'native')? what's your warranty on "
         "woody plants for year 1? do you handle vegetated bioswales "
         "(not just dry-creeks)? have you done residential foundation "
         "removals with a mini-excavator?")
    cur_y = _draw_paragraph(c, p, x, cur_y, w,
                            font=F_SERIF, size=10, leading=14, color=C_MUTED)
    cur_y -= 0.3 * inch

    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 13)
    c.drawString(x, cur_y, "Recommended installers")
    cur_y -= 0.25 * inch

    installers = [
        ("Prairie Restorations Inc.",
         "Native-restoration specialists, MN since 1977"),
        ("Outback Nursery — Install Services",
         "Hastings; 1-gal native specialty"),
        ("Landscape Alternatives",
         "Shafer; design-build with native focus"),
        ("Metro Blooms",
         "Non-profit; rain garden expertise"),
    ]
    for name, blurb in installers:
        c.setFillColor(C_INK)
        c.setFont(F_SERIF_B, 11)
        c.drawString(x, cur_y, name)
        cur_y -= 0.18 * inch
        c.setFillColor(C_MUTED)
        c.setFont(F_SERIF, 10)
        c.drawString(x + 0.18 * inch, cur_y, blurb)
        cur_y -= 0.25 * inch


def page_maintenance_risk(c, page_num: int):
    _fill_paper(c)
    _page_chrome(c, page_num, section="Maintenance & Risk")
    x, y, w, h = _content_box(page_num)
    cur_y = y + h - 0.2 * inch
    cur_y = _draw_section_title(c, x, cur_y, w,
                                "14 — Maintenance & Risk",
                                "How to keep it alive")

    cur_y -= 0.15 * inch
    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 13)
    c.drawString(x, cur_y, "First-year care")
    cur_y -= 0.22 * inch

    care = [
        ("Watering", "Every 5-7 days for first 6 weeks; every 7-10 days "
                     "through first growing season; only during drought "
                     "after that."),
        ("Erosion blanket", "Biodegradable jute or coir over the swale "
                            "channel for year 1. Sedges break through it."),
        ("No fertilizer", "Native prairie plants are adapted to lean "
                          "soils; fertilizer fuels weeds and makes forbs "
                          "flop."),
        ("Weed pull", "Every 2 weeks first 2 summers. Creeping charlie "
                      "regrowth is the main offender."),
    ]
    for label, text in care:
        c.setFillColor(C_ACCENT)
        c.setFont(F_SANS_B, 9)
        c.drawString(x, cur_y, label.upper())
        cur_y -= 0.16 * inch
        cur_y = _draw_paragraph(c, text, x + 0.15 * inch, cur_y,
                                w - 0.15 * inch,
                                font=F_SERIF, size=10, leading=13.5)
        cur_y -= 0.15 * inch

    cur_y -= 0.15 * inch
    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 13)
    c.drawString(x, cur_y, "Year-by-year evolution")
    cur_y -= 0.22 * inch

    yrs = [
        ("Year 1", "Looks 'planted'. Visible bare soil. Many forbs don't "
                   "bloom heavily — root establishment year."),
        ("Year 2", "Drifts begin to fill in. Most forbs bloom. Sedges close "
                   "the swale channel."),
        ("Year 3", "Established look. Bluestem at full size. Pollinator "
                   "populations have discovered the garden."),
        ("Year 5+", "Self-managing meadow. Some species self-seed where "
                    "they're happy. Edit gently."),
    ]
    for label, text in yrs:
        c.setFillColor(C_ACCENT)
        c.setFont(F_SANS_B, 9)
        c.drawString(x, cur_y, label.upper())
        c.setFillColor(C_INK)
        c.setFont(F_SERIF, 10)
        cur_y = _draw_paragraph(c, "  ·  " + text,
                                x + 0.55 * inch, cur_y, w - 0.55 * inch,
                                font=F_SERIF, size=10, leading=13.5)
        cur_y -= 0.1 * inch

    cur_y -= 0.2 * inch
    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 13)
    c.drawString(x, cur_y, "Risk register")
    cur_y -= 0.22 * inch

    risks = [
        ("Storm scour through swale year 1",
         "erosion blanket; consider French drain"),
        ("Creeping charlie reinfestation",
         "hand-pull pre-removal; spot-treat year 1"),
        ("Lupine establishment failure",
         "MN-provenance plugs from Prairie Moon; or fall seed"),
        ("Serviceberry transplant shock",
         "install in fall; deep-water through year 1"),
        ("Snowplow crushes path edge",
         "stake path through first winter"),
    ]
    for risk, mitigation in risks:
        c.setFillColor(C_INK)
        c.setFont(F_SERIF_B, 10)
        c.drawString(x, cur_y, "·  " + risk)
        cur_y -= 0.16 * inch
        c.setFillColor(C_MUTED)
        c.setFont(F_SERIF, 9.5)
        c.drawString(x + 0.3 * inch, cur_y, mitigation)
        cur_y -= 0.2 * inch


def page_back_cover(c, page_num: int):
    _fill_paper(c)
    # Subtle vignette image at top
    hero = ANNOTATED / "render-vignette.png"
    if hero.exists():
        c.drawImage(str(hero), 0, PAGE_H * 0.45,
                    width=PAGE_W, height=PAGE_H * 0.55,
                    preserveAspectRatio=False, mask="auto")

    # Quote
    c.setFillColor(C_PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H * 0.45, fill=1, stroke=0)

    qx = 0.85 * inch
    qy = PAGE_H * 0.40
    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 18)
    c.drawString(qx, qy,
                 "Restoring a small pocket of pre-1850")
    c.drawString(qx, qy - 0.32 * inch,
                 "Hennepin County to its native hands.")

    qy -= 0.95 * inch
    c.setFillColor(C_INK)
    c.setFont(F_SERIF, 11.5)
    body = ("This package is a living document. The plan is good. The "
            "plants are right for this site. The renderings are honest "
            "about year 1, year 3, year 5. The numbers are real. The "
            "mood board points to where to walk before the install — "
            "the Arboretum's prairie garden, Eloise Butler, Lebanon "
            "Hills.")
    cur_y = _draw_paragraph(c, body, qx, qy, PAGE_W - 2 * qx,
                            font=F_SERIF, size=11.5, leading=16)
    cur_y -= 0.2 * inch
    body = ("Take it with you. Write in the margins. Come back to it "
            "when the Cardinal Flower blooms in August of year 3.")
    cur_y = _draw_paragraph(c, body, qx, cur_y, PAGE_W - 2 * qx,
                            font=F_SERIF, size=11.5, leading=16)

    # Footer
    c.setFillColor(C_MUTED)
    c.setFont(F_SANS, 8)
    c.drawString(qx, 0.6 * inch,
                 "8547 Crane Dance Trail   ·   Eden Prairie MN")
    c.drawString(qx, 0.45 * inch,
                 "Designed by Claude (Anthropic) acting as MN "
                 "native-plants specialist  ·  v1.0")


def page_mood_board(c, page_num: int):
    _fill_paper(c)
    _page_chrome(c, page_num, section="Mood Board")
    x, y, w, h = _content_box(page_num)
    cur_y = y + h - 0.2 * inch
    cur_y = _draw_section_title(c, x, cur_y, w,
                                "12 — Mood Board",
                                "Walk these gardens first")

    cur_y -= 0.2 * inch

    intro = ("Browse these with Rima before signing the install contract. "
             "The point is to absorb the visual vocabulary so you "
             "recognize the look as it grows in.")
    cur_y = _draw_paragraph(c, intro, x, cur_y, w,
                            font=F_SERIF, size=11, leading=15,
                            color=C_MUTED)
    cur_y -= 0.25 * inch

    sections = [
        ("Visit in person — three Twin Cities references",
         [("Minnesota Landscape Arboretum — Prairie Garden",
           "Chaska, 25 min from Eden Prairie. Single best visit."),
          ("Eloise Butler Wildflower Garden",
           "Theodore Wirth Park, Mpls. Mature woodland-edge."),
          ("Lebanon Hills Regional Park — savanna restoration",
           "Eagan. The historic community of your land.")]),
        ("Spring",
         [("Serviceberry in April bloom + Prairie Smoke",
           "search Wikimedia Commons: Amelanchier laevis, Geum triflorum"),
          ("Wild Lupine in May",
           "Lupinus perennis  ·  the iconic blue wave")]),
        ("Summer",
         [("Wild Bergamot + Purple Coneflower at peak",
           "Monarda fistulosa, Echinacea purpurea  ·  bee storm"),
          ("Butterfly Milkweed with Monarchs",
           "Asclepias tuberosa  ·  vivid orange umbel")]),
        ("Fall + Winter",
         [("Smooth Blue Aster + Cardinal Flower",
           "late-season blue and red"),
          ("Little Bluestem — copper season",
           "Schizachyrium scoparium  ·  best winter structure")]),
    ]

    for header, items in sections:
        c.setFillColor(C_ACCENT)
        c.setFont(F_SANS_B, 9.5)
        c.drawString(x, cur_y, header.upper())
        cur_y -= 0.2 * inch
        for title, sub in items:
            c.setFillColor(C_INK)
            c.setFont(F_SERIF_B, 10.5)
            c.drawString(x, cur_y, "·  " + title)
            cur_y -= 0.17 * inch
            c.setFillColor(C_MUTED)
            c.setFont(F_SERIF, 9.5)
            c.drawString(x + 0.25 * inch, cur_y, sub)
            cur_y -= 0.22 * inch
        cur_y -= 0.05 * inch

    cur_y -= 0.05 * inch
    c.setFillColor(C_MUTED)
    c.setFont(F_SANS, 8.5)
    c.drawString(x, cur_y, "Full URL list lives in mood-board.md "
                            "in the design package folder.")


# ============================================================
# Master assembly
# ============================================================

def build():
    c = rl_canvas.Canvas(str(OUT_PDF), pagesize=letter)
    c.setTitle("Front-Yard Oak Savanna Edge — Design Booklet")
    c.setAuthor("Claude (Anthropic) for Arun & Rima Batchu")
    c.setSubject("Minnesota native plant landscape design")

    page = 1
    page_cover(c)
    c.showPage()

    page = 2
    page_title_and_contents(c)
    c.showPage()

    page = 3
    page_section_intro(c, page,
        kicker="01 — Vision",
        title="A small pocket of Big Woods savanna",
        body_paragraphs=[
            "We're replacing the declining mugo pine bed in front of the "
            "south-facing bay window with a Minnesota-native pollinator "
            "garden in the Oak Savanna Edge style — a pocket of the "
            "tallgrass prairie / oak savanna community that grew on this "
            "Hennepin County moraine before settlement.",
            "Anchored at the west end by a Serviceberry whose white April "
            "bloom echoes the entry crabapple's pink, flanked by Ninebark "
            "shrubs pruned low to preserve the indoor sightline through "
            "the bay window, with drifts of native prairie forbs in warm "
            "savanna tones — Wild Bergamot, Purple Coneflower, Butterfly "
            "Milkweed, Wild Lupine, False Blue Indigo, Smooth Blue Aster.",
            "The current river-rock drainage swale becomes a fully-"
            "vegetated bioswale (no rock — Rima's preference) where "
            "native sedges and rushes form a fibrous root mat that "
            "armors the flow path while looking like a meadow.",
            "A meandering limestone path enters from the existing east "
            "concrete walkway and arrives at a partially-shaded bench "
            "pocket in the west third — a quiet retreat tucked under the "
            "Serviceberry, oriented to look back through the bloom "
            "toward the entry crabapple and cul-de-sac borrowed view.",
        ],
        section="Vision")
    c.showPage()

    page = 4
    page_section_intro(c, page,
        kicker="02 — Site facts",
        title="What the property tells us",
        body_paragraphs=[
            "Lot 0.36 acres (~15,700 sq ft). Single-family home built "
            "1997, 5,500 sq ft. Tan stucco with wood-shake roof. "
            "Parcel 1311622340067 in Hennepin County.",
            "South-facing front bed, full sun (>6 hours daily). The "
            "stucco wall radiates heat — effectively raising the bed's "
            "hardiness by half a USDA zone (zone 5a microclimate). "
            "Drought-tolerant prairie species thrive here.",
            "Soil is almost certainly Hayden, Lester, or Kilkenny loam — "
            "the well-drained loamy glacial till of the Hennepin moraine. "
            "Confirm via the USDA Web Soil Survey for this parcel before "
            "the installer breaks ground. No amendment is likely needed.",
            "Pre-settlement vegetation (Marschner map): Big Woods / "
            "prairie-forest border subsection. Bur oak savanna on rolling "
            "moraine ridges, tallgrass prairie on flatter ground, "
            "maple-basswood forest in fire-protected ravines. The Oak "
            "Savanna Edge design is not a stylistic choice — it's the "
            "literal reconstruction of what grew on this land before "
            "1850.",
            "Existing assets to preserve: two mature arborvitae anchor "
            "the east end of the bed; a flowering crabapple frames the "
            "front entry in spring; a boxwood-yew hedge wraps the front "
            "porch foundation; the bay window is the family's primary "
            "indoor view — looking south across the lawn to a borrowed "
            "view of a flowering tree on the cul-de-sac.",
        ],
        section="Site Facts")
    c.showPage()

    page = 5
    page_notes(c, page,
        prompt="Walk the bed before the installer arrives. Note: "
               "exact bed length, downspout location, where snow piles "
               "in winter, where the hose reaches.")
    c.showPage()

    page = 6
    with landscape_orientation(c):
        page_full_image(c, page,
            ANNOTATED / "site-plan.png",
            section="Site Plan", kicker="03 — Site Plan",
            title="Top-down master drawing",
            caption="Scale 1\" = 4 ft. North up. Curved bed expands forward "
                    "into the lawn, deepest at the west third where the "
                    "bench pocket lives. The vegetated swale (steel blue) "
                    "replaces the river-rock channel.")
        c.showPage()

    page = 7
    with landscape_orientation(c):
        page_full_image(c, page,
            ANNOTATED / "sections.png",
            section="Cross-Sections", kicker="04 — Cross-Sections",
            title="Side views, three cuts",
            caption="A: through the west third — Serviceberry over bench, "
                    "tiered prairie forbs out to the lawn edge.  B: through "
                    "the center bed — Ninebarks pruned LOW so the bay-"
                    "window sightline at ~4.5 ft AGL stays open.  C: "
                    "through the vegetated swale — three moisture bands; "
                    "sedges and rushes armor the channel; biodegradable "
                    "blanket year 1.")
        c.showPage()

    page = 8
    with landscape_orientation(c):
        page_full_image(c, page,
            ANNOTATED / "construction-details.png",
            section="Construction Details", kicker="05 — Construction Details",
            title="Path, bench pad, edges",
            caption="Detail 1: stepping-stone bed prep — 4\" Class 5 base, "
                    "2\" screenings.  Detail 2: bench pad on pea gravel.  "
                    "Detail 3: trench-cut edge — soft, naturalistic, "
                    "re-cut each spring.  Detail 4: fieldstone mowing strip "
                    "as a low-maintenance alternative.")
        c.showPage()

    page = 9
    page_notes(c, page,
        prompt="Installer feedback. Capture: do they have savanna-palette "
               "experience? what's their warranty on woody plants? do "
               "they handle vegetated bioswales (not just dry creeks)?")
    c.showPage()

    page = 10
    page_planting_plan(c, page)
    c.showPage()

    page = 11
    page_planting_plan_2(c, page)
    c.showPage()

    page = 12
    # Portrait page + image rotated 90° clockwise: months run top→bottom
    # (Apr at top, Nov at bottom), species along the right edge.
    # Trade-off: reader rotates the booklet 90° CW to read, but each
    # bloom bar is ~9" long instead of ~6.5" — most legible layout.
    page_full_image(c, page,
        ANNOTATED / "bloom-gantt.png",
        section="Bloom Calendar", kicker="07 — Bloom Calendar",
        title="Continuous bloom April → November",
        caption="Rotate the booklet 90° clockwise to read. Months run "
                "top to bottom, species along the right edge. 18 species, "
                "no gap month.",
        rotate_image=270)
    c.showPage()

    page = 13
    page_notes(c, page,
        prompt="Plants to add or substitute. What's blooming in your "
               "favorite garden right now that you want here too? Note "
               "any species you saw at the Arboretum and want included.")
    c.showPage()

    page = 14
    with landscape_orientation(c):
        page_full_image(c, page,
            ANNOTATED / "render-year1.png",
            section="Year 1", kicker="08 — Year 1",
            title="The day after planting",
            caption="Honest expectation-setting. Visible mulch and bare "
                    "soil between plants. Plants installed at 1-quart and "
                    "1-gal container size. Most forbs won't bloom heavily "
                    "this first season — root establishment.")
        c.showPage()

    page = 15
    with landscape_orientation(c):
        page_full_image(c, page,
            ANNOTATED / "render-year3.png",
            section="Year 3", kicker="09 — Year 3",
            title="Established",
            caption="Drifts have filled in. Most forbs bloom on schedule. "
                    "Pollinator populations have discovered the garden. "
                    "Bluestem and Dropseed are at three-quarters mature "
                    "size.")
        c.showPage()

    page = 16
    with landscape_orientation(c):
        page_full_image(c, page,
            ANNOTATED / "render-year5.png",
            section="Year 5", kicker="10 — Year 5",
            title="Matured",
            caption="Late-afternoon August. Cardinal Flower in red bloom. "
                    "Ninebarks at full height; Serviceberry casting dappled "
                    "shade. The look is wild and intentional — clearly "
                    "designed but no longer maintained-looking. "
                    "Self-seeded Black-eyed Susan has filled small gaps.")
        c.showPage()

    page = 17
    with landscape_orientation(c):
        page_full_image(c, page,
            ANNOTATED / "render-year3_spring.png",
            section="Year 3 — Spring", kicker="09b — Year 3, May",
            title="The spring wave",
            caption="Mid-May. Wild Lupine in violet-blue, Prairie Smoke "
                    "groundcover in dusty pink, Baptisia just emerging. "
                    "Serviceberry leafing out. Ninebarks budding. The "
                    "vegetated swale is filling with fresh sedge growth. "
                    "Different mood, same garden, three months earlier.")
        c.showPage()

    page = 18
    with landscape_orientation(c):
        page_full_image(c, page,
            ANNOTATED / "render-year3_with_bench.png",
            section="Bench in Place", kicker="10b — Year 3, the bench",
            title="What the seating pocket feels like",
            caption="Closer view of the west-third bench pocket. Weathered "
                    "cedar bench under the Serviceberry, surrounded on "
                    "three sides by Wild Bergamot and Cardinal Flower. "
                    "Stepping-stone path entering from the right. Late "
                    "afternoon golden side light. This is the room you "
                    "sit in.")
        c.showPage()

    page = 19
    with landscape_orientation(c):
        page_full_image(c, page,
            ANNOTATED / "render-vignette.png",
            section="Bench Vignette", kicker="11 — Bench Vignette",
            title="An afternoon at the seat",
            caption="Weathered cedar bench tucked under the Serviceberry. "
                    "Wild Bergamot left, Purple Coneflower right, "
                    "Butterfly Milkweed in front with a Monarch resting "
                    "on it. Stepping-stone path emerging from the right. "
                    "Dappled afternoon light. This is what we're building "
                    "toward.")
        c.showPage()

    page = 20
    page_notes(c, page,
        prompt="Bench placement. After standing at the proposed spot, "
               "where exactly do you want the bench? Note sun angles at "
               "morning, noon, late afternoon. Where does Bree the Bee "
               "(or her honeybee cousins) work?")
    c.showPage()

    page = 21
    page_mood_board(c, page)
    c.showPage()

    page = 22
    page_costs(c, page)
    c.showPage()

    page = 23
    page_maintenance_risk(c, page)
    c.showPage()

    # Multiple notes pages at end for sketches and meeting notes
    for i in range(4):
        page = 24 + i
        prompts = [
            "Quotes received. Installer / date / range / what they noted.",
            "Site walk-through. Things you noticed standing in the bed.",
            "Sketches. Borrow a corner of the page to draw your own ideas.",
            "After install — first-month observations. What thrived. "
            "What looked rough. What surprised you.",
        ]
        page_notes(c, page, prompt=prompts[i])
        c.showPage()

    page = 28
    page_back_cover(c, page)
    c.showPage()

    c.save()
    print(f"booklet (body): {OUT_PDF}")

    _splice_in_plant_profiles()
    _make_installer_variant()

    return OUT_PDF


def _make_installer_variant() -> None:
    """Produce booklet-installer.pdf: the same booklet with the
    Cost & Install page removed (so it's safe to share with potential
    installers without revealing budget or competing-firm names)."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("  (pypdf not installed — skipping installer variant)")
        return

    src = PdfReader(str(OUT_PDF))
    out_path = ROOT / "booklet-installer.pdf"

    # Identify the cost page by scanning for the unique kicker text
    # we drew on it ("13 — Cost & Install").
    cost_page_idx = None
    for i, page in enumerate(src.pages):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if "13 — Cost & Install" in text or "What you're spending" in text:
            cost_page_idx = i
            break

    if cost_page_idx is None:
        print("  (could not locate Cost & Install page; "
              "installer variant will be identical to full booklet)")
        cost_page_idx = -1  # skip removal but still emit

    writer = PdfWriter()
    for i, page in enumerate(src.pages):
        if i == cost_page_idx:
            continue
        writer.add_page(page)

    # Update document metadata so the installer version has its own title
    writer.add_metadata({
        "/Title": "Front-Yard Oak Savanna Edge — Installer Edition",
        "/Author": "Claude (Anthropic) for Arun & Rima Batchu",
        "/Subject": "Minnesota native plant landscape design (installer brief)",
    })

    with open(out_path, "wb") as f:
        writer.write(f)
    n = len(writer.pages)
    print(f"booklet-installer.pdf: {out_path}  ({n} pages, "
          f"Cost page removed)")


def _draw_profiles_divider(canvas_path: Path) -> None:
    """Single-page section divider for the Plant Profiles section."""
    c = rl_canvas.Canvas(str(canvas_path), pagesize=letter)
    _fill_paper(c)

    # Centered title block
    c.setFillColor(C_ACCENT)
    c.setFont(F_SANS_B, 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H * 0.62, "15 — PLANT PROFILES")

    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 36)
    c.drawCentredString(PAGE_W / 2, PAGE_H * 0.55,
                        "The Sixteen Plants")

    c.setFillColor(C_INK)
    c.setFont(F_SERIF, 13)
    c.drawCentredString(PAGE_W / 2, PAGE_H * 0.50,
                        "Botanical plates with qualities, care, "
                        "history, and reason to be")

    # Decorative rule
    c.setStrokeColor(C_RULE)
    c.setLineWidth(1.0)
    c.line(PAGE_W * 0.35, PAGE_H * 0.46,
           PAGE_W * 0.65, PAGE_H * 0.46)

    # Body
    pad = 1.4 * inch
    body = ("The pages that follow profile every species in the "
            "design, from the Serviceberry that anchors the west "
            "end to the Tussock Sedge that armors the swale "
            "channel. Each plate is a hand-painted-style botanical "
            "illustration in the spirit of Curtis's Botanical "
            "Magazine, generated specifically for this project. "
            "Each profile carries four short sections: what the "
            "plant looks like, how to care for it, where it comes "
            "from, and the ecological reason it earns its place "
            "in your garden.")
    f_body = ImageFont = None  # noqa
    c.setFillColor(C_INK)
    c.setFont(F_SERIF, 11.5)
    # naive wrap
    words = body.split()
    cur, lines = "", []
    max_w = PAGE_W - 2 * pad
    for w in words:
        trial = (cur + " " + w).strip()
        if c.stringWidth(trial, F_SERIF, 11.5) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    cy = PAGE_H * 0.40
    for line in lines:
        c.drawCentredString(PAGE_W / 2, cy, line)
        cy -= 0.22 * inch

    # Mascot moment
    c.setFillColor(C_MUTED)
    c.setFont(F_SERIF_B, 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H * 0.18,
                        "— Bree the Bee approves —")

    c.showPage()
    c.save()


def _splice_in_plant_profiles() -> None:
    """Reopen booklet.pdf, insert a divider + plant-profiles.pdf
    BEFORE the back cover (which is the last page)."""
    profiles_pdf = ROOT / "plant-profiles.pdf"
    if not profiles_pdf.exists():
        print("  (no plant-profiles.pdf — skipping splice)")
        return

    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("  (pypdf not installed — skipping splice)")
        return

    # Build the divider as its own one-page PDF
    divider_pdf = ROOT / ".divider-tmp.pdf"
    _draw_profiles_divider(divider_pdf)

    body = PdfReader(str(OUT_PDF))
    profiles = PdfReader(str(profiles_pdf))
    divider = PdfReader(str(divider_pdf))

    writer = PdfWriter()
    # body pages 0..N-2 (everything except back cover at N-1)
    body_pages = list(body.pages)
    back_cover = body_pages[-1]
    for p in body_pages[:-1]:
        writer.add_page(p)
    # divider
    for p in divider.pages:
        writer.add_page(p)
    # all profile pages
    for p in profiles.pages:
        writer.add_page(p)
    # back cover last
    writer.add_page(back_cover)

    with open(OUT_PDF, "wb") as f:
        writer.write(f)
    divider_pdf.unlink(missing_ok=True)

    n = len(writer.pages)
    print(f"booklet (with profiles): {OUT_PDF}  ({n} pages)")


if __name__ == "__main__":
    build()
