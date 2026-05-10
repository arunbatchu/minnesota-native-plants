"""
Photorealistic renderings via Gemini 2.5 Flash Image (Nano Banana 2).

Takes the head-on photo of the existing front bed and edits it to show:
  - year-1 (just-planted) look
  - year-3 (established, summer-peak bloom)
  - year-5 (mature, fully filled-in)
  - bench-pocket vignette (close-up immersive view)

Reads GEMINI_API_KEY from environment, then from .env (gitignored).

Usage:
    python3 render.py                 # all four renderings
    python3 render.py year3           # just the year-3 hero
    python3 render.py vignette        # just the bench close-up
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
PHOTOS = ROOT / "photos"
OUT = ROOT / "annotated"
OUT.mkdir(exist_ok=True)


def load_api_key() -> str:
    """Get the Gemini API key from env, then .env, with a clear error."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")

    raise RuntimeError(
        "GEMINI_API_KEY not found.\n"
        "Set it in the shell:  export GEMINI_API_KEY=...\n"
        f"or paste it into:    {env_file}\n"
        "as a single line:     GEMINI_API_KEY=your_key_here\n"
        "(.env is gitignored.)"
    )


# --------------------------------------------------------------------
# Prompt set — each is carefully scoped to preserve scene fidelity
# --------------------------------------------------------------------

COMMON_CONTEXT = """\
This is a south-facing front yard in Eden Prairie, Minnesota (USDA zone 4b/5a).
The house is tan stucco with a wood-shake roof, a centered bay window, and \
stone quoins. The existing landscape is a row of overgrown leggy mugo pines \
running along the foundation under the bay window, with patches of white \
river-rock visible at the right edge near a downspout.

I am replacing the mugo pines with a Minnesota-native Oak Savanna Edge \
planting. Please keep the house, sky, lawn, and overall photo \
composition exactly the same — only edit the planting bed area in front of \
the bay window. Do not change the camera angle. Do not add buildings or \
fences. Keep the bird feeder shepherd's hooks visible on the left.

CRITICAL — DO NOT add any of these (they are not in the design):
  - No sidewalk, walkway, or concrete strip across the foreground
  - No paving stones, flagstone patio, or pavement of any kind in the
    foreground or front of the planting bed
  - No driveway, curb, or street visible in the front of the lawn
  - No decorative rocks, gravel mulch, or stone borders in the bed
The transition is simple: existing lawn meets the new planting bed
directly with a soft trench-cut edge. Foreground is grass lawn only.
"""

