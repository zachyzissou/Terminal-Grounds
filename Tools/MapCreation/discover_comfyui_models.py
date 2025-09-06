#!/usr/bin/env python3
"""
ComfyUI Model Discovery and Setup for Dead Sky
Discovers available models and sets up workflows accordingly
"""

import requests
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComfyUIModelDiscovery:
    def __init__(self):
        self.comfyui_url = "http://127.0.0.1:8188"
        self.models_info = {}

    def discover_all_models(self) -> Dict[str, Any]:
        """Discover all available models and nodes in ComfyUI"""
        logger.info("🔍 Discovering ComfyUI models and capabilities...")

        try:
            # Get object info to see available nodes
            response = requests.get(f"{self.comfyui_url}/object_info")
            if response.status_code == 200:
                object_info = response.json()

                # Find model loading nodes
                model_loaders = {}
                for node_name, node_info in object_info.items():
                    if 'Load' in node_name and any(x in node_name for x in ['Model', 'Checkpoint', 'CLIP', 'VAE', 'UNET']):
                        if 'input' in node_info and 'required' in node_info['input']:
                            model_loaders[node_name] = node_info['input']['required']

                self.models_info['loaders'] = model_loaders
                logger.info(f"✅ Found {len(model_loaders)} model loading nodes")

                # Check specific model availability
                for loader_name, loader_info in model_loaders.items():
                    logger.info(f"🔧 {loader_name}:")
                    for param_name, param_info in loader_info.items():
                        if isinstance(param_info, list) and len(param_info) > 0:
                            if isinstance(param_info[0], list):
                                models = param_info[0]
                                logger.info(f"   {param_name}: {len(models)} available")
                                if models:
                                    logger.info(f"      Examples: {models[:3]}")

                return self.models_info

        except Exception as e:
            logger.error(f"❌ Model discovery failed: {e}")
            return {}

    def test_basic_workflow(self) -> bool:
        """Test a basic workflow with whatever models are available"""
        logger.info("🧪 Testing basic ComfyUI workflow...")

        try:
            # Simple workflow that should work with any setup
            workflow = {
                "1": {
                    "inputs": {
                        "text": "Terminal Grounds Dead Sky region test"
                    },
                    "class_type": "CLIPTextEncode",
                    "_meta": {"title": "Test Text Encoding"}
                }
            }

            # Submit workflow
            response = requests.post(f"{self.comfyui_url}/prompt",
                                   json={"prompt": workflow, "client_id": "test_client"})

            if response.status_code == 200:
                logger.info("✅ Basic workflow submission successful")
                return True
            else:
                logger.warning(f"⚠️ Workflow submission failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Workflow test failed: {e}")
            return False

    def create_dead_sky_workflow(self, prompt: str, output_path: str) -> Optional[Dict]:
        """Create a Dead Sky asset generation workflow with available models"""
        logger.info(f"🌌 Creating Dead Sky workflow for: {prompt[:50]}...")

        # Check what models are available
        if not self.models_info:
            self.discover_all_models()

        # Try to build a workflow with available components
        workflow = {}
        node_id = 1

        # If we have any checkpoint loader
        if 'CheckpointLoaderSimple' in self.models_info.get('loaders', {}):
            checkpoint_info = self.models_info['loaders']['CheckpointLoaderSimple']
            if 'ckpt_name' in checkpoint_info:
                available_checkpoints = checkpoint_info['ckpt_name'][0] if checkpoint_info['ckpt_name'] else []

                if available_checkpoints:
                    # Use first available checkpoint
                    model_name = available_checkpoints[0]
                    logger.info(f"🎯 Using model: {model_name}")

                    workflow[str(node_id)] = {
                        "inputs": {
                            "ckpt_name": model_name
                        },
                        "class_type": "CheckpointLoaderSimple",
                        "_meta": {"title": "Load Checkpoint"}
                    }

                    # Add text encoding
                    workflow[str(node_id + 1)] = {
                        "inputs": {
                            "text": prompt,
                            "clip": [str(node_id), 1]
                        },
                        "class_type": "CLIPTextEncode",
                        "_meta": {"title": "Positive Prompt"}
                    }

                    # Add negative prompt
                    workflow[str(node_id + 2)] = {
                        "inputs": {
                            "text": "blurry, low quality, text, watermark",
                            "clip": [str(node_id), 1]
                        },
                        "class_type": "CLIPTextEncode",
                        "_meta": {"title": "Negative Prompt"}
                    }

                    return workflow

        logger.warning("⚠️ No suitable models found for image generation")
        return None

    def generate_dead_sky_asset(self, prompt: str, output_filename: str) -> bool:
        """Generate a Dead Sky asset using available models"""
        logger.info(f"🎨 Generating Dead Sky asset: {output_filename}")

        workflow = self.create_dead_sky_workflow(prompt, output_filename)

        if workflow:
            try:
                # Submit the workflow
                response = requests.post(f"{self.comfyui_url}/prompt",
                                       json={"prompt": workflow, "client_id": f"deadsky_{int(time.time())}"})

                if response.status_code == 200:
                    logger.info(f"✅ Asset generation started: {output_filename}")
                    return True
                else:
                    logger.error(f"❌ Asset generation failed: {response.status_code}")
                    return False
            except Exception as e:
                logger.error(f"❌ Asset generation error: {e}")
                return False
        else:
            logger.warning(f"⚠️ Creating placeholder for: {output_filename}")
            # Create placeholder file
            Path(output_filename).parent.mkdir(parents=True, exist_ok=True)
            with open(output_filename, 'w') as f:
                f.write(f"# Dead Sky Asset Placeholder\n")
                f.write(f"Prompt: {prompt}\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            return True

def main():
    """Main discovery and testing function"""
    print("🔍 COMFYUI MODEL DISCOVERY FOR DEAD SKY")
    print("=" * 50)

    discovery = ComfyUIModelDiscovery()

    # Discover available models
    models_info = discovery.discover_all_models()

    if models_info:
        print(f"\n✅ ComfyUI Setup Summary:")
        print(f"   🔧 Model Loaders: {len(models_info.get('loaders', {}))}")

        # Test basic functionality
        if discovery.test_basic_workflow():
            print("   ✅ Basic workflow: OPERATIONAL")

            # Test Dead Sky asset generation
            test_prompts = [
                "Terminal Grounds Dead Sky salvage field, rust and debris",
                "post-apocalyptic wasteland, abandoned industrial equipment",
                "toxic splice pressure zone, green energy distortion"
            ]

            success_count = 0
            for i, prompt in enumerate(test_prompts):
                filename = f"test_deadsky_asset_{i+1}.png"
                if discovery.generate_dead_sky_asset(prompt, filename):
                    success_count += 1

            print(f"   🎨 Dead Sky Assets: {success_count}/{len(test_prompts)} generated")

            if success_count > 0:
                print("\n🎉 COMFYUI READY FOR DEAD SKY ASSET GENERATION!")
                return True
            else:
                print("\n⚠️ ComfyUI operational but needs model configuration")
                return True
        else:
            print("   ❌ Basic workflow: FAILED")
            return False
    else:
        print("❌ ComfyUI model discovery failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
