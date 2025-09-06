# Terminal Grounds - Technical Specifications

## MANDATORY AGENT SYSTEM DISCOVERY PROTOCOL

### CRITICAL: READ THIS FIRST BEFORE ANY WORK

**SYSTEM ARCHITECTURE EVOLUTION**: Terminal Grounds has THREE major asset generation systems that work together:

1. **Pipeline v2.0** - `Tools/ArtGen/terminal_grounds_pipeline.py` + `pipeline/` directory
   - **PRIMARY SYSTEM**: Enterprise-grade unified pipeline
   - CLI interface with batch processing, faction assets, validation
   - Complete asset lifecycle management with UE5 integration
   - **LOCATION**: `Tools/ArtGen/pipeline/` (full module structure)

2. **Proven Templates** - `Tools/ArtGen/terminal_grounds_generator.py`  
   - 92% success rate foundational system
   - Perfect parameters: heun/normal/CFG 3.2/25 steps
   - Template for manual workflow creation

3. **Legacy Systems** - `Tools/ArtGen/archive/` and individual scripts
   - Historical development, mostly archived
   - Reference for troubleshooting only

**AGENT DISCOVERY CHECKLIST** - Execute BEFORE any asset generation work:

```bash
# 1. Check for Pipeline v2.0 (PRIMARY SYSTEM)
ls Tools/ArtGen/pipeline/
python Tools/ArtGen/terminal_grounds_pipeline.py --help

# 2. Verify core generation templates
ls Tools/ArtGen/terminal_grounds_*.py

# 3. Check workflow directory
ls Tools/ArtGen/workflows/

# 4. Verify output directory (CRITICAL)
ls Tools/Comfy/ComfyUI-API/output/
```

**GENERATION ANALYSIS PROTOCOL** - Execute AFTER any asset generation:

```bash
# 1. ALWAYS use Read tool to examine actual images (not just file lists)
Read file_path="C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/[FILENAME.png]"

# 2. Assess visual quality, lore accuracy, and Terminal Grounds aesthetic fit
# 3. NEVER claim success based only on file counts - examine content!
# 4. Reference: Docs/Technical/GENERATION_ANALYSIS_REFERENCE.md for detailed procedures
```

**IF YOU MISS PIPELINE V2.0, YOU'RE MISSING THE PRIMARY SYSTEM!**

## REPRODUCIBLE SUCCESS PATTERNS

### CRITICAL DEVELOPMENT PRINCIPLE

#### USE PIPELINE V2.0 FOR ALL NEW WORK - REFINE EXISTING SYSTEMS ONLY

**Master Template**: `Tools/ArtGen/terminal_grounds_generator.py` - 92% success rate proven

- **7-node workflow structure** (numbered 1-7, not named)
- **PERFECT_PARAMS dictionary** (heun/normal/CFG 3.2/25 steps)
- **Prompt dictionary approach** (location_prompts + style_modifiers)
- **Systematic seed offsets** - `(i * len(styles)) + j`
- **Robust error handling** with try/catch
- **0.5 second delays** between submissions

**For ANY new generation type**: Copy this script, modify ONLY the prompts dictionary

**For fixes**: Edit existing dictionary entries, never rebuild workflow structure

**For emblems**: Use same template, change resolution to 1024x1024, update prompts

**Golden Rule**: If terminal_grounds_generator.py works, use its exact structure everywhere

### GUARANTEED SUCCESS PROMPTS (100% success rate)

- **Underground Bunkers** (both Clean SciFi + Gritty Realism)
- **Metro Maintenance Corridors** (both styles)  
- **IEZ Facility Interiors** (both styles)
- **Tech Wastes Exteriors** (both styles)
- **Research Laboratories** (both styles)
- **Security Checkpoints** (both styles)
- **Industrial Platforms** (both styles)

### RELIABLE FACTION EMBLEMS (95% success rate)

- **Directorate** - Blue chevron design, corporate authority
- **Free77** - Red circular emblem, mercenary aesthetic  
- **NomadClans** - Intricate tribal design, weathered texture

### KNOWN PROBLEM PROMPTS (require fixes)

- **Corporate Plaza** - Outdoor environments fail (use "Corporate Lobby Interior" instead)
- **VulturesUnion Emblem** - Name conflicts with model training (use "Scavenger Union")
- **CorporateCombine Emblem** - Too generic (use "Combine Industries" + "hexagonal blue design")

