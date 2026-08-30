#!/usr/bin/env python3
"""Regenerate docs/learning-graph/book-metrics.md from the book itself.

Every number here is counted from the source, so the report cannot drift from
reality the way a hand-maintained one does. Run it after any pass that adds
chapters, quizzes, sims, species cards or glossary terms.

Usage:
    python3 scripts/book-metrics.py
    python3 scripts/book-metrics.py --check   # fail if the file is stale
"""
import csv
import json
import re
import sys
from pathlib import Path

DOCS = Path("docs")
OUT = DOCS / "learning-graph" / "book-metrics.md"


def words(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)      # code blocks
    text = re.sub(r"https?://\S+", "", text)               # bare URLs
    return len(text.split())


def main(argv):
    check = "--check" in argv

    chapters = sorted(d for d in (DOCS / "chapters").iterdir() if d.is_dir())
    sims = sorted(d for d in (DOCS / "sims").iterdir()
                  if d.is_dir() and (d / "index.md").exists())
    cards = [p for p in (DOCS / "plants").glob("*.md") if p.stem != "index"]
    # Exclude this script's own output. It is generated, not book content,
    # and counting it created a feedback loop: the Equations note names the
    # arithmatex delimiters, so each run found them in the previous run's
    # file and reported the book had math in it.
    md = [p for p in DOCS.rglob("*.md") if p != OUT]

    with open(DOCS / "learning-graph" / "learning-graph.csv") as f:
        concepts = sum(1 for _ in csv.reader(f)) - 1

    glossary = DOCS / "glossary.md"
    faq = DOCS / "faq.md"
    n_gloss = len(re.findall(r"^#### ", glossary.read_text(), re.M))
    n_faq = len(re.findall(r"^### ", faq.read_text(), re.M))

    quiz_q = quiz_applied_q = 0
    for c in chapters:
        for name, add in (("quiz.md", "core"), ("quiz-applied.md", "applied")):
            p = c / name
            if not p.exists():
                continue
            n = len(re.findall(r"^#### \d+\.", p.read_text(), re.M))
            if add == "core":
                quiz_q += n
            else:
                quiz_applied_q += n

    all_text = "\n".join(p.read_text() for p in md)
    diagrams = len(re.findall(r"^#### Diagram:", all_text, re.M))
    mermaid = len(re.findall(r"```mermaid", all_text))
    # Count only real arithmatex delimiters: \( ... \), \[ ... \], $$ ... $$.
    # A bare $...$ regex counted this book's install-cost ranges
    # ("$800 – $1,800") as seven equations, which is why the report used to
    # claim the book had math in it.
    equations = len(re.findall(r"\\\(|\\\[|\$\$", all_text))
    links = len(re.findall(r"\[[^\]]+\]\([^)]+\)", all_text))
    total_words = sum(words(p.read_text()) for p in md)

    shots = len(list((DOCS / "sims").glob("*/*.png")))
    illus = len(list((DOCS / "plants" / "img").glob("*-illustration.png")))
    with_photo = sum(1 for p in cards
                     if re.search(rf"{p.stem}-\d+\.jpg", p.read_text()))
    with_facts = sum(1 for p in cards
                     if re.search(r"\| \*\*(?:Height|Type)\*\* \| (?!—)", p.read_text()))
    host = len(re.findall(r"host plant|larval host", all_text, re.I))

    pages = round(total_words / 250 + (diagrams + mermaid) * 0.25 + len(sims) * 0.5)

    def pct(n):
        return f"{n} ({round(100 * n / len(cards))}%)"

    rows = [
        ("Chapters", len(chapters), "[MicroSims](../sims/index.md)", "Chapter directories"),
        ("Concepts", concepts, "[Concept List](./concept-list.md)", "Rows in learning-graph.csv"),
        ("Glossary Terms", n_gloss, "[Glossary](../glossary.md)", "H4 headers in glossary.md"),
        ("FAQs", n_faq, "[FAQ](../faq.md)", "H3 headers in faq.md"),
        ("Quiz Questions (recall)", quiz_q, "—", "Numbered H4s in quiz.md"),
        ("Quiz Questions (applied)", quiz_applied_q, "—", "Numbered H4s in quiz-applied.md"),
        ("Quiz Questions (total)", quiz_q + quiz_applied_q, "—", "Both quizzes, all chapters"),
        ("Diagrams", diagrams + mermaid, "—", "'#### Diagram:' headers plus mermaid blocks"),
        ("Equations", equations, "—", "arithmatex math delimiters"),
        ("MicroSims", len(sims), "[Simulations](../sims/index.md)", "Directories in docs/sims/"),
        ("MicroSim Screenshots", f"{shots} ({round(100*shots/len(sims))}%)", "[Catalog](../sims/index.md)", "PNGs for the visual catalog"),
        ("Total Words", f"{total_words:,}", "—", "Words in all markdown, excluding code and URLs"),
        ("Links", f"{links:,}", "—", "Markdown-formatted links"),
        ("Equivalent Pages", f"{pages:,}", "—", "250 words/page + 0.25/diagram + 0.5/MicroSim"),
        ("Species Cards", len(cards), "[Plants](../plants/index.md)", "Per-species reference pages"),
        ("Cards w/ Quick Facts", pct(with_facts), "—", "Trait data populated, not just dashes"),
        ("Cards w/ Photos", pct(with_photo), "—", "At least one Wikimedia photo"),
        ("Cards w/ Illustration", pct(illus), "—", "Curtis-style botanical plate available"),
        ("Host-plant Mentions", host, "—", "'host plant' or 'larval host' across the book"),
    ]

    body = [
        "# Book Metrics", "",
        "Counted from the source by `scripts/book-metrics.py`. Re-run that script",
        "after any pass that changes chapters, quizzes, sims, cards or the glossary —",
        "do not edit the numbers by hand.", "",
        "| Metric Name | Value | Link | Notes |",
        "|-------------|-------|------|-------|",
    ]
    body += [f"| {n} | {v} | {l} | {note} |" for n, v, l, note in rows]
    text = "\n".join(body) + "\n"

    if check:
        current = OUT.read_text() if OUT.exists() else ""
        if current != text:
            print("book-metrics.md is STALE — run scripts/book-metrics.py")
            return 1
        print("book-metrics.md is current")
        return 0

    OUT.write_text(text)
    print(f"wrote {OUT}")
    for n, v, _, _ in rows:
        print(f"  {n:28} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
