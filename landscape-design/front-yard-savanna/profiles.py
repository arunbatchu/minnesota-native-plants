"""
Plant profile pages — one PDF page per species.

For each species in the design:
  1. Generate a Curtis's Botanical Magazine-style illustration via
     Gemini 3 Pro Image (Nano Banana Pro).
  2. Lay out a one-page profile PDF with the illustration on top,
     and four prose sections below: Qualities · Care · History · Reason to be.

Output:
  illustrations/<slug>.png      — saved to docs/plants/img/<slug>-illustration.png too
  profiles/<slug>.pdf            — single-species page
  plant-profiles.pdf             — bundle of all profiles in one PDF

Usage:
  python3 profiles.py serviceberry              # one species (illustration + page)
  python3 profiles.py --all                      # all species
  python3 profiles.py --bundle                   # combine all existing pages

Reads GEMINI_API_KEY from .env (gitignored).
"""
from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path
from PIL import Image as PILImage

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as rl_canvas

ROOT = Path(__file__).parent
ILLUSTRATIONS = ROOT / "illustrations"
PROFILES = ROOT / "profiles"
ILLUSTRATIONS.mkdir(exist_ok=True)
PROFILES.mkdir(exist_ok=True)

# Where to also drop illustrations into the textbook itself
TEXTBOOK_PLANTS_IMG = (
    ROOT.parent.parent / "docs" / "plants" / "img"
)

# ============================================================
# Species content — written for each design species
# ============================================================

