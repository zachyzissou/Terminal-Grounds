#!/usr/bin/env python3
"""
Terminal Grounds Prompt Improvements v1
Incremental improvements to enhance lore accuracy and visual quality

Based on visual analysis findings from August 24, 2025 batch generation
"""

# Enhanced location prompts with Terminal Grounds-specific lore elements
ENHANCED_LOCATION_PROMPTS = {
    "Metro_Maintenance_Corridor": {
        "base": "Terminal Grounds Metro_Maintenance_Corridor, underground maintenance tunnel system, Warden toll territory neutral ground",
        "lore_elements": "arched platforms, service alcoves, grated vents, hazard chevrons, weathered concrete, flaked paint, oily puddles, conduit bundles",
        "atmosphere": "warm practicals, cool fill, shafted dust through vents",
        "materials": "brushed metal panels, concrete surfaces, cable management systems"
    },
    
    "IEZ_Facility_Interior": {
        "base": "Terminal Grounds IEZ_Facility_Interior, Interdiction Exclusion Zone outer ring facility, post-cascade damage visible",
        "lore_elements": "phase-sheared surfaces, EMP damage scorch patterns, tilted structural elements, alien tech influence",
        "atmosphere": "charged haze, reality distortion effects, unstable lighting",
        "materials": "slagged steel, cracked surfaces, blue-ash dust contamination"
    },
    
    "Tech_Wastes_Exterior": {
        "base": "Terminal Grounds Tech_Wastes_Exterior, de-industrial wasteland with stuttering automated factories",
        "lore_elements": "autolines, robot arms, cable trellises, coolant plumes, abandoned conveyor systems",
        "atmosphere": "industrial fog, warning strobes through haze, toxic environment",
        "materials": "oxidized alloys, stained polymer panels, glass dust, rusted machinery"
    },
    
    "Corporate_Lobby_Interior": {
        "base": "Terminal Grounds Corporate_Lobby_Interior, abandoned corporate facility interior, post-cascade corporate decay",
        "lore_elements": "shattered glass walls, damaged reception areas, emergency power lighting, corporate debris",
        "atmosphere": "emergency lighting, dust motes, abandoned corporate authority",
        "materials": "cracked marble floors, broken glass panels, emergency lighting systems"
    },
    
    "Underground_Bunker": {
        "base": "Terminal Grounds Underground_Bunker, military fortification, Directorate or abandoned military installation",
        "lore_elements": "reinforced blast doors, military stenciling, emergency systems, defensive positions",
        "atmosphere": "emergency lighting, military discipline, fortified security",
        "materials": "reinforced concrete, heavy steel doors, military-grade equipment"
    },
    
    "Security_Checkpoint": {
        "base": "Terminal Grounds Security_Checkpoint, faction security installation, access control facility",
        "lore_elements": "scanning equipment, guard posts, security barriers, faction identification systems",
        "atmosphere": "institutional authority, surveillance equipment, controlled access",
        "materials": "security scanners, reinforced barriers, identification systems"
    }
}

# Enhanced style modifiers with Terminal Grounds context
ENHANCED_STYLE_MODIFIERS = {
    "Clean_SciFi": {
        "aesthetic": "clean sci-fi industrial aesthetic, functional design, military precision",
        "condition": "well-maintained equipment, operational status, clean surfaces",
        "lighting": "structured industrial lighting, practical illumination systems",
        "details": "precision engineering, sleek panels, minimal wear patterns"
    },
    
    "Gritty_Realism": {
        "aesthetic": "gritty post-apocalyptic realism, scavenger repairs, survival adaptation",
        "condition": "weathered surfaces, believable aging, natural wear patterns, scavenged components",
        "lighting": "harsh practical lighting, emergency power systems, makeshift illumination",
        "details": "visible repairs, improvised modifications, resource scarcity indicators"
    }
}

