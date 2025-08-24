#!/usr/bin/env python3
"""
Terminal Grounds - Clean Asset Generation (No Text)
=====================================================
Generates pristine assets without any text, then applies
professional overlays as a post-processing step.
"""

import json
import subprocess
from pathlib import Path
from typing import Optional, Dict
from PIL import Image, ImageDraw, ImageFont

class CleanAssetPipeline:
    """Generate text-free assets with optional post-process overlays"""
    
    def __init__(self):
        self.comfy_api_dir = Path(r"C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API")
        self.output_dir = self.comfy_api_dir / "output"
        
    def generate_clean_asset(
        self,
        subject: str,
        location: str = "Metro",
        width: int = 1920,
        height: int = 1080,
        steps: int = 30,
        seed: Optional[int] = None
    ) -> Path:
        """Generate a pristine asset without any text"""
        
        # Build text-free prompt focusing on visual quality
        prompt_parts = [
            f"Terminal Grounds {location}",
            subject,
            "AAA game asset production quality",
            "extreme surface detail and texture resolution",
            "photogrammetry-quality materials",
            "microscopic wear patterns and weathering",
            "PBR material properties with accurate roughness",
            "ray-traced global illumination",
            "Unreal Engine 5.6 Nanite virtualized geometry",
            "cinematic composition without any text or UI elements"
        ]
        
        # Strong negative to prevent ANY text generation
        negative = (
            "text, words, letters, numbers, signs, labels, UI, HUD, "
            "interface elements, overlays, watermarks, logos, typography, "
            "writing, characters, symbols, captions, titles, credits, "
            "any textual elements whatsoever, low resolution, blurry"
        )
        
        # Use PowerShell script for generation
        prefix = f"TG_{location}_Clean"
        
        if seed is None:
            import random
            seed = random.randint(10000, 99999)
        
        cmd = [
            "powershell", "-Command",
            f"cd '{self.comfy_api_dir}' && "
            f"./Test-Generate.ps1 "
            f"-Prompt '{', '.join(prompt_parts)}' "
            f"-Negative '{negative}' "
            f"-Prefix {prefix} "
            f"-Width {width} -Height {height} "
            f"-Steps {steps} "
            f"-CFG 3.2 "
            f"-Sampler heun -Scheduler normal "
            f"-Seed {seed} "
            f"-Wait -TimeoutSec 900"
        ]
        
        print(f"🎨 Generating clean asset at {width}x{height}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Find the generated image
        pattern = f"{prefix}_*_.png"
        images = sorted(self.output_dir.glob(pattern), key=lambda x: x.stat().st_mtime)
        
        if images:
            return images[-1]
        else:
            raise RuntimeError("Generation failed - no output found")
    
    def add_professional_overlay(
        self,
        image_path: Path,
        left_text: str = "TERMINAL GROUNDS",
        center_text: str = "",
        right_text: str = "BUILD 0.4.2",
        bar_height_pct: float = 0.08
    ) -> Path:
        """Add clean, professional text overlay to image"""
        
        img = Image.open(image_path)
        width, height = img.size
        
        # Calculate overlay dimensions
        bar_height = int(height * bar_height_pct)
        bar_y = height - bar_height
        
        # Create overlay with transparency
        overlay = Image.new('RGBA', (width, bar_height), (0, 0, 0, 200))
        draw = ImageDraw.Draw(overlay)
        
        # Try to use a professional font, fallback to default
        try:
            font_size = int(bar_height * 0.5)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Add text elements
        padding = int(width * 0.02)
        
        # Left text
        if left_text:
            draw.text((padding, bar_height//2), left_text, 
                     fill=(255, 255, 255, 255), font=font, anchor="lm")
        
        # Center text
        if center_text:
            center_x = width // 2
            draw.text((center_x, bar_height//2), center_text,
                     fill=(255, 255, 255, 255), font=font, anchor="mm")
        
        # Right text
        if right_text:
            draw.text((width - padding, bar_height//2), right_text,
                     fill=(255, 255, 255, 255), font=font, anchor="rm")
        
        # Composite overlay onto image
        img_with_overlay = img.copy()
        img_with_overlay.paste(overlay, (0, bar_y), overlay)
        
        # Save with overlay
        output_path = image_path.parent / f"{image_path.stem}_labeled.png"
        img_with_overlay.save(output_path, "PNG")
        
        return output_path
    
    def create_comparison(self, original_path: Path, labeled_path: Path) -> Path:
        """Create side-by-side comparison of original vs labeled"""
        
        orig = Image.open(original_path)
        labeled = Image.open(labeled_path)
        
        width = orig.width * 2 + 20  # 20px gap
        height = orig.height
        
        comparison = Image.new('RGB', (width, height), (30, 30, 30))
        comparison.paste(orig, (0, 0))
        comparison.paste(labeled, (orig.width + 20, 0))
        
        output_path = original_path.parent / f"{original_path.stem}_comparison.png"
        comparison.save(output_path, "PNG")
        
        return output_path

def demonstrate_clean_pipeline():
    """Show the difference between AI text vs clean overlay"""
    
    pipeline = CleanAssetPipeline()
    
    print("=" * 60)
    print("TERMINAL GROUNDS - Clean Asset Generation Demo")
    print("=" * 60)
    print()
    
    # Generate a clean asset
    print("Step 1: Generating pristine asset without text...")
    clean_image = pipeline.generate_clean_asset(
        subject="industrial maintenance corridor with detailed textures",
        location="Metro",
        width=1920,
        height=1080,
        steps=30
    )
    print(f"✅ Clean asset generated: {clean_image.name}")
    print()
    
    # Add professional overlay
    print("Step 2: Adding professional text overlay...")
    labeled_image = pipeline.add_professional_overlay(
        clean_image,
        left_text="TERMINAL GROUNDS",
        center_text="METRO CORRIDOR",
        right_text="UE 5.6"
    )
    print(f"✅ Labeled asset created: {labeled_image.name}")
    print()
    
    # Create comparison
    print("Step 3: Creating comparison image...")
    comparison = pipeline.create_comparison(clean_image, labeled_image)
    print(f"✅ Comparison saved: {comparison.name}")
    print()
    
    print("🎯 Benefits of this approach:")
    print("   - No garbled AI text (TREGBIR, etc.)")
    print("   - Consistent, professional typography")
    print("   - Full image quality for textures")
    print("   - Easy to update text without regenerating")
    print("   - Perfect for production pipeline")

if __name__ == "__main__":
    # Just save the script for now
    print("Clean Asset Pipeline ready!")
    print("This script will generate text-free images and add clean overlays.")
    print()
    print("To test: python no_text_generation_workflow.py")