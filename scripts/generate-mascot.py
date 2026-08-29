#!/usr/bin/env python3
"""Generate Bree's mascot poses via Gemini 3 Pro Image.

Bree is a rusty-patched bumble bee (Bombus affinis), Minnesota's state bee.
The canonical description lives in docs/img/mascot/character-sheet.md and the
human-readable prompts in docs/img/mascot/image-prompts.md — this script is
the machine-runnable copy of the same thing. If you change one, change all
three.

Usage:
    python3 scripts/generate-mascot.py                 # all poses, skip existing
    python3 scripts/generate-mascot.py --force         # regenerate everything
    python3 scripts/generate-mascot.py --pose welcome  # just one

Requirements:
    pip install google-genai Pillow
    export GEMINI_API_KEY=...
"""
from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

OUT_DIR = Path("docs/img/mascot")
DEFAULT_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")

# The character anchor. Every pose prompt is this text plus one pose clause.
# Do not paraphrase it — the black thoracic spot, the rust patch on abdominal
# segment two, the leaf beret and the watercolor treatment are what make the
# seven images read as one bee.
ANCHOR = (
    "A soft watercolor illustration of Bree, a friendly pedagogical mascot for "
    "a Minnesota Native Plants textbook. Bree is a rusty-patched bumble bee "
    "(Bombus affinis) — round, plump and thoroughly fuzzy, not slim like a "
    "honeybee. She has a black head with large warm brown eyes, a yellow furry "
    "thorax marked with a single black spot between the wings, and a yellow "
    "abdomen bearing a distinct rust-orange patch across its second segment, "
    "shading to black at the tip. Translucent, faintly iridescent wings. She "
    "wears a tiny green leaf beret and carries one small purple wildflower. "
    "Her expression is gentle and kind. The character is small and compact, "
    "suitable for icon-sized display. Style: soft watercolor, warm earthy "
    "tones, clean edges, fully transparent background, suitable for embedding "
    "in educational content. No text anywhere in the image. "
)

POSES = {
    "neutral": (
        "Bree stands upright facing the viewer in a relaxed, neutral pose with "
        "a calm closed-mouth smile. Arms rest naturally at her sides. The pose "
        "is balanced and unassuming, centered and symmetrical — the site logo "
        "and favicon are cut from this image."
    ),
    "welcome": (
        "Bree waves cheerfully with one arm raised, facing the viewer with a "
        "warm, welcoming expression. The pose says 'come in, let's get started.'"
    ),
    "thinking": (
        "Bree rests one arm under her chin in a thoughtful pose, with a small "
        "glowing lightbulb floating above her leaf beret. The pose suggests a "
        "moment of understanding, not confusion."
    ),
    "tip": (
        "Bree points upward with one arm, a small sparkle at her fingertip, "
        "with a bright helpful expression. The pose says 'here's something "
        "useful.'"
    ),
    "warning": (
        "Bree holds up a small round yellow caution sign bearing a black "
        "exclamation mark. Her expression is concerned but kind — she is "
        "warning, never scolding."
    ),
    "encouraging": (
        "Bree gives an enthusiastic thumbs-up with one arm, wings lifted "
        "slightly, wearing a broad supportive smile. The pose says 'you've got "
        "this' for genuinely hard material."
    ),
    "celebration": (
        "Bree raises both arms in celebration with soft confetti and a few "
        "flower petals falling around her, wings spread, beaming. The pose "
        "marks finishing something."
    ),
}


def load_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip().startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.stderr.write(
        "ERROR: GEMINI_API_KEY not set.\n"
        "  Get a key at https://aistudio.google.com/apikey, then:\n"
        "    export GEMINI_API_KEY=...\n"
    )
    sys.exit(2)


def generate(pose: str, clause: str, force: bool, model_id: str) -> bool:
    from google import genai
    from PIL import Image as PILImage

    out_path = OUT_DIR / f"{pose}.png"
    if out_path.exists() and not force:
        print(f"  ↺ {pose} (cached)")
        return True

    client = genai.Client(api_key=load_api_key())
    print(f"  → {pose}: calling {model_id} ...", flush=True)
    response = client.models.generate_content(
        model=model_id, contents=[ANCHOR + clause])

    image_bytes = None
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            image_bytes = part.inline_data.data
            break

    if image_bytes is None:
        for part in response.candidates[0].content.parts:
            if part.text:
                sys.stderr.write(f"  model said: {part.text[:300]}\n")
        sys.stderr.write(f"  ERROR: no image returned for {pose}\n")
        return False

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PILImage.open(io.BytesIO(image_bytes)).save(out_path)
    print(f"  ✓ {out_path}")
    return True


def main() -> int:
    p = argparse.ArgumentParser(description="Generate Bree's mascot poses.")
    p.add_argument("--pose", choices=sorted(POSES), help="Generate just one pose")
    p.add_argument("--force", action="store_true", help="Regenerate existing files")
    p.add_argument("--model", default=DEFAULT_MODEL)
    args = p.parse_args()

    todo = {args.pose: POSES[args.pose]} if args.pose else POSES
    failures = [k for k, v in todo.items()
                if not generate(k, v, args.force, args.model)]
    if failures:
        sys.stderr.write(f"\nFailed: {', '.join(failures)}\n")
        return 1
    print(f"\nDone — {len(todo)} pose(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
