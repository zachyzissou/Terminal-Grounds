"""
Workflow Manager - Intelligent ComfyUI workflow selection and execution
=====================================================================

Manages ComfyUI workflow templates, automatically selects optimal workflows
based on asset specifications, and handles workflow execution with proper
parameter injection.
"""

from __future__ import annotations

import json
import pathlib
import time
from typing import Any, Dict, List, Optional, Union
import logging

from .asset_spec import AssetSpecification, WorkflowType, LoRAConfig
from ..comfyui.enhanced_client import EnhancedComfyClient
from ..utils.logger import setup_logger


class WorkflowTemplate:
    """Represents a ComfyUI workflow template with parameter injection capabilities."""
    
    def __init__(self, name: str, workflow_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        self.name = name
        self.workflow_data = workflow_data
        self.metadata = metadata or {}
        self.parameter_map = self._build_parameter_map()
    
    def _build_parameter_map(self) -> Dict[str, List[str]]:
        """Build a map of injectable parameters to their node paths."""
        param_map = {
            "prompt": [],
            "negative_prompt": [],
            "seed": [],
            "steps": [],
            "cfg": [],
            "width": [],
            "height": [],
            "sampler_name": [],
            "scheduler": [],
            "model": [],
            "loras": []
        }
        
        # Scan workflow nodes for injectable parameters
        for node_id, node in self.workflow_data.items():
            if isinstance(node, dict) and "inputs" in node:
                inputs = node["inputs"]
                
                # Map common parameters
                if "text" in inputs:
                    if node.get("class_type") == "CLIPTextEncode":
                        # Determine if this is positive or negative prompt based on connections
                        if self._is_negative_prompt_node(node_id):
                            param_map["negative_prompt"].append(node_id)
                        else:
                            param_map["prompt"].append(node_id)
                
                for param in ["seed", "steps", "cfg", "width", "height", "sampler_name", "scheduler"]:
                    if param in inputs:
                        param_map[param].append(node_id)
                
                # Handle model loading
                if node.get("class_type") == "CheckpointLoaderSimple" and "ckpt_name" in inputs:
                    param_map["model"].append(node_id)
                
                # Handle LoRA loading
                if "LoRA" in node.get("class_type", ""):
                    param_map["loras"].append(node_id)
        
        return param_map
    
    def _is_negative_prompt_node(self, node_id: str) -> bool:
        """Determine if a text encode node is for negative prompts."""
        # This is a heuristic - in practice, you'd analyze the workflow connections
        # For now, assume nodes with higher IDs are negative prompts
        try:
            return int(node_id) % 2 == 1  # Odd numbered nodes are negative
        except ValueError:
            return "negative" in node_id.lower()
    
    def inject_parameters(self, spec: AssetSpecification) -> Dict[str, Any]:
        """Inject asset specification parameters into the workflow."""
        workflow = json.loads(json.dumps(self.workflow_data))  # Deep copy
        
        # Inject basic parameters
        self._inject_prompts(workflow, spec)
        self._inject_render_settings(workflow, spec)
        self._inject_model_settings(workflow, spec)
        self._inject_loras(workflow, spec)
        
        return workflow
    
    def _inject_prompts(self, workflow: Dict[str, Any], spec: AssetSpecification):
        """Inject prompt parameters into workflow nodes."""
        full_prompt = spec.get_full_prompt()
        negative_prompt = spec.get_full_negative_prompt()
        
        # Inject positive prompts
        for node_id in self.parameter_map["prompt"]:
            if node_id in workflow:
                workflow[node_id]["inputs"]["text"] = full_prompt
        
        # Inject negative prompts
        for node_id in self.parameter_map["negative_prompt"]:
            if node_id in workflow:
                workflow[node_id]["inputs"]["text"] = negative_prompt
    
    def _inject_render_settings(self, workflow: Dict[str, Any], spec: AssetSpecification):
        """Inject render settings into workflow nodes."""
        settings = spec.render_settings
        
        # Inject individual parameters
        for param, value in [
            ("seed", settings.seed or int(time.time())),
            ("steps", settings.steps),
            ("cfg", settings.cfg),
            ("width", settings.width),
            ("height", settings.height),
            ("sampler_name", settings.sampler),
            ("scheduler", settings.scheduler)
        ]:
            for node_id in self.parameter_map[param]:
                if node_id in workflow:
                    workflow[node_id]["inputs"][param] = value
    
    def _inject_model_settings(self, workflow: Dict[str, Any], spec: AssetSpecification):
        """Inject model settings into workflow nodes."""
        for node_id in self.parameter_map["model"]:
            if node_id in workflow:
                workflow[node_id]["inputs"]["ckpt_name"] = spec.model_name
    
    def _inject_loras(self, workflow: Dict[str, Any], spec: AssetSpecification):
        """Inject LoRA configurations into workflow nodes."""
        loras = spec.get_all_loras()
        
        # This is a simplified LoRA injection - real implementation would be more complex
        lora_nodes = self.parameter_map["loras"]
        for i, lora in enumerate(loras[:len(lora_nodes)]):
            if i < len(lora_nodes):
                node_id = lora_nodes[i]
                if node_id in workflow:
                    node = workflow[node_id]
                    if "lora_name" in node["inputs"]:
                        node["inputs"]["lora_name"] = lora.name
                    if "strength_model" in node["inputs"]:
                        node["inputs"]["strength_model"] = lora.strength
                    if "strength_clip" in node["inputs"]:
                        node["inputs"]["strength_clip"] = lora.clip_strength or lora.strength


class WorkflowManager:
    """Manages ComfyUI workflows and their execution."""
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger("WorkflowManager", config.log_level)
        self.comfy_client = EnhancedComfyClient(config.comfyui_url)
        
        # Load workflow templates
        self.templates = {}
        self._load_workflow_templates()
        
        # Workflow selection rules
        self.selection_rules = self._build_selection_rules()
        
        self.logger.info(f"WorkflowManager initialized with {len(self.templates)} templates")
    
    def _load_workflow_templates(self):
        """Load all workflow templates from the workflows directory."""
        workflows_dir = pathlib.Path(__file__).parents[2] / "workflows"
        
        for workflow_file in workflows_dir.glob("*.json"):
            try:
                workflow_data = json.loads(workflow_file.read_text())
                template_name = workflow_file.stem
                
                # Load metadata if available
                metadata_file = workflow_file.with_suffix(".meta.json")
                metadata = {}
                if metadata_file.exists():
                    metadata = json.loads(metadata_file.read_text())
                
                template = WorkflowTemplate(template_name, workflow_data, metadata)
                self.templates[template_name] = template
                
                self.logger.debug(f"Loaded workflow template: {template_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to load workflow {workflow_file}: {e}")
    
    def _build_selection_rules(self) -> Dict[WorkflowType, str]:
        """Build rules for automatic workflow selection."""
        return {
            WorkflowType.CONCEPT_ART: "concept_art",
            WorkflowType.STYLE_BOARD: "style_board", 
            WorkflowType.TEXTURE_DECAL: "texture_decal",
            WorkflowType.HIGH_DETAIL_RENDER: "high_detail_render",
            WorkflowType.ICON_GENERATION: "icon_generation",
            WorkflowType.POSTER_DESIGN: "poster_design",
            WorkflowType.ENVIRONMENT_MATTE: "environment_matte"
        }
    
    def select_workflow(self, spec: AssetSpecification) -> WorkflowTemplate:
        """Select the optimal workflow template for an asset specification."""
        # Primary selection based on workflow_type
        template_name = self.selection_rules.get(spec.workflow_type)
        
        # Fallback to available templates
        if template_name not in self.templates:
            available_templates = list(self.templates.keys())
            if available_templates:
                template_name = available_templates[0]
                self.logger.warning(
                    f"Requested workflow {spec.workflow_type} not found, "
                    f"using fallback: {template_name}"
                )
            else:
                raise ValueError("No workflow templates available")
        
        template = self.templates[template_name]
        self.logger.info(f"Selected workflow template: {template_name} for {spec.name}")
        
        return template
    
    def execute_workflow(
        self,
        template: WorkflowTemplate,
        spec: AssetSpecification,
        output_dir: Optional[pathlib.Path] = None
    ) -> Dict[str, Any]:
        """Execute a workflow template with the given specification."""
        self.logger.info(f"Executing workflow {template.name} for asset {spec.name}")
        
        try:
            # Inject parameters into workflow
            workflow = template.inject_parameters(spec)
            
            # Determine output directory
            if not output_dir:
                output_dir = spec.output_directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Queue workflow for execution
            job_id = self.comfy_client.queue_workflow(workflow)
            self.logger.debug(f"Queued workflow with job ID: {job_id}")
            
            # Wait for completion and download results
            images, history = self.comfy_client.wait_for_images(
                job_id, 
                output_dir,
                timeout=self.config.generation_timeout
            )
            
            # Build result metadata
            result = {
                "job_id": job_id,
                "template_name": template.name,
                "asset_name": spec.name,
                "output_directory": str(output_dir),
                "images": images,
                "history": history,
                "specification": spec.to_dict(),
                "workflow_used": workflow,
                "generation_timestamp": time.time()
            }
            
            # Save metadata sidecar files
            self._save_metadata_sidecars(result, spec, output_dir)
            
            self.logger.info(
                f"Workflow execution completed: {len(images)} images generated"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise
    
    def _save_metadata_sidecars(
        self, 
        result: Dict[str, Any], 
        spec: AssetSpecification, 
        output_dir: pathlib.Path
    ):
        """Save metadata sidecar files for generated images."""
        for image_info in result["images"]:
            image_path = output_dir / image_info["filename"]
            sidecar_path = image_path.with_suffix(image_path.suffix + ".json")
            
            metadata = {
                "asset_specification": spec.to_dict(),
                "generation_info": {
                    "job_id": result["job_id"],
                    "template_name": result["template_name"],
                    "timestamp": result["generation_timestamp"],
                    "comfyui_history": result["history"]
                },
                "image_info": image_info,
                "pipeline_version": "2.0.0"
            }
            
            sidecar_path.write_text(json.dumps(metadata, indent=2))
    
    def validate_all_workflows(self) -> Dict[str, Any]:
        """Validate all loaded workflow templates."""
        validation_results = {
            "all_valid": True,
            "templates_checked": len(self.templates),
            "errors": [],
            "warnings": []
        }
        
        for name, template in self.templates.items():
            try:
                # Basic workflow structure validation
                if not isinstance(template.workflow_data, dict):
                    validation_results["errors"].append(
                        f"Template {name}: workflow_data is not a dictionary"
                    )
                    validation_results["all_valid"] = False
                    continue
                
                # Check for required nodes
                required_node_types = ["CLIPTextEncode", "KSampler", "SaveImage"]
                found_types = set()
                
                for node in template.workflow_data.values():
                    if isinstance(node, dict) and "class_type" in node:
                        found_types.add(node["class_type"])
                
                missing_types = set(required_node_types) - found_types
                if missing_types:
                    validation_results["warnings"].append(
                        f"Template {name}: missing node types {missing_types}"
                    )
                
                # Validate parameter map
                if not template.parameter_map["prompt"]:
                    validation_results["warnings"].append(
                        f"Template {name}: no prompt injection points found"
                    )
                
            except Exception as e:
                validation_results["errors"].append(f"Template {name}: validation error - {e}")
                validation_results["all_valid"] = False
        
        return validation_results
    
    def test_connection(self) -> bool:
        """Test connection to ComfyUI server."""
        try:
            return self.comfy_client.test_connection()
        except Exception as e:
            self.logger.error(f"ComfyUI connection test failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current workflow manager status."""
        return {
            "templates_loaded": len(self.templates),
            "template_names": list(self.templates.keys()),
            "comfyui_connected": self.test_connection(),
            "selection_rules": {wf_type.value: template for wf_type, template in self.selection_rules.items()}
        }
    
    def reload_templates(self):
        """Reload all workflow templates from disk."""
        self.logger.info("Reloading workflow templates")
        self.templates.clear()
        self._load_workflow_templates()
    
    def add_custom_template(self, name: str, workflow_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Add a custom workflow template at runtime."""
        template = WorkflowTemplate(name, workflow_data, metadata)
        self.templates[name] = template
        self.logger.info(f"Added custom workflow template: {name}")
    
    def shutdown(self):
        """Shutdown the workflow manager."""
        self.logger.info("Shutting down WorkflowManager")
        # Any cleanup needed for ComfyUI client
        self.comfy_client.shutdown()


# Convenience functions
def create_simple_workflow(
    model_name: str = "flux.1-dev",
    steps: int = 28,
    cfg: float = 6.5
) -> Dict[str, Any]:
    """Create a simple workflow template programmatically."""
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": model_name}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "", "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "", "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 0,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0]
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"images": ["6", 0]}
        }
    }