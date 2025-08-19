"""
Terminal Grounds Asset Pipeline v2.0
====================================

A unified, intelligent asset generation pipeline for Terminal Grounds game development.

This package provides:
- Intelligent workflow selection and management
- Quality-driven asset generation with automated enhancement
- Faction-aware asset specifications with deep game integration
- Batch processing with CSV import capabilities
- Seamless UE5 integration with automatic material creation
- Comprehensive asset lifecycle management

Key Components:
- PipelineController: Central orchestrator for all pipeline operations
- AssetSpecBuilder: Type-safe asset definitions with faction integration
- WorkflowManager: Smart ComfyUI workflow selection and customization
- QualityAssessmentEngine: Automated quality scoring and enhancement
- BatchProcessor: High-performance CSV batch processing
- AssetManager: Complete asset organization and discovery
- UE5Connector: Seamless Unreal Engine 5 integration

Quick Start:
    from terminal_grounds_pipeline import PipelineController
    
    # Initialize pipeline
    controller = PipelineController()
    
    # Generate single asset
    task_id = controller.generate_asset(
        name="Plasma Rifle",
        asset_type="weapon", 
        faction="directorate",
        description="High-energy directed weapon"
    )
    
    # Process batch CSV
    task_id = controller.process_batch_csv(
        csv_file=Path("weapons.csv"),
        config={"auto_enhance": True, "auto_import_ue5": True}
    )

CLI Usage:
    # Generate single asset
    python -m terminal_grounds_pipeline generate weapon "Plasma Rifle" --faction directorate
    
    # Process CSV batch
    python -m terminal_grounds_pipeline batch-csv data/weapons.csv --auto-import
    
    # Interactive mode
    python -m terminal_grounds_pipeline interactive
"""

__version__ = "2.0.0"
__author__ = "Terminal Grounds Development Team"
__email__ = "dev@terminalgrounds.com"
__description__ = "Unified asset generation pipeline for Terminal Grounds"

# Core pipeline components
from .pipeline_controller import PipelineController, TaskPriority, PipelineStatus
from .config_manager import ConfigManager, ConfigurationError
from .asset_spec import (
    AssetSpecification, 
    AssetSpecBuilder,
    AssetType,
    FactionCode,
    QualityLevel,
    GenerationParameters,
    QualityRequirements
)

# Asset generation and management
from .enhanced_client import EnhancedComfyUIClient, GenerationJob, GenerationStatus
from .workflow_manager import WorkflowManager, WorkflowTemplate, WorkflowCategory
from .quality_assurance import (
    QualityAssessmentEngine,
    QualityAssuranceManager, 
    QualityMetrics,
    QualityRating
)
from .batch_processor import BatchProcessor, BatchConfiguration, BatchSession
from .asset_manager import AssetManager, AssetRecord, AssetStatus

# UE5 integration
from .ue5_connector import UE5Connector, UE5ProjectConfig, create_ue5_config

# Make commonly used classes available at package level
__all__ = [
    # Core pipeline
    "PipelineController",
    "ConfigManager",
    
    # Asset specification
    "AssetSpecification",
    "AssetSpecBuilder", 
    "AssetType",
    "FactionCode",
    
    # Generation and quality
    "EnhancedComfyUIClient",
    "WorkflowManager",
    "QualityAssessmentEngine",
    "QualityAssuranceManager",
    
    # Asset management
    "AssetManager",
    "AssetRecord",
    "BatchProcessor",
    
    # UE5 integration
    "UE5Connector",
    "create_ue5_config",
    
    # Enums and constants
    "TaskPriority",
    "PipelineStatus", 
    "GenerationStatus",
    "QualityRating",
    "AssetStatus"
]

def get_version() -> str:
    """Get the current version of the pipeline"""
    return __version__

def create_pipeline(config_path=None) -> PipelineController:
    """
    Create and initialize a pipeline controller with default settings.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Initialized PipelineController instance
    """
    return PipelineController(config_path)

def validate_installation() -> bool:
    """
    Validate that the pipeline is properly installed and configured.
    
    Returns:
        True if installation is valid, False otherwise
    """
    try:
        controller = PipelineController()
        validation = controller.validate_pipeline()
        controller.shutdown()
        return validation["is_healthy"]
    except Exception:
        return False

# Package metadata
__package_info__ = {
    "name": "terminal_grounds_pipeline",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "author_email": __email__,
    "url": "https://github.com/terminal-grounds/asset-pipeline",
    "license": "MIT",
    "python_requires": ">=3.8",
    "keywords": [
        "game-development",
        "asset-generation", 
        "ai-art",
        "comfyui",
        "unreal-engine",
        "pipeline",
        "automation"
    ],
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
}

# Import validation - ensure all components are available
try:
    # Test critical imports
    from .pipeline_controller import PipelineController
    from .config_manager import ConfigManager
    from .asset_spec import AssetSpecBuilder
    
    _IMPORT_SUCCESS = True
except ImportError as e:
    _IMPORT_SUCCESS = False
    _IMPORT_ERROR = str(e)

if not _IMPORT_SUCCESS:
    import warnings
    warnings.warn(
        f"Terminal Grounds Pipeline import failed: {_IMPORT_ERROR}. "
        "Some functionality may not be available.",
        ImportWarning
    )