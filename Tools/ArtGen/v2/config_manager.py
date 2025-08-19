#!/usr/bin/env python3
"""
Configuration Manager for Terminal Grounds v2.0
===============================================
Centralized configuration management with validation, defaults, and environment support.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Type
from dataclasses import dataclass, field, asdict
import logging
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

@dataclass
class ConfigValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing"""
    pass

class ConfigManager:
    """
    Centralized configuration manager for the Terminal Grounds pipeline.
    Handles loading, validation, environment overrides, and schema migration.
    """
    
    def __init__(self, config_path: Optional[Path] = None, auto_create: bool = True):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file (defaults to standard location)
            auto_create: Whether to create default config if not found
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config_data: Dict[str, Any] = {}
        self.schema_version = "2.0.0"
        
        # Environment variable prefix
        self.env_prefix = "TG_PIPELINE_"
        
        # Load configuration
        if self.config_path.exists():
            self.load_config()
        elif auto_create:
            self.create_default_config()
        else:
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
        
        # Apply environment overrides
        self._apply_environment_overrides()
        
        # Validate configuration
        validation_result = self.validate_config()
        if not validation_result.is_valid:
            logger.error(f"Configuration validation failed: {validation_result.errors}")
            raise ConfigurationError(f"Invalid configuration: {validation_result.errors}")
        
        if validation_result.warnings:
            for warning in validation_result.warnings:
                logger.warning(f"Configuration warning: {warning}")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            
            # Check for schema migration needs
            config_version = self.config_data.get("schema_version", "1.0.0")
            if config_version != self.schema_version:
                logger.info(f"Migrating configuration from {config_version} to {self.schema_version}")
                self._migrate_config(config_version)
            
            return self.config_data
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save_config(self, backup: bool = True) -> bool:
        """Save configuration to file"""
        try:
            # Create backup if requested
            if backup and self.config_path.exists():
                backup_path = self._create_backup()
                logger.info(f"Configuration backed up to {backup_path}")
            
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Update metadata
            self.config_data["pipeline_info"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            self.config_data["schema_version"] = self.schema_version
            
            # Write configuration
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        logger.info("Creating default configuration")
        
        # Load default config from the JSON file we created
        default_config_path = Path(__file__).parent / "pipeline_config.json"
        if default_config_path.exists():
            with open(default_config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
        else:
            # Fallback minimal config if default file is missing
            self.config_data = self._get_minimal_config()
        
        # Update paths to be absolute
        self._resolve_paths()
        
        # Save the config
        self.save_config(backup=False)
        
        return self.config_data
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key_path: Dot-separated path to config value (e.g., "comfyui.connection.timeout_seconds")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = key_path.split('.')
            value = self.config_data
            
            for key in keys:
                value = value[key]
            
            return value
            
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Set configuration value using dot notation
        
        Args:
            key_path: Dot-separated path to config value
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            keys = key_path.split('.')
            config = self.config_data
            
            # Navigate to parent
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # Set value
            config[keys[-1]] = value
            
            logger.debug(f"Configuration updated: {key_path} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set configuration {key_path}: {e}")
            return False
    
    def validate_config(self) -> ConfigValidationResult:
        """Validate configuration against schema and requirements"""
        result = ConfigValidationResult(is_valid=True)
        
        # Required sections
        required_sections = [
            "pipeline_info", "comfyui", "quality_assurance", "models",
            "workflows", "factions", "paths", "generation_defaults"
        ]
        
        for section in required_sections:
            if section not in self.config_data:
                result.errors.append(f"Missing required section: {section}")
                result.is_valid = False
        
        # Validate paths exist
        path_validations = [
            ("paths.base_directory", "Base directory"),
            ("workflows.templates_directory", "Workflow templates directory")
        ]
        
        for path_key, description in path_validations:
            path_value = self.get(path_key)
            if path_value:
                path_obj = Path(path_value)
                if not path_obj.exists():
                    result.warnings.append(f"{description} does not exist: {path_value}")
        
        # Validate ComfyUI settings
        max_concurrent = self.get("comfyui.performance.max_concurrent_jobs", 1)
        if max_concurrent < 1 or max_concurrent > 8:
            result.warnings.append(f"max_concurrent_jobs should be between 1 and 8, got {max_concurrent}")
        
        # Validate quality thresholds
        for asset_type, thresholds in self.get("quality_assurance.thresholds_by_type", {}).items():
            if not isinstance(thresholds, dict):
                result.errors.append(f"Invalid thresholds for {asset_type}: must be dict")
                result.is_valid = False
                continue
            
            min_score = thresholds.get("min", 0)
            target_score = thresholds.get("target", 0)
            hero_score = thresholds.get("hero", 0)
            
            if not (0 <= min_score <= target_score <= hero_score <= 100):
                result.errors.append(f"Invalid quality thresholds for {asset_type}: min <= target <= hero")
                result.is_valid = False
        
        # Validate model paths
        primary_model = self.get("models.primary_model")
        if primary_model:
            # This would check if model file exists in ComfyUI models directory
            result.suggestions.append("Verify primary model file exists in ComfyUI models directory")
        
        # Validate faction data
        enabled_factions = self.get("factions.enabled_factions", [])
        if not enabled_factions:
            result.warnings.append("No factions enabled")
        
        faction_data_dir = self.get("factions.data_directory")
        if faction_data_dir:
            faction_path = Path(faction_data_dir)
            if not faction_path.exists():
                result.warnings.append(f"Faction data directory does not exist: {faction_data_dir}")
        
        logger.info(f"Configuration validation completed: {len(result.errors)} errors, {len(result.warnings)} warnings")
        return result
    
    def get_comfyui_config(self) -> Dict[str, Any]:
        """Get ComfyUI-specific configuration"""
        return self.get("comfyui", {})
    
    def get_quality_config(self) -> Dict[str, Any]:
        """Get quality assurance configuration"""
        return self.get("quality_assurance", {})
    
    def get_faction_config(self, faction_code: str) -> Dict[str, Any]:
        """Get configuration for specific faction"""
        all_factions = self.get("factions.style_profiles", {})
        return all_factions.get(faction_code, {})
    
    def get_asset_defaults(self, asset_type: str) -> Dict[str, Any]:
        """Get default settings for specific asset type"""
        defaults = {}
        
        # Resolution defaults
        resolution = self.get(f"generation_defaults.resolution.{asset_type}")
        if resolution:
            defaults["resolution"] = resolution
        
        # Quality thresholds
        thresholds = self.get(f"quality_assurance.thresholds_by_type.{asset_type}")
        if thresholds:
            defaults["quality_thresholds"] = thresholds
        
        # Sampling defaults
        sampling = self.get("generation_defaults.sampling", {})
        defaults["sampling"] = sampling
        
        return defaults
    
    def get_preset_config(self, preset_name: str) -> Dict[str, Any]:
        """Get preset configuration"""
        return self.get(f"presets.{preset_name}", {})
    
    def update_from_env(self, force_reload: bool = False) -> List[str]:
        """Update configuration from environment variables"""
        if force_reload:
            self._apply_environment_overrides()
        
        # Return list of environment variables that were applied
        applied_vars = []
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                applied_vars.append(f"{key}={value}")
        
        return applied_vars
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides"""
        overrides_applied = []
        
        # Define environment variable mappings
        env_mappings = {
            f"{self.env_prefix}COMFYUI_SERVER": "comfyui.server_detection.server_override",
            f"{self.env_prefix}COMFYUI_PORT": "comfyui.server_detection.primary_port",
            f"{self.env_prefix}PRIMARY_MODEL": "models.primary_model",
            f"{self.env_prefix}MAX_CONCURRENT": "comfyui.performance.max_concurrent_jobs",
            f"{self.env_prefix}QUALITY_THRESHOLD": "quality_assurance.scoring.min_acceptable_score",
            f"{self.env_prefix}OUTPUT_DIR": "paths.output_directory",
            f"{self.env_prefix}LOG_LEVEL": "logging.level",
            f"{self.env_prefix}UE5_AUTO_IMPORT": "ue5_integration.auto_import"
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert value to appropriate type
                converted_value = self._convert_env_value(env_value)
                
                # Set in configuration
                if self.set(config_path, converted_value):
                    overrides_applied.append(f"{env_var} -> {config_path}")
        
        if overrides_applied:
            logger.info(f"Applied {len(overrides_applied)} environment overrides")
            for override in overrides_applied:
                logger.debug(f"Environment override: {override}")
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type"""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer conversion
        try:
            if '.' not in value:
                return int(value)
        except ValueError:
            pass
        
        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _resolve_paths(self):
        """Resolve relative paths to absolute paths"""
        base_dir = Path(self.get("paths.base_directory", ".")).resolve()
        
        # Update base directory to absolute path
        self.set("paths.base_directory", str(base_dir))
        
        # Resolve other paths relative to base directory
        path_keys = [
            "paths.output_directory",
            "paths.staging_directory", 
            "paths.batch_output",
            "paths.assets_database",
            "paths.temp_directory",
            "paths.archive_directory",
            "workflows.templates_directory",
            "workflows.custom_directory",
            "factions.data_directory"
        ]
        
        for path_key in path_keys:
            path_value = self.get(path_key)
            if path_value and not Path(path_value).is_absolute():
                absolute_path = base_dir / path_value
                self.set(path_key, str(absolute_path))
    
    def _migrate_config(self, from_version: str):
        """Migrate configuration from older version"""
        logger.info(f"Migrating configuration from version {from_version}")
        
        # Create backup before migration
        backup_path = self._create_backup(suffix=f"_pre_migration_{from_version}")
        
        # Migration logic based on version
        if from_version.startswith("1."):
            self._migrate_from_v1()
        
        # Update schema version
        self.config_data["schema_version"] = self.schema_version
        self.config_data["last_migration"] = {
            "from_version": from_version,
            "to_version": self.schema_version,
            "migration_date": datetime.now().isoformat(),
            "backup_path": str(backup_path)
        }
        
        # Save migrated configuration
        self.save_config(backup=False)
        
        logger.info(f"Configuration migration completed: {from_version} -> {self.schema_version}")
    
    def _migrate_from_v1(self):
        """Migrate from v1.x configuration format"""
        # This would contain specific migration logic
        # For now, just ensure required sections exist
        
        if "quality_assurance" not in self.config_data:
            self.config_data["quality_assurance"] = {
                "scoring": {"min_acceptable_score": 60.0},
                "enhancement": {"auto_enhance": True}
            }
        
        if "ue5_integration" not in self.config_data:
            self.config_data["ue5_integration"] = {
                "enabled": False,
                "auto_import": False
            }
    
    def _create_backup(self, suffix: str = "") -> Path:
        """Create backup of current configuration"""
        if not self.config_path.exists():
            return self.config_path
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.config_path.stem}_{timestamp}{suffix}.json"
        backup_dir = self.config_path.parent / "config_backups"
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / backup_name
        shutil.copy2(self.config_path, backup_path)
        
        # Cleanup old backups
        self._cleanup_old_backups(backup_dir)
        
        return backup_path
    
    def _cleanup_old_backups(self, backup_dir: Path, keep_count: int = 10):
        """Clean up old backup files"""
        try:
            backup_files = list(backup_dir.glob("*.json"))
            backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            
            # Remove old backups beyond keep_count
            for old_backup in backup_files[keep_count:]:
                old_backup.unlink()
                logger.debug(f"Removed old backup: {old_backup}")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")
    
    def _get_default_config_path(self) -> Path:
        """Get default configuration file path"""
        # Try multiple locations in order of preference
        possible_paths = [
            Path.cwd() / "pipeline_config.json",
            Path(__file__).parent / "pipeline_config.json",
            Path.home() / ".terminal_grounds" / "pipeline_config.json"
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # Return first path as default if none exist
        return possible_paths[0]
    
    def _get_minimal_config(self) -> Dict[str, Any]:
        """Get minimal fallback configuration"""
        return {
            "pipeline_info": {
                "name": "Terminal Grounds Asset Pipeline v2.0",
                "version": "2.0.0",
                "description": "Minimal configuration"
            },
            "comfyui": {
                "server_detection": {"auto_detect": True},
                "connection": {"timeout_seconds": 300},
                "performance": {"max_concurrent_jobs": 1}
            },
            "quality_assurance": {
                "scoring": {"min_acceptable_score": 60.0},
                "enhancement": {"auto_enhance": False}
            },
            "models": {
                "primary_model": "flux1-dev-fp8.safetensors"
            },
            "workflows": {
                "templates_directory": "workflows"
            },
            "factions": {
                "enabled_factions": ["neutral"]
            },
            "paths": {
                "base_directory": str(Path.cwd()),
                "output_directory": "outputs"
            },
            "generation_defaults": {
                "sampling": {"steps": 20, "cfg": 4.0}
            },
            "schema_version": self.schema_version
        }
    
    def export_config(self, export_path: Path, include_comments: bool = True) -> bool:
        """Export configuration with optional comments"""
        try:
            export_data = self.config_data.copy()
            
            if include_comments:
                # Add helpful comments to the exported config
                export_data["_comments"] = {
                    "pipeline_info": "Basic pipeline information and metadata",
                    "comfyui": "ComfyUI server connection and performance settings",
                    "quality_assurance": "Quality scoring and enhancement settings",
                    "models": "AI model configuration and LoRA settings",
                    "factions": "Faction-specific styling and preferences",
                    "paths": "File system paths and directories",
                    "ue5_integration": "Unreal Engine 5 import and integration settings"
                }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False
    
    def reset_to_defaults(self, backup: bool = True) -> bool:
        """Reset configuration to defaults"""
        try:
            if backup:
                backup_path = self._create_backup(suffix="_before_reset")
                logger.info(f"Created backup before reset: {backup_path}")
            
            # Create new default configuration
            self.create_default_config()
            
            logger.info("Configuration reset to defaults")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""
        return {
            "config_file": str(self.config_path),
            "schema_version": self.get("schema_version"),
            "pipeline_version": self.get("pipeline_info.version"),
            "last_updated": self.get("pipeline_info.last_updated"),
            "comfyui_enabled": self.get("comfyui.server_detection.auto_detect", False),
            "ue5_integration": self.get("ue5_integration.enabled", False),
            "enabled_factions": len(self.get("factions.enabled_factions", [])),
            "quality_threshold": self.get("quality_assurance.scoring.min_acceptable_score"),
            "primary_model": self.get("models.primary_model"),
            "base_directory": self.get("paths.base_directory")
        }