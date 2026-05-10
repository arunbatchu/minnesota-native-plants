# Book Improvement Notes — observations from the Crane Dance Trail design session

These notes capture what was *missing* from the *Minnesota Native Plants* textbook when used as the reference for a real residential landscape design (Spring 2026, 8547 Crane Dance Trail, Eden Prairie). They're organized as gaps to fill in future revisions of the book — neither bug reports nor a critique, just a feedback loop from a real-world use.

The session is preserved in `landscape-design/front-yard-savanna/`.

---

## Most-impactful gaps

### 1. Per-species profile pages with botanical illustrations

The current `docs/plants/*.md` cards have:

- 1-2 Wikipedia photos (inconsistent quality, often centered on flowers only)
- A short summary lifted from Wikipedia
- An empty Quick Facts table (height, bloom time, sun, moisture, soil, wildlife value all default to "—")
- Chapter cross-references and image credits

What would substantially upgrade these:

- A **scientific illustration** in the spirit of Curtis's Botanical Magazine (full habit + flower close-up + leaf + seed/fruit + root in one composed plate)
- **Filled-in Quick Facts** — even rough bands (e.g., height "2-3 ft", bloom "Jul-Aug") are more useful than dashes
- A **"Reason to be"** section — *why this species exists in this ecosystem; what depends on it* — that gives readers an emotional + ecological anchor
- A **History / Cultural use** section pulling in indigenous and ethnobotanical context (currently siloed in Ch 13 and not cross-referenced)

**Status:** Pilot underway in this design package. Illustrations and per-species pages generated for the 18 design species; same illustrations dropped into `docs/plants/img/[slug]-illustration.png` to enrich the textbook itself.

### 2. Quick Facts data isn't extracted anywhere

Every species card has the table but no entries. The data exists in horticultural references (Prairie Moon catalog, USDA PLANTS database, MN DNR rare-plant guide, MNFI). A future pass should extract:

- Height range
- Bloom time (month-precision)
- Sun exposure (full sun / part shade / shade)
- Moisture (dry / mesic / wet)
- Soil (sand / loam / clay; pH if relevant)
- Wildlife value (pollinator / bird / butterfly host / mammal)
- USDA hardiness zone
- MN native range (county-level if possible)
- Provenance recommendation (MN-genotype seed source)

Mining Prairie Moon's catalog programmatically would give 80% of this data in a few hours. The plant-gallery-generator skill should learn to populate these fields.

### 3. No worked design examples in the garden-design chapter

Chapter 10 (`Garden Design with Native Plants`) is excellent on principles — sun assessment, rain garden zones, pollinator design, layering — but contains no **end-to-end worked example**. A real homeowner reading it can't see how the principles compose into "here's a real bed in a real yard."

What would help:

- A "case study" sidebar or appendix showing a real design from problem to install
- This Crane Dance Trail design is exactly that artifact, and should be considered for inclusion (with permission) once installed and documented across years 1, 3, 5
- Even a hypothetical worked example would be useful

### 4. No bloom-overlap / phenology visualization

Chapter 6 references a Bloom Calendar MicroSim (`docs/sims/bloom-calendar/main.html`) but the book has no static, printable bloom-overlap chart. We built a Gantt for the 18 design species in this project — that pattern should be exported back to the book as either:

- A general "common MN native bloom calendar" appendix
- A per-chapter bloom strip (Ch 03 prairie, Ch 04 woodland, Ch 05 wetland)
- A reusable component the chapter-content-generator skill can produce

### 5. No path / hardscape / seating chapter

Garden design isn't only about plants. The chapter on garden design briefly mentions "edge definition" but the book has no coverage of:

- Path materials and how to choose them (limestone steppers, flagstone, pea gravel, mulch)
- Trench-cut edges vs. fieldstone mowing strips vs. steel
- Bench placement and orientation principles
- Bench-pad construction
- Lighting choices for native gardens
- Snow-load and winter access considerations

The Crane Dance Trail design encountered all of these and had to invent the answers. A "Hardscape Companions" chapter would slot naturally between Ch 10 (garden design) and Ch 11 (whatever comes next).

### 6. No vegetated-bioswale guidance

Chapter 10's rain garden section is well-done but is ABOUT a depression that holds water, not a *flow* path. The vegetated bioswale (sedge-meadow channel that *conveys* and slows stormwater while looking like a meadow) is a related but distinct topic that:

- Is increasingly common in Twin Cities residential design
- Has a different plant palette (Carex stricta, Carex vulpinoidea, Juncus effusus dominate)
- Has different construction (erosion blanket, plug spacing)
- Is what the Met Council promotes for residential stormwater

Worth a stand-alone section or short chapter.

### 7. No Web Soil Survey workflow

Chapter 02 (Ecoregions & Growing Conditions) and Chapter 10 both reference soil but neither walks the reader through:

