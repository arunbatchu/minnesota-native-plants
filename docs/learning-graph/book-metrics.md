# Book Metrics

This file contains overall metrics for the intelligent textbook.

| Metric Name | Value | Link | Notes |
|-------------|-------|------|-------|
| Chapters | 17 | [Chapters](../chapters/index.md) | Number of chapter directories |
| Concepts | 289 | [Concept List](./concept-list.md) | Concepts from learning graph |
| Glossary Terms | 288 | [Glossary](../glossary.md) | Defined terms |
| FAQs | 70 | [FAQ](../faq.md) | Frequently asked questions |
| Quiz Questions | 170 | - | Questions across all chapters |
| Diagrams | 0 | - | Level 4 headers starting with '#### Diagram:' |
| Equations | 9 | - | LaTeX expressions (inline and display) |
| MicroSims | 22 | [Simulations](../sims/index.md) | Interactive MicroSims |
| Total Words | 175,395 | - | Words in all markdown files |
| Links | 976 | - | Hyperlinks in markdown format |
| Equivalent Pages | 712 | - | Estimated pages (250 words/page + visuals) |
| Species Cards | 99 | [Plants](../plants/index.md) | Per-species reference pages |
| Cards w/ Illustration | 21 (21%) | - | Botanical plates available |
| Cards w/ Photos | 95 (95%) | - | Wikipedia/Wikimedia photo present |
| Cards w/ Quick Facts | 0 (0%) | - | Trait data populated (not just dashes) |
| Host-plant Mentions | 20 | - | Pollinator-host coverage signal |

## Metrics Explanation

- **Chapters**: Count of chapter directories containing index.md files
- **Concepts**: Number of rows in learning-graph.csv
- **Glossary Terms**: H4 headers in glossary.md
- **FAQs**: H3 headers in faq.md
- **Quiz Questions**: H4 headers with numbered questions (e.g., '#### 1.') or H2 headers in quiz.md files
- **Diagrams**: H4 headers starting with '#### Diagram:'
- **Equations**: LaTeX expressions using $ and $$ delimiters
- **MicroSims**: Directories in docs/sims/ with index.md files
- **Total Words**: All words in markdown files (excluding code blocks and URLs)
- **Links**: Markdown-formatted links `[text](url)`
- **Equivalent Pages**: Based on 250 words/page + 0.25 page/diagram + 0.5 page/MicroSim
- **Species Cards**: Files in docs/plants/ (excluding index.md)
- **Cards w/ Illustration**: Cards whose docs/plants/img/<slug>-illustration.png exists
- **Cards w/ Photos**: Cards referencing at least one <slug>-1.jpg photo
- **Cards w/ Quick Facts**: Cards whose Quick Facts table has at least one populated row (not just em-dashes)
- **Host-plant Mentions**: Occurrences of 'host plant' or 'larval host' in chapters — soft signal of pollinator-ecology coverage
