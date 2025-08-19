#!/usr/bin/env python3
"""
Asset Specification System for Terminal Grounds v2.0
===================================================
Type-safe asset definitions with deep faction integration and metadata management.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Literal
from dataclasses import dataclass, field, asdict
from enum import Enum
import time

# Asset type definitions
AssetType = Literal["weapon", "vehicle", "emblem", "poster", "icon", "concept", "environment", "texture", "ui"]
FactionCode = Literal["directorate", "free77", "vultures", "combine", "nomads", "archivists", "wardens", "neutral"]
QualityLevel = Literal["draft", "production", "hero", "cinematic"]

class AssetCategory(Enum):
    EQUIPMENT = "equipment"
    VEHICLE = "vehicle"
    BRANDING = "branding"
    ENVIRONMENT = "environment"
    UI = "ui"

@dataclass
class FactionStyle:
    """Faction visual identity and style parameters"""
    code: str
    name: str
    color_primary: str
    color_secondary: str
    color_accent: str
    style_keywords: List[str]
    material_keywords: List[str]
    aesthetic_tags: List[str]
    lora_preferences: List[str] = field(default_factory=list)
    negative_prompts: List[str] = field(default_factory=list)
    
    @classmethod
    def from_json_file(cls, json_path: Path) -> 'FactionStyle':
        """Load faction style from existing JSON files"""
        with open(json_path) as f:
            data = json.load(f)
            
        return cls(
            code=data.get("code", json_path.stem.lower()),
            name=data.get("name", data.get("faction_name", "")),
            color_primary=data.get("primary_color", data.get("colors", {}).get("primary", "#000000")),
            color_secondary=data.get("secondary_color", data.get("colors", {}).get("secondary", "#ffffff")),
            color_accent=data.get("accent_color", data.get("colors", {}).get("accent", "#ff0000")),
            style_keywords=data.get("style_keywords", data.get("visual_style", [])),
            material_keywords=data.get("material_keywords", []),
            aesthetic_tags=data.get("aesthetic_tags", data.get("themes", [])),
            lora_preferences=data.get("lora_preferences", []),
            negative_prompts=data.get("negative_prompts", [])
        )

@dataclass
class GenerationParameters:
    """ComfyUI generation parameters"""
    model: str = "flux1-dev-fp8.safetensors"
    steps: int = 28
    cfg: float = 4.0
    sampler: str = "dpmpp_2m"
    scheduler: str = "karras"
    width: int = 1024
    height: int = 1024
    seed: Optional[int] = None
    loras: List[Dict[str, Any]] = field(default_factory=list)
    
@dataclass
class QualityRequirements:
    """Quality standards for different asset types"""
    min_resolution: int = 1024
    target_resolution: int = 2048
    min_quality_score: float = 70.0
    enhancement_threshold: float = 80.0
    required_aspects: List[str] = field(default_factory=list)
    
@dataclass
class AssetSpecification:
    """Complete specification for asset generation"""
    # Basic identification
    name: str
    asset_type: AssetType
    faction: FactionCode
    description: str
    
    # Generation parameters
    base_prompt: str
    negative_prompt: str
    generation_params: GenerationParameters
    quality_requirements: QualityRequirements
    
    # Organization
    category: AssetCategory
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processing
    post_processing: List[str] = field(default_factory=list)
    export_formats: List[str] = field(default_factory=lambda: ["png"])
    ue5_import: bool = True
    
    # Tracking
    created_at: float = field(default_factory=time.time)
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssetSpecification':
        """Create from dictionary"""
        # Handle nested dataclasses
        if 'generation_params' in data and isinstance(data['generation_params'], dict):
            data['generation_params'] = GenerationParameters(**data['generation_params'])
        if 'quality_requirements' in data and isinstance(data['quality_requirements'], dict):
            data['quality_requirements'] = QualityRequirements(**data['quality_requirements'])
            
        return cls(**data)

class AssetSpecBuilder:
    """Builder for creating asset specifications with faction integration"""
    
    def __init__(self, faction_data_dir: Path):
        self.faction_data_dir = faction_data_dir
        self.faction_styles: Dict[str, FactionStyle] = {}
        self._load_faction_styles()
        
        # Asset type templates
        self.type_templates = {
            "weapon": self._weapon_template,
            "vehicle": self._vehicle_template,
            "emblem": self._emblem_template,
            "poster": self._poster_template,
            "icon": self._icon_template,
            "concept": self._concept_template,
            "environment": self._environment_template,
            "texture": self._texture_template,
            "ui": self._ui_template
        }
        
    def _load_faction_styles(self):
        """Load faction styles from JSON files"""
        faction_files = [
            "DIR.json", "F77.json", "VLT.json", 
            # Add other faction files as they're created
        ]
        
        for filename in faction_files:
            faction_path = self.faction_data_dir / filename
            if faction_path.exists():
                try:
                    faction_style = FactionStyle.from_json_file(faction_path)
                    self.faction_styles[faction_style.code] = faction_style
                except Exception as e:
                    print(f"Warning: Could not load faction style from {filename}: {e}")
                    
        # Add default neutral faction
        if "neutral" not in self.faction_styles:
            self.faction_styles["neutral"] = FactionStyle(
                code="neutral",
                name="Neutral",
                color_primary="#808080",
                color_secondary="#ffffff",
                color_accent="#000000",
                style_keywords=["clean", "minimal", "functional"],
                material_keywords=["metal", "plastic", "standard"],
                aesthetic_tags=["utilitarian", "generic"]
            )
    
    def create_spec(self, 
                   name: str,
                   asset_type: AssetType,
                   faction: FactionCode,
                   description: str,
                   custom_params: Optional[Dict[str, Any]] = None) -> AssetSpecification:
        """Create asset specification with intelligent defaults"""
        
        # Get faction style
        faction_style = self.faction_styles.get(faction, self.faction_styles["neutral"])
        
        # Get type template
        template_func = self.type_templates.get(asset_type, self._default_template)
        base_spec = template_func(name, description, faction_style)
        
        # Apply custom parameters
        if custom_params:
            self._apply_custom_params(base_spec, custom_params)
            
        return base_spec
        
    def _apply_custom_params(self, spec: AssetSpecification, custom_params: Dict[str, Any]):
        """Apply custom parameters to specification"""
        for key, value in custom_params.items():
            if hasattr(spec, key):
                setattr(spec, key, value)
            elif hasattr(spec.generation_params, key):
                setattr(spec.generation_params, key, value)
            elif hasattr(spec.quality_requirements, key):
                setattr(spec.quality_requirements, key, value)
            else:
                spec.metadata[key] = value
                
    def _weapon_template(self, name: str, description: str, faction_style: FactionStyle) -> AssetSpecification:
        """Template for weapon assets"""
        return AssetSpecification(
            name=name,
            asset_type="weapon",
            faction=faction_style.code,
            description=description,
            base_prompt=self._build_weapon_prompt(name, description, faction_style),
            negative_prompt=self._build_negative_prompt(faction_style, ["blurry", "low quality", "deformed", "broken"]),
            generation_params=GenerationParameters(
                width=1024,
                height=1024,
                steps=32,
                cfg=4.5,
                loras=self._get_faction_loras(faction_style)
            ),
            quality_requirements=QualityRequirements(
                min_resolution=1024,
                target_resolution=2048,
                min_quality_score=80.0,
                required_aspects=["detail", "clarity", "faction_style"]
            ),
            category=AssetCategory.EQUIPMENT,
            tags=[faction_style.code, "weapon", "equipment"],
            post_processing=["upscale", "sharpen"],
            ue5_import=True
        )
        
    def _vehicle_template(self, name: str, description: str, faction_style: FactionStyle) -> AssetSpecification:
        """Template for vehicle assets"""
        return AssetSpecification(
            name=name,
            asset_type="vehicle", 
            faction=faction_style.code,
            description=description,
            base_prompt=self._build_vehicle_prompt(name, description, faction_style),
            negative_prompt=self._build_negative_prompt(faction_style, ["blurry", "low quality", "broken parts"]),
            generation_params=GenerationParameters(
                width=1280,
                height=768,
                steps=30,
                cfg=4.0,
                loras=self._get_faction_loras(faction_style)
            ),
            quality_requirements=QualityRequirements(
                min_resolution=1280,
                target_resolution=2560,
                min_quality_score=75.0,
                required_aspects=["vehicle_design", "faction_identity", "technical_detail"]
            ),
            category=AssetCategory.VEHICLE,
            tags=[faction_style.code, "vehicle", "transport"],
            post_processing=["upscale", "enhance"],
            ue5_import=True
        )
        
    def _emblem_template(self, name: str, description: str, faction_style: FactionStyle) -> AssetSpecification:
        """Template for emblem/logo assets"""
        return AssetSpecification(
            name=name,
            asset_type="emblem",
            faction=faction_style.code,
            description=description,
            base_prompt=self._build_emblem_prompt(name, description, faction_style),
            negative_prompt=self._build_negative_prompt(faction_style, ["blurry", "complex background", "text", "watermark"]),
            generation_params=GenerationParameters(
                width=1024,
                height=1024,
                steps=35,
                cfg=5.0,
                loras=self._get_logo_loras(faction_style)
            ),
            quality_requirements=QualityRequirements(
                min_resolution=1024,
                target_resolution=2048,
                min_quality_score=85.0,
                required_aspects=["clean_design", "faction_identity", "scalability"]
            ),
            category=AssetCategory.BRANDING,
            tags=[faction_style.code, "emblem", "logo", "branding"],
            post_processing=["upscale", "vectorize"],
            export_formats=["png", "svg"],
            ue5_import=True
        )
        
    def _poster_template(self, name: str, description: str, faction_style: FactionStyle) -> AssetSpecification:
        """Template for propaganda/poster assets"""
        return AssetSpecification(
            name=name,
            asset_type="poster",
            faction=faction_style.code,
            description=description,
            base_prompt=self._build_poster_prompt(name, description, faction_style),
            negative_prompt=self._build_negative_prompt(faction_style, ["blurry", "low quality", "cluttered"]),
            generation_params=GenerationParameters(
                width=768,
                height=1024,
                steps=28,
                cfg=4.5,
                loras=self._get_poster_loras(faction_style)
            ),
            quality_requirements=QualityRequirements(
                min_resolution=768,
                target_resolution=1536,
                min_quality_score=75.0,
                required_aspects=["poster_composition", "faction_messaging", "visual_impact"]
            ),
            category=AssetCategory.BRANDING,
            tags=[faction_style.code, "poster", "propaganda"],
            post_processing=["upscale", "color_enhance"],
            ue5_import=True
        )
        
    def _icon_template(self, name: str, description: str, faction_style: FactionStyle) -> AssetSpecification:
        """Template for UI icon assets"""
        return AssetSpecification(
            name=name,
            asset_type="icon",
            faction=faction_style.code,
            description=description,
            base_prompt=self._build_icon_prompt(name, description, faction_style),
            negative_prompt=self._build_negative_prompt(faction_style, ["blurry", "complex", "background", "text"]),
            generation_params=GenerationParameters(
                width=512,
                height=512,
                steps=25,
                cfg=4.0,
                loras=self._get_ui_loras(faction_style)
            ),
            quality_requirements=QualityRequirements(
                min_resolution=512,
                target_resolution=1024,
                min_quality_score=80.0,
                required_aspects=["clarity", "simplicity", "faction_style"]
            ),
            category=AssetCategory.UI,
            tags=[faction_style.code, "icon", "ui"],
            post_processing=["upscale", "clean"],
            export_formats=["png"],
            ue5_import=True
        )
        
    def _concept_template(self, name: str, description: str, faction_style: FactionStyle) -> AssetSpecification:
        """Template for concept art assets"""
        return AssetSpecification(
            name=name,
            asset_type="concept",
            faction=faction_style.code,
            description=description,
            base_prompt=self._build_concept_prompt(name, description, faction_style),
            negative_prompt=self._build_negative_prompt(faction_style, ["blurry", "low quality", "photograph"]),
            generation_params=GenerationParameters(
                width=1280,
                height=768,
                steps=30,
                cfg=4.0,
                loras=self._get_concept_loras(faction_style)
            ),
            quality_requirements=QualityRequirements(
                min_resolution=1280,
                target_resolution=2560,
                min_quality_score=70.0,
                required_aspects=["artistic_quality", "faction_atmosphere", "composition"]
            ),
            category=AssetCategory.ENVIRONMENT,
            tags=[faction_style.code, "concept", "art"],
            post_processing=["upscale", "artistic_enhance"],
            ue5_import=False
        )
        
    def _environment_template(self, name: str, description: str, faction_style: FactionStyle) -> AssetSpecification:
        """Template for environment assets"""
        return AssetSpecification(
            name=name,
            asset_type="environment",
            faction=faction_style.code,
            description=description,
            base_prompt=self._build_environment_prompt(name, description, faction_style),
            negative_prompt=self._build_negative_prompt(faction_style, ["blurry", "low quality", "people", "characters"]),
            generation_params=GenerationParameters(
                width=1536,
                height=864,
                steps=28,
                cfg=4.0,
                loras=self._get_environment_loras(faction_style)
            ),
            quality_requirements=QualityRequirements(
                min_resolution=1536,
                target_resolution=3072,
                min_quality_score=75.0,
                required_aspects=["environment_design", "faction_architecture", "atmosphere"]
            ),
            category=AssetCategory.ENVIRONMENT,
            tags=[faction_style.code, "environment", "scene"],
            post_processing=["upscale", "atmosphere_enhance"],
            ue5_import=False
        )
        
    def _texture_template(self, name: str, description: str, faction_style: FactionStyle) -> AssetSpecification:
        """Template for texture assets"""
        return AssetSpecification(
            name=name,
            asset_type="texture",
            faction=faction_style.code,
            description=description,
            base_prompt=self._build_texture_prompt(name, description, faction_style),
            negative_prompt=self._build_negative_prompt(faction_style, ["blurry", "low quality", "seams", "objects"]),
            generation_params=GenerationParameters(
                width=1024,
                height=1024,
                steps=25,
                cfg=3.5,
                loras=self._get_texture_loras(faction_style)
            ),
            quality_requirements=QualityRequirements(
                min_resolution=1024,
                target_resolution=2048,
                min_quality_score=80.0,
                required_aspects=["seamless", "material_accuracy", "detail"]
            ),
            category=AssetCategory.ENVIRONMENT,
            tags=[faction_style.code, "texture", "material"],
            post_processing=["upscale", "seamless_check"],
            ue5_import=True
        )
        
    def _ui_template(self, name: str, description: str, faction_style: FactionStyle) -> AssetSpecification:
        """Template for UI element assets"""
        return AssetSpecification(
            name=name,
            asset_type="ui",
            faction=faction_style.code,
            description=description,
            base_prompt=self._build_ui_prompt(name, description, faction_style),
            negative_prompt=self._build_negative_prompt(faction_style, ["blurry", "complex", "realistic", "3d"]),
            generation_params=GenerationParameters(
                width=1024,
                height=768,
                steps=25,
                cfg=4.0,
                loras=self._get_ui_loras(faction_style)
            ),
            quality_requirements=QualityRequirements(
                min_resolution=1024,
                target_resolution=2048,
                min_quality_score=80.0,
                required_aspects=["ui_design", "faction_style", "usability"]
            ),
            category=AssetCategory.UI,
            tags=[faction_style.code, "ui", "interface"],
            post_processing=["upscale", "ui_optimize"],
            ue5_import=True
        )
        
    def _default_template(self, name: str, description: str, faction_style: FactionStyle) -> AssetSpecification:
        """Default template for unknown asset types"""
        return AssetSpecification(
            name=name,
            asset_type="concept",
            faction=faction_style.code,
            description=description,
            base_prompt=f"{name}, {description}, {', '.join(faction_style.style_keywords)}",
            negative_prompt=self._build_negative_prompt(faction_style),
            generation_params=GenerationParameters(),
            quality_requirements=QualityRequirements(),
            category=AssetCategory.ENVIRONMENT,
            tags=[faction_style.code, "misc"]
        )
        
    # Prompt building methods
    def _build_weapon_prompt(self, name: str, description: str, faction_style: FactionStyle) -> str:
        """Build weapon-specific prompt"""
        style_terms = ", ".join(faction_style.style_keywords)
        material_terms = ", ".join(faction_style.material_keywords)
        
        return f"{name}, {description}, {style_terms}, {material_terms}, weapon design, detailed, high quality, concept art"
        
    def _build_vehicle_prompt(self, name: str, description: str, faction_style: FactionStyle) -> str:
        """Build vehicle-specific prompt"""
        style_terms = ", ".join(faction_style.style_keywords)
        
        return f"{name}, {description}, {style_terms}, vehicle design, engineering, technical, detailed"
        
    def _build_emblem_prompt(self, name: str, description: str, faction_style: FactionStyle) -> str:
        """Build emblem-specific prompt"""
        aesthetic_terms = ", ".join(faction_style.aesthetic_tags)
        
        return f"{name}, {description}, {aesthetic_terms}, emblem, logo design, clean, vector style, centered"
        
    def _build_poster_prompt(self, name: str, description: str, faction_style: FactionStyle) -> str:
        """Build poster-specific prompt"""
        style_terms = ", ".join(faction_style.style_keywords)
        
        return f"{name}, {description}, {style_terms}, propaganda poster, graphic design, bold, impactful"
        
    def _build_icon_prompt(self, name: str, description: str, faction_style: FactionStyle) -> str:
        """Build icon-specific prompt"""
        return f"{name}, {description}, icon, simple, clean, ui element, minimalist, clear"
        
    def _build_concept_prompt(self, name: str, description: str, faction_style: FactionStyle) -> str:
        """Build concept art prompt"""
        style_terms = ", ".join(faction_style.style_keywords)
        aesthetic_terms = ", ".join(faction_style.aesthetic_tags)
        
        return f"{name}, {description}, {style_terms}, {aesthetic_terms}, concept art, digital painting"
        
    def _build_environment_prompt(self, name: str, description: str, faction_style: FactionStyle) -> str:
        """Build environment-specific prompt"""
        style_terms = ", ".join(faction_style.style_keywords)
        
        return f"{name}, {description}, {style_terms}, environment, architecture, atmospheric, detailed"
        
    def _build_texture_prompt(self, name: str, description: str, faction_style: FactionStyle) -> str:
        """Build texture-specific prompt"""
        material_terms = ", ".join(faction_style.material_keywords)
        
        return f"{name}, {description}, {material_terms}, seamless texture, tileable, material, surface"
        
    def _build_ui_prompt(self, name: str, description: str, faction_style: FactionStyle) -> str:
        """Build UI-specific prompt"""
        return f"{name}, {description}, ui design, interface, clean, functional, modern"
        
    def _build_negative_prompt(self, faction_style: FactionStyle, additional_negatives: List[str] = None) -> str:
        """Build comprehensive negative prompt"""
        base_negatives = ["blurry", "low quality", "bad anatomy", "deformed", "ugly", "watermark"]
        faction_negatives = faction_style.negative_prompts
        extra_negatives = additional_negatives or []
        
        all_negatives = base_negatives + faction_negatives + extra_negatives
        return ", ".join(set(all_negatives))  # Remove duplicates
        
    # LoRA selection methods
    def _get_faction_loras(self, faction_style: FactionStyle) -> List[Dict[str, Any]]:
        """Get faction-appropriate LoRAs"""
        loras = []
        for lora_name in faction_style.lora_preferences:
            loras.append({"name": lora_name, "strength": 0.8})
        return loras
        
    def _get_logo_loras(self, faction_style: FactionStyle) -> List[Dict[str, Any]]:
        """Get logo/emblem appropriate LoRAs"""
        return [{"name": "LogoRedmondV2-Logo-LogoRedmAF", "strength": 0.9}]
        
    def _get_poster_loras(self, faction_style: FactionStyle) -> List[Dict[str, Any]]:
        """Get poster appropriate LoRAs"""
        return [{"name": "Ink_poster-000004", "strength": 0.7}]
        
    def _get_ui_loras(self, faction_style: FactionStyle) -> List[Dict[str, Any]]:
        """Get UI appropriate LoRAs"""
        return []  # UI elements usually work better without LoRAs
        
    def _get_concept_loras(self, faction_style: FactionStyle) -> List[Dict[str, Any]]:
        """Get concept art appropriate LoRAs"""
        return [{"name": "ck-Sommo-Concept-Art-000015", "strength": 0.6}]
        
    def _get_environment_loras(self, faction_style: FactionStyle) -> List[Dict[str, Any]]:
        """Get environment appropriate LoRAs"""
        return [{"name": "Sci-fi_env_flux", "strength": 0.7}]
        
    def _get_texture_loras(self, faction_style: FactionStyle) -> List[Dict[str, Any]]:
        """Get texture appropriate LoRAs"""
        return [{"name": "Textures", "strength": 0.8}]