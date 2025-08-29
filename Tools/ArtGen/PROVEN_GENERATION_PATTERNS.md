# Terminal Grounds - Proven Asset Generation Patterns
## Baseline Reference for Experimental Development

**Version**: 1.0  
**Analysis Date**: August 29, 2025  
**Success Rate**: 92% (terminal_grounds_generator.py benchmark)  
**Scripts Analyzed**: weapon_concepts_sharp.py, terminal_grounds_generator.py, FIXED_faction_vehicle_concepts.py

---

## **CRITICAL SUCCESS FOUNDATION - DO NOT MODIFY**

### **Golden Standard Parameters (PERFECTION_PARAMS)**
```python
PERFECTION_PARAMS = {
    "seed": 94887,           # Proven base seed
    "sampler": "heun",       # Proven sampler
    "scheduler": "normal",   # Proven scheduler  
    "cfg": 3.2,             # Proven CFG for 92% success rate
    "steps": 25,            # Proven steps for reliability
    "width": 1536,          # Proven resolution
    "height": 864           # Proven aspect ratio
}
```

### **7-Node Workflow Structure (MANDATORY)**
```python
workflow = {
    "1": {"class_type": "CheckpointLoaderSimple"},     # Checkpoint
    "2": {"class_type": "CLIPTextEncode"},             # Positive prompt
    "3": {"class_type": "CLIPTextEncode"},             # Negative prompt  
    "4": {"class_type": "EmptyLatentImage"},           # Latent image
    "5": {"class_type": "KSampler"},                   # Sampler
    "6": {"class_type": "VAEDecode"},                  # VAE decode
    "7": {"class_type": "SaveImage"}                   # Save output
}
```

### **Systematic Seed Management**
```python
# Proven seed calculation for consistent results
seed_offset = (i * len(styles)) + j
final_seed = PERFECTION_PARAMS["seed"] + seed_offset

# Alternative proven approach (vehicles)
seed = base_seed + (i * 100)  # 100-unit spacing
```

---

## **TEXT ELIMINATION STRATEGIES**

### **Complete Text Elimination (100% Success)**
**Source**: FIXED_faction_vehicle_concepts.py

**Positive Prompt Strategy**:
- Focus on pure visual elements: "technical mechanical detail, industrial design, realistic wear patterns"
- Remove ALL text references: No "faction insignia, unit numbers, stenciling"
- Emphasize visual quality: "orthographic concept view, game asset design"

**Enhanced Negative Prompts**:
```python
negative_prompt = "text, letters, numbers, symbols, writing, inscriptions, labels, signage, military markings, stencils, unit numbers, faction insignia, readable text, words, typography, character symbols, alphanumeric content, gibberish text, scrambled letters, unreadable markings, nonsense symbols, corrupted signage"
```

### **Text Sharpness Enhancement**
**Source**: weapon_concepts_sharp.py

**Positive Prompt Enhancements**:
- "ultra sharp professional weapon concept art"
- "razor sharp orthographic view, crystal clear technical details"
- "pin-sharp mechanical components, high definition technical drawing"

**Anti-Blur Negative Prompts**:
```python
"blurry, out of focus, soft focus, low resolution, pixelated, fuzzy, hazy, unclear, indistinct, smudged, motion blur, depth of field blur, gaussian blur, soft edges, poor focus, low detail"
```

---

## **BULLETPROOF NEGATIVE PROMPT SYSTEM**

### **Master Negative Prompt Template (200+ words)**
**Source**: terminal_grounds_generator.py (92% success rate)

```python
negative_prompt = "blurry, low quality, pixelated, distorted, bad anatomy, bad lighting, oversaturated, undersaturated, generic, sterile, empty, lifeless, bland, boring, repetitive, copy-paste, artificial, fake, plastic, clean room, laboratory sterile, no character, no personality, no human presence, no wear patterns, no use evidence, blurry text, illegible text, garbled text, nonsensical text, generic sci-fi text, placeholder text, lorem ipsum, corrupted text, fuzzy lettering, low resolution text, pixelated text, distorted signage, soft focus, washed out, watermark, signature, modern cars, contemporary clothing, smartphones, modern technology, fantasy elements, magic, supernatural, cartoon, anime, illustration, abstract, gradient, overexposed, blown highlights"
```

**Critical Categories Covered**:
- Quality issues: "blurry, low quality, pixelated, distorted"
- Text problems: "blurry text, illegible text, garbled text, nonsensical text"  
- Aesthetic problems: "generic, sterile, empty, lifeless, bland"
- Anachronisms: "modern cars, contemporary clothing, smartphones"
- Unwanted styles: "fantasy elements, magic, cartoon, anime"

---

## **PARAMETER VARIATIONS FOR SPECIFIC NEEDS**

### **Enhanced Detail Parameters**
**Source**: weapon_concepts_sharp.py
```python
"cfg": 3.5,        # Slightly higher for more prompt adherence
"steps": 30,       # More steps for detail
```

### **Alternative Model Strategy**
**Source**: FIXED_faction_vehicle_concepts.py
```python
# For vehicles requiring different approach
SDXL_OPTIMIZED_PARAMS = {
    "sampler": "dpmpp_2m",
    "scheduler": "karras", 
    "cfg": 7.0,
    "steps": 30,
    "width": 1024,
    "height": 1024
}
# Model: "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
```

