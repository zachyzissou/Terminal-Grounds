"""
Pipeline Configuration Management
===============================

Centralized configuration management for the Terminal Grounds asset generation pipeline.
Handles loading, validation, and management of all pipeline settings.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, Optional
import logging


class PipelineConfig:
    """Central configuration manager for the pipeline."""
    
    def __init__(self, config_path: Optional[pathlib.Path] = None):
        # Default configuration
        self._config = self._get_default_config()
        
        # Load from file if provided
        if config_path and config_path.exists():
            self.load_config(config_path)
        elif not config_path:
            # Try to find default config file
            default_path = pathlib.Path(__file__).parents[2] / "config.json"
            if default_path.exists():
                self.load_config(default_path)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            # ComfyUI settings
            "comfyui_url": "http://127.0.0.1:8188",
            "generation_timeout": 600.0,
            
            # Directory settings
            "base_output_dir": str(pathlib.Path(__file__).parents[3] / "Docs" / "Generated"),
            "workflow_dir": str(pathlib.Path(__file__).parents[2] / "workflows"),
            "prompt_packs_dir": str(pathlib.Path(__file__).parents[2] / "prompt_packs"),
            
            # Processing settings
            "max_concurrent_jobs": 2,
            "job_timeout": 600.0,
            "retry_failed_jobs": True,
            "max_retries": 3,
            
            # Quality settings
            "quality_gate_enabled": True,
            "auto_enhance_assets": True,
            "auto_upscale_assets": False,
            "min_quality_score": 70.0,
            
            # UE5 integration
            "ue5_integration_enabled": False,
            "ue5_project_path": None,
            "ue5_engine_path": None,
            "use_ue5_python_api": True,
            
            # Logging
            "log_level": "INFO",
            "log_file": None,
            
            # Faction configurations
            "faction_configs": {
                "directorate": {
                    "name": "Directorate",
                    "config_file": "DIR.json"
                },
                "free77": {
                    "name": "Free77", 
                    "config_file": "F77.json"
                },
                "vultures": {
                    "name": "Vultures",
                    "config_file": "VLT.json"
                }
            },
            
            # Model settings
            "default_model": "flux.1-dev",
            "available_models": [
                "flux.1-dev",
                "flux.1-schnell"
            ],
            
            # Advanced settings
            "experimental_features": False,
            "debug_mode": False,
            "telemetry_enabled": False
        }
    
    def load_config(self, config_path: pathlib.Path):
        """Load configuration from file."""
        try:
            config_data = json.loads(config_path.read_text())
            self._config.update(config_data)
        except Exception as e:
            logging.warning(f"Failed to load config from {config_path}: {e}")
    
    def save_config(self, config_path: pathlib.Path):
        """Save current configuration to file."""
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps(self._config, indent=2))
        except Exception as e:
            logging.error(f"Failed to save config to {config_path}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self._config[key] = value
    
    def get_faction_config(self, faction_name: str) -> Dict[str, Any]:
        """Get faction-specific configuration."""
        faction_configs = self._config.get("faction_configs", {})
        faction_info = faction_configs.get(faction_name.lower(), {})
        
        if "config_file" in faction_info:
            # Load faction config file
            config_file = faction_info["config_file"]
            config_path = pathlib.Path(self.prompt_packs_dir) / "factions" / config_file
            
            if config_path.exists():
                try:
                    return json.loads(config_path.read_text())
                except Exception as e:
                    logging.warning(f"Failed to load faction config {config_file}: {e}")
        
        return faction_info
    
    def validate_faction_configs(self) -> Dict[str, Any]:
        """Validate all faction configurations."""
        validation_result = {
            "all_valid": True,
            "errors": [],
            "warnings": []
        }
        
        faction_configs = self._config.get("faction_configs", {})
        
        for faction_name, faction_info in faction_configs.items():
            if "config_file" in faction_info:
                config_file = faction_info["config_file"]
                config_path = pathlib.Path(self.prompt_packs_dir) / "factions" / config_file
                
                if not config_path.exists():
                    validation_result["errors"].append(
                        f"Faction config file not found: {config_file}"
                    )
                    validation_result["all_valid"] = False
                else:
                    try:
                        faction_config = json.loads(config_path.read_text())
                        
                        # Validate required fields
                        required_fields = ["name", "positive", "negative", "defaults"]
                        for field in required_fields:
                            if field not in faction_config:
                                validation_result["warnings"].append(
                                    f"Faction {faction_name} missing field: {field}"
                                )
                        
                    except Exception as e:
                        validation_result["errors"].append(
                            f"Invalid faction config {config_file}: {e}"
                        )
                        validation_result["all_valid"] = False
        
        return validation_result
    
    # Property accessors for common config values
    @property
    def comfyui_url(self) -> str:
        return self._config["comfyui_url"]
    
    @property
    def base_output_dir(self) -> str:
        return self._config["base_output_dir"]
    
    @property
    def workflow_dir(self) -> str:
        return self._config["workflow_dir"]
    
    @property
    def prompt_packs_dir(self) -> str:
        return self._config["prompt_packs_dir"]
    
    @property
    def generation_timeout(self) -> float:
        return self._config["generation_timeout"]
    
    @property
    def max_concurrent_jobs(self) -> int:
        return self._config["max_concurrent_jobs"]
    
    @property
    def log_level(self) -> str:
        return self._config["log_level"]
    
    @property
    def quality_gate_enabled(self) -> bool:
        return self._config["quality_gate_enabled"]
    
    @property
    def ue5_integration_enabled(self) -> bool:
        return self._config["ue5_integration_enabled"]