"""
Quality Assurance System
=======================

Automated quality validation, enhancement, and post-processing for generated assets.
Includes image analysis, upscaling, format conversion, and validation against
Terminal Grounds quality standards.
"""

from __future__ import annotations

import json
import pathlib
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import logging
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

from .asset_spec import AssetSpecification, QualitySettings
from ..utils.logger import setup_logger
from ..utils.image_analysis import ImageAnalyzer
from ..utils.upscaling import Upscaler


@dataclass
class QualityReport:
    """Report on asset quality assessment."""
    asset_name: str
    overall_score: float  # 0-100
    resolution_score: float
    detail_score: float
    composition_score: float
    color_score: float
    faction_alignment_score: float
    
    # Recommendations
    needs_upscaling: bool = False
    needs_enhancement: bool = False
    needs_color_correction: bool = False
    needs_regeneration: bool = False
    
    # Detailed analysis
    detected_issues: List[str] = None
    recommendations: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.detected_issues is None:
            self.detected_issues = []
        if self.recommendations is None:
            self.recommendations = []
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def passes_quality_gate(self) -> bool:
        """Check if asset passes minimum quality requirements."""
        return (
            self.overall_score >= 70.0 and
            self.resolution_score >= 60.0 and
            not self.needs_regeneration
        )


