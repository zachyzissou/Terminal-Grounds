#!/usr/bin/env python3
"""
Quality Assurance System for Terminal Grounds v2.0
==================================================
Automated quality scoring, enhancement decisions, and asset validation.
"""

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    # Create mock cv2 module for basic functionality
    class MockCV2:
        COLOR_BGR2GRAY = 6
        CV_64F = 6
        THRESH_BINARY = 0
        THRESH_OTSU = 8
        RETR_EXTERNAL = 0
        CHAIN_APPROX_SIMPLE = 2
        
        @staticmethod
        def cvtColor(img, code):
            return img
        
        @staticmethod
        def Laplacian(img, ddepth):
            class MockArray:
                def var(self): return 500.0
            return MockArray()
        
        @staticmethod
        def Canny(img, t1, t2):
            return img
        
        @staticmethod
        def threshold(img, thresh, maxval, type):
            return thresh, img
        
        @staticmethod
        def findContours(img, mode, method):
            return [], None
        
        @staticmethod
        def contourArea(contour):
            return 100.0
        
        @staticmethod
        def moments(contour):
            return {"m00": 1, "m10": 50, "m01": 50}
        
        @staticmethod
        def calcHist(images, channels, mask, histSize, ranges):
            return [100] * 256
        
        @staticmethod
        def GaussianBlur(img, ksize, sigmaX):
            return img
        
        @staticmethod
        def absdiff(img1, img2):
            return img1
        
        @staticmethod
        def Sobel(img, ddepth, dx, dy, ksize=3):
            return img
    
    cv2 = MockCV2()
    
    # Create mock numpy
    class MockNumPy:
        ndarray = list  # Use list as a substitute
        
        @staticmethod
        def sum(arr):
            return 100
        
        @staticmethod
        def mean(arr):
            return 50.0
        
        @staticmethod
        def std(arr):
            return 25.0
        
        @staticmethod
        def sqrt(val):
            return val ** 0.5
        
        @staticmethod
        def abs(val):
            return abs(val)
        
        @staticmethod
        def min(arr):
            return 10.0
        
        @staticmethod
        def max(arr):
            return 90.0
    
    np = MockNumPy()
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
try:
    from PIL import Image, ImageStat, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    # Create mock PIL classes
    class MockImage:
        @staticmethod
        def open(path):
            class MockImg:
                size = (1024, 1024)
                mode = 'RGB'
                def convert(self, mode): return self
                def save(self, path, format, **kwargs): pass
                def thumbnail(self, size, resample=None): pass
            return MockImg()
    
    class MockImageStat:
        def __init__(self, img): 
            self.var = [1000, 1000, 1000]
    
    class MockImageFilter:
        pass
    
    Image = MockImage()
    ImageStat = MockImageStat
    ImageFilter = MockImageFilter()
import time

try:
    from .asset_spec import AssetSpecification, AssetType, FactionCode, QualityLevel
except ImportError:
    from asset_spec import AssetSpecification, AssetType, FactionCode, QualityLevel

logger = logging.getLogger(__name__)

class QualityRating(Enum):
    REJECT = "reject"          # < 40: Regeneration required
    POOR = "poor"              # 40-60: Major enhancement needed
    ACCEPTABLE = "acceptable"   # 60-75: Minor enhancement
    GOOD = "good"              # 75-85: Standard quality
    EXCELLENT = "excellent"     # 85-95: High quality
    PERFECT = "perfect"        # 95+: Hero/cinematic quality

@dataclass
class QualityMetrics:
    """Detailed quality assessment metrics"""
    overall_score: float
    rating: QualityRating
    
    # Individual component scores (0-100)
    resolution_score: float
    sharpness_score: float
    detail_score: float
    composition_score: float
    faction_alignment_score: float
    technical_score: float
    
    # Enhancement recommendations
    needs_upscale: bool = False
    needs_sharpen: bool = False
    needs_detail_enhance: bool = False
    needs_color_correct: bool = False
    needs_regeneration: bool = False
    
    # Metadata
    assessment_time: float = field(default_factory=time.time)
    assessed_resolution: Tuple[int, int] = (0, 0)
    file_size_mb: float = 0.0
    
    # Detailed analysis
    analysis_notes: List[str] = field(default_factory=list)
    suggested_improvements: List[str] = field(default_factory=list)

