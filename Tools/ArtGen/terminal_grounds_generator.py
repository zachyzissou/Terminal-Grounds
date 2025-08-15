"""
Terminal Grounds Asset Generator - Complete Pipeline
====================================================
This script handles both workflow generation and output monitoring for Terminal Grounds assets.
Designed to work with your RTX 3090 Ti and FLUX models.
"""

import json
import os
import time
import shutil
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import threading
import queue
from dataclasses import dataclass
from enum import Enum

# Configuration
COMFYUI_SERVER = "127.0.0.1:8000"
PROJECT_ROOT = Path(r"C:\Users\Zachg\Terminal-Grounds")
COMFYUI_OUTPUT = Path(r"C:\Users\Zachg\Documents\ComfyUI\output")  # Adjust if needed
TG_ASSETS_ROOT = PROJECT_ROOT / "Content" / "TG"
STYLE_STAGING_ROOT = PROJECT_ROOT / "Style_Staging"

class AssetType(Enum):
    EMBLEM = "emblem"
    POSTER = "poster"
    ICON = "icon"
    RENDER = "render"
    DECAL = "decal"

@dataclass
class Faction:
    """Faction identity and visual parameters"""
    code: str
    name: str
    color_primary: str
    color_secondary: str
    style_tags: List[str]
    emblem_desc: str
    