## Technical Environment

### AI/ML Setup

- **ComfyUI**: Running on port 8188 (standard ComfyUI)
- **Model**: FLUX1-dev-fp8.safetensors
- **LoRAs**: 173 available in collection
- **CRITICAL - CORRECT OUTPUT DIRECTORY**: `C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/`
- **WRONG OUTPUT DIRECTORY (DO NOT USE)**: `C:/Users/Zachg/Documents/ComfyUI/output/`
- **PRODUCTION STRUCTURE**: Organized into 01_PRODUCTION_READY/, 02_CHIEF_ART_DIRECTOR/, 03_DEVELOPMENT/, 04_ARCHIVE/, 05_QUALITY_CONTROL/
- **ASSET NAMING**: TG_[CATEGORY]_[NAME]_[VARIANT]_[VERSION].png for production, CAD_[CATEGORY]_[FACTION]_[CONCEPT]_[VERSION].png for Chief Art Director enhanced

### Windows Environment (Primary Development Platform)

- **NEVER use unicode characters** in console output (→, ✓, ✗, etc.) - causes 'charmap' codec errors
- **ALWAYS use ASCII alternatives**: -> instead of →, OK instead of ✓, FAILED instead of ✗
- **All Python scripts must include**: `# -*- coding: utf-8 -*-` header for proper encoding
- **Path separators**: Use forward slashes in paths - Python handles Windows conversion automatically

### Text Quality in FLUX Generation

- **PROBLEM**: FLUX models generate gibberish text due to conflicting prompt guidance
- **SOLUTION**: Use specific negative prompts (gibberish text, scrambled letters, unreadable text) instead of generic "text"
- **FOR LOGOS**: Add "clean readable typography, sharp lettering, military stencil precision" to positive prompts
- **FOR CONCEPT ART**: Minimize text references entirely
- **REFERENCE**: See `Tools/ArtGen/text_quality_improvements.md` for complete implementation guide

### AGENT CRITICAL ERROR PREVENTION

**NEVER LOOK IN THE WRONG OUTPUT DIRECTORY AGAIN!**

- **ACTIVE OUTPUT**: `C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/`
- **OLD/UNUSED**: `C:/Users/Zachg/Documents/ComfyUI/output/` (August 2025 old files)
- When analyzing generations, user reports, or checking recent work: **ALWAYS use the Tools/Comfy/ComfyUI-API/output/ directory**
- The Documents/ComfyUI/output directory contains stale files that will confuse analysis

### Known Issues

- **ComfyUI API**: Prompts validate but fail to execute (electron version issue)
- **Workaround**: GUI workflow loading works perfectly
- **Documentation**: See `Tools/ArtGen/API_INVESTIGATION_REPORT.md` for full details

### Planned Safeguards (Future Implementation)

**Status**: Documented for implementation after current 77-asset generation completes

**ComfyUI Stability Safeguards Plan** (August 25, 2025):

- **Queue Health Monitor**: Extend `Tools/test_comfyui_api.py` with progression tracking, 15-minute no-progress alerts
- **Generation Timeout Detection**: Track individual jobs via `/history`, flag >8 minute generations  
- **Resource Monitoring**: GPU/memory usage tracking, OOM prevention
- **Graceful Restart Protocol**: Queue state preservation, controlled shutdown/restart sequence
- **Queue Preservation**: JSON backup of pending items, duplicate prevention on restore
- **Integration**: Enhance `Tools/ArtGen/chief_art_director_organizer.py` with monitoring hooks

**Implementation Approach**: Update existing files only (Tools/test_comfyui_api.py, organizer, CLAUDE.md)
**Benefits**: Prevents lost work, early warning system, automated recovery, production reliability
**Risk**: Low (extends existing tools without replacement)
**Timeline**: Implement when queue is clear to avoid disrupting current 77-asset generation

### Key Scripts

**PRODUCTION-READY (USE THESE):**
- `Tools/ArtGen/FIXED_faction_vehicle_concepts.py` - 100% success vehicle generation (no text corruption)
- `Tools/ArtGen/FIXED_faction_ui_hud_concepts.py` - Copyright-protected UI generation
- `Tools/ArtGen/terminal_grounds_generator.py` - Proven environment generation (95% success)
- `Tools/test_comfyui_api.py` - API connectivity test
- `Tools/TerritorialSystem/territorial_websocket_server.py` - Connection-limited WebSocket server

