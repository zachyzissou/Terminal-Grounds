# Terminal Grounds - Enhanced Lore-Driven Generation Pipeline

## System Architecture Overview

Your existing system is already sophisticated - here are recommended enhancements:

### Core Components (Current)
✅ **Lore Sources**: LORE_BIBLE.md → lore_prompts.json
✅ **Prompt Builder**: Build-LorePrompt.ps1 with Region/Faction/POI integration
✅ **Style System**: quality_presets.json with UE 5.6 capsules
✅ **Submission Flow**: Test-Generate.ps1 with -UseLorePrompt
✅ **Quality Control**: Lore Alignment ≥ 85 threshold

## Proposed Enhancements

### 1. **Enhanced Prompt Sophistication**

#### A. Dynamic Detail Layering
```powershell
# Enhanced Build-LorePrompt.ps1 additions
param(
  [string]$DetailLevel = 'standard',  # minimal, standard, maximum
  [string]$WeatherState = '',         # clear, overcast, storm, haze
  [string]$TimeOfDay = '',            # dawn, day, dusk, night
  [string]$CombatState = '',          # peaceful, tense, active, aftermath
  [float]$WearLevel = 0.7             # 0.0 = pristine, 1.0 = heavily worn
)
```

#### B. Contextual Material Enhancement
```json
{
  "materialStates": {
    "fresh": "clean surfaces, minimal wear, recent construction",
    "lived": "normal wear patterns, functional maintenance, daily use",
    "weathered": "environmental damage, rust patterns, paint loss",
    "battle": "impact scoring, shrapnel marks, emergency repairs",
    "abandoned": "decay overtaking, nature reclaiming, structural failure"
  }
}
```

### 2. **Advanced Style Capsule System**

#### Current Style Capsule (Good):
```
"in-engine render, Unreal Engine 5.6, Lumen GI, Nanite geometry, game-ready, 
gritty realism, photoreal, cinematic lighting, volumetric haze"
```

#### Enhanced Multi-Tier Capsules:
```json
{
  "styleCapsules": {
    "base": "in-engine render, Unreal Engine 5.6, Lumen GI, Nanite geometry",
    "quality": "game-ready, gritty realism, photoreal, AAA production values",
    "lighting": "cinematic lighting, volumetric haze, directional key light, SSAO",
    "materials": "high-frequency normal maps, PBR materials, texture streaming",
    "postfx": "ACES filmic, neutral grade, motion blur, temporal anti-aliasing"
  }
}
```

### 3. **Intelligent Negative Prompt System**

#### Context-Aware Negatives:
```json
{
  "negativeProfiles": {
    "environmental": "text, watermark, logo, typography, poster, borders, UI elements",
    "material": "plastic appearance, unrealistic materials, flat surfaces, uniform wear",
    "lighting": "overexposed, underexposed, flat lighting, no shadows",
    "technical": "low resolution, artifacts, compression, aliasing, clipping",
    "style": "cartoon, anime, illustration, concept art, painterly, clean surfaces"
  }
}
```

### 4. **Enhanced Lore Integration**

#### A. Seasonal/Environmental Modifiers
```json
{
  "environmentalStates": {
    "storm": {
      "lighting": "dramatic storm lighting, lightning reflections",
      "materials": "rain-slicked surfaces, water pooling",
      "atmosphere": "heavy precipitation, reduced visibility"
    },
    "drought": {
      "lighting": "harsh daylight, deep shadows",
      "materials": "dust accumulation, cracked surfaces",
      "atmosphere": "heat haze, dry particle suspension"
    }
  }
}
```

#### B. Faction-Specific Material Libraries
```json
{
  "factionMaterials": {
    "FCT_VUL": {
      "signature": "welded patch repairs, color-coded salvage, functional aesthetics",
      "materials": "mixed metal alloys, polymer patches, exposed wiring",
      "wear": "tool marks, honest wear, practical modifications"
    },
    "FCT_CCB": {
      "signature": "corporate polish, integrated diagnostics, brand consistency",
      "materials": "composite panels, LED status indicators, clean geometries",
      "wear": "minimal use wear, maintained appearance, logo presence"
    }
  }
}
```

