#!/usr/bin/env python3
"""
Organize Terminal Grounds assets for web deployment
Curates best assets from generation pipeline for immediate website use
"""

import os
import shutil
from pathlib import Path

# Paths
OUTPUT_DIR = Path(r"C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\output")
WEB_DIR = Path(r"C:\Users\Zachg\Terminal-Grounds\Web\assets")

# Create web asset directories
os.makedirs(WEB_DIR / "emblems", exist_ok=True)
os.makedirs(WEB_DIR / "environments", exist_ok=True)
os.makedirs(WEB_DIR / "hero_images", exist_ok=True)

def copy_web_assets():
    print("TERMINAL GROUNDS - WEB ASSET ORGANIZER")
    print("=" * 50)
    
    # Copy Enhanced Emblems (Primary faction branding)
    print("\n1. FACTION EMBLEMS:")
    emblem_count = 0
    for emblem_file in OUTPUT_DIR.glob("TG_Enhanced_Emblem_*.png"):
        dest = WEB_DIR / "emblems" / emblem_file.name
        shutil.copy2(emblem_file, dest)
        print(f"   OK {emblem_file.name}")
        emblem_count += 1
    
    # Copy Hero Environmental Assets (Website showcase)
    print(f"\n2. HERO ENVIRONMENTS:")
    hero_assets = [
        # Underground bunkers (best atmospheric)
        "TG_PERFECT_Underground_Bunker_Clean_SciFi_Detail_Dramatic_00004_.png",
        "TG_PERFECT_Underground_Bunker_Gritty_Realism_Detail_Dramatic_00003_.png",
        
        # Tech wastes (post-cascade storytelling) 
        "TG_PERFECT_Tech_Wastes_Exterior_Clean_SciFi_Perspective_Atmospheric_00004_.png",
        "TG_PERFECT_Tech_Wastes_Exterior_Gritty_Realism_Perspective_Atmospheric_00003_.png",
        
        # Metro systems (infrastructure)
        "TG_PERFECT_Metro_Maintenance_Corridor_Clean_SciFi_Wide_Ambient_00003_.png",
        "TG_PERFECT_Metro_Maintenance_Corridor_Gritty_Realism_Wide_Ambient_00002_.png",
        
        # Corporate spaces (facility repurposing)
        "TG_PERFECT_Corporate_Lobby_Interior_Clean_SciFi_Wide_Ambient_00004_.png",
        "TG_PERFECT_IEZ_Facility_Interior_Gritty_Realism_Detail_Dramatic_00003_.png",
        
        # Security checkpoints (authority presence)
        "TG_PERFECT_Security_Checkpoint_Clean_SciFi_Perspective_Atmospheric_00004_.png",
        "TG_PERFECT_Security_Checkpoint_Gritty_Realism_Perspective_Atmospheric_00003_.png"
    ]
    
    hero_count = 0
    for asset_name in hero_assets:
        source_file = OUTPUT_DIR / asset_name
        if source_file.exists():
            dest = WEB_DIR / "hero_images" / asset_name
            shutil.copy2(source_file, dest)
            print(f"   OK {asset_name}")
            hero_count += 1
        else:
            print(f"   WAIT {asset_name} (not found - still generating?)")
    
    # Copy Environmental Showcase Assets
    print(f"\n3. ENVIRONMENTAL SHOWCASES:")
    env_patterns = [
        "TG_PERFECT_*_00001_.png",  # First versions (proven quality)
        "TG_PERFECT_*_00002_.png",  # Second versions (variations)
    ]
    
    env_count = 0
    for pattern in env_patterns:
        for env_file in OUTPUT_DIR.glob(pattern):
            # Skip hero assets already copied
            if env_file.name not in [asset.split("/")[-1] for asset in hero_assets]:
                dest = WEB_DIR / "environments" / env_file.name
                shutil.copy2(env_file, dest)
                env_count += 1
    
    print(f"   OK {env_count} environmental variants copied")
    
    # Create deployment summary
    print(f"\n" + "=" * 50)
    print(f"WEB DEPLOYMENT PACKAGE READY:")
    print(f"  -> {emblem_count} Faction Emblems")
    print(f"  -> {hero_count} Hero Environmental Assets") 
    print(f"  -> {env_count} Environmental Showcase Assets")
    print(f"  -> Total: {emblem_count + hero_count + env_count} AAA-quality web assets")
    print(f"\nDeployment location: {WEB_DIR}")
    
    # Create index file
    with open(WEB_DIR / "ASSET_INDEX.md", "w") as f:
        f.write("# Terminal Grounds - Web Asset Index\n\n")
        f.write(f"**Generated**: August 26, 2025\n")
        f.write(f"**Quality Standard**: AAA Production Ready\n")
        f.write(f"**Total Assets**: {emblem_count + hero_count + env_count}\n\n")
        
        f.write("## Faction Emblems\n")
        for emblem_file in (WEB_DIR / "emblems").glob("*.png"):
            f.write(f"- {emblem_file.name}\n")
        
        f.write("\n## Hero Environmental Assets\n")
        for hero_file in (WEB_DIR / "hero_images").glob("*.png"):
            f.write(f"- {hero_file.name}\n")
            
        f.write(f"\n## Environmental Showcases\n")
        f.write(f"- {env_count} environmental variants in /environments/\n")

if __name__ == "__main__":
    copy_web_assets()