class TerminalGroundsWorkflowBuilder:
    """
    Builds optimized ComfyUI workflows specifically for Terminal Grounds assets.
    Uses FLUX models and advanced techniques for production-quality results.
    """
    
    def __init__(self):
        self.model = "FLUX1\\flux1-dev-fp8.safetensors"  # Verified available model
        self.loras = self._detect_loras()
        
        # UI Icon semantic prompts for Terminal Grounds
        self.icon_prompts = {
            "damage_ballistic": "ballistic damage icon, bullet impact symbol, kinetic projectile, metallic gray, clean vector design",
            "damage_ion": "ion damage icon, electric energy bolt, blue lightning symbol, energy weapon indicator", 
            "extract": "extraction point icon, upward arrow with landing pad, evacuation symbol, bright green",
            "map_ping": "map ping icon, location marker, waypoint diamond, navigation symbol, yellow",
            "rarity_common": "common rarity icon, simple geometric shape, white/gray, basic tier indicator",
            "rarity_legendary": "legendary rarity icon, ornate star burst, golden glow, premium tier symbol",
            "status_charge": "charge status icon, battery symbol, energy bar, blue power indicator",
            "status_heat": "heat status icon, thermometer symbol, red temperature gauge, thermal warning"
        }
        
        # Available art styles from Style_Staging folder
        self.art_styles = {
            "Clean_SciFi": "clean sci-fi aesthetic, sleek design, minimal details, futuristic, polished",
            "Comic_Military": "comic book military style, bold lines, vibrant colors, stylized illustration",
            "Cyberpunk_Military": "cyberpunk military aesthetic, neon accents, high-tech, dark urban",
            "Gritty_Realism": "gritty realistic military style, weathered, battle-worn, photorealistic textures",
            "Hybrid_Tech": "hybrid technology aesthetic, organic-tech fusion, bio-mechanical design",
            "Minimal_Tactical": "minimal tactical design, clean lines, functional aesthetic, subdued colors",
            "Painted_Concept": "painted concept art style, artistic brush strokes, concept illustration",
            "Post_Apocalyptic": "post-apocalyptic style, rusted metal, decay, survival aesthetic",
            "Soviet_Retro": "soviet retro military style, propaganda poster aesthetic, bold red accents",
            "Stylized_Military": "stylized military design, exaggerated proportions, artistic interpretation"
        }
        
    def _detect_loras(self) -> List[str]:
        """Detect available LoRAs for military/sci-fi styling"""
        # Actual LoRAs available in your ComfyUI setup
        military_loras = [
            "2042 - battlefield 2042 style v1.safetensors",
            "0300 Individual soldier exoskeleton armor suit_v1.safetensors", 
            "0307 Russian Federation Alpha Group FSB_v1.safetensors",
            "Future_Warfare_SDXL.safetensors",
            "Faction_Soldier-000008.safetensors",
            "military tactics combined arms formation.safetensors",
            "Reactive armour style.safetensors",
            "cinematic armor style Reactive Armour v1.safetensors",
            "helghast.safetensors",
            "combine soldier.safetensors",
            "WinterSoldier1024.safetensors",
            "XL_Mecha_Angel_Soldier_-_By_HailoKnight.safetensors"
        ]
        
        scifi_loras = [
            "CyberPunk.safetensors",
            "Cyberpunk sceneV1.safetensors", 
            "Blue_Future.safetensors",
            "Interstellar_Scifi_flux-lora-v1.safetensors",
            "SCIFI_Concept_Art_Landscapes.safetensors",
            "Sci-fi_Space_Stations.safetensors",
            "Sci-fi_env_flux.safetensors",
            "Starfield_Concept_Art-000005.safetensors",
            "scifi-landscape.safetensors",
            "scifi-material_V04.safetensors",
            "scifi_buildings_sdxl_lora.safetensors",
            "scifi_super_structure_IL_MIX.safetensors"
        ]
        
        weapon_loras = [
            "AK-47.safetensors",
            "FN P90.safetensors", 
            "FN SCAR-HL.safetensors",
            "HK_M223C_FLUX.safetensors",
            "Heckler & Koch MP5.safetensors",
            "Handheld M134 Minigun.safetensors",
            "LAFC_PRO_GUNS_V3.safetensors",
            "gun style v1.safetensors",
            "uzi.safetensors"
        ]
        
        environment_loras = [
            "Flux-gamemap-2.safetensors",
            "Flux-gamemap-3.safetensors", 
            "Flux-gamemap-5.safetensors",
            "Mass_Effect_3_Environment-000003.safetensors",
            "Rendered Environments SDXL v1.0.safetensors",
            "flux-lora-sceneryart.safetensors",
            "scenery.safetensors",
            "OwSceneryStyle_v1.safetensors"
        ]
        
        texture_loras = [
            "Detailed Skin&Textures Flux V3.safetensors",
            "Enhanced_Lighting_and_Textures_flux_lora.safetensors",
            "Flux Handpainted seamless textures_epoch_5.safetensors",
            "Hand-Painted_2d_Seamless_Textures-000007.safetensors",
            "StylizedTexture_v2.safetensors",
            "textures_flux-000010.safetensors"
        ]
        
        logo_loras = [
            "Graffiti_Logo_Style_Flux.safetensors",
            "Harrlogos_v2.0.safetensors",
            "HMSG-LOGO-XL-000001.safetensors",
            "LogoRedmondV2-Logo-LogoRedmAF.safetensors",
            "logo_v1-000012.safetensors",
            "logomkrdsxl.safetensors"
        ]
        
        return {
            "military": military_loras,
            "scifi": scifi_loras, 
            "weapons": weapon_loras,
            "environments": environment_loras,
            "textures": texture_loras,
            "logos": logo_loras
        }
    
    def build_emblem_workflow(self, faction: Faction, seed: int = None) -> Dict[str, Any]:
        """
        Build a workflow for faction emblem generation with proper styling.
        Uses multiple passes for refinement.
        """
        
        if seed is None:
            seed = abs(hash(faction.code)) % 1000000
            
        # Build sophisticated prompt
        positive_prompt = self._build_emblem_prompt(faction)
        negative_prompt = "text, words, letters, watermark, low quality, blurry, asymmetric, unbalanced, cluttered, complex background"
        
        workflow = {
            # Load checkpoint
            "checkpoint": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": self.model}
            },
            
            # Positive prompt encoding with style emphasis
            "positive_clip": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": positive_prompt,
                    "clip": ["checkpoint", 1]
                }
            },
            
            # Negative prompt
            "negative_clip": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["checkpoint", 1]
                }
            },
            
            # Empty latent at high resolution for emblems
            "latent": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": 2048,
                    "height": 2048,
                    "batch_size": 1
                }
            },
            
            # Initial generation pass
            "ksampler_initial": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": 30,
                    "cfg": 8.5,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1.0,
                    "model": ["checkpoint", 0],
                    "positive": ["positive_clip", 0],
                    "negative": ["negative_clip", 0],
                    "latent_image": ["latent", 0]
                }
            },
            
            # Decode initial result
            "vae_decode": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["ksampler_initial", 0],
                    "vae": ["checkpoint", 2]
                }
            },
            
            # Save the emblem
            "save_emblem": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["vae_decode", 0],
                    "filename_prefix": f"TG_Emblem_{faction.code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            }
        }
        
        # Smart LoRA usage for emblems
        # FLUX alone is excellent for clean emblems, but some LoRAs can add military character
        lora_categories = self.loras
        selected_lora = None
        
        # Use military/tactical LoRAs that enhance rather than override FLUX's emblem capabilities
        military_enhancement_loras = [
            "2042 - battlefield 2042 style v1.safetensors",  # Adds military grittiness
            "Future_Warfare_SDXL.safetensors",  # Enhances sci-fi military aesthetic
            "Faction_Soldier-000008.safetensors"  # Adds faction-specific details
        ]
        
        # For emblems, use subtle LoRA influence (low strength) to add military character
        for lora in military_enhancement_loras:
            if lora in [item for sublist in lora_categories.values() for item in sublist]:
                selected_lora = lora
                lora_strength = 0.4  # Low strength - enhancement not dominance
                break
                
        if selected_lora:
            workflow["lora_loader"] = {
                "class_type": "LoraLoader",
                "inputs": {
                    "lora_name": selected_lora,
                    "strength_model": lora_strength,
                    "strength_clip": lora_strength,
                    "model": ["checkpoint", 0],
                    "clip": ["checkpoint", 1]
                }
            }
            # Update references to use LoRA-enhanced model/clip
            workflow["positive_clip"]["inputs"]["clip"] = ["lora_loader", 1]
            workflow["negative_clip"]["inputs"]["clip"] = ["lora_loader", 1]
            workflow["ksampler_initial"]["inputs"]["model"] = ["lora_loader", 0]
            
        return workflow
    
    def build_poster_workflow(self, faction: Faction, poster_theme: str, seed: int = None) -> Dict[str, Any]:
        """Build workflow for propaganda poster generation"""
        
        if seed is None:
            seed = abs(hash(f"{faction.code}_{poster_theme}")) % 1000000
            
        positive_prompt = self._build_poster_prompt(faction, poster_theme)
        negative_prompt = "low quality, blurry, amateur, ugly, distorted, malformed"
        
        workflow = {
            "checkpoint": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": self.model}
            },
            
            "positive_clip": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": positive_prompt,
                    "clip": ["checkpoint", 1]
                }
            },
            
            "negative_clip": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["checkpoint", 1]
                }
            },
            
            "latent": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": 1536,  # 3:4 ratio for posters
                    "height": 2048,
                    "batch_size": 1
                }
            },
            
            "ksampler": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": 40,
                    "cfg": 9.0,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1.0,
                    "model": ["checkpoint", 0],
                    "positive": ["positive_clip", 0],
                    "negative": ["negative_clip", 0],
                    "latent_image": ["latent", 0]
                }
            },
            
            "vae_decode": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["ksampler", 0],
                    "vae": ["checkpoint", 2]
                }
            },
            
            "save_poster": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["vae_decode", 0],
                    "filename_prefix": f"TG_Poster_{faction.code}_{poster_theme}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            }
        }
        
        return workflow
    
    def build_icon_workflow(self, icon_name: str, size: int = 512, seed: int = None) -> Dict[str, Any]:
        """Build workflow for UI icon generation with semantic accuracy"""
        
        if seed is None:
            seed = abs(hash(icon_name)) % 1000000
            
        # Extract base icon type from filename
        icon_type = None
        for key in self.icon_prompts.keys():
            if key in icon_name:
                icon_type = key
                break
                
        if icon_type:
            icon_prompt = self.icon_prompts[icon_type]
        else:
            # Fallback to generic Terminal Grounds icon
            icon_prompt = "Terminal Grounds UI icon, clean vector design, high contrast"
            
        positive_prompt = f"{icon_prompt}, game UI element, HUD icon, minimalist design, professional vector art, {size}x{size} resolution, transparent background suitable, high contrast silhouette"
        negative_prompt = "text, letters, words, watermark, photo, 3d render, blurry, low quality, complex background, cluttered"
        
        workflow = {
            "checkpoint": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": self.model}
            },
            
            "positive_clip": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": positive_prompt,
                    "clip": ["checkpoint", 1]
                }
            },
            
            "negative_clip": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["checkpoint", 1]
                }
            },
            
            "latent": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": size,
                    "height": size,
                    "batch_size": 1
                }
            },
            
            "ksampler": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": 25,  # Good balance for icons
                    "cfg": 7.5,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["checkpoint", 0],
                    "positive": ["positive_clip", 0],
                    "negative": ["negative_clip", 0],
                    "latent_image": ["latent", 0]
                }
            },
            
            "vae_decode": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["ksampler", 0],
                    "vae": ["checkpoint", 2]
                }
            },
            
            "save_icon": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["vae_decode", 0],
                    "filename_prefix": f"TG_Icon_{icon_name}_{size}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            }
        }
        
        return workflow
        
    def build_style_aware_workflow(self, asset_type: str, faction: Faction, style_name: str, seed: int = None) -> Dict[str, Any]:
        """Build workflow with specific art style from Style_Staging folder"""
        
        if seed is None:
            seed = abs(hash(f"{faction.code}_{style_name}_{asset_type}")) % 1000000
            
        style_prompt = self.art_styles.get(style_name, "")
        
        if asset_type == "faction_emblem":
            base_prompt = self._build_emblem_prompt(faction)
            enhanced_prompt = f"{base_prompt}, {style_prompt}, Style_Staging {style_name} aesthetic"
            size = (2048, 2048)
            steps = 35
            cfg = 8.5
        elif asset_type == "weapon_concept":
            base_prompt = f"Terminal Grounds {faction.name} weapon concept, futuristic military firearm design"
            enhanced_prompt = f"{base_prompt}, {style_prompt}, detailed weapon design, technical illustration"
            size = (1920, 1080)
            steps = 40
            cfg = 8.0
        elif asset_type == "soldier_portrait":
            base_prompt = f"Terminal Grounds {faction.name} soldier portrait, military character design"
            enhanced_prompt = f"{base_prompt}, {style_prompt}, detailed character art, professional military portrait"
            size = (1024, 1536)
            steps = 35
            cfg = 7.5
        else:
            # Generic fallback
            base_prompt = f"Terminal Grounds {asset_type} for {faction.name}"
            enhanced_prompt = f"{base_prompt}, {style_prompt}"
            size = (1024, 1024)
            steps = 30
            cfg = 7.5
            
        negative_prompt = "low quality, blurry, amateur, text, watermark, ui elements, wrong colors"
        
        # Strategic LoRA usage based on asset type
        lora_categories = self.loras
        selected_lora = None
        lora_strength = 0.7
        
        # Asset-specific LoRA selection for maximum impact
        if asset_type == "faction_emblem":
            # Light military enhancement for emblems
            candidates = ["2042 - battlefield 2042 style v1.safetensors", "Future_Warfare_SDXL.safetensors"]
            lora_strength = 0.3  # Very subtle
            
        elif asset_type == "weapon_concept":
            # Strong weapon-specific LoRAs for realistic firearms
            candidates = ["LAFC_PRO_GUNS_V3.safetensors", "gun style v1.safetensors", "AK-47.safetensors", "Future_Warfare_SDXL.safetensors"]
            lora_strength = 0.8  # Strong for technical accuracy
            
        elif asset_type == "soldier_portrait":
            # Military gear and armor LoRAs
            candidates = ["0300 Individual soldier exoskeleton armor suit_v1.safetensors", "Faction_Soldier-000008.safetensors", "2042 - battlefield 2042 style v1.safetensors"]
            lora_strength = 0.7
            
        elif asset_type == "environment_scene":
            # Sci-fi environment LoRAs
            candidates = ["Mass_Effect_3_Environment-000003.safetensors", "SCIFI_Concept_Art_Landscapes.safetensors", "scifi_buildings_sdxl_lora.safetensors"]
            lora_strength = 0.6
            
        elif asset_type == "vehicle_design":
            # Vehicle and tech LoRAs
            candidates = ["Futuristic_Cars_v2.5_flux.safetensors", "MAN_SV_HX60_Military_Truck.safetensors", "Future_Warfare_SDXL.safetensors"]
            lora_strength = 0.7
            
        else:
            # Default sci-fi enhancement
            candidates = ["Enhanced_Lighting_and_Textures_flux_lora.safetensors", "Future_Warfare_SDXL.safetensors"]
            lora_strength = 0.5
        
        # Find first available LoRA from candidates
        all_loras = [item for sublist in lora_categories.values() for item in sublist]
        for candidate in candidates:
            if candidate in all_loras:
                selected_lora = candidate
                break
            
        workflow = {
            "checkpoint": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": self.model}
            }
        }
        
        # Add LoRA if selected
        current_model = ["checkpoint", 0]
        current_clip = ["checkpoint", 1]
        
        if selected_lora:
            workflow["lora_loader"] = {
                "class_type": "LoraLoader",
                "inputs": {
                    "lora_name": selected_lora,
                    "strength_model": lora_strength,
                    "strength_clip": lora_strength,
                    "model": ["checkpoint", 0],
                    "clip": ["checkpoint", 1]
                }
            }
            current_model = ["lora_loader", 0]
            current_clip = ["lora_loader", 1]
            
        workflow.update({
            "positive_clip": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": enhanced_prompt,
                    "clip": current_clip
                }
            },
            
            "negative_clip": {
                "class_type": "CLIPTextEncode", 
                "inputs": {
                    "text": negative_prompt,
                    "clip": current_clip
                }
            },
            
            "latent": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": size[0],
                    "height": size[1],
                    "batch_size": 1
                }
            },
            
            "ksampler": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1.0,
                    "model": current_model,
                    "positive": ["positive_clip", 0],
                    "negative": ["negative_clip", 0],
                    "latent_image": ["latent", 0]
                }
            },
            
            "vae_decode": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["ksampler", 0],
                    "vae": ["checkpoint", 2]
                }
            },
            
            "save_asset": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["vae_decode", 0],
                    "filename_prefix": f"TG_{style_name}_{asset_type}_{faction.code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            }
        })
        
        return workflow
    
    def _build_emblem_prompt(self, faction: Faction) -> str:
        """Build sophisticated prompt for emblem generation"""
        
        base_style = "military faction emblem, game asset, iconic symbol, high contrast, centered composition"
        faction_specific = faction.emblem_desc
        color_scheme = f"{faction.color_primary} and {faction.color_secondary} color scheme"
        style_tags = ", ".join(faction.style_tags)
        
        quality_boost = "professional design, vector style, clean lines, scalable, production ready"
        technical = "white background, no text, symmetrical when appropriate, bold silhouette"
        
        return f"{faction_specific}, {base_style}, {color_scheme}, {style_tags}, {quality_boost}, {technical}"
    
    def _build_poster_prompt(self, faction: Faction, theme: str) -> str:
        """Build prompt for propaganda poster"""
        
        themes = {
            "recruitment": "recruitment poster, join us, heroic pose, inspiring",
            "victory": "victory celebration, triumphant, flags waving, soldiers cheering",
            "warning": "warning poster, danger ahead, caution, dramatic lighting",
            "unity": "unity and strength, together we stand, formation, solidarity"
        }
        
        theme_prompt = themes.get(theme, "propaganda poster")
        
        style = "propaganda poster style, bold graphics, dramatic composition, vintage military poster aesthetic"
        faction_style = f"{faction.name} faction aesthetic, {', '.join(faction.style_tags)}"
        colors = f"dominant {faction.color_primary} and {faction.color_secondary} colors"
        
        quality = "high quality, detailed, professional illustration, game art"
        
        return f"{theme_prompt}, {faction_style}, {style}, {colors}, Terminal Grounds universe, post-apocalyptic sci-fi, {quality}"