### 5. **Smart Sampling Enhancement**

#### HeunPP2 Integration with Context:
```powershell
function Get-OptimalSampler {
    param($DetailLevel, $Resolution, $ContentType)
    
    if ($DetailLevel -eq 'maximum' -and $Resolution -ge '1920x1080') {
        return 'heunpp2'  # Enhanced detail for high-res
    } elseif ($ContentType -eq 'environmental' -and $DetailLevel -eq 'standard') {
        return 'heun'     # Proven performer
    } else {
        return 'dpmpp_2m' # Fast fallback
    }
}
```

### 6. **Quality Assurance Pipeline**

#### Enhanced Audit Criteria:
```json
{
  "auditCriteria": {
    "loreAlignment": {
      "weight": 0.25,
      "factors": ["faction_accuracy", "environmental_consistency", "material_authenticity"]
    },
    "technicalQuality": {
      "weight": 0.25,
      "factors": ["resolution", "clarity", "artifact_presence"]
    },
    "gameReadiness": {
      "weight": 0.25,
      "factors": ["uv_layout_implied", "pbr_compatibility", "optimization_level"]
    },
    "narrativeValue": {
      "weight": 0.25,
      "factors": ["story_support", "emotional_impact", "world_building"]
    }
  }
}
```

### 7. **Advanced Usage Patterns**

#### A. Narrative-Driven Generation:
```powershell
./Test-Generate.ps1 -UseLorePrompt -RegionId REG_METRO_A -FactionId FCT_VUL 
  -Subject "salvage operation checkpoint" 
  -Action "sorting scavenged Directorate equipment after a skirmish"
  -WeatherState "overcast" -CombatState "aftermath" -WearLevel 0.8
  -DetailLevel "maximum" -Sampler heunpp2
```

#### B. Environmental Storytelling:
```powershell
./Test-Generate.ps1 -UseLorePrompt -RegionId REG_IEZ -PoiId POI_IEZ_OUTER_RING
  -Subject "EMP-damaged salvage field"
  -Action "scavengers working under rolling electromagnetic interference"
  -TimeOfDay "dusk" -WeatherState "charged_storm"
  -CombatState "tense" -DetailLevel "maximum"
```

### 8. **Batch Enhancement System**

#### Smart Batch Categories:
```powershell
# Enhanced batch generation with contextual variation
./Batch-Generate-PostApoc.ps1 -UseLorePrompts -VariationLevel "environmental"
  # Generates same scenes across different weather/time states
  
./Batch-Generate-PostApoc.ps1 -UseLorePrompts -VariationLevel "factional"
  # Shows same locations from different faction perspectives
```

### 9. **Integration with HeunPP2**

#### Smart Sampler Selection:
```json
{
  "samplerRules": {
    "heunpp2": {
      "when": ["detail_level == maximum", "resolution >= 1920x1080", "material_focus == true"],
      "benefits": "enhanced texture detail, superior material realism",
      "cost": "15-20% longer generation time"
    },
    "heun": {
      "when": ["detail_level == standard", "batch_generation == true"],
      "benefits": "proven reliability, consistent results",
      "cost": "standard generation time"
    }
  }
}
```

## Implementation Priority

### Phase 1: Immediate (High Impact, Low Effort)
1. **Add HeunPP2 integration** to quality_presets.json
2. **Enhance negative prompts** with context awareness
3. **Fix Build-LorePrompt.ps1** character encoding issues

### Phase 2: Short Term (Medium Impact, Medium Effort)
1. **Implement environmental modifiers** (weather, time of day)
2. **Add faction-specific material libraries**
3. **Create smart sampler selection logic**

### Phase 3: Long Term (High Impact, High Effort)
1. **Build narrative-driven generation system**
2. **Implement multi-tier style capsules**
3. **Create advanced quality assurance pipeline**

Your existing system is already production-quality. These enhancements would elevate it from "excellent" to "industry-leading" for game asset generation.