1. Going to https://websoilsurvey.nrcs.usda.gov/app/
2. Drawing an "Area of Interest" around their parcel
3. Reading the soil map unit name (e.g., Hayden loam, 6-12% slopes)
4. Interpreting the soil's traits for native-plant suitability

This is a 5-minute exercise that 99% of readers don't realize is freely available. A short "how to identify your actual soil" sidebar in Ch 02 would change behavior.

### 8. No pre-settlement vegetation lookup workflow

Chapter 02 mentions ecoregions, but the Marschner pre-settlement vegetation map (the literal best reference for "what would have grown here in 1820") is never referenced or linked. The MN Natural Resource Atlas hosts this at https://mnatlas.org/resources/vegetation-presettlement/ and lets you find your specific parcel's pre-settlement community.

This is *the* answer to "what plants belong here" and would be a magnificent addition to Ch 02's site-assessment section.

### 9. Year-by-year evolution of plantings isn't taught

The book teaches species but not how a *planting* changes over time. A new native garden:

- Year 1 looks "planted" with bare soil between drifts; many forbs don't flower
- Year 2 starts to fill in
- Year 3 is "established" — the look on most native-garden websites
- Year 5 is "matured" — drifts overlap, species composition shifts via self-seeding
- Year 10+ requires editing as some species die out and others colonize

Setting this expectation honestly in Ch 10 would prevent a lot of "did it fail?" anxiety in years 1-2.

### 10. No host-plant / pollinator matrix

Ch 06 (Pollinators & Wildlife) introduces Monarchs, native bees, and host-plant ecology, but doesn't include a **matrix** showing which butterfly/moth species needs which native plant for larval food. This matrix would be:

- A reference card for designers ("which host plants do I need to attract Karner Blue?")
- A teaching tool for students (the *specificity* of host-plant relationships is the most striking insight in pollinator ecology)
- Easy to assemble from the MN Pollinator Plant List

### 11. No installation / phasing / DIY-vs-pro decision framework

Ch 10's content is design-focused. There's no chapter or appendix on:

- DIY vs. professional install — when to choose which
- How to get and compare quotes
- How to phase a multi-season install
- What removal of an existing landscape entails (mugo pine takedown, etc.)
- Cost ranges typical for Twin Cities residential native installs

The installer-packet.md generated for this design would be a strong starting template for a "Working with Installers" appendix.

### 12. No printable / take-along resources

The book is built as a website. There's no:

- Downloadable printable site-assessment checklist
- Printable plant-selection worksheet
- Printable maintenance calendar
- Print-ready species pocket cards

The booklet generator pattern from this design (`booklet.py` using ReportLab) could be generalized into a site-wide "Print this section" feature.

### 13. The site-assessment MicroSim could output a real plan

`docs/sims/site-assessment-tool/main.html` lets users enter site conditions and get plant recommendations. It could be extended to:

- Generate a downloadable planting plan PDF (similar to `plan.md` here)
- Produce a bloom calendar specific to the user's selected species
- Output a printable booklet of the user's choices

This would be a flagship interactive feature.

### 14. Mascot (Bree the Bee) under-utilized

Bree appears at chapter openings and key concepts but doesn't show up in the *practical* sections — site assessment, plant-selection, bloom-calendar reading. A few more Bree mascot moments at decision points would warm those sections.

### 15. Indigenous knowledge mostly lives in a single chapter

Ch 13 (Cultural & Indigenous Uses) is wonderful but stands alone. Cultural uses of specific plants (Serviceberry/Juneberry as food, Wild Bergamot as medicine, Prairie Smoke ceremony, Tobacco) should appear in the *species cards themselves*, not only as a separate chapter. The plant-gallery-generator could optionally pull from Ch 13 when populating "History" sections of cards.

---

## Specific species cards to enrich

The following species are foundational MN natives whose cards exist but are thin. Each could grow into a 2-page profile:

- Wild Bergamot (Monarda fistulosa) — most ecologically generous pollinator plant; deserves full treatment of its bee/moth/hummingbird relationships
- Big Bluestem, Little Bluestem, Indian Grass — the iconic warm-season trio; each card should explain the C4 photosynthesis adaptation
- Cup Plant (Silphium perfoliatum) — water-holding leaves are a teaching moment
- Compass Plant (Silphium laciniatum) — the leaf-orientation behavior is fascinating
- Wild Lupine (Lupinus perennis) — Karner Blue host plant, link to endangered-species ecology
- Bur Oak (Quercus macrocarpa) — keystone species, deserves its own deep page
- Bloodroot — Indigenous use + spring-ephemeral life history
- Pasque Flower — earliest-blooming native, threatened in many MN habitats

---

## Five species the book is missing entirely (as of Spring 2026)

These were added during this design project but represent a class of foundational MN natives that the book should systematically cover:

