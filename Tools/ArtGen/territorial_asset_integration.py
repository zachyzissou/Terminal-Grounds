#!/usr/bin/env python3
"""
Territorial Asset Generation Integration
Connects the proven 92% success rate asset pipeline with real-time territorial control system
Generates faction-specific content based on territorial dominance
"""

import json
import os
import sys
import sqlite3
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

# Import proven generation system
sys.path.append(str(Path(__file__).parent))
from terminal_grounds_generator import PERFECTION_PARAMS, submit_workflow

@dataclass
class TerritorialAssetRequest:
    """Asset generation request based on territorial control"""
    territory_id: int
    territory_name: str
    controlling_faction: int
    control_percentage: float
    contested: bool
    asset_type: str  # "environment", "marker", "ui_element", "propaganda"
    style_variant: str  # Based on control level
    priority: int = 50

class TerritorialAssetIntegration:
    """
    Integrates 92% success rate asset pipeline with territorial control system
    Generates faction-specific assets dynamically based on territorial state
    """
    
    def __init__(self):
        self.db_path = Path("C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db")
        self.output_dir = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/territorial")
        self.output_dir.mkdir(exist_ok=True)
        
        # Asset generation configurations
        self.asset_configs = {
            "environment": {
                "resolution": (1536, 864),
                "generation_time": 310,
                "priority": 1
            },
            "marker": {
                "resolution": (512, 512),
                "generation_time": 120,
                "priority": 2
            },
            "ui_element": {
                "resolution": (256, 256),
                "generation_time": 90,
                "priority": 3
            },
            "propaganda": {
                "resolution": (1024, 1024),
                "generation_time": 200,
                "priority": 2
            }
        }
        
        # Faction asset themes (based on existing lore)
        self.faction_themes = {
            1: {  # Sky Bastion Directorate
                "name": "Directorate",
                "colors": "#2E4053-#161A1D",
                "style": "corporate efficiency, clean lines, blue lighting",
                "architecture": "reinforced corporate structures",
                "atmosphere": "ordered, technological, imposing"
            },
            2: {  # Iron Scavengers
                "name": "IronScavengers", 
                "colors": "#D35400-#7F8C8D",
                "style": "industrial salvage, orange rust, weathered metal",
                "architecture": "improvised fortifications, scavenged materials",
                "atmosphere": "gritty, resourceful, makeshift"
            },
            3: {  # The Seventy-Seven
                "name": "Free77",
                "colors": "#BDC3C7-#34495E",
                "style": "guerrilla networks, urban camouflage, hidden passages",
                "architecture": "concealed structures, resistance hideouts",
                "atmosphere": "secretive, adaptive, rebellious"
            },
            4: {  # Corporate Hegemony
                "name": "CorporateHegemony",
                "colors": "#00C2FF-#0C0F12",
                "style": "corporate hegemony, cyan displays, pristine surfaces",
                "architecture": "gleaming corporate towers, advanced tech",
                "atmosphere": "sterile, powerful, dominating"
            },
            5: {  # Nomad Clans
                "name": "NomadClans",
                "colors": "#AF601A-#6E2C00",
                "style": "environmental adaptation, earth tones, tribal markings",
                "architecture": "mobile structures, organic integration",
                "atmosphere": "nomadic, harmonious with environment, tribal"
            },
            6: {  # Archive Keepers
                "name": "VaultedArchivists",
                "colors": "#8E44AD-#2C3E50",
                "style": "knowledge preservation, purple lighting, ancient tech",
                "architecture": "vault-like repositories, secured knowledge centers",
                "atmosphere": "mysterious, scholarly, protective"
            },
            7: {  # Civic Wardens
                "name": "CivicWardens",
                "colors": "#27AE60-#145A32",
                "style": "community protection, green accents, defensive positions",
                "architecture": "fortified community centers, protective barriers",
                "atmosphere": "protective, community-focused, vigilant"
            }
        }
        
        print("Territorial Asset Integration initialized")
        print(f"Database: {self.db_path}")
        print(f"Output directory: {self.output_dir}")
        
    def get_territorial_state(self) -> List[Dict]:
        """Get current territorial state from CTO database"""
        try:
            connection = sqlite3.connect(str(self.db_path))
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            
            # Query territorial state with faction information
            cursor.execute("""
                SELECT t.id as territory_id, t.territory_name, t.strategic_value,
                       t.contested, t.current_controller_faction_id,
                       f.faction_name, f.palette_hex,
                       COALESCE(fti.influence_level, 0) as control_percentage
                FROM territories t
                LEFT JOIN factions f ON t.current_controller_faction_id = f.id
                LEFT JOIN faction_territorial_influence fti ON t.id = fti.territory_id 
                    AND fti.faction_id = t.current_controller_faction_id
                ORDER BY t.strategic_value DESC
            """)
            
            territories = [dict(row) for row in cursor.fetchall()]
            connection.close()
            
            print(f"Retrieved {len(territories)} territories from database")
            return territories
            
        except Exception as e:
            print(f"Error querying territorial state: {e}")
            return []
    
    def determine_style_variant(self, control_percentage: float, contested: bool) -> str:
        """Determine style variant based on territorial control"""
        if contested:
            return "contested"  # Battle-worn, mixed faction elements
        elif control_percentage >= 80:
            return "dominant"   # Full faction control, pristine
        elif control_percentage >= 60:
            return "established"  # Solid faction control, some wear
        elif control_percentage >= 40:
            return "emerging"   # Early faction control, transitional
        else:
            return "neutral"    # No clear faction dominance
    
    def create_territorial_asset_prompt(self, request: TerritorialAssetRequest) -> str:
        """Create faction-specific prompt for territorial asset generation"""
        
        faction_theme = self.faction_themes.get(request.controlling_faction, self.faction_themes[1])
        base_quality = "masterpiece quality Terminal Grounds"
        
        # Base asset description
        if request.asset_type == "environment":
            asset_desc = f"territorial environment, {faction_theme['name']} controlled zone"
            style_desc = f"{faction_theme['style']}, {faction_theme['architecture']}"
            
        elif request.asset_type == "marker":
            asset_desc = f"territorial control marker, {faction_theme['name']} boundary post"
            style_desc = f"faction insignia with {faction_theme['colors']} color scheme"
            
        elif request.asset_type == "ui_element":
            asset_desc = f"territorial UI interface, {faction_theme['name']} control display"
            style_desc = f"HUD design with {faction_theme['colors']} faction colors"
            
        elif request.asset_type == "propaganda":
            asset_desc = f"faction propaganda display, {faction_theme['name']} messaging"
            style_desc = f"propaganda poster with {faction_theme['colors']} styling"
        else:
            asset_desc = f"territorial asset, {faction_theme['name']} faction element"
            style_desc = f"{faction_theme['style']}"
        
        # Style variant modifiers
        if request.style_variant == "contested":
            condition_mod = ", battle damage from territorial conflicts, contested zone markers, mixed faction elements"
        elif request.style_variant == "dominant":
            condition_mod = f", pristine {faction_theme['name']} control, fully established dominance, no signs of contest"
        elif request.style_variant == "established":
            condition_mod = f", solid {faction_theme['name']} control, well-maintained faction infrastructure"
        elif request.style_variant == "emerging":
            condition_mod = f", early {faction_theme['name']} influence, transitional control markers"
        else:
            condition_mod = ", neutral territory markers, no clear faction dominance"
        
        # Strategic value modifiers
        strategic_value = getattr(request, 'strategic_value', 5)
        if strategic_value >= 8:
            importance_mod = ", high strategic value indicators, heavily fortified structures"
        elif strategic_value >= 5:
            importance_mod = ", moderate strategic importance, standard faction presence"
        else:
            importance_mod = ", outpost-level territorial markers, minimal infrastructure"
        
        prompt = f"{base_quality} {asset_desc}, {style_desc}{condition_mod}{importance_mod}, {faction_theme['atmosphere']}, photorealistic detail, Terminal Grounds aesthetic"
        
        return prompt
    
    def generate_territorial_asset(self, request: TerritorialAssetRequest) -> bool:
        """Generate single territorial asset using proven pipeline parameters"""
        
        try:
            print(f"Generating {request.asset_type} for {request.territory_name} ({self.faction_themes[request.controlling_faction]['name']})")
            
            # Create faction-specific prompt
            prompt = self.create_territorial_asset_prompt(request)
            negative = "blurry, low quality, text, watermark, signature, logo, UI elements, poor composition"
            
            # Get asset configuration
            config = self.asset_configs[request.asset_type]
            
            # Create workflow using proven PERFECTION_PARAMS
            workflow = {
                "1": {
                    "inputs": {
                        "text": prompt,
                        "clip": ["11", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "2": {
                    "inputs": {
                        "text": negative,
                        "clip": ["11", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "3": {
                    "inputs": {
                        "seed": hash(f"{request.territory_id}_{request.controlling_faction}_{request.asset_type}_{request.style_variant}") % 2147483647,
                        "steps": PERFECTION_PARAMS["steps"],
                        "cfg": PERFECTION_PARAMS["cfg"],
                        "sampler_name": PERFECTION_PARAMS["sampler"],
                        "scheduler": PERFECTION_PARAMS["scheduler"],
                        "denoise": 1.0,
                        "model": ["11", 0],
                        "positive": ["1", 0],
                        "negative": ["2", 0],
                        "latent_image": ["8", 0]
                    },
                    "class_type": "KSampler"
                },
                "7": {
                    "inputs": {
                        "samples": ["3", 0],
                        "vae": ["11", 2]
                    },
                    "class_type": "VAEDecode"
                },
                "8": {
                    "inputs": {
                        "width": config["resolution"][0],
                        "height": config["resolution"][1],
                        "batch_size": 1
                    },
                    "class_type": "EmptyLatentImage"
                },
                "9": {
                    "inputs": {
                        "filename_prefix": f"TERRITORIAL_{request.asset_type}_{request.territory_name}_{self.faction_themes[request.controlling_faction]['name']}_{request.style_variant}",
                        "images": ["7", 0]
                    },
                    "class_type": "SaveImage"
                },
                "11": {
                    "inputs": {
                        "ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"
                    },
                    "class_type": "CheckpointLoaderSimple"
                }
            }
            
            # Submit workflow using proven submission method
            result = submit_workflow(workflow, request.territory_name, f"{request.asset_type}_territorial", "Wide", "Ambient")
            
            if result:
                print(f"SUCCESS: Generated {request.asset_type} for {request.territory_name}")
                return True
            else:
                print(f"FAILED: Could not generate {request.asset_type} for {request.territory_name}")
                return False
                
        except Exception as e:
            print(f"ERROR generating territorial asset: {e}")
            return False
    
    def generate_assets_for_territories(self, asset_types: List[str] = None) -> Dict[str, int]:
        """Generate assets for all territories based on current control state"""
        
        if asset_types is None:
            asset_types = ["environment", "marker"]  # Default to key asset types
        
        territories = self.get_territorial_state()
        if not territories:
            print("No territorial data available")
            return {}
        
        results = {"success": 0, "failed": 0, "total": 0}
        
        for territory in territories:
            if not territory["current_controller_faction_id"]:
                continue  # Skip neutral territories
                
            for asset_type in asset_types:
                request = TerritorialAssetRequest(
                    territory_id=territory["territory_id"],
                    territory_name=territory["territory_name"],
                    controlling_faction=territory["current_controller_faction_id"],
                    control_percentage=territory.get("control_percentage", 50),
                    contested=bool(territory["contested"]),
                    asset_type=asset_type,
                    style_variant=self.determine_style_variant(
                        territory.get("control_percentage", 50),
                        bool(territory["contested"])
                    )
                )
                
                results["total"] += 1
                
                if self.generate_territorial_asset(request):
                    results["success"] += 1
                else:
                    results["failed"] += 1
        
        # Calculate success rate
        success_rate = (results["success"] / results["total"] * 100) if results["total"] > 0 else 0
        
        print(f"\nTERRITORIAL ASSET GENERATION COMPLETE")
        print(f"Total assets: {results['total']}")
        print(f"Successful: {results['success']}")
        print(f"Failed: {results['failed']}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Output directory: {self.output_dir}")
        
        return results
    
    def generate_contested_zone_assets(self) -> Dict[str, int]:
        """Generate special assets for contested zones"""
        
        territories = self.get_territorial_state()
        contested_territories = [t for t in territories if t["contested"]]
        
        if not contested_territories:
            print("No contested territories found")
            return {"success": 0, "failed": 0, "total": 0}
        
        results = {"success": 0, "failed": 0, "total": 0}
        
        print(f"Generating contested zone assets for {len(contested_territories)} territories")
        
        for territory in contested_territories:
            # Generate battle-worn environment assets
            request = TerritorialAssetRequest(
                territory_id=territory["territory_id"],
                territory_name=territory["territory_name"],
                controlling_faction=territory["current_controller_faction_id"] or 1,
                control_percentage=territory.get("control_percentage", 50),
                contested=True,
                asset_type="environment",
                style_variant="contested"
            )
            
            results["total"] += 1
            
            if self.generate_territorial_asset(request):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        success_rate = (results["success"] / results["total"] * 100) if results["total"] > 0 else 0
        print(f"Contested zone asset success rate: {success_rate:.1f}%")
        
        return results

def main():
    """Main territorial asset generation execution"""
    print("TERRITORIAL ASSET GENERATION INTEGRATION")
    print("Connecting 92% success rate pipeline with territorial control")
    print("=" * 60)
    
    integration = TerritorialAssetIntegration()
    
    # Test ComfyUI connectivity first
    try:
        import requests
        response = requests.get("http://127.0.0.1:8188/system_stats", timeout=5)
        if response.status_code != 200:
            print("ERROR: ComfyUI API not available")
            return False
    except:
        print("ERROR: ComfyUI API connection failed")
        return False
    
    print("SUCCESS: ComfyUI API connected")
    
    # Generate territorial assets
    if len(sys.argv) > 1 and sys.argv[1] == "--contested-only":
        results = integration.generate_contested_zone_assets()
    else:
        asset_types = ["environment", "marker", "propaganda"]
        results = integration.generate_assets_for_territories(asset_types)
    
    # Evaluate success
    success_rate = (results["success"] / results["total"] * 100) if results["total"] > 0 else 0
    
    if success_rate >= 85:  # Maintain high success rate standard
        print("\nSUCCESS: Territorial asset pipeline operational")
        print("Integration with territorial control system complete")
        return True
    else:
        print("\nISSUES: Asset generation success rate below standard")
        return False

if __name__ == "__main__":
    main()