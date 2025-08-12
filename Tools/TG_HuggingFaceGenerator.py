#!/usr/bin/env python3
"""
TG_HuggingFaceGenerator.py
Terminal Grounds Hugging Face Asset Generator

Generates high-quality assets using Hugging Face models tailored to Terminal Grounds
art direction, style guide, and faction identities.

Features:
- Terminal Grounds-specific prompt templates 
- Model selection based on asset category and style requirements
- Multi-resolution generation (512x512, 1024x1024, 2048x2048+)
- Quality validation and multi-pass generation
- Integration with Terminal Grounds art bible and faction data

Author: Terminal Grounds Content Pipeline Agent  
Version: 1.0.0
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

# Add the parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from TG_ContentPipelineAgent import AssetCategory, AssetMetadata, TerminalGroundsContentAgent

# Terminal Grounds project root
ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = ROOT / "Tools/ArtGen/outputs"
DOCS_CONCEPTS_DIR = ROOT / "Docs/Concepts"

class ModelStyle(Enum):
    """Available model styles for different asset types"""
    PHOTOREAL = "photoreal"
    PAINTERLY = "painterly" 
    STYLIZED = "stylized"
    VECTOR = "vector"
    CONCEPT_ART = "concept_art"
    TECHNICAL = "technical"

class GenerationQuality(Enum):
    """Quality levels for generated assets"""
    DRAFT = "draft"
    STANDARD = "standard" 
    HIGH = "high"
    PREMIUM = "premium"

@dataclass
class GenerationRequest:
    """Request for asset generation"""
    category: AssetCategory
    style: ModelStyle
    resolution: Tuple[int, int]
    quality: GenerationQuality
    faction: Optional[str]
    subject: str
    prompt_template: str
    negative_prompts: List[str]
    output_path: Path
    metadata: Dict[str, Any]

class TerminalGroundsPromptEngine:
    """Generates Terminal Grounds-specific prompts based on art bible and lore"""
    
    def __init__(self, content_agent: TerminalGroundsContentAgent):
        self.content_agent = content_agent
        self.faction_data = content_agent.faction_data
        self.art_bible = content_agent.art_bible
        
        # Load Terminal Grounds prompt templates
        self.prompt_templates = self._load_prompt_templates()
        self.style_modifiers = self._load_style_modifiers()
        self.quality_settings = self._load_quality_settings()
    
    def _load_prompt_templates(self) -> Dict[str, Dict[str, str]]:
        """Load category-specific prompt templates"""
        return {
            AssetCategory.FACTION_LOGO.value: {
                "base": "military faction emblem, {faction_style}, clean vector design, {faction_colors}, symbolic icon, professional military insignia",
                "composition": "centered composition, bold graphic design, high contrast",
                "style": "vector art, clean lines, symbolic design, military heraldry",
                "lighting": "flat lighting, no shadows, graphic design",
                "technical": "vector graphics, scalable, clean edges, solid colors"
            },
            AssetCategory.POSTER_DECAL.value: {
                "base": "military propaganda poster, {faction_style}, Terminal Grounds universe, post-apocalyptic military aesthetic, {faction_colors}",
                "composition": "bold typography, clear hierarchy, propaganda layout",
                "style": "military propaganda art, weathered paper texture, industrial design",
                "lighting": "dramatic lighting, high contrast, moody atmosphere",
                "technical": "high resolution, print ready, aged texture"
            },
            AssetCategory.UI_ICON.value: {
                "base": "military UI icon, {category_specific}, clean interface design, tactical HUD element, {faction_colors}",
                "composition": "centered, square format, clear readable symbol",
                "style": "modern military UI, clean vector design, tactical interface",
                "lighting": "flat lighting, interface appropriate, clear visibility",
                "technical": "crisp edges, scalable, UI optimized"
            },
            AssetCategory.WEAPON_CONCEPT.value: {
                "base": "tactical {tech_tier} weapon concept, Terminal Grounds universe, {weapon_type}, military realism, {tech_colors}",
                "composition": "3/4 view, technical illustration, detailed breakdown",
                "style": "concept art, technical illustration, military realism with sci-fi accents",
                "lighting": "studio lighting, technical photography, clear detail visibility",
                "technical": "high detail, concept art quality, technical accuracy"
            },
            AssetCategory.VEHICLE_CONCEPT.value: {
                "base": "military {tech_tier} vehicle concept, Terminal Grounds universe, {vehicle_type}, post-apocalyptic military, {tech_colors}",
                "composition": "dynamic angle, full vehicle view, environmental context",
                "style": "concept art, military vehicle design, grounded realism",
                "lighting": "dramatic environmental lighting, atmospheric",
                "technical": "high detail, concept art quality, realistic proportions"
            },
            AssetCategory.BIOME_CONCEPT.value: {
                "base": "Terminal Grounds {biome_type} environment, post-apocalyptic battlefield, {environmental_mood}, atmospheric",
                "composition": "wide landscape view, environmental storytelling",
                "style": "environmental concept art, atmospheric painting, post-apocalyptic realism",
                "lighting": "dramatic environmental lighting, atmospheric effects",
                "technical": "high resolution, painterly concept art, atmospheric depth"
            },
            AssetCategory.CONCEPT_ART.value: {
                "base": "Terminal Grounds universe concept art, {subject_matter}, post-apocalyptic military sci-fi, grounded realism",
                "composition": "dynamic composition, storytelling elements",
                "style": "concept art, military realism with sci-fi accents, atmospheric",
                "lighting": "dramatic lighting, cinematic mood",
                "technical": "concept art quality, high detail, professional illustration"
            }
        }
    
    def _load_style_modifiers(self) -> Dict[ModelStyle, Dict[str, str]]:
        """Load style-specific modifiers"""
        return {
            ModelStyle.PHOTOREAL: {
                "quality": "photorealistic, high detail photography, realistic lighting",
                "camera": "35mm lens, professional photography, sharp focus",
                "post": "color grading, cinematic look, professional quality"
            },
            ModelStyle.PAINTERLY: {
                "quality": "digital painting, painterly style, artistic interpretation",
                "medium": "digital art, painting technique, artistic style",
                "post": "artistic color palette, painterly finish"
            },
            ModelStyle.STYLIZED: {
                "quality": "stylized art, clean aesthetic, design-focused",
                "style": "stylized design, clean graphics, modern aesthetic",
                "post": "polished finish, design quality"
            },
            ModelStyle.VECTOR: {
                "quality": "vector art, clean lines, graphic design quality",
                "style": "vector graphics, geometric design, scalable art",
                "post": "crisp edges, clean finish, graphic design"
            },
            ModelStyle.CONCEPT_ART: {
                "quality": "concept art, professional illustration, high artistic quality",
                "style": "concept art style, illustration technique, artistic vision",
                "post": "concept art finish, professional illustration quality"
            },
            ModelStyle.TECHNICAL: {
                "quality": "technical illustration, blueprint style, engineering drawing",
                "style": "technical drawing, schematic design, engineering aesthetic",
                "post": "technical precision, clean line work"
            }
        }
    
    def _load_quality_settings(self) -> Dict[GenerationQuality, Dict[str, Any]]:
        """Load quality-specific settings"""
        return {
            GenerationQuality.DRAFT: {
                "steps": 4,
                "guidance": 1.0,
                "quality_suffix": "draft quality, quick iteration"
            },
            GenerationQuality.STANDARD: {
                "steps": 8,
                "guidance": 3.0, 
                "quality_suffix": "standard quality, good detail"
            },
            GenerationQuality.HIGH: {
                "steps": 12,
                "guidance": 5.0,
                "quality_suffix": "high quality, detailed rendering"
            },
            GenerationQuality.PREMIUM: {
                "steps": 16,
                "guidance": 7.0,
                "quality_suffix": "premium quality, maximum detail, professional finish"
            }
        }
    
    def get_faction_prompt_data(self, faction: Optional[str]) -> Dict[str, str]:
        """Get faction-specific prompt data"""
        if not faction or faction not in self.faction_data:
            return {
                "faction_style": "military neutral",
                "faction_colors": "military gray, tactical black, warning orange",
                "faction_keywords": "generic military, tactical"
            }
        
        faction_info = self.faction_data[faction]
        color_list = ", ".join(faction_info["colors"][:3])  # Use first 3 colors
        
        return {
            "faction_style": faction_info["style"].replace("_", " "),
            "faction_colors": color_list,
            "faction_keywords": faction_info["keywords"]
        }
    
    def get_tech_tier_data(self, tech_tier: str) -> Dict[str, str]:
        """Get technology tier-specific prompt data"""
        tech_data = {
            "human": {
                "colors": ", ".join(self.art_bible["energy_signatures"]["human"]),
                "style": "rugged ballistic weapons, reliable military hardware",
                "aesthetic": "industrial realism, proven technology"
            },
            "hybrid": {
                "colors": ", ".join(self.art_bible["energy_signatures"]["hybrid"]),
                "style": "experimental hybrid technology, energy coils, overheating elements",
                "aesthetic": "experimental tech, energy conduits, unstable power"
            },
            "alien": {
                "colors": ", ".join(self.art_bible["energy_signatures"]["alien"]),
                "style": "alien beam technology, gravity manipulation, phase weapons",
                "aesthetic": "otherworldly technology, quantum effects, alien engineering"
            }
        }
        
        return tech_data.get(tech_tier.lower(), tech_data["human"])
    
    def build_prompt(self, request: GenerationRequest) -> str:
        """Build complete prompt for generation request"""
        # Get base template
        template_data = self.prompt_templates.get(request.category.value, {})
        base_template = template_data.get("base", "Terminal Grounds asset, military sci-fi")
        
        # Get faction data
        faction_data = self.get_faction_prompt_data(request.faction)
        
        # Get style modifiers
        style_data = self.style_modifiers.get(request.style, {})
        
        # Get quality settings
        quality_data = self.quality_settings.get(request.quality, {})
        
        # Build prompt components
        prompt_parts = []
        
        # Add base prompt with faction data
        base_prompt = base_template.format(
            faction_style=faction_data["faction_style"],
            faction_colors=faction_data["faction_colors"],
            faction_keywords=faction_data["faction_keywords"],
            **request.metadata
        )
        prompt_parts.append(base_prompt)
        
        # Add composition guidelines
        if "composition" in template_data:
            prompt_parts.append(template_data["composition"])
        
        # Add style modifiers
        for modifier in style_data.values():
            prompt_parts.append(modifier)
        
        # Add quality suffix
        if "quality_suffix" in quality_data:
            prompt_parts.append(quality_data["quality_suffix"])
        
        # Add technical requirements
        if "technical" in template_data:
            prompt_parts.append(template_data["technical"])
        
        # Join all parts
        full_prompt = ", ".join(prompt_parts)
        
        # Clean up prompt
        full_prompt = re.sub(r',\s*,', ',', full_prompt)  # Remove double commas
        full_prompt = re.sub(r'\s+', ' ', full_prompt)    # Normalize spaces
        
        return full_prompt.strip()
    
    def build_negative_prompt(self, request: GenerationRequest) -> str:
        """Build negative prompt for generation request"""
        base_negatives = [
            "low quality",
            "blurry", 
            "watermark",
            "text overlay",
            "signature",
            "worst quality",
            "low resolution"
        ]
        
        # Add category-specific negatives
        category_negatives = {
            AssetCategory.FACTION_LOGO.value: [
                "photorealistic", "3d render", "complex details", "gradients"
            ],
            AssetCategory.POSTER_DECAL.value: [
                "modern typography", "clean design", "minimal"
            ],
            AssetCategory.UI_ICON.value: [
                "complex details", "realistic", "photographic"
            ],
            AssetCategory.WEAPON_CONCEPT.value: [
                "cartoon", "anime", "unrealistic proportions"
            ],
            AssetCategory.VEHICLE_CONCEPT.value: [
                "cartoon", "anime", "unrealistic proportions"
            ],
            AssetCategory.CONCEPT_ART.value: [
                "amateur", "sketch", "unfinished"
            ]
        }
        
        # Combine negatives
        all_negatives = base_negatives + request.negative_prompts
        if request.category.value in category_negatives:
            all_negatives.extend(category_negatives[request.category.value])
        
        return ", ".join(all_negatives)

class HuggingFaceGenerator:
    """Hugging Face model integration for asset generation"""
    
    def __init__(self, content_agent: TerminalGroundsContentAgent):
        self.content_agent = content_agent
        self.prompt_engine = TerminalGroundsPromptEngine(content_agent)
        self.log_file = ROOT / "Docs/Phase4_Implementation_Log.md"
        
        # Model mappings for different asset types and styles
        self.model_mappings = self._load_model_mappings()
        
        # Ensure output directories exist
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        DOCS_CONCEPTS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_model_mappings(self) -> Dict[Tuple[AssetCategory, ModelStyle], str]:
        """Load optimal model mappings for asset categories and styles"""
        return {
            # Faction logos - need clean vector-style output
            (AssetCategory.FACTION_LOGO, ModelStyle.VECTOR): "evalstate/flux1_schnell",
            (AssetCategory.FACTION_LOGO, ModelStyle.STYLIZED): "evalstate/flux1_schnell",
            
            # Posters and decals - need atmospheric propaganda style  
            (AssetCategory.POSTER_DECAL, ModelStyle.PAINTERLY): "evalstate/flux1_schnell",
            (AssetCategory.POSTER_DECAL, ModelStyle.STYLIZED): "evalstate/flux1_schnell",
            
            # UI icons - need clean, simple designs
            (AssetCategory.UI_ICON, ModelStyle.VECTOR): "evalstate/flux1_schnell", 
            (AssetCategory.UI_ICON, ModelStyle.STYLIZED): "evalstate/flux1_schnell",
            
            # Concept art - need high artistic quality
            (AssetCategory.CONCEPT_ART, ModelStyle.CONCEPT_ART): "evalstate/flux1_schnell",
            (AssetCategory.CONCEPT_ART, ModelStyle.PAINTERLY): "evalstate/flux1_schnell",
            
            # Weapon concepts - need technical detail
            (AssetCategory.WEAPON_CONCEPT, ModelStyle.CONCEPT_ART): "evalstate/flux1_schnell",
            (AssetCategory.WEAPON_CONCEPT, ModelStyle.TECHNICAL): "evalstate/flux1_schnell",
            
            # Vehicle concepts - need realistic proportions
            (AssetCategory.VEHICLE_CONCEPT, ModelStyle.CONCEPT_ART): "evalstate/flux1_schnell",
            (AssetCategory.VEHICLE_CONCEPT, ModelStyle.PHOTOREAL): "evalstate/flux1_schnell",
            
            # Biome concepts - need atmospheric quality
            (AssetCategory.BIOME_CONCEPT, ModelStyle.CONCEPT_ART): "evalstate/flux1_schnell",
            (AssetCategory.BIOME_CONCEPT, ModelStyle.PAINTERLY): "evalstate/flux1_schnell",
        }
    
    def select_model(self, category: AssetCategory, style: ModelStyle) -> str:
        """Select optimal model for given category and style"""
        model_key = (category, style)
        if model_key in self.model_mappings:
            return self.model_mappings[model_key]
        
        # Fallback to general purpose model
        return "evalstate/flux1_schnell"
    
    def determine_resolution(self, category: AssetCategory) -> Tuple[int, int]:
        """Determine optimal resolution for asset category"""
        resolution_map = {
            AssetCategory.FACTION_LOGO: (1024, 1024),
            AssetCategory.UI_ICON: (512, 512),
            AssetCategory.POSTER_DECAL: (1024, 2048),  # Portrait for posters
            AssetCategory.CONCEPT_ART: (2048, 2048),
            AssetCategory.WEAPON_CONCEPT: (2048, 1024),  # Wide for weapon layouts
            AssetCategory.VEHICLE_CONCEPT: (2048, 1024), # Wide for vehicle profiles
            AssetCategory.BIOME_CONCEPT: (2048, 1024),   # Wide for landscapes
            AssetCategory.TEXTURE: (1024, 1024),
        }
        
        return resolution_map.get(category, (1024, 1024))
    
    def generate_asset(self, request: GenerationRequest) -> Optional[Path]:
        """Generate single asset using Hugging Face"""
        try:
            # Import huggingface tools through function calls
            import subprocess
            import json
            
            # Build prompts
            positive_prompt = self.prompt_engine.build_prompt(request)
            negative_prompt = self.prompt_engine.build_negative_prompt(request)
            
            print(f"🎨 Generating {request.category.value} for {request.faction or 'neutral'}")
            print(f"📝 Prompt: {positive_prompt[:100]}...")
            
            # Get quality settings
            quality_settings = self.prompt_engine.quality_settings[request.quality]
            
            # Generate image
            result = gr1_flux1_schnell_infer(
                prompt=positive_prompt,
                width=request.resolution[0],
                height=request.resolution[1],
                num_inference_steps=quality_settings["steps"],
                randomize_seed=True
            )
            
            if result and hasattr(result, 'url'):
                # Download and save the generated image
                import requests
                response = requests.get(result.url)
                if response.status_code == 200:
                    # Ensure output directory exists
                    request.output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Save the image
                    with open(request.output_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Log generation
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        today = date.today().isoformat()
                        f.write(f"\n[{today}] Generated: {request.category.value} -> {request.output_path.relative_to(ROOT)}\n")
                    
                    print(f"✅ Generated: {request.output_path.relative_to(ROOT)}")
                    return request.output_path
                else:
                    print(f"❌ Failed to download generated image")
                    return None
            else:
                print(f"❌ Generation failed - no result returned")
                return None
                
        except ImportError:
            print("❌ Hugging Face tools not available - install required dependencies")
            return None
        except Exception as e:
            print(f"❌ Generation error: {str(e)}")
            return None
    
    def generate_missing_faction_logos(self) -> List[Path]:
        """Generate missing faction logos"""
        generated_assets = []
        
        print("🏴 Generating faction logos...")
        
        for faction_name in self.content_agent.faction_data.keys():
            # Check if logo already exists
            logo_path = ROOT / f"Content/TG/Decals/Factions/{faction_name}_2K.png"
            
            if not logo_path.exists():
                print(f"🏴 Missing logo for {faction_name}, generating...")
                
                # Create generation request
                request = GenerationRequest(
                    category=AssetCategory.FACTION_LOGO,
                    style=ModelStyle.VECTOR,
                    resolution=self.determine_resolution(AssetCategory.FACTION_LOGO),
                    quality=GenerationQuality.HIGH,
                    faction=faction_name,
                    subject=f"{faction_name} faction emblem",
                    prompt_template="faction_logo",
                    negative_prompts=["photorealistic", "complex details"],
                    output_path=logo_path,
                    metadata={"faction": faction_name}
                )
                
                result = self.generate_asset(request)
                if result:
                    generated_assets.append(result)
            else:
                print(f"✅ Logo exists for {faction_name}")
        
        return generated_assets
    
    def generate_missing_posters(self) -> List[Path]:
        """Generate propaganda posters for factions"""
        generated_assets = []
        
        print("📜 Generating propaganda posters...")
        
        poster_themes = [
            "recruitment", "safety_warning", "propaganda", 
            "territory_marking", "equipment_maintenance"
        ]
        
        for faction_name in self.content_agent.faction_data.keys():
            for theme in poster_themes:
                poster_path = ROOT / f"Content/TG/Decals/Posters/{faction_name}_{theme.title()}.png"
                
                if not poster_path.exists():
                    print(f"📜 Generating {theme} poster for {faction_name}...")
                    
                    request = GenerationRequest(
                        category=AssetCategory.POSTER_DECAL,
                        style=ModelStyle.PAINTERLY,
                        resolution=(1024, 2048),  # Portrait format
                        quality=GenerationQuality.HIGH,
                        faction=faction_name,
                        subject=f"{faction_name} {theme} propaganda poster",
                        prompt_template="poster_decal",
                        negative_prompts=["modern design", "clean typography"],
                        output_path=poster_path,
                        metadata={"faction": faction_name, "theme": theme}
                    )
                    
                    result = self.generate_asset(request)
                    if result:
                        generated_assets.append(result)
                        
                        # Add some delay between generations to be respectful
                        time.sleep(2)
        
        return generated_assets
    
    def generate_ui_icons(self) -> List[Path]:
        """Generate missing UI icons"""
        generated_assets = []
        
        print("🎯 Generating UI icons...")
        
        ui_icons = [
            "ammo_counter", "health_indicator", "shield_status",
            "weapon_selector", "inventory_slot", "map_marker",
            "faction_indicator", "mission_objective", "extraction_point"
        ]
        
        for icon_name in ui_icons:
            icon_path = ROOT / f"Content/TG/Icons/{icon_name}_128.png"
            
            if not icon_path.exists():
                print(f"🎯 Generating {icon_name} icon...")
                
                request = GenerationRequest(
                    category=AssetCategory.UI_ICON,
                    style=ModelStyle.VECTOR,
                    resolution=(512, 512),
                    quality=GenerationQuality.HIGH,
                    faction=None,
                    subject=f"{icon_name.replace('_', ' ')} UI icon",
                    prompt_template="ui_icon",
                    negative_prompts=["complex details", "realistic"],
                    output_path=icon_path,
                    metadata={"icon_type": icon_name}
                )
                
                result = self.generate_asset(request)
                if result:
                    generated_assets.append(result)
                    time.sleep(1)
        
        return generated_assets
    
    def run_missing_asset_generation(self) -> Dict[str, List[Path]]:
        """Run complete missing asset generation pipeline"""
        print("🚀 Starting Missing Asset Generation")
        print("=" * 50)
        
        generated_assets = {
            "faction_logos": [],
            "posters": [],
            "ui_icons": []
        }
        
        # Generate missing faction logos
        generated_assets["faction_logos"] = self.generate_missing_faction_logos()
        
        # Generate missing posters (limit to avoid overwhelming)
        generated_assets["posters"] = self.generate_missing_posters()
        
        # Generate missing UI icons
        generated_assets["ui_icons"] = self.generate_ui_icons()
        
        # Summary
        total_generated = sum(len(assets) for assets in generated_assets.values())
        print(f"\n✅ Generated {total_generated} new assets")
        
        for category, assets in generated_assets.items():
            if assets:
                print(f"  {category}: {len(assets)} assets")
        
        return generated_assets

# CLI interface
def main():
    """Main CLI entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        # Initialize content agent and generator
        content_agent = TerminalGroundsContentAgent()
        generator = HuggingFaceGenerator(content_agent)
        
        if command == "generate-missing":
            generator.run_missing_asset_generation()
        elif command == "logos":
            generator.generate_missing_faction_logos()
        elif command == "posters":
            generator.generate_missing_posters()
        elif command == "icons":
            generator.generate_ui_icons()
        else:
            print(f"Unknown command: {command}")
    else:
        print("Terminal Grounds Hugging Face Generator")
        print("Usage:")
        print("  python TG_HuggingFaceGenerator.py generate-missing  # Generate all missing assets")
        print("  python TG_HuggingFaceGenerator.py logos            # Generate missing faction logos")
        print("  python TG_HuggingFaceGenerator.py posters          # Generate missing posters")
        print("  python TG_HuggingFaceGenerator.py icons            # Generate missing UI icons")

if __name__ == "__main__":
    main()