SPECIES = {
    "serviceberry": {
        "common": "Serviceberry",
        "scientific": "Amelanchier laevis",
        "family": "Rosaceae",
        "subtitle": "Allegheny Shadbush · Juneberry",
        "qualities": (
            "A small multi-stem tree or large shrub of the rose family, "
            "growing 15 to 25 feet at maturity with a graceful rounded "
            "crown. Smooth pale-gray bark, and oval finely-toothed "
            "leaves that emerge bronze-purple, mature to soft green, and "
            "turn brilliant orange-red in fall. White five-petaled "
            "flowers appear in drooping clusters before the leaves in "
            "mid-April — one of the earliest woody bloomers in the "
            "Minnesota landscape — followed in June by dark purple "
            "edible berries that birds strip in a few days."
        ),
        "care": (
            "Plant in fall or early spring as a 6 to 8 ft balled-and-"
            "burlapped specimen, not bare-root. Full sun to part shade; "
            "tolerates loam, clay, or sandy soils so long as drainage is "
            "reasonable. Drought-tolerant once established. No regular "
            "pruning required; remove the occasional sucker to maintain "
            "a single-trunk or open multi-stem form. Hardy to USDA Zone 3. "
            "Avoid waterlogged sites and overly rich soils — they "
            "encourage soft growth that's prone to fire blight."
        ),
        "history": (
            "The name \"serviceberry\" descends from \"sorbus,\" the "
            "Latin name for a related fruit. To the Anishinaabe and "
            "Dakota of Minnesota this tree is \"Juneberry\" — its "
            "fruits, eaten raw or pounded with meat and fat into "
            "pemmican, were among the first fresh foods of the year. "
            "Lewis & Clark recorded the species as a key wild food of "
            "the Great Plains, and it has been in continuous "
            "cultivation since."
        ),
        "reason": (
            "A serviceberry is a small ecological universe. April flowers "
            "feed early-emerging native bees when almost nothing else is "
            "open. June berries feed Cedar Waxwings, Robins, Catbirds, "
            "and dozens of other songbirds. Its leaves host the larvae "
            "of more than a hundred native moth and butterfly species. "
            "In a designed garden it offers four seasons of structure — "
            "spring bloom, summer fruit, fiery fall color, winter "
            "silhouette. Plant it as the anchor and the rest of the "
            "garden gathers around it."
        ),
    },
    "ninebark": {
        "common": "Ninebark",
        "scientific": "Physocarpus opulifolius",
        "family": "Rosaceae",
        "subtitle": "Eastern Ninebark",
        "qualities": (
            "An arching deciduous shrub of stream-banks and rocky "
            "openings, growing 5 to 8 feet tall and as wide. The common "
            "name comes from its habit of peeling bark in long curling "
            "strips, exposing layer after layer of red-brown to "
            "cinnamon-colored inner bark — a landmark in the winter "
            "garden. Three-lobed maple-like leaves and clusters of "
            "small white flowers in late June give way to reddish "
            "papery seed capsules that persist into fall."
        ),
        "care": (
            "Tough as nails. Full sun to part shade; tolerates clay, "
            "sand, drought, occasional flooding, urban pollution, road "
            "salt, and rabbits. Hardy to USDA Zone 2. Plant 1-gallon "
            "or 3-gallon container stock; spaces about 5 ft apart for a "
            "loose hedge. Prune in late winter — cut a third of oldest "
            "stems to ground each year to keep the shrub vigorous and "
            "the bark display visible. Avoid 'Summer Wine' and similar "
            "purple-foliage cultivars in stucco-architecture settings — "
            "the foliage clashes."
        ),
        "history": (
            "Ninebark's name appears across Indigenous, Colonial, and "
            "modern horticulture. The Cherokee used a bark decoction as "
            "an emetic and for women's medicine; the Ojibwe used it in "
            "post-childbirth care. Settlers in eastern North America "
            "named it \"ninebark\" for the apparent nine layers of "
            "shedding bark. It became a foundational shrub in 20th-"
            "century American landscape design before the cultivar "
            "explosion of the 2000s; the straight species is now "
            "experiencing a quiet revival among ecological designers."
        ),
        "reason": (
            "Ninebark anchors residential bed design with a visual "
            "presence that shifts every month: white pollinator-loaded "
            "flowers in June, reddish seedheads through summer, golden "
            "leaves in October, and the celebrated peeling bark from "
            "November through April. Native bees, hover flies, and "
            "small butterflies work the bloom. Birds nest in the dense "
            "branching. It is one of the few native shrubs that holds "
            "its own visually against architectural elements — stucco, "
            "stone, brick — without disappearing into the green."
        ),
    },
    "gray-dogwood": {
        "common": "Gray Dogwood",
        "scientific": "Cornus racemosa",
        "family": "Cornaceae",
        "subtitle": "Northern Swamp Dogwood",
        "qualities": (
            "A clonal native shrub forming dense colonies 6 to 10 feet "
            "tall and equally wide. Slender gray-brown stems hold "
            "narrow oval leaves that turn dusty purple-red in autumn. "
            "Flat-topped clusters of small white flowers in early "
            "summer mature to chalk-white berries on bright red "
            "pedicels — one of the most striking fall combinations in "
            "the Minnesota landscape. Birds typically strip the fruit "
            "within a week or two; the red pedicels persist into "
            "winter as decorative accents."
        ),
        "care": (
            "Adaptable to nearly any soil except deep sand or saturated "
            "wetland. Full sun gives best fruit set; tolerates part "
            "shade. Suckers slowly to form thickets — a feature, not a "
            "bug, in informal native plantings, but in formal beds you "
            "may want a root barrier or annual sucker pruning. Hardy "
            "to USDA Zone 3. Disease- and pest-free. No regular feeding "
            "or watering needed once established."
        ),
        "history": (
            "Gray dogwood was used by several Indigenous peoples for "
            "tool handles, basket rims, and arrows; the straight, "
            "flexible young stems take a clean shave. Colonial "
            "herbalists pressed bark and root for a quinine substitute "
            "(it's a relative of the medicinal Cornus florida). In "
            "Minnesota's prairie-forest border ecosystem, it filled "
            "the role of \"thicket maker\" — providing the dense "
            "shrubbery that separated savanna openings from closed "
            "woodland."
        ),
        "reason": (
            "Gray dogwood is the workhorse of bird-supporting "
            "shrub plantings. Its berries feed at least 98 documented "
            "bird species, including Brown Thrashers, Wood Thrushes, "
            "Catbirds, and migrating Warblers. The dense thicket form "
            "provides nesting cover for ground-nesting and "
            "shrub-nesting birds. As a fast-establishing native, it "
            "serves as a placeholder while slower-growing trees like "
            "oak mature; in larger restoration projects it forms the "
            "ecological scaffolding under which an oak savanna or "
            "edge habitat assembles itself."
        ),
    },
    "false-blue-indigo": {
        "common": "False Blue Indigo",
        "scientific": "Baptisia australis",
        "family": "Fabaceae",
        "subtitle": "Wild Blue Indigo · Blue False Indigo",
        "qualities": (
            "A long-lived herbaceous perennial of the pea family, "
            "growing 3 to 4 feet tall with the architectural presence "
            "of a small shrub. Blue-green clover-like leaves on "
            "branching upright stems form a tidy mounded clump. In "
            "late May and June, vertical racemes of indigo-blue pea-"
            "like flowers rise above the foliage, followed by inflated "
            "black seed pods that rattle decoratively into winter. The "
            "deep taproot makes Baptisia nearly impossible to "
            "transplant once established — and nearly impossible to "
            "kill."
        ),
        "care": (
            "Plant from 1-gallon container in spring, into open ground "
            "where it will live for the rest of your gardening life. "
            "Full sun, average to dry soil; tolerates drought, lean "
            "soil, and clay. Slow to establish — expect a quiet first "
            "two summers — then bullet-proof. Hardy to USDA Zone 3. As "
            "a nitrogen-fixing legume, it actively improves soil for "
            "neighboring forbs. Avoid moving once mature; if you must, "
            "do it in early spring with a tarp and prepare to lose half "
            "the root system."
        ),
        "history": (
            "The genus name *Baptisia* derives from Greek *baptein*, "
            "\"to dye\" — Indigenous peoples used several Baptisia "
            "species as a substitute for the imported indigo dye, "
            "though the color is muted compared to true *Indigofera*. "
            "Cherokee and Choctaw used a root preparation for "
            "toothache and as a purgative. In 19th-century horticulture "
            "Baptisia was promoted as a substitute for the southern "
            "lupines, since it is more cold-hardy. It has remained a "
            "stalwart of MN prairie restoration ever since."
        ),
        "reason": (
            "Baptisia anchors a prairie or savanna planting in time. "
            "While neighboring forbs cycle through five-year boom-and-"
            "decline rhythms, Baptisia is in year fifteen still in the "
            "same spot, getting better. Its early-summer bloom feeds "
            "long-tongued bumblebees and the Wild Indigo Duskywing "
            "skipper, which uses Baptisia as its larval host plant. "
            "The seed pods are an ornamental feature into winter. As "
            "a nitrogen fixer, it conditions soil for the rest of the "
            "planting. Plant it as the structural backbone."
        ),
    },
    "prairie-smoke": {
        "common": "Prairie Smoke",
        "scientific": "Geum triflorum",
        "family": "Rosaceae",
        "subtitle": "Old Man's Whiskers · Three-flowered Avens",
        "qualities": (
            "A low evergreen rosette of fern-like compound leaves, "
            "6 to 10 inches tall in flower, that hugs the ground "
            "year-round. In May, slender stems each bearing three "
            "nodding pink-purple urn-shaped flowers rise above the "
            "foliage. As the flowers age the petals fall and the "
            "styles elongate into long feathery plumes — pink, "
            "smoky, twisting — that give the plant its name. The "
            "plumes catch the light and the wind for weeks. By "
            "midsummer the seedheads dry and disperse, leaving the "
            "evergreen rosette behind."
        ),
        "care": (
            "Full sun, well-drained soil; ideal for sandy or rocky "
            "sites. Hates wet feet — site away from downspouts and "
            "low spots. Plant from 4-inch plug or quart container in "
            "spring or fall, 9 to 12 inches apart for groundcover. "
            "Hardy to USDA Zone 3. Slow to spread but extremely "
            "long-lived once established — a clump can persist for "
            "decades. Avoid mulching directly over the rosette; the "
            "evergreen leaves want air."
        ),
        "history": (
            "Prairie smoke is one of the iconic remnant-prairie "
            "indicator species in Minnesota — finding a colony in a "
            "ditch or pasture is considered evidence of pre-settlement "
            "soil. The Blackfeet used a root decoction as eyewash and "
            "as a tea for stomach upset. The seed plumes were "
            "occasionally used for arrow fletching and as kindling. "
            "The name \"old man's whiskers\" appears across Indigenous "
            "and settler vocabularies for the same reason — the "
            "feathery plumes look exactly like grizzled hair."
        ),
        "reason": (
            "Prairie smoke is the path-edge groundcover for which "
            "every native garden secretly hopes. It blooms before "
            "almost everything else in the prairie, drawing early "
            "queen bumblebees out of dormancy. Its evergreen winter "
            "presence keeps the bed from looking dead in March and "
            "October. The seedplumes are unforgettable — visiting "
            "neighbors stop in their tracks. Plant it where children "
            "can touch the plumes; that tactile encounter is how "
            "prairie ecology becomes real for a 6-year-old."
        ),
    },
    "wild-bergamot": {
        "common": "Wild Bergamot",
        "scientific": "Monarda fistulosa",
        "family": "Lamiaceae",
        "subtitle": "Bee Balm · Horsemint",
        "qualities": (
            "A clumping mint-family perennial 2 to 4 feet tall, with "
            "square stems, opposite gray-green leaves that smell "
            "sharply of oregano when bruised, and rounded "
            "two-inch-wide pom-poms of lavender-pink tubular flowers "
            "in July. Flowers persist three to four weeks; the "
            "structural seedheads remain handsome through fall and "
            "into winter. Forms a slowly-expanding colony by "
            "underground rhizomes."
        ),
        "care": (
            "Full sun is best; tolerates light shade. Average to dry "
            "soil; drought-tolerant. Deer-resistant. In humid climates "
            "or crowded plantings, watch for powdery mildew on lower "
            "leaves; thinning the clump and improving airflow usually "
            "fixes it without spraying. Hardy to USDA Zone 3. "
            "Cut back to 6 inches in late winter; the hollow stems "
            "(*fistulosa* means \"hollow\") house overwintering "
            "native bees, so don't tidy too early in spring."
        ),
        "history": (
            "Wild bergamot is the wild ancestor of cultivated Bee Balm "
            "and is named for its similarity in scent to bergamot "
            "orange (*Citrus bergamia*) — Earl Grey tea's flavor note. "
            "The Ojibwe and Menominee used the leaves as a medicinal "
            "tea for respiratory illness, and the species is the "
            "primary source of thymol in pre-aspirin North American "
            "medicine. Following the Boston Tea Party, colonists used "
            "wild bergamot as a black-tea substitute (\"Oswego tea\")."
        ),
        "reason": (
            "If you plant only one pollinator forb, plant this. Wild "
            "bergamot draws an extraordinary diversity of visitors: "
            "long-tongued native bumblebees, Hummingbird Clearwing "
            "moths, Ruby-throated Hummingbirds, Eastern Tiger "
            "Swallowtails, and dozens of native bee species. Its "
            "hollow stems shelter overwintering tunnel-nesting bees. "
            "It is a workhorse that delivers ecological value at "
            "every stage — bloom, seed, winter cover."
        ),
    },
    "purple-coneflower": {
        "common": "Purple Coneflower",
        "scientific": "Echinacea purpurea",
        "family": "Asteraceae",
        "subtitle": "Eastern Purple Coneflower",
        "qualities": (
            "A clumping prairie composite 2 to 3 feet tall, with "
            "rough hairy lance-shaped leaves and large daisy-like "
            "flowers from July through September. The drooping "
            "rose-pink ray petals surround a spiny copper-orange "
            "central cone made of hundreds of tiny disc florets. "
            "Cones persist into winter as architectural seedheads "
            "favored by goldfinches."
        ),
        "care": (
            "Full sun, average to dry well-drained soil. Tolerates "
            "clay better than most coneflowers. Hardy to USDA Zone 3. "
            "Plant from 1-gallon container or seed in fall; "
            "self-seeds modestly into receptive areas (a feature in "
            "naturalistic plantings). Deadheading extends bloom but "
            "removes the seed source for goldfinches; consider "
            "leaving half. Cut stems to 6 inches in late winter."
        ),
        "history": (
            "*Echinacea* derives from Greek *echinos*, \"hedgehog\" — "
            "for the spiny central cone. Plains tribes used the root "
            "extensively as an immune-system modulator, applying it "
            "for everything from snakebite to toothache to colds. "
            "European settlers adopted the use, and a 19th-century "
            "Nebraska physician's commercial Echinacea preparations "
            "became one of the most widely-sold patent medicines of "
            "the era. Modern research has confirmed several of the "
            "traditional uses; Echinacea remains a top-selling herbal "
            "supplement worldwide."
        ),
        "reason": (
            "Purple coneflower is the public face of native-plant "
            "gardening: instantly recognizable, beloved by visitors, "
            "tolerant of mistakes, and ecologically generous. "
            "Long-tongued bees and butterflies (especially Monarchs, "
            "Fritillaries, and Painted Ladies) work the cones; "
            "goldfinches and other small finches harvest the seeds "
            "through fall and winter. In a residential design it "
            "carries the show from July through September while "
            "neighboring forbs hand off bloom."
        ),
    },
    "smooth-blue-aster": {
        "common": "Smooth Blue Aster",
        "scientific": "Symphyotrichum laeve",
        "family": "Asteraceae",
        "subtitle": "Smooth Aster",
        "qualities": (
            "A graceful prairie aster 2 to 3 feet tall, with smooth "
            "blue-green clasping leaves on slender arching stems. From "
            "September into October it produces a cloud of inch-wide "
            "sky-blue daisies with yellow centers, often the last "
            "major bloom in the Minnesota prairie before frost. The "
            "smooth foliage and tidy form distinguish it from many "
            "of its weedier aster cousins."
        ),
        "care": (
            "Full sun is best; tolerates light shade. Average to dry "
            "soil; tolerates drought, clay, and lean conditions. "
            "Deer-resistant. Hardy to USDA Zone 3. Pinch back stems "
            "in early June to encourage compact branching and reduce "
            "any tendency to flop. Self-seeds modestly. Long-lived "
            "and clump-forming rather than aggressively spreading."
        ),
        "history": (
            "Asters were among the most diverse and difficult plant "
            "groups for early North American botanists; the genus has "
            "been split, lumped, and renamed multiple times — the "
            "modern *Symphyotrichum* is a 1995 reorganization of the "
            "old North American \"asters.\" Indigenous peoples used "
            "various asters in smoke for hunting medicine and as a "
            "diaphoretic tea. Smooth blue aster specifically appears "
            "across the prairie-forest border subsection of "
            "Minnesota's pre-settlement vegetation map."
        ),
        "reason": (
            "Smooth blue aster is the closing act of the prairie "
            "season — when bergamot and coneflower are setting seed, "
            "this aster lights up the bed in cool sky-blue. It is a "
            "critical late-season nectar source for migrating "
            "Monarchs and queen bumblebees fattening for hibernation. "
            "The Pearl Crescent butterfly uses it as a larval host. "
            "Its reliable upright form and rich blue color make it "
            "the easiest aster to slot into formal designs without "
            "the wild-edged look of New England aster."
        ),
    },
    "wild-lupine": {
        "common": "Wild Lupine",
        "scientific": "Lupinus perennis",
        "family": "Fabaceae",
        "subtitle": "Sundial Lupine",
        "qualities": (
            "An iconic spring prairie forb 1 to 2 feet tall, with "
            "palmate leaves of 7 to 11 narrow leaflets that orient "
            "throughout the day to track the sun (hence \"sundial "
            "lupine\"). In May and June, vertical racemes of "
            "violet-blue pea-like flowers create the legendary "
            "wave of color that once defined oak savannas across "
            "the upper Midwest. Goes dormant in midsummer, "
            "disappearing entirely by August."
        ),
        "care": (
            "Plant in spring or fall as plug or 1-gallon stock — "
            "MN-genotype provenance is essential. Full sun; sandy or "
            "well-drained loamy soil. Lupine refuses heavy clay and "
            "wet sites. Slow to establish; expect a quiet first "
            "year. Hardy to USDA Zone 3. As a legume, fixes nitrogen "
            "and conditions soil. Do not amend or fertilize — rich "
            "soil makes lupine flop and shortens its life."
        ),
        "history": (
            "Wild lupine is the *only* food plant of the federally "
            "endangered Karner Blue butterfly (*Plebejus melissa "
            "samuelis*). The Karner Blue was widely abundant across "
            "Minnesota's pre-settlement oak savannas. As savannas "
            "were converted to agriculture and shaded out by fire "
            "suppression, lupine populations crashed and the Karner "
            "Blue followed; the butterfly was extirpated from "
            "Minnesota in 2008 and listed as endangered nationally. "
            "Reintroduction efforts depend on restoring lupine."
        ),
        "reason": (
            "To plant wild lupine in Minnesota in 2026 is to "
            "participate in the restoration of an entire vanished "
            "ecosystem. Even one residential planting matters: it "
            "feeds bumblebees and a host of native specialist bees "
            "that no other species supports. If Karner Blues are "
            "ever reintroduced to your area (the work is active in "
            "Wisconsin and may extend to MN), your lupine drift will "
            "be a stepping-stone. Its ephemeral spring presence — "
            "blooming gloriously then fading — teaches a lesson "
            "about prairie phenology that nothing else can."
        ),
    },
    "butterfly-milkweed": {
        "common": "Butterfly Milkweed",
        "scientific": "Asclepias tuberosa",
        "family": "Apocynaceae",
        "subtitle": "Butterfly Weed · Pleurisy Root",
        "qualities": (
            "A clumping prairie milkweed 1 to 2 feet tall, with "
            "narrow alternate leaves on hairy upright stems. From "
            "June into August it produces vibrant clusters of "
            "five-pointed orange flowers — the most saturated orange "
            "in the native flora — followed by typical milkweed "
            "spindle-shaped pods that split to release silk-tufted "
            "seeds. Unlike most milkweeds it does *not* exude white "
            "latex when broken — the sap is clear, hence the genus "
            "name *tuberosa* meaning \"with tuberous root.\""
        ),
        "care": (
            "Full sun, well-drained soil; ideal for sand or sandy "
            "loam. Drought-tolerant. Deer-resistant. The deep taproot "
            "makes Butterfly Milkweed nearly impossible to "
            "transplant — plant once, leave alone. Hardy to USDA "
            "Zone 3. Slow to emerge in spring (mark its location with "
            "a stake the first year so you don't accidentally weed "
            "it). Long-lived once established."
        ),
        "history": (
            "Butterfly milkweed's other common name, \"pleurisy "
            "root,\" reflects its widespread historical use among "
            "Indigenous peoples and 19th-century herbalists for "
            "respiratory illness — the Choctaw, Omaha, Ponca, and "
            "Dakota used a root preparation. The bright orange dye "
            "from the flowers and stems was used in basketwork. "
            "European observers noted the plant as one of the most "
            "visually striking of North American natives, and it has "
            "been in cultivation since the 1690s."
        ),
        "reason": (
            "Butterfly milkweed is one of three Asclepias species "
            "that serve as primary host plants for the Monarch "
            "butterfly — without milkweed, no Monarchs. Its summer "
            "bloom is also a magnet for Eastern Tiger Swallowtails, "
            "Fritillaries, and dozens of native bee species. The "
            "saturated orange is so visually striking it provides "
            "the design's color punctuation. Plant in drifts of 5 "
            "or more for visual mass and pollinator-attraction "
            "amplification."
        ),
    },
    "little-bluestem": {
        "common": "Little Bluestem",
        "scientific": "Schizachyrium scoparium",
        "family": "Poaceae",
        "subtitle": "Beard Grass",
        "qualities": (
            "The signature native warm-season grass of dry prairies "
            "and oak savannas, growing 2 to 3 feet tall in a "
            "fountain-shaped clump. Blue-green summer foliage shifts "
            "in autumn to the famous copper-and-mahogany tones that "
            "define Minnesota prairie color through October. "
            "Feathery silver seedheads catch backlighting from late "
            "summer through winter — among the best sources of "
            "structural light in any native garden."
        ),
        "care": (
            "Full sun, well-drained soil; sand to loam. "
            "Drought-tolerant once established. Deer- and "
            "rabbit-resistant. Hardy to USDA Zone 3. Plant from "
            "1-gallon container 18 to 24 inches apart for a meadow "
            "matrix; closer for a tighter ribbon. Leave standing "
            "through winter — the structure is the point. Cut to "
            "6 inches in late February or March before new growth."
        ),
        "history": (
            "Little bluestem co-dominated the tallgrass prairie with "
            "Big Bluestem (*Andropogon gerardii*) — together they "
            "formed the iconic 6-foot grass sea of pre-settlement "
            "Minnesota. The deep root systems (down to 6 feet) built "
            "the legendary prairie soils that drew settlers and "
            "destroyed the prairies in equal measure. Today, less "
            "than 2% of Minnesota's tallgrass prairie remains. Each "
            "residential planting of little bluestem is a small act "
            "of restoration."
        ),
        "reason": (
            "Little bluestem is the structural connective tissue of "
            "a savanna-style residential bed. Planted in repeated "
            "drifts, it weaves between forb mass and unifies the "
            "composition. It provides cover for ground-nesting "
            "native bees and small birds; its seedheads feed "
            "sparrows in winter. It hosts the larvae of many native "
            "butterflies and skippers. And in November when every "
            "forb has gone brown, the copper bluestem still glows "
            "like an ember through the snow."
        ),
    },
    "prairie-dropseed": {
        "common": "Prairie Dropseed",
        "scientific": "Sporobolus heterolepis",
        "family": "Poaceae",
        "subtitle": "Northern Prairie Dropseed",
        "qualities": (
            "A fine-textured warm-season bunchgrass forming a "
            "graceful arching mound 2 to 3 feet tall and equally "
            "wide. Hair-thin medium-green leaves give it the "
            "softest texture of any prairie grass. Airy panicles of "
            "tiny seeds appear in August, releasing a mild "
            "buttered-popcorn or coriander fragrance that surprises "
            "first-time visitors. Foliage turns golden bronze in "
            "fall."
        ),
        "care": (
            "Full sun is essential; tolerates almost any soil "
            "including clay. Drought-tolerant once established but "
            "appreciates occasional summer water. Hardy to USDA Zone 3. "
            "Slow to establish (3-year root development); plant from "
            "1-gallon stock for fastest results. Long-lived once "
            "settled — an undisturbed clump can persist for decades. "
            "Cut to 6 inches in late winter."
        ),
        "history": (
            "Prairie dropseed was a co-dominant grass of the "
            "drier-mesic prairies of southern Minnesota and was a "
            "Dakota food plant — the seeds, parched and ground, were "
            "used as flour. Following the conversion of prairies to "
            "agriculture, dropseed retreated to remnant sites; it is "
            "now a flagship indicator species for prairie restoration "
            "quality. Its slow establishment and refusal to "
            "transplant easily make it a marker of patient gardeners "
            "and undisturbed soil."
        ),
        "reason": (
            "Prairie dropseed is the front-edge grass of choice for "
            "any bed that meets a path or a lawn. Its fountain form "
            "softens edges; its fine texture contrasts beautifully "
            "with broad-leaved forbs; and the late-summer popcorn "
            "scent is one of the small joys of native gardening that "
            "no garden-design book ever mentions. Native bees and "
            "skippers use the foliage; goldfinches harvest the seed."
        ),
    },
    "blue-flag-iris": {
        "common": "Blue Flag Iris",
        "scientific": "Iris versicolor",
        "family": "Iridaceae",
        "subtitle": "Northern Blue Flag · Larger Blue Flag",
        "qualities": (
            "A bold wetland iris 2 to 3 feet tall, with sword-shaped "
            "blue-green leaves rising from spreading rhizomes. In "
            "late May and June it produces large violet-blue flowers "
            "with bright yellow signal patches and dramatic dark "
            "veining on each falling petal — the classic iris form, "
            "scaled up. Forms colonies in damp soil over time. "
            "Rhizomes are toxic if eaten; do not confuse with edible "
            "Sweet Flag (*Acorus calamus*)."
        ),
        "care": (
            "Best in moist to wet soil; thrives at the edge of a "
            "rain garden, vegetated swale, or pond. Tolerates "
            "average garden soil if watered. Full sun to part shade. "
            "Hardy to USDA Zone 3. Plant from 1-gallon stock or bare-"
            "root rhizome in spring or fall. Divide every 4-5 years "
            "to maintain vigor. Slugs occasionally chew young leaves; "
            "rarely a serious issue."
        ),
        "history": (
            "Blue flag was widely used among Indigenous peoples of "
            "the Great Lakes region, including the Ojibwe and "
            "Anishinaabe, as a powerful medicinal — but specifically "
            "for external use; the rhizomes contain compounds that "
            "are emetic and dermatologically active. The plant "
            "appears in ceremonial contexts in some Algonquian "
            "traditions. The name *versicolor* (\"various-colored\") "
            "refers to the elaborate yellow-and-purple signal "
            "patterning on the falls."
        ),
        "reason": (
            "Blue flag iris is the visual anchor of a vegetated "
            "bioswale or rain garden. Its bold form and "
            "early-summer bloom announce the wet zone of a "
            "composition. Bumblebees and skipper butterflies work "
            "the flowers; the seed pods provide late-season "
            "structural interest. In a residential swale conversion "
            "(rock to vegetated), three or five clumps of Blue Flag "
            "elevate the channel from \"grass meadow\" to \"designed "
            "wet garden\" without losing any of the ecological "
            "function."
        ),
    },
    "tussock-sedge": {
        "common": "Tussock Sedge",
        "scientific": "Carex stricta",
        "family": "Cyperaceae",
        "subtitle": "Upright Sedge",
        "qualities": (
            "A robust clumping sedge of fens, sedge meadows, and "
            "vegetated bioswales, forming distinct elevated "
            "\"tussocks\" 1 to 3 feet tall. Bright green narrow "
            "blades arch outward from a tightly clumped base; the "
            "tussock structure literally raises the plant slightly "
            "above the wet ground around it. Inconspicuous spring "
            "spikelets ripen to brown by midsummer. The fibrous root "
            "mat is the species' superpower — it armors flow paths "
            "in a way no other plant matches."
        ),
        "care": (
            "Plant from plug stock at 9 to 12 inches spacing in wet "
            "or moist soil — the closer spacing matters because the "
            "purpose is rapid canopy closure to outcompete weeds and "
            "armor against erosion. Tolerates seasonal flooding; "
            "tolerates partial drying once established. Full sun to "
            "part shade. Hardy to USDA Zone 3. No maintenance "
            "needed; can be selectively burned in a controlled "
            "spring burn."
        ),
        "history": (
            "Carex stricta was a dominant species of Minnesota's "
            "pre-settlement sedge meadows, which historically "
            "covered substantial acreage in poorly-drained "
            "lowlands across the state. Most sedge meadow has been "
            "tiled and converted to agriculture. The sedge meadow "
            "is one of the great \"missing\" Minnesota habitats — "
            "and tussock sedge is its keystone species. Each "
            "vegetated bioswale planted with *Carex stricta* is a "
            "small fragment of restored sedge meadow."
        ),
        "reason": (
            "Tussock sedge is the structural species of a vegetated "
            "bioswale — the species that physically holds soil "
            "against stormwater flow with its dense fibrous root "
            "mat. Without sedge, a swale is just lawn or ditch; "
            "with sedge, it is a functioning piece of green "
            "stormwater infrastructure. The tussock form provides "
            "habitat for amphibians, ground-nesting birds, and "
            "specialist insects. As a substitute for a rock dry-"
            "creek it is an order of magnitude more ecologically "
            "valuable, and (after year 1) more visually beautiful."
        ),
    },
    "cardinal-flower": {
        "common": "Cardinal Flower",
        "scientific": "Lobelia cardinalis",
        "family": "Campanulaceae",
        "subtitle": "Red Lobelia",
        "qualities": (
            "An upright wetland perennial 2 to 4 feet tall, with "
            "narrow lance-shaped leaves and a vertical spike of "
            "vivid scarlet two-lipped flowers from August into "
            "September. The red is so saturated it is almost "
            "shocking against late-summer prairie greens — the "
            "single most striking flower color in the Minnesota "
            "native flora. Short-lived (3-5 year) but reliably "
            "self-seeds in suitable conditions."
        ),
        "care": (
            "Moist to wet soil; the wetter the better. Full sun to "
            "part shade. Hardy to USDA Zone 3. Plant from 1-gallon "
            "stock in spring or fall; do not let the root ball dry "
            "out during establishment. Mulch lightly in fall to "
            "protect the basal rosette through winter. Allow "
            "self-seeding in compatible spots; replace as the "
            "original parent plants decline. Deer-resistant."
        ),
        "history": (
            "Named for its resemblance to a Cardinal's red robe, the "
            "plant has been cultivated since the 1620s. Indigenous "
            "peoples used the root for love medicine and for "
            "respiratory illness, though the alkaloids are toxic "
            "and the plant requires careful handling. Cardinal "
            "Flower appears in Audubon's earliest American botanical "
            "watercolors (1820s) — it has long been recognized as "
            "one of the most beautiful native plants of eastern "
            "North America."
        ),
        "reason": (
            "Cardinal flower is *the* hummingbird plant. The Ruby-"
            "throated Hummingbird is its primary pollinator — the "
            "narrow tubular red flower is an evolutionary "
            "co-adaptation. In late August and September, when "
            "hummingbirds are migrating south and need high-energy "
            "nectar, a stand of cardinal flower is a refueling "
            "station. The vivid red also draws Eastern Tiger and "
            "Spicebush Swallowtails. In a vegetated bioswale, "
            "cardinal flower transforms the moist slope from "
            "\"green stormwater function\" to \"emotional anchor.\""
        ),
    },
    "swamp-milkweed": {
        "common": "Swamp Milkweed",
        "scientific": "Asclepias incarnata",
        "family": "Apocynaceae",
        "subtitle": "Pink Milkweed · Rose Milkweed",
        "qualities": (
            "An upright clumping milkweed 3 to 4 feet tall, with "
            "narrow lance-shaped leaves and rounded clusters of "
            "small mauve-pink star-shaped flowers from July through "
            "August. Unlike Common Milkweed it does not spread by "
            "rhizomes — it forms a tidy clump that holds its place "
            "indefinitely. Spindle-shaped pods split in fall to "
            "release the iconic silk-tufted milkweed seeds."
        ),
        "care": (
            "Best in moist to wet soil; tolerates average garden "
            "soil if watered. Full sun. Hardy to USDA Zone 3. Plant "
            "from 1-gallon stock; like all milkweeds, slow to "
            "emerge in spring (mark the location). Long-lived once "
            "established; clumps remain in place rather than "
            "spreading. Deer-resistant. The flowers attract "
            "considerable pollinator traffic — site near a "
            "viewing area."
        ),
        "history": (
            "All North American milkweeds were used variously by "
            "Indigenous peoples — the silky seed floss as fiber "
            "(stuffed into life jackets during WWII when imported "
            "kapok was unavailable), the flower buds and very young "
            "shoots as cooked food, the latex sap as a wound "
            "dressing. Swamp milkweed specifically appears in "
            "Anishinaabe and Dakota wetland-edge plant lists. The "
            "common name is misleading — it grows fine in average "
            "garden soil so long as moisture is reliable."
        ),
        "reason": (
            "Swamp milkweed is the second of three primary "
            "Monarch host plants. Where Butterfly Milkweed offers "
            "drought-tolerant prairie habitat and Common Milkweed "
            "offers spreading colonies, Swamp Milkweed offers a "
            "well-behaved clumping habit perfect for residential "
            "design. Female Monarchs lay eggs on swamp milkweed "
            "throughout July and August; the leaves are the "
            "exclusive food of the caterpillars. In a vegetated "
            "bioswale's moist slope, three Swamp Milkweed clumps "
            "make the swale a Monarch nursery."
        ),
    },
}


