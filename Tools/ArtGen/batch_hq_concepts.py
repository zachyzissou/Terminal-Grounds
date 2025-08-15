#!/usr/bin/env python3
"""
Batch-generate high-quality lore-aligned concepts at 1440p using
Euler/normal (steps=30, cfg=4.0), then downscale to 1080p with
Lanczos + optional mild unsharp, and copy results to staging.
"""
import argparse
import json
from pathlib import Path
from typing import List
from PIL import Image, ImageFilter

from comfyui_api_client import ComfyUIAPIClient, COMFYUI_OUTPUT
from atmospheric_concept_workflow import create_atmospheric_concept_workflow

ROOT = Path(__file__).resolve().parents[2]
LORE = ROOT / "Tools" / "ArtGen" / "lore_index.json"
STAGING_RECENT = ROOT / "Style_Staging" / "_Recent_Generations"


def build_lore_prompt(location: str, style: str, extra: str = "") -> tuple[str, str]:
    data = json.loads(LORE.read_text(encoding="utf-8"))
    st = data["styles"].get(style, data["styles"]["Clean_SciFi"])
    loc = data["locations"].get(location, {})
    disallow = data.get("disallow", "")
    parts = [
        f"Terminal Grounds {location}",
        loc.get("scene", ""),
        loc.get("composition", ""),
        loc.get("materials", ""),
        loc.get("lighting", ""),
        loc.get("mood", ""),
        st["positives"],
        extra,
    ]
    positive = ", ".join([p for p in parts if p])
    negative = ", ".join([st["negatives"], disallow])
    return positive, negative


def downscale_with_optional_unsharp(src_path: Path, width: int = 1920, unsharp: bool = True) -> Path:
    STAGING_RECENT.mkdir(parents=True, exist_ok=True)
    with Image.open(src_path) as im:
        w, h = im.size
        ratio = width / float(w)
        new_h = int(h * ratio)
        im2 = im.resize((width, new_h), resample=Image.Resampling.LANCZOS)
        if unsharp:
            im2 = im2.filter(ImageFilter.UnsharpMask(radius=1.2, percent=90, threshold=2))
        out = STAGING_RECENT / (src_path.stem + f"_{width}w" + src_path.suffix)
        im2.save(out)
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--locations", nargs="*", default=[
        "Metro_Maintenance_Corridor",
        "IEZ_Facility_Interior",
    ])
    ap.add_argument("--style", default="Clean_SciFi")
    ap.add_argument("--seeds", nargs="*", type=int, default=[94887, 94890])
    ap.add_argument("--width", type=int, default=2560)
    ap.add_argument("--height", type=int, default=1440)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=4.0)
    ap.add_argument("--timeout", type=int, default=1200)
    ap.add_argument("--extra", default="professional game art")
    ap.add_argument("--downscale", action="store_true")
    args = ap.parse_args()

    client = ComfyUIAPIClient()
    if not client.check_server():
        print("ComfyUI not reachable")
        return 2

    generated: List[str] = []

    for location in args.locations:
        pos, neg = build_lore_prompt(location, args.style, extra=args.extra)
        for seed in args.seeds:
            prefix = f"HQ_{location}_{args.style}_{args.width}x{args.height}_s{args.steps}_cfg{args.cfg}"
            wf = create_atmospheric_concept_workflow(
                prompt=pos,
                seed=seed,
                width=args.width,
                height=args.height,
                steps=args.steps,
                cfg=args.cfg,
                sampler_name="euler",
                scheduler="normal",
                filename_prefix=prefix,
                negative_text=neg,
            )
            data = json.dumps({"prompt": wf}).encode("utf-8")
            import urllib.request
            import urllib.error
            try:
                req = urllib.request.Request(f"{client.base_url}/prompt", data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    body = json.loads(resp.read().decode("utf-8", errors="ignore"))
                pid = body.get("prompt_id", "")
            except Exception as e:
                print("Queue error:", e)
                continue

            if not pid:
                print("Queue failed for", location, seed)
                continue

            imgs = client.wait_for_completion(pid, timeout=args.timeout)
            if not imgs:
                print("Timeout/no output for", location, seed)
                continue

            for fn in imgs:
                generated.append(fn)
                client.copy_to_staging(fn)
                if args.downscale:
                    src_file = COMFYUI_OUTPUT / fn
                    if src_file.exists():
                        downscale_with_optional_unsharp(src_file, width=1920, unsharp=True)

    print("Generated:", generated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
