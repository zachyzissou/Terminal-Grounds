"""
ComfyUI Asset Generator for Terminal Grounds
Processes YAML recipes to generate game assets via ComfyUI
"""
import os
import sys
import json
import yaml
import time
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import argparse
import copy

# Add client to path
sys.path.append(str(Path(__file__).parent.parent / 'client'))
from comfy_client import ComfyClient


class AssetGenerator:
    def __init__(self, comfy_url: str = "http://127.0.0.1:8000", project_root: str = None):
        self.client = ComfyClient(comfy_url)
        self.project_root = Path(project_root or r"C:\Users\Zachg\Terminal-Grounds")
        self.workflow_dir = self.project_root / "Tools" / "Comfy" / "workflows"
        self.manifest_path = self.project_root / "Docs" / "Concepts" / "ASSET_MANIFEST.json"
        self.log_path = self.project_root / "Docs" / "Phase4_Implementation_Log.md"
        
        # Ensure directories exist
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create manifest
        self.manifest = self.load_manifest()
        
        # Base negative prompt
        self.base_negative = "cartoonish, neon cyberpunk excess, watermark, text artifacts, jpeg artifacts, low-res, blurry, oversaturated, anime, manga, illustration style"
        
    def load_manifest(self) -> List[Dict]:
        """Load or create asset manifest"""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        return []
    
    def save_manifest(self):
        """Save asset manifest"""
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def log_generation(self, message: str):
        """Append to implementation log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, 'a') as f:
            f.write(f"\n[{timestamp}] {message}")
        print(f"📝 {message}")
    
    def load_workflow(self, workflow_name: str = "txt2img_base.json") -> Dict:
        """Load workflow template"""
        workflow_path = self.workflow_dir / workflow_name
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")
        
        with open(workflow_path, 'r') as f:
            return json.load(f)
    
    def customize_workflow(self, workflow: Dict, params: Dict) -> Dict:
        """Customize workflow with generation parameters"""
        wf = copy.deepcopy(workflow)
        
        # Update checkpoint model
        if "model" in params and "3" in wf:
            wf["3"]["inputs"]["ckpt_name"] = params["model"]
        
        # Update prompts
        if "4" in wf:  # Positive prompt
            wf["4"]["inputs"]["text"] = params.get("prompt", "")
        
        if "5" in wf:  # Negative prompt
            negative = params.get("negative", self.base_negative)
            wf["5"]["inputs"]["text"] = f"{negative}, {self.base_negative}"
        
        # Update latent image size
        if "6" in wf:
            wf["6"]["inputs"]["width"] = params.get("width", 1024)
            wf["6"]["inputs"]["height"] = params.get("height", 1024)
        
        # Update sampler settings
        if "7" in wf:
            wf["7"]["inputs"]["seed"] = params.get("seed", int(time.time()))
            wf["7"]["inputs"]["steps"] = params.get("steps", 30)
            wf["7"]["inputs"]["cfg"] = params.get("cfg", 7.0)
            wf["7"]["inputs"]["sampler_name"] = params.get("sampler", "euler_ancestral")
        
        # Update output prefix
        if "9" in wf:
            prefix = params.get("name_base", "TG_output")
            wf["9"]["inputs"]["filename_prefix"] = prefix
        
        return wf
    
    def generate_single(self, params: Dict, retry_count: int = 3) -> Optional[Dict]:
        """Generate a single asset with retry logic"""
        for attempt in range(retry_count):
            try:
                # Adjust parameters for retry
                if attempt > 0:
                    params = self.adjust_params_for_retry(params, attempt)
                    print(f"  Retry {attempt} with adjusted params")
                
                # Prepare workflow
                workflow = self.load_workflow()
                workflow = self.customize_workflow(workflow, params)
                
                # Queue the prompt
                result = self.client.queue_prompt(workflow)
                if not result:
                    print(f"  Failed to queue prompt")
                    continue
                
                prompt_id = result.get("prompt_id")
                print(f"  Queued: {prompt_id}")
                
                # Wait for completion
                history = self.client.wait_for_result(prompt_id, timeout=300)
                if not history:
                    print(f"  Generation failed or timed out")
                    continue
                
                # Get output images
                outputs = history.get("outputs", {})
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        for img_info in node_output["images"]:
                            filename = img_info["filename"]
                            subfolder = img_info.get("subfolder", "")
                            
                            # Download the image
                            img_data = self.client.get_image(filename, subfolder)
                            if img_data:
                                return {
                                    "filename": filename,
                                    "data": img_data,
                                    "params": params,
                                    "attempt": attempt + 1
                                }
                
            except Exception as e:
                print(f"  Error on attempt {attempt + 1}: {e}")
        
        return None
    
    def adjust_params_for_retry(self, params: Dict, attempt: int) -> Dict:
        """Adjust generation parameters for retry"""
        adjusted = params.copy()
        
        # Progressive adjustments
        if attempt == 1:
            adjusted["steps"] = min(adjusted.get("steps", 30) + 8, 50)
            adjusted["cfg"] = min(adjusted.get("cfg", 7.0) + 0.5, 9.0)
            # Add quality terms to prompt
            adjusted["prompt"] = f"{params.get('prompt', '')}, high quality, detailed, sharp focus"
        elif attempt == 2:
            adjusted["steps"] = min(adjusted.get("steps", 30) + 14, 60)
            adjusted["cfg"] = min(adjusted.get("cfg", 7.0) + 1.0, 10.0)
            adjusted["seed"] = params.get("seed", 0) + 1000
            # Add more specific terms
            adjusted["prompt"] = f"{params.get('prompt', '')}, ultra detailed, professional, octane render, 8k"
        
        return adjusted
    
    def save_asset(self, asset_data: Dict, output_dir: Path, base_name: str) -> Path:
        """Save generated asset with metadata"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find next available version number
        version = 1
        while True:
            filename = f"{base_name}_v{version:03d}.png"
            filepath = output_dir / filename
            if not filepath.exists():
                break
            version += 1
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(asset_data["data"])
        
        # Save metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "params": asset_data["params"],
            "attempt": asset_data.get("attempt", 1),
            "source_file": asset_data.get("filename", ""),
            "file_path": str(filepath.relative_to(self.project_root))
        }
        
        metadata_path = filepath.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update manifest
        self.manifest.append({
            "id": hashlib.md5(str(filepath).encode()).hexdigest()[:8],
            "path": str(filepath.relative_to(self.project_root)),
            "category": asset_data["params"].get("category", "general"),
            "created": datetime.now().isoformat(),
            "params": asset_data["params"]
        })
        
        return filepath
    
    def process_batch(self, batch: Dict) -> List[Path]:
        """Process a batch of assets"""
        generated = []
        
        category = batch.get("category", "general")
        count = batch.get("count", 1)
        out_dir = Path(batch.get("out_dir", "Tools/ArtGen/outputs"))
        if not out_dir.is_absolute():
            out_dir = self.project_root / out_dir
        
        print(f"\n🎨 Generating {category}: {count} variants")
        
        for i in range(count):
            # Prepare parameters
            params = batch.copy()
            params["seed"] = batch.get("seed", int(time.time())) + i * 1000
            
            print(f"  [{i+1}/{count}] Generating...")
            
            # Generate asset
            result = self.generate_single(params)
            
            if result:
                # Save asset
                base_name = batch.get("name_base", f"{category}_{batch.get('faction', 'general')}")
                filepath = self.save_asset(result, out_dir, base_name)
                generated.append(filepath)
                print(f"  ✅ Saved: {filepath.name}")
            else:
                print(f"  ❌ Failed to generate after retries")
        
        return generated
    
    def load_recipe(self, recipe_path: str) -> Dict:
        """Load YAML recipe file"""
        path = Path(recipe_path)
        if not path.exists():
            raise FileNotFoundError(f"Recipe not found: {recipe_path}")
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def process_recipe(self, recipe_path: str, import_ue: bool = False):
        """Process entire recipe file"""
        recipe = self.load_recipe(recipe_path)
        
        print(f"\n🚀 Processing recipe: {Path(recipe_path).name}")
        print(f"📦 Batches: {len(recipe.get('batches', []))}")
        
        # Test connection
        if not self.client.test_connection():
            print("\n❌ ComfyUI server not reachable at", self.client.base)
            print("Writing stub entries for all batches...")
            self.create_stub_entries(recipe)
            return
        
        all_generated = []
        
        # Process each batch
        for i, batch in enumerate(recipe.get("batches", [])):
            print(f"\n━━━ Batch {i+1}/{len(recipe['batches'])} ━━━")
            generated = self.process_batch(batch)
            all_generated.extend(generated)
            
            # Log progress
            self.log_generation(f"Generated {len(generated)} assets for {batch.get('category', 'unknown')}")
        
        # Save manifest
        self.save_manifest()
        
        # Import to UE if requested
        if import_ue and all_generated:
            self.import_to_unreal(all_generated)
        
        print(f"\n✨ Recipe complete! Generated {len(all_generated)} assets")
        print(f"📄 Manifest updated: {self.manifest_path}")
    
    def create_stub_entries(self, recipe: Dict):
        """Create stub entries when ComfyUI is unavailable"""
        for batch in recipe.get("batches", []):
            for i in range(batch.get("count", 1)):
                stub_entry = {
                    "id": hashlib.md5(f"{batch.get('category')}_{i}_{time.time()}".encode()).hexdigest()[:8],
                    "path": f"STUB_{batch.get('category', 'unknown')}_{i}.png",
                    "category": batch.get("category", "general"),
                    "created": datetime.now().isoformat(),
                    "stub": True,
                    "reason": "ComfyUI unavailable"
                }
                self.manifest.append(stub_entry)
        
        self.save_manifest()
        self.log_generation("Created stub entries - ComfyUI unavailable")
    
    def import_to_unreal(self, asset_paths: List[Path]):
        """Trigger Unreal import (placeholder for actual implementation)"""
        print("\n📦 Preparing Unreal import...")
        # This would call the UE import script
        # For now, just log the action
        self.log_generation(f"Ready for UE import: {len(asset_paths)} assets")


def main():
    parser = argparse.ArgumentParser(description='Generate assets via ComfyUI')
    parser.add_argument('--recipe', required=True, help='Path to YAML recipe file')
    parser.add_argument('--comfy-url', default='http://127.0.0.1:8000',
                      help='ComfyUI server URL')
    parser.add_argument('--project-root', default=r'C:\Users\Zachg\Terminal-Grounds',
                      help='Project root directory')
    parser.add_argument('--import-ue', action='store_true',
                      help='Import generated assets to Unreal Engine')
    
    args = parser.parse_args()
    
    generator = AssetGenerator(args.comfy_url, args.project_root)
    generator.process_recipe(args.recipe, args.import_ue)


if __name__ == '__main__':
    # If run without args, show usage
    if len(sys.argv) == 1:
        print("Terminal Grounds Asset Generator")
        print("Usage: python generate.py --recipe <recipe.yml> [--import-ue]")
        print("\nTesting connection to ComfyUI...")
        
        gen = AssetGenerator()
        if gen.client.test_connection():
            print("✅ ComfyUI is running")
        else:
            print("❌ ComfyUI not found at http://127.0.0.1:8000")
    else:
        main()
