# Agent System Discovery Guide
## Mandatory Protocol for All Future Agents

**CRITICAL**: This guide must be followed by ALL agents working on Terminal Grounds asset generation to prevent missing critical systems.

---

## 🚨 IMMEDIATE DISCOVERY PROTOCOL

### Step 1: System Architecture Reconnaissance
Execute these commands FIRST before any asset generation work:

```bash
# 1. PRIMARY SYSTEM CHECK - Pipeline v2.0
ls Tools/ArtGen/pipeline/
python Tools/ArtGen/terminal_grounds_pipeline.py --help

# 2. PROVEN TEMPLATES CHECK  
ls Tools/ArtGen/terminal_grounds_*.py

# 3. WORKFLOW VERIFICATION
ls Tools/ArtGen/workflows/

# 4. OUTPUT DIRECTORY VALIDATION (CRITICAL)
ls Tools/Comfy/ComfyUI-API/output/

# 5. RECENT GENERATION EVIDENCE
ls -la Tools/Comfy/ComfyUI-API/output/TG_PERFECT_* | head -10
```

### Step 2: System Priority Assessment

**PRIORITY ORDER** - Use systems in this order:

1. **Pipeline v2.0** - `terminal_grounds_pipeline.py` (PRIMARY)
   - Enterprise-grade system with full lifecycle management
   - CLI interface with validation, batch processing, UE5 integration
   - Location: `Tools/ArtGen/pipeline/` directory structure

2. **Proven Templates** - `terminal_grounds_generator.py` (SECONDARY)  
   - 92% success rate foundational system
   - Perfect parameters: heun/normal/CFG 3.2/25 steps
   - Use when Pipeline v2.0 insufficient or for template reference

3. **Manual Workflows** - Individual .json files (TERTIARY)
   - Use only when automated systems cannot handle specific requirements
   - Location: `Tools/ArtGen/workflows/`

---

## 🎯 SYSTEM VALIDATION CHECKLIST

### Pipeline v2.0 Validation
```bash
# Test Pipeline v2.0 presence and functionality
python Tools/ArtGen/terminal_grounds_pipeline.py validate
python Tools/ArtGen/terminal_grounds_pipeline.py status
```

**Expected Results:**
- Pipeline Controller initialized successfully
- All core subsystems available
- ComfyUI connection testable
- Workflow validation system active

### Proven Parameters Validation
```bash
# Verify core generation templates
grep -n "PERFECT_PARAMS" Tools/ArtGen/terminal_grounds_generator.py
grep -n "heun" Tools/ArtGen/terminal_grounds_generator.py
```

**Expected Results:**
- PERFECT_PARAMS dictionary with heun/normal/CFG 3.2/25 steps
- 7-node workflow structure
- Proven location prompt patterns

---

## ⚠️ CRITICAL ERROR PREVENTION

### What Causes System Discovery Failures

1. **Shallow Exploration**: Only checking obvious files instead of systematic discovery
2. **Legacy Focus**: Finding old scripts and assuming they're current
3. **Missing Module Structure**: Not recognizing `pipeline/` directory as complete system
4. **Output Directory Confusion**: Looking in wrong output locations

### Prevention Mechanisms

1. **Always Run Discovery Protocol First**: No exceptions
2. **Validate System Hierarchy**: Pipeline v2.0 → Templates → Manual workflows
3. **Check Recent Activity**: Look for recent generation evidence in correct output directory
4. **Documentation Cross-Reference**: Verify findings against CLAUDE.md

---

## 🔍 DETAILED SYSTEM MAPPING

### Pipeline v2.0 Architecture Discovery

```bash
# Core system components
ls Tools/ArtGen/pipeline/core/
ls Tools/ArtGen/pipeline/integrations/
ls Tools/ArtGen/pipeline/utils/

# Key files to examine:
# - pipeline_controller.py (master orchestrator)
# - asset_spec.py (type-safe specifications)  
# - workflow_manager.py (intelligent selection)
# - quality_assurance.py (automated QA)
# - batch_processor.py (enterprise operations)
```

### Template System Discovery

```bash
# Core proven templates
ls Tools/ArtGen/terminal_grounds_*.py

# Critical validation files
ls TERMINAL_GROUNDS_GENERATION_PLAYBOOK.md
ls AGENT_ERROR_PREVENTION.md
```

### Legacy System Recognition  

```bash
# Archived systems (reference only)
ls Tools/ArtGen/archive/
ls Tools/ArtGen/archive/scripts_20250823/

# Individual utility scripts
ls Tools/ArtGen/aaa_*.py
ls Tools/ArtGen/create_*.py
```

---

## 📊 SUCCESS VALIDATION METRICS

### System Discovery Success Indicators

✅ **COMPLETE DISCOVERY** - All systems identified:
- Pipeline v2.0 architecture mapped
- Proven templates located and validated
- Legacy systems properly categorized
- Output directories correctly identified

✅ **PRIORITY UNDERSTANDING** - System hierarchy clear:
- Pipeline v2.0 recognized as primary
- Template system understood as foundation
- Manual workflows identified as fallback

✅ **CAPABILITY MAPPING** - Feature understanding:
- Batch processing capabilities known
- Quality assurance system identified  
- UE5 integration recognized
- Validation systems discovered

❌ **INCOMPLETE DISCOVERY** - Missing critical systems:
- Pipeline v2.0 not found or understood
- Confusing legacy scripts with current systems
- Wrong output directory assumptions
- Missing recent generation evidence

---

## 🎮 QUICK START VERIFICATION

### Immediate Functionality Test

```bash
# 1. Test Pipeline v2.0 help system
python Tools/ArtGen/terminal_grounds_pipeline.py --help

# 2. Run system validation
python Tools/ArtGen/terminal_grounds_pipeline.py validate

# 3. Check recent generation results
ls -la Tools/Comfy/ComfyUI-API/output/ | grep TG_PERFECT | head -5

# 4. Verify proven parameters
grep -A 10 "PERFECT_PARAMS" Tools/ArtGen/terminal_grounds_generator.py
```

### Agent Readiness Confirmation

Before proceeding with ANY asset generation work, confirm:
- [ ] Pipeline v2.0 system discovered and understood
- [ ] Proven templates identified and parameters validated  
- [ ] System hierarchy and priorities clear
- [ ] Output directories correctly identified
- [ ] Recent generation evidence located and analyzed
- [ ] System architecture fully mapped

---

## 🚨 FAILURE RECOVERY PROTOCOL

### If Critical Systems Were Missed

1. **STOP ALL CURRENT WORK** - Do not proceed with incomplete system knowledge
2. **Execute Full Discovery Protocol** - Run all commands in this guide
3. **Document Findings** - Update understanding with newly discovered systems
4. **Reassess Approach** - Determine if current work approach needs revision
5. **Resume with Complete Knowledge** - Proceed only with full system awareness

### Agent Self-Audit Questions

- Did I find the Pipeline v2.0 system? (`pipeline/` directory)
- Do I understand the three-tier system architecture?
- Can I identify which system to use for different scenarios?
- Do I know the correct output directory location?
- Have I validated recent generation success evidence?

**If ANY answer is "no" - return to discovery protocol**

---

**Last Updated**: August 24, 2025  
**Validation Status**: MANDATORY for all agents  
**Next Review**: After any major system architecture changes  

---

*This guide represents lessons learned from Pipeline v2.0 discovery failure and ensures comprehensive system awareness for all future agents.*