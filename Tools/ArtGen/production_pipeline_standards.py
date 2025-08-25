#!/usr/bin/env python3
"""
Terminal Grounds Production Pipeline Standards v1.2
CTO-designed standardized quality validation and production deployment system

Based on v1.1 analysis and success patterns, this establishes the complete
production pipeline for consistent 100% AAA quality achievement.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Fix Windows Unicode encoding
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

class ProductionPipelineStandards:
    def __init__(self):
        self.output_dir = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output")
        
        # PRODUCTION QUALITY STANDARDS (Based on v1.1 analysis)
        self.quality_standards = {
            "masterpiece_threshold": 2.0,      # MB - Consistently excellent quality
            "aaa_ready_threshold": 1.2,        # MB - Production acceptable  
            "production_minimum": 0.8,         # MB - Minimum acceptable
            "failure_threshold": 0.8,          # MB - Below this = regeneration required
            "target_aaa_percentage": 95,       # % - Minimum AAA ready for production
            "target_masterpiece_percentage": 15 # % - Target for portfolio quality
        }
        
        # PROVEN SUCCESSFUL PARAMETERS (From v1.1 masterpiece assets)
        self.proven_parameters = {
            "seed": 94887,
            "sampler": "heun",
            "scheduler": "normal",
            "cfg_baseline": 3.8,               # Standard quality
            "cfg_enhanced": 4.0,               # Problem asset fixes
            "steps_baseline": 32,              # Standard processing
            "steps_enhanced": 40,              # Problem asset fixes  
            "width": 1792,
            "height": 1024
        }
        
        # SUCCESS PATTERN TEMPLATES (From v1.1 analysis)
        self.success_patterns = {
            "underground_bunker": {
                "success_rate": "100%",
                "average_size": "2.1 MB",
                "key_elements": ["military stenciling", "readable displays", "lived-in details"],
                "prompt_structure": "masterpiece quality + military authenticity + technical detail"
            },
            "metro_corridor": {
                "success_rate": "100%", 
                "average_size": "1.6 MB",
                "key_elements": ["tunnel architecture", "toll systems", "convoy evidence"],
                "prompt_structure": "masterpiece quality + infrastructure detail + human presence"
            },
            "tech_wastes": {
                "success_rate": "100%",
                "average_size": "1.6 MB", 
                "key_elements": ["industrial decay", "scavenger evidence", "machinery detail"],
                "prompt_structure": "masterpiece quality + industrial complexity + survival adaptation"
            }
        }
        
        # FAILURE PATTERNS TO AVOID (From v1.1 analysis)
        self.failure_patterns = {
            "corporate_plaza": {
                "issue": "Outdoor corporate environments cause blank generation",
                "solution": "Pivot to Corporate Lobby Interior (proven 1.32MB success)"
            },
            "clean_scifi_underperformance": {
                "issue": "Clean_SciFi variants prone to sterile results",
                "solution": "Inject complexity details while maintaining clean aesthetic"
            },
            "text_quality_correlation": {
                "issue": "Text clarity correlates with overall file size",
                "solution": "Ensure minimum 1.2MB for readable signage"
            }
        }
    
    def validate_production_readiness(self, batch_directory=None):
        """Comprehensive production readiness validation"""
        if batch_directory is None:
            batch_directory = self.output_dir / "environments"
            
        if not batch_directory.exists():
            return {"error": "Batch directory not found", "production_ready": False}
        
        # Find all PNG assets in directory
        png_files = list(batch_directory.glob("*.png"))
        if not png_files:
            return {"error": "No assets found for validation", "production_ready": False}
        
        validation_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "total_assets": len(png_files),
            "quality_breakdown": {
                "masterpiece": {"count": 0, "files": []},
                "aaa_ready": {"count": 0, "files": []}, 
                "production": {"count": 0, "files": []},
                "needs_regeneration": {"count": 0, "files": []}
            },
            "quality_metrics": {
                "aaa_percentage": 0,
                "masterpiece_percentage": 0,
                "average_size_mb": 0,
                "minimum_size_mb": 0,
                "maximum_size_mb": 0
            },
            "production_ready": False,
            "recommendations": []
        }
        
        total_size = 0
        min_size = float('inf')
        max_size = 0
        
        for file_path in png_files:
            try:
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                total_size += file_size_mb
                min_size = min(min_size, file_size_mb)
                max_size = max(max_size, file_size_mb)
                
                # Classify quality level
                if file_size_mb >= self.quality_standards["masterpiece_threshold"]:
                    validation_results["quality_breakdown"]["masterpiece"]["count"] += 1
                    validation_results["quality_breakdown"]["masterpiece"]["files"].append({
                        "name": file_path.name,
                        "size_mb": round(file_size_mb, 2),
                        "grade": "MASTERPIECE"
                    })
                elif file_size_mb >= self.quality_standards["aaa_ready_threshold"]:
                    validation_results["quality_breakdown"]["aaa_ready"]["count"] += 1
                    validation_results["quality_breakdown"]["aaa_ready"]["files"].append({
                        "name": file_path.name, 
                        "size_mb": round(file_size_mb, 2),
                        "grade": "AAA READY"
                    })
                elif file_size_mb >= self.quality_standards["production_minimum"]:
                    validation_results["quality_breakdown"]["production"]["count"] += 1
                    validation_results["quality_breakdown"]["production"]["files"].append({
                        "name": file_path.name,
                        "size_mb": round(file_size_mb, 2), 
                        "grade": "PRODUCTION"
                    })
                else:
                    validation_results["quality_breakdown"]["needs_regeneration"]["count"] += 1
                    validation_results["quality_breakdown"]["needs_regeneration"]["files"].append({
                        "name": file_path.name,
                        "size_mb": round(file_size_mb, 2),
                        "grade": "NEEDS REGENERATION"
                    })
                    
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
        
        # Calculate quality metrics
        total_count = validation_results["total_assets"]
        aaa_count = (validation_results["quality_breakdown"]["masterpiece"]["count"] + 
                    validation_results["quality_breakdown"]["aaa_ready"]["count"])
        masterpiece_count = validation_results["quality_breakdown"]["masterpiece"]["count"]
        needs_regen_count = validation_results["quality_breakdown"]["needs_regeneration"]["count"]
        
        validation_results["quality_metrics"]["aaa_percentage"] = round((aaa_count / total_count) * 100, 1)
        validation_results["quality_metrics"]["masterpiece_percentage"] = round((masterpiece_count / total_count) * 100, 1)
        validation_results["quality_metrics"]["average_size_mb"] = round(total_size / total_count, 2)
        validation_results["quality_metrics"]["minimum_size_mb"] = round(min_size, 2) if min_size != float('inf') else 0
        validation_results["quality_metrics"]["maximum_size_mb"] = round(max_size, 2)
        
        # Production readiness assessment
        aaa_percentage = validation_results["quality_metrics"]["aaa_percentage"]
        production_ready = (aaa_percentage >= self.quality_standards["target_aaa_percentage"] and 
                          needs_regen_count == 0)
        validation_results["production_ready"] = production_ready
        
        # Generate recommendations
        if production_ready:
            validation_results["recommendations"].append("✅ PRODUCTION READY - All quality standards met")
            validation_results["recommendations"].append(f"✅ {aaa_percentage}% AAA ready exceeds {self.quality_standards['target_aaa_percentage']}% minimum")
        else:
            validation_results["recommendations"].append("❌ ITERATION REQUIRED - Quality standards not met")
            if aaa_percentage < self.quality_standards["target_aaa_percentage"]:
                validation_results["recommendations"].append(f"❌ {aaa_percentage}% AAA ready below {self.quality_standards['target_aaa_percentage']}% minimum")
            if needs_regen_count > 0:
                validation_results["recommendations"].append(f"❌ {needs_regen_count} assets require regeneration")
        
        return validation_results
    
    def generate_production_report(self, batch_name="current_batch", save_path=None):
        """Generate comprehensive production pipeline report"""
        validation = self.validate_production_readiness()
        
        if "error" in validation:
            return validation
        
        report = {
            "terminal_grounds_production_report": {
                "pipeline_version": "1.2",
                "batch_name": batch_name,
                "validation_results": validation,
                "quality_standards": self.quality_standards,
                "proven_parameters": self.proven_parameters,
                "success_patterns": self.success_patterns,
                "failure_patterns": self.failure_patterns,
                "production_recommendations": self._generate_production_recommendations(validation)
            }
        }
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def _generate_production_recommendations(self, validation):
        """Generate CTO production recommendations"""
        recommendations = {
            "immediate_actions": [],
            "quality_improvements": [], 
            "pipeline_optimizations": []
        }
        
        aaa_percentage = validation["quality_metrics"]["aaa_percentage"]
        needs_regen = validation["quality_breakdown"]["needs_regeneration"]["count"]
        
        # Immediate actions
        if validation["production_ready"]:
            recommendations["immediate_actions"].append("DEPLOY: Pipeline ready for production scaling")
            recommendations["immediate_actions"].append("ARCHIVE: Create production asset archive for deployment")
        else:
            recommendations["immediate_actions"].append("ITERATE: Execute v1.2 targeted fixes for failing assets")
            if needs_regen > 0:
                recommendations["immediate_actions"].append(f"REGENERATE: {needs_regen} assets below production threshold")
        
        # Quality improvements
        if aaa_percentage < 90:
            recommendations["quality_improvements"].append("ENHANCE: Increase baseline parameters for consistency")
        if validation["quality_metrics"]["masterpiece_percentage"] < 10:
            recommendations["quality_improvements"].append("OPTIMIZE: Target more masterpiece-level results")
        
        # Pipeline optimizations
        recommendations["pipeline_optimizations"].append("PATTERN: Apply Underground Bunker success template to other locations")
        recommendations["pipeline_optimizations"].append("STYLE: Prioritize Gritty_Realism for higher success rate")
        recommendations["pipeline_optimizations"].append("VALIDATE: Implement file size quality correlation in automation")
        
        return recommendations
    
    def print_production_summary(self, batch_name="current_batch"):
        """Print production pipeline summary to console"""
        validation = self.validate_production_readiness()
        
        if "error" in validation:
            print(f"❌ VALIDATION ERROR: {validation['error']}")
            return
        
        print("TERMINAL GROUNDS PRODUCTION PIPELINE SUMMARY")
        print("=" * 55)
        print(f"Batch: {batch_name}")
        print(f"Validation: {validation['validation_timestamp']}")
        print()
        
        print("QUALITY METRICS:")
        metrics = validation["quality_metrics"]
        print(f"  Total Assets: {validation['total_assets']}")
        print(f"  AAA Ready: {metrics['aaa_percentage']}% ({self.quality_standards['target_aaa_percentage']}% target)")
        print(f"  Masterpiece: {metrics['masterpiece_percentage']}% ({self.quality_standards['target_masterpiece_percentage']}% target)")
        print(f"  Average Size: {metrics['average_size_mb']} MB")
        print(f"  Size Range: {metrics['minimum_size_mb']}-{metrics['maximum_size_mb']} MB")
        print()
        
        print("QUALITY BREAKDOWN:")
        breakdown = validation["quality_breakdown"]
        print(f"  🏆 Masterpiece (2MB+): {breakdown['masterpiece']['count']}")
        print(f"  ⭐ AAA Ready (1.2MB+): {breakdown['aaa_ready']['count']}")
        print(f"  ✅ Production (0.8MB+): {breakdown['production']['count']}")
        print(f"  ❌ Needs Regeneration (<0.8MB): {breakdown['needs_regeneration']['count']}")
        print()
        
        status = "✅ PRODUCTION READY" if validation["production_ready"] else "❌ ITERATION REQUIRED"
        print(f"STATUS: {status}")
        print()
        
        print("RECOMMENDATIONS:")
        for rec in validation["recommendations"]:
            print(f"  {rec}")

if __name__ == "__main__":
    pipeline = ProductionPipelineStandards()
    pipeline.print_production_summary("v1.1_perfection_grade")
    
    # Generate comprehensive report
    report_path = "production_pipeline_report.json"
    report = pipeline.generate_production_report("v1.1_perfection_grade", report_path)
    print(f"\nDetailed report saved: {report_path}")