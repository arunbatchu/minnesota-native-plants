#!/usr/bin/env python3
"""Fill the Quick Facts table on every species card in docs/plants/.

Three data sources, each owning what it is actually good at:

  .plant-gallery/taxonomy.json  family and kingdom, resolved from GBIF.
                                Machine-fetched, never hand-edited.
  .plant-gallery/traits.json    height, bloom, sun, moisture, soil, wildlife.
                                Hand-authored for Minnesota conditions, because
                                the national datasets are wrong at this scale --
                                USDA PLANTS reports Wild Bergamot's flower color
                                as red and its moisture use as high, and it is
                                a lavender dry-prairie plant.
  docs/plants/*.md              the cards themselves; only the Quick Facts block
                                is rewritten, everything else is left alone.

The four animals in the gallery (a butterfly, two bees, a beetle) get a
different field set, because bloom time and soil texture mean nothing for a
beetle.

Usage:
    python3 scripts/fill-quick-facts.py            # write
    python3 scripts/fill-quick-facts.py --check    # report only, no writes
"""
import json
import re
import sys
from pathlib import Path

PLANTS = Path("docs/plants")
TAX = Path(".plant-gallery/taxonomy.json")
TRAITS = Path(".plant-gallery/traits.json")
SPECIES = Path(".plant-gallery/species.json")

PLANT_ROWS = ["Scientific name", "Family", "Height", "Bloom time",
              "Sun", "Moisture", "Soil", "Wildlife value"]
ANIMAL_ROWS = ["Scientific name", "Family", "Type", "Status",
               "Active season", "What it needs", "Where in Minnesota"]

# Matches the "## Quick Facts" heading through the end of its table.
BLOCK_RE = re.compile(
    r"^## Quick Facts\n+(?:\|.*\n)+", re.M)


def build_table(rows):
    out = ["## Quick Facts", "", "| | |", "|---|---|"]
    out += [f"| **{k}** | {v} |" for k, v in rows]
    return "\n".join(out) + "\n"


def main(argv):
    check = "--check" in argv
    tax = json.loads(TAX.read_text())
    traits = json.loads(TRAITS.read_text())
    species = json.loads(SPECIES.read_text())
    animals = traits.get("_animals", {})

    by_slug = {v["slug"]: v for v in species.values()}
    sci_by_slug = {s: v["scientific_name"] for s, v in by_slug.items()}

    filled = skipped = missing_trait = no_block = 0
    gaps = []

    for card in sorted(PLANTS.glob("*.md")):
        slug = card.stem
        if slug == "index":
            continue
        text = card.read_text()
        m = BLOCK_RE.search(text)
        if not m:
            no_block += 1
            gaps.append(f"{slug}: no Quick Facts block")
            continue

        sci = sci_by_slug.get(slug)
        # scientific name also appears as the card's italic subtitle
        if not sci:
            sub = re.search(r"^\*([^*]+)\*$", text, re.M)
            sci = sub.group(1).strip() if sub else None

        t = tax.get(sci) or {}
        family = t.get("family") or "—"

        if slug in animals:
            a = animals[slug]
            rows = [
                ("Scientific name", f"*{sci}*" if sci else "—"),
                ("Family", family),
                ("Type", a["type"]),
                ("Status", a["status"]),
                ("Active season", a["season"]),
                ("What it needs", a["needs"]),
                ("Where in Minnesota", a["where"]),
            ]
        else:
            tr = traits.get(slug)
            if not tr:
                missing_trait += 1
                gaps.append(f"{slug}: no traits entry")
                # still fill family, which we do have
                tr = {}
            rows = [
                ("Scientific name", f"*{sci}*" if sci else "—"),
                ("Family", family),
                ("Height", tr.get("height", "—")),
                ("Bloom time", tr.get("bloom", "—")),
                ("Sun", tr.get("sun", "—")),
                ("Moisture", tr.get("moisture", "—")),
                ("Soil", tr.get("soil", "—")),
                ("Wildlife value", tr.get("wildlife", "—")),
            ]

        new = build_table(rows)
        if m.group(0).rstrip("\n") == new.rstrip("\n"):
            skipped += 1
            continue
        if not check:
            card.write_text(text[:m.start()] + new + text[m.end():])
        filled += 1

    total = len([p for p in PLANTS.glob("*.md") if p.stem != "index"])
    verb = "would fill" if check else "filled"
    print(f"{total} cards: {verb} {filled}, unchanged {skipped}")
    if gaps:
        print(f"\n{len(gaps)} gap(s):")
        for g in gaps:
            print(f"  {g}")
    return 1 if (missing_trait or no_block) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
