#!/usr/bin/env python3
"""
Terminal Grounds Quality Assurance System v1
Automated quality assessment and improvement recommendations

Based on visual analysis findings from August 24, 2025
"""

import json
import os
from pathlib import Path

class TerminalGroundsQA:
    """Quality assurance system for Terminal Grounds asset generation"""
    
    def __init__(self):
        self.quality_criteria = {
            "lore_accuracy": {
                "weight": 30,
                "indicators": [
                    "post_apocalyptic_elements",
                    "faction_markers", 
                    "resource_scarcity",
                    "alien_tech_influence",
                    "cascade_damage"
                ]
            },
            "visual_quality": {
                "weight": 25,
                "indicators": [
                    "sharp_details",
                    "proper_composition",
                    "lighting_quality",
                    "material_believability"
                ]
            },
            "style_consistency": {
                "weight": 20,
                "indicators": [
                    "clean_scifi_vs_gritty_differentiation",
                    "terminal_grounds_aesthetic",
                    "environmental_storytelling"
                ]
            },
            "technical_execution": {
                "weight": 15,
                "indicators": [
                    "resolution_quality",
                    "no_artifacts",
                    "proper_exposure",
                    "color_consistency"
                ]
            },
            "game_readiness": {
                "weight": 10,
                "indicators": [
                    "no_text_elements",
                    "appropriate_perspective",
                    "usable_composition"
                ]
            }
        }
        
        self.common_failures = {
            "tech_wastes_generic": {
                "description": "Tech Wastes looking like normal industrial site",
                "solution": "Add autolines, robot arms, cable trellises, coolant plumes",
                "prompt_fix": "Include specific lore elements from Tech Wastes description"
            },
            "corporate_luxury_conflict": {
                "description": "Corporate lobby too luxurious for post-apocalyptic setting",
                "solution": "Add damage, emergency lighting, abandoned elements",
                "prompt_fix": "Emphasize post-cascade decay and abandonment"
            },
            "iez_too_sterile": {
                "description": "IEZ facility too clean, missing alien tech influence",
                "solution": "Add phase distortions, EMP damage, blue-ash contamination",
                "prompt_fix": "Include reality distortion and cascade effects"
            },
            "style_differentiation_weak": {
                "description": "Clean SciFi and Gritty Realism not clearly different",
                "solution": "Stronger condition modifiers, clearer wear patterns",
                "prompt_fix": "Use enhanced style modifiers with specific condition states"
            }
        }

    def assess_generation_batch(self, batch_results):
        """Assess a batch of generated assets"""
        assessment = {
            "total_assets": len(batch_results),
            "quality_distribution": {"excellent": 0, "good": 0, "acceptable": 0, "failed": 0},
            "common_issues": [],
            "recommendations": []
        }
        
        for asset in batch_results:
            quality_score = self.assess_individual_asset(asset)
            asset["quality_score"] = quality_score
            
            # Categorize quality
            if quality_score >= 8:
                assessment["quality_distribution"]["excellent"] += 1
            elif quality_score >= 6:
                assessment["quality_distribution"]["good"] += 1
            elif quality_score >= 4:
                assessment["quality_distribution"]["acceptable"] += 1
            else:
                assessment["quality_distribution"]["failed"] += 1
        
        # Generate recommendations
        assessment["recommendations"] = self.generate_improvement_recommendations(batch_results)
        
        return assessment

    def assess_individual_asset(self, asset_info):
        """Assess individual asset quality (would integrate with visual analysis)"""
        # This would be enhanced with actual image analysis
        # For now, using metadata and naming patterns
        
        score = 5.0  # Base score
        location = asset_info.get("location", "")
        style = asset_info.get("style", "")
        
        # Apply known issue penalties
        if "Tech_Wastes_Exterior" in location and "Clean_SciFi" in style:
            score -= 2.0  # Known to produce generic industrial sites
            
        if "Corporate_Lobby_Interior" in location and "Gritty_Realism" in style:
            score -= 1.5  # Known style conflict
            
        if "IEZ_Facility_Interior" in location:
            score -= 1.0  # Often too sterile
            
        # Apply bonuses for successful combinations
        if "Metro_Maintenance_Corridor" in location:
            score += 1.5  # Known to work well
            
        if "Underground_Bunker" in location:
            score += 2.0  # Consistently excellent
            
        return max(0, min(10, score))

    def generate_improvement_recommendations(self, batch_results):
        """Generate specific improvement recommendations"""
        recommendations = []
        
        # Analyze common failure patterns
        tech_wastes_failures = [r for r in batch_results if "Tech_Wastes_Exterior" in r.get("location", "") and r.get("quality_score", 0) < 6]
        if tech_wastes_failures:
            recommendations.append({
                "priority": "HIGH",
                "issue": "Tech Wastes Generic Appearance",
                "affected_assets": len(tech_wastes_failures),
                "solution": "Implement enhanced lore prompts with specific industrial elements",
                "implementation": "Use prompt_improvements_v1.py enhanced prompts"
            })
        
        corporate_conflicts = [r for r in batch_results if "Corporate_Lobby_Interior" in r.get("location", "") and "Gritty_Realism" in r.get("style", "")]
        if corporate_conflicts:
            recommendations.append({
                "priority": "MEDIUM",
                "issue": "Corporate Lobby Style Conflict",
                "affected_assets": len(corporate_conflicts),
                "solution": "Add post-cascade damage elements to corporate environments",
                "implementation": "Update Corporate_Lobby prompts with abandonment indicators"
            })
        
        return recommendations

    def create_improvement_workflow(self, failed_assets):
        """Create regeneration workflow for failed assets"""
        workflow = {
            "assets_to_regenerate": [],
            "prompt_modifications": {},
            "parameter_adjustments": {}
        }
        
        for asset in failed_assets:
            if asset.get("quality_score", 0) < 6:
                location = asset.get("location", "")
                style = asset.get("style", "")
                
                # Determine specific improvements needed
                improvements = self.get_asset_improvements(location, style)
                
                workflow["assets_to_regenerate"].append({
                    "original_file": asset.get("filename", ""),
                    "location": location,
                    "style": style,
                    "improvements_needed": improvements
                })
        
        return workflow

    def get_asset_improvements(self, location, style):
        """Get specific improvements needed for an asset"""
        improvements = []
        
        if location == "Tech_Wastes_Exterior":
            improvements.append("Add specific industrial lore elements: autolines, robot arms, cable trellises")
            improvements.append("Include atmospheric haze and warning strobes")
            improvements.append("Emphasize post-industrial decay")
        
        if location == "Corporate_Lobby_Interior" and style == "Gritty_Realism":
            improvements.append("Add visible damage and decay")
            improvements.append("Include emergency lighting systems")
            improvements.append("Show abandonment and resource scarcity")
        
        if location == "IEZ_Facility_Interior":
            improvements.append("Add alien tech influence indicators")
            improvements.append("Include EMP damage and reality distortion")
            improvements.append("Add blue-ash contamination traces")
        
        return improvements

