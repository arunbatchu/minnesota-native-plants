#!/usr/bin/env python3
"""Generate all 7 Bree the Bee mascot poses using OpenAI GPT Image API."""

import base64
import os
import sys
from openai import OpenAI

client = OpenAI()

BASE = """A soft watercolor illustration of Bree the Bee, a friendly pedagogical mascot
for a Minnesota Native Plants textbook. Bree is a round, cheerful honeybee
with golden-yellow and dark brown stripes, translucent iridescent wings,
and large warm brown eyes. She wears a tiny green leaf beret and carries
a small wildflower in one arm. Bree has a gentle, kind expression.
The character is small and compact, suitable for icon-sized display.
Style: soft watercolor, warm tones, clean edges, transparent background,
suitable for embedding in educational content. No text in image."""

POSES = {
    "neutral.png": f"{BASE} Bree stands upright in a relaxed, neutral pose facing the viewer directly, with a calm and friendly closed-mouth smile. Arms rest naturally at her sides with no specific gesture.",
    "welcome.png": f"{BASE} Bree is waving cheerfully with one arm, facing the viewer with a warm, welcoming expression. The pose suggests welcome and let's get started.",
    "thinking.png": f"{BASE} Bree has one arm on her chin in a thoughtful pose, with a small lightbulb above her head. The pose suggests deep thinking and discovery.",
    "tip.png": f"{BASE} Bree is pointing upward with one arm as if sharing an important tip. Expression is helpful and knowing. A small star or sparkle near the pointing gesture.",
    "warning.png": f"{BASE} Bree holds up both arms in a gentle stop or be careful gesture. Expression is concerned but caring. A small exclamation mark nearby.",
    "encouraging.png": f"{BASE} Bree gives a thumbs up with a reassuring, supportive smile. The pose radiates confidence and you can do it energy.",
    "celebration.png": f"{BASE} Bree is jumping or raising both arms in celebration. Expression is joyful and proud. Small confetti or flower petals falling around her.",
}

output_dir = os.path.dirname(os.path.abspath(__file__))

for filename, prompt in POSES.items():
    out_path = os.path.join(output_dir, filename)
    if os.path.exists(out_path):
        print(f"  skipping {filename} (already exists)")
        continue
    print(f"  generating {filename}...")
    try:
        result = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            response_format="b64_json",
            n=1,
        )
        png_bytes = base64.b64decode(result.data[0].b64_json)
        with open(out_path, "wb") as f:
            f.write(png_bytes)
        print(f"  wrote {filename} ({len(png_bytes):,} bytes)")
    except Exception as e:
        print(f"  ERROR generating {filename}: {e}")

print("Done.")
