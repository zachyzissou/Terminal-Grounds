# tools_make_posters.py
# Compose A2 posters with emblem watermark and text.

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import date

ROOT = Path(__file__).resolve().parents[2]
SRC_EMBLEMS = ROOT / "Content/TG/Decals/Factions"
DOC_OUT = ROOT / "Docs/Concepts/Posters"
DECAL_OUT = ROOT / "Content/TG/Decals/Posters"
DOC_OUT.mkdir(parents=True, exist_ok=True)
DECAL_OUT.mkdir(parents=True, exist_ok=True)

POSTERS = [
    ("Directorate", "Maintain Formation", "Report Deviations Immediately"),
    ("VulturesUnion", "Salvage Credit", "Reward Efficient Recovery"),
    ("Free77", "Volunteer Recruitment", "Join the Contract"),
    ("CorporateCombine", "Lab Safety", "Protect Critical Systems"),
    ("NomadClans", "Convoy Discipline", "Follow the Banner"),
    ("VaultedArchivists", "Archive Integrity", "Preserve the Record"),
    ("CivicWardens", "Evac Corridor", "Keep Lanes Clear"),
    ("Neutral", "Grid Safety", "Authorized Personnel Only"),
    ("Neutral", "Report Hybrid Instability", "Alert Wardens"),
]

W, H = 2480, 3508


def choose_emblem(name: str) -> Path:
    # pick the emblem if exists, else fallback
    for p in SRC_EMBLEMS.glob(f"{name}*_2K.png"):
        return p
    for p in SRC_EMBLEMS.glob("*_2K.png"):
        return p
    return SRC_EMBLEMS


def make_poster(bg_hex: str, emblem_png: Path, title: str, subtitle: str, out: Path):
    img = Image.new("RGB", (W, H), bg_hex)
    d = ImageDraw.Draw(img)
    if emblem_png.exists():
        wm = Image.open(emblem_png).convert("RGBA").resize((1800, 1800))
        wm.putalpha(28)
        img.paste(wm, (340, 400), wm)
    # header
    d.rectangle([0, 0, W, 220], fill="#0C0F12")
    try:
        font_t = ImageFont.truetype("arial.ttf", 160)
        font_s = ImageFont.truetype("arial.ttf", 64)
    except Exception:
        font_t = ImageFont.load_default()
        font_s = ImageFont.load_default()
    d.text((120, 40), title, font=font_t, fill="white")
    d.text((120, 260), subtitle, font=font_s, fill="white")
    img.save(out, "PNG")


BG_COLORS = {
    "Directorate": "#2E4053",
    "VulturesUnion": "#1B1B1B",
    "Free77": "#2F2F2F",
    "CorporateCombine": "#0C0F12",
    "NomadClans": "#3B2A1F",
    "VaultedArchivists": "#102B1A",
    "CivicWardens": "#0A2E5C",
    "Neutral": "#202020",
}


def main():
    created = []
    for fac, title, subtitle in POSTERS:
        emblem = choose_emblem(fac)
        bg = BG_COLORS.get(fac, "#202020")
        doc_path = DOC_OUT / f"{fac}_{title.replace(' ', '_')}.png"
        dec_path = DECAL_OUT / f"{fac}_{title.replace(' ', '_')}.png"
        make_poster(bg, emblem, title, subtitle, doc_path)
        make_poster(bg, emblem, title, subtitle, dec_path)
        created.append((doc_path, dec_path))
    # Log
    log = ROOT / "Docs/Phase4_Implementation_Log.md"
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n[{date.today().isoformat()}] Created: {len(created)} poster pairs (Docs/Concepts/Posters + Content/TG/Decals/Posters)\n")

if __name__ == "__main__":
    main()
