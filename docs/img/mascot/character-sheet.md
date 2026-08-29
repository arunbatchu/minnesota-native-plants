# Bree — Character Sheet

The canonical description of this book's learning mascot. Anything that
generates new Bree art or writes Bree dialogue starts here.

## Identity

| Field | Value |
|---|---|
| Name | Bree |
| Species | Rusty-patched Bumble Bee (*Bombus affinis*) — Minnesota's state bee |
| Caste | Worker (female — only workers and males carry the rusty patch) |
| Build | Round and thoroughly fuzzy; a soft ball of a bee, not a slim one |
| Head | Black, with large warm brown eyes |
| Thorax | Yellow, with a single black spot between the wings |
| Abdomen | Yellow at the front with a **rust-orange patch** on the second segment; black toward the tip |
| Wings | Translucent, faintly iridescent |
| Accessories | Tiny green leaf beret; carries one small wildflower |
| Art style | Soft watercolor, warm tones, clean edges |
| Background | Fully transparent RGBA — no scene, no ground shadow, no text |

## Why This Mascot

Bree used to be a honeybee. That was wrong for this book, and wrong in a way
the book itself points out: Chapter 6 says plainly that honeybees are not
native to North America. A textbook about native plants cannot be guided by an
introduced species.

The rusty-patched bumble bee fixes that, and does more than fix it:

- It is **Minnesota's official state bee**, designated in 2019.
- It was **listed as federally endangered in 2017** — the first bumble bee in
  the continental United States to be listed.
- It still hangs on in the Twin Cities, in exactly the prairies and gardens
  this book teaches people to plant.
- It is short-tongued, so it feeds at shallow flowers, and it needs blooms
  from the day the queen emerges in spring until the new queens fatten up in
  fall. That is the bloom-succession lesson in Chapters 6 and 10, walking
  around on six legs.

So Bree is not decoration. She is the reader's stake in the material. Plant
what this book teaches and Bree gets to stay.

## Personality

Warm, patient, encouraging, calm. She treats readers as curious adults and is
never condescending. She addresses them as "fellow nature lovers" or "garden
friends," and reaches for the occasional gentle nature pun.

She is **not** anxious about her own endangered status and never guilt-trips
the reader. She mentions it the way you'd mention where you're from.

## Catchphrases

Alternate between these so no one gets stale:

> "Let's explore the prairie!"
> "Every plant has a story!"
> "Let's grow together!"

## Voice

Short sentences. Plain words. First person. One to three sentences per
appearance — the Chapter 1 self-introduction is the one allowed exception.

Good:

> "This is the chapter where the names finally start sticking. Take it slowly."

> "Every flower on this page is one I can actually feed at. Short tongue —
> I need the shallow ones."

Bad:

- "Hi friends! Let's dive into the wonderful world of pollination!" — too
  bouncy, and *dive into* is banned
- "You can do anything if you believe!" — empty cheerleading
- "Studies show that 40% of native bees..." — she doesn't cite research; the
  chapter does that

## Pose Set

| Pose | File | Use |
|---|---|---|
| Neutral | `neutral.png` | General notes, sidebars, favicon source |
| Welcome | `welcome.png` | Chapter openings — one per chapter |
| Thinking | `thinking.png` | Key concepts, 2–3 per chapter |
| Tip | `tip.png` | Concrete, actionable hints |
| Warning | `warning.png` | Common mistakes, invasive-species alerts |
| Encouraging | `encouraging.png` | Difficult content |
| Celebration | `celebration.png` | Section or chapter close — one per chapter |

Derived assets: `logo.png` (header, trimmed and downscaled from `neutral.png`)
and `../favicon.ico` (generated from `neutral.png`).

## Placement

Canonical rules live in the book-installer skill's
`references/mascot-placement-rules.md`. In short: at most 9 per chapter, one
welcome and one celebration each, never two back-to-back, and the image goes
in the admonition body, never the title bar.

## Regenerating Art

Prompts are in `image-prompts.md` in this directory (excluded from the built
site). Keep the black thoracic spot, the rust patch on abdominal segment two,
the leaf beret, and the watercolor style identical across every pose — a
mascot that drifts between images stops reading as one character.

After generating, always run the trim script so the PNGs are tight:

```bash
python3 $BK_HOME/skills/book-installer/scripts/trim-padding-from-image.py docs/img/mascot/neutral.png
```
