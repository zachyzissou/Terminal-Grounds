# tools_make_swatches.py
# Generates palette swatches and style tiles (simple) for factions/biomes.

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import date

ROOT = Path(__file__).resolve().parents[2]
PAL_DIR = ROOT / "Docs/Concepts/Palettes"
STYLE_DIR = ROOT / "Docs/Concepts/StyleTiles"
PAL_DIR.mkdir(parents=True, exist_ok=True)
STYLE_DIR.mkdir(parents=True, exist_ok=True)

FACTIONS = {
    "Directorate": ["#001F3F", "#36454F", "#FFFFFF", "#4682B4"],
    "VulturesUnion": ["#B22222", "#696969", "#FFD700", "#0F0F0F"],
    "Free77": ["#D2B48C", "#556B2F", "#2F2F2F", "#8B4513"],
    "CorporateCombine": ["#4169E1", "#C0C0C0", "#9370DB", "#FF8C00"],
    "NomadClans": ["#8B4513", "#FF8C00", "#D2B48C", "#1C1C1C"],
    "VaultedArchivists": ["#228B22", "#DAA520", "#4B0082", "#008B8B"],
    "CivicWardens": ["#0080FF", "#FFFFFF", "#FF4500", "#32CD32"],
}


def save_palette(name, colors):
    W, H = 1024, 256
    img = Image.new("RGB", (W, H), "#0C0F12")
    d = ImageDraw.Draw(img)
    w = W // len(colors)
    for i, c in enumerate(colors):
        d.rectangle([i*w, 0, (i+1)*w, H], fill=c)
        d.text((i*w+16, H-48), c, fill="white")
    out = PAL_DIR / f"{name}_palette.png"
    img.save(out, "PNG")
    return out


def save_style_tile(name, colors):
    W, H = 1024, 1024
    img = Image.new("RGB", (W, H), colors[0])
    d = ImageDraw.Draw(img)
    d.rectangle([0, H//3, W, H//3+40], fill=colors[1])
    d.ellipse([W//3, H//3, W//3+320, H//3+320], fill=colors[2])
    d.text((24, 24), name, fill="white")
    out = STYLE_DIR / f"{name}_styletile.png"
    img.save(out, "PNG")
    return out


def main():
    for name, cols in FACTIONS.items():
        save_palette(name, cols)
        save_style_tile(name, cols)
    log = ROOT / "Docs/Phase4_Implementation_Log.md"
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n[{date.today().isoformat()}] Created: Palette + StyleTiles for {len(FACTIONS)} factions under Docs/Concepts\n")

if __name__ == "__main__":
    main()