# ============================================================
# Page layout
# ============================================================

PAGE_W, PAGE_H = letter
MARGIN = 0.75 * inch

C_INK = HexColor("#1f2a1a")
C_TITLE = HexColor("#2a4a25")
C_ACCENT = HexColor("#5d3a1f")
C_RULE = HexColor("#aea580")
C_PAPER = HexColor("#fcf9f0")
C_MUTED = HexColor("#5e5544")

F_SERIF = "Times-Roman"
F_SERIF_B = "Times-Bold"
F_SERIF_I = "Times-Italic"
F_SANS = "Helvetica"
F_SANS_B = "Helvetica-Bold"


def load_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("GEMINI_API_KEY not found")


def illustration_prompt(species: dict) -> str:
    return (
        f"A vintage scientific botanical illustration of {species['common']} "
        f"({species['scientific']}), in the unmistakable style of Curtis's "
        f"Botanical Magazine — late 18th to early 19th century plate, "
        f"hand-painted in watercolor on aged ivory paper. "
        f"Composed plate showing several plant elements arranged on the "
        f"page: the full habit (or a flowering branch in flower), a "
        f"close-up of one open flower with stamens and pistil clearly "
        f"visible, a leaf detail with prominent venation, and a fruit or "
        f"seed structure where appropriate. "
        f"Fine ink-line drawing under transparent watercolor washes. "
        f"Naturalistic accuracy in form, color, and proportion. "
        f"Soft warm muted colors — sage greens, ivory, dusky tones. "
        f"Subtle aged background with very faint sepia spots, like an "
        f"antique scientific journal page. The Latin name "
        f"\"{species['scientific']}\" written in delicate ornate handwritten "
        f"script along the bottom of the plate. "
        f"Portrait orientation. Strictly illustrative — no photography, "
        f"no modern elements, no text other than the Latin name. "
        f"Clean off-white margins."
    )


