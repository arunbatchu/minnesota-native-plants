# Minnesota Native Plants — Project Guidelines

## Project Overview

- **Title**: Minnesota Native Plants
- **Type**: Interactive intelligent textbook built with MkDocs Material
- **Audience**: General public — no prior botany or ecology background required
- **Tone**: Friendly, approachable, calm, and supportive
- **License**: CC BY-NC-SA 4.0

## Content Style Guide

### Writing Style

- Write for a general public audience with no assumed botanical knowledge
- Define technical terms on first use
- Use active voice and short, clear sentences
- Keep paragraphs to 3-5 sentences
- Use "you" to address the reader directly
- Prefer concrete examples over abstract explanations
- Reference Minnesota-specific locations, species, and programs when possible

### Markdown Formatting

- Always place a blank line before any markdown list (required by MkDocs)
- Use `##` for main sections, `###` for subsections within chapters
- Use admonitions for tips, warnings, and key insights
- Embed MicroSims using iframes where interactive content adds value
- Use Title Case for chapter and section headings

### Plant References

- Use common names first, followed by scientific name in italics on first mention: e.g., "Purple Coneflower (*Echinacea purpurea*)"
- After first mention, use common name only
- When listing multiple species, use a bulleted list with both names

### Image Paths

- From chapter pages (`chapters/01-xxx/index.md`): use `../../img/mascot/`
- From learning-graph pages (`learning-graph/xxx.md`): use `../../img/mascot/`
- From top-level docs pages (`docs/xxx.md`): use `img/mascot/`

## Learning Mascot: Bree the Bee

### Character Overview

- **Name**: Bree
- **Species**: Honeybee
- **Personality**: Warm, patient, encouraging, gentle, calm, supportive
- **Catchphrases**: "Let's explore the prairie!", "Every plant has a story!", "Let's grow together!"
- **Visual**: Round, cheerful watercolor honeybee with golden-yellow and dark brown stripes, translucent iridescent wings, large warm brown eyes, tiny green leaf beret, carries a small wildflower
- **Art Style**: Soft watercolor with warm tones and clean edges

### Voice Characteristics

- Uses simple, encouraging language accessible to the general public
- Alternates between three catchphrases to keep content fresh
- Refers to readers as "fellow nature lovers" or "garden friends"
- Occasionally uses gentle nature puns
- Never condescending — treats readers as curious adults

### Mascot Admonition Format

Always place mascot images in the admonition body, never in the title bar:

    !!! mascot-welcome "Title Here"
        <img src="../../img/mascot/welcome.png" class="mascot-admonition-img" alt="Bree waving welcome">
        Admonition text goes here after the img tag.

### Available Poses

| Filename | Pose | Use For |
|----------|------|---------|
| neutral.png | Relaxed, standing | General notes, sidebars |
| welcome.png | Waving | Chapter openings |
| thinking.png | Chin on hand, lightbulb | Key concepts, insights |
| tip.png | Pointing up, sparkle | Tips and hints |
| warning.png | Holding warning sign | Mistakes, invasive species alerts |
| encouraging.png | Thumbs up | Difficult content |
| celebration.png | Arms raised, confetti | Achievements, section completion |

### Placement Rules

| Context | Admonition Type | Frequency |
|---------|----------------|-----------|
| General note / sidebar | mascot-neutral | As needed |
| Chapter opening | mascot-welcome | Every chapter |
| Key concept | mascot-thinking | 2-3 per chapter |
| Helpful tip | mascot-tip | As needed |
| Common mistake / invasive species alert | mascot-warning | As needed |
| Difficult content | mascot-encourage | Where students may struggle |
| Section completion | mascot-celebration | End of major sections |

### Do's and Don'ts

**Do:**

- Use Bree to introduce new topics warmly
- Include a catchphrase in welcome admonitions
- Keep dialogue brief (1-3 sentences)
- Match the pose/image to the content type

**Don't:**

- Use Bree more than 5-6 times per chapter
- Put mascot admonitions back-to-back
- Use the mascot for purely decorative purposes
- Change Bree's personality or speech patterns

## Color Palette

- **Primary**: Green (`#2e7d32` / Material green)
- **Accent**: White
- **Mascot primary**: Forest green (`#2e7d32`)
- **Mascot secondary**: Warm brown (`#795548`)
- **Mascot background**: Light green (`#e8f5e9`)

## Project Structure

```
docs/
├── index.md                  # Home page
├── course-description.md     # Course description with Bloom's taxonomy
├── glossary.md               # Glossary of terms
├── chapters/                 # Chapter content (17 chapters)
├── learning-graph/           # Learning graph files and reports
├── sims/                     # MicroSims (interactive visualizations)
├── img/mascot/               # Bree mascot images (7 poses)
├── css/mascot.css            # Mascot admonition styles
└── js/                       # JavaScript files
```
