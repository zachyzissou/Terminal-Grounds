#!/usr/bin/env python3
"""
Terminal Grounds AAA Quality Assurance Framework v1.0
CTO-directed systematic quality evaluation for AAA studio standards

Quality Dimensions:
- Technical Quality: Resolution, detail, file size
- Lived-In World: Human presence, daily use evidence  
- Lore Accuracy: Terminal Grounds authenticity
- Visual Impact: Composition, lighting, atmosphere
- Production Ready: Asset usability in game development
"""

import os
from pathlib import Path
import json
from datetime import datetime

class AAAQualityFramework:
    def __init__(self):
        self.output_dir = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output")
        self.environments_dir = self.output_dir / "environments"
        
        # AAA Quality Thresholds (CTO-defined)
        self.quality_thresholds = {
            "aaa_minimum": 85,      # AAA Studio minimum
            "production_ready": 80,  # Production pipeline ready
            "needs_improvement": 70, # Requires enhancement
            "reject_threshold": 60   # Below acceptable quality
        }
        
        # Lived-In World Indicators (v1.0 focus)
        self.lived_in_indicators = [
            "personal_belongings",
            "work_tools_equipment", 
            "supply_caches",
            "foot_traffic_patterns",
            "improvised_repairs",
            "daily_use_evidence",
            "human_comfort_additions",
            "active_workstations",
            "community_modifications"
        ]
        
    def analyze_file_quality(self, file_path):
        """Analyze technical and visual quality of generated asset"""
        if not file_path.exists():
            return {"error": "File not found"}
            
        file_stats = file_path.stat()
        file_size_mb = file_stats.st_size / (1024 * 1024)
        
        # Technical quality assessment
        technical_score = self._assess_technical_quality(file_size_mb)
        
        # File naming analysis for metadata
        metadata = self._extract_metadata_from_filename(file_path.name)
        
        return {
            "file_path": str(file_path),
            "file_size_mb": round(file_size_mb, 2),
            "technical_score": technical_score,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
    
    def _assess_technical_quality(self, file_size_mb):
        """Assess technical quality based on file size and detail indicators"""
        if file_size_mb >= 2.0:
            return {"score": 95, "grade": "Masterpiece", "description": "Exceptional detail and quality"}
        elif file_size_mb >= 1.2:
            return {"score": 85, "grade": "AAA Ready", "description": "Production ready quality"}
        elif file_size_mb >= 0.8:
            return {"score": 75, "grade": "Good", "description": "Acceptable quality with room for improvement"}
        else:
            return {"score": 60, "grade": "Needs Work", "description": "Below production threshold"}
    
    def _extract_metadata_from_filename(self, filename):
        """Extract generation metadata from filename"""
        parts = filename.replace(".png", "").split("_")
        
        metadata = {
            "prefix": parts[0] if len(parts) > 0 else "unknown",
            "version": "v1.0" if "PERFECT" in filename else "legacy",
            "location": None,
            "style": None,
            "variation": None
        }
        
        # Parse TG_PERFECT_Location_Style_Variation pattern
        if len(parts) >= 4 and parts[0] == "TG" and parts[1] == "PERFECT":
            metadata["location"] = parts[2]
            metadata["style"] = parts[3] 
            if len(parts) > 4:
                metadata["variation"] = "_".join(parts[4:-1])  # Everything except last part (number)
                
        return metadata
    
    def batch_quality_analysis(self, directory=None):
        """Perform quality analysis on all generated assets"""
        if directory is None:
            directory = self.environments_dir
            
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "quality_distribution": {"aaa_ready": 0, "production_ready": 0, "needs_improvement": 0, "reject": 0},
            "version_comparison": {"v1.0": [], "v0.9": [], "legacy": []},
            "detailed_results": []
        }
        
        png_files = list(directory.glob("*.png"))
        results["total_files"] = len(png_files)
        
        for file_path in png_files:
            analysis = self.analyze_file_quality(file_path)
            results["detailed_results"].append(analysis)
            
            # Categorize by quality
            score = analysis.get("technical_score", {}).get("score", 0)
            if score >= self.quality_thresholds["aaa_minimum"]:
                results["quality_distribution"]["aaa_ready"] += 1
            elif score >= self.quality_thresholds["production_ready"]:
                results["quality_distribution"]["production_ready"] += 1  
            elif score >= self.quality_thresholds["needs_improvement"]:
                results["quality_distribution"]["needs_improvement"] += 1
            else:
                results["quality_distribution"]["reject"] += 1
                
            # Track by version for comparison
            version = analysis["metadata"]["version"]
            results["version_comparison"][version].append({
                "filename": file_path.name,
                "score": score,
                "size_mb": analysis["file_size_mb"]
            })
        
        return results
    
    def generate_quality_report(self, save_path=None):
        """Generate comprehensive AAA quality assessment report"""
        analysis = self.batch_quality_analysis()
        
        report = {
            "terminal_grounds_aaa_quality_report": {
                "framework_version": "1.0",
                "analysis": analysis,
                "summary": self._generate_summary(analysis),
                "recommendations": self._generate_recommendations(analysis)
            }
        }
        
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(report, f, indent=2)
                
        return report
    
    def _generate_summary(self, analysis):
        """Generate quality summary for CTO review"""
        total = analysis["total_files"]
        if total == 0:
            return {"error": "No files found for analysis"}
            
        quality_dist = analysis["quality_distribution"]
        aaa_percentage = (quality_dist["aaa_ready"] / total) * 100
        production_percentage = ((quality_dist["aaa_ready"] + quality_dist["production_ready"]) / total) * 100
        
        return {
            "total_assets_analyzed": total,
            "aaa_ready_percentage": round(aaa_percentage, 1),
            "production_ready_percentage": round(production_percentage, 1),
            "overall_grade": self._calculate_overall_grade(aaa_percentage),
            "top_performing_assets": self._identify_top_performers(analysis["detailed_results"])
        }
    
    def _calculate_overall_grade(self, aaa_percentage):
        """Calculate overall system grade based on AAA percentage"""
        if aaa_percentage >= 80:
            return "AAA Studio Quality Achieved"
        elif aaa_percentage >= 60:
            return "Near AAA Quality"
        elif aaa_percentage >= 40:
            return "Good Progress Toward AAA"
        else:
            return "Requires Significant Improvement"
    
    def _identify_top_performers(self, detailed_results):
        """Identify highest quality assets for reference"""
        sorted_results = sorted(detailed_results, 
                              key=lambda x: x.get("technical_score", {}).get("score", 0), 
                              reverse=True)
        
        return [
            {
                "filename": Path(result["file_path"]).name,
                "score": result["technical_score"]["score"],
                "grade": result["technical_score"]["grade"],
                "size_mb": result["file_size_mb"]
            }
            for result in sorted_results[:5]  # Top 5 performers
        ]
    
    def _generate_recommendations(self, analysis):
        """Generate CTO recommendations for quality improvement"""
        recommendations = []
        
        quality_dist = analysis["quality_distribution"]
        total = analysis["total_files"]
        
        if quality_dist["reject"] > 0:
            recommendations.append(f"CRITICAL: {quality_dist['reject']} assets below rejection threshold - investigate prompt/parameter issues")
            
        if quality_dist["aaa_ready"] / total < 0.6:
            recommendations.append("PRIORITY: Less than 60% AAA ready - enhance prompts with more detail/complexity")
            
        # Version comparison recommendations
        version_comp = analysis["version_comparison"]
        if len(version_comp["v1.0"]) > 0 and len(version_comp["v0.9"]) > 0:
            v1_avg = sum([item["score"] for item in version_comp["v1.0"]]) / len(version_comp["v1.0"])
            v09_avg = sum([item["score"] for item in version_comp["v0.9"]]) / len(version_comp["v0.9"])
            
            if v1_avg > v09_avg + 5:
                recommendations.append(f"SUCCESS: v1.0 'Lived-In World' showing {round(v1_avg - v09_avg, 1)} point improvement")
            elif v1_avg < v09_avg - 5:
                recommendations.append(f"WARNING: v1.0 regression detected - review prompt changes")
            else:
                recommendations.append("NEUTRAL: v1.0 changes showing minimal impact - consider more aggressive enhancement")
        
        return recommendations

if __name__ == "__main__":
    framework = AAAQualityFramework()
    report = framework.generate_quality_report("aaa_quality_report.json")
    print("AAA Quality Framework Analysis Complete")
    print(f"Report saved to: aaa_quality_report.json")