**ARCHIVED/BROKEN (DO NOT USE):**
- `Tools/ArtGen/faction_vehicle_concepts.py` - CAUSES TEXT CORRUPTION
- `Tools/ArtGen/faction_ui_hud_concepts.py` - COPYRIGHT VIOLATION RISK
- `Tools/ArtGen/create_final_workflows.py` - Legacy workflow system
- `Tools/ArtGen/04_BROKEN_SCRIPTS/` - Archived broken scripts with complete documentation

## Development Workflow

### Asset Generation Process

1. Use proven heun/normal parameters
2. Load workflows via ComfyUI GUI (reliable method)
3. Quality assessment using 4-tier scoring system
4. Output integration into game assets

### Quality Assessment Metrics

- Composition Score (0-100)
- Detail Score (0-100)  
- Technical Score (0-100)
- Lore Alignment (0-100)
- Pass Threshold: 85+

## Project Structure

```text
Tools/ArtGen/
├── workflows/              # Production-ready workflows
├── *.py                   # Generation and quality scripts
└── API_INVESTIGATION_REPORT.md  # Detailed technical documentation
```

## Pipeline v2.0 Architecture

- `Tools/ArtGen/pipeline/core/pipeline_controller.py` - Master orchestrator
- `Tools/ArtGen/pipeline/core/asset_spec.py` - Type-safe specifications  
- `Tools/ArtGen/pipeline/core/workflow_manager.py` - Intelligent workflow selection
- `Tools/ArtGen/pipeline/core/quality_assurance.py` - Automated QA system
- `Tools/ArtGen/pipeline/core/batch_processor.py` - Enterprise batch operations
- `Tools/ArtGen/pipeline/integrations/ue5_connector.py` - UE5 integration

## Legacy: Manual Workflow System

**Location**: `Tools/ArtGen/workflows/`

**Ready-to-Use Workflows:**

- `Tools/ArtGen/workflows/TG_Metro_Corridor_FINAL.json` - Underground maintenance areas
- `Tools/ArtGen/workflows/TG_IEZ_Facility_FINAL.json` - Corporate facility interiors  
- `Tools/ArtGen/workflows/TG_TechWastes_FINAL.json` - Industrial wasteland zones

**Manual Usage Instructions:**

1. Open ComfyUI at [http://127.0.0.1:8188](http://127.0.0.1:8188)
2. Drag .json workflow into interface
3. Click "Queue Prompt"
4. Wait ~5 minutes for generation
5. Results appear in `C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/`

### Quality Standards Achieved

- Sharp, detailed environments
- Professional game art quality
- No text/UI artifacts  
- Proper exposure and lighting
- Terminal Grounds aesthetic consistency

## Lore QA Pass (Required)

- Sync lore sources: Docs/Lore/LORE_BIBLE.md → ComfyUI prompt systems.
- Rebuild prompts: Build-LorePrompt.ps1; verify with -UseLorePrompt(s).
- Smoke-test one image per category per style; target Lore Alignment ≥ 85.
- Update overlay_meta/* labels if any display names/locations change.
- Document in project documentation and PR with "Lore QA pass completed".

## Lore Change QA (Required)

Whenever lore is added or edited, run a mandatory lore-accuracy pass across generation pipelines and prompts before merging:

- Refresh lore sources: update `Docs/Lore/LORE_BIBLE.md` excerpts, ComfyUI prompt systems, and any faction/region/POI tables.
- Rebuild automatic prompts: validate `Build-LorePrompt.ps1` outputs and any batch mappings that use `-UseLorePrompt(s)`.
- Verify ComfyUI workflows: ensure positive/negative prompts and cue tokens reflect the new canon; remove obsolete tags; keep seeds deterministic for comparisons.
- Smoke-test batches: 1–2 images per category per style fork; confirm Lore Alignment ≥ 85 in audits and note any drift.
- Update overlays/UI: revise `overlay_meta/*` labels when names/locations change.
- Documentation: record changes in project documentation and this agent file; add a PR checklist item "Lore QA pass completed".

Enforcement: Do not merge lore-affecting PRs without an attached Lore QA summary (what changed, tests run, results, and follow-ups).

Last Updated: September 6, 2025