#!/usr/bin/env python3
"""
Workflow Manager for Terminal Grounds v2.0
==========================================
Intelligent workflow selection and management for ComfyUI asset generation.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    from .asset_spec import AssetSpecification, AssetType, FactionCode, GenerationParameters
except ImportError:
    from asset_spec import AssetSpecification, AssetType, FactionCode, GenerationParameters

logger = logging.getLogger(__name__)

class WorkflowCategory(Enum):
    BASIC = "basic"
    ENHANCED = "enhanced"
    CINEMATIC = "cinematic"
    PRODUCTION = "production"

@dataclass
class WorkflowTemplate:
    """Represents a ComfyUI workflow template"""
    name: str
    category: WorkflowCategory
    asset_types: List[AssetType]
    description: str
    template_path: Path
    requirements: Dict[str, Any] = field(default_factory=dict)
    performance_score: float = 5.0  # 1-10, higher = better quality/slower
    memory_usage: str = "medium"  # low, medium, high
    estimated_time: int = 30  # seconds
    supported_resolutions: List[Tuple[int, int]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.supported_resolutions:
            self.supported_resolutions = [(1024, 1024), (2048, 2048)]
    
    def load_template(self) -> Dict[str, Any]:
        """Load the workflow template JSON"""
        try:
            with open(self.template_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load workflow template {self.name}: {e}")
            return {}
    
    def is_compatible(self, asset_spec: AssetSpecification) -> bool:
        """Check if this workflow is compatible with the asset specification"""
        # Check asset type compatibility
        if asset_spec.asset_type not in self.asset_types:
            return False
            
        # Check resolution compatibility
        requested_res = (asset_spec.generation_params.width, asset_spec.generation_params.height)
        if requested_res not in self.supported_resolutions:
            # Check if any supported resolution is close enough
            for width, height in self.supported_resolutions:
                if abs(width - requested_res[0]) <= 256 and abs(height - requested_res[1]) <= 256:
                    return True
            return False
            
        return True

class WorkflowManager:
    """
    Manages ComfyUI workflow selection and customization for Terminal Grounds assets.
    Automatically selects optimal workflows based on asset requirements.
    """
    
    def __init__(self, workflows_dir: Path, templates_dir: Path):
        self.workflows_dir = workflows_dir
        self.templates_dir = templates_dir
        self.workflows: Dict[str, WorkflowTemplate] = {}
        self.workflow_cache: Dict[str, Dict[str, Any]] = {}
        
        # Load available workflows
        self._discover_workflows()
    
    def _discover_workflows(self):
        """Discover and register available workflow templates"""
        logger.info("Discovering workflow templates...")
        
        # Built-in workflow definitions
        builtin_workflows = [
            WorkflowTemplate(
                name="concept_art",
                category=WorkflowCategory.ENHANCED,
                asset_types=["concept", "environment"],
                description="High-quality concept art generation with artistic focus",
                template_path=self.templates_dir / "concept_art.api.json",
                performance_score=7.0,
                memory_usage="medium",
                estimated_time=45,
                supported_resolutions=[(1280, 768), (1920, 1080), (2560, 1440)]
            ),
            WorkflowTemplate(
                name="weapon_detail",
                category=WorkflowCategory.PRODUCTION,
                asset_types=["weapon"],
                description="Ultra-detailed weapon rendering for close-up views",
                template_path=self.templates_dir / "weapon_detail.api.json",
                performance_score=8.5,
                memory_usage="high",
                estimated_time=60,
                supported_resolutions=[(1024, 1024), (2048, 2048), (4096, 4096)]
            ),
            WorkflowTemplate(
                name="vehicle_showcase",
                category=WorkflowCategory.ENHANCED,
                asset_types=["vehicle"],
                description="Vehicle rendering with environmental context",
                template_path=self.templates_dir / "vehicle_showcase.api.json",
                performance_score=7.5,
                memory_usage="medium",
                estimated_time=50,
                supported_resolutions=[(1280, 768), (1920, 1080)]
            ),
            WorkflowTemplate(
                name="logo_design",
                category=WorkflowCategory.BASIC,
                asset_types=["emblem", "icon"],
                description="Clean vector-style logo and emblem generation",
                template_path=self.templates_dir / "logo_design.api.json",
                performance_score=6.0,
                memory_usage="low",
                estimated_time=25,
                supported_resolutions=[(512, 512), (1024, 1024), (2048, 2048)]
            ),
            WorkflowTemplate(
                name="poster_propaganda",
                category=WorkflowCategory.ENHANCED,
                asset_types=["poster"],
                description="Propaganda poster with bold graphics and text integration",
                template_path=self.templates_dir / "poster_propaganda.api.json",
                performance_score=7.0,
                memory_usage="medium",
                estimated_time=40,
                supported_resolutions=[(768, 1024), (1536, 2048)]
            ),
            WorkflowTemplate(
                name="ui_elements",
                category=WorkflowCategory.BASIC,
                asset_types=["ui", "icon"],
                description="Clean UI elements and interface graphics",
                template_path=self.templates_dir / "ui_elements.api.json",
                performance_score=5.5,
                memory_usage="low",
                estimated_time=20,
                supported_resolutions=[(512, 512), (1024, 768), (1024, 1024)]
            ),
            WorkflowTemplate(
                name="texture_seamless",
                category=WorkflowCategory.PRODUCTION,
                asset_types=["texture"],
                description="Seamless texture generation with tileable output",
                template_path=self.templates_dir / "texture_seamless.api.json",
                performance_score=8.0,
                memory_usage="medium",
                estimated_time=35,
                supported_resolutions=[(1024, 1024), (2048, 2048)]
            ),
            WorkflowTemplate(
                name="environment_wide",
                category=WorkflowCategory.CINEMATIC,
                asset_types=["environment", "concept"],
                description="Wide environmental shots with cinematic composition",
                template_path=self.templates_dir / "environment_wide.api.json",
                performance_score=8.5,
                memory_usage="high",
                estimated_time=70,
                supported_resolutions=[(1920, 1080), (2560, 1440), (3840, 2160)]
            )
        ]
        
        # Register built-in workflows
        for workflow in builtin_workflows:
            self.workflows[workflow.name] = workflow
            
        logger.info(f"Registered {len(self.workflows)} workflow templates")
    
    def select_workflow(self, asset_spec: AssetSpecification, 
                       preferences: Optional[Dict[str, Any]] = None) -> Optional[WorkflowTemplate]:
        """
        Intelligently select the best workflow for an asset specification
        
        Args:
            asset_spec: Asset specification with requirements
            preferences: Optional preferences for workflow selection
        
        Returns:
            Best matching workflow template or None if none suitable
        """
        preferences = preferences or {}
        
        # Filter compatible workflows
        compatible_workflows = [
            workflow for workflow in self.workflows.values()
            if workflow.is_compatible(asset_spec)
        ]
        
        if not compatible_workflows:
            logger.warning(f"No compatible workflows found for asset type {asset_spec.asset_type}")
            return None
        
        # Score workflows based on requirements and preferences
        scored_workflows = []
        for workflow in compatible_workflows:
            score = self._score_workflow(workflow, asset_spec, preferences)
            scored_workflows.append((score, workflow))
        
        # Sort by score (highest first)
        scored_workflows.sort(key=lambda x: x[0], reverse=True)
        
        best_workflow = scored_workflows[0][1]
        logger.info(f"Selected workflow '{best_workflow.name}' for {asset_spec.asset_type} asset")
        
        return best_workflow
    
    def _score_workflow(self, workflow: WorkflowTemplate, 
                       asset_spec: AssetSpecification,
                       preferences: Dict[str, Any]) -> float:
        """Score a workflow based on how well it matches requirements"""
        score = 0.0
        
        # Base compatibility score
        score += 10.0
        
        # Performance vs quality preference
        quality_preference = preferences.get("quality_over_speed", 0.5)  # 0-1 scale
        if quality_preference > 0.7:
            # High quality preference - favor higher performance workflows
            score += workflow.performance_score * 2
        elif quality_preference < 0.3:
            # Speed preference - favor faster workflows
            score += (10 - workflow.performance_score) * 1.5
        else:
            # Balanced preference
            score += workflow.performance_score
        
        # Memory usage consideration
        memory_preference = preferences.get("memory_usage", "medium")
        if memory_preference == "low" and workflow.memory_usage == "low":
            score += 5.0
        elif memory_preference == "high" and workflow.memory_usage == "high":
            score += 3.0
        elif memory_preference == workflow.memory_usage:
            score += 2.0
        
        # Resolution match bonus
        requested_res = (asset_spec.generation_params.width, asset_spec.generation_params.height)
        if requested_res in workflow.supported_resolutions:
            score += 5.0
        
        # Category preference
        quality_level = asset_spec.quality_requirements.min_quality_score
        if quality_level >= 90 and workflow.category == WorkflowCategory.CINEMATIC:
            score += 8.0
        elif quality_level >= 80 and workflow.category == WorkflowCategory.PRODUCTION:
            score += 6.0
        elif quality_level >= 70 and workflow.category == WorkflowCategory.ENHANCED:
            score += 4.0
        elif workflow.category == WorkflowCategory.BASIC:
            score += 2.0
        
        return score
    
    def customize_workflow(self, template: WorkflowTemplate, 
                          asset_spec: AssetSpecification) -> Dict[str, Any]:
        """
        Customize a workflow template with asset-specific parameters
        
        Args:
            template: Workflow template to customize
            asset_spec: Asset specification with generation parameters
            
        Returns:
            Customized workflow ready for ComfyUI
        """
        # Check cache first
        cache_key = f"{template.name}_{hash(str(asset_spec.to_dict()))}"
        if cache_key in self.workflow_cache:
            return self.workflow_cache[cache_key].copy()
        
        # Load base template
        workflow = template.load_template()
        if not workflow:
            logger.error(f"Failed to load workflow template {template.name}")
            return {}
        
        # Apply asset-specific customizations
        workflow = self._apply_generation_params(workflow, asset_spec.generation_params)
        workflow = self._apply_prompts(workflow, asset_spec)
        workflow = self._apply_faction_styling(workflow, asset_spec)
        workflow = self._apply_quality_settings(workflow, asset_spec.quality_requirements)
        
        # Cache the result
        self.workflow_cache[cache_key] = workflow.copy()
        
        logger.info(f"Customized workflow {template.name} for {asset_spec.name}")
        return workflow
    
    def _apply_generation_params(self, workflow: Dict[str, Any], 
                                params: GenerationParameters) -> Dict[str, Any]:
        """Apply generation parameters to workflow"""
        # Find and update nodes that need generation parameters
        for node_id, node_data in workflow.items():
            class_type = node_data.get("class_type", "")
            inputs = node_data.get("inputs", {})
            
            # Update checkpoint loader
            if class_type == "CheckpointLoaderSimple":
                inputs["ckpt_name"] = params.model
            
            # Update sampler settings
            elif class_type == "KSampler":
                inputs.update({
                    "steps": params.steps,
                    "cfg": params.cfg,
                    "sampler_name": params.sampler,
                    "scheduler": params.scheduler
                })
                if params.seed is not None:
                    inputs["seed"] = params.seed
            
            # Update latent dimensions
            elif class_type == "EmptyLatentImage":
                inputs.update({
                    "width": params.width,
                    "height": params.height
                })
            
            # Apply LoRAs if present
            elif "lora" in class_type.lower() and params.loras:
                for i, lora in enumerate(params.loras):
                    if i < len(params.loras):  # Don't exceed available LoRA slots
                        inputs.update({
                            "lora_name": lora.get("name", ""),
                            "strength_model": lora.get("strength", 0.8),
                            "strength_clip": lora.get("strength", 0.8)
                        })
        
        return workflow
    
    def _apply_prompts(self, workflow: Dict[str, Any], 
                      asset_spec: AssetSpecification) -> Dict[str, Any]:
        """Apply prompts to workflow text encoders"""
        for node_id, node_data in workflow.items():
            class_type = node_data.get("class_type", "")
            inputs = node_data.get("inputs", {})
            
            if class_type == "CLIPTextEncode":
                # Check if this is positive or negative prompt based on text content
                current_text = inputs.get("text", "").lower()
                
                # Heuristic: if it contains negative words, it's probably negative prompt
                negative_indicators = ["blurry", "low quality", "bad", "ugly", "deformed", "worst"]
                is_negative = any(indicator in current_text for indicator in negative_indicators)
                
                if is_negative:
                    inputs["text"] = asset_spec.negative_prompt
                else:
                    inputs["text"] = asset_spec.base_prompt
        
        return workflow
    
    def _apply_faction_styling(self, workflow: Dict[str, Any], 
                              asset_spec: AssetSpecification) -> Dict[str, Any]:
        """Apply faction-specific styling to workflow"""
        # This could involve faction-specific LoRAs, color adjustments, etc.
        # For now, we'll focus on the core functionality
        
        # Add faction-specific metadata to save nodes
        for node_id, node_data in workflow.items():
            class_type = node_data.get("class_type", "")
            inputs = node_data.get("inputs", {})
            
            if class_type == "SaveImage":
                # Update filename prefix to include faction
                current_prefix = inputs.get("filename_prefix", "")
                faction_prefix = f"TG_{asset_spec.faction}_{asset_spec.asset_type}"
                inputs["filename_prefix"] = f"{faction_prefix}_{asset_spec.name}"
        
        return workflow
    
    def _apply_quality_settings(self, workflow: Dict[str, Any], 
                               quality_req) -> Dict[str, Any]:
        """Apply quality requirements to workflow"""
        # Adjust sampling settings based on quality requirements
        quality_multiplier = quality_req.min_quality_score / 70.0  # Normalize to 70 baseline
        
        for node_id, node_data in workflow.items():
            class_type = node_data.get("class_type", "")
            inputs = node_data.get("inputs", {})
            
            if class_type == "KSampler":
                # Increase steps for higher quality requirements
                current_steps = inputs.get("steps", 20)
                if quality_req.min_quality_score > 85:
                    inputs["steps"] = max(current_steps, 35)
                elif quality_req.min_quality_score > 75:
                    inputs["steps"] = max(current_steps, 30)
        
        return workflow
    
    def get_workflow_by_name(self, name: str) -> Optional[WorkflowTemplate]:
        """Get a specific workflow by name"""
        return self.workflows.get(name)
    
    def list_workflows(self, asset_type: Optional[AssetType] = None) -> List[WorkflowTemplate]:
        """List available workflows, optionally filtered by asset type"""
        if asset_type:
            return [w for w in self.workflows.values() if asset_type in w.asset_types]
        return list(self.workflows.values())
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get statistics about available workflows"""
        stats = {
            "total_workflows": len(self.workflows),
            "by_category": {},
            "by_asset_type": {},
            "memory_distribution": {"low": 0, "medium": 0, "high": 0},
            "performance_range": {
                "min": min(w.performance_score for w in self.workflows.values()),
                "max": max(w.performance_score for w in self.workflows.values()),
                "avg": sum(w.performance_score for w in self.workflows.values()) / len(self.workflows)
            }
        }
        
        for workflow in self.workflows.values():
            # Count by category
            category_name = workflow.category.value
            stats["by_category"][category_name] = stats["by_category"].get(category_name, 0) + 1
            
            # Count by asset types
            for asset_type in workflow.asset_types:
                stats["by_asset_type"][asset_type] = stats["by_asset_type"].get(asset_type, 0) + 1
            
            # Count by memory usage
            stats["memory_distribution"][workflow.memory_usage] += 1
        
        return stats
    
    def validate_workflows(self) -> Dict[str, List[str]]:
        """Validate all workflow templates and return any issues"""
        issues = {"missing_files": [], "invalid_json": [], "configuration_errors": []}
        
        for name, workflow in self.workflows.items():
            # Check if template file exists
            if not workflow.template_path.exists():
                issues["missing_files"].append(f"{name}: {workflow.template_path}")
                continue
            
            # Try to load and validate JSON
            try:
                template_data = workflow.load_template()
                if not template_data:
                    issues["invalid_json"].append(f"{name}: Empty or invalid JSON")
                    continue
                
                # Basic validation of ComfyUI workflow structure
                if not isinstance(template_data, dict):
                    issues["configuration_errors"].append(f"{name}: Root should be object/dict")
                    continue
                
                # Check for required node types
                has_checkpoint = any(
                    node.get("class_type") == "CheckpointLoaderSimple"
                    for node in template_data.values()
                )
                has_sampler = any(
                    node.get("class_type") == "KSampler"
                    for node in template_data.values()
                )
                has_save = any(
                    node.get("class_type") == "SaveImage"
                    for node in template_data.values()
                )
                
                if not has_checkpoint:
                    issues["configuration_errors"].append(f"{name}: Missing CheckpointLoaderSimple node")
                if not has_sampler:
                    issues["configuration_errors"].append(f"{name}: Missing KSampler node")
                if not has_save:
                    issues["configuration_errors"].append(f"{name}: Missing SaveImage node")
                    
            except Exception as e:
                issues["invalid_json"].append(f"{name}: {str(e)}")
        
        return issues