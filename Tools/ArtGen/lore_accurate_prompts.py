"""
Lore-Accurate Terminal Grounds Prompt Generator
Based on official faction documentation and art bible
"""

from typing import Dict, Any
from datetime import datetime

class TerminalGroundsPromptMaster:
    """
    Creates documentation-accurate prompts for each faction
    Based on official art bible and style guides
    """
    
    def __init__(self):
        # Documentation-accurate faction prompt templates
        self.faction_templates = {
            "DIR": {
                "name": "Directorate",
                "identity": "last remnant of unified human military command from Global Reconstruction Accord collapse",
                "visual_philosophy": "Military Precision, Corporate Authority, Technological Superiority",
                "colors": {
                    "primary": "#001F3F",  # Navy Blue - Authority, command, tradition  
                    "secondary": "#36454F",  # Gunmetal Gray - Industrial strength, durability
                    "accent": "#FFFFFF",  # Crisp White - Cleanliness, precision, medical/tech accents
                    "tech": "#4682B4"  # Steel Blue - Technology interfaces, energy systems
                },
                "emblem_core": "Eagle head in profile within angular shield",
                "emblem_colors": "White eagle on navy field with steel blue border",
                "materials": "Mil-spec aluminum, composite ceramics, ballistic polymers, anodized navy finish, anti-reflective coatings",
                "wear_pattern": "Clean maintenance, minimal corrosion, contact wear at stress points",
                "aesthetic_keywords": [
                    "clean lines", "institutional authority", "technological advancement",
                    "mass-produced", "standardized", "reliable", "military stencil letterforms",
                    "angular", "functional", "recognizable military aesthetics",
                    "regulation appearance", "well-maintained", "properly zeroed"
                ],
                "forbidden": [
                    "field modifications", "improvised", "makeshift", "amateur",
                    "cluttered", "irregular", "non-standard"
                ]
            },
            
            "VLT": {
                "name": "Vultures Union", 
                "identity": "master scavengers and salvage operators who thrive in post-Accord chaos",
                "visual_philosophy": "Salvaged Ingenuity, Industrial Grit, Pragmatic Function",
                "colors": {
                    "primary": "#B22222",  # Rust Red - Oxidation, age, salvaged materials
                    "secondary": "#696969",  # Scrap Metal Gray - Raw steel, industrial debris  
                    "accent": "#FFD700",  # Warning Yellow - Hazard stripes, attention markers
                    "detail": "#0F0F0F",  # Oil Black - Machinery lubricants, soot
                    "copper": "#B87333"  # Copper - Salvaged wiring, heat exchangers, patina
                },
                "emblem_core": "Vulture head silhouette over crossed salvage tools",
                "emblem_colors": "Rust red vulture on scrap gray field with yellow warning border",
                "materials": "Reclaimed steel plate, aluminum sheet, salvaged polymers, natural oxidation, impact damage, field repairs",
                "wear_pattern": "Heavy corrosion, weld spatter, tool marks, impact dents, riveted patches, visible welds",
                "aesthetic_keywords": [
                    "improvisation", "material reuse", "practical problem-solving", 
                    "cobbled together", "surprisingly effective", "jury-rigged systems",
                    "hand-painted stencils", "industrial block letters", "welded-on armor",
                    "field-repaired", "functional but rough", "improvised improvements",
                    "active rust", "oil stains", "thermal discoloration"
                ],
                "forbidden": [
                    "pristine", "corporate", "clean", "standardized", "regulation",
                    "mass-produced", "official"
                ]
            },
            
            "CCB": {
                "name": "Corporate Combine",
                "identity": "fusion of Vector Dynamics, Helix Industries, and Sigma Collective into techno-corporate entity",
                "visual_philosophy": "High-Tech Innovation, Corporate Authority, Experimental Edge", 
                "colors": {
                    "primary": "#4169E1",  # Corporate Blue - Authority, technology, corporate identity
                    "secondary": "#C0C0C0",  # Chrome Silver - Advanced materials, precision manufacturing
                    "accent": "#9370DB",  # Energy Purple - Experimental systems, power indicators
                    "lab": "#F8F8FF",  # Lab White - Clean rooms, medical facilities, sterile
                    "warning": "#FF8C00"  # Warning Orange - Hazard indicators, experimental warnings
                },
                "emblem_core": "Interlocked hexagonal rings representing corporate merger",
                "emblem_colors": "Silver rings on corporate blue field with energy purple accents",
                "materials": "Titanium alloys, carbon nanotubes, metamaterial composites, anodized finishes, vapor deposition coatings, smart materials",
                "wear_pattern": "Precision wear, controlled degradation, prototype aging",
                "aesthetic_keywords": [
                    "cutting-edge technology", "corporate branding", "experimental prototype systems",
                    "advanced", "expensive", "slightly unstable", "sleek", "angular",
                    "clearly high-tech", "futuristic designs", "visible energy systems",
                    "pristine maintenance", "experimental calibration", "prototype status",
                    "clean corporate sans-serif", "precision laser etching"
                ],
                "forbidden": [
                    "makeshift", "salvaged", "rusty", "improvised", "amateur",
                    "low-tech", "primitive", "weathered"
                ]
            }
        }
        
    def build_emblem_prompt(self, faction_code: str, style_emphasis: str = "standard") -> Dict[str, str]:
        """
        Build documentation-accurate emblem prompt for specific faction
        """
        
        if faction_code not in self.faction_templates:
            raise ValueError(f"Unknown faction code: {faction_code}")
            
        faction = self.faction_templates[faction_code]
        
        # Core emblem description from documentation
        core_description = faction["emblem_core"]
        color_scheme = faction["emblem_colors"]
        
        # Build comprehensive positive prompt
        positive_elements = [
            # Primary identity
            f"Terminal Grounds {faction['name']} faction military emblem",
            f"{core_description}",
            f"{color_scheme}",
            
            # Visual philosophy
            f"embodying {faction['visual_philosophy']}",
            
            # Faction identity context  
            f"representing {faction['identity']}",
            
            # Material and construction details
            f"constructed with {faction['materials'][:100]}...",  # Truncate for prompt length
            
            # Aesthetic requirements
            "professional military insignia",
            "vector art style",
            "high contrast design", 
            "centered composition",
            "iconic faction symbol",
            "game asset quality",
            "sharp geometric lines",
            "official military heraldry",
            
            # Key aesthetic words from documentation
            ", ".join(faction["aesthetic_keywords"][:8]),  # Most important keywords
            
            # Technical requirements
            "no text", "no watermarks", "no background", 
            "2048x2048 resolution ready",
            "clean vector graphics"
        ]
        
        # Build comprehensive negative prompt from forbidden elements
        negative_elements = [
            # General quality issues
            "low quality", "blurry", "pixelated", "amateur", "poorly drawn",
            "jpeg artifacts", "noise", "grain", "distorted", "malformed",
            
            # Faction-specific forbidden elements  
            ", ".join(faction["forbidden"]),
            
            # Content restrictions
            "text", "words", "letters", "numbers", "watermark", "signature",
            "copyright", "multiple objects", "cluttered", "complex background",
            "realistic photo", "3d render", "painting", "sketch", "drawing",
            "anime", "cartoon", "asymmetric", "off-center", "duplicate",
            
            # Cross-faction contamination
            "wrong colors", "incorrect faction", "mixed insignia"
        ]
        
        positive_prompt = ", ".join(positive_elements)
        negative_prompt = ", ".join(negative_elements)
        
        return {
            "positive": positive_prompt,
            "negative": negative_prompt,
            "faction_data": faction
        }
        
    def build_all_faction_prompts(self) -> Dict[str, Dict[str, str]]:
        """Build prompts for all documented factions"""
        
        all_prompts = {}
        for faction_code in self.faction_templates.keys():
            all_prompts[faction_code] = self.build_emblem_prompt(faction_code)
            
        return all_prompts

def test_lore_accurate_prompt():
    """Test the lore-accurate prompt generation"""
    
    prompt_master = TerminalGroundsPromptMaster()
    
    # Test Directorate prompt
    dir_prompt = prompt_master.build_emblem_prompt("DIR")
    
    print("=== DIRECTORATE EMBLEM PROMPT ===")
    print("POSITIVE:")
    print(dir_prompt["positive"][:500] + "...")
    print("\nNEGATIVE:")  
    print(dir_prompt["negative"][:300] + "...")
    print(f"\nBased on official documentation: {dir_prompt['faction_data']['name']}")
    print(f"Visual Philosophy: {dir_prompt['faction_data']['visual_philosophy']}")
    
    return dir_prompt

if __name__ == "__main__":
    test_lore_accurate_prompt()