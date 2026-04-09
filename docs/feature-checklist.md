# Feature Checklist

This page shows the implementation status of features in this intelligent textbook.

**Book:** Minnesota Native Plants
**Scan Date:** 2026-04-09

## Content Statistics

| Metric | Count |
|--------|-------|
| Chapters | 17 |
| Concepts in Learning Graph | 289 |
| Interactive MicroSims | 22 |
| Mermaid Diagrams | 34 |
| Glossary Terms | 288 |
| FAQ Questions | 70 |
| Quiz Questions | 170 (10 per chapter) |

## Basic Features

| Feature | Status | Notes |
|---------|--------|-------|
| Navigation sidebar | :white_check_mark: | Left-side menu with all chapters |
| Search functionality | :white_check_mark: | MkDocs search plugin |
| Table of contents | :white_check_mark: | Per-page TOC with `toc.follow` |
| Site title | :white_check_mark: | "Minnesota Native Plants" |
| Site author | :white_check_mark: | Arun Batchu |
| GitHub repository | :white_check_mark: | arunbatchu/minnesota-native-plants |
| Custom logo | :white_check_mark: | Bree mascot neutral pose |
| Custom favicon | :white_check_mark: | Generated from mascot (6 sizes) |
| Color theme | :white_check_mark: | Green primary, white accent |
| Footer navigation | :white_check_mark: | `navigation.footer` enabled |
| Navigation expand | :white_check_mark: | `navigation.expand` enabled |
| Back to top | :white_check_mark: | `navigation.top` enabled |
| Breadcrumbs | :white_check_mark: | `navigation.path` enabled |
| Section index | :white_check_mark: | `navigation.indexes` enabled |
| License page | :white_check_mark: | CC BY-NC-SA 4.0 |
| Contact page | :white_check_mark: | Links to GitHub |
| Copyright footer | :white_check_mark: | With license link |

## Content Enhancement Features

| Feature | Status | Notes |
|---------|--------|-------|
| Admonitions | :white_check_mark: | Standard + 7 custom mascot types |
| Code copy button | :white_check_mark: | `content.code.copy` enabled |
| Syntax highlighting | :white_check_mark: | `pymdownx.highlight` with line numbers |
| Collapsible details | :white_check_mark: | `pymdownx.details` enabled |
| Mermaid diagrams | :white_check_mark: | 34 diagrams via `pymdownx.superfences` |
| MathJax | :white_check_mark: | `pymdownx.arithmatex` + MathJax CDN |
| Footnotes | :white_check_mark: | `footnotes` extension |
| MD in HTML | :white_check_mark: | Required for mascot admonitions |
| GLightbox | :x: | Image zoom on click — not installed |
| KaTeX | :x: | Using MathJax instead |
| Tabbed content | :x: | Not needed currently |
| Task lists | :x: | Not needed currently |
| Emoji | :x: | Not needed per style guide |

## Site-Wide Resources

| Feature | Status | Notes |
|---------|--------|-------|
| Glossary | :white_check_mark: | 288 terms with ISO 11179 definitions |
| FAQ | :white_check_mark: | 70 questions across 6 categories |
| Custom CSS | :white_check_mark: | extra.css + mascot.css |
| Custom JavaScript | :white_check_mark: | extra.js (iframe resize, copy buttons) |
| Google Analytics | :x: | Not configured — add property ID to enable |

## Interactive Learning Features

| Feature | Status | Notes |
|---------|--------|-------|
| MicroSims | :white_check_mark: | 22 p5.js interactive simulations |
| Per-chapter quizzes | :white_check_mark: | 17 quizzes, 10 questions each |
| Pedagogical agent (mascot) | :white_check_mark: | Bree the Bee — 7 watercolor poses |
| Celebration animations | :x: | Plant ID quizzes with confetti — planned |
| Interactive infographic overlays | :x: | Hover/quiz infographics — planned |

## Learning Graph Features

| Feature | Status | Notes |
|---------|--------|-------|
| Course description | :white_check_mark: | 100/100 quality score, Bloom's Taxonomy |
| Learning graph CSV | :white_check_mark: | 289 concepts, 446 edges |
| Learning graph JSON | :white_check_mark: | vis-network format with metadata |
| Graph viewer | :white_check_mark: | Interactive vis.js visualization |
| Concept taxonomy | :white_check_mark: | 15 categories |
| Concept list | :white_check_mark: | 289 concepts enumerated |
| Quality metrics | :white_check_mark: | DAG validation, indegree analysis |
| Taxonomy distribution | :white_check_mark: | All categories under 30% |
| Book metrics report | :x: | Run book-metrics-generator skill |
| Chapter metrics report | :x: | Run book-metrics-generator skill |

## Publishing Features

| Feature | Status | Notes |
|---------|--------|-------|
| GitHub Pages deployment | :white_check_mark: | Live at arunbatchu.github.io |
| Social media cards | :x: | Needs `pip install "mkdocs-material[imaging]"` |
| Edit page button | :white_check_mark: | `content.action.edit` enabled |

## Content Generation

| Feature | Status | Notes |
|---------|--------|-------|
| Chapters | :white_check_mark: | 17 chapters covering all 289 concepts |
| Mascot images | :white_check_mark: | 7 poses, transparent backgrounds |
| Mascot CSS admonitions | :white_check_mark: | 7 custom admonition types |
| CLAUDE.md style guide | :white_check_mark: | Character guidelines + project conventions |
| About page | :x: | Not yet created |
| References per chapter | :x: | Run reference-generator skill |
| Instructor's guide | :x: | Run book-installer instructor guide |
| Custom 404 page | :x: | Run book-installer custom-404 |

## Summary

- **Implemented:** 42 features
- **Not implemented:** 14 features
- **Implementation rate:** 75%

## Recommended Next Steps

1. **References** — Run `reference-generator` skill to add curated references per chapter
2. **About page** — Create docs/about.md with project background
3. **Book metrics** — Run `book-metrics-generator` for detailed statistics
4. **Social cards** — Install imaging dependencies for social media previews
5. **GLightbox** — Add image zoom for plant photos
6. **Celebration animations** — Interactive plant ID quizzes with confetti
7. **Custom 404** — Friendly error page featuring Bree
