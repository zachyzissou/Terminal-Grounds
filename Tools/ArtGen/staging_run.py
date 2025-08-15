#!/usr/bin/env python3
"""
Terminal Grounds - Staging Runner
Generates atmospheric concept iterations from a batch file using the ComfyUI API.
Builds on the two "keeper" recipes you liked and organizes outputs in Style_Staging.
"""
import argparse
import json
import os
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List

from comfyui_api_client import ComfyUIAPIClient, COMFYUI_OUTPUT
from atmospheric_concept_workflow import create_atmospheric_concept_workflow

ROOT = Path(__file__).resolve().parents[2]
STAGING_ROOT = ROOT / "Style_Staging"
RECENT = STAGING_ROOT / "_Recent_Generations"

STYLE_TAGS = {
    "Clean_SciFi": "clean sci-fi aesthetic, sleek, minimal, polished",
    "Gritty_Realism": "gritty realistic, weathered, photoreal textures",
    "Cyberpunk_Military": "cyberpunk military, neon accents, high-tech, dark urban",
    "Minimal_Tactical": "minimal tactical, functional, subdued colors",
    "Soviet_Retro": "soviet retro, propaganda poster aesthetic, bold red accents",
}

DEFAULT_CONCEPTS = [
    {
        "name": "Metro_Maintenance_Corridor",
        "prompt": "underground metro corridor, single-point perspective, leading lines, vanishing point, industrial lighting fixtures, wet concrete, low haze, atmospheric depth, sharp focus",
        "style": "Clean_SciFi"
    },
    {
        "name": "IEZ_Facility_Interior",
        "prompt": "abandoned industrial facility interior, readable shadows, hazard stripes, cinematic rim light, atmospheric depth, sharp focus",
        "style": "Gritty_Realism"
    }
]

DEFAULT_SEEDS = [94887, 94890]


def load_batch(path: Path):
    if path and path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("concepts", DEFAULT_CONCEPTS), data.get("seeds", DEFAULT_SEEDS)
    return DEFAULT_CONCEPTS, DEFAULT_SEEDS


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def copy_to_folder(filename: str, dest_dir: Path):
    src = COMFYUI_OUTPUT / filename
    if not src.exists():
        return False
    ensure_dir(dest_dir)
    dest = dest_dir / filename
    shutil.copy2(src, dest)
    return True


def main():
    ap = argparse.ArgumentParser(description="Run staging concepts via ComfyUI API")
    ap.add_argument("--batch", type=str, default=str(ROOT / "Tools" / "ArtGen" / "inputs" / "staging_batch.json"), help="Path to batch JSON")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=4.2)
    ap.add_argument("--limit", type=int, default=0, help="Max total images (0 = no limit)")
    ap.add_argument("--dry", action="store_true", help="Print actions without queueing")
    args = ap.parse_args()

    # Load batch
    concepts, seeds = load_batch(Path(args.batch))

    client = ComfyUIAPIClient()
    print("Server:", client.base_url)
    if not client.check_server():
        print("ComfyUI server not reachable.")
        return 2

    total = 0
    for concept in concepts:
        name = concept.get("name", "Concept")
        base_prompt = concept.get("prompt", "")
        style_key = concept.get("style", "")
        style_phrase = STYLE_TAGS.get(style_key, "")

        # Build full prompt blending your keeper recipe
        positive = f"Terminal Grounds {base_prompt}"
        if style_phrase:
            positive = f"{positive}, {style_phrase}"
        # Enforce exposure/readability (counter dark/vague)
        positive = f"{positive}, readable shadows, balanced exposure"

        for seed in seeds:
            if args.limit and total >= args.limit:
                print("Reached limit; stopping.")
                return 0

            # Build workflow
            wf: Dict[str, Any] = create_atmospheric_concept_workflow(
                prompt=positive,
                seed=seed,
                width=args.width,
                height=args.height,
                steps=args.steps,
                cfg=args.cfg,
            )

            # Set specific file prefix per concept/style
            if "7" in wf and isinstance(wf["7"], dict):
                inp = wf["7"].get("inputs", {})
                inp["filename_prefix"] = f"STAGE_{style_key}_{name}"
                wf["7"]["inputs"] = inp

            print(f"Queue: {name} [{style_key}] seed={seed} {args.width}x{args.height} steps={args.steps} cfg={args.cfg}")

            if args.dry:
                continue

            pid = client.queue_prompt(wf)
            if not pid:
                print("  queue failed")
                continue

            imgs = client.wait_for_completion(pid, timeout=180)
            if not imgs:
                print("  no images (timeout or failure)")
                continue

            # Copy outputs
            concept_dir = STAGING_ROOT / style_key / name
            copied = 0
            for filename in imgs:
                if copy_to_folder(filename, concept_dir):
                    copied += 1
            print(f"  images: {len(imgs)}, copied: {copied} -> {concept_dir}")

            total += len(imgs)

    print("Done.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
