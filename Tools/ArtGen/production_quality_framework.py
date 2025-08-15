"""
Terminal Grounds Production Quality Framework
Establishes consistent 4K-8K quality standards for ALL asset types
"""

from typing import Dict, Any, List
from enum import Enum

class AssetCategory(Enum):
    LOGOS_INSIGNIAS = "logos_insignias"
    CONCEPT_ART = "concept_art" 
    TEXTURES = "textures"
    CHARACTER_DESIGN = "character_design"
    WORLD_DESIGN = "world_design"
    LEVEL_DESIGN = "level_design"
    UI_ELEMENTS = "ui_elements"
    UX_GRAPHICS = "ux_graphics"
    VEHICLES = "vehicles"
    WEAPONS = "weapons"
    ENVIRONMENTS = "environments"
    MATERIALS = "materials"

class QualityStandard:
    """Production quality standards for each asset type"""
    
    def __init__(self):
        self.standards = {
            AssetCategory.LOGOS_INSIGNIAS: {
                "target_resolution": (4096, 4096),
                "base_generation": (2048, 2048),  # Generate high, upscale minimal
                "upscale_method": "nearest-exact",  # Preserve vector sharpness
                "steps": 35,
                "cfg": 3.5,
                "quality_keywords": [
                    "ultra high resolution", "vector art", "sharp edges", 
                    "crisp lines", "professional logo design", "military insignia"
                ],
                "negative_keywords": [
                    "blurry", "soft", "low resolution", "pixelated", "amateur",
                    "complex background", "cluttered"
                ],
                "background": "transparent or solid color",
                "format": "PNG with alpha channel",
                "usage_notes": "Must be sharp at any zoom level"
            },
            
            AssetCategory.CONCEPT_ART: {
                "target_resolution": (3840, 2160),  # 4K landscape
                "base_generation": (1920, 1080),
                "upscale_method": "RealESRGAN_x2.pth",  # AI upscale for detail
                "steps": 40,
                "cfg": 4.5,
                "quality_keywords": [
                    "concept art", "detailed illustration", "professional game art",
                    "high detail", "cinematic lighting", "atmospheric"
                ],
                "negative_keywords": [
                    "low quality", "amateur", "sketch", "unfinished",
                    "poor composition", "bad lighting"
                ],
                "background": "full scene composition",
                "format": "High quality JPEG or PNG",
                "usage_notes": "Portfolio-quality concept illustrations"
            },
            
            AssetCategory.TEXTURES: {
                "target_resolution": (4096, 4096),  # Seamless tiling
                "base_generation": (2048, 2048),
                "upscale_method": "4x-UltraSharp.pth",  # Detail preservation
                "steps": 45,
                "cfg": 4.0,
                "quality_keywords": [
                    "seamless texture", "tileable", "high resolution", 
                    "detailed surface", "material texture", "PBR ready"
                ],
                "negative_keywords": [
                    "seams", "visible edges", "low resolution", "blurry",
                    "compression artifacts", "repetitive patterns"
                ],
                "background": "seamless pattern",
                "format": "PNG, multiple maps (diffuse, normal, roughness)",
                "usage_notes": "Must tile seamlessly in all directions"
            },
            
            AssetCategory.CHARACTER_DESIGN: {
                "target_resolution": (2048, 3072),  # Portrait aspect
                "base_generation": (1024, 1536),
                "upscale_method": "RealESRGAN_x2.pth",  # Face detail critical
                "steps": 50,
                "cfg": 5.0,
                "quality_keywords": [
                    "character design", "detailed portrait", "professional character art",
                    "high detail", "clear features", "faction appropriate"
                ],
                "negative_keywords": [
                    "blurry face", "malformed", "amateur", "low detail",
                    "bad anatomy", "unclear features"
                ],
                "background": "neutral or faction appropriate",
                "format": "PNG with transparency options",
                "usage_notes": "Face and gear details must be crisp"
            },
            
            AssetCategory.UI_ELEMENTS: {
                "target_resolution": (512, 512),  # Icon standard
                "base_generation": (512, 512),  # Generate at target
                "upscale_method": "none",  # No upscaling blur
                "steps": 30,
                "cfg": 3.0,
                "quality_keywords": [
                    "UI icon", "clean design", "high contrast", 
                    "simple", "recognizable", "game interface"
                ],
                "negative_keywords": [
                    "complex", "cluttered", "low contrast", "unclear",
                    "text", "blurry edges"
                ],
                "background": "transparent",
                "format": "PNG with alpha",
                "usage_notes": "Must be readable at small sizes"
            },
            
            AssetCategory.WEAPONS: {
                "target_resolution": (3840, 2160),  # 4K detail view
                "base_generation": (1920, 1080),
                "upscale_method": "4x-UltraSharp.pth",
                "steps": 45,
                "cfg": 4.8,
                "quality_keywords": [
                    "weapon concept", "detailed firearm", "technical illustration",
                    "high detail", "realistic materials", "professional design"
                ],
                "negative_keywords": [
                    "toy-like", "unrealistic", "low detail", "amateur",
                    "poor materials", "bad perspective"
                ],
                "background": "neutral showcase or in-context",
                "format": "High quality PNG",
                "usage_notes": "Technical accuracy important"
            },
            
            AssetCategory.ENVIRONMENTS: {
                "target_resolution": (7680, 4320),  # 8K for large scenes
                "base_generation": (1920, 1080),
                "upscale_method": "RealESRGAN_x2.pth",  # Then additional scaling
                "steps": 50,
                "cfg": 5.5,
                "quality_keywords": [
                    "environment concept", "detailed landscape", "atmospheric",
                    "cinematic", "high detail", "immersive"
                ],
                "negative_keywords": [
                    "flat", "low detail", "poor atmosphere", "amateur",
                    "bad composition", "unclear"
                ],
                "background": "full environmental scene",
                "format": "High quality JPEG",
                "usage_notes": "Cinematic quality for key art"
            }
        }
    
    def get_optimal_settings(self, asset_type: AssetCategory) -> Dict[str, Any]:
        """Get production-optimized settings for asset type"""
        return self.standards.get(asset_type, {})
    
    def get_quality_workflow(self, asset_type: AssetCategory, faction_data: Dict = None) -> Dict[str, Any]:
        """Generate optimized workflow for specific asset type"""
        
        settings = self.get_optimal_settings(asset_type)
        if not settings:
            raise ValueError(f"No settings defined for {asset_type}")
        
        base_width, base_height = settings["base_generation"]
        target_width, target_height = settings["target_resolution"]
        
        # Build quality-optimized prompt
        quality_prompt = ", ".join(settings["quality_keywords"])
        negative_prompt = ", ".join(settings["negative_keywords"])
        
        if faction_data:
            quality_prompt = f"Terminal Grounds {faction_data.get('name', '')} {quality_prompt}"
        
        workflow = {
            "checkpoint": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
            },
            
            "positive_prompt": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": quality_prompt,
                    "clip": ["checkpoint", 1]
                }
            },
            
            "negative_prompt": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["checkpoint", 1]
                }
            },
            
            "latent": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": base_width,
                    "height": base_height,
                    "batch_size": 1
                }
            },
            
            "sampler": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 12345,  # Will be overridden
                    "steps": settings["steps"],
                    "cfg": settings["cfg"],
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": 1.0,
                    "model": ["checkpoint", 0],
                    "positive": ["positive_prompt", 0],
                    "negative": ["negative_prompt", 0],
                    "latent_image": ["latent", 0]
                }
            },
            
            "decoded": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["sampler", 0],
                    "vae": ["checkpoint", 2]
                }
            }
        }
        
        # Add appropriate upscaling
        if settings["upscale_method"] == "none":
            workflow["save"] = {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["decoded", 0],
                    "filename_prefix": f"TG_PROD_{asset_type.value.upper()}"
                }
            }
        elif settings["upscale_method"] in ["nearest-exact", "bicubic", "bilinear", "lanczos"]:
            workflow["upscaled"] = {
                "class_type": "ImageScale",
                "inputs": {
                    "image": ["decoded", 0],
                    "upscale_method": settings["upscale_method"],
                    "width": target_width,
                    "height": target_height,
                    "crop": "center"
                }
            }
            workflow["save"] = {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["upscaled", 0],
                    "filename_prefix": f"TG_PROD_{asset_type.value.upper()}"
                }
            }
        else:
            # AI upscaling
            workflow["upscale_model"] = {
                "class_type": "UpscaleModelLoader",
                "inputs": {"model_name": settings["upscale_method"]}
            }
            workflow["ai_upscaled"] = {
                "class_type": "ImageUpscaleWithModel",
                "inputs": {
                    "upscale_model": ["upscale_model", 0],
                    "image": ["decoded", 0]
                }
            }
            workflow["final_resize"] = {
                "class_type": "ImageScale",
                "inputs": {
                    "image": ["ai_upscaled", 0],
                    "upscale_method": "lanczos",
                    "width": target_width,
                    "height": target_height,
                    "crop": "center"
                }
            }
            workflow["save"] = {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["final_resize", 0],
                    "filename_prefix": f"TG_PROD_{asset_type.value.upper()}"
                }
            }
        
        return workflow
    
    def print_quality_matrix(self):
        """Print production quality standards matrix"""
        print("=== TERMINAL GROUNDS PRODUCTION QUALITY MATRIX ===")
        print()
        
        for asset_type, settings in self.standards.items():
            print(f"{asset_type.value.upper().replace('_', ' ')}")
            print(f"  Target: {settings['target_resolution'][0]}x{settings['target_resolution'][1]}")
            print(f"  Method: {settings['upscale_method']}")
            print(f"  Steps: {settings['steps']}, CFG: {settings['cfg']}")
            print(f"  Usage: {settings['usage_notes']}")
            print()

def test_production_framework():
    """Test the production quality framework"""
    
    framework = QualityStandard()
    framework.print_quality_matrix()
    
    # Test logo generation
    print("Testing LOGO production workflow...")
    logo_workflow = framework.get_quality_workflow(AssetCategory.LOGOS_INSIGNIAS)
    print(f"Logo workflow nodes: {len(logo_workflow)}")
    
    return framework

if __name__ == "__main__":
    test_production_framework()