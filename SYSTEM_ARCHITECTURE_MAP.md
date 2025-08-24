# Terminal Grounds System Architecture Map
## Complete Technical Overview for Agent Reference

**Purpose**: Provide comprehensive mapping of all Terminal Grounds asset generation systems to prevent discovery failures and ensure proper system utilization.

---

## 🏗️ THREE-TIER ARCHITECTURE OVERVIEW

```
TERMINAL GROUNDS ASSET GENERATION SYSTEMS
┌─────────────────────────────────────────────────────────────┐
│                    TIER 1: ENTERPRISE                       │
│  Pipeline v2.0 - Complete Asset Lifecycle Management       │
│  Location: Tools/ArtGen/terminal_grounds_pipeline.py       │
│           + Tools/ArtGen/pipeline/ (module structure)      │
┌─────────────────────────────────────────────────────────────┤
│                    TIER 2: PROVEN TEMPLATES                │
│  Foundation Systems - 92% Success Rate Parameters         │
│  Location: Tools/ArtGen/terminal_grounds_generator.py      │
│           + Tools/ArtGen/aaa_multistage_final.py          │
┌─────────────────────────────────────────────────────────────┤
│                    TIER 3: LEGACY SYSTEMS                  │
│  Historical Development + Manual Workflows                 │
│  Location: Tools/ArtGen/archive/ + workflows/ directory   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 TIER 1: PIPELINE v2.0 (PRIMARY SYSTEM)

### Core Architecture
```
pipeline/
├── __init__.py                 # Module entry point
├── core/                      # Core functionality
│   ├── pipeline_controller.py # Master orchestrator
│   ├── asset_spec.py          # Type-safe specifications
│   ├── workflow_manager.py    # Intelligent workflow selection
│   ├── quality_assurance.py   # Automated QA system  
│   ├── batch_processor.py     # Enterprise batch operations
│   └── asset_manager.py       # File organization & metadata
├── integrations/              # External system connections
│   └── ue5_connector.py       # Unreal Engine 5 integration
├── comfyui/                   # ComfyUI client systems
│   └── enhanced_client.py     # Advanced API client
└── utils/                     # Supporting utilities
    ├── config.py              # Configuration management
    ├── logger.py              # Logging system
    ├── validation.py          # Input validation
    ├── image_analysis.py      # Quality assessment
    ├── upscaling.py           # Enhancement algorithms
    └── file_utils.py          # File management
```

### Entry Points & Commands
```bash
# Main CLI interface
python Tools/ArtGen/terminal_grounds_pipeline.py [command] [options]

# Available commands:
generate          # Single asset generation
batch-csv         # CSV-based batch processing
faction-assets    # Complete faction asset sets
validate          # System validation and health checks
interactive       # Interactive operation mode
status            # System status overview
```

### Capabilities Matrix
| Feature | Available | Implementation |
|---------|-----------|----------------|
| Single Asset Generation | ✅ | CLI + AssetSpecification |
| Batch Processing | ✅ | CSV import + BatchProcessor |
| Faction-Aware Generation | ✅ | Faction validation + templates |
| Quality Assurance | ✅ | Automated scoring + validation |
| UE5 Integration | ✅ | UE5Connector module |
| Workflow Intelligence | ✅ | WorkflowManager selection |
| Progress Tracking | ✅ | Real-time callbacks |
| System Validation | ✅ | Health check system |

---

## 🔧 TIER 2: PROVEN TEMPLATES (FOUNDATION)

### Core Templates
```
Tools/ArtGen/
├── terminal_grounds_generator.py    # 92% success rate foundation
├── aaa_multistage_final.py         # Multi-stage enhancement pipeline
└── working_flux_generator.py       # Baseline FLUX integration
```

### Proven Parameters (SACRED - NEVER CHANGE)
```python
PERFECT_PARAMS = {
    "seed": 94887,
    "sampler": "heun",
    "scheduler": "normal", 
    "cfg": 3.2,
    "steps": 25,
    "width": 1536,
    "height": 864
}
```

### Template Usage Patterns
```python
# 7-node workflow structure (numbered 1-7, not named)
workflow = {
    "1": CheckpointLoaderSimple,
    "2": CLIPTextEncode (positive),
    "3": CLIPTextEncode (negative),
    "4": EmptyLatentImage,
    "5": KSampler,
    "6": VAEDecode,
    "7": SaveImage
}

# Prompt dictionary approach
location_prompts = {
    "Metro_Maintenance_Corridor": "Terminal Grounds Metro_Maintenance_Corridor, ...",
    "IEZ_Facility_Interior": "Terminal Grounds IEZ_Facility_Interior, ...",
    # etc.
}

# Style modifier system
style_modifiers = {
    "Clean_SciFi": ", clean sci-fi aesthetic, sleek design, ...",
    "Gritty_Realism": ", gritty realistic style, weathered surfaces, ..."
}
```

### Success Rate Data
- **Underground Bunkers**: 100% success (Masterpiece quality: 2MB+ files)
- **Metro Maintenance Corridors**: 100% success  
- **IEZ Facility Interiors**: 100% success
- **Tech Wastes Exteriors**: 100% success
- **Research Laboratories**: 100% success
- **Security Checkpoints**: 100% success
- **Faction Emblems**: 95% success rate

---

## 📁 TIER 3: LEGACY SYSTEMS (REFERENCE ONLY)

### Archive Structure
```
Tools/ArtGen/archive/
├── scripts_20250823/          # August 23 system snapshots
│   ├── aaa_quality_pipeline.py
│   ├── aaa_locked_generator.py
│   ├── aaa_workflow_builder.py
│   └── [various aaa_* scripts]
└── [individual archived scripts]
```

### Manual Workflows (Fallback Only)
```
Tools/ArtGen/workflows/
├── TG_Metro_Corridor_FINAL.json       # Underground maintenance
├── TG_IEZ_Facility_FINAL.json         # Corporate interiors
├── TG_TechWastes_FINAL.json           # Industrial exteriors
├── production/                        # Production workflows
├── experimental/                      # Experimental variants
└── api/                              # API-optimized versions
```

---

## 🎮 CRITICAL SYSTEM LOCATIONS

### Output Directories
```
✅ CORRECT OUTPUT (CURRENT):
C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/