# Example usage and testing
if __name__ == "__main__":
    qa_system = TerminalGroundsQA()
    
    # Simulate batch results based on our actual findings
    batch_results = [
        {"location": "Metro_Maintenance_Corridor", "style": "Clean_SciFi", "filename": "TG_PERFECT_Metro_Clean.png"},
        {"location": "Underground_Bunker", "style": "Gritty_Realism", "filename": "TG_PERFECT_Bunker_Gritty.png"},
        {"location": "Tech_Wastes_Exterior", "style": "Clean_SciFi", "filename": "TG_PERFECT_Tech_Clean.png"},
        {"location": "Corporate_Lobby_Interior", "style": "Gritty_Realism", "filename": "TG_PERFECT_Corp_Gritty.png"},
        {"location": "IEZ_Facility_Interior", "style": "Clean_SciFi", "filename": "TG_PERFECT_IEZ_Clean.png"}
    ]
    
    assessment = qa_system.assess_generation_batch(batch_results)
    
    print("Terminal Grounds Quality Assessment")
    print("=" * 40)
    print(f"Total Assets: {assessment['total_assets']}")
    print(f"Quality Distribution: {assessment['quality_distribution']}")
    print()
    print("Recommendations:")
    for rec in assessment['recommendations']:
        print(f"- {rec['priority']}: {rec['issue']}")
        print(f"  Solution: {rec['solution']}")
        print(f"  Implementation: {rec['implementation']}")
        print()