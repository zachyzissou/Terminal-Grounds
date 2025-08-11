# tools_try_sd_client.py
# Optional Stable Diffusion/ComfyUI client; always writes prompt packs.

import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
PK_DIR = ROOT / "Tools/ArtGen/prompt_packs"
OUT_DIR = ROOT / "Tools/ArtGen/outputs"
DOC_DIR = ROOT / "Docs/Concepts/AI"
PK_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)
DOC_DIR.mkdir(parents=True, exist_ok=True)

PACKS = {
    "Weapons": {
        "positive": "tactical sci-fi weapon, grounded industrial realism, hybrid tech accents, high detail",
        "negative": "lowres, blurry, watermark",
        "camera": "35mm lens, 3/4 view",
        "lighting": "studio softbox",
        "color": "neutral military palette",
        "style": "industrial documentary",
        "seed": 12345
    },
    "Vehicles": {
        "positive": "dieselpunk convoy truck, salvage add-ons, hybrid coils, realistic",
        "negative": "cartoon, anime",
        "camera": "24mm lens, low angle",
        "lighting": "golden hour",
        "color": "earth tones",
        "style": "photojournalistic",
        "seed": 12345
    },
}


def write_packs():
    for name, data in PACKS.items():
        (PK_DIR / f"{name}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def try_automatic1111():
    try:
        urllib.request.urlopen("http://127.0.0.1:7860/sdapi/v1/sd-models", timeout=1)
        return True
    except Exception:
        return False


def main():
    write_packs()
    if try_automatic1111():
        # Placeholder: would post to txt2img and save results
        (OUT_DIR / "note.txt").write_text("Generated via local SD placeholder", encoding="utf-8")
        # Copy to docs
        (DOC_DIR / "note.txt").write_text("Images generated (placeholder)", encoding="utf-8")
    else:
        print("No generator detected; prompts ready.")
    # Log
    log = ROOT / "Docs/Phase4_Implementation_Log.md"
    from datetime import date
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n[{date.today().isoformat()}] Created: prompt packs in Tools/ArtGen/prompt_packs; outputs updated if generator available\n")

if __name__ == "__main__":
    main()