def generate_illustration(slug: str, species: dict, force: bool = False) -> Path:
    out = ILLUSTRATIONS / f"{slug}.png"
    if out.exists() and not force:
        print(f"  ↺ {slug} (cached)")
        return out

    from google import genai
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)

    model_id = os.environ.get("GEMINI_IMAGE_MODEL",
                              "gemini-3-pro-image-preview")
    print(f"  → {slug}: calling {model_id} ...")

    response = client.models.generate_content(
        model=model_id,
        contents=[illustration_prompt(species)],
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            img = PILImage.open(io.BytesIO(part.inline_data.data))
            img.save(out)
            # Also drop into the textbook
            if TEXTBOOK_PLANTS_IMG.exists():
                copy_to = TEXTBOOK_PLANTS_IMG / f"{slug}-illustration.png"
                img.save(copy_to)
            print(f"  ✓ {out}")
            return out
    raise RuntimeError(f"no image data in response for {slug}")


def render_profile_pdf(slug: str, species: dict,
                       illustration_path: Path) -> Path:
    out = PROFILES / f"{slug}.pdf"
    c = rl_canvas.Canvas(str(out), pagesize=letter)
    c.setTitle(f"{species['common']} — Plant Profile")

    # paper
    c.setFillColor(C_PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # ---- top: family + scientific (small kicker) ----
    c.setFillColor(C_ACCENT)
    c.setFont(F_SANS_B, 9)
    c.drawString(MARGIN, PAGE_H - MARGIN + 0.05 * inch,
                 species["family"].upper())

    # ---- title ----
    c.setFillColor(C_TITLE)
    c.setFont(F_SERIF_B, 30)
    c.drawString(MARGIN, PAGE_H - MARGIN - 0.4 * inch, species["common"])

    c.setFillColor(C_INK)
    c.setFont(F_SERIF_I, 16)
    c.drawString(MARGIN, PAGE_H - MARGIN - 0.7 * inch,
                 species["scientific"])

    if species.get("subtitle"):
        c.setFillColor(C_MUTED)
        c.setFont(F_SERIF, 11)
        c.drawString(MARGIN, PAGE_H - MARGIN - 0.95 * inch,
                     species["subtitle"])

    # rule
    c.setStrokeColor(C_RULE)
    c.setLineWidth(0.8)
    c.line(MARGIN, PAGE_H - MARGIN - 1.1 * inch,
           PAGE_W - MARGIN, PAGE_H - MARGIN - 1.1 * inch)

    # ---- illustration block ----
    img_top = PAGE_H - MARGIN - 1.3 * inch
    img_h = 3.4 * inch  # tighter so text doesn't run into footer
    img_w = PAGE_W - 2 * MARGIN

    if illustration_path and illustration_path.exists():
        img = PILImage.open(illustration_path)
        iw, ih = img.size
        aspect = iw / ih
        if aspect > img_w / img_h:
            draw_w = img_w
            draw_h = img_w / aspect
        else:
            draw_h = img_h
            draw_w = img_h * aspect
        draw_x = MARGIN + (img_w - draw_w) / 2
        draw_y = img_top - img_h + (img_h - draw_h) / 2
        c.drawImage(str(illustration_path), draw_x, draw_y,
                    width=draw_w, height=draw_h,
                    preserveAspectRatio=True, mask="auto")

    text_top = img_top - img_h - 0.2 * inch

    # ---- four prose sections ----
    sections = [
        ("Qualities", species["qualities"]),
        ("Care",      species["care"]),
        ("History",   species["history"]),
        ("Reason to be", species["reason"]),
    ]

    cur_y = text_top
    body_w = PAGE_W - 2 * MARGIN

    for label, text in sections:
        # header
        c.setFillColor(C_ACCENT)
        c.setFont(F_SANS_B, 9)
        c.drawString(MARGIN, cur_y, label.upper())
        cur_y -= 0.15 * inch

        # body
        c.setFillColor(C_INK)
        c.setFont(F_SERIF, 10)
        cur_y = _wrap_paragraph(c, text, MARGIN, cur_y, body_w,
                                F_SERIF, 10, leading=12.5)
        cur_y -= 0.13 * inch

    # footer
    c.setFillColor(C_MUTED)
    c.setFont(F_SANS, 7.5)
    c.drawString(MARGIN, MARGIN - 0.3 * inch,
                 f"Front-Yard Oak Savanna Edge  ·  "
                 f"Plant Profile  ·  {species['common']}")
    c.drawRightString(PAGE_W - MARGIN, MARGIN - 0.3 * inch,
                      "Curtis-style botanical illustration "
                      "generated by Gemini 3 Pro Image")

    c.showPage()
    c.save()
    return out


def _wrap_paragraph(c, text: str, x: float, y: float, w: float,
                    font: str, size: float, leading: float) -> float:
    """Word-wrap paragraph with a no-widow rule: if the last line would
    contain only 1-2 short words, pull a word from the previous line down
    so the final line is at least three words long."""
    c.setFont(font, size)
    words = text.split()
    # build lines greedily
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if c.stringWidth(trial, font, size) <= w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)

    # widow control: if the last line has 1-2 short words and there's a
    # prior line we can pull from, rebalance.
    if len(lines) >= 2:
        last_words = lines[-1].split()
        last_line_len = c.stringWidth(lines[-1], font, size)
        # widow = last line is short AND last "thought" is small
        if len(last_words) <= 2 and last_line_len < w * 0.35:
            prev_words = lines[-2].split()
            if len(prev_words) > 3:
                # pull last word of prev line into the orphan line
                pulled = prev_words[-1]
                lines[-2] = " ".join(prev_words[:-1])
                lines[-1] = pulled + " " + lines[-1]

    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def bundle_all() -> Path:
    """Concatenate every per-species PDF into one bundle."""
    from pypdf import PdfWriter, PdfReader
    out = ROOT / "plant-profiles.pdf"
    writer = PdfWriter()
    for slug in SPECIES:
        p = PROFILES / f"{slug}.pdf"
        if p.exists():
            for page in PdfReader(str(p)).pages:
                writer.add_page(page)
    with open(out, "wb") as f:
        writer.write(f)
    print(f"bundle: {out}")
    return out


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("targets", nargs="*",
                        help="species slugs to process")
    parser.add_argument("--all", action="store_true",
                        help="process every species in SPECIES")
    parser.add_argument("--bundle", action="store_true",
                        help="combine existing per-species PDFs")
    parser.add_argument("--force", action="store_true",
                        help="regenerate illustrations even if cached")
    args = parser.parse_args()

    if args.bundle:
        bundle_all()
        sys.exit(0)

    targets = list(SPECIES.keys()) if args.all else args.targets
    if not targets:
        parser.print_help()
        sys.exit(1)

    for slug in targets:
        if slug not in SPECIES:
            print(f"  ✗ unknown species slug: {slug}")
            print(f"    available: {', '.join(SPECIES.keys())}")
            continue
        print(f"\n=== {slug} ===")
        try:
            illustration = generate_illustration(slug, SPECIES[slug],
                                                 force=args.force)
            pdf = render_profile_pdf(slug, SPECIES[slug], illustration)
            print(f"  ✓ {pdf}")
        except Exception as e:
            print(f"  ✗ {slug}: {e}")
