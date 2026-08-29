#!/usr/bin/env python3
"""Generate Bree's mascot poses via OpenAI gpt-image-2.

Bree is a rusty-patched bumble bee (Bombus affinis), Minnesota's state bee.
The canonical description lives in docs/img/mascot/character-sheet.md and the
human-readable prompts in docs/img/mascot/image-prompts.md — this script is
the machine-runnable copy of the same thing. Change one, change all three.

She was a European honeybee until August 2026. Never redraw her as one:
Chapter 6 says honeybees are not native to North America, so an Apis mellifera
mascot contradicts the book it is guiding.

Usage:
    python3 scripts/generate-mascot.py                  # all poses
    python3 scripts/generate-mascot.py welcome tip      # just these
    python3 scripts/generate-mascot.py --out-dir /tmp/x # somewhere else

The API key is read from the shilpiworks env files, the same way
~/adhd/scripts/generate-mascot.py does it.
"""
import base64
import json
import os
import re
import sys
import urllib.request

SW = os.path.expanduser("~/CascadeProjects/shilpiworks")
MODEL = "gpt-image-2"
DEFAULT_OUT = "docs/img/mascot"


def load_key():
    for f in (f"{SW}/backend/.env", f"{SW}/frontend/.env.production.local"):
        if not os.path.exists(f):
            continue
        for line in open(f):
            if line.startswith("OPENAI_API_KEY="):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                v = re.sub(r"\\n$", "", v).strip()   # literal \n guard
                if v:
                    return v
    sys.exit("no OPENAI_API_KEY found in shilpiworks env files")


# The character anchor. Every pose is this text plus one pose clause. Do not
# paraphrase it — the black thoracic spot, the rust patch on abdominal segment
# two, the leaf beret and the watercolor treatment are what make the seven
# images read as one bee rather than seven bees.
BREE = (
    "A friendly watercolor mascot bee named Bree for an educational book about "
    "Minnesota native plants. Bree is a rusty-patched bumble bee (Bombus "
    "affinis) — round, plump and thoroughly fuzzy, not slim like a honeybee. "
    "She has a black head with large warm brown eyes, a yellow furry thorax "
    "marked with a single black spot between the wing bases, and a yellow "
    "abdomen bearing a distinct rust-orange patch across its second segment, "
    "shading to black at the tip. Translucent, faintly iridescent wings. She "
    "wears a tiny green leaf beret and carries one small purple wildflower. "
    "Gentle, kind, calm expression — a warm patient guide, never manic or "
    "zany. Soft watercolor illustration, warm earthy tones, clean edges, "
    "gentle shading, friendly natural-history style. Full body, facing the "
    "viewer. Consistent character design across all images. Isolated on a "
    "fully transparent background, no scene, no ground shadow, no text, no "
    "border, no frame."
)

POSES = {
    "neutral": (
        "Bree standing upright in a relaxed neutral pose with a calm "
        "closed-mouth smile, arms resting naturally at her sides, balanced and "
        "unassuming, centered and symmetrical."
    ),
    "welcome": (
        "Bree waving cheerfully with one arm raised, head tilted slightly, "
        "warm welcoming smile."
    ),
    "thinking": (
        "Bree resting one arm under her chin in a thoughtful pose, a small "
        "glowing lightbulb floating above her leaf beret, curious and "
        "considering."
    ),
    "tip": (
        "Bree pointing gently upward with one arm, a small sparkle at her "
        "fingertip, bright attentive eyes, offering a helpful idea."
    ),
    "warning": (
        "Bree holding up a small round yellow caution sign with a black "
        "exclamation mark, concerned but kind expression — cautionary, never "
        "frightening or scolding."
    ),
    "encouraging": (
        "Bree giving an enthusiastic thumbs-up with one arm, wings lifted "
        "slightly, broad supportive smile, quietly rooting for you."
    ),
    "celebration": (
        "Bree with both arms raised happily above her head, soft confetti and "
        "a few flower petals falling around her, wings spread, delighted but "
        "gentle."
    ),
}


def gen(key, name, pose_text, out_dir):
    body = json.dumps({
        "model": MODEL,
        "prompt": f"{BREE} Pose: {pose_text}",
        "size": "1024x1024",
        "background": "transparent",
        "n": 1,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations", data=body,
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    img = base64.b64decode(d["data"][0]["b64_json"])
    path = os.path.join(out_dir, f"{name}.png")
    with open(path, "wb") as fh:
        fh.write(img)
    print(f"  ok {name}.png  {len(img)//1024}KB")
    return path


def main(argv):
    out_dir = DEFAULT_OUT
    if "--out-dir" in argv:
        i = argv.index("--out-dir")
        out_dir = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]

    wanted = [a for a in argv if not a.startswith("-")] or list(POSES)
    unknown = [w for w in wanted if w not in POSES]
    if unknown:
        sys.exit(f"unknown pose(s): {', '.join(unknown)}\n"
                 f"available: {', '.join(POSES)}")

    os.makedirs(out_dir, exist_ok=True)
    key = load_key()
    print(f"{MODEL} -> {out_dir}  ({len(wanted)} pose(s))")
    failed = []
    for name in wanted:
        try:
            gen(key, name, POSES[name], out_dir)
        except Exception as e:                       # noqa: BLE001
            print(f"  FAIL {name}: {e}", file=sys.stderr)
            failed.append(name)
    if failed:
        print(f"\nfailed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print("\nNow trim the padding:")
    print(f"  python3 $BK_HOME/skills/book-installer/scripts/"
          f"trim-padding-from-image.py {out_dir}/*.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
