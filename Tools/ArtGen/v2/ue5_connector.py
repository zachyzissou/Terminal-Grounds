#!/usr/bin/env python3
"""
UE5 Connector for Terminal Grounds v2.0
=======================================
Seamless integration between asset generation pipeline and Unreal Engine 5.6.
"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import logging
import tempfile

try:
    from .asset_spec import AssetSpecification, AssetType, FactionCode
    from .asset_manager import AssetRecord, AssetFile
except ImportError:
    from asset_spec import AssetSpecification, AssetType, FactionCode
    from asset_manager import AssetRecord, AssetFile

logger = logging.getLogger(__name__)

class UE5AssetType(Enum):
    TEXTURE_2D = "Texture2D"
    MATERIAL = "Material"
    MATERIAL_INSTANCE = "MaterialInstance"
    STATIC_MESH = "StaticMesh"
    BLUEPRINT = "Blueprint"
    WIDGET_BLUEPRINT = "WidgetBlueprint"
    DATA_ASSET = "DataAsset"

class ImportStatus(Enum):
    PENDING = "pending"
    IMPORTING = "importing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class UE5ImportTask:
    """Represents a UE5 import task"""
    task_id: str
    asset_record: AssetRecord
    target_path: str
    import_settings: Dict[str, Any]
    status: ImportStatus = ImportStatus.PENDING
    ue5_assets: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UE5ProjectConfig:
    """UE5 project configuration"""
    project_path: Path
    content_dir: Path
    python_executable: Path
    ue5_cmd_path: Path
    asset_base_path: str = "/Game/Generated"
    material_base_path: str = "/Game/Generated/Materials"
    texture_base_path: str = "/Game/Generated/Textures"
    blueprint_base_path: str = "/Game/Generated/Blueprints"

class UE5AssetProcessor:
    """Processes assets for UE5 import with proper naming and organization"""
    
    def __init__(self, project_config: UE5ProjectConfig):
        self.project_config = project_config
        
        # Asset type mapping
        self.asset_type_mapping = {
            "weapon": {
                "ue5_type": UE5AssetType.TEXTURE_2D,
                "path_suffix": "Weapons",
                "create_material": True
            },
            "vehicle": {
                "ue5_type": UE5AssetType.TEXTURE_2D,
                "path_suffix": "Vehicles",
                "create_material": True
            },
            "emblem": {
                "ue5_type": UE5AssetType.TEXTURE_2D,
                "path_suffix": "Emblems",
                "create_material": False
            },
            "poster": {
                "ue5_type": UE5AssetType.TEXTURE_2D,
                "path_suffix": "Posters",
                "create_material": False
            },
            "icon": {
                "ue5_type": UE5AssetType.TEXTURE_2D,
                "path_suffix": "Icons",
                "create_material": False
            },
            "concept": {
                "ue5_type": UE5AssetType.TEXTURE_2D,
                "path_suffix": "Concepts",
                "create_material": False
            },
            "texture": {
                "ue5_type": UE5AssetType.TEXTURE_2D,
                "path_suffix": "Materials",
                "create_material": True
            },
            "ui": {
                "ue5_type": UE5AssetType.TEXTURE_2D,
                "path_suffix": "UI",
                "create_material": False
            }
        }
        
        # Faction prefixes for asset naming
        self.faction_prefixes = {
            "directorate": "DIR",
            "free77": "F77",
            "vultures": "VLT",
            "combine": "CMB",
            "nomads": "NMD",
            "archivists": "ARC",
            "wardens": "WRD",
            "neutral": "NEU"
        }
    
    def generate_ue5_paths(self, asset_record: AssetRecord) -> Dict[str, str]:
        """Generate UE5 asset paths based on asset specification"""
        
        spec = asset_record.asset_spec
        faction_prefix = self.faction_prefixes.get(spec.faction, "UNK")
        asset_config = self.asset_type_mapping.get(spec.asset_type, self.asset_type_mapping["concept"])
        
        # Clean asset name for UE5
        clean_name = self._sanitize_ue5_name(spec.name)
        
        # Base paths
        texture_path = f"{self.project_config.texture_base_path}/{spec.faction.title()}/{asset_config['path_suffix']}"
        material_path = f"{self.project_config.material_base_path}/{spec.faction.title()}/{asset_config['path_suffix']}"
        
        # Asset naming convention: PREFIX_AssetType_Name
        asset_type_abbrev = self._get_asset_type_abbreviation(spec.asset_type)
        base_name = f"{faction_prefix}_{asset_type_abbrev}_{clean_name}"
        
        paths = {
            "texture": f"{texture_path}/T_{base_name}",
            "base_name": base_name
        }
        
        # Add material path if needed
        if asset_config["create_material"]:
            paths["material"] = f"{material_path}/M_{base_name}"
            paths["material_instance"] = f"{material_path}/MI_{base_name}"
        
        return paths
    
    def prepare_import_settings(self, asset_record: AssetRecord) -> Dict[str, Any]:
        """Prepare UE5 import settings based on asset type and quality"""
        
        spec = asset_record.asset_spec
        asset_config = self.asset_type_mapping.get(spec.asset_type, self.asset_type_mapping["concept"])
        
        # Base import settings
        settings = {
            "bImportTextures": True,
            "bAllowNonPowerOfTwo": True,
            "CompressionSettings": "TC_Default",
            "LODGroup": "TEXTUREGROUP_World",
            "MipGenSettings": "TMGS_FromTextureGroup",
            "PowerOfTwoMode": "None",
            "PaddingColor": "(R=0,G=0,B=0,A=0)",
            "bFlipGreenChannel": False,
            "bUseNewMipFilter": True
        }
        
        # Asset-specific settings
        if spec.asset_type in ["emblem", "icon", "ui"]:
            settings.update({
                "CompressionSettings": "TC_EditorIcon",
                "LODGroup": "TEXTUREGROUP_UI",
                "Filter": "TF_Trilinear",
                "bPreserveBorder": True
            })
        elif spec.asset_type in ["poster", "concept"]:
            settings.update({
                "CompressionSettings": "TC_Default",
                "LODGroup": "TEXTUREGROUP_World",
                "Filter": "TF_Default"
            })
        elif spec.asset_type == "texture":
            settings.update({
                "CompressionSettings": "TC_Default",
                "LODGroup": "TEXTUREGROUP_WorldNormalMap" if "normal" in spec.name.lower() else "TEXTUREGROUP_World",
                "SRGB": "normal" not in spec.name.lower()  # Disable SRGB for normal maps
            })
        
        # Quality-based settings
        if asset_record.quality_score and asset_record.quality_score >= 85:
            settings.update({
                "CompressionQuality": "TCQ_Highest",
                "MaxTextureSize": 4096
            })
        elif asset_record.quality_score and asset_record.quality_score >= 75:
            settings.update({
                "CompressionQuality": "TCQ_High",
                "MaxTextureSize": 2048
            })
        else:
            settings.update({
                "CompressionQuality": "TCQ_Default",
                "MaxTextureSize": 1024
            })
        
        return settings
    
    def create_material_data(self, asset_record: AssetRecord, texture_path: str) -> Dict[str, Any]:
        """Create material and material instance data"""
        
        spec = asset_record.asset_spec
        faction_colors = self._get_faction_colors(spec.faction)
        
        # Base material data
        material_data = {
            "texture_reference": texture_path,
            "faction_colors": faction_colors,
            "metallic": 0.0,
            "roughness": 0.8,
            "specular": 0.5,
            "emissive_strength": 0.0
        }
        
        # Asset-specific material properties
        if spec.asset_type == "weapon":
            material_data.update({
                "metallic": 0.8,
                "roughness": 0.3,
                "specular": 0.9
            })
        elif spec.asset_type == "vehicle":
            material_data.update({
                "metallic": 0.6,
                "roughness": 0.4,
                "specular": 0.7
            })
        elif spec.asset_type in ["emblem", "poster"]:
            material_data.update({
                "emissive_strength": 1.0,
                "unlit": True
            })
        
        return material_data
    
    def _sanitize_ue5_name(self, name: str) -> str:
        """Sanitize name for UE5 compatibility"""
        import re
        
        # Remove special characters and replace with underscores
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        # Remove multiple underscores
        clean_name = re.sub(r'_+', '_', clean_name)
        
        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')
        
        # Ensure it doesn't start with a number
        if clean_name and clean_name[0].isdigit():
            clean_name = f"Asset_{clean_name}"
        
        return clean_name or "UnnamedAsset"
    
    def _get_asset_type_abbreviation(self, asset_type: AssetType) -> str:
        """Get abbreviation for asset type"""
        abbreviations = {
            "weapon": "WPN",
            "vehicle": "VEH",
            "emblem": "EMB",
            "poster": "PST",
            "icon": "ICN",
            "concept": "CON",
            "environment": "ENV",
            "texture": "TEX",
            "ui": "UI"
        }
        return abbreviations.get(asset_type, "AST")
    
    def _get_faction_colors(self, faction: FactionCode) -> Dict[str, str]:
        """Get faction color palette"""
        faction_colors = {
            "directorate": {"primary": "#2B4C8C", "secondary": "#C0C0C0", "accent": "#FFD700"},
            "free77": {"primary": "#8B4513", "secondary": "#F4A460", "accent": "#FF4500"},
            "vultures": {"primary": "#2F2F2F", "secondary": "#FFD700", "accent": "#FF6600"},
            "combine": {"primary": "#4682B4", "secondary": "#E6E6FA", "accent": "#00CED1"},
            "nomads": {"primary": "#D2691E", "secondary": "#F5DEB3", "accent": "#FF8C00"},
            "archivists": {"primary": "#556B2F", "secondary": "#F0E68C", "accent": "#DAA520"},
            "wardens": {"primary": "#483D8B", "secondary": "#FFA500", "accent": "#FF4500"},
            "neutral": {"primary": "#808080", "secondary": "#D3D3D3", "accent": "#A9A9A9"}
        }
        return faction_colors.get(faction, faction_colors["neutral"])

class UE5PythonScriptGenerator:
    """Generates UE5 Python scripts for asset import and processing"""
    
    def __init__(self, project_config: UE5ProjectConfig):
        self.project_config = project_config
    
    def generate_import_script(self, import_task: UE5ImportTask) -> str:
        """Generate Python script for UE5 asset import"""
        
        processor = UE5AssetProcessor(self.project_config)
        paths = processor.generate_ue5_paths(import_task.asset_record)
        import_settings = processor.prepare_import_settings(import_task.asset_record)
        
        # Get primary asset file
        primary_file = import_task.asset_record.primary_file
        if not primary_file:
            raise ValueError("No primary file found for asset")
        
        script = f'''
import unreal

def import_asset():
    """Import asset to UE5 with proper settings"""
    
    # Asset import data
    source_file = r"{primary_file.path}"
    destination_path = "{paths['texture']}"
    
    # Import settings
    import_data = unreal.AutomatedAssetImportData()
    import_data.set_editor_property('filenames', [source_file])
    import_data.set_editor_property('destination_path', destination_path.rsplit('/', 1)[0])
    
    # Texture import options
    texture_options = unreal.TextureImportOptions()
'''
        
        # Add import settings
        for key, value in import_settings.items():
            if isinstance(value, bool):
                script += f'    texture_options.set_editor_property("{key.lower()}", {str(value).lower()})\n'
            elif isinstance(value, str):
                script += f'    texture_options.set_editor_property("{key.lower()}", "{value}")\n'
            elif isinstance(value, (int, float)):
                script += f'    texture_options.set_editor_property("{key.lower()}", {value})\n'
        
        script += f'''
    import_data.set_editor_property('import_options', texture_options)
    
    # Import the asset
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    imported_assets = asset_tools.import_assets_automated(import_data)
    
    if imported_assets:
        imported_asset = imported_assets[0]
        print(f"Successfully imported: {{imported_asset.get_path_name()}}")
        
        # Set metadata
        metadata_tags = [
            ("TG_AssetType", "{import_task.asset_record.asset_spec.asset_type}"),
            ("TG_Faction", "{import_task.asset_record.asset_spec.faction}"),
            ("TG_QualityScore", "{import_task.asset_record.quality_score or 0}"),
            ("TG_Version", "{import_task.asset_record.version}"),
            ("TG_ImportDate", "{time.strftime('%Y-%m-%d %H:%M:%S')}")
        ]
        
        for tag_name, tag_value in metadata_tags:
            unreal.EditorAssetLibrary.set_metadata_tag(imported_asset, tag_name, str(tag_value))
        
        return imported_asset.get_path_name()
    else:
        print("Import failed")
        return None

# Execute import
if __name__ == "__main__":
    result = import_asset()
    if result:
        print(f"IMPORT_SUCCESS: {{result}}")
    else:
        print("IMPORT_FAILED")
'''
        
        return script
    
    def generate_material_creation_script(self, import_task: UE5ImportTask, texture_path: str) -> str:
        """Generate script to create material and material instance"""
        
        processor = UE5AssetProcessor(self.project_config)
        paths = processor.generate_ue5_paths(import_task.asset_record)
        material_data = processor.create_material_data(import_task.asset_record, texture_path)
        
        script = f'''
import unreal

def create_material():
    """Create material and material instance for imported texture"""
    
    # Load the imported texture
    texture_asset = unreal.EditorAssetLibrary.load_asset("{texture_path}")
    if not texture_asset:
        print("Failed to load texture asset")
        return None
    
    # Create material
    material_path = "{paths['material']}"
    material_name = material_path.split('/')[-1]
    material_package_path = '/'.join(material_path.split('/')[:-1])
    
    # Create material asset
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    material_factory = unreal.MaterialFactoryNew()
    
    material = asset_tools.create_asset(
        asset_name=material_name,
        package_path=material_package_path,
        asset_class=unreal.Material,
        factory=material_factory
    )
    
    if material:
        print(f"Created material: {{material.get_path_name()}}")
        
        # Set up material nodes
        material_editing_library = unreal.MaterialEditingLibrary
        
        # Create texture sample node
        texture_sample = material_editing_library.create_material_expression(
            material, unreal.MaterialExpressionTextureSample, -400, 0
        )
        texture_sample.texture = texture_asset
        
        # Connect to base color
        material_editing_library.connect_material_property(
            texture_sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR
        )
'''
        
        # Add faction-specific material properties
        faction_colors = material_data["faction_colors"]
        script += f'''
        # Add faction color tint
        color_node = material_editing_library.create_material_expression(
            material, unreal.MaterialExpressionVectorParameter, -600, 100
        )
        color_node.parameter_name = "FactionTint"
        color_node.default_value = unreal.LinearColor({
            float(int(faction_colors["primary"][1:3], 16))/255.0}, {
            float(int(faction_colors["primary"][3:5], 16))/255.0}, {
            float(int(faction_colors["primary"][5:7], 16))/255.0}, 1.0)
        
        # Multiply texture with faction color
        multiply_node = material_editing_library.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -200, 50
        )
        
        material_editing_library.connect_material_expressions(
            texture_sample, "RGB", multiply_node, "A"
        )
        material_editing_library.connect_material_expressions(
            color_node, "", multiply_node, "B"
        )
        material_editing_library.connect_material_property(
            multiply_node, "", unreal.MaterialProperty.MP_BASE_COLOR
        )
'''
        
        # Add metallic and roughness if needed
        if material_data.get("metallic", 0) > 0:
            script += f'''
        # Metallic
        metallic_node = material_editing_library.create_material_expression(
            material, unreal.MaterialExpressionConstant, -400, 200
        )
        metallic_node.r = {material_data["metallic"]}
        material_editing_library.connect_material_property(
            metallic_node, "", unreal.MaterialProperty.MP_METALLIC
        )
        
        # Roughness
        roughness_node = material_editing_library.create_material_expression(
            material, unreal.MaterialExpressionConstant, -400, 300
        )
        roughness_node.r = {material_data["roughness"]}
        material_editing_library.connect_material_property(
            roughness_node, "", unreal.MaterialProperty.MP_ROUGHNESS
        )
'''
        
        # Handle emissive materials
        if material_data.get("unlit", False):
            script += '''
        material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        
        # Connect texture to emissive
        material_editing_library.connect_material_property(
            multiply_node, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR
        )
'''
        
        script += f'''
        # Compile and save material
        material_editing_library.recompile_material(material)
        unreal.EditorAssetLibrary.save_asset(material.get_path_name())
        
        # Create material instance
        mi_path = "{paths.get('material_instance', paths['material'] + '_Inst')}"
        mi_name = mi_path.split('/')[-1]
        mi_package_path = '/'.join(mi_path.split('/')[:-1])
        
        mi_factory = unreal.MaterialInstanceConstantFactoryNew()
        mi_factory.initial_parent = material
        
        material_instance = asset_tools.create_asset(
            asset_name=mi_name,
            package_path=mi_package_path,
            asset_class=unreal.MaterialInstanceConstant,
            factory=mi_factory
        )
        
        if material_instance:
            print(f"Created material instance: {{material_instance.get_path_name()}}")
            
            # Set metadata for both assets
            metadata_tags = [
                ("TG_AssetType", "{import_task.asset_record.asset_spec.asset_type}"),
                ("TG_Faction", "{import_task.asset_record.asset_spec.faction}"),
                ("TG_SourceTexture", "{texture_path}")
            ]
            
            for tag_name, tag_value in metadata_tags:
                unreal.EditorAssetLibrary.set_metadata_tag(material, tag_name, tag_value)
                unreal.EditorAssetLibrary.set_metadata_tag(material_instance, tag_name, tag_value)
            
            return material_instance.get_path_name()
    
    return None

# Execute material creation
if __name__ == "__main__":
    result = create_material()
    if result:
        print(f"MATERIAL_SUCCESS: {{result}}")
    else:
        print("MATERIAL_FAILED")
'''
        
        return script

class UE5Connector:
    """
    Main UE5 integration connector for Terminal Grounds pipeline.
    Handles asset import, material creation, and UE5 project integration.
    """
    
    def __init__(self, project_config: UE5ProjectConfig):
        self.project_config = project_config
        self.processor = UE5AssetProcessor(project_config)
        self.script_generator = UE5PythonScriptGenerator(project_config)
        
        # Validate UE5 setup
        self._validate_ue5_setup()
        
        # Import tracking
        self.active_imports: Dict[str, UE5ImportTask] = {}
        
        logger.info(f"UE5 Connector initialized for project: {project_config.project_path}")
    
    def import_asset(self, asset_record: AssetRecord, 
                    create_materials: Optional[bool] = None,
                    target_path: Optional[str] = None) -> UE5ImportTask:
        """
        Import asset to UE5 with automatic material creation
        
        Args:
            asset_record: Asset record to import
            create_materials: Whether to create materials (auto-determined if None)
            target_path: Custom target path (auto-generated if None)
            
        Returns:
            Import task for tracking progress
        """
        
        # Generate task ID
        task_id = f"import_{int(time.time() * 1000)}"
        
        # Determine target path
        if not target_path:
            paths = self.processor.generate_ue5_paths(asset_record)
            target_path = paths["texture"]
        
        # Determine if we should create materials
        if create_materials is None:
            asset_config = self.processor.asset_type_mapping.get(
                asset_record.asset_spec.asset_type,
                self.processor.asset_type_mapping["concept"]
            )
            create_materials = asset_config["create_material"]
        
        # Create import task
        import_task = UE5ImportTask(
            task_id=task_id,
            asset_record=asset_record,
            target_path=target_path,
            import_settings=self.processor.prepare_import_settings(asset_record),
            metadata={"create_materials": create_materials}
        )
        
        self.active_imports[task_id] = import_task
        
        try:
            # Execute import
            self._execute_import(import_task)
            
            # Create materials if requested
            if create_materials and import_task.status == ImportStatus.COMPLETED:
                self._create_materials(import_task)
            
            return import_task
            
        except Exception as e:
            import_task.status = ImportStatus.FAILED
            import_task.error_message = str(e)
            import_task.completion_time = time.time()
            logger.error(f"Import failed for task {task_id}: {e}")
            return import_task
    
    def batch_import_assets(self, asset_records: List[AssetRecord],
                          progress_callback: Optional[callable] = None) -> List[UE5ImportTask]:
        """Import multiple assets in batch"""
        
        import_tasks = []
        
        for i, asset_record in enumerate(asset_records):
            try:
                logger.info(f"Importing asset {i+1}/{len(asset_records)}: {asset_record.asset_spec.name}")
                
                import_task = self.import_asset(asset_record)
                import_tasks.append(import_task)
                
                if progress_callback:
                    progress_callback(i + 1, len(asset_records), import_task)
                
            except Exception as e:
                logger.error(f"Failed to import asset {asset_record.asset_spec.name}: {e}")
                continue
        
        return import_tasks
    
    def _execute_import(self, import_task: UE5ImportTask):
        """Execute the UE5 import process"""
        
        import_task.status = ImportStatus.IMPORTING
        import_task.start_time = time.time()
        
        try:
            # Generate import script
            import_script = self.script_generator.generate_import_script(import_task)
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(import_script)
                script_path = f.name
            
            # Execute UE5 Python script
            result = self._run_ue5_python_script(script_path)
            
            # Parse result
            if "IMPORT_SUCCESS:" in result:
                asset_path = result.split("IMPORT_SUCCESS:")[-1].strip()
                import_task.ue5_assets.append(asset_path)
                import_task.status = ImportStatus.PROCESSING
                logger.info(f"Import successful: {asset_path}")
            else:
                raise Exception(f"Import failed: {result}")
            
            # Cleanup
            Path(script_path).unlink(missing_ok=True)
            
        except Exception as e:
            import_task.status = ImportStatus.FAILED
            import_task.error_message = str(e)
            import_task.completion_time = time.time()
            raise
    
    def _create_materials(self, import_task: UE5ImportTask):
        """Create materials for imported texture"""
        
        if not import_task.ue5_assets:
            logger.warning("No imported assets found for material creation")
            return
        
        try:
            # Use first imported asset as texture
            texture_path = import_task.ue5_assets[0]
            
            # Generate material creation script
            material_script = self.script_generator.generate_material_creation_script(
                import_task, texture_path
            )
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(material_script)
                script_path = f.name
            
            # Execute material creation
            result = self._run_ue5_python_script(script_path)
            
            # Parse result
            if "MATERIAL_SUCCESS:" in result:
                material_path = result.split("MATERIAL_SUCCESS:")[-1].strip()
                import_task.ue5_assets.append(material_path)
                logger.info(f"Material created: {material_path}")
            else:
                logger.warning(f"Material creation failed: {result}")
            
            # Mark as completed
            import_task.status = ImportStatus.COMPLETED
            import_task.completion_time = time.time()
            
            # Cleanup
            Path(script_path).unlink(missing_ok=True)
            
        except Exception as e:
            logger.error(f"Material creation failed: {e}")
            # Don't fail the entire import for material creation issues
            import_task.status = ImportStatus.COMPLETED
            import_task.completion_time = time.time()
    
    def _run_ue5_python_script(self, script_path: str) -> str:
        """Run Python script in UE5 Editor"""
        
        try:
            # UE5 command line arguments
            cmd = [
                str(self.project_config.ue5_cmd_path),
                str(self.project_config.project_path),
                "-ExecutePythonScript=" + script_path,
                "-unattended",
                "-nopause",
                "-nosplash",
                "-nullrhi"
            ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=self.project_config.project_path.parent
            )
            
            # Check result
            if result.returncode != 0:
                logger.error(f"UE5 execution failed: {result.stderr}")
                return f"ERROR: {result.stderr}"
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            logger.error("UE5 script execution timed out")
            return "ERROR: Execution timeout"
        except Exception as e:
            logger.error(f"Failed to execute UE5 script: {e}")
            return f"ERROR: {str(e)}"
    
    def _validate_ue5_setup(self):
        """Validate UE5 installation and project setup"""
        
        # Check UE5 executable
        if not self.project_config.ue5_cmd_path.exists():
            raise FileNotFoundError(f"UE5 executable not found: {self.project_config.ue5_cmd_path}")
        
        # Check project file
        if not self.project_config.project_path.exists():
            raise FileNotFoundError(f"UE5 project not found: {self.project_config.project_path}")
        
        # Check content directory
        if not self.project_config.content_dir.exists():
            logger.warning(f"Content directory not found, creating: {self.project_config.content_dir}")
            self.project_config.content_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("UE5 setup validation passed")
    
    def get_import_status(self, task_id: str) -> Optional[UE5ImportTask]:
        """Get status of import task"""
        return self.active_imports.get(task_id)
    
    def list_ue5_assets(self, asset_path: str = "/Game/Generated") -> List[Dict[str, Any]]:
        """List assets in UE5 project"""
        
        # This would use UE5's asset registry API
        # For now, return placeholder data
        logger.info(f"Listing UE5 assets in {asset_path}")
        return []
    
    def cleanup_failed_imports(self) -> int:
        """Clean up failed import tasks"""
        
        cleaned_count = 0
        current_time = time.time()
        
        for task_id, task in list(self.active_imports.items()):
            if (task.status == ImportStatus.FAILED or
                (task.start_time and current_time - task.start_time > 600)):  # 10 minutes
                del self.active_imports[task_id]
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} failed import tasks")
        return cleaned_count
    
    def get_import_statistics(self) -> Dict[str, Any]:
        """Get import statistics"""
        
        stats = {
            "total_imports": len(self.active_imports),
            "by_status": {},
            "by_asset_type": {},
            "by_faction": {},
            "average_import_time": 0.0
        }
        
        import_times = []
        
        for task in self.active_imports.values():
            # Count by status
            status = task.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Count by asset type
            asset_type = task.asset_record.asset_spec.asset_type
            stats["by_asset_type"][asset_type] = stats["by_asset_type"].get(asset_type, 0) + 1
            
            # Count by faction
            faction = task.asset_record.asset_spec.faction
            stats["by_faction"][faction] = stats["by_faction"].get(faction, 0) + 1
            
            # Collect import times
            if task.start_time and task.completion_time:
                import_times.append(task.completion_time - task.start_time)
        
        if import_times:
            stats["average_import_time"] = sum(import_times) / len(import_times)
        
        return stats

def create_ue5_config(project_name: str = "TerminalGrounds") -> UE5ProjectConfig:
    """Create UE5 configuration with sensible defaults"""
    
    # Default paths - adjust based on your setup
    base_path = Path("C:/UnrealEngine")
    project_base = Path("C:/UnrealProjects")
    
    return UE5ProjectConfig(
        project_path=project_base / project_name / f"{project_name}.uproject",
        content_dir=project_base / project_name / "Content",
        python_executable=Path("C:/Python/python.exe"),  # Adjust to your Python
        ue5_cmd_path=base_path / "UE_5.6" / "Engine" / "Binaries" / "Win64" / "UnrealEditor-Cmd.exe"
    )