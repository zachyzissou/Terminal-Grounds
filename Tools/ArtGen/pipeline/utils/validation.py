"""
Validation utilities
===================
"""

from typing import Any, List


def validate_faction(faction_name: str) -> bool:
    """Validate faction name."""
    valid_factions = [
        "directorate", "free77", "vultures", "corporate", 
        "wardens", "archivists", "nomads", "neutral"
    ]
    return faction_name.lower() in valid_factions


def validate_biome(biome_name: str) -> bool:
    """Validate biome name."""
    valid_biomes = ["iez", "wastes", "metro", "highlands", "underground"]
    return biome_name.lower() in valid_biomes


def validate_asset_type(asset_type: str) -> bool:
    """Validate asset type."""
    valid_types = [
        "weapon", "vehicle", "gear", "building", "character",
        "environment", "ui_icon", "poster", "texture", "concept"
    ]
    return asset_type.lower() in valid_types