@dataclass
class QualityAssessmentResult:
    """Complete quality assessment result"""
    metrics: QualityMetrics
    asset_spec: AssetSpecification
    image_path: Path
    assessment_id: str
    recommendations: Dict[str, Any] = field(default_factory=dict)

class QualityAssessmentEngine:
    """
    Advanced quality assessment using computer vision and asset-specific criteria.
    Evaluates generated assets against Terminal Grounds quality standards.
    """
    
    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or Path("models/quality")
        
        # Quality thresholds for different asset types
        self.type_thresholds = {
            "weapon": {"min": 75, "target": 85, "hero": 90},
            "vehicle": {"min": 70, "target": 80, "hero": 85},
            "emblem": {"min": 80, "target": 90, "hero": 95},
            "poster": {"min": 65, "target": 75, "hero": 85},
            "icon": {"min": 75, "target": 85, "hero": 90},
            "concept": {"min": 60, "target": 75, "hero": 85},
            "environment": {"min": 65, "target": 80, "hero": 90},
            "texture": {"min": 75, "target": 85, "hero": 90},
            "ui": {"min": 70, "target": 80, "hero": 85}
        }
        
        # Faction-specific quality expectations
        self.faction_quality_profiles = {
            "directorate": {"precision": 0.9, "clean_lines": 0.85, "symmetry": 0.8},
            "free77": {"ruggedness": 0.8, "weathering": 0.7, "practical": 0.85},
            "vultures": {"industrial": 0.8, "worn": 0.75, "makeshift": 0.7},
            "combine": {"high_tech": 0.9, "sleek": 0.85, "corporate": 0.8},
            "nomads": {"tribal": 0.8, "organic": 0.75, "weathered": 0.7},
            "archivists": {"mystical": 0.8, "ancient": 0.75, "ornate": 0.8},
            "wardens": {"defensive": 0.85, "sturdy": 0.8, "utilitarian": 0.85},
            "neutral": {"generic": 0.7, "functional": 0.75, "balanced": 0.7}
        }
        
    def assess_quality(self, image_path: Path, asset_spec: AssetSpecification) -> QualityAssessmentResult:
        """
        Comprehensive quality assessment of generated asset
        
        Args:
            image_path: Path to generated image
            asset_spec: Original asset specification
            
        Returns:
            Complete quality assessment result
        """
        assessment_id = f"qa_{int(time.time() * 1000)}"
        
        try:
            # Load and validate image
            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
                
            # Perform assessment
            metrics = self._assess_image_quality(image_path, asset_spec)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metrics, asset_spec)
            
            # Create result
            result = QualityAssessmentResult(
                metrics=metrics,
                asset_spec=asset_spec,
                image_path=image_path,
                assessment_id=assessment_id,
                recommendations=recommendations
            )
            
            logger.info(f"Quality assessment complete: {metrics.overall_score:.1f} ({metrics.rating.value})")
            return result
            
        except Exception as e:
            logger.error(f"Quality assessment failed for {image_path}: {e}")
            # Return minimal failing result
            metrics = QualityMetrics(
                overall_score=0.0,
                rating=QualityRating.REJECT,
                resolution_score=0.0,
                sharpness_score=0.0,
                detail_score=0.0,
                composition_score=0.0,
                faction_alignment_score=0.0,
                technical_score=0.0,
                needs_regeneration=True,
                analysis_notes=[f"Assessment failed: {str(e)}"]
            )
            
            return QualityAssessmentResult(
                metrics=metrics,
                asset_spec=asset_spec,
                image_path=image_path,
                assessment_id=assessment_id
            )
    
    def _assess_image_quality(self, image_path: Path, asset_spec: AssetSpecification) -> QualityMetrics:
        """Perform detailed image quality analysis"""
        
        # Load image
        pil_image = Image.open(image_path)
        cv_image = cv2.imread(str(image_path))
        
        if cv_image is None:
            raise ValueError("Could not load image with OpenCV")
        
        # Basic image properties
        width, height = pil_image.size
        file_size_mb = image_path.stat().st_size / (1024 * 1024)
        
        # Individual assessments
        resolution_score = self._assess_resolution(width, height, asset_spec)
        sharpness_score = self._assess_sharpness(cv_image)
        detail_score = self._assess_detail_richness(cv_image, pil_image)
        composition_score = self._assess_composition(cv_image, asset_spec)
        faction_score = self._assess_faction_alignment(pil_image, asset_spec)
        technical_score = self._assess_technical_quality(pil_image, cv_image)
        
        # Calculate weighted overall score
        weights = self._get_assessment_weights(asset_spec.asset_type)
        overall_score = (
            resolution_score * weights["resolution"] +
            sharpness_score * weights["sharpness"] +
            detail_score * weights["detail"] +
            composition_score * weights["composition"] +
            faction_score * weights["faction"] +
            technical_score * weights["technical"]
        )
        
        # Determine rating
        rating = self._score_to_rating(overall_score)
        
        # Generate enhancement recommendations
        needs_upscale = resolution_score < 70
        needs_sharpen = sharpness_score < 75
        needs_detail_enhance = detail_score < 70
        needs_color_correct = technical_score < 70
        needs_regeneration = overall_score < 40
        
        # Analysis notes
        analysis_notes = []
        if resolution_score < 60:
            analysis_notes.append("Resolution below target for asset type")
        if sharpness_score < 60:
            analysis_notes.append("Image appears soft or blurry")
        if detail_score < 60:
            analysis_notes.append("Insufficient detail richness")
        if composition_score < 60:
            analysis_notes.append("Composition needs improvement")
        if faction_score < 60:
            analysis_notes.append("Faction style alignment issues")
        
        return QualityMetrics(
            overall_score=overall_score,
            rating=rating,
            resolution_score=resolution_score,
            sharpness_score=sharpness_score,
            detail_score=detail_score,
            composition_score=composition_score,
            faction_alignment_score=faction_score,
            technical_score=technical_score,
            needs_upscale=needs_upscale,
            needs_sharpen=needs_sharpen,
            needs_detail_enhance=needs_detail_enhance,
            needs_color_correct=needs_color_correct,
            needs_regeneration=needs_regeneration,
            assessed_resolution=(width, height),
            file_size_mb=file_size_mb,
            analysis_notes=analysis_notes
        )
    
    def _assess_resolution(self, width: int, height: int, asset_spec: AssetSpecification) -> float:
        """Assess if resolution meets requirements"""
        target_width = asset_spec.generation_params.width
        target_height = asset_spec.generation_params.height
        min_resolution = asset_spec.quality_requirements.min_resolution
        
        # Calculate resolution scores
        width_ratio = min(width / target_width, 1.0)
        height_ratio = min(height / target_height, 1.0)
        resolution_ratio = min(width_ratio, height_ratio)
        
        # Bonus for exceeding target resolution
        if width >= target_width * 1.5 and height >= target_height * 1.5:
            resolution_ratio = min(resolution_ratio * 1.2, 1.0)
        
        # Penalty for falling below minimum
        total_pixels = width * height
        min_pixels = min_resolution * min_resolution
        if total_pixels < min_pixels:
            resolution_ratio *= 0.5
        
        return resolution_ratio * 100
    
    def _assess_sharpness(self, cv_image: np.ndarray) -> float:
        """Assess image sharpness using Laplacian variance"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize sharpness score (empirically derived thresholds)
            if laplacian_var > 1000:
                return 100.0
            elif laplacian_var > 500:
                return 80.0 + (laplacian_var - 500) / 500 * 20
            elif laplacian_var > 100:
                return 50.0 + (laplacian_var - 100) / 400 * 30
            else:
                return max(0.0, laplacian_var / 100 * 50)
                
        except Exception as e:
            logger.warning(f"Sharpness assessment failed: {e}")
            return 50.0  # Default middle score
    
    def _assess_detail_richness(self, cv_image: np.ndarray, pil_image: Image.Image) -> float:
        """Assess detail richness using edge detection and texture analysis"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Edge detection for detail assessment
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Texture analysis using local binary patterns approximation
            texture_score = self._calculate_texture_score(gray)
            
            # Color richness (for non-monochrome assets)
            color_richness = self._calculate_color_richness(pil_image)
            
            # Combine scores
            detail_score = (edge_density * 0.4 + texture_score * 0.4 + color_richness * 0.2) * 100
            
            return min(100.0, detail_score)
            
        except Exception as e:
            logger.warning(f"Detail assessment failed: {e}")
            return 50.0
    
    def _assess_composition(self, cv_image: np.ndarray, asset_spec: AssetSpecification) -> float:
        """Assess composition quality based on asset type"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            composition_score = 60.0  # Base score
            
            # Asset-specific composition checks
            if asset_spec.asset_type in ["emblem", "icon"]:
                # Check for centeredness
                center_score = self._assess_centeredness(gray)
                composition_score += center_score * 0.4
                
            elif asset_spec.asset_type in ["weapon", "vehicle"]:
                # Check for main subject prominence
                subject_score = self._assess_subject_prominence(gray)
                composition_score += subject_score * 0.4
                
            elif asset_spec.asset_type in ["poster"]:
                # Check for visual hierarchy
                hierarchy_score = self._assess_visual_hierarchy(gray)
                composition_score += hierarchy_score * 0.4
                
            # Rule of thirds check (general)
            thirds_score = self._assess_rule_of_thirds(gray)
            composition_score += thirds_score * 0.2
            
            return min(100.0, composition_score)
            
        except Exception as e:
            logger.warning(f"Composition assessment failed: {e}")
            return 60.0
    
    def _assess_faction_alignment(self, pil_image: Image.Image, asset_spec: AssetSpecification) -> float:
        """Assess how well the asset aligns with faction visual identity"""
        try:
            faction = asset_spec.faction
            if faction not in self.faction_quality_profiles:
                return 70.0  # Neutral score for unknown factions
            
            faction_profile = self.faction_quality_profiles[faction]
            
            # Color palette analysis
            colors = pil_image.getcolors(maxcolors=256*256*256)
            if colors:
                palette_score = self._assess_faction_colors(colors, faction)
            else:
                palette_score = 50.0
            
            # Style consistency (basic implementation)
            style_score = self._assess_faction_style(pil_image, faction_profile)
            
            # Combine scores
            faction_score = (palette_score * 0.6 + style_score * 0.4)
            
            return min(100.0, faction_score)
            
        except Exception as e:
            logger.warning(f"Faction alignment assessment failed: {e}")
            return 70.0
    
    def _assess_technical_quality(self, pil_image: Image.Image, cv_image: np.ndarray) -> float:
        """Assess technical image quality (compression artifacts, noise, etc.)"""
        try:
            technical_score = 80.0  # Base score
            
            # Check for JPEG artifacts (if applicable)
            if hasattr(pil_image, 'format') and pil_image.format == 'JPEG':
                # Simple artifact detection
                artifact_score = self._detect_compression_artifacts(cv_image)
                technical_score += (artifact_score - 50) * 0.3
            
            # Check for noise
            noise_score = self._assess_noise_level(cv_image)
            technical_score += (noise_score - 50) * 0.3
            
            # Check for color banding
            banding_score = self._assess_color_banding(cv_image)
            technical_score += (banding_score - 50) * 0.2
            
            # Check bit depth adequacy
            bit_depth_score = self._assess_bit_depth(pil_image)
            technical_score += (bit_depth_score - 50) * 0.2
            
            return max(0.0, min(100.0, technical_score))
            
        except Exception as e:
            logger.warning(f"Technical quality assessment failed: {e}")
            return 70.0
    
    def _get_assessment_weights(self, asset_type: AssetType) -> Dict[str, float]:
        """Get quality assessment weights for different asset types"""
        
        base_weights = {
            "resolution": 0.2,
            "sharpness": 0.2,
            "detail": 0.2,
            "composition": 0.2,
            "faction": 0.1,
            "technical": 0.1
        }
        
        # Adjust weights based on asset type
        if asset_type in ["emblem", "icon"]:
            base_weights.update({
                "sharpness": 0.3,
                "composition": 0.3,
                "detail": 0.15,
                "faction": 0.15
            })
        elif asset_type in ["weapon", "vehicle"]:
            base_weights.update({
                "detail": 0.3,
                "resolution": 0.25,
                "sharpness": 0.25
            })
        elif asset_type == "concept":
            base_weights.update({
                "composition": 0.3,
                "detail": 0.25,
                "faction": 0.2
            })
        
        return base_weights
    
    def _score_to_rating(self, score: float) -> QualityRating:
        """Convert numeric score to quality rating"""
        if score >= 95:
            return QualityRating.PERFECT
        elif score >= 85:
            return QualityRating.EXCELLENT
        elif score >= 75:
            return QualityRating.GOOD
        elif score >= 60:
            return QualityRating.ACCEPTABLE
        elif score >= 40:
            return QualityRating.POOR
        else:
            return QualityRating.REJECT
    
    def _generate_recommendations(self, metrics: QualityMetrics, asset_spec: AssetSpecification) -> Dict[str, Any]:
        """Generate enhancement and improvement recommendations"""
        recommendations = {
            "immediate_actions": [],
            "enhancements": [],
            "regeneration_suggestions": [],
            "technical_fixes": []
        }
        
        # Immediate action recommendations
        if metrics.needs_regeneration:
            recommendations["immediate_actions"].append("Regenerate asset - quality below acceptable threshold")
        
        # Enhancement recommendations
        if metrics.needs_upscale:
            recommendations["enhancements"].append({
                "type": "upscale",
                "reason": f"Resolution score: {metrics.resolution_score:.1f}",
                "method": "4x-UltraSharp upscaler",
                "priority": "high"
            })
        
        if metrics.needs_sharpen:
            recommendations["enhancements"].append({
                "type": "sharpen",
                "reason": f"Sharpness score: {metrics.sharpness_score:.1f}",
                "method": "unsharp mask or detail enhancement",
                "priority": "medium"
            })
        
        if metrics.needs_detail_enhance:
            recommendations["enhancements"].append({
                "type": "detail_enhance",
                "reason": f"Detail score: {metrics.detail_score:.1f}",
                "method": "AI detail enhancement pass",
                "priority": "medium"
            })
        
        if metrics.needs_color_correct:
            recommendations["enhancements"].append({
                "type": "color_correction",
                "reason": f"Technical score: {metrics.technical_score:.1f}",
                "method": "faction-appropriate color grading",
                "priority": "low"
            })
        
        # Regeneration suggestions for poor quality
        if metrics.overall_score < 60:
            recommendations["regeneration_suggestions"].extend([
                "Increase generation steps for better quality",
                "Adjust CFG scale for better prompt adherence",
                "Consider different sampler or scheduler",
                "Refine prompts for better faction alignment"
            ])
        
        return recommendations
    
    # Helper methods for specific assessments
    def _calculate_texture_score(self, gray: np.ndarray) -> float:
        """Calculate texture richness score"""
        try:
            # Simple texture analysis using standard deviation in local patches
            h, w = gray.shape
            patch_size = min(32, h // 8, w // 8)
            texture_scores = []
            
            for y in range(0, h - patch_size, patch_size):
                for x in range(0, w - patch_size, patch_size):
                    patch = gray[y:y+patch_size, x:x+patch_size]
                    texture_scores.append(np.std(patch))
            
            if texture_scores:
                avg_texture = np.mean(texture_scores)
                return min(1.0, avg_texture / 50.0)  # Normalize
            return 0.5
            
        except Exception:
            return 0.5
    
    def _calculate_color_richness(self, pil_image: Image.Image) -> float:
        """Calculate color diversity and richness"""
        try:
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Calculate color statistics
            stat = ImageStat.Stat(pil_image)
            
            # Use variance in RGB channels as richness indicator
            color_variance = np.mean(stat.var)
            return min(1.0, color_variance / 10000.0)  # Normalize
            
        except Exception:
            return 0.5
    
    def _assess_centeredness(self, gray: np.ndarray) -> float:
        """Assess how centered the main subject is (for emblems/icons)"""
        try:
            # Find contours to locate main subject
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return 50.0
            
            # Find largest contour (assumed to be main subject)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate centroid
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Calculate distance from image center
                h, w = gray.shape
                center_x, center_y = w // 2, h // 2
                distance = np.sqrt((cx - center_x)**2 + (cy - center_y)**2)
                
                # Normalize distance (max distance would be corner to center)
                max_distance = np.sqrt(center_x**2 + center_y**2)
                centeredness = 1.0 - (distance / max_distance)
                
                return centeredness * 100
            
            return 50.0
            
        except Exception:
            return 50.0
    
    def _assess_subject_prominence(self, gray: np.ndarray) -> float:
        """Assess how prominent the main subject is"""
        try:
            # Use edge detection to find main subject
            edges = cv2.Canny(gray, 50, 150)
            
            # Calculate edge density in center vs edges
            h, w = gray.shape
            center_region = edges[h//4:3*h//4, w//4:3*w//4]
            edge_region = edges.copy()
            edge_region[h//4:3*h//4, w//4:3*w//4] = 0
            
            center_density = np.sum(center_region > 0) / center_region.size
            edge_density = np.sum(edge_region > 0) / edge_region.size
            
            if edge_density > 0:
                prominence = center_density / (center_density + edge_density)
                return prominence * 100
            
            return 70.0  # Default if no edges detected
            
        except Exception:
            return 70.0
    
    def _assess_visual_hierarchy(self, gray: np.ndarray) -> float:
        """Assess visual hierarchy (for posters)"""
        # Simplified implementation - could be enhanced with more sophisticated analysis
        try:
            # Analyze contrast distribution
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            
            # Look for good contrast distribution
            low_contrast = np.sum(hist[64:192])  # Mid-tones
            high_contrast = np.sum(hist[:64]) + np.sum(hist[192:])  # Darks and lights
            
            total_pixels = gray.size
            contrast_ratio = high_contrast / total_pixels
            
            # Good hierarchy should have both mid-tones and contrast
            if 0.3 <= contrast_ratio <= 0.7:
                return 80.0
            else:
                return 60.0
                
        except Exception:
            return 60.0
    
    def _assess_rule_of_thirds(self, gray: np.ndarray) -> float:
        """Assess composition using rule of thirds"""
        try:
            h, w = gray.shape
            
            # Define thirds lines
            third_h, third_w = h // 3, w // 3
            
            # Calculate edge density at thirds intersections
            thirds_points = [
                (third_w, third_h), (2 * third_w, third_h),
                (third_w, 2 * third_h), (2 * third_w, 2 * third_h)
            ]
            
            edges = cv2.Canny(gray, 50, 150)
            
            total_edge_density = 0
            for x, y in thirds_points:
                region = edges[max(0, y-20):min(h, y+20), max(0, x-20):min(w, x+20)]
                if region.size > 0:
                    density = np.sum(region > 0) / region.size
                    total_edge_density += density
            
            # Normalize and score
            avg_density = total_edge_density / len(thirds_points)
            return min(100.0, avg_density * 1000)  # Scale appropriately
            
        except Exception:
            return 50.0
    
    def _assess_faction_colors(self, colors: List[Tuple], faction: FactionCode) -> float:
        """Assess color palette alignment with faction"""
        # Simplified color assessment - could be enhanced with color theory
        try:
            # Extract dominant colors (simplified)
            total_pixels = sum(count for count, color in colors)
            dominant_colors = sorted(colors, key=lambda x: x[0], reverse=True)[:5]
            
            # This is a placeholder for more sophisticated color analysis
            # In a full implementation, you'd compare against faction color palettes
            
            return 70.0  # Default neutral score
            
        except Exception:
            return 70.0
    
    def _assess_faction_style(self, pil_image: Image.Image, faction_profile: Dict) -> float:
        """Assess style consistency with faction profile"""
        # Placeholder for advanced style analysis
        # Could use style transfer networks or feature matching
        return 70.0
    
    def _detect_compression_artifacts(self, cv_image: np.ndarray) -> float:
        """Detect compression artifacts"""
        # Simplified artifact detection
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Look for blocky patterns (8x8 JPEG blocks)
            block_score = self._detect_blocking_artifacts(gray)
            
            return 100.0 - block_score * 50  # Convert to quality score
            
        except Exception:
            return 80.0
    
    def _detect_blocking_artifacts(self, gray: np.ndarray) -> float:
        """Detect blocking artifacts"""
        try:
            # Simple block artifact detection
            h, w = gray.shape
            block_differences = []
            
            # Check for discontinuities at 8-pixel intervals
            for y in range(8, h-8, 8):
                for x in range(8, w-8, 8):
                    # Compare adjacent blocks
                    diff = abs(float(gray[y, x]) - float(gray[y, x-1]))
                    block_differences.append(diff)
            
            if block_differences:
                avg_diff = np.mean(block_differences)
                return min(1.0, avg_diff / 50.0)  # Normalize
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _assess_noise_level(self, cv_image: np.ndarray) -> float:
        """Assess image noise level"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Use noise estimation based on high-frequency content
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            noise = cv2.absdiff(gray, blur)
            noise_level = np.mean(noise)
            
            # Convert to quality score (lower noise = higher score)
            quality_score = max(0, 100 - noise_level * 2)
            return quality_score
            
        except Exception:
            return 80.0
    
    def _assess_color_banding(self, cv_image: np.ndarray) -> float:
        """Assess color banding issues"""
        try:
            # Simple banding detection using gradient analysis
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Calculate gradients
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Look for unnatural gradient patterns
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            smooth_areas = grad_magnitude < 10  # Areas with low gradients
            
            if np.sum(smooth_areas) > 0:
                # Check for sudden jumps in smooth areas (indication of banding)
                banding_score = self._detect_sudden_transitions(gray, smooth_areas)
                return 100.0 - banding_score * 30
            
            return 90.0
            
        except Exception:
            return 80.0
    
    def _detect_sudden_transitions(self, gray: np.ndarray, smooth_areas: np.ndarray) -> float:
        """Detect sudden transitions in smooth areas"""
        # Placeholder for banding detection algorithm
        return 0.0
    
    def _assess_bit_depth(self, pil_image: Image.Image) -> float:
        """Assess if bit depth is adequate"""
        try:
            # Check bit depth and dynamic range
            if pil_image.mode == 'RGB':
                return 100.0  # 8-bit per channel is adequate for most uses
            elif pil_image.mode == 'L':
                return 80.0   # Grayscale is adequate but not optimal
            else:
                return 60.0   # Other modes may have limitations
                
        except Exception:
            return 80.0

    def get_quality_gate_decision(self, metrics: QualityMetrics, asset_spec: AssetSpecification) -> Dict[str, Any]:
        """
        Make quality gate decision based on metrics and asset requirements
        
        Returns:
            Dictionary with decision, actions, and reasoning
        """
        asset_type = asset_spec.asset_type
        thresholds = self.type_thresholds.get(asset_type, {"min": 70, "target": 80, "hero": 85})
        
        decision = {
            "pass": False,
            "action": "reject",
            "reasoning": [],
            "required_enhancements": [],
            "estimated_improvement": 0.0
        }
        
        score = metrics.overall_score
        min_threshold = thresholds["min"]
        target_threshold = thresholds["target"]
        
        if score >= target_threshold:
            decision.update({
                "pass": True,
                "action": "approve",
                "reasoning": [f"Quality score {score:.1f} meets target threshold {target_threshold}"]
            })
        elif score >= min_threshold:
            decision.update({
                "pass": True,
                "action": "approve_with_enhancement",
                "reasoning": [f"Quality score {score:.1f} meets minimum threshold {min_threshold}"],
                "required_enhancements": self._get_required_enhancements(metrics)
            })
        else:
            # Calculate if enhancement could bring it to acceptable level
            potential_improvement = self._estimate_enhancement_improvement(metrics)
            if score + potential_improvement >= min_threshold:
                decision.update({
                    "pass": False,
                    "action": "enhance_and_retry",
                    "reasoning": [f"Quality score {score:.1f} below minimum, but enhancement may improve to {score + potential_improvement:.1f}"],
                    "required_enhancements": self._get_required_enhancements(metrics),
                    "estimated_improvement": potential_improvement
                })
            else:
                decision.update({
                    "pass": False,
                    "action": "regenerate",
                    "reasoning": [f"Quality score {score:.1f} too low, regeneration required"],
                })
        
        return decision
    
    def _get_required_enhancements(self, metrics: QualityMetrics) -> List[str]:
        """Get list of required enhancements based on metrics"""
        enhancements = []
        
        if metrics.needs_upscale:
            enhancements.append("upscale")
        if metrics.needs_sharpen:
            enhancements.append("sharpen")
        if metrics.needs_detail_enhance:
            enhancements.append("detail_enhance")
        if metrics.needs_color_correct:
            enhancements.append("color_correct")
            
        return enhancements
    
    def _estimate_enhancement_improvement(self, metrics: QualityMetrics) -> float:
        """Estimate potential quality improvement from enhancements"""
        improvement = 0.0
        
        if metrics.needs_upscale and metrics.resolution_score < 70:
            improvement += min(20.0, 80.0 - metrics.resolution_score) * 0.2
        
        if metrics.needs_sharpen and metrics.sharpness_score < 70:
            improvement += min(15.0, 85.0 - metrics.sharpness_score) * 0.2
        
        if metrics.needs_detail_enhance and metrics.detail_score < 70:
            improvement += min(10.0, 80.0 - metrics.detail_score) * 0.2
        
        if metrics.needs_color_correct and metrics.technical_score < 70:
            improvement += min(10.0, 80.0 - metrics.technical_score) * 0.1
        
        return improvement

