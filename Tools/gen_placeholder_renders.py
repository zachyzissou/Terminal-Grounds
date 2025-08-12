#!/usr/bin/env python3
"""
Generate lightweight placeholder renders for README embedding until UE MRQ exports are available.
Outputs 1920x1080 PNGs under Docs/Concepts/Renders.
"""
import os
from pathlib import Path
from datetime import date
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Docs/Concepts/Renders"
OUT.mkdir(parents=True, exist_ok=True)

SCENES = [
    ("Hero", "Terminal Grounds — Visual Kickstart"),
    ("IEZ_Day", "IEZ — Day"),
    ("IEZ_Night", "IEZ — Night"),
    ("TechWastes_Day", "Tech Wastes — Day"),
    ("TechWastes_Night", "Tech Wastes — Night"),
    ("SkyBastion_Day", "Sky Bastion — Day"),
    ("SkyBastion_Night", "Sky Bastion — Night"),
    ("BlackVault_Day", "Black Vault — Day"),
    ("BlackVault_Night", "Black Vault — Night"),
]


def draw_card(title: str, subtitle: str, bg: str) -> Image.Image:
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    try:
        ft = ImageFont.truetype("arial.ttf", 72)
        fs = ImageFont.truetype("arial.ttf", 36)
    except Exception:
        ft = ImageFont.load_default()
        fs = ImageFont.load_default()
    d.text((80, 60), title, fill="white", font=ft)
    d.text((80, 150), subtitle, fill="#D0D8E0", font=fs)
    d.text((80, h-80), date.today().isoformat(), fill="#A0A8B0", font=fs)
    return img


def main():
    for name, label in SCENES:
        bg = "#10161F" if "Night" in name else "#0F1A24"
        if name == "Hero":
            bg = "#0B1320"
        img = draw_card("Terminal Grounds", label, bg)
        out = OUT / f"{name}.png"
        img.save(out, "PNG")
    print(f"Wrote {len(SCENES)} placeholder renders to {OUT}")


if __name__ == "__main__":
    main()