# Post-cascade environmental markers (critical for Terminal Grounds feel)
POST_CASCADE_ELEMENTS = {
    "universal": "post-cascade world, 6 months after IEZ disaster, resource scarcity, improvised repairs",
    "tech_signs": "alien tech influence, EMP damage residue, reality distortion traces",
    "faction_presence": "faction territorial markers, scavenged equipment, survival modifications"
}

def build_enhanced_prompt(location, style, angle="Wide", lighting="Ambient"):
    """Build enhanced prompt with proper Terminal Grounds lore integration"""
    
    # Get enhanced location data
    location_data = ENHANCED_LOCATION_PROMPTS.get(location, {
        "base": f"Terminal Grounds {location}",
        "lore_elements": "generic industrial environment",
        "atmosphere": "neutral lighting",
        "materials": "standard materials"
    })
    
    # Get enhanced style data
    style_data = ENHANCED_STYLE_MODIFIERS.get(style, {
        "aesthetic": "standard aesthetic",
        "condition": "normal condition",
        "lighting": "standard lighting",
        "details": "basic details"
    })
    
    # Build comprehensive prompt
    base_description = location_data["base"]
    lore_elements = location_data["lore_elements"] 
    atmosphere = location_data["atmosphere"]
    materials = location_data["materials"]
    
    aesthetic = style_data["aesthetic"]
    condition = style_data["condition"] 
    style_lighting = style_data["lighting"]
    details = style_data["details"]
    
    # Universal Terminal Grounds context
    post_cascade = POST_CASCADE_ELEMENTS["universal"]
    
    # Camera and lighting variations (keep existing proven patterns)
    camera_angles = {
        "Wide": "wide angle shot, establishing shot, full environment view",
        "Detail": "detailed close-up view, architectural details, surface textures", 
        "Perspective": "dramatic perspective, dynamic angle, cinematic composition"
    }
    
    lighting_moods = {
        "Ambient": "ambient lighting, soft natural illumination",
        "Dramatic": "dramatic lighting, strong shadows, high contrast",
        "Atmospheric": "atmospheric lighting, volumetric fog, moody atmosphere"
    }
    
    angle_modifier = camera_angles.get(angle, "")
    lighting_modifier = lighting_moods.get(lighting, "")
    
    # Construct final prompt with proper ordering
    prompt_parts = [
        base_description,
        lore_elements,
        aesthetic,
        condition,
        materials,
        atmosphere,
        post_cascade,
        "professional game art concept, high detail environmental design",
        "sharp focus crisp edges, fine surface textures, balanced exposure",
        "architectural visualization quality",
        angle_modifier,
        lighting_modifier
    ]
    
    return ", ".join(filter(None, prompt_parts))

def build_enhanced_negative_prompt():
    """Enhanced negative prompt to prevent common issues"""
    base_negative = "text, words, letters, numbers, UI elements, interface, HUD, overlays, logos, signs, typography, screen text, digital displays"
    quality_negative = "blurry, soft focus, low quality, abstract, gradient, overexposed, blown highlights, washed out"
    unwanted_elements = "watermark, signature, modern cars, contemporary clothing, smartphones, modern technology"
    style_conflicts = "fantasy elements, magic, supernatural, cartoon, anime, illustration"
    
    return ", ".join([base_negative, quality_negative, unwanted_elements, style_conflicts])

# Test the improvements
if __name__ == "__main__":
    print("Enhanced Terminal Grounds Prompt System")
    print("=" * 50)
    
    # Test problematic location
    tech_wastes_prompt = build_enhanced_prompt("Tech_Wastes_Exterior", "Clean_SciFi", "Perspective", "Atmospheric")
    print("Enhanced Tech Wastes Prompt:")
    print(tech_wastes_prompt)
    print()
    
    # Test improved corporate lobby
    corporate_prompt = build_enhanced_prompt("Corporate_Lobby_Interior", "Gritty_Realism", "Wide", "Ambient")
    print("Enhanced Corporate Lobby Prompt:")
    print(corporate_prompt)
    print()
    
    print("Enhanced Negative Prompt:")
    print(build_enhanced_negative_prompt())