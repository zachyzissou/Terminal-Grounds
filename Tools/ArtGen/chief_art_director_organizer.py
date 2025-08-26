#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chief Art Director Asset Organizer
Automatically organizes generated assets into production structure
"""

import os
import shutil
import re
from pathlib import Path
import json
from datetime import datetime

OUTPUT_DIR = "C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output"

ORGANIZATION_RULES = {
    # Production Ready Assets (TG_PERFECT series)
    r"TG_PERFECT.*Corporate.*": "01_PRODUCTION_READY/environments/corporate",
    r"TG_PERFECT.*Underground.*": "01_PRODUCTION_READY/environments/underground", 
    r"TG_PERFECT.*Metro.*": "01_PRODUCTION_READY/environments/underground",
    r"TG_PERFECT.*Tech_Wastes.*": "01_PRODUCTION_READY/environments/wasteland",
    r"TG_PERFECT.*Security.*": "01_PRODUCTION_READY/environments/industrial",
    r"TG_PERFECT.*IEZ.*": "01_PRODUCTION_READY/environments/industrial",
    
    # Chief Art Director Enhanced Assets
    r"CHIEF_ART_DIRECTOR.*Emblem.*": "02_CHIEF_ART_DIRECTOR/enhanced_emblems",
    r"CAD_EMBLEM.*": "02_CHIEF_ART_DIRECTOR/enhanced_emblems",
    r"CAD_TERRITORY.*": "01_PRODUCTION_READY/factions/territory_markers",
    r"CAD_EXTRACTION.*": "01_PRODUCTION_READY/factions/extraction_zones",
    r"CAD_SILHOUETTE.*": "02_CHIEF_ART_DIRECTOR/visual_studies",
    
    # Enhanced Faction Assets (Phase 2)
    r"TG_Enhanced_Emblem.*": "02_CHIEF_ART_DIRECTOR/enhanced_emblems",
    r"TG_Territory.*": "01_PRODUCTION_READY/factions/territory_markers",
    r"TG_Extraction.*": "01_PRODUCTION_READY/factions/extraction_zones", 
    r"TG_Silhouette.*": "02_CHIEF_ART_DIRECTOR/visual_studies",
    
    # Bloom Game Branding
    r"BLOOM_LOGO.*": "02_CHIEF_ART_DIRECTOR/game_branding",
    
    # Concept Art Library
    r"TG_CONCEPT_WEAPON.*": "01_PRODUCTION_READY/weapons",
    r"TG_CONCEPT_VEHICLE.*": "01_PRODUCTION_READY/vehicles",
    r"TG_CONCEPT_OPERATOR.*": "02_CHIEF_ART_DIRECTOR/character_studies",
    
    # Standard Faction Assets
    r"TG_Emblem.*": "01_PRODUCTION_READY/factions/emblems",
    
    # Development/Testing Assets
    r"TG_.*Test.*": "03_DEVELOPMENT/batch_" + datetime.now().strftime("%Y-%m-%d"),
    r"TG_.*Debug.*": "03_DEVELOPMENT/batch_" + datetime.now().strftime("%Y-%m-%d"),
    r"PA_.*": "03_DEVELOPMENT/batch_" + datetime.now().strftime("%Y-%m-%d"),
}

NAMING_CONVENTIONS = {
    # Production Ready Conversions
    r"TG_PERFECT_Corporate_.*_Clean_SciFi.*": lambda m: f"TG_ENV_Corporate_{extract_location(m)}_CleanSciFi_v01.png",
    r"TG_PERFECT_Corporate_.*_Gritty_Realism.*": lambda m: f"TG_ENV_Corporate_{extract_location(m)}_GrittyRealism_v01.png",
    r"TG_PERFECT_Underground_.*_Clean_SciFi.*": lambda m: f"TG_ENV_Underground_{extract_location(m)}_CleanSciFi_v01.png",
    r"TG_PERFECT_Underground_.*_Gritty_Realism.*": lambda m: f"TG_ENV_Underground_{extract_location(m)}_GrittyRealism_v01.png",
    r"TG_PERFECT_Metro_.*_Clean_SciFi.*": lambda m: f"TG_ENV_Metro_{extract_location(m)}_CleanSciFi_v01.png",
    r"TG_PERFECT_Metro_.*_Gritty_Realism.*": lambda m: f"TG_ENV_Metro_{extract_location(m)}_GrittyRealism_v01.png",
    
    # Chief Art Director Conversions
    r"CHIEF_ART_DIRECTOR_(.+)_Enhanced.*": lambda m: f"CAD_EMBLEM_{m.group(1)}_Enhanced_v01.png",
}

def extract_location(match):
    """Extract location name from PERFECT series naming"""
    filename = match.group(0)
    # Extract location between TG_PERFECT_ and style indicators
    parts = filename.split('_')
    location_parts = []
    capture = False
    for part in parts:
        if part == "PERFECT":
            capture = True
            continue
        if capture and part not in ["Clean", "Gritty", "Wide", "Detail", "Perspective", "Atmospheric", "SciFi", "Realism"]:
            location_parts.append(part)
        elif capture and part in ["Clean", "Gritty"]:
            break
    return "_".join(location_parts)

def organize_assets():
    """Organize loose assets in output directory"""
    output_path = Path(OUTPUT_DIR)
    organized_count = 0
    
    # Get all PNG files in root output directory
    loose_files = [f for f in output_path.glob("*.png") if f.is_file()]
    
    organization_log = {
        "timestamp": datetime.now().isoformat(),
        "organized_assets": [],
        "skipped_assets": [],
        "errors": []
    }
    
    for file_path in loose_files:
        filename = file_path.name
        original_path = str(file_path)
        
        # Find matching organization rule
        target_folder = None
        for pattern, folder in ORGANIZATION_RULES.items():
            if re.match(pattern, filename):
                target_folder = folder
                break
        
        if not target_folder:
            organization_log["skipped_assets"].append({
                "file": filename,
                "reason": "No matching organization rule"
            })
            continue
        
        # Apply naming convention if applicable
        new_filename = filename
        for pattern, converter in NAMING_CONVENTIONS.items():
            match = re.match(pattern, filename)
            if match:
                if callable(converter):
                    new_filename = converter(match)
                else:
                    new_filename = converter
                break
        
        # Create target directory and move file
        target_path = output_path / target_folder
        target_path.mkdir(parents=True, exist_ok=True)
        
        final_path = target_path / new_filename
        
        try:
            shutil.move(original_path, str(final_path))
            organized_count += 1
            
            organization_log["organized_assets"].append({
                "original": filename,
                "new_name": new_filename,
                "category": target_folder,
                "path": str(final_path)
            })
            
            print(f"ORGANIZED: {filename} -> {target_folder}/{new_filename}")
            
        except Exception as e:
            organization_log["errors"].append({
                "file": filename,
                "error": str(e)
            })
            print(f"ERROR organizing {filename}: {e}")
    
    # Save organization log
    log_path = output_path / "05_QUALITY_CONTROL" / "organization_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_path, 'w') as f:
        json.dump(organization_log, f, indent=2)
    
    print("\\n=== CHIEF ART DIRECTOR ORGANIZATION COMPLETE ===")
    print(f"Assets organized: {organized_count}")
    print(f"Assets skipped: {len(organization_log['skipped_assets'])}")
    print(f"Errors: {len(organization_log['errors'])}")
    print(f"Log saved: {log_path}")

def create_directory_structure():
    """Ensure all production directories exist"""
    base_path = Path(OUTPUT_DIR)
    
    directories = [
        "01_PRODUCTION_READY/factions/emblems",
        "01_PRODUCTION_READY/factions/territory_markers", 
        "01_PRODUCTION_READY/factions/extraction_zones",
        "01_PRODUCTION_READY/factions/silhouettes",
        "01_PRODUCTION_READY/environments/corporate",
        "01_PRODUCTION_READY/environments/industrial", 
        "01_PRODUCTION_READY/environments/underground",
        "01_PRODUCTION_READY/environments/wasteland",
        "01_PRODUCTION_READY/weapons",
        "01_PRODUCTION_READY/vehicles",
        "01_PRODUCTION_READY/ui_elements",
        "02_CHIEF_ART_DIRECTOR/enhanced_emblems",
        "02_CHIEF_ART_DIRECTOR/visual_studies",
        "02_CHIEF_ART_DIRECTOR/game_branding",
        "02_CHIEF_ART_DIRECTOR/character_studies",
        "02_CHIEF_ART_DIRECTOR/faction_palettes",
        "03_DEVELOPMENT/batch_" + datetime.now().strftime("%Y-%m-%d"),
        "03_DEVELOPMENT/experimental",
        "04_ARCHIVE/legacy_batches",
        "04_ARCHIVE/deprecated_tests",
        "05_QUALITY_CONTROL/pending_review",
        "05_QUALITY_CONTROL/approved"
    ]
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("Chief Art Director directory structure created successfully!")

def main():
    print("=" * 60)
    print("CHIEF ART DIRECTOR ASSET ORGANIZER")
    print("=" * 60)
    
    # Ensure directory structure exists
    create_directory_structure()
    
    # Organize loose assets
    organize_assets()

if __name__ == "__main__":
    main()