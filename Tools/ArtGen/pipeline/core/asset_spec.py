"""
Asset Specification System
=========================

Defines the structure and validation for asset generation specifications.
This system replaces the scattered parameter handling with a unified,
type-safe specification format.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from ..utils.validation import validate_faction, validate_biome, validate_asset_type


class AssetType(Enum):
    """Supported asset types in Terminal Grounds."""
    WEAPON = "weapon"
    VEHICLE = "vehicle"
    GEAR = "gear"
    BUILDING = "building"
    CHARACTER = "character"
    ENVIRONMENT = "environment"
    UI_ICON = "ui_icon"
    POSTER = "poster"
    TEXTURE = "texture"
    CONCEPT = "concept"


class OutputFormat(Enum):
    """Supported output formats."""
    PNG = "png"
    JPG = "jpg"
    EXR = "exr"
    TGA = "tga"


class WorkflowType(Enum):
    """Available ComfyUI workflow types."""
    CONCEPT_ART = "concept_art"
    STYLE_BOARD = "style_board"
    TEXTURE_DECAL = "texture_decal"
    HIGH_DETAIL_RENDER = "high_detail_render"
    ICON_GENERATION = "icon_generation"
    POSTER_DESIGN = "poster_design"
    ENVIRONMENT_MATTE = "environment_matte"


@dataclass
class RenderSettings:
    """Rendering configuration for asset generation."""
    width: int = 1024
    height: int = 1024
    steps: int = 28
    cfg: float = 6.5
    sampler: str = "dpmpp_2m"
    scheduler: str = "karras"
    seed: Optional[int] = None
    batch_size: int = 1


@dataclass
class LoRAConfig:
    """LoRA model configuration."""
    name: str
    strength: float = 0.8
    clip_strength: Optional[float] = None


@dataclass
class QualitySettings:
    """Quality assurance and post-processing settings."""
    auto_upscale: bool = False
    target_resolution: Optional[tuple[int, int]] = None
    enhance_details: bool = False
    color_correction: bool = False
    format_conversion: bool = False
    validation_strict: bool = True


@dataclass
class FactionContext:
    """Faction-specific context for asset generation."""
    name: str
    style_loras: List[LoRAConfig] = field(default_factory=list)
    palette: List[str] = field(default_factory=list)
    positive_prompts: List[str] = field(default_factory=list)
    negative_prompts: List[str] = field(default_factory=list)
    cultural_elements: List[str] = field(default_factory=list)
    technology_level: str = "mixed"
    aesthetic_keywords: List[str] = field(default_factory=list)


@dataclass
class BiomeContext:
    """Biome-specific context for environmental assets."""
    name: str
    style_loras: List[LoRAConfig] = field(default_factory=list)
    palette: List[str] = field(default_factory=list)
    environmental_prompts: List[str] = field(default_factory=list)
    weather_conditions: List[str] = field(default_factory=list)
    lighting_conditions: List[str] = field(default_factory=list)


@dataclass
class AssetSpecification:
    """
    Complete specification for asset generation.
    
    This class encapsulates all parameters needed to generate an asset,
    including prompts, rendering settings, faction context, and output
    configuration.
    """
    
    # Core identification
    name: str
    asset_type: AssetType
    category: str = "general"
    description: str = ""
    
    # Generation prompts
    primary_prompt: str = ""
    secondary_prompts: List[str] = field(default_factory=list)
    negative_prompt: str = ""
    style_prompts: List[str] = field(default_factory=list)
    
    # Context and affiliation
    faction: Optional[str] = None
    biome: Optional[str] = None
    faction_context: Optional[FactionContext] = None
    biome_context: Optional[BiomeContext] = None
    
    # Technical settings
    render_settings: RenderSettings = field(default_factory=RenderSettings)
    workflow_type: WorkflowType = WorkflowType.CONCEPT_ART
    model_name: str = "flux.1-dev"
    loras: List[LoRAConfig] = field(default_factory=list)
    
    # Output configuration
    output_format: OutputFormat = OutputFormat.PNG
    output_directory: Optional[pathlib.Path] = None
    filename_template: str = "{name}_{faction}_{timestamp}"
    
    # Quality and processing
    quality_settings: QualitySettings = field(default_factory=QualitySettings)
    
    # Integration settings
    auto_import_ue5: bool = False
    ue5_asset_path: str = "/Game/ArtGen/Generated"
    metadata_tags: Dict[str, Any] = field(default_factory=dict)
    
    # Pipeline metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "2.0.0"
    priority: int = 5  # 1-10, higher is more urgent
    
    def __post_init__(self):
        """Validate and enhance specification after creation."""
        # Validate asset type
        if isinstance(self.asset_type, str):
            self.asset_type = AssetType(self.asset_type.lower())
        
        # Validate faction
        if self.faction:
            validate_faction(self.faction)
            if not self.faction_context:
                self.faction_context = self._load_faction_context(self.faction)
        
        # Validate biome
        if self.biome:
            validate_biome(self.biome)
            if not self.biome_context:
                self.biome_context = self._load_biome_context(self.biome)
        
        # Auto-select workflow if not specified
        if self.workflow_type == WorkflowType.CONCEPT_ART:
            self.workflow_type = self._auto_select_workflow()
        
        # Build composite prompt
        if not self.primary_prompt:
            self.primary_prompt = self._build_primary_prompt()
        
        # Set default output directory
        if not self.output_directory:
            self.output_directory = self._get_default_output_directory()
    
    def _load_faction_context(self, faction_name: str) -> FactionContext:
        """Load faction context from configuration files."""
        try:
            faction_path = pathlib.Path(__file__).parents[2] / f"prompt_packs/factions/{faction_name.upper()}.json"
            if faction_path.exists():
                data = json.loads(faction_path.read_text())
                return FactionContext(
                    name=data["name"],
                    style_loras=[LoRAConfig(**lora) for lora in data.get("defaults", {}).get("loras", [])],
                    palette=data.get("palette", []),
                    positive_prompts=data.get("positive", []),
                    negative_prompts=data.get("negative", []),
                    aesthetic_keywords=data.get("aesthetic_keywords", [])
                )
        except Exception:
            pass
        
        # Return default faction context
        return FactionContext(name=faction_name)
    
    def _load_biome_context(self, biome_name: str) -> BiomeContext:
        """Load biome context from configuration files."""
        try:
            biome_path = pathlib.Path(__file__).parents[2] / f"prompt_packs/biomes/{biome_name.upper()}.json"
            if biome_path.exists():
                data = json.loads(biome_path.read_text())
                return BiomeContext(
                    name=data["name"],
                    style_loras=[LoRAConfig(**lora) for lora in data.get("defaults", {}).get("loras", [])],
                    palette=data.get("palette", []),
                    environmental_prompts=data.get("positive", [])
                )
        except Exception:
            pass
        
        return BiomeContext(name=biome_name)
    
    def _auto_select_workflow(self) -> WorkflowType:
        """Automatically select the best workflow for this asset type."""
        workflow_mapping = {
            AssetType.WEAPON: WorkflowType.HIGH_DETAIL_RENDER,
            AssetType.VEHICLE: WorkflowType.HIGH_DETAIL_RENDER,
            AssetType.GEAR: WorkflowType.HIGH_DETAIL_RENDER,
            AssetType.BUILDING: WorkflowType.ENVIRONMENT_MATTE,
            AssetType.CHARACTER: WorkflowType.CONCEPT_ART,
            AssetType.ENVIRONMENT: WorkflowType.ENVIRONMENT_MATTE,
            AssetType.UI_ICON: WorkflowType.ICON_GENERATION,
            AssetType.POSTER: WorkflowType.POSTER_DESIGN,
            AssetType.TEXTURE: WorkflowType.TEXTURE_DECAL,
            AssetType.CONCEPT: WorkflowType.CONCEPT_ART,
        }
        
        return workflow_mapping.get(self.asset_type, WorkflowType.CONCEPT_ART)
    
    def _build_primary_prompt(self) -> str:
        """Build the primary prompt from available context."""
        prompt_parts = []
        
        # Add Terminal Grounds prefix
        prompt_parts.append("Terminal Grounds")
        
        # Add asset type and name
        if self.name:
            prompt_parts.append(self.name)
        
        prompt_parts.append(self.asset_type.value)
        
        # Add faction elements
        if self.faction_context:
            prompt_parts.extend(self.faction_context.positive_prompts[:2])
            prompt_parts.extend(self.faction_context.aesthetic_keywords[:3])
        
        # Add biome elements
        if self.biome_context:
            prompt_parts.extend(self.biome_context.environmental_prompts[:2])
        
        # Add style elements
        prompt_parts.extend(self.style_prompts[:2])
        
        # Add quality enhancers
        prompt_parts.extend([
            "high detail", 
            "sharp focus", 
            "professional concept art",
            "cinematic quality"
        ])
        
        return ", ".join(filter(None, prompt_parts))
    
    def _get_default_output_directory(self) -> pathlib.Path:
        """Get the default output directory for this asset type."""
        base_dir = pathlib.Path(__file__).parents[3] / "Docs" / "Concepts"
        
        # Map asset types to subdirectories
        type_mapping = {
            AssetType.WEAPON: "Weapons",
            AssetType.VEHICLE: "Vehicles", 
            AssetType.GEAR: "Gear",
            AssetType.BUILDING: "POIs",
            AssetType.CHARACTER: "Characters",
            AssetType.ENVIRONMENT: "Renders",
            AssetType.UI_ICON: "UI",
            AssetType.POSTER: "Posters",
            AssetType.TEXTURE: "Textures",
            AssetType.CONCEPT: "General"
        }
        
        subdir = type_mapping.get(self.asset_type, "General")
        return base_dir / subdir
    
    def get_full_prompt(self) -> str:
        """Get the complete, formatted prompt for generation."""
        parts = [self.primary_prompt]
        parts.extend(self.secondary_prompts)
        parts.extend(self.style_prompts)
        
        return ", ".join(filter(None, parts))
    
    def get_full_negative_prompt(self) -> str:
        """Get the complete negative prompt."""
        parts = [self.negative_prompt] if self.negative_prompt else []
        
        if self.faction_context:
            parts.extend(self.faction_context.negative_prompts)
        
        # Add default negative prompts
        parts.extend([
            "blurry", "low quality", "amateur", "distorted", "artifacts"
        ])
        
        return ", ".join(filter(None, parts))
    
    def get_all_loras(self) -> List[LoRAConfig]:
        """Get all LoRA configurations including faction and biome LoRAs."""
        all_loras = list(self.loras)
        
        if self.faction_context:
            all_loras.extend(self.faction_context.style_loras)
        
        if self.biome_context:
            all_loras.extend(self.biome_context.style_loras)
        
        # Remove duplicates by name
        seen_names = set()
        unique_loras = []
        for lora in all_loras:
            if lora.name not in seen_names:
                unique_loras.append(lora)
                seen_names.add(lora.name)
        
        return unique_loras
    
    def get_filename(self) -> str:
        """Generate the output filename based on template."""
        template_vars = {
            "name": self.name.lower().replace(" ", "_"),
            "faction": self.faction.lower() if self.faction else "neutral",
            "biome": self.biome.lower() if self.biome else "",
            "type": self.asset_type.value,
            "timestamp": datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
            "category": self.category.lower().replace(" ", "_")
        }
        
        filename = self.filename_template.format(**template_vars)
        return f"{filename}.{self.output_format.value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert specification to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert specification to JSON string."""
        data = self.to_dict()
        # Convert datetime to ISO string
        data["created_at"] = self.created_at.isoformat()
        # Convert Path objects to strings
        if self.output_directory:
            data["output_directory"] = str(self.output_directory)
        return json.dumps(data, indent=2)
    
    def save(self, filepath: pathlib.Path) -> None:
        """Save specification to file."""
        filepath.write_text(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssetSpecification:
        """Create specification from dictionary."""
        # Handle datetime conversion
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        
        # Handle Path conversion
        if "output_directory" in data and data["output_directory"]:
            data["output_directory"] = pathlib.Path(data["output_directory"])
        
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> AssetSpecification:
        """Create specification from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_file(cls, filepath: pathlib.Path) -> AssetSpecification:
        """Load specification from file."""
        data = json.loads(filepath.read_text())
        return cls.from_dict(data)
    
    @classmethod
    def create_quick(
        cls,
        asset_type: str,
        name: str,
        faction: str = "neutral",
        **kwargs
    ) -> AssetSpecification:
        """Create a quick specification with minimal parameters."""
        return cls(
            name=name,
            asset_type=AssetType(asset_type.lower()),
            faction=faction,
            **kwargs
        )
    
    @classmethod
    def create_faction_asset(
        cls,
        faction_name: str,
        asset_type: str,
        faction_config: Dict[str, Any],
        index: int = 0
    ) -> AssetSpecification:
        """Create an asset specification specifically for a faction."""
        return cls(
            name=f"{faction_name} {asset_type} {index + 1:02d}",
            asset_type=AssetType(asset_type.lower()),
            faction=faction_name,
            render_settings=RenderSettings(
                seed=faction_config.get("defaults", {}).get("seed", 0) + index,
                **faction_config.get("render_overrides", {})
            )
        )
    
    @classmethod
    def create_from_csv_row(
        cls,
        row: Dict[str, str],
        template: AssetSpecification
    ) -> AssetSpecification:
        """Create specification from CSV row data."""
        spec = AssetSpecification(
            name=row.get("Name", "Unknown"),
            asset_type=template.asset_type,
            faction=row.get("Faction", template.faction),
            category=template.category,
            description=row.get("Description", ""),
            render_settings=RenderSettings(
                seed=template.render_settings.seed + int(row.get("SeedOffset", 0))
            ),
            workflow_type=template.workflow_type,
            quality_settings=template.quality_settings,
            auto_import_ue5=template.auto_import_ue5
        )
        
        # Add CSV-specific metadata
        spec.metadata_tags.update({
            "csv_source": True,
            "csv_data": {k: v for k, v in row.items() if v}
        })
        
        return spec


# Convenience functions for common asset types
def create_weapon_spec(name: str, faction: str = "neutral", **kwargs) -> AssetSpecification:
    """Create a weapon asset specification."""
    return AssetSpecification.create_quick("weapon", name, faction, **kwargs)


def create_vehicle_spec(name: str, faction: str = "neutral", **kwargs) -> AssetSpecification:
    """Create a vehicle asset specification."""
    return AssetSpecification.create_quick("vehicle", name, faction, **kwargs)


def create_concept_spec(name: str, faction: str = "neutral", **kwargs) -> AssetSpecification:
    """Create a concept art specification."""
    return AssetSpecification.create_quick("concept", name, faction, **kwargs)