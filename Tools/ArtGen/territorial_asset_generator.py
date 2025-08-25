#!/usr/bin/env python3
"""
Terminal Grounds Territorial Asset Generator
CTO Implementation - Pipeline v2.0 Integration

Extends the proven 92% success rate system for territorial-specific assets
Uses heun/normal/CFG 3.2/25 steps parameters for consistent AAA quality
Integrates with faction data from Factions.csv for accurate territorial representation
"""

import json
import os
import sys
import time
import csv
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
from pathlib import Path

# Add the parent directory to the path to import existing modules
sys.path.append(str(Path(__file__).parent))
from terminal_grounds_generator import PERFECT_PARAMS, submit_workflow

# TERRITORIAL ASSET SPECIFICATIONS

@dataclass
class FactionData:
    """Faction data structure matching Factions.csv"""
    faction_name: str
    discipline: float
    aggression: float
    tech_level: float
    loot_tier_bias: Dict[str, float]
    vehicle_affinity: Dict[str, float]
    event_preference: Dict[str, str]
    palette_hex: str
    emblem_ref: str
    notes: str

@dataclass
class TerritorialAssetSpec:
    """Specification for territorial asset generation"""
    asset_type: str
    territory_name: str
    controlling_faction: str
    contested: bool
    strategic_value: int
    resolution: Tuple[int, int]
    style_variant: str

