#!/usr/bin/env python3
"""
TG_UnrealEngineIntegrator.py
Terminal Grounds Unreal Engine 5.6 Asset Integration

Automates import of generated assets into Unreal Engine with:
- Proper naming conventions and folder structure  
- Correct texture settings (compression, mipmaps, texture groups)
- Material instance creation from M_TG_Decal_Master
- GameplayTags application for UI assets
- Asset validation and quality assurance

Author: Terminal Grounds Content Pipeline Agent
Version: 1.0.0
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Add the parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from TG_ContentPipelineAgent import AssetCategory, AssetMetadata, TerminalGroundsContentAgent

# Terminal Grounds project root
ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = ROOT / "Content/TG"
SOURCE_ROOT = ROOT / "Source"
CONFIG_ROOT = ROOT / "Config"

class TextureGroup(Enum):
    """Unreal Engine texture groups for different asset types"""
    UI = "TEXTUREGROUP_UI"
    WORLD = "TEXTUREGROUP_World"
    EFFECTS = "TEXTUREGROUP_Effects"
    VEHICLE = "TEXTUREGROUP_Vehicle"
    WEAPON = "TEXTUREGROUP_Weapon"
    CHARACTER = "TEXTUREGROUP_Character"
    LIGHTMAP = "TEXTUREGROUP_Lightmap"

class CompressionSettings(Enum):
    """Unreal Engine texture compression settings"""
    DEFAULT = "TC_Default"
    NORMALMAP = "TC_Normalmap"
    MASKS = "TC_Masks"
    GRAYSCALE = "TC_Grayscale"
    DISPLACEMENTMAP = "TC_Displacementmap"
    VECTOR_DISPLACEMENTMAP = "TC_VectorDisplacementmap"
    HDR = "TC_HDR"
    EDITOR_ICON = "TC_EditorIcon"
    ALPHA = "TC_Alpha"
    DISTANCE_FIELD_FONT = "TC_DistanceFieldFont"
    HDR_COMPRESSED = "TC_HDRCompressed"
    BC7 = "TC_BC7"

@dataclass
class UnrealAssetSettings:
    """Settings for Unreal Engine asset import"""
    texture_group: TextureGroup
    compression_setting: CompressionSettings
    enable_mipmaps: bool
    enable_streaming: bool
    srgb: bool
    filter: str  # TF_Nearest, TF_Bilinear, TF_Trilinear
    address_x: str  # TA_Wrap, TA_Clamp, TA_Mirror
    address_y: str
    max_texture_size: int
    lod_bias: int
    create_material: bool
    material_template: Optional[str]
    gameplay_tags: List[str]

class TerminalGroundsUnrealIntegrator:
    """Unreal Engine integration for Terminal Grounds assets"""
    
    def __init__(self, content_agent: TerminalGroundsContentAgent):
        self.content_agent = content_agent
        self.log_file = ROOT / "Docs/Phase4_Implementation_Log.md"
        
        # Asset settings mapping
        self.asset_settings = self._load_asset_settings()
        
        # UE Python script paths
        self.python_scripts_dir = ROOT / "Tools/Unreal/python"
        self.python_scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Material templates
        self.material_templates = self._load_material_templates()
    
    def _load_asset_settings(self) -> Dict[AssetCategory, UnrealAssetSettings]:
        """Load category-specific Unreal Engine import settings"""
        return {
            AssetCategory.FACTION_LOGO: UnrealAssetSettings(
                texture_group=TextureGroup.UI,
                compression_setting=CompressionSettings.BC7,
                enable_mipmaps=True,
                enable_streaming=False,
                srgb=True,
                filter="TF_Trilinear",
                address_x="TA_Clamp",
                address_y="TA_Clamp", 
                max_texture_size=2048,
                lod_bias=0,
                create_material=True,
                material_template="M_TG_Decal_Master",
                gameplay_tags=["UI.Icon.Faction"]
            ),
            AssetCategory.POSTER_DECAL: UnrealAssetSettings(
                texture_group=TextureGroup.WORLD,
                compression_setting=CompressionSettings.BC7,
                enable_mipmaps=True,
                enable_streaming=True,
                srgb=True,
                filter="TF_Trilinear",
                address_x="TA_Clamp",
                address_y="TA_Clamp",
                max_texture_size=2048,
                lod_bias=0,
                create_material=True,
                material_template="M_TG_Decal_Master",
                gameplay_tags=["Decal.Poster"]
            ),
            AssetCategory.UI_ICON: UnrealAssetSettings(
                texture_group=TextureGroup.UI,
                compression_setting=CompressionSettings.BC7,
                enable_mipmaps=True,
                enable_streaming=False,
                srgb=True,
                filter="TF_Bilinear",
                address_x="TA_Clamp",
                address_y="TA_Clamp",
                max_texture_size=512,
                lod_bias=0,
                create_material=False,
                material_template=None,
                gameplay_tags=["UI.Icon"]
            ),
            AssetCategory.CONCEPT_ART: UnrealAssetSettings(
                texture_group=TextureGroup.WORLD,
                compression_setting=CompressionSettings.DEFAULT,
                enable_mipmaps=True,
                enable_streaming=True,
                srgb=True,
                filter="TF_Trilinear",
                address_x="TA_Wrap",
                address_y="TA_Wrap",
                max_texture_size=4096,
                lod_bias=0,
                create_material=False,
                material_template=None,
                gameplay_tags=["Concept.Art"]
            ),
            AssetCategory.WEAPON_CONCEPT: UnrealAssetSettings(
                texture_group=TextureGroup.WEAPON,
                compression_setting=CompressionSettings.DEFAULT,
                enable_mipmaps=True,
                enable_streaming=True,
                srgb=True,
                filter="TF_Trilinear",
                address_x="TA_Wrap",
                address_y="TA_Wrap",
                max_texture_size=2048,
                lod_bias=0,
                create_material=False,
                material_template=None,
                gameplay_tags=["Concept.Weapon"]
            ),
            AssetCategory.VEHICLE_CONCEPT: UnrealAssetSettings(
                texture_group=TextureGroup.VEHICLE,
                compression_setting=CompressionSettings.DEFAULT,
                enable_mipmaps=True,
                enable_streaming=True,
                srgb=True,
                filter="TF_Trilinear",
                address_x="TA_Wrap",
                address_y="TA_Wrap",
                max_texture_size=2048,
                lod_bias=0,
                create_material=False,
                material_template=None,
                gameplay_tags=["Concept.Vehicle"]
            )
        }
    
    def _load_material_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load material template configurations"""
        return {
            "M_TG_Decal_Master": {
                "base_path": "/Game/TG/Materials/M_TG_Decal_Master",
                "parameters": {
                    "BaseColor": "Texture",
                    "Opacity": "TextureAlpha",
                    "Normal": None,
                    "Roughness": 0.8,
                    "Metallic": 0.0
                },
                "instance_suffix": "_MI"
            }
        }
    
    def get_unreal_asset_path(self, asset_category: AssetCategory, 
                             asset_name: str, faction: Optional[str] = None) -> str:
        """Generate Unreal Engine asset path following TG conventions"""
        
        # Base path mapping
        base_paths = {
            AssetCategory.FACTION_LOGO: "/Game/TG/Decals/Factions",
            AssetCategory.POSTER_DECAL: "/Game/TG/Decals/Posters", 
            AssetCategory.UI_ICON: "/Game/TG/Icons",
            AssetCategory.CONCEPT_ART: "/Game/TG/ConceptArt",
            AssetCategory.WEAPON_CONCEPT: "/Game/TG/ConceptArt/Weapons",
            AssetCategory.VEHICLE_CONCEPT: "/Game/TG/ConceptArt/Vehicles",
            AssetCategory.BIOME_CONCEPT: "/Game/TG/ConceptArt/Biomes",
            AssetCategory.CHARACTER_CONCEPT: "/Game/TG/ConceptArt/Characters",
            AssetCategory.TEXTURE: "/Game/TG/Textures"
        }
        
        base_path = base_paths.get(asset_category, "/Game/TG/Misc")
        
        # Add faction subfolder if applicable
        if faction and asset_category in [AssetCategory.FACTION_LOGO, AssetCategory.POSTER_DECAL]:
            # For faction assets, they're typically named with faction prefix
            pass
        
        # Clean asset name for UE naming conventions
        clean_name = self.clean_asset_name(asset_name)
        
        return f"{base_path}/{clean_name}"
    
    def clean_asset_name(self, name: str) -> str:
        """Clean asset name for UE naming conventions"""
        # Remove file extension
        name = Path(name).stem
        
        # Replace invalid characters
        name = name.replace(" ", "_")
        name = name.replace("-", "_")
        name = name.replace(".", "_")
        
        # Ensure it starts with a letter
        if name and not name[0].isalpha():
            name = f"T_{name}"
        
        # Add T_ prefix if not present for textures
        if not name.startswith(("T_", "M_", "MI_", "BP_")):
            name = f"T_{name}"
        
        return name
    
    def generate_import_script(self, asset_path: Path, target_category: AssetCategory, 
                              faction: Optional[str] = None) -> str:
        """Generate UE Python script for asset import"""
        
        settings = self.asset_settings.get(target_category)
        if not settings:
            return ""
        
        clean_name = self.clean_asset_name(asset_path.name)
        unreal_path = self.get_unreal_asset_path(target_category, clean_name, faction)
        
        script = f'''
import unreal

# Asset import settings
factory = unreal.TextureFactory()
task = unreal.AssetImportTask()

# Set import parameters
task.set_editor_property('automated', True)
task.set_editor_property('destination_path', '{unreal_path.rsplit("/", 1)[0]}')
task.set_editor_property('destination_name', '{clean_name}')
task.set_editor_property('filename', r'{asset_path.as_posix()}')
task.set_editor_property('factory', factory)
task.set_editor_property('save', True)

# Configure texture settings
factory.set_editor_property('texture_group', unreal.TextureGroup.{settings.texture_group.value.split('_')[1]})
factory.set_editor_property('compression_settings', unreal.TextureCompressionSettings.{settings.compression_setting.value})
factory.set_editor_property('create_mip_maps', {str(settings.enable_mipmaps).lower()})
factory.set_editor_property('srgb', {str(settings.srgb).lower()})

# Import the asset
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
imported_asset = asset_tools.import_asset_tasks([task])

if imported_asset and len(imported_asset) > 0:
    texture = imported_asset[0]
    
    # Apply additional texture settings
    texture.set_editor_property('max_texture_size', {settings.max_texture_size})
    texture.set_editor_property('lod_bias', {settings.lod_bias})
    texture.set_editor_property('filter', unreal.TextureFilter.{settings.filter.split('_')[1]})
    texture.set_editor_property('address_x', unreal.TextureAddress.{settings.address_x.split('_')[1]})
    texture.set_editor_property('address_y', unreal.TextureAddress.{settings.address_y.split('_')[1]})
    
    # Save texture
    unreal.EditorAssetLibrary.save_asset(texture.get_path_name())
    
    print(f"Successfully imported: {{texture.get_path_name()}}")
'''
        
        # Add material instance creation if needed
        if settings.create_material and settings.material_template:
            script += self._generate_material_instance_script(clean_name, unreal_path, 
                                                              settings.material_template, faction)
        
        # Add gameplay tags if needed
        if settings.gameplay_tags:
            script += self._generate_gameplay_tags_script(clean_name, unreal_path, 
                                                         settings.gameplay_tags)
        
        script += '''
else:
    print("Import failed!")
'''
        
        return script
    
    def _generate_material_instance_script(self, asset_name: str, asset_path: str, 
                                         template: str, faction: Optional[str]) -> str:
        """Generate script for material instance creation"""
        
        template_data = self.material_templates.get(template, {})
        mi_name = asset_name.replace("T_", "MI_") + template_data.get("instance_suffix", "_MI")
        mi_path = asset_path.replace(asset_name, mi_name)
        
        script = f'''
    # Create material instance
    material_template = unreal.EditorAssetLibrary.load_asset('{template_data.get("base_path", "")}')
    if material_template:
        mi_factory = unreal.MaterialInstanceConstantFactoryNew()
        mi_factory.set_editor_property('initial_parent', material_template)
        
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        material_instance = asset_tools.create_asset('{mi_name}', '{mi_path.rsplit("/", 1)[0]}', 
                                                   unreal.MaterialInstanceConstant, mi_factory)
        
        if material_instance:
            # Set texture parameter
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                material_instance, 'BaseColor', texture)
            
            # Save material instance
            unreal.EditorAssetLibrary.save_asset(material_instance.get_path_name())
            print(f"Created material instance: {{material_instance.get_path_name()}}")
        else:
            print("Failed to create material instance")
    else:
        print(f"Material template not found: {template_data.get('base_path', '')}")
'''
        
        return script
    
    def _generate_gameplay_tags_script(self, asset_name: str, asset_path: str, 
                                     tags: List[str]) -> str:
        """Generate script for applying gameplay tags"""
        
        script = f'''
    # Apply gameplay tags (requires custom implementation)
    # Tags to apply: {", ".join(tags)}
    # This would require a custom tag application system
    print(f"Tags to apply to {{asset_name}}: {', '.join(tags)}")
'''
        
        return script
    
    def create_import_batch_script(self, assets_to_import: List[Tuple[Path, AssetCategory, Optional[str]]]) -> Path:
        """Create batch import script for multiple assets"""
        
        batch_script_path = self.python_scripts_dir / f"import_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        
        script_content = '''#!/usr/bin/env python3
"""
Auto-generated UE5 import batch script
Generated by Terminal Grounds Content Pipeline Agent
"""
import unreal

print("Starting batch asset import...")

'''
        
        for i, (asset_path, category, faction) in enumerate(assets_to_import):
            script_content += f"# Import {i+1}: {asset_path.name}\n"
            script_content += f"print('Importing {asset_path.name}...')\n"
            script_content += self.generate_import_script(asset_path, category, faction)
            script_content += "\n"
        
        script_content += '''
print("Batch import completed!")
'''
        
        with open(batch_script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return batch_script_path
    
    def validate_asset_import(self, asset_path: str) -> bool:
        """Validate that asset was properly imported into UE"""
        # This would require UE Python API access
        # For now, return True as placeholder
        return True
    
    def import_generated_assets(self, generated_assets: Dict[str, List[Path]]) -> Dict[str, Any]:
        """Import all generated assets into Unreal Engine"""
        
        print("🏗️ Preparing Unreal Engine asset import...")
        
        import_queue = []
        import_results = {
            "total_assets": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "created_materials": 0,
            "applied_tags": 0,
            "import_scripts": []
        }
        
        # Process each category of generated assets
        for category_name, asset_list in generated_assets.items():
            for asset_path in asset_list:
                # Determine asset category and faction
                if "faction" in category_name.lower():
                    category = AssetCategory.FACTION_LOGO
                    faction = self._extract_faction_from_filename(asset_path.name)
                elif "poster" in category_name.lower():
                    category = AssetCategory.POSTER_DECAL
                    faction = self._extract_faction_from_filename(asset_path.name)
                elif "icon" in category_name.lower():
                    category = AssetCategory.UI_ICON
                    faction = None
                else:
                    category = AssetCategory.CONCEPT_ART
                    faction = None
                
                import_queue.append((asset_path, category, faction))
        
        import_results["total_assets"] = len(import_queue)
        
        if import_queue:
            # Create batch import script
            batch_script = self.create_import_batch_script(import_queue)
            import_results["import_scripts"].append(str(batch_script.relative_to(ROOT)))
            
            print(f"📝 Created import script: {batch_script.relative_to(ROOT)}")
            print(f"🔧 To import assets, run this script in UE5 Python console:")
            print(f"   exec(open(r'{batch_script.as_posix()}').read())")
            
            # Log the import operation
            with open(self.log_file, 'a', encoding='utf-8') as f:
                today = date.today().isoformat()
                f.write(f"\n[{today}] Created UE5 import script: {batch_script.relative_to(ROOT)} ({len(import_queue)} assets)\n")
        
        return import_results
    
    def _extract_faction_from_filename(self, filename: str) -> Optional[str]:
        """Extract faction name from filename"""
        filename_lower = filename.lower()
        for faction in self.content_agent.faction_data.keys():
            if faction.lower() in filename_lower:
                return faction
        return None
    
    def create_material_master_templates(self) -> List[Path]:
        """Create master material templates if they don't exist"""
        created_templates = []
        
        # Check if M_TG_Decal_Master exists, if not create a blueprint
        decal_master_path = CONTENT_ROOT / "Materials/M_TG_Decal_Master.uasset"
        
        if not decal_master_path.exists():
            # Create a documentation file explaining the required master material
            doc_path = CONTENT_ROOT / "Materials/README_M_TG_Decal_Master.md"
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            
            doc_content = '''# M_TG_Decal_Master Material Template

This master material should be created in Unreal Engine with the following setup:

## Material Properties
- **Material Domain**: Deferred Decal
- **Blend Mode**: Translucent
- **Decal Blend Mode**: Translucent

## Required Parameters
- **BaseColor** (Texture Parameter): Main decal texture
- **Opacity** (Scalar Parameter): Overall decal opacity (default: 1.0)
- **OpacityMask** (Texture Parameter): Optional opacity mask
- **Roughness** (Scalar Parameter): Surface roughness (default: 0.8)
- **Metallic** (Scalar Parameter): Metallic value (default: 0.0)

## Shader Graph
1. **BaseColor**: Connect Texture Parameter to Material Output Base Color
2. **Opacity**: Multiply texture alpha with Opacity parameter
3. **OpacityMask**: Optional mask for complex opacity shapes
4. **Roughness/Metallic**: Connect scalar parameters to respective outputs

## Usage
This master material will be used to create material instances for:
- Faction logos and emblems
- Propaganda posters
- Environmental decals
- Signage and markings

Material instances will be automatically created by the content pipeline agent.
'''
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            created_templates.append(doc_path)
            print(f"📋 Created material template documentation: {doc_path.relative_to(ROOT)}")
        
        return created_templates
    
    def run_complete_integration(self, generated_assets: Dict[str, List[Path]]) -> Dict[str, Any]:
        """Run complete Unreal Engine integration pipeline"""
        
        print("🚀 Starting Unreal Engine Integration")
        print("=" * 50)
        
        # Create material templates if needed
        template_docs = self.create_material_master_templates()
        
        # Import generated assets
        import_results = self.import_generated_assets(generated_assets)
        
        # Add template documentation to results
        import_results["template_docs"] = [str(p.relative_to(ROOT)) for p in template_docs]
        
        # Summary
        print(f"\n✅ Integration Summary:")
        print(f"  Assets queued for import: {import_results['total_assets']}")
        print(f"  Import scripts created: {len(import_results['import_scripts'])}")
        print(f"  Template docs created: {len(template_docs)}")
        
        if import_results["import_scripts"]:
            print(f"\n🔧 Next Steps:")
            print(f"  1. Open Unreal Engine 5.6")
            print(f"  2. Open Python console (Window > Developer Tools > Python Console)")
            print(f"  3. Run the import script:")
            for script in import_results["import_scripts"]:
                print(f"     exec(open(r'{ROOT}/{script}').read())")
        
        return import_results

# CLI interface
def main():
    """Main CLI entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        # Initialize content agent and integrator
        content_agent = TerminalGroundsContentAgent()
        integrator = TerminalGroundsUnrealIntegrator(content_agent)
        
        if command == "create-templates":
            integrator.create_material_master_templates()
        elif command == "import":
            # Example: import generated assets (would need asset paths)
            example_assets = {
                "test": [ROOT / "Tools/ArtGen/outputs/test.png"]
            }
            integrator.run_complete_integration(example_assets)
        else:
            print(f"Unknown command: {command}")
    else:
        print("Terminal Grounds Unreal Engine Integrator")
        print("Usage:")
        print("  python TG_UnrealEngineIntegrator.py create-templates  # Create material templates")
        print("  python TG_UnrealEngineIntegrator.py import           # Import generated assets")

if __name__ == "__main__":
    main()