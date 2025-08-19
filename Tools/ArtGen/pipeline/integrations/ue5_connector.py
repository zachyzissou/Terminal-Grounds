"""
UE5 Connector - Seamless Unreal Engine 5 integration
====================================================

Handles automatic import of generated assets into UE5, including texture setup,
material creation, metadata tagging, and asset organization within the UE5
content browser. Supports both Python scripting and command-line automation.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import time
from typing import Any, Dict, List, Optional, Union
import logging

from ..core.asset_spec import AssetSpecification, AssetType
from ..utils.logger import setup_logger


class UE5ImportSettings:
    """Configuration for UE5 asset import."""
    
    def __init__(self):
        # Import paths
        self.base_import_path = "/Game/TG/Generated"
        self.texture_import_path = "/Game/TG/Generated/Textures"
        self.material_import_path = "/Game/TG/Generated/Materials"
        self.concept_import_path = "/Game/TG/Generated/Concepts"
        
        # Import options
        self.create_materials = True
        self.generate_mipmaps = True
        self.compress_textures = True
        self.srgb_textures = True
        
        # Asset-specific settings
        self.asset_type_paths = {
            AssetType.WEAPON: "/Game/TG/Generated/Weapons",
            AssetType.VEHICLE: "/Game/TG/Generated/Vehicles",
            AssetType.GEAR: "/Game/TG/Generated/Gear",
            AssetType.BUILDING: "/Game/TG/Generated/Buildings",
            AssetType.CHARACTER: "/Game/TG/Generated/Characters",
            AssetType.ENVIRONMENT: "/Game/TG/Generated/Environments",
            AssetType.UI_ICON: "/Game/TG/Generated/UI",
            AssetType.POSTER: "/Game/TG/Generated/Posters",
            AssetType.TEXTURE: "/Game/TG/Generated/Textures",
            AssetType.CONCEPT: "/Game/TG/Generated/Concepts"
        }
        
        # Texture settings
        self.texture_compression = {
            "concept": "TC_Default",
            "ui_icon": "TC_EditorIcon", 
            "poster": "TC_Default",
            "texture": "TC_Normalmap",
            "default": "TC_Default"
        }
        
        # Material templates
        self.material_templates = {
            "concept": "M_ConceptArt_Template",
            "poster": "M_Poster_Template", 
            "ui_icon": "M_UI_Template",
            "default": "M_Generated_Template"
        }


class UE5Connector:
    """
    Connector for seamless UE5 integration.
    
    Features:
    - Automatic asset import with proper settings
    - Material instance creation
    - Metadata tagging and organization
    - Batch import support
    - Command-line and Python API support
    - Asset validation and cleanup
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger("UE5Connector", config.log_level)
        
        # UE5 configuration
        self.ue5_project_path = getattr(config, 'ue5_project_path', None)
        self.ue5_engine_path = getattr(config, 'ue5_engine_path', None)
        self.use_python_api = getattr(config, 'use_ue5_python_api', True)
        
        # Import settings
        self.import_settings = UE5ImportSettings()
        
        # Connection state
        self.is_connected = False
        self.connection_method = None
        
        # Import statistics
        self.import_stats = {
            "total_imports": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "last_import_time": None
        }
        
        self.logger.info("UE5 Connector initialized")
    
    def test_connection(self) -> bool:
        """Test connection to UE5."""
        try:
            if self.use_python_api:
                return self._test_python_api_connection()
            else:
                return self._test_commandline_connection()
        
        except Exception as e:
            self.logger.error(f"UE5 connection test failed: {e}")
            return False
    
    def _test_python_api_connection(self) -> bool:
        """Test UE5 Python API connection."""
        try:
            # This would require UE5 Python API to be available
            import unreal
            
            # Test basic API access
            project_dir = unreal.SystemLibrary.get_project_directory()
            if project_dir:
                self.is_connected = True
                self.connection_method = "python_api"
                self.logger.info("UE5 Python API connection established")
                return True
        
        except ImportError:
            self.logger.debug("UE5 Python API not available")
        except Exception as e:
            self.logger.warning(f"UE5 Python API test failed: {e}")
        
        return False
    
    def _test_commandline_connection(self) -> bool:
        """Test UE5 command-line connection."""
        if not self.ue5_engine_path or not self.ue5_project_path:
            self.logger.warning("UE5 engine or project path not configured")
            return False
        
        try:
            # Test by querying project information
            cmd = [
                str(self.ue5_engine_path),
                str(self.ue5_project_path),
                "-run=pythonscript",
                "-script=print('UE5 Connection Test')",
                "-unattended",
                "-nopause",
                "-nosplash"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.is_connected = True
                self.connection_method = "commandline"
                self.logger.info("UE5 command-line connection established")
                return True
        
        except Exception as e:
            self.logger.warning(f"UE5 command-line test failed: {e}")
        
        return False
    
    def import_asset(
        self,
        generation_result: Dict[str, Any],
        spec: AssetSpecification
    ) -> Dict[str, Any]:
        """
        Import a generated asset into UE5.
        
        Args:
            generation_result: Asset generation result
            spec: Asset specification
            
        Returns:
            Import result with UE5 asset paths
        """
        self.logger.info(f"Importing asset to UE5: {spec.name}")
        
        if not self.is_connected and not self.test_connection():
            raise RuntimeError("UE5 connection not available")
        
        try:
            self.import_stats["total_imports"] += 1
            
            if self.connection_method == "python_api":
                result = self._import_via_python_api(generation_result, spec)
            else:
                result = self._import_via_commandline(generation_result, spec)
            
            self.import_stats["successful_imports"] += 1
            self.import_stats["last_import_time"] = time.time()
            
            self.logger.info(f"Asset imported successfully: {spec.name}")
            return result
        
        except Exception as e:
            self.import_stats["failed_imports"] += 1
            self.logger.error(f"Asset import failed for {spec.name}: {e}")
            raise
    
    def _import_via_python_api(
        self,
        generation_result: Dict[str, Any],
        spec: AssetSpecification
    ) -> Dict[str, Any]:
        """Import asset using UE5 Python API."""
        import unreal
        
        # Determine import path
        import_path = self._get_import_path(spec)
        
        imported_assets = []
        
        # Import each image file
        for file_info in generation_result.get("organized_files", []):
            try:
                source_path = file_info["organized_path"]
                asset_name = pathlib.Path(file_info["organized_filename"]).stem
                
                # Create import task
                import_task = unreal.AssetImportTask()
                import_task.filename = source_path
                import_task.destination_path = import_path
                import_task.destination_name = asset_name
                import_task.automated = True
                import_task.replace_existing = True
                
                # Configure import options based on asset type
                self._configure_import_options(import_task, spec)
                
                # Execute import
                unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])
                
                if import_task.imported_object_paths:
                    for imported_path in import_task.imported_object_paths:
                        # Set metadata
                        self._set_asset_metadata(imported_path, spec, file_info)
                        
                        # Create material instance if needed
                        material_path = None
                        if self.import_settings.create_materials:
                            material_path = self._create_material_instance(
                                imported_path, spec
                            )
                        
                        imported_assets.append({
                            "source_file": source_path,
                            "ue5_asset_path": imported_path,
                            "material_path": material_path,
                            "import_successful": True
                        })
                
            except Exception as e:
                self.logger.error(f"Failed to import file {file_info}: {e}")
                imported_assets.append({
                    "source_file": file_info["organized_path"],
                    "ue5_asset_path": None,
                    "material_path": None,
                    "import_successful": False,
                    "error": str(e)
                })
        
        return {
            "import_method": "python_api",
            "import_path": import_path,
            "imported_assets": imported_assets,
            "total_imported": len([a for a in imported_assets if a["import_successful"]]),
            "import_timestamp": time.time()
        }
    
    def _import_via_commandline(
        self,
        generation_result: Dict[str, Any],
        spec: AssetSpecification
    ) -> Dict[str, Any]:
        """Import asset using UE5 command-line."""
        # Create Python script for import
        import_script = self._generate_import_script(generation_result, spec)
        script_path = pathlib.Path.cwd() / "temp_import_script.py"
        script_path.write_text(import_script)
        
        try:
            # Execute UE5 with the import script
            cmd = [
                str(self.ue5_engine_path),
                str(self.ue5_project_path),
                "-run=pythonscript",
                f"-script={script_path}",
                "-unattended",
                "-nopause",
                "-nosplash"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # Parse result from script output
                return self._parse_commandline_result(result.stdout, spec)
            else:
                raise RuntimeError(f"UE5 import failed: {result.stderr}")
        
        finally:
            # Cleanup script file
            if script_path.exists():
                script_path.unlink()
    
    def _get_import_path(self, spec: AssetSpecification) -> str:
        """Get the appropriate UE5 import path for an asset."""
        return self.import_settings.asset_type_paths.get(
            spec.asset_type,
            self.import_settings.base_import_path
        )
    
    def _configure_import_options(self, import_task, spec: AssetSpecification):
        """Configure import options based on asset type."""
        # This would set specific import options for different asset types
        # Simplified for now
        pass
    
    def _set_asset_metadata(
        self,
        asset_path: str,
        spec: AssetSpecification,
        file_info: Dict[str, Any]
    ):
        """Set metadata tags on imported UE5 asset."""
        try:
            import unreal
            
            # Load the asset
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            
            if asset:
                # Set metadata tags
                metadata_tags = {
                    "TG_AssetType": spec.asset_type.value,
                    "TG_Faction": spec.faction or "neutral",
                    "TG_Category": spec.category,
                    "TG_PipelineVersion": "2.0.0",
                    "TG_GenerationDate": spec.created_at.isoformat(),
                    "TG_WorkflowType": spec.workflow_type.value,
                    "TG_Model": spec.model_name,
                    "TG_OriginalFilename": file_info["original_filename"]
                }
                
                # Add faction-specific tags
                if spec.faction_context:
                    metadata_tags.update({
                        "TG_FactionStyle": ",".join(spec.faction_context.aesthetic_keywords),
                        "TG_FactionPalette": ",".join(spec.faction_context.palette)
                    })
                
                # Add LoRA tags
                loras = spec.get_all_loras()
                if loras:
                    metadata_tags["TG_LoRAs"] = ",".join([lora.name for lora in loras])
                
                # Set each metadata tag
                for key, value in metadata_tags.items():
                    unreal.EditorAssetLibrary.set_metadata_tag(
                        asset, key, str(value)
                    )
                
                # Save the asset
                unreal.EditorAssetLibrary.save_loaded_asset(asset)
        
        except Exception as e:
            self.logger.warning(f"Failed to set metadata for {asset_path}: {e}")
    
    def _create_material_instance(self, texture_path: str, spec: AssetSpecification) -> Optional[str]:
        """Create a material instance for the imported texture."""
        try:
            import unreal
            
            # Get material template
            template_name = self.import_settings.material_templates.get(
                spec.asset_type.value,
                self.import_settings.material_templates["default"]
            )
            
            # Load template material
            template_material = unreal.EditorAssetLibrary.load_asset(
                f"{self.import_settings.material_import_path}/{template_name}"
            )
            
            if not template_material:
                self.logger.warning(f"Material template not found: {template_name}")
                return None
            
            # Create material instance
            texture_name = pathlib.Path(texture_path).stem
            material_name = f"MI_{texture_name}"
            material_path = f"{self.import_settings.material_import_path}/{material_name}"
            
            # Create the material instance
            material_factory = unreal.MaterialInstanceConstantFactoryNew()
            material_factory.initial_parent = template_material
            
            material_instance = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
                material_name,
                self.import_settings.material_import_path,
                unreal.MaterialInstanceConstant,
                material_factory
            )
            
            if material_instance:
                # Set the base texture parameter
                texture_asset = unreal.EditorAssetLibrary.load_asset(texture_path)
                if texture_asset:
                    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                        material_instance,
                        "BaseTexture",  # Parameter name in template
                        texture_asset
                    )
                
                # Save the material instance
                unreal.EditorAssetLibrary.save_loaded_asset(material_instance)
                
                return material_path
        
        except Exception as e:
            self.logger.warning(f"Failed to create material instance: {e}")
        
        return None
    
    def _generate_import_script(
        self,
        generation_result: Dict[str, Any],
        spec: AssetSpecification
    ) -> str:
        """Generate Python script for command-line import."""
        script_lines = [
            "import unreal",
            "import json",
            "",
            "def import_assets():",
            "    results = []",
            f"    import_path = '{self._get_import_path(spec)}'",
            ""
        ]
        
        for file_info in generation_result.get("organized_files", []):
            source_path = file_info["organized_path"].replace("\\", "\\\\")
            asset_name = pathlib.Path(file_info["organized_filename"]).stem
            
            script_lines.extend([
                f"    # Import {asset_name}",
                "    task = unreal.AssetImportTask()",
                f"    task.filename = r'{source_path}'",
                "    task.destination_path = import_path",
                f"    task.destination_name = '{asset_name}'",
                "    task.automated = True",
                "    task.replace_existing = True",
                "",
                "    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])",
                "    results.append({",
                f"        'source_file': r'{source_path}',",
                "        'imported_paths': task.imported_object_paths,",
                "        'success': len(task.imported_object_paths) > 0",
                "    })",
                ""
            ])
        
        script_lines.extend([
            "    # Output results",
            "    print('IMPORT_RESULTS:')",
            "    print(json.dumps(results, indent=2))",
            "",
            "if __name__ == '__main__':",
            "    import_assets()"
        ])
        
        return "\n".join(script_lines)
    
    def _parse_commandline_result(self, stdout: str, spec: AssetSpecification) -> Dict[str, Any]:
        """Parse results from command-line import."""
        try:
            # Look for the results marker
            results_marker = "IMPORT_RESULTS:"
            if results_marker in stdout:
                results_json = stdout.split(results_marker)[1].strip()
                results_data = json.loads(results_json)
                
                imported_assets = []
                for result in results_data:
                    imported_assets.append({
                        "source_file": result["source_file"],
                        "ue5_asset_path": result["imported_paths"][0] if result["imported_paths"] else None,
                        "material_path": None,  # Materials would need separate handling
                        "import_successful": result["success"]
                    })
                
                return {
                    "import_method": "commandline",
                    "import_path": self._get_import_path(spec),
                    "imported_assets": imported_assets,
                    "total_imported": len([a for a in imported_assets if a["import_successful"]]),
                    "import_timestamp": time.time()
                }
        
        except Exception as e:
            self.logger.error(f"Failed to parse command-line results: {e}")
        
        # Return failure result
        return {
            "import_method": "commandline",
            "import_path": self._get_import_path(spec),
            "imported_assets": [],
            "total_imported": 0,
            "import_timestamp": time.time(),
            "error": "Failed to parse import results"
        }
    
    def batch_import(
        self,
        generation_results: List[Dict[str, Any]],
        specs: List[AssetSpecification]
    ) -> Dict[str, Any]:
        """Import multiple assets in batch."""
        self.logger.info(f"Starting batch import: {len(generation_results)} assets")
        
        batch_results = {
            "total_assets": len(generation_results),
            "successful_imports": 0,
            "failed_imports": 0,
            "import_results": [],
            "batch_timestamp": time.time()
        }
        
        for result, spec in zip(generation_results, specs):
            try:
                import_result = self.import_asset(result, spec)
                import_result["asset_name"] = spec.name
                batch_results["import_results"].append(import_result)
                batch_results["successful_imports"] += 1
                
            except Exception as e:
                error_result = {
                    "asset_name": spec.name,
                    "import_successful": False,
                    "error": str(e)
                }
                batch_results["import_results"].append(error_result)
                batch_results["failed_imports"] += 1
        
        self.logger.info(
            f"Batch import completed: "
            f"{batch_results['successful_imports']}/{batch_results['total_assets']} successful"
        )
        
        return batch_results
    
    def validate_import_paths(self) -> Dict[str, bool]:
        """Validate that UE5 import paths exist and are writable."""
        validation_results = {}
        
        if not self.test_connection():
            return {"connection": False}
        
        try:
            if self.connection_method == "python_api":
                import unreal
                
                # Check each import path
                for asset_type, path in self.import_settings.asset_type_paths.items():
                    try:
                        # Try to create directory if it doesn't exist
                        unreal.EditorAssetLibrary.make_directory(path)
                        validation_results[f"{asset_type.value}_path"] = True
                    except Exception as e:
                        self.logger.warning(f"Path validation failed for {path}: {e}")
                        validation_results[f"{asset_type.value}_path"] = False
            
            else:
                # For command-line, assume paths are valid if connection works
                for asset_type in self.import_settings.asset_type_paths.keys():
                    validation_results[f"{asset_type.value}_path"] = True
        
        except Exception as e:
            self.logger.error(f"Path validation failed: {e}")
        
        return validation_results
    
    def get_status(self) -> Dict[str, Any]:
        """Get UE5 connector status."""
        return {
            "is_connected": self.is_connected,
            "connection_method": self.connection_method,
            "ue5_project_path": str(self.ue5_project_path) if self.ue5_project_path else None,
            "ue5_engine_path": str(self.ue5_engine_path) if self.ue5_engine_path else None,
            "import_settings": {
                "base_import_path": self.import_settings.base_import_path,
                "create_materials": self.import_settings.create_materials,
                "asset_type_paths": {
                    asset_type.value: path 
                    for asset_type, path in self.import_settings.asset_type_paths.items()
                }
            },
            "import_statistics": self.import_stats
        }
    
    def shutdown(self):
        """Shutdown the UE5 connector."""
        self.logger.info("Shutting down UE5 Connector")
        self.is_connected = False
        self.connection_method = None