PROMPTS = {
    "year3": COMMON_CONTEXT + """
Replace the mugo pines and the visible white river rock with a mature \
year-3 Minnesota Oak Savanna Edge planting in mid-July at peak bloom:

  - WEST end (left of frame): a young Serviceberry tree about 8 feet tall \
    with a slim multi-stem form, light green oval leaves, no flowers (it \
    bloomed in April). Behind it, a small mounding Gray Dogwood shrub.
  - FLANKING the bay window: two low Ninebark shrubs, pruned to about 30 \
    inches tall so they do not block the bay window. Small white flower \
    clusters.
  - MID-DRIFT in front of the bay window (kept under 30 inches mature \
    height for indoor sightline): drifts of Wild Bergamot (lavender-pink \
    pom-pom flowers, ~3 ft), Purple Coneflower (purple drooping rays, \
    yellow-orange centers, ~2.5 ft), and Butterfly Milkweed (vivid \
    orange umbel clusters, ~1.5 ft).
  - LOW EDGE: a continuous ribbon of Little Bluestem grass tufts \
    (blue-green summer color, 2 ft) and Prairie Smoke groundcover.
  - At the RIGHT side, where the white river-rock is now: a \
    fully-vegetated bioswale — a meadow of native sedges (Tussock Sedge \
    bright green tussocks, Fox Sedge), with Blue Flag Iris (deep blue) \
    and Cardinal Flower (red) at the wet center. NO ROCK should be visible.

Time of day: late morning, gentle warm light, soft cumulus clouds. \
Subtle pollinators (bees, a Monarch butterfly) on the bergamot or \
coneflower add life but do not dominate. Photographic, not illustrative. \
Sharp focus throughout. The garden should look established but \
intentional — clear drifts of repeated species, not a chaotic wildflower \
mix.
""",

    "year1": COMMON_CONTEXT + """
Show the same Minnesota Oak Savanna Edge planting in late summer of \
year ONE — just installed three months ago:

  - All plants visibly small. Visible bare soil and shredded hardwood \
    mulch BETWEEN plants. Plants drawn as 1-quart and 1-gallon container \
    sizes: forbs about 8-12 inches tall and 8 inches wide, grasses small \
    tufts.
  - Serviceberry on the west end is a 6-foot stick-shaped tree, not yet \
    leafed-out fully.
  - Ninebark shrubs are short, about 18 inches tall, recently planted.
  - The vegetated swale on the right has small sedge plugs spaced about \
    9 inches apart, with bare soil visible between them. A biodegradable \
    jute erosion-control blanket lies over the swale channel center.
  - A few flowers visible (some Wild Bergamot, some Coneflower) but most \
    plants are just foliage. NO ROCK in the swale area.

Time of day: late morning. Plant tags on plastic stakes still visible \
on a few specimens. The look is honest — clearly "just planted," not \
yet established. This sets expectations for the homeowner.
""",

    "year5": COMMON_CONTEXT + """
Show the same Minnesota Oak Savanna Edge planting in mid-August of \
year FIVE — fully matured:

  - The Serviceberry on the west end is now 15 feet tall with a full \
    multi-stem rounded canopy.
  - The Ninebarks have been allowed to grow to 5 feet tall (still \
    pruned away from the window) with arching branches and exfoliating \
    cinnamon-brown bark visible.
  - The forb drifts have fully knit together — no bare soil visible \
    anywhere. Drifts overlap at edges. Self-sown Black-eyed Susan and \
    extra Coneflower have appeared in gaps.
  - Little Bluestem and Prairie Dropseed are full-sized billowing \
    fountain forms, golden-tipped.
  - The vegetated swale is a dense sedge meadow with Cardinal Flower \
    spikes in red August bloom.
  - A few specimens are visibly aging gracefully — some lupines have \
    died out and been replaced by self-seeded Coneflower; this is normal \
    succession.

Time of day: late afternoon, warm side light. Goldfinches on the \
coneflower seedheads. The look is "wild and intentional" — clearly \
designed but no longer maintained-looking.
""",

    "vignette": """\
A close-up landscape photograph from inside a Minnesota oak savanna \
front-yard garden in mid-July at peak bloom. The viewer is sitting on a \
weathered cedar bench tucked into a small clearing in the planting. \
Behind the bench, a young Serviceberry tree with light-green leaves \
provides dappled afternoon shade. To either side, drifts of Wild \
Bergamot (lavender-pink pom-pom flowers ~3 ft tall) and Purple \
Coneflower (purple drooping rays with yellow-orange centers) bloom at \
shoulder height. In the foreground, a tuft of Little Bluestem grass \
blue-green in summer color; a path of natural-cut limestone steppers \
emerges from the right. A Monarch butterfly rests on a nearby Butterfly \
Milkweed (vivid orange umbel). Soft warm afternoon light filters \
through the serviceberry leaves. Bees hum among the bergamot. Tan \
stucco wall of a house visible far behind the planting. Photographic, \
high detail, naturalistic light, intimate scale, gentle. The feel is \
"sit here for an hour with a coffee and watch the prairie work."

Aspect ratio: landscape, like a magazine spread.
""",
}


PROMPTS["year3_spring"] = COMMON_CONTEXT + """
Replace the mugo pines and the visible white river rock with a year-3 \
Minnesota Oak Savanna Edge planting in MID-MAY (spring bloom moment):

  - WEST end (left of frame): a young Serviceberry tree about 8 feet \
    tall with light green oval leaves, a few late white flower clusters \
    fading.
  - FLANKING the bay window: two compact Ninebark shrubs about 30 inches \
    tall with chartreuse-green spring foliage, flower buds not yet open.
  - MID-DRIFT in front of the bay window: drifts of Wild Lupine \
    (vertical violet-blue racemes about 18 inches tall — the iconic spring \
    moment), False Blue Indigo just emerging with deep-blue spires, \
    and Prairie Smoke as a low groundcover with dusty-pink nodding \
    flowers and feathery seedheads in front.
  - LOW EDGE: short tufts of Little Bluestem in fresh blue-green spring \
    color, not yet at full size.
  - At the RIGHT side, where the white river-rock is now: a vegetated \
    bioswale showing fresh sedge growth, with Blue Flag Iris in deep \
    blue flower at the wet center. NO ROCK should be visible.

Time of day: late morning, soft cool spring light, scattered cumulus, \
fresh saturated greens. The garden should look fully alive but not yet \
at peak — the spring wave. Preserve the bird-feeder shepherd's hooks \
visible on the LEFT in the original photo.
"""

