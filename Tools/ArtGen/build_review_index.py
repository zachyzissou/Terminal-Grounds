#!/usr/bin/env python3
"""
Build a simple HTML gallery for Style_Staging/_Recent_Generations to review outputs.
Groups by inferred category prefix and creates clickable thumbnails.
"""
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "Style_Staging" / "_Recent_Generations"
OUT = STAGING / "index.html"

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

CSS = """
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }
h1 { margin: 0 0 16px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
.card { border: 1px solid #ddd; border-radius: 8px; padding: 8px; background: #fff; }
.card img { width: 100%; height: auto; border-radius: 4px; }
.meta { font-size: 12px; color: #555; margin-top: 6px; }
.group { margin: 24px 0; }
.group h2 { margin: 8px 0 8px; font-size: 18px; }
footer { margin-top: 24px; font-size: 12px; color: #666; }
"""

def infer_group(name: str) -> str:
    # Use the first 2-3 underscore segments to infer a category
    parts = name.split("_")
    if len(parts) >= 2 and parts[0] in ("PROD", "TG"):
        # PROD_* or TG_* => keep two parts
        return "_".join(parts[:2])
    # fallback to first token
    return parts[0]


def main():
    if not STAGING.exists():
        print(f"No staging dir: {STAGING}")
        return 1

    images = [p for p in STAGING.iterdir() if p.suffix.lower() in IMG_EXTS]
    if not images:
        print("No images found.")
        return 0

    # Sort newest first
    images.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    # Group
    groups = {}
    for img in images:
        grp = infer_group(img.stem)
        groups.setdefault(grp, []).append(img)

    # Write HTML
    with OUT.open("w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><head><meta charset='utf-8'>\n")
        f.write("<meta name='viewport' content='width=device-width, initial-scale=1'>\n")
        f.write("<title>Style Staging Review</title><style>" + CSS + "</style></head><body>\n")
        f.write("<h1>Style Staging Review</h1>\n")
        f.write(f"<div class='meta'>Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>")

        for grp, files in groups.items():
            f.write(f"<div class='group'><h2>{grp} ({len(files)})</h2>")
            f.write("<div class='grid'>")
            for img in files:
                rel = img.name  # same folder
                f.write("<div class='card'>")
                f.write(f"<a href='{rel}' target='_blank'><img src='{rel}' loading='lazy'></a>")
                f.write(f"<div class='meta'>{img.name}</div>")
                f.write("</div>")
            f.write("</div></div>")

        f.write("<footer>Folder: Style_Staging/_Recent_Generations</footer>")
        f.write("</body></html>")

    print(f"Wrote {OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
