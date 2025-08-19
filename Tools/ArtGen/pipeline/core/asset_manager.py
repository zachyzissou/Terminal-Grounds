"""
Asset Manager - Intelligent asset organization and file management
================================================================

Handles asset organization, naming conventions, metadata management,
version control, and file system operations. Provides a structured
approach to asset storage that scales with the project.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import logging
import hashlib

from .asset_spec import AssetSpecification, AssetType
from ..utils.logger import setup_logger
from ..utils.file_utils import safe_filename, ensure_directory


class AssetMetadata:
    """Comprehensive metadata for generated assets."""
    
    def __init__(self, spec: AssetSpecification, generation_result: Dict[str, Any]):
        self.asset_name = spec.name
        self.asset_type = spec.asset_type.value
        self.faction = spec.faction
        self.biome = spec.biome
        self.category = spec.category
        
        # Generation metadata
        self.created_at = datetime.utcnow()
        self.pipeline_version = "2.0.0"
        self.workflow_used = generation_result.get("template_name", "unknown")
        self.job_id = generation_result.get("job_id", "")
        
        # Technical details
        self.specification = spec.to_dict()
        self.generation_settings = {
            "model": spec.model_name,
            "render_settings": spec.render_settings.__dict__,
            "loras": [lora.__dict__ for lora in spec.get_all_loras()]
        }
        
        # File information
        self.files = []
        for img_info in generation_result.get("images", []):
            self.files.append({
                "filename": img_info["filename"],
                "path": img_info.get("local_path", ""),
                "type": "image",
                "format": pathlib.Path(img_info["filename"]).suffix[1:].upper(),
                "size_bytes": 0,  # Will be filled when organizing
                "checksum": ""    # Will be calculated when organizing
            })
        
        # Quality information
        self.quality_data = {}
        
        # Tags and searchable metadata
        self.tags = self._generate_tags(spec)
        
        # Version information
        self.version = 1
        self.is_latest = True
        self.parent_version = None
    
    def _generate_tags(self, spec: AssetSpecification) -> List[str]:
        """Generate searchable tags for the asset."""
        tags = []
        
        # Basic tags
        tags.append(spec.asset_type.value)
        if spec.faction:
            tags.append(f"faction:{spec.faction}")
        if spec.biome:
            tags.append(f"biome:{spec.biome}")
        if spec.category:
            tags.append(f"category:{spec.category}")
        
        # Technical tags
        tags.append(f"model:{spec.model_name}")
        tags.append(f"resolution:{spec.render_settings.width}x{spec.render_settings.height}")
        
        # Faction-specific tags
        if spec.faction_context:
            for keyword in spec.faction_context.aesthetic_keywords:
                tags.append(f"style:{keyword}")
        
        # LoRA tags
        for lora in spec.get_all_loras():
            tags.append(f"lora:{lora.name}")
        
        return tags
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "asset_name": self.asset_name,
            "asset_type": self.asset_type,
            "faction": self.faction,
            "biome": self.biome,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "pipeline_version": self.pipeline_version,
            "workflow_used": self.workflow_used,
            "job_id": self.job_id,
            "specification": self.specification,
            "generation_settings": self.generation_settings,
            "files": self.files,
            "quality_data": self.quality_data,
            "tags": self.tags,
            "version": self.version,
            "is_latest": self.is_latest,
            "parent_version": self.parent_version
        }
    
    def update_quality_data(self, quality_report):
        """Update metadata with quality assessment results."""
        if quality_report:
            self.quality_data = {
                "overall_score": quality_report.overall_score,
                "resolution_score": quality_report.resolution_score,
                "detail_score": quality_report.detail_score,
                "composition_score": quality_report.composition_score,
                "color_score": quality_report.color_score,
                "faction_alignment_score": quality_report.faction_alignment_score,
                "passes_quality_gate": quality_report.passes_quality_gate,
                "detected_issues": quality_report.detected_issues,
                "recommendations": quality_report.recommendations
            }


class AssetRegistry:
    """Central registry for tracking all generated assets."""
    
    def __init__(self, registry_path: pathlib.Path):
        self.registry_path = registry_path
        self.assets: Dict[str, AssetMetadata] = {}
        self.load_registry()
    
    def load_registry(self):
        """Load asset registry from disk."""
        if self.registry_path.exists():
            try:
                data = json.loads(self.registry_path.read_text())
                # Would need to reconstruct AssetMetadata objects from data
                # Simplified for now
                pass
            except Exception:
                pass
    
    def save_registry(self):
        """Save asset registry to disk."""
        try:
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            
            registry_data = {
                "version": "2.0.0",
                "last_updated": datetime.utcnow().isoformat(),
                "total_assets": len(self.assets),
                "assets": {
                    asset_id: metadata.to_dict() 
                    for asset_id, metadata in self.assets.items()
                }
            }
            
            self.registry_path.write_text(json.dumps(registry_data, indent=2))
            
        except Exception as e:
            logging.error(f"Failed to save asset registry: {e}")
    
    def register_asset(self, asset_id: str, metadata: AssetMetadata):
        """Register a new asset in the registry."""
        self.assets[asset_id] = metadata
        self.save_registry()
    
    def search_assets(
        self,
        asset_type: Optional[str] = None,
        faction: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[AssetMetadata]:
        """Search assets by criteria."""
        results = []
        
        for metadata in self.assets.values():
            # Filter by asset type
            if asset_type and metadata.asset_type != asset_type:
                continue
            
            # Filter by faction
            if faction and metadata.faction != faction:
                continue
            
            # Filter by tags
            if tags:
                if not any(tag in metadata.tags for tag in tags):
                    continue
            
            results.append(metadata)
        
        return results


class AssetManager:
    """
    Comprehensive asset management system.
    
    Features:
    - Structured directory organization
    - Intelligent file naming
    - Metadata tracking and indexing
    - Version control
    - Asset discovery and search
    - Cleanup and maintenance
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger("AssetManager", config.log_level)
        
        # Base directories
        self.base_output_dir = pathlib.Path(config.base_output_dir)
        self.registry_path = self.base_output_dir / "asset_registry.json"
        
        # Asset registry
        self.registry = AssetRegistry(self.registry_path)
        
        # Directory structure configuration
        self.directory_structure = self._define_directory_structure()
        
        # Naming conventions
        self.naming_conventions = self._define_naming_conventions()
        
        self.logger.info(f"Asset Manager initialized: {self.base_output_dir}")
    
    def _define_directory_structure(self) -> Dict[str, Dict[str, str]]:
        """Define the organized directory structure."""
        return {
            "by_type": {
                AssetType.WEAPON.value: "Weapons",
                AssetType.VEHICLE.value: "Vehicles",
                AssetType.GEAR.value: "Gear", 
                AssetType.BUILDING.value: "Buildings",
                AssetType.CHARACTER.value: "Characters",
                AssetType.ENVIRONMENT.value: "Environments",
                AssetType.UI_ICON.value: "UI/Icons",
                AssetType.POSTER.value: "Posters",
                AssetType.TEXTURE.value: "Textures",
                AssetType.CONCEPT.value: "Concepts"
            },
            "by_faction": {
                "directorate": "Factions/Directorate",
                "free77": "Factions/Free77",
                "vultures": "Factions/Vultures",
                "corporate": "Factions/Corporate",
                "wardens": "Factions/Wardens",
                "archivists": "Factions/Archivists",
                "nomads": "Factions/Nomads",
                "neutral": "Neutral"
            },
            "by_quality": {
                "raw": "Raw",
                "processed": "Processed",
                "final": "Final",
                "archive": "Archive"
            },
            "special": {
                "iterations": "Iterations",
                "references": "References",
                "work_in_progress": "WIP"
            }
        }
    
    def _define_naming_conventions(self) -> Dict[str, str]:
        """Define asset naming conventions."""
        return {
            "standard": "{faction}_{type}_{name}_{version}_{timestamp}",
            "simple": "{faction}_{name}_{version}",
            "detailed": "{faction}_{type}_{category}_{name}_{quality}_{version}_{timestamp}",
            "ue5_compatible": "T_{Type}_{Faction}_{Name}_{Version}"
        }
    
    def organize_asset(
        self,
        generation_result: Dict[str, Any],
        spec: AssetSpecification,
        organization_mode: str = "by_type"
    ) -> Dict[str, Any]:
        """
        Organize a generated asset into the proper directory structure.
        
        Args:
            generation_result: Result from workflow execution
            spec: Asset specification
            organization_mode: Organization strategy ("by_type", "by_faction", etc.)
            
        Returns:
            Updated result with organized file paths
        """
        self.logger.info(f"Organizing asset: {spec.name}")
        
        try:
            # Create asset metadata
            metadata = AssetMetadata(spec, generation_result)
            
            # Determine target directory
            target_dir = self._get_target_directory(spec, organization_mode)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate asset ID
            asset_id = self._generate_asset_id(spec)
            
            # Organize files
            organized_files = self._organize_files(
                generation_result["images"],
                target_dir,
                spec,
                metadata
            )
            
            # Update metadata with file information
            self._update_file_metadata(organized_files, metadata)
            
            # Create master metadata file
            metadata_file = target_dir / f"{asset_id}_metadata.json"
            metadata_file.write_text(json.dumps(metadata.to_dict(), indent=2))
            
            # Register asset
            self.registry.register_asset(asset_id, metadata)
            
            # Create convenience links if needed
            self._create_convenience_links(organized_files, spec)
            
            # Update generation result
            organized_result = generation_result.copy()
            organized_result.update({
                "asset_id": asset_id,
                "organized_directory": str(target_dir),
                "organized_files": organized_files,
                "metadata_file": str(metadata_file),
                "organization_timestamp": time.time()
            })
            
            self.logger.info(f"Asset organized successfully: {asset_id}")
            return organized_result
            
        except Exception as e:
            self.logger.error(f"Failed to organize asset {spec.name}: {e}")
            raise
    
    def _get_target_directory(
        self,
        spec: AssetSpecification,
        organization_mode: str
    ) -> pathlib.Path:
        """Determine the target directory for an asset."""
        base_dir = self.base_output_dir
        
        if organization_mode == "by_type":
            type_dir = self.directory_structure["by_type"].get(
                spec.asset_type.value, "Other"
            )
            return base_dir / type_dir
        
        elif organization_mode == "by_faction" and spec.faction:
            faction_dir = self.directory_structure["by_faction"].get(
                spec.faction.lower(), "Neutral"
            )
            return base_dir / faction_dir / self.directory_structure["by_type"].get(
                spec.asset_type.value, "Other"
            )
        
        elif organization_mode == "hybrid":
            # Organize by type, then by faction
            type_dir = self.directory_structure["by_type"].get(
                spec.asset_type.value, "Other"
            )
            if spec.faction:
                faction_subdir = spec.faction.title()
                return base_dir / type_dir / faction_subdir
            else:
                return base_dir / type_dir
        
        else:
            # Default to type-based organization
            type_dir = self.directory_structure["by_type"].get(
                spec.asset_type.value, "Other"
            )
            return base_dir / type_dir
    
    def _generate_asset_id(self, spec: AssetSpecification) -> str:
        """Generate a unique asset identifier."""
        # Create a deterministic but unique ID based on spec content
        id_components = [
            spec.name,
            spec.asset_type.value,
            spec.faction or "neutral",
            str(spec.render_settings.seed),
            str(spec.created_at.timestamp())
        ]
        
        id_string = "_".join(id_components)
        id_hash = hashlib.md5(id_string.encode()).hexdigest()[:8]
        
        # Create human-readable ID
        safe_name = safe_filename(spec.name)
        asset_id = f"{spec.asset_type.value}_{safe_name}_{id_hash}"
        
        return asset_id
    
    def _organize_files(
        self,
        image_files: List[Dict[str, Any]],
        target_dir: pathlib.Path,
        spec: AssetSpecification,
        metadata: AssetMetadata
    ) -> List[Dict[str, Any]]:
        """Organize and rename files according to conventions."""
        organized_files = []
        
        for i, img_info in enumerate(image_files):
            try:
                source_path = pathlib.Path(img_info["local_path"])
                
                # Generate organized filename
                organized_filename = self._generate_organized_filename(
                    spec, i, source_path.suffix
                )
                
                target_path = target_dir / organized_filename
                
                # Copy/move file to organized location
                if source_path != target_path:
                    shutil.copy2(source_path, target_path)
                
                # Calculate file checksum
                checksum = self._calculate_file_checksum(target_path)
                
                # Create organized file info
                organized_info = {
                    "original_filename": img_info["filename"],
                    "organized_filename": organized_filename,
                    "organized_path": str(target_path),
                    "size_bytes": target_path.stat().st_size,
                    "checksum": checksum,
                    "format": source_path.suffix[1:].upper(),
                    "index": i
                }
                
                organized_files.append(organized_info)
                
                # Create sidecar metadata file
                sidecar_path = target_path.with_suffix(target_path.suffix + ".json")
                sidecar_data = {
                    "asset_metadata": metadata.to_dict(),
                    "file_info": organized_info,
                    "generation_info": img_info
                }
                sidecar_path.write_text(json.dumps(sidecar_data, indent=2))
                
            except Exception as e:
                self.logger.error(f"Failed to organize file {img_info}: {e}")
        
        return organized_files
    
    def _generate_organized_filename(
        self,
        spec: AssetSpecification,
        index: int,
        extension: str
    ) -> str:
        """Generate an organized filename based on conventions."""
        # Use standard naming convention by default
        template = self.naming_conventions["standard"]
        
        # Prepare template variables
        variables = {
            "faction": (spec.faction or "neutral").title(),
            "type": spec.asset_type.value.title(),
            "category": safe_filename(spec.category),
            "name": safe_filename(spec.name),
            "version": "v01",  # Start with version 1
            "timestamp": datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
            "quality": "raw",  # Will be updated after processing
            "index": f"{index:02d}" if index > 0 else ""
        }
        
        # Generate filename
        filename = template.format(**variables)
        
        # Add index suffix if multiple files
        if index > 0:
            filename += f"_{index:02d}"
        
        # Clean up the filename
        filename = safe_filename(filename)
        
        return filename + extension
    
    def _calculate_file_checksum(self, file_path: pathlib.Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _update_file_metadata(
        self,
        organized_files: List[Dict[str, Any]],
        metadata: AssetMetadata
    ):
        """Update metadata with organized file information."""
        metadata.files = []
        
        for file_info in organized_files:
            metadata.files.append({
                "filename": file_info["organized_filename"],
                "path": file_info["organized_path"],
                "type": "image",
                "format": file_info["format"],
                "size_bytes": file_info["size_bytes"],
                "checksum": file_info["checksum"],
                "index": file_info["index"]
            })
    
    def _create_convenience_links(
        self,
        organized_files: List[Dict[str, Any]],
        spec: AssetSpecification
    ):
        """Create convenience links for easy access."""
        try:
            # Create faction-specific links if organizing by type
            if spec.faction:
                faction_dir = self.base_output_dir / "By_Faction" / spec.faction.title()
                faction_dir.mkdir(parents=True, exist_ok=True)
                
                for file_info in organized_files:
                    source_path = pathlib.Path(file_info["organized_path"])
                    link_path = faction_dir / source_path.name
                    
                    # Create symbolic link (if supported)
                    try:
                        if not link_path.exists():
                            link_path.symlink_to(source_path)
                    except OSError:
                        # Fallback to copying if symlinks not supported
                        shutil.copy2(source_path, link_path)
        
        except Exception as e:
            self.logger.warning(f"Failed to create convenience links: {e}")
    
    def search_assets(
        self,
        query: str = "",
        asset_type: Optional[str] = None,
        faction: Optional[str] = None,
        tags: Optional[List[str]] = None,
        quality_threshold: Optional[float] = None
    ) -> List[AssetMetadata]:
        """Search for assets using various criteria."""
        results = self.registry.search_assets(asset_type, faction, tags)
        
        # Filter by quality threshold
        if quality_threshold is not None:
            results = [
                asset for asset in results
                if asset.quality_data.get("overall_score", 0) >= quality_threshold
            ]
        
        # Text search in names and tags
        if query:
            query_lower = query.lower()
            results = [
                asset for asset in results
                if (query_lower in asset.asset_name.lower() or
                    any(query_lower in tag.lower() for tag in asset.tags))
            ]
        
        return results
    
    def get_asset_versions(self, asset_name: str) -> List[AssetMetadata]:
        """Get all versions of a specific asset."""
        return [
            asset for asset in self.registry.assets.values()
            if asset.asset_name == asset_name
        ]
    
    def cleanup_old_versions(self, keep_versions: int = 3):
        """Clean up old asset versions, keeping only the specified number."""
        self.logger.info(f"Cleaning up old versions, keeping {keep_versions} versions")
        
        # Group assets by name
        asset_groups = {}
        for asset in self.registry.assets.values():
            if asset.asset_name not in asset_groups:
                asset_groups[asset.asset_name] = []
            asset_groups[asset.asset_name].append(asset)
        
        # Clean up each group
        for asset_name, versions in asset_groups.items():
            if len(versions) > keep_versions:
                # Sort by version number (descending)
                versions.sort(key=lambda x: x.version, reverse=True)
                
                # Keep the latest versions, remove the rest
                to_remove = versions[keep_versions:]
                
                for old_version in to_remove:
                    self._remove_asset_files(old_version)
                    # Remove from registry
                    asset_id = next(
                        (aid for aid, meta in self.registry.assets.items() 
                         if meta == old_version), None
                    )
                    if asset_id:
                        del self.registry.assets[asset_id]
                
                self.logger.info(
                    f"Cleaned up {len(to_remove)} old versions of {asset_name}"
                )
        
        # Save updated registry
        self.registry.save_registry()
    
    def _remove_asset_files(self, metadata: AssetMetadata):
        """Remove asset files from disk."""
        for file_info in metadata.files:
            try:
                file_path = pathlib.Path(file_info["path"])
                if file_path.exists():
                    file_path.unlink()
                
                # Remove sidecar files
                sidecar_path = file_path.with_suffix(file_path.suffix + ".json")
                if sidecar_path.exists():
                    sidecar_path.unlink()
                    
            except Exception as e:
                self.logger.warning(f"Failed to remove file {file_info['path']}: {e}")
    
    def validate_directories(self) -> bool:
        """Validate that all required directories exist and are writable."""
        try:
            # Check base output directory
            self.base_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Test write access
            test_file = self.base_output_dir / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Directory validation failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get asset manager status."""
        return {
            "base_output_directory": str(self.base_output_dir),
            "total_assets": len(self.registry.assets),
            "directory_structure": self.directory_structure,
            "registry_path": str(self.registry_path),
            "directories_valid": self.validate_directories()
        }