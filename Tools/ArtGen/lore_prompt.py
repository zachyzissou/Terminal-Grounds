#!/usr/bin/env python3
"""
Lore-aware prompt builder for Terminal Grounds.
Encodes world/style cues so prompts stay consistent across generations.
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class StyleProfile:
    name: str
    positives: str
    negatives: str


STYLES: Dict[str, StyleProfile] = {
    "Clean_SciFi": StyleProfile(
        name="Clean_SciFi",
        positives=(
            "clean sci-fi industrial, machined surfaces, anodized metals, structured lighting,"
            " precise geometry, restrained color palette, subtle wear, professional game art"
        ),
        negatives=(
            "grunge overload, whimsical, fantasy ornaments, cartoonish, heavy grime, text, watermark"
        ),
    ),
    "Gritty_Realism": StyleProfile(
        name="Gritty_Realism",
        positives=(
            "gritty realism, grounded materials, believable aging, cinematic lighting,"
            " volumetric atmosphere, high detail but natural texture"
        ),
        negatives=(
            "over-stylized, plastic sheen, excessive bloom, text, watermark"
        ),
    ),
}


def build_prompt(
    location: str,
    scene: str,
    style: str = "Clean_SciFi",
    extra: str = "",
) -> tuple[str, str]:
    prof = STYLES.get(style, STYLES["Clean_SciFi"])
    base = f"Terminal Grounds {location}, {scene}, {prof.positives}"
    if extra:
        base += ", " + extra
    negatives = prof.negatives
    return base, negatives
