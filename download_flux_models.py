#!/usr/bin/env python3
"""
FLUX Model Downloader for Terminal Grounds
Downloads required text encoders and VAE models for ComfyUI FLUX workflow
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Tuple
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FLUXModelDownloader:
    """Downloads required FLUX models for ComfyUI"""

    def __init__(self):
        self.comfyui_models_path = Path("Tools/Comfy/ComfyUI/models")
        self.text_encoders_path = self.comfyui_models_path / "text_encoders"
        self.vae_path = self.comfyui_models_path / "vae"

        # Required models from official FLUX.1-dev repository
        self.required_models = {
            "text_encoders": [
                {
                    "name": "clip_l.safetensors",
                    "url": "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/text_encoder/model.safetensors",
                    "size_gb": 0.235,
                    "description": "CLIP text encoder for FLUX"
                },
                {
                    "name": "t5xxl_fp8_e4m3fn.safetensors",
                    "url": "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/text_encoder_2/model.safetensors",
                    "size_gb": 4.9,
                    "description": "T5-XXL text encoder for FLUX"
                }
            ],
            "vae": [
                {
                    "name": "ae.safetensors",
                    "url": "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors",
                    "size_gb": 0.335,
                    "description": "VAE autoencoder for FLUX"
                }
            ]
        }

        # Create directories if they don't exist
        self.text_encoders_path.mkdir(parents=True, exist_ok=True)
        self.vae_path.mkdir(parents=True, exist_ok=True)

    def check_available_space(self) -> float:
        """Check available disk space in GB"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.comfyui_models_path)
            return free / (1024**3)  # Convert to GB
        except:
            return float('inf')  # Assume sufficient space if check fails

    def check_existing_models(self) -> Dict[str, bool]:
        """Check which models are already downloaded"""
        existing = {}

        for category, models in self.required_models.items():
            for model in models:
                if category == "text_encoders":
                    model_path = self.text_encoders_path / model["name"]
                else:
                    model_path = self.vae_path / model["name"]

                existing[model["name"]] = model_path.exists()
                if existing[model["name"]]:
                    size_mb = model_path.stat().st_size / (1024**2)
                    logger.info(f"✅ Found existing: {model['name']} ({size_mb:.1f} MB)")

        return existing

    def download_with_progress(self, url: str, output_path: Path, description: str) -> bool:
        """Download a file with progress tracking"""
        try:
            logger.info(f"Downloading {description}...")
            logger.info(f"URL: {url}")
            logger.info(f"Output: {output_path}")

            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(output_path, 'wb') as f:
                downloaded = 0
                start_time = time.time()

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Progress update every 100MB
                        if downloaded % (100 * 1024 * 1024) == 0:
                            elapsed = time.time() - start_time
                            speed_mbps = (downloaded / (1024**2)) / elapsed if elapsed > 0 else 0
                            percent = (downloaded / total_size * 100) if total_size > 0 else 0
                            logger.info(f"  Progress: {downloaded / (1024**2):.1f} MB downloaded ({percent:.1f}%) - {speed_mbps:.1f} MB/s")

            final_size = output_path.stat().st_size / (1024**2)
            elapsed = time.time() - start_time
            logger.info(f"✅ Downloaded {description}: {final_size:.1f} MB in {elapsed:.1f}s")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to download {description}: {e}")
            if output_path.exists():
                output_path.unlink()  # Remove partial download
            return False

    def download_all_models(self, force_download: bool = False) -> Dict[str, any]:
        """Download all required FLUX models"""
        logger.info("=== FLUX MODEL DOWNLOADER ===")

        results = {
            "success": False,
            "downloaded": [],
            "skipped": [],
            "failed": [],
            "total_size_gb": 0
        }

        # Check available space
        available_space = self.check_available_space()
        required_space = sum(
            sum(model["size_gb"] for model in models)
            for models in self.required_models.values()
        )

        logger.info(f"Available space: {available_space:.1f} GB")
        logger.info(f"Required space: {required_space:.1f} GB")

        if available_space < required_space:
            logger.error(f"❌ Insufficient disk space! Need {required_space:.1f} GB, have {available_space:.1f} GB")
            return results

        # Check existing models
        existing_models = self.check_existing_models()

        # Download missing models
        for category, models in self.required_models.items():
            for model in models:
                model_name = model["name"]

                if existing_models.get(model_name) and not force_download:
                    logger.info(f"⏭️  Skipping {model_name} (already exists)")
                    results["skipped"].append(model_name)
                    continue

                # Determine output path
                if category == "text_encoders":
                    output_path = self.text_encoders_path / model_name
                else:
                    output_path = self.vae_path / model_name

                # Download the model
                success = self.download_with_progress(
                    model["url"],
                    output_path,
                    model["description"]
                )

                if success:
                    results["downloaded"].append(model_name)
                    results["total_size_gb"] += model["size_gb"]
                else:
                    results["failed"].append(model_name)

        # Check if all downloads successful
        results["success"] = len(results["failed"]) == 0

        return results

    def verify_installation(self) -> bool:
        """Verify all required models are properly installed"""
        logger.info("=== VERIFYING FLUX MODEL INSTALLATION ===")

        all_present = True
        for category, models in self.required_models.items():
            for model in models:
                if category == "text_encoders":
                    model_path = self.text_encoders_path / model["name"]
                else:
                    model_path = self.vae_path / model["name"]

                if model_path.exists():
                    size_mb = model_path.stat().st_size / (1024**2)
                    logger.info(f"✅ {model['name']}: {size_mb:.1f} MB")
                else:
                    logger.error(f"❌ Missing: {model['name']}")
                    all_present = False

        if all_present:
            logger.info("🎉 All FLUX models are properly installed!")
        else:
            logger.error("❌ Some FLUX models are missing")

        return all_present

def main():
    """Main execution function"""
    try:
        downloader = FLUXModelDownloader()

        print("🚀 FLUX MODEL DOWNLOADER FOR TERMINAL GROUNDS")
        print("=" * 60)

        # Check what we need
        existing = downloader.check_existing_models()
        missing_count = sum(1 for exists in existing.values() if not exists)

        if missing_count == 0:
            print("✅ All FLUX models already present!")
            return downloader.verify_installation()

        print(f"📦 Need to download {missing_count} FLUX models")

        # Download missing models
        results = downloader.download_all_models()

        # Report results
        print("\n" + "=" * 60)
        print("📊 DOWNLOAD RESULTS")
        print("=" * 60)
        print(f"✅ Downloaded: {len(results['downloaded'])} models")
        print(f"⏭️  Skipped: {len(results['skipped'])} models")
        print(f"❌ Failed: {len(results['failed'])} models")
        print(f"💾 Total Size: {results['total_size_gb']:.1f} GB")

        if results["downloaded"]:
            print("\n📥 Successfully Downloaded:")
            for model in results["downloaded"]:
                print(f"  • {model}")

        if results["failed"]:
            print("\n❌ Failed Downloads:")
            for model in results["failed"]:
                print(f"  • {model}")

        # Final verification
        if results["success"]:
            print("\n🎉 ALL FLUX MODELS READY!")
            print("🚀 You can now run the Dead Sky region builder with full ComfyUI support!")
            downloader.verify_installation()
            return True
        else:
            print("\n⚠️  Some models failed to download. Check your internet connection and try again.")
            return False

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