---

## **LORE INTEGRATION SYSTEM**

### **PowerShell Lore Integration**
**Source**: terminal_grounds_generator.py
```python
def get_lore_prompt(region_id, faction_id=None):
    """Use existing Build-LorePrompt.ps1 to generate lore-accurate prompts"""
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", 
           "C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/Build-LorePrompt.ps1",
           "-RegionId", region_id, "-IncludeStyleCapsule"]
    # Always include fallback to manual prompts
```

### **Lore Mapping System**
```python
lore_mapping = {
    "Metro_Maintenance_Corridor": "REG_METRO_A",
    "IEZ_Facility_Interior": "REG_IEZ", 
    "Tech_Wastes_Exterior": "REG_TECH_WASTES"
}
```

---

## **PROMPT CONSTRUCTION PATTERNS**

### **Master Prompt Structure**
**Source**: terminal_grounds_generator.py
```python
# Base location + Style modifier + Angle + Lighting + TG context
positive_prompt = base_prompt + style_modifier + angle_modifier + lighting_modifier + tg_context

# Universal Terminal Grounds context
tg_context = ", post-cascade world, 6 months after IEZ disaster, resource scarcity, professional game art concept, high detail environmental design, sharp focus crisp edges, fine surface textures, balanced exposure, architectural visualization quality"
```

### **Proven Style Modifiers**
```python
style_modifiers = {
    "Clean_SciFi": ", functional lived-in industrial aesthetic, well-maintained but actively used equipment, operational status with human touches",
    "Gritty_Realism": ", gritty lived-in post-apocalyptic aesthetic, weathered surfaces with human adaptation marks, survival-worn environment"
}
```

---

## **SUBMISSION AND TIMING PATTERNS**

### **Proven Submission Pattern**
```python
def submit_workflow(workflow):
    client_id = str(uuid.uuid4())
    prompt_data = {"prompt": workflow, "client_id": client_id}
    data = json.dumps(prompt_data).encode('utf-8')
    req = urllib.request.Request("http://127.0.0.1:8188/prompt", 
                               data=data, 
                               headers={'Content-Type': 'application/json'})
    time.sleep(0.5)  # Critical timing between submissions
```

### **Error Handling Pattern**
```python
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        return result.get('prompt_id')
except Exception as e:
    print(f"Error: {e}")
    return None
```

---

## **MODEL SELECTION STRATEGIES**

### **Primary Model (FLUX)**
- **File**: "FLUX1\\flux1-dev-fp8.safetensors"
- **Best For**: Environments, general concepts, high success rate
- **Parameters**: heun/normal/CFG 3.2/25 steps

### **Secondary Model (SDXL)**  
- **File**: "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
- **Best For**: Vehicles, when FLUX text corruption occurs
- **Parameters**: dpmpp_2m/karras/CFG 7.0/30 steps

---

## **QUALITY VALIDATION CHECKLIST**

### **Pre-Generation Validation**
- [ ] Using 7-node numbered workflow structure
- [ ] PERFECTION_PARAMS applied correctly
- [ ] Bulletproof negative prompt included
- [ ] Systematic seed calculation implemented
- [ ] 0.5 second delays between submissions

### **Post-Generation Quality Check**
- [ ] No text corruption or gibberish
- [ ] Sharp focus and clear details
- [ ] Terminal Grounds aesthetic consistency
- [ ] Proper faction color schemes (if applicable)
- [ ] No anachronisms or modern elements

---

## **EXPERIMENTAL DEVELOPMENT GUIDELINES**

### **For Text Elimination Experiments**
- **Baseline**: Complete text elimination from FIXED_faction_vehicle_concepts.py
- **Safe to Test**: Advanced negative prompt refinements
- **Risky**: Adding any text-related positive prompts

### **For Visual Enhancement Experiments**
- **Baseline**: heun/normal/CFG 3.2/25 steps from terminal_grounds_generator.py
- **Safe to Test**: CFG variations 3.0-3.8, step variations 25-35
- **Risky**: Changing sampler/scheduler combination

### **For Efficiency Experiments**
- **Baseline**: 0.5 second submission delays, single batch processing
- **Safe to Test**: Batch size optimizations, queue management
- **Risky**: Removing delays or parallel submissions

---

## **CRITICAL SUCCESS FACTORS - NEVER MODIFY**

1. **7-Node Workflow Structure**: Essential for reliability
2. **heun/normal Combination**: Proven 92% success rate foundation
3. **CFG 3.2**: Sweet spot for Terminal Grounds aesthetic
4. **Systematic Seed Management**: Prevents duplicate generations
5. **Bulletproof Negative Prompts**: Essential quality protection
6. **0.5 Second Submission Delays**: Prevents queue corruption

---

**WARNING**: Any experimental modifications should be tested on small batches (3-5 assets) before large-scale deployment. Always maintain one proven baseline script as fallback.

**SUCCESS VALIDATION**: New experimental approaches must achieve >90% success rate on 10-asset test batch before replacing proven patterns.