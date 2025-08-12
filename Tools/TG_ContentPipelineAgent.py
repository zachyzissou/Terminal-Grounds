#!/usr/bin/env python3
"""
TG_ContentPipelineAgent.py
Terminal Grounds UE5.6 Content Pipeline Agent

A comprehensive content pipeline agent that:
1. Audits current assets for placeholders/generic content
2. Generates replacement assets via Hugging Face models
3. Imports assets into Unreal Engine 5.6 with proper settings
4. Creates material instances and applies tags
5. Maintains asset manifests and logs

Author: Terminal Grounds Content Pipeline Agent
Version: 1.0.0
"""

import os
import sys
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Try to import optional dependencies
try:
    from PIL import Image, ImageStat
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Terminal Grounds project root
ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = ROOT / "Content/TG"
ARTGEN_ROOT = ROOT / "Tools/ArtGen"
OUTPUTS_DIR = ARTGEN_ROOT / "outputs"
DOCS_ROOT = ROOT / "Docs"
CONFIG_DIR = ROOT / "Config"

# Asset directories to scan
SCAN_DIRECTORIES = [
    CONTENT_ROOT / "ConceptArt",
    CONTENT_ROOT / "Decals",
    CONTENT_ROOT / "Icons", 
    CONTENT_ROOT / "UI",
    CONTENT_ROOT / "Textures",
    CONTENT_ROOT / "Materials",
    CONTENT_ROOT / "Props",
    CONTENT_ROOT / "Vehicles",
    CONTENT_ROOT / "Characters",
    CONTENT_ROOT / "Environment",
    DOCS_ROOT / "Concepts",
]

# Image extensions to process
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tga', '.tiff', '.webp'}

# Placeholder detection patterns
PLACEHOLDER_PATTERNS = [
    r'placeholder',
    r'temp',
    r'todo',
    r'missing',
    r'generic',
    r'stock',
    r'default',
    r'untitled',
    r'new_asset',
    r'tbd',
    r'wip',
    r'test',
    r'dummy',
    r'sample'
]

# Watermark detection patterns
WATERMARK_PATTERNS = [
    r'shutterstock',
    r'getty',
    r'watermark',
    r'unsplash',
    r'freepik',
    r'adobe.stock',
    r'istock'
]

class AssetCategory(Enum):
    """Asset categories for generation targeting"""
    CONCEPT_ART = "concept_art"
    FACTION_LOGO = "faction_logo"
    POSTER_DECAL = "poster_decal"
    UI_ICON = "ui_icon"
    TEXTURE = "texture"
    WEAPON_CONCEPT = "weapon_concept"
    VEHICLE_CONCEPT = "vehicle_concept"
    BIOME_CONCEPT = "biome_concept"
    CHARACTER_CONCEPT = "character_concept"
    UNKNOWN = "unknown"

