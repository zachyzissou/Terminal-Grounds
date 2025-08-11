# tools_make_icons.py
# Generates simple SVG icons and exports PNGs to Content/TG/Icons.

import os
from pathlib import Path
try:
    import cairosvg  # type: ignore
except Exception:
    cairosvg = None
try:
    from PIL import Image, ImageDraw
except Exception:
    Image = None

ROOT = Path(__file__).resolve().parents[2]
SVG_DIR = ROOT / "Tools/ArtGen/icons/svg"
PNG_DIR = ROOT / "Content/TG/Icons"
SVG_DIR.mkdir(parents=True, exist_ok=True)
PNG_DIR.mkdir(parents=True, exist_ok=True)

ICONS = {
    "damage_ballistic": "<circle cx='32' cy='32' r='26' stroke='#FFFFFF' stroke-width='6' fill='none'/><rect x='28' y='8' width='8' height='48' fill='#FFFFFF' />",
    "damage_ion": "<circle cx='32' cy='32' r='26' stroke='#00E5FF' stroke-width='6' fill='none'/><path d='M16 32 L32 12 L48 32 L32 52 Z' fill='#00E5FF'/>",
    "status_heat": "<path d='M32 8 C28 20 36 24 32 40 C28 24 36 20 32 8 Z' fill='#FF5722'/>",
    "status_charge": "<polygon points='28,8 48,32 36,32 44,56 16,28 28,28' fill='#50E3C2'/>",
    "rarity_common": "<rect x='8' y='8' width='48' height='48' fill='#CCCCCC'/>",
    "rarity_legendary": "<rect x='8' y='8' width='48' height='48' fill='#DAA520'/>",
    "map_ping": "<circle cx='32' cy='24' r='12' fill='#00B0FF'/><path d='M32 40 L24 56 L40 56 Z' fill='#00B0FF'/>",
    "extract": "<path d='M16 40 H48 V48 H16 Z M24 16 H40 V40 H24 Z' fill='#FFFFFF'/>",
}

HEADER = """<svg viewBox='0 0 64 64' xmlns='http://www.w3.org/2000/svg'>%s</svg>"""


def write_svg(name: str, body: str):
    p = SVG_DIR / f"{name}.svg"
    p.write_text(HEADER % body, encoding="utf-8")
    return p


def export_png(svg_path: Path, size=128):
    out = PNG_DIR / f"{svg_path.stem}_{size}.png"
    if cairosvg:
        cairosvg.svg2png(url=str(svg_path), write_to=str(out), output_width=size, output_height=size)
    else:
        if Image:
            img = Image.new("RGBA", (size, size), (0,0,0,0))
            d = ImageDraw.Draw(img)
            d.rectangle([8,8,size-8,size-8], outline=(255,255,255,255), width=3)
            img.save(out, "PNG")
        else:
            (SVG_DIR / "convert_me_icons.md").write_text("Install cairosvg or Pillow to export PNGs", encoding="utf-8")
    return out


def main():
    for name, body in ICONS.items():
        svg = write_svg(name, body)
        export_png(svg, 64)
        export_png(svg, 128)

    log = ROOT / "Docs/Phase4_Implementation_Log.md"
    from datetime import date
    today = date.today().isoformat()
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n[{today}] Created: UI icons -> {len(ICONS)} SVGs in Tools/ArtGen/icons/svg and PNGs in Content/TG/Icons\n")

if __name__ == "__main__":
    main()