class QualityAssurance:
    """
    Automated quality assurance system for generated assets.
    
    Features:
    - Image quality analysis and scoring
    - Automatic upscaling and enhancement
    - Format conversion and optimization
    - Faction style compliance checking
    - Quality gate enforcement
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger("QualityAssurance", config.log_level)
        
        # Initialize analysis tools
        self.image_analyzer = ImageAnalyzer()
        self.upscaler = Upscaler(config)
        
        # Quality thresholds
        self.quality_thresholds = {
            "min_resolution": (512, 512),
            "target_resolution": (1024, 1024),
            "min_detail_score": 60.0,
            "min_composition_score": 50.0,
            "min_color_score": 60.0,
            "min_overall_score": 70.0
        }
        
        # Enhancement presets
        self.enhancement_presets = self._load_enhancement_presets()
        
        self.logger.info("Quality Assurance system initialized")
    
    def _load_enhancement_presets(self) -> Dict[str, Dict[str, Any]]:
        """Load enhancement presets for different asset types."""
        return {
            "weapon": {
                "sharpness_boost": 1.2,
                "contrast_boost": 1.1,
                "saturation_boost": 1.05,
                "brightness_adjust": 0.0
            },
            "vehicle": {
                "sharpness_boost": 1.1,
                "contrast_boost": 1.15,
                "saturation_boost": 1.1,
                "brightness_adjust": 0.05
            },
            "environment": {
                "sharpness_boost": 1.0,
                "contrast_boost": 1.05,
                "saturation_boost": 1.2,
                "brightness_adjust": 0.1
            },
            "character": {
                "sharpness_boost": 1.3,
                "contrast_boost": 1.1,
                "saturation_boost": 1.0,
                "brightness_adjust": -0.05
            },
            "ui_icon": {
                "sharpness_boost": 1.4,
                "contrast_boost": 1.2,
                "saturation_boost": 1.1,
                "brightness_adjust": 0.0
            }
        }
    
    def validate_output(
        self,
        generation_result: Dict[str, Any],
        spec: AssetSpecification
    ) -> QualityReport:
        """
        Validate generated output against quality standards.
        
        Args:
            generation_result: Generation result from workflow execution
            spec: Original asset specification
            
        Returns:
            Quality assessment report
        """
        self.logger.info(f"Validating output for asset: {spec.name}")
        
        # Initialize report
        report = QualityReport(
            asset_name=spec.name,
            overall_score=0.0,
            resolution_score=0.0,
            detail_score=0.0,
            composition_score=0.0,
            color_score=0.0,
            faction_alignment_score=0.0
        )
        
        images = generation_result.get("images", [])
        if not images:
            report.detected_issues.append("No images generated")
            report.needs_regeneration = True
            return report
        
        # Analyze primary image (first in list)
        primary_image_path = pathlib.Path(images[0]["local_path"])
        
        try:
            # Load and analyze image
            image = Image.open(primary_image_path)
            analysis_result = self.image_analyzer.analyze_image(image, spec)
            
            # Calculate scores
            report.resolution_score = self._calculate_resolution_score(image, spec)
            report.detail_score = analysis_result.get("detail_score", 0.0)
            report.composition_score = analysis_result.get("composition_score", 0.0)
            report.color_score = analysis_result.get("color_score", 0.0)
            report.faction_alignment_score = self._calculate_faction_alignment_score(
                image, spec, analysis_result
            )
            
            # Calculate overall score
            report.overall_score = self._calculate_overall_score(report)
            
            # Determine recommendations
            self._generate_recommendations(report, image, spec)
            
            # Store analysis metadata
            report.metadata = {
                "image_size": image.size,
                "image_mode": image.mode,
                "file_size": primary_image_path.stat().st_size,
                "analysis_timestamp": time.time(),
                "detailed_analysis": analysis_result
            }
            
        except Exception as e:
            self.logger.error(f"Quality validation failed for {spec.name}: {e}")
            report.detected_issues.append(f"Analysis error: {e}")
            report.needs_regeneration = True
        
        self.logger.info(
            f"Quality validation completed for {spec.name}: "
            f"Score {report.overall_score:.1f}/100"
        )
        
        return report
    
    def _calculate_resolution_score(
        self,
        image: Image.Image,
        spec: AssetSpecification
    ) -> float:
        """Calculate resolution quality score."""
        width, height = image.size
        target_width = spec.render_settings.width
        target_height = spec.render_settings.height
        
        # Calculate resolution ratio
        actual_pixels = width * height
        target_pixels = target_width * target_height
        resolution_ratio = actual_pixels / target_pixels
        
        # Score based on how close to target resolution
        if resolution_ratio >= 1.0:
            score = 100.0
        elif resolution_ratio >= 0.75:
            score = 80.0 + (resolution_ratio - 0.75) * 80
        elif resolution_ratio >= 0.5:
            score = 50.0 + (resolution_ratio - 0.5) * 120
        else:
            score = resolution_ratio * 100
        
        return min(100.0, max(0.0, score))
    
    def _calculate_faction_alignment_score(
        self,
        image: Image.Image,
        spec: AssetSpecification,
        analysis_result: Dict[str, Any]
    ) -> float:
        """Calculate how well the image aligns with faction aesthetics."""
        if not spec.faction_context:
            return 75.0  # Neutral score if no faction specified
        
        score = 75.0  # Base score
        
        # Check color palette alignment
        if spec.faction_context.palette:
            palette_score = analysis_result.get("palette_alignment", 0.0)
            score += (palette_score - 50.0) * 0.3
        
        # Check style elements (simplified heuristic)
        style_keywords = spec.faction_context.aesthetic_keywords
        if style_keywords:
            # This would use more sophisticated style analysis in practice
            style_score = analysis_result.get("style_alignment", 0.0)
            score += (style_score - 50.0) * 0.2
        
        return min(100.0, max(0.0, score))
    
    def _calculate_overall_score(self, report: QualityReport) -> float:
        """Calculate weighted overall quality score."""
        weights = {
            "resolution": 0.25,
            "detail": 0.30,
            "composition": 0.20,
            "color": 0.15,
            "faction_alignment": 0.10
        }
        
        overall = (
            report.resolution_score * weights["resolution"] +
            report.detail_score * weights["detail"] +
            report.composition_score * weights["composition"] +
            report.color_score * weights["color"] +
            report.faction_alignment_score * weights["faction_alignment"]
        )
        
        return min(100.0, max(0.0, overall))
    
    def _generate_recommendations(
        self,
        report: QualityReport,
        image: Image.Image,
        spec: AssetSpecification
    ):
        """Generate improvement recommendations based on analysis."""
        # Resolution recommendations
        if report.resolution_score < 80.0:
            current_size = image.size
            target_size = (spec.render_settings.width, spec.render_settings.height)
            
            if current_size[0] < target_size[0] or current_size[1] < target_size[1]:
                report.needs_upscaling = True
                report.recommendations.append(
                    f"Upscale from {current_size} to {target_size}"
                )
        
        # Detail enhancement recommendations
        if report.detail_score < 70.0:
            report.needs_enhancement = True
            report.recommendations.append("Apply detail enhancement")
        
        # Color correction recommendations
        if report.color_score < 60.0:
            report.needs_color_correction = True
            report.recommendations.append("Apply color correction")
        
        # Regeneration recommendations
        if report.overall_score < 50.0:
            report.needs_regeneration = True
            report.recommendations.append("Consider regenerating with adjusted parameters")
        
        # Quality-specific issues
        if report.resolution_score < self.quality_thresholds["min_resolution"][0]:
            report.detected_issues.append("Resolution below minimum threshold")
        
        if report.detail_score < self.quality_thresholds["min_detail_score"]:
            report.detected_issues.append("Insufficient detail quality")
        
        if report.composition_score < self.quality_thresholds["min_composition_score"]:
            report.detected_issues.append("Poor composition score")
    
    def upscale_asset(
        self,
        generation_result: Dict[str, Any],
        spec: AssetSpecification,
        target_scale: float = 2.0
    ) -> Dict[str, Any]:
        """
        Upscale generated asset using AI upscaling.
        
        Args:
            generation_result: Original generation result
            spec: Asset specification
            target_scale: Upscaling factor
            
        Returns:
            Updated generation result with upscaled images
        """
        self.logger.info(f"Upscaling asset: {spec.name}")
        
        upscaled_images = []
        
        for image_info in generation_result["images"]:
            try:
                original_path = pathlib.Path(image_info["local_path"])
                
                # Generate upscaled filename
                upscaled_filename = f"{original_path.stem}_upscaled{original_path.suffix}"
                upscaled_path = original_path.parent / upscaled_filename
                
                # Perform upscaling
                self.upscaler.upscale_image(
                    original_path,
                    upscaled_path,
                    scale=target_scale,
                    model="RealESRGAN"  # or other upscaling model
                )
                
                # Create new image info
                upscaled_info = image_info.copy()
                upscaled_info.update({
                    "filename": upscaled_filename,
                    "local_path": str(upscaled_path),
                    "upscaled": True,
                    "upscale_factor": target_scale,
                    "original_path": str(original_path)
                })
                
                upscaled_images.append(upscaled_info)
                
                self.logger.debug(f"Upscaled image: {upscaled_filename}")
                
            except Exception as e:
                self.logger.error(f"Failed to upscale image {image_info}: {e}")
                # Keep original image if upscaling fails
                upscaled_images.append(image_info)
        
        # Update generation result
        updated_result = generation_result.copy()
        updated_result["images"] = upscaled_images
        updated_result["upscaling_applied"] = True
        updated_result["upscaling_timestamp"] = time.time()
        
        return updated_result
    
    def enhance_asset(
        self,
        generation_result: Dict[str, Any],
        spec: AssetSpecification
    ) -> Dict[str, Any]:
        """
        Apply enhancement filters to improve image quality.
        
        Args:
            generation_result: Generation result
            spec: Asset specification
            
        Returns:
            Updated generation result with enhanced images
        """
        self.logger.info(f"Enhancing asset: {spec.name}")
        
        # Get enhancement preset for asset type
        preset_name = spec.asset_type.value
        preset = self.enhancement_presets.get(preset_name, self.enhancement_presets["weapon"])
        
        enhanced_images = []
        
        for image_info in generation_result["images"]:
            try:
                image_path = pathlib.Path(image_info["local_path"])
                
                # Load image
                image = Image.open(image_path)
                
                # Apply enhancements
                enhanced_image = self._apply_enhancements(image, preset, spec)
                
                # Generate enhanced filename
                enhanced_filename = f"{image_path.stem}_enhanced{image_path.suffix}"
                enhanced_path = image_path.parent / enhanced_filename
                
                # Save enhanced image
                enhanced_image.save(enhanced_path, quality=95, optimize=True)
                
                # Create new image info
                enhanced_info = image_info.copy()
                enhanced_info.update({
                    "filename": enhanced_filename,
                    "local_path": str(enhanced_path),
                    "enhanced": True,
                    "enhancement_preset": preset_name,
                    "original_path": str(image_path)
                })
                
                enhanced_images.append(enhanced_info)
                
                self.logger.debug(f"Enhanced image: {enhanced_filename}")
                
            except Exception as e:
                self.logger.error(f"Failed to enhance image {image_info}: {e}")
                # Keep original image if enhancement fails
                enhanced_images.append(image_info)
        
        # Update generation result
        updated_result = generation_result.copy()
        updated_result["images"] = enhanced_images
        updated_result["enhancement_applied"] = True
        updated_result["enhancement_timestamp"] = time.time()
        
        return updated_result
    
    def _apply_enhancements(
        self,
        image: Image.Image,
        preset: Dict[str, Any],
        spec: AssetSpecification
    ) -> Image.Image:
        """Apply enhancement filters based on preset."""
        enhanced = image.copy()
        
        # Apply sharpness enhancement
        if preset.get("sharpness_boost", 1.0) != 1.0:
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = sharpness_enhancer.enhance(preset["sharpness_boost"])
        
        # Apply contrast enhancement
        if preset.get("contrast_boost", 1.0) != 1.0:
            contrast_enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = contrast_enhancer.enhance(preset["contrast_boost"])
        
        # Apply saturation enhancement
        if preset.get("saturation_boost", 1.0) != 1.0:
            saturation_enhancer = ImageEnhance.Color(enhanced)
            enhanced = saturation_enhancer.enhance(preset["saturation_boost"])
        
        # Apply brightness adjustment
        if preset.get("brightness_adjust", 0.0) != 0.0:
            brightness_enhancer = ImageEnhance.Brightness(enhanced)
            brightness_factor = 1.0 + preset["brightness_adjust"]
            enhanced = brightness_enhancer.enhance(brightness_factor)
        
        # Apply unsharp mask for additional detail
        if spec.asset_type.value in ["weapon", "ui_icon"]:
            enhanced = enhanced.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        return enhanced
    
    def convert_format(
        self,
        generation_result: Dict[str, Any],
        target_format: str,
        quality: int = 95
    ) -> Dict[str, Any]:
        """
        Convert images to different format.
        
        Args:
            generation_result: Generation result
            target_format: Target format (PNG, JPG, etc.)
            quality: Quality setting for lossy formats
            
        Returns:
            Updated generation result with converted images
        """
        self.logger.info(f"Converting images to {target_format}")
        
        converted_images = []
        
        for image_info in generation_result["images"]:
            try:
                image_path = pathlib.Path(image_info["local_path"])
                
                # Load image
                image = Image.open(image_path)
                
                # Generate new filename
                new_filename = f"{image_path.stem}.{target_format.lower()}"
                new_path = image_path.parent / new_filename
                
                # Save in new format
                save_kwargs = {"optimize": True}
                if target_format.upper() == "JPG":
                    save_kwargs["quality"] = quality
                    # Convert RGBA to RGB for JPEG
                    if image.mode == "RGBA":
                        background = Image.new("RGB", image.size, (255, 255, 255))
                        background.paste(image, mask=image.split()[-1])
                        image = background
                
                image.save(new_path, format=target_format.upper(), **save_kwargs)
                
                # Create new image info
                converted_info = image_info.copy()
                converted_info.update({
                    "filename": new_filename,
                    "local_path": str(new_path),
                    "format_converted": True,
                    "target_format": target_format,
                    "original_format": image_path.suffix[1:].upper()
                })
                
                converted_images.append(converted_info)
                
            except Exception as e:
                self.logger.error(f"Failed to convert image {image_info}: {e}")
                converted_images.append(image_info)
        
        # Update generation result
        updated_result = generation_result.copy()
        updated_result["images"] = converted_images
        updated_result["format_conversion_applied"] = True
        
        return updated_result
    
    def batch_validate(
        self,
        generation_results: List[Dict[str, Any]],
        specs: List[AssetSpecification]
    ) -> List[QualityReport]:
        """Validate multiple assets in batch."""
        self.logger.info(f"Batch validating {len(generation_results)} assets")
        
        reports = []
        for result, spec in zip(generation_results, specs):
            report = self.validate_output(result, spec)
            reports.append(report)
        
        # Generate batch summary
        passed = sum(1 for report in reports if report.passes_quality_gate)
        average_score = sum(report.overall_score for report in reports) / len(reports)
        
        self.logger.info(
            f"Batch validation completed: {passed}/{len(reports)} passed, "
            f"average score: {average_score:.1f}"
        )
        
        return reports
    
    def get_status(self) -> Dict[str, Any]:
        """Get quality assurance system status."""
        return {
            "upscaler_available": self.upscaler.is_available(),
            "image_analyzer_available": self.image_analyzer.is_available(),
            "quality_thresholds": self.quality_thresholds,
            "enhancement_presets": list(self.enhancement_presets.keys())
        }