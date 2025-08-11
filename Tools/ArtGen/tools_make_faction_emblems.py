# tools_make_faction_emblems.py
# Generates 7 faction emblems as SVGs (Tools/ArtGen/svg) and 2K PNG decals (Content/TG/Decals/Factions)
# Uses cairosvg if available; otherwise writes a convert_me script.

import os, sys, json
from pathlib import Path

try:
    import cairosvg  # type: ignore
except Exception:
    cairosvg = None
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = None

ROOT = Path(__file__).resolve().parents[2]
SVG_DIR = ROOT / "Tools/ArtGen/svg"
PNG_DIR = ROOT / "Content/TG/Decals/Factions"
PNG_DIR.mkdir(parents=True, exist_ok=True)
SVG_DIR.mkdir(parents=True, exist_ok=True)

FACTIONS = [
    ("Directorate", "#2E4053", "#9FB2C9"),
    ("VulturesUnion", "#1B1B1B", "#FFC107"),
    ("Free77", "#2F2F2F", "#D2B48C"),
    ("CorporateCombine", "#0C0F12", "#6DA6FF"),
    ("NomadClans", "#3B2A1F", "#FF8C00"),
    ("VaultedArchivists", "#102B1A", "#DAA520"),
    ("CivicWardens", "#0A2E5C", "#FF6A00"),
]


def svg_chevron_grid(hex_primary="#2E4053", hex_accent="#9FB2C9"):
    cols = []
    for x in range(64, 1024, 64):
        cols.append(f'<line x1="{x}" y1="0" x2="{x}" y2="1024"/>')
    rows = []
    for y in range(64, 1024, 64):
        rows.append(f'<line x1="0" y1="{y}" x2="1024" y2="{y}"/>')
    return f'''<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <rect width="1024" height="1024" fill="{hex_primary}"/>
  <g opacity="0.25" stroke="{hex_accent}" stroke-width="4">{''.join(cols)}{''.join(rows)}</g>
  <path d="M128 384 L512 768 L896 384" fill="none" stroke="{hex_accent}" stroke-width="64" stroke-linecap="round"/>
</svg>'''


def svg_beak_bolt(bg="#1B1B1B", accent="#FFC107"):
    return f'''<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <rect width="1024" height="1024" fill="{bg}"/>
  <polygon points="256,512 640,256 512,512 768,640" fill="{accent}"/>
  <polygon points="384,384 896,256 512,768" fill="{accent}" opacity="0.4"/>
</svg>'''


def svg_stencil_77(bg="#2F2F2F", accent="#D2B48C"):
    return f'''<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <rect width="1024" height="1024" fill="{bg}"/>
  <path d="M128 256 H896 L640 512 H512 L896 768 H128 Z" fill="{accent}"/>
</svg>'''


def svg_hex_shield(bg="#0C0F12", accent="#6DA6FF"):
    return f'''<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <rect width="1024" height="1024" fill="{bg}"/>
  <polygon points="512,128 832,320 832,704 512,896 192,704 192,320" fill="none" stroke="{accent}" stroke-width="48"/>
  <circle cx="512" cy="512" r="120" fill="{accent}" opacity="0.25"/>
</svg>'''


def svg_banner_axle(bg="#3B2A1F", accent="#FF8C00"):
    return f'''<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <rect width="1024" height="1024" fill="{bg}"/>
  <rect x="256" y="128" width="512" height="640" fill="{accent}"/>
  <circle cx="512" cy="864" r="96" stroke="{accent}" stroke-width="32" fill="none"/>
</svg>'''


def svg_eye_coil(bg="#102B1A", accent="#DAA520"):
    return f'''<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <rect width="1024" height="1024" fill="{bg}"/>
  <ellipse cx="512" cy="512" rx="384" ry="224" fill="none" stroke="{accent}" stroke-width="32"/>
  <circle cx="512" cy="512" r="96" fill="{accent}"/>
  <circle cx="512" cy="512" r="192" fill="none" stroke="{accent}" stroke-width="24" opacity="0.4"/>
</svg>'''


def svg_bastion_block(bg="#0A2E5C", accent="#FF6A00"):
    return f'''<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <rect width="1024" height="1024" fill="{bg}"/>
  <rect x="256" y="256" width="512" height="512" fill="none" stroke="{accent}" stroke-width="48"/>
  <rect x="384" y="384" width="256" height="256" fill="{accent}" opacity="0.3"/>
</svg>'''


def write_svg(name: str, svg: str):
    out = SVG_DIR / f"{name}.svg"
    out.write_text(svg, encoding="utf-8")
    return out


def export_png(svg_path: Path):
    png_out = PNG_DIR / f"{svg_path.stem}_2K.png"
    if cairosvg is not None:
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_out), output_width=2048, output_height=2048)
        return png_out
    # Fallback: simple PNG block with label if Pillow available
    if Image is not None:
        img = Image.new("RGB", (2048, 2048), "#202020")
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 64)
        except Exception:
            font = ImageFont.load_default()
        d.text((48, 48), f"{svg_path.stem} emblem (fallback)", fill="white", font=font)
        img.save(png_out, "PNG")
    else:
        # Write conversion helper
        conv_bat = SVG_DIR / "convert_me.bat"
        conv_sh = SVG_DIR / "convert_me.sh"
        conv_bat.write_text("REM install cairosvg: pip install cairosvg\n", encoding="utf-8")
        conv_sh.write_text("# pip install cairosvg\n", encoding="utf-8")
    return png_out


def main():
    gens = [
        ("Directorate", svg_chevron_grid),
        ("VulturesUnion", svg_beak_bolt),
        ("Free77", svg_stencil_77),
        ("CorporateCombine", svg_hex_shield),
        ("NomadClans", svg_banner_axle),
        ("VaultedArchivists", svg_eye_coil),
        ("CivicWardens", svg_bastion_block),
    ]
    created = []
    for name, fn in gens:
        svg = fn()
        svg_path = write_svg(name, svg)
        png_path = export_png(svg_path)
        created.append({"name": name, "svg": str(svg_path.relative_to(ROOT)), "png": str(png_path.relative_to(ROOT))})
    # Log to implementation log
    log = ROOT / "Docs/Phase4_Implementation_Log.md"
    with log.open("a", encoding="utf-8") as f:
        from datetime import date
        today = date.today().isoformat()
        for entry in created:
            f.write(f"\n[{today}] Created: {entry['name']} emblem -> SVG: {entry['svg']}, PNG: {entry['png']}\n")
    print(json.dumps(created, indent=2))

if __name__ == "__main__":
    main()
