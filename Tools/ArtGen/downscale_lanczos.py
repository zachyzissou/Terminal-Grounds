#!/usr/bin/env python3
"""
Downscale images with Lanczos for crisp 1080p results after oversampling.
- Default: take the newest ComfyUI output and write *_1080p.png to Style_Staging/_Recent_Generations
- Or pass --input to downscale a specific file.
"""
import argparse
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
COMFY_OUT = Path.home() / "Documents" / "ComfyUI" / "output"
STAGING_RECENT = ROOT / "Style_Staging" / "_Recent_Generations"

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def find_latest(folder: Path) -> Path | None:
    imgs = [p for p in folder.iterdir() if p.suffix.lower() in IMG_EXTS]
    if not imgs:
        return None
    imgs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return imgs[0]


def downscale_to_width(src: Path, width: int = 1920, *, unsharp: bool = False, radius: float = 1.2, percent: int = 90, threshold: int = 2) -> Path:
    STAGING_RECENT.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        w, h = im.size
        if w <= width:
            # No upscale; just copy
            out = STAGING_RECENT / (src.stem + "_copy" + src.suffix)
            if unsharp:
                im = im.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))
            im.save(out)
            return out
        ratio = width / float(w)
        new_h = int(h * ratio)
        im2 = im.resize((width, new_h), resample=Image.Resampling.LANCZOS)
        if unsharp:
            im2 = im2.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))
        out = STAGING_RECENT / (src.stem + f"_{width}w" + src.suffix)
        im2.save(out)
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=str, default="", help="Specific image to downscale")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--unsharp", action="store_true", help="Apply mild unsharp mask after resize")
    ap.add_argument("--radius", type=float, default=1.2)
    ap.add_argument("--percent", type=int, default=90)
    ap.add_argument("--threshold", type=int, default=2)
    args = ap.parse_args()

    if args.input:
        src = Path(args.input)
    else:
        src = find_latest(COMFY_OUT)
    if not src or not src.exists():
        print("No image found to downscale.")
        return 1

    out = downscale_to_width(src, args.width, unsharp=args.unsharp, radius=args.radius, percent=args.percent, threshold=args.threshold)
    print(f"Wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
