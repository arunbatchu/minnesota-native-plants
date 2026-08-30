#!/usr/bin/env python3
"""Check that quiz options and answer letters agree.

Every answer explanation says "The correct answer is **C**". That only means
anything if the options are actually labelled A/B/C/D, and for a long time the
letters existed only in a CSS rule — so anywhere the stylesheet did not load,
readers saw "1. 2. 3. 4." next to an answer that said C.

This enforces the invariant so it cannot come back:

  1. Every option block is <ol type="A">, not a markdown list relying on CSS
  2. Every question has an answer block
  3. Every stated answer letter is within range of the options offered
  4. Every answer carries a **See:** backlink to its chapter

Usage:
    python3 scripts/validate-quizzes.py
Exits non-zero if anything fails.
"""
import re
import sys
from pathlib import Path

CHAPTERS = Path("docs/chapters")
QUESTION = re.compile(r"^#### (\d+)\.", re.M)
OPTIONS_OK = re.compile(r'<ol type="A"[^>]*>(.*?)</ol>', re.S)
OPTIONS_OLD = re.compile(r'<div class="upper-alpha"[^>]*>', re.S)
ANSWER = re.compile(r"The correct answer is \*\*([A-Z])\*\*")
SEE = re.compile(r"\*\*See:\*\* \[Chapter \d+\]")
LETTERS = "ABCDEFGH"


def main():
    failures = []
    files = sorted(list(CHAPTERS.glob("*/quiz.md"))
                   + list(CHAPTERS.glob("*/quiz-applied.md")))
    n_q = 0

    for p in files:
        text = p.read_text()
        rel = p.relative_to(Path("docs"))

        for m in OPTIONS_OLD.finditer(text):
            line = text[:m.start()].count("\n") + 1
            failures.append(
                f"{rel}:{line}  option block still uses "
                f'<div class="upper-alpha"> — the letters would come from CSS '
                f"only. Run scripts/fix-quiz-option-labels.py")

        # split into per-question chunks so answers pair with their options
        chunks = re.split(r"(?=^#### \d+\.)", text, flags=re.M)[1:]
        for chunk in chunks:
            n_q += 1
            qnum = QUESTION.search(chunk).group(1)
            where = f"{rel} Q{qnum}"

            opts = OPTIONS_OK.search(chunk)
            if not opts:
                failures.append(f"{where}  no <ol type=\"A\"> options block")
                continue
            n_opts = len(re.findall(r"<li>", opts.group(1)))
            if n_opts < 2:
                failures.append(f"{where}  only {n_opts} option(s)")

            ans = ANSWER.search(chunk)
            if not ans:
                failures.append(f"{where}  no 'The correct answer is **X**'")
                continue
            letter = ans.group(1)
            if letter not in LETTERS[:n_opts]:
                failures.append(
                    f"{where}  answer is {letter} but only {n_opts} options "
                    f"({LETTERS[:n_opts]}) are offered")

            if not SEE.search(chunk):
                failures.append(f"{where}  no **See:** chapter backlink")

    print(f"checked {n_q} questions across {len(files)} quiz files")
    if failures:
        print(f"\n{len(failures)} problem(s):", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("all quizzes valid: options are A/B/C/D in the markup, "
          "answer letters in range, backlinks present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