❌ WRONG OUTPUT (LEGACY - DO NOT USE):
C:/Users/Zachg/Documents/ComfyUI/output/
```

### Key Configuration Files
```
Tools/ArtGen/
├── CLAUDE.md                                    # Agent instructions
├── TERMINAL_GROUNDS_GENERATION_PLAYBOOK.md     # Success guide
├── AGENT_ERROR_PREVENTION.md                   # Error prevention
└── AGENT_SYSTEM_DISCOVERY_GUIDE.md             # Discovery protocol
```

### ComfyUI Integration
```
Tools/Comfy/ComfyUI-API/
├── main.py                     # ComfyUI server entry point
├── output/                     # Generated asset output
├── Build-LorePrompt.ps1        # Lore system integration
└── lore_prompts.json           # Faction-specific prompts
```

---

## 🔍 AGENT DISCOVERY VALIDATION

### System Presence Verification
```bash
# Pipeline v2.0 verification
[ -f "Tools/ArtGen/terminal_grounds_pipeline.py" ] && echo "✅ Pipeline v2.0 Found"
[ -d "Tools/ArtGen/pipeline/" ] && echo "✅ Pipeline Module Found"

# Template system verification  
[ -f "Tools/ArtGen/terminal_grounds_generator.py" ] && echo "✅ Core Template Found"
grep -q "PERFECT_PARAMS" Tools/ArtGen/terminal_grounds_generator.py && echo "✅ Proven Parameters Found"

# Output directory verification
[ -d "Tools/Comfy/ComfyUI-API/output/" ] && echo "✅ Correct Output Directory Found"
ls Tools/Comfy/ComfyUI-API/output/TG_PERFECT_* &>/dev/null && echo "✅ Recent Generations Found"
```

### Functional Validation
```bash
# Pipeline v2.0 functionality test
python Tools/ArtGen/terminal_grounds_pipeline.py --help | grep -q "Terminal Grounds Asset Generation Pipeline v2.0" && echo "✅ Pipeline v2.0 Functional"

# System validation capability
python Tools/ArtGen/terminal_grounds_pipeline.py validate 2>/dev/null && echo "✅ Validation System Working"
```

---

## 🚨 COMMON DISCOVERY FAILURES & PREVENTION

### Failure Mode 1: Missing Pipeline v2.0
**Symptoms**: Agent only finds individual scripts, misses enterprise system
**Cause**: Not checking for `pipeline/` directory structure
**Prevention**: Always check both `terminal_grounds_pipeline.py` AND `pipeline/` directory

### Failure Mode 2: Legacy System Confusion  
**Symptoms**: Agent focuses on archived scripts as current systems
**Cause**: Not understanding system evolution and priorities
**Prevention**: Use tier priority system (Pipeline v2.0 → Templates → Legacy)

### Failure Mode 3: Output Directory Confusion
**Symptoms**: Agent looks in wrong output directory
**Cause**: Finding old documentation or following wrong paths
**Prevention**: Always verify correct output directory: `Tools/Comfy/ComfyUI-API/output/`

### Failure Mode 4: Capability Underestimation
**Symptoms**: Agent doesn't recognize advanced features (batch processing, UE5 integration, etc.)
**Cause**: Shallow system exploration without feature discovery
**Prevention**: Execute help commands and explore module structure

---

## 📊 SYSTEM EVOLUTION TIMELINE

```
2025-01-01  │  Individual scripts, 10% success rate
2025-08-01  │  Parameter breakthrough, 92% success rate  
2025-08-23  │  AAA multi-stage systems development
2025-08-24  │  Production marathon validation (28 assets)
2025-08-24  │  Pipeline v2.0 enterprise system deployment
```

---

## 🎯 AGENT SUCCESS CRITERIA

### Complete System Awareness Checklist
- [ ] Pipeline v2.0 architecture mapped and understood
- [ ] Template system parameters validated  
- [ ] Legacy systems properly categorized
- [ ] Output directories correctly identified
- [ ] System capabilities fully documented
- [ ] Tier priorities clearly established
- [ ] Recent generation evidence located
- [ ] Functional validation successful

### Operational Readiness Confirmation
- [ ] Can determine which system to use for any given scenario
- [ ] Understands parameter inheritance from proven templates
- [ ] Knows how to validate system health and functionality
- [ ] Can locate and interpret recent generation results
- [ ] Understands system evolution and current state

---

**Last Updated**: August 24, 2025  
**System Version**: Pipeline v2.0 + Templates + Legacy  
**Validation Status**: COMPREHENSIVE  
**Next Review**: After major system architecture changes  

---

*This architecture map ensures no future agent will miss critical system components and provides complete technical reference for optimal system utilization.*