PROMPTS["year3_with_bench"] = COMMON_CONTEXT + """
Replace the mugo pines and the visible white river rock with a year-3 \
Minnesota Oak Savanna Edge planting in mid-July at peak bloom, \
emphasizing the BENCH POCKET in the WEST third of the bed:

  - WEST third (LEFT of bay window): a young Serviceberry tree about 8 \
    feet tall casting dappled afternoon shade over a weathered-cedar \
    BENCH set in a small pea-gravel pad about 5 feet wide, oriented to \
    face EAST (back toward the front yard). The bench is partially \
    nested into the planting, surrounded on three sides by tall prairie \
    forbs. The pea-gravel pad is barely visible — it's just under the \
    bench, not extending into the lawn.
  - Behind the bench: drifts of Wild Bergamot (lavender-pink pom-poms) \
    and a few Cardinal Flower spikes in red.
  - In front of the bay window: low Ninebarks pruned about 30 inches \
    tall, drifts of Purple Coneflower and Butterfly Milkweed (orange).
  - Three or four small natural-cut limestone STEPPING STONES (not a \
    paved path, not flagstone patio — just spaced individual stones \
    set into the lawn or planting), forming a gentle suggestion of a \
    path from the right edge of the bed to the bench. The stones are \
    embedded in the planting and grass — they should not look like \
    a continuous walk.
  - At the RIGHT side: vegetated bioswale with sedges and Blue Flag \
    Iris. NO ROCK.
  - FOREGROUND: just lawn. No sidewalk, no concrete, no paving.

Time of day: late afternoon, warm golden side light. Preserve the \
bird-feeder shepherd's hooks. Photographic, naturalistic, the bench \
should look INVITING — like you'd sit there with coffee for an hour.
"""

SOURCE_PHOTO = {
    "year3": PHOTOS / "01-front-existing.jpg",
    "year1": PHOTOS / "01-front-existing.jpg",
    "year5": PHOTOS / "01-front-existing.jpg",
    "year3_spring": PHOTOS / "01-front-existing.jpg",
    "year3_with_bench": PHOTOS / "01-front-existing.jpg",
    "vignette": None,  # generated from prompt only, no source image
}


# --------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------

def render(name: str, prompt: str, source: Path | None) -> Path:
    from google import genai

    api_key = load_api_key()
    client = genai.Client(api_key=api_key)

    contents: list = [prompt]
    if source is not None and source.exists():
        contents.append(Image.open(source))

    model_id = os.environ.get("GEMINI_IMAGE_MODEL",
                               "gemini-3-pro-image-preview")
    print(f"  → calling {model_id} "
          f"({'edit' if source else 'gen'})...")

    response = client.models.generate_content(
        model=model_id,
        contents=contents,
    )

    out_path = OUT / f"render-{name}.png"

    saved = False
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            data = part.inline_data.data
            # data is bytes
            img = Image.open(io.BytesIO(data))
            img.save(out_path)
            saved = True
            break

    if not saved:
        # Maybe it returned text instead of image — surface that
        for part in response.candidates[0].content.parts:
            if part.text:
                print(f"  ! model returned TEXT instead of image:\n"
                      f"    {part.text[:300]}")
        raise RuntimeError(
            f"No image data in response for {name}. "
            "Check the model name or rate limit."
        )

    print(f"  ✓ {out_path}")
    return out_path


# --------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------

if __name__ == "__main__":
    targets = sys.argv[1:] or list(PROMPTS.keys())
    for name in targets:
        if name not in PROMPTS:
            print(f"unknown render target: {name}. "
                  f"choices: {', '.join(PROMPTS.keys())}")
            continue
        try:
            render(name, PROMPTS[name], SOURCE_PHOTO[name])
        except Exception as e:
            print(f"  ✗ {name}: {e}")
