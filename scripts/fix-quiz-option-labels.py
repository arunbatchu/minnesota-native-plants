#!/usr/bin/env python3
"""Make quiz option labels A/B/C/D in the markup, not just in CSS.

Every quiz answer says "The correct answer is **C**", but the options were
written as a markdown ordered list wrapped in <div class="upper-alpha">, so the
letters existed only in a stylesheet rule. Wherever that CSS does not load —
GitHub's markdown view, an editor preview, a print, a plain-text render — the
reader sees "1. 2. 3. 4." and an answer that says C.

This rewrites each block to an explicit list that carries its own labels:

    <div class="upper-alpha" markdown>        <ol type="A" class="upper-alpha">
    1. text                             ->    <li>text</li>
    </div>                                    </ol>

`type="A"` is honored by browsers with no stylesheet at all, and screen readers
announce the letters. The class stays so the existing CSS rule still applies on
the site, where author CSS outranks the presentational attribute.

Usage:
    python3 scripts/fix-quiz-option-labels.py
    python3 scripts/fix-quiz-option-labels.py --check
"""
import re
import sys
from pathlib import Path

CHAPTERS = Path("docs/chapters")
BLOCK = re.compile(
    r'<div class="upper-alpha" markdown>\n(.*?)\n</div>', re.S)
ITEM = re.compile(r"^\s*\d+\.\s+(.*)$")


def md_to_html(s):
    """The six option lines that carry inline markdown need it as HTML now."""
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def convert(text):
    def repl(m):
        items = []
        for line in m.group(1).splitlines():
            it = ITEM.match(line)
            if not it:
                return m.group(0)          # unexpected shape: leave untouched
            items.append(md_to_html(it.group(1).strip()))
        body = "\n".join(f"<li>{i}</li>" for i in items)
        return f'<ol type="A" class="upper-alpha">\n{body}\n</ol>'
    return BLOCK.sub(repl, text)


def main(argv):
    check = "--check" in argv
    files = sorted(list(CHAPTERS.glob("*/quiz.md"))
                   + list(CHAPTERS.glob("*/quiz-applied.md")))
    changed = blocks = skipped = 0

    for p in files:
        t = p.read_text()
        before = len(BLOCK.findall(t))
        if not before:
            continue
        new = convert(t)
        after = len(BLOCK.findall(new))
        skipped += after
        if new != t:
            if not check:
                p.write_text(new)
            changed += 1
            blocks += before - after

    verb = "would convert" if check else "converted"
    print(f"{verb} {blocks} option blocks across {changed} files")
    if skipped:
        print(f"WARNING: {skipped} block(s) left unconverted — unexpected shape",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
