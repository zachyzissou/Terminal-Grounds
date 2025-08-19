"""
Pipeline Controller - Master orchestrator for all asset generation
================================================================

This is the single entry point for all asset generation tasks.
Coordinates all subsystems and provides a unified interface.
"""

from __future__ import annotations

import json
import logging
import pathlib
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .asset_spec import AssetSpecification
from .workflow_manager import WorkflowManager
from .quality_assurance import QualityAssurance
from .batch_processor import BatchProcessor
from .asset_manager import AssetManager
from ..integrations.ue5_connector import UE5Connector
from ..utils.logger import setup_logger
from ..utils.config import PipelineConfig


class PipelineController:
    """
    Master controller for the Terminal Grounds asset generation pipeline.
    
    This class provides the primary interface for all asset generation operations,
    coordinating between ComfyUI workflows, quality assurance, asset management,
    and UE5 integration.
    """
    
    def __init__(self, config_path: Optional[pathlib.Path] = None):
        """Initialize the pipeline controller with configuration."""
        self.config = PipelineConfig(config_path)
        self.logger = setup_logger("PipelineController", self.config.log_level)
        
        # Initialize core subsystems
        self.workflow_manager = WorkflowManager(self.config)
        self.quality_assurance = QualityAssurance(self.config)
        self.batch_processor = BatchProcessor(self.config)
        self.asset_manager = AssetManager(self.config)
        self.ue5_connector = UE5Connector(self.config)
        
        self.logger.info("Pipeline Controller initialized successfully")
    
    def generate_single_asset(
        self,
        asset_spec: Union[AssetSpecification, Dict[str, Any], str],
        output_dir: Optional[pathlib.Path] = None
    ) -> Dict[str, Any]:
        """
        Generate a single asset from specification.
        
        Args:
            asset_spec: Asset specification (object, dict, or JSON path)
            output_dir: Override output directory
            
        Returns:
            Generation result with metadata and file paths
        """
        # Parse asset specification
        if isinstance(asset_spec, str):
            spec = AssetSpecification.from_file(pathlib.Path(asset_spec))
        elif isinstance(asset_spec, dict):
            spec = AssetSpecification.from_dict(asset_spec)
        else:
            spec = asset_spec
            
        self.logger.info(f"Generating asset: {spec.name}")
        
        try:
            # Select optimal workflow
            workflow = self.workflow_manager.select_workflow(spec)
            self.logger.debug(f"Selected workflow: {workflow.name}")
            
            # Generate asset using ComfyUI
            generation_result = self.workflow_manager.execute_workflow(
                workflow, spec, output_dir
            )
            
            # Run quality assurance
            qa_result = self.quality_assurance.validate_output(
                generation_result, spec
            )
            
            # Post-process if needed
            if qa_result.needs_upscaling:
                generation_result = self.quality_assurance.upscale_asset(
                    generation_result, spec
                )
            
            if qa_result.needs_enhancement:
                generation_result = self.quality_assurance.enhance_asset(
                    generation_result, spec
                )
            
            # Organize and manage asset
            final_result = self.asset_manager.organize_asset(
                generation_result, spec
            )
            
            # Optional UE5 integration
            if spec.auto_import_ue5:
                ue5_result = self.ue5_connector.import_asset(final_result, spec)
                final_result.update({"ue5_import": ue5_result})
            
            self.logger.info(f"Asset generation completed: {spec.name}")
            return final_result
            
        except Exception as e:
            self.logger.error(f"Asset generation failed for {spec.name}: {e}")
            raise
    
    def generate_batch(
        self,
        batch_spec: Union[str, pathlib.Path, List[AssetSpecification]],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Generate multiple assets in batch mode.
        
        Args:
            batch_spec: Batch specification file or list of asset specs
            progress_callback: Optional callback for progress updates
            
        Returns:
            Batch generation results with statistics
        """
        self.logger.info("Starting batch generation")
        
        # Load batch specifications
        if isinstance(batch_spec, (str, pathlib.Path)):
            batch_data = self.batch_processor.load_batch_spec(pathlib.Path(batch_spec))
        else:
            batch_data = batch_spec
            
        return self.batch_processor.process_batch(
            batch_data, progress_callback
        )
    
    def generate_from_csv(
        self,
        csv_path: pathlib.Path,
        template_spec: AssetSpecification,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Generate assets from CSV data (like the Weapons.csv).
        
        Args:
            csv_path: Path to CSV file
            template_spec: Template specification to use
            progress_callback: Optional progress callback
            
        Returns:
            Generation results
        """
        self.logger.info(f"Generating from CSV: {csv_path}")
        
        return self.batch_processor.process_csv_batch(
            csv_path, template_spec, progress_callback
        )
    
    def create_faction_assets(
        self,
        faction_name: str,
        asset_types: List[str],
        count_per_type: int = 5
    ) -> Dict[str, Any]:
        """
        Generate a complete set of assets for a specific faction.
        
        Args:
            faction_name: Name of the faction
            asset_types: List of asset types to generate
            count_per_type: Number of assets per type
            
        Returns:
            Generation results
        """
        self.logger.info(f"Creating faction assets for: {faction_name}")
        
        # Load faction configuration
        faction_config = self.config.get_faction_config(faction_name)
        
        # Create asset specifications for each type
        batch_specs = []
        for asset_type in asset_types:
            for i in range(count_per_type):
                spec = AssetSpecification.create_faction_asset(
                    faction_name, asset_type, faction_config, index=i
                )
                batch_specs.append(spec)
        
        return self.generate_batch(batch_specs)
    
    def validate_pipeline(self) -> Dict[str, Any]:
        """
        Run comprehensive pipeline validation.
        
        Returns:
            Validation results
        """
        self.logger.info("Running pipeline validation")
        
        validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "comfyui_connection": False,
            "workflows_valid": False,
            "faction_configs": False,
            "output_directories": False,
            "ue5_connection": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Test ComfyUI connection
            if self.workflow_manager.test_connection():
                validation_results["comfyui_connection"] = True
            else:
                validation_results["errors"].append("ComfyUI connection failed")
            
            # Validate workflows
            workflow_validation = self.workflow_manager.validate_all_workflows()
            validation_results["workflows_valid"] = workflow_validation["all_valid"]
            if not workflow_validation["all_valid"]:
                validation_results["errors"].extend(workflow_validation["errors"])
            
            # Check faction configurations
            faction_validation = self.config.validate_faction_configs()
            validation_results["faction_configs"] = faction_validation["all_valid"]
            if not faction_validation["all_valid"]:
                validation_results["errors"].extend(faction_validation["errors"])
            
            # Check output directories
            if self.asset_manager.validate_directories():
                validation_results["output_directories"] = True
            else:
                validation_results["errors"].append("Output directory validation failed")
            
            # Test UE5 connection (optional)
            try:
                if self.ue5_connector.test_connection():
                    validation_results["ue5_connection"] = True
            except Exception as e:
                validation_results["warnings"].append(f"UE5 connection test failed: {e}")
            
        except Exception as e:
            validation_results["errors"].append(f"Validation error: {e}")
            self.logger.error(f"Pipeline validation failed: {e}")
        
        # Overall status
        validation_results["overall_status"] = (
            "PASS" if not validation_results["errors"] else "FAIL"
        )
        
        return validation_results
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status and metrics.
        
        Returns:
            Status information
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "workflow_manager": self.workflow_manager.get_status(),
            "batch_processor": self.batch_processor.get_status(),
            "asset_manager": self.asset_manager.get_status(),
            "quality_assurance": self.quality_assurance.get_status(),
            "ue5_connector": self.ue5_connector.get_status()
        }
    
    def shutdown(self):
        """Gracefully shutdown the pipeline controller."""
        self.logger.info("Shutting down Pipeline Controller")
        
        # Shutdown all subsystems
        self.workflow_manager.shutdown()
        self.batch_processor.shutdown()
        self.ue5_connector.shutdown()
        
        self.logger.info("Pipeline Controller shutdown complete")


# Convenience function for quick asset generation
def generate_asset(
    asset_type: str,
    name: str,
    faction: str = "neutral",
    **kwargs
) -> Dict[str, Any]:
    """
    Quick asset generation function.
    
    Args:
        asset_type: Type of asset (weapon, vehicle, etc.)
        name: Asset name
        faction: Faction affiliation
        **kwargs: Additional parameters
        
    Returns:
        Generation result
    """
    controller = PipelineController()
    
    spec = AssetSpecification.create_quick(
        asset_type=asset_type,
        name=name,
        faction=faction,
        **kwargs
    )
    
    return controller.generate_single_asset(spec)