| Common name | Scientific | Why it matters |
|---|---|---|
| Serviceberry | *Amelanchier laevis* | Anchor small tree in residential design; April bloom; bird food; iconic |
| Ninebark | *Physocarpus opulifolius* | Most-used native foundation shrub; four-season interest; exfoliating bark |
| Gray Dogwood | *Cornus racemosa* | Native shrub; white berries on red pedicels are a fall signature |
| False Blue Indigo | *Baptisia australis* | Long-lived structural prairie forb; nitrogen fixer; deer-resistant |
| Prairie Smoke | *Geum triflorum* | Iconic spring groundcover; feathery seed plumes are unmistakable |

Cards for these five were generated and committed during this session.

A future pass should sweep through other foundational species the book is missing:

- Pagoda Dogwood (*Cornus alternifolia*)
- Witch Hazel (*Hamamelis virginiana*) — late fall bloom!
- New Jersey Tea (*Ceanothus americanus*) — small native shrub
- Pussytoes (*Antennaria neglecta*)
- Wild Strawberry (*Fragaria virginiana*)
- Tussock Sedge (*Carex stricta*) — major bioswale species
- Fox Sedge (*Carex vulpinoidea*)
- Soft Rush (*Juncus effusus*)
- Great Blue Lobelia (*Lobelia siphilitica*)
- Hairy Beardtongue (*Penstemon hirsutus*)
- Anise Hyssop (*Agastache foeniculum*)
- Smooth Penstemon (*Penstemon digitalis*)
- Joe-Pye Weed (*Eutrochium maculatum*)
- Cardinal Flower (*Lobelia cardinalis*) — done
- Showy Goldenrod (*Solidago speciosa*) — well-behaved native goldenrod

---

## Minor items observed

- **Image rendering:** The plant-gallery-generator pulls 1280px thumbnails from Wikipedia. For the gallery cards this is fine; for any future "print" use case, higher-res sources or licensed botanical photography would help.

- **Image-credit format inconsistency:** The auto-generated `## Image Credits` section uses `Photographer (License)` format. For prints this might want fuller "Image: [credit]. License: [text]. Source: Wikimedia Commons." for proper attribution.

- **Card slug for "False Blue Indigo":** The auto-slugifier produced `false-blue-indigo`. That's fine, but the more common name is just "Wild Indigo" or "Blue Wild Indigo" in MN — worth a short alias note in the data file.

- **Auto-link applied 9 replacements** in chapters this session (Common Milkweed, Wild Bergamot, Wild Columbine, Wild Lupine in Ch 06; Gray Dogwood, Ninebark, Prairie Smoke, Serviceberry, False Blue Indigo in Ch 10). Future runs should consider linking the *second* mention as well when a chapter discusses a species in depth across multiple sections.

- **Glossary update opportunity:** The site has terms like "ecoregion," "Marschner map," "pre-settlement vegetation," "bioswale," "plug," "screenings," "provenance." Some are in the glossary, others aren't. Worth a sweep.

- **No "downloads" section:** The site has chapters and microsims but no page that aggregates "things you can print and take with you" — checklists, maintenance calendars, pocket plant guides, the bloom calendar.

---

## Suggested next moves for the textbook (in priority order)

1. **Add the 5 missing species cards** ✅ DONE
2. **Generate Curtis-style botanical illustrations** for the 18 design species ✅ DONE (21 illustrations now)
3. **Drop those illustrations into the textbook's species cards** ✅ DONE (template embeds them automatically)
4. **Add a "Worked Example" appendix** built from this design package — DEFERRED until install completes
5. **Populate Quick Facts data** for at least the 30 most-used species — DEFERRED (substantial scrape effort)
6. **Add bloom Gantt charts** to chapters 03, 04, 05, 06, 10 — DEFERRED (one chapter at a time)
7. **Web Soil Survey + Marschner workflow sidebars** in Ch 02 ✅ DONE
8. **Vegetated bioswale section** in Ch 10 ✅ DONE
9. **Year-by-year evolution sidebar** in Ch 10 ✅ DONE
10. **Pollinator host-plant matrix** in Ch 06 ✅ DONE
11. **Working with Installers appendix** built from installer-packet.md ✅ DONE (added as section to Ch 11)
12. **Print-ready downloads page** with site-assessment checklist, maintenance calendar, plant pocket cards, bloom calendar — DEFERRED

**Eight of twelve items completed.** The remaining four are explicitly deferred (worked-example needs install photos; Quick Facts and per-chapter bloom charts are substantial work; downloads page needs site-wide infrastructure).

---

## How this file should evolve

This file is a *snapshot* — observations from one design project. It will be richer if subsequent design projects (or the same project at year 1, year 3, year 5) add their own observations.

Consider creating `docs/book-improvement-notes/` as a directory of these files, one per project / cycle, so the book authors can read across them.

The session that produced this file is preserved in `landscape-design/front-yard-savanna/`.