class TerritorialAssetGenerator:
    """
    Generates territorial assets using proven Pipeline v2.0 parameters
    Maintains 92% success rate while adding territorial context
    """
    
    def __init__(self):
        self.comfyui_url = "http://127.0.0.1:8188"
        self.output_dir = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output")
        self.factions = self.load_faction_data()
        
        # Territorial asset workflow templates
        self.territorial_workflows = {
            "territory_flag": self.create_territory_flag_workflow,
            "control_structure": self.create_control_structure_workflow,
            "boundary_marker": self.create_boundary_marker_workflow,
            "territorial_ui": self.create_territorial_ui_workflow,
            "influence_overlay": self.create_influence_overlay_workflow
        }
        
        print(f"✅ Territorial Asset Generator initialized")
        print(f"✅ Loaded {len(self.factions)} factions")
        print(f"✅ Output directory: {self.output_dir}")

    def load_faction_data(self) -> Dict[str, FactionData]:
        """Load faction data from Factions.csv"""
        factions = {}
        factions_csv_path = Path("C:/Users/Zachg/Terminal-Grounds/Data/Tables/Factions.csv")
        
        if not factions_csv_path.exists():
            print(f"⚠️  Factions.csv not found at {factions_csv_path}")
            return factions
        
        try:
            with open(factions_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not row['Id'] or row['Id'] == '':  # Skip empty rows
                        continue
                        
                    # Parse JSON fields
                    loot_bias = self.parse_bias_field(row['LootTierBias'])
                    vehicle_affinity = self.parse_bias_field(row['VehicleAffinity'])
                    event_preference = self.parse_preference_field(row['EventPreference'])
                    
                    faction_data = FactionData(
                        faction_name=row['Id'],
                        discipline=float(row['Discipline']),
                        aggression=float(row['Aggression']),
                        tech_level=float(row['TechLevel']),
                        loot_tier_bias=loot_bias,
                        vehicle_affinity=vehicle_affinity,
                        event_preference=event_preference,
                        palette_hex=row['PaletteHex'],
                        emblem_ref=row['EmblemRef'],
                        notes=row['Notes']
                    )
                    
                    factions[faction_data.faction_name] = faction_data
                    
        except Exception as e:
            print(f"❌ Error loading faction data: {e}")
            
        return factions

    def parse_bias_field(self, bias_str: str) -> Dict[str, float]:
        """Parse bias field like 'Field:0.7;Splice:0.25;Monolith:0.05'"""
        bias_dict = {}
        if bias_str:
            pairs = bias_str.split(';')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':')
                    bias_dict[key.strip()] = float(value.strip())
        return bias_dict

    def parse_preference_field(self, pref_str: str) -> Dict[str, str]:
        """Parse preference field like 'ConvoyWar:0.7'"""
        pref_dict = {}
        if pref_str:
            pairs = pref_str.split(';')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':')
                    pref_dict[key.strip()] = value.strip()
        return pref_dict

    def generate_territorial_assets(self, territory_specs: List[TerritorialAssetSpec]) -> List[str]:
        """
        Generate territorial assets for specified territories
        Returns list of generated asset filenames
        """
        generated_assets = []
        
        for spec in territory_specs:
            print(f"\n🎯 Generating {spec.asset_type} for {spec.territory_name}")
            
            if spec.controlling_faction not in self.factions:
                print(f"❌ Unknown faction: {spec.controlling_faction}")
                continue
            
            faction_data = self.factions[spec.controlling_faction]
            
            # Generate asset using appropriate workflow
            if spec.asset_type in self.territorial_workflows:
                workflow_func = self.territorial_workflows[spec.asset_type]
                workflow = workflow_func(spec, faction_data)
                
                # Generate asset with proven parameters
                asset_filename = self.execute_territorial_workflow(workflow, spec)
                if asset_filename:
                    generated_assets.append(asset_filename)
                    
            else:
                print(f"❌ Unknown asset type: {spec.asset_type}")
        
        return generated_assets

    def create_territory_flag_workflow(self, spec: TerritorialAssetSpec, faction: FactionData) -> dict:
        """
        Create workflow for territorial flags
        Shows faction control with appropriate styling
        """
        
        # Extract colors from palette
        colors = faction.palette_hex.split('-')
        primary_color = colors[0] if colors else "#FFFFFF"
        secondary_color = colors[1] if len(colors) > 1 else primary_color
        
        # Generate faction-specific flag prompt
        flag_prompt = self.generate_flag_prompt(spec, faction, primary_color, secondary_color)
        
        # Use proven workflow structure (7-node pattern)
        workflow = {
            "1": {
                "inputs": {
                    "text": flag_prompt,
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "2": {
                "inputs": {
                    "text": "blurry, low quality, text, watermark, signature, username, logo, brand name, copyright",
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "seed": spec.strategic_value * 1000,  # Deterministic seed based on strategic value
                    "steps": PERFECT_PARAMS["steps"],
                    "cfg": PERFECT_PARAMS["cfg"],
                    "sampler_name": PERFECT_PARAMS["sampler"],
                    "scheduler": PERFECT_PARAMS["scheduler"],
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
                    "width": 1024,  # Square format for flags
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "9": {
                "inputs": {
                    "filename_prefix": f"territorial_flag_{spec.territory_name.lower().replace(' ', '_')}_{faction.faction_name.lower().replace(' ', '_')}",
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
        
        return workflow

    def generate_flag_prompt(self, spec: TerritorialAssetSpec, faction: FactionData, 
                           primary_color: str, secondary_color: str) -> str:
        """Generate faction-specific flag prompt"""
        
        # Base flag description
        base_prompt = f"masterpiece quality Terminal Grounds territorial flag, {faction.faction_name} faction control marker"
        
        # Add faction-specific elements based on their characteristics
        if faction.faction_name == "Sky Bastion Directorate":
            faction_elements = f"corporate military flag with directorate insignia, blue and dark gray color scheme {primary_color} {secondary_color}, chevron design, authority symbols"
        elif faction.faction_name == "Iron Scavengers":
            faction_elements = f"rugged scavenger banner, orange and gray weathered design {primary_color} {secondary_color}, salvage symbols, worn industrial aesthetic"
        elif faction.faction_name == "The Seventy-Seven":
            faction_elements = f"mercenary contractor flag, red circular emblem {primary_color} {secondary_color}, professional military design, contractor insignia"
        elif faction.faction_name == "Corporate Hegemony":
            faction_elements = f"high-tech corporate banner, cyan and black design {primary_color} {secondary_color}, hexagonal patterns, brand warfare aesthetics"
        elif faction.faction_name == "Nomad Clans":
            faction_elements = f"tribal nomad banner, brown and orange weathered cloth {primary_color} {secondary_color}, intricate clan markings, mobile adaptation symbols"
        elif faction.faction_name == "Archive Keepers":
            faction_elements = f"information warfare flag, purple and dark blue design {primary_color} {secondary_color}, data stream patterns, archive symbols"
        elif faction.faction_name == "Civic Wardens":
            faction_elements = f"community defense banner, green and dark colors {primary_color} {secondary_color}, protective symbols, civilian organization aesthetics"
        else:
            faction_elements = f"faction banner with {primary_color} and {secondary_color} color scheme"
        
        # Territory status modifiers
        if spec.contested:
            status_modifier = ", battle-worn with damage from recent conflicts, contested territory markers"
        else:
            status_modifier = ", well-maintained showing established control, secure territory markers"
        
        # Strategic value modifiers
        if spec.strategic_value >= 8:
            importance_modifier = ", high-value strategic location indicators, reinforced flagpole"
        elif spec.strategic_value >= 5:
            importance_modifier = ", moderate strategic importance markers"
        else:
            importance_modifier = ", outpost-level territorial marker"
        
        prompt = f"{base_prompt}, {faction_elements}{status_modifier}{importance_modifier}, photorealistic detail, Terminal Grounds aesthetic"
        
        return prompt

    def create_control_structure_workflow(self, spec: TerritorialAssetSpec, faction: FactionData) -> dict:
        """Create workflow for control structures (bases, outposts, checkpoints)"""
        
        structure_prompt = self.generate_structure_prompt(spec, faction)
        
        # Use standard workflow with appropriate resolution
        workflow = self.create_base_workflow(structure_prompt, spec)
        return workflow

    def create_boundary_marker_workflow(self, spec: TerritorialAssetSpec, faction: FactionData) -> dict:
        """Create workflow for territorial boundary markers"""
        
        marker_prompt = self.generate_boundary_prompt(spec, faction)
        workflow = self.create_base_workflow(marker_prompt, spec)
        return workflow

    def create_territorial_ui_workflow(self, spec: TerritorialAssetSpec, faction: FactionData) -> dict:
        """Create workflow for territorial UI elements"""
        
        ui_prompt = self.generate_ui_prompt(spec, faction)
        workflow = self.create_base_workflow(ui_prompt, spec)
        return workflow

    def create_influence_overlay_workflow(self, spec: TerritorialAssetSpec, faction: FactionData) -> dict:
        """Create workflow for territorial influence overlays"""
        
        overlay_prompt = self.generate_overlay_prompt(spec, faction)
        workflow = self.create_base_workflow(overlay_prompt, spec)
        return workflow

    def create_base_workflow(self, prompt: str, spec: TerritorialAssetSpec) -> dict:
        """Create base workflow using proven parameters"""
        
        workflow = {
            "1": {
                "inputs": {
                    "text": prompt,
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "2": {
                "inputs": {
                    "text": "blurry, low quality, text, watermark, signature, username, logo, brand name, copyright, UI elements, game interface",
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "seed": hash(f"{spec.territory_name}_{spec.controlling_faction}_{spec.asset_type}") % 2147483647,
                    "steps": PERFECT_PARAMS["steps"],
                    "cfg": PERFECT_PARAMS["cfg"],
                    "sampler_name": PERFECT_PARAMS["sampler"],
                    "scheduler": PERFECT_PARAMS["scheduler"],
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
                    "width": spec.resolution[0],
                    "height": spec.resolution[1],
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "9": {
                "inputs": {
                    "filename_prefix": f"territorial_{spec.asset_type}_{spec.territory_name.lower().replace(' ', '_')}_{spec.controlling_faction.lower().replace(' ', '_')}",
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
        
        return workflow

    def generate_structure_prompt(self, spec: TerritorialAssetSpec, faction: FactionData) -> str:
        """Generate control structure prompt"""
        return f"masterpiece quality Terminal Grounds {faction.faction_name} control structure in {spec.territory_name}, faction military outpost with {faction.palette_hex} color scheme, Terminal Grounds aesthetic, photorealistic detail"

    def generate_boundary_prompt(self, spec: TerritorialAssetSpec, faction: FactionData) -> str:
        """Generate boundary marker prompt"""
        return f"Terminal Grounds territorial boundary marker, {faction.faction_name} faction border post, {faction.palette_hex} colors, warning signs and territorial indicators, photorealistic"

    def generate_ui_prompt(self, spec: TerritorialAssetSpec, faction: FactionData) -> str:
        """Generate UI element prompt"""
        return f"Terminal Grounds territorial UI element, {faction.faction_name} faction interface, {faction.palette_hex} color scheme, clean HUD design, minimal UI aesthetic"

    def generate_overlay_prompt(self, spec: TerritorialAssetSpec, faction: FactionData) -> str:
        """Generate influence overlay prompt"""
        return f"Terminal Grounds territorial influence overlay, {faction.faction_name} faction control visualization, {faction.palette_hex} colors, map overlay design, tactical interface"

    def execute_territorial_workflow(self, workflow: dict, spec: TerritorialAssetSpec) -> Optional[str]:
        """Execute workflow using proven ComfyUI submission method"""
        
        try:
            # Use the proven submit_workflow function from terminal_grounds_generator
            result = submit_workflow(self.comfyui_url, workflow)
            
            if result and "filename" in result:
                print(f"✅ Generated: {result['filename']}")
                return result["filename"]
            else:
                print(f"❌ Generation failed for {spec.asset_type}")
                return None
                
        except Exception as e:
            print(f"❌ Error executing workflow: {e}")
            return None

def main():
    """Main function for territorial asset generation"""
    
    generator = TerritorialAssetGenerator()
    
    # Example territorial asset specifications
    territorial_specs = [
        TerritorialAssetSpec(
            asset_type="territory_flag",
            territory_name="Metro Region",
            controlling_faction="Civic Wardens",
            contested=False,
            strategic_value=8,
            resolution=(1024, 1024),
            style_variant="established_control"
        ),
        TerritorialAssetSpec(
            asset_type="territory_flag",
            territory_name="Tech Wastes",
            controlling_faction="Iron Scavengers",
            contested=True,
            strategic_value=6,
            resolution=(1024, 1024),
            style_variant="contested_territory"
        ),
        TerritorialAssetSpec(
            asset_type="control_structure",
            territory_name="IEZ Facility",
            controlling_faction="Sky Bastion Directorate",
            contested=False,
            strategic_value=9,
            resolution=(1536, 864),
            style_variant="military_outpost"
        )
    ]
    
    # Generate territorial assets
    generated_assets = generator.generate_territorial_assets(territorial_specs)
    
    print(f"\n🎯 Territorial asset generation complete!")
    print(f"✅ Generated {len(generated_assets)} assets:")
    for asset in generated_assets:
        print(f"   • {asset}")

if __name__ == "__main__":
    main()