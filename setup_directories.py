"""
Setup all required directories for Terminal Grounds asset pipeline
"""
import os

project_root = r"C:\Users\Zachg\Terminal-Grounds"

directories = [
    "Content/TG/Decals/Factions",
    "Content/TG/Decals/Posters",
    "Content/TG/Icons",
    "Docs/Concepts/AI",
    "Docs/Concepts/Logos",
    "Docs/Concepts/Palettes",
    "Docs/Concepts/Posters",
    "Docs/Concepts/Renders",
    "Docs/Concepts/StyleTiles",
    "Docs/Concepts/AI/Weapons",
    "Docs/Concepts/AI/Vehicles",
    "Docs/Concepts/AI/Characters",
    "Docs/Concepts/AI/Biomes",
    "Docs/PressKit",
    "Tools/ArtGen/recipes",
    "Tools/ArtGen/outputs",
    "Tools/Validation",
    "Tools/Comfy/workflows",
    "Tools/Comfy/client",
    "Tools/Unreal/python",
    "_Placeholders"  # For quarantine
]

for dir_path in directories:
    full_path = os.path.join(project_root, dir_path.replace('/', os.sep))
    os.makedirs(full_path, exist_ok=True)
    print(f"✓ Created: {full_path}")

print(f"\n✅ All directories created successfully!")
