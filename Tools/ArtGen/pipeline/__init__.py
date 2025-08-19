"""
Terminal Grounds Asset Generation Pipeline v2.0
==============================================

A complete overhaul of the asset generation system providing:
- Unified control and coordination
- Smart workflow selection
- Faction-aware generation
- Automated quality assurance
- Intelligent asset management
- Seamless UE5 integration
"""

__version__ = "2.0.0"
__author__ = "Terminal Grounds Development Team"

from .core.pipeline_controller import PipelineController
from .core.asset_spec import AssetSpecification
from .core.workflow_manager import WorkflowManager
from .core.quality_assurance import QualityAssurance
from .core.batch_processor import BatchProcessor
from .core.asset_manager import AssetManager
from .integrations.ue5_connector import UE5Connector

__all__ = [
    "PipelineController",
    "AssetSpecification", 
    "WorkflowManager",
    "QualityAssurance",
    "BatchProcessor",
    "AssetManager",
    "UE5Connector"
]