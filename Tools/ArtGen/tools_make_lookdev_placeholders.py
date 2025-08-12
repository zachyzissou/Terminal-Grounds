#!/usr/bin/env python3
"""
Create placeholder look-dev renders by composing existing posters/palettes into 1920x1080 PNGs.
Outputs to Docs/Concepts/Renders so README embeds resolve before UE MRQ captures.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import date

ROOT = Path(__file__).resolve().parents[2]
RENDERS = ROOT / "Docs/Concepts/Renders"
POSTERS = ROOT / "Docs/Concepts/Posters"
PALETTES = ROOT / "Docs/Concepts/Palettes"
RENDERS.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080


def banner(text: str, bg=(12, 15, 18)):
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except Exception:
        font = ImageFont.load_default()
    try:
        bbox = d.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        tw, th = (len(text) * 24, 72)
    d.text(((W - tw) // 2, H - th - 40), text, font=font, fill=(255, 255, 255))
    return img


def grid_from_images(paths: list[Path], cols=3, rows=2, pad=16):
    img = Image.new("RGB", (W, H), (8, 8, 10))
    # draw grid of images
    cw = (W - (cols + 1) * pad) // cols
    ch = (H - (rows + 1) * pad) // rows
    i = 0
    for r in range(rows):
        for c in range(cols):
            if i >= len(paths):
                break
            p = paths[i]
            try:
                im = Image.open(p).convert("RGB")
                im = im.resize((cw, ch))
                x = pad + c * (cw + pad)
                y = pad + r * (ch + pad)
                img.paste(im, (x, y))
            except Exception:
                pass
            i += 1
    return img


def save(img: Image.Image, name: str):
    out = RENDERS / name
    img.save(out, "PNG")
    return out


def main():
    # Hero composites
    posters = sorted(POSTERS.glob("*.png"))
    palettes = sorted(PALETTES.glob("*_palette.png"))
    if posters:
        save(grid_from_images(posters[:6]), "Hero_IEZ.png")
        save(grid_from_images(list(reversed(posters))[:6]), "Hero_Wastes.png")
    if palettes:
        save(grid_from_images(palettes[:6]), "IEZ_palette.png")
        save(grid_from_images(list(reversed(palettes))[:6]), "Wastes_palette.png")
    # Simple labeled moods
    save(banner("Sky Bastion — storm look"), "SkyBastion_storm.png")
    save(banner("Black Vault — mood"), "BlackVault_mood.png")

    # Log
    log = ROOT / "Docs/Phase4_Implementation_Log.md"
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n[{date.today().isoformat()}] Created placeholder look-dev renders in Docs/Concepts/Renders (6 images)\n")


if __name__ == "__main__":
    main()