class QualityAssuranceManager:
    """
    High-level quality assurance orchestrator for the Terminal Grounds pipeline.
    Manages quality gates, enhancement workflows, and quality tracking.
    """
    
    def __init__(self, assessment_engine: QualityAssessmentEngine):
        self.assessment_engine = assessment_engine
        self.quality_history: List[QualityAssessmentResult] = []
        
    def process_asset(self, image_path: Path, asset_spec: AssetSpecification) -> Dict[str, Any]:
        """
        Complete quality assurance processing for an asset
        
        Returns:
            Processing result with decisions and actions
        """
        # Assess quality
        assessment_result = self.assessment_engine.assess_quality(image_path, asset_spec)
        
        # Make quality gate decision
        gate_decision = self.assessment_engine.get_quality_gate_decision(
            assessment_result.metrics, 
            asset_spec
        )
        
        # Record in history
        self.quality_history.append(assessment_result)
        
        # Return comprehensive result
        return {
            "assessment": assessment_result,
            "gate_decision": gate_decision,
            "processing_timestamp": time.time(),
            "next_actions": self._determine_next_actions(gate_decision, assessment_result)
        }
    
    def _determine_next_actions(self, gate_decision: Dict, assessment_result: QualityAssessmentResult) -> List[Dict[str, Any]]:
        """Determine concrete next actions based on quality gate decision"""
        actions = []
        
        if gate_decision["action"] == "approve":
            actions.append({
                "type": "approve",
                "description": "Asset approved for production use",
                "priority": "info"
            })
            
        elif gate_decision["action"] == "approve_with_enhancement":
            for enhancement in gate_decision["required_enhancements"]:
                actions.append({
                    "type": "enhance",
                    "method": enhancement,
                    "description": f"Apply {enhancement} enhancement",
                    "priority": "medium"
                })
                
        elif gate_decision["action"] == "enhance_and_retry":
            for enhancement in gate_decision["required_enhancements"]:
                actions.append({
                    "type": "enhance",
                    "method": enhancement,
                    "description": f"Apply {enhancement} enhancement",
                    "priority": "high"
                })
            actions.append({
                "type": "reassess",
                "description": "Re-assess quality after enhancement",
                "priority": "high"
            })
            
        elif gate_decision["action"] == "regenerate":
            actions.append({
                "type": "regenerate",
                "description": "Regenerate asset with improved parameters",
                "priority": "critical",
                "suggestions": assessment_result.recommendations.get("regeneration_suggestions", [])
            })
        
        return actions
    
    def get_quality_statistics(self) -> Dict[str, Any]:
        """Get quality statistics from processing history"""
        if not self.quality_history:
            return {"message": "No quality assessments recorded yet"}
        
        scores = [result.metrics.overall_score for result in self.quality_history]
        ratings = [result.metrics.rating.value for result in self.quality_history]
        
        stats = {
            "total_assessments": len(self.quality_history),
            "average_score": np.mean(scores),
            "score_std": np.std(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "rating_distribution": {},
            "recent_trend": self._calculate_quality_trend()
        }
        
        # Calculate rating distribution
        for rating in QualityRating:
            count = sum(1 for r in ratings if r == rating.value)
            stats["rating_distribution"][rating.value] = count
        
        return stats
    
    def _calculate_quality_trend(self) -> str:
        """Calculate recent quality trend"""
        if len(self.quality_history) < 5:
            return "insufficient_data"
        
        recent_scores = [result.metrics.overall_score for result in self.quality_history[-5:]]
        earlier_scores = [result.metrics.overall_score for result in self.quality_history[-10:-5]] if len(self.quality_history) >= 10 else []
        
        if not earlier_scores:
            return "stable"
        
        recent_avg = np.mean(recent_scores)
        earlier_avg = np.mean(earlier_scores)
        
        if recent_avg > earlier_avg + 5:
            return "improving"
        elif recent_avg < earlier_avg - 5:
            return "declining"
        else:
            return "stable"