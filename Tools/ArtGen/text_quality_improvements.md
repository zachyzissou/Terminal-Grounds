# Text Quality Improvements for FLUX Generation

## Problem Analysis
FLUX models often generate gibberish text due to:
- Conflicting prompt guidance (saying "text" in negative prompts)
- Lack of specific typography guidance
- Model limitations with character formation

## Implemented Solutions

### 1. Three-Tier Text Strategy

**Tier 1: Text-Free Assets (Post-Production Text Overlay)**
- **Use Case**: Logos, branding, UI elements where precise text is critical
- **Approach**: Generate clean design without text, add text in post-production
- **Negative Prompts**: Include all text-related terms to ensure clean base

**Tier 2: Environmental Text (Signage, Labels, Posters)**  
- **Use Case**: Scene elements like signs, computer screens, facility labels, faction posters
- **Approach**: Encourage readable text with specific guidance
- **Positive Prompts**: "readable signage, clear facility labels, legible computer displays, military stencil text, faction identification markers"
- **Negative Prompts**: Only "gibberish text, scrambled letters" - allow text but improve quality

**Tier 3: Concept Art Focus**
- **Use Case**: Weapons, vehicles, characters where text is incidental  
- **Approach**: Minimize text references, focus on design
- **Strategy**: Avoid text entirely in prompts

### 2. Negative Prompt Specificity
**Updated from generic "text" to specific issues:**
```
- gibberish text
- scrambled letters
- unreadable text
- corrupted characters
- malformed letters
- text artifacts
- garbled words
- broken characters
- illegible text
- poor font rendering
- messy lettering
- unclear text
```

### 3. Category-Specific Handling
- **Logos/Branding**: Emphasize typography quality
- **Concept Art**: Minimize text references
- **Emblems**: Add "readable lettering, military stencil precision"

### 4. Specific Use Cases

**Logos & Branding (Text Overlay Approach):**
- Generate clean design without text
- Add professional typography in post-production
- Ensures pixel-perfect text quality and readability
- Maintains consistent branding standards

**Environmental Scenes (AI-Generated Text):**
- Encourage readable signage: "AUTHORIZED PERSONNEL ONLY", "EXTRACTION ZONE", "DIRECTORATE FACILITY"
- Use faction-specific terminology in prompts
- Request specific text: "BLOOM facility signs", "Iron Scavengers territory markers"
- Essential for authentic post-cascade world atmosphere

**Examples of Environmental Text Prompts:**
```
+ readable facility signage saying BLOOM EXTRACTION
+ clear warning labels with AUTHORIZED PERSONNEL ONLY  
+ computer terminals displaying facility status
+ faction propaganda posters with legible text
+ directional signage showing EXTRACTION ZONE ALPHA
+ military stencil text reading DIRECTORATE COMPOUND
```

### 5. Implementation Strategy
**Current Generation (92 assets):** Using existing prompts for consistency
**Future Generations:** Apply tiered approach
- Logos → Text-free + post overlay
- Environments → Readable AI text  
- Concept art → Design focus

### 6. Quality Improvements Expected
- **Logos**: Perfect text through post-production
- **Environments**: More authentic facility atmosphere with readable signs
- **Overall**: Professional consistency across all asset types

## Files Updated
- `clean_test_ironscavengers.py` - Enhanced with category-specific text handling
- `phase2_complete_faction_emblems.py` - Updated negative prompts for text quality
- All existing scripts should be reviewed for "text" in negative prompts

## Expected Improvements
- Reduced gibberish text in logos and emblems
- Cleaner typography in branding assets  
- More professional text rendering
- Better character formation consistency

Date: August 25, 2025
Status: Implemented in current generation scripts