class OutputWatcher:
    """
    Watches ComfyUI output folder and organizes assets for review.
    Provides real-time feedback on generation progress.
    """
    
    def __init__(self, comfyui_output: Path, project_root: Path):
        self.comfyui_output = comfyui_output
        self.project_root = project_root
        self.review_dir = project_root / "Tools" / "ArtGen" / "outputs" / "review"
        self.approved_dir = project_root / "Tools" / "ArtGen" / "outputs" / "approved"
        self.watching = False
        self.file_queue = queue.Queue()
        
        # Create directories
        self.review_dir.mkdir(parents=True, exist_ok=True)
        self.approved_dir.mkdir(parents=True, exist_ok=True)
        
    def start_watching(self):
        """Start watching for new files"""
        self.watching = True
        watcher_thread = threading.Thread(target=self._watch_loop, daemon=True)
        watcher_thread.start()
        
    def stop_watching(self):
        """Stop watching"""
        self.watching = False
        
    def _watch_loop(self):
        """Main watching loop"""
        known_files = set(os.listdir(self.comfyui_output)) if self.comfyui_output.exists() else set()
        
        while self.watching:
            try:
                current_files = set(os.listdir(self.comfyui_output))
                new_files = current_files - known_files
                
                for filename in new_files:
                    if filename.startswith("TG_") and filename.endswith(".png"):
                        filepath = self.comfyui_output / filename
                        self.file_queue.put(filepath)
                        print(f"  [PHOTO] New asset detected: {filename}")
                        self._process_new_file(filepath)
                        
                known_files = current_files
                
            except Exception as e:
                print(f"  [WARNING] Watch error: {e}")
                
            time.sleep(1)
            
    def _process_new_file(self, filepath: Path):
        """Process newly generated file"""
        filename = filepath.name
        
        # Determine asset type from filename
        if "Emblem" in filename:
            asset_type = AssetType.EMBLEM
            subfolder = "Emblems"
        elif "Poster" in filename:
            asset_type = AssetType.POSTER
            subfolder = "Posters"
        elif "Icon" in filename:
            asset_type = AssetType.ICON
            subfolder = "Icons"
        else:
            asset_type = AssetType.DECAL
            subfolder = "Misc"
            
        # Copy to review folder
        review_path = self.review_dir / subfolder
        review_path.mkdir(exist_ok=True)
        
        dest_path = review_path / filename
        shutil.copy2(filepath, dest_path)
        
        print(f"  [SUCCESS] Copied to review: {subfolder}/{filename}")
        
        # Generate review HTML
        self._update_review_html()
        
    def _update_review_html(self):
        """Generate HTML for reviewing assets"""
        
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Terminal Grounds - Asset Review</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
        }
        h1 {
            color: #00ff00;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .category {
            margin: 30px 0;
            border-left: 3px solid #00ff00;
            padding-left: 20px;
        }
        .assets {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .asset {
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 10px;
            transition: transform 0.2s;
        }
        .asset:hover {
            transform: scale(1.05);
            border-color: #00ff00;
        }
        .asset img {
            width: 100%;
            height: 200px;
            object-fit: contain;
            background: #000;
            border-radius: 4px;
        }
        .asset-name {
            margin-top: 10px;
            font-size: 12px;
            color: #aaa;
            word-break: break-all;
        }
        .asset-actions {
            margin-top: 10px;
            display: flex;
            gap: 10px;
        }
        button {
            flex: 1;
            padding: 5px;
            border: 1px solid #00ff00;
            background: transparent;
            color: #00ff00;
            cursor: pointer;
            transition: all 0.2s;
        }
        button:hover {
            background: #00ff00;
            color: #000;
        }
        .stats {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
    </style>
</head>
<body>
    <h1>Terminal Grounds - Asset Review Dashboard</h1>
    
    <div class="stats">
        <strong>Generation Statistics:</strong><br>
        Generated: {total_count} assets<br>
        Review Pending: {review_count}<br>
        Approved: {approved_count}<br>
        Last Update: {timestamp}
    </div>
"""
        
        # Count assets
        total_count = 0
        review_count = 0
        approved_count = len(list(self.approved_dir.glob("**/*.png")))
        
        # Add each category
        for subfolder in ["Emblems", "Posters", "Icons", "Misc"]:
            folder_path = self.review_dir / subfolder
            if folder_path.exists():
                assets = list(folder_path.glob("*.png"))
                review_count += len(assets)
                total_count += len(assets)
                
                if assets:
                    html_content += f"""
    <div class="category">
        <h2>{subfolder}</h2>
        <div class="assets">
"""
                    for asset in assets:
                        rel_path = asset.relative_to(self.review_dir)
                        html_content += f"""
            <div class="asset">
                <img src="{rel_path.as_posix()}" alt="{asset.name}">
                <div class="asset-name">{asset.name}</div>
                <div class="asset-actions">
                    <button onclick="approve('{rel_path.as_posix()}')">Approve</button>
                    <button onclick="reject('{rel_path.as_posix()}')">Reject</button>
                </div>
            </div>
"""
                    html_content += """
        </div>
    </div>
"""
        
        # Add JavaScript for actions
        html_content += """
    <script>
        function approve(path) {
            // This would need a backend to actually move files
            alert('Approved: ' + path + '\\n(Backend integration needed)');
        }
        
        function reject(path) {
            if(confirm('Delete ' + path + '?')) {
                alert('Rejected: ' + path + '\\n(Backend integration needed)');
            }
        }
    </script>
</body>
</html>
"""
        
        # Format template
        html_content = html_content.format(
            total_count=total_count + approved_count,
            review_count=review_count,
            approved_count=approved_count,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Save HTML
        html_path = self.review_dir / "review_dashboard.html"
        html_path.write_text(html_content)
        
        print(f"  [CHART] Review dashboard updated: {html_path}")

class TerminalGroundsAssetPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self):
        self.workflow_builder = TerminalGroundsWorkflowBuilder()
        self.output_watcher = OutputWatcher(COMFYUI_OUTPUT, PROJECT_ROOT)
        self.comfyui_server = COMFYUI_SERVER
        
        # Define factions with lore-accurate descriptions
        self.factions = [
            Faction(
                code="DIR",
                name="Directorate", 
                color_primary="#2E4053",  # Military blue-gray
                color_secondary="#9FB2C9",  # Light tactical blue
                style_tags=["brutalist efficiency", "stark geometry", "military stencil", "negative space", "command authority"],
                emblem_desc="chevron insignia with gridlines and command numerals, brutalist military aesthetic, matte ceramic finish, stark geometric design representing Shattered Accord remnants"
            ),
            Faction(
                code="VLT",
                name="Vultures Union",
                color_primary="#D35400",  # Rust orange
                color_secondary="#F0C27B",  # Weathered metal
                style_tags=["salvage symbols", "hazard warnings", "industrial stencils", "corroded metal", "makeshift reliability"],
                emblem_desc="scavenger bird skull with salvage tools, hazard warning aesthetic, corroded metal texture, welded plates, function over form design philosophy"
            ),
            Faction(
                code="F77",
                name="Free 77",
                color_primary="#34495E",  # Dark tactical
                color_secondary="#BDC3C7",  # Professional silver
                style_tags=["contract seals", "77 numerals", "mercenary badges", "professional military", "corporate hybrid"],
                emblem_desc="stenciled number 77 with bullet holes, professional military contractor aesthetic, tactical fabric textures, modular armor design elements"
            ),
            Faction(
                code="CCB",
                name="Corporate Combine",
                color_primary="#00C2FF",  # Corporate cyan
                color_secondary="#C0F3FF",  # Light ceramic blue
                style_tags=["hexagonal shields", "ceramic patterns", "security badges", "cutting-edge tech", "geometric precision"],
                emblem_desc="hexagonal shield with ceramic patterns, corporate security badge, high-tech ceramic finish, reactive armor aesthetic, smart glass elements"
            ),
            Faction(
                code="NMD", 
                name="Nomad Clans",
                color_primary="#AF601A",  # Desert rust
                color_secondary="#EAC086",  # Weathered tan
                style_tags=["vehicle parts", "tribal glyphs", "road symbols", "convoy culture", "hand-painted warrior"],
                emblem_desc="tribal wheel hub with convoy symbols, weathered metal with leather accents, desert-worn fabric textures, mobile survival aesthetic"
            ),
            Faction(
                code="VAC",
                name="Vaulted Archivists",
                color_primary="#8E44AD",  # Mystic purple
                color_secondary="#BBA1E1",  # Ancient tech glow
                style_tags=["eye-over-coil", "arcane symbols", "data streams", "mystical technology", "esoteric geometric"],
                emblem_desc="all-seeing eye within electromagnetic coil, arcane data stream patterns, ancient alloy finish, crystalline tech integration, knowledge preservation motifs"
            ),
            Faction(
                code="CWD",
                name="Civic Wardens",
                color_primary="#27AE60",  # Community green
                color_secondary="#A9DFBF",  # Safety light green
                style_tags=["mesh barriers", "sandbags", "civil defense", "community protection", "urban militia"],
                emblem_desc="fortress wall with mesh barriers, civil defense symbols, concrete and chain link textures, makeshift protection aesthetic, urban militia stencil"
            )
        ]
        
    def check_comfyui_server(self) -> bool:
        """Check if ComfyUI is running"""
        try:
            response = urllib.request.urlopen(f"http://{self.comfyui_server}/system_stats")
            return response.status == 200
        except:
            return False
            
    def queue_workflow(self, workflow: Dict[str, Any]) -> str:
        """Queue a workflow to ComfyUI"""
        data = json.dumps({"prompt": workflow}).encode('utf-8')
        req = urllib.request.Request(
            f"http://{self.comfyui_server}/prompt",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read())
                return result.get('prompt_id', '')
        except Exception as e:
            print(f"[ERROR] Error queueing workflow: {e}")
            return ""
            
    def generate_all_emblems(self):
        """Generate emblems for all factions"""
        print("\n" + "="*60)
        print("GENERATING FACTION EMBLEMS")
        print("="*60)
        
        for faction in self.factions:
            print(f"\n[ART] Generating emblem for {faction.name} ({faction.code})...")
            
            workflow = self.workflow_builder.build_emblem_workflow(faction)
            prompt_id = self.queue_workflow(workflow)
            
            if prompt_id:
                print(f"  [SUCCESS] Queued with ID: {prompt_id}")
                print(f"  ⏳ Generating (this takes 30-60 seconds)...")
                time.sleep(2)  # Small delay between submissions
            else:
                print(f"  [ERROR] Failed to queue")
                
    def generate_all_posters(self):
        """Generate propaganda posters for all factions"""
        print("\n" + "="*60)
        print("GENERATING PROPAGANDA POSTERS")
        print("="*60)
        
        themes = ["recruitment", "victory", "warning", "unity"]
        
        for faction in self.factions:
            for theme in themes:
                print(f"\n[ART] Generating {theme} poster for {faction.name}...")
                
                workflow = self.workflow_builder.build_poster_workflow(faction, theme)
                prompt_id = self.queue_workflow(workflow)
                
                if prompt_id:
                    print(f"  [SUCCESS] Queued with ID: {prompt_id}")
                    time.sleep(2)
                else:
                    print(f"  [ERROR] Failed to queue")
                    
    def generate_all_icons(self):
        """Generate all UI icons from placeholder report"""
        print("\n" + "="*60)
        print("GENERATING UI ICONS")
        print("="*60)
        
        # Icons from the placeholder report
        icons_to_generate = [
            ("damage_ballistic", 512),
            ("damage_ballistic", 1024),
            ("damage_ion", 512), 
            ("damage_ion", 1024),
            ("extract", 512),
            ("extract", 1024),
            ("map_ping", 512),
            ("map_ping", 1024),
            ("rarity_common", 512),
            ("rarity_common", 1024),
            ("rarity_legendary", 512),
            ("rarity_legendary", 1024),
            ("status_charge", 512),
            ("status_charge", 1024),
            ("status_heat", 512),
            ("status_heat", 1024)
        ]
        
        for icon_name, size in icons_to_generate:
            print(f"\n[ART] Generating {icon_name} icon ({size}x{size})...")
            
            workflow = self.workflow_builder.build_icon_workflow(icon_name, size)
            prompt_id = self.queue_workflow(workflow)
            
            if prompt_id:
                print(f"  [SUCCESS] Queued with ID: {prompt_id}")
                time.sleep(1)  # Small delay between submissions
            else:
                print(f"  [ERROR] Failed to queue")
                
    def generate_placeholder_batch(self):
        """Generate all assets from the placeholder report using FLUX-dev"""
        print("\n" + "="*60)
        print("GENERATING PLACEHOLDER BATCH (FLUX-DEV)")
        print("="*60)
        
        # Read the batch plan but override with better settings
        batch_path = PROJECT_ROOT / "Tools" / "ArtGen" / "outputs" / "batch_from_report.plan.json"
        if not batch_path.exists():
            print("[ERROR] Batch plan not found")
            return
            
        with open(batch_path) as f:
            batch_data = json.load(f)
            
        print(f"[INFO] Processing {len(batch_data['items'])} items...")
        
        for i, item in enumerate(batch_data['items']):
            category = item['category']
            target = item['target']
            base_prompt = item['prompt']
            
            print(f"\n[ART] [{i+1}/{len(batch_data['items'])}] Generating {target}...")
            
            # Determine asset type and use appropriate workflow
            if category == "ui-icon":
                # Extract icon name from target path
                icon_name = Path(target).stem.replace("_128", "").replace("_64", "")
                size = 1024  # Generate at high res, can downscale later
                workflow = self.workflow_builder.build_icon_workflow(icon_name, size)
            elif category == "concept":
                # Use emblem workflow for concept art with enhanced prompts
                workflow = self._build_concept_workflow(target, base_prompt)
            else:
                continue  # Skip unknown categories
                
            prompt_id = self.queue_workflow(workflow)
            
            if prompt_id:
                print(f"  [SUCCESS] Queued with ID: {prompt_id}")
                time.sleep(2)  # Delay to avoid overwhelming ComfyUI
            else:
                print(f"  [ERROR] Failed to queue")
                
    def _build_concept_workflow(self, target: str, base_prompt: str) -> Dict[str, Any]:
        """Build workflow for concept art generation"""
        
        # Enhanced prompt for concept art
        enhanced_prompt = f"{base_prompt}, Terminal Grounds universe, post-apocalyptic sci-fi, detailed concept art, professional game art, high quality illustration"
        negative_prompt = "text, watermark, logo, UI elements, low quality, blurry, amateur"
        
        seed = abs(hash(target)) % 1000000
        
        workflow = {
            "checkpoint": {
                "class_type": "CheckpointLoaderSimple", 
                "inputs": {"ckpt_name": self.workflow_builder.model}
            },
            
            "positive_clip": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": enhanced_prompt,
                    "clip": ["checkpoint", 1]
                }
            },
            
            "negative_clip": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["checkpoint", 1]
                }
            },
            
            "latent": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": 1024,
                    "height": 1024, 
                    "batch_size": 1
                }
            },
            
            "ksampler": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": 30,  # FLUX-dev quality instead of schnell
                    "cfg": 8.0,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1.0,
                    "model": ["checkpoint", 0],
                    "positive": ["positive_clip", 0],
                    "negative": ["negative_clip", 0],
                    "latent_image": ["latent", 0]
                }
            },
            
            "vae_decode": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["ksampler", 0],
                    "vae": ["checkpoint", 2]
                }
            },
            
            "save_concept": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["vae_decode", 0],
                    "filename_prefix": f"TG_Concept_{Path(target).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            }
        }
        
        return workflow
                    
    def run_interactive(self):
        """Run interactive generation session with monitoring"""
        
        print("""
================================================================
     TERMINAL GROUNDS - ADVANCED ASSET GENERATOR         
================================================================
        """)
        
        # Check server
        print("Checking ComfyUI server...", end=" ")
        if not self.check_comfyui_server():
            print("NOT RUNNING!")
            print("\nPlease start ComfyUI in API mode:")
            print("   Run: C:\\ComfyUI\\run_comfyui_api.bat")
            return
        print("Connected!")
        
        # Start output watcher
        print("Starting output watcher...")
        self.output_watcher.start_watching()
        print("Watcher active!")
        
        while True:
            print("""
================================================================
                  STAGING PIPELINE MENU                  
================================================================
  1. Generate Concept Variations (Emblems)               
  2. Generate Concept Variations (Posters)               
  3. Generate UI Icon Concepts                           
  4. Generate Weapon Concepts (Uses Weapon LoRAs)        
  5. Generate Soldier Portraits (Uses Military LoRAs)    
  6. Generate Environment Concepts (Uses Sci-Fi LoRAs)   
  7. Generate All Placeholder Assets (Batch)             
  8. Open Review Dashboard                               
  9. Approve/Reject Assets (Interactive)                 
  10. Export Approved to Final Locations                 
  11. Exit                                               
================================================================
            """)
            
            choice = input("Select option (1-11): ").strip()
            
            if choice == "1":
                self._generate_emblem_concepts()
                
            elif choice == "2":
                self._generate_poster_concepts()
                
            elif choice == "3":
                self.generate_all_icons()
                
            elif choice == "4":
                self.generate_weapon_concepts()
                
            elif choice == "5":
                self.generate_soldier_portraits()
                
            elif choice == "6":
                self.generate_environment_concepts()
                
            elif choice == "7":
                self.generate_placeholder_batch()
                
            elif choice == "8":
                dashboard_path = self.output_watcher.review_dir / "review_dashboard.html"
                if dashboard_path.exists():
                    os.startfile(dashboard_path)
                    print("[SUCCESS] Dashboard opened in browser")
                else:
                    print("[WARNING] No dashboard generated yet")
                    
            elif choice == "9":
                self._interactive_approval()
                
            elif choice == "10":
                self._export_approved_assets()
                
            elif choice == "11":
                print("\nStopping watcher...")
                self.output_watcher.stop_watching()
                print("Goodbye!")
                break
                
            else:
                print("[ERROR] Invalid choice")
                
    def _generate_specific_faction(self):
        """Generate assets for a specific faction"""
        print("\nSelect faction:")
        for i, faction in enumerate(self.factions, 1):
            print(f"  {i}. {faction.name} ({faction.code})")
            
        faction_choice = input("Enter number: ").strip()
        
        try:
            faction_idx = int(faction_choice) - 1
            faction = self.factions[faction_idx]
            
            print(f"\nGenerating assets for {faction.name}:")
            print("  1. Emblem only")
            print("  2. Posters only")
            print("  3. Both")
            
            asset_choice = input("Enter choice: ").strip()
            
            if asset_choice in ["1", "3"]:
                workflow = self.workflow_builder.build_emblem_workflow(faction)
                self.queue_workflow(workflow)
                print(f"[SUCCESS] Emblem queued for {faction.name}")
                
            if asset_choice in ["2", "3"]:
                for theme in ["recruitment", "victory"]:
                    workflow = self.workflow_builder.build_poster_workflow(faction, theme)
                    self.queue_workflow(workflow)
                    print(f"[SUCCESS] {theme.capitalize()} poster queued for {faction.name}")
                    
        except (ValueError, IndexError):
            print("ERROR: Invalid selection")
            
    def _generate_emblem_concepts(self):
        """Generate multiple emblem concept variations for each faction"""
        print("\nEMBLEM CONCEPT GENERATION")
        print("Generating 3 variations per faction for comparison...")
        
        for faction in self.factions:
            print(f"\nGenerating concepts for {faction.name}...")
            
            # Generate 3 variations with different seeds and slight prompt variations
            variations = [
                "primary emblem design",
                "alternative emblem concept", 
                "stylized emblem variant"
            ]
            
            for i, variation in enumerate(variations, 1):
                print(f"  Variation {i}: {variation}")
                
                # Create modified faction for variation
                modified_desc = f"{faction.emblem_desc}, {variation}"
                temp_faction = Faction(
                    code=f"{faction.code}_v{i}",
                    name=faction.name,
                    color_primary=faction.color_primary,
                    color_secondary=faction.color_secondary,
                    style_tags=faction.style_tags,
                    emblem_desc=modified_desc
                )
                
                workflow = self.workflow_builder.build_emblem_workflow(temp_faction, seed=1000 + i)
                prompt_id = self.queue_workflow(workflow)
                
                if prompt_id:
                    print(f"    SUCCESS: Queued: {prompt_id}")
                else:
                    print(f"    FAILED")
                    
                time.sleep(2)
                
    def generate_weapon_concepts(self):
        """Generate weapon concepts using your weapon LoRAs for maximum detail"""
        print("\nWEAPON CONCEPT GENERATION")
        print("Using weapon-specific LoRAs for technical accuracy...")
        
        # Terminal Grounds weapon tiers from lore
        weapon_concepts = [
            ("human_assault_rifle", "Human-tier assault rifle, conventional ballistics, tactical rails"),
            ("hybrid_energy_weapon", "Hybrid-tier energy rifle, alien tech integration, glowing conduits"),
            ("alien_graviton_weapon", "Alien-tier graviton manipulator, organic curves, reality-bending effects"),
            ("salvaged_smg", "Vultures Union salvaged SMG, makeshift modifications, welded plates"),
            ("corporate_plasma_rifle", "Corporate Combine plasma rifle, sleek design, smart targeting"),
            ("nomad_desert_carbine", "Nomad Clans desert carbine, weathered survival weapon"),
            ("archivists_void_lance", "Vaulted Archivists void lance, mystical technology, energy coils")
        ]
        
        for weapon_name, description in weapon_concepts:
            print(f"\n[ART] Generating {weapon_name}...")
            
            # Build enhanced prompt with Terminal Grounds lore
            prompt = f"{description}, Terminal Grounds universe, post-apocalyptic sci-fi, detailed weapon concept art, technical illustration, professional game art"
            
            workflow = self.workflow_builder.build_style_aware_workflow(
                "weapon_concept", self.factions[0], "Gritty_Realism", seed=3000 + hash(weapon_name) % 1000
            )
            
            prompt_id = self.queue_workflow(workflow)
            
            if prompt_id:
                print(f"    SUCCESS: Queued: {prompt_id}")
                time.sleep(2)
            else:
                print(f"    FAILED")
                
    def generate_soldier_portraits(self):
        """Generate soldier portraits using military gear LoRAs"""
        print("\nSOLDIER PORTRAIT GENERATION") 
        print("Using exoskeleton and military gear LoRAs...")
        
        for faction in self.factions[:4]:  # First 4 factions for testing
            print(f"\n[ART] Generating {faction.name} soldier...")
            
            workflow = self.workflow_builder.build_style_aware_workflow(
                "soldier_portrait", faction, "Gritty_Realism", seed=4000 + hash(faction.code) % 1000
            )
            
            prompt_id = self.queue_workflow(workflow)
            
            if prompt_id:
                print(f"    SUCCESS: Queued: {prompt_id}")
                time.sleep(2)
            else:
                print(f"    FAILED")
                
    def generate_environment_concepts(self):
        """Generate environment concepts using sci-fi landscape LoRAs"""
        print("\nENVIRONMENT CONCEPT GENERATION")
        print("Using Mass Effect and sci-fi environment LoRAs...")
        
        # Terminal Grounds locations from lore
        locations = [
            ("iez_center", "IEZ center with twisted metal and energy anomalies"),
            ("metro_tunnels", "Underground metro tunnels, neutral trading post"),
            ("tech_wastes", "Industrial tech wastes, automated factories"), 
            ("sky_bastion", "Vertical sky bastion platforms, industrial steam"),
            ("harvester_wreck", "Massive alien Harvester wreck site, salvage operation")
        ]
        
        for location_name, description in locations:
            print(f"\n[ART] Generating {location_name}...")
            
            workflow = self.workflow_builder.build_style_aware_workflow(
                "environment_scene", self.factions[0], "Post_Apocalyptic", seed=5000 + hash(location_name) % 1000
            )
            
            prompt_id = self.queue_workflow(workflow)
            
            if prompt_id:
                print(f"    SUCCESS: Queued: {prompt_id}")
                time.sleep(2)
            else:
                print(f"    FAILED")
                
    def _generate_poster_concepts(self):
        """Generate multiple poster concept variations"""
        print("\n[ART] POSTER CONCEPT GENERATION")
        
        # Focus on 2-3 key factions for concept exploration
        key_factions = self.factions[:3]  # First 3 factions
        themes = ["recruitment", "victory"]  # 2 main themes
        
        for faction in key_factions:
            for theme in themes:
                print(f"\n[INFO] {faction.name} - {theme} poster concepts...")
                
                # Generate 2 variations per theme
                for i in range(1, 3):
                    print(f"  [TARGET] Concept variation {i}")
                    
                    workflow = self.workflow_builder.build_poster_workflow(faction, theme, seed=2000 + i)
                    prompt_id = self.queue_workflow(workflow)
                    
                    if prompt_id:
                        print(f"    [SUCCESS] Queued: {prompt_id}")
                    else:
                        print(f"    [ERROR] Failed")
                        
                    time.sleep(2)
                    
    def _interactive_approval(self):
        """Interactive asset approval system"""
        print("\n[SEARCH] INTERACTIVE ASSET APPROVAL")
        
        review_assets = list(self.output_watcher.review_dir.glob("**/*.png"))
        
        if not review_assets:
            print("[WARNING] No assets found in review folder")
            return
            
        print(f"[INFO] Found {len(review_assets)} assets for review")
        
        for asset in review_assets:
            rel_path = asset.relative_to(self.output_watcher.review_dir)
            print(f"\n[PHOTO] Reviewing: {rel_path}")
            print(f"   Path: {asset}")
            
            while True:
                action = input("   Action: [A]pprove, [R]eject, [S]kip, [Q]uit: ").strip().upper()
                
                if action == "A":
                    # Move to approved folder
                    approved_path = self.output_watcher.approved_dir / rel_path
                    approved_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(asset, approved_path)
                    print(f"   [SUCCESS] Approved: {rel_path}")
                    break
                elif action == "R":
                    # Delete the asset
                    asset.unlink()
                    print(f"   [ERROR] Rejected: {rel_path}")
                    break
                elif action == "S":
                    print(f"   [SKIP] Skipped: {rel_path}")
                    break
                elif action == "Q":
                    return
                else:
                    print("   Invalid choice. Use A/R/S/Q")
                    
    def _export_approved_assets(self):
        """Export approved assets to final Unreal Engine locations"""
        print("\n[PACKAGE] EXPORTING APPROVED ASSETS")
        
        approved_assets = list(self.output_watcher.approved_dir.glob("**/*.png"))
        
        if not approved_assets:
            print("[WARNING] No approved assets found")
            return
            
        print(f"[INFO] Exporting {len(approved_assets)} approved assets...")
        
        for asset in approved_assets:
            # Determine target location based on filename
            if "Emblem" in asset.name or "emblem" in asset.name:
                target_dir = TG_ASSETS_ROOT / "Decals" / "Factions"
            elif "Poster" in asset.name or "poster" in asset.name:
                target_dir = TG_ASSETS_ROOT / "Decals" / "Posters"  
            elif "Icon" in asset.name or "icon" in asset.name:
                target_dir = TG_ASSETS_ROOT / "Icons"
            else:
                target_dir = TG_ASSETS_ROOT / "Generated"
                
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy asset to final location
            target_path = target_dir / asset.name
            shutil.copy2(asset, target_path)
            
            print(f"  [FOLDER] {asset.name} → {target_path.relative_to(PROJECT_ROOT)}")
            
        print(f"\n[SUCCESS] Exported {len(approved_assets)} assets to Content/TG/")
            
    def _process_approved_assets(self):
        """Move approved assets to final locations"""
        print("\n[PACKAGE] Processing approved assets...")
        
        # This would move approved assets to Content/TG folders
        # For now, just showing what would happen
        
        approved_count = 0
        for asset_path in self.output_watcher.approved_dir.glob("**/*.png"):
            filename = asset_path.name
            
            if "Emblem" in filename:
                dest = TG_ASSETS_ROOT / "Decals" / "Factions" / filename
            elif "Poster" in filename:
                dest = TG_ASSETS_ROOT / "Decals" / "Posters" / filename
            elif "Icon" in filename:
                dest = TG_ASSETS_ROOT / "Icons" / "UI" / filename
            else:
                dest = TG_ASSETS_ROOT / "Decals" / "Misc" / filename
                
            print(f"  Would move: {filename} -> {dest.relative_to(PROJECT_ROOT)}")
            approved_count += 1
            
        if approved_count == 0:
            print("  No approved assets found")
        else:
            print(f"\n  Total: {approved_count} assets ready to process")

def main():
    """Main entry point"""
    pipeline = TerminalGroundsAssetPipeline()
    pipeline.run_interactive()

if __name__ == "__main__":
    main()
