#!/usr/bin/env python3
"""Resolve family and kingdom for every gallery species via the GBIF API.

GBIF's species/match endpoint is free, needs no key, and is authoritative for
taxonomy — which is exactly the part of the Quick Facts table that should never
be hand-authored. It also tells us kingdom, which is how we catch the animals
that ended up in a plant gallery.

Writes .plant-gallery/taxonomy.json:
    {"<scientific name>": {"family": ..., "genus": ..., "kingdom": ...,
                           "order": ..., "match": ..., "confidence": ...}}

Usage:
    python3 scripts/fetch-taxonomy.py
    python3 scripts/fetch-taxonomy.py --force   # re-resolve everything
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

SPECIES = Path(".plant-gallery/species.json")
OUT = Path(".plant-gallery/taxonomy.json")
API = "https://api.gbif.org/v1/species/match"


def match(name):
    url = f"{API}?name={urllib.parse.quote(name)}"
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)


def main(argv):
    force = "--force" in argv
    species = json.loads(SPECIES.read_text())
    cache = {} if force else (json.loads(OUT.read_text()) if OUT.exists() else {})

    names = sorted({v["scientific_name"] for v in species.values()})
    todo = [n for n in names if n not in cache]
    print(f"{len(names)} names, {len(todo)} to resolve")

    for i, name in enumerate(todo, 1):
        try:
            d = match(name)
            cache[name] = {
                "family": d.get("family"),
                "genus": d.get("genus"),
                "order": d.get("order"),
                "kingdom": d.get("kingdom"),
                "class": d.get("class"),
                "match": d.get("matchType"),
                "confidence": d.get("confidence"),
                "accepted": d.get("scientificName"),
            }
            flag = "" if d.get("matchType") == "EXACT" else f"  [{d.get('matchType')}]"
            print(f"  {i:>3}/{len(todo)}  {name:38} -> "
                  f"{d.get('family') or '?':18} {d.get('kingdom') or '?'}{flag}")
        except Exception as e:                       # noqa: BLE001
            print(f"  {i:>3}/{len(todo)}  {name:38} -> FAILED {e}", file=sys.stderr)
            cache[name] = {"family": None, "kingdom": None, "match": "ERROR"}
        time.sleep(0.05)

    OUT.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")

    # Report what needs a human look
    animals = [n for n, v in cache.items() if v.get("kingdom") == "Animalia"]
    fuzzy = [n for n, v in cache.items() if v.get("match") not in ("EXACT", None)]
    missing = [n for n, v in cache.items() if not v.get("family")]

    print(f"\nwrote {OUT}  ({len(cache)} names)")
    if animals:
        print(f"\nNOT PLANTS ({len(animals)}):")
        for n in sorted(animals):
            print(f"  {n}  ({cache[n].get('class')})")
    if fuzzy:
        print(f"\nNON-EXACT MATCHES ({len(fuzzy)}):")
        for n in sorted(fuzzy):
            print(f"  {n:38} {cache[n]['match']:10} -> {cache[n].get('accepted')}")
    if missing:
        print(f"\nNO FAMILY ({len(missing)}): {', '.join(sorted(missing))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