class AssetPriority(Enum):
    """Priority levels for asset replacement"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class AssetMetadata:
    """Metadata for tracked assets"""
    filepath: str
    filename: str
    category: AssetCategory
    priority: AssetPriority
    size_bytes: int
    resolution: Optional[Tuple[int, int]]
    is_placeholder: bool
    has_watermark: bool
    placeholder_score: float
    tags: List[str]
    faction: Optional[str]
    last_modified: str
    content_hash: str
    notes: List[str]

class TerminalGroundsContentAgent:
    """Main content pipeline agent class"""
    
    def __init__(self):
        self.flagged_assets: List[AssetMetadata] = []
        self.asset_manifest: Dict[str, Any] = {}
        self.faction_data = self._load_faction_data()
        self.art_bible = self._load_art_bible()
        self.log_file = ROOT / "Docs/Phase4_Implementation_Log.md"
        
        # Ensure required directories exist
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        (DOCS_ROOT / "Tech").mkdir(parents=True, exist_ok=True)
    
    def _load_faction_data(self) -> Dict[str, Any]:
        """Load faction data from art bible"""
        factions = {
            "Directorate": {
                "colors": ["#001F3F", "#36454F", "#FFFFFF", "#4682B4"],
                "style": "military_precision",
                "keywords": "disciplined, tactical, navy, steel"
            },
            "VulturesUnion": {
                "colors": ["#B22222", "#696969", "#FFD700", "#B87333"],
                "style": "salvage_industrial",
                "keywords": "scrap, rust, warning_stripes, oil"
            },
            "Free77": {
                "colors": ["#D2B48C", "#556B2F", "#2F2F2F", "#8B4513"],
                "style": "contractor_practical",
                "keywords": "desert, tactical, mercenary, brown"
            },
            "CorporateCombine": {
                "colors": ["#4169E1", "#C0C0C0", "#9370DB", "#FF8C00"],
                "style": "corporate_clean",
                "keywords": "blue, chrome, energy, professional"
            },
            "NomadClans": {
                "colors": ["#8B4513", "#FF8C00", "#D2B48C", "#4682B4"],
                "style": "convoy_rugged",
                "keywords": "brown, orange, convoy, road_worn"
            },
            "VaultedArchivists": {
                "colors": ["#102B1A", "#DAA520", "#50E3C2", "#B8E986"],
                "style": "alien_mystical",
                "keywords": "violet, eye, coil, archive"
            },
            "CivicWardens": {
                "colors": ["#0A2E5C", "#FF6A00", "#2E8B57", "#D4AF37"],
                "style": "defensive_militia",
                "keywords": "bastion, sandbags, orange, neighborhood"
            }
        }
        return factions
    
    def _load_art_bible(self) -> Dict[str, Any]:
        """Load art direction from art bible"""
        return {
            "primary_palette": ["#2A2D32", "#4A4E55", "#6A7080", "#3D2F1F", "#5C4A32", "#2F3D1F"],
            "energy_signatures": {
                "human": ["#4A90E2", "#7ED321"],
                "hybrid": ["#BD10E0", "#F5A623"], 
                "alien": ["#50E3C2", "#B8E986"]
            },
            "style_keywords": "grounded_realism, military_authentic, sci_fi_accents, post_apocalyptic_grit",
            "lighting": "practical_sources, atmospheric_haze, dramatic_contrast",
            "mood": "tactical_tension, salvage_economy, alien_mystery"
        }
    
    def detect_placeholder_content(self, filepath: Path) -> Tuple[bool, float, List[str]]:
        """Detect if an asset is placeholder content"""
        filename = filepath.name.lower()
        notes = []
        placeholder_score = 0.0
        
        # Check filename for placeholder patterns
        for pattern in PLACEHOLDER_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                placeholder_score += 0.3
                notes.append(f"Filename contains '{pattern}'")
        
        # Check for watermark patterns
        for pattern in WATERMARK_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                placeholder_score += 0.5
                notes.append(f"Filename suggests watermarked content '{pattern}'")
        
        # Check for generic naming patterns
        generic_patterns = [
            r'^image\d*\.(png|jpg|jpeg)$',
            r'^untitled.*\.(png|jpg|jpeg)$',
            r'^copy.*of.*\.(png|jpg|jpeg)$',
            r'^\d{8,}.*\.(png|jpg|jpeg)$'  # Long number filenames (often stock)
        ]
        
        for pattern in generic_patterns:
            if re.match(pattern, filename):
                placeholder_score += 0.4
                notes.append(f"Generic filename pattern detected")
        
        # If PIL is available, check image content
        if PIL_AVAILABLE and filepath.suffix.lower() in IMAGE_EXTENSIONS:
            try:
                with Image.open(filepath) as img:
                    # Check for very small images (likely icons/placeholders)
                    if img.size[0] <= 32 or img.size[1] <= 32:
                        placeholder_score += 0.2
                        notes.append("Very small resolution suggests placeholder")
                    
                    # Check for very uniform colors (solid color placeholders)
                    stat = ImageStat.Stat(img)
                    if all(std < 10 for std in stat.stddev):
                        placeholder_score += 0.3
                        notes.append("Very uniform colors suggest placeholder")
                        
            except Exception as e:
                notes.append(f"Could not analyze image content: {str(e)}")
        
        is_placeholder = placeholder_score >= 0.5
        return is_placeholder, min(placeholder_score, 1.0), notes
    
    def categorize_asset(self, filepath: Path) -> AssetCategory:
        """Categorize asset based on path and filename"""
        path_str = str(filepath).lower()
        filename = filepath.name.lower()
        
        # Check path-based categorization
        if "faction" in path_str and ("emblem" in path_str or "logo" in path_str):
            return AssetCategory.FACTION_LOGO
        elif "poster" in path_str or "decal" in path_str:
            return AssetCategory.POSTER_DECAL
        elif "icon" in path_str or "ui" in path_str:
            return AssetCategory.UI_ICON
        elif "weapon" in path_str:
            return AssetCategory.WEAPON_CONCEPT
        elif "vehicle" in path_str:
            return AssetCategory.VEHICLE_CONCEPT
        elif "biome" in path_str or "environment" in path_str:
            return AssetCategory.BIOME_CONCEPT
        elif "character" in path_str:
            return AssetCategory.CHARACTER_CONCEPT
        elif "concept" in path_str:
            return AssetCategory.CONCEPT_ART
        elif "texture" in path_str or "material" in path_str:
            return AssetCategory.TEXTURE
        else:
            return AssetCategory.UNKNOWN
    
    def extract_faction_from_path(self, filepath: Path) -> Optional[str]:
        """Extract faction name from file path"""
        path_str = str(filepath).lower()
        for faction in self.faction_data.keys():
            if faction.lower() in path_str:
                return faction
        return None
    
    def calculate_content_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file content"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return "unknown"
    
    def get_image_resolution(self, filepath: Path) -> Optional[Tuple[int, int]]:
        """Get image resolution if PIL is available"""
        if not PIL_AVAILABLE or filepath.suffix.lower() not in IMAGE_EXTENSIONS:
            return None
        
        try:
            with Image.open(filepath) as img:
                return img.size
        except Exception:
            return None
    
    def audit_asset(self, filepath: Path) -> AssetMetadata:
        """Audit a single asset and create metadata"""
        is_placeholder, placeholder_score, notes = self.detect_placeholder_content(filepath)
        category = self.categorize_asset(filepath)
        faction = self.extract_faction_from_path(filepath)
        
        # Determine priority based on category and placeholder status
        if is_placeholder:
            if category in [AssetCategory.FACTION_LOGO, AssetCategory.UI_ICON]:
                priority = AssetPriority.CRITICAL
            elif category in [AssetCategory.POSTER_DECAL, AssetCategory.CONCEPT_ART]:
                priority = AssetPriority.HIGH
            else:
                priority = AssetPriority.MEDIUM
        else:
            priority = AssetPriority.LOW
        
        # Generate tags
        tags = []
        if faction:
            tags.append(f"faction:{faction}")
        tags.append(f"category:{category.value}")
        if is_placeholder:
            tags.append("placeholder")
        
        stat = filepath.stat()
        
        return AssetMetadata(
            filepath=str(filepath.relative_to(ROOT)),
            filename=filepath.name,
            category=category,
            priority=priority,
            size_bytes=stat.st_size,
            resolution=self.get_image_resolution(filepath),
            is_placeholder=is_placeholder,
            has_watermark=any("watermark" in note.lower() for note in notes),
            placeholder_score=placeholder_score,
            tags=tags,
            faction=faction,
            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            content_hash=self.calculate_content_hash(filepath),
            notes=notes
        )
    
    def scan_content_directories(self) -> List[AssetMetadata]:
        """Recursively scan all content directories for assets"""
        print("🔍 Scanning content directories for assets...")
        all_assets = []
        
        for scan_dir in SCAN_DIRECTORIES:
            if not scan_dir.exists():
                print(f"⚠️  Directory not found: {scan_dir}")
                continue
                
            print(f"📁 Scanning: {scan_dir.relative_to(ROOT)}")
            
            for filepath in scan_dir.rglob('*'):
                if (filepath.is_file() and 
                    filepath.suffix.lower() in IMAGE_EXTENSIONS and
                    not filepath.name.startswith('.')):
                    
                    try:
                        asset_metadata = self.audit_asset(filepath)
                        all_assets.append(asset_metadata)
                        
                        if asset_metadata.is_placeholder:
                            self.flagged_assets.append(asset_metadata)
                            print(f"🚩 Flagged: {asset_metadata.filepath} (score: {asset_metadata.placeholder_score:.2f})")
                        
                    except Exception as e:
                        print(f"❌ Error auditing {filepath}: {str(e)}")
        
        print(f"✅ Scanned {len(all_assets)} assets, flagged {len(self.flagged_assets)} for replacement")
        return all_assets
    
    def generate_audit_report(self, all_assets: List[AssetMetadata]) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        
        # Convert assets to JSON-serializable format
        def asset_to_dict(asset: AssetMetadata) -> Dict[str, Any]:
            data = asdict(asset)
            data['category'] = asset.category.value
            data['priority'] = asset.priority.value
            return data
        
        report = {
            "audit_date": datetime.now().isoformat(),
            "total_assets_scanned": len(all_assets),
            "flagged_for_replacement": len(self.flagged_assets),
            "summary_by_category": {},
            "summary_by_priority": {},
            "summary_by_faction": {},
            "flagged_assets": [asset_to_dict(asset) for asset in self.flagged_assets],
            "all_assets": [asset_to_dict(asset) for asset in all_assets]
        }
        
        # Category summary
        for category in AssetCategory:
            assets_in_category = [a for a in all_assets if a.category == category]
            flagged_in_category = [a for a in assets_in_category if a.is_placeholder]
            report["summary_by_category"][category.value] = {
                "total": len(assets_in_category),
                "flagged": len(flagged_in_category),
                "percentage_flagged": len(flagged_in_category) / len(assets_in_category) * 100 if assets_in_category else 0
            }
        
        # Priority summary
        for priority in AssetPriority:
            assets_with_priority = [a for a in self.flagged_assets if a.priority == priority]
            report["summary_by_priority"][priority.value] = len(assets_with_priority)
        
        # Faction summary
        for faction in self.faction_data.keys():
            faction_assets = [a for a in all_assets if a.faction == faction]
            flagged_faction_assets = [a for a in faction_assets if a.is_placeholder]
            report["summary_by_faction"][faction] = {
                "total": len(faction_assets),
                "flagged": len(flagged_faction_assets)
            }
        
        return report
    
    def save_audit_report(self, report: Dict[str, Any]):
        """Save audit report to disk"""
        report_path = DOCS_ROOT / "Tech/asset_audit_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Audit report saved: {report_path.relative_to(ROOT)}")
        
        # Also log to implementation log
        with open(self.log_file, 'a', encoding='utf-8') as f:
            today = date.today().isoformat()
            f.write(f"\n[{today}] Asset audit completed: {report['total_assets_scanned']} scanned, {report['flagged_for_replacement']} flagged for replacement\n")
    
    def run_asset_audit(self) -> Dict[str, Any]:
        """Run complete asset audit process"""
        print("🚀 Starting Terminal Grounds Content Pipeline Asset Audit")
        print("=" * 60)
        
        # Reset flagged assets
        self.flagged_assets = []
        
        # Scan all directories
        all_assets = self.scan_content_directories()
        
        # Generate report
        report = self.generate_audit_report(all_assets)
        
        # Save report
        self.save_audit_report(report)
        
        # Print summary
        print("\n📊 AUDIT SUMMARY")
        print("=" * 30)
        print(f"Total assets scanned: {report['total_assets_scanned']}")
        print(f"Assets flagged for replacement: {report['flagged_for_replacement']}")
        print("\nBy Priority:")
        for priority, count in report['summary_by_priority'].items():
            print(f"  {priority.upper()}: {count}")
        print("\nBy Category:")
        for category, data in report['summary_by_category'].items():
            if data['total'] > 0:
                print(f"  {category}: {data['flagged']}/{data['total']} ({data['percentage_flagged']:.1f}%)")
        
        return report

# CLI interface
def main():
    """Main CLI entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "audit":
        agent = TerminalGroundsContentAgent()
        agent.run_asset_audit()
    else:
        print("Terminal Grounds Content Pipeline Agent")
        print("Usage:")
        print("  python TG_ContentPipelineAgent.py audit    # Run asset audit")
        print("  # More commands coming soon...")

if __name__ == "__main__":
    main()